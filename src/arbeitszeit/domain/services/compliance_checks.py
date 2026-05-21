from datetime import datetime
from typing import Sequence

from arbeitszeit.domain.entities import TimeBooking
from arbeitszeit.domain.enums import BookingType, ReviewCaseType


def check_break_compliance(day_bookings: Sequence[TimeBooking]) -> list[ReviewCaseType]:
    work_seconds = _net_work_seconds(day_bookings)
    break_seconds = _total_break_seconds(day_bookings)
    flags: list[ReviewCaseType] = []

    if work_seconds > 9 * 3600 and break_seconds < 45 * 60:
        flags.append(ReviewCaseType.POSSIBLE_BREAK_VIOLATION)
    elif work_seconds > 6 * 3600 and break_seconds < 30 * 60:
        flags.append(ReviewCaseType.POSSIBLE_BREAK_VIOLATION)

    return flags


def check_max_hours(day_bookings: Sequence[TimeBooking]) -> list[ReviewCaseType]:
    work_seconds = _net_work_seconds(day_bookings)
    flags: list[ReviewCaseType] = []

    if work_seconds > 10 * 3600:
        flags.append(ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION)
    elif work_seconds > 8 * 3600:
        flags.append(ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION)

    return flags


def check_rest_period(last_go: datetime, next_come: datetime) -> list[ReviewCaseType]:
    rest_seconds = (next_come - last_go).total_seconds()
    if rest_seconds < 11 * 3600:
        return [ReviewCaseType.POSSIBLE_REST_VIOLATION]
    return []


def _net_work_seconds(day_bookings: Sequence[TimeBooking]) -> float:
    work_start: datetime | None = None
    total = 0.0
    for booking in day_bookings:
        if booking.booking_type == BookingType.COME:
            work_start = booking.booked_at
        elif booking.booking_type == BookingType.GO and work_start is not None:
            total += (booking.booked_at - work_start).total_seconds()
            work_start = None
    return total


def _total_break_seconds(day_bookings: Sequence[TimeBooking]) -> float:
    break_start: datetime | None = None
    total = 0.0
    for booking in day_bookings:
        if booking.booking_type == BookingType.BREAK_START:
            break_start = booking.booked_at
        elif booking.booking_type == BookingType.BREAK_END and break_start is not None:
            total += (booking.booked_at - break_start).total_seconds()
            break_start = None
    return total
