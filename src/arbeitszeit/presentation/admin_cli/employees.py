"""Admin-CLI: Mitarbeiter- und Kartenverwaltung (direktes SQL, ADMIN-Rolle).

Schreibende Operationen sind ausschließlich Benutzern mit ADMIN-Rolle erlaubt.
Lesende Operationen (list) sind ohne Rolleneinschränkung nutzbar.
"""

import argparse
import json
import sqlite3
import sys
from datetime import date, datetime, timezone


def _require_admin(conn: sqlite3.Connection, user_id: int) -> None:
    row = conn.execute("SELECT role, active FROM user_accounts WHERE id = ?", (user_id,)).fetchone()
    if row is None or not row["active"] or row["role"] != "ADMIN":
        print("Fehler: Zugriff verweigert. Aktion erfordert ADMIN-Rolle.", file=sys.stderr)
        sys.exit(1)


def _audit(
    conn: sqlite3.Connection,
    event_type: str,
    object_type: str,
    object_id: int,
    user_id: int,
    employee_id: int | None = None,
    details: dict[str, object] | None = None,
) -> None:
    conn.execute(
        "INSERT INTO audit_log "
        "(event_type, object_type, object_id, user_id, employee_id, event_at, details_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            event_type,
            object_type,
            object_id,
            user_id,
            employee_id,
            datetime.now(timezone.utc).isoformat(),
            json.dumps(details or {}, ensure_ascii=False, sort_keys=True),
        ),
    )


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


def cmd_employees_add(conn: sqlite3.Connection, args: argparse.Namespace, user_id: int) -> None:
    _require_admin(conn, user_id)
    now = datetime.now(timezone.utc).isoformat()
    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES (?, ?, ?, 1, ?, ?) RETURNING id",
            (args.personnel_no, args.first_name, args.last_name, now, now),
        ).fetchone()
        employee_id = row["id"]
        _audit(
            conn,
            "EMPLOYEE_CREATED",
            "employees",
            employee_id,
            user_id,
            employee_id,
            {
                "personnel_no": args.personnel_no,
                "first_name": args.first_name,
                "last_name": args.last_name,
            },
        )
        conn.execute("COMMIT")
    except sqlite3.IntegrityError as exc:
        conn.execute("ROLLBACK")
        print(f"Fehler: Personalnummer bereits vergeben. ({exc})", file=sys.stderr)
        sys.exit(1)
    print(f"Mitarbeiter angelegt (ID {employee_id}).")


def cmd_employees_deactivate(
    conn: sqlite3.Connection, args: argparse.Namespace, user_id: int
) -> None:
    _require_admin(conn, user_id)
    conn.execute("BEGIN")
    row = conn.execute("SELECT id, active FROM employees WHERE id = ?", (args.id,)).fetchone()
    if row is None:
        conn.execute("ROLLBACK")
        print(f"Fehler: Mitarbeiter {args.id} nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE employees SET active = 0, updated_at = ? WHERE id = ?",
        (now, args.id),
    )
    _audit(conn, "EMPLOYEE_DEACTIVATED", "employees", args.id, user_id, args.id, {})
    conn.execute("COMMIT")
    print(f"Mitarbeiter {args.id} deaktiviert.")


def cmd_cards_assign(conn: sqlite3.Connection, args: argparse.Namespace, user_id: int) -> None:
    _require_admin(conn, user_id)
    emp = conn.execute(
        "SELECT id, active FROM employees WHERE id = ?", (args.employee_id,)
    ).fetchone()
    if emp is None:
        print(f"Fehler: Mitarbeiter {args.employee_id} nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    now = datetime.now(timezone.utc).isoformat()
    today = date.today().isoformat()
    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "INSERT INTO rfid_cards "
            "(uid_hash, employee_id, status, valid_from, created_at) "
            "VALUES (?, ?, 'ACTIVE', ?, ?) RETURNING id",
            (args.uid_hash, args.employee_id, today, now),
        ).fetchone()
        card_id = row["id"]
        _audit(
            conn,
            "CARD_ASSIGNED",
            "rfid_cards",
            card_id,
            user_id,
            args.employee_id,
            {
                "uid_hash": args.uid_hash,
                "employee_id": args.employee_id,
            },
        )
        conn.execute("COMMIT")
    except sqlite3.IntegrityError as exc:
        conn.execute("ROLLBACK")
        print(f"Fehler: UID-Hash bereits vergeben. ({exc})", file=sys.stderr)
        sys.exit(1)
    print(f"Karte zugewiesen (ID {card_id}).")


def cmd_cards_replace(conn: sqlite3.Connection, args: argparse.Namespace, user_id: int) -> None:
    _require_admin(conn, user_id)
    old_card = conn.execute(
        "SELECT id, employee_id, status FROM rfid_cards WHERE id = ?",
        (args.old_card_id,),
    ).fetchone()
    if old_card is None:
        print(f"Fehler: Karte {args.old_card_id} nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    now = datetime.now(timezone.utc).isoformat()
    today = date.today().isoformat()
    try:
        conn.execute("BEGIN")
        new_row = conn.execute(
            "INSERT INTO rfid_cards "
            "(uid_hash, employee_id, status, valid_from, created_at) "
            "VALUES (?, ?, 'ACTIVE', ?, ?) RETURNING id",
            (args.uid_hash, old_card["employee_id"], today, now),
        ).fetchone()
        new_card_id = new_row["id"]
        conn.execute(
            "UPDATE rfid_cards SET status = 'REPLACED', valid_until = ?, "
            "replaced_by_card_id = ? WHERE id = ?",
            (today, new_card_id, args.old_card_id),
        )
        _audit(
            conn,
            "CARD_REPLACED",
            "rfid_cards",
            new_card_id,
            user_id,
            old_card["employee_id"],
            {
                "old_card_id": args.old_card_id,
                "new_card_id": new_card_id,
                "uid_hash": args.uid_hash,
            },
        )
        conn.execute("COMMIT")
    except sqlite3.IntegrityError as exc:
        conn.execute("ROLLBACK")
        print(f"Fehler: UID-Hash bereits vergeben. ({exc})", file=sys.stderr)
        sys.exit(1)
    print(f"Karte ersetzt: alt={args.old_card_id}, neu={new_card_id}.")


def cmd_cards_deactivate(conn: sqlite3.Connection, args: argparse.Namespace, user_id: int) -> None:
    _require_admin(conn, user_id)
    card = conn.execute(
        "SELECT id, employee_id FROM rfid_cards WHERE id = ?", (args.id,)
    ).fetchone()
    if card is None:
        print(f"Fehler: Karte {args.id} nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    conn.execute("BEGIN")
    conn.execute("UPDATE rfid_cards SET status = 'INACTIVE' WHERE id = ?", (args.id,))
    _audit(
        conn,
        "CARD_DEACTIVATED",
        "rfid_cards",
        args.id,
        user_id,
        card["employee_id"],
        {},
    )
    conn.execute("COMMIT")
    print(f"Karte {args.id} deaktiviert.")


def register_subcommands(
    sub: argparse._SubParsersAction,  # type: ignore[type-arg]
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
    cards = sub.add_parser("cards", help="Kartenverwaltung")
    cards_sub = cards.add_subparsers(dest="cards_cmd", required=True)

    assign = cards_sub.add_parser("assign", help="Karte einem Mitarbeiter zuweisen")
    assign.add_argument("--employee-id", required=True, type=int)
    assign.add_argument("--uid-hash", required=True)

    replace = cards_sub.add_parser("replace", help="Karte ersetzen")
    replace.add_argument("--old-card-id", required=True, type=int)
    replace.add_argument("--uid-hash", required=True)

    deact_card = cards_sub.add_parser("deactivate", help="Karte deaktivieren")
    deact_card.add_argument("id", type=int)
