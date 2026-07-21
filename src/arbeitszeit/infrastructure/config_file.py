"""Zentrale Konfigurationsdatei-Unterstützung für arbeitszeit.

Lädt config.toml mit tomllib (Python 3.11+, Stdlib, read-only).

Suchreihenfolge:
  1. explizit übergebener Pfad  (z. B. aus --config CLI-Argument)
  2. ENV ARBEITSZEIT_CONFIG
  3. ~/.config/arbeitszeit/config.toml
  4. ./config.toml
"""

from __future__ import annotations

__version__ = "1.2"

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    path: Path | None = None


@dataclass(frozen=True, slots=True)
class TerminalConfig:
    id: int | None = None
    rfid: str | None = None


@dataclass(frozen=True, slots=True)
class BackupConfig:
    backup_dir: Path | None = None
    export_dir: Path | None = None
    log_dir: Path | None = None


@dataclass(frozen=True, slots=True)
class AdminConfig:
    user_id: int | None = None


@dataclass(frozen=True, slots=True)
class AppConfig:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    terminal: TerminalConfig = field(default_factory=TerminalConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    admin: AdminConfig = field(default_factory=AdminConfig)


def find_config() -> Path | None:
    """Findet config.toml in der vordefinierten Suchreihenfolge.

    Expliziter Pfad (CLI-Argument) wird nicht hier aufgelöst – das übernimmt
    der Aufrufer. Diese Funktion deckt ENV, XDG und Working-Directory ab.
    """
    env_val = os.environ.get("ARBEITSZEIT_CONFIG")
    if env_val:
        return Path(env_val)
    xdg = Path.home() / ".config" / "arbeitszeit" / "config.toml"
    if xdg.is_file():
        return xdg
    local = Path("config.toml")
    if local.is_file():
        return local.resolve()
    return None


def load_config(config_path: Path) -> AppConfig:
    """Lädt AppConfig aus der angegebenen config.toml-Datei."""
    with config_path.open("rb") as f:
        data: dict[str, Any] = tomllib.load(f)
    return _parse(data)


def _parse(data: dict[str, Any]) -> AppConfig:
    db_raw: dict[str, Any] = data.get("database", {})
    term_raw: dict[str, Any] = data.get("terminal", {})
    backup_raw: dict[str, Any] = data.get("backup", {})
    admin_raw: dict[str, Any] = data.get("admin", {})

    return AppConfig(
        database=DatabaseConfig(
            path=Path(str(db_raw["path"])) if "path" in db_raw else None,
        ),
        terminal=TerminalConfig(
            id=int(term_raw["id"]) if "id" in term_raw else None,
            rfid=str(term_raw["rfid"]) if "rfid" in term_raw else None,
        ),
        backup=BackupConfig(
            backup_dir=Path(str(backup_raw["backup_dir"])) if "backup_dir" in backup_raw else None,
            export_dir=Path(str(backup_raw["export_dir"])) if "export_dir" in backup_raw else None,
            log_dir=Path(str(backup_raw["log_dir"])) if "log_dir" in backup_raw else None,
        ),
        admin=AdminConfig(
            user_id=int(admin_raw["user_id"]) if "user_id" in admin_raw else None,
        ),
    )


def _toml_string(val: Path | str) -> str:
    """Gibt val als TOML-String-Literal zurück (Backslashes und Anführungszeichen escaped)."""
    escaped = str(val).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _terminal_section(config: AppConfig) -> list[str]:
    """Gibt TOML-Zeilen für [terminal] zurück; leere Liste wenn kein Feld gesetzt."""
    lines: list[str] = []
    if config.terminal.id is not None:
        lines.append(f"id = {config.terminal.id!r}")
    if config.terminal.rfid is not None:
        lines.append(f"rfid = {_toml_string(config.terminal.rfid)}")
    if lines:
        return ["[terminal]"] + lines + [""]
    return []


def _backup_section(config: AppConfig) -> list[str]:
    """Gibt TOML-Zeilen für [backup] zurück; leere Liste wenn kein Feld gesetzt."""
    lines: list[str] = []
    if config.backup.backup_dir is not None:
        lines.append(f"backup_dir = {_toml_string(config.backup.backup_dir)}")
    if config.backup.export_dir is not None:
        lines.append(f"export_dir = {_toml_string(config.backup.export_dir)}")
    if config.backup.log_dir is not None:
        lines.append(f"log_dir = {_toml_string(config.backup.log_dir)}")
    if lines:
        return ["[backup]"] + lines + [""]
    return []


def write_config(config: AppConfig, path: Path) -> None:
    """Schreibt AppConfig als TOML-Datei. Nur gesetzte Felder werden ausgegeben."""
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    if config.database.path is not None:
        lines += ["[database]", f"path = {_toml_string(config.database.path)}", ""]

    lines += _terminal_section(config)
    lines += _backup_section(config)

    if config.admin.user_id is not None:
        lines += ["[admin]", f"user_id = {config.admin.user_id!r}", ""]

    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
