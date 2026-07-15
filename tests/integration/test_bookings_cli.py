"""Integrationstests für admin_cli bookings-Befehle."""

import argparse
import sys
from datetime import timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.presentation.admin_cli.bookings import (
    _parse_booking_type,
    _parse_dt,
    cmd_bookings_approve_supplement,
    cmd_bookings_correct,
    cmd_bookings_reject_supplement,
    cmd_bookings_supplement,
)
from arbeitszeit.presentation.admin_cli.main import run as cli_run


def _make_db(tmp_path: Path) -> Path:
    db = tmp_path / "test.db"
    conn = open_connection(db)
    run_migrations(conn)
    conn.close()
    return db


def _insert_user(db: Path, role: str) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, employee_id, active, created_at, updated_at) "
        "VALUES (?, 'x', ?, NULL, 1, '2026-01-01', '2026-01-01') "
        "RETURNING id",
        (role.lower(), role),
    ).fetchone()
    conn.close()
    return int(row["id"])


def _seed_employee(db: Path, admin_id: int) -> int:
    cli_run(
        [
            "--db", str(db), "--user-id", str(admin_id),
            "employees", "add",
            "--personnel-no", "E001",
            "--first-name", "Max",
            "--last-name", "Muster",
        ]
    )
    conn = open_connection(db)
    row = conn.execute("SELECT id FROM employees WHERE personnel_no = 'E001'").fetchone()
    conn.close()
    return int(row["id"])


def _insert_booking(db: Path, employee_id: int) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO time_bookings "
        "(employee_id, booking_type, booked_at, source, current_status, "
        "terminal_id, rfid_card_id, device_event_id, note, created_at) "
        "VALUES (?, 'COME', '2026-01-01T08:00:00+00:00', 'MANUAL', 'OK', "
        "NULL, NULL, NULL, NULL, '2026-01-01') "
        "RETURNING id",
        (employee_id,),
    ).fetchone()
    conn.close()
    return int(row["id"])


def _insert_supplement(db: Path, employee_id: int, admin_id: int) -> int:
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(
        employee_id=employee_id,
        type="COME",
        at="2026-01-01T08:00:00",
        reason="Test-Nachtrag",
        related_booking_id=None,
    )
    cmd_bookings_supplement(conn, audit_conn, args, admin_id)
    row = conn.execute("SELECT id FROM supplements ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    audit_conn.close()
    return int(row["id"])


# ---------------------------------------------------------------------------
# _parse_dt
# ---------------------------------------------------------------------------


def test_parse_dt_ohne_timezone_erhaelt_utc() -> None:
    dt = _parse_dt("2026-01-01T08:00:00")
    assert dt.tzinfo == timezone.utc


def test_parse_dt_mit_timezone_bleibt_erhalten() -> None:
    dt = _parse_dt("2026-01-01T08:00:00+01:00")
    assert dt.utcoffset() is not None


def test_parse_dt_ungueltig_exitiert_1() -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_dt("kein-datum")
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# _parse_booking_type
# ---------------------------------------------------------------------------


def test_parse_booking_type_gueltig() -> None:
    from arbeitszeit.domain.enums import BookingType

    assert _parse_booking_type("COME") == BookingType.COME
    assert _parse_booking_type("go") == BookingType.GO


def test_parse_booking_type_ungueltig_exitiert_1() -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_booking_type("UNGUELTIG")
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# cmd_bookings_correct
# ---------------------------------------------------------------------------


def test_bookings_correct_buchung_nicht_gefunden_exitiert_1(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(booking_id=9999, type="GO", at="2026-01-01T09:00:00", reason="x")
    try:
        with pytest.raises(SystemExit) as exc:
            cmd_bookings_correct(conn, audit_conn, args, admin_id)
        assert exc.value.code == 1
    finally:
        conn.close()
        audit_conn.close()


def test_bookings_correct_ungueltige_buchungsart_exitiert_1(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(
        booking_id=1, type="FALSCH", at="2026-01-01T09:00:00", reason="x"
    )
    try:
        with pytest.raises(SystemExit) as exc:
            cmd_bookings_correct(conn, audit_conn, args, admin_id)
        assert exc.value.code == 1
    finally:
        conn.close()
        audit_conn.close()


def test_bookings_correct_erfolg(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    employee_id = _seed_employee(db, admin_id)
    booking_id = _insert_booking(db, employee_id)
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(
        booking_id=booking_id,
        type="GO",
        at="2026-01-01T17:00:00",
        reason="Korrektur",
    )
    try:
        cmd_bookings_correct(conn, audit_conn, args, admin_id)
    finally:
        conn.close()
        audit_conn.close()
    out = capsys.readouterr().out
    assert "Korrektur angelegt" in out


# ---------------------------------------------------------------------------
# cmd_bookings_supplement
# ---------------------------------------------------------------------------


def test_bookings_supplement_mitarbeiter_nicht_gefunden_exitiert_1(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(
        employee_id=9999, type="COME", at="2026-01-01T08:00:00", reason="x", related_booking_id=None
    )
    try:
        with pytest.raises(SystemExit) as exc:
            cmd_bookings_supplement(conn, audit_conn, args, admin_id)
        assert exc.value.code == 1
    finally:
        conn.close()
        audit_conn.close()


def test_bookings_supplement_erfolg(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    employee_id = _seed_employee(db, admin_id)
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(
        employee_id=employee_id,
        type="COME",
        at="2026-01-01T08:00:00",
        reason="Vergessen",
        related_booking_id=None,
    )
    try:
        cmd_bookings_supplement(conn, audit_conn, args, admin_id)
    finally:
        conn.close()
        audit_conn.close()
    out = capsys.readouterr().out
    assert "Nachtrag angelegt" in out


# ---------------------------------------------------------------------------
# cmd_bookings_approve_supplement
# ---------------------------------------------------------------------------


def test_bookings_approve_supplement_nicht_gefunden_exitiert_1(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(supplement_id=9999)
    try:
        with pytest.raises(SystemExit) as exc:
            cmd_bookings_approve_supplement(conn, audit_conn, args, admin_id)
        assert exc.value.code == 1
    finally:
        conn.close()
        audit_conn.close()


def test_bookings_approve_supplement_erfolg(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    employee_id = _seed_employee(db, admin_id)
    supplement_id = _insert_supplement(db, employee_id, admin_id)
    capsys.readouterr()  # Ausgaben aus Setup leeren
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(supplement_id=supplement_id)
    try:
        cmd_bookings_approve_supplement(conn, audit_conn, args, admin_id)
    finally:
        conn.close()
        audit_conn.close()
    out = capsys.readouterr().out
    assert "genehmigt" in out


# ---------------------------------------------------------------------------
# cmd_bookings_reject_supplement
# ---------------------------------------------------------------------------


def test_bookings_reject_supplement_nicht_gefunden_exitiert_1(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(supplement_id=9999, reason="x")
    try:
        with pytest.raises(SystemExit) as exc:
            cmd_bookings_reject_supplement(conn, audit_conn, args, admin_id)
        assert exc.value.code == 1
    finally:
        conn.close()
        audit_conn.close()


def test_bookings_reject_supplement_erfolg(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    employee_id = _seed_employee(db, admin_id)
    supplement_id = _insert_supplement(db, employee_id, admin_id)
    capsys.readouterr()
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(supplement_id=supplement_id, reason="Begründung")
    try:
        cmd_bookings_reject_supplement(conn, audit_conn, args, admin_id)
    finally:
        conn.close()
        audit_conn.close()
    out = capsys.readouterr().out
    assert "abgelehnt" in out
