"""CLI-seitige Rollenprüfung für lesende Operationen ohne Use Case.

Schreibende Operationen delegieren die Rollenprüfung an Use Cases in der
Anwendungsschicht. Lesende Operationen (reports, schedule show, system) haben
keine Use Cases und prüfen die Rolle deshalb hier auf CLI-Ebene.
"""

import sqlite3
import sys


def require_admin_or_reviewer(conn: sqlite3.Connection, user_id: int) -> None:
    row = conn.execute(
        "SELECT role, active FROM user_accounts WHERE id = ?", (user_id,)
    ).fetchone()
    if row is None or not row["active"] or row["role"] not in ("ADMIN", "REVIEWER"):
        print(
            "Fehler: Zugriff verweigert. Aktion erfordert ADMIN- oder REVIEWER-Rolle.",
            file=sys.stderr,
        )
        sys.exit(1)


def require_admin_or_tech(conn: sqlite3.Connection, user_id: int) -> None:
    row = conn.execute(
        "SELECT role, active FROM user_accounts WHERE id = ?", (user_id,)
    ).fetchone()
    if row is None or not row["active"] or row["role"] not in ("ADMIN", "TECH"):
        print(
            "Fehler: Zugriff verweigert. Aktion erfordert ADMIN- oder TECH-Rolle.",
            file=sys.stderr,
        )
        sys.exit(1)
