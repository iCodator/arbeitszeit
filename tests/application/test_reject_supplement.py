import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
from arbeitszeit.domain import audit_events

from arbeitszeit.application.commands import RejectSupplementCommand
from arbeitszeit.application.use_cases.reject_supplement import RejectSupplementUseCase
from arbeitszeit.domain.entities import ReviewCase, Supplement, UserAccount
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
    UserRole,
)
from arbeitszeit.domain.errors import NotFoundError, PermissionDeniedError, ValidationError
from tests.application.fakes import FakeUnitOfWork

_NOW = datetime(2025, 3, 10, 9, 0, tzinfo=timezone.utc)
_EVENT_AT = datetime(2025, 3, 10, 8, 0, tzinfo=timezone.utc)
_REJECTOR_ID = 1  # id des REVIEWER-UserAccounts (erstes Element im Fake-Store)


def _make_uow_with_pending_supplement(
    related_booking_id: int | None = None,
) -> tuple[FakeUnitOfWork, int]:
    uow = FakeUnitOfWork()
    uow.user_account_repo.add(UserAccount(
        id=0, employee_id=None, username="reviewer",
        role=UserRole.REVIEWER, is_active=True,
    ))
    supplement = uow.supplement_repo.add(Supplement(
        id=0,
        employee_id=1,
        related_booking_id=related_booking_id,
        booking_type=BookingType.COME,
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


def _uow_with_rejector() -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    uow.user_account_repo.add(UserAccount(
        id=0, employee_id=None, username="reviewer",
        role=UserRole.REVIEWER, is_active=True,
    ))
    return uow


def _cmd(supplement_id: int, **overrides) -> RejectSupplementCommand:
    defaults = dict(
        supplement_id=supplement_id,
        rejected_by_user_id=_REJECTOR_ID,
        reason="Zeitraum nicht plausibel",
    )
    return RejectSupplementCommand(**{**defaults, **overrides})


# --- Rollenprüfung ---

def test_unbekannter_benutzer_loest_permission_denied():
    uow = FakeUnitOfWork()
    uc = RejectSupplementUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(supplement_id=1, rejected_by_user_id=999))


def test_benutzer_ohne_reviewer_rolle_loest_permission_denied():
    uow = FakeUnitOfWork()
    emp_user = uow.user_account_repo.add(UserAccount(
        id=0, employee_id=None, username="emp",
        role=UserRole.EMPLOYEE, is_active=True,
    ))
    uc = RejectSupplementUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(supplement_id=1, rejected_by_user_id=emp_user.id))


def test_inaktiver_benutzer_loest_permission_denied():
    uow = FakeUnitOfWork()
    inactive = uow.user_account_repo.add(UserAccount(
        id=0, employee_id=None, username="inactive_reviewer",
        role=UserRole.REVIEWER, is_active=False,
    ))
    uc = RejectSupplementUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(supplement_id=1, rejected_by_user_id=inactive.id))


# --- Fehlerbehandlung ---

def test_nachtrag_nicht_gefunden_loest_not_found_error():
    uow = _uow_with_rejector()
    uc = RejectSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(supplement_id=99))


def test_nachtrag_nicht_pending_loest_validation_error():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uow.supplement_repo.approve(supplement_id, approved_by_user_id=3, approved_at=_NOW)
    uc = RejectSupplementUseCase(uow)

    with pytest.raises(ValidationError):
        uc.execute(_cmd(supplement_id))


# --- Fehlerpfade hinterlassen keine Spuren ---

def test_fehler_kein_commit_kein_audit_log():
    uow = _uow_with_rejector()
    uc = RejectSupplementUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(supplement_id=99))

    assert not uow.committed
    assert len(uow.audit_log_repo.entries) == 0


# --- Supplement wird abgelehnt ---

def test_supplement_erhaelt_status_rejected():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = RejectSupplementUseCase(uow)

    uc.execute(_cmd(supplement_id))

    s = uow.supplement_repo.get_by_id(supplement_id)
    assert s is not None
    assert s.approval_status == ApprovalStatus.REJECTED
    assert s.rejected_by_user_id == _REJECTOR_ID
    assert s.rejected_at is not None
    assert uow.committed


# --- ReviewCase wird geschlossen ---

def test_manual_entry_review_case_wird_mit_note_geschlossen():
    uow, supplement_id = _make_uow_with_pending_supplement()
    review_case = uow.review_case_repo.add(ReviewCase(
        id=0, employee_id=1, case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
        severity=ReviewSeverity.INFO, status=ReviewCaseStatus.OPEN,
        description="Nachtrag", booking_id=None,
        created_at=_NOW, closed_at=None, closed_by_user_id=None,
    ))
    uc = RejectSupplementUseCase(uow)

    result = uc.execute(_cmd(supplement_id))

    assert result.review_case_id == review_case.id
    closed = uow.review_case_repo._store[review_case.id]
    assert closed.status == ReviewCaseStatus.CLOSED_WITH_NOTE
    assert closed.note == "Zeitraum nicht plausibel"


def test_anderer_review_case_bleibt_offen():
    uow, supplement_id = _make_uow_with_pending_supplement()
    other_case = uow.review_case_repo.add(ReviewCase(
        id=0, employee_id=1, case_type=ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION,
        severity=ReviewSeverity.WARN, status=ReviewCaseStatus.OPEN,
        description="Anderer Fall", booking_id=None,
        created_at=_NOW, closed_at=None, closed_by_user_id=None,
    ))
    uc = RejectSupplementUseCase(uow)

    uc.execute(_cmd(supplement_id))

    still_open = uow.review_case_repo._store[other_case.id]
    assert still_open.status == ReviewCaseStatus.OPEN


def test_kein_review_case_wenn_keiner_passt():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = RejectSupplementUseCase(uow)

    result = uc.execute(_cmd(supplement_id))

    assert result.review_case_id is None


# --- Audit-Log ---

def test_audit_log_eintrag_vorhanden():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = RejectSupplementUseCase(uow)

    uc.execute(_cmd(supplement_id))

    assert len(uow.audit_log_repo.entries) == 1
    entry = uow.audit_log_repo.entries[0]
    assert entry.event_type == audit_events.SUPPLEMENT_REJECTED
    assert entry.object_type == "supplements"
    assert entry.employee_id == 1


def test_audit_log_enthaelt_begruendung():
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = RejectSupplementUseCase(uow)

    uc.execute(_cmd(supplement_id))

    details = json.loads(uow.audit_log_repo.entries[0].details_json)
    assert details["reason"] == "Zeitraum nicht plausibel"
    assert details["supplement_id"] == supplement_id
