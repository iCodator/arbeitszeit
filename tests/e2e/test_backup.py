import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.backup import BackupResult, SQLiteBackupService
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations

_NOW = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)


def _make_db(path: Path) -> None:
    conn = open_connection(path)
    run_migrations(conn)
    conn.close()


def _insert_employee(path: Path, personnel_no: str) -> None:
    conn = open_connection(path)
    conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES (?, 'Test', 'User', 1, '2025-01-01', '2025-01-01')",
        (personnel_no,),
    )
    conn.close()


def _count_employees(path: Path) -> int:
    conn = open_connection(path)
    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    conn.close()
    return count


# --- create_local_backup ---


def test_backup_erstellt_datei(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    backup_path = service.create_local_backup(now=_NOW)
    assert backup_path.exists()
    assert backup_path.stat().st_size > 0


def test_backup_dateiname_enthaelt_timestamp(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    backup_path = service.create_local_backup(now=_NOW)
    assert "20250601T080000Z" in backup_path.name


def test_backup_dir_wird_automatisch_angelegt(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    tief = tmp_path / "neu" / "verschachtelt" / "backups"
    service = SQLiteBackupService(db, tief)
    service.create_local_backup(now=_NOW)
    assert tief.exists()


def test_backup_enthaelt_alle_tabellen(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    backup_path = service.create_local_backup(now=_NOW)

    src_conn = open_connection(db)
    bak_conn = open_connection(backup_path)
    src_tables = {r[0] for r in src_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    bak_tables = {r[0] for r in bak_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    src_conn.close()
    bak_conn.close()
    assert src_tables == bak_tables


def test_run_gibt_backup_result_zurueck(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    result = service.run()
    assert isinstance(result, BackupResult)
    assert result.backup_path.exists()
    assert result.size_bytes > 0
    assert result.synced_to_nas is False


# --- restore_from ---


def test_restore_stellt_daten_wieder_her(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    _insert_employee(db, "E001")

    service = SQLiteBackupService(db, tmp_path / "backups")
    backup_path = service.create_local_backup(now=_NOW)

    # Datensatz nach Backup löschen
    conn = open_connection(db)
    conn.execute("DELETE FROM employees WHERE personnel_no = 'E001'")
    conn.close()
    assert _count_employees(db) == 0

    # Restore
    service.restore_from(backup_path)
    assert _count_employees(db) == 1


def test_backup_und_restore_roundtrip_mehrere_datensaetze(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    for i in range(5):
        _insert_employee(db, f"E{i:03d}")

    service = SQLiteBackupService(db, tmp_path / "backups")
    backup_path = service.create_local_backup(now=_NOW)

    # Weitere Einträge nach Backup hinzufügen (sollen nach Restore weg sein)
    _insert_employee(db, "E999")
    assert _count_employees(db) == 6

    service.restore_from(backup_path)
    assert _count_employees(db) == 5


def test_restore_aus_backup_behaelt_schema_migrations(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    backup_path = service.create_local_backup(now=_NOW)

    service.restore_from(backup_path)

    conn = open_connection(db)
    rows = conn.execute(
        "SELECT version FROM schema_migrations ORDER BY version"
    ).fetchall()
    conn.close()
    versions = [r["version"] for r in rows]
    assert "0001" in versions
    assert "0002" in versions
