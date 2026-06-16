"""Admin-CLI: PDF/CSV-Export und Pflichtauswertungen (ADMIN/REVIEWER-Rolle)."""

import argparse
import json
import sqlite3
import sys
from datetime import date

from arbeitszeit.infrastructure.export import csv_exporter, pdf_report_service
from arbeitszeit.infrastructure.export.report_queries import (
    BookingRow,
    CorrectionRow,
    ReviewCaseRow,
    SupplementRow,
    list_corrections,
    list_open_bookings,
    list_open_bookings_in_period,
    list_open_review_cases,
    list_open_review_cases_in_period,
    list_supplements,
    list_warn_bookings,
)
from arbeitszeit.presentation.admin_cli._intervals import (
    day_interval,
)


def _require_admin_or_reviewer(conn: sqlite3.Connection, user_id: int) -> None:
    row = conn.execute(
        "SELECT role, active FROM user_accounts WHERE id = ?", (user_id,)
    ).fetchone()
    if row is None or not row["active"] or row["role"] not in ("ADMIN", "REVIEWER"):
        print(
            "Fehler: Zugriff verweigert. Aktion erfordert ADMIN- oder REVIEWER-Rolle.",
            file=sys.stderr,
        )
        sys.exit(1)


def _get_export_dir(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT config_value_json FROM system_config "
        "WHERE config_key = 'export.export_dir' ORDER BY version DESC LIMIT 1"
    ).fetchone()
    if row is None:
        print(
            "Fehler: system_config-Schlüssel 'export.export_dir' nicht gesetzt.",
            file=sys.stderr,
        )
        sys.exit(1)
    return str(json.loads(row["config_value_json"]))


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        print(
            f"Fehler: Ungültiges Datum {value!r} (erwartet YYYY-MM-DD)", file=sys.stderr
        )
        sys.exit(1)


def _print_bookings_table(rows: list[BookingRow]) -> None:
    if not rows:
        print("Keine Buchungen gefunden.")
        return
    print(f"{'ID':>6}  {'Mitarbeiter':25}  {'Art':12}  {'Zeitpunkt':22}  Status")
    print("-" * 85)
    for r in rows:
        print(
            f"{r.booking_id:>6}  {r.employee_name:25}  "
            f"{r.booking_type.value:12}  {r.booked_at.isoformat():22}  {r.status.value}"
        )
    print(f"\n{len(rows)} Buchung(en).")


def _print_corrections_table(rows: list[CorrectionRow]) -> None:
    if not rows:
        print("Keine Korrekturen gefunden.")
        return
    for r in rows:
        print(
            f"[{r.correction_id}] {r.employee_name} ({r.personnel_no}): "
            f"{r.old_booking_type.value} @ {r.old_booked_at.isoformat()} → "
            f"{r.new_booking_type.value} @ {r.new_booked_at.isoformat()} "
            f"(Grund: {r.reason})"
        )
    print(f"\n{len(rows)} Korrektur(en).")


def _print_supplements_table(rows: list[SupplementRow]) -> None:
    if not rows:
        print("Keine Nachträge gefunden.")
        return
    for r in rows:
        print(
            f"[{r.supplement_id}] {r.employee_name} ({r.personnel_no}): "
            f"{r.booking_type.value} @ {r.event_at.isoformat()} "
            f"({r.approval_status.value}) — {r.reason}"
        )
    print(f"\n{len(rows)} Nachtrag/Nachträge.")


def _print_review_cases_table(rows: list[ReviewCaseRow]) -> None:
    if not rows:
        print("Keine Prüffälle gefunden.")
        return
    for r in rows:
        print(
            f"[{r.case_id}] {r.employee_name} ({r.personnel_no}): "
            f"{r.case_type.value} ({r.severity.value}) — {r.description}"
        )
    print(f"\n{len(rows)} Prüffall/-fälle.")


# --- Export-Befehle ---


def cmd_reports_export_csv(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    from pathlib import Path

    export_dir = Path(_get_export_dir(conn))
    from_dt, _ = day_interval(_parse_date(args.from_date))
    _, to_dt = day_interval(_parse_date(args.to_date))
    employee_id = getattr(args, "employee_id", None)
    detail_path = csv_exporter.export_detail(
        conn, from_dt, to_dt, export_dir, employee_id
    )
    condensed_path = csv_exporter.export_condensed(
        conn, from_dt, to_dt, export_dir, employee_id
    )
    print(f"Detail-CSV: {detail_path}")
    print(f"Verdichtet-CSV: {condensed_path}")


def cmd_reports_export_pdf_day(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    from pathlib import Path

    export_dir = Path(_get_export_dir(conn))
    day = _parse_date(args.date)
    path = pdf_report_service.create_daily_report(conn, day, export_dir)
    print(f"PDF: {path}")


def cmd_reports_export_pdf_week(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    from pathlib import Path

    export_dir = Path(_get_export_dir(conn))
    path = pdf_report_service.create_weekly_report(
        conn, args.year, args.week, export_dir
    )
    print(f"PDF: {path}")


def cmd_reports_export_pdf_month(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    from pathlib import Path

    export_dir = Path(_get_export_dir(conn))
    path = pdf_report_service.create_monthly_report(
        conn, args.year, args.month, export_dir
    )
    print(f"PDF: {path}")


def cmd_reports_export_pdf_employee(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    from pathlib import Path

    export_dir = Path(_get_export_dir(conn))
    from_dt, _ = day_interval(_parse_date(args.from_date))
    _, to_dt = day_interval(_parse_date(args.to_date))
    path = pdf_report_service.create_employee_report(
        conn, args.employee_id, from_dt, to_dt, export_dir
    )
    print(f"PDF: {path}")


# --- Pflichtauswertungen (Pflichtenheft v3 §7.12) ---


def cmd_reports_open_bookings(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    employee_id = getattr(args, "employee_id", None)
    from_date = getattr(args, "from_date", None)
    to_date = getattr(args, "to_date", None)
    if from_date is not None and to_date is not None:
        from_dt, _ = day_interval(_parse_date(from_date))
        _, to_dt = day_interval(_parse_date(to_date))
        rows = list_open_bookings_in_period(
            conn, from_dt, to_dt, employee_id=employee_id
        )
        print(f"Offene Buchungen (Status OPEN) von {from_date} bis {to_date}:")
    else:
        rows = list_open_bookings(conn, employee_id=employee_id)
        print("Offene Buchungen (Status OPEN) — alle:")
    _print_bookings_table(rows)


def cmd_reports_warn_cases(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    from_dt, _ = day_interval(_parse_date(args.from_date))
    _, to_dt = day_interval(_parse_date(args.to_date))
    employee_id = getattr(args, "employee_id", None)
    rows = list_warn_bookings(conn, from_dt, to_dt, employee_id=employee_id)
    print("Buchungen mit WARN/NEEDS_REVIEW:")
    _print_bookings_table(rows)


def cmd_reports_corrections(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    from_dt, _ = day_interval(_parse_date(args.from_date))
    _, to_dt = day_interval(_parse_date(args.to_date))
    employee_id = getattr(args, "employee_id", None)
    rows = list_corrections(conn, from_dt, to_dt, employee_id=employee_id)
    print("Buchungskorrekturen:")
    _print_corrections_table(rows)


def cmd_reports_supplements(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    from_dt, _ = day_interval(_parse_date(args.from_date))
    _, to_dt = day_interval(_parse_date(args.to_date))
    employee_id = getattr(args, "employee_id", None)
    rows = list_supplements(conn, from_dt, to_dt, employee_id=employee_id)
    print("Nachträge:")
    _print_supplements_table(rows)


def cmd_reports_open_review_cases(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin_or_reviewer(conn, user_id)
    employee_id = getattr(args, "employee_id", None)
    from_date = getattr(args, "from_date", None)
    to_date = getattr(args, "to_date", None)
    if from_date is not None and to_date is not None:
        from_dt, _ = day_interval(_parse_date(from_date))
        _, to_dt = day_interval(_parse_date(to_date))
        rows = list_open_review_cases_in_period(
            conn, from_dt, to_dt, employee_id=employee_id
        )
        print(f"Offene Prüffälle von {from_date} bis {to_date}:")
    else:
        rows = list_open_review_cases(conn, employee_id=employee_id)
        print("Offene Prüffälle — alle:")
    _print_review_cases_table(rows)


def register_subcommands(
    sub: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    reports = sub.add_parser("reports", help="Berichte und Pflichtauswertungen")
    rsub = reports.add_subparsers(dest="reports_cmd", required=True)

    # --- Export ---
    csv_cmd = rsub.add_parser("export-csv", help="CSV-Export (Detail + verdichtet)")
    csv_cmd.add_argument(
        "--from", required=True, dest="from_date", metavar="YYYY-MM-DD"
    )
    csv_cmd.add_argument("--to", required=True, dest="to_date", metavar="YYYY-MM-DD")
    csv_cmd.add_argument("--employee-id", type=int, default=None)

    pdf_day = rsub.add_parser("export-pdf-day", help="Tagesbericht als PDF")
    pdf_day.add_argument("date", metavar="YYYY-MM-DD")

    pdf_week = rsub.add_parser("export-pdf-week", help="Wochenbericht als PDF")
    pdf_week.add_argument("year", type=int)
    pdf_week.add_argument("week", type=int)

    pdf_month = rsub.add_parser("export-pdf-month", help="Monatsbericht als PDF")
    pdf_month.add_argument("year", type=int)
    pdf_month.add_argument("month", type=int)

    pdf_emp = rsub.add_parser("export-pdf-employee", help="Mitarbeiterbericht als PDF")
    pdf_emp.add_argument("--employee-id", required=True, type=int)
    pdf_emp.add_argument(
        "--from", required=True, dest="from_date", metavar="YYYY-MM-DD"
    )
    pdf_emp.add_argument("--to", required=True, dest="to_date", metavar="YYYY-MM-DD")

    # --- Pflichtauswertungen ---
    ob = rsub.add_parser("open-bookings", help="Offene Buchungen anzeigen")
    ob.add_argument("--from", dest="from_date", metavar="YYYY-MM-DD", default=None)
    ob.add_argument("--to", dest="to_date", metavar="YYYY-MM-DD", default=None)
    ob.add_argument("--employee-id", type=int, default=None)

    wc = rsub.add_parser("warn-cases", help="WARN/NEEDS_REVIEW-Buchungen anzeigen")
    wc.add_argument("--from", required=True, dest="from_date", metavar="YYYY-MM-DD")
    wc.add_argument("--to", required=True, dest="to_date", metavar="YYYY-MM-DD")
    wc.add_argument("--employee-id", type=int, default=None)

    corr = rsub.add_parser("corrections", help="Buchungskorrekturen anzeigen")
    corr.add_argument("--from", required=True, dest="from_date", metavar="YYYY-MM-DD")
    corr.add_argument("--to", required=True, dest="to_date", metavar="YYYY-MM-DD")
    corr.add_argument("--employee-id", type=int, default=None)

    suppl = rsub.add_parser("supplements", help="Nachträge anzeigen")
    suppl.add_argument("--from", required=True, dest="from_date", metavar="YYYY-MM-DD")
    suppl.add_argument("--to", required=True, dest="to_date", metavar="YYYY-MM-DD")
    suppl.add_argument("--employee-id", type=int, default=None)

    orc = rsub.add_parser("open-review-cases", help="Offene Prüffälle anzeigen")
    orc.add_argument("--from", dest="from_date", metavar="YYYY-MM-DD", default=None)
    orc.add_argument("--to", dest="to_date", metavar="YYYY-MM-DD", default=None)
    orc.add_argument("--employee-id", type=int, default=None)
