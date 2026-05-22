"""
Backup-Script – manuell oder per systemd-Timer/cron aufzurufen.

Verwendung:
    python scripts/backup.py --db arbeitszeit.db --backup-dir backups/

Optionaler NAS-Sync wird über die system_config-Einträge
'backup.nas_enabled' und 'backup.nas_path' gesteuert.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.infrastructure.backup import SQLiteBackupService
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.repositories import SQLiteSystemConfigRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Erstellt ein SQLite-Backup.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("arbeitszeit.db"),
        help="Pfad zur Datenbankdatei (Standard: arbeitszeit.db)",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("backups"),
        help="Zielverzeichnis für Backups (Standard: backups/)",
    )
    args = parser.parse_args()

    db_path: Path = args.db
    backup_dir: Path = args.backup_dir

    if not db_path.exists():
        print(f"Fehler: Datenbankdatei nicht gefunden: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = open_connection(db_path)
    config = SQLiteSystemConfigRepository(conn)
    nas_enabled = json.loads(config.get_current("backup.nas_enabled") or "false")
    nas_path_json = config.get_current("backup.nas_path")
    nas_path = Path(json.loads(nas_path_json)) if nas_path_json and json.loads(nas_path_json) else None
    conn.close()

    service = SQLiteBackupService(db_path, backup_dir)
    result = service.run(nas_path=nas_path if nas_enabled and nas_path else None)

    print(f"Backup: {result.backup_path}  ({result.size_bytes:,} Bytes)")
    if result.synced_to_nas:
        print(f"NAS-Sync: {nas_path}")
    else:
        print("NAS-Sync: deaktiviert")


if __name__ == "__main__":
    main()
