import sqlite3

from arbeitszeit.domain.entities import Employee


class SQLiteEmployeeRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get_by_id(self, employee_id: int) -> Employee | None:
        row = self._conn.execute(
            "SELECT id, personnel_no, first_name, last_name, active " "FROM employees WHERE id = ?",
            (employee_id,),
        ).fetchone()
        return _row_to_employee(row) if row else None

    def get_active_by_personnel_no(self, personnel_no: str) -> Employee | None:
        row = self._conn.execute(
            "SELECT id, personnel_no, first_name, last_name, active "
            "FROM employees WHERE personnel_no = ? AND active = 1",
            (personnel_no,),
        ).fetchone()
        return _row_to_employee(row) if row else None


def _row_to_employee(row: sqlite3.Row) -> Employee:
    return Employee(
        id=row["id"],
        personnel_no=row["personnel_no"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        is_active=bool(row["active"]),
    )
