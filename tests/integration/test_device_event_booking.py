"""Integrationstests: device_events-Verkettung mit time_bookings."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import BookingType
from arbeitszeit.domain.errors import UnknownCardError
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.hardware.ports import RawBookingRequest
from arbeitszeit.presentation.terminal_ui.booking_loop import process_booking

_UID_HASH = "aabbccdd"
_NOW = datetime(2026, 6, 11, 8, 0, tzinfo=timezone.utc)


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
    return int(row["id"])


@pytest.fixture
def card_id(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E001', 'Test', 'User', 1, '2026-01-01', '2026-01-01') RETURNING id"
    ).fetchone()
    emp_id = row["id"]
    row = conn.execute(
        "INSERT INTO rfid_cards "
        "(uid_hash, employee_id, status, valid_from, created_at) "
        "VALUES (?, ?, 'ACTIVE', '2026-01-01', '2026-01-01') RETURNING id",
        (_UID_HASH, emp_id),
    ).fetchone()
    conn.close()
    return int(row["id"])


def _device_events(db: Path) -> list[dict[str, object]]:
    conn = open_connection(db)
    rows = conn.execute(
        "SELECT id, event_type, terminal_id, rfid_uid_hash FROM device_events ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _bookings_with_device_event(db: Path) -> list[dict[str, object]]:
    conn = open_connection(db)
    rows = conn.execute("SELECT id, device_event_id FROM time_bookings ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Test 1: Erfolgreiche Buchung ---


def test_erfolgreiche_buchung_schreibt_device_event_und_verknuepft_id(db: Path, terminal_id: int, card_id: int) -> None:
    process_booking(RawBookingRequest(BookingType.COME, _UID_HASH, _NOW), db, terminal_id)

    events = _device_events(db)
    assert len(events) == 1, "Genau ein device_events-Record erwartet"
    assert events[0]["event_type"] == "RFID_SCAN"
    assert events[0]["rfid_uid_hash"] == _UID_HASH
    assert events[0]["terminal_id"] == terminal_id

    bookings = _bookings_with_device_event(db)
    assert len(bookings) == 1, "Genau eine time_bookings-Zeile erwartet"
    assert (
        bookings[0]["device_event_id"] == events[0]["id"]
    ), "time_bookings.device_event_id muss auf device_events.id zeigen"


# --- Test 2: Abgelehnte Buchung (UnknownCard) ---


def test_unknown_card_schreibt_device_event_aber_keine_buchung(db: Path, terminal_id: int) -> None:
    with pytest.raises(UnknownCardError):
        process_booking(RawBookingRequest(BookingType.COME, "unbekannte_uid", _NOW), db, terminal_id)

    # device_events-Record existiert trotzdem (Geräteereignis war real)
    events = _device_events(db)
    assert len(events) == 1
    assert events[0]["event_type"] == "RFID_SCAN"

    # Keine time_bookings-Zeile
    bookings = _bookings_with_device_event(db)
    assert len(bookings) == 0


# --- Test 3: Fehler beim device_events-INSERT ---


def test_fehler_im_device_event_insert_verhindert_buchung(db: Path, terminal_id: int, card_id: int) -> None:
    # Fehler im device_event_repo.add() simulieren
    with patch(
        "arbeitszeit.infrastructure.db.repositories.device_event"
        ".SQLiteDeviceEventRepository.add",
        side_effect=Exception("DB-Fehler beim device_events-INSERT"),
    ):
        with pytest.raises(Exception, match="DB-Fehler"):
            process_booking(RawBookingRequest(BookingType.COME, _UID_HASH, _NOW), db, terminal_id)

    # Keine time_bookings-Zeile entstanden
    bookings = _bookings_with_device_event(db)
    assert len(bookings) == 0
