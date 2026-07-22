import binascii
import hashlib
import os
import sqlite3
import sys
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations

# Passwort für alle test-internen Admin-Accounts (via make_seed_password_hash).
# Wird von _patch_cli_getpass als getpass-Antwort injiziert.
SEED_ADMIN_PASSWORD = "testpass"


def make_seed_password_hash(password: str = SEED_ADMIN_PASSWORD) -> str:
    """PBKDF2-Hash für Test-Passwörter, identisch mit user_accounts._hash_password."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return binascii.hexlify(salt).decode() + ":" + binascii.hexlify(dk).decode()


@pytest.fixture(autouse=True)
def _patch_cli_getpass(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patcht getpass.getpass für alle Integrationstests → SEED_ADMIN_PASSWORD."""
    import getpass as _gp

    monkeypatch.setattr(_gp, "getpass", lambda prompt="": SEED_ADMIN_PASSWORD)


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
