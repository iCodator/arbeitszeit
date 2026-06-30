from datetime import date, datetime
from typing import Literal, Protocol

from arbeitszeit.domain.entities import (
    AuditLogEntry,
    BookingCorrection,
    Employee,
    ReviewCase,
    RfidCard,
    Supplement,
    TimeBooking,
    UserAccount,
    WorkScheduleVersion,
)
from arbeitszeit.domain.enums import BookingStatus, ChangeOrigin, ReviewCaseStatus
from arbeitszeit.domain.value_objects import (
    DeviceEventId,
    EmployeeId,
    ReviewCaseId,
    RfidCardId,
    SupplementId,
    TerminalId,
    TimeBookingId,
    UserAccountId,
    WorkScheduleVersionId,
)


class EmployeeRepository(Protocol):
    def get_by_id(self, employee_id: EmployeeId) -> Employee | None: ...
    def get_active_by_personnel_no(self, personnel_no: str) -> Employee | None: ...


class UserAccountRepository(Protocol):
    def get_by_id(self, user_id: UserAccountId) -> UserAccount | None: ...
    def get_by_username(self, username: str) -> UserAccount | None: ...


class RfidCardRepository(Protocol):
    def get_by_uid_hash(self, uid_hash: str) -> RfidCard | None: ...
    def get_active_by_uid_hash(self, uid_hash: str) -> RfidCard | None: ...
    def get_by_id(self, card_id: RfidCardId) -> RfidCard | None: ...


class TimeBookingRepository(Protocol):
    def add(self, booking: TimeBooking) -> TimeBooking: ...
    def get_by_id(self, booking_id: TimeBookingId) -> TimeBooking | None: ...
    def list_for_employee_on_day(self, employee_id: EmployeeId, day: date) -> list[TimeBooking]:
        # Muss aufsteigend nach booked_at sortiert zurückgeben.
        # Compliance-Prüfungen (Pausen, Ruhezeit, Maximalstunden) setzen
        # chronologische Reihenfolge voraus.
        ...

    def list_open_for_employee(self, employee_id: EmployeeId) -> list[TimeBooking]: ...
    def list_between(
        self, employee_id: EmployeeId, from_dt: datetime, to_dt: datetime
    ) -> list[TimeBooking]: ...
    def set_status(
        self,
        booking_id: TimeBookingId,
        status: BookingStatus,
        reason: str | None = None,
        changed_by_user_id: UserAccountId | None = None,
    ) -> None: ...


class WorkScheduleRepository(Protocol):
    def add(self, version: WorkScheduleVersion) -> WorkScheduleVersion: ...
    def close_version(self, version_id: WorkScheduleVersionId, valid_until: date) -> None: ...
    def get_effective(
        self,
        weekday: int,
        on_date: date,
        employee_id: EmployeeId | None = None,
    ) -> WorkScheduleVersion | None: ...
    def list_versions(
        self,
        weekday: int | None = None,
        scope_employee_id: EmployeeId | None = None,
    ) -> list[WorkScheduleVersion]:
        # scope_employee_id=None  → ausschließlich GLOBAL-Versionen
        # scope_employee_id=<id>  → ausschließlich EMPLOYEE-Versionen für diesen MA
        # Niemals beide Scopes gemischt zurückgeben.
        # Rückgabe aufsteigend nach valid_from sortiert.
        ...


class ReviewCaseRepository(Protocol):
    def add(self, case: ReviewCase) -> ReviewCase: ...
    def list_open_for_employee(self, employee_id: EmployeeId) -> list[ReviewCase]: ...
    def resolve(
        self,
        case_id: ReviewCaseId,
        status: Literal[ReviewCaseStatus.RESOLVED, ReviewCaseStatus.CLOSED_WITH_NOTE],
        closed_by_user_id: UserAccountId,
        note: str | None = None,
    ) -> None: ...


class SupplementRepository(Protocol):
    def add(self, supplement: Supplement) -> Supplement: ...
    def get_by_id(self, supplement_id: SupplementId) -> Supplement | None: ...
    def list_pending(self) -> list[Supplement]: ...
    def approve(
        self, supplement_id: SupplementId, approved_by_user_id: UserAccountId, approved_at: datetime
    ) -> None: ...
    def reject(
        self, supplement_id: SupplementId, rejected_by_user_id: UserAccountId, rejected_at: datetime
    ) -> None: ...


class BookingCorrectionRepository(Protocol):
    def add(self, correction: BookingCorrection) -> BookingCorrection: ...
    def list_for_booking(self, booking_id: TimeBookingId) -> list[BookingCorrection]: ...


class AuditLogRepository(Protocol):
    def add(self, entry: AuditLogEntry) -> AuditLogEntry:
        # Implementierungen MÜSSEN Persistenz auch dann garantieren, wenn die
        # aufrufende UnitOfWork-Transaktion nachträglich zurückgerollt wird.
        # Grund: Abweisungen (UnknownCard, InactiveCard) schreiben hier vor
        # dem Rollback — das ist auditpflichtig und darf nicht verloren gehen.
        # SQLite-Implementierung: separate autocommit-Verbindung verwenden.
        ...


class DeviceEventRepository(Protocol):
    def add(
        self,
        event_type: str,
        terminal_id: TerminalId | None,
        rfid_uid_hash: str | None,
        payload_json: str,
        occurred_at: datetime,
    ) -> DeviceEventId:
        # Gibt die neue device_events.id zurück.
        ...


class SystemConfigRepository(Protocol):
    def get_current(self, config_key: str) -> str | None: ...
    def set_current(
        self,
        config_key: str,
        value_json: str,
        change_origin: ChangeOrigin,
        changed_by_user_id: UserAccountId | None,
        changed_at: datetime,
        reason: str | None = None,
    ) -> None: ...
