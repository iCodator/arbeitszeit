import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations

_EXPECTED_TABLES = {
    "schema_migrations",
    "employees",
    "user_accounts",
    "rfid_cards",
    "terminals",
    "time_bookings",
    "booking_status_history",
    "booking_corrections",
    "supplements",
    "review_cases",
    "review_case_actions",
    "work_schedule_versions",
    "system_config",
    "device_events",
    "system_events",
    "audit_log",
}


@pytest.fixture
def conn(tmp_path):
    db = tmp_path / "test.db"
    connection = open_connection(db)
    yield connection
    connection.close()


def _table_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        """
    ).fetchall()
    return {row[0] for row in rows}


def test_leere_db_wird_vollstaendig_migriert(conn):
    executed = run_migrations(conn)

    assert executed == ["0001", "0002", "0003", "0004", "0005"]
    assert _EXPECTED_TABLES.issubset(_table_names(conn))


def test_erneutes_ausfuehren_ist_idempotent(conn):
    run_migrations(conn)
    executed_second = run_migrations(conn)

    assert executed_second == []
    assert _EXPECTED_TABLES.issubset(_table_names(conn))


def test_seed_daten_vorhanden_nach_migration(conn):
    run_migrations(conn)

    schedule_rows = conn.execute(
        "SELECT weekday, start_time, end_time "
        "FROM work_schedule_versions ORDER BY weekday"
    ).fetchall()
    assert len(schedule_rows) == 5

    weekdays = {row[0]: (row[1], row[2]) for row in schedule_rows}
    assert weekdays[1] == ("07:30", "18:00")
    assert weekdays[4] == ("07:30", "14:00")
    assert weekdays[5] == ("07:30", "16:00")

    config_keys = {
        row[0]
        for row in conn.execute("SELECT config_key FROM system_config").fetchall()
    }
    assert "app.timezone" in config_keys
    assert "backup.nas_enabled" in config_keys


def test_audit_log_enthaelt_seed_eintraege(conn):
    run_migrations(conn)

    count = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE event_type = 'SEEDED'"
    ).fetchone()[0]
    assert count == 9


def test_schema_migrations_enthaelt_genau_die_erwarteten_versionen(conn):
    run_migrations(conn)

    versions = {
        row[0]
        for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
    }
    assert versions == {"0001", "0002", "0003", "0004", "0005"}


def test_migration_0004_fuegt_neue_spalten_ein(conn):
    run_migrations(conn)

    supplement_cols = {
        row[1]
        for row in conn.execute("PRAGMA table_info(supplements)").fetchall()
    }
    assert "rejected_by_user_id" in supplement_cols
    assert "rejected_at" in supplement_cols

    review_cols = {
        row[1]
        for row in conn.execute("PRAGMA table_info(review_cases)").fetchall()
    }
    assert "note" in review_cols


def test_migration_0005_fuegt_device_event_id_ein(conn):
    run_migrations(conn)

    tb_cols = {
        row[1]
        for row in conn.execute("PRAGMA table_info(time_bookings)").fetchall()
    }
    assert "device_event_id" in tb_cols

    fk_targets = {
        row[2]
        for row in conn.execute("PRAGMA foreign_key_list(time_bookings)").fetchall()
    }
    assert "device_events" in fk_targets


def test_wiederholte_ausfuehrung_erzeugt_keine_doppelten_seed_daten(conn):
    run_migrations(conn)
    run_migrations(conn)

    schedule_count = conn.execute(
        "SELECT COUNT(*) FROM work_schedule_versions"
    ).fetchone()[0]
    assert schedule_count == 5

    config_count = conn.execute(
        "SELECT COUNT(*) FROM system_config"
    ).fetchone()[0]
    assert config_count == 4
