"""Tests für config_setup: setup_config() und resolve_config_write_path()."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.config_file import (
    AppConfig,
    BackupConfig,
    DatabaseConfig,
    TerminalConfig,
    write_config,
)
from arbeitszeit.infrastructure.config_setup import resolve_config_write_path, setup_config
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations

__version__ = "1.0"


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------


def _make_db(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    conn = open_connection(path)
    run_migrations(conn)
    conn.close()
    return path


def _set_config(db: Path, key: str, value: object) -> None:
    conn = open_connection(db)
    conn.execute(
        "INSERT INTO system_config "
        "(config_key, config_value_json, version, change_origin, changed_by_user_id, changed_at) "
        "VALUES (?, ?, 2, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00')",
        (key, json.dumps(value)),
    )
    conn.close()


# ---------------------------------------------------------------------------
# resolve_config_write_path
# ---------------------------------------------------------------------------


def test_resolve_explicit_pfad_wird_direkt_zurückgegeben(tmp_path: Path) -> None:
    p = tmp_path / "explicit.toml"
    assert resolve_config_write_path(p) == p


def test_resolve_vorhandene_config_via_env(tmp_path: Path, monkeypatch: object) -> None:
    existing = tmp_path / "config.toml"
    existing.write_bytes(b"")
    monkeypatch.setenv("ARBEITSZEIT_CONFIG", str(existing))  # type: ignore[attr-defined]
    assert resolve_config_write_path(None) == existing


def test_resolve_fallback_auf_xdg(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.delenv("ARBEITSZEIT_CONFIG", raising=False)  # type: ignore[attr-defined]
    monkeypatch.setattr(Path, "home", lambda: tmp_path)  # type: ignore[attr-defined]
    monkeypatch.chdir(tmp_path)  # type: ignore[attr-defined]
    result = resolve_config_write_path(None)
    assert result == tmp_path / ".config" / "arbeitszeit" / "config.toml"


# ---------------------------------------------------------------------------
# setup_config – Grundverhalten
# ---------------------------------------------------------------------------


def test_leere_eingabe_behaelt_bestehende_werte(tmp_path: Path, monkeypatch: object) -> None:
    """Leere Eingabe für alle Felder lässt die vorhandene Konfiguration unverändert."""
    config_path = tmp_path / "config.toml"
    original = AppConfig(
        database=DatabaseConfig(path=Path("/data/arbeitszeit.db")),
        terminal=TerminalConfig(id=3, numpad="USB Numpad", rfid="RFID Reader"),
        backup=BackupConfig(backup_dir=Path("/var/backups")),
    )
    write_config(original, config_path)

    monkeypatch.setattr("builtins.input", lambda _prompt="": "")  # type: ignore[attr-defined]
    result = setup_config(config_path)

    assert result.database.path == Path("/data/arbeitszeit.db")
    assert result.terminal.id == 3
    assert result.terminal.numpad == "USB Numpad"
    assert result.terminal.rfid == "RFID Reader"
    assert result.backup.backup_dir == Path("/var/backups")


def test_einzelner_wert_geaendert_andere_bleiben(tmp_path: Path, monkeypatch: object) -> None:
    """Ändert nur terminal.id — alle anderen Werte aus bestehender Config bleiben."""
    config_path = tmp_path / "config.toml"
    original = AppConfig(
        database=DatabaseConfig(path=Path("/data/arbeitszeit.db")),
        terminal=TerminalConfig(id=1, numpad="USB Numpad", rfid="RFID Reader"),
        backup=BackupConfig(backup_dir=Path("/var/backups")),
    )
    write_config(original, config_path)

    # Reihenfolge der Prompts: database.path, terminal.id, terminal.numpad,
    #   terminal.rfid, admin.user_id, backup.backup_dir, backup.export_dir, backup.log_dir
    responses = iter(["", "5", "", "", "", "", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(responses))  # type: ignore[attr-defined]
    result = setup_config(config_path)

    assert result.terminal.id == 5
    assert result.database.path == Path("/data/arbeitszeit.db")
    assert result.terminal.numpad == "USB Numpad"
    assert result.terminal.rfid == "RFID Reader"
    assert result.backup.backup_dir == Path("/var/backups")


# ---------------------------------------------------------------------------
# setup_config – DB-Migrationshinweise
# ---------------------------------------------------------------------------


def test_db_hinweis_leere_eingabe_uebernimmt_nicht(tmp_path: Path, monkeypatch: object) -> None:
    """Leere Eingabe bei DB-Migrationshinweis: Feld bleibt None."""
    db = _make_db(tmp_path)
    _set_config(db, "backup.backup_dir", "/db/backups")

    config_path = tmp_path / "config.toml"
    monkeypatch.setattr("builtins.input", lambda _prompt="": "")  # type: ignore[attr-defined]
    result = setup_config(config_path, db_path=db)

    assert result.backup.backup_dir is None


def test_db_hinweis_explizite_eingabe_uebernimmt_wert(tmp_path: Path, monkeypatch: object) -> None:
    """Gibt der Nutzer den Vorschlagswert ein, wird er als backup_dir übernommen."""
    db = _make_db(tmp_path)
    _set_config(db, "backup.backup_dir", "/db/backups")

    config_path = tmp_path / "config.toml"
    # Index 5 = backup.backup_dir (Reihenfolge: db.path, term.id, numpad, rfid, admin, backup_dir)
    responses = iter(["", "", "", "", "", "/db/backups", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(responses))  # type: ignore[attr-defined]
    result = setup_config(config_path, db_path=db)

    assert result.backup.backup_dir == Path("/db/backups")


# ---------------------------------------------------------------------------
# setup_config – CLI-Override
# ---------------------------------------------------------------------------


def test_cli_override_ueberspringt_prompt(tmp_path: Path, monkeypatch: object) -> None:
    """cli_db_path wird direkt gesetzt; der database.path-Prompt erscheint nicht."""
    config_path = tmp_path / "config.toml"
    prompt_labels: list[str] = []

    def capturing_input(prompt: str = "") -> str:
        prompt_labels.append(prompt)
        return ""

    monkeypatch.setattr("builtins.input", capturing_input)  # type: ignore[attr-defined]
    db_path = tmp_path / "arbeitszeit.db"
    result = setup_config(config_path, cli_db_path=db_path)

    assert result.database.path == db_path
    assert not any("database.path" in p for p in prompt_labels)
