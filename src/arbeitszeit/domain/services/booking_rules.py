from typing import Sequence

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
        if booking_type in (
            BookingType.GO, BookingType.BREAK_END, BookingType.BREAK_START
        ):
            raise InvalidBookingSequenceError(
                f"Erste Tagesbuchung darf nicht {booking_type} sein."
            )
        return

    open_work = _has_open_work(day_bookings)
    open_break = _has_open_break(day_bookings)

    if booking_type == BookingType.COME:
        if open_work:
            raise InvalidBookingSequenceError("COME nach offenem COME nicht zulässig.")
        if open_break:
            raise InvalidBookingSequenceError(
                "COME während offener Pause nicht zulässig."
            )

    elif booking_type == BookingType.GO:
        if not open_work:
            raise InvalidBookingSequenceError(
                "GO ohne offene Arbeitsphase nicht zulässig."
            )
        if open_break:
            raise OpenPhaseConflictError("GO bei offener Pause: Pause zuerst schließen.")

    elif booking_type == BookingType.BREAK_START:
        if not open_work:
            raise InvalidBookingSequenceError("BREAK_START ohne offene Arbeitsphase.")
        if open_break:
            raise InvalidBookingSequenceError(
                "BREAK_START bei offener Pause nicht zulässig."
            )

    elif booking_type == BookingType.BREAK_END:
        if not open_break:
            raise InvalidBookingSequenceError(
                "BREAK_END ohne offene Pause nicht zulässig."
            )


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
