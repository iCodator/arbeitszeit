"""Integrationstests für csv_exporter.py gegen In-Memory-SQLite."""

__version__ = "1.0"

import csv
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.export.csv_exporter import (
    export_condensed,
    export_detail,
    export_review_cases,
)

_NOW = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)
_LATER = datetime(2025, 6, 1, 17, 0, tzinfo=timezone.utc)
_FROM = datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc)
_TO = datetime(2025, 6, 30, 23, 59, tzinfo=timezone.utc)
_EXPORT_NOW = datetime(2025, 6, 1, 18, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fixtures und Helfer
# ---------------------------------------------------------------------------


@pytest.fixture
def export_dir(tmp_path: Path) -> Path:
    return tmp_path / "export"


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
    source: str = "TERMINAL",
) -> int:
    return int(
        conn.execute(
            "INSERT INTO time_bookings (employee_id, booking_type, booked_at, "
            "source, current_status, created_at) "
            "VALUES (?, ?, ?, ?, ?, '2025-01-01T00:00:00+00:00') RETURNING id",
            (employee_id, booking_type, booked_at.isoformat(), source, status),
        ).fetchone()["id"]
    )


def _insert_user(conn: sqlite3.Connection) -> int:
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


def _insert_correction(
    conn: sqlite3.Connection, booking_id: int, corrected_at: datetime = _NOW
) -> int:
    user_id = _insert_user(conn)
    old = json.dumps({"booking_type": "COME", "booked_at": _NOW.isoformat()})
    new = json.dumps({"booking_type": "GO", "booked_at": _LATER.isoformat()})
    return int(
        conn.execute(
            "INSERT INTO booking_corrections "
            "(time_booking_id, old_values_json, new_values_json, reason, "
            "corrected_by_user_id, corrected_at) "
            "VALUES (?, ?, ?, 'Typ falsch', ?, ?) RETURNING id",
            (booking_id, old, new, user_id, corrected_at.isoformat()),
        ).fetchone()["id"]
    )


def _insert_supplement(
    conn: sqlite3.Connection, employee_id: int, event_at: datetime = _NOW
) -> int:
    user_id = _insert_user(conn)
    return int(
        conn.execute(
            "INSERT INTO supplements "
            "(employee_id, booking_type, event_at, recorded_at, reason, "
            "recorded_by_user_id, approval_status) "
            "VALUES (?, 'COME', ?, ?, 'Vergessen', ?, 'PENDING') RETURNING id",
            (employee_id, event_at.isoformat(), _NOW.isoformat(), user_id),
        ).fetchone()["id"]
    )


def _insert_review_case(
    conn: sqlite3.Connection,
    employee_id: int,
    booking_id: int | None = None,
    case_type: str = "POSSIBLE_MAX_HOURS_VIOLATION",
    status: str = "OPEN",
    severity: str = "WARN",
    detected_at: datetime = _NOW,
    note: str | None = None,
) -> int:
    closed_at = _NOW.isoformat() if status in ("RESOLVED", "CLOSED_WITH_NOTE") else None
    closed_by: int | None = None
    if closed_at is not None:
        closed_by = _insert_user(conn)
    return int(
        conn.execute(
            "INSERT INTO review_cases "
            "(employee_id, time_booking_id, case_type, status, severity, "
            "description, detected_at, closed_at, closed_by_user_id, note) "
            "VALUES (?, ?, ?, ?, ?, 'Test', ?, ?, ?, ?) RETURNING id",
            (
                employee_id,
                booking_id,
                case_type,
                status,
                severity,
                detected_at.isoformat(),
                closed_at,
                closed_by,
                note,
            ),
        ).fetchone()["id"]
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Dateinamen
# ---------------------------------------------------------------------------


def test_export_detail_dateiname_korrekt(conn: sqlite3.Connection, export_dir: Path) -> None:
    _insert_booking(conn, _insert_employee(conn))
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)
    assert path.name == "export_detail_20250601_20250630_20250601T180000Z.csv"


def test_export_verdichtet_dateiname_korrekt(conn: sqlite3.Connection, export_dir: Path) -> None:
    _insert_booking(conn, _insert_employee(conn))
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)
    assert path.name == "export_verdichtet_20250601_20250630_20250601T180000Z.csv"


def test_export_dir_wird_angelegt(conn: sqlite3.Connection, export_dir: Path) -> None:
    subdir = export_dir / "sub"
    _insert_booking(conn, _insert_employee(conn))
    export_detail(conn, _FROM, _TO, subdir, now=_EXPORT_NOW)
    assert subdir.exists()


# ---------------------------------------------------------------------------
# Detail-CSV: Inhalt
# ---------------------------------------------------------------------------


def test_detail_csv_enthaelt_buchungszeile(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW)
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert len(rows) == 1
    r = rows[0]
    assert r["mitarbeiter_nr"] == "E001"
    assert r["mitarbeiter_name"] == "Anna Muster"
    assert r["buchungsart"] == "COME"
    assert r["status"] == "OPEN"
    assert r["datum"] == "2025-06-01"
    assert r["uhrzeit"] == "08:00"
    assert r["quelle"] == "TERMINAL"
    assert r["ist_nachtrag"] == "nein"
    assert r["ist_korrigiert"] == "nein"


def test_detail_csv_nachtrag_gekennzeichnet(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW, source="MANUAL", status="OK")
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["ist_nachtrag"] == "ja"
    assert rows[0]["quelle"] == "MANUAL"


def test_detail_csv_korrigierte_buchung_gekennzeichnet(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW, status="CORRECTED")
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["ist_korrigiert"] == "ja"


def test_detail_csv_dauer_fuer_go_berechnet(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="COME", booked_at=_NOW, status="OPEN")
    _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER, status="OK")
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    go_row = next(r for r in rows if r["buchungsart"] == "GO")
    # _LATER - _NOW = 9h = 540 Minuten
    assert go_row["dauer_minuten"] == "540"


def test_detail_csv_come_ohne_dauer(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW)
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["dauer_minuten"] == ""


def test_detail_csv_filtert_nach_employee_id(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_booking(conn, emp1)
    _insert_booking(conn, emp2)
    path = export_detail(conn, _FROM, _TO, export_dir, employee_id=emp1, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert len(rows) == 1
    assert rows[0]["mitarbeiter_nr"] == "E001"


def test_detail_csv_leere_datei_wenn_keine_buchungen(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)
    rows = _read_csv(path)
    assert rows == []


def test_detail_csv_break_end_dauer_berechnet(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    """BREAK_END-Dauer aus BREAK_START berechnet; deckt _last_before BREAK_START-Pfad ab."""
    emp_id = _insert_employee(conn)
    t_break_start = datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc)
    t_break_end = datetime(2025, 6, 1, 12, 30, tzinfo=timezone.utc)
    _insert_booking(conn, emp_id, booking_type="COME", booked_at=_NOW, status="OPEN")
    _insert_booking(
        conn, emp_id, booking_type="BREAK_START", booked_at=t_break_start, status="OPEN"
    )
    _insert_booking(conn, emp_id, booking_type="BREAK_END", booked_at=t_break_end, status="OK")
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    break_end_row = next(r for r in rows if r["buchungsart"] == "BREAK_END")
    assert break_end_row["dauer_minuten"] == "30"


def test_detail_csv_break_end_ohne_break_start_keine_dauer(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    """BREAK_END ohne vorangehenden BREAK_START → opener=None → dauer_minuten leer."""
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="BREAK_END", booked_at=_NOW, status="OPEN")
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["dauer_minuten"] == ""


def test_export_detail_ohne_now_parameter(conn: sqlite3.Connection, export_dir: Path) -> None:
    """now=None → datetime.now() wird intern gesetzt; Datei wird erzeugt."""
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id)
    path = export_detail(conn, _FROM, _TO, export_dir)
    assert path.exists()


# ---------------------------------------------------------------------------
# Verdichteter CSV: Inhalt
# ---------------------------------------------------------------------------


def test_verdichtet_csv_eine_zeile_pro_tag(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="COME", booked_at=_NOW)
    _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER, status="OK")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert len(rows) == 1
    r = rows[0]
    assert r["mitarbeiter_nr"] == "E001"
    assert r["datum"] == "2025-06-01"
    assert r["anzahl_buchungen"] == "2"
    # 9h Nettoarbeitszeit = 540 Minuten (keine Pausen → identisch mit Bruttozeit)
    assert r["nettoarbeitszeit_minuten"] == "540"


def test_verdichtet_csv_pausenzeit_und_nettoarbeitszeit_korrekt(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    # COME 08:00 → BREAK_START 12:00 → BREAK_END 12:30 → GO 17:00
    # Nettoarbeitszeit: (12:00-08:00) + (17:00-12:30) = 240 + 270 = 510 min
    # Nettopausenzeit: 12:30-12:00 = 30 min
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="COME", booked_at=_NOW)
    _insert_booking(
        conn,
        emp_id,
        booking_type="BREAK_START",
        booked_at=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
        status="OPEN",
    )
    _insert_booking(
        conn,
        emp_id,
        booking_type="BREAK_END",
        booked_at=datetime(2025, 6, 1, 12, 30, tzinfo=timezone.utc),
        status="OK",
    )
    _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER, status="OK")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["nettopausenzeit_minuten"] == "30"
    assert rows[0]["nettoarbeitszeit_minuten"] == "510"
    assert rows[0]["pausenanzahl"] == "1"


def test_verdichtet_csv_korrekturen_und_nachtraege(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp_id = _insert_employee(conn)
    b_id = _insert_booking(conn, emp_id, status="CORRECTED")
    _insert_correction(conn, b_id, corrected_at=_NOW)
    _insert_supplement(conn, emp_id, event_at=_NOW)
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["korrekturen"] == "1"
    assert rows[0]["nachtraege"] == "1"


def test_verdichtet_csv_zwei_mitarbeiter_zwei_zeilen(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_booking(conn, emp1)
    _insert_booking(conn, emp2)
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert len(rows) == 2
    personnel_nos = {r["mitarbeiter_nr"] for r in rows}
    assert personnel_nos == {"E001", "E002"}


def test_verdichtet_csv_offene_buchungen_gezaehlt(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, status="OPEN")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["offene_buchungen"] == "1"


def test_verdichtet_csv_warn_buchungen_gezaehlt(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER, status="WARN")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["warn_buchungen"] == "1"


def test_verdichtet_csv_needs_review_buchungen_gezaehlt(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER, status="NEEDS_REVIEW")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["pruefpflicht_buchungen"] == "1"


def test_verdichtet_csv_break_start_ohne_come_nullzeit(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    """BREAK_START als erste Buchung → work_phase_start=None → Arbeitszeit bleibt 0."""
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="BREAK_START", booked_at=_NOW, status="OPEN")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["nettoarbeitszeit_minuten"] == "0"


def test_verdichtet_csv_break_end_ohne_break_start_nullpause(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    """BREAK_END ohne vorangehenden BREAK_START → break_phase_start=None → Pausenzeit 0."""
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="BREAK_END", booked_at=_NOW, status="OK")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["nettopausenzeit_minuten"] == "0"


def test_verdichtet_csv_go_ohne_come_nullzeit(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    """GO ohne vorangehenden COME → work_phase_start=None → Arbeitszeit bleibt 0."""
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER, status="OK")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["nettoarbeitszeit_minuten"] == "0"


def test_export_condensed_ohne_now_parameter(conn: sqlite3.Connection, export_dir: Path) -> None:
    """now=None → datetime.now() wird intern gesetzt; Datei wird erzeugt."""
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id)
    path = export_condensed(conn, _FROM, _TO, export_dir)
    assert path.exists()


# ---------------------------------------------------------------------------
# Prüffälle-Export
# ---------------------------------------------------------------------------


def test_export_review_cases_dateiname_korrekt(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp_id = _insert_employee(conn)
    _insert_review_case(conn, emp_id)
    path = export_review_cases(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)
    assert path.name == "export_prueffaelle_20250601_20250630_20250601T180000Z.csv"


def test_export_review_cases_enthaelt_prueffall(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp_id = _insert_employee(conn)
    booking_id = _insert_booking(conn, emp_id)
    _insert_review_case(conn, emp_id, booking_id=booking_id, severity="CRITICAL")
    path = export_review_cases(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert len(rows) == 1
    r = rows[0]
    assert r["mitarbeiter_nr"] == "E001"
    assert r["typ"] == "POSSIBLE_MAX_HOURS_VIOLATION"
    assert r["schwere"] == "CRITICAL"
    assert r["status"] == "OPEN"
    assert r["buchungs_id"] == str(booking_id)


def test_export_review_cases_leere_datei_wenn_keine_faelle(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    path = export_review_cases(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)
    rows = _read_csv(path)
    assert rows == []


def test_export_review_cases_booking_id_leer_wenn_kein_bezug(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    """Prüffall ohne Buchungsbezug → buchungs_id-Spalte leer."""
    emp_id = _insert_employee(conn)
    _insert_review_case(conn, emp_id, booking_id=None)
    path = export_review_cases(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["buchungs_id"] == ""


def test_export_review_cases_mit_note(conn: sqlite3.Connection, export_dir: Path) -> None:
    emp_id = _insert_employee(conn)
    _insert_review_case(conn, emp_id, note="Zur Kenntnis genommen")
    path = export_review_cases(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["hinweis"] == "Zur Kenntnis genommen"


def test_export_review_cases_filtert_nach_employee_id(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_review_case(conn, emp1)
    _insert_review_case(conn, emp2)
    path = export_review_cases(conn, _FROM, _TO, export_dir, employee_id=emp1, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert len(rows) == 1
    assert rows[0]["mitarbeiter_nr"] == "E001"


def test_export_review_cases_ohne_now_parameter(
    conn: sqlite3.Connection, export_dir: Path
) -> None:
    """now=None → datetime.now() wird intern gesetzt; Datei wird erzeugt."""
    emp_id = _insert_employee(conn)
    _insert_review_case(conn, emp_id)
    path = export_review_cases(conn, _FROM, _TO, export_dir)
    assert path.exists()
