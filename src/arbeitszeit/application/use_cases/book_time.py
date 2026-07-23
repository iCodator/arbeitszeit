__version__ = "1.8"

import json
from datetime import datetime, timedelta, timezone
from typing import Sequence

from arbeitszeit.application.commands import BookCommand
from arbeitszeit.application.results import BookResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.application.use_cases._booking_evaluation import evaluate_booking
from arbeitszeit.application.use_cases._tz import to_local
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import (
    AuditLogEntry,
    Employee,
    ReviewCase,
    RfidCard,
    TimeBooking,
    WorkScheduleVersion,
)
from arbeitszeit.domain.enums import (
    BookingStatus,
    BookingType,
    CardStatus,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.domain.errors import (
    InactiveCardError,
    InactiveEmployeeError,
    InvalidBookingSequenceError,
    NotFoundError,
    UnknownCardError,
)
from arbeitszeit.domain.services.booking_rules import validate_booking_sequence
from arbeitszeit.domain.services.compliance_checks import ComplianceFlag
from arbeitszeit.domain.value_objects import (
    AuditLogEntryId,
    EmployeeId,
    ReviewCaseId,
    TimeBookingId,
)

_NEXT_BOOKING_TYPE: dict[BookingType, BookingType] = {
    BookingType.COME: BookingType.BREAK_START,
    BookingType.BREAK_START: BookingType.BREAK_END,
    BookingType.BREAK_END: BookingType.GO,
}


def _schedule_duration(schedule: WorkScheduleVersion) -> timedelta:
    base = datetime(2000, 1, 1)
    return datetime.combine(base, schedule.end_time) - datetime.combine(base, schedule.start_time)


def _is_short_day(schedule: WorkScheduleVersion | None) -> bool:
    """True wenn Zeitplan vorhanden und Solldauer ≤ 6 h (§ 4 ArbZG: kein Pausenanspruch)."""
    return schedule is not None and _schedule_duration(schedule) <= timedelta(hours=6)


def _derive_for_short_day(day_bookings: Sequence[BookingType]) -> BookingType:
    """Buchungstyp-Ableitung für einen Kurztag (Sollzeit ≤ 6 h, §4 ArbZG).

    2. Scan (genau 1 Buchung vorhanden): GO.
    3. Scan oder mehr (≥ 2 Buchungen): InvalidBookingSequenceError.
    """
    if len(day_bookings) >= 2:
        raise InvalidBookingSequenceError(
            "Kurztag (Sollzeit ≤ 6 h): Tagesablauf nach COME und GO bereits "
            "abgeschlossen — weitere Buchung unzulässig."
        )
    return BookingType.GO


def derive_booking_type(
    day_bookings: Sequence[BookingType],
    schedule: WorkScheduleVersion | None = None,
) -> BookingType:
    """Leitet den nächsten Buchungstyp aus der bisherigen Tagessequenz ab.

    Standardsequenz: COME → BREAK_START → BREAK_END → GO.
    Wirft InvalidBookingSequenceError wenn der Tagesablauf abgeschlossen ist.

    Kurztag-Ausnahme (Sollzeit ≤ 6 h, §4 ArbZG): 2. Scan → GO statt
    BREAK_START; 3. Scan → InvalidBookingSequenceError mit Kurztag-Hinweis.
    Ohne schedule greift ausschließlich die Standard-Positionslogik.
    """
    if not day_bookings:
        return BookingType.COME
    if _is_short_day(schedule):
        return _derive_for_short_day(day_bookings)
    next_type = _NEXT_BOOKING_TYPE.get(day_bookings[-1])
    if next_type is None:
        raise InvalidBookingSequenceError(
            "Tagesablauf abgeschlossen — keine weitere Buchung zulässig."
        )
    return next_type


def _detect_open_prev_shift(
    day_bookings: Sequence[TimeBooking],
    prev_bookings: Sequence[TimeBooking],
    employee_id: EmployeeId,
    booked_at: datetime,
) -> dict[str, object] | None:
    if not day_bookings and prev_bookings:
        last_prev = prev_bookings[-1]
        if last_prev.booking_type != BookingType.GO:
            return {
                "employee_id": employee_id,
                "previous_day_date": (booked_at.date() - timedelta(days=1)).isoformat(),
                "last_known_booking_type": last_prev.booking_type.value,
                "last_known_booking_at": last_prev.booked_at.isoformat(),
            }
    return None


class BookUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: BookCommand) -> BookResult:
        # Terminal-Buchungen erfordern keine explizite UserRole-Prüfung. Die
        # Authentifikation erfolgt durch die gültige RFID-Karte des Mitarbeiters;
        # dies ist die vom Regelwerk v5 §16 vorgesehene Mitarbeiteraktion.
        # Schreibende Admin-Aktionen (Korrektur, Nachtrag, Regelzeitänderung) prüfen
        # die UserRole gesondert in ihren jeweiligen Use Cases.
        with self._uow:
            card = self._verify_card(cmd.uid_hash, cmd.terminal_id)
            employee = self._verify_employee(card.employee_id)

            day_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                employee.id, cmd.booked_at.date()
            )

            day_booking_types = [b.booking_type for b in day_bookings]

            local_booked_at = to_local(cmd.booked_at)
            schedule = self._uow.work_schedule_repo.get_effective(
                local_booked_at.isoweekday(), local_booked_at.date(), employee.id
            )
            booking_type = derive_booking_type(day_booking_types, schedule)
            validate_booking_sequence(booking_type, day_booking_types)

            schedule_flags: list[ComplianceFlag] = []
            if schedule is not None and not (
                schedule.start_time <= local_booked_at.time() <= schedule.end_time
            ):
                schedule_flags = [
                    ComplianceFlag(ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW, ReviewSeverity.WARN)
                ]

            prev_bookings = self._uow.time_booking_repo.list_for_employee_on_day(
                employee.id, cmd.booked_at.date() - timedelta(days=1)
            )

            # Offene Vortagsschicht erkennen: tritt auf, wenn die heutige Buchungsliste
            # leer ist, aber am Vortag Buchungen existieren und die letzte davon kein GO
            # ist. Kein normaler Betriebsfall (keine Nachtschichten) — deutet auf eine
            # vergessene Abmeldung hin. Die aktuelle Buchung wird trotzdem regulär
            # verarbeitet; der Befund wird als Audit-Log-Eintrag festgehalten.
            open_shift_details = _detect_open_prev_shift(
                day_bookings, prev_bookings, employee.id, cmd.booked_at
            )

            placeholder = TimeBooking(
                id=TimeBookingId(0),
                employee_id=employee.id,
                booking_type=booking_type,
                booked_at=cmd.booked_at,
                source=cmd.source,
                status=BookingStatus.OPEN,
                terminal_id=cmd.terminal_id,
                rfid_card_id=card.id,
                device_event_id=cmd.device_event_id,
                note=None,
            )
            projected = list(day_bookings) + [placeholder]
            status, flags = evaluate_booking(
                booking_type, projected, prev_bookings, schedule_flags
            )

            # Write-Ahead via conn (in aktiver Transaktion): Absicht festhalten
            # bevor die Buchung geschrieben wird. Wird atomar mit der Buchung
            # committed. Bei Rollback geht PENDING verloren — das ist gewollt.
            # Crash-Detektion: PENDING ohne nachfolgendes TIME_BOOKED für
            # (employee_id, booking_type, booked_at) deutet auf Absturz hin.
            # HINWEIS: audit_conn (autocommit) darf hier NICHT schreiben, weil
            # conn nach dem BEGIN-DEFERRED noch keine Schreiboperation hatte —
            # ein autocommit-Write zwischen erstem SELECT und erstem conn-Write
            # löst SQLITE_BUSY_SNAPSHOT aus.
            self._uow.audit_log_repo.add_transactional(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.TIME_BOOKED_PENDING,
                    object_type="time_bookings",
                    object_id=0,
                    user_id=None,
                    employee_id=employee.id,
                    event_at=datetime.now(timezone.utc),
                    details_json=json.dumps(
                        {
                            "booking_type": booking_type.value,
                            "booked_at": cmd.booked_at.isoformat(),
                            "terminal_id": cmd.terminal_id,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

            booking = self._uow.time_booking_repo.add(
                TimeBooking(
                    id=TimeBookingId(0),
                    employee_id=employee.id,
                    booking_type=booking_type,
                    booked_at=cmd.booked_at,
                    source=cmd.source,
                    status=status,
                    terminal_id=cmd.terminal_id,
                    rfid_card_id=card.id,
                    device_event_id=cmd.device_event_id,
                    note=None,
                )
            )

            now = datetime.now(timezone.utc)
            follow_up_case_ids = self._write_review_cases(flags, employee.id, booking.id, now)

            # Erst commit, dann Audit-Log schreiben: nach commit hält conn keinen
            # RESERVED-Lock mehr, sodass audit_conn (autocommit) schreiben kann
            # ohne zu blockieren. Ablehnungspfade sind nicht betroffen, weil conn
            # dort nur SELECTs ausführt.
            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.TIME_BOOKED,
                    object_type="time_bookings",
                    object_id=booking.id,
                    user_id=None,
                    employee_id=employee.id,
                    event_at=now,
                    details_json=json.dumps(
                        {
                            "booking_type": booking_type.value,
                            "booked_at": cmd.booked_at.isoformat(),
                            "status": status.value,
                            "terminal_id": cmd.terminal_id,
                            "rfid_card_id": card.id,
                            "follow_up_case_ids": follow_up_case_ids,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

            if open_shift_details is not None:
                self._uow.audit_log_repo.add(
                    AuditLogEntry(
                        id=AuditLogEntryId(0),
                        event_type=audit_events.OPEN_SHIFT_PREVIOUS_DAY_DETECTED,
                        object_type="time_bookings",
                        object_id=booking.id,
                        user_id=None,
                        employee_id=employee.id,
                        event_at=now,
                        details_json=json.dumps(
                            open_shift_details,
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                    )
                )

            return BookResult(
                booking_id=booking.id,
                status=status,
                follow_up_case_ids=tuple(follow_up_case_ids),
                employee_first_name=employee.first_name,
                employee_last_name=employee.last_name,
                booking_type=booking.booking_type,
                booked_at=booking.booked_at,
            )

    def _verify_card(self, uid_hash: str, terminal_id: int) -> RfidCard:
        # INVARIANTE: Vor audit_log_repo.add() in Ablehnungspfaden darf conn
        # keine Schreiboperation ausgeführt haben (sonst WRITE-Lock-Konflikt
        # mit audit_conn trotz WAL). Hier nur SELECTs — muss so bleiben.
        card = self._uow.rfid_card_repo.get_by_uid_hash(uid_hash)
        if card is None:
            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.BOOKING_REJECTED_UNKNOWN_CARD,
                    object_type="rfid_cards",
                    object_id=0,
                    user_id=None,
                    employee_id=None,
                    event_at=datetime.now(timezone.utc),
                    details_json=json.dumps(
                        {"uid_hash_prefix": uid_hash[:8], "terminal_id": terminal_id},
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )
            raise UnknownCardError(f"Unbekannte RFID-UID: {uid_hash}")
        if card.status != CardStatus.ACTIVE:
            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.BOOKING_REJECTED_INACTIVE_CARD,
                    object_type="rfid_cards",
                    object_id=card.id,
                    user_id=None,
                    employee_id=card.employee_id,
                    event_at=datetime.now(timezone.utc),
                    details_json=json.dumps(
                        {
                            "card_id": card.id,
                            "card_status": card.status.value,
                            "terminal_id": terminal_id,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )
            raise InactiveCardError(f"Karte {card.id} ist nicht aktiv.")
        return card

    def _verify_employee(self, employee_id: EmployeeId) -> Employee:
        employee = self._uow.employee_repo.get_by_id(employee_id)
        if employee is None:
            raise NotFoundError(f"Mitarbeiter {employee_id} nicht gefunden.")
        if not employee.is_active:
            raise InactiveEmployeeError(f"Mitarbeiter {employee_id} ist nicht aktiv.")
        return employee

    def _write_review_cases(
        self,
        flags: list[ComplianceFlag],
        employee_id: EmployeeId,
        booking_id: TimeBookingId,
        now: datetime,
    ) -> list[ReviewCaseId]:
        follow_up_case_ids: list[ReviewCaseId] = []
        for flag in flags:
            case = self._uow.review_case_repo.add(
                ReviewCase(
                    id=ReviewCaseId(0),
                    employee_id=employee_id,
                    case_type=flag.case_type,
                    severity=flag.severity,
                    status=ReviewCaseStatus.OPEN,
                    description=f"Automatisch erkannt bei Buchung #{booking_id}",
                    booking_id=booking_id,
                    created_at=now,
                    closed_at=None,
                    closed_by_user_id=None,
                )
            )
            follow_up_case_ids.append(case.id)
        return follow_up_case_ids
