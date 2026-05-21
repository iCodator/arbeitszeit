import json
from datetime import datetime, timezone

from arbeitszeit.application.commands import CreateCorrectionCommand
from arbeitszeit.application.results import CorrectionResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain.entities import AuditLogEntry, BookingCorrection
from arbeitszeit.domain.enums import BookingStatus, ReviewCaseStatus
from arbeitszeit.domain.errors import NotFoundError


class CorrectBookingUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: CreateCorrectionCommand) -> CorrectionResult:
        with self._uow:
            booking = self._uow.time_booking_repo.get_by_id(cmd.original_booking_id)
            if booking is None:
                raise NotFoundError(
                    f"Buchung {cmd.original_booking_id} nicht gefunden."
                )

            correction = self._uow.booking_correction_repo.add(BookingCorrection(
                id=0,
                original_booking_id=booking.id,
                corrected_by_user_id=cmd.corrected_by_user_id,
                reason=cmd.reason,
                old_booking_type=booking.booking_type,
                old_booked_at=booking.booked_at,
                new_booking_type=cmd.new_booking_type,
                new_booked_at=cmd.new_booked_at,
                created_at=datetime.now(timezone.utc),
            ))

            self._uow.time_booking_repo.set_status(
                booking.id,
                BookingStatus.CORRECTED,
                reason=cmd.reason,
                changed_by_user_id=cmd.corrected_by_user_id,
            )

            open_cases = self._uow.review_case_repo.list_open_for_employee(
                booking.employee_id
            )
            review_case_id: int | None = None
            for case in open_cases:
                if case.booking_id == booking.id:
                    self._uow.review_case_repo.resolve(
                        case.id,
                        status=ReviewCaseStatus.RESOLVED,
                        closed_by_user_id=cmd.corrected_by_user_id,
                        note=cmd.reason,
                    )
                    review_case_id = case.id
                    break

            now = datetime.now(timezone.utc)
            self._uow.audit_log_repo.add(AuditLogEntry(
                id=0,
                event_type="BOOKING_CORRECTED",
                object_type="booking_corrections",
                object_id=correction.id,
                user_id=cmd.corrected_by_user_id,
                employee_id=booking.employee_id,
                event_at=now,
                details_json=json.dumps({
                    "original_booking_id": booking.id,
                    "old_booking_type": booking.booking_type,
                    "old_booked_at": booking.booked_at.isoformat(),
                    "new_booking_type": cmd.new_booking_type,
                    "new_booked_at": cmd.new_booked_at.isoformat(),
                    "review_case_id": review_case_id,
                }),
            ))

            self._uow.commit()
            return CorrectionResult(
                correction_id=correction.id,
                updated_booking_id=booking.id,
                review_case_id=review_case_id,
            )
