import sqlite3
from datetime import datetime

from arbeitszeit.domain.entities import Supplement
from arbeitszeit.domain.enums import ApprovalStatus, BookingType
from arbeitszeit.domain.errors import NotFoundError

from ._helpers import _parse_dt

# DB: related_time_booking_id → entity: related_booking_id
_SELECT = (
    "SELECT id, employee_id, related_time_booking_id, booking_type, event_at, "
    "recorded_at, reason, recorded_by_user_id, approval_status, "
    "approved_by_user_id, approved_at, rejected_by_user_id, rejected_at "
    "FROM supplements"
)


class SQLiteSupplementRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, supplement: Supplement) -> Supplement:
        row = self._conn.execute(
            "INSERT INTO supplements "
            "(employee_id, related_time_booking_id, booking_type, event_at, "
            "recorded_at, reason, recorded_by_user_id, approval_status, "
            "approved_by_user_id, approved_at, rejected_by_user_id, rejected_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (
                supplement.employee_id,
                supplement.related_booking_id,
                supplement.booking_type.value,
                supplement.event_at.isoformat(),
                supplement.recorded_at.isoformat(),
                supplement.reason,
                supplement.recorded_by_user_id,
                supplement.approval_status.value,
                supplement.approved_by_user_id,
                supplement.approved_at.isoformat() if supplement.approved_at else None,
                supplement.rejected_by_user_id,
                supplement.rejected_at.isoformat() if supplement.rejected_at else None,
            ),
        ).fetchone()
        return Supplement(
            id=row["id"],
            employee_id=supplement.employee_id,
            related_booking_id=supplement.related_booking_id,
            booking_type=supplement.booking_type,
            event_at=supplement.event_at,
            recorded_at=supplement.recorded_at,
            reason=supplement.reason,
            recorded_by_user_id=supplement.recorded_by_user_id,
            approval_status=supplement.approval_status,
            approved_by_user_id=supplement.approved_by_user_id,
            approved_at=supplement.approved_at,
            rejected_by_user_id=supplement.rejected_by_user_id,
            rejected_at=supplement.rejected_at,
        )

    def get_by_id(self, supplement_id: int) -> Supplement | None:
        row = self._conn.execute(f"{_SELECT} WHERE id = ?", (supplement_id,)).fetchone()
        return _row_to_supplement(row) if row else None

    def list_pending(self) -> list[Supplement]:
        rows = self._conn.execute(
            f"{_SELECT} WHERE approval_status = 'PENDING' ORDER BY recorded_at",
        ).fetchall()
        return [_row_to_supplement(r) for r in rows]

    def approve(
        self, supplement_id: int, approved_by_user_id: int, approved_at: datetime
    ) -> None:
        cursor = self._conn.execute(
            "UPDATE supplements SET approval_status = 'APPROVED', "
            "approved_by_user_id = ?, approved_at = ? WHERE id = ?",
            (approved_by_user_id, approved_at.isoformat(), supplement_id),
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Supplement {supplement_id} nicht gefunden.")

    def reject(
        self, supplement_id: int, rejected_by_user_id: int, rejected_at: datetime
    ) -> None:
        cursor = self._conn.execute(
            "UPDATE supplements SET approval_status = 'REJECTED', "
            "rejected_by_user_id = ?, rejected_at = ? WHERE id = ?",
            (rejected_by_user_id, rejected_at.isoformat(), supplement_id),
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Supplement {supplement_id} nicht gefunden.")


def _row_to_supplement(row: sqlite3.Row) -> Supplement:
    return Supplement(
        id=row["id"],
        employee_id=row["employee_id"],
        related_booking_id=row["related_time_booking_id"],
        booking_type=BookingType(row["booking_type"]),
        event_at=_parse_dt(row["event_at"]),
        recorded_at=_parse_dt(row["recorded_at"]),
        reason=row["reason"],
        recorded_by_user_id=row["recorded_by_user_id"],
        approval_status=ApprovalStatus(row["approval_status"]),
        approved_by_user_id=row["approved_by_user_id"],
        approved_at=_parse_dt(row["approved_at"]) if row["approved_at"] else None,
        rejected_by_user_id=row["rejected_by_user_id"],
        rejected_at=_parse_dt(row["rejected_at"]) if row["rejected_at"] else None,
    )
