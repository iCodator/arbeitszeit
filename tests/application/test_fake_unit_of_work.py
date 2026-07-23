"""Tests für die commit-or-rollback-Semantik und Grenzfallverhalten von FakeUnitOfWork."""

__version__ = "1.1"

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.entities import TimeBooking
from arbeitszeit.domain.enums import BookingSource, BookingStatus, BookingType
from arbeitszeit.domain.value_objects import EmployeeId, RfidCardId, TerminalId, TimeBookingId
from tests.application.fakes import FakeUnitOfWork


def test_vergessenes_commit_setzt_rolled_back() -> None:
    uow = FakeUnitOfWork()
    with uow:
        pass  # commit() absichtlich weggelassen

    assert uow.rolled_back is True
    assert uow.committed is False


def test_korrekter_commit_kein_rollback() -> None:
    uow = FakeUnitOfWork()
    with uow:
        uow.commit()

    assert uow.committed is True
    assert uow.rolled_back is False


# --- FakeTimeBookingRepository.list_between Grenzfall ---


def _make_booking(booked_at: datetime) -> TimeBooking:
    return TimeBooking(
        id=TimeBookingId(0),
        employee_id=EmployeeId(1),
        booking_type=BookingType.COME,
        booked_at=booked_at,
        source=BookingSource.TERMINAL,
        status=BookingStatus.OPEN,
        terminal_id=TerminalId(1),
        rfid_card_id=RfidCardId(1),
        device_event_id=None,
        note=None,
    )


def test_list_between_to_dt_exklusiv() -> None:
    """Buchung genau an to_dt darf nicht zurückgegeben werden (halboffenes Intervall [from, to))."""
    uow = FakeUnitOfWork()
    to_dt = datetime(2025, 6, 2, 0, 0, tzinfo=timezone.utc)
    uow.time_booking_repo.add(_make_booking(booked_at=to_dt))

    result = uow.time_booking_repo.list_between(
        1,
        datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc),
        to_dt,
    )

    assert len(result) == 0
