import json
import sqlite3
import sys
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry
from arbeitszeit.domain.value_objects import AuditLogEntryId
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def conn(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    connection = open_connection(db_path)
    run_migrations(connection)
    yield connection
    connection.close()


@pytest.fixture
def audit_conn(
    db_path: Path,
    conn: sqlite3.Connection,  # conn zuerst, damit Migrationen angewendet sind
) -> Generator[sqlite3.Connection, None, None]:
    connection = open_connection(db_path)
    yield connection
    connection.close()


@pytest.fixture
def uow(conn: sqlite3.Connection, audit_conn: sqlite3.Connection) -> SQLiteUnitOfWork:
    return SQLiteUnitOfWork(conn, audit_conn)


# --- Transaktionsverhalten ---


def test_commit_macht_daten_sichtbar(conn: sqlite3.Connection, uow: SQLiteUnitOfWork) -> None:
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E001', 'Test', 'User', 1, '2025-01-01', '2025-01-01')"
        )
        uow.commit()

    count = conn.execute("SELECT COUNT(*) FROM employees WHERE personnel_no = 'E001'").fetchone()[0]
    assert count == 1


def test_rollback_verwirft_daten(conn: sqlite3.Connection, uow: SQLiteUnitOfWork) -> None:
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E002', 'Roll', 'Back', 1, '2025-01-01', '2025-01-01')"
        )
        uow.rollback()

    count = conn.execute("SELECT COUNT(*) FROM employees WHERE personnel_no = 'E002'").fetchone()[0]
    assert count == 0


def test_exception_im_with_block_loest_rollback_aus(
    conn: sqlite3.Connection, uow: SQLiteUnitOfWork
) -> None:
    with pytest.raises(ValueError):
        with uow:
            conn.execute(
                "INSERT INTO employees "
                "(personnel_no, first_name, last_name, active, created_at, updated_at) "
                "VALUES ('E003', 'Ex', 'Ception', 1, '2025-01-01', '2025-01-01')"
            )
            raise ValueError("simulierter Fehler")

    count = conn.execute("SELECT COUNT(*) FROM employees WHERE personnel_no = 'E003'").fetchone()[0]
    assert count == 0


def test_kein_spurious_rollback_nach_commit(
    conn: sqlite3.Connection, uow: SQLiteUnitOfWork
) -> None:
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E004', 'Spu', 'Rious', 1, '2025-01-01', '2025-01-01')"
        )
        uow.commit()
    # __exit__ wird mit exc_type=None aufgerufen → kein Rollback
    # Daten müssen noch da sein
    count = conn.execute("SELECT COUNT(*) FROM employees WHERE personnel_no = 'E004'").fetchone()[0]
    assert count == 1


def test_transaction_open_flag_nach_commit_false(
    conn: sqlite3.Connection, uow: SQLiteUnitOfWork
) -> None:
    with uow:
        uow.commit()
    assert not uow._transaction_open


def test_transaction_open_flag_nach_rollback_false(
    conn: sqlite3.Connection, uow: SQLiteUnitOfWork
) -> None:
    with uow:
        uow.rollback()
    assert not uow._transaction_open


def test_vergessenes_commit_rollt_automatisch_zurueck(
    conn: sqlite3.Connection, uow: SQLiteUnitOfWork
) -> None:
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E005', 'Kein', 'Commit', 1, '2025-01-01', '2025-01-01')"
        )
        # commit() absichtlich weggelassen

    count = conn.execute("SELECT COUNT(*) FROM employees WHERE personnel_no = 'E005'").fetchone()[0]
    assert count == 0


def test_mehrfache_transaktionen_hintereinander(
    conn: sqlite3.Connection, uow: SQLiteUnitOfWork
) -> None:
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E010', 'Erste', 'Transaktion', 1, '2025-01-01', '2025-01-01')"
        )
        uow.commit()

    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E011', 'Zweite', 'Transaktion', 1, '2025-01-01', '2025-01-01')"
        )
        uow.commit()

    count = conn.execute(
        "SELECT COUNT(*) FROM employees WHERE personnel_no IN ('E010', 'E011')"
    ).fetchone()[0]
    assert count == 2


# --- Audit-Log: Persistenz bei Rollback (via audit_conn) ---


def test_audit_log_bleibt_nach_rollback_erhalten(
    conn: sqlite3.Connection, uow: SQLiteUnitOfWork
) -> None:
    entry = AuditLogEntry(
        id=AuditLogEntryId(0),
        event_type=audit_events.BOOKING_REJECTED_UNKNOWN_CARD,
        object_type="rfid_cards",
        object_id=0,
        user_id=None,
        employee_id=None,
        event_at=datetime(2025, 3, 10, 8, 0, tzinfo=timezone.utc),
        details_json=json.dumps({"uid_hash": "abc", "terminal_id": 1}),
    )

    with pytest.raises(ValueError):
        with uow:
            uow.audit_log_repo.add(entry)
            raise ValueError("simulierte Abweisung")

    count = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE event_type = 'BOOKING_REJECTED_UNKNOWN_CARD'"
    ).fetchone()[0]
    assert count == 1, "Audit-Log-Eintrag muss rollback-resistent sein"


def test_audit_log_schreibbar_waehrend_conn_nur_liest(
    conn: sqlite3.Connection, uow: SQLiteUnitOfWork
) -> None:
    # Spiegelt das Produktionsszenario in book_time.py:
    # Bei Abweisung (UnknownCard/InactiveCard) führt conn ausschließlich SELECTs aus
    # und hat keinen WRITE-Lock. WAL-Modus erlaubt audit_conn zu schreiben,
    # weil SHARED + ein paralleler Writer koexistieren können.
    # SQLite-Einschränkung: Hat conn bereits einen WRITE-Lock (INSERT/UPDATE),
    # würde audit_conn blockiert – das passiert in den Ablehnungspfaden aber nicht.
    entry = AuditLogEntry(
        id=AuditLogEntryId(0),
        event_type=audit_events.BOOKING_REJECTED_INACTIVE_CARD,
        object_type="rfid_cards",
        object_id=1,
        user_id=None,
        employee_id=None,
        event_at=datetime(2025, 3, 10, 8, 0, tzinfo=timezone.utc),
        details_json=json.dumps({"card_id": 1, "card_status": "INACTIVE"}),
    )

    with pytest.raises(ValueError):
        with uow:
            # Nur READ auf conn (kein WRITE-Lock-Upgrade) – wie bei Kartenabweisung
            conn.execute("SELECT COUNT(*) FROM employees").fetchone()
            # audit_conn schreibt parallel: gelingt dank WAL + SHARED-Lock auf conn
            uow.audit_log_repo.add(entry)
            raise ValueError("Abweisung simuliert")

    audit_count = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE event_type = 'BOOKING_REJECTED_INACTIVE_CARD'"
    ).fetchone()[0]
    assert audit_count == 1
