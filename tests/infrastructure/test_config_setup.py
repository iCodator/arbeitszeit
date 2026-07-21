"""Tests für config_setup: setup_config() und resolve_config_write_path()."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.config_file import (
    AppConfig,
    BackupConfig,
    DatabaseConfig,
    TerminalConfig,
    write_config,
)
from arbeitszeit.infrastructure.config_setup import (
    _collect_db_hints,
    _init_config,
    _int_field,
    _path_field,
    _read_db_hints,
    _str_field,
    resolve_config_write_path,
    setup_config,
)
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations

__version__ = "1.1"


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
        terminal=TerminalConfig(id=3, rfid="RFID Reader"),
        backup=BackupConfig(backup_dir=Path("/var/backups")),
    )
    write_config(original, config_path)

    monkeypatch.setattr("builtins.input", lambda _prompt="": "")  # type: ignore[attr-defined]
    result = setup_config(config_path)

    assert result.database.path == Path("/data/arbeitszeit.db")
    assert result.terminal.id == 3
    assert result.terminal.rfid == "RFID Reader"
    assert result.backup.backup_dir == Path("/var/backups")


def test_einzelner_wert_geaendert_andere_bleiben(tmp_path: Path, monkeypatch: object) -> None:
    """Ändert nur terminal.id — alle anderen Werte aus bestehender Config bleiben."""
    config_path = tmp_path / "config.toml"
    original = AppConfig(
        database=DatabaseConfig(path=Path("/data/arbeitszeit.db")),
        terminal=TerminalConfig(id=1, rfid="RFID Reader"),
        backup=BackupConfig(backup_dir=Path("/var/backups")),
    )
    write_config(original, config_path)

    # Reihenfolge der Prompts: database.path, terminal.id, terminal.rfid,
    #   admin.user_id, backup.backup_dir, backup.export_dir, backup.log_dir
    responses = iter(["", "5", "", "", "", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(responses))  # type: ignore[attr-defined]
    result = setup_config(config_path)

    assert result.terminal.id == 5
    assert result.database.path == Path("/data/arbeitszeit.db")
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
    # Index 4 = backup.backup_dir (Reihenfolge: db.path, term.id, rfid, admin, backup_dir)
    responses = iter(["", "", "", "", "/db/backups", "", ""])
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


# ---------------------------------------------------------------------------
# _path_field – Einheitstests
# ---------------------------------------------------------------------------


def test_path_field_cli_override() -> None:
    """cli is not None → direkt zurückgeben, kein Prompt."""
    assert _path_field("Pfad", Path("/alt"), Path("/neu")) == Path("/neu")


def test_path_field_eingabe_setzt_pfad(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nutzereingabe wird als Path zurückgegeben."""
    monkeypatch.setattr("builtins.input", lambda _p="": "/eingabe/pfad")
    assert _path_field("Pfad", None, None) == Path("/eingabe/pfad")


def test_path_field_leer_behaelt_aktuell(monkeypatch: pytest.MonkeyPatch) -> None:
    """Leere Eingabe → aktuellen Wert unverändert zurückgeben."""
    monkeypatch.setattr("builtins.input", lambda _p="": "")
    assert _path_field("Pfad", Path("/behalten"), None) == Path("/behalten")


# ---------------------------------------------------------------------------
# _str_field – Einheitstests
# ---------------------------------------------------------------------------


def test_str_field_cli_override() -> None:
    """cli is not None → direkt zurückgeben, kein Prompt (Zeile 101)."""
    assert _str_field("Feld", "alt", "neu") == "neu"


def test_str_field_eingabe_uebernimmt_wert(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nutzereingabe wird direkt zurückgegeben."""
    monkeypatch.setattr("builtins.input", lambda _p="": "eingabe")
    assert _str_field("Feld", None, None) == "eingabe"


def test_str_field_leer_behaelt_aktuell(monkeypatch: pytest.MonkeyPatch) -> None:
    """Leere Eingabe → aktuellen Wert behalten."""
    monkeypatch.setattr("builtins.input", lambda _p="": "")
    assert _str_field("Feld", "bestehend", None) == "bestehend"


# ---------------------------------------------------------------------------
# _int_field – Einheitstests
# ---------------------------------------------------------------------------


def test_int_field_cli_override() -> None:
    """cli is not None → direkt zurückgeben, kein Prompt (Zeile 109)."""
    assert _int_field("Zahl", 3, 7) == 7


def test_int_field_gueltige_eingabe(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gültige Ganzzahl wird zurückgegeben."""
    monkeypatch.setattr("builtins.input", lambda _p="": "5")
    assert _int_field("Zahl", None, None) == 5


def test_int_field_ungueltig_dann_gueltig(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ungültige Eingabe → Fehlermeldung, danach gültige Zahl (Zeilen 116–117)."""
    responses = iter(["abc", "42"])
    monkeypatch.setattr("builtins.input", lambda _p="": next(responses))
    assert _int_field("Zahl", None, None) == 42


def test_int_field_leer_behaelt_aktuell(monkeypatch: pytest.MonkeyPatch) -> None:
    """Leere Eingabe → aktuellen Wert behalten."""
    monkeypatch.setattr("builtins.input", lambda _p="": "")
    assert _int_field("Zahl", 3, None) == 3


# ---------------------------------------------------------------------------
# _init_config – Einheitstests
# ---------------------------------------------------------------------------


def test_init_config_datei_vorhanden(tmp_path: Path) -> None:
    """Vorhandene config.toml wird geladen, Status ist 'geladen'."""
    config_path = tmp_path / "config.toml"
    write_config(AppConfig(database=DatabaseConfig(path=Path("/db"))), config_path)
    cfg, status = _init_config(config_path)
    assert cfg.database.path == Path("/db")
    assert status == "geladen"


def test_init_config_datei_fehlt(tmp_path: Path) -> None:
    """Fehlende config.toml → AppConfig-Default, Status 'wird neu erstellt'."""
    cfg, status = _init_config(tmp_path / "neu.toml")
    assert cfg == AppConfig()
    assert status == "wird neu erstellt"


# ---------------------------------------------------------------------------
# _collect_db_hints – Einheitstests
# ---------------------------------------------------------------------------


def test_collect_db_hints_ohne_db_pfad() -> None:
    """db_path=None → leeres Dict, kein DB-Zugriff."""
    assert _collect_db_hints(None) == {}


def test_collect_db_hints_db_ohne_konfigurierte_pfade(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """DB erreichbar, aber keine backup-Pfade gesetzt → leeres Dict (Zweig 131→133)."""
    db = _make_db(tmp_path)
    result = _collect_db_hints(db)
    assert result == {}
    assert "Migrationshinweise" not in capsys.readouterr().out


def test_collect_db_hints_mit_eintraegen(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """DB mit backup_dir-Eintrag → Dict mit Wert, Statusmeldung gedruckt."""
    db = _make_db(tmp_path)
    _set_config(db, "backup.backup_dir", "/bak")
    result = _collect_db_hints(db)
    assert result.get("backup_dir") == "/bak"
    assert "Migrationshinweise" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# _read_db_hints – Einheitstests
# ---------------------------------------------------------------------------


def test_read_db_hints_db_fehler_gibt_leeres_dict(tmp_path: Path) -> None:
    """Nicht-migrierte DB (kein system_config) → Exception abgefangen → {} (Zeilen 66–67)."""
    empty_db = tmp_path / "empty.db"
    result = _read_db_hints(empty_db)
    assert result == {}


def test_read_db_hints_falscher_wert_wird_ignoriert(tmp_path: Path) -> None:
    """JSON-Wert ist leer/falsy → Feld nicht in Hints (Zweig 61→49)."""
    db = _make_db(tmp_path)
    _set_config(db, "backup.backup_dir", "")
    result = _read_db_hints(db)
    assert "backup_dir" not in result


# ---------------------------------------------------------------------------
# setup_config – KeyboardInterrupt
# ---------------------------------------------------------------------------


def test_setup_config_keyboard_interrupt_beendet_prozess(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """KeyboardInterrupt im Prompt-Block → sys.exit(1) (Zeilen 193–195)."""
    def raise_interrupt(prompt: str = "") -> str:
        raise KeyboardInterrupt

    config_path = tmp_path / "config.toml"
    monkeypatch.setattr("builtins.input", raise_interrupt)
    with pytest.raises(SystemExit) as exc_info:
        setup_config(config_path)
    assert exc_info.value.code == 1
