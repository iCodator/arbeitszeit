__version__ = "1.1"

import sys
from pathlib import Path
from typing import cast

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import CreateEmployeeCommand, DeactivateEmployeeCommand
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.application.use_cases.manage_employees import (
    CreateEmployeeUseCase,
    DeactivateEmployeeUseCase,
)
from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from arbeitszeit.domain.value_objects import EmployeeId, UserAccountId

from .fakes import FakeUnitOfWork


def _as_uow(uow: FakeUnitOfWork) -> UnitOfWork:
    return cast(UnitOfWork, uow)


def _make_admin(uow: FakeUnitOfWork, username: str = "admin") -> int:
    from arbeitszeit.domain.entities import UserAccount

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


def _make_employee(uow: FakeUnitOfWork, personnel_no: str = "M001") -> int:
    from arbeitszeit.domain.entities import Employee

    emp = uow.employee_repo.add(
        Employee(
            id=EmployeeId(0),
            personnel_no=personnel_no,
            first_name="Anna",
            last_name="Test",
            is_active=True,
        )
    )
    return emp.id


# --- CreateEmployeeUseCase ---

class TestCreateEmployee:
    def test_happy_path_legt_mitarbeiter_an(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        cmd = CreateEmployeeCommand(
            acting_user_id=UserAccountId(admin_id),
            personnel_no="M001",
            first_name="Lisa",
            last_name="Muster",
        )
        result = CreateEmployeeUseCase(_as_uow(uow)).execute(cmd)
        assert result.employee_id > 0
        saved = uow.employee_repo.get_by_id(result.employee_id)
        assert saved is not None
        assert saved.personnel_no == "M001"
        assert saved.is_active is True
        assert uow.committed is True

    def test_audit_log_wird_geschrieben(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        CreateEmployeeUseCase(_as_uow(uow)).execute(
            CreateEmployeeCommand(
                acting_user_id=UserAccountId(admin_id),
                personnel_no="M002",
                first_name="Karl",
                last_name="Muster",
            )
        )
        assert len(uow.audit_log_repo.entries) == 1
        entry = uow.audit_log_repo.entries[0]
        assert entry.event_type == "EMPLOYEE_CREATED"

    def test_wirft_permission_denied_fuer_nicht_admin(self) -> None:
        uow = FakeUnitOfWork()
        from arbeitszeit.domain.entities import UserAccount
        reviewer = uow.user_account_repo.add(
            UserAccount(
                id=UserAccountId(0),
                employee_id=None,
                username="rev",
                role=UserRole.REVIEWER,
                is_active=True,
            )
        )
        with pytest.raises(PermissionDeniedError):
            CreateEmployeeUseCase(_as_uow(uow)).execute(
                CreateEmployeeCommand(
                    acting_user_id=UserAccountId(reviewer.id),
                    personnel_no="M003",
                    first_name="X",
                    last_name="Y",
                )
            )
        assert uow.committed is False

    def test_wirft_conflict_bei_doppelter_personalnummer(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        _make_employee(uow, "M001")
        with pytest.raises(ConflictError):
            CreateEmployeeUseCase(_as_uow(uow)).execute(
                CreateEmployeeCommand(
                    acting_user_id=UserAccountId(admin_id),
                    personnel_no="M001",
                    first_name="X",
                    last_name="Y",
                )
            )
        assert uow.committed is False

    def test_wirft_conflict_bei_reaktivierter_inaktiver_personalnummer(self) -> None:
        """Inaktiver Mitarbeiter mit gleicher Personalnummer darf nicht neu angelegt werden."""
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow, "M001")
        uow.employee_repo.deactivate(emp_id)
        with pytest.raises(ConflictError):
            CreateEmployeeUseCase(_as_uow(uow)).execute(
                CreateEmployeeCommand(
                    acting_user_id=UserAccountId(admin_id),
                    personnel_no="M001",
                    first_name="X",
                    last_name="Y",
                )
            )
        assert uow.committed is False


# --- DeactivateEmployeeUseCase ---

class TestDeactivateEmployee:
    def test_happy_path_deaktiviert_mitarbeiter(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        DeactivateEmployeeUseCase(_as_uow(uow)).execute(
            DeactivateEmployeeCommand(
                acting_user_id=UserAccountId(admin_id),
                employee_id=EmployeeId(emp_id),
            )
        )
        saved = uow.employee_repo.get_by_id(emp_id)
        assert saved is not None
        assert saved.is_active is False
        assert uow.committed is True

    def test_audit_log_wird_geschrieben(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        DeactivateEmployeeUseCase(_as_uow(uow)).execute(
            DeactivateEmployeeCommand(
                acting_user_id=UserAccountId(admin_id),
                employee_id=EmployeeId(emp_id),
            )
        )
        assert len(uow.audit_log_repo.entries) == 1
        assert uow.audit_log_repo.entries[0].event_type == "EMPLOYEE_DEACTIVATED"

    def test_wirft_permission_denied_fuer_nicht_admin(self) -> None:
        uow = FakeUnitOfWork()
        emp_id = _make_employee(uow)
        from arbeitszeit.domain.entities import UserAccount
        tech = uow.user_account_repo.add(
            UserAccount(
                id=UserAccountId(0),
                employee_id=None,
                username="tech",
                role=UserRole.TECH,
                is_active=True,
            )
        )
        with pytest.raises(PermissionDeniedError):
            DeactivateEmployeeUseCase(_as_uow(uow)).execute(
                DeactivateEmployeeCommand(
                    acting_user_id=UserAccountId(tech.id),
                    employee_id=EmployeeId(emp_id),
                )
            )

    def test_wirft_not_found_fuer_unbekannten_mitarbeiter(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        with pytest.raises(NotFoundError):
            DeactivateEmployeeUseCase(_as_uow(uow)).execute(
                DeactivateEmployeeCommand(
                    acting_user_id=UserAccountId(admin_id),
                    employee_id=EmployeeId(9999),
                )
            )
