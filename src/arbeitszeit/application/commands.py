__version__ = "1.1"

from dataclasses import dataclass
from datetime import date, datetime, time

from arbeitszeit.domain.enums import BookingSource, BookingType, ChangeOrigin, ScopeType, UserRole
from arbeitszeit.domain.value_objects import (
    DeviceEventId,
    EmployeeId,
    RfidCardId,
    SupplementId,
    TerminalId,
    TimeBookingId,
    UserAccountId,
)


@dataclass(frozen=True, slots=True)
class BookCommand:
    uid_hash: str
    terminal_id: TerminalId
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


# --- Mitarbeiterverwaltung ---

@dataclass(frozen=True, slots=True)
class CreateEmployeeCommand:
    acting_user_id: UserAccountId
    personnel_no: str
    first_name: str
    last_name: str


@dataclass(frozen=True, slots=True)
class DeactivateEmployeeCommand:
    acting_user_id: UserAccountId
    employee_id: EmployeeId


# --- RFID-Kartenverwaltung ---

@dataclass(frozen=True, slots=True)
class AssignRfidCardCommand:
    acting_user_id: UserAccountId
    employee_id: EmployeeId
    uid_hash: str


@dataclass(frozen=True, slots=True)
class ReplaceRfidCardCommand:
    acting_user_id: UserAccountId
    old_card_id: RfidCardId
    uid_hash: str


@dataclass(frozen=True, slots=True)
class DeactivateRfidCardCommand:
    acting_user_id: UserAccountId
    card_id: RfidCardId


# --- Benutzerkontenverwaltung ---

@dataclass(frozen=True, slots=True)
class CreateUserAccountCommand:
    acting_user_id: UserAccountId
    username: str
    password_hash: str
    role: UserRole
    employee_id: EmployeeId | None = None


@dataclass(frozen=True, slots=True)
class DeactivateUserAccountCommand:
    acting_user_id: UserAccountId
    target_user_id: UserAccountId


@dataclass(frozen=True, slots=True)
class ReactivateUserAccountCommand:
    acting_user_id: UserAccountId
    target_user_id: UserAccountId


@dataclass(frozen=True, slots=True)
class ChangeUserRoleCommand:
    acting_user_id: UserAccountId
    target_user_id: UserAccountId
    new_role: UserRole


@dataclass(frozen=True, slots=True)
class BootstrapAdminCommand:
    username: str
    password_hash: str
