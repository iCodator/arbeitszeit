#!/usr/bin/env python3
"""Zeigt die aktuelle arbeitszeit-Konfiguration: config.toml und DB-Einträge.

Verwendung:
    python scripts/show_config.py --db arbeitszeit.db
    python scripts/show_config.py --db arbeitszeit.db --all-versions
    python scripts/show_config.py --db arbeitszeit.db --json
"""

from __future__ import annotations

__version__ = "1.0"

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.infrastructure.config_file import find_config, load_config
from arbeitszeit.infrastructure.db.connection import open_connection


def _current_config(db: Path) -> list[dict[str, object]]:
    """Gibt den jeweils neuesten Wert pro config_key zurück."""
    conn = open_connection(db)
    try:
        rows = conn.execute(
            """
            SELECT
                s.config_key,
                s.config_value_json,
                s.version,
                s.change_origin,
                s.changed_by_user_id,
                s.changed_at,
                s.reason
            FROM system_config s
            WHERE s.version = (
                SELECT MAX(s2.version)
                FROM system_config s2
                WHERE s2.config_key = s.config_key
            )
            ORDER BY s.config_key
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _all_versions(db: Path) -> list[dict[str, object]]:
    """Gibt alle Versionen aller Keys zurück, neueste zuerst."""
    conn = open_connection(db)
    try:
        rows = conn.execute(
            """
            SELECT
                config_key,
                config_value_json,
                version,
                change_origin,
                changed_by_user_id,
                changed_at,
                reason
            FROM system_config
            ORDER BY config_key, version DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _decode_value(raw_json: str) -> str:
    """Dekodiert JSON-Wert für lesbaren Output."""
    try:
        val = json.loads(raw_json)
        if val is None:
            return "(nicht gesetzt)"
        if isinstance(val, str):
            return val
        return str(val)
    except (json.JSONDecodeError, TypeError):
        return raw_json


def _print_table(rows: list[dict[str, object]], all_versions: bool = False) -> None:
    """Gibt system_config-Einträge als Tabelle aus."""
    if not rows:
        print("  Keine Konfigurationseinträge vorhanden.")
        return

    col_key = max(len("Schlüssel"), *(len(str(r["config_key"])) for r in rows))
    col_val = max(len("Wert"), *(len(_decode_value(str(r["config_value_json"]))) for r in rows))
    col_val = min(col_val, 40)
    col_origin = max(len("Herkunft"), *(len(str(r["change_origin"])) for r in rows))

    header = (
        f"  {'Schlüssel':{col_key}}  {'Wert':{col_val}}  {'Ver':>3}  "
        f"{'Herkunft':{col_origin}}  Geändert am"
    )
    sep = "  " + "-" * (len(header) - 2)

    print(header)
    print(sep)

    prev_key = ""
    for r in rows:
        key = str(r["config_key"])
        raw_val = str(r["config_value_json"])
        val = _decode_value(raw_val)
        if len(val) > col_val:
            val = val[:col_val - 1] + "…"
        version = int(str(r["version"]))
        origin = str(r["change_origin"])
        changed_at = str(r["changed_at"])[:16]

        if all_versions and key != prev_key and prev_key:
            print()
        prev_key = key

        print(
            f"  {key:{col_key}}  {val:{col_val}}  {version:>3}  "
            f"{origin:{col_origin}}  {changed_at}"
        )

    print(sep)
    print(f"  {len(rows)} Eintrag/Einträge")


def _print_config_toml(config_path: Path) -> None:
    """Gibt config.toml-Werte strukturiert aus."""
    try:
        cfg = load_config(config_path)
    except Exception as exc:  # noqa: BLE001
        print(f"  Fehler beim Lesen: {exc}")
        return

    rows: list[tuple[str, str]] = []
    if cfg.database.path is not None:
        rows.append(("database.path", str(cfg.database.path)))
    if cfg.terminal.id is not None:
        rows.append(("terminal.id", str(cfg.terminal.id)))
    if cfg.terminal.numpad is not None:
        rows.append(("terminal.numpad", cfg.terminal.numpad))
    if cfg.terminal.rfid is not None:
        rows.append(("terminal.rfid", cfg.terminal.rfid))
    if cfg.backup.backup_dir is not None:
        rows.append(("backup.backup_dir", str(cfg.backup.backup_dir)))
    if cfg.backup.export_dir is not None:
        rows.append(("backup.export_dir", str(cfg.backup.export_dir)))
    if cfg.backup.log_dir is not None:
        rows.append(("backup.log_dir", str(cfg.backup.log_dir)))
    if cfg.admin.user_id is not None:
        rows.append(("admin.user_id", str(cfg.admin.user_id)))

    if not rows:
        print("  (keine Werte gesetzt)")
        return

    col_key = max(len(k) for k, _ in rows)
    for key, val in rows:
        print(f"  {key:{col_key}}  =  {val}")
    print(f"  ({len(rows)} Felder)")


def main(argv: list[str] | None = None) -> None:
    """Konfigurationsanzeige: config.toml-Werte und DB-Einträge."""
    parser = argparse.ArgumentParser(
        description="Zeigt die arbeitszeit-Konfiguration (config.toml + DB).",
    )
    parser.add_argument(
        "--db",
        required=True,
        type=Path,
        metavar="DB_PATH",
        help="Pfad zur SQLite-Datenbankdatei",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        metavar="CONFIG_PATH",
        help="Pfad zu config.toml (Standard: automatische Suche)",
    )
    parser.add_argument(
        "--all-versions",
        action="store_true",
        help="Alle Versionen statt nur die aktuellen anzeigen",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Ausgabe als JSON",
    )
    args = parser.parse_args(argv)

    db: Path = args.db
    if not db.exists():
        print(f"Fehler: Datenbankdatei nicht gefunden: {db}", file=sys.stderr)
        sys.exit(1)

    # config.toml suchen
    config_path: Path | None = args.config if args.config is not None else find_config()

    if args.as_json:
        rows = _all_versions(db) if args.all_versions else _current_config(db)
        output: dict[str, object] = {
            "db": [
                {
                    "key": r["config_key"],
                    "value": json.loads(str(r["config_value_json"])),
                    "version": r["version"],
                    "change_origin": r["change_origin"],
                    "changed_at": r["changed_at"],
                    "reason": r["reason"],
                }
                for r in rows
            ]
        }
        if config_path is not None and config_path.exists():
            try:
                cfg = load_config(config_path)
                output["config_toml"] = {
                    "path": str(config_path),
                    "database_path": str(cfg.database.path) if cfg.database.path else None,
                    "terminal_id": cfg.terminal.id,
                    "terminal_numpad": cfg.terminal.numpad,
                    "terminal_rfid": cfg.terminal.rfid,
                    "backup_dir": str(cfg.backup.backup_dir) if cfg.backup.backup_dir else None,
                    "export_dir": str(cfg.backup.export_dir) if cfg.backup.export_dir else None,
                    "log_dir": str(cfg.backup.log_dir) if cfg.backup.log_dir else None,
                    "admin_user_id": cfg.admin.user_id,
                }
            except Exception as exc:  # noqa: BLE001
                output["config_toml_error"] = str(exc)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # --- Textausgabe ---
    print()
    print("=== config.toml", end="")
    if config_path is not None and config_path.exists():
        print(f": {config_path} ===")
        _print_config_toml(config_path)
    elif config_path is not None:
        print(f": {config_path} ===")
        print("  (Datei nicht vorhanden)")
    else:
        print(" ===")
        print("  (keine config.toml gefunden — nutze --config um Pfad anzugeben)")

    print()
    print(f"=== DB (system_config): {db} ===")
    rows_db = _all_versions(db) if args.all_versions else _current_config(db)
    _print_table(rows_db, all_versions=args.all_versions)
    print()


if __name__ == "__main__":
    main()
