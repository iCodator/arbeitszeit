"""Admin-CLI: Buchungskorrekturen und Nachträge (ADMIN/REVIEWER-Rolle).

Alle Schreiboperationen laufen über Use Cases aus der Application-Schicht.
Die Rollenprüfung erfolgt dort; hier wird nur noch Fehler-Handling und
Ausgabe gemacht.
"""

import argparse
import sqlite3
import sys
from datetime import datetime, timezone

from arbeitszeit.application.commands import (
    ApproveSupplementCommand,
    CreateCorrectionCommand,
    CreateSupplementCommand,
    RejectSupplementCommand,
)
from arbeitszeit.application.use_cases.approve_supplement import (
    ApproveSupplementUseCase,
)
from arbeitszeit.application.use_cases.correct_booking import CorrectBookingUseCase
from arbeitszeit.application.use_cases.register_supplement import (
    RegisterSupplementUseCase,
)
from arbeitszeit.application.use_cases.reject_supplement import RejectSupplementUseCase
from arbeitszeit.domain.enums import BookingType
from arbeitszeit.domain.errors import DomainError
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork


def _make_uow(conn: sqlite3.Connection, audit_conn: sqlite3.Connection) -> SQLiteUnitOfWork:
    return SQLiteUnitOfWork(conn, audit_conn)


def _parse_dt(value: str) -> datetime:
    """Parst einen ISO-8601-Datetime-String mit UTC-Fallback."""
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        print(
            f"Fehler: Ungültiges Datumsformat: {value!r} (erwartet ISO-8601)",
            file=sys.stderr,
        )
        sys.exit(1)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_booking_type(value: str) -> BookingType:
    try:
        return BookingType(value.upper())
    except ValueError:
        valid = ", ".join(t.value for t in BookingType)
        print(f"Fehler: Ungültige Buchungsart {value!r}. Gültig: {valid}", file=sys.stderr)
        sys.exit(1)


def cmd_bookings_correct(
    conn: sqlite3.Connection,
    audit_conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
) -> None:
    cmd = CreateCorrectionCommand(
        original_booking_id=args.booking_id,
        corrected_by_user_id=user_id,
        reason=args.reason,
        new_booking_type=_parse_booking_type(args.type),
        new_booked_at=_parse_dt(args.at),
    )
    try:
        result = CorrectBookingUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(
        f"Korrektur angelegt (ID {result.correction_id}), "
        f"Buchung {result.updated_booking_id} auf CORRECTED gesetzt."
    )


def cmd_bookings_supplement(
    conn: sqlite3.Connection,
    audit_conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
) -> None:
    now = datetime.now(timezone.utc)
    cmd = CreateSupplementCommand(
        employee_id=args.employee_id,
        related_booking_id=args.related_booking_id,
        booking_type=_parse_booking_type(args.type),
        event_at=_parse_dt(args.at),
        recorded_at=now,
        reason=args.reason,
        recorded_by_user_id=user_id,
    )
    try:
        result = RegisterSupplementUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(
        f"Nachtrag angelegt (ID {result.supplement_id}), "
        f"Prüffall {result.review_case_id} erzeugt."
    )


def cmd_bookings_approve_supplement(
    conn: sqlite3.Connection,
    audit_conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
) -> None:
    cmd = ApproveSupplementCommand(
        supplement_id=args.supplement_id,
        approving_user_id=user_id,
    )
    try:
        result = ApproveSupplementUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(
        f"Nachtrag {args.supplement_id} genehmigt, "
        f"Buchung {result.booking_id} angelegt (Status: {result.booking_status.value})."
    )


def cmd_bookings_reject_supplement(
    conn: sqlite3.Connection,
    audit_conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
) -> None:
    cmd = RejectSupplementCommand(
        supplement_id=args.supplement_id,
        rejected_by_user_id=user_id,
        reason=args.reason,
    )
    try:
        RejectSupplementUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Nachtrag {args.supplement_id} abgelehnt.")


def register_subcommands(
    sub: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    bookings = sub.add_parser("bookings", help="Buchungskorrekturen und Nachträge")
    bsub = bookings.add_subparsers(dest="bookings_cmd", required=True)

    correct = bsub.add_parser("correct", help="Buchung korrigieren")
    correct.add_argument("--booking-id", required=True, type=int)
    correct.add_argument("--type", required=True, metavar="BOOKING_TYPE")
    correct.add_argument("--at", required=True, metavar="DATETIME")
    correct.add_argument("--reason", required=True)

    supplement = bsub.add_parser("supplement", help="Nachtrag erfassen")
    supplement.add_argument("--employee-id", required=True, type=int)
    supplement.add_argument("--type", required=True, metavar="BOOKING_TYPE")
    supplement.add_argument("--at", required=True, metavar="DATETIME")
    supplement.add_argument("--reason", required=True)
    supplement.add_argument("--related-booking-id", type=int, default=None)

    approve = bsub.add_parser("approve-supplement", help="Nachtrag freigeben")
    approve.add_argument("--supplement-id", required=True, type=int)

    reject = bsub.add_parser("reject-supplement", help="Nachtrag ablehnen")
    reject.add_argument("--supplement-id", required=True, type=int)
    reject.add_argument("--reason", required=True)
