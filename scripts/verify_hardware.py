#!/usr/bin/env python3
"""Interaktiver Hardware-Smoke-Test für den RFID-Reader.

Prüft in zwei Stufen:
  1. Gerätedatei erreichbar und lesbar
  2. RFID-Reader: Wartet auf Karten-Scan (UID-Lesung bis Enter)

Wird typischerweise einmalig bei Erstinbetriebnahme oder nach Hardware-Tausch
aufgerufen, bevor der Terminal-UI-Dienst gestartet wird.

Voraussetzungen:
  - Linux mit evdev-Kernelmodul
  - python-evdev installiert (pip install evdev)
  - Lesezugriff auf /dev/input/event* (Gruppe 'input' oder root)
  - Gerätepfad via --rfid oder interaktive Auswahl

Verwendung:
    python scripts/verify_hardware.py --rfid /dev/input/event4
    python scripts/verify_hardware.py                          # interaktive Geräteauswahl
    python scripts/verify_hardware.py --list                   # nur Geräteliste anzeigen
"""

from __future__ import annotations

__version__ = "1.2"

import argparse
import os
import select
import sys
import time
from pathlib import Path
from typing import Any, cast

# ---------------------------------------------------------------------------
# Optionaler evdev-Import — Fehlermeldung vor Abbruch
# ---------------------------------------------------------------------------

try:
    from evdev import InputDevice, categorize, ecodes
    from evdev.events import KeyEvent

    _EVDEV_AVAILABLE = True
except ImportError:
    _EVDEV_AVAILABLE = False


# ---------------------------------------------------------------------------
# Hash-Hilfsfunktion — bevorzugt hash_uid() aus dem Projektmodul
# ---------------------------------------------------------------------------

import hashlib as _hashlib


def _compute_uid_hash(raw_uid: str) -> str:
    """SHA-256-Hash der RFID-UID.

    Nutzt hash_uid() aus arbeitszeit.infrastructure.hardware.uid_hash wenn das
    Paket im Pfad liegt, sonst identische Inline-Implementierung. So bleibt die
    Berechnung konsistent mit der Produktionslogik, auch wenn der Algorithmus
    dort künftig geändert wird.
    """
    try:
        sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
        from arbeitszeit.infrastructure.hardware.uid_hash import hash_uid

        return hash_uid(raw_uid)
    except ImportError:
        return _hashlib.sha256(raw_uid.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Ausgabe-Hilfsfunktionen
# ---------------------------------------------------------------------------


def _mask_uid(uid: str) -> str:
    """Gibt die ersten 4 Zeichen der UID in Großbuchstaben zurück, Rest maskiert."""
    return uid.upper()[:4] + "****"


def _ok(msg: str) -> None:
    print(f"  \033[32m✔\033[0m  {msg}")


def _fail(msg: str) -> None:
    print(f"  \033[31m✘\033[0m  {msg}")


def _info(msg: str) -> None:
    print(f"  \033[90m→\033[0m  {msg}")


def _header(msg: str) -> None:
    print(f"\n\033[1m{msg}\033[0m")
    print("─" * 50)


# ---------------------------------------------------------------------------
# Geräte-Auflistung
# ---------------------------------------------------------------------------

def list_input_devices() -> list[dict[str, Any]]:
    """Gibt alle lesbaren /dev/input/event*-Geräte mit Namen zurück."""
    if not _EVDEV_AVAILABLE:
        return []
    devices = []
    for path in sorted(Path("/dev/input").glob("event*")):
        if not os.access(path, os.R_OK):
            continue
        try:
            dev = InputDevice(str(path))
            devices.append({"path": str(path), "name": dev.name, "phys": dev.phys or ""})
            dev.close()
        except Exception:
            pass
    return devices


def print_device_list() -> None:
    _header("Verfügbare Eingabegeräte")
    devices = list_input_devices()
    if not devices:
        _fail("Keine lesbaren /dev/input/event*-Geräte gefunden.")
        _info("Prüfe: Gruppe 'input' oder sudo erforderlich?")
        return
    col_path = max(len(d["path"]) for d in devices)
    print(f"  {'Gerätedatei':{col_path}}  Name")
    print(f"  {'-' * col_path}  {'-' * 40}")
    for d in devices:
        print(f"  {d['path']:{col_path}}  {d['name']}")


# ---------------------------------------------------------------------------
# Interaktive Geräteauswahl
# ---------------------------------------------------------------------------

def _prompt_device(label: str, devices: list[dict[str, Any]]) -> str:
    """Lässt den Benutzer ein Gerät per Nummer oder direkter Pfadeingabe wählen."""
    print(f"\n  Verfügbare Geräte für {label}:")
    for i, d in enumerate(devices, 1):
        print(f"    [{i}]  {d['path']}  —  {d['name']}")
    print("    [m]  Pfad manuell eingeben")
    while True:
        raw = input(f"\n  Auswahl für {label}: ").strip()
        if raw == "m":
            path = input("  Gerätepfad: ").strip()
            if path:
                return path
        elif raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(devices):
                return str(devices[idx]["path"])
        print("  Ungültige Eingabe. Bitte Nummer oder 'm' eingeben.")


def select_rfid_interactively() -> str:
    devices = list_input_devices()
    if not devices:
        print("\n\033[31mFehler:\033[0m Keine lesbaren Eingabegeräte gefunden.", file=sys.stderr)
        print("Prüfe ob Gruppe 'input' zugewiesen oder sudo erforderlich ist.", file=sys.stderr)
        sys.exit(1)
    print_device_list()
    return _prompt_device("RFID-Reader", devices)


# ---------------------------------------------------------------------------
# Stufe 1: Gerätedatei prüfen
# ---------------------------------------------------------------------------

def check_device_access(rfid_path: str) -> bool:
    _header("Stufe 1 — Gerätedatei")
    p = Path(rfid_path)
    if not p.exists():
        _fail(f"RFID-Reader: Gerätedatei nicht gefunden: {rfid_path}")
        return False
    elif not os.access(rfid_path, os.R_OK):
        _fail(f"RFID-Reader: Keine Leseberechtigung: {rfid_path}")
        _info("Prüfe: sudo usermod -aG input $USER && Neuanmeldung")
        return False
    else:
        _ok(f"RFID-Reader: {rfid_path} — lesbar")
        return True


# ---------------------------------------------------------------------------
# Stufe 2: RFID-Reader-Test
# ---------------------------------------------------------------------------

_HEX_KEY_CHAR: dict[str, str] = {
    **{f"KEY_{d}": d for d in "0123456789"},
    **{f"KEY_{c}": c.lower() for c in "ABCDEF"},
    **{f"KEY_KP{d}": d for d in "0123456789"},
}
_HEX_KEY_CHAR_SHIFT: dict[str, str] = {k: v.upper() for k, v in _HEX_KEY_CHAR.items()}

_RFID_TIMEOUT = 15.0  # Sekunden


def test_rfid(rfid_path: str) -> bool:
    _header("Stufe 2 — RFID-Reader")
    print(f"  Gerät: {rfid_path}")
    print(f"  Bitte innerhalb von {_RFID_TIMEOUT:.0f}s eine RFID-Karte an den Leser halten.")

    try:
        dev = InputDevice(rfid_path)
    except Exception as exc:
        _fail(f"Gerät konnte nicht geöffnet werden: {exc}")
        return False

    try:
        deadline = time.monotonic() + _RFID_TIMEOUT
        chars: list[str] = []
        shift_active = False
        uid_raw: str | None = None

        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            ready, _, _ = select.select([dev.fd], [], [], min(remaining, 0.5))
            if not ready:
                continue
            for event in dev.read():
                if event.type != ecodes.EV_KEY:
                    continue
                key_event = cast(KeyEvent, categorize(event))
                keycode = key_event.keycode
                if isinstance(keycode, tuple):
                    keycode = keycode[0]
                if key_event.keystate == key_event.key_down:
                    if keycode in ("KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"):
                        shift_active = True
                    elif keycode in ("KEY_ENTER", "KEY_KPENTER"):
                        uid_raw = "".join(chars)
                        break
                    else:
                        char_map = _HEX_KEY_CHAR_SHIFT if shift_active else _HEX_KEY_CHAR
                        c = char_map.get(keycode)
                        if c is not None:
                            chars.append(c)
                elif key_event.keystate == key_event.key_up:
                    if keycode in ("KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"):
                        shift_active = False
            if uid_raw is not None:
                break

        if uid_raw is None:
            _fail(f"Kein RFID-Scan innerhalb von {_RFID_TIMEOUT:.0f}s erkannt.")
            _info("Prüfe ob das richtige Gerät ausgewählt ist.")
            _info("RFID-Reader muss UID als HID-Tastatureingabe (Hex + Enter) liefern.")
            return False

        if not uid_raw:
            _fail("RFID-Scan erkannt, aber UID war leer (kein Hex-Inhalt vor Enter).")
            _info("Prüfe ob der Reader UIDs als Hex-String kodiert.")
            return False

        uid_hash = _compute_uid_hash(uid_raw)
        _ok("RFID-Karte erkannt:")
        _info(f"Rohe UID (Hex):  {_mask_uid(uid_raw)}  (erste 4 Zeichen, Rest maskiert)")
        _info(f"Länge:           {len(uid_raw)} Zeichen ({len(uid_raw) * 4} Bit)")
        _info(f"SHA-256-Hash:    {uid_hash}  (wie in DB gespeichert)")
        return True

    except Exception as exc:
        _fail(f"Fehler beim Lesen vom RFID-Reader: {exc}")
        return False
    finally:
        try:
            dev.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Zusammenfassung
# ---------------------------------------------------------------------------

def print_summary(results: dict[str, bool]) -> None:
    _header("Ergebnis")
    labels = {
        "access":  "Gerätezugriff",
        "rfid":    "RFID-Reader",
    }
    all_ok = True
    for key, label in labels.items():
        if key not in results:
            continue
        ok = results[key]
        if ok:
            _ok(label)
        else:
            _fail(label)
            all_ok = False

    print()
    if all_ok:
        print("  \033[32m\033[1mAlle Prüfungen bestanden — Hardware betriebsbereit.\033[0m")
    else:
        print("  \033[31m\033[1mMindestens eine Prüfung fehlgeschlagen.\033[0m")
        print("  Bitte Gerätepfad und Berechtigungen prüfen.")
        print("  Hinweise zur udev-Regel: docs/betrieb/hardware_inbetriebnahme_protokoll.md")
    print()


# ---------------------------------------------------------------------------
# Einstiegspunkt
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Interaktiver Hardware-Smoke-Test für den RFID-Reader.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Beispiele:\n"
            "  python scripts/verify_hardware.py --list\n"
            "  python scripts/verify_hardware.py\n"
            "  python scripts/verify_hardware.py --rfid /dev/input/event4\n"
            "  python scripts/verify_hardware.py --skip-interactive\n"
        ),
    )
    parser.add_argument(
        "--rfid",
        metavar="GERÄTPFAD",
        help="Pfad zum RFID-Reader, z. B. /dev/input/event4",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Nur verfügbare Eingabegeräte auflisten und beenden",
    )
    parser.add_argument(
        "--skip-interactive",
        action="store_true",
        help="Nur Gerätedatei prüfen, keinen Karten-Test durchführen",
    )
    args = parser.parse_args(argv)

    print("\n\033[1marbeitszeit — Hardware-Smoke-Test\033[0m")
    print("=" * 50)

    if args.list:
        print_device_list()
        print()
        return 0

    if not _EVDEV_AVAILABLE:
        print(
            "\n\033[31mFehler:\033[0m python-evdev ist nicht installiert.\n"
            "  pip install evdev\n",
            file=sys.stderr,
        )
        return 2

    if args.rfid:
        rfid_path = args.rfid
    else:
        print("\nKein Gerätepfad angegeben — interaktive Auswahl.\n")
        rfid_path = select_rfid_interactively()

    results: dict[str, bool] = {}

    results["access"] = check_device_access(rfid_path)

    if not results["access"]:
        print_summary(results)
        return 1

    if args.skip_interactive:
        _info("--skip-interactive: Karten-Test übersprungen.")
        print_summary(results)
        return 0

    results["rfid"] = test_rfid(rfid_path)

    print_summary(results)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
