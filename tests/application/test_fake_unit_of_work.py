"""Tests für die commit-or-rollback-Semantik von FakeUnitOfWork."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from tests.application.fakes import FakeUnitOfWork


def test_vergessenes_commit_setzt_rolled_back() -> None:
    uow = FakeUnitOfWork()
    with uow:
        pass  # commit() absichtlich weggelassen

    assert uow.rolled_back is True
    assert uow.committed is False


def test_korrekter_commit_kein_rollback() -> None:
    uow = FakeUnitOfWork()
    with uow:
        uow.commit()

    assert uow.committed is True
    assert uow.rolled_back is False
