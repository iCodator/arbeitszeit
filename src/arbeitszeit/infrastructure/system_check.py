"""Systemcheck — Pflichtenheft v3 §7.10.

Prüft fünf Bereiche und protokolliert das Ergebnis als SELFTEST_OK oder SELFTEST_FAIL
in system_events. Aufrufbar manuell und beim Systemstart.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import subprocess  # nosec B404
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from arbeitszeit.infrastructure.config_file import AppConfig
from arbeitszeit.infrastructure.db.connection import open_connection

_REQUIRED_CONFIG_KEYS = (
    "app.timezone",
    "booking.grace_seconds_after_numpad_select",
    "backup.nas_enabled",
    "backup.nas_path",
    # backup_dir, export_dir, log_dir sind in config.toml gewandert
)

_MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "migrations"
_TIMEDATECTL = "/usr/bin/timedatectl"


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class SystemCheckResult:
    checks: tuple[CheckResult, ...]

    @property
    def overall_ok(self) -> bool:
        return all(c.ok for c in self.checks)


def run_system_check(
    db_path: Path,
    *,
    numpad_path: Path | None = None,
    rfid_path: Path | None = None,
    app_config: AppConfig | None = None,
) -> SystemCheckResult:
    """Führt alle Systemprüfungen aus und schreibt das Ergebnis in system_events."""
    checks: list[CheckResult] = []

    db_result, conn = _check_db_access(db_path)
    checks.append(db_result)

    if conn is not None:
        try:
            checks.append(_check_config_keys(conn))
            checks.append(_check_nas(conn))
            checks.append(_check_fk_consistency(conn))
        finally:
            conn.close()

    checks.append(_check_config_file_paths(app_config))
    checks.append(_check_ntp())
    checks.append(_check_devices(numpad_path, rfid_path))

    result = SystemCheckResult(checks=tuple(checks))
    _write_event(db_path, result)
    return result


def _check_db_access(
    db_path: Path,
) -> tuple[CheckResult, sqlite3.Connection | None]:
    try:
        conn = open_connection(db_path)
    except Exception as exc:
        return CheckResult(name="db_access", ok=False, detail=str(exc)), None

    try:
        applied = {
            row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
        }
    except sqlite3.OperationalError as exc:
        conn.close()
        return CheckResult(name="db_access", ok=False, detail=str(exc)), None

    expected = {
        path.name.split("_", maxsplit=1)[0]
        for path in sorted(_MIGRATIONS_DIR.glob("[0-9][0-9][0-9][0-9]_*.sql"))
    }
    missing = expected - applied
    if missing:
        conn.close()
        return (
            CheckResult(
                name="db_access",
                ok=False,
                detail=f"Fehlende Migrationen: {sorted(missing)}",
            ),
            None,
        )

    return CheckResult(name="db_access", ok=True, detail="OK"), conn


def _check_config_keys(conn: sqlite3.Connection) -> CheckResult:
    missing = [
        key
        for key in _REQUIRED_CONFIG_KEYS
        if conn.execute(
            "SELECT 1 FROM system_config WHERE config_key = ? LIMIT 1", (key,)
        ).fetchone()
        is None
    ]
    if missing:
        return CheckResult(
            name="config_keys",
            ok=False,
            detail=f"Fehlende Konfigurationsschlüssel: {missing}",
        )
    return CheckResult(name="config_keys", ok=True, detail="OK")


def _check_nas(conn: sqlite3.Connection) -> CheckResult:
    # -------------------------------------------------------------------------
    # Designentscheidung: Kein aktiver Netzwerk-Erreichbarkeitstest des NAS.
    #
    # Dieser Check prüft ausschließlich:
    #   (a) Ist backup.nas_enabled in system_config auf true gesetzt?
    #   (b) Ist backup.nas_path gesetzt und nicht leer?
    #   (c) Existiert der konfigurierte Pfad im Dateisystem (Path.exists())?
    #   (d) Ist der Pfad schreibbar (os.access(..., os.W_OK))?
    #
    # Es wird KEIN Netzwerk-Ping, TCP-Verbindungstest oder DNS-Auflösung
    # durchgeführt. Das ist bewusst:
    #
    #   1. Das NAS wird als Dateisystem-Mount eingebunden (z.B. /mnt/nas/...).
    #      Path.exists() + os.access() testen den Mount-Punkt direkt – ist der
    #      Mount aktiv und schreibbar, ist das NAS erreichbar. Kein separater
    #      Netzwerktest notwendig.
    #
    #   2. Ein Ping/TCP-Test würde bei vorübergehend nicht erreichbarem NAS
    #      (Neustart, Wartung) SELFTEST_FAIL erzeugen, obwohl das System voll
    #      funktionsfähig ist. Das wäre ein irreführendes Signal.
    #
    #   3. Netzwerkerreichbarkeit (DNS, SMB/NFS-Port) ist Aufgabe des
    #      Betriebssystems und der systemd-Mount-Unit, nicht dieses Checks.
    #
    # Ausführliche Begründung: docs/SECURITY.md, Abschnitt 4.
    # -------------------------------------------------------------------------
    row = conn.execute(
        "SELECT config_value_json FROM system_config "
        "WHERE config_key = 'backup.nas_enabled' ORDER BY version DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return CheckResult(name="nas_reachability", ok=True, detail="NAS-Backup nicht konfiguriert")

    try:
        nas_enabled = json.loads(row[0])
    except (ValueError, TypeError):
        nas_enabled = False

    if not nas_enabled:
        return CheckResult(name="nas_reachability", ok=True, detail="NAS-Backup deaktiviert")

    row = conn.execute(
        "SELECT config_value_json FROM system_config "
        "WHERE config_key = 'backup.nas_path' ORDER BY version DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return CheckResult(
            name="nas_reachability",
            ok=False,
            detail="backup.nas_enabled=true, aber backup.nas_path nicht gesetzt",
        )

    try:
        nas_path_str = json.loads(row[0])
    except (ValueError, TypeError):
        nas_path_str = None

    if not nas_path_str:
        return CheckResult(
            name="nas_reachability",
            ok=False,
            detail="backup.nas_path ist leer oder null",
        )

    nas_path = Path(nas_path_str)
    if not nas_path.exists():
        return CheckResult(
            name="nas_reachability",
            ok=False,
            detail=f"NAS-Pfad nicht erreichbar: {nas_path}",
        )
    if not os.access(nas_path, os.W_OK):
        return CheckResult(
            name="nas_reachability",
            ok=False,
            detail=f"NAS-Pfad nicht schreibbar: {nas_path}",
        )
    return CheckResult(name="nas_reachability", ok=True, detail=f"OK ({nas_path})")


def _check_fk_consistency(conn: sqlite3.Connection) -> CheckResult:
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        return CheckResult(
            name="fk_consistency",
            ok=False,
            detail=f"{len(violations)} verwaiste Fremdschlüssel-Referenz(en)",
        )
    return CheckResult(name="fk_consistency", ok=True, detail="OK")


def _check_config_file_paths(app_config: AppConfig | None) -> CheckResult:
    if app_config is None:
        return CheckResult(
            name="config_file_paths",
            ok=True,
            detail="Keine AppConfig übergeben, übersprungen",
        )
    issues = [
        f"{label}: {path}"
        for label, path in (
            ("backup_dir", app_config.backup.backup_dir),
            ("export_dir", app_config.backup.export_dir),
        )
        if path is not None and not path.exists()
    ]
    if issues:
        return CheckResult(
            name="config_file_paths",
            ok=False,
            detail=f"Konfigurierte Pfade nicht vorhanden: {'; '.join(issues)}",
        )
    return CheckResult(name="config_file_paths", ok=True, detail="OK")


def _check_ntp() -> CheckResult:
    """Prüft via timedatectl, ob NTP aktiv und synchronisiert ist (§9.3)."""
    try:
        proc = subprocess.run(  # nosec B603 — absoluter Pfad (_TIMEDATECTL), feste Argumente, kein shell=True
            [_TIMEDATECTL, "show", "--property=NTP", "--property=NTPSynchronized", "--no-pager"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        props = dict(
            line.split("=", 1)
            for line in proc.stdout.splitlines()
            if "=" in line
        )
        ntp_active = props.get("NTP", "no").lower() == "yes"
        ntp_synced = props.get("NTPSynchronized", "no").lower() == "yes"
        if not ntp_active:
            return CheckResult(name="ntp_sync", ok=False, detail="NTP nicht aktiv (NTP=no)")
        if not ntp_synced:
            return CheckResult(
                name="ntp_sync", ok=False,
                detail="NTP aktiv, aber nicht synchronisiert (NTPSynchronized=no)"
            )
        return CheckResult(name="ntp_sync", ok=True, detail="NTP aktiv und synchronisiert")
    except FileNotFoundError:
        return CheckResult(
            name="ntp_sync", ok=False,
            detail="timedatectl nicht gefunden — NTP-Status unbekannt"
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            name="ntp_sync", ok=False,
            detail="timedatectl Timeout — NTP-Status unbekannt"
        )
    except Exception as exc:
        return CheckResult(name="ntp_sync", ok=False, detail=f"NTP-Prüfung fehlgeschlagen: {exc}")


def _check_devices(
    numpad_path: Path | None,
    rfid_path: Path | None,
) -> CheckResult:
    if numpad_path is None and rfid_path is None:
        return CheckResult(
            name="device_availability",
            ok=True,
            detail="Keine Gerätepfade angegeben, übersprungen",
        )
    unavailable = [
        f"{label}: {path}"
        for label, path in (("Numpad", numpad_path), ("RFID", rfid_path))
        if path is not None and (not path.exists() or not os.access(path, os.R_OK))
    ]
    if unavailable:
        return CheckResult(
            name="device_availability",
            ok=False,
            detail=f"Nicht erreichbar: {', '.join(unavailable)}",
        )
    return CheckResult(name="device_availability", ok=True, detail="OK")


def _write_event(db_path: Path, result: SystemCheckResult) -> None:
    event_type = "SELFTEST_OK" if result.overall_ok else "SELFTEST_FAIL"
    severity = "INFO" if result.overall_ok else "WARN"
    details = {"checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in result.checks]}
    try:
        conn = open_connection(db_path)
        try:
            conn.execute(
                "INSERT INTO system_events "
                "(event_type, source, severity, event_at, details_json) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    event_type,
                    "system_check",
                    severity,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(details),
                ),
            )
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        logging.warning("system_check._write_event fehlgeschlagen: %s", exc, exc_info=True)
