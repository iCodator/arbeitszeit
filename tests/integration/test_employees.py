"""Integrationstests für admin_cli employees- und cards-Befehle."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.presentation.admin_cli.main import run as cli_run


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
        "VALUES ('admin', 'x', 'ADMIN', NULL, 1, '2026-01-01', '2026-01-01') "
        "RETURNING id"
    ).fetchone()
    conn.close()
    return row["id"]


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
    return row["id"]


def _seed_rfid_card(db: Path, employee_id: int, admin_id: int, uid_hash: str = "aabbcc") -> int:
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
    return row["id"]


def _get_employee(db: Path, employee_id: int) -> dict | None:
    conn = open_connection(db)
    row = conn.execute(
        "SELECT id, personnel_no, active FROM employees WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _get_card(db: Path, card_id: int) -> dict | None:
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


def test_employees_add_legt_mitarbeiter_an(tmp_path):
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


def test_employees_add_doppelte_personalnummer_schlaegt_fehl(tmp_path):
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


def test_employees_list_laeuft_ohne_fehler(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    _seed_employee(db, admin_id)

    cli_run(["--db", str(db), "--user-id", str(admin_id), "employees", "list"])


# --- employees deactivate ---


def test_employees_deactivate_setzt_active_0(tmp_path):
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


def test_employees_deactivate_unbekannte_id_schlaegt_fehl(tmp_path):
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


def test_cards_assign_legt_rfid_karte_an(tmp_path):
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
            "deadbeef",
        ]
    )

    conn = open_connection(db)
    row = conn.execute(
        "SELECT status, employee_id FROM rfid_cards WHERE uid_hash = 'deadbeef'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["status"] == "ACTIVE"
    assert row["employee_id"] == emp_id
    assert "CARD_ASSIGNED" in _audit_events(db, "rfid_cards")


# --- cards replace ---


def test_cards_replace_deaktiviert_alte_karte(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    emp_id = _seed_employee(db, admin_id)
    old_card_id = _seed_rfid_card(db, emp_id, admin_id, "aabbcc")

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
            "ddeeff",
        ]
    )

    old = _get_card(db, old_card_id)
    assert old is not None
    assert old["status"] == "REPLACED"

    conn = open_connection(db)
    new_row = conn.execute("SELECT status FROM rfid_cards WHERE uid_hash = 'ddeeff'").fetchone()
    conn.close()
    assert new_row is not None
    assert new_row["status"] == "ACTIVE"
    assert "CARD_REPLACED" in _audit_events(db, "rfid_cards")


# --- cards deactivate ---


def test_cards_deactivate_setzt_status_inactive(tmp_path):
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
