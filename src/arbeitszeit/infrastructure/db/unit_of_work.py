import sqlite3
from types import TracebackType

from arbeitszeit.infrastructure.db.repositories import (
    SQLiteAuditLogRepository,
    SQLiteBookingCorrectionRepository,
    SQLiteDeviceEventRepository,
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
    # Transaktionssemantik: __exit__ rollt IMMER zurück, sofern kein explizites
    # commit() erfolgt ist. Das gilt auch ohne Exception. Hintergrund: eine
    # vergessene Bestätigung soll nie stillschweigend persistieren.

    def __init__(
        self,
        conn: sqlite3.Connection,
        audit_conn: sqlite3.Connection | None = None,
    ) -> None:
        # conn: Haupt-Verbindung für alle Use-Case-Transaktionen (BEGIN/COMMIT/ROLLBACK).
        #
        # audit_conn: MUSS via open_connection() erzeugt worden sein (isolation_level=None,
        # WAL-Modus, busy_timeout). Niemals manuell mit abweichenden PRAGMAs öffnen,
        # da die Autocommit-Garantie und Locking-Robustheit davon abhängen.
        # Ohne audit_conn fällt das AuditLog auf conn zurück; Einträge vor Rollback gehen verloren.
        self._conn = conn
        self._transaction_open = False
        self.device_event_repo = SQLiteDeviceEventRepository(conn)
        self.employee_repo = SQLiteEmployeeRepository(conn)
        self.user_account_repo = SQLiteUserAccountRepository(conn)
        self.rfid_card_repo = SQLiteRfidCardRepository(conn)
        self.time_booking_repo = SQLiteTimeBookingRepository(conn)
        self.work_schedule_repo = SQLiteWorkScheduleRepository(conn)
        self.review_case_repo = SQLiteReviewCaseRepository(conn)
        self.supplement_repo = SQLiteSupplementRepository(conn)
        self.booking_correction_repo = SQLiteBookingCorrectionRepository(conn)
        self.audit_log_repo = SQLiteAuditLogRepository(conn, audit_conn)
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
        if self._transaction_open:
            self.rollback()
