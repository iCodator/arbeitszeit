"""Admin-CLI: Mitarbeiter- und Kartenverwaltung (ADMIN-Rolle).

Alle Schreiboperationen laufen über Use Cases der Application-Schicht.
Die Rollenprüfung erfolgt dort; hier wird nur noch Fehler-Handling und Ausgabe gemacht.
"""

__version__ = "1.0"

import argparse
import sqlite3
import sys

from arbeitszeit.application.commands import (
    AssignRfidCardCommand,
    CreateEmployeeCommand,
    DeactivateEmployeeCommand,
    DeactivateRfidCardCommand,
    ReplaceRfidCardCommand,
)
from arbeitszeit.application.use_cases.manage_employees import (
    CreateEmployeeUseCase,
    DeactivateEmployeeUseCase,
)
from arbeitszeit.application.use_cases.manage_rfid_cards import (
    AssignRfidCardUseCase,
    DeactivateRfidCardUseCase,
    ReplaceRfidCardUseCase,
)
from arbeitszeit.domain.errors import DomainError
from arbeitszeit.domain.value_objects import EmployeeId, RfidCardId, UserAccountId
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork
from arbeitszeit.infrastructure.hardware import EmptyUidError, HardwareTimeoutError
from arbeitszeit.infrastructure.hardware.evdev_reader import (
    DeviceNotFoundError,
    resolve_evdev_device,
    scan_rfid_uid_hash,
)


def _make_uow(conn: sqlite3.Connection, audit_conn: sqlite3.Connection) -> SQLiteUnitOfWork:
    return SQLiteUnitOfWork(conn, audit_conn)


def cmd_employees_list(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rows = conn.execute(
        "SELECT id, personnel_no, first_name, last_name, active "
        "FROM employees ORDER BY personnel_no"
    ).fetchall()
    if not rows:
        print("Keine Mitarbeiter vorhanden.")
        return
    print(f"{'ID':>4}  {'Nr':10}  {'Name':30}  Status")
    print("-" * 60)
    for row in rows:
        status = "aktiv" if row["active"] else "inaktiv"
        name = f"{row['first_name']} {row['last_name']}"
        print(f"{row['id']:>4}  {row['personnel_no']:10}  {name:30}  {status}")


def cmd_employees_add(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    cmd = CreateEmployeeCommand(
        acting_user_id=UserAccountId(user_id),
        personnel_no=args.personnel_no,
        first_name=args.first_name,
        last_name=args.last_name,
    )
    try:
        result = CreateEmployeeUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Mitarbeiter angelegt (ID {result.employee_id}).")


def cmd_employees_deactivate(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    cmd = DeactivateEmployeeCommand(
        acting_user_id=UserAccountId(user_id),
        employee_id=EmployeeId(args.id),
    )
    try:
        DeactivateEmployeeUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Mitarbeiter {args.id} deaktiviert.")


def cmd_cards_assign(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    if args.uid_hash and args.scan:
        print("Fehler: --uid-hash und --scan schließen sich aus.", file=sys.stderr)
        sys.exit(1)
    if not args.uid_hash and not args.scan:
        print("Fehler: --uid-hash oder --scan ist erforderlich.", file=sys.stderr)
        sys.exit(1)
    if args.scan and not args.rfid:
        print("Fehler: --scan erfordert --rfid.", file=sys.stderr)
        sys.exit(1)

    if args.scan:
        try:
            rfid_path = resolve_evdev_device(args.rfid)
        except DeviceNotFoundError as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            sys.exit(1)
        print("Bitte Karte an den RFID-Reader halten …")
        try:
            uid_hash = scan_rfid_uid_hash(rfid_path)
        except HardwareTimeoutError as exc:
            print(f"Fehler: Timeout – {exc}", file=sys.stderr)
            sys.exit(1)
        except (EmptyUidError, OSError) as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        uid_hash = args.uid_hash

    cmd = AssignRfidCardCommand(
        acting_user_id=UserAccountId(user_id),
        employee_id=EmployeeId(args.employee_id),
        uid_hash=uid_hash,
    )
    try:
        result = AssignRfidCardUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Karte zugewiesen (ID {result.card_id}).")


def cmd_cards_replace(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    cmd = ReplaceRfidCardCommand(
        acting_user_id=UserAccountId(user_id),
        old_card_id=RfidCardId(args.old_card_id),
        uid_hash=args.uid_hash,
    )
    try:
        result = ReplaceRfidCardUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Karte ersetzt: alt={args.old_card_id}, neu={result.new_card_id}.")


def cmd_cards_deactivate(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    cmd = DeactivateRfidCardCommand(
        acting_user_id=UserAccountId(user_id),
        card_id=RfidCardId(args.id),
    )
    try:
        DeactivateRfidCardUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Karte {args.id} deaktiviert.")


def register_subcommands(
    sub: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    # --- employees ---
    emp = sub.add_parser("employees", help="Mitarbeiterverwaltung")
    emp_sub = emp.add_subparsers(dest="employees_cmd", required=True)

    emp_sub.add_parser("list", help="Alle Mitarbeiter auflisten")

    add = emp_sub.add_parser("add", help="Mitarbeiter anlegen")
    add.add_argument("--personnel-no", required=True)
    add.add_argument("--first-name", required=True)
    add.add_argument("--last-name", required=True)

    deact = emp_sub.add_parser("deactivate", help="Mitarbeiter deaktivieren")
    deact.add_argument("id", type=int)

    # --- cards ---
    cards = sub.add_parser("cards", help="RFID-Kartenverwaltung")
    cards_sub = cards.add_subparsers(dest="cards_cmd", required=True)

    assign = cards_sub.add_parser("assign", help="Neue RFID-Karte einem Mitarbeiter zuweisen")
    assign.add_argument("--employee-id", type=int, required=True)
    assign.add_argument("--uid-hash", help="Fertig berechneter SHA-256-Hash der Karten-UID")
    assign.add_argument(
        "--rfid",
        metavar="RFID_GERÄT",
        help="Gerätename oder -pfad des RFID-Readers (für --scan)",
    )
    assign.add_argument(
        "--scan",
        action="store_true",
        help="UID direkt vom RFID-Reader lesen (erfordert --rfid)",
    )

    replace = cards_sub.add_parser("replace", help="Verlorene/defekte Karte ersetzen")
    replace.add_argument("--old-card-id", type=int, required=True)
    replace.add_argument("--uid-hash", required=True)

    deact_card = cards_sub.add_parser("deactivate", help="Karte deaktivieren")
    deact_card.add_argument("id", type=int)
