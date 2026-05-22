import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import CreateSupplementCommand
from arbeitszeit.application.use_cases.register_supplement import (
    RegisterSupplementUseCase,
)
from arbeitszeit.domain.entities import Employee
from arbeitszeit.domain.enums import ApprovalStatus, BookingType, ReviewCaseStatus
from arbeitszeit.domain.errors import NotFoundError
from tests.application.fakes import FakeUnitOfWork

_NOW = datetime(2025, 3, 10, 9, 0, tzinfo=timezone.utc)


def _make_uow_with_employee() -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    uow.employee_repo.add(Employee(
        id=0,
        personnel_no="E001",
        first_name="Anna",
        last_name="Muster",
        is_active=True,
    ))
    return uow


def _cmd(**overrides) -> CreateSupplementCommand:
    defaults = dict(
        employee_id=1,
        related_booking_id=None,
        booking_type=BookingType.COME,
        event_at=_NOW,
        recorded_at=_NOW,
        reason="Vergessen einzustempeln",
        recorded_by_user_id=2,
    )
    return CreateSupplementCommand(**{**defaults, **overrides})


def test_unbekannter_mitarbeiter_loest_not_found_error():
    uow = FakeUnitOfWork()
    uc = RegisterSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(employee_id=99))


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
    assert entry.event_type == "SUPPLEMENT_CREATED"
    assert entry.object_type == "supplements"
    assert entry.employee_id == 1


def test_related_booking_id_wird_durchgereicht():
    uow = _make_uow_with_employee()
    uc = RegisterSupplementUseCase(uow)

    result = uc.execute(_cmd(related_booking_id=42))

    supplement = uow.supplement_repo.get_by_id(result.supplement_id)
    assert supplement is not None
    assert supplement.related_booking_id == 42
