import sqlite3

from arbeitszeit.domain.entities import UserAccount
from arbeitszeit.domain.enums import UserRole


class SQLiteUserAccountRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get_by_id(self, user_id: int) -> UserAccount | None:
        row = self._conn.execute(
            "SELECT id, employee_id, username, role, active "
            "FROM user_accounts WHERE id = ?",
            (user_id,),
        ).fetchone()
        return _row_to_user_account(row) if row else None

    def add(
        self,
        username: str,
        password_hash: str,
        role: UserRole,
        employee_id: int | None,
        now: str,
    ) -> int:
        row = self._conn.execute(
            "INSERT INTO user_accounts "
            "(username, password_hash, role, employee_id, active, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 1, ?, ?) RETURNING id",
            (username, password_hash, role.value, employee_id, now, now),
        ).fetchone()
        return int(row["id"])

    def get_by_username(self, username: str) -> UserAccount | None:
        row = self._conn.execute(
            "SELECT id, employee_id, username, role, active "
            "FROM user_accounts WHERE username = ?",
            (username,),
        ).fetchone()
        return _row_to_user_account(row) if row else None


def _row_to_user_account(row: sqlite3.Row) -> UserAccount:
    return UserAccount(
        id=row["id"],
        employee_id=row["employee_id"],
        username=row["username"],
        role=UserRole(row["role"]),
        is_active=bool(row["active"]),
    )
