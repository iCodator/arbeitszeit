__version__ = "1.2"

import hmac as _hmac
import json as _json
import os as _os
import sqlite3

from arbeitszeit.domain.entities import AuditLogEntry

_INSERT = (
    "INSERT INTO audit_log "
    "(event_type, object_type, object_id, user_id, employee_id, "
    "event_at, details_json, chain_hash) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id"
)

_GENESIS_HASH = "0" * 64


def compute_audit_chain_hash(
    event_type: str,
    event_at_iso: str,
    employee_id: int | None,
    details_json: str,
    prev_hash: str,
    key: bytes,
) -> str:
    """Berechnet den HMAC-SHA256-Kettenhash für einen Audit-Log-Eintrag.

    Wirft ValueError wenn key leer ist.
    Kanonische Eingabe via JSON (sort_keys=True) verhindert Mehrdeutigkeiten.
    """
    if not key:
        raise ValueError("key darf nicht leer sein")
    data = _json.dumps(
        {
            "details_json": details_json,
            "employee_id": employee_id,
            "event_at": event_at_iso,
            "event_type": event_type,
            "prev_hash": prev_hash,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return _hmac.new(key, data.encode("utf-8"), "sha256").hexdigest()


def _get_prev_chain_hash(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT chain_hash FROM audit_log "
        "WHERE chain_hash IS NOT NULL AND chain_hash != '' "
        "ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row["chain_hash"] if row else _GENESIS_HASH


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
        key = _os.environ.get("AUDIT_HMAC_KEY", "").encode("utf-8")
        if key:
            prev_hash = _get_prev_chain_hash(conn)
            chain_hash: str | None = compute_audit_chain_hash(
                event_type=entry.event_type,
                event_at_iso=entry.event_at.isoformat(),
                employee_id=int(entry.employee_id) if entry.employee_id is not None else None,
                details_json=entry.details_json,
                prev_hash=prev_hash,
                key=key,
            )
        else:
            chain_hash = None

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
                chain_hash,
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
