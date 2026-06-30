from dataclasses import dataclass

from arbeitszeit.domain.enums import BookingStatus
from arbeitszeit.domain.value_objects import (
    BookingCorrectionId,
    ReviewCaseId,
    SupplementId,
    TimeBookingId,
    WorkScheduleVersionId,
)


@dataclass(frozen=True, slots=True)
class BookResult:
    booking_id: TimeBookingId
    status: BookingStatus
    follow_up_case_ids: tuple[ReviewCaseId, ...]


@dataclass(frozen=True, slots=True)
class SupplementResult:
    supplement_id: SupplementId
    review_case_id: ReviewCaseId | None


@dataclass(frozen=True, slots=True)
class CorrectionResult:
    correction_id: BookingCorrectionId
    updated_booking_id: TimeBookingId
    review_case_id: ReviewCaseId | None


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
