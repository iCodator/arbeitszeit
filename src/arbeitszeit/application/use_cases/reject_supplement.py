import json
from datetime import datetime, timezone

from arbeitszeit.application.commands import RejectSupplementCommand
from arbeitszeit.application.results import RejectSupplementResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry
from arbeitszeit.domain.enums import ApprovalStatus, ReviewCaseStatus, ReviewCaseType
from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.errors import NotFoundError, PermissionDeniedError, ValidationError


class RejectSupplementUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: RejectSupplementCommand) -> RejectSupplementResult:
        with self._uow:
            rejector = self._uow.user_account_repo.get_by_id(cmd.rejected_by_user_id)
            if (
                rejector is None
                or not rejector.is_active
                or rejector.role not in {UserRole.REVIEWER, UserRole.ADMIN}
            ):
                raise PermissionDeniedError(
                    f"Benutzer {cmd.rejected_by_user_id} ist nicht berechtigt, "
                    "Nachträge abzulehnen."
                )

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

            now = datetime.now(timezone.utc)
            self._uow.supplement_repo.reject(
                supplement.id, cmd.rejected_by_user_id, now
            )

            review_case_id: int | None = None
            open_cases = self._uow.review_case_repo.list_open_for_employee(
                supplement.employee_id
            )
            for case in open_cases:
                if (
                    case.case_type == ReviewCaseType.MANUAL_ENTRY_REVIEW
                    and supplement.related_booking_id is not None
                    and case.booking_id == supplement.related_booking_id
                ):
                    self._uow.review_case_repo.resolve(
                        case.id,
                        status=ReviewCaseStatus.CLOSED_WITH_NOTE,
                        closed_by_user_id=cmd.rejected_by_user_id,
                        note=cmd.reason,
                    )
                    review_case_id = case.id
                    break

            self._uow.audit_log_repo.add(AuditLogEntry(
                id=0,
                event_type=audit_events.SUPPLEMENT_REJECTED,
                object_type="supplements",
                object_id=supplement.id,
                user_id=cmd.rejected_by_user_id,
                employee_id=supplement.employee_id,
                event_at=now,
                details_json=json.dumps(
                    {
                        "supplement_id": supplement.id,
                        "reason": cmd.reason,
                        "closed_review_case_id": review_case_id,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            ))

            self._uow.commit()
            return RejectSupplementResult(
                supplement_id=supplement.id,
                review_case_id=review_case_id,
            )
