#!/usr/bin/env python3
"""Zeigt alle aktuellen system_config-Einträge der arbeitszeit-Datenbank.

Verwendung:
    python scripts/show_config.py --db arbeitszeit.db
    python scripts/show_config.py --db arbeitszeit.db --all-versions
    python scripts/show_config.py --db arbeitszeit.db --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

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
    if not rows:
        print("Keine Konfigurationseinträge vorhanden.")
        return

    # Spaltenbreiten berechnen
    col_key = max(len("Schlüssel"), *(len(str(r["config_key"])) for r in rows))
    col_val = max(len("Wert"), *(len(_decode_value(str(r["config_value_json"]))) for r in rows))
    col_val = min(col_val, 40)  # Wert auf 40 Zeichen begrenzen
    col_origin = max(len("Herkunft"), *(len(str(r["change_origin"])) for r in rows))

    header = (
        f"{'Schlüssel':{col_key}}  {'Wert':{col_val}}  {'Ver':>3}  "
        f"{'Herkunft':{col_origin}}  Geändert am"
    )
    sep = "-" * len(header)

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
        changed_at = str(r["changed_at"])[:16]  # YYYY-MM-DDTHH:MM

        # Leerzeile zwischen verschiedenen Keys bei --all-versions
        if all_versions and key != prev_key and prev_key:
            print()
        prev_key = key

        print(
            f"{key:{col_key}}  {val:{col_val}}  {version:>3}  "
            f"{origin:{col_origin}}  {changed_at}"
        )

    print(sep)
    print(f"{len(rows)} Eintrag/Einträge")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Zeigt system_config-Einträge der arbeitszeit-Datenbank.",
    )
    parser.add_argument(
        "--db",
        required=True,
        type=Path,
        metavar="DB_PATH",
        help="Pfad zur SQLite-Datenbankdatei",
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

    rows = _all_versions(db) if args.all_versions else _current_config(db)

    if args.as_json:
        # Werte für JSON-Ausgabe dekodieren
        output = [
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
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        _print_table(rows, all_versions=args.all_versions)


if __name__ == "__main__":
    main()
