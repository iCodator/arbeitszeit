"""Gemeinsame Abfrage- und Projektionsschicht für alle Exportkanäle.

Alle Ausgabekanäle (CSV, PDF, UI-Pflichtauswertungen) nutzen ausschließlich
diese Funktionen als Datenquelle. Direkte Ad-hoc-Queries außerhalb dieses
Moduls sind architektonisch verboten (Regelwerk v3 §11).

DB-Spalten-Mapping (Schema ↔ Entity):
  time_bookings.current_status  → BookingStatus
  review_cases.time_booking_id  → booking_id
  review_cases.detected_at      → created_at
  booking_corrections.time_booking_id   → original_booking_id
  booking_corrections.old_values_json   → old_booking_type, old_booked_at (JSON)
  booking_corrections.new_values_json   → new_booking_type, new_booked_at (JSON)
  booking_corrections.corrected_at      → created_at
  supplements.related_time_booking_id   → related_booking_id
  employees.active                      → is_active (INTEGER 0/1)
"""
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime

from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.infrastructure.db.repositories._helpers import _parse_dt


# ---------------------------------------------------------------------------
# Normierte Datenstrukturen
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BookingRow:
    """Einzelne Buchung mit Mitarbeiterzuordnung für Berichte."""
    booking_id: int
    employee_id: int
    personnel_no: str
    employee_name: str          # "Vorname Nachname"
    booking_type: BookingType
    booked_at: datetime
    source: BookingSource
    status: BookingStatus
    is_manual: bool             # source == MANUAL


@dataclass(frozen=True)
class CorrectionRow:
    """Korrektur mit altem und neuem Zustand (Regelwerk v3 §12)."""
    correction_id: int
    booking_id: int
    employee_id: int
    personnel_no: str
    employee_name: str
    old_booking_type: BookingType
    old_booked_at: datetime
    new_booking_type: BookingType
    new_booked_at: datetime
    reason: str
    corrected_by_user_id: int
    corrected_at: datetime


@dataclass(frozen=True)
class SupplementRow:
    """Nachtrag als nachträglich erfasster Datensatz (Regelwerk v3 §13/§19)."""
    supplement_id: int
    employee_id: int
    personnel_no: str
    employee_name: str
    booking_type: BookingType
    event_at: datetime
    recorded_at: datetime
    reason: str
    approval_status: ApprovalStatus
    related_booking_id: int | None
    approved_by_user_id: int | None
    approved_at: datetime | None


@dataclass(frozen=True)
class ReviewCaseRow:
    """Offener oder aktiver Prüffall (Pflichtenheft v3 §7.6/§7.12)."""
    case_id: int
    employee_id: int
    personnel_no: str
    employee_name: str
    case_type: ReviewCaseType
    severity: ReviewSeverity
    status: ReviewCaseStatus
    booking_id: int | None
    description: str
    detected_at: datetime
    note: str | None


# ---------------------------------------------------------------------------
# Interne Row-Parser
# ---------------------------------------------------------------------------

def _parse_booking_row(row: sqlite3.Row) -> BookingRow:
    source = BookingSource(row["source"])
    return BookingRow(
        booking_id=row["booking_id"],
        employee_id=row["employee_id"],
        personnel_no=row["personnel_no"],
        employee_name=f"{row['first_name']} {row['last_name']}",
        booking_type=BookingType(row["booking_type"]),
        booked_at=_parse_dt(row["booked_at"]),
        source=source,
        status=BookingStatus(row["current_status"]),
        is_manual=(source == BookingSource.MANUAL),
    )


def _parse_correction_row(row: sqlite3.Row) -> CorrectionRow:
    old = json.loads(row["old_values_json"])
    new = json.loads(row["new_values_json"])
    return CorrectionRow(
        correction_id=row["correction_id"],
        booking_id=row["time_booking_id"],
        employee_id=row["employee_id"],
        personnel_no=row["personnel_no"],
        employee_name=f"{row['first_name']} {row['last_name']}",
        old_booking_type=BookingType(old["booking_type"]),
        old_booked_at=_parse_dt(old["booked_at"]),
        new_booking_type=BookingType(new["booking_type"]),
        new_booked_at=_parse_dt(new["booked_at"]),
        reason=row["reason"],
        corrected_by_user_id=row["corrected_by_user_id"],
        corrected_at=_parse_dt(row["corrected_at"]),
    )


def _parse_supplement_row(row: sqlite3.Row) -> SupplementRow:
    return SupplementRow(
        supplement_id=row["supplement_id"],
        employee_id=row["employee_id"],
        personnel_no=row["personnel_no"],
        employee_name=f"{row['first_name']} {row['last_name']}",
        booking_type=BookingType(row["booking_type"]),
        event_at=_parse_dt(row["event_at"]),
        recorded_at=_parse_dt(row["recorded_at"]),
        reason=row["reason"],
        approval_status=ApprovalStatus(row["approval_status"]),
        related_booking_id=row["related_time_booking_id"],
        approved_by_user_id=row["approved_by_user_id"],
        approved_at=_parse_dt(row["approved_at"]) if row["approved_at"] else None,
    )


def _parse_review_case_row(row: sqlite3.Row) -> ReviewCaseRow:
    return ReviewCaseRow(
        case_id=row["case_id"],
        employee_id=row["employee_id"],
        personnel_no=row["personnel_no"],
        employee_name=f"{row['first_name']} {row['last_name']}",
        case_type=ReviewCaseType(row["case_type"]),
        severity=ReviewSeverity(row["severity"]),
        status=ReviewCaseStatus(row["status"]),
        booking_id=row["time_booking_id"],
        description=row["description"],
        detected_at=_parse_dt(row["detected_at"]),
        note=row["note"],
    )


# ---------------------------------------------------------------------------
# Öffentliche Abfragefunktionen
# ---------------------------------------------------------------------------

def list_bookings(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    employee_id: int | None = None,
) -> list[BookingRow]:
    """Alle Buchungen im Zeitraum, optional auf einen Mitarbeiter beschränkt.

    Aufsteigend nach booked_at sortiert.
    """
    sql = (
        "SELECT tb.id AS booking_id, tb.employee_id, e.personnel_no, "
        "e.first_name, e.last_name, tb.booking_type, tb.booked_at, "
        "tb.source, tb.current_status "
        "FROM time_bookings tb "
        "JOIN employees e ON e.id = tb.employee_id "
        "WHERE tb.booked_at >= ? AND tb.booked_at < ?"
    )
    params: list = [from_dt.isoformat(), to_dt.isoformat()]
    if employee_id is not None:
        sql += " AND tb.employee_id = ?"
        params.append(employee_id)
    sql += " ORDER BY tb.booked_at"
    rows = conn.execute(sql, params).fetchall()
    return [_parse_booking_row(r) for r in rows]


def list_open_bookings(
    conn: sqlite3.Connection,
    employee_id: int | None = None,
) -> list[BookingRow]:
    """Buchungen mit Status OPEN — offene Arbeitsphasen und offene Pausen.

    Keine Zeitbereichsbeschränkung: offene Buchungen können beliebig alt sein.
    """
    sql = (
        "SELECT tb.id AS booking_id, tb.employee_id, e.personnel_no, "
        "e.first_name, e.last_name, tb.booking_type, tb.booked_at, "
        "tb.source, tb.current_status "
        "FROM time_bookings tb "
        "JOIN employees e ON e.id = tb.employee_id "
        "WHERE tb.current_status = 'OPEN'"
    )
    params: list = []
    if employee_id is not None:
        sql += " AND tb.employee_id = ?"
        params.append(employee_id)
    sql += " ORDER BY tb.booked_at"
    rows = conn.execute(sql, params).fetchall()
    return [_parse_booking_row(r) for r in rows]


def list_warn_bookings(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    employee_id: int | None = None,
) -> list[BookingRow]:
    """Buchungen mit Status WARN oder NEEDS_REVIEW im Zeitraum."""
    sql = (
        "SELECT tb.id AS booking_id, tb.employee_id, e.personnel_no, "
        "e.first_name, e.last_name, tb.booking_type, tb.booked_at, "
        "tb.source, tb.current_status "
        "FROM time_bookings tb "
        "JOIN employees e ON e.id = tb.employee_id "
        "WHERE tb.current_status IN ('WARN', 'NEEDS_REVIEW') "
        "AND tb.booked_at >= ? AND tb.booked_at < ?"
    )
    params: list = [from_dt.isoformat(), to_dt.isoformat()]
    if employee_id is not None:
        sql += " AND tb.employee_id = ?"
        params.append(employee_id)
    sql += " ORDER BY tb.booked_at"
    rows = conn.execute(sql, params).fetchall()
    return [_parse_booking_row(r) for r in rows]


def list_open_bookings_in_period(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    employee_id: int | None = None,
) -> list[BookingRow]:
    """Buchungen mit Status OPEN und booked_at im Zeitraum [from_dt, to_dt).

    Pflichtenheft v3 §7.12: Pflichtauswertungen müssen nach Zeitraum filterbar sein.
    """
    sql = (
        "SELECT tb.id AS booking_id, tb.employee_id, e.personnel_no, "
        "e.first_name, e.last_name, tb.booking_type, tb.booked_at, "
        "tb.source, tb.current_status "
        "FROM time_bookings tb "
        "JOIN employees e ON e.id = tb.employee_id "
        "WHERE tb.current_status = 'OPEN' "
        "AND tb.booked_at >= ? AND tb.booked_at < ?"
    )
    params: list = [from_dt.isoformat(), to_dt.isoformat()]
    if employee_id is not None:
        sql += " AND tb.employee_id = ?"
        params.append(employee_id)
    sql += " ORDER BY tb.booked_at"
    rows = conn.execute(sql, params).fetchall()
    return [_parse_booking_row(r) for r in rows]


def list_corrections(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    employee_id: int | None = None,
) -> list[CorrectionRow]:
    """Buchungskorrekturen im Zeitraum (nach corrected_at).

    Enthält alten und neuen Zustand, Begründung, korrigierende Person und
    Zeitstempel — entspricht §7.12 und Regelwerk v3 §12.
    """
    sql = (
        "SELECT bc.id AS correction_id, bc.time_booking_id, "
        "bc.old_values_json, bc.new_values_json, bc.reason, "
        "bc.corrected_by_user_id, bc.corrected_at, "
        "tb.employee_id, e.personnel_no, e.first_name, e.last_name "
        "FROM booking_corrections bc "
        "JOIN time_bookings tb ON tb.id = bc.time_booking_id "
        "JOIN employees e ON e.id = tb.employee_id "
        "WHERE bc.corrected_at >= ? AND bc.corrected_at < ?"
    )
    params: list = [from_dt.isoformat(), to_dt.isoformat()]
    if employee_id is not None:
        sql += " AND tb.employee_id = ?"
        params.append(employee_id)
    sql += " ORDER BY bc.corrected_at"
    rows = conn.execute(sql, params).fetchall()
    return [_parse_correction_row(r) for r in rows]


def list_supplements(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    employee_id: int | None = None,
) -> list[SupplementRow]:
    """Nachträge im Zeitraum (nach event_at).

    Kennzeichnung als nachträglich erfasster Datensatz mit Begründung und
    Freigabebezug — Regelwerk v3 §13/§19, Pflichtenheft v3 §7.12.
    """
    sql = (
        "SELECT s.id AS supplement_id, s.employee_id, e.personnel_no, "
        "e.first_name, e.last_name, s.booking_type, s.event_at, "
        "s.recorded_at, s.reason, s.approval_status, "
        "s.related_time_booking_id, s.approved_by_user_id, s.approved_at "
        "FROM supplements s "
        "JOIN employees e ON e.id = s.employee_id "
        "WHERE s.event_at >= ? AND s.event_at < ?"
    )
    params: list = [from_dt.isoformat(), to_dt.isoformat()]
    if employee_id is not None:
        sql += " AND s.employee_id = ?"
        params.append(employee_id)
    sql += " ORDER BY s.event_at"
    rows = conn.execute(sql, params).fetchall()
    return [_parse_supplement_row(r) for r in rows]


def list_open_review_cases(
    conn: sqlite3.Connection,
    employee_id: int | None = None,
) -> list[ReviewCaseRow]:
    """Offene und aktive Prüffälle (Status OPEN oder IN_REVIEW).

    Keine Zeitbereichsbeschränkung: alle ungelösten Prüffälle.
    """
    sql = (
        "SELECT rc.id AS case_id, rc.employee_id, e.personnel_no, "
        "e.first_name, e.last_name, rc.case_type, rc.severity, rc.status, "
        "rc.time_booking_id, rc.description, rc.detected_at, rc.note "
        "FROM review_cases rc "
        "JOIN employees e ON e.id = rc.employee_id "
        "WHERE rc.status IN ('OPEN', 'IN_REVIEW')"
    )
    params: list = []
    if employee_id is not None:
        sql += " AND rc.employee_id = ?"
        params.append(employee_id)
    sql += " ORDER BY rc.detected_at"
    rows = conn.execute(sql, params).fetchall()
    return [_parse_review_case_row(r) for r in rows]


def list_open_review_cases_in_period(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    employee_id: int | None = None,
) -> list[ReviewCaseRow]:
    """Offene und aktive Prüffälle mit detected_at im Zeitraum.

    Pflichtenheft v3 §7.12: Pflichtauswertungen müssen nach Zeitraum
    filterbar sein. Ergänzt list_open_review_cases() um Zeitraumbeschränkung.
    """
    sql = (
        "SELECT rc.id AS case_id, rc.employee_id, e.personnel_no, "
        "e.first_name, e.last_name, rc.case_type, rc.severity, rc.status, "
        "rc.time_booking_id, rc.description, rc.detected_at, rc.note "
        "FROM review_cases rc "
        "JOIN employees e ON e.id = rc.employee_id "
        "WHERE rc.status IN ('OPEN', 'IN_REVIEW') "
        "AND rc.detected_at >= ? AND rc.detected_at < ?"
    )
    params: list = [from_dt.isoformat(), to_dt.isoformat()]
    if employee_id is not None:
        sql += " AND rc.employee_id = ?"
        params.append(employee_id)
    sql += " ORDER BY rc.detected_at"
    rows = conn.execute(sql, params).fetchall()
    return [_parse_review_case_row(r) for r in rows]


def list_review_cases_for_booking(
    conn: sqlite3.Connection,
    booking_id: int,
) -> list[ReviewCaseRow]:
    """Alle Prüffälle (offen und geschlossen) zu einer bestimmten Buchung."""
    sql = (
        "SELECT rc.id AS case_id, rc.employee_id, e.personnel_no, "
        "e.first_name, e.last_name, rc.case_type, rc.severity, rc.status, "
        "rc.time_booking_id, rc.description, rc.detected_at, rc.note "
        "FROM review_cases rc "
        "JOIN employees e ON e.id = rc.employee_id "
        "WHERE rc.time_booking_id = ? "
        "ORDER BY rc.detected_at"
    )
    rows = conn.execute(sql, (booking_id,)).fetchall()
    return [_parse_review_case_row(r) for r in rows]


def get_employee_identity(
    conn: sqlite3.Connection,
    employee_id: int,
) -> tuple[str, str]:
    """Gibt (personnel_no, employee_name) aus employees-Stammdaten zurück.

    Fallback auf str(employee_id) / 'MA {id}' wenn kein Eintrag vorhanden —
    schützt Exportfunktionen gegen verwaiste Buchungsreferenzen bei
    verletzter referenzieller Integrität. Im Normalbetrieb nie ausgelöst.
    """
    row = conn.execute(
        "SELECT personnel_no, first_name || ' ' || last_name AS name "
        "FROM employees WHERE id = ?",
        (employee_id,),
    ).fetchone()
    if row:
        return row["personnel_no"], row["name"]
    return str(employee_id), f"MA {employee_id}"
