from dataclasses import dataclass
from datetime import datetime

from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
    BookingType,
    CardStatus,
    ChangeOrigin,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
    UserRole,
)


@dataclass(frozen=True)
class Employee:
    id: int
    personnel_no: str
    full_name: str
    is_active: bool


@dataclass(frozen=True)
class UserAccount:
    id: int
    employee_id: int
    username: str
    role: UserRole
    is_active: bool


@dataclass(frozen=True)
class RfidCard:
    id: int
    employee_id: int
    uid_hash: str
    status: CardStatus
    assigned_at: datetime


@dataclass(frozen=True)
class TimeBooking:
    id: int
    employee_id: int
    booking_type: BookingType
    booked_at: datetime
    source: BookingSource
    status: BookingStatus
    terminal_id: int | None
    device_event_id: int | None


@dataclass(frozen=True)
class WorkScheduleVersion:
    id: int
    weekday: int
    start_time: str
    end_time: str
    valid_from: str
    valid_until: str | None
    change_origin: ChangeOrigin
    changed_by_user_id: int | None


@dataclass(frozen=True)
class ReviewCase:
    id: int
    employee_id: int
    case_type: ReviewCaseType
    severity: ReviewSeverity
    status: ReviewCaseStatus
    booking_id: int | None
    created_at: datetime
    resolved_at: datetime | None


@dataclass(frozen=True)
class Supplement:
    id: int
    employee_id: int
    booking_type: BookingType
    booked_at: datetime
    reason: str
    created_by_user_id: int
    approval_status: ApprovalStatus


@dataclass(frozen=True)
class BookingCorrection:
    id: int
    original_booking_id: int
    corrected_by_user_id: int
    reason: str
    new_booking_type: BookingType | None
    new_booked_at: datetime | None
    created_at: datetime


@dataclass(frozen=True)
class AuditLogEntry:
    id: int
    event_type: str
    performed_by_user_id: int | None
    target_table: str | None
    target_id: int | None
    detail: str | None
    created_at: datetime
