"""Integrationstests für report_queries.py gegen In-Memory-SQLite."""

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

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
from arbeitszeit.infrastructure.export.report_queries import (
    list_bookings,
    list_corrections,
    list_open_bookings,
    list_open_review_cases,
    list_open_review_cases_in_period,
    list_review_cases_for_booking,
    list_supplements,
    list_warn_bookings,
)

_NOW = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)
_LATER = datetime(2025, 6, 1, 17, 0, tzinfo=timezone.utc)
_TOMORROW = datetime(2025, 6, 2, 8, 0, tzinfo=timezone.utc)
_FROM = datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc)
_TO = datetime(2025, 6, 30, 23, 59, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------


def _insert_employee(conn: sqlite3.Connection, personnel_no: str = "E001") -> int:
    row = conn.execute(
        "INSERT INTO employees (personnel_no, first_name, last_name, active, "
        "created_at, updated_at) VALUES (?, 'Anna', 'Muster', 1, "
        "'2025-01-01', '2025-01-01') RETURNING id",
        (personnel_no,),
    ).fetchone()
    return int(row["id"])


def _insert_booking(
    conn: sqlite3.Connection,
    employee_id: int,
    booking_type: str = "COME",
    booked_at: datetime = _NOW,
    status: str = "OPEN",
    source: str = "TERMINAL",
) -> int:
    row = conn.execute(
        "INSERT INTO time_bookings (employee_id, booking_type, booked_at, "
        "source, current_status, created_at) "
        "VALUES (?, ?, ?, ?, ?, '2025-01-01T00:00:00+00:00') RETURNING id",
        (employee_id, booking_type, booked_at.isoformat(), source, status),
    ).fetchone()
    return int(row["id"])


def _insert_correction(
    conn: sqlite3.Connection, booking_id: int, user_id: int, corrected_at: datetime = _NOW
) -> int:
    old = json.dumps({"booking_type": "COME", "booked_at": _NOW.isoformat()})
    new = json.dumps({"booking_type": "GO", "booked_at": _LATER.isoformat()})
    row = conn.execute(
        "INSERT INTO booking_corrections "
        "(time_booking_id, old_values_json, new_values_json, reason, "
        "corrected_by_user_id, corrected_at) "
        "VALUES (?, ?, ?, 'Typ falsch', ?, ?) RETURNING id",
        (booking_id, old, new, user_id, corrected_at.isoformat()),
    ).fetchone()
    return int(row["id"])


def _insert_supplement(
    conn: sqlite3.Connection, employee_id: int, event_at: datetime = _NOW
) -> int:
    user_id = _ensure_user(conn)
    row = conn.execute(
        "INSERT INTO supplements "
        "(employee_id, booking_type, event_at, recorded_at, reason, "
        "recorded_by_user_id, approval_status) "
        "VALUES (?, 'COME', ?, ?, 'Vergessen', ?, 'PENDING') RETURNING id",
        (employee_id, event_at.isoformat(), _NOW.isoformat(), user_id),
    ).fetchone()
    return int(row["id"])


def _ensure_user(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id FROM user_accounts LIMIT 1").fetchone()
    if row:
        return int(row["id"])
    return _insert_user(conn)


def _insert_review_case(
    conn: sqlite3.Connection,
    employee_id: int,
    booking_id: int | None = None,
    case_type: str = "POSSIBLE_MAX_HOURS_VIOLATION",
    status: str = "OPEN",
    severity: str = "WARN",
    detected_at: datetime = _NOW,
) -> int:
    closed_at = _NOW.isoformat() if status in ("RESOLVED", "CLOSED_WITH_NOTE") else None
    closed_by = 1 if status in ("RESOLVED", "CLOSED_WITH_NOTE") else None
    if closed_by is not None:
        closed_by = _ensure_user(conn)
    row = conn.execute(
        "INSERT INTO review_cases "
        "(employee_id, time_booking_id, case_type, status, severity, "
        "description, detected_at, closed_at, closed_by_user_id) "
        "VALUES (?, ?, ?, ?, ?, 'Test', ?, ?, ?) RETURNING id",
        (
            employee_id,
            booking_id,
            case_type,
            status,
            severity,
            detected_at.isoformat(),
            closed_at,
            closed_by,
        ),
    ).fetchone()
    return int(row["id"])


def _insert_user(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "INSERT INTO user_accounts (username, password_hash, role, active, "
        "created_at, updated_at) "
        "VALUES ('admin', 'hash', 'ADMIN', 1, '2025-01-01', '2025-01-01') "
        "RETURNING id",
    ).fetchone()
    return int(row["id"])


# ---------------------------------------------------------------------------
# list_bookings
# ---------------------------------------------------------------------------


def test_list_bookings_liefert_buchung_im_zeitraum(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW)

    result = list_bookings(conn, _FROM, _TO)

    assert len(result) == 1
    b = result[0]
    assert isinstance(b, BookingRow)
    assert b.booking_type == BookingType.COME
    assert b.personnel_no == "E001"
    assert b.employee_name == "Anna Muster"
    assert b.status == BookingStatus.OPEN
    assert not b.is_manual


def test_list_bookings_filtert_nach_employee_id(conn: sqlite3.Connection) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_booking(conn, emp1, booked_at=_NOW)
    _insert_booking(conn, emp2, booked_at=_NOW)

    result = list_bookings(conn, _FROM, _TO, employee_id=emp1)

    assert len(result) == 1
    assert result[0].employee_id == emp1


def test_list_bookings_exkludiert_buchungen_ausserhalb_zeitraum(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=datetime(2025, 7, 1, 8, 0, tzinfo=timezone.utc))

    result = list_bookings(conn, _FROM, _TO)

    assert result == []


def test_list_bookings_kennzeichnet_manual_buchung(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_NOW, source="MANUAL")

    result = list_bookings(conn, _FROM, _TO)

    assert result[0].is_manual is True
    assert result[0].source == BookingSource.MANUAL


def test_list_bookings_sortiert_nach_booked_at(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booked_at=_LATER)
    _insert_booking(conn, emp_id, booked_at=_NOW)

    result = list_bookings(conn, _FROM, _TO)

    assert result[0].booked_at < result[1].booked_at


# ---------------------------------------------------------------------------
# list_open_bookings
# ---------------------------------------------------------------------------


def test_list_open_bookings_liefert_nur_offene(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, status="OPEN")
    _insert_booking(conn, emp_id, booking_type="GO", status="OK", booked_at=_LATER)

    result = list_open_bookings(conn)

    assert len(result) == 1
    assert result[0].status == BookingStatus.OPEN


def test_list_open_bookings_filtert_nach_employee_id(conn: sqlite3.Connection) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_booking(conn, emp1, status="OPEN")
    _insert_booking(conn, emp2, status="OPEN")

    result = list_open_bookings(conn, employee_id=emp1)

    assert len(result) == 1
    assert result[0].employee_id == emp1


# ---------------------------------------------------------------------------
# list_warn_bookings
# ---------------------------------------------------------------------------


def test_list_warn_bookings_liefert_warn_und_needs_review(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    _insert_booking(conn, emp_id, booking_type="GO", status="WARN", booked_at=_LATER)
    _insert_booking(conn, emp_id, booking_type="COME", status="OPEN", booked_at=_NOW)

    result = list_warn_bookings(conn, _FROM, _TO)

    assert len(result) == 1
    assert result[0].status == BookingStatus.WARN


# ---------------------------------------------------------------------------
# list_corrections
# ---------------------------------------------------------------------------


def test_list_corrections_liefert_korrektur_mit_altem_und_neuem_zustand(
    conn: sqlite3.Connection,
) -> None:
    emp_id = _insert_employee(conn)
    user_id = _insert_user(conn)
    booking_id = _insert_booking(conn, emp_id, status="CORRECTED")
    _insert_correction(conn, booking_id, user_id, corrected_at=_NOW)

    result = list_corrections(conn, _FROM, _TO)

    assert len(result) == 1
    c = result[0]
    assert isinstance(c, CorrectionRow)
    assert c.booking_id == booking_id
    assert c.old_booking_type == BookingType.COME
    assert c.new_booking_type == BookingType.GO
    assert c.reason == "Typ falsch"
    assert c.personnel_no == "E001"


def test_list_corrections_filtert_nach_employee_id(conn: sqlite3.Connection) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    user_id = _insert_user(conn)
    b1 = _insert_booking(conn, emp1, status="CORRECTED")
    b2 = _insert_booking(conn, emp2, status="CORRECTED")
    _insert_correction(conn, b1, user_id)
    _insert_correction(conn, b2, user_id)

    result = list_corrections(conn, _FROM, _TO, employee_id=emp1)

    assert len(result) == 1
    assert result[0].employee_id == emp1


# ---------------------------------------------------------------------------
# list_supplements — Nachtragskennzeichnung
# ---------------------------------------------------------------------------


def test_list_supplements_liefert_nachtrag(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    _insert_supplement(conn, emp_id, event_at=_NOW)

    result = list_supplements(conn, _FROM, _TO)

    assert len(result) == 1
    s = result[0]
    assert isinstance(s, SupplementRow)
    assert s.approval_status == ApprovalStatus.PENDING
    assert s.booking_type == BookingType.COME
    assert s.personnel_no == "E001"
    assert s.related_booking_id is None


def test_list_supplements_filtert_nach_zeitraum(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    _insert_supplement(conn, emp_id, event_at=datetime(2025, 7, 1, 8, 0, tzinfo=timezone.utc))

    result = list_supplements(conn, _FROM, _TO)

    assert result == []


def test_list_supplements_filtert_nach_employee_id(conn: sqlite3.Connection) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_supplement(conn, emp1)
    _insert_supplement(conn, emp2)

    result = list_supplements(conn, _FROM, _TO, employee_id=emp1)

    assert len(result) == 1
    assert result[0].employee_id == emp1


# ---------------------------------------------------------------------------
# list_open_review_cases
# ---------------------------------------------------------------------------


def test_list_open_review_cases_liefert_offene_faelle(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    booking_id = _insert_booking(conn, emp_id)
    _insert_review_case(conn, emp_id, booking_id, status="OPEN")

    result = list_open_review_cases(conn)

    assert len(result) == 1
    rc = result[0]
    assert isinstance(rc, ReviewCaseRow)
    assert rc.status == ReviewCaseStatus.OPEN
    assert rc.booking_id == booking_id
    assert rc.case_type == ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION
    assert rc.severity == ReviewSeverity.WARN


def test_list_open_review_cases_exkludiert_geschlossene(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    booking_id = _insert_booking(conn, emp_id)
    _insert_review_case(conn, emp_id, booking_id, status="RESOLVED")

    result = list_open_review_cases(conn)

    assert result == []


def test_list_open_review_cases_filtert_nach_employee_id(conn: sqlite3.Connection) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    b1 = _insert_booking(conn, emp1)
    b2 = _insert_booking(conn, emp2)
    _insert_review_case(conn, emp1, b1)
    _insert_review_case(conn, emp2, b2)

    result = list_open_review_cases(conn, employee_id=emp1)

    assert len(result) == 1
    assert result[0].employee_id == emp1


# ---------------------------------------------------------------------------
# list_open_review_cases_in_period
# ---------------------------------------------------------------------------


def test_list_open_review_cases_in_period_liefert_faelle_im_zeitraum(
    conn: sqlite3.Connection,
) -> None:
    emp_id = _insert_employee(conn)
    _insert_review_case(conn, emp_id, detected_at=_NOW)

    result = list_open_review_cases_in_period(conn, _FROM, _TO)

    assert len(result) == 1
    assert result[0].employee_id == emp_id


def test_list_open_review_cases_in_period_exkludiert_faelle_ausserhalb(
    conn: sqlite3.Connection,
) -> None:
    emp_id = _insert_employee(conn)
    outside = datetime(2025, 7, 1, 8, 0, tzinfo=timezone.utc)
    _insert_review_case(conn, emp_id, detected_at=outside)

    result = list_open_review_cases_in_period(conn, _FROM, _TO)

    assert result == []


def test_list_open_review_cases_in_period_filtert_nach_employee_id(
    conn: sqlite3.Connection,
) -> None:
    emp1 = _insert_employee(conn, "E001")
    emp2 = _insert_employee(conn, "E002")
    _insert_review_case(conn, emp1, detected_at=_NOW)
    _insert_review_case(conn, emp2, detected_at=_NOW)

    result = list_open_review_cases_in_period(conn, _FROM, _TO, employee_id=emp1)

    assert len(result) == 1
    assert result[0].employee_id == emp1


# ---------------------------------------------------------------------------
# list_review_cases_for_booking
# ---------------------------------------------------------------------------


def test_list_review_cases_for_booking_liefert_alle_typen(conn: sqlite3.Connection) -> None:
    emp_id = _insert_employee(conn)
    booking_id = _insert_booking(conn, emp_id)
    other_booking_id = _insert_booking(conn, emp_id, booking_type="GO", booked_at=_LATER)
    _insert_review_case(conn, emp_id, booking_id, status="OPEN")
    _insert_review_case(
        conn, emp_id, booking_id, status="RESOLVED", case_type="OUTSIDE_SCHEDULE_WINDOW"
    )
    _insert_review_case(conn, emp_id, other_booking_id)  # anderer Buchungsbezug

    result = list_review_cases_for_booking(conn, booking_id)

    assert len(result) == 2
    assert all(rc.booking_id == booking_id for rc in result)


# ---------------------------------------------------------------------------
# Pflichtfall V3 §16: Auswertung offener und auffälliger Fälle
# ---------------------------------------------------------------------------


def test_pflichtfall_offene_und_auffaellige_faelle(conn: sqlite3.Connection) -> None:
    """V3 §16 Testpflicht: Systemweit kombinierte Abfrage aller kritischen Zustände."""
    emp_id = _insert_employee(conn)

    open_booking_id = _insert_booking(conn, emp_id, status="OPEN", booked_at=_NOW)
    warn_booking_id = _insert_booking(
        conn, emp_id, booking_type="GO", status="WARN", booked_at=_LATER
    )
    _insert_review_case(
        conn,
        emp_id,
        warn_booking_id,
        case_type="POSSIBLE_MAX_HOURS_VIOLATION",
        severity="WARN",
    )
    _insert_supplement(conn, emp_id, event_at=_NOW)

    open_bookings = list_open_bookings(conn)
    warn_bookings = list_warn_bookings(conn, _FROM, _TO)
    open_cases = list_open_review_cases(conn)
    supplements = list_supplements(conn, _FROM, _TO)

    assert len(open_bookings) == 1
    assert open_bookings[0].booking_id == open_booking_id

    assert len(warn_bookings) == 1
    assert warn_bookings[0].booking_id == warn_booking_id

    assert len(open_cases) == 1
    assert open_cases[0].case_type == ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION

    assert len(supplements) == 1
    assert supplements[0].approval_status == ApprovalStatus.PENDING
