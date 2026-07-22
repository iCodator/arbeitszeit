"""Use Cases für Benutzerkontenverwaltung (ADMIN-Rolle, Ausnahme: Bootstrap)."""

__version__ = "1.1"

import json
from datetime import datetime, timezone

from arbeitszeit.application.commands import (
    BootstrapAdminCommand,
    ChangeUserRoleCommand,
    CreateUserAccountCommand,
    DeactivateUserAccountCommand,
    ReactivateUserAccountCommand,
)
from arbeitszeit.application.results import BootstrapAdminResult, CreateUserAccountResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry, UserAccount
from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.errors import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from arbeitszeit.domain.value_objects import AuditLogEntryId, UserAccountId

_ALLOWED_ROLES = {UserRole.ADMIN, UserRole.REVIEWER, UserRole.TECH}


class CreateUserAccountUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: CreateUserAccountCommand) -> CreateUserAccountResult:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Benutzerkonten anzulegen."
                )

            if cmd.role not in _ALLOWED_ROLES:
                raise ValidationError(
                    f"Rolle '{cmd.role.value}' ist nicht erlaubt. "
                    f"Erlaubt: {', '.join(r.value for r in _ALLOWED_ROLES)}"
                )

            if self._uow.user_account_repo.get_by_username(cmd.username) is not None:
                raise ConflictError(
                    f"Benutzername '{cmd.username}' ist bereits vergeben."
                )

            now = datetime.now(timezone.utc)
            saved = self._uow.user_account_repo.add(
                UserAccount(
                    id=UserAccountId(0),
                    employee_id=cmd.employee_id,
                    username=cmd.username,
                    role=cmd.role,
                    is_active=True,
                ),
                cmd.password_hash,
            )

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.USER_ACCOUNT_CREATED,
                    object_type="user_accounts",
                    object_id=saved.id,
                    user_id=cmd.acting_user_id,
                    employee_id=None,
                    event_at=now,
                    details_json=json.dumps(
                        {"username": cmd.username, "role": cmd.role.value},
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

            return CreateUserAccountResult(user_id=saved.id)


class DeactivateUserAccountUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: DeactivateUserAccountCommand) -> None:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Benutzerkonten zu deaktivieren."
                )

            target = self._uow.user_account_repo.get_by_id(cmd.target_user_id)
            if target is None:
                raise NotFoundError(f"Benutzerkonto {cmd.target_user_id} nicht gefunden.")

            is_last_admin = target.role == UserRole.ADMIN and not (
                self._uow.user_account_repo.has_other_active_admin(cmd.target_user_id)
            )
            if is_last_admin:
                raise ConflictError(
                    "Das letzte aktive Administratorkonto kann nicht deaktiviert werden."
                )

            now = datetime.now(timezone.utc)
            self._uow.user_account_repo.deactivate(cmd.target_user_id)

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.USER_ACCOUNT_DEACTIVATED,
                    object_type="user_accounts",
                    object_id=cmd.target_user_id,
                    user_id=cmd.acting_user_id,
                    employee_id=None,
                    event_at=now,
                    details_json=json.dumps(
                        {"username": target.username}, ensure_ascii=False, sort_keys=True
                    ),
                )
            )


class ReactivateUserAccountUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: ReactivateUserAccountCommand) -> None:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Benutzerkonten zu reaktivieren."
                )

            target = self._uow.user_account_repo.get_by_id(cmd.target_user_id)
            if target is None:
                raise NotFoundError(f"Benutzerkonto {cmd.target_user_id} nicht gefunden.")

            now = datetime.now(timezone.utc)
            self._uow.user_account_repo.reactivate(cmd.target_user_id)

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.USER_ACCOUNT_REACTIVATED,
                    object_type="user_accounts",
                    object_id=cmd.target_user_id,
                    user_id=cmd.acting_user_id,
                    employee_id=None,
                    event_at=now,
                    details_json=json.dumps(
                        {"username": target.username}, ensure_ascii=False, sort_keys=True
                    ),
                )
            )


class ChangeUserRoleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: ChangeUserRoleCommand) -> None:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Rollen zu ändern."
                )

            if cmd.new_role not in _ALLOWED_ROLES:
                raise ValidationError(
                    f"Rolle '{cmd.new_role.value}' ist nicht erlaubt."
                )

            target = self._uow.user_account_repo.get_by_id(cmd.target_user_id)
            if target is None:
                raise NotFoundError(f"Benutzerkonto {cmd.target_user_id} nicht gefunden.")

            if (
                target.role == UserRole.ADMIN
                and cmd.new_role != UserRole.ADMIN
                and not self._uow.user_account_repo.has_other_active_admin(cmd.target_user_id)
            ):
                raise ConflictError(
                    "Die Rolle des letzten aktiven Administrators kann nicht geändert werden."
                )

            now = datetime.now(timezone.utc)
            self._uow.user_account_repo.set_role(cmd.target_user_id, cmd.new_role)

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.USER_ACCOUNT_ROLE_CHANGED,
                    object_type="user_accounts",
                    object_id=cmd.target_user_id,
                    user_id=cmd.acting_user_id,
                    employee_id=None,
                    event_at=now,
                    details_json=json.dumps(
                        {
                            "username": target.username,
                            "old_role": target.role.value,
                            "new_role": cmd.new_role.value,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )


class BootstrapAdminUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: BootstrapAdminCommand) -> BootstrapAdminResult:
        with self._uow:
            if self._uow.user_account_repo.has_active_admin():
                raise ConflictError(
                    "Es existiert bereits ein aktives Administratorkonto. "
                    "Bootstrap nicht möglich."
                )

            if self._uow.user_account_repo.get_by_username(cmd.username) is not None:
                raise ConflictError(
                    f"Benutzername '{cmd.username}' ist bereits vergeben."
                )

            now = datetime.now(timezone.utc)
            saved = self._uow.user_account_repo.add(
                UserAccount(
                    id=UserAccountId(0),
                    employee_id=None,
                    username=cmd.username,
                    role=UserRole.ADMIN,
                    is_active=True,
                ),
                cmd.password_hash,
            )

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.USER_ACCOUNT_CREATED,
                    object_type="user_accounts",
                    object_id=saved.id,
                    user_id=saved.id,
                    employee_id=None,
                    event_at=now,
                    details_json=json.dumps(
                        {"username": cmd.username, "role": UserRole.ADMIN.value, "bootstrap": True},
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

            return BootstrapAdminResult(user_id=saved.id, username=saved.username)
