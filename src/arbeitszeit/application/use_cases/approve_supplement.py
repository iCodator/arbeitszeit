import json
from datetime import datetime, timedelta, timezone

from arbeitszeit.application.commands import ApproveSupplementCommand
from arbeitszeit.application.results import ApproveSupplementResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry, ReviewCase, TimeBooking
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
    UserRole,
)
from arbeitszeit.domain.errors import (
    InactiveEmployeeError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
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
            (b.booked_at for b in reversed(prev_bookings) if b.booking_type == BookingType.GO),
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


class ApproveSupplementUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: ApproveSupplementCommand) -> ApproveSupplementResult:
        with self._uow:
            approver = self._uow.user_account_repo.get_by_id(cmd.approving_user_id)
            if (
                approver is None
                or not approver.is_active
                or approver.role not in {UserRole.REVIEWER, UserRole.ADMIN}
            ):
                raise PermissionDeniedError(
                    f"Benutzer {cmd.approving_user_id} ist nicht berechtigt, "
                    "Nachträge freizugeben."
                )

            supplement = self._uow.supplement_repo.get_by_id(cmd.supplement_id)
            if supplement is None:
                raise NotFoundError(f"Nachtrag {cmd.supplement_id} nicht gefunden.")
            if supplement.approval_status != ApprovalStatus.PENDING:
                raise ValidationError(
                    f"Nachtrag {cmd.supplement_id} ist nicht im Status PENDING "
                    f"(aktuell: {supplement.approval_status.value})."
                )

            employee = self._uow.employee_repo.get_by_id(supplement.employee_id)
            if employee is None:
                raise NotFoundError(f"Mitarbeiter {supplement.employee_id} nicht gefunden.")
            if not employee.is_active:
                raise InactiveEmployeeError(f"Mitarbeiter {supplement.employee_id} ist inaktiv.")

            now = datetime.now(timezone.utc)
            self._uow.supplement_repo.approve(supplement.id, cmd.approving_user_id, now)

            review_case_id: int | None = None
            open_cases = self._uow.review_case_repo.list_open_for_employee(supplement.employee_id)
            for case in open_cases:
                if (
                    case.case_type == ReviewCaseType.MANUAL_ENTRY_REVIEW
                    and case.booking_id == supplement.related_booking_id
                ):
                    self._uow.review_case_repo.resolve(
                        case.id,
                        status=ReviewCaseStatus.RESOLVED,
                        closed_by_user_id=cmd.approving_user_id,
                    )
                    review_case_id = case.id
                    break

            day_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                supplement.employee_id, supplement.event_at.date()
            )
            validate_booking_sequence(
                supplement.booking_type,
                [b.booking_type for b in day_bookings],
            )

            placeholder = TimeBooking(
                id=0,
                employee_id=supplement.employee_id,
                booking_type=supplement.booking_type,
                booked_at=supplement.event_at,
                source=BookingSource.MANUAL,
                status=BookingStatus.OPEN,
                terminal_id=None,
                rfid_card_id=None,
                device_event_id=None,
                note=None,
            )
            schedule_flags: list[ComplianceFlag] = []
            schedule = self._uow.work_schedule_repo.get_effective(
                supplement.event_at.isoweekday(),
                supplement.event_at.date(),
                employee.id,
            )
            if schedule is not None and not (
                schedule.start_time <= supplement.event_at.time() <= schedule.end_time
            ):
                schedule_flags = [
                    ComplianceFlag(ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW, ReviewSeverity.WARN)
                ]

            prev_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                supplement.employee_id,
                supplement.event_at.date() - timedelta(days=1),
            )
            projected = list(day_bookings) + [placeholder]
            status, flags = _evaluate_booking(
                supplement.booking_type, projected, prev_bookings, schedule_flags
            )

            booking = self._uow.time_booking_repo.add(
                TimeBooking(
                    id=0,
                    employee_id=supplement.employee_id,
                    booking_type=supplement.booking_type,
                    booked_at=supplement.event_at,
                    source=BookingSource.MANUAL,
                    status=status,
                    terminal_id=None,
                    rfid_card_id=None,
                    device_event_id=None,
                    note=None,
                )
            )

            follow_up_case_ids: list[int] = []
            for flag in flags:
                case = self._uow.review_case_repo.add(
                    ReviewCase(
                        id=0,
                        employee_id=supplement.employee_id,
                        case_type=flag.case_type,
                        severity=flag.severity,
                        status=ReviewCaseStatus.OPEN,
                        description=(f"Automatisch erkannt bei Freigabe Nachtrag #{supplement.id}"),
                        booking_id=booking.id,
                        created_at=now,
                        closed_at=None,
                        closed_by_user_id=None,
                    )
                )
                follow_up_case_ids.append(case.id)

            # Erst commit, dann Audit-Log schreiben (siehe BookUseCase für Begründung).
            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=0,
                    event_type=audit_events.SUPPLEMENT_APPROVED,
                    object_type="supplements",
                    object_id=supplement.id,
                    user_id=cmd.approving_user_id,
                    employee_id=supplement.employee_id,
                    event_at=now,
                    details_json=json.dumps(
                        {
                            "supplement_id": supplement.id,
                            "booking_id": booking.id,
                            "booking_type": supplement.booking_type.value,
                            "booking_status": status.value,
                            "follow_up_case_ids": follow_up_case_ids,
                            "closed_review_case_id": review_case_id,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )
            return ApproveSupplementResult(
                supplement_id=supplement.id,
                booking_id=booking.id,
                booking_status=status,
                follow_up_case_ids=tuple(follow_up_case_ids),
            )
