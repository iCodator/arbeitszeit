from dataclasses import dataclass
from datetime import date, datetime, time

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
    ScopeType,
    UserRole,
)


@dataclass(frozen=True)
class Employee:
    id: int
    personnel_no: str
    first_name: str
    last_name: str
    is_active: bool


@dataclass(frozen=True)
class UserAccount:
    id: int
    employee_id: int | None
    username: str
    role: UserRole
    is_active: bool


@dataclass(frozen=True)
class RfidCard:
    id: int
    employee_id: int
    uid_hash: str
    status: CardStatus
    valid_from: date
    valid_until: date | None
    replaced_by_card_id: int | None

    def __post_init__(self) -> None:
        if self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("valid_until darf nicht vor valid_from liegen.")


@dataclass(frozen=True)
class TimeBooking:
    id: int
    employee_id: int
    booking_type: BookingType
    booked_at: datetime
    source: BookingSource
    status: BookingStatus
    terminal_id: int | None
    rfid_card_id: int | None
    device_event_id: int | None
    note: str | None


@dataclass(frozen=True)
class WorkScheduleVersion:
    id: int
    scope_type: ScopeType
    scope_employee_id: int | None
    weekday: int
    start_time: time
    end_time: time
    valid_from: date
    valid_until: date | None
    change_origin: ChangeOrigin
    changed_by_user_id: int | None

    def __post_init__(self) -> None:
        if self.scope_type == ScopeType.GLOBAL and self.scope_employee_id is not None:
            raise ValueError(
                "Globale Regelarbeitszeit darf keinen Mitarbeiterbezug haben."
            )
        if self.scope_type == ScopeType.EMPLOYEE and self.scope_employee_id is None:
            raise ValueError(
                "Mitarbeiterbezogene Regelarbeitszeit muss scope_employee_id haben."
            )
        if not (1 <= self.weekday <= 7):
            raise ValueError(
                f"Wochentag {self.weekday} ungültig, muss 1–7 sein."
            )
        if self.start_time >= self.end_time:
            raise ValueError(
                "start_time muss vor end_time liegen."
            )
        if self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("valid_until darf nicht vor valid_from liegen.")


@dataclass(frozen=True)
class ReviewCase:
    id: int
    employee_id: int
    case_type: ReviewCaseType
    severity: ReviewSeverity
    status: ReviewCaseStatus
    description: str
    booking_id: int | None
    created_at: datetime
    closed_at: datetime | None
    closed_by_user_id: int | None
    note: str | None = None

    def __post_init__(self) -> None:
        open_statuses = {ReviewCaseStatus.OPEN, ReviewCaseStatus.IN_REVIEW}
        closed_statuses = {ReviewCaseStatus.RESOLVED, ReviewCaseStatus.CLOSED_WITH_NOTE}
        if self.status in open_statuses:
            if self.closed_at is not None or self.closed_by_user_id is not None:
                raise ValueError("Offener Prüffall darf keine Schließungsdaten haben.")
        elif self.status in closed_statuses:
            if self.closed_at is None or self.closed_by_user_id is None:
                raise ValueError("Geschlossener Prüffall muss Schließungsdaten haben.")


@dataclass(frozen=True)
class Supplement:
    id: int
    employee_id: int
    related_booking_id: int | None
    booking_type: BookingType
    event_at: datetime
    recorded_at: datetime
    reason: str
    recorded_by_user_id: int
    approval_status: ApprovalStatus
    approved_by_user_id: int | None
    approved_at: datetime | None
    rejected_by_user_id: int | None = None
    rejected_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.approval_status == ApprovalStatus.PENDING:
            if self.approved_by_user_id is not None or self.approved_at is not None:
                raise ValueError(
                    "Ausstehender Nachtrag darf keine Freigabedaten haben."
                )
            if self.rejected_by_user_id is not None or self.rejected_at is not None:
                raise ValueError(
                    "Ausstehender Nachtrag darf keine Ablehnungsdaten haben."
                )
        elif self.approval_status == ApprovalStatus.APPROVED:
            if self.approved_by_user_id is None or self.approved_at is None:
                raise ValueError("Genehmigter Nachtrag muss Freigabedaten haben.")
            if self.rejected_by_user_id is not None or self.rejected_at is not None:
                raise ValueError(
                    "Genehmigter Nachtrag darf keine Ablehnungsdaten haben."
                )
        elif self.approval_status == ApprovalStatus.REJECTED:
            if self.rejected_by_user_id is None or self.rejected_at is None:
                raise ValueError("Abgelehnter Nachtrag muss Ablehnungsdaten haben.")
            if self.approved_by_user_id is not None or self.approved_at is not None:
                raise ValueError(
                    "Abgelehnter Nachtrag darf keine Freigabedaten haben."
                )


@dataclass(frozen=True)
class BookingCorrection:
    id: int
    original_booking_id: int
    corrected_by_user_id: int
    reason: str
    old_booking_type: BookingType
    old_booked_at: datetime
    new_booking_type: BookingType
    new_booked_at: datetime
    created_at: datetime


@dataclass(frozen=True)
class AuditLogEntry:
    id: int
    event_type: str
    # object_type ist immer der exakte Tabellenname der betroffenen Entität
    # (z. B. "time_bookings", "supplements", "booking_corrections").
    # Einheitliche Konvention für Auswertungen und Filterung im audit_log.
    object_type: str
    object_id: int
    user_id: int | None
    employee_id: int | None
    event_at: datetime
    details_json: str
