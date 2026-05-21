from dataclasses import dataclass
from typing import Sequence

from arbeitszeit.domain.enums import BookingStatus, BookingType, ReviewCaseType
from arbeitszeit.domain.errors import InvalidBookingSequenceError, OpenPhaseConflictError


@dataclass(frozen=True)
class ValidationResult:
    accepted: bool
    initial_status: BookingStatus
    reason_code: str | None
    follow_up_case_types: tuple[ReviewCaseType, ...]


def validate_booking_sequence(
    booking_type: BookingType,
    day_bookings: Sequence[BookingType],
) -> ValidationResult:
    if not day_bookings:
        if booking_type in (BookingType.GO, BookingType.BREAK_END):
            raise InvalidBookingSequenceError(
                f"Erste Tagesbuchung darf nicht {booking_type} sein."
            )
        return ValidationResult(
            accepted=True,
            initial_status=BookingStatus.OPEN,
            reason_code=None,
            follow_up_case_types=(),
        )

    last = day_bookings[-1]
    _open_break = _has_open_break(day_bookings)
    _open_work = _has_open_work(day_bookings)

    if booking_type == BookingType.COME:
        if last == BookingType.COME or _open_work:
            raise InvalidBookingSequenceError("COME nach offenem COME nicht zulässig.")
        if _open_break:
            raise InvalidBookingSequenceError("COME während offener Pause nicht zulässig.")

    elif booking_type == BookingType.GO:
        if last == BookingType.GO or not _open_work:
            raise InvalidBookingSequenceError("GO nach offenem GO nicht zulässig.")
        if _open_break:
            raise OpenPhaseConflictError("GO bei offener Pause: Pausenphase muss zuerst geschlossen werden.")

    elif booking_type == BookingType.BREAK_START:
        if _open_break:
            raise InvalidBookingSequenceError("BREAK_START nach BREAK_START ohne BREAK_END nicht zulässig.")

    elif booking_type == BookingType.BREAK_END:
        if not _open_break:
            raise InvalidBookingSequenceError("BREAK_END ohne offene Pause nicht zulässig.")

    return ValidationResult(
        accepted=True,
        initial_status=BookingStatus.OPEN,
        reason_code=None,
        follow_up_case_types=(),
    )


def _has_open_break(day_bookings: Sequence[BookingType]) -> bool:
    open_break = False
    for bt in day_bookings:
        if bt == BookingType.BREAK_START:
            open_break = True
        elif bt == BookingType.BREAK_END:
            open_break = False
    return open_break


def _has_open_work(day_bookings: Sequence[BookingType]) -> bool:
    open_work = False
    for bt in day_bookings:
        if bt == BookingType.COME:
            open_work = True
        elif bt == BookingType.GO:
            open_work = False
    return open_work
