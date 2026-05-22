import sqlite3
from types import TracebackType


class SQLiteUnitOfWork:
    """UnitOfWork gegen eine SQLite-Verbindung (isolation_level=None).

    Repository-Attribute werden in Phase 4 Schritt 4 eingebunden.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._transaction_open = False

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
        # Rollback nur wenn noch eine Transaktion offen ist.
        # Nach commit() ist _transaction_open False → kein spurious ROLLBACK.
        if exc_type is not None and self._transaction_open:
            self.rollback()
