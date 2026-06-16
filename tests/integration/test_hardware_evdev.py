"""
Tests für evdev-spezifische Logik: Hex-Filter (map_rfid_key) und Fehlerhierarchie.
Physische Hardware wird nicht benötigt; getestet werden die reinen Mappingfunktionen.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.hardware import HardwareTimeoutError
from arbeitszeit.infrastructure.hardware.evdev_reader import map_rfid_key

# --- HardwareTimeoutError ---


def test_hardware_timeout_error_ist_runtime_error_subklasse():
    assert issubclass(HardwareTimeoutError, RuntimeError)


# --- map_rfid_key: Hex-Filter-Logik ---


def test_hex_ziffern_werden_gemappt():
    for d in "0123456789":
        assert map_rfid_key(f"KEY_{d}", shift_active=False) == d


def test_hex_buchstaben_a_bis_f_ohne_shift_kleinschreibung():
    for c in "ABCDEF":
        result = map_rfid_key(f"KEY_{c}", shift_active=False)
        assert result == c.lower(), f"KEY_{c} ohne Shift sollte '{c.lower()}' liefern"


def test_hex_buchstaben_a_bis_f_mit_shift_grossschreibung():
    for c in "ABCDEF":
        result = map_rfid_key(f"KEY_{c}", shift_active=True)
        assert result == c.upper(), f"KEY_{c} mit Shift sollte '{c.upper()}' liefern"


def test_nicht_hex_buchstaben_werden_ignoriert():
    for c in "GHIJKLMNOPQRSTUVWXYZ":
        assert map_rfid_key(f"KEY_{c}", shift_active=False) is None
        assert map_rfid_key(f"KEY_{c}", shift_active=True) is None


def test_kp_ziffern_werden_gemappt():
    for d in "0123456789":
        assert map_rfid_key(f"KEY_KP{d}", shift_active=False) == d


def test_unbekannte_keycodes_werden_ignoriert():
    assert map_rfid_key("KEY_F1", shift_active=False) is None
    assert map_rfid_key("KEY_SPACE", shift_active=False) is None
    assert map_rfid_key("KEY_BACKSPACE", shift_active=False) is None
