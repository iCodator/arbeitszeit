import json
from datetime import datetime, timezone
from datetime import timedelta

from arbeitszeit.application.commands import ChangeWorkScheduleCommand
from arbeitszeit.application.results import WorkScheduleChangeResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain.entities import AuditLogEntry, WorkScheduleVersion
from arbeitszeit.domain.errors import ConflictError, ValidationError


class ManageWorkScheduleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: ChangeWorkScheduleCommand) -> WorkScheduleChangeResult:
        with self._uow:
            repo = self._uow.work_schedule_repo

            current = repo.get_effective(
                weekday=cmd.weekday,
                on_date=cmd.valid_from,
                employee_id=cmd.scope_employee_id,
            )

            if current is not None and current.valid_from == cmd.valid_from:
                raise ConflictError(
                    f"Für diesen Scope und Wochentag existiert bereits eine Version "
                    f"mit valid_from={cmd.valid_from}."
                )

            existing = repo.list_versions(
                weekday=cmd.weekday,
                scope_employee_id=cmd.scope_employee_id,
            )
            if any(v.valid_from > cmd.valid_from for v in existing):
                raise ValidationError(
                    f"Es existiert bereits eine spätere Version für diesen Scope "
                    f"(Wochentag {cmd.weekday}). Rückwärts-Einfügen ist nicht erlaubt."
                )

            superseded_id: int | None = None
            if current is not None:
                repo.close_version(current.id, cmd.valid_from - timedelta(days=1))
                superseded_id = current.id

            new_version = WorkScheduleVersion(
                id=0,
                scope_type=cmd.scope_type,
                scope_employee_id=cmd.scope_employee_id,
                weekday=cmd.weekday,
                start_time=cmd.start_time,
                end_time=cmd.end_time,
                valid_from=cmd.valid_from,
                valid_until=None,
                change_origin=cmd.change_origin,
                changed_by_user_id=cmd.changed_by_user_id,
            )
            saved = repo.add(new_version)

            self._uow.audit_log_repo.add(AuditLogEntry(
                id=0,
                event_type="WORK_SCHEDULE_CHANGED",
                object_type="work_schedule_versions",
                object_id=saved.id,
                user_id=cmd.changed_by_user_id,
                employee_id=None,
                event_at=datetime.now(timezone.utc),
                details_json=json.dumps({
                    "weekday": cmd.weekday,
                    "scope_type": cmd.scope_type,
                    "scope_employee_id": cmd.scope_employee_id,
                    "valid_from": cmd.valid_from.isoformat(),
                    "superseded_version_id": superseded_id,
                    "reason": cmd.reason,
                }),
            ))

            self._uow.commit()
            return WorkScheduleChangeResult(
                new_version_id=saved.id,
                superseded_version_id=superseded_id,
            )
