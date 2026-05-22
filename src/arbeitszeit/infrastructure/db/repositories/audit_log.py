import sqlite3

from arbeitszeit.domain.entities import AuditLogEntry


class SQLiteAuditLogRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, entry: AuditLogEntry) -> AuditLogEntry:
        row = self._conn.execute(
            "INSERT INTO audit_log "
            "(event_type, object_type, object_id, user_id, employee_id, "
            "event_at, details_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (
                entry.event_type,
                entry.object_type,
                entry.object_id,
                entry.user_id,
                entry.employee_id,
                entry.event_at.isoformat(),
                entry.details_json,
            ),
        ).fetchone()
        return AuditLogEntry(
            id=row["id"],
            event_type=entry.event_type,
            object_type=entry.object_type,
            object_id=entry.object_id,
            user_id=entry.user_id,
            employee_id=entry.employee_id,
            event_at=entry.event_at,
            details_json=entry.details_json,
        )
