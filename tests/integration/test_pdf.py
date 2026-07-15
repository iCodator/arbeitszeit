"""Integrationstests für pdf_report_service.py.

Prüft: PDF wird erzeugt, hat validen Header, enthält Inhalt (Seitenanzahl > 0),
Dateiname entspricht Konvention, Pflichtabschnitte und Erläuterungen vorhanden.
"""

import json
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pypdf
import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.export.pdf_report_service import (
    create_daily_report,
    create_employee_report,
    create_monthly_report,
    create_weekly_report,
)

_REPORT_NOW = datetime(2025, 6, 1, 18, 0, tzinfo=timezone.utc)
_NOW = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)
_LATER = datetime(2025, 6, 1, 17, 0, tzinfo=timezone.utc)
_FROM = datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc)
_TO = datetime(2025, 6, 30, 23, 59, tzinfo=timezone.utc)


@pytest.fixture
def export_dir(tmp_path: Path) -> Path:
    return tmp_path / "pdf"


def _insert_employee(conn: sqlite3.Connection, personnel_no: str = "E001") -> int:
    return int(
        conn.execute(
            "INSERT INTO employees (personnel_no, first_name, last_name, active, "
            "created_at, updated_at) VALUES (?, 'Anna', 'Muster', 1, "
            "'2025-01-01', '2025-01-01') RETURNING id",
            (personnel_no,),
        ).fetchone()["id"]
    )


def _insert_booking(
    conn: sqlite3.Connection,
    employee_id: int,
    booking_type: str = "COME",
    booked_at: datetime = _NOW,
    status: str = "OPEN",
) -> int:
    return int(
        conn.execute(
            "INSERT INTO time_bookings (employee_id, booking_type, booked_at, "
            "source, current_status, created_at) "
            "VALUES (?, ?, ?, 'TERMINAL', ?, '2025-01-01T00:00:00+00:00') RETURNING id",
            (employee_id, booking_type, booked_at.isoformat(), status),
        ).fetchone()["id"]
    )


def _ensure_user(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id FROM user_accounts LIMIT 1").fetchone()
    if row:
        return int(row["id"])
    return int(
        conn.execute(
            "INSERT INTO user_accounts (username, password_hash, role, active, "
            "created_at, updated_at) VALUES ('admin', 'x', 'ADMIN', 1, "
            "'2025-01-01', '2025-01-01') RETURNING id"
        ).fetchone()["id"]
    )


def _insert_correction_for(conn: sqlite3.Connection, booking_id: int) -> int:
    user_id = _ensure_user(conn)
    old = json.dumps({"booking_type": "COME", "booked_at": _NOW.isoformat()})
    new = json.dumps({"booking_type": "GO", "booked_at": _LATER.isoformat()})
    return int(
        conn.execute(
            "INSERT INTO booking_corrections "
            "(time_booking_id, old_values_json, new_values_json, reason, "
            "corrected_by_user_id, corrected_at) "
            "VALUES (?, ?, ?, 'Testkorrektur', ?, ?) RETURNING id",
            (booking_id, old, new, user_id, _NOW.isoformat()),
        ).fetchone()["id"]
    )


def _insert_supplement_for(conn: sqlite3.Connection, employee_id: int) -> int:
    user_id = _ensure_user(conn)
    return int(
        conn.execute(
            "INSERT INTO supplements "
            "(employee_id, booking_type, event_at, recorded_at, reason, "
            "recorded_by_user_id, approval_status) "
            "VALUES (?, 'COME', ?, ?, 'Testnachtrag', ?, 'PENDING') RETURNING id",
            (employee_id, _NOW.isoformat(), _NOW.isoformat(), user_id),
        ).fetchone()["id"]
    )


def _insert_review_case_for(conn: sqlite3.Connection, employee_id: int) -> int:
    return int(
        conn.execute(
            "INSERT INTO review_cases "
            "(employee_id, case_type, severity, status, description, detected_at) "
            "VALUES (?, 'OPEN_WORK_PHASE', 'WARN', 'OPEN', 'Testfall', ?) RETURNING id",
            (employee_id, _NOW.isoformat()),
        ).fetchone()["id"]
    )


def _is_valid_pdf(path: Path) -> bool:
    with path.open("rb") as f:
        return f.read(4) == b"%PDF"


def _pdf_text(path: Path) -> str:
    reader = pypdf.PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


_PFLICHT_ABSCHNITTE = [
    "Buchungen",
    "Korrekturen",
    "Nachträge",
    "Offene Prüffälle",
    "Erläuterungen",
]


# ---------------------------------------------------------------------------
# Hilfsfunktionen für alle Berichte
# ---------------------------------------------------------------------------


def _base_setup(conn: sqlite3.Connection) -> int:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, "COME", _NOW, "OPEN")
    _insert_booking(conn, emp_id, "GO", _LATER, "OK")
    return emp_id


# ---------------------------------------------------------------------------
# Tagesbericht
# ---------------------------------------------------------------------------


def test_tagesbericht_dateiname_korrekt(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_daily_report(conn, date(2025, 6, 1), export_dir, now=_REPORT_NOW)
    assert path.name == "bericht_tag_2025-06-01_20250601T180000Z.pdf"


def test_tagesbericht_valides_pdf(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_daily_report(conn, date(2025, 6, 1), export_dir, now=_REPORT_NOW)
    assert path.exists()
    assert _is_valid_pdf(path)
    assert path.stat().st_size > 1000


def test_tagesbericht_leerer_tag_erzeugt_pdf(conn: sqlite3.Connection, export_dir: Path) -> None:
    path = create_daily_report(conn, date(2025, 6, 1), export_dir, now=_REPORT_NOW)
    assert path.exists()
    assert _is_valid_pdf(path)


def test_tagesbericht_verzeichnis_wird_angelegt(conn: sqlite3.Connection, export_dir: Path) -> None:
    subdir = export_dir / "sub"
    create_daily_report(conn, date(2025, 6, 1), subdir, now=_REPORT_NOW)
    assert subdir.exists()


# ---------------------------------------------------------------------------
# Wochenbericht
# ---------------------------------------------------------------------------


def test_wochenbericht_dateiname_korrekt(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_weekly_report(conn, 2025, 23, export_dir, now=_REPORT_NOW)
    assert path.name == "bericht_woche_2025-W23_20250601T180000Z.pdf"


def test_wochenbericht_valides_pdf(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_weekly_report(conn, 2025, 23, export_dir, now=_REPORT_NOW)
    assert path.exists()
    assert _is_valid_pdf(path)
    assert path.stat().st_size > 1000


# ---------------------------------------------------------------------------
# Monatsbericht
# ---------------------------------------------------------------------------


def test_monatsbericht_dateiname_korrekt(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_monthly_report(conn, 2025, 6, export_dir, now=_REPORT_NOW)
    assert path.name == "bericht_monat_2025-06_20250601T180000Z.pdf"


def test_monatsbericht_valides_pdf(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_monthly_report(conn, 2025, 6, export_dir, now=_REPORT_NOW)
    assert path.exists()
    assert _is_valid_pdf(path)
    assert path.stat().st_size > 1000


# ---------------------------------------------------------------------------
# Mitarbeiterbericht
# ---------------------------------------------------------------------------


def test_mitarbeiterbericht_dateiname_korrekt(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _base_setup(conn)
    path = create_employee_report(conn, emp_id, _FROM, _TO, export_dir, now=_REPORT_NOW)
    assert path.name == "bericht_mitarbeiter_E001_20250601_20250630_20250601T180000Z.pdf"


def test_mitarbeiterbericht_valides_pdf(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _base_setup(conn)
    path = create_employee_report(conn, emp_id, _FROM, _TO, export_dir, now=_REPORT_NOW)
    assert path.exists()
    assert _is_valid_pdf(path)
    assert path.stat().st_size > 1000


def test_mitarbeiterbericht_filtert_nach_employee(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_booking(conn, emp1, "COME", _NOW, "OPEN")
    _insert_booking(conn, emp2, "COME", _NOW, "OPEN")

    path1 = create_employee_report(conn, emp1, _FROM, _TO, export_dir, now=_REPORT_NOW)
    path2 = create_employee_report(
        conn,
        emp2,
        _FROM,
        _TO,
        export_dir,
        now=datetime(2025, 6, 1, 18, 1, tzinfo=timezone.utc),
    )

    assert "E001" in path1.name
    assert "E002" in path2.name
    assert path1.name != path2.name


# ---------------------------------------------------------------------------
# Pflichtfall: Schlüsselfelder vorhanden (Zeitraum, Erstellungszeitpunkt)
# ---------------------------------------------------------------------------


def test_alle_vier_berichtstypen_erzeugen_gueltige_pdfs(conn: sqlite3.Connection, export_dir: Path) -> None:
    """Pflichtenheft v3 §7.11 + §16: Alle vier Berichte müssen generierbar sein."""
    emp_id = _base_setup(conn)
    results = [
        create_daily_report(conn, date(2025, 6, 1), export_dir, now=_REPORT_NOW),
        create_weekly_report(conn, 2025, 23, export_dir, now=_REPORT_NOW),
        create_monthly_report(conn, 2025, 6, export_dir, now=_REPORT_NOW),
        create_employee_report(conn, emp_id, _FROM, _TO, export_dir, now=_REPORT_NOW),
    ]
    for path in results:
        assert path.exists(), f"Nicht erzeugt: {path}"
        assert _is_valid_pdf(path), f"Kein valides PDF: {path}"
        assert path.stat().st_size > 1000, f"Zu klein: {path}"


# ---------------------------------------------------------------------------
# Inhaltsprüfung: Pflichtabschnitte und Erläuterungen
# ---------------------------------------------------------------------------


def test_tagesbericht_enthaelt_pflichtabschnitte(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_daily_report(conn, date(2025, 6, 1), export_dir, now=_REPORT_NOW)
    text = _pdf_text(path)
    for abschnitt in _PFLICHT_ABSCHNITTE:
        assert abschnitt in text, f"Abschnitt fehlt im Tagesbericht: {abschnitt}"


def test_wochenbericht_enthaelt_pflichtabschnitte(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_weekly_report(conn, 2025, 23, export_dir, now=_REPORT_NOW)
    text = _pdf_text(path)
    for abschnitt in _PFLICHT_ABSCHNITTE:
        assert abschnitt in text, f"Abschnitt fehlt im Wochenbericht: {abschnitt}"


def test_monatsbericht_enthaelt_pflichtabschnitte(conn: sqlite3.Connection, export_dir: Path) -> None:
    _base_setup(conn)
    path = create_monthly_report(conn, 2025, 6, export_dir, now=_REPORT_NOW)
    text = _pdf_text(path)
    for abschnitt in _PFLICHT_ABSCHNITTE:
        assert abschnitt in text, f"Abschnitt fehlt im Monatsbericht: {abschnitt}"


def test_mitarbeiterbericht_enthaelt_pflichtabschnitte(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _base_setup(conn)
    path = create_employee_report(conn, emp_id, _FROM, _TO, export_dir, now=_REPORT_NOW)
    text = _pdf_text(path)
    for abschnitt in _PFLICHT_ABSCHNITTE:
        assert abschnitt in text, f"Abschnitt fehlt im Mitarbeiterbericht: {abschnitt}"


def test_erlaeuterungen_enthalten_statusbegriffe(conn: sqlite3.Connection, export_dir: Path) -> None:
    """Pflichtenheft v3 §7.11: Berichte müssen Statusterminologie erläutern."""
    _base_setup(conn)
    path = create_daily_report(conn, date(2025, 6, 1), export_dir, now=_REPORT_NOW)
    text = _pdf_text(path)
    for begriff in ["OPEN", "WARN", "NEEDS_REVIEW", "Nachträge", "Korrekturen"]:
        assert begriff in text, f"Erläuterungsbegriff fehlt: {begriff}"


def test_mitarbeiterbericht_ohne_buchungen_robust(conn: sqlite3.Connection, export_dir: Path) -> None:
    """create_employee_report darf nicht fehlschlagen wenn keine Buchungen im Zeitraum."""
    emp_id = _insert_employee(conn, "E001")
    # keine Buchungen im Zeitraum
    path = create_employee_report(conn, emp_id, _FROM, _TO, export_dir, now=_REPORT_NOW)
    assert path.exists()
    assert _is_valid_pdf(path)
    assert "E001" in path.name


def test_mitarbeiterbericht_name_aus_stammdaten(conn: sqlite3.Connection, export_dir: Path) -> None:
    """MA-Name kommt aus employees-Tabelle, nicht aus Buchungen."""
    emp_id = _insert_employee(conn, "E001")
    # keine Buchungen im Zeitraum → Name muss trotzdem korrekt sein
    path = create_employee_report(conn, emp_id, _FROM, _TO, export_dir, now=_REPORT_NOW)
    text = _pdf_text(path)
    assert "Anna Muster" in text


def test_mitarbeiterbericht_ohne_buchungen_mit_korrekturen_nachtraegen_prueffaellen(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    """Pflichtauswertung: Bericht ohne Buchungen im Zeitraum, aber mit Korrekturen,
    Nachträgen und Prüffällen muss sinnvoll erzeugt werden (Pflichtenheft v3 §7.12)."""
    emp_id = _insert_employee(conn, "E001")

    # Buchung außerhalb des Berichtszeitraums — nur für FK-Referenz der Korrektur
    booking_id = _insert_booking(
        conn,
        emp_id,
        status="CORRECTED",
        booked_at=datetime(2025, 5, 1, 8, 0, tzinfo=timezone.utc),
    )
    _insert_correction_for(conn, booking_id)
    _insert_supplement_for(conn, emp_id)
    _insert_review_case_for(conn, emp_id)

    # Bericht für Juni — keine Buchungen in diesem Zeitraum
    path = create_employee_report(conn, emp_id, _FROM, _TO, export_dir, now=_REPORT_NOW)

    assert path.exists()
    assert _is_valid_pdf(path)
    assert "E001" in path.name
    text = _pdf_text(path)
    assert "Anna Muster" in text
    for abschnitt in _PFLICHT_ABSCHNITTE:
        assert abschnitt in text, f"Abschnitt fehlt: {abschnitt}"
