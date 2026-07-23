"""Admin-CLI: Audit-Log-Abfragen (ADMIN/REVIEWER-Rolle)."""

__version__ = "1.1"

import argparse
import hmac
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

from arbeitszeit.domain import audit_events
from arbeitszeit.infrastructure.db.repositories.audit_log import (
    compute_audit_chain_hash,
)
from arbeitszeit.presentation.admin_cli._auth import require_admin_or_reviewer

_GENESIS_HASH = "0" * 64


def _positive_int(value: str) -> int:
    try:
        n = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} ist keine gültige Ganzzahl") from exc
    if n <= 0:
        raise argparse.ArgumentTypeError(f"--days muss größer als 0 sein, got {n}")
    return n


def cmd_audit_open_shifts(
    conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
) -> None:
    require_admin_or_reviewer(conn, user_id)
    days: int = args.days
    from_dt = datetime.now(timezone.utc) - timedelta(days=days)

    rows = conn.execute(
        """
        SELECT
            a.event_at,
            a.employee_id,
            e.first_name,
            e.last_name,
            a.details_json
        FROM audit_log a
        LEFT JOIN employees e ON e.id = a.employee_id
        WHERE a.event_type = ?
          AND a.event_at >= ?
        ORDER BY a.event_at ASC
        """,
        (audit_events.OPEN_SHIFT_PREVIOUS_DAY_DETECTED, from_dt.isoformat()),
    ).fetchall()

    print(f"Offene Vortagsschichten — letzte {days} Tag(e):")
    print()

    if not rows:
        print(f"Keine offenen Vortagsschichten in den letzten {days} Tag(en) gefunden.")
        return

    print(
        f"  {'Erkannt am':16}  {'Mitarbeiter':25}  "
        f"{'Vortag':10}  {'Letzter Typ':11}  {'Letzte Buchung':16}"
    )
    print(f"  {'-' * 16}  {'-' * 25}  {'-' * 10}  {'-' * 11}  {'-' * 16}")

    for row in rows:
        details = json.loads(row["details_json"])
        erkannt = datetime.fromisoformat(row["event_at"]).astimezone()
        erkannt_str = erkannt.strftime("%d.%m.%Y %H:%M")

        if row["first_name"] and row["last_name"]:
            name = f"{row['last_name']}, {row['first_name']}"
        else:
            name = f"ID {row['employee_id']}"

        vortag = details.get("previous_day_date", "?")
        letzter_typ = details.get("last_known_booking_type", "?")
        letzte_buchung_raw = details.get("last_known_booking_at", "")
        if letzte_buchung_raw:
            letzte_buchung_str = (
                datetime.fromisoformat(letzte_buchung_raw).astimezone().strftime("%d.%m.%Y %H:%M")
            )
        else:
            letzte_buchung_str = "?"

        print(
            f"  {erkannt_str:16}  {name:25}  "
            f"{vortag:10}  {letzter_typ:11}  {letzte_buchung_str:16}"
        )

    print()
    print(f"{len(rows)} offene Vortagsschicht(en) in den letzten {days} Tag(en).")


def cmd_audit_verify_chain(
    conn: sqlite3.Connection,
    args: argparse.Namespace,
    user_id: int,
) -> None:
    require_admin_or_reviewer(conn, user_id)

    key_str = os.environ.get("AUDIT_HMAC_KEY", "")
    if not key_str:
        print(
            "FEHLER: AUDIT_HMAC_KEY nicht gesetzt — Kettenprüfung nicht möglich.",
            file=sys.stderr,
        )
        sys.exit(1)

    key = key_str.encode("utf-8")

    rows = conn.execute(
        "SELECT id, event_type, event_at, employee_id, details_json, chain_hash "
        "FROM audit_log ORDER BY id ASC"
    ).fetchall()

    prev_hash = _GENESIS_HASH
    verified = 0
    skipped = 0
    broken: list[int] = []

    for row in rows:
        if row["chain_hash"] is None:
            skipped += 1
            continue

        expected = compute_audit_chain_hash(
            event_type=row["event_type"],
            event_at_iso=row["event_at"],
            employee_id=row["employee_id"],
            details_json=row["details_json"],
            prev_hash=prev_hash,
            key=key,
        )

        if hmac.compare_digest(expected, row["chain_hash"]):
            verified += 1
        else:
            broken.append(int(row["id"]))

        prev_hash = row["chain_hash"]

    if skipped:
        print(f"Hinweis: {skipped} Eintrag(-einträge) ohne HMAC übersprungen.")

    if not broken:
        print(f"OK: {verified} Audit-Eintrag(-einträge) erfolgreich verifiziert.")
        return

    print(
        f"FEHLER: {len(broken)} Eintrag(-einträge) mit ungültigem Kettenhash: "
        f"IDs {broken}",
        file=sys.stderr,
    )
    sys.exit(1)


def register_subcommands(
    sub: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    audit = sub.add_parser("audit", help="Audit-Log-Abfragen")
    asub = audit.add_subparsers(dest="audit_cmd", required=True)

    os_cmd = asub.add_parser(
        "open-shifts",
        help="Offene Vortagsschichten aus dem Audit-Log anzeigen",
        description=(
            "Listet alle erkannten offenen Vortagsschichten im gewählten Zeitraum auf. "
            "Eine offene Vortagsschicht liegt vor, wenn ein Mitarbeiter eine Buchung "
            "als erste Buchung des Tages auslöst, obwohl die Schicht des Vortags ohne "
            "Gehen-Buchung endete. Diese Einträge erfordern manuelle Nachbearbeitung."
        ),
    )
    os_cmd.add_argument(
        "--days",
        type=_positive_int,
        default=30,
        metavar="N",
        help="Anzahl Tage rückwirkend (Standard: 30)",
    )

    asub.add_parser(
        "verify-chain",
        help="HMAC-Kette des Audit-Logs verifizieren",
        description=(
            "Liest alle Audit-Log-Einträge in ID-Reihenfolge und prüft, ob die "
            "HMAC-SHA256-Kettenhashes konsistent sind. Einträge ohne chain_hash "
            "(vor Aktivierung des HMAC-Schutzes) werden übersprungen. "
            "Benötigt die Umgebungsvariable AUDIT_HMAC_KEY."
        ),
    )
