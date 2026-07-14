"""Terminal-UI-Einstiegspunkt: Endlosschleife für den operativen Buchungsbetrieb."""

__version__ = "1.0"

import json
import logging
import signal
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import FrameType
from typing import TypeVar

from arbeitszeit.domain.errors import (
    DomainError,
    InactiveCardError,
    InactiveEmployeeError,
    InvalidBookingSequenceError,
    OpenPhaseConflictError,
    UnknownCardError,
)
from arbeitszeit.infrastructure.config_file import AppConfig, find_config, load_config
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

_T = TypeVar("_T")


def _resolve_or_exit(cli_val: _T | None, cfg_val: _T | None, label: str) -> _T:
    """Gibt cli_val zurück, falls gesetzt; sonst cfg_val; sonst Fehler."""
    val = cli_val if cli_val is not None else cfg_val
    if val is None:
        print(f"Fehler: {label} nicht konfiguriert.", file=sys.stderr)
        sys.exit(1)
    return val


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


def _setup_file_logging(db_path: Path, app_config: AppConfig | None = None) -> None:
    try:
        # config.toml hat Vorrang; Fallback auf DB (Rückwärtskompatibilität)
        log_dir: Path | None = app_config.backup.log_dir if app_config is not None else None
        if log_dir is None:
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
            log_dir = Path(value)
        log_path = log_dir / "terminal_ui.log"
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
    *,
    app_config: AppConfig | None = None,
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
        app_config=app_config,
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
    _setup_file_logging(db_path, app_config)

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
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        metavar="CONFIG_PATH",
        help="Pfad zu config.toml (Standard: automatische Suche)",
    )
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument(
        "--numpad",
        default=None,
        help='Gerätename (z.B. "USB Numpad") oder Pfad (/dev/input/eventX)',
    )
    parser.add_argument(
        "--rfid",
        default=None,
        help='Gerätename (z.B. "RFID Reader") oder Pfad (/dev/input/eventX)',
    )
    parser.add_argument("--terminal-id", type=int, default=None)
    _args = parser.parse_args()

    # Config laden: explizit > ENV ARBEITSZEIT_CONFIG > XDG > lokal
    _app_config: AppConfig | None = None
    _cfg_src: Path | None = _args.config if _args.config is not None else find_config()
    if _cfg_src is not None:
        try:
            _app_config = load_config(_cfg_src)
        except Exception as _exc:
            print(f"Fehler beim Laden von {_cfg_src}: {_exc}", file=sys.stderr)
            sys.exit(1)

    # Werte auflösen: CLI > config.toml > Fehler
    _db_path = _resolve_or_exit(
        _args.db,
        _app_config.database.path if _app_config else None,
        "--db / [database] path in config.toml",
    )
    _numpad = _resolve_or_exit(
        _args.numpad,
        _app_config.terminal.numpad if _app_config else None,
        "--numpad / [terminal] numpad in config.toml",
    )
    _rfid = _resolve_or_exit(
        _args.rfid,
        _app_config.terminal.rfid if _app_config else None,
        "--rfid / [terminal] rfid in config.toml",
    )
    _terminal_id = _resolve_or_exit(
        _args.terminal_id,
        _app_config.terminal.id if _app_config else None,
        "--terminal-id / [terminal] id in config.toml",
    )

    run(_db_path, _numpad, _rfid, _terminal_id, app_config=_app_config)
