import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import ApproveSupplementCommand
from arbeitszeit.application.use_cases.approve_supplement import ApproveSupplementUseCase
from arbeitszeit.domain.entities import Employee, ReviewCase, Supplement
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.domain.errors import InactiveEmployeeError, NotFoundError, ValidationError
from tests.application.fakes import FakeUnitOfWork

_NOW = datetime(2025, 3, 10, 9, 0, tzinfo=timezone.utc)
_EVENT_AT = datetime(2025, 3, 10, 8, 0, tzinfo=timezone.utc)


def _make_uow_with_pending_supplement(
    employee_active: bool = True,
    related_booking_id: int | None = None,
    booking_type: BookingType = BookingType.COME,
) -> tuple[FakeUnitOfWork, int]:
    uow = FakeUnitOfWork()
    emp = uow.employee_repo.add(Employee(
        id=0, personnel_no="E001", first_name="Anna",
        last_name="Muster", is_active=employee_active,
    ))
    supplement = uow.supplement_repo.add(Supplement(
        id=0,
        employee_id=emp.id,
        related_booking_id=related_booking_id,
        booking_type=booking_type,
        event_at=_EVENT_AT,
        recorded_at=_NOW,
        reason="Vergessen einzustempeln",
        recorded_by_user_id=2,
        approval_status=ApprovalStatus.PENDING,
        approved_by_user_id=None,
        approved_at=None,
        rejected_by_user_id=None,
        rejected_at=None,
    ))
    return uow, supplement.id


def _cmd(supplement_id: int, **overrides) -> ApproveSupplementCommand:
    defaults = dict(supplement_id=supplement_id, approved_by_user_id=3)
    return ApproveSupplementCommand(**{**defaults, **overrides})


# --- Fehlerbehandlung ---

def test_nachtrag_nicht_gefunden_loest_not_found_error():
    uow = FakeUnitOfWork()
    uc = ApproveSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(supplement_id=99))


def test_nachtrag_nicht_pending_loest_validation_error():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uow.supplement_repo.approve(supplement_id, approved_by_user_id=3, approved_at=_NOW)
    uc = ApproveSupplementUseCase(uow)

    with pytest.raises(ValidationError):
        uc.execute(_cmd(supplement_id))


def test_inaktiver_mitarbeiter_loest_inactive_employee_error():
    uow, supplement_id = _make_uow_with_pending_supplement(employee_active=False)
    uc = ApproveSupplementUseCase(uow)

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd(supplement_id))


def test_fehlender_mitarbeiter_loest_not_found_error():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uow.employee_repo._store.clear()
    uc = ApproveSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(supplement_id))


# --- Fehlerpfade hinterlassen keine Spuren ---

def test_fehler_kein_commit_kein_audit_log():
    uow = FakeUnitOfWork()
    uc = ApproveSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(supplement_id=99))

    assert not uow.committed
    assert len(uow.audit_log_repo.entries) == 0


# --- Supplement wird genehmigt ---

def test_supplement_erhaelt_status_approved():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(uow)

    uc.execute(_cmd(supplement_id))

    s = uow.supplement_repo.get_by_id(supplement_id)
    assert s is not None
    assert s.approval_status == ApprovalStatus.APPROVED
    assert s.approved_by_user_id == 3
    assert s.approved_at is not None
    assert uow.committed


# --- Buchung wird angelegt ---

def test_buchung_wird_angelegt():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(uow)

    result = uc.execute(_cmd(supplement_id))

    assert result.booking_id > 0
    booking = uow.time_booking_repo.get_by_id(result.booking_id)
    assert booking is not None
    assert booking.source == BookingSource.MANUAL
    assert booking.booking_type == BookingType.COME


def test_buchung_hat_status_open_fuer_come():
    uow, supplement_id = _make_uow_with_pending_supplement(
        booking_type=BookingType.COME
    )
    uc = ApproveSupplementUseCase(uow)

    result = uc.execute(_cmd(supplement_id))

    assert result.booking_status == BookingStatus.OPEN
    assert result.follow_up_case_ids == ()


def test_buchung_ohne_compliance_flags_hat_status_ok():
    from datetime import timedelta
    from arbeitszeit.domain.entities import TimeBooking
    from arbeitszeit.domain.enums import BookingStatus as BS
    uow, supplement_id = _make_uow_with_pending_supplement(
        booking_type=BookingType.GO
    )
    # COME 08:00 bereits vorhanden, GO um 13:00 -> 5h, kein Flag
    uow.time_booking_repo.add(TimeBooking(
        id=0, employee_id=1, booking_type=BookingType.COME,
        booked_at=_EVENT_AT,
        source=BookingSource.TERMINAL, status=BS.OPEN,
        terminal_id=1, rfid_card_id=1, device_event_id=None, note=None,
    ))
    go_supplement = uow.supplement_repo.add(Supplement(
        id=0, employee_id=1, related_booking_id=None,
        booking_type=BookingType.GO,
        event_at=_EVENT_AT + timedelta(hours=5),
        recorded_at=_NOW, reason="Test", recorded_by_user_id=2,
        approval_status=ApprovalStatus.PENDING,
        approved_by_user_id=None, approved_at=None,
        rejected_by_user_id=None, rejected_at=None,
    ))
    uc = ApproveSupplementUseCase(uow)

    result = uc.execute(_cmd(go_supplement.id))

    assert result.booking_status == BookingStatus.OK
    assert result.follow_up_case_ids == ()


# --- ReviewCase wird geschlossen ---

def test_manual_entry_review_case_wird_geschlossen():
    uow, supplement_id = _make_uow_with_pending_supplement()
    review_case = uow.review_case_repo.add(ReviewCase(
        id=0, employee_id=1, case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
        severity=ReviewSeverity.INFO, status=ReviewCaseStatus.OPEN,
        description="Nachtrag", booking_id=None,
        created_at=_NOW, closed_at=None, closed_by_user_id=None,
    ))
    uc = ApproveSupplementUseCase(uow)

    uc.execute(_cmd(supplement_id))

    closed = uow.review_case_repo._store[review_case.id]
    assert closed.status == ReviewCaseStatus.RESOLVED


def test_kein_review_case_wenn_keiner_passt():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(uow)

    result = uc.execute(_cmd(supplement_id))

    assert result.follow_up_case_ids == ()


# --- Audit-Log ---

def test_audit_log_eintrag_vorhanden():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(uow)

    uc.execute(_cmd(supplement_id))

    assert len(uow.audit_log_repo.entries) == 1
    entry = uow.audit_log_repo.entries[0]
    assert entry.event_type == "SUPPLEMENT_APPROVED"
    assert entry.object_type == "supplements"
    assert entry.employee_id == 1


def test_audit_log_enthaelt_fachliche_felder():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(uow)

    result = uc.execute(_cmd(supplement_id))

    details = json.loads(uow.audit_log_repo.entries[0].details_json)
    assert details["supplement_id"] == supplement_id
    assert details["booking_id"] == result.booking_id
    assert details["booking_type"] == "COME"
    assert details["booking_status"] == "OPEN"
