import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import BookingType
from arbeitszeit.domain.errors import InvalidBookingSequenceError, OpenPhaseConflictError
from arbeitszeit.domain.services.booking_rules import validate_booking_sequence


def test_erste_buchung_go_wird_abgelehnt():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.GO, [])


def test_erste_buchung_break_end_wird_abgelehnt():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.BREAK_END, [])


def test_come_nach_offenem_come():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.COME, [BookingType.COME])


def test_go_nach_offenem_go():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.GO, [BookingType.COME, BookingType.GO])


def test_break_start_nach_break_start():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(
            BookingType.BREAK_START,
            [BookingType.COME, BookingType.BREAK_START],
        )


def test_break_end_ohne_offene_pause():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.BREAK_END, [BookingType.COME])


def test_come_waehrend_offener_pause():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(
            BookingType.COME,
            [BookingType.COME, BookingType.BREAK_START],
        )


def test_go_bei_offener_pause():
    with pytest.raises(OpenPhaseConflictError):
        validate_booking_sequence(
            BookingType.GO,
            [BookingType.COME, BookingType.BREAK_START],
        )


def test_break_start_ohne_offene_arbeitsphase():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.BREAK_START, [])


def test_break_start_nach_go():
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(
            BookingType.BREAK_START,
            [BookingType.COME, BookingType.GO],
        )
