"""Tests für presentation/terminal_ui/booking_loop.py.

Testet die Integrationsschicht zwischen RawBookingRequest,
UnitOfWork (FakeUnitOfWork) und BookUseCase.

Getestete Aspekte:
  - process_booking(): erfolgreiche Buchungen mit verschiedenen Buchungstypen
  - process_booking(): Fehlerweiterleitung bei DomainError-Subklassen
  - process_booking(): device_event wird VOR der Buchung geschrieben, auch bei Fehler
  - process_booking(): uid_hash wird korrekt aus RawBookingRequest übernommen
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
from collections.abc import Callable
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.application.results import BookResult
from arbeitszeit.domain.entities import Employee, RfidCard, TimeBooking
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
from arbeitszeit.domain.value_objects import EmployeeId, RfidCardId, TerminalId, TimeBookingId
from arbeitszeit.infrastructure.hardware.ports import RawBookingRequest
from arbeitszeit.infrastructure.hardware.simulator import SimulatedHardwareReader
from arbeitszeit.presentation.terminal_ui.booking_loop import format_feedback, process_booking
from tests.application.fakes import FakeUnitOfWork

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
            id=EmployeeId(0),
            personnel_no="P001",
            first_name="Test",
            last_name="Mitarbeiter",
            is_active=employee_active,
        )
    )
    uow.rfid_card_repo.add(
        RfidCard(
            id=RfidCardId(0),
            employee_id=emp.id,
            uid_hash=uid_hash,
            status=card_status,
            valid_from=_DATE,
            valid_until=None,
            replaced_by_card_id=None,
        )
    )
    return uow


def _make_request(
    booking_type: BookingType,
    occurred_at: datetime | None = None,
    uid_hash: str = _UID_HASH,
) -> RawBookingRequest:
    return RawBookingRequest(
        booking_type=booking_type,
        uid_hash=uid_hash,
        occurred_at=occurred_at or _dt(8),
    )


# ---------------------------------------------------------------------------
# Fixture: patches open_connection + SQLiteUnitOfWork in booking_loop
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_uow(monkeypatch: pytest.MonkeyPatch) -> FakeUnitOfWork:
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
def fake_uow_factory(monkeypatch: pytest.MonkeyPatch) -> Callable[[FakeUnitOfWork], None]:
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

    def test_kommen_buchung_gibt_booking_result_zurueck(self, fake_uow: FakeUnitOfWork) -> None:
        result = process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        assert isinstance(result, BookResult)
        assert result.booking_id > 0

    def test_kommen_buchung_hat_status_open(self, fake_uow: FakeUnitOfWork) -> None:
        result = process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        assert result.status == BookingStatus.OPEN

    def test_gehen_buchung_nach_kommen_hat_status_ok(self, fake_uow: FakeUnitOfWork) -> None:
        fake_uow.time_booking_repo.add(
            TimeBooking(
                id=TimeBookingId(0),
                employee_id=EmployeeId(1),
                booking_type=BookingType.COME,
                booked_at=_dt(8),
                source=BookingSource.TERMINAL,
                status=BookingStatus.OPEN,
                terminal_id=TerminalId(_TERMINAL_ID),
                rfid_card_id=RfidCardId(1),
                device_event_id=None,
                note=None,
            )
        )
        result = process_booking(_make_request(BookingType.GO, _dt(13)), Path("dummy.db"), _TERMINAL_ID)

        assert result.status == BookingStatus.OK

    def test_uid_hash_vom_request_wird_korrekt_verwendet(
        self, fake_uow_factory: Callable[[FakeUnitOfWork], None]
    ) -> None:
        """process_booking muss den uid_hash aus dem RawBookingRequest unverändert an
        BookUseCase weitergeben; der Use Case schlägt damit in rfid_card_repo nach."""
        custom_hash = "custom_uid_hash_xyz"
        uow = _make_uow(uid_hash=custom_hash)
        fake_uow_factory(uow)

        result = process_booking(
            _make_request(BookingType.COME, uid_hash=custom_hash),
            Path("dummy.db"),
            _TERMINAL_ID,
        )

        assert result.status == BookingStatus.OPEN

    def test_terminal_id_wird_an_buchung_weitergegeben(self, fake_uow: FakeUnitOfWork) -> None:
        terminal_id = 42
        result = process_booking(_make_request(BookingType.COME), Path("dummy.db"), terminal_id)

        booking = fake_uow.time_booking_repo.get_by_id(result.booking_id)
        assert booking is not None
        assert booking.terminal_id == terminal_id

    def test_occurred_at_vom_request_wird_als_booked_at_gespeichert(
        self, fake_uow: FakeUnitOfWork
    ) -> None:
        occurred = _dt(7, 30)
        result = process_booking(_make_request(BookingType.COME, occurred), Path("dummy.db"), _TERMINAL_ID)

        booking = fake_uow.time_booking_repo.get_by_id(result.booking_id)
        assert booking is not None
        assert booking.booked_at == occurred

    def test_booking_source_ist_terminal(self, fake_uow: FakeUnitOfWork) -> None:
        result = process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        booking = fake_uow.time_booking_repo.get_by_id(result.booking_id)
        assert booking is not None
        assert booking.source == BookingSource.TERMINAL

    def test_uow_ist_nach_erfolgreicher_buchung_committed(self, fake_uow: FakeUnitOfWork) -> None:
        process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        assert fake_uow.committed

    def test_pause_start_buchung_nach_kommen_hat_status_open(
        self, fake_uow: FakeUnitOfWork
    ) -> None:
        fake_uow.time_booking_repo.add(
            TimeBooking(
                id=TimeBookingId(0),
                employee_id=EmployeeId(1),
                booking_type=BookingType.COME,
                booked_at=_dt(8),
                source=BookingSource.TERMINAL,
                status=BookingStatus.OPEN,
                terminal_id=TerminalId(_TERMINAL_ID),
                rfid_card_id=RfidCardId(1),
                device_event_id=None,
                note=None,
            )
        )
        result = process_booking(_make_request(BookingType.BREAK_START, _dt(12)), Path("dummy.db"), _TERMINAL_ID)

        assert result.status == BookingStatus.OPEN


# ---------------------------------------------------------------------------
# Tests: process_booking() — device_event wird immer geschrieben
# ---------------------------------------------------------------------------


class TestDeviceEventPersistenz:

    def test_device_event_wird_vor_buchung_geschrieben(self, fake_uow: FakeUnitOfWork) -> None:
        process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        assert len(fake_uow.device_event_repo._records) == 1

    def test_device_event_hat_rfid_scan_typ(self, fake_uow: FakeUnitOfWork) -> None:
        process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        event = fake_uow.device_event_repo._records[0]
        assert event["event_type"] == "RFID_SCAN"

    def test_device_event_uid_hash_stimmt_mit_request_ueberein(
        self, fake_uow: FakeUnitOfWork
    ) -> None:
        process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        event = fake_uow.device_event_repo._records[0]
        assert event["rfid_uid_hash"] == _UID_HASH

    def test_device_event_terminal_id_stimmt_ueberein(self, fake_uow: FakeUnitOfWork) -> None:
        process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        event = fake_uow.device_event_repo._records[0]
        assert event["terminal_id"] == _TERMINAL_ID

    def test_device_event_wird_auch_bei_domain_error_geschrieben(
        self, fake_uow_factory: Callable[[FakeUnitOfWork], None]
    ) -> None:
        """Auch bei UnknownCardError muss device_event persistiert sein.

        Dies ist Kern-Anforderung aus booking_loop.py: Das Geräteereignis ist real
        eingetreten, unabhängig vom fachlichen Buchungsergebnis.
        """
        uow = _make_uow(uid_hash="andere_karte")
        fake_uow_factory(uow)

        with pytest.raises(UnknownCardError):
            process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        assert len(uow.device_event_repo._records) == 1

    def test_buchung_referenziert_device_event_id(self, fake_uow: FakeUnitOfWork) -> None:
        result = process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

        booking = fake_uow.time_booking_repo.get_by_id(result.booking_id)
        assert booking is not None
        assert booking.device_event_id == fake_uow.device_event_repo._records[0]["id"]


# ---------------------------------------------------------------------------
# Tests: process_booking() — Fehlerweiterleitung (DomainErrors)
# ---------------------------------------------------------------------------


class TestProcessBookingFehler:

    def test_unbekannte_karte_loest_unknown_card_error(
        self, fake_uow_factory: Callable[[FakeUnitOfWork], None]
    ) -> None:
        uow = _make_uow(uid_hash="andere_karte")
        fake_uow_factory(uow)

        with pytest.raises(UnknownCardError):
            process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

    def test_inaktive_karte_loest_inactive_card_error(
        self, fake_uow_factory: Callable[[FakeUnitOfWork], None]
    ) -> None:
        uow = _make_uow(card_status=CardStatus.INACTIVE)
        fake_uow_factory(uow)

        with pytest.raises(InactiveCardError):
            process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)

    def test_ungueltige_sequenz_loest_invalid_booking_sequence_error(
        self, fake_uow_factory: Callable[[FakeUnitOfWork], None]
    ) -> None:
        """GO als erste Buchung des Tages muss InvalidBookingSequenceError werfen."""
        uow = _make_uow()
        fake_uow_factory(uow)

        with pytest.raises(InvalidBookingSequenceError):
            process_booking(_make_request(BookingType.GO, _dt(17)), Path("dummy.db"), _TERMINAL_ID)

    def test_domain_error_wird_nicht_abgefangen(
        self, fake_uow_factory: Callable[[FakeUnitOfWork], None]
    ) -> None:
        """process_booking fängt DomainErrors NICHT ab — das ist Aufgabe der terminal_ui."""
        uow = _make_uow(uid_hash="falsch")
        fake_uow_factory(uow)

        with pytest.raises(UnknownCardError):
            process_booking(_make_request(BookingType.COME), Path("dummy.db"), _TERMINAL_ID)


# ---------------------------------------------------------------------------
# Tests: format_feedback()
# ---------------------------------------------------------------------------


class TestFormatFeedback:

    def _result(self, status: BookingStatus) -> BookResult:
        return BookResult(
            booking_id=TimeBookingId(1),
            status=status,
            follow_up_case_ids=(),
            employee_first_name="Test",
            employee_last_name="Mitarbeiter",
            booking_type=BookingType.COME,
            booked_at=datetime(2025, 6, 16, 8, 0, tzinfo=timezone.utc),
        )

    def test_status_open_gibt_buchung_erfasst(self) -> None:
        msg = format_feedback(self._result(BookingStatus.OPEN))
        assert "Buchung erfasst." in msg

    def test_status_ok_gibt_buchung_erfasst(self) -> None:
        msg = format_feedback(self._result(BookingStatus.OK))
        assert "Buchung erfasst." in msg

    def test_status_warn_enthaelt_hinweis(self) -> None:
        msg = format_feedback(self._result(BookingStatus.WARN))
        assert "Hinweis" in msg

    def test_status_needs_review_enthaelt_pruefpflicht(self) -> None:
        msg = format_feedback(self._result(BookingStatus.NEEDS_REVIEW))
        assert "Prüfpflicht" in msg

    def test_warn_meldung_beginnt_mit_buchung_erfasst(self) -> None:
        msg = format_feedback(self._result(BookingStatus.WARN))
        assert "Buchung erfasst" in msg

    def test_needs_review_meldung_beginnt_mit_buchung_erfasst(self) -> None:
        msg = format_feedback(self._result(BookingStatus.NEEDS_REVIEW))
        assert "Buchung erfasst" in msg

    def test_format_enthaelt_name(self) -> None:
        msg = format_feedback(self._result(BookingStatus.OPEN))
        assert "Test Mitarbeiter" in msg

    def test_format_enthaelt_buchungsart(self) -> None:
        msg = format_feedback(self._result(BookingStatus.OPEN))
        assert "Beginn" in msg

    def test_alle_relevanten_status_haben_meldung(self) -> None:
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
            assert f"Status: {status.value}" not in msg, (
                f"Format-Fallback für {status} — fehlende Eintragung in _STATUS_MESSAGES?"
            )


# ---------------------------------------------------------------------------
# Tests: SimulatedHardwareReader — Grundverhalten (Sicherheitsnetz)
# ---------------------------------------------------------------------------


class TestSimulatedHardwareReaderGrundverhalten:
    """Minimale Tests die sicherstellen, dass SimulatedHardwareReader korrekt
    als HardwareReader-Protokoll-Implementierung für Tests funktioniert."""

    def test_inject_und_read_next_liefert_request(self) -> None:
        reader = SimulatedHardwareReader()
        occurred = _dt(9, 15)
        reader.inject(BookingType.COME, uid_hash="hash1", occurred_at=occurred)

        raw = reader.read_next()

        assert isinstance(raw, RawBookingRequest)
        assert raw.booking_type == BookingType.COME
        assert raw.uid_hash == "hash1"
        assert raw.occurred_at == occurred

    def test_leere_queue_loest_runtime_error(self) -> None:
        reader = SimulatedHardwareReader()

        with pytest.raises(RuntimeError):
            reader.read_next()

    def test_mehrere_requests_werden_in_reihenfolge_geliefert(self) -> None:
        reader = SimulatedHardwareReader()
        reader.inject(BookingType.COME, uid_hash="h1", occurred_at=_dt(8))
        reader.inject(BookingType.GO, uid_hash="h1", occurred_at=_dt(17))

        first = reader.read_next()
        second = reader.read_next()

        assert isinstance(first, RawBookingRequest)
        assert isinstance(second, RawBookingRequest)
        assert first.booking_type == BookingType.COME
        assert second.booking_type == BookingType.GO

    def test_pending_zaehler_stimmt(self) -> None:
        reader = SimulatedHardwareReader()
        assert reader.pending == 0
        reader.inject(BookingType.COME, uid_hash="h1")
        assert reader.pending == 1
        reader.read_next()
        assert reader.pending == 0
