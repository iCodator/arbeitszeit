import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import BookingType
from arbeitszeit.infrastructure.hardware import (
    AdminActionRequest,
    EmptyUidError,
    HardwareReader,
    RawBookingRequest,
    SimulatedHardwareReader,
    hash_uid,
)
from arbeitszeit.domain.enums import AdminAction

_T = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)


# --- SimulatedHardwareReader ---


def test_inject_und_read_next_liefert_richtigen_buchungstyp() -> None:
    sim = SimulatedHardwareReader()
    sim.inject(BookingType.COME, "HASH001", occurred_at=_T)
    req = sim.read_next()
    assert isinstance(req, RawBookingRequest)
    assert req.booking_type == BookingType.COME
    assert req.uid_hash == "HASH001"
    assert req.occurred_at == _T


def test_inject_reihenfolge_wird_eingehalten() -> None:
    sim = SimulatedHardwareReader()
    sim.inject(BookingType.COME, "HASH_A", occurred_at=_T)
    sim.inject(BookingType.GO, "HASH_B", occurred_at=_T)
    first = sim.read_next()
    second = sim.read_next()
    assert isinstance(first, RawBookingRequest)
    assert isinstance(second, RawBookingRequest)
    assert first.booking_type == BookingType.COME
    assert second.booking_type == BookingType.GO


def test_leere_queue_wirft_runtime_error() -> None:
    sim = SimulatedHardwareReader()
    with pytest.raises(RuntimeError):
        sim.read_next()


def test_pending_zaehlt_korrekt() -> None:
    sim = SimulatedHardwareReader()
    assert sim.pending == 0
    sim.inject(BookingType.GO, "H1")
    sim.inject(BookingType.COME, "H2")
    assert sim.pending == 2
    sim.read_next()
    assert sim.pending == 1


def test_close_ist_idempotent() -> None:
    sim = SimulatedHardwareReader()
    sim.inject(BookingType.COME, "HASH", occurred_at=_T)
    sim.close()
    sim.close()  # kein Fehler


def test_occurred_at_wird_gesetzt_wenn_nicht_angegeben() -> None:
    sim = SimulatedHardwareReader()
    vor = datetime.now(timezone.utc)
    sim.inject(BookingType.COME, "HASH")
    nach = datetime.now(timezone.utc)
    req = sim.read_next()
    assert isinstance(req, RawBookingRequest)
    assert vor <= req.occurred_at <= nach


def test_raw_booking_request_ist_immutable() -> None:
    req = RawBookingRequest(
        booking_type=BookingType.GO,
        uid_hash="HASH",
        occurred_at=_T,
    )
    with pytest.raises((AttributeError, TypeError)):
        req.uid_hash = "ANDERER"  # type: ignore[misc]


# --- uid_hash ---


def test_hash_uid_ist_deterministisch() -> None:
    assert hash_uid("AABBCCDD") == hash_uid("AABBCCDD")


def test_hash_uid_verschiedene_uids_haben_verschiedene_hashes() -> None:
    assert hash_uid("AABBCCDD") != hash_uid("11223344")


def test_hash_uid_ist_sha256_hex() -> None:
    result = hash_uid("test")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_hash_uid_gross_klein_sensitiv() -> None:
    assert hash_uid("aabbccdd") != hash_uid("AABBCCDD")


# --- Protocol-Konformität ---


def test_simulated_reader_erfuellt_hardware_reader_protocol() -> None:
    sim = SimulatedHardwareReader()
    assert isinstance(sim, HardwareReader)
    sim.inject(BookingType.COME, "HASH", occurred_at=_T)
    req = sim.read_next()
    assert isinstance(req, RawBookingRequest)
    assert req.booking_type == BookingType.COME
    sim.close()


def test_inject_admin_action_und_read_next_liefert_admin_action_request() -> None:
    sim = SimulatedHardwareReader()
    sim.inject_admin_action(AdminAction.STOP)
    req = sim.read_next()
    assert isinstance(req, AdminActionRequest)
    assert req.action == AdminAction.STOP


def test_inject_rfid_uid_hash_und_read_rfid_uid_hash() -> None:
    sim = SimulatedHardwareReader()
    sim.inject_rfid_uid_hash("deadbeef1234")
    assert sim.read_rfid_uid_hash() == "deadbeef1234"


def test_read_rfid_uid_hash_leere_queue_loest_runtime_error() -> None:
    sim = SimulatedHardwareReader()
    with pytest.raises(RuntimeError):
        sim.read_rfid_uid_hash()


def test_gemischte_queue_reihenfolge_wird_eingehalten() -> None:
    sim = SimulatedHardwareReader()
    sim.inject(BookingType.COME, "HASH_A", occurred_at=_T)
    sim.inject_admin_action(AdminAction.RESTART)
    first = sim.read_next()
    second = sim.read_next()
    assert isinstance(first, RawBookingRequest)
    assert isinstance(second, AdminActionRequest)
    assert second.action == AdminAction.RESTART


# --- EmptyUidError ---


def test_empty_uid_error_ist_runtime_error_subklasse() -> None:
    assert issubclass(EmptyUidError, RuntimeError)


def test_empty_uid_error_kann_als_runtime_error_gefangen_werden() -> None:
    with pytest.raises(RuntimeError):
        raise EmptyUidError("test")
