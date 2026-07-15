"""E2E-Tests: Nachtragsprozess von Erfassung bis Genehmigung/Ablehnung.

Verwendet echte dateibasierte SQLite-DB (tmp_path / "arbeitszeit.db")
und reale Use-Case-Implementierungen ohne Mocks.
"""

__version__ = "1.1"

import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.commands import (
    ApproveSupplementCommand,
    CreateSupplementCommand,
    RejectSupplementCommand,
)
from arbeitszeit.domain.value_objects import EmployeeId, SupplementId, UserAccountId
from arbeitszeit.application.use_cases.approve_supplement import (
    ApproveSupplementUseCase,
)
from arbeitszeit.application.use_cases.register_supplement import (
    RegisterSupplementUseCase,
)
from arbeitszeit.application.use_cases.reject_supplement import RejectSupplementUseCase
from arbeitszeit.domain.enums import ApprovalStatus, BookingStatus, BookingType
from arbeitszeit.domain.errors import (
    InactiveEmployeeError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork

_EVENT_AT = datetime(2026, 5, 1, 7, 30, tzinfo=timezone.utc)
_RECORDED_AT = datetime(2026, 5, 2, 9, 0, tzinfo=timezone.utc)


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = tmp_path / "arbeitszeit.db"
    conn = open_connection(path)
    run_migrations(conn)
    conn.close()
    return path


@pytest.fixture
def employee_id(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E001', 'Test', 'Nutzer', 1, '2026-01-01', '2026-01-01') RETURNING id"
    ).fetchone()
    conn.close()
    return int(row["id"])


@pytest.fixture
def inactive_employee_id(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E002', 'Inaktiv', 'Nutzer', 0, '2026-01-01', '2026-01-01') RETURNING id"
    ).fetchone()
    conn.close()
    return int(row["id"])


@pytest.fixture
def reviewer_user_id(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, active, created_at, updated_at) "
        "VALUES ('reviewer1', 'x', 'REVIEWER', 1, '2026-01-01', '2026-01-01') RETURNING id"
    ).fetchone()
    conn.close()
    return int(row["id"])


@pytest.fixture
def admin_user_id(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, active, created_at, updated_at) "
        "VALUES ('admin1', 'x', 'ADMIN', 1, '2026-01-01', '2026-01-01') RETURNING id"
    ).fetchone()
    conn.close()
    return int(row["id"])


@pytest.fixture
def employee_user_id(db: Path) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, active, created_at, updated_at) "
        "VALUES ('emp1', 'x', 'EMPLOYEE', 1, '2026-01-01', '2026-01-01') RETURNING id"
    ).fetchone()
    conn.close()
    return int(row["id"])


@contextmanager
def _make_uow(db: Path) -> Generator[SQLiteUnitOfWork, None, None]:
    conn = open_connection(db)
    audit_conn = open_connection(db)
    try:
        yield SQLiteUnitOfWork(conn, audit_conn)
    finally:
        audit_conn.close()
        conn.close()


def _create_supplement(db: Path, employee_id: int, user_id: int) -> int:
    cmd = CreateSupplementCommand(
        employee_id=EmployeeId(employee_id),
        related_booking_id=None,
        booking_type=BookingType.COME,
        event_at=_EVENT_AT,
        recorded_at=_RECORDED_AT,
        reason="Vergessen einzustempeln",
        recorded_by_user_id=UserAccountId(user_id),
    )
    with _make_uow(db) as uow:
        result = RegisterSupplementUseCase(uow).execute(cmd)
    return result.supplement_id


def test_nachtrag_erfassen_reviewer(db: Path, employee_id: int, reviewer_user_id: int) -> None:
    cmd = CreateSupplementCommand(
        employee_id=EmployeeId(employee_id),
        related_booking_id=None,
        booking_type=BookingType.COME,
        event_at=_EVENT_AT,
        recorded_at=_RECORDED_AT,
        reason="Vergessen einzustempeln",
        recorded_by_user_id=UserAccountId(reviewer_user_id),
    )
    with _make_uow(db) as uow:
        result = RegisterSupplementUseCase(uow).execute(cmd)

    assert result.supplement_id > 0
    assert result.review_case_id is not None

    conn = open_connection(db)
    row = conn.execute(
        "SELECT approval_status FROM supplements WHERE id = ?", (result.supplement_id,)
    ).fetchone()
    conn.close()
    assert row["approval_status"] == ApprovalStatus.PENDING.value


def test_nachtrag_erfassen_employee_verweigert(
    db: Path, employee_id: int, employee_user_id: int
) -> None:
    cmd = CreateSupplementCommand(
        employee_id=EmployeeId(employee_id),
        related_booking_id=None,
        booking_type=BookingType.COME,
        event_at=_EVENT_AT,
        recorded_at=_RECORDED_AT,
        reason="Test",
        recorded_by_user_id=UserAccountId(employee_user_id),
    )
    with _make_uow(db) as uow:
        with pytest.raises(PermissionDeniedError):
            RegisterSupplementUseCase(uow).execute(cmd)


def test_nachtrag_erfassen_unbekannter_mitarbeiter(db: Path, reviewer_user_id: int) -> None:
    cmd = CreateSupplementCommand(
        employee_id=EmployeeId(9999),
        related_booking_id=None,
        booking_type=BookingType.COME,
        event_at=_EVENT_AT,
        recorded_at=_RECORDED_AT,
        reason="Test",
        recorded_by_user_id=UserAccountId(reviewer_user_id),
    )
    with _make_uow(db) as uow:
        with pytest.raises(NotFoundError):
            RegisterSupplementUseCase(uow).execute(cmd)


def test_nachtrag_genehmigen_erzeugt_buchung(
    db: Path, employee_id: int, reviewer_user_id: int, admin_user_id: int
) -> None:
    supplement_id = _create_supplement(db, employee_id, reviewer_user_id)

    cmd = ApproveSupplementCommand(
        supplement_id=SupplementId(supplement_id),
        approving_user_id=UserAccountId(admin_user_id),
    )
    with _make_uow(db) as uow:
        result = ApproveSupplementUseCase(uow).execute(cmd)

    assert result.booking_id > 0
    assert result.booking_status in (
        BookingStatus.OK,
        BookingStatus.OPEN,
        BookingStatus.WARN,
        BookingStatus.NEEDS_REVIEW,
    )

    conn = open_connection(db)
    row = conn.execute(
        "SELECT approval_status FROM supplements WHERE id = ?", (supplement_id,)
    ).fetchone()
    booking_row = conn.execute(
        "SELECT source FROM time_bookings WHERE id = ?", (result.booking_id,)
    ).fetchone()
    conn.close()

    assert row["approval_status"] == ApprovalStatus.APPROVED.value
    assert booking_row["source"] == "MANUAL"


def test_nachtrag_ablehnen_reviewer(db: Path, employee_id: int, reviewer_user_id: int) -> None:
    supplement_id = _create_supplement(db, employee_id, reviewer_user_id)

    cmd = RejectSupplementCommand(
        supplement_id=SupplementId(supplement_id),
        rejected_by_user_id=UserAccountId(reviewer_user_id),
        reason="Nicht nachvollziehbar",
    )
    with _make_uow(db) as uow:
        result = RejectSupplementUseCase(uow).execute(cmd)

    assert result.supplement_id == supplement_id

    conn = open_connection(db)
    row = conn.execute(
        "SELECT approval_status FROM supplements WHERE id = ?", (supplement_id,)
    ).fetchone()
    conn.close()
    assert row["approval_status"] == ApprovalStatus.REJECTED.value


def test_nachtrag_genehmigen_nach_ablehnung_verweigert(
    db: Path, employee_id: int, reviewer_user_id: int, admin_user_id: int
) -> None:
    supplement_id = _create_supplement(db, employee_id, reviewer_user_id)
    with _make_uow(db) as uow:
        RejectSupplementUseCase(uow).execute(
            RejectSupplementCommand(
                supplement_id=SupplementId(supplement_id),
                rejected_by_user_id=UserAccountId(reviewer_user_id),
                reason="Abgelehnt",
            )
        )
    with _make_uow(db) as uow:
        with pytest.raises(ValidationError):
            ApproveSupplementUseCase(uow).execute(
                ApproveSupplementCommand(
                    supplement_id=SupplementId(supplement_id),
                    approving_user_id=UserAccountId(admin_user_id),
                )
            )


def test_nachtrag_genehmigen_inaktiver_mitarbeiter(
    db: Path, inactive_employee_id: int, reviewer_user_id: int, admin_user_id: int
) -> None:
    # Direkt einfügen (RegisterSupplement lehnt inaktive Mitarbeiter ab)
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO supplements "
        "(employee_id, booking_type, event_at, recorded_at, reason, recorded_by_user_id, "
        "approval_status) "
        "VALUES (?, 'COME', ?, ?, 'Test', ?, 'PENDING') RETURNING id",
        (
            inactive_employee_id,
            _EVENT_AT.isoformat(),
            _RECORDED_AT.isoformat(),
            reviewer_user_id,
        ),
    ).fetchone()
    conn.close()

    supplement_id = row["id"]
    with _make_uow(db) as uow:
        with pytest.raises(InactiveEmployeeError):
            ApproveSupplementUseCase(uow).execute(
                ApproveSupplementCommand(
                    supplement_id=SupplementId(int(supplement_id)),
                    approving_user_id=UserAccountId(admin_user_id),
                )
            )


def test_nachtrag_genehmigen_unbekannter_benutzer(
    db: Path, employee_id: int, reviewer_user_id: int
) -> None:
    supplement_id = _create_supplement(db, employee_id, reviewer_user_id)
    with _make_uow(db) as uow:
        with pytest.raises(PermissionDeniedError):
            ApproveSupplementUseCase(uow).execute(
                ApproveSupplementCommand(
                    supplement_id=SupplementId(supplement_id),
                    approving_user_id=UserAccountId(9999),
                )
            )
