"""Tests für presentation/terminal_ui/main.py."""

import logging
import os
import signal
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.errors import (
    InvalidBookingSequenceError,
    OpenPhaseConflictError,
    UnknownCardError,
)
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.system_check import CheckResult, SystemCheckResult
from arbeitszeit.presentation.terminal_ui.main import _log_system_event, _run_one_cycle, run

_MAIN = "arbeitszeit.presentation.terminal_ui.main"


def _ok_system_result() -> SystemCheckResult:
    return SystemCheckResult(checks=(CheckResult("db_access", True, "OK"),))


def _fail_system_result() -> SystemCheckResult:
    return SystemCheckResult(
        checks=(CheckResult("ntp_sync", False, "NTP nicht aktiv (NTP=no)"),)
    )


def _make_db(tmp_path: Path) -> Path:
    db = tmp_path / "test.db"
    conn = open_connection(db)
    run_migrations(conn)
    conn.close()
    return db


# ---------------------------------------------------------------------------
# _log_system_event
# ---------------------------------------------------------------------------


def test_log_system_event_schreibt_in_system_events(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    _log_system_event(db, "APPLICATION_ERROR", {"error": "Testfehler", "type": "RuntimeError"})
    conn = open_connection(db)
    row = conn.execute(
        "SELECT event_type, source, severity FROM system_events "
        "WHERE event_type = 'APPLICATION_ERROR'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["event_type"] == "APPLICATION_ERROR"
    assert row["source"] == "terminal_ui"
    assert row["severity"] == "ERROR"


def test_log_system_event_ungueltige_db_loggt_warnung_kein_crash(
    caplog: pytest.LogCaptureFixture,
) -> None:
    invalid_db = Path("/nonexistent_dir/no.db")
    with caplog.at_level(logging.WARNING):
        _log_system_event(invalid_db, "APP_ERROR", {"error": "x"})
    assert any("_log_system_event" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# _run_one_cycle
# ---------------------------------------------------------------------------


def _make_mock_monitor() -> MagicMock:
    monitor = MagicMock()
    monitor.check.return_value = None
    return monitor


def _make_mock_reader() -> MagicMock:
    return MagicMock()


def test_run_one_cycle_erfolg_druckt_feedback(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    reader = _make_mock_reader()
    monitor = _make_mock_monitor()
    mock_result = MagicMock()

    with (
        patch(
            "arbeitszeit.presentation.terminal_ui.main.process_booking",
            return_value=mock_result,
        ),
        patch(
            "arbeitszeit.presentation.terminal_ui.main.format_feedback",
            return_value="Buchung OK",
        ),
    ):
        _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    out = capsys.readouterr().out
    assert "Buchung OK" in out
    monitor.check.assert_called_once()


def test_run_one_cycle_domain_error_bekannt_druckt_meldung(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    reader = _make_mock_reader()
    monitor = _make_mock_monitor()

    with patch(
        "arbeitszeit.presentation.terminal_ui.main.process_booking",
        side_effect=UnknownCardError("Test"),
    ):
        _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    out = capsys.readouterr().out
    assert "Karte nicht erkannt" in out


def test_run_one_cycle_domain_error_unbekannt_zeigt_fehlermeldung(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    reader = _make_mock_reader()
    monitor = _make_mock_monitor()

    class _CustomDomainError(InvalidBookingSequenceError):
        pass

    with patch(
        "arbeitszeit.presentation.terminal_ui.main.process_booking",
        side_effect=InvalidBookingSequenceError("Spezifische Meldung"),
    ):
        _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    out = capsys.readouterr().out
    assert "Buchungsreihenfolge" in out


def test_run_one_cycle_generic_exception_loggt_und_faehrt_fort(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    reader = _make_mock_reader()
    monitor = _make_mock_monitor()

    with patch(
        "arbeitszeit.presentation.terminal_ui.main.process_booking",
        side_effect=RuntimeError("unerwarteter Fehler"),
    ):
        _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    err = capsys.readouterr().err
    assert "Interner Fehler" in err

    conn = open_connection(db)
    row = conn.execute(
        "SELECT event_type FROM system_events WHERE event_type = 'APPLICATION_ERROR'"
    ).fetchone()
    conn.close()
    assert row is not None


def test_run_one_cycle_open_phase_conflict_druckt_meldung(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    reader = _make_mock_reader()
    monitor = _make_mock_monitor()

    with patch(
        "arbeitszeit.presentation.terminal_ui.main.process_booking",
        side_effect=OpenPhaseConflictError("conflict"),
    ):
        _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    out = capsys.readouterr().out
    assert "Offene Phase" in out


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------


def test_run_schliesst_reader_in_finally(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    with (
        patch(f"{_MAIN}.run_system_check", return_value=_ok_system_result()),
        patch(f"{_MAIN}.EvdevHardwareReader") as mock_reader_cls,
        patch(f"{_MAIN}._run_one_cycle", side_effect=StopIteration),
    ):
        with pytest.raises(StopIteration):
            run(db, "/dev/null", "/dev/null", 1)
    mock_reader_cls.return_value.close.assert_called_once()


def test_run_systemcheck_fehlerhaft_druckt_systemwarnung(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    db = _make_db(tmp_path)
    with (
        patch(f"{_MAIN}.run_system_check", return_value=_fail_system_result()),
        patch(f"{_MAIN}.notify"),
        patch(f"{_MAIN}.EvdevHardwareReader"),
        patch(f"{_MAIN}._run_one_cycle", side_effect=StopIteration),
    ):
        with pytest.raises(StopIteration):
            run(db, "/dev/null", "/dev/null", 1)
    out = capsys.readouterr().out
    assert "SYSTEMWARNUNG" in out
    assert "NTP" in out


def test_run_systemcheck_fehlerhaft_ruft_notify_critical_auf(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    with (
        patch(f"{_MAIN}.run_system_check", return_value=_fail_system_result()),
        patch(f"{_MAIN}.notify") as mock_notify,
        patch(f"{_MAIN}.EvdevHardwareReader"),
        patch(f"{_MAIN}._run_one_cycle", side_effect=StopIteration),
    ):
        with pytest.raises(StopIteration):
            run(db, "/dev/null", "/dev/null", 1)
    mock_notify.assert_called_once()
    assert mock_notify.call_args.kwargs.get("urgency") == "critical"


def test_run_initialisiert_reader_mit_gerätepfaden(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    with (
        patch(f"{_MAIN}.run_system_check", return_value=_ok_system_result()),
        patch(f"{_MAIN}.resolve_evdev_device", side_effect=lambda x: x),
        patch(f"{_MAIN}.EvdevHardwareReader") as mock_reader_cls,
        patch(f"{_MAIN}._run_one_cycle", side_effect=StopIteration),
    ):
        with pytest.raises(StopIteration):
            run(db, "/dev/numpad", "/dev/rfid", 1)
    mock_reader_cls.assert_called_once()
    kwargs = mock_reader_cls.call_args.kwargs
    assert kwargs.get("numpad_path") == "/dev/numpad"
    assert kwargs.get("rfid_path") == "/dev/rfid"
    assert isinstance(kwargs.get("rfid_timeout"), float)


def test_run_sigterm_beendet_schleife_sauber(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    cycle_count = [0]

    def fake_cycle(*_args: object, **_kwargs: object) -> None:
        cycle_count[0] += 1
        if cycle_count[0] == 1:
            os.kill(os.getpid(), signal.SIGTERM)

    with (
        patch(f"{_MAIN}.run_system_check", return_value=_ok_system_result()),
        patch(f"{_MAIN}.EvdevHardwareReader") as mock_reader_cls,
        patch(f"{_MAIN}._run_one_cycle", side_effect=fake_cycle),
    ):
        run(db, "/dev/null", "/dev/null", 1)

    assert cycle_count[0] == 1
    mock_reader_cls.return_value.close.assert_called_once()
