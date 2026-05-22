import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork


@pytest.fixture
def conn(tmp_path):
    db = tmp_path / "test.db"
    connection = open_connection(db)
    run_migrations(connection)
    yield connection
    connection.close()


@pytest.fixture
def uow(conn):
    return SQLiteUnitOfWork(conn)


# --- Transaktionsverhalten ---

def test_commit_macht_daten_sichtbar(conn, uow):
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E001', 'Test', 'User', 1, '2025-01-01', '2025-01-01')"
        )
        uow.commit()

    count = conn.execute(
        "SELECT COUNT(*) FROM employees WHERE personnel_no = 'E001'"
    ).fetchone()[0]
    assert count == 1


def test_rollback_verwirft_daten(conn, uow):
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E002', 'Roll', 'Back', 1, '2025-01-01', '2025-01-01')"
        )
        uow.rollback()

    count = conn.execute(
        "SELECT COUNT(*) FROM employees WHERE personnel_no = 'E002'"
    ).fetchone()[0]
    assert count == 0


def test_exception_im_with_block_loest_rollback_aus(conn, uow):
    with pytest.raises(ValueError):
        with uow:
            conn.execute(
                "INSERT INTO employees "
                "(personnel_no, first_name, last_name, active, created_at, updated_at) "
                "VALUES ('E003', 'Ex', 'Ception', 1, '2025-01-01', '2025-01-01')"
            )
            raise ValueError("simulierter Fehler")

    count = conn.execute(
        "SELECT COUNT(*) FROM employees WHERE personnel_no = 'E003'"
    ).fetchone()[0]
    assert count == 0


def test_kein_spurious_rollback_nach_commit(conn, uow):
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E004', 'Spu', 'Rious', 1, '2025-01-01', '2025-01-01')"
        )
        uow.commit()
    # __exit__ wird mit exc_type=None aufgerufen → kein Rollback
    # Daten müssen noch da sein
    count = conn.execute(
        "SELECT COUNT(*) FROM employees WHERE personnel_no = 'E004'"
    ).fetchone()[0]
    assert count == 1


def test_transaction_open_flag_nach_commit_false(conn, uow):
    with uow:
        uow.commit()
    assert not uow._transaction_open


def test_transaction_open_flag_nach_rollback_false(conn, uow):
    with uow:
        uow.rollback()
    assert not uow._transaction_open


def test_mehrfache_transaktionen_hintereinander(conn, uow):
    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E010', 'Erste', 'Transaktion', 1, '2025-01-01', '2025-01-01')"
        )
        uow.commit()

    with uow:
        conn.execute(
            "INSERT INTO employees "
            "(personnel_no, first_name, last_name, active, created_at, updated_at) "
            "VALUES ('E011', 'Zweite', 'Transaktion', 1, '2025-01-01', '2025-01-01')"
        )
        uow.commit()

    count = conn.execute(
        "SELECT COUNT(*) FROM employees WHERE personnel_no IN ('E010', 'E011')"
    ).fetchone()[0]
    assert count == 2
