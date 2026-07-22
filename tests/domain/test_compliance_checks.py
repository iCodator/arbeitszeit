__version__ = "1.1"

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.entities import TimeBooking
from arbeitszeit.domain.enums import (
    BookingSource,
    BookingStatus,
    BookingType,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.domain.services.compliance_checks import (
    ComplianceFlag,
    check_break_compliance,
    check_max_hours,
    check_rest_period,
)
from arbeitszeit.domain.value_objects import EmployeeId, TimeBookingId


def _booking(booking_type: BookingType, hour: int, minute: int = 0) -> TimeBooking:
    return TimeBooking(
        id=TimeBookingId(0),
        employee_id=EmployeeId(1),
        booking_type=booking_type,
        booked_at=datetime(2024, 1, 15, hour, minute, tzinfo=timezone.utc),
        source=BookingSource.TERMINAL,
        status=BookingStatus.OK,
        terminal_id=None,
        rfid_card_id=None,
        device_event_id=None,
        note=None,
    )


def _dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute, tzinfo=timezone.utc)


def _has(flags: list[ComplianceFlag], case_type: ReviewCaseType) -> bool:
    return any(f.case_type == case_type for f in flags)


def _severity(
    flags: list[ComplianceFlag], case_type: ReviewCaseType
) -> ReviewSeverity | None:
    for f in flags:
        if f.case_type == case_type:
            return f.severity
    return None


# --- check_break_compliance ---


def test_keine_pausenverletzung_bei_kurzer_arbeitszeit() -> None:
    bookings = [_booking(BookingType.COME, 8), _booking(BookingType.GO, 11)]
    assert check_break_compliance(bookings) == []


def test_pausenverletzung_ueber_6h_ohne_ausreichende_pause() -> None:
    bookings = [
        _booking(BookingType.COME, 7),
        _booking(BookingType.BREAK_START, 13),
        _booking(BookingType.BREAK_END, 13, 10),
        _booking(BookingType.GO, 14),
    ]
    flags = check_break_compliance(bookings)
    assert _has(flags, ReviewCaseType.POSSIBLE_BREAK_VIOLATION)


def test_pausenverletzung_ueber_9h_ohne_45min_pause() -> None:
    bookings = [
        _booking(BookingType.COME, 7),
        _booking(BookingType.BREAK_START, 12),
        _booking(BookingType.BREAK_END, 12, 20),
        _booking(BookingType.GO, 17, 30),
    ]
    flags = check_break_compliance(bookings)
    assert _has(flags, ReviewCaseType.POSSIBLE_BREAK_VIOLATION)
    assert _severity(flags, ReviewCaseType.POSSIBLE_BREAK_VIOLATION) == ReviewSeverity.CRITICAL


def test_keine_pausenverletzung_mit_ausreichender_pause() -> None:
    bookings = [
        _booking(BookingType.COME, 7),
        _booking(BookingType.BREAK_START, 12),
        _booking(BookingType.BREAK_END, 12, 31),
        _booking(BookingType.GO, 14),
    ]
    assert check_break_compliance(bookings) == []


# --- check_max_hours ---


def test_keine_ueberschreitung_bei_normaler_arbeitszeit() -> None:
    bookings = [_booking(BookingType.COME, 7, 30), _booking(BookingType.GO, 15, 30)]
    assert check_max_hours(bookings) == []


def test_max_hours_warnung_ueber_8h() -> None:
    bookings = [_booking(BookingType.COME, 7), _booking(BookingType.GO, 15, 1)]
    flags = check_max_hours(bookings)
    assert _has(flags, ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION)
    assert _severity(flags, ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION) == ReviewSeverity.WARN


def test_max_hours_eskalation_ueber_10h() -> None:
    bookings = [_booking(BookingType.COME, 7), _booking(BookingType.GO, 17, 1)]
    flags = check_max_hours(bookings)
    assert _has(flags, ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION)
    assert _severity(flags, ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION) == ReviewSeverity.CRITICAL


# --- check_rest_period ---


def test_keine_ruhezeiverletzung_bei_ausreichender_ruhezeit() -> None:
    last_go = datetime(2024, 1, 15, 17, 0, tzinfo=timezone.utc)
    next_come = datetime(2024, 1, 16, 5, 0, tzinfo=timezone.utc)
    assert check_rest_period(last_go, next_come) == []


def test_ruhezeit_verletzung_unter_11h() -> None:
    last_go = datetime(2024, 1, 15, 18, 0, tzinfo=timezone.utc)
    next_come = datetime(2024, 1, 16, 4, 0, tzinfo=timezone.utc)
    flags = check_rest_period(last_go, next_come)
    assert _has(flags, ReviewCaseType.POSSIBLE_REST_VIOLATION)
    assert _severity(flags, ReviewCaseType.POSSIBLE_REST_VIOLATION) == ReviewSeverity.CRITICAL


# --- Robustheit: pathologische Buchungsfolgen ---


def test_break_start_ohne_vorherigen_come_wird_ignoriert() -> None:
    # work_block_start ist None beim BREAK_START → kein Arbeitsblock gezählt.
    # Tritt auf bei Altdaten oder manuellen Importen ohne vorangehenden COME.
    bookings = [_booking(BookingType.BREAK_START, 8)]
    assert check_break_compliance(bookings) == []
    assert check_max_hours(bookings) == []


def test_break_end_ohne_vorherigen_break_start_wird_ignoriert() -> None:
    # break_start ist None beim BREAK_END → keine Pausendauer gezählt.
    # Tritt auf wenn BREAK_END-Eintrag ohne korrespondierenden BREAK_START in DB.
    bookings = [_booking(BookingType.COME, 7), _booking(BookingType.BREAK_END, 9)]
    assert check_break_compliance(bookings) == []
    assert check_max_hours(bookings) == []


def test_go_ohne_vorherigen_come_wird_ignoriert() -> None:
    # work_block_start ist None beim GO → kein Arbeitsblock gezählt.
    # Tritt auf wenn GO ohne vorangehenden COME in der Buchungsfolge steht.
    bookings = [_booking(BookingType.GO, 12)]
    assert check_break_compliance(bookings) == []
    assert check_max_hours(bookings) == []


# --- Regression: CRITICAL nicht durch WARN verdeckt ---


def test_critical_nicht_durch_warn_verdeckt() -> None:
    """Gleichzeitig max_continuous > 6 h UND net_work > 9 h mit < 45 min Pause.

    Bugverhalten: erster Treffer (max_continuous > 6 h) gibt WARN zurück und
    kehrt sofort zurück; die schwerwiegendere CRITICAL-Bedingung wird nie geprüft.
    Korrekt: alle Bedingungen werden geprüft, schwerste Severity gewinnt → CRITICAL.

    Szenario aus dem Audit-Befund [Hoch] compliance_checks.py:33–47:
    COME 07:00 → BREAK_START 14:30 (7,5 h ununterbrochen, > 6 h)
    BREAK_START 14:30 → BREAK_END 14:40 (10 min Pause, < 45 min)
    BREAK_END 14:40 → GO 17:00 (2 h 20 min)
    net_work = 7,5 h + 2,33 h = 9,83 h > 9 h, total_break = 10 min < 45 min.
    """
    bookings = [
        _booking(BookingType.COME, 7, 0),
        _booking(BookingType.BREAK_START, 14, 30),
        _booking(BookingType.BREAK_END, 14, 40),
        _booking(BookingType.GO, 17, 0),
    ]
    flags = check_break_compliance(bookings)
    assert _has(flags, ReviewCaseType.POSSIBLE_BREAK_VIOLATION)
    assert _severity(flags, ReviewCaseType.POSSIBLE_BREAK_VIOLATION) == ReviewSeverity.CRITICAL
