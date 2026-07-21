"""Tests für DebouncedHardwareReader (Anti-Doppel-Scan-Schutz)."""

__version__ = "1.0"

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.hardware.debounce import DebouncedHardwareReader
from arbeitszeit.infrastructure.hardware.simulator import SimulatedHardwareReader

_NOW = datetime(2025, 3, 10, 8, 0, 0, tzinfo=timezone.utc)
_UID_A = "uid_hash_aaaa"
_UID_B = "uid_hash_bbbb"

# Zu patchender Modulpfad für time.monotonic in debounce.py
_MOD = "arbeitszeit.infrastructure.hardware.debounce"


def _make_debounced() -> tuple[DebouncedHardwareReader, SimulatedHardwareReader]:
    sim = SimulatedHardwareReader()
    return DebouncedHardwareReader(sim), sim


# --- Grundverhalten ---


def test_erster_scan_wird_normal_verarbeitet() -> None:
    debounced, sim = _make_debounced()
    sim.inject(_UID_A, _NOW)

    with patch(f"{_MOD}.time") as mt:
        mt.monotonic.side_effect = [100.0]
        result = debounced.read_next()

    assert result.uid_hash == _UID_A
    assert sim.pending == 0


# --- Doppel-Scan-Erkennung (gleiche Karte, < DEBOUNCE_SECONDS) ---


def test_zweiter_scan_gleiche_karte_innerhalb_3s_wird_verworfen() -> None:
    # Drei Scans: A (t=100), A (t=101 — Duplikat), B (t=101).
    # Das zweite A wird verworfen; read_next() wartet auf B.
    # → Zwei read_next()-Aufrufe ergeben A und B (nicht A, A, B).
    debounced, sim = _make_debounced()
    sim.inject(_UID_A, _NOW)   # 1. Scan: wird verarbeitet
    sim.inject(_UID_A, _NOW)   # 2. Scan: Duplikat, wird verworfen
    sim.inject(_UID_B, _NOW)   # 3. Scan: andere Karte, wird verarbeitet

    with patch(f"{_MOD}.time") as mt:
        mt.monotonic.side_effect = [
            100.0,   # 1. read_next: erstes A akzeptiert
            101.0,   # 2. read_next (1. Versuch): zweites A → Duplikat (101−100=1<3)
            101.0,   # 2. read_next (2. Versuch): B akzeptiert
        ]
        result1 = debounced.read_next()
        result2 = debounced.read_next()

    assert result1.uid_hash == _UID_A
    assert result2.uid_hash == _UID_B
    assert sim.pending == 0  # alle drei Scans aus der Queue verbraucht


def test_doppel_scan_aktualisiert_nicht_den_timestamp() -> None:
    # Der Timestamp des letzten akzeptierten Scans soll nur bei akzeptierten
    # Scans fortgeschrieben werden — nicht bei verworfenen Duplikaten.
    # Sonst könnte ein Duplikat bei t=2 den Zeitraum auf t=2 verschieben
    # und den legitimen Scan bei t=4 ebenfalls blockieren (4−2=2 < 3).
    debounced, sim = _make_debounced()
    sim.inject(_UID_A, _NOW)   # t=0: akzeptiert → last=0
    sim.inject(_UID_A, _NOW)   # t=2: Duplikat → verworfen, last bleibt 0
    sim.inject(_UID_A, _NOW)   # t=4: 4−0=4 ≥ 3 → akzeptiert

    with patch(f"{_MOD}.time") as mt:
        mt.monotonic.side_effect = [0.0, 2.0, 4.0]
        result1 = debounced.read_next()
        result2 = debounced.read_next()

    assert result1.uid_hash == _UID_A
    assert result2.uid_hash == _UID_A
    assert sim.pending == 0


# --- Legitimer Folgescan (gleiche Karte, ≥ DEBOUNCE_SECONDS) ---


def test_gleiche_karte_nach_debounce_fenster_wird_erneut_verarbeitet() -> None:
    # 5 Sekunden Abstand > DEBOUNCE_SECONDS → kein Entprellungseffekt
    debounced, sim = _make_debounced()
    sim.inject(_UID_A, _NOW)
    sim.inject(_UID_A, _NOW)

    with patch(f"{_MOD}.time") as mt:
        mt.monotonic.side_effect = [100.0, 105.0]   # Δt = 5 s > 3 s
        result1 = debounced.read_next()
        result2 = debounced.read_next()

    assert result1.uid_hash == _UID_A
    assert result2.uid_hash == _UID_A


def test_grenzfall_exakt_debounce_sekunden_wird_nicht_verworfen() -> None:
    # Bei exakt DEBOUNCE_SECONDS (3.0 s) gilt die Bedingung < 3.0 NICHT.
    # Die Buchung muss durchkommen.
    debounced, sim = _make_debounced()
    sim.inject(_UID_A, _NOW)
    sim.inject(_UID_A, _NOW)

    with patch(f"{_MOD}.time") as mt:
        mt.monotonic.side_effect = [100.0, 103.0]   # Δt = 3.0 s — genau Grenze
        result1 = debounced.read_next()
        result2 = debounced.read_next()

    assert result1.uid_hash == _UID_A
    assert result2.uid_hash == _UID_A


# --- Verschiedene Karten (< DEBOUNCE_SECONDS) ---


def test_verschiedene_karten_innerhalb_3s_werden_beide_verarbeitet() -> None:
    # Verschiedene Karten → kein Entprellungsblock, auch wenn Abstand < 3 s
    debounced, sim = _make_debounced()
    sim.inject(_UID_A, _NOW)
    sim.inject(_UID_B, _NOW)

    with patch(f"{_MOD}.time") as mt:
        mt.monotonic.side_effect = [100.0, 100.5]   # Δt = 0.5 s < 3 s, aber andere Karte
        result1 = debounced.read_next()
        result2 = debounced.read_next()

    assert result1.uid_hash == _UID_A
    assert result2.uid_hash == _UID_B


# --- Protokollierung verworfener Doppel-Scans ---


def test_doppel_scan_erzeugt_info_log_eintrag(caplog: pytest.LogCaptureFixture) -> None:
    debounced, sim = _make_debounced()
    sim.inject(_UID_A, _NOW)   # akzeptiert
    sim.inject(_UID_A, _NOW)   # Duplikat → soll geloggt werden
    sim.inject(_UID_B, _NOW)   # damit read_next() etwas zurückgeben kann

    with patch(f"{_MOD}.time") as mt:
        mt.monotonic.side_effect = [100.0, 101.0, 101.0]
        with caplog.at_level(logging.INFO, logger=_MOD):
            debounced.read_next()   # verarbeitet A
            debounced.read_next()   # verwirft A, verarbeitet B

    log_messages = [r.message for r in caplog.records]
    assert any("Doppel-Scan" in msg for msg in log_messages)
    assert any("Δt=" in msg for msg in log_messages)


def test_akzeptierter_scan_erzeugt_keinen_log_eintrag(caplog: pytest.LogCaptureFixture) -> None:
    debounced, sim = _make_debounced()
    sim.inject(_UID_A, _NOW)

    with patch(f"{_MOD}.time") as mt:
        mt.monotonic.side_effect = [100.0]
        with caplog.at_level(logging.INFO, logger=_MOD):
            debounced.read_next()

    assert caplog.records == []


# --- close() delegiert an den zugrundeliegenden Reader ---


def test_close_schliesst_den_zugrundeliegenden_reader() -> None:
    mock_reader = MagicMock()
    debounced = DebouncedHardwareReader(mock_reader)
    debounced.close()

    mock_reader.close.assert_called_once()
