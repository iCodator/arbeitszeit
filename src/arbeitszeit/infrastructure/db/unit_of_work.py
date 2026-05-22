import sqlite3
from types import TracebackType

from arbeitszeit.infrastructure.db.repositories import (
    SQLiteAuditLogRepository,
    SQLiteBookingCorrectionRepository,
    SQLiteEmployeeRepository,
    SQLiteReviewCaseRepository,
    SQLiteRfidCardRepository,
    SQLiteSupplementRepository,
    SQLiteSystemConfigRepository,
    SQLiteTimeBookingRepository,
    SQLiteUserAccountRepository,
    SQLiteWorkScheduleRepository,
)


class SQLiteUnitOfWork:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._transaction_open = False
        self.employee_repo = SQLiteEmployeeRepository(conn)
        self.user_account_repo = SQLiteUserAccountRepository(conn)
        self.rfid_card_repo = SQLiteRfidCardRepository(conn)
        self.time_booking_repo = SQLiteTimeBookingRepository(conn)
        self.work_schedule_repo = SQLiteWorkScheduleRepository(conn)
        self.review_case_repo = SQLiteReviewCaseRepository(conn)
        self.supplement_repo = SQLiteSupplementRepository(conn)
        self.booking_correction_repo = SQLiteBookingCorrectionRepository(conn)
        self.audit_log_repo = SQLiteAuditLogRepository(conn)
        self.system_config_repo = SQLiteSystemConfigRepository(conn)

    def __enter__(self) -> "SQLiteUnitOfWork":
        self._conn.execute("BEGIN")
        self._transaction_open = True
        return self

    def commit(self) -> None:
        self._conn.execute("COMMIT")
        self._transaction_open = False

    def rollback(self) -> None:
        self._conn.execute("ROLLBACK")
        self._transaction_open = False

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # Jede noch offene Transaktion wird zurückgerollt – mit oder ohne Exception.
        # Nur ein explizites commit() schliesst die Transaktion ohne Rollback.
        if self._transaction_open:
            self.rollback()
