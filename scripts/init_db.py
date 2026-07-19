#!/usr/bin/env python3
"""CLI-Einstieg für Datenbankinitialisierung. Delegiert alles an migrations.py."""

__version__ = "1.1"

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.infrastructure.config_file import find_config, load_config
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


def _resolve_db_path(explicit_db: Path | None, config_path: Path | None) -> Path:
    """Ermittelt den Datenbankpfad: --db > config.toml > interaktive Abfrage."""
    if explicit_db is not None:
        return explicit_db

    if config_path is None:
        config_path = find_config()

    if config_path is not None:
        cfg = load_config(config_path)
        if cfg.database.path is not None:
            print(f"Datenbankpfad aus {config_path}: {cfg.database.path}")
            return cfg.database.path

    default = Path("arbeitszeit.db").resolve()
    antwort = input(f"Datenbankpfad [{default}]: ").strip()
    return Path(antwort) if antwort else default


def main() -> None:
    parser = argparse.ArgumentParser(description="Datenbankinitialisierung und Migrationen.")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Pfad zur config.toml (Standard: automatische Suche)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Pfad zur Datenbankdatei (überschreibt config.toml und interaktive Abfrage)",
    )
    args = parser.parse_args()
    db_path: Path = _resolve_db_path(args.db, args.config)

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
