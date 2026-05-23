"""PDF-Berichte via reportlab (Pflichtenheft v3 §7.11, Regelwerk v3 §12/§13).

Alle vier Berichtstypen verwenden report_queries.py als Datenquelle.

Dateinamen:
  bericht_tag_YYYY-MM-DD_YYYYMMDDTHHMMSSZ.pdf
  bericht_woche_YYYY-WNN_YYYYMMDDTHHMMSSZ.pdf
  bericht_monat_YYYY-MM_YYYYMMDDTHHMMSSZ.pdf
  bericht_mitarbeiter_NNNN_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.pdf
"""
import calendar
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from arbeitszeit.infrastructure.export.report_queries import (
    BookingRow,
    CorrectionRow,
    SupplementRow,
    get_employee_identity,
    list_bookings,
    list_corrections,
    list_open_review_cases,
    list_supplements,
)

_STYLES = getSampleStyleSheet()
_PAGE_W, _PAGE_H = A4
_MARGIN = 2 * cm

_TBL_HEADER = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2F8")]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#AAAAAA")),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
])


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _h1(text: str) -> Paragraph:
    return Paragraph(text, _STYLES["Heading1"])


def _h2(text: str) -> Paragraph:
    return Paragraph(text, _STYLES["Heading2"])


def _p(text: str) -> Paragraph:
    return Paragraph(text, _STYLES["Normal"])


def _space(cm_val: float = 0.4) -> Spacer:
    return Spacer(1, cm_val * cm)


def _meta_table(rows: list[tuple[str, str]]) -> Table:
    data = [[_p(f"<b>{k}:</b>"), _p(v)] for k, v in rows]
    t = Table(data, colWidths=[4 * cm, None])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def _booking_table(bookings: list[BookingRow]) -> Table:
    header = ["MA-Nr", "Name", "Datum", "Uhrzeit", "Art", "Status", "Quelle"]
    rows = [header]
    for b in bookings:
        rows.append([
            b.personnel_no,
            b.employee_name,
            b.booked_at.date().isoformat(),
            b.booked_at.strftime("%H:%M"),
            b.booking_type.value,
            b.status.value,
            b.source.value,
        ])
    col_w = [2 * cm, 3.5 * cm, 2.5 * cm, 2 * cm, 3 * cm, 3 * cm, 2.5 * cm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(_TBL_HEADER)
    return t


def _correction_table(corrections: list[CorrectionRow]) -> Table:
    header = ["MA-Nr", "Name", "Alter Typ", "Alter Zeitpunkt",
              "Neuer Typ", "Neuer Zeitpunkt", "Begründung", "Zeitstempel"]
    rows = [header]
    for c in corrections:
        rows.append([
            c.personnel_no,
            c.employee_name,
            c.old_booking_type.value,
            c.old_booked_at.strftime("%d.%m.%Y %H:%M"),
            c.new_booking_type.value,
            c.new_booked_at.strftime("%d.%m.%Y %H:%M"),
            c.reason[:40],
            c.corrected_at.strftime("%d.%m.%Y %H:%M"),
        ])
    col_w = [1.8 * cm, 3 * cm, 2 * cm, 3 * cm, 2 * cm, 3 * cm, 4 * cm, 3 * cm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(_TBL_HEADER)
    return t


def _supplement_table(supplements: list[SupplementRow]) -> Table:
    header = ["MA-Nr", "Name", "Art", "Ereigniszeitpunkt", "Begründung", "Freigabestatus"]
    rows = [header]
    for s in supplements:
        rows.append([
            s.personnel_no,
            s.employee_name,
            s.booking_type.value,
            s.event_at.strftime("%d.%m.%Y %H:%M"),
            s.reason[:40],
            s.approval_status.value,
        ])
    col_w = [1.8 * cm, 3.2 * cm, 2.5 * cm, 3.5 * cm, 5 * cm, 2.5 * cm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(_TBL_HEADER)
    return t


_HINWEISE: list[tuple[str, str]] = [
    ("OPEN",
     "Buchung noch offen – die zugehörige Abschluss-Buchung (GO bzw. BREAK_END) "
     "steht noch aus. Prüfung oder manuelle Klärung erforderlich."),
    ("WARN",
     "Auffällig – ein Hinweis liegt vor (z. B. Buchung außerhalb des Regelzeitfensters, "
     "Arbeitszeit über 8 h). Keine zwingende Prüfung, aber Aufmerksamkeit empfohlen."),
    ("NEEDS_REVIEW",
     "Prüfpflichtig – ein kritischer Befund liegt vor (z. B. Arbeitszeit über 10 h, "
     "Ruhezeit unter 11 h). Muss von einem Prüfer bearbeitet und abgeschlossen werden."),
    ("Nachträge",
     "Manuell nachträglich erfasste Buchungen (Quelle: MANUAL). "
     "Freigabestatus: PENDING = noch offen, APPROVED = genehmigt, REJECTED = abgelehnt."),
    ("Korrekturen",
     "Buchungen, die von einem Bearbeiter korrigiert wurden. "
     "Die ursprüngliche Buchung bleibt mit Status CORRECTED erhalten; "
     "der neue Zustand ist in der Korrekturtabelle (Alter/Neuer Typ und Zeitpunkt) dokumentiert."),
]


def _build_pdf(
    path: Path,
    title: str,
    meta: list[tuple[str, str]],
    bookings: list[BookingRow],
    corrections: list[CorrectionRow],
    supplements: list[SupplementRow],
    conn: sqlite3.Connection,
    employee_id: int | None,
) -> None:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        bottomMargin=_MARGIN,
    )
    story = []

    story.append(_h1(title))
    story.append(_space(0.3))
    story.append(_meta_table(meta))
    story.append(_space())

    # Buchungen
    story.append(_h2("Buchungen"))
    if bookings:
        story.append(_booking_table(bookings))
    else:
        story.append(_p("Keine Buchungen im Zeitraum."))
    story.append(_space())

    # Korrekturen
    story.append(_h2("Korrekturen"))
    if corrections:
        story.append(_correction_table(corrections))
    else:
        story.append(_p("Keine Korrekturen im Zeitraum."))
    story.append(_space())

    # Nachträge
    story.append(_h2("Nachträge"))
    if supplements:
        story.append(_supplement_table(supplements))
    else:
        story.append(_p("Keine Nachträge im Zeitraum."))
    story.append(_space())

    # Offene Prüffälle
    open_cases = list_open_review_cases(conn, employee_id=employee_id)
    story.append(_h2("Offene Prüffälle"))
    if open_cases:
        header = ["MA-Nr", "Name", "Typ", "Schwere", "Beschreibung", "Erkannt am"]
        rows = [header]
        for rc in open_cases:
            rows.append([
                rc.personnel_no,
                rc.employee_name,
                rc.case_type.value,
                rc.severity.value,
                rc.description[:50],
                rc.detected_at.strftime("%d.%m.%Y"),
            ])
        col_w = [1.8 * cm, 3 * cm, 4 * cm, 2 * cm, 5.5 * cm, 2.5 * cm]
        t = Table(rows, colWidths=col_w, repeatRows=1)
        t.setStyle(_TBL_HEADER)
        story.append(t)
    else:
        story.append(_p("Keine offenen Prüffälle."))

    # Erläuterungen
    story.append(_space())
    story.append(_h2("Erläuterungen"))
    story.append(_meta_table(_HINWEISE))

    doc.build(story)


# ---------------------------------------------------------------------------
# Öffentliche Berichtsfunktionen
# ---------------------------------------------------------------------------

def create_daily_report(
    conn: sqlite3.Connection,
    day: date,
    export_dir: Path,
    now: datetime | None = None,
) -> Path:
    """Tagesbericht für alle Mitarbeiter an einem Datum."""
    if now is None:
        now = datetime.now(timezone.utc)
    from_dt = datetime(day.year, day.month, day.day, 0, 0, tzinfo=timezone.utc)
    to_dt = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone.utc)

    export_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bericht_tag_{day.isoformat()}_{now.strftime('%Y%m%dT%H%M%SZ')}.pdf"
    path = export_dir / filename

    meta = [
        ("Berichtstyp", "Tagesbericht"),
        ("Datum", day.isoformat()),
        ("Erstellt am", now.strftime("%d.%m.%Y %H:%M UTC")),
    ]
    _build_pdf(
        path, f"Tagesbericht {day.isoformat()}", meta,
        list_bookings(conn, from_dt, to_dt),
        list_corrections(conn, from_dt, to_dt),
        list_supplements(conn, from_dt, to_dt),
        conn, employee_id=None,
    )
    return path


def create_weekly_report(
    conn: sqlite3.Connection,
    year: int,
    week: int,
    export_dir: Path,
    now: datetime | None = None,
) -> Path:
    """Wochenbericht (ISO-Woche) für alle Mitarbeiter."""
    if now is None:
        now = datetime.now(timezone.utc)
    monday = date.fromisocalendar(year, week, 1)
    sunday = monday + timedelta(days=6)
    from_dt = datetime(monday.year, monday.month, monday.day, 0, 0, tzinfo=timezone.utc)
    to_dt = datetime(sunday.year, sunday.month, sunday.day, 23, 59, 59, tzinfo=timezone.utc)

    export_dir.mkdir(parents=True, exist_ok=True)
    week_str = f"{year}-W{week:02d}"
    filename = f"bericht_woche_{week_str}_{now.strftime('%Y%m%dT%H%M%SZ')}.pdf"
    path = export_dir / filename

    meta = [
        ("Berichtstyp", "Wochenbericht"),
        ("Woche", week_str),
        ("Zeitraum", f"{monday.isoformat()} – {sunday.isoformat()}"),
        ("Erstellt am", now.strftime("%d.%m.%Y %H:%M UTC")),
    ]
    _build_pdf(
        path, f"Wochenbericht {week_str}", meta,
        list_bookings(conn, from_dt, to_dt),
        list_corrections(conn, from_dt, to_dt),
        list_supplements(conn, from_dt, to_dt),
        conn, employee_id=None,
    )
    return path


def create_monthly_report(
    conn: sqlite3.Connection,
    year: int,
    month: int,
    export_dir: Path,
    now: datetime | None = None,
) -> Path:
    """Monatsbericht für alle Mitarbeiter."""
    if now is None:
        now = datetime.now(timezone.utc)
    last_day = calendar.monthrange(year, month)[1]
    from_dt = datetime(year, month, 1, 0, 0, tzinfo=timezone.utc)
    to_dt = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    export_dir.mkdir(parents=True, exist_ok=True)
    month_str = f"{year}-{month:02d}"
    filename = f"bericht_monat_{month_str}_{now.strftime('%Y%m%dT%H%M%SZ')}.pdf"
    path = export_dir / filename

    meta = [
        ("Berichtstyp", "Monatsbericht"),
        ("Monat", month_str),
        ("Zeitraum", f"{from_dt.date().isoformat()} – {to_dt.date().isoformat()}"),
        ("Erstellt am", now.strftime("%d.%m.%Y %H:%M UTC")),
    ]
    _build_pdf(
        path, f"Monatsbericht {month_str}", meta,
        list_bookings(conn, from_dt, to_dt),
        list_corrections(conn, from_dt, to_dt),
        list_supplements(conn, from_dt, to_dt),
        conn, employee_id=None,
    )
    return path


def create_employee_report(
    conn: sqlite3.Connection,
    employee_id: int,
    from_dt: datetime,
    to_dt: datetime,
    export_dir: Path,
    now: datetime | None = None,
) -> Path:
    """Mitarbeiterbericht für einen bestimmten Mitarbeiter und Zeitraum."""
    if now is None:
        now = datetime.now(timezone.utc)

    bookings = list_bookings(conn, from_dt, to_dt, employee_id=employee_id)
    personnel_no, employee_name = get_employee_identity(conn, employee_id)

    export_dir.mkdir(parents=True, exist_ok=True)
    filename = (
        f"bericht_mitarbeiter_{personnel_no}_"
        f"{from_dt.strftime('%Y%m%d')}_{to_dt.strftime('%Y%m%d')}_"
        f"{now.strftime('%Y%m%dT%H%M%SZ')}.pdf"
    )
    path = export_dir / filename

    meta = [
        ("Berichtstyp", "Mitarbeiterbericht"),
        ("Mitarbeiter", f"{employee_name} ({personnel_no})"),
        ("Zeitraum", f"{from_dt.date().isoformat()} – {to_dt.date().isoformat()}"),
        ("Erstellt am", now.strftime("%d.%m.%Y %H:%M UTC")),
    ]
    _build_pdf(
        path, f"Mitarbeiterbericht {employee_name}", meta,
        bookings,
        list_corrections(conn, from_dt, to_dt, employee_id=employee_id),
        list_supplements(conn, from_dt, to_dt, employee_id=employee_id),
        conn, employee_id=employee_id,
    )
    return path
