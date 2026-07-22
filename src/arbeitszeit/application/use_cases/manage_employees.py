"""Use Cases für Mitarbeiterverwaltung (ADMIN-Rolle erforderlich)."""

__version__ = "1.1"

import json
from datetime import datetime, timezone

from arbeitszeit.application.commands import CreateEmployeeCommand, DeactivateEmployeeCommand
from arbeitszeit.application.results import CreateEmployeeResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry, Employee
from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from arbeitszeit.domain.value_objects import AuditLogEntryId, EmployeeId


class CreateEmployeeUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: CreateEmployeeCommand) -> CreateEmployeeResult:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Mitarbeiter anzulegen."
                )

            if self._uow.employee_repo.get_by_personnel_no(cmd.personnel_no) is not None:
                raise ConflictError(
                    f"Personalnummer '{cmd.personnel_no}' ist bereits vergeben "
                    "(aktiv oder inaktiv)."
                )

            now = datetime.now(timezone.utc)
            saved = self._uow.employee_repo.add(
                Employee(
                    id=EmployeeId(0),
                    personnel_no=cmd.personnel_no,
                    first_name=cmd.first_name,
                    last_name=cmd.last_name,
                    is_active=True,
                )
            )

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.EMPLOYEE_CREATED,
                    object_type="employees",
                    object_id=saved.id,
                    user_id=cmd.acting_user_id,
                    employee_id=saved.id,
                    event_at=now,
                    details_json=json.dumps(
                        {
                            "personnel_no": cmd.personnel_no,
                            "first_name": cmd.first_name,
                            "last_name": cmd.last_name,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

            return CreateEmployeeResult(employee_id=saved.id)


class DeactivateEmployeeUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: DeactivateEmployeeCommand) -> None:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Mitarbeiter zu deaktivieren."
                )

            employee = self._uow.employee_repo.get_by_id(cmd.employee_id)
            if employee is None:
                raise NotFoundError(f"Mitarbeiter {cmd.employee_id} nicht gefunden.")

            now = datetime.now(timezone.utc)
            self._uow.employee_repo.deactivate(cmd.employee_id)

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.EMPLOYEE_DEACTIVATED,
                    object_type="employees",
                    object_id=cmd.employee_id,
                    user_id=cmd.acting_user_id,
                    employee_id=cmd.employee_id,
                    event_at=now,
                    details_json=json.dumps({}, ensure_ascii=False),
                )
            )
