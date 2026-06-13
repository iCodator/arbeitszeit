"""ArbZG-Prüfhilfen für Pausen, Höchstarbeitszeit und Ruhezeiten.

Alle Prüfungen arbeiten auf der **Netto-Arbeitszeit** (Gesamtdauer der Arbeitsphasen
abzüglich aller erfassten Pausen). §4 ArbZG definiert die Pausenpflicht formal über
die Brutto-Anwesenheitszeit; die Netto-Betrachtung ist als fachliche Prüfhilfe
konzipiert und ersetzt keine rechtsverbindliche Einzelfallbewertung.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from arbeitszeit.domain.entities import TimeBooking
from arbeitszeit.domain.enums import BookingType, ReviewCaseType, ReviewSeverity


@dataclass(frozen=True)
class ComplianceFlag:
    case_type: ReviewCaseType
    severity: ReviewSeverity


@dataclass(frozen=True)
class _WorkStats:
    net_work: float
    total_break: float
    max_continuous: float


def check_break_compliance(day_bookings: Sequence[TimeBooking]) -> list[ComplianceFlag]:
    stats = _work_stats(day_bookings)

    # Verlaufstatbestand: ununterbrochener Arbeitsblock > 6h
    if stats.max_continuous > 6 * 3600:
        return [ComplianceFlag(ReviewCaseType.POSSIBLE_BREAK_VIOLATION, ReviewSeverity.WARN)]

    # > 9h Nettoarbeitszeit mit < 45min Gesamtpause
    if stats.net_work > 9 * 3600 and stats.total_break < 45 * 60:
        return [ComplianceFlag(ReviewCaseType.POSSIBLE_BREAK_VIOLATION, ReviewSeverity.CRITICAL)]

    # > 6h Nettoarbeitszeit mit < 30min Gesamtpause
    if stats.net_work > 6 * 3600 and stats.total_break < 30 * 60:
        return [ComplianceFlag(ReviewCaseType.POSSIBLE_BREAK_VIOLATION, ReviewSeverity.WARN)]

    return []


def check_max_hours(day_bookings: Sequence[TimeBooking]) -> list[ComplianceFlag]:
    stats = _work_stats(day_bookings)
    if stats.net_work > 10 * 3600:
        return [ComplianceFlag(
            ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION, ReviewSeverity.CRITICAL
        )]
    if stats.net_work > 8 * 3600:
        return [ComplianceFlag(
            ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION, ReviewSeverity.WARN
        )]
    return []


def check_rest_period(last_go: datetime, next_come: datetime) -> list[ComplianceFlag]:
    if (next_come - last_go).total_seconds() < 11 * 3600:
        return [ComplianceFlag(
            ReviewCaseType.POSSIBLE_REST_VIOLATION, ReviewSeverity.CRITICAL
        )]
    return []


def _work_stats(day_bookings: Sequence[TimeBooking]) -> _WorkStats:
    # day_bookings must be in chronological order
    net_work = 0.0
    total_break = 0.0
    max_continuous = 0.0

    work_block_start: datetime | None = None
    break_start: datetime | None = None

    for booking in day_bookings:
        bt = booking.booking_type
        ts = booking.booked_at

        if bt == BookingType.COME:
            work_block_start = ts

        elif bt == BookingType.BREAK_START:
            if work_block_start is not None:
                block = (ts - work_block_start).total_seconds()
                net_work += block
                max_continuous = max(max_continuous, block)
                work_block_start = None
            break_start = ts

        elif bt == BookingType.BREAK_END:
            if break_start is not None:
                total_break += (ts - break_start).total_seconds()
                break_start = None
            work_block_start = ts

        elif bt == BookingType.GO:
            if work_block_start is not None:
                block = (ts - work_block_start).total_seconds()
                net_work += block
                max_continuous = max(max_continuous, block)
                work_block_start = None

    return _WorkStats(
        net_work=net_work, total_break=total_break, max_continuous=max_continuous
    )
