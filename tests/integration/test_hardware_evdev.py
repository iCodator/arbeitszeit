"""
Tests für evdev-spezifische Logik: Hex-Filter (map_rfid_key), Fehlerhierarchie
und Unit-Tests für EvdevHardwareReader-Methoden (ohne physische Hardware).
"""

import logging
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from evdev import ecodes

from arbeitszeit.domain.enums import BookingType
from arbeitszeit.infrastructure.hardware import HardwareTimeoutError
from arbeitszeit.infrastructure.hardware.evdev_reader import EvdevHardwareReader, map_rfid_key

# Keystate-Konstanten wie in evdev.events.KeyEvent
_KEY_DOWN = 1
_KEY_UP = 0


def _make_reader() -> EvdevHardwareReader:
    """Erzeugt EvdevHardwareReader via object.__new__ — kein physisches Gerät nötig."""
    reader: EvdevHardwareReader = object.__new__(EvdevHardwareReader)
    reader._numpad = MagicMock()
    reader._numpad.path = "/dev/input/event0"
    reader._rfid = MagicMock()
    reader._rfid.path = "/dev/input/event1"
    reader._rfid.fd = 99  # Dummy-FD, da select.select gemockt wird
    reader._rfid_timeout = 5.0
    return reader


def _raw_ev(keycode: str, keystate: int) -> SimpleNamespace:
    """Fake evdev InputEvent für eine Taste (type=EV_KEY)."""
    return SimpleNamespace(type=ecodes.EV_KEY, value=keystate, keycode=keycode)


def _key_ev(keycode: str, keystate: int) -> SimpleNamespace:
    """Fake KeyEvent wie von categorize() zurückgegeben."""
    return SimpleNamespace(keystate=keystate, keycode=keycode, key_down=_KEY_DOWN, key_up=_KEY_UP)


def _categorize_mock(event: SimpleNamespace) -> SimpleNamespace:
    """Bildet einen _raw_ev auf einen _key_ev ab (Attribut keycode aus dem Event)."""
    return _key_ev(event.keycode, event.value)

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


# --- EvdevHardwareReader.close() ---


class TestEvdevClose:
    def test_ungrab_und_close_werden_auf_beiden_geraeten_aufgerufen(self) -> None:
        reader = _make_reader()
        reader.close()
        reader._numpad.ungrab.assert_called_once()
        reader._numpad.close.assert_called_once()
        reader._rfid.ungrab.assert_called_once()
        reader._rfid.close.assert_called_once()

    def test_oserror_bei_ungrab_logt_warning_und_close_wird_aufgerufen(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        reader = _make_reader()
        reader._numpad.ungrab.side_effect = OSError("Gerät gesperrt")
        with caplog.at_level(logging.WARNING):
            reader.close()
        assert "ungrab" in caplog.text
        reader._numpad.close.assert_called_once()
        reader._rfid.ungrab.assert_called_once()
        reader._rfid.close.assert_called_once()

    def test_oserror_bei_close_logt_warning_und_zweites_geraet_wird_bearbeitet(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        reader = _make_reader()
        reader._numpad.close.side_effect = OSError("close fehlgeschlagen")
        with caplog.at_level(logging.WARNING):
            reader.close()
        assert "close" in caplog.text
        reader._rfid.ungrab.assert_called_once()
        reader._rfid.close.assert_called_once()


# --- EvdevHardwareReader._read_rfid_uid() ---


_CATEGORIZE = "arbeitszeit.infrastructure.hardware.evdev_reader.categorize"


class TestReadRfidUid:
    def _run(
        self,
        reader: EvdevHardwareReader,
        events: list[SimpleNamespace],
        *,
        select_ready: bool = True,
    ) -> str:
        reader._rfid.read.return_value = events
        select_ret = ([reader._rfid.fd], [], []) if select_ready else ([], [], [])
        with patch("select.select", return_value=select_ret):
            with patch(_CATEGORIZE, side_effect=_categorize_mock):
                with patch("time.monotonic", return_value=0.0):
                    return reader._read_rfid_uid(5.0)

    def test_einfache_uid_eine_ziffer(self) -> None:
        reader = _make_reader()
        result = self._run(reader, [_raw_ev("KEY_1", _KEY_DOWN), _raw_ev("KEY_KPENTER", _KEY_DOWN)])
        assert result == "1"

    def test_mehrere_zeichen_bis_enter(self) -> None:
        reader = _make_reader()
        result = self._run(
            reader,
            [
                _raw_ev("KEY_A", _KEY_DOWN),
                _raw_ev("KEY_B", _KEY_DOWN),
                _raw_ev("KEY_ENTER", _KEY_DOWN),
            ],
        )
        assert result == "ab"

    def test_shift_modifier_liefert_grossbuchstaben(self) -> None:
        reader = _make_reader()
        result = self._run(
            reader,
            [
                _raw_ev("KEY_LEFTSHIFT", _KEY_DOWN),
                _raw_ev("KEY_A", _KEY_DOWN),
                _raw_ev("KEY_LEFTSHIFT", _KEY_UP),
                _raw_ev("KEY_ENTER", _KEY_DOWN),
            ],
        )
        assert result == "A"

    def test_select_timeout_wirft_hardware_timeout_error(self) -> None:
        reader = _make_reader()
        with pytest.raises(HardwareTimeoutError):
            self._run(reader, [], select_ready=False)

    def test_deadline_abgelaufen_wirft_hardware_timeout_error(self) -> None:
        reader = _make_reader()
        with patch(_CATEGORIZE, side_effect=_categorize_mock):
            with patch("time.monotonic", side_effect=[0.0, 1000.0]):
                with pytest.raises(HardwareTimeoutError):
                    reader._read_rfid_uid(5.0)

    def test_nicht_hex_taste_wird_ignoriert(self) -> None:
        reader = _make_reader()
        result = self._run(
            reader,
            [
                _raw_ev("KEY_G", _KEY_DOWN),
                _raw_ev("KEY_1", _KEY_DOWN),
                _raw_ev("KEY_ENTER", _KEY_DOWN),
            ],
        )
        assert result == "1"


# --- EvdevHardwareReader._read_booking_type() ---


class TestReadBookingType:
    def _run(
        self, reader: EvdevHardwareReader, events: list[SimpleNamespace]
    ) -> BookingType:
        reader._numpad.read_loop.return_value = iter(events)
        with patch(_CATEGORIZE, side_effect=_categorize_mock):
            return reader._read_booking_type()

    def test_kp1_liefert_come(self) -> None:
        reader = _make_reader()
        result = self._run(reader, [_raw_ev("KEY_KP1", _KEY_DOWN)])
        assert result == BookingType.COME

    def test_kp4_liefert_break_end(self) -> None:
        reader = _make_reader()
        result = self._run(reader, [_raw_ev("KEY_KP4", _KEY_DOWN)])
        assert result == BookingType.BREAK_END

    def test_key_up_wird_uebersprungen(self) -> None:
        reader = _make_reader()
        result = self._run(
            reader, [_raw_ev("KEY_KP1", _KEY_UP), _raw_ev("KEY_KP1", _KEY_DOWN)]
        )
        assert result == BookingType.COME

    def test_leerer_loop_wirft_oserror(self) -> None:
        reader = _make_reader()
        reader._numpad.read_loop.return_value = iter([])
        with pytest.raises(OSError):
            reader._read_booking_type()
