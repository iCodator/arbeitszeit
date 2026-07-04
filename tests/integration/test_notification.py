"""Tests für infrastructure/notification.py — alle vier Ausführungspfade."""

import logging
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.notification import notify

_PATCH = "arbeitszeit.infrastructure.notification.subprocess.run"


def test_notify_erfolg_ruft_subprocess_auf() -> None:
    with patch(_PATCH) as mock_run:
        notify("Titel", "Text")
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[0] == "/usr/bin/notify-send"
    assert "--urgency=normal" in args
    assert "Titel" in args
    assert "Text" in args


def test_notify_urgency_wird_uebergeben() -> None:
    with patch(_PATCH) as mock_run:
        notify("T", "B", urgency="critical")
    args = mock_run.call_args[0][0]
    assert "--urgency=critical" in args


def test_notify_file_not_found_loggt_debug_kein_crash(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with patch(_PATCH, side_effect=FileNotFoundError):
        with caplog.at_level(logging.DEBUG):
            notify("T", "B")
    assert any("notify-send" in r.message for r in caplog.records)


def test_notify_timeout_expired_loggt_debug_kein_crash(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with patch(_PATCH, side_effect=subprocess.TimeoutExpired(cmd="x", timeout=3)):
        with caplog.at_level(logging.DEBUG):
            notify("T", "B")
    assert any("notify-send" in r.message for r in caplog.records)


def test_notify_generic_exception_loggt_warning_kein_crash(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with patch(_PATCH, side_effect=RuntimeError("unbekannter Fehler")):
        with caplog.at_level(logging.WARNING):
            notify("T", "B")
    assert any("notification.notify" in r.message for r in caplog.records)
