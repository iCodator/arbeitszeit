"""Gesamtmigrations-Test: verifiziert die vollständige Migrationskette 0001–0006.

Historischer Ursprung: Phase 1 (Grundgerüst). Ursprünglich 6 Testfälle für
Migrationen 0001 und 0002. Mit jeder späteren Migration (0003–0006, Phase 4/5)
wurden passende Testfälle ergänzt; der Prüfumfang wuchs auf 12 Tests.

Jeder Testlauf verifiziert den aktuellen Gesamtstand der Migrationskette,
nicht nur den historischen Phase-1-Lieferumfang.
"""

import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Generator

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
def conn(tmp_path: Path) -> Generator[sqlite3.Connection, None, None]:
    db = tmp_path / "test.db"
    connection = open_connection(db)
    yield connection
    connection.close()


def _table_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        """).fetchall()
    return {row[0] for row in rows}


def test_leere_db_wird_vollstaendig_migriert(conn: sqlite3.Connection) -> None:
    executed = run_migrations(conn)

    assert executed == ["0001", "0002", "0003", "0004", "0005", "0006", "0007", "0008", "0009"]
    assert _EXPECTED_TABLES.issubset(_table_names(conn))


def test_erneutes_ausfuehren_ist_idempotent(conn: sqlite3.Connection) -> None:
    run_migrations(conn)
    executed_second = run_migrations(conn)

    assert executed_second == []
    assert _EXPECTED_TABLES.issubset(_table_names(conn))


def test_seed_daten_vorhanden_nach_migration(conn: sqlite3.Connection) -> None:
    run_migrations(conn)

    schedule_rows = conn.execute(
        "SELECT weekday, start_time, end_time " "FROM work_schedule_versions ORDER BY weekday"
    ).fetchall()
    assert len(schedule_rows) == 5

    weekdays = {row[0]: (row[1], row[2]) for row in schedule_rows}
    assert weekdays[1] == ("07:30", "18:00")
    assert weekdays[4] == ("07:30", "14:00")
    assert weekdays[5] == ("07:30", "16:00")

    config_keys = {
        row[0] for row in conn.execute("SELECT config_key FROM system_config").fetchall()
    }
    assert "app.timezone" in config_keys
    assert "backup.nas_enabled" in config_keys


def test_audit_log_enthaelt_seed_eintraege(conn: sqlite3.Connection) -> None:
    run_migrations(conn)

    count = conn.execute("SELECT COUNT(*) FROM audit_log WHERE event_type = 'SEEDED'").fetchone()[0]
    assert count == 9


def test_schema_migrations_enthaelt_genau_die_erwarteten_versionen(
    conn: sqlite3.Connection,
) -> None:
    run_migrations(conn)

    versions = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}
    assert versions == {"0001", "0002", "0003", "0004", "0005", "0006", "0007", "0008", "0009"}


def test_migration_0004_fuegt_neue_spalten_ein(conn: sqlite3.Connection) -> None:
    run_migrations(conn)

    supplement_cols = {row[1] for row in conn.execute("PRAGMA table_info(supplements)").fetchall()}
    assert "rejected_by_user_id" in supplement_cols
    assert "rejected_at" in supplement_cols

    review_cols = {row[1] for row in conn.execute("PRAGMA table_info(review_cases)").fetchall()}
    assert "note" in review_cols


def test_migration_0005_fuegt_device_event_id_ein(conn: sqlite3.Connection) -> None:
    run_migrations(conn)

    tb_cols = {row[1] for row in conn.execute("PRAGMA table_info(time_bookings)").fetchall()}
    assert "device_event_id" in tb_cols

    fk_targets = {
        row[2] for row in conn.execute("PRAGMA foreign_key_list(time_bookings)").fetchall()
    }
    assert "device_events" in fk_targets


def test_migration_0005_erhaelt_time_bookings_foreign_keys_und_indizes(
    conn: sqlite3.Connection,
) -> None:
    run_migrations(conn)

    fk_targets = {
        row[2] for row in conn.execute("PRAGMA foreign_key_list(time_bookings)").fetchall()
    }
    assert {"employees", "rfid_cards", "terminals", "device_events"} == fk_targets

    index_names = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'index' AND tbl_name = 'time_bookings' "
            "AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    }
    assert "idx_time_bookings_employee_booked_at" in index_names
    assert "idx_time_bookings_status_booked_at" in index_names

    ddl = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'time_bookings'"
    ).fetchone()["sql"]
    assert "booking_type IN ('COME', 'GO', 'BREAK_START', 'BREAK_END')" in ddl
    assert "source IN ('TERMINAL', 'MANUAL', 'IMPORT')" in ddl
    assert "'OK'" in ddl and "'OPEN'" in ddl and "'NEEDS_REVIEW'" in ddl


_MIGRATIONS_ROOT = Path(__file__).parents[1] / "migrations"
_MIGRATIONS_UP_TO_0004 = [
    "0001_schema.sql",
    "0002_seed_defaults.sql",
    "0003_cleanup_booking_status.sql",
    "0004_supplement_reject_fields_and_review_note.sql",
]


def test_migration_0005_datensatz_bleibt_erhalten(conn: sqlite3.Connection, tmp_path: Path) -> None:
    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    for fname in _MIGRATIONS_UP_TO_0004:
        shutil.copy(_MIGRATIONS_ROOT / fname, partial_dir / fname)

    run_migrations(conn, migrations_dir=partial_dir)

    conn.execute("BEGIN")
    conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E001', 'Test', 'User', 1, '2025-01-01T00:00:00', '2025-01-01T00:00:00')"
    )
    employee_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.execute(
        "INSERT INTO time_bookings "
        "(employee_id, booking_type, booked_at, source, current_status, created_at) "
        "VALUES (?, 'COME', '2025-01-01T07:30:00+00:00', 'TERMINAL', 'OPEN', "
        "'2025-01-01T07:30:00+00:00')",
        (employee_id,),
    )
    conn.execute("COMMIT")

    run_migrations(conn)  # wendet 0005 an

    row = conn.execute(
        "SELECT device_event_id FROM time_bookings WHERE employee_id = ?",
        (employee_id,),
    ).fetchone()
    assert row is not None
    assert row["device_event_id"] is None


def test_fehlgeschlagene_migration_hinterlaesst_keinen_schema_migrations_eintrag(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    shutil.copy(_MIGRATIONS_ROOT / "0001_schema.sql", partial_dir / "0001_schema.sql")
    run_migrations(conn, migrations_dir=partial_dir)

    # Kaputte Migration nachträglich hinzufügen:
    # employees existiert bereits nach 0001 → OperationalError
    broken = partial_dir / "0002_broken.sql"
    broken.write_text("CREATE TABLE employees (x TEXT);")

    with pytest.raises(sqlite3.OperationalError):
        run_migrations(conn, migrations_dir=partial_dir)

    versions = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}
    assert "0002" not in versions


def test_migration_0006_application_error_event_type_verfuegbar(conn: sqlite3.Connection) -> None:
    run_migrations(conn)

    conn.execute(
        "INSERT INTO system_events "
        "(event_type, source, severity, event_at) "
        "VALUES ('APPLICATION_ERROR', 'test', 'ERROR', '2026-01-01T00:00:00+00:00')"
    )
    row = conn.execute("SELECT event_type FROM system_events WHERE source = 'test'").fetchone()
    assert row["event_type"] == "APPLICATION_ERROR"


def test_migration_0009_fuegt_chain_hash_spalte_hinzu(conn: sqlite3.Connection) -> None:
    run_migrations(conn)

    audit_cols = {row[1] for row in conn.execute("PRAGMA table_info(audit_log)").fetchall()}
    assert "chain_hash" in audit_cols

    conn.execute(
        "INSERT INTO audit_log "
        "(event_type, object_type, object_id, user_id, employee_id, event_at, details_json, chain_hash) "
        "VALUES ('TEST', 'test', 0, NULL, NULL, '2026-01-01T00:00:00+00:00', '{}', 'abc123')"
    )
    row = conn.execute("SELECT chain_hash FROM audit_log WHERE event_type = 'TEST'").fetchone()
    assert row["chain_hash"] == "abc123"


def test_wiederholte_ausfuehrung_erzeugt_keine_doppelten_seed_daten(
    conn: sqlite3.Connection,
) -> None:
    run_migrations(conn)
    run_migrations(conn)

    schedule_count = conn.execute("SELECT COUNT(*) FROM work_schedule_versions").fetchone()[0]
    assert schedule_count == 5

    config_count = conn.execute("SELECT COUNT(*) FROM system_config").fetchone()[0]
    assert config_count == 3
