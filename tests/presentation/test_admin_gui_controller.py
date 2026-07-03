import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.entities import Employee, RfidCard, UserAccount
from arbeitszeit.domain.enums import CardStatus, UserRole
from arbeitszeit.domain.errors import ConflictError, NotFoundError
from arbeitszeit.domain.value_objects import EmployeeId, RfidCardId, UserAccountId
from arbeitszeit.presentation.admin_gui.controller import (
    assign_rfid_card,
    bootstrap_admin,
    change_user_role,
    create_employee,
    create_user_account,
    deactivate_employee,
    deactivate_rfid_card,
    deactivate_user_account,
    reactivate_user_account,
    replace_rfid_card,
)

sys.path.insert(0, str(Path(__file__).parents[1]))
from application.fakes import FakeUnitOfWork

# ─────────────────────────────────────────────────────────────────────────────
# Hilfsfunktionen
# ─────────────────────────────────────────────────────────────────────────────

def _admin(uow: FakeUnitOfWork, username: str = "admin") -> int:
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


def _employee(uow: FakeUnitOfWork, personnel_no: str = "M001") -> int:
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


def _card(uow: FakeUnitOfWork, employee_id: int, uid_hash: str = "abc123") -> int:
    from datetime import date
    card = uow.rfid_card_repo.add(
        RfidCard(
            id=RfidCardId(0),
            employee_id=employee_id,
            uid_hash=uid_hash,
            status=CardStatus.ACTIVE,
            valid_from=date.today(),
            valid_until=None,
            replaced_by_card_id=None,
        )
    )
    return card.id


# ─────────────────────────────────────────────────────────────────────────────
# create_employee
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateEmployee:
    def test_legt_mitarbeiter_an(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        result = create_employee(uow, admin_id, "M001", "Lisa", "Muster")
        assert result.employee_id > 0
        emp = uow.employee_repo.get_by_id(result.employee_id)
        assert emp is not None
        assert emp.personnel_no == "M001"
        assert emp.is_active is True

    def test_wirft_conflict_bei_duplikat_personalnummer(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        create_employee(uow, admin_id, "M001", "Anna", "Eins")
        uow2 = FakeUnitOfWork()
        uow2.user_account_repo.add(
            UserAccount(
                id=UserAccountId(0),
                employee_id=None,
                username="admin",
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        uow2.employee_repo.add(
            Employee(
                id=EmployeeId(0),
                personnel_no="M001",
                first_name="Anna",
                last_name="Eins",
                is_active=True,
            )
        )
        with pytest.raises(ConflictError):
            create_employee(uow2, 1, "M001", "Berta", "Zwei")


# ─────────────────────────────────────────────────────────────────────────────
# deactivate_employee
# ─────────────────────────────────────────────────────────────────────────────

class TestDeactivateEmployee:
    def test_deaktiviert_mitarbeiter(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        emp_id = _employee(uow)
        deactivate_employee(uow, admin_id, emp_id)
        emp = uow.employee_repo.get_by_id(emp_id)
        assert emp is not None
        assert emp.is_active is False

    def test_wirft_not_found_bei_unbekannter_id(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        with pytest.raises(NotFoundError):
            deactivate_employee(uow, admin_id, 9999)


# ─────────────────────────────────────────────────────────────────────────────
# assign_rfid_card
# ─────────────────────────────────────────────────────────────────────────────

class TestAssignRfidCard:
    def test_weist_karte_zu(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        emp_id = _employee(uow)
        result = assign_rfid_card(uow, admin_id, emp_id, "hashXYZ")
        assert result.card_id > 0
        card = uow.rfid_card_repo.get_by_id(result.card_id)
        assert card is not None
        assert card.uid_hash == "hashXYZ"
        assert card.status == CardStatus.ACTIVE

    def test_wirft_not_found_bei_unbekanntem_mitarbeiter(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        with pytest.raises(NotFoundError):
            assign_rfid_card(uow, admin_id, 9999, "hashXYZ")


# ─────────────────────────────────────────────────────────────────────────────
# replace_rfid_card
# ─────────────────────────────────────────────────────────────────────────────

class TestReplaceRfidCard:
    def test_ersetzt_karte(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        emp_id = _employee(uow)
        old_id = _card(uow, emp_id, "oldHash")
        result = replace_rfid_card(uow, admin_id, old_id, "newHash")
        assert result.new_card_id > 0
        assert result.new_card_id != old_id
        new_card = uow.rfid_card_repo.get_by_id(result.new_card_id)
        assert new_card is not None
        assert new_card.uid_hash == "newHash"

    def test_wirft_not_found_bei_unbekannter_alter_karte(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        with pytest.raises(NotFoundError):
            replace_rfid_card(uow, admin_id, 9999, "newHash")


# ─────────────────────────────────────────────────────────────────────────────
# deactivate_rfid_card
# ─────────────────────────────────────────────────────────────────────────────

class TestDeactivateRfidCard:
    def test_deaktiviert_karte(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        emp_id = _employee(uow)
        card_id = _card(uow, emp_id)
        deactivate_rfid_card(uow, admin_id, card_id)
        card = uow.rfid_card_repo.get_by_id(card_id)
        assert card is not None
        assert card.status == CardStatus.INACTIVE

    def test_wirft_not_found_bei_unbekannter_karte(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        with pytest.raises(NotFoundError):
            deactivate_rfid_card(uow, admin_id, 9999)


# ─────────────────────────────────────────────────────────────────────────────
# create_user_account
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateUserAccount:
    def test_legt_konto_ohne_mitarbeiter_id_an(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        result = create_user_account(uow, admin_id, "reviewer1", "hash", UserRole.REVIEWER)
        assert result.user_id > 0
        acct = uow.user_account_repo.get_by_id(result.user_id)
        assert acct is not None
        assert acct.username == "reviewer1"
        assert acct.role == UserRole.REVIEWER

    def test_legt_konto_mit_mitarbeiter_id_an(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        emp_id = _employee(uow)
        result = create_user_account(uow, admin_id, "emp_user", "hash", UserRole.REVIEWER, emp_id)
        acct = uow.user_account_repo.get_by_id(result.user_id)
        assert acct is not None
        assert acct.employee_id == emp_id

    def test_wirft_conflict_bei_duplikat_username(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        create_user_account(uow, admin_id, "duplikat", "hash", UserRole.REVIEWER)
        with pytest.raises(ConflictError):
            create_user_account(uow, admin_id, "duplikat", "hash2", UserRole.TECH)


# ─────────────────────────────────────────────────────────────────────────────
# bootstrap_admin
# ─────────────────────────────────────────────────────────────────────────────

class TestBootstrapAdmin:
    def test_legt_ersten_admin_an(self):
        uow = FakeUnitOfWork()
        result = bootstrap_admin(uow, "erster_admin", "pw_hash")
        assert result.user_id > 0
        assert result.username == "erster_admin"
        assert uow.user_account_repo.has_active_admin() is True

    def test_wirft_conflict_wenn_admin_bereits_existiert(self):
        uow = FakeUnitOfWork()
        bootstrap_admin(uow, "erster_admin", "pw_hash")
        uow2 = FakeUnitOfWork()
        uow2.user_account_repo.add(
            UserAccount(
                id=UserAccountId(0),
                employee_id=None,
                username="admin",
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        with pytest.raises(ConflictError):
            bootstrap_admin(uow2, "zweiter_admin", "pw_hash")


# ─────────────────────────────────────────────────────────────────────────────
# deactivate_user_account
# ─────────────────────────────────────────────────────────────────────────────

class TestDeactivateUserAccount:
    def test_deaktiviert_konto(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        target = uow.user_account_repo.add(
            UserAccount(
                id=UserAccountId(0),
                employee_id=None,
                username="reviewer",
                role=UserRole.REVIEWER,
                is_active=True,
            )
        )
        deactivate_user_account(uow, admin_id, target.id)
        acct = uow.user_account_repo.get_by_id(target.id)
        assert acct is not None
        assert acct.is_active is False

    def test_wirft_not_found_bei_unbekannter_id(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        with pytest.raises(NotFoundError):
            deactivate_user_account(uow, admin_id, 9999)


# ─────────────────────────────────────────────────────────────────────────────
# reactivate_user_account
# ─────────────────────────────────────────────────────────────────────────────

class TestReactivateUserAccount:
    def test_reaktiviert_deaktiviertes_konto(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        target = uow.user_account_repo.add(
            UserAccount(
                id=UserAccountId(0),
                employee_id=None,
                username="reviewer",
                role=UserRole.REVIEWER,
                is_active=False,
            )
        )
        reactivate_user_account(uow, admin_id, target.id)
        acct = uow.user_account_repo.get_by_id(target.id)
        assert acct is not None
        assert acct.is_active is True

    def test_wirft_not_found_bei_unbekannter_id(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        with pytest.raises(NotFoundError):
            reactivate_user_account(uow, admin_id, 9999)


# ─────────────────────────────────────────────────────────────────────────────
# change_user_role
# ─────────────────────────────────────────────────────────────────────────────

class TestChangeUserRole:
    def test_aendert_rolle_auf_tech(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        target = uow.user_account_repo.add(
            UserAccount(
                id=UserAccountId(0),
                employee_id=None,
                username="reviewer",
                role=UserRole.REVIEWER,
                is_active=True,
            )
        )
        change_user_role(uow, admin_id, target.id, UserRole.TECH)
        acct = uow.user_account_repo.get_by_id(target.id)
        assert acct is not None
        assert acct.role == UserRole.TECH

    def test_wirft_not_found_bei_unbekannter_id(self):
        uow = FakeUnitOfWork()
        admin_id = _admin(uow)
        with pytest.raises(NotFoundError):
            change_user_role(uow, admin_id, 9999, UserRole.TECH)
