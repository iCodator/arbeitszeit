import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.system_check import (
    SystemCheckResult,
    run_system_check,
)


def _make_db(tmp_path: Path) -> Path:
    db = tmp_path / "arbeitszeit.db"
    conn = open_connection(db)
    run_migrations(conn)
    # Deployment-spezifische Keys, die setup.py im echten Betrieb setzt:
    for key, value in (
        ("backup.backup_dir", str(tmp_path / "backups")),
        ("export.export_dir", str(tmp_path / "exports")),
    ):
        conn.execute(
            "INSERT INTO system_config "
            "(config_key, config_value_json, version, change_origin, changed_at) "
            "VALUES (?, ?, 1, 'MIGRATION', datetime('now'))",
            (key, json.dumps(value)),
        )
    conn.close()
    return db


def _system_events(db: Path) -> list[dict]:
    conn = open_connection(db)
    rows = conn.execute(
        "SELECT event_type, severity, source, details_json FROM system_events ORDER BY id"
    ).fetchall()
    conn.close()
    return [
        {
            "event_type": r["event_type"],
            "severity": r["severity"],
            "source": r["source"],
            "details": json.loads(r["details_json"]) if r["details_json"] else {},
        }
        for r in rows
    ]


# --- Grundlegende Rückgabe ---


def test_selftest_gibt_system_check_result_zurueck(tmp_path):
    db = _make_db(tmp_path)
    result = run_system_check(db)
    assert isinstance(result, SystemCheckResult)


def test_selftest_ok_bei_korrekt_migrierter_db(tmp_path):
    db = _make_db(tmp_path)
    result = run_system_check(db)
    assert result.overall_ok


def test_selftest_protokolliert_selftest_ok_in_system_events(tmp_path):
    db = _make_db(tmp_path)
    run_system_check(db)
    events = _system_events(db)
    assert any(e["event_type"] == "SELFTEST_OK" for e in events)


def test_selftest_ok_event_hat_source_system_check(tmp_path):
    db = _make_db(tmp_path)
    run_system_check(db)
    events = _system_events(db)
    ok_event = next(e for e in events if e["event_type"] == "SELFTEST_OK")
    assert ok_event["source"] == "system_check"


def test_selftest_ok_event_hat_severity_info(tmp_path):
    db = _make_db(tmp_path)
    run_system_check(db)
    events = _system_events(db)
    ok_event = next(e for e in events if e["event_type"] == "SELFTEST_OK")
    assert ok_event["severity"] == "INFO"


def test_selftest_details_enthalten_alle_pruefbereiche(tmp_path):
    db = _make_db(tmp_path)
    result = run_system_check(db)
    names = {c.name for c in result.checks}
    assert "db_access" in names
    assert "config_keys" in names
    assert "nas_reachability" in names
    assert "fk_consistency" in names
    assert "device_availability" in names


# --- DB-Zugriff ---


def test_selftest_fail_bei_nicht_existierender_db(tmp_path):
    result = run_system_check(tmp_path / "ghost.db")
    assert not result.overall_ok
    db_check = next(c for c in result.checks if c.name == "db_access")
    assert not db_check.ok


def test_selftest_fail_bei_fehlender_migration(tmp_path):
    db = _make_db(tmp_path)
    conn = open_connection(db)
    conn.execute("DELETE FROM schema_migrations WHERE version = '0005'")
    conn.close()
    result = run_system_check(db)
    assert not result.overall_ok
    db_check = next(c for c in result.checks if c.name == "db_access")
    assert not db_check.ok
    assert "0005" in db_check.detail


# --- Konfigurationsprüfung ---


def test_selftest_fail_bei_fehlendem_config_key(tmp_path):
    db = _make_db(tmp_path)
    conn = open_connection(db)
    conn.execute("DELETE FROM system_config WHERE config_key = 'app.timezone'")
    conn.close()
    result = run_system_check(db)
    assert not result.overall_ok
    cfg_check = next(c for c in result.checks if c.name == "config_keys")
    assert not cfg_check.ok
    assert "app.timezone" in cfg_check.detail


def test_selftest_fail_protokolliert_selftest_fail_event(tmp_path):
    db = _make_db(tmp_path)
    conn = open_connection(db)
    conn.execute("DELETE FROM system_config WHERE config_key = 'app.timezone'")
    conn.close()
    run_system_check(db)
    events = _system_events(db)
    assert any(e["event_type"] == "SELFTEST_FAIL" for e in events)


def test_selftest_fail_event_hat_severity_warn(tmp_path):
    db = _make_db(tmp_path)
    conn = open_connection(db)
    conn.execute("DELETE FROM system_config WHERE config_key = 'app.timezone'")
    conn.close()
    run_system_check(db)
    events = _system_events(db)
    fail_event = next(e for e in events if e["event_type"] == "SELFTEST_FAIL")
    assert fail_event["severity"] == "WARN"


# --- FK-Konsistenz ---


def test_selftest_fail_bei_fk_verletzung(tmp_path):
    db = _make_db(tmp_path)
    conn = open_connection(db)
    # FK-Prüfung deaktivieren, um eine verwaiste Referenz einzufügen
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute(
        "INSERT INTO rfid_cards "
        "(uid_hash, employee_id, status, valid_from, created_at) "
        "VALUES ('deadbeef', 9999, 'ACTIVE', '2025-01-01', '2025-01-01')"
    )
    conn.execute("PRAGMA foreign_keys = ON")
    conn.close()
    result = run_system_check(db)
    assert not result.overall_ok
    fk_check = next(c for c in result.checks if c.name == "fk_consistency")
    assert not fk_check.ok


# --- NAS-Prüfung ---


def test_nas_check_uebersprungen_wenn_deaktiviert(tmp_path):
    db = _make_db(tmp_path)
    result = run_system_check(db)
    nas_check = next(c for c in result.checks if c.name == "nas_reachability")
    assert nas_check.ok


def test_nas_check_schlaegt_fehl_bei_nicht_existierendem_pfad(tmp_path):
    db = _make_db(tmp_path)
    conn = open_connection(db)
    next_v = conn.execute(
        "SELECT COALESCE(MAX(version), 0) + 1 FROM system_config "
        "WHERE config_key = 'backup.nas_enabled'"
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO system_config "
        "(config_key, config_value_json, version, change_origin, changed_by_user_id, changed_at) "
        "VALUES ('backup.nas_enabled', 'true', ?, 'MIGRATION', NULL, '2025-01-01')",
        (next_v,),
    )
    next_v2 = conn.execute(
        "SELECT COALESCE(MAX(version), 0) + 1 FROM system_config "
        "WHERE config_key = 'backup.nas_path'"
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO system_config "
        "(config_key, config_value_json, version, change_origin, changed_by_user_id, changed_at) "
        "VALUES ('backup.nas_path', '\"/nonexistent/nas\"', ?, 'MIGRATION', NULL, '2025-01-01')",
        (next_v2,),
    )
    conn.close()
    result = run_system_check(db)
    nas_check = next(c for c in result.checks if c.name == "nas_reachability")
    assert not nas_check.ok


# --- Geräteverfügbarkeit ---


def test_geraete_check_uebersprungen_ohne_pfade(tmp_path):
    db = _make_db(tmp_path)
    result = run_system_check(db)
    dev_check = next(c for c in result.checks if c.name == "device_availability")
    assert dev_check.ok
    assert "übersprungen" in dev_check.detail


def test_geraete_check_schlaegt_fehl_bei_nicht_existierendem_numpad(tmp_path):
    db = _make_db(tmp_path)
    result = run_system_check(db, numpad_path=tmp_path / "dev_numpad_ghost")
    dev_check = next(c for c in result.checks if c.name == "device_availability")
    assert not dev_check.ok
    assert "Numpad" in dev_check.detail


def test_geraete_check_ok_bei_existierender_geraetedatei(tmp_path):
    db = _make_db(tmp_path)
    fake_dev = tmp_path / "fake_numpad"
    fake_dev.write_bytes(b"")
    result = run_system_check(db, numpad_path=fake_dev)
    dev_check = next(c for c in result.checks if c.name == "device_availability")
    assert dev_check.ok
