"""
Liest Buchungsanfragen von zwei evdev-Geräten:
  - Numpad (USB-Numpad): Buchungstyp-Auswahl per Taste 1–4
  - RFID-Reader (HID-Keyboard): Karten-UID als Tastenfolge + Enter

Voraussetzungen:
  - Linux, physische Geräte unter /dev/input/event*
  - Gerätepfade werden übergeben (z. B. aus config oder Autodetect)
  - Prozess benötigt Lesezugriff auf die Gerätedateien
    (Gruppe 'input' oder root, oder udev-Regel)

Unterstütztes Reader-Modell:
  EvdevHardwareReader setzt voraus, dass der RFID-Reader seine UID als
  HID-Tastatureingabe liefert: Hex-Zeichen (0–9, A–F, mit oder ohne Shift),
  abgeschlossen durch Enter. Nicht-Hex-Zeichen werden ignoriert; Präfixe,
  Suffixe oder abweichende Kodierungen erfordern eine angepasste Reader-Policy.

_read_booking_type() blockiert unbegrenzt, bis eine gültige Taste gedrückt
wird. Das ist beabsichtigt: Das System wartet im Idle auf eine Buchungsauswahl.
Timeout-Logik für den Wartezustand gehört in die aufrufende Betriebsschicht.

Lebenszyklus: Die aufrufende Schicht ist für close() verantwortlich.
Empfohlen ist try/finally oder ein Context Manager, damit close()
auch bei Ausnahmen sicher erreicht wird.

Anmerkung: Dieses Modul wird nur auf dem Zielsystem (Raspberry Pi o. ä.) genutzt.
Im Testbetrieb ist SimulatedHardwareReader zu verwenden.
"""
import select
import time
from datetime import datetime, timezone

from evdev import InputDevice, categorize, ecodes

from arbeitszeit.domain.enums import BookingType

from .ports import EmptyUidError, HardwareReader, HardwareTimeoutError, RawBookingRequest
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

# Nur Hex-Zeichen (0–9, A–F) – RFID-Lesegeräte liefern ausschließlich Hex-UIDs.
# Andere alphanumerische Zeichen werden bewusst ignoriert (kein Rauschen/Fremdeingaben).
_HEX_KEY_CHAR: dict[str, str] = {
    **{f"KEY_{d}": d for d in "0123456789"},
    **{f"KEY_{c}": c.lower() for c in "ABCDEF"},
    **{f"KEY_KP{d}": d for d in "0123456789"},
}
_HEX_KEY_CHAR_SHIFT: dict[str, str] = {k: v.upper() for k, v in _HEX_KEY_CHAR.items()}

# Timeout (Sekunden) für den RFID-Lesevorgang nach Buchungstyp-Auswahl.
_RFID_READ_TIMEOUT: float = 5.0


def map_rfid_key(keycode: str, shift_active: bool) -> str | None:
    """Bildet einen HID-Keycode auf ein Hex-Zeichen ab, oder None bei Nicht-Hex.

    Testbar ohne Hardware: enthält die gesamte Filterlogik des RFID-Lesevorgangs.
    """
    char_map = _HEX_KEY_CHAR_SHIFT if shift_active else _HEX_KEY_CHAR
    return char_map.get(keycode)


class EvdevHardwareReader(HardwareReader):
    """Liest Buchungsanfragen von physischen evdev-Geräten.

    grab=True (Standard) schließt die Geräte exklusiv für andere Prozesse.
    Sinnvoll im Kiosk-Betrieb; für Diagnose/Test grab=False übergeben.
    Bei Prozessabsturz mit grab=True kann das Gerät temporär blockiert bleiben –
    Absturzverhalten und Reconnect-Logik gehören in die aufrufende Schicht.
    """

    def __init__(
        self,
        numpad_path: str,
        rfid_path: str,
        *,
        grab: bool = True,
        rfid_timeout: float = _RFID_READ_TIMEOUT,
    ) -> None:
        self._numpad = InputDevice(numpad_path)
        self._rfid = InputDevice(rfid_path)
        self._rfid_timeout = rfid_timeout
        if grab:
            self._numpad.grab()
            self._rfid.grab()

    def read_next(self) -> RawBookingRequest:
        booking_type = self._read_booking_type()
        # occurred_at erst nach vollständiger UID-Lesung:
        # Setzt den Zeitstempel auf den Abschluss der Buchungsanforderung,
        # nicht auf den Zwischenstand nach Tastenauswahl.
        raw_uid = self._read_rfid_uid(timeout=self._rfid_timeout).strip()
        occurred_at = datetime.now(timezone.utc)
        if not raw_uid:
            raise EmptyUidError(
                "RFID-Lesegerät lieferte leere UID – Buchungsvorgang abgebrochen."
            )
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
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise HardwareTimeoutError(
                    f"RFID-Lesevorgang überschritt {timeout}s-Zeitlimit."
                )
            ready, _, _ = select.select([self._rfid.fd], [], [], remaining)
            if not ready:
                raise HardwareTimeoutError(
                    f"RFID-Lesevorgang überschritt {timeout}s-Zeitlimit."
                )
            for event in self._rfid.read():
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
                        return "".join(chars)
                    else:
                        c = map_rfid_key(keycode, shift_active)
                        if c is not None:
                            chars.append(c)
                elif key_event.keystate == key_event.key_up:
                    if keycode in ("KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"):
                        shift_active = False

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
