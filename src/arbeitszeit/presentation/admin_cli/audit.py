"""Admin-CLI: Audit-Log-Abfragen (ADMIN/REVIEWER-Rolle)."""

__version__ = "1.0"

import argparse
import json
import sqlite3
from datetime import datetime, timedelta, timezone

from arbeitszeit.domain import audit_events
from arbeitszeit.presentation.admin_cli._auth import require_admin_or_reviewer


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
