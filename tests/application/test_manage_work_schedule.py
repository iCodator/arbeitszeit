import json
import sys
from datetime import date, time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import ChangeWorkScheduleCommand
from arbeitszeit.application.use_cases.manage_work_schedule import (
    ManageWorkScheduleUseCase,
)
from arbeitszeit.domain.entities import UserAccount
from arbeitszeit.domain.enums import ChangeOrigin, ScopeType, UserRole
from arbeitszeit.domain.errors import ConflictError, PermissionDeniedError, ValidationError
from tests.application.fakes import FakeUnitOfWork

_ADMIN_ID = 1  # id des ADMIN-UserAccounts (erstes Element im Fake-Store)


def _make_uow() -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    uow.user_account_repo.add(UserAccount(
        id=0, employee_id=None, username="admin",
        role=UserRole.ADMIN, is_active=True,
    ))
    return uow


def _cmd(**overrides) -> ChangeWorkScheduleCommand:
    defaults = dict(
        scope_type=ScopeType.GLOBAL,
        scope_employee_id=None,
        weekday=1,
        start_time=time(7, 30),
        end_time=time(16, 0),
        valid_from=date(2025, 1, 1),
        change_origin=ChangeOrigin.ADMIN_UI,
        changed_by_user_id=_ADMIN_ID,
        reason=None,
    )
    return ChangeWorkScheduleCommand(**{**defaults, **overrides})


# --- Basis-Anlage ---

def test_neue_version_wird_angelegt():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)

    result = uc.execute(_cmd())

    assert result.new_version_id > 0
    assert uow.committed


def test_erste_version_hat_kein_superseded():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)

    result = uc.execute(_cmd())

    assert result.superseded_version_id is None


# --- Bestehende Version wird geschlossen ---

def test_bestehende_version_wird_geschlossen():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)

    first = uc.execute(_cmd(valid_from=date(2025, 1, 1)))
    uow.committed = False

    second = uc.execute(_cmd(valid_from=date(2025, 6, 1), start_time=time(8, 0)))

    assert second.superseded_version_id == first.new_version_id
    assert uow.committed

    closed = uow.work_schedule_repo._store[first.new_version_id]
    assert closed.valid_until == date(2025, 5, 31)


# --- ConflictError ---

def test_gleiche_valid_from_loest_conflict_error():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(valid_from=date(2025, 1, 1)))

    with pytest.raises(ConflictError):
        uc.execute(_cmd(valid_from=date(2025, 1, 1), start_time=time(8, 0)))


def test_identische_version_loest_conflict_error():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(valid_from=date(2025, 1, 1)))

    with pytest.raises(ConflictError):
        uc.execute(_cmd(valid_from=date(2025, 1, 1)))


# --- ValidationError ---

def test_rueckwaerts_insertion_loest_validation_error():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(valid_from=date(2025, 6, 1)))

    with pytest.raises(ValidationError):
        uc.execute(_cmd(valid_from=date(2025, 1, 1)))


def test_rueckwaerts_insertion_anderer_wochentag_erlaubt():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(weekday=1, valid_from=date(2025, 6, 1)))

    result = uc.execute(_cmd(weekday=2, valid_from=date(2025, 1, 1)))

    assert result.new_version_id > 0


# --- Audit-Log ---

def test_audit_log_eintrag_vorhanden():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)

    uc.execute(_cmd())

    assert len(uow.audit_log_repo.entries) == 1
    entry = uow.audit_log_repo.entries[0]
    assert entry.event_type == "WORK_SCHEDULE_CHANGED"
    assert entry.object_type == "work_schedule_versions"


def test_audit_log_enthaelt_fachliche_felder():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)

    first = uc.execute(_cmd(valid_from=date(2025, 1, 1)))
    uow.committed = False
    uc.execute(_cmd(valid_from=date(2025, 6, 1), start_time=time(8, 0)))

    entry = uow.audit_log_repo.entries[1]
    details = json.loads(entry.details_json)
    assert details["scope_type"] == "GLOBAL"
    assert details["start_time"] == "08:00"
    assert details["end_time"] == "16:00"
    assert details["change_origin"] == "ADMIN_UI"
    assert details["superseded_version_id"] == first.new_version_id
    assert details["previous_valid_from"] == "2025-01-01"
    assert details["previous_start_time"] == "07:30"
    assert details["previous_end_time"] == "16:00"


def test_audit_log_erste_version_hat_keine_previous_felder():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)

    uc.execute(_cmd(valid_from=date(2025, 1, 1)))

    details = json.loads(uow.audit_log_repo.entries[0].details_json)
    assert details["previous_valid_from"] is None
    assert details["previous_start_time"] is None
    assert details["previous_end_time"] is None


# --- Transaktionsverhalten ---

def test_rollback_bei_validation_error():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(valid_from=date(2025, 6, 1)))
    uow.committed = False
    uow.rolled_back = False

    with pytest.raises(ValidationError):
        uc.execute(_cmd(valid_from=date(2025, 1, 1)))

    assert uow.rolled_back
    assert not uow.committed


# --- Scope-Trennung ---

def test_employee_scope_unabhaengig_von_global():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(
        scope_type=ScopeType.GLOBAL, scope_employee_id=None, valid_from=date(2025, 6, 1)
    ))

    result = uc.execute(_cmd(
        scope_type=ScopeType.EMPLOYEE, scope_employee_id=42, valid_from=date(2025, 1, 1)
    ))

    assert result.new_version_id > 0
    assert result.superseded_version_id is None


def test_employee_scopes_verschiedener_mitarbeiter_sind_unabhaengig():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(
        scope_type=ScopeType.EMPLOYEE, scope_employee_id=42, valid_from=date(2025, 6, 1)
    ))

    result = uc.execute(_cmd(
        scope_type=ScopeType.EMPLOYEE, scope_employee_id=43, valid_from=date(2025, 1, 1)
    ))

    assert result.new_version_id > 0
    assert result.superseded_version_id is None


# --- Kein Audit-Log bei Fehler ---

def test_kein_audit_log_bei_conflict_error():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(valid_from=date(2025, 1, 1)))
    log_count_before = len(uow.audit_log_repo.entries)

    with pytest.raises(ConflictError):
        uc.execute(_cmd(valid_from=date(2025, 1, 1), start_time=time(8, 0)))

    assert len(uow.audit_log_repo.entries) == log_count_before


def test_kein_audit_log_bei_validation_error():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(valid_from=date(2025, 6, 1)))
    log_count_before = len(uow.audit_log_repo.entries)

    with pytest.raises(ValidationError):
        uc.execute(_cmd(valid_from=date(2025, 1, 1)))

    assert len(uow.audit_log_repo.entries) == log_count_before


# --- Rollenprüfung ---

def test_changed_by_user_id_none_loest_permission_denied():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(changed_by_user_id=None))


def test_unbekannter_benutzer_loest_permission_denied():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(changed_by_user_id=999))


def test_benutzer_ohne_admin_rolle_loest_permission_denied():
    uow = _make_uow()
    reviewer = uow.user_account_repo.add(UserAccount(
        id=0, employee_id=None, username="reviewer",
        role=UserRole.REVIEWER, is_active=True,
    ))
    uc = ManageWorkScheduleUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(changed_by_user_id=reviewer.id))


def test_inaktiver_admin_loest_permission_denied():
    uow = _make_uow()
    inactive = uow.user_account_repo.add(UserAccount(
        id=0, employee_id=None, username="inactive_admin",
        role=UserRole.ADMIN, is_active=False,
    ))
    uc = ManageWorkScheduleUseCase(uow)

    with pytest.raises(PermissionDeniedError):
        uc.execute(_cmd(changed_by_user_id=inactive.id))
