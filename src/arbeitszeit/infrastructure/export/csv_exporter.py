"""CSV-Export: detaillierter und verdichteter Export via report_queries.

Dateinamen (Pflichtenheft v3 §7.11):
  export_detail_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
  export_verdichtet_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv

Der export_dir-Pfad wird vom aufrufenden Code aus system_config gelesen
und hier direkt übergeben (system_config.get_current('export.export_dir')).
"""

__version__ = "1.1"

import csv
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from arbeitszeit.application.queries import (
    BookingRow,
)
from arbeitszeit.domain.enums import BookingStatus, BookingType
from arbeitszeit.infrastructure.export.report_queries import (
    list_bookings,
    list_corrections,
    list_open_review_cases_in_period,
    list_supplements,
)

# ---------------------------------------------------------------------------
# Dateinamen
# ---------------------------------------------------------------------------


def _make_filename(prefix: str, from_dt: datetime, to_dt: datetime, now: datetime) -> str:
    return (
        f"{prefix}_"
        f"{from_dt.strftime('%Y%m%d')}_"
        f"{to_dt.strftime('%Y%m%d')}_"
        f"{now.strftime('%Y%m%dT%H%M%SZ')}.csv"
    )


# ---------------------------------------------------------------------------
# Hilfsfunktionen für Dauer und Tagesstatistik
# ---------------------------------------------------------------------------


def _duration_minutes(b: BookingRow, day: list[BookingRow]) -> int | None:
    """Berechnet die Dauer in Minuten für eine schließende Buchung.

    GO     → Minuten seit letztem COME
    BREAK_END → Minuten seit letztem BREAK_START
    COME / BREAK_START → None (Phase beginnt erst)
    """
    if b.booking_type == BookingType.GO:
        opener = _last_before(day, b, BookingType.COME)
    elif b.booking_type == BookingType.BREAK_END:
        opener = _last_before(day, b, BookingType.BREAK_START)
    else:
        return None
    if opener is None:
        return None
    delta = b.booked_at - opener.booked_at
    return int(delta.total_seconds() // 60)


def _last_before(
    day: list[BookingRow], current: BookingRow, btype: BookingType
) -> BookingRow | None:
    result = None
    for b in day:
        if b.booked_at >= current.booked_at:
            break
        if b.booking_type == btype:
            result = b
    return result


def _group_by_employee_day(
    bookings: list[BookingRow],
) -> dict[tuple[int, date], list[BookingRow]]:
    groups: dict[tuple[int, date], list[BookingRow]] = defaultdict(list)
    for b in bookings:
        groups[(b.employee_id, b.booked_at.date())].append(b)
    return groups


def _close_work_phase(
    b: BookingRow, work_phase_start: datetime | None
) -> tuple[float, datetime | None]:
    """Schließt laufende Arbeitsphase; gibt (delta_seconds, None) zurück."""
    if work_phase_start is None:
        return 0.0, None
    return (b.booked_at - work_phase_start).total_seconds(), None


def _close_break_phase(
    b: BookingRow, break_phase_start: datetime | None
) -> tuple[float, datetime | None]:
    """Schließt laufende Pausenphase; gibt (delta_seconds, None) zurück."""
    if break_phase_start is None:
        return 0.0, None
    return (b.booked_at - break_phase_start).total_seconds(), None


def _accumulate_phase_times(day: list[BookingRow]) -> tuple[float, float, int]:
    """Summiert Arbeitszeit, Pausenzeit und Pausenanzahl per Zustandsmaschine.

    Nettoarbeitszeit = Summe aller Arbeitsphasen (COME→BREAK_START + BREAK_END→GO).
    Pausen werden nicht zur Arbeitszeit gezählt.
    """
    work_seconds = 0.0
    break_seconds = 0.0
    pause_count = 0
    work_phase_start: datetime | None = None
    break_phase_start: datetime | None = None

    for b in sorted(day, key=lambda x: x.booked_at):
        if b.booking_type == BookingType.COME:
            work_phase_start = b.booked_at
        elif b.booking_type == BookingType.BREAK_START:
            delta, work_phase_start = _close_work_phase(b, work_phase_start)
            work_seconds += delta
            break_phase_start = b.booked_at
            pause_count += 1
        elif b.booking_type == BookingType.BREAK_END:
            delta, break_phase_start = _close_break_phase(b, break_phase_start)
            break_seconds += delta
            work_phase_start = b.booked_at
        elif b.booking_type == BookingType.GO:
            delta, work_phase_start = _close_work_phase(b, work_phase_start)
            work_seconds += delta

    return work_seconds, break_seconds, pause_count


def _count_booking_statuses(day: list[BookingRow]) -> tuple[int, int, int]:
    """Zählt OPEN-, WARN- und NEEDS_REVIEW-Buchungen im Tages-Block."""
    open_count = 0
    warn_count = 0
    needs_review_count = 0
    for b in day:
        if b.status == BookingStatus.OPEN:
            open_count += 1
        elif b.status == BookingStatus.WARN:
            warn_count += 1
        elif b.status == BookingStatus.NEEDS_REVIEW:
            needs_review_count += 1
    return open_count, warn_count, needs_review_count


def _day_stats(day: list[BookingRow]) -> dict[str, object]:
    """Berechnet Tagesstatistiken aus Buchungsliste."""
    work_seconds, break_seconds, pause_count = _accumulate_phase_times(day)
    open_count, warn_count, needs_review_count = _count_booking_statuses(day)
    return {
        "nettoarbeitszeit_minuten": int(work_seconds // 60),
        "nettopausenzeit_minuten": int(break_seconds // 60),
        "pausenanzahl": pause_count,
        "anzahl_buchungen": len(day),
        "offene_buchungen": open_count,
        "warn_buchungen": warn_count,
        "pruefpflicht_buchungen": needs_review_count,
    }


# ---------------------------------------------------------------------------
# Detail-Export
# ---------------------------------------------------------------------------

_DETAIL_FIELDS = [
    "buchungs_id",
    "mitarbeiter_nr",
    "mitarbeiter_name",
    "datum",
    "uhrzeit",
    "buchungsart",
    "status",
    "quelle",
    "ist_nachtrag",
    "ist_korrigiert",
    "dauer_minuten",
]


def export_detail(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    export_dir: Path,
    employee_id: int | None = None,
    now: datetime | None = None,
) -> Path:
    """Schreibt einen detaillierten CSV-Export und gibt den Dateipfad zurück.

    Eine Zeile pro Buchung. Dauer wird aus dem Tagesverlauf abgeleitet.
    Nachträge (source=MANUAL) und korrigierte Buchungen (status=CORRECTED)
    werden explizit gekennzeichnet.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    bookings = list_bookings(conn, from_dt, to_dt, employee_id=employee_id)
    groups = _group_by_employee_day(bookings)

    export_dir.mkdir(parents=True, exist_ok=True)
    filename = _make_filename("export_detail", from_dt, to_dt, now)
    path = export_dir / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_DETAIL_FIELDS)
        writer.writeheader()

        for b in bookings:
            day = groups[(b.employee_id, b.booked_at.date())]
            writer.writerow(
                {
                    "buchungs_id": b.booking_id,
                    "mitarbeiter_nr": b.personnel_no,
                    "mitarbeiter_name": b.employee_name,
                    "datum": b.booked_at.date().isoformat(),
                    "uhrzeit": b.booked_at.strftime("%H:%M"),
                    "buchungsart": b.booking_type.value,
                    "status": b.status.value,
                    "quelle": b.source.value,
                    "ist_nachtrag": "ja" if b.is_manual else "nein",
                    "ist_korrigiert": ("ja" if b.status.value == "CORRECTED" else "nein"),
                    "dauer_minuten": _duration_minutes(b, day) or "",
                }
            )

    return path


# ---------------------------------------------------------------------------
# Verdichteter Export
# ---------------------------------------------------------------------------

_CONDENSED_FIELDS = [
    "mitarbeiter_nr",
    "mitarbeiter_name",
    "datum",
    "nettoarbeitszeit_minuten",
    "nettopausenzeit_minuten",
    "pausenanzahl",
    "anzahl_buchungen",
    "offene_buchungen",
    "warn_buchungen",
    "pruefpflicht_buchungen",
    "korrekturen",
    "nachtraege",
]


def export_condensed(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    export_dir: Path,
    employee_id: int | None = None,
    now: datetime | None = None,
) -> Path:
    """Schreibt einen verdichteten CSV-Export und gibt den Dateipfad zurück.

    Eine Zeile pro Mitarbeiter und Kalendertag. Enthält summierte Arbeitszeit,
    Pausenzeit, Statuszählungen, Korrekturen und Nachträge.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    bookings = list_bookings(conn, from_dt, to_dt, employee_id=employee_id)
    corrections = list_corrections(conn, from_dt, to_dt, employee_id=employee_id)
    supplements = list_supplements(conn, from_dt, to_dt, employee_id=employee_id)
    groups = _group_by_employee_day(bookings)

    # Korrekturen pro (employee_id, date)
    corr_count: dict[tuple[int, date], int] = defaultdict(int)
    for c in corrections:
        corr_count[(c.employee_id, c.corrected_at.date())] += 1

    # Nachträge pro (employee_id, date)
    supp_count: dict[tuple[int, date], int] = defaultdict(int)
    for s in supplements:
        supp_count[(s.employee_id, s.event_at.date())] += 1

    export_dir.mkdir(parents=True, exist_ok=True)
    filename = _make_filename("export_verdichtet", from_dt, to_dt, now)
    path = export_dir / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CONDENSED_FIELDS)
        writer.writeheader()

        for (emp_id, day_date), day in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            stats = _day_stats(day)
            first = day[0]
            writer.writerow(
                {
                    "mitarbeiter_nr": first.personnel_no,
                    "mitarbeiter_name": first.employee_name,
                    "datum": day_date.isoformat(),
                    **stats,
                    "korrekturen": corr_count.get((emp_id, day_date), 0),
                    "nachtraege": supp_count.get((emp_id, day_date), 0),
                }
            )

    return path


# ---------------------------------------------------------------------------
# Prüffälle-Export (Pflichtenheft v5 §7.13)
# ---------------------------------------------------------------------------

_REVIEW_CASE_FIELDS = [
    "prueffall_id",
    "mitarbeiter_nr",
    "mitarbeiter_name",
    "typ",
    "schwere",
    "status",
    "beschreibung",
    "buchungs_id",
    "erkannt_am",
    "hinweis",
]


def export_review_cases(
    conn: sqlite3.Connection,
    from_dt: datetime,
    to_dt: datetime,
    export_dir: Path,
    employee_id: int | None = None,
    now: datetime | None = None,
) -> Path:
    """Exportiert offene Prüffälle im Zeitraum als CSV.

    Eine Zeile pro Prüffall. Erfüllt §7.13: Pflichtauswertungen müssen
    exportierbar sein.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    rows = list_open_review_cases_in_period(conn, from_dt, to_dt, employee_id=employee_id)
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = _make_filename("export_prueffaelle", from_dt, to_dt, now)
    path = export_dir / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_REVIEW_CASE_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "prueffall_id": r.case_id,
                    "mitarbeiter_nr": r.personnel_no,
                    "mitarbeiter_name": r.employee_name,
                    "typ": r.case_type.value,
                    "schwere": r.severity.value,
                    "status": r.status.value,
                    "beschreibung": r.description,
                    "buchungs_id": r.booking_id if r.booking_id is not None else "",
                    "erkannt_am": r.detected_at.isoformat(),
                    "hinweis": r.note or "",
                }
            )

    return path
