__version__ = "1.0"

import json
from datetime import datetime, timedelta, timezone

from arbeitszeit.application.commands import ApproveSupplementCommand
from arbeitszeit.application.results import ApproveSupplementResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.application.use_cases._booking_evaluation import evaluate_booking
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry, Employee, ReviewCase, Supplement, TimeBooking
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
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
from arbeitszeit.domain.services.compliance_checks import ComplianceFlag
from arbeitszeit.domain.value_objects import (
    AuditLogEntryId,
    EmployeeId,
    ReviewCaseId,
    SupplementId,
    TimeBookingId,
    UserAccountId,
)


class ApproveSupplementUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: ApproveSupplementCommand) -> ApproveSupplementResult:
        with self._uow:
            self._check_permission(cmd.approving_user_id)
            supplement = self._validate_supplement(cmd.supplement_id)
            employee = self._validate_employee(supplement.employee_id)

            now = datetime.now(timezone.utc)
            self._uow.supplement_repo.approve(supplement.id, cmd.approving_user_id, now)
            review_case_id = self._close_related_review_case(supplement, cmd.approving_user_id)

            day_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                supplement.employee_id, supplement.event_at.date()
            )
            validate_booking_sequence(
                supplement.booking_type,
                [b.booking_type for b in day_bookings],
            )

            placeholder = TimeBooking(
                id=TimeBookingId(0),
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
            schedule_flags = self._build_schedule_flags(supplement, employee)
            prev_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                supplement.employee_id,
                supplement.event_at.date() - timedelta(days=1),
            )
            projected = list(day_bookings) + [placeholder]
            status, flags = evaluate_booking(
                supplement.booking_type, projected, prev_bookings, schedule_flags
            )

            booking = self._uow.time_booking_repo.add(
                TimeBooking(
                    id=TimeBookingId(0),
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
            follow_up_case_ids = self._create_follow_up_cases(
                supplement.employee_id, booking.id, flags, cmd.approving_user_id, now, supplement.id
            )

            # Erst commit, dann Audit-Log schreiben (siehe BookUseCase für Begründung).
            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
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

    def _check_permission(self, user_id: UserAccountId) -> None:
        approver = self._uow.user_account_repo.get_by_id(user_id)
        if (
            approver is None
            or not approver.is_active
            or approver.role not in {UserRole.REVIEWER, UserRole.ADMIN}
        ):
            raise PermissionDeniedError(
                f"Benutzer {user_id} ist nicht berechtigt, Nachträge freizugeben."
            )

    def _validate_supplement(self, supplement_id: SupplementId) -> Supplement:
        supplement = self._uow.supplement_repo.get_by_id(supplement_id)
        if supplement is None:
            raise NotFoundError(f"Nachtrag {supplement_id} nicht gefunden.")
        if supplement.approval_status != ApprovalStatus.PENDING:
            raise ValidationError(
                f"Nachtrag {supplement_id} ist nicht im Status PENDING "
                f"(aktuell: {supplement.approval_status.value})."
            )
        return supplement

    def _validate_employee(self, employee_id: EmployeeId) -> Employee:
        employee = self._uow.employee_repo.get_by_id(employee_id)
        if employee is None:
            raise NotFoundError(f"Mitarbeiter {employee_id} nicht gefunden.")
        if not employee.is_active:
            raise InactiveEmployeeError(f"Mitarbeiter {employee_id} ist inaktiv.")
        return employee

    def _close_related_review_case(
        self,
        supplement: Supplement,
        approving_user_id: UserAccountId,
    ) -> ReviewCaseId | None:
        open_cases = self._uow.review_case_repo.list_open_for_employee(supplement.employee_id)
        for case in open_cases:
            if (
                case.case_type == ReviewCaseType.MANUAL_ENTRY_REVIEW
                and case.booking_id == supplement.related_booking_id
            ):
                self._uow.review_case_repo.resolve(
                    case.id,
                    status=ReviewCaseStatus.RESOLVED,
                    closed_by_user_id=approving_user_id,
                )
                return case.id
        return None

    def _build_schedule_flags(
        self,
        supplement: Supplement,
        employee: Employee,
    ) -> list[ComplianceFlag]:
        schedule = self._uow.work_schedule_repo.get_effective(
            supplement.event_at.isoweekday(),
            supplement.event_at.date(),
            employee.id,
        )
        if schedule is not None and not (
            schedule.start_time <= supplement.event_at.time() <= schedule.end_time
        ):
            return [ComplianceFlag(ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW, ReviewSeverity.WARN)]
        return []

    def _create_follow_up_cases(
        self,
        employee_id: EmployeeId,
        booking_id: TimeBookingId,
        flags: list[ComplianceFlag],
        approver_id: UserAccountId,
        now: datetime,
        supplement_id: SupplementId,
    ) -> list[ReviewCaseId]:
        case_ids: list[ReviewCaseId] = []
        for flag in flags:
            case = self._uow.review_case_repo.add(
                ReviewCase(
                    id=ReviewCaseId(0),
                    employee_id=employee_id,
                    case_type=flag.case_type,
                    severity=flag.severity,
                    status=ReviewCaseStatus.OPEN,
                    description=f"Automatisch erkannt bei Freigabe Nachtrag #{supplement_id}",
                    booking_id=booking_id,
                    created_at=now,
                    closed_at=None,
                    closed_by_user_id=None,
                )
            )
            case_ids.append(case.id)
        return case_ids
