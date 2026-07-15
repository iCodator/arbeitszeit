import sqlite3
import sys
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations


@pytest.fixture
def conn(tmp_path: Path) -> Generator[sqlite3.Connection, None, None]:
    connection = open_connection(tmp_path / "test.db")
    run_migrations(connection)
    yield connection
    connection.close()


@pytest.fixture
def employee_id(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "INSERT INTO employees "
        "(personnel_no, first_name, last_name, active, created_at, updated_at) "
        "VALUES ('E001', 'Test', 'User', 1, '2025-01-01', '2025-01-01') RETURNING id"
    ).fetchone()
    return int(row["id"])


@pytest.fixture
def user_id(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, active, created_at, updated_at) "
        "VALUES ('admin', 'hash', 'ADMIN', 1, '2025-01-01', '2025-01-01') RETURNING id"
    ).fetchone()
    return int(row["id"])
