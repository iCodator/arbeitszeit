__version__ = "1.1"

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import BookingType
from arbeitszeit.domain.errors import (
    InvalidBookingSequenceError,
    OpenPhaseConflictError,
)
from arbeitszeit.domain.services.booking_rules import validate_booking_sequence


def test_erste_buchung_go_wird_abgelehnt() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.GO, [])


def test_erste_buchung_break_end_wird_abgelehnt() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.BREAK_END, [])


def test_come_nach_offenem_come() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.COME, [BookingType.COME])


def test_go_nach_offenem_go() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.GO, [BookingType.COME, BookingType.GO])


def test_break_start_nach_break_start() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(
            BookingType.BREAK_START,
            [BookingType.COME, BookingType.BREAK_START],
        )


def test_break_end_ohne_offene_pause() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.BREAK_END, [BookingType.COME])


def test_come_waehrend_offener_pause() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(
            BookingType.COME,
            [BookingType.COME, BookingType.BREAK_START],
        )


def test_go_bei_offener_pause() -> None:
    with pytest.raises(OpenPhaseConflictError):
        validate_booking_sequence(
            BookingType.GO,
            [BookingType.COME, BookingType.BREAK_START],
        )


def test_break_start_ohne_offene_arbeitsphase() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.BREAK_START, [])


def test_break_start_nach_go() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(
            BookingType.BREAK_START,
            [BookingType.COME, BookingType.GO],
        )


# --- Erfolgspfade ---


def test_come_erste_buchung_wird_akzeptiert() -> None:
    validate_booking_sequence(BookingType.COME, [])


def test_come_nach_abgeschlossenem_kommen_gehen_zyklus_wird_abgelehnt() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(BookingType.COME, [BookingType.COME, BookingType.GO])


def test_come_nach_vollem_zyklus_mit_pause_wird_abgelehnt() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(
            BookingType.COME,
            [BookingType.COME, BookingType.BREAK_START, BookingType.BREAK_END, BookingType.GO],
        )


def test_go_nach_come_wird_akzeptiert() -> None:
    validate_booking_sequence(BookingType.GO, [BookingType.COME])


def test_break_start_nach_come_wird_akzeptiert() -> None:
    validate_booking_sequence(BookingType.BREAK_START, [BookingType.COME])


def test_break_end_nach_break_start_wird_akzeptiert() -> None:
    validate_booking_sequence(BookingType.BREAK_END, [BookingType.COME, BookingType.BREAK_START])


def test_come_nach_go_bei_noch_offener_pause() -> None:
    # Sonderfall: DB enthält bereits GO während offener Pause (z.B. Altdaten).
    # open_work=False (durch GO), open_break=True (kein BREAK_END nach BREAK_START).
    # Weiteres COME ist abzulehnen (offene Pause).
    with pytest.raises(InvalidBookingSequenceError):
        validate_booking_sequence(
            BookingType.COME,
            [BookingType.COME, BookingType.BREAK_START, BookingType.GO],
        )
