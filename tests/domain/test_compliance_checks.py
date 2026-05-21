import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.entities import TimeBooking
from arbeitszeit.domain.enums import BookingSource, BookingStatus, BookingType, ReviewCaseType
from arbeitszeit.domain.services.compliance_checks import (
    check_break_compliance,
    check_max_hours,
    check_rest_period,
)


def _booking(booking_type: BookingType, hour: int, minute: int = 0) -> TimeBooking:
    return TimeBooking(
        id=0,
        employee_id=1,
        booking_type=booking_type,
        booked_at=datetime(2024, 1, 15, hour, minute, tzinfo=timezone.utc),
        source=BookingSource.TERMINAL,
        status=BookingStatus.OK,
        terminal_id=None,
        device_event_id=None,
    )


def _dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute, tzinfo=timezone.utc)


# --- check_break_compliance ---

def test_keine_pausenverletzung_bei_kurzer_arbeitszeit():
    bookings = [_booking(BookingType.COME, 8), _booking(BookingType.GO, 11)]
    assert check_break_compliance(bookings) == []


def test_pausenverletzung_ueber_6h_ohne_ausreichende_pause():
    bookings = [
        _booking(BookingType.COME, 7),
        _booking(BookingType.BREAK_START, 13),
        _booking(BookingType.BREAK_END, 13, 10),
        _booking(BookingType.GO, 14),
    ]
    flags = check_break_compliance(bookings)
    assert ReviewCaseType.POSSIBLE_BREAK_VIOLATION in flags


def test_pausenverletzung_ueber_9h_ohne_45min_pause():
    bookings = [
        _booking(BookingType.COME, 7),
        _booking(BookingType.BREAK_START, 12),
        _booking(BookingType.BREAK_END, 12, 20),
        _booking(BookingType.GO, 17, 30),
    ]
    flags = check_break_compliance(bookings)
    assert ReviewCaseType.POSSIBLE_BREAK_VIOLATION in flags


def test_keine_pausenverletzung_mit_ausreichender_pause():
    bookings = [
        _booking(BookingType.COME, 7),
        _booking(BookingType.BREAK_START, 12),
        _booking(BookingType.BREAK_END, 12, 31),
        _booking(BookingType.GO, 14),
    ]
    assert check_break_compliance(bookings) == []


# --- check_max_hours ---

def test_keine_ueberschreitung_bei_normaler_arbeitszeit():
    bookings = [_booking(BookingType.COME, 7, 30), _booking(BookingType.GO, 15, 30)]
    assert check_max_hours(bookings) == []


def test_max_hours_verletzung_ueber_8h():
    bookings = [_booking(BookingType.COME, 7), _booking(BookingType.GO, 15, 1)]
    flags = check_max_hours(bookings)
    assert ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION in flags


def test_max_hours_verletzung_ueber_10h():
    bookings = [_booking(BookingType.COME, 7), _booking(BookingType.GO, 17, 1)]
    flags = check_max_hours(bookings)
    assert ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION in flags


# --- check_rest_period ---

def test_keine_ruhezeiverletzung_bei_ausreichender_ruhezeit():
    last_go = datetime(2024, 1, 15, 17, 0, tzinfo=timezone.utc)
    next_come = datetime(2024, 1, 16, 5, 0, tzinfo=timezone.utc)  # 12h später
    assert check_rest_period(last_go, next_come) == []


def test_ruhezeit_verletzung_unter_11h():
    last_go = datetime(2024, 1, 15, 18, 0, tzinfo=timezone.utc)
    next_come = datetime(2024, 1, 16, 4, 0, tzinfo=timezone.utc)  # nur 10h später
    flags = check_rest_period(last_go, next_come)
    assert ReviewCaseType.POSSIBLE_REST_VIOLATION in flags
