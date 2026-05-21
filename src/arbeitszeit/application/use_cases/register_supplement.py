import json
from datetime import datetime, timezone

from arbeitszeit.application.commands import CreateSupplementCommand
from arbeitszeit.application.results import SupplementResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain.entities import AuditLogEntry, ReviewCase, Supplement
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.domain.errors import NotFoundError


class RegisterSupplementUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: CreateSupplementCommand) -> SupplementResult:
        with self._uow:
            employee = self._uow.employee_repo.get_by_id(cmd.employee_id)
            if employee is None:
                raise NotFoundError(
                    f"Mitarbeiter {cmd.employee_id} nicht gefunden."
                )

            supplement = self._uow.supplement_repo.add(Supplement(
                id=0,
                employee_id=cmd.employee_id,
                related_booking_id=cmd.related_booking_id,
                booking_type=cmd.booking_type,
                event_at=cmd.event_at,
                recorded_at=cmd.recorded_at,
                reason=cmd.reason,
                recorded_by_user_id=cmd.recorded_by_user_id,
                approval_status=ApprovalStatus.PENDING,
                approved_by_user_id=None,
                approved_at=None,
            ))

            now = datetime.now(timezone.utc)
            review_case = self._uow.review_case_repo.add(ReviewCase(
                id=0,
                employee_id=cmd.employee_id,
                case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
                severity=ReviewSeverity.INFO,
                status=ReviewCaseStatus.OPEN,
                description=(
                    f"Nachtrag #{supplement.id}: {cmd.booking_type} "
                    f"am {cmd.event_at.date()} — {cmd.reason}"
                ),
                booking_id=cmd.related_booking_id,
                created_at=now,
                closed_at=None,
                closed_by_user_id=None,
            ))

            self._uow.audit_log_repo.add(AuditLogEntry(
                id=0,
                event_type="SUPPLEMENT_CREATED",
                object_type="supplements",
                object_id=supplement.id,
                user_id=cmd.recorded_by_user_id,
                employee_id=cmd.employee_id,
                event_at=now,
                details_json=json.dumps({
                    "booking_type": cmd.booking_type,
                    "event_at": cmd.event_at.isoformat(),
                    "related_booking_id": cmd.related_booking_id,
                    "review_case_id": review_case.id,
                }),
            ))

            self._uow.commit()
            return SupplementResult(
                supplement_id=supplement.id,
                review_case_id=review_case.id,
            )
