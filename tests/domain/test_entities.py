import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.entities import ReviewCase, Supplement
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)

_NOW = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)


def _review_case(**overrides):
    defaults = dict(
        id=1,
        employee_id=1,
        case_type=ReviewCaseType.OPEN_WORK_PHASE,
        severity=ReviewSeverity.WARN,
        status=ReviewCaseStatus.OPEN,
        description="Offene Arbeitsphase",
        booking_id=None,
        created_at=_NOW,
        closed_at=None,
        closed_by_user_id=None,
    )
    return ReviewCase(**{**defaults, **overrides})


def _supplement(**overrides):
    defaults = dict(
        id=1,
        employee_id=1,
        related_booking_id=None,
        booking_type=BookingType.COME,
        event_at=_NOW,
        recorded_at=_NOW,
        reason="Vergessen einzustempeln",
        recorded_by_user_id=2,
        approval_status=ApprovalStatus.PENDING,
        approved_by_user_id=None,
        approved_at=None,
    )
    return Supplement(**{**defaults, **overrides})


# --- ReviewCase ---

def test_review_case_open_ohne_schliessungsdaten_ist_gueltig():
    case = _review_case(status=ReviewCaseStatus.OPEN)
    assert case.closed_at is None
    assert case.closed_by_user_id is None


def test_review_case_open_mit_schliessungsdaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _review_case(
            status=ReviewCaseStatus.OPEN,
            closed_at=_NOW,
            closed_by_user_id=1,
        )


def test_review_case_in_review_mit_schliessungsdaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _review_case(
            status=ReviewCaseStatus.IN_REVIEW,
            closed_at=_NOW,
            closed_by_user_id=1,
        )


def test_review_case_resolved_mit_schliessungsdaten_ist_gueltig():
    case = _review_case(
        status=ReviewCaseStatus.RESOLVED,
        closed_at=_NOW,
        closed_by_user_id=5,
    )
    assert case.closed_at == _NOW
    assert case.closed_by_user_id == 5


def test_review_case_resolved_ohne_schliessungsdaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _review_case(
            status=ReviewCaseStatus.RESOLVED,
            closed_at=None,
            closed_by_user_id=None,
        )


def test_review_case_closed_with_note_ohne_schliessungsdaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _review_case(
            status=ReviewCaseStatus.CLOSED_WITH_NOTE,
            closed_at=None,
            closed_by_user_id=None,
        )


# --- Supplement ---

def test_supplement_pending_ohne_freigabedaten_ist_gueltig():
    s = _supplement(approval_status=ApprovalStatus.PENDING)
    assert s.approved_by_user_id is None
    assert s.approved_at is None


def test_supplement_pending_mit_freigabedaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _supplement(
            approval_status=ApprovalStatus.PENDING,
            approved_by_user_id=3,
            approved_at=_NOW,
        )


def test_supplement_approved_mit_freigabedaten_ist_gueltig():
    s = _supplement(
        approval_status=ApprovalStatus.APPROVED,
        approved_by_user_id=3,
        approved_at=_NOW,
    )
    assert s.approved_by_user_id == 3
    assert s.approved_at == _NOW


def test_supplement_approved_ohne_freigabedaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _supplement(
            approval_status=ApprovalStatus.APPROVED,
            approved_by_user_id=None,
            approved_at=None,
        )


def test_supplement_rejected_ohne_freigabedaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _supplement(
            approval_status=ApprovalStatus.REJECTED,
            approved_by_user_id=None,
            approved_at=None,
        )
