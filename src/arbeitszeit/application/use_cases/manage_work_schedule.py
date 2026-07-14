__version__ = "1.0"

import json
from datetime import datetime, timedelta, timezone

from arbeitszeit.application.commands import ChangeWorkScheduleCommand
from arbeitszeit.application.results import WorkScheduleChangeResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry, WorkScheduleVersion
from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.errors import (
    ConflictError,
    PermissionDeniedError,
    ValidationError,
)
from arbeitszeit.domain.value_objects import (
    AuditLogEntryId,
    WorkScheduleVersionId,
)


class ManageWorkScheduleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: ChangeWorkScheduleCommand) -> WorkScheduleChangeResult:
        with self._uow:
            self._check_permission(cmd)
            repo = self._uow.work_schedule_repo

            current = repo.get_effective(
                weekday=cmd.weekday,
                on_date=cmd.valid_from,
                employee_id=cmd.scope_employee_id,
            )
            self._validate_no_conflict(cmd, current)

            superseded_id: WorkScheduleVersionId | None = None
            if current is not None:
                repo.close_version(current.id, cmd.valid_from - timedelta(days=1))
                superseded_id = current.id

            new_version = WorkScheduleVersion(
                id=WorkScheduleVersionId(0),
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

            # Erst commit, dann Audit-Log schreiben (siehe BookUseCase für Begründung).
            self._uow.commit()

            self._write_audit(cmd, saved, current, superseded_id)

            return WorkScheduleChangeResult(
                new_version_id=saved.id,
                superseded_version_id=superseded_id,
            )

    def _check_permission(self, cmd: ChangeWorkScheduleCommand) -> None:
        if cmd.changed_by_user_id is None:
            raise PermissionDeniedError(
                "Regelarbeitszeitänderungen erfordern einen authentifizierten Benutzer."
            )
        actor = self._uow.user_account_repo.get_by_id(cmd.changed_by_user_id)
        if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
            raise PermissionDeniedError(
                f"Benutzer {cmd.changed_by_user_id} ist nicht berechtigt, "
                "Regelarbeitszeiten zu ändern (nur ADMIN)."
            )

    def _validate_no_conflict(
        self,
        cmd: ChangeWorkScheduleCommand,
        current: WorkScheduleVersion | None,
    ) -> None:
        if current is not None and current.valid_from == cmd.valid_from:
            raise ConflictError(
                f"Für diesen Scope und Wochentag existiert bereits eine Version "
                f"mit valid_from={cmd.valid_from}."
            )
        existing = self._uow.work_schedule_repo.list_versions(
            weekday=cmd.weekday,
            scope_employee_id=cmd.scope_employee_id,
        )
        if any(v.valid_from > cmd.valid_from for v in existing):
            raise ValidationError(
                f"Es existiert bereits eine spätere Version für diesen Scope "
                f"(Wochentag {cmd.weekday}). Rückwärts-Einfügen ist nicht erlaubt."
            )

    def _write_audit(
        self,
        cmd: ChangeWorkScheduleCommand,
        saved: WorkScheduleVersion,
        current: WorkScheduleVersion | None,
        superseded_id: WorkScheduleVersionId | None,
    ) -> None:
        self._uow.audit_log_repo.add(
            AuditLogEntry(
                id=AuditLogEntryId(0),
                event_type=audit_events.WORK_SCHEDULE_CHANGED,
                object_type="work_schedule_versions",
                object_id=saved.id,
                user_id=cmd.changed_by_user_id,
                employee_id=None,
                event_at=datetime.now(timezone.utc),
                details_json=json.dumps(
                    {
                        "weekday": cmd.weekday,
                        "scope_type": cmd.scope_type.value,
                        "scope_employee_id": cmd.scope_employee_id,
                        "start_time": cmd.start_time.isoformat(timespec="minutes"),
                        "end_time": cmd.end_time.isoformat(timespec="minutes"),
                        "valid_from": cmd.valid_from.isoformat(),
                        "change_origin": cmd.change_origin.value,
                        "superseded_version_id": superseded_id,
                        "previous_valid_from": (
                            current.valid_from.isoformat() if current is not None else None
                        ),
                        "previous_start_time": (
                            current.start_time.isoformat(timespec="minutes")
                            if current is not None
                            else None
                        ),
                        "previous_end_time": (
                            current.end_time.isoformat(timespec="minutes")
                            if current is not None
                            else None
                        ),
                        "reason": cmd.reason,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            )
        )
