"""Admin-CLI: Systemcheck, Backup und Konfiguration (ADMIN/TECH-Rolle)."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from arbeitszeit.infrastructure.backup.backup_service import SQLiteBackupService
from arbeitszeit.infrastructure.config_file import AppConfig
from arbeitszeit.infrastructure.config_setup import resolve_config_write_path, setup_config
from arbeitszeit.infrastructure.system_check import run_system_check
from arbeitszeit.presentation.admin_cli._auth import require_admin_or_tech


def cmd_system_check(
    db_path: Path,
    conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
    *,
    app_config: AppConfig | None = None,
) -> None:
    """Systemcheck auslösen und Ergebnis ausgeben."""
    require_admin_or_tech(conn, user_id)
    result = run_system_check(db_path, app_config=app_config)
    print("Systemcheck-Ergebnis:")
    print(f"  Gesamt: {'OK' if result.overall_ok else 'FEHLER'}")
    print()
    for check in result.checks:
        status = "OK  " if check.ok else "FAIL"
        print(f"  [{status}] {check.name}: {check.detail}")
    sys.exit(0 if result.overall_ok else 1)


def cmd_system_backup(
    db_path: Path,
    conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
    *,
    app_config: AppConfig | None = None,
) -> None:
    """Manuelles Backup auslösen.

    backup_dir und export_dir: app_config hat Vorrang vor DB-Werten (Fallback
    für Bestandsinstallationen die noch keine config.toml haben).
    """
    require_admin_or_tech(conn, user_id)

    # backup_dir: config.toml > DB-Fallback
    backup_dir: Path | None = app_config.backup.backup_dir if app_config is not None else None
    if backup_dir is None:
        row = conn.execute(
            "SELECT config_value_json FROM system_config "
            "WHERE config_key = 'backup.backup_dir' ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if row is not None:
            backup_dir = Path(json.loads(row["config_value_json"]))

    if backup_dir is None:
        print(
            "Fehler: backup_dir nicht konfiguriert. "
            "Entweder [backup] backup_dir in config.toml oder "
            "system_config-Schlüssel 'backup.backup_dir' setzen.",
            file=sys.stderr,
        )
        sys.exit(1)

    # export_dir: config.toml > DB-Fallback
    export_dir: Path | None = app_config.backup.export_dir if app_config is not None else None
    if export_dir is None:
        row = conn.execute(
            "SELECT config_value_json FROM system_config "
            "WHERE config_key = 'export.export_dir' ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if row is not None:
            val = json.loads(row["config_value_json"])
            if val is not None:
                export_dir = Path(val)

    service = SQLiteBackupService(db_path, backup_dir, export_dir=export_dir)
    try:
        backup_path = service.create_local_backup()
    except Exception as exc:
        print(f"Fehler beim Backup: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Backup erstellt: {backup_path}")

    nas_enabled_row = conn.execute(
        "SELECT config_value_json FROM system_config "
        "WHERE config_key = 'backup.nas_enabled' ORDER BY version DESC LIMIT 1"
    ).fetchone()
    nas_enabled = nas_enabled_row is not None and bool(
        json.loads(nas_enabled_row["config_value_json"])
    )

    if nas_enabled:
        nas_path_row = conn.execute(
            "SELECT config_value_json FROM system_config "
            "WHERE config_key = 'backup.nas_path' ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if nas_path_row is not None:
            nas_path_val = json.loads(nas_path_row["config_value_json"])
            if nas_path_val is not None:
                try:
                    service.sync_to_nas(Path(nas_path_val))
                    print("NAS-Synchronisation erfolgreich.")
                except Exception as exc:
                    print(
                        f"Fehler: NAS-Synchronisation fehlgeschlagen: {exc}",
                        file=sys.stderr,
                    )
                    sys.exit(1)


def cmd_system_setup(
    db_path: Path,
    conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
    *,
    app_config: AppConfig | None = None,
) -> None:
    """Konfigurationsdatei interaktiv bearbeiten."""
    require_admin_or_tech(conn, user_id)
    config_path = resolve_config_write_path(getattr(args, "config", None))
    setup_config(config_path, db_path=db_path)


def register_subcommands(
    sub: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Subcommands für den 'system'-Bereich registrieren."""
    system = sub.add_parser("system", help="Systemcheck, Backup und Konfiguration")
    ssub = system.add_subparsers(dest="system_cmd", required=True)
    ssub.add_parser("check", help="Systemcheck auslösen und Ergebnis anzeigen")
    ssub.add_parser("backup", help="Manuelles Backup auslösen")
    ssub.add_parser("setup", help="Konfigurationsdatei interaktiv bearbeiten")
