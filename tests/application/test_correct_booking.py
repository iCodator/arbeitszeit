import dataclasses
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
from arbeitszeit.application.commands import CreateCorrectionCommand
from arbeitszeit.application.use_cases.correct_booking import CorrectBookingUseCase
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import Employee, ReviewCase, TimeBooking, UserAccount
from arbeitszeit.domain.enums import (
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
    UserRole,
)
from arbeitszeit.domain.errors import (
    InactiveEmployeeError,
    NotFoundError,
    PermissionDeniedError,
)

from tests.application.fakes import FakeUnitOfWork

_NOW = datetime(2025, 3, 10, 17, 0, tzinfo=timezone.utc)
_EARLIER = datetime(2025, 3, 10, 8, 0, tzinfo=timezone.utc)
_ACTOR_ID = 1  # id des REVIEWER-UserAccounts (erstes Element im Fake-Store)


def _make_uow_with_booking() -> tuple[FakeUnitOfWork, int]:
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
    emp = uow.employee_repo.add(
        Employee(
            id=0,
            personnel_no="E001",
            first_name="Anna",
            last_name="Muster",
            is_active=True,
        )
    )
    booking = uow.time_booking_repo.add(
        TimeBooking(
            id=0,
            employee_id=emp.id,
            booking_type=BookingType.COME,
            booked_at=_EARLIER,
            source=BookingSource.TERMINAL,
            status=BookingStatus.OPEN,
            terminal_id=1,
            rfid_card_id=1,
            device_event_id=None,
            note=None,
        )
    )
    return uow, booking.id


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


def _cmd(booking_id: int, **overrides) -> CreateCorrectionCommand:
    defaults = dict(
        original_booking_id=booking_id,
        corrected_by_user_id=_ACTOR_ID,
        reason="Falscher Typ eingestempelt",
        new_booking_type=BookingType.GO,
        new_booked_at=_NOW,
    )
    return CreateCorrectionCommand(**{**defaults, **overrides})


# --- Rollenprüfung ---


def test_unbekannter_benutzer_loest_permission_denied():
    uow, booking_id = _make_uow_with_booking()
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(booking_id, corrected_by_user_id=999))


def test_benutzer_ohne_reviewer_rolle_loest_permission_denied():
    uow, booking_id = _make_uow_with_booking()
    emp_user = uow.user_account_repo.add(
        UserAccount(
            id=0,
            employee_id=None,
            username="emp",
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
    )
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(booking_id, corrected_by_user_id=emp_user.id))


def test_inaktiver_benutzer_loest_permission_denied():
    uow, booking_id = _make_uow_with_booking()
    inactive = uow.user_account_repo.add(
        UserAccount(
            id=0,
            employee_id=None,
            username="inactive_reviewer",
            role=UserRole.REVIEWER,
            is_active=False,
        )
    )
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(booking_id, corrected_by_user_id=inactive.id))


# --- Fehlerbehandlung ---


def test_buchung_nicht_gefunden_loest_not_found_error():
    uow = _uow_with_actor()
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(booking_id=99))


def test_fehlender_mitarbeiterdatensatz_loest_not_found_error():
    uow = _uow_with_actor()
    booking = uow.time_booking_repo.add(
        TimeBooking(
            id=0,
            employee_id=99,
            booking_type=BookingType.COME,
            booked_at=_EARLIER,
            source=BookingSource.TERMINAL,
            status=BookingStatus.OPEN,
            terminal_id=1,
            rfid_card_id=1,
            device_event_id=None,
            note=None,
        )
    )
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(booking.id))


def test_buchung_erhaelt_status_corrected():
    uow, booking_id = _make_uow_with_booking()
    uc = CorrectBookingUseCase(uow)

    result = uc.execute(_cmd(booking_id))

    booking = uow.time_booking_repo.get_by_id(result.updated_booking_id)
    assert booking is not None
    assert booking.status == BookingStatus.CORRECTED
    assert uow.committed


def test_korrekturobjekt_wird_angelegt():
    uow, booking_id = _make_uow_with_booking()
    uc = CorrectBookingUseCase(uow)

    result = uc.execute(_cmd(booking_id))

    assert result.correction_id > 0
    corrections = uow.booking_correction_repo.list_for_booking(booking_id)
    assert len(corrections) == 1
    assert corrections[0].old_booking_type == BookingType.COME
    assert corrections[0].new_booking_type == BookingType.GO


def test_nur_passender_review_case_wird_geschlossen():
    uow, booking_id = _make_uow_with_booking()

    other_booking = uow.time_booking_repo.add(
        TimeBooking(
            id=0,
            employee_id=1,
            booking_type=BookingType.GO,
            booked_at=_NOW,
            source=BookingSource.TERMINAL,
            status=BookingStatus.NEEDS_REVIEW,
            terminal_id=1,
            rfid_card_id=1,
            device_event_id=None,
            note=None,
        )
    )
    case_matching = uow.review_case_repo.add(
        ReviewCase(
            id=0,
            employee_id=1,
            case_type=ReviewCaseType.OPEN_WORK_PHASE,
            severity=ReviewSeverity.WARN,
            status=ReviewCaseStatus.OPEN,
            description="Passender Fall",
            booking_id=booking_id,
            created_at=_EARLIER,
            closed_at=None,
            closed_by_user_id=None,
        )
    )
    case_other = uow.review_case_repo.add(
        ReviewCase(
            id=0,
            employee_id=1,
            case_type=ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION,
            severity=ReviewSeverity.WARN,
            status=ReviewCaseStatus.OPEN,
            description="Anderer Fall",
            booking_id=other_booking.id,
            created_at=_EARLIER,
            closed_at=None,
            closed_by_user_id=None,
        )
    )

    uc = CorrectBookingUseCase(uow)
    result = uc.execute(_cmd(booking_id))

    assert result.review_case_id == case_matching.id

    closed = uow.review_case_repo._store[case_matching.id]
    assert closed.status == ReviewCaseStatus.RESOLVED

    still_open = uow.review_case_repo._store[case_other.id]
    assert still_open.status == ReviewCaseStatus.OPEN


def test_kein_review_case_wenn_keiner_passt():
    uow, booking_id = _make_uow_with_booking()
    uc = CorrectBookingUseCase(uow)

    result = uc.execute(_cmd(booking_id))

    assert result.review_case_id is None


def test_audit_log_eintrag_vorhanden():
    uow, booking_id = _make_uow_with_booking()
    uc = CorrectBookingUseCase(uow)

    uc.execute(_cmd(booking_id))

    assert len(uow.audit_log_repo.entries) == 1
    entry = uow.audit_log_repo.entries[0]
    assert entry.event_type == audit_events.BOOKING_CORRECTED
    assert entry.object_type == "booking_corrections"
    assert entry.employee_id == 1


def test_audit_log_enthaelt_fachliche_felder():
    uow, booking_id = _make_uow_with_booking()
    uc = CorrectBookingUseCase(uow)

    uc.execute(_cmd(booking_id))

    details = json.loads(uow.audit_log_repo.entries[0].details_json)
    assert details["old_booking_type"] == "COME"
    assert details["new_booking_type"] == "GO"
    assert details["reason"] == "Falscher Typ eingestempelt"
    assert details["status_after"] == "CORRECTED"
    assert details["original_booking_id"] == booking_id


def test_inaktiver_mitarbeiter_loest_inactive_employee_error():
    uow, booking_id = _make_uow_with_booking()
    emp = uow.employee_repo.get_by_id(1)
    uow.employee_repo._store[1] = dataclasses.replace(emp, is_active=False)
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd(booking_id))


def test_inaktiver_mitarbeiter_kein_commit_kein_audit_log():
    uow, booking_id = _make_uow_with_booking()
    emp = uow.employee_repo.get_by_id(1)
    uow.employee_repo._store[1] = dataclasses.replace(emp, is_active=False)
    uow.committed = False
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd(booking_id))

    assert not uow.committed
    assert len(uow.audit_log_repo.entries) == 0


# --- Review-Case-Selektivität nach Typ ---


def test_manual_entry_review_bleibt_offen_trotz_gleicher_booking_id():
    # MANUAL_ENTRY_REVIEW gehört zum Nachtragsprozess, nicht zur Buchungskorrektur –
    # bleibt auch dann offen, wenn booking_id übereinstimmt.
    uow, booking_id = _make_uow_with_booking()
    manual_case = uow.review_case_repo.add(
        ReviewCase(
            id=0,
            employee_id=1,
            case_type=ReviewCaseType.MANUAL_ENTRY_REVIEW,
            severity=ReviewSeverity.INFO,
            status=ReviewCaseStatus.OPEN,
            description="Nachtrag-Review",
            booking_id=booking_id,
            created_at=_EARLIER,
            closed_at=None,
            closed_by_user_id=None,
        )
    )
    uc = CorrectBookingUseCase(uow)

    result = uc.execute(_cmd(booking_id))

    assert uow.review_case_repo._store[manual_case.id].status == ReviewCaseStatus.OPEN
    assert result.review_case_id is None


def test_mehrere_korrigierbare_faelle_werden_alle_geschlossen():
    # Zwei Compliance-Fälle zur selben Buchung → beide werden geschlossen.
    uow, booking_id = _make_uow_with_booking()
    case1 = uow.review_case_repo.add(
        ReviewCase(
            id=0,
            employee_id=1,
            case_type=ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION,
            severity=ReviewSeverity.WARN,
            status=ReviewCaseStatus.OPEN,
            description="Maximalstunden",
            booking_id=booking_id,
            created_at=_EARLIER,
            closed_at=None,
            closed_by_user_id=None,
        )
    )
    case2 = uow.review_case_repo.add(
        ReviewCase(
            id=0,
            employee_id=1,
            case_type=ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW,
            severity=ReviewSeverity.WARN,
            status=ReviewCaseStatus.OPEN,
            description="Fenster",
            booking_id=booking_id,
            created_at=_EARLIER,
            closed_at=None,
            closed_by_user_id=None,
        )
    )
    uc = CorrectBookingUseCase(uow)

    result = uc.execute(_cmd(booking_id))

    assert uow.review_case_repo._store[case1.id].status == ReviewCaseStatus.RESOLVED
    assert uow.review_case_repo._store[case2.id].status == ReviewCaseStatus.RESOLVED
    assert result.review_case_id == case1.id  # erster geschlossener Fall
