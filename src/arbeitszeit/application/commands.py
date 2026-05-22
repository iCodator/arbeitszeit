from dataclasses import dataclass
from datetime import date, datetime, time

from arbeitszeit.domain.enums import BookingSource, BookingType, ChangeOrigin, ScopeType


@dataclass(frozen=True, slots=True)
class BookCommand:
    uid_hash: str
    terminal_id: int
    booking_type: BookingType
    booked_at: datetime
    device_event_id: int | None
    source: BookingSource = BookingSource.TERMINAL


@dataclass(frozen=True, slots=True)
class CreateSupplementCommand:
    employee_id: int
    related_booking_id: int | None
    booking_type: BookingType
    event_at: datetime
    recorded_at: datetime
    reason: str
    recorded_by_user_id: int


@dataclass(frozen=True, slots=True)
class CreateCorrectionCommand:
    original_booking_id: int
    corrected_by_user_id: int
    reason: str
    new_booking_type: BookingType
    new_booked_at: datetime


@dataclass(frozen=True, slots=True)
class ApproveSupplementCommand:
    supplement_id: int
    approved_by_user_id: int


@dataclass(frozen=True, slots=True)
class RejectSupplementCommand:
    supplement_id: int
    rejected_by_user_id: int
    reason: str


@dataclass(frozen=True, slots=True)
class ChangeWorkScheduleCommand:
    scope_type: ScopeType
    scope_employee_id: int | None
    weekday: int
    start_time: time
    end_time: time
    valid_from: date
    change_origin: ChangeOrigin
    changed_by_user_id: int | None
    reason: str | None
