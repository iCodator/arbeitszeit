"""Admin-CLI: Admin-RFID-Kartenverwaltung.

Admin-RFID-Karten ermöglichen es, am Terminal administrative Aktionen
(Stop, Neustart) durch Kartenscan auszulösen, ohne SSH-Zugang.
"""

__version__ = "1.0"

import argparse
import sqlite3
import sys

from arbeitszeit.domain.value_objects import AdminRfidCardId
from arbeitszeit.infrastructure.config_file import AppConfig
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork
from arbeitszeit.infrastructure.hardware import EmptyUidError, HardwareTimeoutError
from arbeitszeit.infrastructure.hardware.evdev_reader import (
    DeviceNotFoundError,
    resolve_evdev_device,
    scan_rfid_uid_hash,
)


def _validate_uid_source(args: argparse.Namespace, rfid_device: str | None) -> None:
    if args.uid_hash:
        if args.scan:
            print("Fehler: --uid-hash und --scan schließen sich aus.", file=sys.stderr)
            sys.exit(1)
        return
    if not args.scan:
        print("Fehler: --uid-hash oder --scan ist erforderlich.", file=sys.stderr)
        sys.exit(1)
    if not rfid_device:
        print(
            "Fehler: --scan erfordert --rfid oder [terminal] rfid in config.toml.",
            file=sys.stderr,
        )
        sys.exit(1)


def _resolve_uid_hash(args: argparse.Namespace, rfid_device: str | None) -> str:
    if not args.scan:
        return args.uid_hash  # type: ignore[no-any-return]
    if rfid_device is None:
        print(
            "Fehler: --scan erfordert --rfid oder [terminal] rfid in config.toml.",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        rfid_path = resolve_evdev_device(rfid_device)
    except DeviceNotFoundError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
    print("Bitte Admin-Karte an den RFID-Reader halten …")
    try:
        uid_hash = scan_rfid_uid_hash(rfid_path)
    except HardwareTimeoutError as exc:
        print(f"Fehler: Timeout – {exc}", file=sys.stderr)
        sys.exit(1)
    except (EmptyUidError, OSError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
    return uid_hash


def cmd_admin_cards_assign(
    conn: sqlite3.Connection,
    audit_conn: sqlite3.Connection,
    args: argparse.Namespace,
    app_config: AppConfig | None = None,
) -> None:
    rfid_device = getattr(args, "rfid", None) or (app_config.terminal.rfid if app_config else None)
    _validate_uid_source(args, rfid_device)
    uid_hash = _resolve_uid_hash(args, rfid_device)
    label: str | None = getattr(args, "label", None) or None
    try:
        with SQLiteUnitOfWork(conn, audit_conn) as uow:
            card = uow.admin_rfid_card_repo.add(uid_hash, label)
            uow.commit()
    except sqlite3.IntegrityError:
        print("Fehler: UID-Hash bereits als Admin-Karte registriert.", file=sys.stderr)
        sys.exit(1)
    print(f"Admin-Karte angelegt (ID {card.id}).")


def cmd_admin_cards_deactivate(
    conn: sqlite3.Connection,
    audit_conn: sqlite3.Connection,
    args: argparse.Namespace,
) -> None:
    exists = conn.execute(
        "SELECT 1 FROM admin_rfid_cards WHERE id = ?", (args.id,)
    ).fetchone()
    if exists is None:
        print(f"Fehler: Admin-Karte {args.id} nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    with SQLiteUnitOfWork(conn, audit_conn) as uow:
        uow.admin_rfid_card_repo.deactivate(AdminRfidCardId(args.id))
        uow.commit()
    print(f"Admin-Karte {args.id} deaktiviert.")


def cmd_admin_cards_list(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT id, uid_hash, label, active, created_at "
        "FROM admin_rfid_cards ORDER BY id"
    ).fetchall()
    if not rows:
        print("Keine Admin-RFID-Karten vorhanden.")
        return
    print(f"{'ID':>4}  {'UID-Hash (Anfang)':18}  {'Label':20}  {'Status':8}  Angelegt")
    print("-" * 80)
    for row in rows:
        status = "aktiv" if row["active"] else "inaktiv"
        label = row["label"] or "–"
        uid_short = row["uid_hash"][:16]
        print(f"{row['id']:>4}  {uid_short:18}  {label:20}  {status:8}  {row['created_at'][:19]}")


def register_subcommands(
    sub: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    ac = sub.add_parser("admin-cards", help="Admin-RFID-Kartenverwaltung")
    ac_sub = ac.add_subparsers(dest="admin-cards_cmd", required=True)

    assign = ac_sub.add_parser("assign", help="Admin-RFID-Karte anlegen")
    assign.add_argument("--label", help="Bezeichnung der Karte (optional)")
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

    deact = ac_sub.add_parser("deactivate", help="Admin-RFID-Karte deaktivieren")
    deact.add_argument("id", type=int)

    ac_sub.add_parser("list", help="Alle Admin-RFID-Karten auflisten")
