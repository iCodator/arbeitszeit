"""Admin-CLI: Systemcheck und Backup (ADMIN/TECH-Rolle)."""
import argparse
import sqlite3
import sys
from pathlib import Path

from arbeitszeit.infrastructure.backup.backup_service import SQLiteBackupService
from arbeitszeit.infrastructure.system_check import run_system_check


def _require_admin_or_tech(conn: sqlite3.Connection, user_id: int) -> None:
    row = conn.execute(
        "SELECT role, active FROM user_accounts WHERE id = ?", (user_id,)
    ).fetchone()
    if row is None or not row["active"] or row["role"] not in ("ADMIN", "TECH"):
        print(
            "Fehler: Zugriff verweigert. Aktion erfordert ADMIN- oder TECH-Rolle.",
            file=sys.stderr,
        )
        sys.exit(1)


def cmd_system_check(
    db_path: Path,
    conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
) -> None:
    _require_admin_or_tech(conn, user_id)
    result = run_system_check(db_path)
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
) -> None:
    _require_admin_or_tech(conn, user_id)
    backup_dir_row = conn.execute(
        "SELECT config_value FROM system_config "
        "WHERE config_key = 'backup.backup_dir' ORDER BY version DESC LIMIT 1"
    ).fetchone()
    if backup_dir_row is None:
        print(
            "Fehler: system_config-Schlüssel 'backup.backup_dir' nicht gesetzt.",
            file=sys.stderr,
        )
        sys.exit(1)
    backup_dir = Path(backup_dir_row["config_value"])

    export_dir: Path | None = None
    export_dir_row = conn.execute(
        "SELECT config_value FROM system_config "
        "WHERE config_key = 'export.export_dir' ORDER BY version DESC LIMIT 1"
    ).fetchone()
    if export_dir_row is not None:
        export_dir = Path(export_dir_row["config_value"])

    service = SQLiteBackupService(db_path, backup_dir, export_dir=export_dir)
    try:
        backup_path = service.create_local_backup()
    except Exception as exc:
        print(f"Fehler beim Backup: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Backup erstellt: {backup_path}")

    nas_enabled_row = conn.execute(
        "SELECT config_value FROM system_config "
        "WHERE config_key = 'backup.nas_enabled' ORDER BY version DESC LIMIT 1"
    ).fetchone()
    nas_enabled = nas_enabled_row is not None and nas_enabled_row["config_value"].lower() == "true"

    if nas_enabled:
        nas_path_row = conn.execute(
            "SELECT config_value FROM system_config "
            "WHERE config_key = 'backup.nas_path' ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if nas_path_row is not None:
            try:
                service.sync_to_nas(Path(nas_path_row["config_value"]))
                print("NAS-Synchronisation erfolgreich.")
            except Exception as exc:
                print(f"Warnung: NAS-Synchronisation fehlgeschlagen: {exc}", file=sys.stderr)


def register_subcommands(
    sub: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    system = sub.add_parser("system", help="Systemcheck und Backup")
    ssub = system.add_subparsers(dest="system_cmd", required=True)
    ssub.add_parser("check", help="Systemcheck auslösen und Ergebnis anzeigen")
    ssub.add_parser("backup", help="Manuelles Backup auslösen")
