import sqlite3
from datetime import date, datetime, timezone

from arbeitszeit.domain.entities import WorkScheduleVersion
from arbeitszeit.domain.enums import ChangeOrigin, ScopeType
from arbeitszeit.domain.errors import NotFoundError, ValidationError

from ._helpers import _parse_date, _parse_time

_SELECT = (
    "SELECT id, scope_type, scope_employee_id, weekday, start_time, end_time, "
    "valid_from, valid_until, change_origin, changed_by_user_id "
    "FROM work_schedule_versions"
)


class SQLiteWorkScheduleRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, version: WorkScheduleVersion) -> WorkScheduleVersion:
        row = self._conn.execute(
            "INSERT INTO work_schedule_versions "
            "(scope_type, scope_employee_id, weekday, start_time, end_time, "
            "valid_from, valid_until, change_origin, changed_by_user_id, changed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (
                version.scope_type.value,
                version.scope_employee_id,
                version.weekday,
                version.start_time.strftime("%H:%M"),
                version.end_time.strftime("%H:%M"),
                version.valid_from.isoformat(),
                version.valid_until.isoformat() if version.valid_until else None,
                version.change_origin.value,
                version.changed_by_user_id,
                datetime.now(timezone.utc).isoformat(),
            ),
        ).fetchone()
        return WorkScheduleVersion(
            id=row["id"],
            scope_type=version.scope_type,
            scope_employee_id=version.scope_employee_id,
            weekday=version.weekday,
            start_time=version.start_time,
            end_time=version.end_time,
            valid_from=version.valid_from,
            valid_until=version.valid_until,
            change_origin=version.change_origin,
            changed_by_user_id=version.changed_by_user_id,
        )

    def close_version(self, version_id: int, valid_until: date) -> None:
        row = self._conn.execute(
            "SELECT valid_from FROM work_schedule_versions WHERE id = ?",
            (version_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError(f"WorkScheduleVersion {version_id} nicht gefunden.")
        valid_from = _parse_date(row["valid_from"])
        if valid_until < valid_from:
            raise ValidationError(f"valid_until {valid_until} liegt vor valid_from {valid_from}.")
        self._conn.execute(
            "UPDATE work_schedule_versions SET valid_until = ? WHERE id = ?",
            (valid_until.isoformat(), version_id),
        )

    def get_effective(
        self,
        weekday: int,
        on_date: date,
        employee_id: int | None = None,
    ) -> WorkScheduleVersion | None:
        on_date_s = on_date.isoformat()
        if employee_id is not None:
            row = self._conn.execute(
                f"{_SELECT} WHERE scope_type = 'EMPLOYEE' AND scope_employee_id = ? "
                "AND weekday = ? AND valid_from <= ? "
                "AND (valid_until IS NULL OR valid_until >= ?) "
                "ORDER BY valid_from DESC LIMIT 1",
                (employee_id, weekday, on_date_s, on_date_s),
            ).fetchone()
            if row:
                return _row_to_version(row)

        row = self._conn.execute(
            f"{_SELECT} WHERE scope_type = 'GLOBAL' AND weekday = ? "
            "AND valid_from <= ? AND (valid_until IS NULL OR valid_until >= ?) "
            "ORDER BY valid_from DESC LIMIT 1",
            (weekday, on_date_s, on_date_s),
        ).fetchone()
        return _row_to_version(row) if row else None

    def list_versions(
        self,
        weekday: int | None = None,
        scope_employee_id: int | None = None,
    ) -> list[WorkScheduleVersion]:
        # scope_employee_id=None bedeutet GLOBAL-Scope (kein "alle Scopes").
        # Caller, der EMPLOYEE-Versionen sucht, muss eine konkrete employee_id übergeben.
        scope_type = ScopeType.EMPLOYEE if scope_employee_id is not None else ScopeType.GLOBAL
        if weekday is not None:
            rows = self._conn.execute(
                f"{_SELECT} WHERE scope_type = ? AND scope_employee_id IS ? "
                "AND weekday = ? ORDER BY valid_from",
                (scope_type.value, scope_employee_id, weekday),
            ).fetchall()
        else:
            rows = self._conn.execute(
                f"{_SELECT} WHERE scope_type = ? AND scope_employee_id IS ? " "ORDER BY valid_from",
                (scope_type.value, scope_employee_id),
            ).fetchall()
        return [_row_to_version(r) for r in rows]


def _row_to_version(row: sqlite3.Row) -> WorkScheduleVersion:
    return WorkScheduleVersion(
        id=row["id"],
        scope_type=ScopeType(row["scope_type"]),
        scope_employee_id=row["scope_employee_id"],
        weekday=row["weekday"],
        start_time=_parse_time(row["start_time"]),
        end_time=_parse_time(row["end_time"]),
        valid_from=_parse_date(row["valid_from"]),
        valid_until=_parse_date(row["valid_until"]) if row["valid_until"] else None,
        change_origin=ChangeOrigin(row["change_origin"]),
        changed_by_user_id=row["changed_by_user_id"],
    )
