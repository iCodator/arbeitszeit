"""Integrationstests für admin_cli schedule-Befehle."""

import argparse
import sqlite3
import sys
from datetime import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.presentation.admin_cli.schedule import (
    _parse_time,
    cmd_schedule_set,
    cmd_schedule_show,
)


def _make_db(tmp_path: Path) -> Path:
    db = tmp_path / "test.db"
    conn = open_connection(db)
    run_migrations(conn)
    conn.execute("DELETE FROM work_schedule_versions")
    conn.close()
    return db


def _insert_employee(conn: "sqlite3.Connection") -> int:
    row = conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E001', 'Max', 'Muster', 1, '2026-01-01', '2026-01-01') RETURNING id"
    ).fetchone()
    return int(row["id"])


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


# ---------------------------------------------------------------------------
# _parse_time
# ---------------------------------------------------------------------------


def test_parse_time_gueltig() -> None:
    assert _parse_time("08:30") == time(8, 30)


def test_parse_time_null_uhr() -> None:
    assert _parse_time("00:00") == time(0, 0)


def test_parse_time_ungueltig_exitiert_1() -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_time("nicht-eine-uhrzeit")
    assert exc.value.code == 1


def test_parse_time_nur_stunden_exitiert_1() -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_time("08")
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# cmd_schedule_show
# ---------------------------------------------------------------------------


def test_schedule_show_leere_db(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    args = argparse.Namespace()
    try:
        cmd_schedule_show(conn, args, admin_id)
    finally:
        conn.close()
    assert "Keine aktiven" in capsys.readouterr().out


def test_schedule_show_reviewer_zugelassen(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    reviewer_id = _insert_user(db, "REVIEWER")
    conn = open_connection(db)
    args = argparse.Namespace()
    try:
        cmd_schedule_show(conn, args, reviewer_id)
    finally:
        conn.close()


def test_schedule_show_globale_version(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    conn.execute(
        "INSERT INTO work_schedule_versions "
        "(scope_type, scope_employee_id, weekday, start_time, end_time, valid_from, valid_until, "
        "change_origin, changed_by_user_id, changed_at) "
        "VALUES ('GLOBAL', NULL, 1, '07:30', '16:00', '2026-01-01', NULL, "
        "'MIGRATION', NULL, '2026-01-01T00:00:00')"
    )
    args = argparse.Namespace()
    try:
        cmd_schedule_show(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "Globale" in out
    assert "Mo" in out


def test_schedule_show_mitarbeiterspezifisch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    employee_id = _insert_employee(conn)
    conn.execute(
        "INSERT INTO work_schedule_versions "
        "(scope_type, scope_employee_id, weekday, start_time, end_time, valid_from, valid_until, "
        "change_origin, changed_by_user_id, changed_at) "
        "VALUES ('EMPLOYEE', ?, 2, '08:00', '17:00', '2026-01-01', NULL, "
        "'MIGRATION', NULL, '2026-01-01T00:00:00')",
        (employee_id,),
    )
    args = argparse.Namespace()
    try:
        cmd_schedule_show(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "Mitarbeiterspezifisch" in out


def test_schedule_show_nur_global_zeigt_hinweis(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    conn.execute(
        "INSERT INTO work_schedule_versions "
        "(scope_type, scope_employee_id, weekday, start_time, end_time, valid_from, valid_until, "
        "change_origin, changed_by_user_id, changed_at) "
        "VALUES ('GLOBAL', NULL, 1, '07:30', '16:00', '2026-01-01', NULL, "
        "'MIGRATION', NULL, '2026-01-01T00:00:00')"
    )
    args = argparse.Namespace()
    try:
        cmd_schedule_show(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "Globale Praxisregel" in out


def test_schedule_show_nur_mitarbeiter_zeigt_hinweis(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    employee_id = _insert_employee(conn)
    conn.execute(
        "INSERT INTO work_schedule_versions "
        "(scope_type, scope_employee_id, weekday, start_time, end_time, valid_from, valid_until, "
        "change_origin, changed_by_user_id, changed_at) "
        "VALUES ('EMPLOYEE', ?, 3, '08:00', '17:00', '2026-01-01', NULL, "
        "'MIGRATION', NULL, '2026-01-01T00:00:00')",
        (employee_id,),
    )
    args = argparse.Namespace()
    try:
        cmd_schedule_show(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "Keine globale" in out


# ---------------------------------------------------------------------------
# cmd_schedule_set
# ---------------------------------------------------------------------------


def test_schedule_set_ungueltige_datum_exitiert_1(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(
        from_date="kein-datum",
        weekday=1,
        start="07:30",
        end="16:00",
        employee_id=None,
    )
    try:
        with pytest.raises(SystemExit) as exc:
            cmd_schedule_set(conn, audit_conn, args, admin_id)
        assert exc.value.code == 1
    finally:
        conn.close()
        audit_conn.close()


def test_schedule_set_global_erfolg(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    audit_conn = open_connection(db)
    args = argparse.Namespace(
        from_date="01.01.2026",
        weekday=1,
        start="07:30",
        end="16:00",
        employee_id=None,
    )
    try:
        cmd_schedule_set(conn, audit_conn, args, admin_id)
    finally:
        conn.close()
        audit_conn.close()
    out = capsys.readouterr().out
    assert "Globale" in out
    assert "Mo" in out
