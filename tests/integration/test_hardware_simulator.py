import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import BookingType
from arbeitszeit.infrastructure.hardware import (
    EmptyUidError,
    HardwareReader,
    RawBookingRequest,
    SimulatedHardwareReader,
    hash_uid,
)

_T = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)


# --- SimulatedHardwareReader ---


def test_inject_und_read_next_liefert_richtigen_buchungstyp():
    sim = SimulatedHardwareReader()
    sim.inject(BookingType.COME, "HASH001", occurred_at=_T)
    req = sim.read_next()
    assert req.booking_type == BookingType.COME
    assert req.uid_hash == "HASH001"
    assert req.occurred_at == _T


def test_inject_reihenfolge_wird_eingehalten():
    sim = SimulatedHardwareReader()
    sim.inject(BookingType.COME, "HASH_A", occurred_at=_T)
    sim.inject(BookingType.GO, "HASH_B", occurred_at=_T)
    assert sim.read_next().booking_type == BookingType.COME
    assert sim.read_next().booking_type == BookingType.GO


def test_leere_queue_wirft_runtime_error():
    sim = SimulatedHardwareReader()
    with pytest.raises(RuntimeError):
        sim.read_next()


def test_pending_zaehlt_korrekt():
    sim = SimulatedHardwareReader()
    assert sim.pending == 0
    sim.inject(BookingType.GO, "H1")
    sim.inject(BookingType.COME, "H2")
    assert sim.pending == 2
    sim.read_next()
    assert sim.pending == 1


def test_close_ist_idempotent():
    sim = SimulatedHardwareReader()
    sim.inject(BookingType.COME, "HASH", occurred_at=_T)
    sim.close()
    sim.close()  # kein Fehler


def test_occurred_at_wird_gesetzt_wenn_nicht_angegeben():
    sim = SimulatedHardwareReader()
    vor = datetime.now(timezone.utc)
    sim.inject(BookingType.COME, "HASH")
    nach = datetime.now(timezone.utc)
    req = sim.read_next()
    assert vor <= req.occurred_at <= nach


def test_raw_booking_request_ist_immutable():
    req = RawBookingRequest(
        booking_type=BookingType.GO,
        uid_hash="HASH",
        occurred_at=_T,
    )
    with pytest.raises((AttributeError, TypeError)):
        req.uid_hash = "ANDERER"  # type: ignore[misc]


# --- uid_hash ---


def test_hash_uid_ist_deterministisch():
    assert hash_uid("AABBCCDD") == hash_uid("AABBCCDD")


def test_hash_uid_verschiedene_uids_haben_verschiedene_hashes():
    assert hash_uid("AABBCCDD") != hash_uid("11223344")


def test_hash_uid_ist_sha256_hex():
    result = hash_uid("test")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_hash_uid_gross_klein_sensitiv():
    assert hash_uid("aabbccdd") != hash_uid("AABBCCDD")


# --- Protocol-Konformität ---


def test_simulated_reader_erfuellt_hardware_reader_protocol():
    sim: HardwareReader = SimulatedHardwareReader()
    sim.inject(BookingType.COME, "HASH", occurred_at=_T)
    req = sim.read_next()
    assert req.booking_type == BookingType.COME
    sim.close()


# --- EmptyUidError ---


def test_empty_uid_error_ist_runtime_error_subklasse():
    assert issubclass(EmptyUidError, RuntimeError)


def test_empty_uid_error_kann_als_runtime_error_gefangen_werden():
    with pytest.raises(RuntimeError):
        raise EmptyUidError("test")
