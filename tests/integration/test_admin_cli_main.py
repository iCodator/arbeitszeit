"""Tests für Fehler-Initialisierungspfade von admin_cli/main.py."""

__version__ = "1.0"

import argparse
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.config_file import AdminConfig, AppConfig, DatabaseConfig
from arbeitszeit.presentation.admin_cli.main import (
    _dispatch,
    _load_app_config,
    _resolve_db_path,
    _resolve_user_id,
)

_MOD = "arbeitszeit.presentation.admin_cli.main"


def _ns(**kwargs: object) -> argparse.Namespace:
    """Erzeugt argparse.Namespace mit Defaults für config/db/user_id."""
    ns = argparse.Namespace(config=None, db=None, user_id=None)
    for key, val in kwargs.items():
        setattr(ns, key, val)
    return ns


# ---------------------------------------------------------------------------
# _load_app_config
# ---------------------------------------------------------------------------


def test_load_app_config_kein_fund_gibt_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Kein --config und find_config() findet nichts → None (Zeile 23)."""
    monkeypatch.setattr(f"{_MOD}.find_config", lambda: None)
    assert _load_app_config(_ns()) is None


def test_load_app_config_laedt_gueltige_toml(tmp_path: Path) -> None:
    """--config mit gültiger TOML-Datei → AppConfig-Objekt."""
    cfg = tmp_path / "config.toml"
    cfg.write_text('[database]\npath = "/tmp/arbeitszeit.db"\n', encoding="utf-8")
    result = _load_app_config(_ns(config=cfg))
    assert result is not None
    assert result.database.path == Path("/tmp/arbeitszeit.db")


def test_load_app_config_ungueltige_toml_beendet_prozess(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--config mit ungültiger TOML-Datei → sys.exit(1) (Zeilen 26–28)."""
    cfg = tmp_path / "bad.toml"
    cfg.write_text("kein gültiges toml [\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        _load_app_config(_ns(config=cfg))
    assert exc_info.value.code == 1
    assert "Fehler" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# _resolve_db_path
# ---------------------------------------------------------------------------


def test_resolve_db_path_aus_config(tmp_path: Path) -> None:
    """Kein --db, AppConfig mit database.path → Pfad aus Config (Zeile 34)."""
    db_path = tmp_path / "arbeitszeit.db"
    config = AppConfig(database=DatabaseConfig(path=db_path))
    assert _resolve_db_path(_ns(), config) == db_path


def test_resolve_db_path_fehlt_beendet_prozess(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Weder --db noch config.database.path → sys.exit(1) (Zeilen 36–41)."""
    with pytest.raises(SystemExit) as exc_info:
        _resolve_db_path(_ns(), None)
    assert exc_info.value.code == 1
    assert "DB-Pfad" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# _resolve_user_id
# ---------------------------------------------------------------------------


def test_resolve_user_id_aus_env_gueltig(monkeypatch: pytest.MonkeyPatch) -> None:
    """ADMIN_USER_ID=7, kein --user-id → 7 aus ENV (Zeilen 49–52)."""
    monkeypatch.setenv("ADMIN_USER_ID", "7")
    assert _resolve_user_id(_ns()) == 7


def test_resolve_user_id_aus_env_ungueltig_beendet_prozess(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """ADMIN_USER_ID=keine_zahl → sys.exit(1) (Zeilen 53–58)."""
    monkeypatch.setenv("ADMIN_USER_ID", "keine_zahl")
    with pytest.raises(SystemExit) as exc_info:
        _resolve_user_id(_ns())
    assert exc_info.value.code == 1
    assert "ADMIN_USER_ID" in capsys.readouterr().err


def test_resolve_user_id_aus_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Kein --user-id, kein ENV, AppConfig.admin.user_id=5 → 5 (Zeile 60)."""
    monkeypatch.delenv("ADMIN_USER_ID", raising=False)
    config = AppConfig(admin=AdminConfig(user_id=5))
    assert _resolve_user_id(_ns(), config) == 5


def test_resolve_user_id_fehlt_beendet_prozess(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Kein --user-id, kein ENV, keine Config → sys.exit(1) (Zeilen 62–67)."""
    monkeypatch.delenv("ADMIN_USER_ID", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        _resolve_user_id(_ns(), None)
    assert exc_info.value.code == 1
    assert "Benutzer-ID" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# _dispatch – kein Handler (False-Zweig Zeile 223)
# ---------------------------------------------------------------------------


def test_dispatch_kein_handler_kein_fehler() -> None:
    """cmd=None → handler=None → kein Aufruf, kein Fehler."""
    conn = sqlite3.connect(":memory:")
    audit_conn = sqlite3.connect(":memory:")
    try:
        args = argparse.Namespace(domain="employees")  # kein employees_cmd gesetzt
        _dispatch(args, conn, audit_conn, 1, Path("/tmp/x.db"))
    finally:
        conn.close()
        audit_conn.close()
