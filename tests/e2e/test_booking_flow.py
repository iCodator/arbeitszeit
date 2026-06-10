import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import BookingStatus, BookingType
from arbeitszeit.domain.errors import InactiveCardError, UnknownCardError
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.hardware.simulator import SimulatedHardwareReader
from arbeitszeit.presentation.terminal_ui.booking_loop import process_booking

_UID_HASH = "aabbccdd"
_INACTIVE_UID_HASH = "deadbeef"


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = tmp_path / "arbeitszeit.db"
    conn = open_connection(path)
    run_migrations(conn)
    conn.close()
    return path


@pytest.fixture
def terminal_id(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO terminals (terminal_code, active, created_at) "
        "VALUES ('T01', 1, '2026-01-01') RETURNING id"
    ).fetchone()
    conn.close()
    return row["id"]


@pytest.fixture
def employee_id(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E001', 'Test', 'Nutzer', 1, '2026-01-01', '2026-01-01') RETURNING id"
    ).fetchone()
    conn.close()
    return row["id"]


@pytest.fixture
def card_id(db: Path, employee_id: int) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO rfid_cards "
        "(uid_hash, employee_id, status, valid_from, created_at) "
        "VALUES (?, ?, 'ACTIVE', '2026-01-01', '2026-01-01') RETURNING id",
        (_UID_HASH, employee_id),
    ).fetchone()
    conn.close()
    return row["id"]


@pytest.fixture
def inactive_card_id(db: Path, employee_id: int) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO rfid_cards "
        "(uid_hash, employee_id, status, valid_from, created_at) "
        "VALUES (?, ?, 'INACTIVE', '2026-01-01', '2026-01-01') RETURNING id",
        (_INACTIVE_UID_HASH, employee_id),
    ).fetchone()
    conn.close()
    return row["id"]


def _bookings(db: Path) -> list[dict]:
    conn = open_connection(db)
    rows = conn.execute(
        "SELECT booking_type, current_status FROM time_bookings ORDER BY id"
    ).fetchall()
    conn.close()
    return [{"type": r["booking_type"], "status": r["current_status"]} for r in rows]


def _audit_events(db: Path) -> list[str]:
    conn = open_connection(db)
    rows = conn.execute("SELECT event_type FROM audit_log ORDER BY id").fetchall()
    conn.close()
    return [r["event_type"] for r in rows]


# --- Erfolgreiche Buchungsabläufe ---


def test_come_go_ablauf(db, terminal_id, card_id):
    reader = SimulatedHardwareReader()
    now = datetime(2026, 5, 26, 8, 0, tzinfo=timezone.utc)
    reader.inject(BookingType.COME, _UID_HASH, now)
    result_come = process_booking(reader, db, terminal_id)
    assert result_come.status == BookingStatus.OPEN

    reader.inject(BookingType.GO, _UID_HASH, now.replace(hour=16))
    result_go = process_booking(reader, db, terminal_id)
    assert result_go.status in (BookingStatus.OK, BookingStatus.WARN)

    buchungen = _bookings(db)
    assert len(buchungen) == 2
    assert buchungen[0]["type"] == "COME"
    assert buchungen[1]["type"] == "GO"


def test_come_pause_go_ablauf(db, terminal_id, card_id):
    reader = SimulatedHardwareReader()
    base = datetime(2026, 5, 26, 8, 0, tzinfo=timezone.utc)
    reader.inject(BookingType.COME, _UID_HASH, base)
    reader.inject(BookingType.BREAK_START, _UID_HASH, base.replace(hour=12))
    reader.inject(BookingType.BREAK_END, _UID_HASH, base.replace(hour=12, minute=30))
    reader.inject(BookingType.GO, _UID_HASH, base.replace(hour=16))

    for _ in range(4):
        process_booking(reader, db, terminal_id)

    buchungen = _bookings(db)
    assert len(buchungen) == 4
    types = [b["type"] for b in buchungen]
    assert types == ["COME", "BREAK_START", "BREAK_END", "GO"]


def test_buchung_erzeugt_audit_log_eintrag(db, terminal_id, card_id):
    reader = SimulatedHardwareReader()
    reader.inject(BookingType.COME, _UID_HASH, datetime(2026, 5, 26, 8, 0, tzinfo=timezone.utc))
    process_booking(reader, db, terminal_id)

    events = _audit_events(db)
    assert "TIME_BOOKED" in events


def test_book_result_enthaelt_booking_id(db, terminal_id, card_id):
    reader = SimulatedHardwareReader()
    reader.inject(BookingType.COME, _UID_HASH, datetime(2026, 5, 26, 8, 0, tzinfo=timezone.utc))
    result = process_booking(reader, db, terminal_id)
    assert result.booking_id > 0


# --- Abweisung unbekannte RFID-Karte ---


def test_unbekannte_karte_wirft_unknown_card_error(db, terminal_id):
    reader = SimulatedHardwareReader()
    reader.inject(BookingType.COME, "unbekannter_hash", datetime.now(timezone.utc))
    with pytest.raises(UnknownCardError):
        process_booking(reader, db, terminal_id)


def test_unbekannte_karte_erstellt_audit_log(db, terminal_id):
    reader = SimulatedHardwareReader()
    reader.inject(BookingType.COME, "unbekannter_hash", datetime.now(timezone.utc))
    try:
        process_booking(reader, db, terminal_id)
    except UnknownCardError:
        pass

    events = _audit_events(db)
    assert "BOOKING_REJECTED_UNKNOWN_CARD" in events


def test_unbekannte_karte_speichert_keine_buchung(db, terminal_id):
    reader = SimulatedHardwareReader()
    reader.inject(BookingType.COME, "unbekannter_hash", datetime.now(timezone.utc))
    try:
        process_booking(reader, db, terminal_id)
    except UnknownCardError:
        pass

    assert len(_bookings(db)) == 0


# --- Abweisung inaktive Karte ---


def test_inaktive_karte_wirft_inactive_card_error(db, terminal_id, inactive_card_id):
    reader = SimulatedHardwareReader()
    reader.inject(BookingType.COME, _INACTIVE_UID_HASH, datetime.now(timezone.utc))
    with pytest.raises(InactiveCardError):
        process_booking(reader, db, terminal_id)


def test_inaktive_karte_erstellt_audit_log(db, terminal_id, inactive_card_id):
    reader = SimulatedHardwareReader()
    reader.inject(BookingType.COME, _INACTIVE_UID_HASH, datetime.now(timezone.utc))
    try:
        process_booking(reader, db, terminal_id)
    except InactiveCardError:
        pass

    events = _audit_events(db)
    assert "BOOKING_REJECTED_INACTIVE_CARD" in events


def test_inaktive_karte_speichert_keine_buchung(db, terminal_id, inactive_card_id):
    reader = SimulatedHardwareReader()
    reader.inject(BookingType.COME, _INACTIVE_UID_HASH, datetime.now(timezone.utc))
    try:
        process_booking(reader, db, terminal_id)
    except InactiveCardError:
        pass

    assert len(_bookings(db)) == 0


# --- APPLICATION_ERROR-Logging ---


from arbeitszeit.domain.errors import UnknownCardError
from arbeitszeit.infrastructure.time_monitor import SystemTimeMonitor
from arbeitszeit.presentation.terminal_ui.main import _run_one_cycle


def _make_monitor(db: Path) -> SystemTimeMonitor:
    monitor = SystemTimeMonitor(db, threshold_seconds=60.0)
    monitor.check()  # Basiszeitpunkt setzen
    return monitor


def test_unerwartete_exception_schreibt_application_error_in_system_events(
    db, terminal_id
):
    class BrokenReader:
        def read_next(self):
            raise RuntimeError("Gerätepanne simuliert")

        def close(self):
            pass

    _run_one_cycle(BrokenReader(), db, terminal_id, _make_monitor(db))

    conn = open_connection(db)
    events = conn.execute(
        "SELECT event_type, details_json FROM system_events "
        "WHERE event_type = 'APPLICATION_ERROR'"
    ).fetchall()
    conn.close()

    assert len(events) == 1
    details = json.loads(events[0]["details_json"])
    assert details["type"] == "RuntimeError"
    assert "Gerätepanne" in details["error"]


def test_domain_error_schreibt_kein_application_error(db, terminal_id):
    class DomainErrorReader:
        def read_next(self):
            raise UnknownCardError("Test-DomainError")

        def close(self):
            pass

    _run_one_cycle(DomainErrorReader(), db, terminal_id, _make_monitor(db))

    conn = open_connection(db)
    count = conn.execute(
        "SELECT COUNT(*) FROM system_events WHERE event_type = 'APPLICATION_ERROR'"
    ).fetchone()[0]
    conn.close()
    assert count == 0
