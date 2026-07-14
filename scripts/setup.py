#!/usr/bin/env python3
"""Ersteinrichtung und Pflege der config.toml.

Bearbeitet interaktiv alle deploy-spezifischen Konfigurationswerte.
Idempotent: bestehende Werte bleiben bei leerer Eingabe unverändert.

Verwendung (interaktiv):
    python scripts/setup.py

Verwendung (nicht-interaktiv / Ersteinrichtung):
    python scripts/setup.py --db /pfad/zur/arbeitszeit.db \\
        --backup-dir /var/backups/arbeitszeit \\
        --export-dir /var/exports/arbeitszeit \\
        --log-dir /var/log/arbeitszeit

Alle --*-Flags sind optional. Fehlende Werte werden interaktiv abgefragt.
Wenn --db angegeben wird, liest das Script vorhandene DB-Werte als
Migrationsvorschläge ein (Migrationspfad für Bestandsinstallationen).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.infrastructure.config_setup import resolve_config_write_path, setup_config


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ersteinrichtung/Pflege der arbeitszeit config.toml.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        metavar="CONFIG_PATH",
        help="Pfad zu config.toml (Standard: automatische Suche, dann XDG-Standardpfad)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        metavar="DB_PATH",
        help=(
            "Datenbankpfad: wird als database.path gesetzt und für "
            "Migrationsvorschläge (backup_dir etc.) aus der DB gelesen"
        ),
    )
    parser.add_argument(
        "--terminal-id",
        type=int,
        default=None,
        metavar="ID",
        help="Terminal-ID (nicht-interaktiv)",
    )
    parser.add_argument(
        "--numpad",
        default=None,
        metavar="NAME",
        help="Numpad-Gerätename (nicht-interaktiv)",
    )
    parser.add_argument(
        "--rfid",
        default=None,
        metavar="NAME",
        help="RFID-Gerätename (nicht-interaktiv)",
    )
    parser.add_argument(
        "--admin-user-id",
        type=int,
        default=None,
        metavar="ID",
        help="Admin-Benutzer-ID (nicht-interaktiv)",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Backup-Verzeichnis (nicht-interaktiv)",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Exportverzeichnis für CSV/PDF (nicht-interaktiv)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Log-Verzeichnis (nicht-interaktiv)",
    )
    args = parser.parse_args()

    config_path = resolve_config_write_path(args.config)

    # --db dient als direkter CLI-Override für database.path (überspringt Prompt)
    cli_db_path = args.db.resolve() if args.db is not None else None

    setup_config(
        config_path,
        db_path=args.db,
        cli_db_path=cli_db_path,
        cli_terminal_id=args.terminal_id,
        cli_numpad=args.numpad,
        cli_rfid=args.rfid,
        cli_admin_user_id=args.admin_user_id,
        cli_backup_dir=args.backup_dir,
        cli_export_dir=args.export_dir,
        cli_log_dir=args.log_dir,
    )

    print()
    print("Terminal-UI starten:")
    print("  python -m arbeitszeit.presentation.terminal_ui.main --config <CONFIG>")
    print("Admin-CLI starten:")
    print("  python -m arbeitszeit.presentation.admin_cli.main --config <CONFIG> ...")


if __name__ == "__main__":
    main()
