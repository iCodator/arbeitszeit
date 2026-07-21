"""pytest-Fixtures für das gesamte tests/-Verzeichnis."""

__version__ = "1.0"

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.helpers import make_config_toml as _make_config_toml


@pytest.fixture
def make_config_toml(tmp_path: Path) -> Callable[..., Path]:
    def factory(
        *,
        database_path: Path | None = None,
        rfid: str | None = None,
        backup_dir: Path | None = None,
        export_dir: Path | None = None,
        log_dir: Path | None = None,
        admin_user_id: int | None = None,
        filename: str = "config.toml",
    ) -> Path:
        return _make_config_toml(
            tmp_path,
            database_path=database_path,
            rfid=rfid,
            backup_dir=backup_dir,
            export_dir=export_dir,
            log_dir=log_dir,
            admin_user_id=admin_user_id,
            filename=filename,
        )

    return factory
