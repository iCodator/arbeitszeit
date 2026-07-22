import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.hardware import (
    EmptyUidError,
    HardwareReader,
    RawBookingRequest,
    SimulatedHardwareReader,
    hash_uid,
)

_T = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)


# --- SimulatedHardwareReader ---


def test_inject_und_read_next_liefert_richtigen_request() -> None:
    sim = SimulatedHardwareReader()
    sim.inject("HASH001", occurred_at=_T)
    req = sim.read_next()
    assert req.uid_hash == "HASH001"
    assert req.occurred_at == _T


def test_inject_reihenfolge_wird_eingehalten() -> None:
    sim = SimulatedHardwareReader()
    sim.inject("HASH_A", occurred_at=_T)
    sim.inject("HASH_B", occurred_at=_T)
    assert sim.read_next().uid_hash == "HASH_A"
    assert sim.read_next().uid_hash == "HASH_B"


def test_leere_queue_wirft_runtime_error() -> None:
    sim = SimulatedHardwareReader()
    with pytest.raises(RuntimeError):
        sim.read_next()


def test_pending_zaehlt_korrekt() -> None:
    sim = SimulatedHardwareReader()
    assert sim.pending == 0
    sim.inject("H1")
    sim.inject("H2")
    assert sim.pending == 2
    sim.read_next()
    assert sim.pending == 1


def test_close_ist_idempotent() -> None:
    sim = SimulatedHardwareReader()
    sim.inject("HASH", occurred_at=_T)
    sim.close()
    sim.close()  # kein Fehler


def test_occurred_at_wird_gesetzt_wenn_nicht_angegeben() -> None:
    sim = SimulatedHardwareReader()
    vor = datetime.now(timezone.utc)
    sim.inject("HASH")
    nach = datetime.now(timezone.utc)
    req = sim.read_next()
    assert vor <= req.occurred_at <= nach


def test_raw_booking_request_ist_immutable() -> None:
    req = RawBookingRequest(
        uid_hash="HASH",
        occurred_at=_T,
    )
    with pytest.raises((AttributeError, TypeError)):
        req.uid_hash = "ANDERER"  # type: ignore[misc]


# --- uid_hash ---


def test_hash_uid_ohne_pepper_wirft_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RFID_PEPPER", raising=False)
    with pytest.raises(ValueError, match="RFID_PEPPER"):
        hash_uid("AABBCCDD")


def test_hash_uid_ist_pepper_abhaengig(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RFID_PEPPER", "secret1")
    hash1 = hash_uid("AABBCCDD")
    monkeypatch.setenv("RFID_PEPPER", "secret2")
    hash2 = hash_uid("AABBCCDD")
    assert hash1 != hash2


def test_hash_uid_ist_deterministisch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RFID_PEPPER", "testsecret")
    assert hash_uid("AABBCCDD") == hash_uid("AABBCCDD")


def test_hash_uid_verschiedene_uids_haben_verschiedene_hashes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RFID_PEPPER", "testsecret")
    assert hash_uid("AABBCCDD") != hash_uid("11223344")


def test_hash_uid_ist_hmac_sha256_hex64(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RFID_PEPPER", "testsecret")
    result = hash_uid("test")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_hash_uid_gross_klein_sensitiv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RFID_PEPPER", "testsecret")
    assert hash_uid("aabbccdd") != hash_uid("AABBCCDD")


# --- Protocol-Konformität ---


def test_simulated_reader_erfuellt_hardware_reader_protocol() -> None:
    sim = SimulatedHardwareReader()
    assert isinstance(sim, HardwareReader)
    sim.inject("HASH", occurred_at=_T)
    req = sim.read_next()
    assert req.uid_hash == "HASH"
    sim.close()


# --- EmptyUidError ---


def test_empty_uid_error_ist_runtime_error_subklasse() -> None:
    assert issubclass(EmptyUidError, RuntimeError)


def test_empty_uid_error_kann_als_runtime_error_gefangen_werden() -> None:
    with pytest.raises(RuntimeError):
        raise EmptyUidError("test")
