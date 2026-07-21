"""Terminal-UI-Einstiegspunkt: Endlosschleife für den operativen Buchungsbetrieb."""

__version__ = "1.6"

import argparse
import json
import logging
import signal
import sys
import time
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

_SCAN_PROMPT = "\n" * 4 + "  Karte an das RFID-Lesegerät halten ...\n" + "\n" * 4


def _clear_screen() -> None:
    print("\033[2J\033[H", end="", flush=True)


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
    """Ein Buchungszyklus: Menü → Zeitcheck → Buchung → Feedback → 5 s Pause."""
    _clear_screen()
    print(_SCAN_PROMPT, end="", flush=True)
    try:
        monitor.check()
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
    time.sleep(2)


def run(
    db_path: Path,
    rfid_device: str,
    terminal_id: int,
    *,
    app_config: AppConfig | None = None,
) -> None:
    """Endlosschleife mit Systemcheck, Buchungsverarbeitung und Graceful Shutdown."""
    try:
        rfid_path = resolve_evdev_device(rfid_device)
    except DeviceNotFoundError as exc:
        notify("Arbeitszeit — Gerät nicht gefunden", str(exc), urgency="critical")
        sys.exit(1)

    result = run_system_check(
        db_path,
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

    running = True

    def _stop(signum: int, frame: FrameType | None) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    threshold = load_threshold_from_config(db_path)
    monitor = SystemTimeMonitor(db_path, threshold_seconds=threshold)
    monitor.check()  # Basiszeitpunkt setzen

    reader = EvdevHardwareReader(rfid_path=rfid_path)
    try:
        while running:
            _run_one_cycle(reader, db_path, terminal_id, monitor)
    finally:
        reader.close()


def main() -> None:
    """Einstiegspunkt: Argumente parsen, Konfiguration laden, run() aufrufen."""
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
        "--rfid",
        default=None,
        help='Gerätename (z.B. "RFID Reader") oder Pfad (/dev/input/eventX)',
    )
    parser.add_argument("--terminal-id", type=int, default=None)
    args = parser.parse_args()

    # Config laden: explizit > ENV ARBEITSZEIT_CONFIG > XDG > lokal
    app_config: AppConfig | None = None
    cfg_src: Path | None = args.config if args.config is not None else find_config()
    if cfg_src is not None:
        try:
            app_config = load_config(cfg_src)
        except Exception as exc:  # noqa: BLE001
            print(f"Fehler beim Laden von {cfg_src}: {exc}", file=sys.stderr)
            sys.exit(1)

    # Werte auflösen: CLI > config.toml > Fehler
    db_path = _resolve_or_exit(
        args.db,
        app_config.database.path if app_config else None,
        "--db / [database] path in config.toml",
    )
    rfid = _resolve_or_exit(
        args.rfid,
        app_config.terminal.rfid if app_config else None,
        "--rfid / [terminal] rfid in config.toml",
    )
    terminal_id = _resolve_or_exit(
        args.terminal_id,
        app_config.terminal.id if app_config else None,
        "--terminal-id / [terminal] id in config.toml",
    )

    _setup_file_logging(db_path, app_config)
    try:
        run(db_path, rfid, terminal_id, app_config=app_config)
    except Exception:
        logging.exception("Terminal-UI: nicht abgefangener Fehler in run()")
        raise


if __name__ == "__main__":  # pragma: no cover
    main()
