import json
import sqlite3

from arbeitszeit.domain.entities import BookingCorrection
from arbeitszeit.domain.enums import BookingType

from ._helpers import _parse_dt

# DB schema: time_booking_id, old_values_json, new_values_json, corrected_at
# Entity: original_booking_id, old_booking_type, old_booked_at,
#         new_booking_type, new_booked_at, created_at
_SELECT = (
    "SELECT id, time_booking_id, old_values_json, new_values_json, "
    "reason, corrected_by_user_id, corrected_at FROM booking_corrections"
)


class SQLiteBookingCorrectionRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, correction: BookingCorrection) -> BookingCorrection:
        old_values = json.dumps(
            {
                "booking_type": correction.old_booking_type.value,
                "booked_at": correction.old_booked_at.isoformat(),
            },
            sort_keys=True,
        )
        new_values = json.dumps(
            {
                "booking_type": correction.new_booking_type.value,
                "booked_at": correction.new_booked_at.isoformat(),
            },
            sort_keys=True,
        )
        row = self._conn.execute(
            "INSERT INTO booking_corrections "
            "(time_booking_id, old_values_json, new_values_json, reason, "
            "corrected_by_user_id, corrected_at) "
            "VALUES (?, ?, ?, ?, ?, ?) RETURNING id",
            (
                correction.original_booking_id,
                old_values,
                new_values,
                correction.reason,
                correction.corrected_by_user_id,
                correction.created_at.isoformat(),
            ),
        ).fetchone()
        return BookingCorrection(
            id=row["id"],
            original_booking_id=correction.original_booking_id,
            corrected_by_user_id=correction.corrected_by_user_id,
            reason=correction.reason,
            old_booking_type=correction.old_booking_type,
            old_booked_at=correction.old_booked_at,
            new_booking_type=correction.new_booking_type,
            new_booked_at=correction.new_booked_at,
            created_at=correction.created_at,
        )

    def list_for_booking(self, booking_id: int) -> list[BookingCorrection]:
        rows = self._conn.execute(
            f"{_SELECT} WHERE time_booking_id = ? ORDER BY corrected_at",
            (booking_id,),
        ).fetchall()
        return [_row_to_correction(r) for r in rows]


def _row_to_correction(row: sqlite3.Row) -> BookingCorrection:
    old = json.loads(row["old_values_json"])
    new = json.loads(row["new_values_json"])
    return BookingCorrection(
        id=row["id"],
        original_booking_id=row["time_booking_id"],
        corrected_by_user_id=row["corrected_by_user_id"],
        reason=row["reason"],
        old_booking_type=BookingType(old["booking_type"]),
        old_booked_at=_parse_dt(old["booked_at"]),
        new_booking_type=BookingType(new["booking_type"]),
        new_booked_at=_parse_dt(new["booked_at"]),
        created_at=_parse_dt(row["corrected_at"]),
    )
