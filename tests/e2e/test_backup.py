import json
import subprocess
import sys
from unittest.mock import Mock
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


def _audit_events(path: Path) -> list[dict]:
    conn = open_connection(path)
    rows = conn.execute(
        "SELECT event_type, details_json FROM audit_log ORDER BY id"
    ).fetchall()
    conn.close()
    return [
        {"event_type": r["event_type"], "details": json.loads(r["details_json"])}
        for r in rows
    ]


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


# --- Fehlerpfade ---


def test_nas_sync_fehler_wirft_called_process_error(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    service.create_local_backup(now=_NOW)

    with pytest.raises(subprocess.CalledProcessError):
        service.sync_to_nas(Path("/nonexistent/nas/path"))


def test_restore_aus_nicht_existierender_datei_wirft_file_not_found(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")

    with pytest.raises(FileNotFoundError):
        service.restore_from(tmp_path / "ghost.db")


def test_restore_aus_beschaedigter_datei_schlaegt_fehl(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")

    corrupt = tmp_path / "corrupt.db"
    corrupt.write_bytes(b"this is not a valid sqlite database file")

    with pytest.raises(Exception):
        service.restore_from(corrupt)


# --- Audit-Log-Verifikation ---


def test_backup_erstellt_audit_eintrag(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    service.create_local_backup(now=_NOW)

    events = _audit_events(db)
    assert any(e["event_type"] == "BACKUP_CREATED" for e in events)


def test_restore_erstellt_audit_eintrag(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    backup_path = service.create_local_backup(now=_NOW)
    service.restore_from(backup_path)

    events = _audit_events(db)
    assert any(e["event_type"] == "RESTORE_COMPLETED" for e in events)


def test_nas_sync_erfolg_erstellt_audit_eintrag(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    service.create_local_backup(now=_NOW)

    nas_dir = tmp_path / "nas"
    nas_dir.mkdir()
    service.sync_to_nas(nas_dir)

    events = _audit_events(db)
    assert any(e["event_type"] == "BACKUP_SYNCED_TO_NAS" for e in events)


def test_nas_sync_audit_eintrag_ohne_rsync(tmp_path, monkeypatch):
    """Isolierter Test: BACKUP_SYNCED_TO_NAS ohne Abhängigkeit von rsync."""
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    service.create_local_backup(now=_NOW)

    monkeypatch.setattr(subprocess, "run", Mock())
    service.sync_to_nas(tmp_path / "nas")

    events = _audit_events(db)
    assert any(e["event_type"] == "BACKUP_SYNCED_TO_NAS" for e in events)


def test_nas_sync_fehler_erstellt_audit_eintrag_mit_cmd_und_stderr(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    _make_db(db)
    service = SQLiteBackupService(db, tmp_path / "backups")
    service.create_local_backup(now=_NOW)

    with pytest.raises(subprocess.CalledProcessError):
        service.sync_to_nas(Path("/nonexistent/nas/path"))

    events = _audit_events(db)
    failed = next(e for e in events if e["event_type"] == "BACKUP_SYNC_FAILED")
    assert failed["details"]["returncode"] != 0
    assert "cmd" in failed["details"]
    assert "stderr" in failed["details"]
