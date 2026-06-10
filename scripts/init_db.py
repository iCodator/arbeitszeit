#!/usr/bin/env python3
"""CLI-Einstieg für Datenbankinitialisierung. Delegiert alles an migrations.py."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.repositories import SQLiteSystemConfigRepository

_DEPLOYMENT_KEYS = ("backup.backup_dir", "export.export_dir")


def setup_vollstaendig(db_path: Path) -> bool:
    """True wenn alle Deployment-Keys in system_config gesetzt sind."""
    conn = open_connection(db_path)
    try:
        config = SQLiteSystemConfigRepository(conn)
        return all(config.get_current(k) is not None for k in _DEPLOYMENT_KEYS)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Datenbankinitialisierung und Migrationen.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("arbeitszeit.db"),
        help="Pfad zur Datenbankdatei (Standard: arbeitszeit.db)",
    )
    args = parser.parse_args()
    db_path: Path = args.db

    conn = open_connection(db_path)
    try:
        executed = run_migrations(conn)
    finally:
        conn.close()

    setup_ok = setup_vollstaendig(db_path)

    if executed:
        for version in executed:
            print(f"Migration {version} angewendet.")
        if not setup_ok:
            print("⚠  Ersteinrichtung noch erforderlich:")
            print(f"   python scripts/setup.py --db {db_path}")
    else:
        if setup_ok:
            print("Keine neuen Migrationen. System betriebsbereit.")
        else:
            print("Keine neuen Migrationen.")
            print("⚠  Ersteinrichtung noch erforderlich:")
            print(f"   python scripts/setup.py --db {db_path}")


if __name__ == "__main__":
    main()
