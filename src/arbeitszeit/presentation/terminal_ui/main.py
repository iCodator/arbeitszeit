"""Terminal-UI-Einstiegspunkt: Endlosschleife für den operativen Buchungsbetrieb."""

import json
import logging
import signal
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import FrameType

from arbeitszeit.domain.errors import (
    DomainError,
    InactiveCardError,
    InactiveEmployeeError,
    InvalidBookingSequenceError,
    OpenPhaseConflictError,
    UnknownCardError,
)
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.repositories import SQLiteSystemConfigRepository
from arbeitszeit.infrastructure.hardware.evdev_reader import (
    DeviceNotFoundError,
    EvdevHardwareReader,
    resolve_evdev_device,
)
from arbeitszeit.infrastructure.hardware.ports import HardwareReader
from arbeitszeit.infrastructure.notification import notify
from arbeitszeit.infrastructure.system_check import run_system_check
from arbeitszeit.infrastructure.time_monitor import (
    SystemTimeMonitor,
    load_threshold_from_config,
)

from .booking_loop import format_feedback, process_booking

_DOMAIN_MESSAGES: dict[type[DomainError], str] = {
    UnknownCardError: "Karte nicht erkannt.",
    InactiveCardError: "Karte deaktiviert.",
    InactiveEmployeeError: "Mitarbeiter inaktiv.",
    InvalidBookingSequenceError: "Ungültige Buchungsreihenfolge.",
    OpenPhaseConflictError: "Offene Phase — bitte zuerst abschließen.",
}


def _log_system_event(db_path: Path, event_type: str, details: dict[str, object]) -> None:
    try:
        conn = open_connection(db_path)
        try:
            conn.execute(
                "INSERT INTO system_events "
                "(event_type, source, severity, event_at, details_json) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    event_type,
                    "terminal_ui",
                    "ERROR",
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(details, default=str),
                ),
            )
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        logging.warning("_log_system_event fehlgeschlagen: %s", exc, exc_info=True)


def _ensure_terminal_exists(db_path: Path, terminal_id: int) -> None:
    conn = open_connection(db_path)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO terminals (id, terminal_code, active, created_at) "
            "VALUES (?, ?, 1, ?)",
            (terminal_id, f"TERMINAL-{terminal_id}", datetime.now(timezone.utc).isoformat()),
        )
    finally:
        conn.close()


def _setup_file_logging(db_path: Path) -> None:
    try:
        conn = open_connection(db_path)
        try:
            row = conn.execute(
                "SELECT config_value_json FROM system_config "
                "WHERE config_key = 'logging.log_dir' "
                "ORDER BY version DESC LIMIT 1"
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return
        value = json.loads(row["config_value_json"])
        if value is None:
            return
        log_path = Path(value) / "terminal_ui.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
        root = logging.getLogger()
        root.addHandler(handler)
        root.setLevel(logging.WARNING)
    except Exception as exc:  # noqa: BLE001
        logging.warning("Logging-Konfiguration fehlgeschlagen: %s", exc)


def _run_one_cycle(
    reader: HardwareReader,
    db_path: Path,
    terminal_id: int,
    monitor: SystemTimeMonitor,
) -> None:
    """Ein Buchungszyklus: Zeitcheck → Buchung → Feedback oder Fehlerbehandlung."""
    monitor.check()
    try:
        booking_result = process_booking(reader, db_path, terminal_id)
        print(format_feedback(booking_result))
    except DomainError as exc:
        msg = _DOMAIN_MESSAGES.get(type(exc), f"Fehler: {exc.message}")
        print(msg)
    except Exception as exc:
        print("Interner Fehler — Betrieb wird fortgesetzt.", file=sys.stderr)
        logging.exception("Buchungszyklus: unbehandelter Fehler")
        _log_system_event(
            db_path,
            "APPLICATION_ERROR",
            {
                "error": str(exc),
                "type": type(exc).__name__,
                "traceback": traceback.format_exc(),
            },
        )


def run(
    db_path: Path,
    numpad_device: str,
    rfid_device: str,
    terminal_id: int,
) -> None:
    """Endlosschleife mit Systemcheck, Buchungsverarbeitung und Graceful Shutdown."""
    try:
        numpad_path = resolve_evdev_device(numpad_device)
        rfid_path = resolve_evdev_device(rfid_device)
    except DeviceNotFoundError as exc:
        notify("Arbeitszeit — Gerät nicht gefunden", str(exc), urgency="critical")
        sys.exit(1)

    result = run_system_check(
        db_path,
        numpad_path=Path(numpad_path),
        rfid_path=Path(rfid_path),
    )
    if not result.overall_ok:
        print("=" * 50)
        print("SYSTEMWARNUNG — Betrieb eingeschränkt:")
        for check in result.checks:
            if not check.ok:
                print(f"  FEHLER: {check.name}: {check.detail}")
        print("=" * 50)
        # Kein sys.exit() — Buchungsbetrieb läuft weiter (Praxisbetrieb darf nicht blockieren)
        fehler = "; ".join(c.detail for c in result.checks if not c.ok)
        notify("Arbeitszeit — Systemfehler", fehler, urgency="critical")

    _ensure_terminal_exists(db_path, terminal_id)
    _setup_file_logging(db_path)

    running = True

    def _stop(signum: int, frame: FrameType | None) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    threshold = load_threshold_from_config(db_path)
    monitor = SystemTimeMonitor(db_path, threshold_seconds=threshold)
    monitor.check()  # Basiszeitpunkt setzen

    grace_conn = open_connection(db_path)
    try:
        grace_json = SQLiteSystemConfigRepository(grace_conn).get_current(
            "booking.grace_seconds_after_numpad_select"
        )
    finally:
        grace_conn.close()
    rfid_timeout = float(json.loads(grace_json)) if grace_json is not None else 5.0

    reader = EvdevHardwareReader(
        numpad_path=numpad_path,
        rfid_path=rfid_path,
        rfid_timeout=rfid_timeout,
    )
    try:
        while running:
            _run_one_cycle(reader, db_path, terminal_id, monitor)
    finally:
        reader.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Arbeitszeit Terminal-UI")
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument(
        "--numpad",
        required=True,
        help='Gerätename (z.B. "USB Numpad") oder Pfad (/dev/input/eventX)',
    )
    parser.add_argument(
        "--rfid",
        required=True,
        help='Gerätename (z.B. "RFID Reader") oder Pfad (/dev/input/eventX)',
    )
    parser.add_argument("--terminal-id", required=True, type=int)
    args = parser.parse_args()
    run(args.db, args.numpad, args.rfid, args.terminal_id)
