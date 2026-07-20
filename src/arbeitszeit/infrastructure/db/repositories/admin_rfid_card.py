__version__ = "1.0"

import sqlite3
from datetime import datetime, timezone

from arbeitszeit.domain.entities import AdminRfidCard
from arbeitszeit.domain.value_objects import AdminRfidCardId


class SQLiteAdminRfidCardRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, uid_hash: str, label: str | None) -> AdminRfidCard:
        now = datetime.now(timezone.utc).isoformat()
        row = self._conn.execute(
            "INSERT INTO admin_rfid_cards (uid_hash, label, active, created_at) "
            "VALUES (?, ?, 1, ?) RETURNING id",
            (uid_hash, label, now),
        ).fetchone()
        return AdminRfidCard(
            id=AdminRfidCardId(row["id"]),
            uid_hash=uid_hash,
            label=label,
            active=True,
            created_at=datetime.fromisoformat(now),
        )

    def get_active_by_uid_hash(self, uid_hash: str) -> AdminRfidCard | None:
        row = self._conn.execute(
            "SELECT id, uid_hash, label, active, created_at "
            "FROM admin_rfid_cards WHERE uid_hash = ? AND active = 1",
            (uid_hash,),
        ).fetchone()
        return _row_to_card(row) if row else None

    def deactivate(self, card_id: AdminRfidCardId) -> None:
        self._conn.execute(
            "UPDATE admin_rfid_cards SET active = 0 WHERE id = ?",
            (card_id,),
        )

    def list_all(self) -> list[AdminRfidCard]:
        rows = self._conn.execute(
            "SELECT id, uid_hash, label, active, created_at "
            "FROM admin_rfid_cards ORDER BY id"
        ).fetchall()
        return [_row_to_card(r) for r in rows]


def _row_to_card(row: sqlite3.Row) -> AdminRfidCard:
    return AdminRfidCard(
        id=AdminRfidCardId(row["id"]),
        uid_hash=row["uid_hash"],
        label=row["label"],
        active=bool(row["active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )
