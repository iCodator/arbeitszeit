__version__ = "1.1"

import dataclasses
import sqlite3
from datetime import datetime, timezone

from arbeitszeit.domain.entities import Employee


class SQLiteEmployeeRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, employee: Employee) -> Employee:
        now = datetime.now(timezone.utc).isoformat()
        row = self._conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES (?, ?, ?, 1, ?, ?) RETURNING id",
            (employee.personnel_no, employee.first_name, employee.last_name, now, now),
        ).fetchone()
        return dataclasses.replace(employee, id=row["id"])

    def get_by_id(self, employee_id: int) -> Employee | None:
        row = self._conn.execute(
            "SELECT id, personnel_no, first_name, last_name, active "
            "FROM employees WHERE id = ?",
            (employee_id,),
        ).fetchone()
        return _row_to_employee(row) if row else None

    def get_by_personnel_no(self, personnel_no: str) -> Employee | None:
        row = self._conn.execute(
            "SELECT id, personnel_no, first_name, last_name, active "
            "FROM employees WHERE personnel_no = ?",
            (personnel_no,),
        ).fetchone()
        return _row_to_employee(row) if row else None

    def get_active_by_personnel_no(self, personnel_no: str) -> Employee | None:
        row = self._conn.execute(
            "SELECT id, personnel_no, first_name, last_name, active "
            "FROM employees WHERE personnel_no = ? AND active = 1",
            (personnel_no,),
        ).fetchone()
        return _row_to_employee(row) if row else None

    def deactivate(self, employee_id: int) -> None:
        self._conn.execute(
            "UPDATE employees SET active = 0, updated_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), employee_id),
        )


def _row_to_employee(row: sqlite3.Row) -> Employee:
    return Employee(
        id=row["id"],
        personnel_no=row["personnel_no"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        is_active=bool(row["active"]),
    )
