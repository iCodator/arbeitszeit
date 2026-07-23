__version__ = "1.1"

import sqlite3

from arbeitszeit.domain.entities import AuditLogEntry

_INSERT = (
    "INSERT INTO audit_log "
    "(event_type, object_type, object_id, user_id, employee_id, "
    "event_at, details_json) "
    "VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id"
)


class SQLiteAuditLogRepository:
    def __init__(
        self,
        conn: sqlite3.Connection,
        audit_conn: sqlite3.Connection | None = None,
    ) -> None:
        # audit_conn muss mit isolation_level=None geöffnet sein (open_connection tut das)
        # und darf nie ein BEGIN erhalten. Dann gilt für sqlite3 mit isolation_level=None:
        # Jedes DML-Statement committed automatisch (kein aktiver Transaction-Kontext).
        # SQLiteUnitOfWork ruft BEGIN/COMMIT/ROLLBACK ausschließlich auf conn, nie auf
        # audit_conn – die Autocommit-Garantie ist damit durch die Architektur gesichert.
        # Ohne audit_conn fällt write auf conn zurück: kein Rollback-Schutz.
        self._conn = conn
        self._write_conn = audit_conn if audit_conn is not None else conn

    def _write(self, conn: sqlite3.Connection, entry: AuditLogEntry) -> AuditLogEntry:
        row = conn.execute(
            _INSERT,
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

    def add(self, entry: AuditLogEntry) -> AuditLogEntry:
        return self._write(self._write_conn, entry)

    def add_transactional(self, entry: AuditLogEntry) -> AuditLogEntry:
        # Schreibt via conn (in aktiver Transaktion). Wird bei Rollback rückgängig gemacht.
        # Für Write-Ahead-Einträge, die atomar mit der Buchung committen sollen.
        return self._write(self._conn, entry)
