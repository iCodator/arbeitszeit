"""Terminal-UI-Einstiegspunkt: Endlosschleife für den operativen Buchungsbetrieb."""
import json
import signal
import sys
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
from arbeitszeit.infrastructure.hardware.evdev_reader import EvdevHardwareReader
from arbeitszeit.infrastructure.system_check import run_system_check
from .booking_loop import format_feedback, process_booking

_DOMAIN_MESSAGES: dict[type[DomainError], str] = {
    UnknownCardError: "Karte nicht erkannt.",
    InactiveCardError: "Karte deaktiviert.",
    InactiveEmployeeError: "Mitarbeiter inaktiv.",
    InvalidBookingSequenceError: "Ungültige Buchungsreihenfolge.",
    OpenPhaseConflictError: "Offene Phase — bitte zuerst abschließen.",
}


def _log_system_event(db_path: Path, event_type: str, details: dict) -> None:
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
    except Exception:
        pass


def run(
    db_path: Path,
    numpad_device: str,
    rfid_device: str,
    terminal_id: int,
) -> None:
    """Endlosschleife mit Systemcheck, Buchungsverarbeitung und Graceful Shutdown."""
    result = run_system_check(
        db_path,
        numpad_path=Path(numpad_device),
        rfid_path=Path(rfid_device),
    )
    if not result.overall_ok:
        print("WARNUNG: Systemcheck hat Probleme festgestellt:", file=sys.stderr)
        for check in result.checks:
            if not check.ok:
                print(f"  [{check.name}] {check.detail}", file=sys.stderr)

    running = True

    def _stop(signum: int, frame: FrameType | None) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    reader = EvdevHardwareReader(numpad_path=numpad_device, rfid_path=rfid_device)
    try:
        while running:
            try:
                booking_result = process_booking(reader, db_path, terminal_id)
                print(format_feedback(booking_result))
            except DomainError as exc:
                msg = _DOMAIN_MESSAGES.get(type(exc), f"Fehler: {exc.message}")
                print(msg)
            except Exception as exc:
                print("Interner Fehler — Betrieb wird fortgesetzt.", file=sys.stderr)
                _log_system_event(
                    db_path,
                    "APPLICATION_ERROR",
                    {"error": str(exc), "type": type(exc).__name__},
                )
    finally:
        reader.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Arbeitszeit Terminal-UI")
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--numpad", required=True)
    parser.add_argument("--rfid", required=True)
    parser.add_argument("--terminal-id", required=True, type=int)
    args = parser.parse_args()
    run(args.db, args.numpad, args.rfid, args.terminal_id)
