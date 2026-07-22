"""Integrationstests für admin_cli audit-Befehle."""

__version__ = "1.0"

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain import audit_events
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.presentation.admin_cli.audit import cmd_audit_open_shifts
from arbeitszeit.presentation.admin_cli.main import run as cli_run
from tests.integration.conftest import make_seed_password_hash


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
        "VALUES (?, ?, ?, NULL, 1, '2026-01-01', '2026-01-01') "
        "RETURNING id",
        (role.lower(), make_seed_password_hash(), role),
    ).fetchone()
    conn.close()
    return int(row["id"])


def _insert_employee(db: Path, personnel_no: str, first: str, last: str) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES (?, ?, ?, 1, '2026-01-01', '2026-01-01') RETURNING id",
        (personnel_no, first, last),
    ).fetchone()
    conn.close()
    return int(row["id"])


def _insert_open_shift_audit(
    db: Path,
    employee_id: int,
    event_at: datetime,
    previous_day_date: str,
    last_booking_type: str,
    last_booking_at: str,
) -> None:
    details = json.dumps(
        {
            "employee_id": employee_id,
            "last_known_booking_at": last_booking_at,
            "last_known_booking_type": last_booking_type,
            "previous_day_date": previous_day_date,
        },
        sort_keys=True,
    )
    conn = open_connection(db)
    conn.execute(
        "INSERT INTO audit_log "
        "(event_type, object_type, object_id, user_id, employee_id, event_at, details_json) "
        "VALUES (?, 'time_bookings', 1, NULL, ?, ?, ?)",
        (
            audit_events.OPEN_SHIFT_PREVIOUS_DAY_DETECTED,
            employee_id,
            event_at.isoformat(),
            details,
        ),
    )
    conn.close()


def _args(days: int = 30) -> argparse.Namespace:
    return argparse.Namespace(days=days)


# ---------------------------------------------------------------------------
# Chronologisch sortierte Ausgabe bei mehreren Einträgen
# ---------------------------------------------------------------------------


def test_mehrere_eintraege_chronologisch_sortiert(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    emp1 = _insert_employee(db, "E001", "Anna", "Müller")
    emp2 = _insert_employee(db, "E002", "Max", "Schmidt")

    now = datetime.now(timezone.utc)
    # emp2-Eintrag liegt zeitlich VOR emp1-Eintrag — Ausgabe muss emp2 zuerst zeigen
    _insert_open_shift_audit(
        db, emp2, now - timedelta(hours=2), "2026-07-20", "COME", "2026-07-20T08:00:00+00:00"
    )
    _insert_open_shift_audit(
        db, emp1, now - timedelta(hours=1), "2026-07-20", "BREAK_START", "2026-07-20T12:00:00+00:00"
    )

    conn = open_connection(db)
    try:
        cmd_audit_open_shifts(conn, _args(days=30), admin_id)
    finally:
        conn.close()

    out = capsys.readouterr().out
    assert "Schmidt, Max" in out
    assert "Müller, Anna" in out
    # Schmidt (älterer Eintrag) muss vor Müller erscheinen
    assert out.index("Schmidt") < out.index("Müller")
    assert "2 offene Vortagsschicht" in out
    assert "COME" in out
    assert "BREAK_START" in out


# ---------------------------------------------------------------------------
# Keine Einträge → verständliche Leermeldung
# ---------------------------------------------------------------------------


def test_keine_eintraege_leermeldung(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")

    conn = open_connection(db)
    try:
        cmd_audit_open_shifts(conn, _args(days=30), admin_id)
    finally:
        conn.close()

    out = capsys.readouterr().out
    assert "Keine offenen Vortagsschichten" in out
    # Kein leerer Output, kein Fehler
    assert "30" in out


# ---------------------------------------------------------------------------
# Einträge außerhalb des Zeitraums werden ausgeschlossen
# ---------------------------------------------------------------------------


def test_eintraege_ausserhalb_zeitraum_ausgeschlossen(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    emp = _insert_employee(db, "E001", "Alt", "Eintrag")

    now = datetime.now(timezone.utc)
    # Eintrag liegt 60 Tage zurück — bei --days 30 außerhalb des Fensters
    _insert_open_shift_audit(
        db, emp, now - timedelta(days=60), "2026-05-21", "GO", "2026-05-21T17:00:00+00:00"
    )
    # Eintrag liegt 5 Tage zurück — innerhalb von --days 30
    _insert_open_shift_audit(
        db, emp, now - timedelta(days=5), "2026-07-15", "COME", "2026-07-15T08:00:00+00:00"
    )

    conn = open_connection(db)
    try:
        cmd_audit_open_shifts(conn, _args(days=30), admin_id)
    finally:
        conn.close()

    out = capsys.readouterr().out
    # Nur der neuere Eintrag darf erscheinen
    assert "1 offene Vortagsschicht" in out
    assert "2026-07-15" in out
    assert "2026-05-21" not in out


# ---------------------------------------------------------------------------
# Ungültige --days-Werte → Fehlermeldung, kein Absturz
# ---------------------------------------------------------------------------


def test_days_negativ_gibt_fehlermeldung(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    with pytest.raises(SystemExit) as exc:
        cli_run(
            ["--db", str(db), "--user-id", str(admin_id), "audit", "open-shifts", "--days", "-5"]
        )
    assert exc.value.code != 0


def test_days_null_gibt_fehlermeldung(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    with pytest.raises(SystemExit) as exc:
        cli_run(
            ["--db", str(db), "--user-id", str(admin_id), "audit", "open-shifts", "--days", "0"]
        )
    assert exc.value.code != 0


def test_days_nicht_numerisch_gibt_fehlermeldung(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    with pytest.raises(SystemExit) as exc:
        cli_run(
            ["--db", str(db), "--user-id", str(admin_id), "audit", "open-shifts", "--days", "abc"]
        )
    assert exc.value.code != 0


# ---------------------------------------------------------------------------
# Rollenprüfung: REVIEWER hat Zugriff, TECH nicht
# ---------------------------------------------------------------------------


def test_reviewer_hat_zugriff(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db = _make_db(tmp_path)
    reviewer_id = _insert_user(db, "REVIEWER")
    conn = open_connection(db)
    try:
        cmd_audit_open_shifts(conn, _args(days=30), reviewer_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "Keine offenen Vortagsschichten" in out


def test_tech_wird_abgewiesen(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    tech_id = _insert_user(db, "TECH")
    conn = open_connection(db)
    try:
        with pytest.raises(SystemExit) as exc:
            cmd_audit_open_shifts(conn, _args(days=30), tech_id)
        assert exc.value.code == 1
    finally:
        conn.close()
