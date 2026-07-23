"""Admin-CLI: Benutzerkontenverwaltung für ADMIN, REVIEWER und TECH.

Alle Schreiboperationen laufen über Use Cases der Application-Schicht.
Die Rollenprüfung erfolgt dort; hier wird nur noch Fehler-Handling und Ausgabe gemacht.
"""

__version__ = "1.1"

import argparse
import binascii
import hashlib
import os
import secrets
import sqlite3
import sys

from arbeitszeit.application.commands import (
    BootstrapAdminCommand,
    ChangeUserRoleCommand,
    CreateUserAccountCommand,
    DeactivateUserAccountCommand,
    ReactivateUserAccountCommand,
)
from arbeitszeit.application.use_cases.manage_user_accounts import (
    BootstrapAdminUseCase,
    ChangeUserRoleUseCase,
    CreateUserAccountUseCase,
    DeactivateUserAccountUseCase,
    ReactivateUserAccountUseCase,
)
from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.errors import DomainError
from arbeitszeit.domain.value_objects import UserAccountId
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork


def _make_uow(conn: sqlite3.Connection, audit_conn: sqlite3.Connection) -> SQLiteUnitOfWork:
    return SQLiteUnitOfWork(conn, audit_conn)


def _hash_password(password: str) -> str:
    # PBKDF2-HMAC-SHA256, 260.000 Iterationen, 16-Byte-Zufallssalt.
    # Ausgabeformat: hex(salt):hex(dk)
    # Technische Maßnahme gemäß DSGVO Art. 32.
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return binascii.hexlify(salt).decode() + ":" + binascii.hexlify(dk).decode()


def cmd_users_add(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    password = args.password or secrets.token_urlsafe(12)
    password_hash = _hash_password(password)

    try:
        role = UserRole(args.role.upper())
    except ValueError:
        print(f"Fehler: Ungültige Rolle '{args.role}'.", file=sys.stderr)
        sys.exit(1)

    cmd = CreateUserAccountCommand(
        acting_user_id=UserAccountId(user_id),
        username=args.username,
        password_hash=password_hash,
        role=role,
        employee_id=args.employee_id,
    )
    try:
        result = CreateUserAccountUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)

    print(f"Benutzerkonto angelegt (ID {result.user_id}).")
    if not args.password:
        print(f"Generiertes Passwort (einmalig sichtbar): {password}", file=sys.stderr)


def cmd_users_list(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rows = conn.execute(
        "SELECT id, username, role, active FROM user_accounts "
        "WHERE role != 'EMPLOYEE' ORDER BY role, username"
    ).fetchall()
    if not rows:
        print("Keine Benutzerkonten vorhanden.")
        return
    print(f"{'ID':>4}  {'Benutzername':20}  {'Rolle':10}  Status")
    print("-" * 52)
    for row in rows:
        status = "aktiv" if row["active"] else "inaktiv"
        print(f"{row['id']:>4}  {row['username']:20}  {row['role']:10}  {status}")


def cmd_users_deactivate(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    cmd = DeactivateUserAccountCommand(
        acting_user_id=UserAccountId(user_id),
        target_user_id=UserAccountId(args.deactivate_user_id),
    )
    try:
        DeactivateUserAccountUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Benutzerkonto {args.deactivate_user_id} deaktiviert.")


def cmd_users_reactivate(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    cmd = ReactivateUserAccountCommand(
        acting_user_id=UserAccountId(user_id),
        target_user_id=UserAccountId(args.reactivate_user_id),
    )
    try:
        ReactivateUserAccountUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Benutzerkonto {args.reactivate_user_id} reaktiviert.")


def cmd_users_change_role(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    try:
        new_role = UserRole(args.role.upper())
    except ValueError:
        print(f"Fehler: Ungültige Rolle '{args.role}'.", file=sys.stderr)
        sys.exit(1)

    cmd = ChangeUserRoleCommand(
        acting_user_id=UserAccountId(user_id),
        target_user_id=UserAccountId(args.target_user_id),
        new_role=new_role,
    )
    try:
        ChangeUserRoleUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)
    print(f"Rolle von Benutzerkonto {args.target_user_id} geändert.")


def cmd_users_bootstrap(
    conn: sqlite3.Connection, audit_conn: sqlite3.Connection, args: argparse.Namespace
) -> None:
    password = args.password or secrets.token_urlsafe(12)
    password_hash = _hash_password(password)

    cmd = BootstrapAdminCommand(username=args.username, password_hash=password_hash)
    try:
        result = BootstrapAdminUseCase(_make_uow(conn, audit_conn)).execute(cmd)
    except DomainError as exc:
        print(f"Fehler: {exc.message}", file=sys.stderr)
        sys.exit(1)

    print(f"Erstes Administratorkonto angelegt (ID {result.user_id}).")
    if not args.password:
        print(f"Generiertes Passwort (einmalig sichtbar): {password}", file=sys.stderr)


def register_subcommands(
    sub: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    users = sub.add_parser("users", help="Benutzerkonten verwalten (ADMIN/REVIEWER/TECH)")
    users_sub = users.add_subparsers(dest="users_cmd", required=True)

    # add
    add = users_sub.add_parser("add", help="Benutzerkonto anlegen")
    add.add_argument("--username", required=True, help="Benutzername (eindeutig)")
    add.add_argument(
        "--role",
        required=True,
        choices=["ADMIN", "REVIEWER", "TECH"],
        help="Rolle: ADMIN, REVIEWER oder TECH",
    )
    add.add_argument(
        "--employee-id", type=int, default=None, help="Verknüpfter Mitarbeiter (optional)"
    )
    add.add_argument(
        "--password",
        default=None,
        help="Passwort (wird gehasht gespeichert; leer lassen für automatisch generiertes)",
    )

    # list
    users_sub.add_parser("list", help="Alle Benutzerkonten anzeigen")

    # deactivate
    deact = users_sub.add_parser("deactivate", help="Benutzerkonto deaktivieren")
    deact.add_argument("--user-id", dest="deactivate_user_id", type=int, required=True)

    # reactivate
    react = users_sub.add_parser("reactivate", help="Benutzerkonto reaktivieren")
    react.add_argument("--user-id", dest="reactivate_user_id", type=int, required=True)

    # change-role
    change = users_sub.add_parser("change-role", help="Rolle eines Benutzerkontos ändern")
    change.add_argument("--user-id", dest="target_user_id", type=int, required=True)
    change.add_argument("--role", required=True, choices=["ADMIN", "REVIEWER", "TECH"])

    # bootstrap
    boot = users_sub.add_parser(
        "bootstrap",
        help="Erstes Administratorkonto anlegen (nur wenn kein Admin existiert)",
    )
    boot.add_argument("--username", required=True, help="Benutzername des ersten Administrators")
    boot.add_argument(
        "--password", default=None, help="Passwort (leer lassen für automatisch generiertes)"
    )
