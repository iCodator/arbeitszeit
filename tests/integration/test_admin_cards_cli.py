"""Integrationstests für presentation/admin_cli/admin_cards.py."""

__version__ = "1.0"

import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.presentation.admin_cli.admin_cards import (
    cmd_admin_cards_assign,
    cmd_admin_cards_deactivate,
    cmd_admin_cards_list,
)

_UID_HASH = "aabbccdd1122334455667788"
_UID_HASH_2 = "deadbeef9988776655443322"


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    conn = open_connection(path)
    run_migrations(conn)
    conn.close()
    return path


def _open(db: Path):  # type: ignore[no-untyped-def]
    return open_connection(db)


def _ns(**kwargs: object) -> argparse.Namespace:
    ns = argparse.Namespace(uid_hash=None, scan=False, label=None, rfid=None, id=None)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def _cards(db: Path) -> list[dict[str, object]]:
    conn = open_connection(db)
    rows = conn.execute("SELECT id, uid_hash, label, active FROM admin_rfid_cards").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# cmd_admin_cards_assign
# ---------------------------------------------------------------------------


def test_assign_legt_karte_mit_uid_hash_an(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    conn = _open(db)
    cmd_admin_cards_assign(conn, _open(db), _ns(uid_hash=_UID_HASH, label="Erstkarte"))
    conn.close()

    karten = _cards(db)
    assert len(karten) == 1
    assert karten[0]["uid_hash"] == _UID_HASH
    assert karten[0]["label"] == "Erstkarte"
    assert karten[0]["active"] == 1
    assert "Admin-Karte angelegt" in capsys.readouterr().out


def test_assign_ohne_label_legt_karte_an(db: Path) -> None:
    conn = _open(db)
    cmd_admin_cards_assign(conn, _open(db), _ns(uid_hash=_UID_HASH))
    conn.close()

    karten = _cards(db)
    assert len(karten) == 1
    assert karten[0]["label"] is None


def test_assign_doppelter_uid_hash_beendet_prozess(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    conn = _open(db)
    cmd_admin_cards_assign(conn, _open(db), _ns(uid_hash=_UID_HASH))
    conn.close()

    conn2 = _open(db)
    with pytest.raises(SystemExit) as exc_info:
        cmd_admin_cards_assign(conn2, _open(db), _ns(uid_hash=_UID_HASH))
    conn2.close()

    assert exc_info.value.code == 1
    assert "bereits" in capsys.readouterr().err


def test_assign_ohne_uid_hash_und_ohne_scan_beendet_prozess(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    conn = _open(db)
    with pytest.raises(SystemExit) as exc_info:
        cmd_admin_cards_assign(conn, _open(db), _ns())
    conn.close()

    assert exc_info.value.code == 1
    assert "erforderlich" in capsys.readouterr().err


def test_assign_uid_hash_und_scan_gleichzeitig_beendet_prozess(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    conn = _open(db)
    with pytest.raises(SystemExit) as exc_info:
        cmd_admin_cards_assign(conn, _open(db), _ns(uid_hash=_UID_HASH, scan=True))
    conn.close()

    assert exc_info.value.code == 1
    assert "schließen sich aus" in capsys.readouterr().err


def test_assign_mehrere_karten_moeglich(db: Path) -> None:
    conn = _open(db)
    cmd_admin_cards_assign(conn, _open(db), _ns(uid_hash=_UID_HASH))
    conn.close()
    conn2 = _open(db)
    cmd_admin_cards_assign(conn2, _open(db), _ns(uid_hash=_UID_HASH_2))
    conn2.close()

    assert len(_cards(db)) == 2


# ---------------------------------------------------------------------------
# cmd_admin_cards_deactivate
# ---------------------------------------------------------------------------


def _insert_card(db: Path, uid_hash: str, label: str | None = None) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO admin_rfid_cards (uid_hash, label, active, created_at) "
        "VALUES (?, ?, 1, '2026-01-01T00:00:00') RETURNING id",
        (uid_hash, label),
    ).fetchone()
    conn.close()
    return int(row["id"])


def test_deactivate_setzt_active_auf_null(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    card_id = _insert_card(db, _UID_HASH)
    conn = _open(db)
    cmd_admin_cards_deactivate(conn, _open(db), _ns(id=card_id))
    conn.close()

    karten = _cards(db)
    assert karten[0]["active"] == 0
    assert str(card_id) in capsys.readouterr().out


def test_deactivate_unbekannte_id_beendet_prozess(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    conn = _open(db)
    with pytest.raises(SystemExit) as exc_info:
        cmd_admin_cards_deactivate(conn, _open(db), _ns(id=999))
    conn.close()

    assert exc_info.value.code == 1
    assert "nicht gefunden" in capsys.readouterr().err


def test_deactivate_nur_die_richtige_karte(db: Path) -> None:
    id_a = _insert_card(db, _UID_HASH, label="A")
    _insert_card(db, _UID_HASH_2, label="B")

    conn = _open(db)
    cmd_admin_cards_deactivate(conn, _open(db), _ns(id=id_a))
    conn.close()

    karten = {k["uid_hash"]: k["active"] for k in _cards(db)}
    assert karten[_UID_HASH] == 0
    assert karten[_UID_HASH_2] == 1


# ---------------------------------------------------------------------------
# cmd_admin_cards_list
# ---------------------------------------------------------------------------


def test_list_ohne_karten_zeigt_hinweis(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    conn = _open(db)
    cmd_admin_cards_list(conn)
    conn.close()

    assert "Keine" in capsys.readouterr().out


def test_list_zeigt_alle_karten(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _insert_card(db, _UID_HASH, label="Karte Alpha")
    _insert_card(db, _UID_HASH_2, label="Karte Beta")

    conn = _open(db)
    cmd_admin_cards_list(conn)
    conn.close()

    out = capsys.readouterr().out
    assert "Karte Alpha" in out
    assert "Karte Beta" in out
    assert _UID_HASH[:16] in out
    assert _UID_HASH_2[:16] in out


def test_list_zeigt_aktiv_inaktiv_status(
    db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    card_id = _insert_card(db, _UID_HASH, label="Prüfkarte")
    conn_d = _open(db)
    cmd_admin_cards_deactivate(conn_d, _open(db), _ns(id=card_id))
    conn_d.close()

    conn = _open(db)
    cmd_admin_cards_list(conn)
    conn.close()

    out = capsys.readouterr().out
    assert "inaktiv" in out
