__version__ = "1.0"

from arbeitszeit.domain.entities import TimeBooking
from arbeitszeit.domain.enums import BookingStatus, BookingType, ReviewSeverity
from arbeitszeit.domain.services.compliance_checks import (
    ComplianceFlag,
    check_break_compliance,
    check_max_hours,
    check_rest_period,
)


def evaluate_booking(
    booking_type: BookingType,
    projected: list[TimeBooking],
    prev_bookings: list[TimeBooking] | None = None,
    extra_flags: list[ComplianceFlag] | None = None,
) -> tuple[BookingStatus, list[ComplianceFlag]]:
    if booking_type in (BookingType.COME, BookingType.BREAK_START):
        return BookingStatus.OPEN, list(extra_flags or [])

    flags = check_break_compliance(projected) + check_max_hours(projected)

    if prev_bookings is not None:
        flags += _check_rest_period_flags(prev_bookings, projected)

    flags += list(extra_flags or [])
    return _flags_to_status(flags), flags


def _check_rest_period_flags(
    prev_bookings: list[TimeBooking],
    projected: list[TimeBooking],
) -> list[ComplianceFlag]:
    last_go = next(
        (b.booked_at for b in reversed(prev_bookings) if b.booking_type == BookingType.GO),
        None,
    )
    first_come = next(
        (b.booked_at for b in projected if b.booking_type == BookingType.COME),
        None,
    )
    if last_go is not None and first_come is not None:
        return check_rest_period(last_go, first_come)
    return []


def _flags_to_status(flags: list[ComplianceFlag]) -> BookingStatus:
    if not flags:
        return BookingStatus.OK
    if any(f.severity == ReviewSeverity.CRITICAL for f in flags):
        return BookingStatus.NEEDS_REVIEW
    return BookingStatus.WARN
