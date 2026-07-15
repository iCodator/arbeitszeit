"""Integrationstests für admin_cli system-Befehle (cmd_system_check, cmd_system_backup)."""

import argparse
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.backup.backup_service import SQLiteBackupService
from arbeitszeit.infrastructure.config_file import AppConfig, BackupConfig
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.system_check import CheckResult, SystemCheckResult
from arbeitszeit.presentation.admin_cli.system import (
    cmd_system_backup,
    cmd_system_check,
    cmd_system_setup,
)


def _make_db(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    conn = open_connection(path)
    run_migrations(conn)
    conn.close()
    return path


def _insert_user(db: Path, role: str) -> int:
    """Legt einen User mit gegebener Rolle an und gibt dessen ID zurück."""
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, employee_id, active, created_at, updated_at) "
        "VALUES (?, 'x', ?, NULL, 1, '2026-01-01', '2026-01-01') "
        "RETURNING id",
        (role.lower(), role),
    ).fetchone()
    conn.close()
    return int(row["id"])


def _set_config(db: Path, key: str, value: object) -> None:
    """Fügt einen system_config-Eintrag bei version=2 ein (überschreibt Seed-Daten)."""
    conn = open_connection(db)
    conn.execute(
        "INSERT INTO system_config "
        "(config_key, config_value_json, version, change_origin, changed_by_user_id, changed_at) "
        "VALUES (?, ?, 2, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00')",
        (key, json.dumps(value)),
    )
    conn.close()


# ---------------------------------------------------------------------------
# cmd_system_check
# ---------------------------------------------------------------------------


class TestCmdSystemCheck:
    def test_reviewer_wird_abgewiesen(self, tmp_path: Path) -> None:
        db = _make_db(tmp_path)
        reviewer_id = _insert_user(db, "REVIEWER")
        conn = open_connection(db)
        try:
            with pytest.raises(SystemExit) as exc:
                cmd_system_check(db, conn, argparse.Namespace(), reviewer_id)
            assert exc.value.code == 1
        finally:
            conn.close()

    def test_overall_ok_true_exitiert_mit_code_0(self, tmp_path: Path) -> None:
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        mock_result = SystemCheckResult(
            checks=(CheckResult(name="db_access", ok=True, detail="OK"),)
        )
        conn = open_connection(db)
        try:
            with patch(
                "arbeitszeit.presentation.admin_cli.system.run_system_check",
                return_value=mock_result,
            ):
                with pytest.raises(SystemExit) as exc:
                    cmd_system_check(db, conn, argparse.Namespace(), admin_id)
            assert exc.value.code == 0
        finally:
            conn.close()

    def test_overall_ok_false_exitiert_mit_code_1(self, tmp_path: Path) -> None:
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        mock_result = SystemCheckResult(
            checks=(CheckResult(name="db_access", ok=False, detail="Migrationsfehler"),)
        )
        conn = open_connection(db)
        try:
            with patch(
                "arbeitszeit.presentation.admin_cli.system.run_system_check",
                return_value=mock_result,
            ):
                with pytest.raises(SystemExit) as exc:
                    cmd_system_check(db, conn, argparse.Namespace(), admin_id)
            assert exc.value.code == 1
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# cmd_system_backup
# ---------------------------------------------------------------------------


class TestCmdSystemBackup:
    def test_reviewer_wird_abgewiesen(self, tmp_path: Path) -> None:
        db = _make_db(tmp_path)
        reviewer_id = _insert_user(db, "REVIEWER")
        conn = open_connection(db)
        try:
            with pytest.raises(SystemExit) as exc:
                cmd_system_backup(db, conn, argparse.Namespace(), reviewer_id)
            assert exc.value.code == 1
        finally:
            conn.close()

    def test_fehlende_backup_dir_config_exitiert_1(self, tmp_path: Path) -> None:
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        conn = open_connection(db)
        try:
            with pytest.raises(SystemExit) as exc:
                cmd_system_backup(db, conn, argparse.Namespace(), admin_id)
            assert exc.value.code == 1
        finally:
            conn.close()

    def test_lokales_backup_ohne_nas_erstellt_datei(self, tmp_path: Path) -> None:
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        backup_dir = tmp_path / "backup"
        _set_config(db, "backup.backup_dir", str(backup_dir))
        _set_config(db, "backup.nas_enabled", False)
        conn = open_connection(db)
        try:
            cmd_system_backup(db, conn, argparse.Namespace(), admin_id)
        finally:
            conn.close()
        assert len(list(backup_dir.glob("*.db"))) == 1

    def test_export_dir_wird_an_service_weitergegeben(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        backup_dir = tmp_path / "backup"
        export_dir = tmp_path / "export"
        _set_config(db, "backup.backup_dir", str(backup_dir))
        _set_config(db, "export.export_dir", str(export_dir))
        _set_config(db, "backup.nas_enabled", False)

        captured: dict[str, object] = {}
        original_init = SQLiteBackupService.__init__

        def capturing_init(
            self: SQLiteBackupService,
            db_path: Path,
            backup_dir_arg: Path,
            *,
            export_dir: Path | None = None,
        ) -> None:
            captured["export_dir"] = export_dir
            original_init(self, db_path, backup_dir_arg, export_dir=export_dir)

        monkeypatch.setattr(SQLiteBackupService, "__init__", capturing_init)
        conn = open_connection(db)
        try:
            cmd_system_backup(db, conn, argparse.Namespace(), admin_id)
        finally:
            conn.close()
        assert captured["export_dir"] == export_dir

    def test_nas_sync_wird_aufgerufen(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        backup_dir = tmp_path / "backup"
        nas_dir = tmp_path / "nas"
        _set_config(db, "backup.backup_dir", str(backup_dir))
        _set_config(db, "backup.nas_enabled", True)
        _set_config(db, "backup.nas_path", str(nas_dir))

        synced_to: list[Path] = []
        monkeypatch.setattr(
            SQLiteBackupService, "sync_to_nas", lambda self, path: synced_to.append(path)
        )
        conn = open_connection(db)
        try:
            cmd_system_backup(db, conn, argparse.Namespace(), admin_id)
        finally:
            conn.close()
        assert synced_to == [nas_dir]

    def test_create_local_backup_fehler_exitiert_1(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        backup_dir = tmp_path / "backup"
        _set_config(db, "backup.backup_dir", str(backup_dir))

        def fail_backup(self: SQLiteBackupService) -> Path:
            raise RuntimeError("Disk voll")

        monkeypatch.setattr(SQLiteBackupService, "create_local_backup", fail_backup)
        conn = open_connection(db)
        try:
            with pytest.raises(SystemExit) as exc:
                cmd_system_backup(db, conn, argparse.Namespace(), admin_id)
            assert exc.value.code == 1
        finally:
            conn.close()

    def test_nas_sync_fehler_exitiert_1(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        backup_dir = tmp_path / "backup"
        nas_dir = tmp_path / "nas"
        _set_config(db, "backup.backup_dir", str(backup_dir))
        _set_config(db, "backup.nas_enabled", True)
        _set_config(db, "backup.nas_path", str(nas_dir))

        def fail_sync(self: SQLiteBackupService, path: Path) -> None:
            raise RuntimeError("NAS nicht erreichbar")

        monkeypatch.setattr(SQLiteBackupService, "sync_to_nas", fail_sync)
        conn = open_connection(db)
        try:
            with pytest.raises(SystemExit) as exc:
                cmd_system_backup(db, conn, argparse.Namespace(), admin_id)
            assert exc.value.code == 1
        finally:
            conn.close()

    def test_app_config_backup_dir_wird_verwendet(self, tmp_path: Path) -> None:
        """app_config.backup.backup_dir hat Vorrang — kein DB-Eintrag nötig."""
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        backup_dir = tmp_path / "backup_aus_config"
        app_config = AppConfig(backup=BackupConfig(backup_dir=backup_dir))
        conn = open_connection(db)
        try:
            cmd_system_backup(db, conn, argparse.Namespace(), admin_id, app_config=app_config)
        finally:
            conn.close()
        assert len(list(backup_dir.glob("*.db"))) == 1

    def test_app_config_hat_vorrang_vor_db_backup_dir(self, tmp_path: Path) -> None:
        """Wenn app_config und DB beide backup_dir haben, gewinnt app_config."""
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        db_backup_dir = tmp_path / "backup_aus_db"
        cfg_backup_dir = tmp_path / "backup_aus_config"
        _set_config(db, "backup.backup_dir", str(db_backup_dir))
        app_config = AppConfig(backup=BackupConfig(backup_dir=cfg_backup_dir))
        conn = open_connection(db)
        try:
            cmd_system_backup(db, conn, argparse.Namespace(), admin_id, app_config=app_config)
        finally:
            conn.close()
        assert len(list(cfg_backup_dir.glob("*.db"))) == 1
        assert not db_backup_dir.exists()


# ---------------------------------------------------------------------------
# cmd_system_setup
# ---------------------------------------------------------------------------


class TestCmdSystemSetup:
    def test_reviewer_wird_abgewiesen(self, tmp_path: Path) -> None:
        db = _make_db(tmp_path)
        reviewer_id = _insert_user(db, "REVIEWER")
        conn = open_connection(db)
        try:
            with pytest.raises(SystemExit) as exc:
                cmd_system_setup(db, conn, argparse.Namespace(), reviewer_id)
            assert exc.value.code == 1
        finally:
            conn.close()

    def test_setup_schreibt_config_toml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """setup_config wird aufgerufen und schreibt eine config.toml."""
        db = _make_db(tmp_path)
        admin_id = _insert_user(db, "ADMIN")
        config_path = tmp_path / "config.toml"

        # input() mocken: leere Eingabe für alle Felder (Werte bleiben None)
        monkeypatch.setattr("builtins.input", lambda _prompt="": "")
        # resolve_config_write_path mocken damit kein Home-Verzeichnis beschrieben wird
        monkeypatch.setattr(
            "arbeitszeit.presentation.admin_cli.system.resolve_config_write_path",
            lambda _explicit: config_path,
        )
        conn = open_connection(db)
        try:
            cmd_system_setup(db, conn, argparse.Namespace(), admin_id)
        finally:
            conn.close()
        assert config_path.exists()
