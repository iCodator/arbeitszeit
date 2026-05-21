import sys
from datetime import date, time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import ChangeWorkScheduleCommand
from arbeitszeit.application.use_cases.manage_work_schedule import ManageWorkScheduleUseCase
from arbeitszeit.domain.enums import ChangeOrigin, ScopeType
from arbeitszeit.domain.errors import ConflictError, ValidationError

from tests.application.fakes import FakeUnitOfWork


def _make_uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


def _cmd(**overrides) -> ChangeWorkScheduleCommand:
    defaults = dict(
        scope_type=ScopeType.GLOBAL,
        scope_employee_id=None,
        weekday=1,
        start_time=time(7, 30),
        end_time=time(16, 0),
        valid_from=date(2025, 1, 1),
        change_origin=ChangeOrigin.ADMIN_UI,
        changed_by_user_id=1,
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


# --- Scope-Trennung ---

def test_employee_scope_unabhaengig_von_global():
    uow = _make_uow()
    uc = ManageWorkScheduleUseCase(uow)
    uc.execute(_cmd(scope_type=ScopeType.GLOBAL, scope_employee_id=None, valid_from=date(2025, 6, 1)))

    result = uc.execute(
        _cmd(scope_type=ScopeType.EMPLOYEE, scope_employee_id=42, valid_from=date(2025, 1, 1))
    )

    assert result.new_version_id > 0
    assert result.superseded_version_id is None
