"""Use Cases für RFID-Kartenverwaltung (ADMIN-Rolle erforderlich)."""

__version__ = "1.0"

import json
from datetime import date, datetime, timezone

from arbeitszeit.application.commands import (
    AssignRfidCardCommand,
    DeactivateRfidCardCommand,
    ReplaceRfidCardCommand,
)
from arbeitszeit.application.results import AssignRfidCardResult, ReplaceRfidCardResult
from arbeitszeit.application.unit_of_work import UnitOfWork
from arbeitszeit.domain import audit_events
from arbeitszeit.domain.entities import AuditLogEntry, RfidCard
from arbeitszeit.domain.enums import CardStatus, UserRole
from arbeitszeit.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from arbeitszeit.domain.value_objects import AuditLogEntryId, RfidCardId


class AssignRfidCardUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: AssignRfidCardCommand) -> AssignRfidCardResult:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Karten zuzuweisen."
                )

            employee = self._uow.employee_repo.get_by_id(cmd.employee_id)
            if employee is None:
                raise NotFoundError(f"Mitarbeiter {cmd.employee_id} nicht gefunden.")

            if self._uow.rfid_card_repo.get_by_uid_hash(cmd.uid_hash) is not None:
                raise ConflictError(
                    f"UID-Hash '{cmd.uid_hash}' ist bereits vergeben."
                )

            now = datetime.now(timezone.utc)
            saved = self._uow.rfid_card_repo.add(
                RfidCard(
                    id=RfidCardId(0),
                    uid_hash=cmd.uid_hash,
                    employee_id=cmd.employee_id,
                    status=CardStatus.ACTIVE,
                    valid_from=date.today(),
                    valid_until=None,
                    replaced_by_card_id=None,
                )
            )

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.CARD_ASSIGNED,
                    object_type="rfid_cards",
                    object_id=saved.id,
                    user_id=cmd.acting_user_id,
                    employee_id=cmd.employee_id,
                    event_at=now,
                    details_json=json.dumps(
                        {
                            "uid_hash": cmd.uid_hash,
                            "employee_id": cmd.employee_id,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

            return AssignRfidCardResult(card_id=saved.id)


class ReplaceRfidCardUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: ReplaceRfidCardCommand) -> ReplaceRfidCardResult:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Karten zu ersetzen."
                )

            old_card = self._uow.rfid_card_repo.get_by_id(cmd.old_card_id)
            if old_card is None:
                raise NotFoundError(f"Karte {cmd.old_card_id} nicht gefunden.")

            if self._uow.rfid_card_repo.get_by_uid_hash(cmd.uid_hash) is not None:
                raise ConflictError(
                    f"UID-Hash '{cmd.uid_hash}' ist bereits vergeben."
                )

            now = datetime.now(timezone.utc)
            today = date.today()

            new_card = self._uow.rfid_card_repo.add(
                RfidCard(
                    id=RfidCardId(0),
                    uid_hash=cmd.uid_hash,
                    employee_id=old_card.employee_id,
                    status=CardStatus.ACTIVE,
                    valid_from=today,
                    valid_until=None,
                    replaced_by_card_id=None,
                )
            )

            self._uow.rfid_card_repo.set_status(
                cmd.old_card_id,
                CardStatus.REPLACED,
                replaced_by_card_id=new_card.id,
                valid_until=today,
            )

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.CARD_REPLACED,
                    object_type="rfid_cards",
                    object_id=new_card.id,
                    user_id=cmd.acting_user_id,
                    employee_id=old_card.employee_id,
                    event_at=now,
                    details_json=json.dumps(
                        {
                            "old_card_id": cmd.old_card_id,
                            "new_card_id": new_card.id,
                            "uid_hash": cmd.uid_hash,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

            return ReplaceRfidCardResult(new_card_id=new_card.id)


class DeactivateRfidCardUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, cmd: DeactivateRfidCardCommand) -> None:
        with self._uow:
            actor = self._uow.user_account_repo.get_by_id(cmd.acting_user_id)
            if actor is None or not actor.is_active or actor.role != UserRole.ADMIN:
                raise PermissionDeniedError(
                    f"Benutzer {cmd.acting_user_id} ist nicht berechtigt, "
                    "Karten zu deaktivieren."
                )

            card = self._uow.rfid_card_repo.get_by_id(cmd.card_id)
            if card is None:
                raise NotFoundError(f"Karte {cmd.card_id} nicht gefunden.")

            now = datetime.now(timezone.utc)
            self._uow.rfid_card_repo.set_status(cmd.card_id, CardStatus.INACTIVE)

            self._uow.commit()

            self._uow.audit_log_repo.add(
                AuditLogEntry(
                    id=AuditLogEntryId(0),
                    event_type=audit_events.CARD_DEACTIVATED,
                    object_type="rfid_cards",
                    object_id=cmd.card_id,
                    user_id=cmd.acting_user_id,
                    employee_id=card.employee_id,
                    event_at=now,
                    details_json=json.dumps({}, ensure_ascii=False),
                )
            )
