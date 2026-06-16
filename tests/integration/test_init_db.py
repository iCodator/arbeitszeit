"""Integrationstests für scripts/init_db.py — Setup-Check-Verhalten."""

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import ChangeOrigin
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.repositories import SQLiteSystemConfigRepository

_SCRIPTS_DIR = Path(__file__).parents[2] / "scripts"


def _load_init_db():
    spec = importlib.util.spec_from_file_location(
        "init_db", _SCRIPTS_DIR / "init_db.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _migrierte_db(tmp_path: Path) -> Path:
    db = tmp_path / "arbeitszeit.db"
    conn = open_connection(db)
    run_migrations(conn)
    conn.close()
    return db


def _setze_deployment_keys(db: Path, tmp_path: Path) -> None:
    conn = open_connection(db)
    config = SQLiteSystemConfigRepository(conn)
    now = datetime.now(timezone.utc)
    for key, val in (
        ("backup.backup_dir", str(tmp_path / "backups")),
        ("export.export_dir", str(tmp_path / "exports")),
    ):
        config.set_current(
            key, json.dumps(val), ChangeOrigin.MIGRATION, None, now, "test"
        )
    conn.close()


# --- setup_vollstaendig ---


def test_setup_vollstaendig_false_nach_migration_ohne_setup(tmp_path):
    db = _migrierte_db(tmp_path)
    mod = _load_init_db()
    assert mod.setup_vollstaendig(db) is False


def test_setup_vollstaendig_true_nach_vollstaendigem_setup(tmp_path):
    db = _migrierte_db(tmp_path)
    _setze_deployment_keys(db, tmp_path)
    mod = _load_init_db()
    assert mod.setup_vollstaendig(db) is True


def test_setup_vollstaendig_false_wenn_nur_ein_key_gesetzt(tmp_path):
    db = _migrierte_db(tmp_path)
    conn = open_connection(db)
    SQLiteSystemConfigRepository(conn).set_current(
        "backup.backup_dir",
        json.dumps(str(tmp_path / "backups")),
        ChangeOrigin.MIGRATION,
        None,
        datetime.now(timezone.utc),
        "test",
    )
    conn.close()
    mod = _load_init_db()
    assert mod.setup_vollstaendig(db) is False


# --- Ausgabe main() ---


def test_main_gibt_warnung_aus_bei_fehlenden_deployment_keys(tmp_path, capsys):
    db = _migrierte_db(tmp_path)
    mod = _load_init_db()
    sys.argv = ["init_db.py", "--db", str(db)]
    mod.main()
    out = capsys.readouterr().out
    assert "Ersteinrichtung noch erforderlich" in out
    assert "setup.py" in out


def test_main_meldet_betriebsbereit_wenn_setup_vollstaendig(tmp_path, capsys):
    db = _migrierte_db(tmp_path)
    _setze_deployment_keys(db, tmp_path)
    mod = _load_init_db()
    sys.argv = ["init_db.py", "--db", str(db)]
    mod.main()
    out = capsys.readouterr().out
    assert "betriebsbereit" in out
    assert "Ersteinrichtung" not in out
