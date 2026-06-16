import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.entities import (
    BookingCorrection,
    Employee,
    ReviewCase,
    RfidCard,
    Supplement,
    UserAccount,
    WorkScheduleVersion,
)
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingType,
    CardStatus,
    ChangeOrigin,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
    ScopeType,
    UserRole,
)

_NOW = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
_TODAY = date(2024, 1, 15)
_YESTERDAY = date(2024, 1, 14)
_TOMORROW = date(2024, 1, 16)


def _rfid_card(**overrides):
    defaults = dict(
        id=1,
        employee_id=1,
        uid_hash="abc123",
        status=CardStatus.ACTIVE,
        valid_from=_TODAY,
        valid_until=None,
        replaced_by_card_id=None,
    )
    return RfidCard(**{**defaults, **overrides})


def _work_schedule(**overrides):
    from datetime import time

    defaults = dict(
        id=1,
        scope_type=ScopeType.GLOBAL,
        scope_employee_id=None,
        weekday=1,
        start_time=time(7, 30),
        end_time=time(16, 0),
        valid_from=_TODAY,
        valid_until=None,
        change_origin=ChangeOrigin.SYSTEM_SEED,
        changed_by_user_id=None,
    )
    return WorkScheduleVersion(**{**defaults, **overrides})


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
        rejected_by_user_id=None,
        rejected_at=None,
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


def test_review_case_closed_with_note_mit_note_ist_gueltig():
    case = _review_case(
        status=ReviewCaseStatus.CLOSED_WITH_NOTE,
        closed_at=_NOW,
        closed_by_user_id=5,
        note="Besprochen und dokumentiert.",
    )
    assert case.note == "Besprochen und dokumentiert."
    assert case.closed_by_user_id == 5


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


def test_supplement_pending_mit_ablehnungsdaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _supplement(
            approval_status=ApprovalStatus.PENDING,
            rejected_by_user_id=3,
            rejected_at=_NOW,
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


def test_supplement_approved_mit_ablehnungsdaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _supplement(
            approval_status=ApprovalStatus.APPROVED,
            approved_by_user_id=3,
            approved_at=_NOW,
            rejected_by_user_id=5,
            rejected_at=_NOW,
        )


def test_supplement_rejected_mit_ablehnungsdaten_ist_gueltig():
    s = _supplement(
        approval_status=ApprovalStatus.REJECTED,
        rejected_by_user_id=4,
        rejected_at=_NOW,
    )
    assert s.rejected_by_user_id == 4
    assert s.rejected_at == _NOW


def test_supplement_rejected_ohne_ablehnungsdaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _supplement(
            approval_status=ApprovalStatus.REJECTED,
        )


def test_supplement_rejected_mit_freigabedaten_ist_ungueltig():
    with pytest.raises(ValueError):
        _supplement(
            approval_status=ApprovalStatus.REJECTED,
            rejected_by_user_id=4,
            rejected_at=_NOW,
            approved_by_user_id=3,
            approved_at=_NOW,
        )


# --- RfidCard ---


def test_rfid_card_ohne_valid_until_ist_gueltig():
    card = _rfid_card(valid_from=_TODAY, valid_until=None)
    assert card.valid_until is None


def test_rfid_card_valid_until_nach_valid_from_ist_gueltig():
    card = _rfid_card(valid_from=_TODAY, valid_until=_TOMORROW)
    assert card.valid_until == _TOMORROW


def test_rfid_card_valid_until_vor_valid_from_ist_ungueltig():
    with pytest.raises(ValueError):
        _rfid_card(valid_from=_TODAY, valid_until=_YESTERDAY)


# --- WorkScheduleVersion ---


def test_work_schedule_global_ohne_mitarbeiterbezug_ist_gueltig():
    ws = _work_schedule(scope_type=ScopeType.GLOBAL, scope_employee_id=None)
    assert ws.scope_employee_id is None


def test_work_schedule_global_mit_mitarbeiterbezug_ist_ungueltig():
    with pytest.raises(ValueError):
        _work_schedule(scope_type=ScopeType.GLOBAL, scope_employee_id=5)


def test_work_schedule_employee_mit_mitarbeiterbezug_ist_gueltig():
    ws = _work_schedule(scope_type=ScopeType.EMPLOYEE, scope_employee_id=3)
    assert ws.scope_employee_id == 3


def test_work_schedule_employee_ohne_mitarbeiterbezug_ist_ungueltig():
    with pytest.raises(ValueError):
        _work_schedule(scope_type=ScopeType.EMPLOYEE, scope_employee_id=None)


def test_work_schedule_valid_until_vor_valid_from_ist_ungueltig():
    with pytest.raises(ValueError):
        _work_schedule(valid_from=_TODAY, valid_until=_YESTERDAY)


def test_work_schedule_ungueltige_wochentage_sind_ungueltig():
    with pytest.raises(ValueError):
        _work_schedule(weekday=0)
    with pytest.raises(ValueError):
        _work_schedule(weekday=8)


def test_work_schedule_start_time_nach_end_time_ist_ungueltig():
    from datetime import time

    with pytest.raises(ValueError):
        _work_schedule(start_time=time(16, 0), end_time=time(7, 30))


def test_work_schedule_gleiche_start_und_end_time_ist_ungueltig():
    from datetime import time

    with pytest.raises(ValueError):
        _work_schedule(start_time=time(8, 0), end_time=time(8, 0))


# --- Employee ---


def test_employee_mit_leerem_personnel_no_ist_ungueltig():
    with pytest.raises(ValueError):
        Employee(
            id=1, personnel_no="", first_name="Anna", last_name="Muster", is_active=True
        )


def test_employee_mit_nur_leerzeichen_personnel_no_ist_ungueltig():
    with pytest.raises(ValueError):
        Employee(
            id=1,
            personnel_no="   ",
            first_name="Anna",
            last_name="Muster",
            is_active=True,
        )


def test_employee_mit_gueltigem_personnel_no_ist_gueltig():
    emp = Employee(
        id=1, personnel_no="E001", first_name="Anna", last_name="Muster", is_active=True
    )
    assert emp.personnel_no == "E001"


# --- UserAccount ---


def test_user_account_mit_leerem_username_ist_ungueltig():
    with pytest.raises(ValueError):
        UserAccount(
            id=1, employee_id=None, username="", role=UserRole.ADMIN, is_active=True
        )


def test_user_account_mit_nur_leerzeichen_username_ist_ungueltig():
    with pytest.raises(ValueError):
        UserAccount(
            id=1, employee_id=None, username="  ", role=UserRole.ADMIN, is_active=True
        )


def test_user_account_mit_gueltigem_username_ist_gueltig():
    acc = UserAccount(
        id=1, employee_id=None, username="admin", role=UserRole.ADMIN, is_active=True
    )
    assert acc.username == "admin"


# --- ReviewCase: CLOSED_WITH_NOTE erfordert note ---


def test_review_case_closed_with_note_ohne_note_ist_ungueltig():
    with pytest.raises(ValueError):
        ReviewCase(
            id=1,
            employee_id=1,
            case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
            severity=ReviewSeverity.INFO,
            status=ReviewCaseStatus.CLOSED_WITH_NOTE,
            description="Test",
            booking_id=None,
            created_at=_NOW,
            closed_at=_NOW,
            closed_by_user_id=1,
            note=None,
        )


def test_review_case_closed_with_note_mit_leerer_note_ist_ungueltig():
    with pytest.raises(ValueError):
        ReviewCase(
            id=1,
            employee_id=1,
            case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
            severity=ReviewSeverity.INFO,
            status=ReviewCaseStatus.CLOSED_WITH_NOTE,
            description="Test",
            booking_id=None,
            created_at=_NOW,
            closed_at=_NOW,
            closed_by_user_id=1,
            note="   ",
        )


def test_review_case_closed_with_note_mit_gueltiger_note_ist_gueltig():
    case = ReviewCase(
        id=1,
        employee_id=1,
        case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
        severity=ReviewSeverity.INFO,
        status=ReviewCaseStatus.CLOSED_WITH_NOTE,
        description="Test",
        booking_id=None,
        created_at=_NOW,
        closed_at=_NOW,
        closed_by_user_id=1,
        note="Begründung vorhanden",
    )
    assert case.note == "Begründung vorhanden"


def test_review_case_resolved_ohne_note_ist_gueltig():
    case = ReviewCase(
        id=1,
        employee_id=1,
        case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
        severity=ReviewSeverity.INFO,
        status=ReviewCaseStatus.RESOLVED,
        description="Test",
        booking_id=None,
        created_at=_NOW,
        closed_at=_NOW,
        closed_by_user_id=1,
        note=None,
    )
    assert case.status == ReviewCaseStatus.RESOLVED


# --- Supplement: zeitliche Plausibilität ---

_RECORDED = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
_APPROVED_LATER = datetime(2024, 1, 16, 10, 0, tzinfo=timezone.utc)
_BEFORE_RECORDED = datetime(2024, 1, 14, 10, 0, tzinfo=timezone.utc)


def test_supplement_approved_at_vor_recorded_at_ist_ungueltig():
    with pytest.raises(ValueError):
        Supplement(
            id=1,
            employee_id=1,
            related_booking_id=None,
            booking_type=BookingType.COME,
            event_at=_RECORDED,
            recorded_at=_RECORDED,
            reason="Test",
            recorded_by_user_id=2,
            approval_status=ApprovalStatus.APPROVED,
            approved_by_user_id=3,
            approved_at=_BEFORE_RECORDED,
        )


def test_supplement_approved_at_gleich_recorded_at_ist_gueltig():
    sup = Supplement(
        id=1,
        employee_id=1,
        related_booking_id=None,
        booking_type=BookingType.COME,
        event_at=_RECORDED,
        recorded_at=_RECORDED,
        reason="Test",
        recorded_by_user_id=2,
        approval_status=ApprovalStatus.APPROVED,
        approved_by_user_id=3,
        approved_at=_RECORDED,
    )
    assert sup.approved_at == sup.recorded_at


def test_supplement_rejected_at_vor_recorded_at_ist_ungueltig():
    with pytest.raises(ValueError):
        Supplement(
            id=1,
            employee_id=1,
            related_booking_id=None,
            booking_type=BookingType.COME,
            event_at=_RECORDED,
            recorded_at=_RECORDED,
            reason="Test",
            recorded_by_user_id=2,
            approval_status=ApprovalStatus.REJECTED,
            approved_by_user_id=None,
            approved_at=None,
            rejected_by_user_id=3,
            rejected_at=_BEFORE_RECORDED,
        )


# --- BookingCorrection: zeitliche Plausibilität ---

_OLD_BOOKED = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
_CORRECTION_CREATED = datetime(2024, 1, 15, 17, 0, tzinfo=timezone.utc)
_NEW_BOOKED = datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)


def test_booking_correction_created_vor_old_booked_at_ist_ungueltig():
    early = datetime(2024, 1, 15, 7, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        BookingCorrection(
            id=1,
            original_booking_id=10,
            corrected_by_user_id=2,
            reason="Fehler",
            old_booking_type=BookingType.COME,
            old_booked_at=_OLD_BOOKED,
            new_booking_type=BookingType.GO,
            new_booked_at=_NEW_BOOKED,
            created_at=early,
        )


def test_booking_correction_created_at_gleich_old_booked_at_ist_gueltig():
    correction = BookingCorrection(
        id=1,
        original_booking_id=10,
        corrected_by_user_id=2,
        reason="Fehler",
        old_booking_type=BookingType.COME,
        old_booked_at=_OLD_BOOKED,
        new_booking_type=BookingType.GO,
        new_booked_at=_NEW_BOOKED,
        created_at=_OLD_BOOKED,
    )
    assert correction.created_at == correction.old_booked_at
