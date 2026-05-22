from dataclasses import dataclass

from arbeitszeit.domain.enums import BookingStatus


@dataclass(frozen=True, slots=True)
class BookResult:
    booking_id: int
    status: BookingStatus
    follow_up_case_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SupplementResult:
    supplement_id: int
    review_case_id: int | None


@dataclass(frozen=True, slots=True)
class CorrectionResult:
    correction_id: int
    updated_booking_id: int
    review_case_id: int | None


@dataclass(frozen=True, slots=True)
class WorkScheduleChangeResult:
    new_version_id: int
    superseded_version_id: int | None


@dataclass(frozen=True, slots=True)
class ApproveSupplementResult:
    supplement_id: int
    booking_id: int
    booking_status: BookingStatus
    follow_up_case_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class RejectSupplementResult:
    supplement_id: int
    review_case_id: int | None
