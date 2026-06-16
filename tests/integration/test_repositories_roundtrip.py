"""
Roundtrip-Integrationstests für alle SQLite-Repositories.
Jeder Test geht den Weg: Repository-Methode → echte SQLite-DB → Ergebnis prüfen.
Fixtures conn / employee_id / user_id kommen aus conftest.py.
"""

import sys
from datetime import date, datetime, time, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.entities import (
    AuditLogEntry,
    BookingCorrection,
    TimeBooking,
    WorkScheduleVersion,
)
from arbeitszeit.domain.enums import (
    BookingSource,
    BookingStatus,
    BookingType,
    CardStatus,
    ChangeOrigin,
    ScopeType,
)
from arbeitszeit.infrastructure.db.repositories import (
    SQLiteAuditLogRepository,
    SQLiteBookingCorrectionRepository,
    SQLiteEmployeeRepository,
    SQLiteRfidCardRepository,
    SQLiteSystemConfigRepository,
    SQLiteTimeBookingRepository,
    SQLiteUserAccountRepository,
    SQLiteWorkScheduleRepository,
)

_NOW = datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc)
_TODAY = date(2025, 6, 1)
# Wochentag 6 (Samstag) — kein Konflikt mit Seed-Daten (Mo–Fr, weekday 1–5)
_WEEKDAY = 6


def _insert_rfid_card(
    conn, employee_id: int, uid_hash: str = "HASH001", status: str = "ACTIVE"
) -> int:
    row = conn.execute(
        "INSERT INTO rfid_cards "
        "(uid_hash, employee_id, status, valid_from, created_at) "
        "VALUES (?, ?, ?, '2025-01-01', '2025-01-01T00:00:00+00:00') RETURNING id",
        (uid_hash, employee_id, status),
    ).fetchone()
    return row["id"]


def _make_booking(
    employee_id: int,
    booking_type: BookingType = BookingType.COME,
    booked_at: datetime = _NOW,
    status: BookingStatus = BookingStatus.OPEN,
) -> TimeBooking:
    return TimeBooking(
        id=0,
        employee_id=employee_id,
        booking_type=booking_type,
        booked_at=booked_at,
        source=BookingSource.TERMINAL,
        status=status,
        terminal_id=None,
        rfid_card_id=None,
        device_event_id=None,
        note=None,
    )


def _make_work_schedule(
    scope_type: ScopeType = ScopeType.GLOBAL,
    scope_employee_id: int | None = None,
    weekday: int = _WEEKDAY,
    valid_from: date = date(2025, 1, 1),
    start_time: time = time(8, 0),
    end_time: time = time(17, 0),
) -> WorkScheduleVersion:
    return WorkScheduleVersion(
        id=0,
        scope_type=scope_type,
        scope_employee_id=scope_employee_id,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        valid_from=valid_from,
        valid_until=None,
        change_origin=ChangeOrigin.SYSTEM_SEED,
        changed_by_user_id=None,
    )


# --- EmployeeRepository ---


def test_employee_get_by_id(conn, employee_id):
    repo = SQLiteEmployeeRepository(conn)
    emp = repo.get_by_id(employee_id)
    assert emp is not None
    assert emp.id == employee_id
    assert emp.is_active is True


def test_employee_get_by_id_gibt_none_fuer_unbekannte_id(conn):
    assert SQLiteEmployeeRepository(conn).get_by_id(99999) is None


def test_employee_get_active_by_personnel_no(conn, employee_id):
    repo = SQLiteEmployeeRepository(conn)
    emp = repo.get_active_by_personnel_no("E001")
    assert emp is not None
    assert emp.id == employee_id


def test_employee_get_active_by_personnel_no_gibt_none_fuer_inaktiven(conn):
    conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E002', 'In', 'Aktiv', 0, '2025-01-01', '2025-01-01')"
    )
    assert SQLiteEmployeeRepository(conn).get_active_by_personnel_no("E002") is None


# --- UserAccountRepository ---


def test_user_account_get_by_id(conn, user_id):
    user = SQLiteUserAccountRepository(conn).get_by_id(user_id)
    assert user is not None
    assert user.id == user_id
    assert user.is_active is True


def test_user_account_get_by_username(conn, user_id):
    user = SQLiteUserAccountRepository(conn).get_by_username("admin")
    assert user is not None
    assert user.id == user_id


def test_user_account_get_by_username_gibt_none_fuer_unbekannten(conn):
    assert SQLiteUserAccountRepository(conn).get_by_username("nobody") is None


# --- RfidCardRepository ---


def test_rfid_card_get_by_uid_hash_findet_aktive_karte(conn, employee_id):
    _insert_rfid_card(conn, employee_id, uid_hash="HASH_ACTIVE", status="ACTIVE")
    card = SQLiteRfidCardRepository(conn).get_by_uid_hash("HASH_ACTIVE")
    assert card is not None
    assert card.status == CardStatus.ACTIVE


def test_rfid_card_get_by_uid_hash_findet_auch_inaktive_karte(conn, employee_id):
    _insert_rfid_card(conn, employee_id, uid_hash="HASH_INACTIVE", status="INACTIVE")
    assert SQLiteRfidCardRepository(conn).get_by_uid_hash("HASH_INACTIVE") is not None


def test_rfid_card_get_active_by_uid_hash_gibt_none_fuer_inaktive_karte(conn, employee_id):
    _insert_rfid_card(conn, employee_id, uid_hash="HASH_INACTIVE", status="INACTIVE")
    assert SQLiteRfidCardRepository(conn).get_active_by_uid_hash("HASH_INACTIVE") is None


def test_rfid_card_get_by_id(conn, employee_id):
    card_id = _insert_rfid_card(conn, employee_id, uid_hash="HASH_ID")
    card = SQLiteRfidCardRepository(conn).get_by_id(card_id)
    assert card is not None
    assert card.id == card_id


# --- TimeBookingRepository ---


def test_time_booking_add_und_get_by_id_roundtrip(conn, employee_id):
    repo = SQLiteTimeBookingRepository(conn)
    saved = repo.add(_make_booking(employee_id))
    assert saved.id > 0
    loaded = repo.get_by_id(saved.id)
    assert loaded is not None
    assert loaded.booking_type == BookingType.COME
    assert loaded.status == BookingStatus.OPEN
    assert loaded.employee_id == employee_id


def test_time_booking_list_for_employee_on_day_filtert_nach_tag(conn, employee_id):
    repo = SQLiteTimeBookingRepository(conn)
    b_mo = repo.add(
        _make_booking(employee_id, booked_at=datetime(2025, 6, 1, 8, 0, tzinfo=timezone.utc))
    )
    b_mo2 = repo.add(
        _make_booking(
            employee_id,
            booking_type=BookingType.GO,
            booked_at=datetime(2025, 6, 1, 17, 0, tzinfo=timezone.utc),
            status=BookingStatus.OK,
        )
    )
    # Buchung am Folgetag — darf nicht im Ergebnis sein
    repo.add(_make_booking(employee_id, booked_at=datetime(2025, 6, 2, 8, 0, tzinfo=timezone.utc)))
    result = repo.list_for_employee_on_day(employee_id, date(2025, 6, 1))
    assert {r.id for r in result} == {b_mo.id, b_mo2.id}


def test_time_booking_list_open_for_employee(conn, employee_id):
    repo = SQLiteTimeBookingRepository(conn)
    open_b = repo.add(_make_booking(employee_id, status=BookingStatus.OPEN))
    repo.add(
        _make_booking(
            employee_id,
            booking_type=BookingType.GO,
            booked_at=datetime(2025, 6, 1, 17, 0, tzinfo=timezone.utc),
            status=BookingStatus.OK,
        )
    )
    result = repo.list_open_for_employee(employee_id)
    assert len(result) == 1
    assert result[0].id == open_b.id


def test_time_booking_list_between(conn, employee_id):
    repo = SQLiteTimeBookingRepository(conn)
    b_in = repo.add(
        _make_booking(employee_id, booked_at=datetime(2025, 6, 1, 9, 0, tzinfo=timezone.utc))
    )
    # Buchung außerhalb des Zeitraums
    repo.add(_make_booking(employee_id, booked_at=datetime(2025, 6, 5, 8, 0, tzinfo=timezone.utc)))
    result = repo.list_between(
        employee_id,
        datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc),
        datetime(2025, 6, 2, 0, 0, tzinfo=timezone.utc),
    )
    assert len(result) == 1
    assert result[0].id == b_in.id


# --- WorkScheduleRepository ---


def test_work_schedule_add_und_get_effective_roundtrip(conn):
    repo = SQLiteWorkScheduleRepository(conn)
    added = repo.add(_make_work_schedule())
    assert added.id > 0
    found = repo.get_effective(weekday=_WEEKDAY, on_date=_TODAY)
    assert found is not None
    assert found.id == added.id


def test_work_schedule_list_versions_filtert_nach_scope(conn, employee_id):
    repo = SQLiteWorkScheduleRepository(conn)
    repo.add(_make_work_schedule(scope_type=ScopeType.GLOBAL))
    repo.add(_make_work_schedule(scope_type=ScopeType.EMPLOYEE, scope_employee_id=employee_id))
    global_versions = repo.list_versions(weekday=_WEEKDAY, scope_employee_id=None)
    employee_versions = repo.list_versions(weekday=_WEEKDAY, scope_employee_id=employee_id)
    assert all(v.scope_type == ScopeType.GLOBAL for v in global_versions)
    assert all(v.scope_type == ScopeType.EMPLOYEE for v in employee_versions)


def test_work_schedule_get_effective_zwei_employee_versionen_waehlt_neuere(conn, employee_id):
    """Pflicht-Testfall: Infrastruktur selektiert deterministisch die neuere Version."""
    repo = SQLiteWorkScheduleRepository(conn)
    repo.add(
        _make_work_schedule(
            scope_type=ScopeType.EMPLOYEE,
            scope_employee_id=employee_id,
            valid_from=date(2024, 1, 1),
            start_time=time(8, 0),
            end_time=time(12, 0),
        )
    )
    newer = repo.add(
        _make_work_schedule(
            scope_type=ScopeType.EMPLOYEE,
            scope_employee_id=employee_id,
            valid_from=date(2025, 1, 1),
            start_time=time(9, 0),
            end_time=time(13, 0),
        )
    )
    result = repo.get_effective(weekday=_WEEKDAY, on_date=date(2025, 6, 1), employee_id=employee_id)
    assert result is not None
    assert result.id == newer.id
    assert result.start_time == time(9, 0)


# --- BookingCorrectionRepository ---


def test_booking_correction_add_und_list_for_booking_roundtrip(conn, employee_id, user_id):
    booking_repo = SQLiteTimeBookingRepository(conn)
    corr_repo = SQLiteBookingCorrectionRepository(conn)
    booking = booking_repo.add(_make_booking(employee_id))
    correction = corr_repo.add(
        BookingCorrection(
            id=0,
            original_booking_id=booking.id,
            corrected_by_user_id=user_id,
            reason="Buchungstyp falsch erfasst",
            old_booking_type=BookingType.COME,
            old_booked_at=_NOW,
            new_booking_type=BookingType.GO,
            new_booked_at=datetime(2025, 6, 1, 17, 0, tzinfo=timezone.utc),
            created_at=_NOW,
        )
    )
    assert correction.id > 0
    corrections = corr_repo.list_for_booking(booking.id)
    assert len(corrections) == 1
    assert corrections[0].id == correction.id
    assert corrections[0].new_booking_type == BookingType.GO


# --- AuditLogRepository ---


def test_audit_log_add_weist_id_zu(conn):
    repo = SQLiteAuditLogRepository(conn)
    entry = repo.add(
        AuditLogEntry(
            id=0,
            event_type="TEST_EVENT",
            object_type="TEST_OBJECT",
            object_id=42,
            user_id=None,
            employee_id=None,
            event_at=_NOW,
            details_json='{"test": true}',
        )
    )
    assert entry.id > 0


# --- SystemConfigRepository ---


def test_system_config_get_current_gibt_none_fuer_unbekannten_schluessel(conn):
    assert SQLiteSystemConfigRepository(conn).get_current("test.unbekannt") is None


def test_system_config_set_current_und_get_current_roundtrip(conn, user_id):
    repo = SQLiteSystemConfigRepository(conn)
    repo.set_current(
        config_key="test.wert",
        value_json='"hallo"',
        change_origin=ChangeOrigin.ADMIN_UI,
        changed_by_user_id=user_id,
        changed_at=_NOW,
    )
    assert repo.get_current("test.wert") == '"hallo"'


def test_system_config_set_current_zweimal_inkrementiert_version(conn, user_id):
    repo = SQLiteSystemConfigRepository(conn)
    repo.set_current(
        config_key="test.versioniert",
        value_json='"v1"',
        change_origin=ChangeOrigin.ADMIN_UI,
        changed_by_user_id=user_id,
        changed_at=_NOW,
    )
    repo.set_current(
        config_key="test.versioniert",
        value_json='"v2"',
        change_origin=ChangeOrigin.ADMIN_UI,
        changed_by_user_id=user_id,
        changed_at=_NOW,
    )
    assert repo.get_current("test.versioniert") == '"v2"'
    rows = conn.execute(
        "SELECT version FROM system_config WHERE config_key = 'test.versioniert' "
        "ORDER BY version"
    ).fetchall()
    assert [r["version"] for r in rows] == [1, 2]
