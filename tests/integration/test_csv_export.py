"""Integrationstests für csv_exporter.py gegen In-Memory-SQLite."""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.export.csv_exporter import (
    export_condensed,
    export_detail,
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
def export_dir(tmp_path):
    return tmp_path / "export"


def _insert_employee(conn, personnel_no: str = "E001") -> int:
    return conn.execute(
        "INSERT INTO employees (personnel_no, first_name, last_name, active, "
        "created_at, updated_at) VALUES (?, 'Anna', 'Muster', 1, "
        "'2025-01-01', '2025-01-01') RETURNING id",
        (personnel_no,),
    ).fetchone()["id"]


def _insert_booking(conn, employee_id, booking_type="COME", booked_at=_NOW,
                    status="OPEN", source="TERMINAL") -> int:
    return conn.execute(
        "INSERT INTO time_bookings (employee_id, booking_type, booked_at, "
        "source, current_status, created_at) "
        "VALUES (?, ?, ?, ?, ?, '2025-01-01T00:00:00+00:00') RETURNING id",
        (employee_id, booking_type, booked_at.isoformat(), source, status),
    ).fetchone()["id"]


def _insert_user(conn) -> int:
    row = conn.execute("SELECT id FROM user_accounts LIMIT 1").fetchone()
    if row:
        return row["id"]
    return conn.execute(
        "INSERT INTO user_accounts (username, password_hash, role, active, "
        "created_at, updated_at) VALUES ('admin', 'x', 'ADMIN', 1, "
        "'2025-01-01', '2025-01-01') RETURNING id"
    ).fetchone()["id"]


def _insert_correction(conn, booking_id, corrected_at=_NOW) -> int:
    user_id = _insert_user(conn)
    old = json.dumps({"booking_type": "COME", "booked_at": _NOW.isoformat()})
    new = json.dumps({"booking_type": "GO", "booked_at": _LATER.isoformat()})
    return conn.execute(
        "INSERT INTO booking_corrections "
        "(time_booking_id, old_values_json, new_values_json, reason, "
        "corrected_by_user_id, corrected_at) "
        "VALUES (?, ?, ?, 'Typ falsch', ?, ?) RETURNING id",
        (booking_id, old, new, user_id, corrected_at.isoformat()),
    ).fetchone()["id"]


def _insert_supplement(conn, employee_id, event_at=_NOW) -> int:
    user_id = _insert_user(conn)
    return conn.execute(
        "INSERT INTO supplements "
        "(employee_id, booking_type, event_at, recorded_at, reason, "
        "recorded_by_user_id, approval_status) "
        "VALUES (?, 'COME', ?, ?, 'Vergessen', ?, 'PENDING') RETURNING id",
        (employee_id, event_at.isoformat(), _NOW.isoformat(), user_id),
    ).fetchone()["id"]


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Dateinamen
# ---------------------------------------------------------------------------

def test_export_detail_dateiname_korrekt(conn, export_dir):
    _insert_booking(conn, _insert_employee(conn))
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)
    assert path.name == "export_detail_20250601_20250630_20250601T180000Z.csv"


def test_export_verdichtet_dateiname_korrekt(conn, export_dir):
    _insert_booking(conn, _insert_employee(conn))
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)
    assert path.name == "export_verdichtet_20250601_20250630_20250601T180000Z.csv"


def test_export_dir_wird_angelegt(conn, export_dir):
    subdir = export_dir / "sub"
    _insert_booking(conn, _insert_employee(conn))
    export_detail(conn, _FROM, _TO, subdir, now=_EXPORT_NOW)
    assert subdir.exists()


# ---------------------------------------------------------------------------
# Detail-CSV: Inhalt
# ---------------------------------------------------------------------------

def test_detail_csv_enthaelt_buchungszeile(conn, export_dir):
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


def test_detail_csv_nachtrag_gekennzeichnet(conn, export_dir):
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW, source="MANUAL", status="OK")
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["ist_nachtrag"] == "ja"
    assert rows[0]["quelle"] == "MANUAL"


def test_detail_csv_korrigierte_buchung_gekennzeichnet(conn, export_dir):
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW, status="CORRECTED")
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["ist_korrigiert"] == "ja"


def test_detail_csv_dauer_fuer_go_berechnet(conn, export_dir):
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="COME", booked_at=_NOW, status="OPEN")
    _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER, status="OK")
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    go_row = next(r for r in rows if r["buchungsart"] == "GO")
    # _LATER - _NOW = 9h = 540 Minuten
    assert go_row["dauer_minuten"] == "540"


def test_detail_csv_come_ohne_dauer(conn, export_dir):
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW)
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["dauer_minuten"] == ""


def test_detail_csv_filtert_nach_employee_id(conn, export_dir):
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_booking(conn, emp1)
    _insert_booking(conn, emp2)
    path = export_detail(conn, _FROM, _TO, export_dir, employee_id=emp1, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert len(rows) == 1
    assert rows[0]["mitarbeiter_nr"] == "E001"


def test_detail_csv_leere_datei_wenn_keine_buchungen(conn, export_dir):
    path = export_detail(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)
    rows = _read_csv(path)
    assert rows == []


# ---------------------------------------------------------------------------
# Verdichteter CSV: Inhalt
# ---------------------------------------------------------------------------

def test_verdichtet_csv_eine_zeile_pro_tag(conn, export_dir):
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


def test_verdichtet_csv_pausenzeit_und_nettoarbeitszeit_korrekt(conn, export_dir):
    # COME 08:00 → BREAK_START 12:00 → BREAK_END 12:30 → GO 17:00
    # Nettoarbeitszeit: (12:00-08:00) + (17:00-12:30) = 240 + 270 = 510 min
    # Nettopausenzeit: 12:30-12:00 = 30 min
    # Die Pause muss aus der Arbeitszeit herausgerechnet werden — nicht addiert.
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="COME", booked_at=_NOW)
    _insert_booking(
        conn, emp_id, booking_type="BREAK_START",
        booked_at=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc), status="OPEN"
    )
    _insert_booking(
        conn, emp_id, booking_type="BREAK_END",
        booked_at=datetime(2025, 6, 1, 12, 30, tzinfo=timezone.utc), status="OK"
    )
    _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER, status="OK")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["nettopausenzeit_minuten"] == "30"
    assert rows[0]["nettoarbeitszeit_minuten"] == "510"


def test_verdichtet_csv_korrekturen_und_nachtraege(conn, export_dir):
    emp_id = _insert_employee(conn)
    b_id = _insert_booking(conn, emp_id, status="CORRECTED")
    _insert_correction(conn, b_id, corrected_at=_NOW)
    _insert_supplement(conn, emp_id, event_at=_NOW)
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["korrekturen"] == "1"
    assert rows[0]["nachtraege"] == "1"


def test_verdichtet_csv_zwei_mitarbeiter_zwei_zeilen(conn, export_dir):
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_booking(conn, emp1)
    _insert_booking(conn, emp2)
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert len(rows) == 2
    personnel_nos = {r["mitarbeiter_nr"] for r in rows}
    assert personnel_nos == {"E001", "E002"}


def test_verdichtet_csv_offene_buchungen_gezaehlt(conn, export_dir):
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, status="OPEN")
    path = export_condensed(conn, _FROM, _TO, export_dir, now=_EXPORT_NOW)

    rows = _read_csv(path)
    assert rows[0]["offene_buchungen"] == "1"
