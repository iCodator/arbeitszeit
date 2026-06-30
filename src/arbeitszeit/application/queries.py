"""Query-DTOs für die lesende Seite (CQRS-Read).

Spiegelt die Write-Seite in `commands.py`. Enthält ausschließlich Datenstrukturen
für Abfrageergebnisse — keine SQL-Logik. Die Ausführung der Abfragen liegt in
`infrastructure/export/report_queries.py`.

Architektur-Hinweis: Die Query-Funktionen (`list_bookings`, `list_corrections` …)
operieren auf `sqlite3.Connection` und gehören zur Infrastructure. Die Row-Typen
selbst sind reine Datenstrukturen ohne DB-Abhängigkeit und werden hier definiert,
damit Presentation-Module keine Infrastructure-Klassen als Typen importieren müssen.
"""

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


@dataclass(frozen=True)
class BookingRow:
    """Einzelne Buchung mit Mitarbeiterzuordnung für Berichte."""

    booking_id: int
    employee_id: int
    personnel_no: str
    employee_name: str  # "Vorname Nachname"
    booking_type: BookingType
    booked_at: datetime
    source: BookingSource
    status: BookingStatus
    is_manual: bool  # source == MANUAL


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
