"""Tests für _intervals.py (Zeitraum-Hilfsfunktionen) und _auth.py (Rollenprüfung)."""

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.presentation.admin_cli._auth import (
    require_admin_or_reviewer,
)
from arbeitszeit.presentation.admin_cli._intervals import (
    day_interval,
    month_interval,
    week_interval,
)


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


# ---------------------------------------------------------------------------
# day_interval
# ---------------------------------------------------------------------------


def test_day_interval_normaler_tag() -> None:
    from_dt, to_dt = day_interval(date(2026, 3, 15))
    assert from_dt == datetime(2026, 3, 15, tzinfo=timezone.utc)
    assert to_dt == datetime(2026, 3, 16, tzinfo=timezone.utc)


def test_day_interval_monatsende() -> None:
    from_dt, to_dt = day_interval(date(2026, 1, 31))
    assert to_dt.day == 1
    assert to_dt.month == 2


def test_day_interval_dauer_24h() -> None:
    from_dt, to_dt = day_interval(date(2026, 6, 1))
    assert to_dt - from_dt == timedelta(hours=24)


# ---------------------------------------------------------------------------
# week_interval
# ---------------------------------------------------------------------------


def test_week_interval_startet_montag() -> None:
    from_dt, to_dt = week_interval(2026, 1)
    assert from_dt.weekday() == 0


def test_week_interval_dauer_7_tage() -> None:
    from_dt, to_dt = week_interval(2026, 20)
    assert (to_dt - from_dt).days == 7


def test_week_interval_utc() -> None:
    from_dt, _ = week_interval(2026, 10)
    assert from_dt.tzinfo == timezone.utc


# ---------------------------------------------------------------------------
# month_interval
# ---------------------------------------------------------------------------


def test_month_interval_normaler_monat() -> None:
    from_dt, to_dt = month_interval(2026, 3)
    assert from_dt == datetime(2026, 3, 1, tzinfo=timezone.utc)
    assert to_dt == datetime(2026, 4, 1, tzinfo=timezone.utc)


def test_month_interval_dezember_springt_ins_naechste_jahr() -> None:
    from_dt, to_dt = month_interval(2026, 12)
    assert to_dt == datetime(2027, 1, 1, tzinfo=timezone.utc)


def test_month_interval_februar() -> None:
    from_dt, to_dt = month_interval(2026, 2)
    assert from_dt.month == 2
    assert to_dt.month == 3


# ---------------------------------------------------------------------------
# require_admin_or_reviewer
# ---------------------------------------------------------------------------


def test_require_admin_or_reviewer_admin_zugelassen(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    try:
        require_admin_or_reviewer(conn, admin_id)
    finally:
        conn.close()


def test_require_admin_or_reviewer_reviewer_zugelassen(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    reviewer_id = _insert_user(db, "REVIEWER")
    conn = open_connection(db)
    try:
        require_admin_or_reviewer(conn, reviewer_id)
    finally:
        conn.close()


def test_require_admin_or_reviewer_tech_abgewiesen(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    tech_id = _insert_user(db, "TECH")
    conn = open_connection(db)
    try:
        with pytest.raises(SystemExit) as exc:
            require_admin_or_reviewer(conn, tech_id)
        assert exc.value.code == 1
    finally:
        conn.close()


def test_require_admin_or_reviewer_unbekannter_user_abgewiesen(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    conn = open_connection(db)
    try:
        with pytest.raises(SystemExit) as exc:
            require_admin_or_reviewer(conn, 9999)
        assert exc.value.code == 1
    finally:
        conn.close()
