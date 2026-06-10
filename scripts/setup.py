#!/usr/bin/env python3
"""Ersteinrichtung – setzt deployment-spezifische system_config-Einträge.

Muss nach scripts/init_db.py aufgerufen werden, bevor das System erstmals
genutzt wird. Idempotent: bereits konfigurierte Schlüssel werden übersprungen.

Verwendung (interaktiv):
    python scripts/setup.py --db arbeitszeit.db

Verwendung (nicht-interaktiv):
    python scripts/setup.py --db arbeitszeit.db \\
        --backup-dir /var/backups/arbeitszeit \\
        --export-dir /var/exports/arbeitszeit
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.domain.enums import ChangeOrigin
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.repositories import SQLiteSystemConfigRepository


def _prompt_path(label: str) -> Path:
    while True:
        raw = input(f"  {label}: ").strip()
        if raw:
            return Path(raw)
        print("  Bitte einen Pfad eingeben.")


def _configure_key(
    config: SQLiteSystemConfigRepository,
    key: str,
    label: str,
    cli_value: Path | None,
    now: datetime,
) -> None:
    existing_json = config.get_current(key)
    if existing_json is not None:
        existing = json.loads(existing_json)
        print(f"  {key}: bereits konfiguriert ({existing!r}) — übersprungen.")
        return

    path = cli_value if cli_value is not None else _prompt_path(label)
    path = path.resolve()
    path.mkdir(parents=True, exist_ok=True)

    config.set_current(
        key,
        json.dumps(str(path)),
        ChangeOrigin.MIGRATION,
        changed_by_user_id=None,
        changed_at=now,
        reason="Ersteinrichtung",
    )
    print(f"  {key} gesetzt: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ersteinrichtung der deployment-spezifischen system_config-Einträge.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("arbeitszeit.db"),
        help="Pfad zur Datenbankdatei (Standard: arbeitszeit.db)",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Backup-Verzeichnis (nicht-interaktiv)",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=None,
        help="Exportverzeichnis für CSV/PDF (nicht-interaktiv)",
    )
    args = parser.parse_args()

    db_path: Path = args.db
    if not db_path.exists():
        print(f"Fehler: Datenbank nicht gefunden: {db_path}", file=sys.stderr)
        print("Bitte zuerst scripts/init_db.py ausführen.", file=sys.stderr)
        sys.exit(1)

    conn = open_connection(db_path)
    config = SQLiteSystemConfigRepository(conn)
    now = datetime.now(timezone.utc)

    print("Ersteinrichtung arbeitszeit")
    print("=" * 40)

    try:
        _configure_key(
            config,
            "backup.backup_dir",
            "Backup-Verzeichnis (absoluter Pfad)",
            args.backup_dir,
            now,
        )
        _configure_key(
            config,
            "export.export_dir",
            "Exportverzeichnis für CSV/PDF (absoluter Pfad)",
            args.export_dir,
            now,
        )
    finally:
        conn.close()

    print("=" * 40)
    print("Ersteinrichtung abgeschlossen. System betriebsbereit.")
    print("Terminal-UI: python -m arbeitszeit.presentation.terminal_ui.main --db <DB> ...")
    print("Admin-CLI:   python -m arbeitszeit.presentation.admin_cli.main --db <DB> --user-id <ID> ...")


if __name__ == "__main__":
    main()
