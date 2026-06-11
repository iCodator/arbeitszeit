"""Admin-CLI: Benutzerkontenverwaltung für ADMIN, REVIEWER und TECH.

Schreibende Operationen erfordern ADMIN-Rolle.
Lesende Operationen (list) sind ohne Rolleneinschränkung nutzbar.
"""
import argparse
import binascii
import hashlib
import json
import os
import secrets
import sqlite3
import sys
from datetime import datetime, timezone

from arbeitszeit.domain import audit_events

_ALLOWED_ROLES = ("ADMIN", "REVIEWER", "TECH")


def _require_admin(conn: sqlite3.Connection, user_id: int) -> None:
    row = conn.execute(
        "SELECT role, active FROM user_accounts WHERE id = ?", (user_id,)
    ).fetchone()
    if row is None or not row["active"] or row["role"] != "ADMIN":
        print("Fehler: Zugriff verweigert. Aktion erfordert ADMIN-Rolle.", file=sys.stderr)
        sys.exit(1)


def _audit(
    conn: sqlite3.Connection,
    event_type: str,
    object_id: int,
    user_id: int,
    details: dict | None = None,
) -> None:
    conn.execute(
        "INSERT INTO audit_log "
        "(event_type, object_type, object_id, user_id, employee_id, event_at, details_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            event_type,
            "user_accounts",
            object_id,
            user_id,
            None,
            datetime.now(timezone.utc).isoformat(),
            json.dumps(details or {}, ensure_ascii=False, sort_keys=True),
        ),
    )


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return binascii.hexlify(salt).decode() + ":" + binascii.hexlify(dk).decode()


def cmd_users_add(conn: sqlite3.Connection, args: argparse.Namespace, user_id: int) -> None:
    _require_admin(conn, user_id)
    role = args.role.upper()
    if role not in _ALLOWED_ROLES:
        print(
            f"Fehler: Ungültige Rolle '{role}'. Erlaubt: {', '.join(_ALLOWED_ROLES)}",
            file=sys.stderr,
        )
        sys.exit(1)

    password = args.password or secrets.token_urlsafe(12)
    password_hash = _hash_password(password)
    now = datetime.now(timezone.utc).isoformat()

    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "INSERT INTO user_accounts "
            "(username, password_hash, role, employee_id, active, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 1, ?, ?) RETURNING id",
            (args.username, password_hash, role, args.employee_id, now, now),
        ).fetchone()
        new_id = row["id"]
        _audit(
            conn,
            audit_events.USER_ACCOUNT_CREATED,
            new_id,
            user_id,
            {"username": args.username, "role": role},
        )
        conn.execute("COMMIT")
    except sqlite3.IntegrityError as exc:
        conn.execute("ROLLBACK")
        print(f"Fehler: Benutzername bereits vergeben. ({exc})", file=sys.stderr)
        sys.exit(1)

    print(f"Benutzerkonto angelegt (ID {new_id}).")
    if not args.password:
        print(f"Generiertes Passwort (einmalig sichtbar): {password}")


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
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin(conn, user_id)
    row = conn.execute(
        "SELECT id, username, active FROM user_accounts WHERE id = ?",
        (args.deactivate_user_id,),
    ).fetchone()
    if row is None:
        print(f"Fehler: Benutzerkonto {args.deactivate_user_id} nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    if not row["active"]:
        print(f"Hinweis: Benutzerkonto '{row['username']}' ist bereits inaktiv.")
        return
    conn.execute("BEGIN")
    conn.execute(
        "UPDATE user_accounts SET active = 0, updated_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), args.deactivate_user_id),
    )
    _audit(
        conn,
        audit_events.USER_ACCOUNT_DEACTIVATED,
        args.deactivate_user_id,
        user_id,
        {"username": row["username"]},
    )
    conn.execute("COMMIT")
    print(f"Benutzerkonto '{row['username']}' deaktiviert.")


def cmd_users_reactivate(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin(conn, user_id)
    row = conn.execute(
        "SELECT id, username, active FROM user_accounts WHERE id = ?",
        (args.reactivate_user_id,),
    ).fetchone()
    if row is None:
        print(f"Fehler: Benutzerkonto {args.reactivate_user_id} nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    if row["active"]:
        print(f"Hinweis: Benutzerkonto '{row['username']}' ist bereits aktiv.")
        return
    conn.execute("BEGIN")
    conn.execute(
        "UPDATE user_accounts SET active = 1, updated_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), args.reactivate_user_id),
    )
    _audit(
        conn,
        audit_events.USER_ACCOUNT_REACTIVATED,
        args.reactivate_user_id,
        user_id,
        {"username": row["username"]},
    )
    conn.execute("COMMIT")
    print(f"Benutzerkonto '{row['username']}' reaktiviert.")


def cmd_users_change_role(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin(conn, user_id)
    row = conn.execute(
        "SELECT id, username, role FROM user_accounts WHERE id = ?",
        (args.target_user_id,),
    ).fetchone()
    if row is None:
        print(f"Fehler: Benutzerkonto {args.target_user_id} nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    new_role = args.role.upper()
    if new_role not in _ALLOWED_ROLES:
        print(
            f"Fehler: Ungültige Rolle '{new_role}'. Erlaubt: {', '.join(_ALLOWED_ROLES)}",
            file=sys.stderr,
        )
        sys.exit(1)
    old_role = row["role"]
    conn.execute("BEGIN")
    conn.execute(
        "UPDATE user_accounts SET role = ?, updated_at = ? WHERE id = ?",
        (new_role, datetime.now(timezone.utc).isoformat(), args.target_user_id),
    )
    _audit(
        conn,
        audit_events.USER_ACCOUNT_ROLE_CHANGED,
        args.target_user_id,
        user_id,
        {"username": row["username"], "old_role": old_role, "new_role": new_role},
    )
    conn.execute("COMMIT")
    print(f"Rolle von '{row['username']}' geändert: {old_role} → {new_role}.")


def cmd_users_bootstrap(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    count = conn.execute(
        "SELECT COUNT(*) FROM user_accounts WHERE role = 'ADMIN' AND active = 1"
    ).fetchone()[0]
    if count > 0:
        print(
            "Fehler: Es existiert bereits ein aktives Administratorkonto. "
            "Bootstrap nicht möglich.",
            file=sys.stderr,
        )
        sys.exit(1)

    password = args.password or secrets.token_urlsafe(12)
    password_hash = _hash_password(password)
    now = datetime.now(timezone.utc).isoformat()

    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "INSERT INTO user_accounts "
            "(username, password_hash, role, employee_id, active, created_at, updated_at) "
            "VALUES (?, ?, 'ADMIN', NULL, 1, ?, ?) RETURNING id",
            (args.username, password_hash, now, now),
        ).fetchone()
        new_id = row["id"]
        _audit(
            conn,
            audit_events.USER_ACCOUNT_CREATED,
            new_id,
            new_id,
            {"username": args.username, "role": "ADMIN", "bootstrap": True},
        )
        conn.execute("COMMIT")
    except sqlite3.IntegrityError as exc:
        conn.execute("ROLLBACK")
        print(f"Fehler: Benutzername bereits vergeben. ({exc})", file=sys.stderr)
        sys.exit(1)

    print(f"Erstes Administratorkonto angelegt (ID {new_id}).")
    if not args.password:
        print(f"Generiertes Passwort (einmalig sichtbar): {password}")


def register_subcommands(sub: argparse._SubParsersAction) -> None:
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
    add.add_argument("--employee-id", type=int, default=None, help="Verknüpfter Mitarbeiter (optional)")
    add.add_argument("--password", default=None, help="Passwort (wird gehasht gespeichert; leer lassen für automatisch generiertes)")

    # list
    users_sub.add_parser("list", help="Alle Benutzerkonten anzeigen")

    # deactivate
    deact = users_sub.add_parser("deactivate", help="Benutzerkonto deaktivieren")
    deact.add_argument("--user-id", dest="deactivate_user_id", type=int, required=True, help="ID des zu deaktivierenden Kontos")

    # reactivate
    react = users_sub.add_parser("reactivate", help="Benutzerkonto reaktivieren")
    react.add_argument("--user-id", dest="reactivate_user_id", type=int, required=True, help="ID des zu reaktivierenden Kontos")

    # change-role
    change = users_sub.add_parser("change-role", help="Rolle eines Benutzerkontos ändern")
    change.add_argument("--user-id", dest="target_user_id", type=int, required=True, help="ID des Benutzerkontos")
    change.add_argument("--role", required=True, choices=["ADMIN", "REVIEWER", "TECH"], help="Neue Rolle")

    # bootstrap
    boot = users_sub.add_parser("bootstrap", help="Erstes Administratorkonto anlegen (nur wenn kein Admin existiert)")
    boot.add_argument("--username", required=True, help="Benutzername des ersten Administrators")
    boot.add_argument("--password", default=None, help="Passwort (leer lassen für automatisch generiertes)")
