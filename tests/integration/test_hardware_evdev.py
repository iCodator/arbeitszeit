"""
Tests für evdev-spezifische Logik: Hex-Filter (map_rfid_key), Fehlerhierarchie
und Unit-Tests für EvdevHardwareReader-Methoden (ohne physische Hardware).
"""

__version__ = "1.1"

import logging
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from evdev import ecodes

from arbeitszeit.domain.enums import BookingType
from arbeitszeit.infrastructure.hardware import EmptyUidError, HardwareTimeoutError
from arbeitszeit.infrastructure.hardware.evdev_reader import (
    DeviceNotFoundError,
    EvdevHardwareReader,
    map_rfid_key,
    resolve_evdev_device,
)

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


def test_hardware_timeout_error_ist_runtime_error_subklasse() -> None:
    assert issubclass(HardwareTimeoutError, RuntimeError)


# --- map_rfid_key: Hex-Filter-Logik ---


def test_hex_ziffern_werden_gemappt() -> None:
    for d in "0123456789":
        assert map_rfid_key(f"KEY_{d}", shift_active=False) == d


def test_hex_buchstaben_a_bis_f_ohne_shift_kleinschreibung() -> None:
    for c in "ABCDEF":
        result = map_rfid_key(f"KEY_{c}", shift_active=False)
        assert result == c.lower(), f"KEY_{c} ohne Shift sollte '{c.lower()}' liefern"


def test_hex_buchstaben_a_bis_f_mit_shift_grossschreibung() -> None:
    for c in "ABCDEF":
        result = map_rfid_key(f"KEY_{c}", shift_active=True)
        assert result == c.upper(), f"KEY_{c} mit Shift sollte '{c.upper()}' liefern"


def test_nicht_hex_buchstaben_werden_ignoriert() -> None:
    for c in "GHIJKLMNOPQRSTUVWXYZ":
        assert map_rfid_key(f"KEY_{c}", shift_active=False) is None
        assert map_rfid_key(f"KEY_{c}", shift_active=True) is None


def test_kp_ziffern_werden_gemappt() -> None:
    for d in "0123456789":
        assert map_rfid_key(f"KEY_KP{d}", shift_active=False) == d


def test_unbekannte_keycodes_werden_ignoriert() -> None:
    assert map_rfid_key("KEY_F1", shift_active=False) is None
    assert map_rfid_key("KEY_SPACE", shift_active=False) is None
    assert map_rfid_key("KEY_BACKSPACE", shift_active=False) is None


# --- EvdevHardwareReader.close() ---


class TestEvdevClose:
    def test_ungrab_und_close_werden_auf_beiden_geraeten_aufgerufen(self) -> None:
        reader = _make_reader()
        numpad = cast(MagicMock, reader._numpad)
        rfid = cast(MagicMock, reader._rfid)
        reader.close()
        numpad.ungrab.assert_called_once()
        numpad.close.assert_called_once()
        rfid.ungrab.assert_called_once()
        rfid.close.assert_called_once()

    def test_oserror_bei_ungrab_logt_warning_und_close_wird_aufgerufen(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        reader = _make_reader()
        numpad = cast(MagicMock, reader._numpad)
        rfid = cast(MagicMock, reader._rfid)
        numpad.ungrab.side_effect = OSError("Gerät gesperrt")
        with caplog.at_level(logging.WARNING):
            reader.close()
        assert "ungrab" in caplog.text
        numpad.close.assert_called_once()
        rfid.ungrab.assert_called_once()
        rfid.close.assert_called_once()

    def test_oserror_bei_close_logt_warning_und_zweites_geraet_wird_bearbeitet(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        reader = _make_reader()
        numpad = cast(MagicMock, reader._numpad)
        rfid = cast(MagicMock, reader._rfid)
        numpad.close.side_effect = OSError("close fehlgeschlagen")
        with caplog.at_level(logging.WARNING):
            reader.close()
        assert "close" in caplog.text
        rfid.ungrab.assert_called_once()
        rfid.close.assert_called_once()


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
        rfid = cast(MagicMock, reader._rfid)
        rfid.read.return_value = events
        select_ret: tuple[list[Any], list[Any], list[Any]] = ([rfid.fd], [], []) if select_ready else ([], [], [])
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


# --- EvdevHardwareReader._read_booking_type_or_admin() ---


class TestReadBookingType:
    def _run(
        self, reader: EvdevHardwareReader, events: list[SimpleNamespace]
    ) -> BookingType:
        numpad = cast(MagicMock, reader._numpad)
        numpad.read_loop.return_value = iter(events)
        with patch(_CATEGORIZE, side_effect=_categorize_mock):
            result = reader._read_booking_type_or_admin()
        assert isinstance(result, BookingType)
        return result

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
        numpad = cast(MagicMock, reader._numpad)
        numpad.read_loop.return_value = iter([])
        with pytest.raises(OSError):
            reader._read_booking_type_or_admin()


# --- resolve_evdev_device() ---

_EVDEV_READER = "arbeitszeit.infrastructure.hardware.evdev_reader"


class TestResolveEvdevDevice:
    def test_pfad_wird_direkt_zurückgegeben(self) -> None:
        with patch(f"{_EVDEV_READER}.list_devices") as mock_list:
            result = resolve_evdev_device("/dev/input/event3")
        assert result == "/dev/input/event3"
        mock_list.assert_not_called()

    def test_name_wird_aufgelöst(self) -> None:
        mock_dev_a = MagicMock()
        mock_dev_a.name = "Other Device"
        mock_dev_b = MagicMock()
        mock_dev_b.name = "USB Numpad"

        def fake_input_device(path: str) -> MagicMock:
            return mock_dev_a if path == "/dev/input/event0" else mock_dev_b

        with (
            patch(
                f"{_EVDEV_READER}.list_devices",
                return_value=["/dev/input/event0", "/dev/input/event1"],
            ),
            patch(f"{_EVDEV_READER}.InputDevice", side_effect=fake_input_device),
        ):
            result = resolve_evdev_device("USB Numpad")
        assert result == "/dev/input/event1"

    def test_name_nicht_gefunden_wirft_exception(self) -> None:
        mock_dev = MagicMock()
        mock_dev.name = "Other Device"
        with (
            patch(f"{_EVDEV_READER}.list_devices", return_value=["/dev/input/event0"]),
            patch(f"{_EVDEV_READER}.InputDevice", return_value=mock_dev),
        ):
            with pytest.raises(DeviceNotFoundError):
                resolve_evdev_device("Unbekanntes Gerät")

    def test_oserror_beim_öffnen_wird_übersprungen(self) -> None:
        mock_dev = MagicMock()
        mock_dev.name = "USB Numpad"

        call_count = [0]

        def fake_input_device(path: str) -> MagicMock:
            call_count[0] += 1
            if call_count[0] == 1:
                raise OSError("Gerät nicht lesbar")
            return mock_dev

        with (
            patch(
                f"{_EVDEV_READER}.list_devices",
                return_value=["/dev/input/event0", "/dev/input/event1"],
            ),
            patch(f"{_EVDEV_READER}.InputDevice", side_effect=fake_input_device),
        ):
            result = resolve_evdev_device("USB Numpad")
        assert result == "/dev/input/event1"


# --- scan_rfid_uid_hash() ---

from arbeitszeit.infrastructure.hardware.evdev_reader import scan_rfid_uid_hash  # noqa: E402
from arbeitszeit.infrastructure.hardware.uid_hash import hash_uid  # noqa: E402


def _make_enter_event() -> SimpleNamespace:
    return _raw_ev("KEY_KPENTER", _KEY_DOWN)


class TestScanRfidUidHash:
    def _run_scan(
        self,
        mock_device: MagicMock,
        events: list[SimpleNamespace],
        *,
        select_ready: bool = True,
        timeout: float = 5.0,
    ) -> str:
        mock_device.read.return_value = events
        select_ret: tuple[list[Any], list[Any], list[Any]] = ([mock_device.fd], [], []) if select_ready else ([], [], [])
        with (
            patch(f"{_EVDEV_READER}.InputDevice", return_value=mock_device),
            patch("select.select", return_value=select_ret),
            patch(_CATEGORIZE, side_effect=_categorize_mock),
            patch("time.monotonic", return_value=0.0),
        ):
            return scan_rfid_uid_hash("/dev/input/event5", timeout=timeout)

    def test_erfolgreicher_scan_gibt_hash_zurück(self) -> None:
        dev = MagicMock()
        dev.fd = 42
        result = self._run_scan(
            dev,
            [_raw_ev("KEY_A", _KEY_DOWN), _raw_ev("KEY_1", _KEY_DOWN), _make_enter_event()],
        )
        assert result == hash_uid("a1")

    def test_timeout_wirft_hardware_timeout_error(self) -> None:
        dev = MagicMock()
        dev.fd = 42
        with pytest.raises(HardwareTimeoutError):
            self._run_scan(dev, [], select_ready=False)

    def test_leere_uid_wirft_empty_uid_error(self) -> None:
        dev = MagicMock()
        dev.fd = 42
        with pytest.raises(EmptyUidError):
            self._run_scan(dev, [_make_enter_event()])

    def test_device_wird_in_finally_geschlossen(self) -> None:
        dev = MagicMock()
        dev.fd = 42
        try:
            self._run_scan(dev, [], select_ready=False)
        except HardwareTimeoutError:
            pass
        dev.close.assert_called_once()

    def test_ungrab_oserror_wird_ignoriert(self) -> None:
        dev = MagicMock()
        dev.fd = 42
        dev.ungrab.side_effect = OSError("ungrab fehlgeschlagen")
        with pytest.raises(HardwareTimeoutError):
            self._run_scan(dev, [], select_ready=False)
        dev.close.assert_called_once()
