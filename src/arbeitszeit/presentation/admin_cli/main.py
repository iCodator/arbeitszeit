"""Admin-CLI-Einstiegspunkt: administrative Verwaltung der Zeiterfassung."""

__version__ = "1.1"

import argparse
import os
import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path

from arbeitszeit.infrastructure.config_file import AppConfig, find_config, load_config
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations

from . import bookings, employees, reports, schedule, system, user_accounts


def _load_app_config(args: argparse.Namespace) -> AppConfig | None:
    config_path: Path | None = getattr(args, "config", None)
    src = config_path if config_path is not None else find_config()
    if src is None:
        return None
    try:
        return load_config(src)
    except Exception as exc:  # noqa: BLE001
        print(f"Fehler beim Laden von {src}: {exc}", file=sys.stderr)
        sys.exit(1)


def _resolve_db_path(args: argparse.Namespace, app_config: AppConfig | None) -> Path:
    db: Path | None = getattr(args, "db", None)
    if db is None and app_config is not None:
        db = app_config.database.path
    if db is None:
        print(
            "Fehler: DB-Pfad erforderlich. "
            "Entweder --db oder [database] path in config.toml.",
            file=sys.stderr,
        )
        sys.exit(1)
    return db


def _resolve_user_id(args: argparse.Namespace, app_config: AppConfig | None = None) -> int:
    # Priorität: CLI > ENV ADMIN_USER_ID > config.toml > Fehler
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
    if user_id is None and app_config is not None:
        user_id = app_config.admin.user_id
    if user_id is None:
        print(
            "Fehler: Benutzer-ID erforderlich. "
            "--user-id, ADMIN_USER_ID oder [admin] user_id in config.toml setzen.",
            file=sys.stderr,
        )
        sys.exit(1)
    return user_id


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="admin",
        description="Arbeitszeit Admin-CLI",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        metavar="CONFIG_PATH",
        help="Pfad zu config.toml (Standard: automatische Suche)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        metavar="DB_PATH",
        help="Pfad zur SQLite-Datenbankdatei (alternativ: [database] path in config.toml)",
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=None,
        metavar="ID",
        help="Benutzer-ID (alternativ: ADMIN_USER_ID oder [admin] user_id in config.toml)",
    )

    sub = parser.add_subparsers(dest="domain", required=True)
    employees.register_subcommands(sub)
    bookings.register_subcommands(sub)
    schedule.register_subcommands(sub)
    reports.register_subcommands(sub)
    system.register_subcommands(sub)
    user_accounts.register_subcommands(sub)

    args = parser.parse_args(argv)

    app_config = _load_app_config(args)
    db_path = _resolve_db_path(args, app_config)

    # Bootstrap benötigt keine user-id — es gibt noch keinen Admin
    if getattr(args, "domain", None) == "users" and getattr(args, "users_cmd", None) == "bootstrap":
        conn = open_connection(db_path)
        try:
            run_migrations(conn)
            audit_conn = open_connection(db_path)
            try:
                user_accounts.cmd_users_bootstrap(conn, audit_conn, args)
            finally:
                audit_conn.close()
        finally:
            conn.close()
        return

    user_id = _resolve_user_id(args, app_config)

    conn = open_connection(db_path)
    try:
        run_migrations(conn)
        audit_conn = open_connection(db_path)
        try:
            _dispatch(args, conn, audit_conn, user_id, db_path, app_config=app_config)
        finally:
            audit_conn.close()
    finally:
        conn.close()


def _dispatch(
    args: argparse.Namespace,
    conn: sqlite3.Connection,
    audit_conn: sqlite3.Connection,
    user_id: int,
    db_path: Path,
    *,
    app_config: AppConfig | None = None,
) -> None:
    table: dict[tuple[str, str], Callable[[], None]] = {
        ("employees", "list"): lambda: employees.cmd_employees_list(conn, args),
        ("employees", "add"): lambda: employees.cmd_employees_add(conn, audit_conn, args, user_id),
        ("employees", "deactivate"): lambda: employees.cmd_employees_deactivate(
            conn, audit_conn, args, user_id
        ),
        ("cards", "assign"): lambda: employees.cmd_cards_assign(conn, audit_conn, args, user_id),
        ("cards", "replace"): lambda: employees.cmd_cards_replace(conn, audit_conn, args, user_id),
        ("cards", "deactivate"): lambda: employees.cmd_cards_deactivate(
            conn, audit_conn, args, user_id
        ),
        ("bookings", "correct"): lambda: bookings.cmd_bookings_correct(
            conn, audit_conn, args, user_id
        ),
        ("bookings", "supplement"): lambda: bookings.cmd_bookings_supplement(
            conn, audit_conn, args, user_id
        ),
        ("bookings", "approve-supplement"): lambda: bookings.cmd_bookings_approve_supplement(
            conn, audit_conn, args, user_id
        ),
        ("bookings", "reject-supplement"): lambda: bookings.cmd_bookings_reject_supplement(
            conn, audit_conn, args, user_id
        ),
        ("schedule", "set"): lambda: schedule.cmd_schedule_set(conn, audit_conn, args, user_id),
        ("schedule", "show"): lambda: schedule.cmd_schedule_show(conn, args, user_id),
        ("reports", "export-csv"): lambda: reports.cmd_reports_export_csv(conn, args, user_id),
        ("reports", "export-csv-review-cases"): lambda: reports.cmd_reports_export_csv_review_cases(
            conn, args, user_id
        ),
        ("reports", "export-pdf-day"): lambda: reports.cmd_reports_export_pdf_day(
            conn, args, user_id
        ),
        ("reports", "export-pdf-week"): lambda: reports.cmd_reports_export_pdf_week(
            conn, args, user_id
        ),
        ("reports", "export-pdf-month"): lambda: reports.cmd_reports_export_pdf_month(
            conn, args, user_id
        ),
        ("reports", "export-pdf-employee"): lambda: reports.cmd_reports_export_pdf_employee(
            conn, args, user_id
        ),
        ("reports", "open-bookings"): lambda: reports.cmd_reports_open_bookings(
            conn, args, user_id
        ),
        ("reports", "warn-cases"): lambda: reports.cmd_reports_warn_cases(conn, args, user_id),
        ("reports", "corrections"): lambda: reports.cmd_reports_corrections(conn, args, user_id),
        ("reports", "supplements"): lambda: reports.cmd_reports_supplements(conn, args, user_id),
        ("reports", "open-review-cases"): lambda: reports.cmd_reports_open_review_cases(
            conn, args, user_id
        ),
        ("system", "check"): lambda: system.cmd_system_check(
            db_path, conn, args, user_id, app_config=app_config
        ),
        ("system", "backup"): lambda: system.cmd_system_backup(
            db_path, conn, args, user_id, app_config=app_config
        ),
        ("system", "setup"): lambda: system.cmd_system_setup(
            db_path, conn, args, user_id, app_config=app_config
        ),
        ("users", "add"): lambda: user_accounts.cmd_users_add(conn, audit_conn, args, user_id),
        ("users", "list"): lambda: user_accounts.cmd_users_list(conn, args),
        ("users", "deactivate"): lambda: user_accounts.cmd_users_deactivate(
            conn, audit_conn, args, user_id
        ),
        ("users", "reactivate"): lambda: user_accounts.cmd_users_reactivate(
            conn, audit_conn, args, user_id
        ),
        ("users", "change-role"): lambda: user_accounts.cmd_users_change_role(
            conn, audit_conn, args, user_id
        ),
        ("users", "bootstrap"): lambda: user_accounts.cmd_users_bootstrap(conn, audit_conn, args),
    }
    domain: str = args.domain
    cmd: str | None = getattr(args, f"{domain}_cmd", None)
    handler = table.get((domain, cmd)) if cmd is not None else None
    if handler is not None:
        handler()


if __name__ == "__main__":  # pragma: no cover
    run()
