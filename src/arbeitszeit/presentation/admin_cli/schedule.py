"""Admin-CLI: Regelarbeitszeit verwalten.

schedule set: nur ADMIN; Rollenprüfung erfolgt in ManageWorkScheduleUseCase
              (Anwendungsschicht), nicht hier.
schedule show: ADMIN und REVIEWER; Rollenprüfung auf CLI-Ebene via
               require_admin_or_reviewer() aus _auth.py.
"""

__version__ = "1.2"

import argparse
import sqlite3
import sys
from datetime import date, datetime, time

from arbeitszeit.application.commands import ChangeWorkScheduleCommand
from arbeitszeit.application.use_cases.manage_work_schedule import (
    ManageWorkScheduleUseCase,
)
from arbeitszeit.domain.enums import ChangeOrigin, ScopeType
from arbeitszeit.domain.errors import DomainError
from arbeitszeit.domain.value_objects import EmployeeId, UserAccountId
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork
from arbeitszeit.presentation.admin_cli._auth import require_admin_or_reviewer

_WEEKDAY_NAMES = {1: "Mo", 2: "Di", 3: "Mi", 4: "Do", 5: "Fr", 6: "Sa", 7: "So"}


def _parse_time(value: str) -> time:
    try:
        h, m = value.split(":")
        return time(int(h), int(m))
    except (ValueError, AttributeError):
        print(f"Fehler: Ungültiges Zeitformat {value!r} (erwartet HH:MM)", file=sys.stderr)
        sys.exit(1)


def cmd_schedule_set(
    conn: sqlite3.Connection,
    audit_conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
) -> None:
    try:
        valid_from = datetime.strptime(args.from_date, "%d.%m.%Y").date()
    except ValueError:
        print(
            f"Fehler: Ungültiges Datum {args.from_date!r} (erwartet TT.MM.JJJJ)",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.employee_id is not None:
        scope_type = ScopeType.EMPLOYEE
        scope_employee_id = EmployeeId(args.employee_id)
    else:
        scope_type = ScopeType.GLOBAL
        scope_employee_id = None

    cmd = ChangeWorkScheduleCommand(
        scope_type=scope_type,
        scope_employee_id=scope_employee_id,
        weekday=args.weekday,
        start_time=_parse_time(args.start),
        end_time=_parse_time(args.end),
        valid_from=valid_from,
        change_origin=ChangeOrigin.ADMIN_UI,
        changed_by_user_id=UserAccountId(user_id),
        reason=None,
    )
    try:
        result = ManageWorkScheduleUseCase(SQLiteUnitOfWork(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)

    day_name = _WEEKDAY_NAMES.get(args.weekday, str(args.weekday))
    if scope_type == ScopeType.EMPLOYEE:
        print(
            f"Mitarbeiterspezifische Regelarbeitszeit gesetzt (Version {result.new_version_id}): "
            f"Mitarbeiter {args.employee_id}, {day_name} {args.start}–{args.end} "
            f"ab {valid_from.strftime('%d.%m.%Y')}."
        )
    else:
        print(
            f"Globale Regelarbeitszeit gesetzt (Version {result.new_version_id}): "
            f"{day_name} {args.start}–{args.end} ab {valid_from.strftime('%d.%m.%Y')}."
        )
    if result.superseded_version_id is not None:
        print(f"Vorgängerversion {result.superseded_version_id} geschlossen.")


def _partition_by_scope(rows: list[sqlite3.Row]) -> tuple[list[sqlite3.Row], list[sqlite3.Row]]:
    global_rows = [r for r in rows if r["scope_type"] == "GLOBAL"]
    employee_rows = [r for r in rows if r["scope_type"] == "EMPLOYEE"]
    return global_rows, employee_rows


def _print_global_section(global_rows: list[sqlite3.Row]) -> None:
    if not global_rows:
        return
    print("Globale Regelarbeitszeit (gültige Versionen):")
    print(f"  {'ID':>4}  {'Tag':3}  {'Von':5}  {'Bis':5}  {'Gültig ab'}")
    for r in global_rows:
        day_name = _WEEKDAY_NAMES.get(r["weekday"], str(r["weekday"]))
        gueltig_ab = date.fromisoformat(r["valid_from"]).strftime("%d.%m.%Y")
        print(
            f"  {r['id']:>4}  {day_name:3}  "
            f"{r['start_time']:5}  {r['end_time']:5}  {gueltig_ab}"
        )


def _print_employee_section(employee_rows: list[sqlite3.Row]) -> None:
    if not employee_rows:
        return
    print("\nMitarbeiterspezifische Regelarbeitszeit:")
    print(f"  {'ID':>4}  {'MitarID':>7}  {'Tag':3}  {'Von':5}  {'Bis':5}  {'Gültig ab'}")
    for r in employee_rows:
        day_name = _WEEKDAY_NAMES.get(r["weekday"], str(r["weekday"]))
        gueltig_ab = date.fromisoformat(r["valid_from"]).strftime("%d.%m.%Y")
        print(
            f"  {r['id']:>4}  {r['scope_employee_id']:>7}  "
            f"{day_name:3}  {r['start_time']:5}  {r['end_time']:5}  {gueltig_ab}"
        )


def _print_scope_hint(global_rows: list[sqlite3.Row], employee_rows: list[sqlite3.Row]) -> None:
    if not global_rows and employee_rows:
        print("\nHinweis: Keine globale Regelarbeitszeit aktiv — globale Praxisregel gilt.")
    elif global_rows and not employee_rows:
        print("\nHinweis: Globale Praxisregel gilt für alle Mitarbeiter (keine Ausnahmen).")


def cmd_schedule_show(conn: sqlite3.Connection, args: argparse.Namespace, user_id: int) -> None:
    require_admin_or_reviewer(conn, user_id)
    rows = conn.execute(
        "SELECT id, scope_type, scope_employee_id, weekday, start_time, end_time, "
        "valid_from, valid_until "
        "FROM work_schedule_versions "
        "WHERE valid_until IS NULL "
        "ORDER BY scope_type, scope_employee_id, weekday"
    ).fetchall()
    if not rows:
        print("Keine aktiven Regelarbeitszeitversionen vorhanden.")
        return
    global_rows, employee_rows = _partition_by_scope(rows)
    _print_global_section(global_rows)
    _print_employee_section(employee_rows)
    _print_scope_hint(global_rows, employee_rows)


def register_subcommands(
    sub: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    sched = sub.add_parser("schedule", help="Regelarbeitszeit verwalten")
    ssub = sched.add_subparsers(dest="schedule_cmd", required=True)

    set_cmd = ssub.add_parser("set", help="Regelarbeitszeit setzen")
    set_cmd.add_argument(
        "--weekday", required=True, type=int, choices=range(1, 8), metavar="1-7 (1=Mo)"
    )
    set_cmd.add_argument("--start", required=True, metavar="HH:MM")
    set_cmd.add_argument("--end", required=True, metavar="HH:MM")
    set_cmd.add_argument("--from", required=True, dest="from_date", metavar="TT.MM.JJJJ")
    set_cmd.add_argument(
        "--employee-id",
        type=int,
        default=None,
        metavar="ID",
        help="Mitarbeiter-ID für mitarbeiterspezifische Ausnahme (leer = globale Regel)",
    )

    ssub.add_parser("show", help="Aktive Regelarbeitszeiten anzeigen")
