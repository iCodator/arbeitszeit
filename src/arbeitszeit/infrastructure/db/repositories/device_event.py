import sqlite3
from datetime import datetime


class SQLiteDeviceEventRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(
        self,
        event_type: str,
        terminal_id: int | None,
        rfid_uid_hash: str | None,
        payload_json: str,
        occurred_at: datetime,
    ) -> int:
        row = self._conn.execute(
            "INSERT INTO device_events "
            "(event_type, terminal_id, rfid_uid_hash, payload_json, occurred_at) "
            "VALUES (?, ?, ?, ?, ?) RETURNING id",
            (
                event_type,
                terminal_id,
                rfid_uid_hash,
                payload_json,
                occurred_at.isoformat(),
            ),
        ).fetchone()
        return int(row["id"])
