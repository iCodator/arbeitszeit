import sqlite3

from arbeitszeit.domain.entities import RfidCard
from arbeitszeit.domain.enums import CardStatus

from ._helpers import _parse_date


class SQLiteRfidCardRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get_by_uid_hash(self, uid_hash: str) -> RfidCard | None:
        row = self._conn.execute(
            "SELECT id, uid_hash, employee_id, status, valid_from, valid_until, "
            "replaced_by_card_id FROM rfid_cards WHERE uid_hash = ?",
            (uid_hash,),
        ).fetchone()
        return _row_to_card(row) if row else None

    def get_active_by_uid_hash(self, uid_hash: str) -> RfidCard | None:
        row = self._conn.execute(
            "SELECT id, uid_hash, employee_id, status, valid_from, valid_until, "
            "replaced_by_card_id FROM rfid_cards WHERE uid_hash = ? AND status = 'ACTIVE'",
            (uid_hash,),
        ).fetchone()
        return _row_to_card(row) if row else None

    def get_by_id(self, card_id: int) -> RfidCard | None:
        row = self._conn.execute(
            "SELECT id, uid_hash, employee_id, status, valid_from, valid_until, "
            "replaced_by_card_id FROM rfid_cards WHERE id = ?",
            (card_id,),
        ).fetchone()
        return _row_to_card(row) if row else None


def _row_to_card(row: sqlite3.Row) -> RfidCard:
    return RfidCard(
        id=row["id"],
        uid_hash=row["uid_hash"],
        employee_id=row["employee_id"],
        status=CardStatus(row["status"]),
        valid_from=_parse_date(row["valid_from"]),
        valid_until=_parse_date(row["valid_until"]) if row["valid_until"] else None,
        replaced_by_card_id=row["replaced_by_card_id"],
    )
