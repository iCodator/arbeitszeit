import sqlite3
from datetime import datetime

from arbeitszeit.domain.enums import ChangeOrigin


class SQLiteSystemConfigRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get_current(self, config_key: str) -> str | None:
        row = self._conn.execute(
            "SELECT config_value_json FROM system_config "
            "WHERE config_key = ? ORDER BY version DESC LIMIT 1",
            (config_key,),
        ).fetchone()
        return row["config_value_json"] if row else None

    def set_current(
        self,
        config_key: str,
        value_json: str,
        change_origin: ChangeOrigin,
        changed_by_user_id: int | None,
        changed_at: datetime,
        reason: str | None = None,
    ) -> None:
        next_version = self._conn.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 FROM system_config WHERE config_key = ?",
            (config_key,),
        ).fetchone()[0]
        self._conn.execute(
            "INSERT INTO system_config "
            "(config_key, config_value_json, version, change_origin, "
            "changed_by_user_id, changed_at, reason) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                config_key,
                value_json,
                next_version,
                change_origin.value,
                changed_by_user_id,
                changed_at.isoformat(),
                reason,
            ),
        )
