"""Datenbankverbindung und Konfigurationsauflösung für die Admin-TUI."""

__version__ = "1.0"

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from arbeitszeit.infrastructure.config_file import AppConfig, find_config, load_config
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations


@dataclass(slots=True)
class AppState:
    conn: sqlite3.Connection
    audit_conn: sqlite3.Connection
    db_path: Path
    user_id: int
    cfg: AppConfig | None


def load_app_config(config_path: Path | None = None) -> tuple[AppConfig | None, str | None]:
    """Lädt AppConfig; gibt (config, None) bei Erfolg oder (None, Fehlermeldung) zurück."""
    src = config_path if config_path is not None else find_config()
    if src is None:
        return None, None
    try:
        return load_config(src), None
    except Exception as exc:
        return None, f"config.toml konnte nicht geladen werden: {exc}"


def resolve_db_path(db_arg: Path | None, cfg: AppConfig | None) -> Path:
    """Ermittelt den DB-Pfad; raises ValueError wenn keiner gefunden."""
    if db_arg is not None:
        return db_arg
    if cfg is not None and cfg.database.path is not None:
        return cfg.database.path
    raise ValueError(
        "Kein Datenbankpfad angegeben. "
        "--db oder [database] path in config.toml setzen."
    )


def resolve_user_id(user_id_arg: int | None, cfg: AppConfig | None) -> int:
    """Ermittelt die Benutzer-ID; raises ValueError wenn keine gefunden."""
    if user_id_arg is not None:
        return user_id_arg
    env_val = os.environ.get("ADMIN_USER_ID")
    if env_val is not None:
        try:
            return int(env_val)
        except ValueError as exc:
            raise ValueError(
                f"ADMIN_USER_ID muss eine Ganzzahl sein, got {env_val!r}."
            ) from exc
    if cfg is not None and cfg.admin.user_id is not None:
        return cfg.admin.user_id
    raise ValueError(
        "Keine Benutzer-ID angegeben. "
        "ADMIN_USER_ID oder [admin] user_id in config.toml setzen."
    )


def open_app_state(
    db_path: Path, user_id: int, cfg: AppConfig | None = None
) -> AppState:
    """Öffnet beide DB-Verbindungen, führt Migrationen aus und gibt AppState zurück."""
    conn = open_connection(db_path)
    run_migrations(conn)
    audit_conn = open_connection(db_path)
    return AppState(
        conn=conn,
        audit_conn=audit_conn,
        db_path=db_path,
        user_id=user_id,
        cfg=cfg,
    )


def close_app_state(state: AppState) -> None:
    """Schließt beide DB-Verbindungen."""
    state.audit_conn.close()
    state.conn.close()
