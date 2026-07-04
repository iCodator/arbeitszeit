"""Integrationstests für admin_cli reports-Befehle."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.queries import (
    BookingRow,
    CorrectionRow,
    ReviewCaseRow,
    SupplementRow,
)
from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.presentation.admin_cli.reports import (
    _get_export_dir,
    _parse_date,
    _print_bookings_table,
    _print_corrections_table,
    _print_review_cases_table,
    _print_supplements_table,
    cmd_reports_corrections,
    cmd_reports_export_csv,
    cmd_reports_export_csv_review_cases,
    cmd_reports_export_pdf_day,
    cmd_reports_export_pdf_employee,
    cmd_reports_export_pdf_month,
    cmd_reports_export_pdf_week,
    cmd_reports_open_bookings,
    cmd_reports_open_review_cases,
    cmd_reports_supplements,
    cmd_reports_warn_cases,
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
    return row["id"]


def _set_config(db: Path, key: str, value: object) -> None:
    conn = open_connection(db)
    conn.execute(
        "INSERT INTO system_config "
        "(config_key, config_value_json, version, change_origin, changed_by_user_id, changed_at) "
        "VALUES (?, ?, 2, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00')",
        (key, json.dumps(value)),
    )
    conn.close()


_NOW = datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)


def _booking_row() -> BookingRow:
    return BookingRow(
        booking_id=1,
        employee_id=1,
        personnel_no="E001",
        employee_name="Max Muster",
        booking_type=BookingType.COME,
        booked_at=_NOW,
        source=BookingSource.TERMINAL,
        status=BookingStatus.OK,
        is_manual=False,
    )


def _correction_row() -> CorrectionRow:
    return CorrectionRow(
        correction_id=1,
        booking_id=1,
        employee_id=1,
        personnel_no="E001",
        employee_name="Max Muster",
        old_booking_type=BookingType.COME,
        old_booked_at=_NOW,
        new_booking_type=BookingType.GO,
        new_booked_at=_NOW,
        reason="Tippfehler",
        corrected_by_user_id=1,
        corrected_at=_NOW,
    )


def _supplement_row() -> SupplementRow:
    return SupplementRow(
        supplement_id=1,
        employee_id=1,
        personnel_no="E001",
        employee_name="Max Muster",
        booking_type=BookingType.COME,
        event_at=_NOW,
        recorded_at=_NOW,
        reason="Vergessen",
        approval_status=ApprovalStatus.PENDING,
        related_booking_id=None,
        approved_by_user_id=None,
        approved_at=None,
    )


def _review_case_row() -> ReviewCaseRow:
    return ReviewCaseRow(
        case_id=1,
        employee_id=1,
        personnel_no="E001",
        employee_name="Max Muster",
        case_type=ReviewCaseType.OPEN_WORK_PHASE,
        severity=ReviewSeverity.CRITICAL,
        status=ReviewCaseStatus.OPEN,
        booking_id=1,
        description="Offene Arbeitsphase erkannt.",
        detected_at=_NOW,
        note=None,
    )


# ---------------------------------------------------------------------------
# _parse_date
# ---------------------------------------------------------------------------


def test_parse_date_gueltig() -> None:

    d = _parse_date("2026-03-15")
    assert d.year == 2026 and d.month == 3 and d.day == 15


def test_parse_date_ungueltig_exitiert_1() -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_date("kein-datum")
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# _get_export_dir
# ---------------------------------------------------------------------------


def test_get_export_dir_kein_config_exitiert_1(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    conn = open_connection(db)
    try:
        with pytest.raises(SystemExit) as exc:
            _get_export_dir(conn)
        assert exc.value.code == 1
    finally:
        conn.close()


def test_get_export_dir_gibt_pfad_zurueck(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    export_dir = tmp_path / "export"
    _set_config(db, "export.export_dir", str(export_dir))
    conn = open_connection(db)
    try:
        result = _get_export_dir(conn)
        assert result == str(export_dir)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# _print_*_table — leer und mit Daten
# ---------------------------------------------------------------------------


def test_print_bookings_table_leer(capsys: pytest.CaptureFixture) -> None:
    _print_bookings_table([])
    assert "Keine Buchungen" in capsys.readouterr().out


def test_print_bookings_table_mit_daten(capsys: pytest.CaptureFixture) -> None:
    _print_bookings_table([_booking_row()])
    out = capsys.readouterr().out
    assert "Max Muster" in out
    assert "1 Buchung" in out


def test_print_corrections_table_leer(capsys: pytest.CaptureFixture) -> None:
    _print_corrections_table([])
    assert "Keine Korrekturen" in capsys.readouterr().out


def test_print_corrections_table_mit_daten(capsys: pytest.CaptureFixture) -> None:
    _print_corrections_table([_correction_row()])
    out = capsys.readouterr().out
    assert "Tippfehler" in out
    assert "1 Korrektur" in out


def test_print_supplements_table_leer(capsys: pytest.CaptureFixture) -> None:
    _print_supplements_table([])
    assert "Keine Nachträge" in capsys.readouterr().out


def test_print_supplements_table_mit_daten(capsys: pytest.CaptureFixture) -> None:
    _print_supplements_table([_supplement_row()])
    out = capsys.readouterr().out
    assert "Vergessen" in out
    assert "1 Nachtrag" in out


def test_print_review_cases_table_leer(capsys: pytest.CaptureFixture) -> None:
    _print_review_cases_table([])
    assert "Keine Prüffälle" in capsys.readouterr().out


def test_print_review_cases_table_mit_daten(capsys: pytest.CaptureFixture) -> None:
    _print_review_cases_table([_review_case_row()])
    out = capsys.readouterr().out
    assert "Offene Arbeitsphase" in out
    assert "1 Prüffall" in out


# ---------------------------------------------------------------------------
# cmd_reports_open_bookings
# ---------------------------------------------------------------------------


def test_open_bookings_alle_leere_db(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    args = argparse.Namespace(employee_id=None, from_date=None, to_date=None)
    try:
        cmd_reports_open_bookings(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "alle" in out
    assert "Keine Buchungen" in out


def test_open_bookings_mit_zeitraum(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    args = argparse.Namespace(
        employee_id=None, from_date="2026-01-01", to_date="2026-01-31"
    )
    try:
        cmd_reports_open_bookings(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "2026-01-01" in out


def test_open_bookings_reviewer_zugelassen(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    reviewer_id = _insert_user(db, "REVIEWER")
    conn = open_connection(db)
    args = argparse.Namespace(employee_id=None, from_date=None, to_date=None)
    try:
        cmd_reports_open_bookings(conn, args, reviewer_id)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# cmd_reports_warn_cases
# ---------------------------------------------------------------------------


def test_warn_cases_leere_db(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    args = argparse.Namespace(from_date="2026-01-01", to_date="2026-01-31", employee_id=None)
    try:
        cmd_reports_warn_cases(conn, args, admin_id)
    finally:
        conn.close()
    assert "Keine Buchungen" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# cmd_reports_corrections
# ---------------------------------------------------------------------------


def test_corrections_leere_db(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    args = argparse.Namespace(from_date="2026-01-01", to_date="2026-01-31", employee_id=None)
    try:
        cmd_reports_corrections(conn, args, admin_id)
    finally:
        conn.close()
    assert "Keine Korrekturen" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# cmd_reports_supplements
# ---------------------------------------------------------------------------


def test_supplements_leere_db(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    args = argparse.Namespace(from_date="2026-01-01", to_date="2026-01-31", employee_id=None)
    try:
        cmd_reports_supplements(conn, args, admin_id)
    finally:
        conn.close()
    assert "Keine Nachträge" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# cmd_reports_open_review_cases
# ---------------------------------------------------------------------------


def test_open_review_cases_alle_leere_db(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    args = argparse.Namespace(employee_id=None, from_date=None, to_date=None)
    try:
        cmd_reports_open_review_cases(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "alle" in out
    assert "Keine Prüffälle" in out


def test_open_review_cases_mit_zeitraum(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    conn = open_connection(db)
    args = argparse.Namespace(
        employee_id=None, from_date="2026-01-01", to_date="2026-01-31"
    )
    try:
        cmd_reports_open_review_cases(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "2026-01-01" in out


# ---------------------------------------------------------------------------
# Export-Befehle (mit gemockten Exportern)
# ---------------------------------------------------------------------------


def test_export_csv_gibt_pfade_aus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    _set_config(db, "export.export_dir", str(export_dir))

    monkeypatch.setattr(
        "arbeitszeit.presentation.admin_cli.reports.csv_exporter.export_detail",
        lambda *a, **kw: tmp_path / "detail.csv",
    )
    monkeypatch.setattr(
        "arbeitszeit.presentation.admin_cli.reports.csv_exporter.export_condensed",
        lambda *a, **kw: tmp_path / "condensed.csv",
    )

    conn = open_connection(db)
    args = argparse.Namespace(from_date="2026-01-01", to_date="2026-01-31", employee_id=None)
    try:
        cmd_reports_export_csv(conn, args, admin_id)
    finally:
        conn.close()
    out = capsys.readouterr().out
    assert "detail.csv" in out
    assert "condensed.csv" in out


def test_export_csv_review_cases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    _set_config(db, "export.export_dir", str(export_dir))

    monkeypatch.setattr(
        "arbeitszeit.presentation.admin_cli.reports.csv_exporter.export_review_cases",
        lambda *a, **kw: tmp_path / "review_cases.csv",
    )

    conn = open_connection(db)
    args = argparse.Namespace(from_date="2026-01-01", to_date="2026-01-31", employee_id=None)
    try:
        cmd_reports_export_csv_review_cases(conn, args, admin_id)
    finally:
        conn.close()
    assert "review_cases.csv" in capsys.readouterr().out


def test_export_pdf_day(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    _set_config(db, "export.export_dir", str(export_dir))

    monkeypatch.setattr(
        "arbeitszeit.presentation.admin_cli.reports.pdf_report_service.create_daily_report",
        lambda *a, **kw: tmp_path / "day.pdf",
    )

    conn = open_connection(db)
    args = argparse.Namespace(date="2026-01-15")
    try:
        cmd_reports_export_pdf_day(conn, args, admin_id)
    finally:
        conn.close()
    assert "day.pdf" in capsys.readouterr().out


def test_export_pdf_week(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    _set_config(db, "export.export_dir", str(export_dir))

    monkeypatch.setattr(
        "arbeitszeit.presentation.admin_cli.reports.pdf_report_service.create_weekly_report",
        lambda *a, **kw: tmp_path / "week.pdf",
    )

    conn = open_connection(db)
    args = argparse.Namespace(year=2026, week=3)
    try:
        cmd_reports_export_pdf_week(conn, args, admin_id)
    finally:
        conn.close()
    assert "week.pdf" in capsys.readouterr().out


def test_export_pdf_month(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    _set_config(db, "export.export_dir", str(export_dir))

    monkeypatch.setattr(
        "arbeitszeit.presentation.admin_cli.reports.pdf_report_service.create_monthly_report",
        lambda *a, **kw: tmp_path / "month.pdf",
    )

    conn = open_connection(db)
    args = argparse.Namespace(year=2026, month=1)
    try:
        cmd_reports_export_pdf_month(conn, args, admin_id)
    finally:
        conn.close()
    assert "month.pdf" in capsys.readouterr().out


def test_export_pdf_employee(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    admin_id = _insert_user(db, "ADMIN")
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    _set_config(db, "export.export_dir", str(export_dir))

    monkeypatch.setattr(
        "arbeitszeit.presentation.admin_cli.reports.pdf_report_service.create_employee_report",
        lambda *a, **kw: tmp_path / "employee.pdf",
    )

    conn = open_connection(db)
    args = argparse.Namespace(employee_id=1, from_date="2026-01-01", to_date="2026-01-31")
    try:
        cmd_reports_export_pdf_employee(conn, args, admin_id)
    finally:
        conn.close()
    assert "employee.pdf" in capsys.readouterr().out
