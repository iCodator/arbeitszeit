"""Integrationstests: SystemTimeMonitor — Zeitsprungprotokollierung.

V3 §9.3 / Regelwerk v3 §21: Zeitsprünge und manuelle Uhrzeitänderungen
müssen erkannt und in system_events protokolliert werden.

Tests injizieren kontrollierte Wall-Clock- und Monotonic-Clock-Werte,
um Sprünge reproduzierbar zu simulieren.
"""

import sqlite3
import sys
from collections.abc import Callable, Generator
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.time_monitor import (
    SystemTimeMonitor,
    load_threshold_from_config,
)

_T0_WALL = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)
_T0_MONO = 1000.0


def _make_clocks(
    wall_sequence: list[datetime], mono_sequence: list[float]
) -> tuple[Callable[[], datetime], Callable[[], float]]:
    """Erzeugt injizierbare Clock-Callables aus Sequenzlisten."""
    wall_iter = iter(wall_sequence)
    mono_iter = iter(mono_sequence)
    return lambda: next(wall_iter), lambda: next(mono_iter)


def _events(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = conn.execute("SELECT event_type, details_json FROM system_events ORDER BY id").fetchall()
    return [{"event_type": r["event_type"], "details_json": r["details_json"]} for r in rows]


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = tmp_path / "arbeitszeit.db"
    conn = open_connection(path)
    run_migrations(conn)
    conn.close()
    return path


@pytest.fixture
def conn(db: Path) -> Generator[sqlite3.Connection, None, None]:
    c = open_connection(db)
    yield c
    c.close()


def test_erster_aufruf_kein_ereignis(db: Path, conn: sqlite3.Connection) -> None:
    """Erster check()-Aufruf setzt nur den Basiszeitpunkt — kein Ereignis."""

    def wall_fn() -> datetime:
        return _T0_WALL

    def mono_fn() -> float:
        return _T0_MONO

    monitor = SystemTimeMonitor(
        db, threshold_seconds=60.0, _wall_clock=wall_fn, _mono_clock=mono_fn
    )
    monitor.check()
    assert _events(conn) == []


def test_normaler_ablauf_kein_ereignis(db: Path, conn: sqlite3.Connection) -> None:
    """Zwei aufeinanderfolgende Aufrufe ohne Sprung erzeugen kein Ereignis."""
    from datetime import timedelta

    wall_times = [_T0_WALL, _T0_WALL + timedelta(seconds=120)]
    mono_times = [_T0_MONO, _T0_MONO + 120.0]
    wall_fn, mono_fn = _make_clocks(wall_times, mono_times)
    monitor = SystemTimeMonitor(
        db, threshold_seconds=60.0, _wall_clock=wall_fn, _mono_clock=mono_fn
    )
    monitor.check()
    monitor.check()
    assert _events(conn) == []


def test_vorwaertssprung_wird_erkannt(db: Path, conn: sqlite3.Connection) -> None:
    """Wall-Clock springt 300s vorwärts bei nur 60s Monoton-Elapsed → TIME_JUMP_DETECTED."""
    from datetime import timedelta

    wall_times = [_T0_WALL, _T0_WALL + timedelta(seconds=360)]
    mono_times = [_T0_MONO, _T0_MONO + 60.0]
    wall_fn, mono_fn = _make_clocks(wall_times, mono_times)
    monitor = SystemTimeMonitor(
        db, threshold_seconds=60.0, _wall_clock=wall_fn, _mono_clock=mono_fn
    )
    monitor.check()
    monitor.check()
    evts = _events(conn)
    assert len(evts) == 1
    assert evts[0]["event_type"] == "TIME_JUMP_DETECTED"


def test_rueckwaertssprung_wird_erkannt(db: Path, conn: sqlite3.Connection) -> None:
    """Wall-Clock springt 300s zurück → MANUAL_TIME_CHANGE_DETECTED."""
    from datetime import timedelta

    wall_times = [_T0_WALL, _T0_WALL - timedelta(seconds=300)]
    mono_times = [_T0_MONO, _T0_MONO + 60.0]
    wall_fn, mono_fn = _make_clocks(wall_times, mono_times)
    monitor = SystemTimeMonitor(
        db, threshold_seconds=60.0, _wall_clock=wall_fn, _mono_clock=mono_fn
    )
    monitor.check()
    monitor.check()
    evts = _events(conn)
    assert len(evts) == 1
    assert evts[0]["event_type"] == "MANUAL_TIME_CHANGE_DETECTED"


def test_sprung_unter_schwellenwert_kein_ereignis(db: Path, conn: sqlite3.Connection) -> None:
    """Differenz unterhalb des Schwellenwerts (30s < 60s) → kein Ereignis."""
    from datetime import timedelta

    wall_times = [_T0_WALL, _T0_WALL + timedelta(seconds=90)]
    mono_times = [_T0_MONO, _T0_MONO + 60.0]
    wall_fn, mono_fn = _make_clocks(wall_times, mono_times)
    monitor = SystemTimeMonitor(
        db, threshold_seconds=60.0, _wall_clock=wall_fn, _mono_clock=mono_fn
    )
    monitor.check()
    monitor.check()
    assert _events(conn) == []


def test_details_json_enthaelt_diff_seconds(db: Path, conn: sqlite3.Connection) -> None:
    """Das Ereignis enthält diff_seconds im details_json."""
    import json as json_mod
    from datetime import timedelta

    wall_times = [_T0_WALL, _T0_WALL + timedelta(seconds=360)]
    mono_times = [_T0_MONO, _T0_MONO + 60.0]
    wall_fn, mono_fn = _make_clocks(wall_times, mono_times)
    monitor = SystemTimeMonitor(
        db, threshold_seconds=60.0, _wall_clock=wall_fn, _mono_clock=mono_fn
    )
    monitor.check()
    monitor.check()
    evts = _events(conn)
    details = json_mod.loads(str(evts[0]["details_json"]))
    assert "diff_seconds" in details
    assert abs(details["diff_seconds"] - 300.0) < 1.0


def test_load_threshold_from_config_fallback(db: Path) -> None:
    """Ohne system_config-Eintrag wird der Default-Schwellenwert zurückgegeben."""
    threshold = load_threshold_from_config(db, default=45.0)
    assert threshold == 45.0


def test_load_threshold_from_config_liest_wert(db: Path) -> None:
    """Wenn system_config den Schlüssel enthält, wird der konfigurierte Wert gelesen."""
    conn = open_connection(db)
    conn.execute(
        "INSERT INTO system_config "
        "(config_key, config_value_json, version, change_origin, changed_at) "
        "VALUES ('time_monitor.jump_threshold_seconds', '120', 1, 'MIGRATION', '2026-01-01')"
    )
    conn.close()
    threshold = load_threshold_from_config(db, default=60.0)
    assert threshold == 120.0
