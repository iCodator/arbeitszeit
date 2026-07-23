__version__ = "1.4"

import json
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
from arbeitszeit.application.commands import BookCommand
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.application.use_cases.book_time import BookUseCase, derive_booking_type
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import (
    Employee,
    RfidCard,
    TimeBooking,
    WorkScheduleVersion,
)
from arbeitszeit.domain.enums import (
    BookingSource,
    BookingStatus,
    BookingType,
    CardStatus,
    ChangeOrigin,
    ReviewCaseType,
    ScopeType,
)
from arbeitszeit.domain.errors import (
    InactiveCardError,
    InactiveEmployeeError,
    InvalidBookingSequenceError,
    NotFoundError,
    UnknownCardError,
)
from arbeitszeit.domain.value_objects import (
    EmployeeId,
    RfidCardId,
    TerminalId,
    TimeBookingId,
    WorkScheduleVersionId,
)
from tests.application.fakes import FakeUnitOfWork

_DATE = date(2025, 3, 10)
_YESTERDAY = _DATE - timedelta(days=1)


def _T(h: int, m: int = 0) -> datetime:
    return datetime(_DATE.year, _DATE.month, _DATE.day, h, m, tzinfo=timezone.utc)


def _TY(h: int, m: int = 0) -> datetime:
    return datetime(_YESTERDAY.year, _YESTERDAY.month, _YESTERDAY.day, h, m, tzinfo=timezone.utc)


def _as_uow(uow: FakeUnitOfWork) -> UnitOfWork:
    return cast(UnitOfWork, uow)


def _make_uow(
    employee_active: bool = True, card_status: CardStatus = CardStatus.ACTIVE
) -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    emp = uow.employee_repo.add(
        Employee(
            id=EmployeeId(0),
            personnel_no="E001",
            first_name="Anna",
            last_name="Muster",
            is_active=employee_active,
        )
    )
    uow.rfid_card_repo.add(
        RfidCard(
            id=RfidCardId(0),
            employee_id=emp.id,
            uid_hash="abc123",
            status=card_status,
            valid_from=_DATE,
            valid_until=None,
            replaced_by_card_id=None,
        )
    )
    return uow


def _cmd(**overrides: Any) -> BookCommand:
    defaults = dict(
        uid_hash="abc123",
        terminal_id=1,
        booked_at=_T(8),
        device_event_id=None,
        source=BookingSource.TERMINAL,
    )
    return BookCommand(**{**defaults, **overrides})


def _add_booking(uow: FakeUnitOfWork, booking_type: BookingType, hour: int) -> TimeBooking:
    return uow.time_booking_repo.add(
        TimeBooking(
            id=TimeBookingId(0),
            employee_id=EmployeeId(1),
            booking_type=booking_type,
            booked_at=_T(hour),
            source=BookingSource.TERMINAL,
            status=BookingStatus.OPEN,
            terminal_id=TerminalId(1),
            rfid_card_id=RfidCardId(1),
            device_event_id=None,
            note=None,
        )
    )


def _add_booking_at(uow: FakeUnitOfWork, booking_type: BookingType, dt: datetime) -> TimeBooking:
    return uow.time_booking_repo.add(
        TimeBooking(
            id=TimeBookingId(0),
            employee_id=EmployeeId(1),
            booking_type=booking_type,
            booked_at=dt,
            source=BookingSource.TERMINAL,
            status=BookingStatus.OPEN,
            terminal_id=TerminalId(1),
            rfid_card_id=RfidCardId(1),
            device_event_id=None,
            note=None,
        )
    )


def _add_global_schedule(
    uow: FakeUnitOfWork,
    weekday: int,
    start: time,
    end: time,
) -> None:
    uow.work_schedule_repo.add(
        WorkScheduleVersion(
            id=WorkScheduleVersionId(0),
            scope_type=ScopeType.GLOBAL,
            scope_employee_id=None,
            weekday=weekday,
            start_time=start,
            end_time=end,
            valid_from=date(2000, 1, 1),
            valid_until=None,
            change_origin=ChangeOrigin.SYSTEM_SEED,
            changed_by_user_id=None,
        )
    )


# --- Fehlerbehandlung Karte / Mitarbeiter ---


def test_unbekannte_uid_loest_unknown_card_error() -> None:
    uow = _make_uow()
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(UnknownCardError):
        uc.execute(_cmd(uid_hash="unknown"))


def test_inaktive_karte_loest_inactive_card_error() -> None:
    uow = _make_uow(card_status=CardStatus.INACTIVE)
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(InactiveCardError):
        uc.execute(_cmd())


def test_inaktiver_mitarbeiter_loest_inactive_employee_error() -> None:
    uow = _make_uow(employee_active=False)
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd())


def test_fehlender_mitarbeiterdatensatz_loest_not_found_error() -> None:
    uow = _make_uow()
    uow.employee_repo._store.clear()
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(NotFoundError):
        uc.execute(_cmd())


# --- Sequenzfehler ---


def test_fuenfter_scan_loest_invalid_sequence_error() -> None:
    """Fünfter RFID-Scan (nach abgeschlossenem Tagesablauf) wirft InvalidBookingSequenceError."""
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    _add_booking(uow, BookingType.BREAK_START, 10)
    _add_booking(uow, BookingType.BREAK_END, 11)
    _add_booking(uow, BookingType.GO, 17)
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(InvalidBookingSequenceError):
        uc.execute(_cmd(booked_at=_T(18)))


# --- Statusbestimmung ---


def test_come_buchung_hat_status_open() -> None:
    uow = _make_uow()
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(booked_at=_T(8)))  # leere History → COME

    assert result.status == BookingStatus.OPEN
    assert result.follow_up_case_ids == ()
    assert uow.committed


def test_go_ohne_compliance_flags_hat_status_ok() -> None:
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    _add_booking(uow, BookingType.BREAK_START, 9)
    _add_booking(uow, BookingType.BREAK_END, 9)  # 0-min Pause → netto = brutto = 5h
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(booked_at=_T(13)))  # 4. Scan → GO

    assert result.status == BookingStatus.OK
    assert result.follow_up_case_ids == ()


def test_break_start_hat_status_open() -> None:
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(booked_at=_T(12)))  # COME in History → BREAK_START

    assert result.status == BookingStatus.OPEN


def test_break_end_nach_kurzer_pause_hat_status_ok() -> None:
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    _add_booking(uow, BookingType.BREAK_START, 12)
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(booked_at=_T(12, 30)))  # COME+BREAK_START in History → BREAK_END

    assert result.status == BookingStatus.OK


def test_go_nach_mehr_als_8h_hat_status_warn() -> None:
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 7)
    _add_booking(uow, BookingType.BREAK_START, 9)
    _add_booking(uow, BookingType.BREAK_END, 9)  # 0-min Pause → Schichtlänge unverändert
    uc = BookUseCase(_as_uow(uow))

    go_at = _T(7) + timedelta(hours=8, minutes=30)
    result = uc.execute(_cmd(booked_at=go_at))  # 4. Scan → GO

    assert result.status == BookingStatus.WARN
    assert len(result.follow_up_case_ids) > 0


def test_go_nach_mehr_als_10h_hat_status_needs_review() -> None:
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 7)
    _add_booking(uow, BookingType.BREAK_START, 9)
    _add_booking(uow, BookingType.BREAK_END, 9)  # 0-min Pause
    uc = BookUseCase(_as_uow(uow))

    go_at = _T(7) + timedelta(hours=10, minutes=30)
    result = uc.execute(_cmd(booked_at=go_at))  # 4. Scan → GO

    assert result.status == BookingStatus.NEEDS_REVIEW
    assert len(result.follow_up_case_ids) > 0


def test_buchung_wird_trotz_warn_gespeichert() -> None:
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 7)
    _add_booking(uow, BookingType.BREAK_START, 9)
    _add_booking(uow, BookingType.BREAK_END, 9)  # 0-min Pause
    uc = BookUseCase(_as_uow(uow))

    go_at = _T(7) + timedelta(hours=8, minutes=30)
    result = uc.execute(_cmd(booked_at=go_at))  # 4. Scan → GO

    saved = uow.time_booking_repo.get_by_id(result.booking_id)
    assert saved is not None
    assert saved.status == BookingStatus.WARN


# --- Audit-Log ---


def test_audit_log_eintrag_vorhanden() -> None:
    uow = _make_uow()
    uc = BookUseCase(_as_uow(uow))

    uc.execute(_cmd())

    assert len(uow.audit_log_repo.entries) == 1
    entry = uow.audit_log_repo.entries[0]
    assert entry.event_type == audit_events.TIME_BOOKED
    assert entry.employee_id == 1


# --- device_event_id wird durchgereicht ---


def test_device_event_id_wird_in_buchung_gespeichert() -> None:
    uow = _make_uow()
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(device_event_id=42))

    saved = uow.time_booking_repo.get_by_id(result.booking_id)
    assert saved is not None
    assert saved.device_event_id == 42


# --- Abweisungsprotokoll ---


def test_unbekannte_karte_schreibt_audit_log() -> None:
    uow = _make_uow()
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(UnknownCardError):
        uc.execute(_cmd(uid_hash="unbekannt"))

    entries = [
        e
        for e in uow.audit_log_repo.entries
        if e.event_type == audit_events.BOOKING_REJECTED_UNKNOWN_CARD
    ]
    assert len(entries) == 1


def test_unbekannte_karte_audit_log_nur_hash_praefix() -> None:
    """BOOKING_REJECTED_UNKNOWN_CARD darf nur uid_hash_prefix (8 Zeichen) loggen."""
    uow = _make_uow()
    uid = "deadbeef" * 8  # 64 Hex-Zeichen wie SHA-256
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(UnknownCardError):
        uc.execute(_cmd(uid_hash=uid))

    entries = [
        e
        for e in uow.audit_log_repo.entries
        if e.event_type == audit_events.BOOKING_REJECTED_UNKNOWN_CARD
    ]
    details = json.loads(entries[0].details_json)
    assert details.get("uid_hash_prefix") == uid[:8]
    assert "uid_hash" not in details


def test_inaktive_karte_schreibt_audit_log() -> None:
    uow = _make_uow(card_status=CardStatus.INACTIVE)
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(InactiveCardError):
        uc.execute(_cmd())

    entries = [
        e
        for e in uow.audit_log_repo.entries
        if e.event_type == audit_events.BOOKING_REJECTED_INACTIVE_CARD
    ]
    assert len(entries) == 1


# --- Ruhezeitprüfung (V3 §7.9 / ArbZG §5) ---


def test_go_nach_weniger_als_11h_ruhezeit_hat_status_needs_review() -> None:
    _YESTERDAY = _DATE - timedelta(days=1)

    def _TY(h: int) -> datetime:
        return datetime(
            _YESTERDAY.year, _YESTERDAY.month, _YESTERDAY.day, h, 0, tzinfo=timezone.utc
        )

    uow = _make_uow()
    # Vortag: COME 08:00 → GO 20:00
    _add_booking_at(uow, BookingType.COME, _TY(8))
    _add_booking_at(uow, BookingType.GO, _TY(20))
    # Heute: vollständige Sequenz bis vor GO (nur 10h Ruhezeit nach 20:00 gestern)
    _add_booking_at(uow, BookingType.COME, _T(6))
    _add_booking_at(uow, BookingType.BREAK_START, _T(9))
    _add_booking_at(uow, BookingType.BREAK_END, _T(9))  # 0-min Pause
    uc = BookUseCase(_as_uow(uow))

    # GO heute (4. Scan) → Ruhezeitprüfung: 20:00 → 06:00 = 10h < 11h → NEEDS_REVIEW
    result = uc.execute(_cmd(booked_at=_T(14)))

    assert result.status == BookingStatus.NEEDS_REVIEW
    cases = uow.review_case_repo.list_open_for_employee(1)
    assert any(c.case_type == ReviewCaseType.POSSIBLE_REST_VIOLATION for c in cases)


# --- Regelzeitfenster (Regelwerk §9/§10) ---


def test_come_ausserhalb_regelzeitfenster_erzeugt_review_case() -> None:
    # _DATE = 2025-03-10, isoweekday = 1 (Montag)
    uow = _make_uow()
    _add_global_schedule(uow, weekday=1, start=time(8, 0), end=time(17, 0))
    uc = BookUseCase(_as_uow(uow))

    # COME um 06:00 – vor Fensterbeginn 08:00 (leere History → COME)
    result = uc.execute(_cmd(booked_at=_T(6)))

    assert result.status == BookingStatus.OPEN
    assert len(result.follow_up_case_ids) > 0
    cases = uow.review_case_repo.list_open_for_employee(1)
    assert any(c.case_type == ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW for c in cases)


# --- Offene Vortagsschicht ---


def test_offene_vortagsschicht_erzeugt_audit_log_eintrag() -> None:
    uow = _make_uow()
    # Vortag: COME ohne GO — offene Schicht
    _add_booking_at(uow, BookingType.COME, _TY(8))
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(booked_at=_T(8)))  # leere Heute-History → COME

    # Buchung muss trotzdem erfolgreich sein
    assert result.status == BookingStatus.OPEN
    saved = uow.time_booking_repo.get_by_id(result.booking_id)
    assert saved is not None
    assert saved.booking_type == BookingType.COME

    # Audit-Log-Eintrag für offene Vortagsschicht muss vorhanden sein
    anomalie_entries = [
        e
        for e in uow.audit_log_repo.entries
        if e.event_type == audit_events.OPEN_SHIFT_PREVIOUS_DAY_DETECTED
    ]
    assert len(anomalie_entries) == 1
    details = json.loads(anomalie_entries[0].details_json)
    assert details["employee_id"] == 1
    assert details["previous_day_date"] == _YESTERDAY.isoformat()
    assert details["last_known_booking_type"] == BookingType.COME.value
    assert "last_known_booking_at" in details


def test_korrekt_abgeschlossener_vortag_erzeugt_kein_sonderaudit() -> None:
    uow = _make_uow()
    # Vortag: vollständiger Zyklus COME → GO
    _add_booking_at(uow, BookingType.COME, _TY(8))
    _add_booking_at(uow, BookingType.GO, _TY(17))
    uc = BookUseCase(_as_uow(uow))

    uc.execute(_cmd(booked_at=_T(8)))

    anomalie_entries = [
        e
        for e in uow.audit_log_repo.entries
        if e.event_type == audit_events.OPEN_SHIFT_PREVIOUS_DAY_DETECTED
    ]
    assert len(anomalie_entries) == 0


def test_kein_vortag_erzeugt_kein_sonderaudit() -> None:
    uow = _make_uow()
    # Keine Buchungen am Vortag
    uc = BookUseCase(_as_uow(uow))

    uc.execute(_cmd(booked_at=_T(8)))

    anomalie_entries = [
        e
        for e in uow.audit_log_repo.entries
        if e.event_type == audit_events.OPEN_SHIFT_PREVIOUS_DAY_DETECTED
    ]
    assert len(anomalie_entries) == 0


# --- derive_booking_type ---


def test_derive_leere_sequenz_ergibt_come() -> None:
    assert derive_booking_type([]) == BookingType.COME


def test_derive_nach_come_ergibt_break_start() -> None:
    assert derive_booking_type([BookingType.COME]) == BookingType.BREAK_START


def test_derive_nach_come_break_start_ergibt_break_end() -> None:
    assert derive_booking_type([BookingType.COME, BookingType.BREAK_START]) == BookingType.BREAK_END


def test_derive_nach_come_break_start_break_end_ergibt_go() -> None:
    assert derive_booking_type(
        [BookingType.COME, BookingType.BREAK_START, BookingType.BREAK_END]
    ) == BookingType.GO


def test_derive_nach_vollstaendigem_tag_wirft_invalid_sequence_error() -> None:
    with pytest.raises(InvalidBookingSequenceError):
        derive_booking_type(
            [BookingType.COME, BookingType.BREAK_START, BookingType.BREAK_END, BookingType.GO]
        )


# --- derive_booking_type: Sollzeit-Ausnahmeregel (§ 4 ArbZG) ---


def _make_schedule(start: time, end: time) -> WorkScheduleVersion:
    return WorkScheduleVersion(
        id=WorkScheduleVersionId(0),
        scope_type=ScopeType.GLOBAL,
        scope_employee_id=None,
        weekday=1,
        start_time=start,
        end_time=end,
        valid_from=date(2000, 1, 1),
        valid_until=None,
        change_origin=ChangeOrigin.SYSTEM_SEED,
        changed_by_user_id=None,
    )


def test_derive_booking_type_break_start_when_schedule_over_6h() -> None:
    # 7-h-Schicht (08:00–15:00): > 6 h → Pausenpflicht → BREAK_START
    sched = _make_schedule(time(8, 0), time(15, 0))
    assert derive_booking_type([BookingType.COME], schedule=sched) == BookingType.BREAK_START


def test_derive_booking_type_go_when_schedule_under_6h() -> None:
    # 5-h-Schicht (08:00–13:00): ≤ 6 h → kein Pausenanspruch → GO
    sched = _make_schedule(time(8, 0), time(13, 0))
    assert derive_booking_type([BookingType.COME], schedule=sched) == BookingType.GO


def test_derive_booking_type_go_when_schedule_exactly_6h_no_break_required() -> None:
    # Grenzfall: exakt 6 h (08:00–14:00).
    # § 4 ArbZG schreibt Pause erst bei *mehr als* 6 h vor; bei genau 6 h
    # besteht kein Pausenanspruch. Die Bedingung ist daher ≤ 6 h (inklusiv).
    sched = _make_schedule(time(8, 0), time(14, 0))
    assert derive_booking_type([BookingType.COME], schedule=sched) == BookingType.GO


def test_derive_booking_type_break_start_when_no_schedule_fallback() -> None:
    # Kein Zeitplan → Positionslogik greift unverändert: 2. Scan = BREAK_START
    assert derive_booking_type([BookingType.COME], schedule=None) == BookingType.BREAK_START


# --- Sollzeit-Ausnahmeregel: Integration über BookUseCase ---


def test_zweiter_scan_mit_kurzem_zeitplan_ergibt_go() -> None:
    # Schicht ≤ 6 h: 2. Scan soll GO erzeugen (keine Pause nötig)
    # _DATE = 2025-03-10 → isoweekday = 1 (Montag)
    uow = _make_uow()
    _add_global_schedule(uow, weekday=1, start=time(8, 0), end=time(13, 0))  # 5 h
    _add_booking(uow, BookingType.COME, 8)
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(booked_at=_T(13)))

    saved = uow.time_booking_repo.get_by_id(result.booking_id)
    assert saved is not None
    assert saved.booking_type == BookingType.GO


def test_zweiter_scan_ohne_zeitplan_ergibt_break_start() -> None:
    # Kein Zeitplan: 2. Scan bleibt BREAK_START (Positionslogik)
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(booked_at=_T(10)))

    saved = uow.time_booking_repo.get_by_id(result.booking_id)
    assert saved is not None
    assert saved.booking_type == BookingType.BREAK_START


# --- Schritt 4: Dritter Scan auf Kurztag ---


def test_derive_booking_type_kurztag_dritter_scan_wirft_invalid_sequence_error() -> None:
    # [COME, GO] + Kurztag-Zeitplan → 3. Scan muss InvalidBookingSequenceError werfen,
    # Fehlermeldung muss "Kurztag" enthalten
    sched = _make_schedule(time(8, 0), time(13, 0))  # 5 h ≤ 6 h
    with pytest.raises(InvalidBookingSequenceError, match="Kurztag"):
        derive_booking_type([BookingType.COME, BookingType.GO], schedule=sched)


def test_derive_booking_type_langtag_dritter_scan_ergibt_break_end() -> None:
    # [COME, BREAK_START] + Langtag-Zeitplan (> 6 h) → regulärer Ablauf: BREAK_END
    sched = _make_schedule(time(8, 0), time(17, 0))  # 9 h > 6 h
    result = derive_booking_type([BookingType.COME, BookingType.BREAK_START], schedule=sched)
    assert result == BookingType.BREAK_END


def test_kurztag_dritter_scan_wird_abgewiesen_ohne_buchung() -> None:
    # Integration: Kurztag ≤ 6 h, bereits COME + GO im Repo → 3. Scan wirft Exception,
    # keine Buchung wird geschrieben
    uow = _make_uow()
    _add_global_schedule(uow, weekday=1, start=time(8, 0), end=time(13, 0))  # 5 h
    _add_booking(uow, BookingType.COME, 8)
    _add_booking(uow, BookingType.GO, 13)
    buchungen_vorher = len(uow.time_booking_repo._store)
    uc = BookUseCase(_as_uow(uow))

    with pytest.raises(InvalidBookingSequenceError, match="Kurztag"):
        uc.execute(_cmd(booked_at=_T(14)))

    assert len(uow.time_booking_repo._store) == buchungen_vorher


# --- Regression: UTC vs. Lokalzeit bei Regelzeitfenster-Prüfung ---


def test_buchung_innerhalb_cest_regelzeitfenster_kein_schedule_flag() -> None:
    """Buchung 06:00 UTC = 08:00 CEST liegt innerhalb Fenster 07:30–18:00.

    Bugverhalten: book_time.py:145 vergleicht UTC-Zeit (06:00) mit lokalem
    Regelzeitplan (07:30–18:00) → 06:00 < 07:30 → fälschlich
    OUTSIDE_SCHEDULE_WINDOW gesetzt. Korrekt: Lokalzeit 08:00 ≥ 07:30 → kein Flag.
    Datum: 2025-06-16 (Montag, isoweekday=1) → CEST = UTC+2.
    """
    uow = _make_uow()
    _add_global_schedule(uow, weekday=1, start=time(7, 30), end=time(18, 0))
    uc = BookUseCase(_as_uow(uow))

    booked_at = datetime(2025, 6, 16, 6, 0, tzinfo=timezone.utc)  # = 08:00 CEST
    result = uc.execute(_cmd(booked_at=booked_at))

    assert result.status == BookingStatus.OPEN  # COME-Buchung hat immer OPEN
    cases = uow.review_case_repo.list_open_for_employee(1)
    assert not any(c.case_type == ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW for c in cases)


def test_schedule_lookup_verwendet_lokalen_wochentag() -> None:
    """Buchung Sonntag 22:30 UTC = Montag 00:30 CEST → Montag-Zeitplan muss verwendet werden.

    Bugverhalten: book_time.py:139 verwendet cmd.booked_at.isoweekday() = 7 (Sonntag,
    UTC-Datum) → kein Montag-Zeitplan gefunden → schedule=None → kein Schedule-Flag.
    Korrekt: Lokal-Wochentag 1 (Montag) → Montag-Zeitplan gefunden; 00:30 < 07:30
    → OUTSIDE_SCHEDULE_WINDOW wird korrekt gesetzt.
    Datum: 2025-06-15 (Sonntag UTC) = 2025-06-16 (Montag CEST).
    """
    uow = _make_uow()
    _add_global_schedule(uow, weekday=1, start=time(7, 30), end=time(18, 0))  # nur Montag
    uc = BookUseCase(_as_uow(uow))

    booked_at = datetime(2025, 6, 15, 22, 30, tzinfo=timezone.utc)  # = 00:30 Montag CEST
    uc.execute(_cmd(booked_at=booked_at))

    cases = uow.review_case_repo.list_open_for_employee(1)
    assert any(c.case_type == ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW for c in cases)


def test_langtag_dritter_scan_ergibt_break_end() -> None:
    # Integration: Langtag > 6 h, bereits COME + BREAK_START im Repo
    # → 3. Scan via BookUseCase = BREAK_END (kein Kurztag-Fehler)
    uow = _make_uow()
    _add_global_schedule(uow, weekday=1, start=time(8, 0), end=time(17, 0))  # 9 h
    _add_booking(uow, BookingType.COME, 8)
    _add_booking(uow, BookingType.BREAK_START, 12)
    uc = BookUseCase(_as_uow(uow))

    result = uc.execute(_cmd(booked_at=_T(13)))

    saved = uow.time_booking_repo.get_by_id(result.booking_id)
    assert saved is not None
    assert saved.booking_type == BookingType.BREAK_END
