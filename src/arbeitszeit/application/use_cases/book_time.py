import json
from datetime import datetime, timedelta, timezone

from arbeitszeit.application.commands import BookCommand
from arbeitszeit.application.results import BookResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry, ReviewCase, TimeBooking
from arbeitszeit.domain.enums import (
    BookingStatus,
    BookingType,
    CardStatus,
    ReviewCaseStatus,
    ReviewCaseType,
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
    check_rest_period,
)


def _evaluate_booking(
    booking_type: BookingType,
    projected: list[TimeBooking],
    prev_bookings: list[TimeBooking] | None = None,
    extra_flags: list[ComplianceFlag] | None = None,
) -> tuple[BookingStatus, list[ComplianceFlag]]:
    if booking_type in (BookingType.COME, BookingType.BREAK_START):
        return BookingStatus.OPEN, list(extra_flags or [])

    flags = check_break_compliance(projected) + check_max_hours(projected)

    if prev_bookings is not None:
        last_go = next(
            (
                b.booked_at
                for b in reversed(prev_bookings)
                if b.booking_type == BookingType.GO
            ),
            None,
        )
        first_come = next(
            (b.booked_at for b in projected if b.booking_type == BookingType.COME),
            None,
        )
        if last_go is not None and first_come is not None:
            flags += check_rest_period(last_go, first_come)

    flags += list(extra_flags or [])

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
            # INVARIANTE Ablehnungspfade: Vor jedem audit_log_repo.add() in einem
            # Ablehnungspfad (UnknownCard/InactiveCard) darf conn keine Schreiboperation
            # (INSERT/UPDATE/DELETE) ausgeführt haben. Schreibt conn bereits, hält es
            # einen WRITE-Lock; audit_conn kann dann trotz WAL nicht schreiben.
            # Aktuell sind hier nur SELECTs vor dem ersten Ablehnungs-Audit-Write –
            # diese Reihenfolge muss bei Erweiterungen gewahrt bleiben.
            card = self._uow.rfid_card_repo.get_by_uid_hash(cmd.uid_hash)
            if card is None:
                self._uow.audit_log_repo.add(AuditLogEntry(
                    id=0,
                    event_type=audit_events.BOOKING_REJECTED_UNKNOWN_CARD,
                    object_type="rfid_cards",
                    object_id=0,
                    user_id=None,
                    employee_id=None,
                    event_at=datetime.now(timezone.utc),
                    details_json=json.dumps(
                        {"uid_hash": cmd.uid_hash, "terminal_id": cmd.terminal_id},
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                ))
                raise UnknownCardError(f"Unbekannte RFID-UID: {cmd.uid_hash}")

            if card.status != CardStatus.ACTIVE:
                self._uow.audit_log_repo.add(AuditLogEntry(
                    id=0,
                    event_type=audit_events.BOOKING_REJECTED_INACTIVE_CARD,
                    object_type="rfid_cards",
                    object_id=card.id,
                    user_id=None,
                    employee_id=card.employee_id,
                    event_at=datetime.now(timezone.utc),
                    details_json=json.dumps(
                        {
                            "card_id": card.id,
                            "card_status": card.status.value,
                            "terminal_id": cmd.terminal_id,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                ))
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

            schedule_flags: list[ComplianceFlag] = []
            schedule = self._uow.work_schedule_repo.get_effective(
                cmd.booked_at.isoweekday(), cmd.booked_at.date(), employee.id
            )
            if schedule is not None and not (
                schedule.start_time <= cmd.booked_at.time() <= schedule.end_time
            ):
                schedule_flags = [ComplianceFlag(
                    ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW, ReviewSeverity.WARN
                )]

            prev_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                employee.id, cmd.booked_at.date() - timedelta(days=1)
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
            status, flags = _evaluate_booking(
                cmd.booking_type, projected, prev_bookings, schedule_flags
            )

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
                event_type=audit_events.TIME_BOOKED,
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
