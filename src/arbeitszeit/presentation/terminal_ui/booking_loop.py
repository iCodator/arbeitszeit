"""Buchungsablauf: Numpad-Eingabe → RFID-Scan → BookUseCase → Feedback."""
from pathlib import Path

from arbeitszeit.application.commands import BookCommand
from arbeitszeit.application.results import BookResult
from arbeitszeit.application.use_cases.book_time import BookUseCase
from arbeitszeit.domain.enums import BookingSource, BookingStatus
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork
from arbeitszeit.infrastructure.hardware.ports import HardwareReader

_STATUS_MESSAGES = {
    BookingStatus.OPEN: "Buchung erfasst.",
    BookingStatus.OK: "Buchung erfasst.",
    BookingStatus.WARN: "Buchung erfasst — Hinweis: Regelzeitabweichung festgestellt.",
    BookingStatus.NEEDS_REVIEW: "Buchung erfasst — Prüfpflicht: Manuelle Überprüfung erforderlich.",
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
    cmd = BookCommand(
        uid_hash=request.uid_hash,
        terminal_id=terminal_id,
        booking_type=request.booking_type,
        booked_at=request.occurred_at,
        device_event_id=None,
        source=BookingSource.TERMINAL,
    )
    conn = open_connection(db_path)
    audit_conn = open_connection(db_path)
    try:
        uow = SQLiteUnitOfWork(conn, audit_conn)
        return BookUseCase(uow).execute(cmd)
    finally:
        conn.close()
        audit_conn.close()


def format_feedback(result: BookResult) -> str:
    return _STATUS_MESSAGES.get(result.status, f"Status: {result.status.value}")
