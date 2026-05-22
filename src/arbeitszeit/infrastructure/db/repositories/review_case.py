import sqlite3
from datetime import datetime, timezone
from typing import Literal

from arbeitszeit.domain.entities import ReviewCase
from arbeitszeit.domain.enums import ReviewCaseStatus, ReviewCaseType, ReviewSeverity

from ._helpers import _parse_dt

# DB: time_booking_id → entity: booking_id
# DB: detected_at     → entity: created_at
_SELECT = (
    "SELECT id, employee_id, time_booking_id, case_type, status, severity, "
    "detected_at, description, closed_at, closed_by_user_id, note "
    "FROM review_cases"
)


class SQLiteReviewCaseRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, case: ReviewCase) -> ReviewCase:
        row = self._conn.execute(
            "INSERT INTO review_cases "
            "(employee_id, time_booking_id, case_type, status, severity, "
            "detected_at, description, closed_at, closed_by_user_id, note) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (
                case.employee_id,
                case.booking_id,
                case.case_type.value,
                case.status.value,
                case.severity.value,
                case.created_at.isoformat(),
                case.description,
                case.closed_at.isoformat() if case.closed_at else None,
                case.closed_by_user_id,
                case.note,
            ),
        ).fetchone()
        return ReviewCase(
            id=row["id"],
            employee_id=case.employee_id,
            case_type=case.case_type,
            severity=case.severity,
            status=case.status,
            description=case.description,
            booking_id=case.booking_id,
            created_at=case.created_at,
            closed_at=case.closed_at,
            closed_by_user_id=case.closed_by_user_id,
            note=case.note,
        )

    def list_open_for_employee(self, employee_id: int) -> list[ReviewCase]:
        rows = self._conn.execute(
            f"{_SELECT} WHERE employee_id = ? AND status IN ('OPEN', 'IN_REVIEW')",
            (employee_id,),
        ).fetchall()
        return [_row_to_case(r) for r in rows]

    def resolve(
        self,
        case_id: int,
        status: Literal[ReviewCaseStatus.RESOLVED, ReviewCaseStatus.CLOSED_WITH_NOTE],
        closed_by_user_id: int,
        note: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "UPDATE review_cases "
            "SET status = ?, closed_at = ?, closed_by_user_id = ?, note = ? "
            "WHERE id = ?",
            (status.value, now, closed_by_user_id, note, case_id),
        )


def _row_to_case(row: sqlite3.Row) -> ReviewCase:
    return ReviewCase(
        id=row["id"],
        employee_id=row["employee_id"],
        case_type=ReviewCaseType(row["case_type"]),
        severity=ReviewSeverity(row["severity"]),
        status=ReviewCaseStatus(row["status"]),
        description=row["description"],
        booking_id=row["time_booking_id"],
        created_at=_parse_dt(row["detected_at"]),
        closed_at=_parse_dt(row["closed_at"]) if row["closed_at"] else None,
        closed_by_user_id=row["closed_by_user_id"],
        note=row["note"],
    )
