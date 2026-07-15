"""Gemeinsame Test-Hilfsfunktionen."""

__version__ = "1.0"

from pathlib import Path

from arbeitszeit.infrastructure.config_file import (
    AdminConfig,
    AppConfig,
    BackupConfig,
    DatabaseConfig,
    TerminalConfig,
    write_config,
)


def make_config_toml(
    tmp_path: Path,
    *,
    database_path: Path | None = None,
    rfid: str | None = None,
    numpad: str | None = None,
    backup_dir: Path | None = None,
    export_dir: Path | None = None,
    log_dir: Path | None = None,
    admin_user_id: int | None = None,
    filename: str = "config.toml",
) -> Path:
    config = AppConfig(
        database=DatabaseConfig(path=database_path),
        terminal=TerminalConfig(rfid=rfid, numpad=numpad),
        backup=BackupConfig(backup_dir=backup_dir, export_dir=export_dir, log_dir=log_dir),
        admin=AdminConfig(user_id=admin_user_id),
    )
    path = tmp_path / filename
    write_config(config, path)
    return path
