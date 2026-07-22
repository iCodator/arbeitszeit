__version__ = "1.1"

import sys
from pathlib import Path
from typing import cast

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import (
    BootstrapAdminCommand,
    ChangeUserRoleCommand,
    CreateUserAccountCommand,
    DeactivateUserAccountCommand,
    ReactivateUserAccountCommand,
)
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.application.use_cases.manage_user_accounts import (
    BootstrapAdminUseCase,
    ChangeUserRoleUseCase,
    CreateUserAccountUseCase,
    DeactivateUserAccountUseCase,
    ReactivateUserAccountUseCase,
)
from arbeitszeit.domain.entities import UserAccount
from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from arbeitszeit.domain.value_objects import UserAccountId

from .fakes import FakeUnitOfWork


def _as_uow(uow: FakeUnitOfWork) -> UnitOfWork:
    return cast(UnitOfWork, uow)


def _make_admin(uow: FakeUnitOfWork, username: str = "admin") -> int:
    acct = uow.user_account_repo.add(
        UserAccount(
            id=UserAccountId(0),
            employee_id=None,
            username=username,
            role=UserRole.ADMIN,
            is_active=True,
        )
    )
    return acct.id


def _make_user(uow: FakeUnitOfWork, username: str, role: UserRole = UserRole.REVIEWER) -> int:
    acct = uow.user_account_repo.add(
        UserAccount(
            id=UserAccountId(0),
            employee_id=None,
            username=username,
            role=role,
            is_active=True,
        )
    )
    return acct.id


# --- CreateUserAccountUseCase ---

class TestCreateUserAccount:
    def test_happy_path_legt_konto_an(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        result = CreateUserAccountUseCase(_as_uow(uow)).execute(
            CreateUserAccountCommand(
                acting_user_id=UserAccountId(admin_id),
                username="newuser",
                password_hash="hash",
                role=UserRole.REVIEWER,
            )
        )
        assert result.user_id > 0
        saved = uow.user_account_repo.get_by_id(result.user_id)
        assert saved is not None
        assert saved.username == "newuser"
        assert saved.role == UserRole.REVIEWER
        assert uow.committed is True

    def test_audit_log_wird_geschrieben(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        CreateUserAccountUseCase(_as_uow(uow)).execute(
            CreateUserAccountCommand(
                acting_user_id=UserAccountId(admin_id),
                username="u2",
                password_hash="h",
                role=UserRole.TECH,
            )
        )
        assert len(uow.audit_log_repo.entries) == 1
        assert uow.audit_log_repo.entries[0].event_type == "USER_ACCOUNT_CREATED"

    def test_wirft_permission_denied_fuer_nicht_admin(self) -> None:
        uow = FakeUnitOfWork()
        reviewer_id = _make_user(uow, "rev")
        with pytest.raises(PermissionDeniedError):
            CreateUserAccountUseCase(_as_uow(uow)).execute(
                CreateUserAccountCommand(
                    acting_user_id=UserAccountId(reviewer_id),
                    username="x",
                    password_hash="h",
                    role=UserRole.REVIEWER,
                )
            )

    def test_wirft_conflict_bei_doppeltem_benutzernamen(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        _make_user(uow, "dupe")
        with pytest.raises(ConflictError):
            CreateUserAccountUseCase(_as_uow(uow)).execute(
                CreateUserAccountCommand(
                    acting_user_id=UserAccountId(admin_id),
                    username="dupe",
                    password_hash="h",
                    role=UserRole.REVIEWER,
                )
            )


# --- DeactivateUserAccountUseCase ---

class TestDeactivateUserAccount:
    def test_happy_path(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        target_id = _make_user(uow, "target")
        DeactivateUserAccountUseCase(_as_uow(uow)).execute(
            DeactivateUserAccountCommand(
                acting_user_id=UserAccountId(admin_id),
                target_user_id=UserAccountId(target_id),
            )
        )
        saved = uow.user_account_repo.get_by_id(target_id)
        assert saved is not None
        assert saved.is_active is False
        assert uow.committed is True

    def test_audit_log(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        target_id = _make_user(uow, "target")
        DeactivateUserAccountUseCase(_as_uow(uow)).execute(
            DeactivateUserAccountCommand(
                acting_user_id=UserAccountId(admin_id),
                target_user_id=UserAccountId(target_id),
            )
        )
        assert uow.audit_log_repo.entries[0].event_type == "USER_ACCOUNT_DEACTIVATED"

    def test_wirft_not_found(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        with pytest.raises(NotFoundError):
            DeactivateUserAccountUseCase(_as_uow(uow)).execute(
                DeactivateUserAccountCommand(
                    acting_user_id=UserAccountId(admin_id),
                    target_user_id=UserAccountId(9999),
                )
            )

    def test_wirft_conflict_beim_deaktivieren_des_letzten_admins(self) -> None:
        """Letzter aktiver Admin darf nicht deaktiviert werden."""
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        with pytest.raises(ConflictError):
            DeactivateUserAccountUseCase(_as_uow(uow)).execute(
                DeactivateUserAccountCommand(
                    acting_user_id=UserAccountId(admin_id),
                    target_user_id=UserAccountId(admin_id),
                )
            )
        assert uow.committed is False

    def test_kein_conflict_wenn_zweiter_admin_vorhanden(self) -> None:
        """Deaktivierung eines Admins ist erlaubt, wenn ein weiterer aktiver Admin existiert."""
        uow = FakeUnitOfWork()
        admin1_id = _make_admin(uow, "admin1")
        admin2_id = _make_admin(uow, "admin2")
        DeactivateUserAccountUseCase(_as_uow(uow)).execute(
            DeactivateUserAccountCommand(
                acting_user_id=UserAccountId(admin1_id),
                target_user_id=UserAccountId(admin2_id),
            )
        )
        assert uow.committed is True


# --- ReactivateUserAccountUseCase ---

class TestReactivateUserAccount:
    def test_happy_path(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        target_id = _make_user(uow, "target")
        uow.user_account_repo.deactivate(target_id)
        ReactivateUserAccountUseCase(_as_uow(uow)).execute(
            ReactivateUserAccountCommand(
                acting_user_id=UserAccountId(admin_id),
                target_user_id=UserAccountId(target_id),
            )
        )
        saved = uow.user_account_repo.get_by_id(target_id)
        assert saved is not None
        assert saved.is_active is True

    def test_audit_log(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        target_id = _make_user(uow, "target")
        uow.user_account_repo.deactivate(target_id)
        ReactivateUserAccountUseCase(_as_uow(uow)).execute(
            ReactivateUserAccountCommand(
                acting_user_id=UserAccountId(admin_id),
                target_user_id=UserAccountId(target_id),
            )
        )
        assert uow.audit_log_repo.entries[0].event_type == "USER_ACCOUNT_REACTIVATED"


# --- ChangeUserRoleUseCase ---

class TestChangeUserRole:
    def test_happy_path(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        target_id = _make_user(uow, "target", UserRole.REVIEWER)
        ChangeUserRoleUseCase(_as_uow(uow)).execute(
            ChangeUserRoleCommand(
                acting_user_id=UserAccountId(admin_id),
                target_user_id=UserAccountId(target_id),
                new_role=UserRole.TECH,
            )
        )
        saved = uow.user_account_repo.get_by_id(target_id)
        assert saved is not None
        assert saved.role == UserRole.TECH
        assert uow.committed is True

    def test_audit_log(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        target_id = _make_user(uow, "target")
        ChangeUserRoleUseCase(_as_uow(uow)).execute(
            ChangeUserRoleCommand(
                acting_user_id=UserAccountId(admin_id),
                target_user_id=UserAccountId(target_id),
                new_role=UserRole.TECH,
            )
        )
        entry = uow.audit_log_repo.entries[0]
        assert entry.event_type == "USER_ACCOUNT_ROLE_CHANGED"

    def test_wirft_not_found(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        with pytest.raises(NotFoundError):
            ChangeUserRoleUseCase(_as_uow(uow)).execute(
                ChangeUserRoleCommand(
                    acting_user_id=UserAccountId(admin_id),
                    target_user_id=UserAccountId(9999),
                    new_role=UserRole.TECH,
                )
            )

    def test_wirft_conflict_beim_degradieren_des_letzten_admins(self) -> None:
        """Rollenwechsel weg von ADMIN ist verboten, wenn kein anderer aktiver Admin existiert."""
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        with pytest.raises(ConflictError):
            ChangeUserRoleUseCase(_as_uow(uow)).execute(
                ChangeUserRoleCommand(
                    acting_user_id=UserAccountId(admin_id),
                    target_user_id=UserAccountId(admin_id),
                    new_role=UserRole.REVIEWER,
                )
            )
        assert uow.committed is False

    def test_kein_conflict_wenn_zweiter_admin_bei_rollenwechsel(self) -> None:
        """Rollenwechsel eines Admins ist erlaubt, wenn ein weiterer aktiver Admin existiert."""
        uow = FakeUnitOfWork()
        admin1_id = _make_admin(uow, "admin1")
        admin2_id = _make_admin(uow, "admin2")
        ChangeUserRoleUseCase(_as_uow(uow)).execute(
            ChangeUserRoleCommand(
                acting_user_id=UserAccountId(admin1_id),
                target_user_id=UserAccountId(admin2_id),
                new_role=UserRole.REVIEWER,
            )
        )
        assert uow.committed is True


# --- BootstrapAdminUseCase ---

class TestBootstrapAdmin:
    def test_happy_path_legt_ersten_admin_an(self) -> None:
        uow = FakeUnitOfWork()
        result = BootstrapAdminUseCase(_as_uow(uow)).execute(
            BootstrapAdminCommand(username="firstadmin", password_hash="hash")
        )
        assert result.user_id > 0
        assert result.username == "firstadmin"
        saved = uow.user_account_repo.get_by_id(result.user_id)
        assert saved is not None
        assert saved.role == UserRole.ADMIN
        assert uow.committed is True

    def test_audit_log(self) -> None:
        uow = FakeUnitOfWork()
        BootstrapAdminUseCase(_as_uow(uow)).execute(
            BootstrapAdminCommand(username="firstadmin", password_hash="hash")
        )
        assert uow.audit_log_repo.entries[0].event_type == "USER_ACCOUNT_CREATED"

    def test_wirft_conflict_wenn_admin_existiert(self) -> None:
        uow = FakeUnitOfWork()
        _make_admin(uow)
        with pytest.raises(ConflictError):
            BootstrapAdminUseCase(_as_uow(uow)).execute(
                BootstrapAdminCommand(username="secondadmin", password_hash="hash")
            )
        assert uow.committed is False

    def test_wirft_conflict_bei_doppeltem_benutzernamen(self) -> None:
        uow = FakeUnitOfWork()
        _make_user(uow, "taken", UserRole.REVIEWER)
        with pytest.raises(ConflictError):
            BootstrapAdminUseCase(_as_uow(uow)).execute(
                BootstrapAdminCommand(username="taken", password_hash="hash")
            )
