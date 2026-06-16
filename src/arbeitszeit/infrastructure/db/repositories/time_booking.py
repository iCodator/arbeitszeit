import sqlite3
from datetime import date, datetime, timedelta, timezone

from arbeitszeit.domain.entities import TimeBooking
from arbeitszeit.domain.enums import BookingSource, BookingStatus, BookingType
from arbeitszeit.domain.errors import NotFoundError

from ._helpers import _parse_dt

_SELECT = (
    "SELECT id, employee_id, rfid_card_id, booking_type, booked_at, source, "
    "terminal_id, device_event_id, current_status, note FROM time_bookings"
)


class SQLiteTimeBookingRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, booking: TimeBooking) -> TimeBooking:
        row = self._conn.execute(
            "INSERT INTO time_bookings "
            "(employee_id, rfid_card_id, booking_type, booked_at, source, "
            "terminal_id, device_event_id, current_status, note, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (
                booking.employee_id,
                booking.rfid_card_id,
                booking.booking_type.value,
                booking.booked_at.isoformat(),
                booking.source.value,
                booking.terminal_id,
                booking.device_event_id,
                booking.status.value,
                booking.note,
                datetime.now(timezone.utc).isoformat(),
            ),
        ).fetchone()
        return TimeBooking(
            id=row["id"],
            employee_id=booking.employee_id,
            booking_type=booking.booking_type,
            booked_at=booking.booked_at,
            source=booking.source,
            status=booking.status,
            terminal_id=booking.terminal_id,
            rfid_card_id=booking.rfid_card_id,
            device_event_id=booking.device_event_id,
            note=booking.note,
        )

    def get_by_id(self, booking_id: int) -> TimeBooking | None:
        row = self._conn.execute(f"{_SELECT} WHERE id = ?", (booking_id,)).fetchone()
        return _row_to_booking(row) if row else None

    def list_for_employee_on_day(
        self, employee_id: int, day: date
    ) -> list[TimeBooking]:
        # `day` muss ein UTC-Kalendertag sein, konsistent mit UTC-normalisierten booked_at-Werten.
        # Die Application-Schicht ist verantwortlich für die Normalisierung vor dem Aufruf.
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        next_day = day_start + timedelta(days=1)
        rows = self._conn.execute(
            f"{_SELECT} WHERE employee_id = ? AND booked_at >= ? AND booked_at < ? "
            "ORDER BY booked_at",
            (employee_id, day_start.isoformat(), next_day.isoformat()),
        ).fetchall()
        return [_row_to_booking(r) for r in rows]

    def list_open_for_employee(self, employee_id: int) -> list[TimeBooking]:
        rows = self._conn.execute(
            f"{_SELECT} WHERE employee_id = ? AND current_status = 'OPEN'",
            (employee_id,),
        ).fetchall()
        return [_row_to_booking(r) for r in rows]

    def list_between(
        self, employee_id: int, from_dt: datetime, to_dt: datetime
    ) -> list[TimeBooking]:
        rows = self._conn.execute(
            f"{_SELECT} WHERE employee_id = ? AND booked_at >= ? AND booked_at <= ? "
            "ORDER BY booked_at",
            (employee_id, from_dt.isoformat(), to_dt.isoformat()),
        ).fetchall()
        return [_row_to_booking(r) for r in rows]

    def set_status(
        self,
        booking_id: int,
        status: BookingStatus,
        reason: str | None = None,
        changed_by_user_id: int | None = None,
    ) -> None:
        row = self._conn.execute(
            "SELECT current_status FROM time_bookings WHERE id = ?",
            (booking_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError(f"TimeBooking {booking_id} nicht gefunden.")
        old_status = row["current_status"]
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "UPDATE time_bookings SET current_status = ? WHERE id = ?",
            (status.value, booking_id),
        )
        self._conn.execute(
            "INSERT INTO booking_status_history "
            "(time_booking_id, old_status, new_status, reason, changed_by_user_id, changed_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (booking_id, old_status, status.value, reason, changed_by_user_id, now),
        )


def _row_to_booking(row: sqlite3.Row) -> TimeBooking:
    return TimeBooking(
        id=row["id"],
        employee_id=row["employee_id"],
        booking_type=BookingType(row["booking_type"]),
        booked_at=_parse_dt(row["booked_at"]),
        source=BookingSource(row["source"]),
        status=BookingStatus(row["current_status"]),
        terminal_id=row["terminal_id"],
        rfid_card_id=row["rfid_card_id"],
        device_event_id=row["device_event_id"],
        note=row["note"],
    )
