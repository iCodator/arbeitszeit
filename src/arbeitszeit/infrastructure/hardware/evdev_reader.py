"""
Liest Buchungsanfragen von zwei evdev-Geräten:
  - Numpad (USB-Numpad): Buchungstyp-Auswahl per Taste 1–4
  - RFID-Reader (HID-Keyboard): Karten-UID als Tastenfolge + Enter

Voraussetzungen:
  - Linux, physische Geräte unter /dev/input/event*
  - Gerätepfade werden übergeben (z. B. aus config oder Autodetect)
  - Prozess benötigt Lesezugriff auf die Gerätedateien
    (Gruppe 'input' oder root, oder udev-Regel)

Anmerkung: Dieses Modul wird nur auf dem Zielsystem (Raspberry Pi o. ä.) genutzt.
Im Testbetrieb ist SimulatedHardwareReader zu verwenden.
"""
from datetime import datetime, timezone

import evdev
from evdev import InputDevice, categorize, ecodes

from arbeitszeit.domain.enums import BookingType

from .ports import RawBookingRequest
from .uid_hash import hash_uid

# Numpad-Tasten 1–4 (KP-Variante und normale Ziffern) → BookingType
_NUMPAD_TO_BOOKING_TYPE: dict[str, BookingType] = {
    "KEY_KP1": BookingType.COME,
    "KEY_1":   BookingType.COME,
    "KEY_KP2": BookingType.GO,
    "KEY_2":   BookingType.GO,
    "KEY_KP3": BookingType.BREAK_START,
    "KEY_3":   BookingType.BREAK_START,
    "KEY_KP4": BookingType.BREAK_END,
    "KEY_4":   BookingType.BREAK_END,
}

# HID-Tastatur-Keycodes → ASCII-Zeichen (ohne Shift)
_KEY_CHAR: dict[str, str] = {
    **{f"KEY_{d}": d for d in "0123456789"},
    **{f"KEY_{c}": c.lower() for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    **{f"KEY_KP{d}": d for d in "0123456789"},
}

# Mit Shift (für Lesegeräte, die Uppercase oder Sonderzeichen ausgeben)
_KEY_CHAR_SHIFT: dict[str, str] = {
    **{k: v.upper() for k, v in _KEY_CHAR.items()},
}


class EvdevHardwareReader:
    """Liest Buchungsanfragen von physischen evdev-Geräten."""

    def __init__(
        self,
        numpad_path: str,
        rfid_path: str,
        *,
        grab: bool = True,
    ) -> None:
        self._numpad = InputDevice(numpad_path)
        self._rfid = InputDevice(rfid_path)
        if grab:
            self._numpad.grab()
            self._rfid.grab()

    def read_next(self) -> RawBookingRequest:
        booking_type = self._read_booking_type()
        occurred_at = datetime.now(timezone.utc)
        raw_uid = self._read_rfid_uid()
        return RawBookingRequest(
            booking_type=booking_type,
            uid_hash=hash_uid(raw_uid),
            occurred_at=occurred_at,
        )

    def _read_booking_type(self) -> BookingType:
        for event in self._numpad.read_loop():
            if event.type != ecodes.EV_KEY:
                continue
            key_event = categorize(event)
            if key_event.keystate != key_event.key_down:
                continue
            keycode = key_event.keycode
            if isinstance(keycode, list):
                keycode = keycode[0]
            bt = _NUMPAD_TO_BOOKING_TYPE.get(keycode)
            if bt is not None:
                return bt
        raise OSError("Numpad-Gerät unerwartet geschlossen.")

    def _read_rfid_uid(self) -> str:
        chars: list[str] = []
        shift_active = False
        for event in self._rfid.read_loop():
            if event.type != ecodes.EV_KEY:
                continue
            key_event = categorize(event)
            keycode = key_event.keycode
            if isinstance(keycode, list):
                keycode = keycode[0]
            if key_event.keystate == key_event.key_down:
                if keycode in ("KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"):
                    shift_active = True
                elif keycode in ("KEY_ENTER", "KEY_KPENTER"):
                    break
                else:
                    char_map = _KEY_CHAR_SHIFT if shift_active else _KEY_CHAR
                    c = char_map.get(keycode)
                    if c is not None:
                        chars.append(c)
            elif key_event.keystate == key_event.key_up:
                if keycode in ("KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"):
                    shift_active = False
        return "".join(chars)

    def close(self) -> None:
        for dev in (self._numpad, self._rfid):
            try:
                dev.ungrab()
            except Exception:
                pass
            try:
                dev.close()
            except Exception:
                pass
