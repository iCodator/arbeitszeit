"""Backup-Script – manuell oder per systemd-Timer/cron aufzurufen.

Verwendung (mit config.toml):
    python scripts/backup.py --db arbeitszeit.db

Verwendung (explizit, ohne config.toml):
    python scripts/backup.py --db arbeitszeit.db --backup-dir backups/

backup_dir und export_dir werden bevorzugt aus config.toml gelesen.
NAS-Sync wird weiterhin über die system_config-Einträge
'backup.nas_enabled' und 'backup.nas_path' gesteuert.
"""

__version__ = "1.0"

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.infrastructure.backup import SQLiteBackupService
from arbeitszeit.infrastructure.config_file import find_config, load_config
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.repositories import SQLiteSystemConfigRepository


def main() -> None:
    """Backup erstellen und optional auf NAS synchronisieren."""
    parser = argparse.ArgumentParser(description="Erstellt ein SQLite-Backup.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("arbeitszeit.db"),
        help="Pfad zur Datenbankdatei (Standard: arbeitszeit.db)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        metavar="CONFIG_PATH",
        help="Pfad zu config.toml (Standard: automatische Suche)",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help=(
            "Zielverzeichnis für Backups "
            "(Standard: [backup] backup_dir aus config.toml, dann 'backups/')"
        ),
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=None,
        help="Exportverzeichnis (CSV/PDF); wird in backup-dir/exports/ kopiert",
    )
    args = parser.parse_args()

    db_path: Path = args.db

    if not db_path.exists():
        print(f"Fehler: Datenbankdatei nicht gefunden: {db_path}", file=sys.stderr)
        sys.exit(1)

    # backup_dir: CLI > config.toml > Fallback
    backup_dir: Path = args.backup_dir
    export_dir: Path | None = args.export_dir

    if backup_dir is None or export_dir is None:
        cfg_src = args.config if args.config is not None else find_config()
        if cfg_src is not None:
            try:
                app_config = load_config(cfg_src)
                if backup_dir is None and app_config.backup.backup_dir is not None:
                    backup_dir = app_config.backup.backup_dir
                if export_dir is None and app_config.backup.export_dir is not None:
                    export_dir = app_config.backup.export_dir
            except Exception as exc:  # noqa: BLE001
                print(f"Warnung: config.toml konnte nicht geladen werden: {exc}", file=sys.stderr)

    if backup_dir is None:
        backup_dir = Path("backups")

    conn = open_connection(db_path)
    config = SQLiteSystemConfigRepository(conn)
    nas_enabled = json.loads(config.get_current("backup.nas_enabled") or "false")
    nas_path_json = config.get_current("backup.nas_path")
    _nas_path_raw = json.loads(nas_path_json) if nas_path_json else None
    nas_path = Path(_nas_path_raw) if _nas_path_raw else None
    conn.close()

    service = SQLiteBackupService(db_path, backup_dir, export_dir=export_dir)
    result = service.run(nas_path=nas_path if nas_enabled and nas_path else None)

    print(f"Backup: {result.backup_path}  ({result.size_bytes:,} Bytes)")
    if result.synced_to_nas:
        print(f"NAS-Sync: {nas_path}")
    else:
        print("NAS-Sync: deaktiviert")


if __name__ == "__main__":
    main()
