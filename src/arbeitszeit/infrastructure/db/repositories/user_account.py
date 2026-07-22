__version__ = "1.1"

import dataclasses
import sqlite3
from datetime import datetime, timezone

from arbeitszeit.domain.entities import UserAccount
from arbeitszeit.domain.enums import UserRole


class SQLiteUserAccountRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, account: UserAccount, password_hash: str) -> UserAccount:
        now = datetime.now(timezone.utc).isoformat()
        row = self._conn.execute(
            "INSERT INTO user_accounts "
            "(username, password_hash, role, employee_id, active, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 1, ?, ?) RETURNING id",
            (account.username, password_hash, account.role.value, account.employee_id, now, now),
        ).fetchone()
        return dataclasses.replace(account, id=row["id"])

    def get_by_id(self, user_id: int) -> UserAccount | None:
        row = self._conn.execute(
            "SELECT id, employee_id, username, role, active "
            "FROM user_accounts WHERE id = ?",
            (user_id,),
        ).fetchone()
        return _row_to_user_account(row) if row else None

    def get_by_username(self, username: str) -> UserAccount | None:
        row = self._conn.execute(
            "SELECT id, employee_id, username, role, active "
            "FROM user_accounts WHERE username = ?",
            (username,),
        ).fetchone()
        return _row_to_user_account(row) if row else None

    def deactivate(self, user_id: int) -> None:
        self._conn.execute(
            "UPDATE user_accounts SET active = 0, updated_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), user_id),
        )

    def reactivate(self, user_id: int) -> None:
        self._conn.execute(
            "UPDATE user_accounts SET active = 1, updated_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), user_id),
        )

    def set_role(self, user_id: int, role: UserRole) -> None:
        self._conn.execute(
            "UPDATE user_accounts SET role = ?, updated_at = ? WHERE id = ?",
            (role.value, datetime.now(timezone.utc).isoformat(), user_id),
        )

    def has_active_admin(self) -> bool:
        row = self._conn.execute(
            "SELECT COUNT(*) FROM user_accounts WHERE role = 'ADMIN' AND active = 1"
        ).fetchone()
        return bool(row[0])

    def has_other_active_admin(self, user_id: int) -> bool:
        row = self._conn.execute(
            "SELECT COUNT(*) FROM user_accounts "
            "WHERE role = 'ADMIN' AND active = 1 AND id != ?",
            (user_id,),
        ).fetchone()
        return bool(row[0])


def _row_to_user_account(row: sqlite3.Row) -> UserAccount:
    return UserAccount(
        id=row["id"],
        employee_id=row["employee_id"],
        username=row["username"],
        role=UserRole(row["role"]),
        is_active=bool(row["active"]),
    )
