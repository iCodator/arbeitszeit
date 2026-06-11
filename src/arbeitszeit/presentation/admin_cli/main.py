"""Admin-CLI-Einstiegspunkt: administrative Verwaltung der Zeiterfassung."""
import argparse
import os
import sys
from pathlib import Path

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations

from . import bookings, employees, reports, schedule, system, user_accounts


def _resolve_user_id(args: argparse.Namespace) -> int:
    user_id: int | None = getattr(args, "user_id", None)
    if user_id is None:
        env_val = os.environ.get("ADMIN_USER_ID")
        if env_val is not None:
            try:
                user_id = int(env_val)
            except ValueError:
                print(
                    f"Fehler: ADMIN_USER_ID muss eine Ganzzahl sein, got {env_val!r}",
                    file=sys.stderr,
                )
                sys.exit(1)
    if user_id is None:
        print(
            "Fehler: Benutzer-ID erforderlich. "
            "Entweder --user-id oder Umgebungsvariable ADMIN_USER_ID setzen.",
            file=sys.stderr,
        )
        sys.exit(1)
    return user_id


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="admin",
        description="Arbeitszeit Admin-CLI",
    )
    parser.add_argument("--db", required=True, type=Path, metavar="DB_PATH",
                        help="Pfad zur SQLite-Datenbankdatei")
    parser.add_argument("--user-id", type=int, default=None, metavar="ID",
                        help="Benutzer-ID (alternativ: ADMIN_USER_ID-Umgebungsvariable)")

    sub = parser.add_subparsers(dest="domain", required=True)
    employees.register_subcommands(sub)
    bookings.register_subcommands(sub)
    schedule.register_subcommands(sub)
    reports.register_subcommands(sub)
    system.register_subcommands(sub)
    user_accounts.register_subcommands(sub)

    args = parser.parse_args(argv)
    user_id = _resolve_user_id(args)

    conn = open_connection(args.db)
    try:
        run_migrations(conn)
        audit_conn = open_connection(args.db)
        try:
            _dispatch(args, conn, audit_conn, user_id, args.db)
        finally:
            audit_conn.close()
    finally:
        conn.close()


def _dispatch(
    args: argparse.Namespace,
    conn,
    audit_conn,
    user_id: int,
    db_path: Path,
) -> None:
    domain = args.domain

    if domain == "employees":
        cmd = args.employees_cmd
        if cmd == "list":
            employees.cmd_employees_list(conn, args)
        elif cmd == "add":
            employees.cmd_employees_add(conn, args, user_id)
        elif cmd == "deactivate":
            employees.cmd_employees_deactivate(conn, args, user_id)

    elif domain == "cards":
        cmd = args.cards_cmd
        if cmd == "assign":
            employees.cmd_cards_assign(conn, args, user_id)
        elif cmd == "replace":
            employees.cmd_cards_replace(conn, args, user_id)
        elif cmd == "deactivate":
            employees.cmd_cards_deactivate(conn, args, user_id)

    elif domain == "bookings":
        cmd = args.bookings_cmd
        if cmd == "correct":
            bookings.cmd_bookings_correct(conn, audit_conn, args, user_id)
        elif cmd == "supplement":
            bookings.cmd_bookings_supplement(conn, audit_conn, args, user_id)
        elif cmd == "approve-supplement":
            bookings.cmd_bookings_approve_supplement(conn, audit_conn, args, user_id)
        elif cmd == "reject-supplement":
            bookings.cmd_bookings_reject_supplement(conn, audit_conn, args, user_id)

    elif domain == "schedule":
        cmd = args.schedule_cmd
        if cmd == "set":
            schedule.cmd_schedule_set(conn, audit_conn, args, user_id)
        elif cmd == "show":
            schedule.cmd_schedule_show(conn, args, user_id)

    elif domain == "reports":
        cmd = args.reports_cmd
        if cmd == "export-csv":
            reports.cmd_reports_export_csv(conn, args, user_id)
        elif cmd == "export-pdf-day":
            reports.cmd_reports_export_pdf_day(conn, args, user_id)
        elif cmd == "export-pdf-week":
            reports.cmd_reports_export_pdf_week(conn, args, user_id)
        elif cmd == "export-pdf-month":
            reports.cmd_reports_export_pdf_month(conn, args, user_id)
        elif cmd == "export-pdf-employee":
            reports.cmd_reports_export_pdf_employee(conn, args, user_id)
        elif cmd == "open-bookings":
            reports.cmd_reports_open_bookings(conn, args, user_id)
        elif cmd == "warn-cases":
            reports.cmd_reports_warn_cases(conn, args, user_id)
        elif cmd == "corrections":
            reports.cmd_reports_corrections(conn, args, user_id)
        elif cmd == "supplements":
            reports.cmd_reports_supplements(conn, args, user_id)
        elif cmd == "open-review-cases":
            reports.cmd_reports_open_review_cases(conn, args, user_id)

    elif domain == "system":
        cmd = args.system_cmd
        if cmd == "check":
            system.cmd_system_check(db_path, conn, args, user_id)
        elif cmd == "backup":
            system.cmd_system_backup(db_path, conn, args, user_id)

    elif domain == "users":
        cmd = args.users_cmd
        if cmd == "add":
            user_accounts.cmd_users_add(conn, args, user_id)
        elif cmd == "list":
            user_accounts.cmd_users_list(conn, args)
        elif cmd == "deactivate":
            user_accounts.cmd_users_deactivate(conn, args, user_id)


if __name__ == "__main__":
    run()
