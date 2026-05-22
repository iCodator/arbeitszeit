import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingType,
    ReviewCaseStatus,
    ReviewCaseType,
    ReviewSeverity,
)
from arbeitszeit.domain.errors import NotFoundError
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.repositories import (
    SQLiteReviewCaseRepository,
    SQLiteSupplementRepository,
)

_NOW = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)


@pytest.fixture
def conn(tmp_path):
    connection = open_connection(tmp_path / "test.db")
    run_migrations(connection)
    yield connection
    connection.close()


@pytest.fixture
def employee_id(conn) -> int:
    row = conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E001', 'Test', 'User', 1, '2025-01-01', '2025-01-01') RETURNING id"
    ).fetchone()
    return row["id"]


@pytest.fixture
def user_id(conn) -> int:
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, active, created_at, updated_at) "
        "VALUES ('admin', 'hash', 'ADMIN', 1, '2025-01-01', '2025-01-01') RETURNING id"
    ).fetchone()
    return row["id"]


def _insert_supplement(conn, employee_id: int, recorded_by_user_id: int) -> int:
    row = conn.execute(
        "INSERT INTO supplements "
        "(employee_id, related_time_booking_id, booking_type, event_at, "
        "recorded_at, reason, recorded_by_user_id, approval_status, "
        "approved_by_user_id, approved_at, rejected_by_user_id, rejected_at) "
        "VALUES (?, NULL, 'COME', '2025-06-01T08:00:00+00:00', "
        "'2025-06-01T09:00:00+00:00', 'Vergessen', ?, 'PENDING', "
        "NULL, NULL, NULL, NULL) RETURNING id",
        (employee_id, recorded_by_user_id),
    ).fetchone()
    return row["id"]


def _insert_review_case(conn, employee_id: int) -> int:
    row = conn.execute(
        "INSERT INTO review_cases "
        "(employee_id, time_booking_id, case_type, status, severity, "
        "detected_at, description, closed_at, closed_by_user_id, note) "
        "VALUES (?, NULL, 'MANUAL_ENTRY_REVIEW', 'OPEN', 'WARN', "
        "'2025-06-01T08:00:00+00:00', 'Prüfung erforderlich', NULL, NULL, NULL) "
        "RETURNING id",
        (employee_id,),
    ).fetchone()
    return row["id"]


# --- SQLiteSupplementRepository: rowcount-Verhalten ---


def test_approve_auf_unbekannter_id_wirft_not_found_error(conn, user_id):
    repo = SQLiteSupplementRepository(conn)
    with pytest.raises(NotFoundError):
        repo.approve(
            supplement_id=99999,
            approved_by_user_id=user_id,
            approved_at=_NOW,
        )


def test_reject_auf_unbekannter_id_wirft_not_found_error(conn, user_id):
    repo = SQLiteSupplementRepository(conn)
    with pytest.raises(NotFoundError):
        repo.reject(
            supplement_id=99999,
            rejected_by_user_id=user_id,
            rejected_at=_NOW,
        )


def test_approve_auf_bekannter_id_wirft_keinen_fehler(conn, employee_id, user_id):
    supplement_id = _insert_supplement(conn, employee_id, user_id)
    repo = SQLiteSupplementRepository(conn)
    repo.approve(
        supplement_id=supplement_id,
        approved_by_user_id=user_id,
        approved_at=_NOW,
    )
    row = conn.execute(
        "SELECT approval_status FROM supplements WHERE id = ?", (supplement_id,)
    ).fetchone()
    assert row["approval_status"] == ApprovalStatus.APPROVED.value


def test_reject_auf_bekannter_id_wirft_keinen_fehler(conn, employee_id, user_id):
    supplement_id = _insert_supplement(conn, employee_id, user_id)
    repo = SQLiteSupplementRepository(conn)
    repo.reject(
        supplement_id=supplement_id,
        rejected_by_user_id=user_id,
        rejected_at=_NOW,
    )
    row = conn.execute(
        "SELECT approval_status FROM supplements WHERE id = ?", (supplement_id,)
    ).fetchone()
    assert row["approval_status"] == ApprovalStatus.REJECTED.value


# --- SQLiteReviewCaseRepository: rowcount-Verhalten ---


def test_resolve_auf_unbekannter_id_wirft_not_found_error(conn, user_id):
    repo = SQLiteReviewCaseRepository(conn)
    with pytest.raises(NotFoundError):
        repo.resolve(
            case_id=99999,
            status=ReviewCaseStatus.RESOLVED,
            closed_by_user_id=user_id,
        )


def test_resolve_auf_bekannter_id_setzt_status(conn, employee_id, user_id):
    case_id = _insert_review_case(conn, employee_id)
    repo = SQLiteReviewCaseRepository(conn)
    repo.resolve(
        case_id=case_id,
        status=ReviewCaseStatus.RESOLVED,
        closed_by_user_id=user_id,
    )
    row = conn.execute(
        "SELECT status FROM review_cases WHERE id = ?", (case_id,)
    ).fetchone()
    assert row["status"] == ReviewCaseStatus.RESOLVED.value
