__version__ = "1.1"

from dataclasses import dataclass
from datetime import datetime

from arbeitszeit.domain.enums import BookingStatus, BookingType
from arbeitszeit.domain.value_objects import (
    BookingCorrectionId,
    EmployeeId,
    ReviewCaseId,
    RfidCardId,
    SupplementId,
    TimeBookingId,
    UserAccountId,
    WorkScheduleVersionId,
)


@dataclass(frozen=True, slots=True)
class BookResult:
    booking_id: TimeBookingId
    status: BookingStatus
    follow_up_case_ids: tuple[ReviewCaseId, ...]
    employee_first_name: str
    employee_last_name: str
    booking_type: BookingType
    booked_at: datetime


@dataclass(frozen=True, slots=True)
class SupplementResult:
    supplement_id: SupplementId
    review_case_id: ReviewCaseId | None


@dataclass(frozen=True, slots=True)
class CorrectionResult:
    correction_id: BookingCorrectionId
    updated_booking_id: TimeBookingId
    review_case_ids: list[ReviewCaseId]


@dataclass(frozen=True, slots=True)
class WorkScheduleChangeResult:
    new_version_id: WorkScheduleVersionId
    superseded_version_id: WorkScheduleVersionId | None


@dataclass(frozen=True, slots=True)
class ApproveSupplementResult:
    supplement_id: SupplementId
    booking_id: TimeBookingId
    booking_status: BookingStatus
    follow_up_case_ids: tuple[ReviewCaseId, ...]


@dataclass(frozen=True, slots=True)
class RejectSupplementResult:
    supplement_id: SupplementId
    review_case_id: ReviewCaseId | None


@dataclass(frozen=True, slots=True)
class CreateEmployeeResult:
    employee_id: EmployeeId


@dataclass(frozen=True, slots=True)
class AssignRfidCardResult:
    card_id: RfidCardId


@dataclass(frozen=True, slots=True)
class ReplaceRfidCardResult:
    new_card_id: RfidCardId


@dataclass(frozen=True, slots=True)
class CreateUserAccountResult:
    user_id: UserAccountId


@dataclass(frozen=True, slots=True)
class BootstrapAdminResult:
    user_id: UserAccountId
    username: str
