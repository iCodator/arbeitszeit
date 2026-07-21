"""
Liest Buchungsanfragen vom RFID-Reader:
  - RFID-Reader (HID-Keyboard): Karten-UID als Tastenfolge + Enter

Voraussetzungen:
  - Linux, physisches Gerät unter /dev/input/event*
  - Gerätepfad wird übergeben (z. B. aus config oder Autodetect)
  - Prozess benötigt Lesezugriff auf die Gerätedatei
    (Gruppe 'input' oder root, oder udev-Regel)

Unterstütztes Reader-Modell:
  EvdevHardwareReader setzt voraus, dass der RFID-Reader seine UID als
  HID-Tastatureingabe liefert: Hex-Zeichen (0–9, A–F, mit oder ohne Shift),
  abgeschlossen durch Enter. Nicht-Hex-Zeichen werden ignoriert; Präfixe,
  Suffixe oder abweichende Kodierungen erfordern eine angepasste Reader-Policy.

read_next() wartet blockierend bis zu _RFID_READ_TIMEOUT Sekunden auf einen
RFID-Scan. Bei Ablauf des Timeouts wird HardwareTimeoutError geworfen und der
Zyklus in der aufrufenden Schicht neu gestartet. Dies ermöglicht einen
Graceful Shutdown nach SIGTERM innerhalb endlicher Zeit.

Lebenszyklus: Die aufrufende Schicht ist für close() verantwortlich.
Empfohlen ist try/finally oder ein Context Manager, damit close()
auch bei Ausnahmen sicher erreicht wird.

Anmerkung: Dieses Modul wird nur auf dem Zielsystem (Raspberry Pi o. ä.) genutzt.
Im Testbetrieb ist SimulatedHardwareReader zu verwenden.
"""

__version__ = "1.2"

import logging
import select
import time
from datetime import datetime, timezone
from typing import cast

from evdev import InputDevice, categorize, ecodes, list_devices
from evdev.events import KeyEvent

from .ports import (
    EmptyUidError,
    HardwareReader,
    HardwareTimeoutError,
    RawBookingRequest,
)
from .uid_hash import hash_uid


class DeviceNotFoundError(OSError):
    """Kein evdev-Gerät mit dem angegebenen Namen gefunden."""


# Nur Hex-Zeichen (0–9, A–F) – RFID-Lesegeräte liefern ausschließlich Hex-UIDs.
# Andere alphanumerische Zeichen werden bewusst ignoriert (kein Rauschen/Fremdeingaben).
_HEX_KEY_CHAR: dict[str, str] = {
    **{f"KEY_{d}": d for d in "0123456789"},
    **{f"KEY_{c}": c.lower() for c in "ABCDEF"},
    **{f"KEY_KP{d}": d for d in "0123456789"},
}
_HEX_KEY_CHAR_SHIFT: dict[str, str] = {k: v.upper() for k, v in _HEX_KEY_CHAR.items()}

# Timeout (Sekunden) für den RFID-Lesevorgang. Begrenzt die Wartezeit in
# select.select() so dass SIGTERM nach spätestens diesem Intervall wirksam wird
# (PEP 475: select.select() wird nach EINTR automatisch neu gestartet,
# kehrt aber beim Timeout-Ablauf zurück → Hauptschleife kann running prüfen).
_RFID_READ_TIMEOUT: float = 5.0

_SHIFT_KEYS = ("KEY_LEFTSHIFT", "KEY_RIGHTSHIFT")
_ENTER_KEYS = ("KEY_ENTER", "KEY_KPENTER")


def resolve_evdev_device(name_or_path: str) -> str:
    """Gibt den /dev/input/eventX-Pfad für ein Gerät zurück.

    Beginnt der Wert mit '/dev/', wird er direkt zurückgegeben (Pfad-Modus).
    Sonst werden alle evdev-Geräte nach device.name durchsucht.
    Wirft DeviceNotFoundError wenn kein Gerät mit dem Namen gefunden wird.
    """
    if name_or_path.startswith("/dev/"):
        return name_or_path
    for path in list_devices():
        try:
            dev = InputDevice(path)
            if dev.name == name_or_path:
                return path
        except OSError:
            continue
    raise DeviceNotFoundError(f"Evdev-Gerät '{name_or_path}' nicht gefunden.")


def map_rfid_key(keycode: str, shift_active: bool) -> str | None:
    """Bildet einen HID-Keycode auf ein Hex-Zeichen ab, oder None bei Nicht-Hex.

    Testbar ohne Hardware: enthält die gesamte Filterlogik des RFID-Lesevorgangs.
    """
    char_map = _HEX_KEY_CHAR_SHIFT if shift_active else _HEX_KEY_CHAR
    return char_map.get(keycode)


def _normalize_keycode(keycode: str | tuple[str, ...]) -> str:
    """Normalisiert evdev-Keycodes: Tupel-Varianten werden auf das erste Element reduziert."""
    return keycode[0] if isinstance(keycode, tuple) else keycode


def _apply_rfid_key_down(
    keycode: str,
    chars: list[str],
    shift_active: bool,
) -> tuple[str | None, bool]:
    """Verarbeitet einen Key-Down-Event: Shift, Enter oder Hex-Zeichen."""
    if keycode in _SHIFT_KEYS:
        return None, True
    if keycode in _ENTER_KEYS:
        return "".join(chars), shift_active
    c = map_rfid_key(keycode, shift_active)
    if c is not None:
        chars.append(c)
    return None, shift_active


def _apply_rfid_key_up(keycode: str, shift_active: bool) -> bool:
    """Gibt den neuen Shift-Status nach einem Key-Up-Event zurück."""
    if keycode in _SHIFT_KEYS:
        return False
    return shift_active


def _process_rfid_key(
    key_event: KeyEvent,
    keycode: str,
    chars: list[str],
    shift_active: bool,
) -> tuple[str | None, bool]:
    """Dispatcht ein einzelnes Key-Event auf Key-Down oder Key-Up-Verarbeitung."""
    if key_event.keystate == key_event.key_down:
        return _apply_rfid_key_down(keycode, chars, shift_active)
    if key_event.keystate == key_event.key_up:
        return None, _apply_rfid_key_up(keycode, shift_active)
    return None, shift_active


def scan_rfid_uid_hash(rfid_path: str, timeout: float = 15.0) -> str:
    """Liest einmalig eine RFID-UID und gibt deren SHA-256-Hash zurück.

    Öffnet nur das RFID-Gerät. Wirft HardwareTimeoutError wenn
    innerhalb von `timeout` Sekunden keine vollständige UID gescannt wird,
    EmptyUidError wenn die UID nach dem Lesen leer ist.
    """
    device = InputDevice(rfid_path)
    try:
        device.grab()
        chars: list[str] = []
        shift_active = False
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise HardwareTimeoutError(f"RFID-Scan überschritt {timeout}s-Zeitlimit.")
            ready, _, _ = select.select([device.fd], [], [], remaining)
            if not ready:
                raise HardwareTimeoutError(f"RFID-Scan überschritt {timeout}s-Zeitlimit.")
            for event in device.read():
                if event.type != ecodes.EV_KEY:
                    continue
                key_event = cast(KeyEvent, categorize(event))
                keycode = _normalize_keycode(key_event.keycode)
                uid, shift_active = _process_rfid_key(key_event, keycode, chars, shift_active)
                if uid is not None:
                    raw_uid = uid.strip()
                    if not raw_uid:
                        raise EmptyUidError("RFID-Gerät lieferte leere UID.")
                    return hash_uid(raw_uid)
    finally:
        try:
            device.ungrab()
        except OSError:
            pass
        device.close()


class EvdevHardwareReader(HardwareReader):
    """Liest Buchungsanfragen vom physischen RFID-Reader.

    grab=True (Standard) schließt das Gerät exklusiv für andere Prozesse.
    Sinnvoll im Kiosk-Betrieb; für Diagnose/Test grab=False übergeben.
    Bei Prozessabsturz mit grab=True kann das Gerät temporär blockiert bleiben –
    Absturzverhalten und Reconnect-Logik gehören in die aufrufende Schicht.
    """

    def __init__(
        self,
        rfid_path: str,
        *,
        grab: bool = True,
    ) -> None:
        self._rfid = InputDevice(rfid_path)
        if grab:
            self._rfid.grab()

    def read_next(self) -> RawBookingRequest:
        raw_uid = self._read_rfid_uid(timeout=_RFID_READ_TIMEOUT).strip()
        occurred_at = datetime.now(timezone.utc)
        if not raw_uid:
            raise EmptyUidError("RFID-Lesegerät lieferte leere UID – Buchungsvorgang abgebrochen.")
        return RawBookingRequest(
            uid_hash=hash_uid(raw_uid),
            occurred_at=occurred_at,
        )

    def _wait_rfid_ready(self, deadline: float, timeout: float) -> None:
        """Wartet auf ein RFID-Event innerhalb der Deadline.

        Wirft HardwareTimeoutError wenn die Deadline abgelaufen ist oder select() nicht antwortet.
        """
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise HardwareTimeoutError(f"RFID-Lesevorgang überschritt {timeout}s-Zeitlimit.")
        ready, _, _ = select.select([self._rfid.fd], [], [], remaining)
        if not ready:
            raise HardwareTimeoutError(f"RFID-Lesevorgang überschritt {timeout}s-Zeitlimit.")

    def _read_rfid_batch(
        self,
        chars: list[str],
        shift_active: bool,
    ) -> tuple[str | None, bool]:
        """Verarbeitet eine Charge von RFID-Events aus einem read()-Aufruf.

        Gibt (UID, shift_active) zurück wenn Enter erkannt, sonst (None, shift_active).
        """
        for event in self._rfid.read():
            if event.type != ecodes.EV_KEY:
                continue
            key_event = cast(KeyEvent, categorize(event))
            keycode = _normalize_keycode(key_event.keycode)
            uid, shift_active = _process_rfid_key(key_event, keycode, chars, shift_active)
            if uid is not None:
                return uid, shift_active
        return None, shift_active

    def _read_rfid_uid(self, timeout: float) -> str:
        """Liest Hex-UID vom RFID-Reader bis Enter oder Timeout.

        Wirft HardwareTimeoutError wenn innerhalb von `timeout` Sekunden
        keine vollständige UID (abgeschlossen durch Enter) gelesen wird.
        Nicht-Hex-Zeichen werden ignoriert.
        """
        chars: list[str] = []
        shift_active = False
        deadline = time.monotonic() + timeout
        while True:
            self._wait_rfid_ready(deadline, timeout)
            result, shift_active = self._read_rfid_batch(chars, shift_active)
            if result is not None:
                return result

    def close(self) -> None:
        try:
            self._rfid.ungrab()
        except OSError as exc:
            logging.warning(
                "evdev: ungrab() fehlgeschlagen [%s]: %s", self._rfid.path, exc, exc_info=True
            )
        try:
            self._rfid.close()
        except OSError as exc:
            logging.warning(
                "evdev: close() fehlgeschlagen [%s]: %s", self._rfid.path, exc, exc_info=True
            )
