from dataclasses import dataclass
from datetime import date, datetime, time

from arbeitszeit.domain.enums import BookingSource, BookingType, ChangeOrigin, ScopeType
from arbeitszeit.domain.value_objects import (
    DeviceEventId,
    EmployeeId,
    SupplementId,
    TerminalId,
    TimeBookingId,
    UserAccountId,
)


@dataclass(frozen=True, slots=True)
class BookCommand:
    uid_hash: str
    terminal_id: TerminalId
    booking_type: BookingType
    booked_at: datetime
    device_event_id: DeviceEventId | None
    source: BookingSource = BookingSource.TERMINAL


@dataclass(frozen=True, slots=True)
class CreateSupplementCommand:
    employee_id: EmployeeId
    related_booking_id: TimeBookingId | None
    booking_type: BookingType
    event_at: datetime
    recorded_at: datetime
    reason: str
    recorded_by_user_id: UserAccountId


@dataclass(frozen=True, slots=True)
class CreateCorrectionCommand:
    original_booking_id: TimeBookingId
    corrected_by_user_id: UserAccountId
    reason: str
    new_booking_type: BookingType
    new_booked_at: datetime


@dataclass(frozen=True, slots=True)
class ApproveSupplementCommand:
    supplement_id: SupplementId
    approving_user_id: UserAccountId


@dataclass(frozen=True, slots=True)
class RejectSupplementCommand:
    supplement_id: SupplementId
    rejected_by_user_id: UserAccountId
    reason: str


@dataclass(frozen=True, slots=True)
class ChangeWorkScheduleCommand:
    scope_type: ScopeType
    scope_employee_id: EmployeeId | None
    weekday: int
    start_time: time
    end_time: time
    valid_from: date
    change_origin: ChangeOrigin
    changed_by_user_id: UserAccountId | None
    reason: str | None
