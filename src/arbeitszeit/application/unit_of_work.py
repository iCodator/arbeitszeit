from types import TracebackType
from typing import Protocol

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


class UnitOfWork(Protocol):
    employee_repo: EmployeeRepository
    user_account_repo: UserAccountRepository
    rfid_card_repo: RfidCardRepository
    time_booking_repo: TimeBookingRepository
    work_schedule_repo: WorkScheduleRepository
    review_case_repo: ReviewCaseRepository
    supplement_repo: SupplementRepository
    booking_correction_repo: BookingCorrectionRepository
    audit_log_repo: AuditLogRepository
    system_config_repo: SystemConfigRepository
    device_event_repo: DeviceEventRepository

    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
