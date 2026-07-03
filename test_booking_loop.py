"""Tests für presentation/terminal_ui/booking_loop.py.

Testet die Integrationsschicht zwischen HardwareReader (SimulatedHardwareReader),
UnitOfWork (FakeUnitOfWork) und BookUseCase.

Getestete Aspekte:
  - process_booking(): erfolgreiche Buchungen mit verschiedenen Buchungstypen
  - process_booking(): Fehlerweiterleitung bei DomainError-Subklassen
  - process_booking(): device_event wird VOR der Buchung geschrieben, auch bei Fehler
  - process_booking(): uid_hash wird korrekt vom Reader übernommen
  - format_feedback(): Statusmeldungen für alle BookingStatus-Werte

Design-Entscheidung: process_booking() öffnet intern eine SQLite-Verbindung
(open_connection) und baut SQLiteUnitOfWork auf. Um das zu vermeiden, werden
hier die internen Abhängigkeiten über Monkeypatching (pytest monkeypatch) ersetzt:
  - open_connection → gibt FakeSQLiteConnection zurück
  - SQLiteUnitOfWork → gibt FakeUnitOfWork zurück

Damit bleiben die Tests hermetisch ohne Dateisystem- oder DB-Zugriff.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from tests.application.fakes import FakeUnitOfWork

from arbeitszeit.application.results import BookResult
from arbeitszeit.domain.entities import Employee, RfidCard
from arbeitszeit.domain.enums import (
    BookingSource,
    BookingStatus,
    BookingType,
    CardStatus,
)
from arbeitszeit.domain.errors import (
    InactiveCardError,
    InvalidBookingSequenceError,
    UnknownCardError,
)
from arbeitszeit.infrastructure.hardware.simulator import SimulatedHardwareReader
from arbeitszeit.presentation.terminal_ui.booking_loop import format_feedback, process_booking

# ---------------------------------------------------------------------------
# Konstanten & Hilfsfunktionen
# ---------------------------------------------------------------------------

_DATE = date(2025, 6, 16)
_UID_HASH = "abc123hash"
_TERMINAL_ID = 1


def _dt(h: int, m: int = 0) -> datetime:
    return datetime(_DATE.year, _DATE.month, _DATE.day, h, m, tzinfo=timezone.utc)


def _make_uow(
    *,
    uid_hash: str = _UID_HASH,
    card_status: CardStatus = CardStatus.ACTIVE,
    employee_active: bool = True,
) -> FakeUnitOfWork:
    """Erzeugt FakeUnitOfWork mit einem Mitarbeiter und einer RFID-Karte."""
    uow = FakeUnitOfWork()
    emp = uow.employee_repo.add(
        Employee(
            id=0,
            personnel_no="P001",
            first_name="Test",
            last_name="Mitarbeiter",
            is_active=employee_active,
        )
    )
    uow.rfid_card_repo.add(
        RfidCard(
            id=0,
            employee_id=emp.id,
            uid_hash=uid_hash,
            status=card_status,
            valid_from=_DATE,
            valid_until=None,
            replaced_by_card_id=None,
        )
    )
    return uow


def _inject(
    reader: SimulatedHardwareReader,
    booking_type: BookingType,
    occurred_at: datetime | None = None,
) -> None:
    reader.inject(
        booking_type=booking_type,
        uid_hash=_UID_HASH,
        occurred_at=occurred_at or _dt(8),
    )


def _make_reader(
    booking_type: BookingType, occurred_at: datetime | None = None
) -> SimulatedHardwareReader:
    reader = SimulatedHardwareReader()
    _inject(reader, booking_type, occurred_at)
    return reader


# ---------------------------------------------------------------------------
# Fixture: patches open_connection + SQLiteUnitOfWork in booking_loop
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_uow(monkeypatch) -> FakeUnitOfWork:
    """Ersetzt open_connection und SQLiteUnitOfWork in booking_loop durch Fakes.

    Gibt die FakeUnitOfWork-Instanz zurück, die der Test für Assertions nutzen kann.
    """
    uow = _make_uow()
    fake_conn = MagicMock()

    monkeypatch.setattr(
        "arbeitszeit.presentation.terminal_ui.booking_loop.open_connection",
        lambda _path: fake_conn,
    )
    monkeypatch.setattr(
        "arbeitszeit.presentation.terminal_ui.booking_loop.SQLiteUnitOfWork",
        lambda _conn, _audit_conn: uow,
    )
    return uow


@pytest.fixture
def fake_uow_factory(monkeypatch):
    """Wie fake_uow, aber gibt eine Factory zurück um custom FakeUnitOfWork zu übergeben."""
    def _factory(uow: FakeUnitOfWork) -> None:
        fake_conn = MagicMock()
        monkeypatch.setattr(
            "arbeitszeit.presentation.terminal_ui.booking_loop.open_connection",
            lambda _path: fake_conn,
        )
        monkeypatch.setattr(
            "arbeitszeit.presentation.terminal_ui.booking_loop.SQLiteUnitOfWork",
            lambda _conn, _audit_conn: uow,
        )
    return _factory


# ---------------------------------------------------------------------------
# Tests: process_booking() — Erfolgreiche Buchungen
# ---------------------------------------------------------------------------


class TestProcessBookingErfolg:

    def test_kommen_buchung_gibt_booking_result_zurueck(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        result = process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        assert isinstance(result, BookResult)
        assert result.booking_id > 0

    def test_kommen_buchung_hat_status_open(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        result = process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        assert result.status == BookingStatus.OPEN

    def test_gehen_buchung_nach_kommen_hat_status_ok(self, fake_uow):
        # COME vorher in die FakeUnitOfWork schreiben
        from arbeitszeit.domain.entities import TimeBooking
        from arbeitszeit.domain.enums import BookingSource, BookingStatus
        fake_uow.time_booking_repo.add(
            TimeBooking(
                id=0,
                employee_id=1,
                booking_type=BookingType.COME,
                booked_at=_dt(8),
                source=BookingSource.TERMINAL,
                status=BookingStatus.OPEN,
                terminal_id=_TERMINAL_ID,
                rfid_card_id=1,
                device_event_id=None,
                note=None,
            )
        )
        reader = _make_reader(BookingType.GO, _dt(13))

        result = process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        assert result.status == BookingStatus.OK

    def test_uid_hash_vom_reader_wird_korrekt_verwendet(self, fake_uow_factory):
        """process_booking muss den uid_hash aus dem RawBookingRequest unverändert an
        BookUseCase weitergeben; der Use Case schlägt damit in rfid_card_repo nach."""
        custom_hash = "custom_uid_hash_xyz"
        uow = _make_uow(uid_hash=custom_hash)
        fake_uow_factory(uow)

        reader = SimulatedHardwareReader()
        reader.inject(
            booking_type=BookingType.COME,
            uid_hash=custom_hash,
            occurred_at=_dt(8),
        )

        result = process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        assert result.status == BookingStatus.OPEN

    def test_terminal_id_wird_an_buchung_weitergegeben(self, fake_uow):
        terminal_id = 42
        reader = _make_reader(BookingType.COME)

        result = process_booking(reader, Path("dummy.db"), terminal_id)

        booking = fake_uow.time_booking_repo.get_by_id(result.booking_id)
        assert booking is not None
        assert booking.terminal_id == terminal_id

    def test_occurred_at_vom_reader_wird_als_booked_at_gespeichert(self, fake_uow):
        occurred = _dt(7, 30)
        reader = SimulatedHardwareReader()
        reader.inject(BookingType.COME, uid_hash=_UID_HASH, occurred_at=occurred)

        result = process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        booking = fake_uow.time_booking_repo.get_by_id(result.booking_id)
        assert booking is not None
        assert booking.booked_at == occurred

    def test_booking_source_ist_terminal(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        result = process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        booking = fake_uow.time_booking_repo.get_by_id(result.booking_id)
        assert booking is not None
        assert booking.source == BookingSource.TERMINAL

    def test_uow_ist_nach_erfolgreicher_buchung_committed(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        assert fake_uow.committed

    def test_pause_start_buchung_nach_kommen_hat_status_open(self, fake_uow):
        from arbeitszeit.domain.entities import TimeBooking
        fake_uow.time_booking_repo.add(
            TimeBooking(
                id=0,
                employee_id=1,
                booking_type=BookingType.COME,
                booked_at=_dt(8),
                source=BookingSource.TERMINAL,
                status=BookingStatus.OPEN,
                terminal_id=_TERMINAL_ID,
                rfid_card_id=1,
                device_event_id=None,
                note=None,
            )
        )
        reader = _make_reader(BookingType.BREAK_START, _dt(12))

        result = process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        assert result.status == BookingStatus.OPEN


# ---------------------------------------------------------------------------
# Tests: process_booking() — device_event wird immer geschrieben
# ---------------------------------------------------------------------------


class TestDeviceEventPersistenz:

    def test_device_event_wird_vor_buchung_geschrieben(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        assert len(fake_uow.device_event_repo._records) == 1

    def test_device_event_hat_rfid_scan_typ(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        event = fake_uow.device_event_repo._records[0]
        assert event["event_type"] == "RFID_SCAN"

    def test_device_event_uid_hash_stimmt_mit_reader_ueberein(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        event = fake_uow.device_event_repo._records[0]
        assert event["rfid_uid_hash"] == _UID_HASH

    def test_device_event_terminal_id_stimmt_ueberein(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        event = fake_uow.device_event_repo._records[0]
        assert event["terminal_id"] == _TERMINAL_ID

    def test_device_event_wird_auch_bei_domain_error_geschrieben(self, fake_uow_factory):
        """Auch bei UnknownCardError muss device_event persistiert sein.

        Dies ist Kern-Anforderung aus booking_loop.py: Das Geräteereignis ist real
        eingetreten, unabhängig vom fachlichen Buchungsergebnis.
        """
        # UoW mit unbekannter Karte — der uid_hash stimmt nicht überein
        uow = _make_uow(uid_hash="andere_karte")
        fake_uow_factory(uow)

        reader = SimulatedHardwareReader()
        reader.inject(BookingType.COME, uid_hash=_UID_HASH, occurred_at=_dt(8))

        with pytest.raises(UnknownCardError):
            process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        # device_event muss trotzdem geschrieben worden sein
        assert len(uow.device_event_repo._records) == 1

    def test_buchung_referenziert_device_event_id(self, fake_uow):
        reader = _make_reader(BookingType.COME)

        result = process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

        booking = fake_uow.time_booking_repo.get_by_id(result.booking_id)
        assert booking is not None
        assert booking.device_event_id == fake_uow.device_event_repo._records[0]["id"]


# ---------------------------------------------------------------------------
# Tests: process_booking() — Fehlerweiterleitung (DomainErrors)
# ---------------------------------------------------------------------------


class TestProcessBookingFehler:

    def test_unbekannte_karte_loest_unknown_card_error(self, fake_uow_factory):
        uow = _make_uow(uid_hash="andere_karte")
        fake_uow_factory(uow)
        reader = SimulatedHardwareReader()
        reader.inject(BookingType.COME, uid_hash=_UID_HASH, occurred_at=_dt(8))

        with pytest.raises(UnknownCardError):
            process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

    def test_inaktive_karte_loest_inactive_card_error(self, fake_uow_factory):
        uow = _make_uow(card_status=CardStatus.INACTIVE)
        fake_uow_factory(uow)
        reader = _make_reader(BookingType.COME)

        with pytest.raises(InactiveCardError):
            process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

    def test_ungueltige_sequenz_loest_invalid_booking_sequence_error(self, fake_uow_factory):
        """GO als erste Buchung des Tages muss InvalidBookingSequenceError werfen."""
        uow = _make_uow()
        fake_uow_factory(uow)
        reader = _make_reader(BookingType.GO, _dt(17))

        with pytest.raises(InvalidBookingSequenceError):
            process_booking(reader, Path("dummy.db"), _TERMINAL_ID)

    def test_domain_error_wird_nicht_abgefangen(self, fake_uow_factory):
        """process_booking fängt DomainErrors NICHT ab — das ist Aufgabe der terminal_ui."""
        uow = _make_uow(uid_hash="falsch")
        fake_uow_factory(uow)
        reader = SimulatedHardwareReader()
        reader.inject(BookingType.COME, uid_hash=_UID_HASH, occurred_at=_dt(8))

        # UnknownCardError muss bis zum Aufrufer durchkommen
        with pytest.raises(UnknownCardError):
            process_booking(reader, Path("dummy.db"), _TERMINAL_ID)


# ---------------------------------------------------------------------------
# Tests: format_feedback()
# ---------------------------------------------------------------------------


class TestFormatFeedback:

    def _result(self, status: BookingStatus) -> BookResult:
        return BookResult(booking_id=1, status=status, follow_up_case_ids=())

    def test_status_open_gibt_buchung_erfasst(self):
        assert format_feedback(self._result(BookingStatus.OPEN)) == "Buchung erfasst."

    def test_status_ok_gibt_buchung_erfasst(self):
        assert format_feedback(self._result(BookingStatus.OK)) == "Buchung erfasst."

    def test_status_warn_enthaelt_hinweis(self):
        msg = format_feedback(self._result(BookingStatus.WARN))
        assert "Hinweis" in msg

    def test_status_needs_review_enthaelt_pruefpflicht(self):
        msg = format_feedback(self._result(BookingStatus.NEEDS_REVIEW))
        assert "Prüfpflicht" in msg

    def test_warn_meldung_beginnt_mit_buchung_erfasst(self):
        msg = format_feedback(self._result(BookingStatus.WARN))
        assert msg.startswith("Buchung erfasst")

    def test_needs_review_meldung_beginnt_mit_buchung_erfasst(self):
        msg = format_feedback(self._result(BookingStatus.NEEDS_REVIEW))
        assert msg.startswith("Buchung erfasst")

    def test_alle_relevanten_status_haben_meldung(self):
        """Kein BookingStatus der im Buchungsloop vorkommt darf ein leeres Fallback erzeugen."""
        relevante_status = [
            BookingStatus.OPEN,
            BookingStatus.OK,
            BookingStatus.WARN,
            BookingStatus.NEEDS_REVIEW,
        ]
        for status in relevante_status:
            msg = format_feedback(self._result(status))
            assert msg, f"Leere Meldung für Status {status}"
            # Kein roher Enum-Wert darf durchkommen
            assert f"Status: {status.value}" not in msg, (
                f"Format-Fallback für {status} — fehlende Eintragung in _STATUS_MESSAGES?"
            )


# ---------------------------------------------------------------------------
# Tests: SimulatedHardwareReader — Grundverhalten (Sicherheitsnetz)
# ---------------------------------------------------------------------------


class TestSimulatedHardwareReaderGrundverhalten:
    """Minimale Tests die sicherstellen, dass SimulatedHardwareReader korrekt
    als HardwareReader-Protokoll-Implementierung für Tests funktioniert."""

    def test_inject_und_read_next_liefert_request(self):
        reader = SimulatedHardwareReader()
        occurred = _dt(9, 15)
        reader.inject(BookingType.COME, uid_hash="hash1", occurred_at=occurred)

        request = reader.read_next()

        assert request.booking_type == BookingType.COME
        assert request.uid_hash == "hash1"
        assert request.occurred_at == occurred

    def test_leere_queue_loest_runtime_error(self):
        reader = SimulatedHardwareReader()

        with pytest.raises(RuntimeError):
            reader.read_next()

    def test_mehrere_requests_werden_in_reihenfolge_geliefert(self):
        reader = SimulatedHardwareReader()
        reader.inject(BookingType.COME, uid_hash="h1", occurred_at=_dt(8))
        reader.inject(BookingType.GO, uid_hash="h1", occurred_at=_dt(17))

        first = reader.read_next()
        second = reader.read_next()

        assert first.booking_type == BookingType.COME
        assert second.booking_type == BookingType.GO

    def test_pending_zaehler_stimmt(self):
        reader = SimulatedHardwareReader()
        assert reader.pending == 0
        reader.inject(BookingType.COME, uid_hash="h1")
        assert reader.pending == 1
        reader.read_next()
        assert reader.pending == 0
