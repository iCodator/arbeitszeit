"""Integrationstests für admin_cli employees- und cards-Befehle."""

__version__ = "1.3"

import argparse
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.hardware import EmptyUidError, HardwareTimeoutError
from arbeitszeit.infrastructure.hardware.evdev_reader import DeviceNotFoundError
from arbeitszeit.presentation.admin_cli.employees import _resolve_uid_hash, _validate_uid_source
from arbeitszeit.presentation.admin_cli.main import run as cli_run
from tests.integration.conftest import make_seed_password_hash

_MOD = "arbeitszeit.presentation.admin_cli.employees"

_HASH_A = "aabbccdd" * 8  # 64 Hex-Zeichen für Standardkarte
_HASH_B = "ddeeff00" * 8  # 64 Hex-Zeichen für Ersatzkarte
_VALID_HASH = "deadbeef" * 8  # 64 Hex-Zeichen


def _make_db(tmp_path: Path) -> Path:
    db = tmp_path / "arbeitszeit.db"
    conn = open_connection(db)
    run_migrations(conn)
    conn.close()
    return db


def _seed_admin(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, employee_id, active, created_at, updated_at) "
        "VALUES ('admin', ?, 'ADMIN', NULL, 1, '2026-01-01', '2026-01-01') "
        "RETURNING id",
        (make_seed_password_hash(),),
    ).fetchone()
    conn.close()
    return int(row["id"])


def _seed_employee(db: Path, admin_id: int, personnel_no: str = "E001") -> int:
    cli_run(
        [
            "--db",
            str(db),
            "--user-id",
            str(admin_id),
            "employees",
            "add",
            "--personnel-no",
            personnel_no,
            "--first-name",
            "Test",
            "--last-name",
            "Nutzer",
        ]
    )
    conn = open_connection(db)
    row = conn.execute(
        "SELECT id FROM employees WHERE personnel_no = ?", (personnel_no,)
    ).fetchone()
    conn.close()
    return int(row["id"])


def _seed_rfid_card(db: Path, employee_id: int, admin_id: int, uid_hash: str = _HASH_A) -> int:
    cli_run(
        [
            "--db",
            str(db),
            "--user-id",
            str(admin_id),
            "cards",
            "assign",
            "--employee-id",
            str(employee_id),
            "--uid-hash",
            uid_hash,
        ]
    )
    conn = open_connection(db)
    row = conn.execute(
        "SELECT id FROM rfid_cards WHERE uid_hash = ?", (uid_hash,)
    ).fetchone()
    conn.close()
    return int(row["id"])


def _get_employee(db: Path, employee_id: int) -> dict[str, object] | None:
    conn = open_connection(db)
    row = conn.execute(
        "SELECT id, personnel_no, active FROM employees WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _get_card(db: Path, card_id: int) -> dict[str, object] | None:
    conn = open_connection(db)
    row = conn.execute(
        "SELECT id, status, employee_id FROM rfid_cards WHERE id = ?", (card_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _audit_events(db: Path, object_type: str) -> list[str]:
    conn = open_connection(db)
    rows = conn.execute(
        "SELECT event_type FROM audit_log WHERE object_type = ? ORDER BY id",
        (object_type,),
    ).fetchall()
    conn.close()
    return [r["event_type"] for r in rows]


# --- employees add ---


def test_employees_add_legt_mitarbeiter_an(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)

    cli_run(
        [
            "--db",
            str(db),
            "--user-id",
            str(admin_id),
            "employees",
            "add",
            "--personnel-no",
            "E001",
            "--first-name",
            "Anna",
            "--last-name",
            "Muster",
        ]
    )

    conn = open_connection(db)
    row = conn.execute(
        "SELECT personnel_no, active FROM employees WHERE personnel_no = 'E001'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["active"] == 1
    assert "EMPLOYEE_CREATED" in _audit_events(db, "employees")


def test_employees_add_doppelte_personalnummer_schlaegt_fehl(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    _seed_employee(db, admin_id, "E001")

    with pytest.raises(SystemExit):
        cli_run(
            [
                "--db",
                str(db),
                "--user-id",
                str(admin_id),
                "employees",
                "add",
                "--personnel-no",
                "E001",
                "--first-name",
                "Zweite",
                "--last-name",
                "Person",
            ]
        )

    conn = open_connection(db)
    count = conn.execute("SELECT COUNT(*) FROM employees WHERE personnel_no = 'E001'").fetchone()[0]
    conn.close()
    assert count == 1


# --- employees list ---


def test_employees_list_laeuft_ohne_fehler(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    _seed_employee(db, admin_id)

    cli_run(["--db", str(db), "--user-id", str(admin_id), "employees", "list"])


# --- employees deactivate ---


def test_employees_deactivate_setzt_active_0(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    emp_id = _seed_employee(db, admin_id)

    cli_run(
        [
            "--db",
            str(db),
            "--user-id",
            str(admin_id),
            "employees",
            "deactivate",
            str(emp_id),
        ]
    )

    emp = _get_employee(db, emp_id)
    assert emp is not None
    assert emp["active"] == 0
    assert "EMPLOYEE_DEACTIVATED" in _audit_events(db, "employees")


def test_employees_deactivate_unbekannte_id_schlaegt_fehl(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)

    with pytest.raises(SystemExit):
        cli_run(
            [
                "--db",
                str(db),
                "--user-id",
                str(admin_id),
                "employees",
                "deactivate",
                "9999",
            ]
        )


# --- cards assign ---


def test_cards_assign_legt_rfid_karte_an(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    emp_id = _seed_employee(db, admin_id)

    cli_run(
        [
            "--db",
            str(db),
            "--user-id",
            str(admin_id),
            "cards",
            "assign",
            "--employee-id",
            str(emp_id),
            "--uid-hash",
            _VALID_HASH,
        ]
    )

    conn = open_connection(db)
    row = conn.execute(
        "SELECT status, employee_id FROM rfid_cards WHERE uid_hash = ?",
        (_VALID_HASH,),
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["status"] == "ACTIVE"
    assert row["employee_id"] == emp_id
    assert "CARD_ASSIGNED" in _audit_events(db, "rfid_cards")


# --- cards replace ---


def test_cards_replace_deaktiviert_alte_karte(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    emp_id = _seed_employee(db, admin_id)
    old_card_id = _seed_rfid_card(db, emp_id, admin_id, _HASH_A)

    cli_run(
        [
            "--db",
            str(db),
            "--user-id",
            str(admin_id),
            "cards",
            "replace",
            "--old-card-id",
            str(old_card_id),
            "--uid-hash",
            _HASH_B,
        ]
    )

    old = _get_card(db, old_card_id)
    assert old is not None
    assert old["status"] == "REPLACED"

    conn = open_connection(db)
    new_row = conn.execute(
        "SELECT status FROM rfid_cards WHERE uid_hash = ?", (_HASH_B,)
    ).fetchone()
    conn.close()
    assert new_row is not None
    assert new_row["status"] == "ACTIVE"
    assert "CARD_REPLACED" in _audit_events(db, "rfid_cards")


# --- cards deactivate ---


def test_cards_deactivate_setzt_status_inactive(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    emp_id = _seed_employee(db, admin_id)
    card_id = _seed_rfid_card(db, emp_id, admin_id)

    cli_run(
        [
            "--db",
            str(db),
            "--user-id",
            str(admin_id),
            "cards",
            "deactivate",
            str(card_id),
        ]
    )

    card = _get_card(db, card_id)
    assert card is not None
    assert card["status"] == "INACTIVE"
    assert "CARD_DEACTIVATED" in _audit_events(db, "rfid_cards")


# ---------------------------------------------------------------------------
# employees list – Leerfall
# ---------------------------------------------------------------------------


def test_employees_list_keine_mitarbeiter(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run(["--db", str(db), "--user-id", str(admin_id), "employees", "list"])
    assert "Keine Mitarbeiter" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# _validate_uid_source – Einheitstests
# ---------------------------------------------------------------------------


def _args(**kwargs: object) -> argparse.Namespace:
    ns = argparse.Namespace(uid_hash=None, scan=False, rfid=None, employee_id=1)
    for key, val in kwargs.items():
        setattr(ns, key, val)
    return ns


def test_validate_uid_source_uid_hash_und_scan_schliessen_sich_aus(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        _validate_uid_source(_args(uid_hash="abc", scan=True), None)
    assert exc_info.value.code == 1
    assert "schließen sich aus" in capsys.readouterr().err


def test_validate_uid_source_kein_uid_quelle_fehler(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        _validate_uid_source(_args(uid_hash=None, scan=False), None)
    assert exc_info.value.code == 1
    assert "erforderlich" in capsys.readouterr().err


def test_validate_uid_source_scan_ohne_rfid_fehler(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        _validate_uid_source(_args(scan=True), None)
    assert exc_info.value.code == 1
    assert "--rfid" in capsys.readouterr().err


def test_validate_uid_source_uid_hash_gueltig_kein_fehler() -> None:
    _validate_uid_source(_args(uid_hash="deadbeef"), None)  # darf nicht werfen


def test_validate_uid_source_scan_mit_rfid_gueltig() -> None:
    _validate_uid_source(_args(scan=True), "/dev/input/event0")  # darf nicht werfen


# ---------------------------------------------------------------------------
# _resolve_uid_hash – Einheitstests
# ---------------------------------------------------------------------------


def test_resolve_uid_hash_uid_hash_direkt() -> None:
    assert _resolve_uid_hash(_args(scan=False, uid_hash=_VALID_HASH), None) == _VALID_HASH


def test_resolve_uid_hash_ungueltige_formatierung_loest_fehler(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--uid-hash mit ungültigem Format (nicht 64 Hex-Zeichen) muss SystemExit auslösen."""
    with pytest.raises(SystemExit) as exc_info:
        _resolve_uid_hash(_args(scan=False, uid_hash="abc123"), None)
    assert exc_info.value.code == 1
    assert "uid-hash" in capsys.readouterr().err.lower()


def test_resolve_uid_hash_scan_device_not_found(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch(f"{_MOD}.resolve_evdev_device", side_effect=DeviceNotFoundError("Nicht gefunden")),
        pytest.raises(SystemExit) as exc_info,
    ):
        _resolve_uid_hash(_args(scan=True), "USB Numpad")
    assert exc_info.value.code == 1
    assert "Nicht gefunden" in capsys.readouterr().err


def test_resolve_uid_hash_scan_timeout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch(f"{_MOD}.resolve_evdev_device", return_value="/dev/input/event0"),
        patch(f"{_MOD}.scan_rfid_uid_hash", side_effect=HardwareTimeoutError("Timeout")),
        pytest.raises(SystemExit) as exc_info,
    ):
        _resolve_uid_hash(_args(scan=True), "USB Numpad")
    assert exc_info.value.code == 1
    assert "Timeout" in capsys.readouterr().err


def test_resolve_uid_hash_scan_empty_uid(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch(f"{_MOD}.resolve_evdev_device", return_value="/dev/input/event0"),
        patch(f"{_MOD}.scan_rfid_uid_hash", side_effect=EmptyUidError("Leere UID")),
        pytest.raises(SystemExit) as exc_info,
    ):
        _resolve_uid_hash(_args(scan=True), "USB Numpad")
    assert exc_info.value.code == 1


def test_resolve_uid_hash_scan_os_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch(f"{_MOD}.resolve_evdev_device", return_value="/dev/input/event0"),
        patch(f"{_MOD}.scan_rfid_uid_hash", side_effect=OSError("Gerätedatei fehlt")),
        pytest.raises(SystemExit) as exc_info,
    ):
        _resolve_uid_hash(_args(scan=True), "USB Numpad")
    assert exc_info.value.code == 1
    assert "Gerätedatei" in capsys.readouterr().err


def test_resolve_uid_hash_scan_erfolg() -> None:
    with (
        patch(f"{_MOD}.resolve_evdev_device", return_value="/dev/input/event0"),
        patch(f"{_MOD}.scan_rfid_uid_hash", return_value="cafebabe"),
    ):
        result = _resolve_uid_hash(_args(scan=True), "USB Numpad")
    assert result == "cafebabe"


# ---------------------------------------------------------------------------
# cmd_cards_assign / replace / deactivate – DomainError-Pfade
# ---------------------------------------------------------------------------


def test_cards_assign_unbekannte_employee_id_fehler(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    with pytest.raises(SystemExit) as exc_info:
        cli_run(
            [
                "--db", str(db), "--user-id", str(admin_id),
                "cards", "assign", "--employee-id", "9999", "--uid-hash", _VALID_HASH,
            ]
        )
    assert exc_info.value.code == 1
    assert "Fehler" in capsys.readouterr().err


def test_cards_replace_unbekannte_karte_fehler(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    with pytest.raises(SystemExit) as exc_info:
        cli_run(
            [
                "--db", str(db), "--user-id", str(admin_id),
                "cards", "replace", "--old-card-id", "9999", "--uid-hash", _VALID_HASH,
            ]
        )
    assert exc_info.value.code == 1
    assert "Fehler" in capsys.readouterr().err


def test_cards_deactivate_unbekannte_karte_fehler(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    with pytest.raises(SystemExit) as exc_info:
        cli_run(
            [
                "--db", str(db), "--user-id", str(admin_id),
                "cards", "deactivate", "9999",
            ]
        )
    assert exc_info.value.code == 1
    assert "Fehler" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# config.toml-Fallback für --rfid bei cards assign
# ---------------------------------------------------------------------------


def test_validate_uid_source_ohne_rfid_und_ohne_config(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        _validate_uid_source(_args(scan=True), None)
    assert exc_info.value.code == 1
    assert "config.toml" in capsys.readouterr().err


def test_validate_uid_source_config_rfid_ausreichend() -> None:
    _validate_uid_source(_args(scan=True), "Sycreader RFID Technology")  # darf nicht werfen


def test_resolve_uid_hash_config_fallback() -> None:
    """rfid_device aus config.toml (kein args.rfid) wird an resolve_evdev_device übergeben."""
    config_rfid = "Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader"
    with (
        patch(f"{_MOD}.resolve_evdev_device", return_value="/dev/input/event0") as mock_resolve,
        patch(f"{_MOD}.scan_rfid_uid_hash", return_value="feedcafe"),
    ):
        result = _resolve_uid_hash(_args(scan=True), config_rfid)
    assert result == "feedcafe"
    mock_resolve.assert_called_once_with(config_rfid)


def test_cmd_cards_assign_scan_verwendet_config_rfid(tmp_path: Path) -> None:
    """Ohne --rfid: app_config.terminal.rfid wird als RFID-Gerät verwendet (Ende-zu-Ende)."""
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    emp_id = _seed_employee(db, admin_id)

    config_path = tmp_path / "config.toml"
    config_path.write_text('[terminal]\nrfid = "Sycreader RFID"\n', encoding="utf-8")

    with (
        patch(f"{_MOD}.resolve_evdev_device", return_value="/dev/input/event0"),
        patch(f"{_MOD}.scan_rfid_uid_hash", return_value="feedcafe"),
    ):
        cli_run(
            [
                "--db", str(db),
                "--config", str(config_path),
                "--user-id", str(admin_id),
                "cards", "assign",
                "--employee-id", str(emp_id),
                "--scan",
                # kein --rfid; RFID-Gerät kommt aus config.toml
            ]
        )

    conn = open_connection(db)
    row = conn.execute("SELECT uid_hash FROM rfid_cards WHERE uid_hash = 'feedcafe'").fetchone()
    conn.close()
    assert row is not None
