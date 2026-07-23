import dataclasses
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import Any, Literal

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
    BookingType,
    CardStatus,
    ChangeOrigin,
    ReviewCaseStatus,
    ScopeType,
    UserRole,
)
from arbeitszeit.domain.ports.repositories import (
    AuditLogRepository,
    BookingCorrectionRepository,
    DeviceEventRepository,
    EmployeeRepository,
    ReviewCaseRepository,
    RfidCardRepository,
    SupplementRepository,
    SystemConfigRepository,
    TimeBookingRepository,
    UserAccountRepository,
    WorkScheduleRepository,
)
from arbeitszeit.domain.value_objects import (
    AuditLogEntryId,
    BookingCorrectionId,
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


class FakeDeviceEventRepository:
    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._next_id = 1

    def add(
        self,
        event_type: str,
        terminal_id: TerminalId | None,
        rfid_uid_hash: str | None,
        payload_json: str,
        occurred_at: datetime,
    ) -> DeviceEventId:
        new_id = DeviceEventId(self._next_id)
        self._records.append(
            {
                "id": new_id,
                "event_type": event_type,
                "terminal_id": terminal_id,
                "rfid_uid_hash": rfid_uid_hash,
                "payload_json": payload_json,
                "occurred_at": occurred_at,
            }
        )
        self._next_id += 1
        return new_id


class FakeEmployeeRepository:
    def __init__(self) -> None:
        self._store: dict[int, Employee] = {}
        self._next_id = 1

    def add(self, employee: Employee) -> Employee:
        new = dataclasses.replace(employee, id=EmployeeId(self._next_id))
        self._store[new.id] = new
        self._next_id += 1
        return new

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self._store.get(employee_id)

    def get_by_personnel_no(self, personnel_no: str) -> Employee | None:
        return next(
            (e for e in self._store.values() if e.personnel_no == personnel_no),
            None,
        )

    def get_active_by_personnel_no(self, personnel_no: str) -> Employee | None:
        return next(
            (e for e in self._store.values() if e.personnel_no == personnel_no and e.is_active),
            None,
        )

    def deactivate(self, employee_id: int) -> None:
        existing = self._store[employee_id]
        self._store[employee_id] = dataclasses.replace(existing, is_active=False)


class FakeUserAccountRepository:
    def __init__(self) -> None:
        self._store: dict[int, UserAccount] = {}
        self._next_id = 1

    def add(self, account: UserAccount, password_hash: str = "") -> UserAccount:
        new = dataclasses.replace(account, id=UserAccountId(self._next_id))
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

    def deactivate(self, user_id: int) -> None:
        existing = self._store[user_id]
        self._store[user_id] = dataclasses.replace(existing, is_active=False)

    def reactivate(self, user_id: int) -> None:
        existing = self._store[user_id]
        self._store[user_id] = dataclasses.replace(existing, is_active=True)

    def set_role(self, user_id: int, role: UserRole) -> None:
        existing = self._store[user_id]
        self._store[user_id] = dataclasses.replace(existing, role=role)

    def has_active_admin(self) -> bool:
        return any(
            a.role == UserRole.ADMIN and a.is_active for a in self._store.values()
        )

    def has_other_active_admin(self, user_id: int) -> bool:
        return any(
            a.role == UserRole.ADMIN and a.is_active and a.id != user_id
            for a in self._store.values()
        )


class FakeRfidCardRepository:
    def __init__(self) -> None:
        self._store: dict[int, RfidCard] = {}
        self._next_id = 1

    def add(self, card: RfidCard) -> RfidCard:
        new = dataclasses.replace(card, id=RfidCardId(self._next_id))
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
            (
                c
                for c in self._store.values()
                if c.uid_hash == uid_hash and c.status == CardStatus.ACTIVE
            ),
            None,
        )

    def get_by_id(self, card_id: int) -> RfidCard | None:
        return self._store.get(card_id)

    def set_status(
        self,
        card_id: int,
        status: CardStatus,
        replaced_by_card_id: RfidCardId | None = None,
        valid_until: date | None = None,
    ) -> None:
        existing = self._store[card_id]
        self._store[card_id] = dataclasses.replace(
            existing,
            status=status,
            replaced_by_card_id=replaced_by_card_id,
            valid_until=valid_until,
        )


class FakeTimeBookingRepository:
    def __init__(self) -> None:
        self._store: dict[int, TimeBooking] = {}
        self._next_id = 1

    def add(self, booking: TimeBooking) -> TimeBooking:
        new = dataclasses.replace(booking, id=TimeBookingId(self._next_id))
        self._store[new.id] = new
        self._next_id += 1
        return new

    def get_by_id(self, booking_id: int) -> TimeBooking | None:
        return self._store.get(booking_id)

    def list_for_employee_on_day(self, employee_id: int, day: date) -> list[TimeBooking]:
        return sorted(
            (
                b
                for b in self._store.values()
                if b.employee_id == employee_id and b.booked_at.date() == day
            ),
            key=lambda b: b.booked_at,
        )

    def list_open_for_employee(self, employee_id: int) -> list[TimeBooking]:
        return [
            b
            for b in self._store.values()
            if b.employee_id == employee_id and b.status == BookingStatus.OPEN
        ]

    def list_between(
        self, employee_id: int, from_dt: datetime, to_dt: datetime
    ) -> list[TimeBooking]:
        return sorted(
            (
                b
                for b in self._store.values()
                if b.employee_id == employee_id and from_dt <= b.booked_at < to_dt
            ),
            key=lambda b: b.booked_at,
        )

    def set_status(
        self,
        booking_id: int,
        status: BookingStatus,
        reason: str | None = None,
        changed_by_user_id: int | None = None,
    ) -> None:
        existing = self._store[booking_id]
        self._store[booking_id] = dataclasses.replace(existing, status=status)

    def update(
        self,
        booking_id: int,
        new_booking_type: BookingType,
        new_booked_at: datetime,
    ) -> None:
        existing = self._store[booking_id]
        self._store[booking_id] = dataclasses.replace(
            existing, booking_type=new_booking_type, booked_at=new_booked_at
        )


class FakeWorkScheduleRepository:
    def __init__(self) -> None:
        self._store: dict[int, WorkScheduleVersion] = {}
        self._next_id = 1

    def add(self, version: WorkScheduleVersion) -> WorkScheduleVersion:
        new = dataclasses.replace(version, id=WorkScheduleVersionId(self._next_id))
        self._store[new.id] = new
        self._next_id += 1
        return new

    def close_version(self, version_id: int, valid_until: date) -> None:
        existing = self._store[version_id]
        self._store[version_id] = dataclasses.replace(existing, valid_until=valid_until)

    def get_effective(
        self,
        weekday: int,
        on_date: date,
        employee_id: int | None = None,
    ) -> WorkScheduleVersion | None:
        def _matches(v: WorkScheduleVersion) -> bool:
            return (
                v.weekday == weekday
                and v.valid_from <= on_date
                and (v.valid_until is None or v.valid_until >= on_date)
            )

        if employee_id is not None:
            candidates = sorted(
                (
                    v
                    for v in self._store.values()
                    if _matches(v)
                    and v.scope_type == ScopeType.EMPLOYEE
                    and v.scope_employee_id == employee_id
                ),
                key=lambda v: v.valid_from,
                reverse=True,
            )
            if candidates:
                return candidates[0]

        candidates = sorted(
            (v for v in self._store.values() if _matches(v) and v.scope_type == ScopeType.GLOBAL),
            key=lambda v: v.valid_from,
            reverse=True,
        )
        return candidates[0] if candidates else None

    def list_versions(
        self,
        weekday: int | None = None,
        scope_employee_id: int | None = None,
    ) -> list[WorkScheduleVersion]:
        scope_type = ScopeType.EMPLOYEE if scope_employee_id is not None else ScopeType.GLOBAL
        result = [
            v
            for v in self._store.values()
            if v.scope_type == scope_type and v.scope_employee_id == scope_employee_id
        ]
        if weekday is not None:
            result = [v for v in result if v.weekday == weekday]
        return sorted(result, key=lambda v: v.valid_from)


class FakeReviewCaseRepository:
    def __init__(self) -> None:
        self._store: dict[int, ReviewCase] = {}
        self._next_id = 1

    def add(self, case: ReviewCase) -> ReviewCase:
        new = dataclasses.replace(case, id=ReviewCaseId(self._next_id))
        self._store[new.id] = new
        self._next_id += 1
        return new

    def list_open_for_employee(self, employee_id: int) -> list[ReviewCase]:
        return [
            c
            for c in self._store.values()
            if c.employee_id == employee_id
            and c.status in (ReviewCaseStatus.OPEN, ReviewCaseStatus.IN_REVIEW)
        ]

    def resolve(
        self,
        case_id: int,
        status: Literal[ReviewCaseStatus.RESOLVED, ReviewCaseStatus.CLOSED_WITH_NOTE],
        closed_by_user_id: UserAccountId,
        note: str | None = None,
    ) -> None:
        existing = self._store[case_id]
        self._store[case_id] = dataclasses.replace(
            existing,
            status=status,
            closed_at=datetime.now(timezone.utc),
            closed_by_user_id=closed_by_user_id,
            note=note,
        )


class FakeSupplementRepository:
    def __init__(self) -> None:
        self._store: dict[int, Supplement] = {}
        self._next_id = 1

    def add(self, supplement: Supplement) -> Supplement:
        new = dataclasses.replace(supplement, id=SupplementId(self._next_id))
        self._store[new.id] = new
        self._next_id += 1
        return new

    def get_by_id(self, supplement_id: int) -> Supplement | None:
        return self._store.get(supplement_id)

    def list_pending(self) -> list[Supplement]:
        return [s for s in self._store.values() if s.approval_status == ApprovalStatus.PENDING]

    def approve(
        self, supplement_id: int, approved_by_user_id: UserAccountId, approved_at: datetime
    ) -> None:
        existing = self._store[supplement_id]
        self._store[supplement_id] = dataclasses.replace(
            existing,
            approval_status=ApprovalStatus.APPROVED,
            approved_by_user_id=approved_by_user_id,
            approved_at=approved_at,
        )

    def reject(
        self, supplement_id: int, rejected_by_user_id: UserAccountId, rejected_at: datetime
    ) -> None:
        existing = self._store[supplement_id]
        self._store[supplement_id] = dataclasses.replace(
            existing,
            approval_status=ApprovalStatus.REJECTED,
            rejected_by_user_id=rejected_by_user_id,
            rejected_at=rejected_at,
        )


class FakeBookingCorrectionRepository:
    def __init__(self) -> None:
        self._store: dict[int, BookingCorrection] = {}
        self._next_id = 1

    def add(self, correction: BookingCorrection) -> BookingCorrection:
        new = dataclasses.replace(correction, id=BookingCorrectionId(self._next_id))
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
        new = dataclasses.replace(entry, id=AuditLogEntryId(self._next_id))
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
        self.device_event_repo = FakeDeviceEventRepository()
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
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if not self.committed:
            self.rollback()


# Typ-Kompatibilitätsprüfung: Fakes müssen die Repository-Protokolle erfüllen
def _check_protocol_compliance() -> None:
    _dev: DeviceEventRepository = FakeDeviceEventRepository()
    _emp: EmployeeRepository = FakeEmployeeRepository()
    _usr: UserAccountRepository = FakeUserAccountRepository()
    _rfi: RfidCardRepository = FakeRfidCardRepository()
    _tbk: TimeBookingRepository = FakeTimeBookingRepository()
    _wsc: WorkScheduleRepository = FakeWorkScheduleRepository()
    _rvc: ReviewCaseRepository = FakeReviewCaseRepository()
    _sup: SupplementRepository = FakeSupplementRepository()
    _bco: BookingCorrectionRepository = FakeBookingCorrectionRepository()
    _aud: AuditLogRepository = FakeAuditLogRepository()
    _sys: SystemConfigRepository = FakeSystemConfigRepository()
