import dataclasses
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

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
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingStatus,
    CardStatus,
    ChangeOrigin,
    ReviewCaseStatus,
    ScopeType,
)
from arbeitszeit.domain.ports.repositories import (
    AuditLogRepository,
    BookingCorrectionRepository,
    EmployeeRepository,
    ReviewCaseRepository,
    RfidCardRepository,
    SupplementRepository,
    SystemConfigRepository,
    TimeBookingRepository,
    UserAccountRepository,
    WorkScheduleRepository,
)


class FakeEmployeeRepository:
    def __init__(self) -> None:
        self._store: dict[int, Employee] = {}
        self._next_id = 1

    def add(self, employee: Employee) -> Employee:
        new = dataclasses.replace(employee, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self._store.get(employee_id)

    def get_active_by_personnel_no(self, personnel_no: str) -> Employee | None:
        return next(
            (e for e in self._store.values() if e.personnel_no == personnel_no and e.is_active),
            None,
        )


class FakeUserAccountRepository:
    def __init__(self) -> None:
        self._store: dict[int, UserAccount] = {}
        self._next_id = 1

    def add(self, account: UserAccount) -> UserAccount:
        new = dataclasses.replace(account, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def get_by_id(self, user_id: int) -> UserAccount | None:
        return self._store.get(user_id)

    def get_by_username(self, username: str) -> UserAccount | None:
        return next(
            (a for a in self._store.values() if a.username == username),
            None,
        )


class FakeRfidCardRepository:
    def __init__(self) -> None:
        self._store: dict[int, RfidCard] = {}
        self._next_id = 1

    def add(self, card: RfidCard) -> RfidCard:
        new = dataclasses.replace(card, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def get_by_uid_hash(self, uid_hash: str) -> RfidCard | None:
        return next(
            (c for c in self._store.values() if c.uid_hash == uid_hash),
            None,
        )

    def get_active_by_uid_hash(self, uid_hash: str) -> RfidCard | None:
        return next(
            (c for c in self._store.values() if c.uid_hash == uid_hash and c.status == CardStatus.ACTIVE),
            None,
        )

    def get_by_id(self, card_id: int) -> RfidCard | None:
        return self._store.get(card_id)


class FakeTimeBookingRepository:
    def __init__(self) -> None:
        self._store: dict[int, TimeBooking] = {}
        self._next_id = 1

    def add(self, booking: TimeBooking) -> TimeBooking:
        new = dataclasses.replace(booking, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def get_by_id(self, booking_id: int) -> TimeBooking | None:
        return self._store.get(booking_id)

    def list_for_employee_on_day(self, employee_id: int, day: date) -> list[TimeBooking]:
        return [
            b for b in self._store.values()
            if b.employee_id == employee_id and b.booked_at.date() == day
        ]

    def list_open_for_employee(self, employee_id: int) -> list[TimeBooking]:
        return [
            b for b in self._store.values()
            if b.employee_id == employee_id and b.status == BookingStatus.OPEN
        ]

    def list_between(self, employee_id: int, from_dt: datetime, to_dt: datetime) -> list[TimeBooking]:
        return [
            b for b in self._store.values()
            if b.employee_id == employee_id and from_dt <= b.booked_at <= to_dt
        ]

    def set_status(
        self,
        booking_id: int,
        status: BookingStatus,
        reason: str | None = None,
        changed_by_user_id: int | None = None,
    ) -> None:
        existing = self._store[booking_id]
        self._store[booking_id] = dataclasses.replace(existing, status=status)


class FakeWorkScheduleRepository:
    def __init__(self) -> None:
        self._store: dict[int, WorkScheduleVersion] = {}
        self._next_id = 1

    def add(self, version: WorkScheduleVersion) -> WorkScheduleVersion:
        new = dataclasses.replace(version, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def close_version(self, version_id: int, valid_until: date) -> None:
        existing = self._store[version_id]
        # dataclasses.replace triggers __post_init__ → valid_until < valid_from raises ValueError
        self._store[version_id] = dataclasses.replace(existing, valid_until=valid_until)

    def get_effective(
        self,
        weekday: int,
        on_date: date,
        employee_id: int | None = None,
    ) -> WorkScheduleVersion | None:
        # EMPLOYEE-Scope hat Vorrang vor GLOBAL
        if employee_id is not None:
            employee_version = next(
                (
                    v for v in self._store.values()
                    if v.weekday == weekday
                    and v.scope_type == ScopeType.EMPLOYEE
                    and v.scope_employee_id == employee_id
                    and v.valid_from <= on_date
                    and (v.valid_until is None or v.valid_until >= on_date)
                ),
                None,
            )
            if employee_version is not None:
                return employee_version
        return next(
            (
                v for v in self._store.values()
                if v.weekday == weekday
                and v.scope_type == ScopeType.GLOBAL
                and v.valid_from <= on_date
                and (v.valid_until is None or v.valid_until >= on_date)
            ),
            None,
        )

    def list_versions(
        self,
        weekday: int | None = None,
        scope_employee_id: int | None = None,
    ) -> list[WorkScheduleVersion]:
        # scope_employee_id=None filtert auf GLOBAL (scope_employee_id IS NULL)
        result = [v for v in self._store.values() if v.scope_employee_id == scope_employee_id]
        if weekday is not None:
            result = [v for v in result if v.weekday == weekday]
        return result


class FakeReviewCaseRepository:
    def __init__(self) -> None:
        self._store: dict[int, ReviewCase] = {}
        self._next_id = 1

    def add(self, case: ReviewCase) -> ReviewCase:
        new = dataclasses.replace(case, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def list_open_for_employee(self, employee_id: int) -> list[ReviewCase]:
        return [
            c for c in self._store.values()
            if c.employee_id == employee_id
            and c.status in (ReviewCaseStatus.OPEN, ReviewCaseStatus.IN_REVIEW)
        ]

    def resolve(
        self,
        case_id: int,
        status: Literal[ReviewCaseStatus.RESOLVED, ReviewCaseStatus.CLOSED_WITH_NOTE],
        closed_by_user_id: int,
        note: str | None = None,
    ) -> None:
        existing = self._store[case_id]
        self._store[case_id] = dataclasses.replace(
            existing,
            status=status,
            closed_at=datetime.now(timezone.utc),
            closed_by_user_id=closed_by_user_id,
        )


class FakeSupplementRepository:
    def __init__(self) -> None:
        self._store: dict[int, Supplement] = {}
        self._next_id = 1

    def add(self, supplement: Supplement) -> Supplement:
        new = dataclasses.replace(supplement, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def get_by_id(self, supplement_id: int) -> Supplement | None:
        return self._store.get(supplement_id)

    def list_pending(self) -> list[Supplement]:
        return [s for s in self._store.values() if s.approval_status == ApprovalStatus.PENDING]

    def approve(self, supplement_id: int, approved_by_user_id: int, approved_at: datetime) -> None:
        existing = self._store[supplement_id]
        self._store[supplement_id] = dataclasses.replace(
            existing,
            approval_status=ApprovalStatus.APPROVED,
            approved_by_user_id=approved_by_user_id,
            approved_at=approved_at,
        )

    def reject(self, supplement_id: int, rejected_by_user_id: int, rejected_at: datetime) -> None:
        existing = self._store[supplement_id]
        self._store[supplement_id] = dataclasses.replace(
            existing,
            approval_status=ApprovalStatus.REJECTED,
            approved_by_user_id=rejected_by_user_id,
            approved_at=rejected_at,
        )


class FakeBookingCorrectionRepository:
    def __init__(self) -> None:
        self._store: dict[int, BookingCorrection] = {}
        self._next_id = 1

    def add(self, correction: BookingCorrection) -> BookingCorrection:
        new = dataclasses.replace(correction, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def list_for_booking(self, booking_id: int) -> list[BookingCorrection]:
        return [c for c in self._store.values() if c.original_booking_id == booking_id]


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self._store: dict[int, AuditLogEntry] = {}
        self._next_id = 1

    def add(self, entry: AuditLogEntry) -> AuditLogEntry:
        new = dataclasses.replace(entry, id=self._next_id)
        self._store[new.id] = new
        self._next_id += 1
        return new

    @property
    def entries(self) -> list[AuditLogEntry]:
        return list(self._store.values())


class FakeSystemConfigRepository:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get_current(self, config_key: str) -> str | None:
        return self._store.get(config_key)

    def set_current(
        self,
        config_key: str,
        value_json: str,
        change_origin: ChangeOrigin,
        changed_by_user_id: int | None,
        changed_at: datetime,
        reason: str | None = None,
    ) -> None:
        self._store[config_key] = value_json


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.employee_repo = FakeEmployeeRepository()
        self.user_account_repo = FakeUserAccountRepository()
        self.rfid_card_repo = FakeRfidCardRepository()
        self.time_booking_repo = FakeTimeBookingRepository()
        self.work_schedule_repo = FakeWorkScheduleRepository()
        self.review_case_repo = FakeReviewCaseRepository()
        self.supplement_repo = FakeSupplementRepository()
        self.booking_correction_repo = FakeBookingCorrectionRepository()
        self.audit_log_repo = FakeAuditLogRepository()
        self.system_config_repo = FakeSystemConfigRepository()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        if exc_type is not None:
            self.rollback()


# Typ-Kompatibilitätsprüfung: Fakes müssen die Repository-Protokolle erfüllen
def _check_protocol_compliance() -> None:
    _: EmployeeRepository = FakeEmployeeRepository()
    _: UserAccountRepository = FakeUserAccountRepository()  # type: ignore[no-redef]
    _: RfidCardRepository = FakeRfidCardRepository()  # type: ignore[no-redef]
    _: TimeBookingRepository = FakeTimeBookingRepository()  # type: ignore[no-redef]
    _: WorkScheduleRepository = FakeWorkScheduleRepository()  # type: ignore[no-redef]
    _: ReviewCaseRepository = FakeReviewCaseRepository()  # type: ignore[no-redef]
    _: SupplementRepository = FakeSupplementRepository()  # type: ignore[no-redef]
    _: BookingCorrectionRepository = FakeBookingCorrectionRepository()  # type: ignore[no-redef]
    _: AuditLogRepository = FakeAuditLogRepository()  # type: ignore[no-redef]
    _: SystemConfigRepository = FakeSystemConfigRepository()  # type: ignore[no-redef]
