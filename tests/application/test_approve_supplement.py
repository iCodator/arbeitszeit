import json
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
from arbeitszeit.application.commands import ApproveSupplementCommand
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.application.use_cases.approve_supplement import (
    ApproveSupplementUseCase,
)
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import (
    Employee,
    ReviewCase,
    Supplement,
    UserAccount,
    WorkScheduleVersion,
)
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
    BookingType,
    ChangeOrigin,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
    ScopeType,
    UserRole,
)
from arbeitszeit.domain.errors import (
    InactiveEmployeeError,
    InvalidBookingSequenceError,
    NotFoundError,
    OpenPhaseConflictError,
    PermissionDeniedError,
    ValidationError,
)
from arbeitszeit.domain.value_objects import (
    EmployeeId,
    ReviewCaseId,
    RfidCardId,
    SupplementId,
    TerminalId,
    TimeBookingId,
    UserAccountId,
    WorkScheduleVersionId,
)
from tests.application.fakes import FakeUnitOfWork

_NOW = datetime(2025, 3, 10, 9, 0, tzinfo=timezone.utc)
_EVENT_AT = datetime(2025, 3, 10, 8, 0, tzinfo=timezone.utc)


_APPROVER_ID = 1  # id des REVIEWER-UserAccounts (erstes Element im Fake-Store)


def _as_uow(uow: FakeUnitOfWork) -> UnitOfWork:
    return cast(UnitOfWork, uow)


def _make_uow_with_pending_supplement(
    employee_active: bool = True,
    related_booking_id: int | None = None,
    booking_type: BookingType = BookingType.COME,
) -> tuple[FakeUnitOfWork, int]:
    uow = FakeUnitOfWork()
    uow.user_account_repo.add(
        UserAccount(
            id=UserAccountId(0),
            employee_id=None,
            username="reviewer",
            role=UserRole.REVIEWER,
            is_active=True,
        )
    )
    emp = uow.employee_repo.add(
        Employee(
            id=EmployeeId(0),
            personnel_no="E001",
            first_name="Anna",
            last_name="Muster",
            is_active=employee_active,
        )
    )
    supplement = uow.supplement_repo.add(
        Supplement(
            id=SupplementId(0),
            employee_id=emp.id,
            related_booking_id=(
                TimeBookingId(related_booking_id) if related_booking_id is not None else None
            ),
            booking_type=booking_type,
            event_at=_EVENT_AT,
            recorded_at=_NOW,
            reason="Vergessen einzustempeln",
            recorded_by_user_id=UserAccountId(2),
            approval_status=ApprovalStatus.PENDING,
            approved_by_user_id=None,
            approved_at=None,
            rejected_by_user_id=None,
            rejected_at=None,
        )
    )
    return uow, supplement.id


def _cmd(supplement_id: int, **overrides: Any) -> ApproveSupplementCommand:
    defaults = dict(supplement_id=supplement_id, approving_user_id=_APPROVER_ID)
    return ApproveSupplementCommand(**{**defaults, **overrides})


def _uow_with_reviewer() -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    uow.user_account_repo.add(
        UserAccount(
            id=UserAccountId(0),
            employee_id=None,
            username="reviewer",
            role=UserRole.REVIEWER,
            is_active=True,
        )
    )
    return uow


# --- Fehlerbehandlung ---


def test_nachtrag_nicht_gefunden_loest_not_found_error() -> None:
    uow = _uow_with_reviewer()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(supplement_id=99))


def test_nachtrag_nicht_pending_loest_validation_error() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    uow.supplement_repo.approve(
        supplement_id, approved_by_user_id=UserAccountId(3), approved_at=_NOW
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(ValidationError):
        uc.execute(_cmd(supplement_id))


def test_inaktiver_mitarbeiter_loest_inactive_employee_error() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement(employee_active=False)
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd(supplement_id))


def test_fehlender_mitarbeiter_loest_not_found_error() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    uow.employee_repo._store.clear()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(supplement_id))


def test_go_als_erste_buchung_loest_invalid_sequence_error() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement(booking_type=BookingType.GO)
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(InvalidBookingSequenceError):
        uc.execute(_cmd(supplement_id))


def test_break_end_ohne_offene_pause_loest_invalid_sequence_error() -> None:
    from arbeitszeit.domain.entities import TimeBooking
    from arbeitszeit.domain.enums import BookingStatus as BS

    uow, supplement_id = _make_uow_with_pending_supplement(booking_type=BookingType.BREAK_END)
    uow.time_booking_repo.add(
        TimeBooking(
            id=TimeBookingId(0),
            employee_id=EmployeeId(1),
            booking_type=BookingType.COME,
            booked_at=_EVENT_AT - timedelta(hours=1),
            source=BookingSource.TERMINAL,
            status=BS.OPEN,
            terminal_id=TerminalId(1),
            rfid_card_id=RfidCardId(1),
            device_event_id=None,
            note=None,
        )
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(InvalidBookingSequenceError):
        uc.execute(_cmd(supplement_id))


def test_go_bei_offener_pause_loest_open_phase_conflict() -> None:
    from arbeitszeit.domain.entities import TimeBooking
    from arbeitszeit.domain.enums import BookingStatus as BS

    uow, supplement_id = _make_uow_with_pending_supplement(booking_type=BookingType.GO)
    uow.time_booking_repo.add(
        TimeBooking(
            id=TimeBookingId(0),
            employee_id=EmployeeId(1),
            booking_type=BookingType.COME,
            booked_at=_EVENT_AT - timedelta(hours=2),
            source=BookingSource.TERMINAL,
            status=BS.OPEN,
            terminal_id=TerminalId(1),
            rfid_card_id=RfidCardId(1),
            device_event_id=None,
            note=None,
        )
    )
    uow.time_booking_repo.add(
        TimeBooking(
            id=TimeBookingId(0),
            employee_id=EmployeeId(1),
            booking_type=BookingType.BREAK_START,
            booked_at=_EVENT_AT - timedelta(hours=1),
            source=BookingSource.TERMINAL,
            status=BS.OPEN,
            terminal_id=TerminalId(1),
            rfid_card_id=RfidCardId(1),
            device_event_id=None,
            note=None,
        )
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(OpenPhaseConflictError):
        uc.execute(_cmd(supplement_id))


# --- Fehlerpfade hinterlassen keine Spuren ---


def test_fehler_kein_commit_kein_audit_log() -> None:
    uow = _uow_with_reviewer()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(supplement_id=99))

    assert not uow.committed
    assert len(uow.audit_log_repo.entries) == 0


# --- Supplement wird genehmigt ---


def test_supplement_erhaelt_status_approved() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    uc.execute(_cmd(supplement_id))

    s = uow.supplement_repo.get_by_id(supplement_id)
    assert s is not None
    assert s.approval_status == ApprovalStatus.APPROVED
    assert s.approved_by_user_id == _APPROVER_ID
    assert s.approved_at is not None
    assert uow.committed


# --- Buchung wird angelegt ---


def test_buchung_wird_angelegt() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    result = uc.execute(_cmd(supplement_id))

    assert result.booking_id > 0
    booking = uow.time_booking_repo.get_by_id(result.booking_id)
    assert booking is not None
    assert booking.source == BookingSource.MANUAL
    assert booking.booking_type == BookingType.COME


def test_buchung_hat_status_open_fuer_come() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement(booking_type=BookingType.COME)
    uc = ApproveSupplementUseCase(_as_uow(uow))

    result = uc.execute(_cmd(supplement_id))

    assert result.booking_status == BookingStatus.OPEN
    assert result.follow_up_case_ids == ()


def test_buchung_ohne_compliance_flags_hat_status_ok() -> None:
    from arbeitszeit.domain.entities import TimeBooking
    from arbeitszeit.domain.enums import BookingStatus as BS

    uow, supplement_id = _make_uow_with_pending_supplement(booking_type=BookingType.GO)
    # COME 08:00 bereits vorhanden, GO um 13:00 -> 5h, kein Flag
    uow.time_booking_repo.add(
        TimeBooking(
            id=TimeBookingId(0),
            employee_id=EmployeeId(1),
            booking_type=BookingType.COME,
            booked_at=_EVENT_AT,
            source=BookingSource.TERMINAL,
            status=BS.OPEN,
            terminal_id=TerminalId(1),
            rfid_card_id=RfidCardId(1),
            device_event_id=None,
            note=None,
        )
    )
    go_supplement = uow.supplement_repo.add(
        Supplement(
            id=SupplementId(0),
            employee_id=EmployeeId(1),
            related_booking_id=None,
            booking_type=BookingType.GO,
            event_at=_EVENT_AT + timedelta(hours=5),
            recorded_at=_NOW,
            reason="Test",
            recorded_by_user_id=UserAccountId(2),
            approval_status=ApprovalStatus.PENDING,
            approved_by_user_id=None,
            approved_at=None,
            rejected_by_user_id=None,
            rejected_at=None,
        )
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    result = uc.execute(_cmd(go_supplement.id))

    assert result.booking_status == BookingStatus.OK
    assert result.follow_up_case_ids == ()


# --- ReviewCase wird geschlossen ---


def test_manual_entry_review_case_wird_geschlossen() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    review_case = uow.review_case_repo.add(
        ReviewCase(
            id=ReviewCaseId(0),
            employee_id=EmployeeId(1),
            case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
            severity=ReviewSeverity.INFO,
            status=ReviewCaseStatus.OPEN,
            description="Nachtrag",
            booking_id=None,
            created_at=_NOW,
            closed_at=None,
            closed_by_user_id=None,
        )
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    uc.execute(_cmd(supplement_id))

    closed = uow.review_case_repo._store[review_case.id]
    assert closed.status == ReviewCaseStatus.RESOLVED


def test_kein_review_case_wenn_keiner_passt() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    result = uc.execute(_cmd(supplement_id))

    assert result.follow_up_case_ids == ()


# --- Audit-Log ---


def test_audit_log_eintrag_vorhanden() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    uc.execute(_cmd(supplement_id))

    assert len(uow.audit_log_repo.entries) == 1
    entry = uow.audit_log_repo.entries[0]
    assert entry.event_type == audit_events.SUPPLEMENT_APPROVED
    assert entry.object_type == "supplements"
    assert entry.employee_id == 1


def test_audit_log_enthaelt_fachliche_felder() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    result = uc.execute(_cmd(supplement_id))

    details = json.loads(uow.audit_log_repo.entries[0].details_json)
    assert details["supplement_id"] == supplement_id
    assert details["booking_id"] == result.booking_id
    assert details["booking_type"] == "COME"
    assert details["booking_status"] == "OPEN"


# --- Rollenprüfung ---


def test_unbekannter_benutzer_loest_permission_denied() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(supplement_id, approving_user_id=999))


def test_benutzer_ohne_reviewer_rolle_loest_permission_denied() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    employee_user = uow.user_account_repo.add(
        UserAccount(
            id=UserAccountId(0),
            employee_id=EmployeeId(1),
            username="employee",
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(supplement_id, approving_user_id=employee_user.id))


def test_inaktiver_benutzer_loest_permission_denied() -> None:
    uow, supplement_id = _make_uow_with_pending_supplement()
    inactive = uow.user_account_repo.add(
        UserAccount(
            id=UserAccountId(0),
            employee_id=None,
            username="inactive_reviewer",
            role=UserRole.REVIEWER,
            is_active=False,
        )
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(supplement_id, approving_user_id=inactive.id))


# --- Review-Case-Selektivität ---


def test_nur_passender_review_case_wird_geschlossen() -> None:
    # Nachtrag mit related_booking_id=7 → schließt genau den Case mit booking_id=7
    uow, supplement_id = _make_uow_with_pending_supplement(related_booking_id=7)
    case_matching = uow.review_case_repo.add(
        ReviewCase(
            id=ReviewCaseId(0),
            employee_id=EmployeeId(1),
            case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
            severity=ReviewSeverity.INFO,
            status=ReviewCaseStatus.OPEN,
            description="Passender Fall",
            booking_id=TimeBookingId(7),
            created_at=_NOW,
            closed_at=None,
            closed_by_user_id=None,
        )
    )
    case_other_booking = uow.review_case_repo.add(
        ReviewCase(
            id=ReviewCaseId(0),
            employee_id=EmployeeId(1),
            case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
            severity=ReviewSeverity.INFO,
            status=ReviewCaseStatus.OPEN,
            description="Anderer Nachtrag",
            booking_id=TimeBookingId(99),
            created_at=_NOW,
            closed_at=None,
            closed_by_user_id=None,
        )
    )
    case_other_type = uow.review_case_repo.add(
        ReviewCase(
            id=ReviewCaseId(0),
            employee_id=EmployeeId(1),
            case_type=ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION,
            severity=ReviewSeverity.WARN,
            status=ReviewCaseStatus.OPEN,
            description="Anderer Typ",
            booking_id=TimeBookingId(7),
            created_at=_NOW,
            closed_at=None,
            closed_by_user_id=None,
        )
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    uc.execute(_cmd(supplement_id))

    assert uow.review_case_repo._store[case_matching.id].status == ReviewCaseStatus.RESOLVED
    assert uow.review_case_repo._store[case_other_booking.id].status == ReviewCaseStatus.OPEN
    assert uow.review_case_repo._store[case_other_type.id].status == ReviewCaseStatus.OPEN


# --- Regelzeitfenster ---


def test_nachtrag_ausserhalb_regelzeitfenster_erzeugt_review_case() -> None:
    # _EVENT_AT = 2025-03-10 08:00 UTC, isoweekday=1 (Montag)
    # Fenster 09:00–17:00 → 08:00 liegt vor Fensterbeginn → OUTSIDE_SCHEDULE_WINDOW
    uow, supplement_id = _make_uow_with_pending_supplement()
    uow.work_schedule_repo.add(
        WorkScheduleVersion(
            id=WorkScheduleVersionId(0),
            scope_type=ScopeType.GLOBAL,
            scope_employee_id=None,
            weekday=1,
            start_time=time(9, 0),
            end_time=time(17, 0),
            valid_from=date(2000, 1, 1),
            valid_until=None,
            change_origin=ChangeOrigin.SYSTEM_SEED,
            changed_by_user_id=None,
        )
    )
    uc = ApproveSupplementUseCase(_as_uow(uow))

    result = uc.execute(_cmd(supplement_id))

    # COME → Status bleibt OPEN; aber OUTSIDE_SCHEDULE_WINDOW ReviewCase angelegt
    assert result.booking_status == BookingStatus.OPEN
    assert len(result.follow_up_case_ids) > 0
    cases = uow.review_case_repo.list_open_for_employee(1)
    assert any(c.case_type == ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW for c in cases)
