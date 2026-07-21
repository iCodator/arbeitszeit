"""Buchungsablauf: RFID-Scan → BookUseCase → Feedback."""

__version__ = "1.1"

from pathlib import Path

from arbeitszeit.application.commands import BookCommand
from arbeitszeit.application.results import BookResult
from arbeitszeit.application.use_cases.book_time import BookUseCase
from arbeitszeit.domain.enums import BookingSource, BookingStatus, BookingType
from arbeitszeit.domain.value_objects import TerminalId
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork
from arbeitszeit.infrastructure.hardware.ports import HardwareReader

_STATUS_MESSAGES = {
    BookingStatus.OPEN: "Buchung erfasst.",
    BookingStatus.OK: "Buchung erfasst.",
    BookingStatus.WARN: "Buchung erfasst — Hinweis: Regelzeitabweichung festgestellt.",
    BookingStatus.NEEDS_REVIEW: "Buchung erfasst — Prüfpflicht: Manuelle Überprüfung erforderlich.",
}

_BOOKING_TYPE_DISPLAY: dict[BookingType, str] = {
    BookingType.COME: "Beginn",
    BookingType.GO: "Ende",
    BookingType.BREAK_START: "Pausenbeginn",
    BookingType.BREAK_END: "Pausenende",
}


def process_booking(
    reader: HardwareReader,
    db_path: Path,
    terminal_id: int,
) -> BookResult:
    """Liest eine Buchungsanforderung vom Hardware-Reader und verarbeitet sie.

    Gibt BookResult bei Erfolg zurück. Wirft DomainError-Subklassen bei
    fachlichen Fehlern (unbekannte Karte, inaktive Karte, ungültige Sequenz).
    """
    request = reader.read_next()
    conn = open_connection(db_path)
    audit_conn = open_connection(db_path)
    try:
        uow = SQLiteUnitOfWork(conn, audit_conn)

        # device_events-Record VOR dem BookUseCase-Aufruf schreiben.
        # Läuft auf derselben Verbindung im Autocommit-Modus (isolation_level=None,
        # kein BEGIN aktiv), wird also sofort committed und bleibt auch dann erhalten,
        # wenn die Buchung fachlich scheitert (z. B. UnknownCard). Das ist gewollt:
        # Das Geräteereignis ist real eingetreten, unabhängig vom Buchungsergebnis.
        # Schlägt dieser INSERT fehl, wird keine Buchung versucht (Exception weiterreichen).
        device_event_id = uow.device_event_repo.add(
            event_type="RFID_SCAN",
            terminal_id=TerminalId(terminal_id),
            rfid_uid_hash=request.uid_hash,
            payload_json="{}",
            occurred_at=request.occurred_at,
        )

        cmd = BookCommand(
            uid_hash=request.uid_hash,
            terminal_id=TerminalId(terminal_id),
            booked_at=request.occurred_at,
            device_event_id=device_event_id,
            source=BookingSource.TERMINAL,
        )
        return BookUseCase(uow).execute(cmd)
    finally:
        conn.close()
        audit_conn.close()


def format_feedback(result: BookResult) -> str:
    name = f"{result.employee_first_name} {result.employee_last_name}"
    art = _BOOKING_TYPE_DISPLAY.get(result.booking_type, result.booking_type.value)
    local = result.booked_at.astimezone()
    datum = local.strftime("%d.%m.%Y")
    uhrzeit = local.strftime("%H:%M")
    status_msg = _STATUS_MESSAGES.get(result.status, f"Status: {result.status.value}")
    return f"{name}, {art}, {datum}, {uhrzeit}: {status_msg}"
