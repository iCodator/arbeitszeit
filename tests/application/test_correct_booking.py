import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import CreateCorrectionCommand
from arbeitszeit.application.use_cases.correct_booking import CorrectBookingUseCase
from arbeitszeit.domain.entities import Employee, ReviewCase, TimeBooking
from arbeitszeit.domain.enums import (
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.domain.errors import InactiveEmployeeError, NotFoundError
from tests.application.fakes import FakeUnitOfWork

_NOW = datetime(2025, 3, 10, 17, 0, tzinfo=timezone.utc)
_EARLIER = datetime(2025, 3, 10, 8, 0, tzinfo=timezone.utc)


def _make_uow_with_booking() -> tuple[FakeUnitOfWork, int]:
    uow = FakeUnitOfWork()
    emp = uow.employee_repo.add(Employee(
        id=0, personnel_no="E001", first_name="Anna",
        last_name="Muster", is_active=True,
    ))
    booking = uow.time_booking_repo.add(TimeBooking(
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
    ))
    return uow, booking.id


def _cmd(booking_id: int, **overrides) -> CreateCorrectionCommand:
    defaults = dict(
        original_booking_id=booking_id,
        corrected_by_user_id=2,
        reason="Falscher Typ eingestempelt",
        new_booking_type=BookingType.GO,
        new_booked_at=_NOW,
    )
    return CreateCorrectionCommand(**{**defaults, **overrides})


def test_buchung_nicht_gefunden_loest_not_found_error():
    uow = FakeUnitOfWork()
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd(booking_id=99))


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

    other_booking = uow.time_booking_repo.add(TimeBooking(
        id=0, employee_id=1, booking_type=BookingType.GO, booked_at=_NOW,
        source=BookingSource.TERMINAL, status=BookingStatus.NEEDS_REVIEW,
        terminal_id=1, rfid_card_id=1, device_event_id=None, note=None,
    ))
    case_matching = uow.review_case_repo.add(ReviewCase(
        id=0, employee_id=1, case_type=ReviewCaseType.OPEN_WORK_PHASE,
        severity=ReviewSeverity.WARN, status=ReviewCaseStatus.OPEN,
        description="Passender Fall", booking_id=booking_id,
        created_at=_EARLIER, closed_at=None, closed_by_user_id=None,
    ))
    case_other = uow.review_case_repo.add(ReviewCase(
        id=0, employee_id=1, case_type=ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION,
        severity=ReviewSeverity.WARN, status=ReviewCaseStatus.OPEN,
        description="Anderer Fall", booking_id=other_booking.id,
        created_at=_EARLIER, closed_at=None, closed_by_user_id=None,
    ))

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
    assert entry.event_type == "BOOKING_CORRECTED"
    assert entry.object_type == "booking_corrections"
    assert entry.employee_id == 1


def test_audit_log_enthaelt_fachliche_felder():
    import json
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
    import dataclasses
    uow.employee_repo._store[1] = dataclasses.replace(emp, is_active=False)
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd(booking_id))


def test_inaktiver_mitarbeiter_kein_commit_kein_audit_log():
    uow, booking_id = _make_uow_with_booking()
    emp = uow.employee_repo.get_by_id(1)
    import dataclasses
    uow.employee_repo._store[1] = dataclasses.replace(emp, is_active=False)
    uow.committed = False
    uc = CorrectBookingUseCase(uow)

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd(booking_id))

    assert not uow.committed
    assert len(uow.audit_log_repo.entries) == 0
