import json
from datetime import datetime, timezone

from arbeitszeit.application.commands import BookCommand
from arbeitszeit.application.results import BookResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain.entities import AuditLogEntry, ReviewCase, TimeBooking
from arbeitszeit.domain.enums import (
    BookingStatus,
    BookingType,
    CardStatus,
    ReviewCaseStatus,
    ReviewSeverity,
)
from arbeitszeit.domain.errors import (
    InactiveCardError,
    InactiveEmployeeError,
    NotFoundError,
    UnknownCardError,
)
from arbeitszeit.domain.services.booking_rules import validate_booking_sequence
from arbeitszeit.domain.services.compliance_checks import (
    ComplianceFlag,
    check_break_compliance,
    check_max_hours,
)


def _evaluate_booking(
    booking_type: BookingType,
    projected: list[TimeBooking],
) -> tuple[BookingStatus, list[ComplianceFlag]]:
    if booking_type in (BookingType.COME, BookingType.BREAK_START):
        return BookingStatus.OPEN, []

    flags = check_break_compliance(projected) + check_max_hours(projected)
    if not flags:
        return BookingStatus.OK, []
    if any(f.severity == ReviewSeverity.CRITICAL for f in flags):
        return BookingStatus.NEEDS_REVIEW, flags
    return BookingStatus.WARN, flags


class BookUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: BookCommand) -> BookResult:
        with self._uow:
            card = self._uow.rfid_card_repo.get_by_uid_hash(cmd.uid_hash)
            if card is None:
                raise UnknownCardError(f"Unbekannte RFID-UID: {cmd.uid_hash}")

            if card.status != CardStatus.ACTIVE:
                raise InactiveCardError(f"Karte {card.id} ist nicht aktiv.")

            employee = self._uow.employee_repo.get_by_id(card.employee_id)
            if employee is None:
                raise NotFoundError(
                    f"Mitarbeiter {card.employee_id} nicht gefunden."
                )
            if not employee.is_active:
                raise InactiveEmployeeError(
                    f"Mitarbeiter {card.employee_id} ist nicht aktiv."
                )

            day_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                employee.id, cmd.booked_at.date()
            )

            validate_booking_sequence(
                cmd.booking_type,
                [b.booking_type for b in day_bookings],
            )

            placeholder = TimeBooking(
                id=0,
                employee_id=employee.id,
                booking_type=cmd.booking_type,
                booked_at=cmd.booked_at,
                source=cmd.source,
                status=BookingStatus.OPEN,
                terminal_id=cmd.terminal_id,
                rfid_card_id=card.id,
                device_event_id=cmd.device_event_id,
                note=None,
            )
            projected = list(day_bookings) + [placeholder]
            status, flags = _evaluate_booking(cmd.booking_type, projected)

            booking = self._uow.time_booking_repo.add(
                TimeBooking(
                    id=0,
                    employee_id=employee.id,
                    booking_type=cmd.booking_type,
                    booked_at=cmd.booked_at,
                    source=cmd.source,
                    status=status,
                    terminal_id=cmd.terminal_id,
                    rfid_card_id=card.id,
                    device_event_id=cmd.device_event_id,
                    note=None,
                )
            )

            now = datetime.now(timezone.utc)
            follow_up_case_ids: list[int] = []

            for flag in flags:
                case = self._uow.review_case_repo.add(ReviewCase(
                    id=0,
                    employee_id=employee.id,
                    case_type=flag.case_type,
                    severity=flag.severity,
                    status=ReviewCaseStatus.OPEN,
                    description=f"Automatisch erkannt bei Buchung #{booking.id}",
                    booking_id=booking.id,
                    created_at=now,
                    closed_at=None,
                    closed_by_user_id=None,
                ))
                follow_up_case_ids.append(case.id)

            self._uow.audit_log_repo.add(AuditLogEntry(
                id=0,
                event_type="TIME_BOOKED",
                object_type="time_bookings",
                object_id=booking.id,
                user_id=None,
                employee_id=employee.id,
                event_at=now,
                details_json=json.dumps(
                    {
                        "booking_type": cmd.booking_type.value,
                        "booked_at": cmd.booked_at.isoformat(),
                        "status": status.value,
                        "terminal_id": cmd.terminal_id,
                        "rfid_card_id": card.id,
                        "follow_up_case_ids": follow_up_case_ids,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            ))

            self._uow.commit()
            return BookResult(
                booking_id=booking.id,
                status=status,
                follow_up_case_ids=tuple(follow_up_case_ids),
            )
