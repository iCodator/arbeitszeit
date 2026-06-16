import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
from arbeitszeit.application.commands import BookCommand
from arbeitszeit.application.use_cases.book_time import BookUseCase
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
    OpenPhaseConflictError,
    UnknownCardError,
)
from tests.application.fakes import FakeUnitOfWork

_DATE = date(2025, 3, 10)


def _T(h: int, m: int = 0) -> datetime:
    return datetime(_DATE.year, _DATE.month, _DATE.day, h, m, tzinfo=timezone.utc)


def _make_uow(
    employee_active: bool = True, card_status: CardStatus = CardStatus.ACTIVE
) -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    emp = uow.employee_repo.add(
        Employee(
            id=0,
            personnel_no="E001",
            first_name="Anna",
            last_name="Muster",
            is_active=employee_active,
        )
    )
    uow.rfid_card_repo.add(
        RfidCard(
            id=0,
            employee_id=emp.id,
            uid_hash="abc123",
            status=card_status,
            valid_from=_DATE,
            valid_until=None,
            replaced_by_card_id=None,
        )
    )
    return uow


def _cmd(**overrides) -> BookCommand:
    defaults = dict(
        uid_hash="abc123",
        terminal_id=1,
        booking_type=BookingType.COME,
        booked_at=_T(8),
        device_event_id=None,
        source=BookingSource.TERMINAL,
    )
    return BookCommand(**{**defaults, **overrides})


def _add_booking(uow: FakeUnitOfWork, booking_type: BookingType, hour: int) -> TimeBooking:
    return uow.time_booking_repo.add(
        TimeBooking(
            id=0,
            employee_id=1,
            booking_type=booking_type,
            booked_at=_T(hour),
            source=BookingSource.TERMINAL,
            status=BookingStatus.OPEN,
            terminal_id=1,
            rfid_card_id=1,
            device_event_id=None,
            note=None,
        )
    )


def _add_booking_at(uow: FakeUnitOfWork, booking_type: BookingType, dt: datetime) -> TimeBooking:
    return uow.time_booking_repo.add(
        TimeBooking(
            id=0,
            employee_id=1,
            booking_type=booking_type,
            booked_at=dt,
            source=BookingSource.TERMINAL,
            status=BookingStatus.OPEN,
            terminal_id=1,
            rfid_card_id=1,
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
            id=0,
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


def test_unbekannte_uid_loest_unknown_card_error():
    uow = _make_uow()
    uc = BookUseCase(uow)

    with pytest.raises(UnknownCardError):
        uc.execute(_cmd(uid_hash="unknown"))


def test_inaktive_karte_loest_inactive_card_error():
    uow = _make_uow(card_status=CardStatus.INACTIVE)
    uc = BookUseCase(uow)

    with pytest.raises(InactiveCardError):
        uc.execute(_cmd())


def test_inaktiver_mitarbeiter_loest_inactive_employee_error():
    uow = _make_uow(employee_active=False)
    uc = BookUseCase(uow)

    with pytest.raises(InactiveEmployeeError):
        uc.execute(_cmd())


def test_fehlender_mitarbeiterdatensatz_loest_not_found_error():
    uow = _make_uow()
    uow.employee_repo._store.clear()
    uc = BookUseCase(uow)

    with pytest.raises(NotFoundError):
        uc.execute(_cmd())


# --- Sequenzfehler ---


def test_go_als_erste_buchung_loest_invalid_sequence_error():
    uow = _make_uow()
    uc = BookUseCase(uow)

    with pytest.raises(InvalidBookingSequenceError):
        uc.execute(_cmd(booking_type=BookingType.GO, booked_at=_T(17)))


def test_break_end_ohne_offene_pause_loest_invalid_sequence_error():
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    uc = BookUseCase(uow)

    with pytest.raises(InvalidBookingSequenceError):
        uc.execute(_cmd(booking_type=BookingType.BREAK_END, booked_at=_T(12)))


def test_come_nach_offenem_come_loest_invalid_sequence_error():
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    uc = BookUseCase(uow)

    with pytest.raises(InvalidBookingSequenceError):
        uc.execute(_cmd(booking_type=BookingType.COME, booked_at=_T(9)))


def test_go_bei_offener_pause_loest_open_phase_conflict_error():
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    _add_booking(uow, BookingType.BREAK_START, 12)
    uc = BookUseCase(uow)

    with pytest.raises(OpenPhaseConflictError):
        uc.execute(_cmd(booking_type=BookingType.GO, booked_at=_T(17)))


# --- Statusbestimmung ---


def test_come_buchung_hat_status_open():
    uow = _make_uow()
    uc = BookUseCase(uow)

    result = uc.execute(_cmd(booking_type=BookingType.COME, booked_at=_T(8)))

    assert result.status == BookingStatus.OPEN
    assert result.follow_up_case_ids == ()
    assert uow.committed


def test_go_ohne_compliance_flags_hat_status_ok():
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    uc = BookUseCase(uow)

    # 5h Arbeitszeit ohne Pause: kein Compliance-Flag (< 6h ununterbrochen, < 6h netto)
    result = uc.execute(_cmd(booking_type=BookingType.GO, booked_at=_T(13)))

    assert result.status == BookingStatus.OK
    assert result.follow_up_case_ids == ()


def test_break_start_hat_status_open():
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    uc = BookUseCase(uow)

    result = uc.execute(_cmd(booking_type=BookingType.BREAK_START, booked_at=_T(12)))

    assert result.status == BookingStatus.OPEN


def test_break_end_nach_kurzer_pause_hat_status_ok():
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 8)
    _add_booking(uow, BookingType.BREAK_START, 12)
    uc = BookUseCase(uow)

    result = uc.execute(_cmd(booking_type=BookingType.BREAK_END, booked_at=_T(12, 30)))

    assert result.status == BookingStatus.OK


def test_go_nach_mehr_als_8h_hat_status_warn():
    uow = _make_uow()
    come_at = _T(7)
    _add_booking(uow, BookingType.COME, 7)
    uc = BookUseCase(uow)

    go_at = come_at + timedelta(hours=8, minutes=30)
    result = uc.execute(_cmd(booking_type=BookingType.GO, booked_at=go_at))

    assert result.status == BookingStatus.WARN
    assert len(result.follow_up_case_ids) > 0


def test_go_nach_mehr_als_10h_hat_status_needs_review():
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 7)
    uc = BookUseCase(uow)

    go_at = _T(7) + timedelta(hours=10, minutes=30)
    result = uc.execute(_cmd(booking_type=BookingType.GO, booked_at=go_at))

    assert result.status == BookingStatus.NEEDS_REVIEW
    assert len(result.follow_up_case_ids) > 0


def test_buchung_wird_trotz_warn_gespeichert():
    uow = _make_uow()
    _add_booking(uow, BookingType.COME, 7)
    uc = BookUseCase(uow)

    go_at = _T(7) + timedelta(hours=8, minutes=30)
    result = uc.execute(_cmd(booking_type=BookingType.GO, booked_at=go_at))

    saved = uow.time_booking_repo.get_by_id(result.booking_id)
    assert saved is not None
    assert saved.status == BookingStatus.WARN


# --- Audit-Log ---


def test_audit_log_eintrag_vorhanden():
    uow = _make_uow()
    uc = BookUseCase(uow)

    uc.execute(_cmd())

    assert len(uow.audit_log_repo.entries) == 1
    entry = uow.audit_log_repo.entries[0]
    assert entry.event_type == audit_events.TIME_BOOKED
    assert entry.employee_id == 1


# --- device_event_id wird durchgereicht ---


def test_device_event_id_wird_in_buchung_gespeichert():
    uow = _make_uow()
    uc = BookUseCase(uow)

    result = uc.execute(_cmd(device_event_id=42))

    saved = uow.time_booking_repo.get_by_id(result.booking_id)
    assert saved is not None
    assert saved.device_event_id == 42


# --- Abweisungsprotokoll ---


def test_unbekannte_karte_schreibt_audit_log():
    uow = _make_uow()
    uc = BookUseCase(uow)

    with pytest.raises(UnknownCardError):
        uc.execute(_cmd(uid_hash="unbekannt"))

    entries = [
        e
        for e in uow.audit_log_repo.entries
        if e.event_type == audit_events.BOOKING_REJECTED_UNKNOWN_CARD
    ]
    assert len(entries) == 1


def test_inaktive_karte_schreibt_audit_log():
    uow = _make_uow(card_status=CardStatus.INACTIVE)
    uc = BookUseCase(uow)

    with pytest.raises(InactiveCardError):
        uc.execute(_cmd())

    entries = [
        e
        for e in uow.audit_log_repo.entries
        if e.event_type == audit_events.BOOKING_REJECTED_INACTIVE_CARD
    ]
    assert len(entries) == 1


# --- Ruhezeitprüfung (V3 §7.9 / ArbZG §5) ---


def test_go_nach_weniger_als_11h_ruhezeit_hat_status_needs_review():
    _YESTERDAY = _DATE - timedelta(days=1)

    def _TY(h: int) -> datetime:
        return datetime(
            _YESTERDAY.year, _YESTERDAY.month, _YESTERDAY.day, h, 0, tzinfo=timezone.utc
        )

    uow = _make_uow()
    # Vortag: COME 08:00 → GO 20:00
    _add_booking_at(uow, BookingType.COME, _TY(8))
    _add_booking_at(uow, BookingType.GO, _TY(20))
    # Heute: COME 06:00 (nur 10h Ruhezeit nach 20:00 gestern)
    _add_booking_at(uow, BookingType.COME, _T(6))
    uc = BookUseCase(uow)

    # GO heute → Ruhezeitprüfung: 20:00 → 06:00 = 10h < 11h → CRITICAL → NEEDS_REVIEW
    result = uc.execute(_cmd(booking_type=BookingType.GO, booked_at=_T(14)))

    assert result.status == BookingStatus.NEEDS_REVIEW
    cases = uow.review_case_repo.list_open_for_employee(1)
    assert any(c.case_type == ReviewCaseType.POSSIBLE_REST_VIOLATION for c in cases)


# --- Regelzeitfenster (Regelwerk §9/§10) ---


def test_come_ausserhalb_regelzeitfenster_erzeugt_review_case():
    # _DATE = 2025-03-10, isoweekday = 1 (Montag)
    uow = _make_uow()
    _add_global_schedule(uow, weekday=1, start=time(8, 0), end=time(17, 0))
    uc = BookUseCase(uow)

    # COME um 06:00 – vor Fensterbeginn 08:00
    result = uc.execute(_cmd(booking_type=BookingType.COME, booked_at=_T(6)))

    assert result.status == BookingStatus.OPEN
    assert len(result.follow_up_case_ids) > 0
    cases = uow.review_case_repo.list_open_for_employee(1)
    assert any(c.case_type == ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW for c in cases)
