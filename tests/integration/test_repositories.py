import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import (
    ApprovalStatus,
    BookingStatus,
    ReviewCaseStatus,
    ScopeType,
)
from arbeitszeit.domain.errors import NotFoundError, ValidationError
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.repositories import (
    SQLiteReviewCaseRepository,
    SQLiteSupplementRepository,
    SQLiteTimeBookingRepository,
    SQLiteWorkScheduleRepository,
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


# --- SQLiteWorkScheduleRepository ---


def _insert_work_schedule_version(
    conn,
    weekday: int = 1,
    valid_from: str = "2025-01-01",
    valid_until: str | None = None,
    scope_type: str = "GLOBAL",
    scope_employee_id: int | None = None,
) -> int:
    row = conn.execute(
        "INSERT INTO work_schedule_versions "
        "(scope_type, scope_employee_id, weekday, start_time, end_time, "
        "valid_from, valid_until, change_origin, changed_by_user_id, changed_at) "
        "VALUES (?, ?, ?, '08:00', '17:00', ?, ?, 'SYSTEM_SEED', NULL, "
        "'2025-01-01T00:00:00+00:00') RETURNING id",
        (scope_type, scope_employee_id, weekday, valid_from, valid_until),
    ).fetchone()
    return row["id"]


def _insert_time_booking(conn, employee_id: int, status: str = "OPEN") -> int:
    row = conn.execute(
        "INSERT INTO time_bookings "
        "(employee_id, rfid_card_id, booking_type, booked_at, source, "
        "terminal_id, device_event_id, current_status, note, created_at) "
        "VALUES (?, NULL, 'COME', '2025-06-01T08:00:00+00:00', 'TERMINAL', "
        "NULL, NULL, ?, NULL, '2025-06-01T08:00:00+00:00') RETURNING id",
        (employee_id, status),
    ).fetchone()
    return row["id"]


def test_add_work_schedule_version_ist_abrufbar(conn):
    version_id = _insert_work_schedule_version(conn, weekday=1, valid_from="2025-01-01")
    row = conn.execute(
        "SELECT id, weekday, valid_from FROM work_schedule_versions WHERE id = ?",
        (version_id,),
    ).fetchone()
    assert row["id"] == version_id
    assert row["weekday"] == 1
    assert row["valid_from"] == "2025-01-01"


def test_close_version_setzt_valid_until(conn):
    repo = SQLiteWorkScheduleRepository(conn)
    version_id = _insert_work_schedule_version(conn, valid_from="2025-01-01")
    repo.close_version(version_id, date(2025, 6, 30))
    row = conn.execute(
        "SELECT valid_until FROM work_schedule_versions WHERE id = ?", (version_id,)
    ).fetchone()
    assert row["valid_until"] == "2025-06-30"


def test_close_version_auf_unbekannter_id_wirft_not_found_error(conn):
    repo = SQLiteWorkScheduleRepository(conn)
    with pytest.raises(NotFoundError):
        repo.close_version(99999, date(2025, 6, 30))


def test_close_version_mit_ungueltigem_datum_wirft_validation_error(conn):
    repo = SQLiteWorkScheduleRepository(conn)
    version_id = _insert_work_schedule_version(conn, valid_from="2025-06-01")
    with pytest.raises(ValidationError):
        repo.close_version(version_id, date(2025, 5, 31))


def test_get_effective_employee_scope_hat_vorrang_vor_global(conn, employee_id):
    repo = SQLiteWorkScheduleRepository(conn)
    _insert_work_schedule_version(
        conn, weekday=1, valid_from="2025-01-01",
        scope_type="GLOBAL", scope_employee_id=None,
    )
    _insert_work_schedule_version(
        conn, weekday=1, valid_from="2025-01-01",
        scope_type="EMPLOYEE", scope_employee_id=employee_id,
    )
    result = repo.get_effective(weekday=1, on_date=date(2025, 6, 1), employee_id=employee_id)
    assert result is not None
    assert result.scope_type == ScopeType.EMPLOYEE
    assert result.scope_employee_id == employee_id


def test_get_effective_faellt_auf_global_zurueck(conn, employee_id):
    repo = SQLiteWorkScheduleRepository(conn)
    _insert_work_schedule_version(
        conn, weekday=1, valid_from="2025-01-01",
        scope_type="GLOBAL", scope_employee_id=None,
    )
    result = repo.get_effective(weekday=1, on_date=date(2025, 6, 1), employee_id=employee_id)
    assert result is not None
    assert result.scope_type == ScopeType.GLOBAL


# --- SQLiteTimeBookingRepository: set_status ---


def test_set_status_aktualisiert_current_status(conn, employee_id):
    repo = SQLiteTimeBookingRepository(conn)
    booking_id = _insert_time_booking(conn, employee_id, status="OPEN")
    repo.set_status(booking_id, BookingStatus.OK)
    row = conn.execute(
        "SELECT current_status FROM time_bookings WHERE id = ?", (booking_id,)
    ).fetchone()
    assert row["current_status"] == BookingStatus.OK.value


def test_set_status_schreibt_statushistorie_eintrag(conn, employee_id):
    repo = SQLiteTimeBookingRepository(conn)
    booking_id = _insert_time_booking(conn, employee_id, status="OPEN")
    repo.set_status(booking_id, BookingStatus.OK, reason="Tagesabschluss")
    row = conn.execute(
        "SELECT old_status, new_status, reason FROM booking_status_history "
        "WHERE time_booking_id = ?",
        (booking_id,),
    ).fetchone()
    assert row is not None
    assert row["old_status"] == BookingStatus.OPEN.value
    assert row["new_status"] == BookingStatus.OK.value
    assert row["reason"] == "Tagesabschluss"


def test_set_status_auf_unbekannter_id_wirft_not_found_error(conn):
    repo = SQLiteTimeBookingRepository(conn)
    with pytest.raises(NotFoundError):
        repo.set_status(99999, BookingStatus.OK)
