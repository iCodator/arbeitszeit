"""Interaktive Konfigurationspflege: Laden, Bearbeiten, Schreiben von config.toml.

Stellt die gemeinsame Update-Logik für scripts/setup.py und
admin_cli system setup bereit. Beide Einstiege rufen ausschließlich
setup_config() auf — keine doppelte Interaktions- oder Merge-Logik.
"""

from __future__ import annotations

__version__ = "1.0"

import json
import sys
from pathlib import Path

from arbeitszeit.infrastructure.config_file import (
    AdminConfig,
    AppConfig,
    BackupConfig,
    DatabaseConfig,
    TerminalConfig,
    find_config,
    load_config,
    write_config,
)
from arbeitszeit.infrastructure.db.connection import open_connection


def resolve_config_write_path(explicit_path: Path | None) -> Path:
    """Schreibpfad für config.toml: explizit angegeben > vorhandene Datei > XDG-Standard."""
    if explicit_path is not None:
        return explicit_path
    existing = find_config()
    if existing is not None:
        return existing
    return Path.home() / ".config" / "arbeitszeit" / "config.toml"


def _read_db_hints(db_path: Path) -> dict[str, str]:
    """Liest Pfadwerte aus alter DB-Konfiguration als Migrationsvorschläge.

    Liest backup.backup_dir, export.export_dir, logging.log_dir aus system_config.
    Schlägt lautlos fehl (leeres Dict) wenn DB nicht erreichbar ist.
    """
    try:
        conn = open_connection(db_path)
        try:
            hints: dict[str, str] = {}
            for db_key, hint_key in (
                ("backup.backup_dir", "backup_dir"),
                ("export.export_dir", "export_dir"),
                ("logging.log_dir", "log_dir"),
            ):
                row = conn.execute(
                    "SELECT config_value_json FROM system_config "
                    "WHERE config_key = ? ORDER BY version DESC LIMIT 1",
                    (db_key,),
                ).fetchone()
                if row is not None:
                    val = json.loads(row[0])
                    if val:
                        hints[hint_key] = str(val)
            return hints
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        return {}


def _ask(label: str, current: str | None, hint: str | None = None) -> str | None:
    """Interaktive Abfrage eines Felds.

    Zeigt current (oder hint bei fehlendem current) als Default in eckigen Klammern.
    Leere Eingabe → None (bestehenden Wert behalten).
    """
    default = current if current is not None else hint
    from_hint = current is None and hint is not None
    if default is not None:
        tag = "  ← DB-Migrationshinweis" if from_hint else ""
        raw = input(f"  {label} [{default}]{tag}: ").strip()
    else:
        raw = input(f"  {label}: ").strip()
    return raw or None


def setup_config(
    config_path: Path,
    db_path: Path | None = None,
    *,
    cli_db_path: Path | None = None,
    cli_terminal_id: int | None = None,
    cli_numpad: str | None = None,
    cli_rfid: str | None = None,
    cli_admin_user_id: int | None = None,
    cli_backup_dir: Path | None = None,
    cli_export_dir: Path | None = None,
    cli_log_dir: Path | None = None,
) -> AppConfig:
    """Bearbeitet config.toml interaktiv und schreibt sie zurück.

    Verhalten:
    - Leere Eingabe lässt bestehende Werte unverändert.
    - cli_*-Override überspringt den Prompt für dieses Feld.
    - Fehlende Abschnitte werden ergänzt ohne andere Bereiche zu überschreiben.
    - DB-Migrationshinweise werden als Vorschlagswert angezeigt wenn das Feld
      in config.toml noch nicht gesetzt ist.
    """
    existing = load_config(config_path) if config_path.exists() else AppConfig()
    status = "geladen" if config_path.exists() else "wird neu erstellt"
    print(f"Konfigurationsdatei: {config_path}  [{status}]")

    db_hints: dict[str, str] = {}
    if db_path is not None and db_path.exists():
        db_hints = _read_db_hints(db_path)
        if db_hints:
            print("  (Migrationshinweise aus DB eingelesen)")

    print("Leere Eingabe → Wert unverändert lassen.  Strg+C zum Abbrechen.")
    print("-" * 60)

    def _path_field(
        label: str, cur: Path | None, cli: Path | None, hint: str | None = None
    ) -> Path | None:
        if cli is not None:
            return cli
        inp = _ask(label, str(cur) if cur else None, hint)
        return Path(inp) if inp else cur

    def _str_field(
        label: str, cur: str | None, cli: str | None, hint: str | None = None
    ) -> str | None:
        if cli is not None:
            return cli
        inp = _ask(label, cur, hint)
        return inp if inp else cur

    def _int_field(label: str, cur: int | None, cli: int | None) -> int | None:
        if cli is not None:
            return cli
        while True:
            inp = _ask(label, str(cur) if cur is not None else None)
            if inp is None:
                return cur
            try:
                return int(inp)
            except ValueError:
                print("    Bitte eine ganze Zahl eingeben.")

    try:
        db_path_val = _path_field("database.path", existing.database.path, cli_db_path)
        terminal_id_val = _int_field("terminal.id", existing.terminal.id, cli_terminal_id)
        numpad_val = _str_field("terminal.numpad", existing.terminal.numpad, cli_numpad)
        rfid_val = _str_field("terminal.rfid", existing.terminal.rfid, cli_rfid)
        admin_user_id_val = _int_field(
            "admin.user_id (optional)", existing.admin.user_id, cli_admin_user_id
        )
        backup_dir_val = _path_field(
            "backup.backup_dir",
            existing.backup.backup_dir,
            cli_backup_dir,
            db_hints.get("backup_dir"),
        )
        export_dir_val = _path_field(
            "backup.export_dir",
            existing.backup.export_dir,
            cli_export_dir,
            db_hints.get("export_dir"),
        )
        log_dir_val = _path_field(
            "backup.log_dir",
            existing.backup.log_dir,
            cli_log_dir,
            db_hints.get("log_dir"),
        )
    except KeyboardInterrupt:
        print("\nAbgebrochen.")
        sys.exit(1)

    updated = AppConfig(
        database=DatabaseConfig(path=db_path_val),
        terminal=TerminalConfig(id=terminal_id_val, numpad=numpad_val, rfid=rfid_val),
        backup=BackupConfig(
            backup_dir=backup_dir_val, export_dir=export_dir_val, log_dir=log_dir_val
        ),
        admin=AdminConfig(user_id=admin_user_id_val),
    )

    write_config(updated, config_path)
    print("-" * 60)
    print(f"Konfiguration gespeichert: {config_path}")

    missing = [
        f for f, v in (
            ("database.path", updated.database.path),
            ("terminal.id", updated.terminal.id),
            ("terminal.numpad", updated.terminal.numpad),
            ("terminal.rfid", updated.terminal.rfid),
        )
        if v is None
    ]
    if missing:
        print(f"Hinweis: Pflichtfelder noch nicht konfiguriert: {', '.join(missing)}")

    return updated
