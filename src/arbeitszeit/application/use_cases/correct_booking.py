__version__ = "1.1"

import json
from datetime import datetime, timezone

from arbeitszeit.application.commands import CreateCorrectionCommand
from arbeitszeit.application.results import CorrectionResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry, BookingCorrection, TimeBooking
from arbeitszeit.domain.enums import (
    BookingStatus,
    ReviewCaseStatus,
    ReviewCaseType,
    UserRole,
)
from arbeitszeit.domain.errors import (
    InactiveEmployeeError,
    NotFoundError,
    PermissionDeniedError,
)
from arbeitszeit.domain.value_objects import (
    AuditLogEntryId,
    BookingCorrectionId,
    ReviewCaseId,
    UserAccountId,
)

# Nur Prüffälle, die inhaltlich durch Korrektur der Buchung erledigt sind.
# MANUAL_ENTRY_REVIEW (Nachtragsprozess), UNKNOWN_CARD_ATTEMPT, INACTIVE_CARD_ATTEMPT
# und TIME_ANOMALY werden nicht durch eine Buchungskorrektur geschlossen.
_CORRECTABLE_CASE_TYPES = frozenset(
    {
        ReviewCaseType.OPEN_WORK_PHASE,
        ReviewCaseType.OPEN_BREAK_PHASE,
        ReviewCaseType.IMPLAUSIBLE_SEQUENCE,
        ReviewCaseType.POSSIBLE_BREAK_VIOLATION,
        ReviewCaseType.POSSIBLE_REST_VIOLATION,
        ReviewCaseType.POSSIBLE_MAX_HOURS_VIOLATION,
        ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW,
    }
)


class CorrectBookingUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: CreateCorrectionCommand) -> CorrectionResult:
        with self._uow:
            self._check_permission(cmd.corrected_by_user_id)

            booking = self._uow.time_booking_repo.get_by_id(cmd.original_booking_id)
            if booking is None:
                raise NotFoundError(f"Buchung {cmd.original_booking_id} nicht gefunden.")

            employee = self._uow.employee_repo.get_by_id(booking.employee_id)
            if employee is None:
                raise NotFoundError(f"Mitarbeiter {booking.employee_id} nicht gefunden.")
            if not employee.is_active:
                raise InactiveEmployeeError(f"Mitarbeiter {booking.employee_id} ist inaktiv.")

            now = datetime.now(timezone.utc)

            correction = self._uow.booking_correction_repo.add(
                BookingCorrection(
                    id=BookingCorrectionId(0),
                    original_booking_id=booking.id,
                    corrected_by_user_id=cmd.corrected_by_user_id,
                    reason=cmd.reason,
                    old_booking_type=booking.booking_type,
                    old_booked_at=booking.booked_at,
                    new_booking_type=cmd.new_booking_type,
                    new_booked_at=cmd.new_booked_at,
                    created_at=now,
                )
            )

            self._uow.time_booking_repo.set_status(
                booking.id,
                BookingStatus.CORRECTED,
                reason=cmd.reason,
                changed_by_user_id=cmd.corrected_by_user_id,
            )
            self._uow.time_booking_repo.update(
                booking.id,
                cmd.new_booking_type,
                cmd.new_booked_at,
            )

            review_case_id = self._close_correctable_cases(
                booking, cmd.corrected_by_user_id, cmd.reason
            )

            # Erst commit, dann Audit-Log schreiben (siehe BookUseCase für Begründung).
            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.BOOKING_CORRECTED,
                    object_type="booking_corrections",
                    object_id=correction.id,
                    user_id=cmd.corrected_by_user_id,
                    employee_id=booking.employee_id,
                    event_at=now,
                    details_json=json.dumps(
                        {
                            "original_booking_id": booking.id,
                            "old_booking_type": booking.booking_type.value,
                            "old_booked_at": booking.booked_at.isoformat(),
                            "new_booking_type": cmd.new_booking_type.value,
                            "new_booked_at": cmd.new_booked_at.isoformat(),
                            "reason": cmd.reason,
                            "status_after": BookingStatus.CORRECTED.value,
                            "review_case_id": review_case_id,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

            return CorrectionResult(
                correction_id=correction.id,
                updated_booking_id=booking.id,
                review_case_id=review_case_id,
            )

    def _check_permission(self, user_id: UserAccountId) -> None:
        actor = self._uow.user_account_repo.get_by_id(user_id)
        if (
            actor is None
            or not actor.is_active
            or actor.role not in {UserRole.ADMIN, UserRole.REVIEWER}
        ):
            raise PermissionDeniedError(
                f"Benutzer {user_id} ist nicht berechtigt, Buchungen zu korrigieren."
            )

    def _close_correctable_cases(
        self,
        booking: TimeBooking,
        closed_by_user_id: UserAccountId,
        reason: str,
    ) -> ReviewCaseId | None:
        open_cases = self._uow.review_case_repo.list_open_for_employee(booking.employee_id)
        review_case_id: ReviewCaseId | None = None
        for case in open_cases:
            if case.booking_id == booking.id and case.case_type in _CORRECTABLE_CASE_TYPES:
                self._uow.review_case_repo.resolve(
                    case.id,
                    status=ReviewCaseStatus.RESOLVED,
                    closed_by_user_id=closed_by_user_id,
                    note=reason,
                )
                if review_case_id is None:
                    review_case_id = case.id
        return review_case_id
