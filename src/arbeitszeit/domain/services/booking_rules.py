from typing import Callable, Sequence

from arbeitszeit.domain.enums import BookingType
from arbeitszeit.domain.errors import (
    InvalidBookingSequenceError,
    OpenPhaseConflictError,
)


def validate_booking_sequence(
    booking_type: BookingType,
    day_bookings: Sequence[BookingType],
) -> None:
    # day_bookings must be in chronological order
    if not day_bookings:
        _validate_first_booking(booking_type)
        return
    open_work = _has_open_work(day_bookings)
    open_break = _has_open_break(day_bookings)
    validator = _VALIDATORS.get(booking_type)
    if validator is not None:
        validator(open_work, open_break)


def _validate_first_booking(booking_type: BookingType) -> None:
    if booking_type in (BookingType.GO, BookingType.BREAK_END, BookingType.BREAK_START):
        raise InvalidBookingSequenceError(f"Erste Tagesbuchung darf nicht {booking_type} sein.")


def _validate_come(open_work: bool, open_break: bool) -> None:
    if open_work:
        raise InvalidBookingSequenceError("COME nach offenem COME nicht zulässig.")
    if open_break:
        raise InvalidBookingSequenceError("COME während offener Pause nicht zulässig.")


def _validate_go(open_work: bool, open_break: bool) -> None:
    if not open_work:
        raise InvalidBookingSequenceError("GO ohne offene Arbeitsphase nicht zulässig.")
    if open_break:
        raise OpenPhaseConflictError("GO bei offener Pause: Pause zuerst schließen.")


def _validate_break_start(open_work: bool, open_break: bool) -> None:
    # Deckt implizit auch den Regelwerk-v5-§6-Fall „BREAK_START nach GO" ab:
    # Nach einem GO ist keine Arbeitsphase mehr offen, sodass dieser Check
    # greift, ohne dass ein eigener GO-Zweig erforderlich ist.
    if not open_work:
        raise InvalidBookingSequenceError("BREAK_START ohne offene Arbeitsphase.")
    if open_break:
        raise InvalidBookingSequenceError("BREAK_START bei offener Pause nicht zulässig.")


def _validate_break_end(open_work: bool, open_break: bool) -> None:
    if not open_break:
        raise InvalidBookingSequenceError("BREAK_END ohne offene Pause nicht zulässig.")


_VALIDATORS: dict[BookingType, Callable[[bool, bool], None]] = {
    BookingType.COME: _validate_come,
    BookingType.GO: _validate_go,
    BookingType.BREAK_START: _validate_break_start,
    BookingType.BREAK_END: _validate_break_end,
}


def _has_open_work(day_bookings: Sequence[BookingType]) -> bool:
    open_work = False
    for bt in day_bookings:
        if bt == BookingType.COME:
            open_work = True
        elif bt == BookingType.GO:
            open_work = False
    return open_work


def _has_open_break(day_bookings: Sequence[BookingType]) -> bool:
    open_break = False
    for bt in day_bookings:
        if bt == BookingType.BREAK_START:
            open_break = True
        elif bt == BookingType.BREAK_END:
            open_break = False
    return open_break
