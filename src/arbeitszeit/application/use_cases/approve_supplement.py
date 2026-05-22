import json
from datetime import datetime, timezone

from arbeitszeit.application.commands import ApproveSupplementCommand
from arbeitszeit.application.results import ApproveSupplementResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain.entities import AuditLogEntry, ReviewCase, TimeBooking
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.domain.errors import InactiveEmployeeError, NotFoundError, ValidationError
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


class ApproveSupplementUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: ApproveSupplementCommand) -> ApproveSupplementResult:
        with self._uow:
            supplement = self._uow.supplement_repo.get_by_id(cmd.supplement_id)
            if supplement is None:
                raise NotFoundError(
                    f"Nachtrag {cmd.supplement_id} nicht gefunden."
                )
            if supplement.approval_status != ApprovalStatus.PENDING:
                raise ValidationError(
                    f"Nachtrag {cmd.supplement_id} ist nicht im Status PENDING "
                    f"(aktuell: {supplement.approval_status.value})."
                )

            employee = self._uow.employee_repo.get_by_id(supplement.employee_id)
            if employee is None:
                raise NotFoundError(
                    f"Mitarbeiter {supplement.employee_id} nicht gefunden."
                )
            if not employee.is_active:
                raise InactiveEmployeeError(
                    f"Mitarbeiter {supplement.employee_id} ist inaktiv."
                )

            now = datetime.now(timezone.utc)
            self._uow.supplement_repo.approve(
                supplement.id, cmd.approved_by_user_id, now
            )

            review_case_id: int | None = None
            open_cases = self._uow.review_case_repo.list_open_for_employee(
                supplement.employee_id
            )
            for case in open_cases:
                if (
                    case.case_type == ReviewCaseType.MANUAL_ENTRY_REVIEW
                    and case.booking_id == supplement.related_booking_id
                ):
                    self._uow.review_case_repo.resolve(
                        case.id,
                        status=ReviewCaseStatus.RESOLVED,
                        closed_by_user_id=cmd.approved_by_user_id,
                    )
                    review_case_id = case.id
                    break

            day_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                supplement.employee_id, supplement.event_at.date()
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
            projected = list(day_bookings) + [placeholder]
            status, flags = _evaluate_booking(supplement.booking_type, projected)

            booking = self._uow.time_booking_repo.add(TimeBooking(
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
            ))

            follow_up_case_ids: list[int] = []
            for flag in flags:
                case = self._uow.review_case_repo.add(ReviewCase(
                    id=0,
                    employee_id=supplement.employee_id,
                    case_type=flag.case_type,
                    severity=flag.severity,
                    status=ReviewCaseStatus.OPEN,
                    description=(
                        f"Automatisch erkannt bei Freigabe Nachtrag #{supplement.id}"
                    ),
                    booking_id=booking.id,
                    created_at=now,
                    closed_at=None,
                    closed_by_user_id=None,
                ))
                follow_up_case_ids.append(case.id)

            self._uow.audit_log_repo.add(AuditLogEntry(
                id=0,
                event_type="SUPPLEMENT_APPROVED",
                object_type="supplements",
                object_id=supplement.id,
                user_id=cmd.approved_by_user_id,
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
            ))

            self._uow.commit()
            return ApproveSupplementResult(
                supplement_id=supplement.id,
                booking_id=booking.id,
                booking_status=status,
                follow_up_case_ids=tuple(follow_up_case_ids),
            )
