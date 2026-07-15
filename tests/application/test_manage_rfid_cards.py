import sys
from datetime import date
from pathlib import Path
from typing import cast

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import (
    AssignRfidCardCommand,
    DeactivateRfidCardCommand,
    ReplaceRfidCardCommand,
)
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.application.use_cases.manage_rfid_cards import (
    AssignRfidCardUseCase,
    DeactivateRfidCardUseCase,
    ReplaceRfidCardUseCase,
)
from arbeitszeit.domain.entities import Employee, RfidCard, UserAccount
from arbeitszeit.domain.enums import CardStatus, UserRole
from arbeitszeit.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from arbeitszeit.domain.value_objects import EmployeeId, RfidCardId, UserAccountId

from .fakes import FakeUnitOfWork


def _as_uow(uow: FakeUnitOfWork) -> UnitOfWork:
    return cast(UnitOfWork, uow)


def _make_admin(uow: FakeUnitOfWork) -> int:
    acct = uow.user_account_repo.add(
        UserAccount(
            id=UserAccountId(0),
            employee_id=None,
            username="admin",
            role=UserRole.ADMIN,
            is_active=True,
        )
    )
    return acct.id


def _make_employee(uow: FakeUnitOfWork) -> int:
    emp = uow.employee_repo.add(
        Employee(
            id=EmployeeId(0),
            personnel_no="M001",
            first_name="A",
            last_name="B",
            is_active=True,
        )
    )
    return emp.id


def _make_card(uow: FakeUnitOfWork, employee_id: int, uid_hash: str = "abc123") -> int:
    card = uow.rfid_card_repo.add(
        RfidCard(
            id=RfidCardId(0),
            uid_hash=uid_hash,
            employee_id=EmployeeId(employee_id),
            status=CardStatus.ACTIVE,
            valid_from=date(2026, 1, 1),
            valid_until=None,
            replaced_by_card_id=None,
        )
    )
    return card.id


# --- AssignRfidCardUseCase ---

class TestAssignRfidCard:
    def test_happy_path_weist_karte_zu(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        result = AssignRfidCardUseCase(_as_uow(uow)).execute(
            AssignRfidCardCommand(
                acting_user_id=UserAccountId(admin_id),
                employee_id=EmployeeId(emp_id),
                uid_hash="newhash",
            )
        )
        assert result.card_id > 0
        card = uow.rfid_card_repo.get_by_id(result.card_id)
        assert card is not None
        assert card.status == CardStatus.ACTIVE
        assert uow.committed is True

    def test_audit_log_card_assigned(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        AssignRfidCardUseCase(_as_uow(uow)).execute(
            AssignRfidCardCommand(
                acting_user_id=UserAccountId(admin_id),
                employee_id=EmployeeId(emp_id),
                uid_hash="newhash",
            )
        )
        assert len(uow.audit_log_repo.entries) == 1
        assert uow.audit_log_repo.entries[0].event_type == "CARD_ASSIGNED"

    def test_wirft_permission_denied(self) -> None:
        uow = FakeUnitOfWork()
        emp_id = _make_employee(uow)
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
            AssignRfidCardUseCase(_as_uow(uow)).execute(
                AssignRfidCardCommand(
                    acting_user_id=UserAccountId(reviewer.id),
                    employee_id=EmployeeId(emp_id),
                    uid_hash="x",
                )
            )

    def test_wirft_not_found_fuer_unbekannten_mitarbeiter(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        with pytest.raises(NotFoundError):
            AssignRfidCardUseCase(_as_uow(uow)).execute(
                AssignRfidCardCommand(
                    acting_user_id=UserAccountId(admin_id),
                    employee_id=EmployeeId(9999),
                    uid_hash="x",
                )
            )

    def test_wirft_conflict_bei_doppeltem_uid_hash(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        _make_card(uow, emp_id, uid_hash="existing")
        with pytest.raises(ConflictError):
            AssignRfidCardUseCase(_as_uow(uow)).execute(
                AssignRfidCardCommand(
                    acting_user_id=UserAccountId(admin_id),
                    employee_id=EmployeeId(emp_id),
                    uid_hash="existing",
                )
            )


# --- ReplaceRfidCardUseCase ---

class TestReplaceRfidCard:
    def test_happy_path_ersetzt_karte(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        old_id = _make_card(uow, emp_id, "oldhash")
        result = ReplaceRfidCardUseCase(_as_uow(uow)).execute(
            ReplaceRfidCardCommand(
                acting_user_id=UserAccountId(admin_id),
                old_card_id=RfidCardId(old_id),
                uid_hash="newhash",
            )
        )
        assert result.new_card_id > 0
        old = uow.rfid_card_repo.get_by_id(old_id)
        assert old is not None
        assert old.status == CardStatus.REPLACED
        assert old.replaced_by_card_id == result.new_card_id
        assert uow.committed is True

    def test_audit_log_card_replaced(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        old_id = _make_card(uow, emp_id, "oldhash")
        ReplaceRfidCardUseCase(_as_uow(uow)).execute(
            ReplaceRfidCardCommand(
                acting_user_id=UserAccountId(admin_id),
                old_card_id=RfidCardId(old_id),
                uid_hash="newhash",
            )
        )
        assert len(uow.audit_log_repo.entries) == 1
        assert uow.audit_log_repo.entries[0].event_type == "CARD_REPLACED"

    def test_wirft_not_found_fuer_unbekannte_alte_karte(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        with pytest.raises(NotFoundError):
            ReplaceRfidCardUseCase(_as_uow(uow)).execute(
                ReplaceRfidCardCommand(
                    acting_user_id=UserAccountId(admin_id),
                    old_card_id=RfidCardId(9999),
                    uid_hash="newhash",
                )
            )

    def test_wirft_conflict_bei_doppeltem_uid_hash(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        old_id = _make_card(uow, emp_id, "oldhash")
        _make_card(uow, emp_id, "existing")
        with pytest.raises(ConflictError):
            ReplaceRfidCardUseCase(_as_uow(uow)).execute(
                ReplaceRfidCardCommand(
                    acting_user_id=UserAccountId(admin_id),
                    old_card_id=RfidCardId(old_id),
                    uid_hash="existing",
                )
            )


# --- DeactivateRfidCardUseCase ---

class TestDeactivateRfidCard:
    def test_happy_path_deaktiviert_karte(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        card_id = _make_card(uow, emp_id)
        DeactivateRfidCardUseCase(_as_uow(uow)).execute(
            DeactivateRfidCardCommand(
                acting_user_id=UserAccountId(admin_id),
                card_id=RfidCardId(card_id),
            )
        )
        card = uow.rfid_card_repo.get_by_id(card_id)
        assert card is not None
        assert card.status == CardStatus.INACTIVE
        assert uow.committed is True

    def test_audit_log_card_deactivated(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        emp_id = _make_employee(uow)
        card_id = _make_card(uow, emp_id)
        DeactivateRfidCardUseCase(_as_uow(uow)).execute(
            DeactivateRfidCardCommand(
                acting_user_id=UserAccountId(admin_id),
                card_id=RfidCardId(card_id),
            )
        )
        assert uow.audit_log_repo.entries[0].event_type == "CARD_DEACTIVATED"

    def test_wirft_not_found_fuer_unbekannte_karte(self) -> None:
        uow = FakeUnitOfWork()
        admin_id = _make_admin(uow)
        with pytest.raises(NotFoundError):
            DeactivateRfidCardUseCase(_as_uow(uow)).execute(
                DeactivateRfidCardCommand(
                    acting_user_id=UserAccountId(admin_id),
                    card_id=RfidCardId(9999),
                )
            )
