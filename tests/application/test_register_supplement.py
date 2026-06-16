import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
from arbeitszeit.application.commands import CreateSupplementCommand
from arbeitszeit.application.use_cases.register_supplement import (
    RegisterSupplementUseCase,
)
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import Employee, TimeBooking, UserAccount
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseStatus,
    UserRole,
)
from arbeitszeit.domain.errors import (
    InactiveEmployeeError,
    NotFoundError,
    PermissionDeniedError,
)
from tests.application.fakes import FakeUnitOfWork

_NOW = datetime(2025, 3, 10, 9, 0, tzinfo=timezone.utc)
_ACTOR_ID = 1  # id des REVIEWER-UserAccounts (erstes Element im Fake-Store)


def _make_uow_with_employee(employee_active: bool = True) -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    uow.user_account_repo.add(
        UserAccount(
            id=0,
            employee_id=None,
            username="reviewer",
            role=UserRole.REVIEWER,
            is_active=True,
        )
    )
    uow.employee_repo.add(
        Employee(
            id=0,
            personnel_no="E001",
            first_name="Anna",
            last_name="Muster",
            is_active=employee_active,
        )
    )
    return uow


def _uow_with_actor() -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    uow.user_account_repo.add(
        UserAccount(
            id=0,
            employee_id=None,
            username="reviewer",
            role=UserRole.REVIEWER,
            is_active=True,
        )
    )
    return uow


def _cmd(**overrides) -> CreateSupplementCommand:
    defaults = dict(
        employee_id=1,
        related_booking_id=None,
        booking_type=BookingType.COME,
        event_at=_NOW,
        recorded_at=_NOW,
        reason="Vergessen einzustempeln",
        recorded_by_user_id=_ACTOR_ID,
    )
    return CreateSupplementCommand(**{**defaults, **overrides})


# --- Rollenprüfung ---


def test_unbekannter_benutzer_loest_permission_denied():
    uow = FakeUnitOfWork()
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(recorded_by_user_id=999))


def test_benutzer_ohne_reviewer_rolle_loest_permission_denied():
    uow = FakeUnitOfWork()
    emp_user = uow.user_account_repo.add(
        UserAccount(
            id=0,
            employee_id=None,
            username="emp",
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
    )
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(recorded_by_user_id=emp_user.id))


def test_inaktiver_benutzer_loest_permission_denied():
    uow = FakeUnitOfWork()
    inactive = uow.user_account_repo.add(
        UserAccount(
            id=0,
            employee_id=None,
            username="inactive_reviewer",
            role=UserRole.REVIEWER,
            is_active=False,
        )
    )
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(recorded_by_user_id=inactive.id))


# --- Fehlerbehandlung ---


def test_unbekannter_mitarbeiter_loest_not_found_error():
    uow = _uow_with_actor()
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(employee_id=99))


def test_inaktiver_mitarbeiter_loest_inactive_employee_error():
    uow = _make_uow_with_employee(employee_active=False)
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd(employee_id=1))


def test_nachtrag_wird_angelegt():
    uow = _make_uow_with_employee()
    uc = RegisterSupplementUseCase(uow)

    result = uc.execute(_cmd())

    assert result.supplement_id > 0
    assert uow.committed


def test_nachtrag_ist_pending():
    uow = _make_uow_with_employee()
    uc = RegisterSupplementUseCase(uow)

    result = uc.execute(_cmd())

    supplement = uow.supplement_repo.get_by_id(result.supplement_id)
    assert supplement is not None
    assert supplement.approval_status == ApprovalStatus.PENDING
    assert supplement.approved_by_user_id is None
    assert supplement.approved_at is None
    assert supplement.rejected_by_user_id is None
    assert supplement.rejected_at is None


def test_review_case_wird_angelegt():
    uow = _make_uow_with_employee()
    uc = RegisterSupplementUseCase(uow)

    result = uc.execute(_cmd())

    assert result.review_case_id is not None
    assert result.review_case_id > 0


def test_review_case_ist_offen():
    uow = _make_uow_with_employee()
    uc = RegisterSupplementUseCase(uow)

    result = uc.execute(_cmd())

    cases = uow.review_case_repo.list_open_for_employee(1)
    assert len(cases) == 1
    assert cases[0].id == result.review_case_id
    assert cases[0].status == ReviewCaseStatus.OPEN


def test_audit_log_eintrag_vorhanden():
    uow = _make_uow_with_employee()
    uc = RegisterSupplementUseCase(uow)

    uc.execute(_cmd())

    assert len(uow.audit_log_repo.entries) == 1
    entry = uow.audit_log_repo.entries[0]
    assert entry.event_type == audit_events.SUPPLEMENT_CREATED
    assert entry.object_type == "supplements"
    assert entry.employee_id == 1


def test_audit_log_enthaelt_fachliche_felder():
    import json

    uow = _make_uow_with_employee()
    booking_id = _add_booking(uow)
    uc = RegisterSupplementUseCase(uow)

    result = uc.execute(_cmd(related_booking_id=booking_id))

    details = json.loads(uow.audit_log_repo.entries[0].details_json)
    assert details["booking_type"] == "COME"
    assert details["reason"] == "Vergessen einzustempeln"
    assert details["approval_status"] == "PENDING"
    assert details["related_booking_id"] == booking_id
    assert details["review_case_id"] == result.review_case_id
    assert "recorded_at" in details


def test_related_booking_id_wird_durchgereicht():
    uow = _make_uow_with_employee()
    booking_id = _add_booking(uow)
    uc = RegisterSupplementUseCase(uow)

    result = uc.execute(_cmd(related_booking_id=booking_id))

    supplement = uow.supplement_repo.get_by_id(result.supplement_id)
    assert supplement is not None
    assert supplement.related_booking_id == booking_id


# --- Fehlerpfade hinterlassen keine Spuren ---


def test_not_found_error_kein_commit_kein_audit_log():
    uow = _uow_with_actor()
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(employee_id=99))

    assert not uow.committed
    assert len(uow.audit_log_repo.entries) == 0
    assert len(uow.supplement_repo.list_pending()) == 0


def test_inactive_employee_error_kein_commit_kein_audit_log():
    uow = _make_uow_with_employee(employee_active=False)
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd(employee_id=1))

    assert not uow.committed
    assert len(uow.audit_log_repo.entries) == 0
    assert len(uow.supplement_repo.list_pending()) == 0


# --- ReviewCase-Beschreibung ---


def test_review_case_description_enthaelt_fachliche_referenz():
    uow = _make_uow_with_employee()
    uc = RegisterSupplementUseCase(uow)

    uc.execute(_cmd())

    cases = uow.review_case_repo.list_open_for_employee(1)
    desc = cases[0].description
    assert "Nachtrag #" in desc
    assert "COME" in desc
    assert str(_NOW.date()) in desc


# --- related_booking_id-Existenzprüfung ---


def _add_booking(uow: FakeUnitOfWork) -> int:
    booking = uow.time_booking_repo.add(
        TimeBooking(
            id=0,
            employee_id=1,
            booking_type=BookingType.COME,
            booked_at=_NOW,
            source=BookingSource.TERMINAL,
            status=BookingStatus.OPEN,
            terminal_id=1,
            rfid_card_id=1,
            device_event_id=None,
            note=None,
        )
    )
    return booking.id


def test_related_booking_id_existiert_nachtrag_wird_angelegt():
    uow = _make_uow_with_employee()
    booking_id = _add_booking(uow)
    uc = RegisterSupplementUseCase(uow)

    result = uc.execute(_cmd(related_booking_id=booking_id))

    assert result.supplement_id > 0
    supplement = uow.supplement_repo.get_by_id(result.supplement_id)
    assert supplement is not None
    assert supplement.related_booking_id == booking_id


def test_related_booking_id_nicht_gefunden_loest_not_found_error():
    uow = _make_uow_with_employee()
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(related_booking_id=999))

    assert not uow.committed
    assert len(uow.audit_log_repo.entries) == 0
    assert len(uow.supplement_repo.list_pending()) == 0
