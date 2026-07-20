"""Tests für presentation/terminal_ui/main.py."""

__version__ = "1.2"

import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.enums import AdminAction
from arbeitszeit.domain.errors import (
    InvalidBookingSequenceError,
    OpenPhaseConflictError,
    UnknownCardError,
)
from arbeitszeit.infrastructure.config_file import AppConfig, BackupConfig
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.hardware.evdev_reader import DeviceNotFoundError
from arbeitszeit.infrastructure.hardware.ports import AdminActionRequest
from arbeitszeit.infrastructure.hardware.simulator import SimulatedHardwareReader
from arbeitszeit.infrastructure.system_check import CheckResult, SystemCheckResult
from arbeitszeit.presentation.terminal_ui.main import (
    CycleResult,
    _handle_admin_action,
    _log_system_event,
    _resolve_or_exit,
    _run_one_cycle,
    _setup_file_logging,
    _should_continue,
    main,
    run,
)

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


@pytest.fixture
def no_sleep_no_clear() -> Generator[None, None, None]:
    with (
        patch("time.sleep"),
        patch(f"{_MAIN}._clear_screen"),
    ):
        yield


def test_run_one_cycle_erfolg_druckt_feedback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], no_sleep_no_clear: None
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
    tmp_path: Path, capsys: pytest.CaptureFixture[str], no_sleep_no_clear: None
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
    tmp_path: Path, capsys: pytest.CaptureFixture[str], no_sleep_no_clear: None
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
    tmp_path: Path, capsys: pytest.CaptureFixture[str], no_sleep_no_clear: None
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
    tmp_path: Path, capsys: pytest.CaptureFixture[str], no_sleep_no_clear: None
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
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
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


def test_run_device_not_found_ruft_notify_auf_und_beendet(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    with (
        patch(
            f"{_MAIN}.resolve_evdev_device",
            side_effect=DeviceNotFoundError("Gerät nicht gefunden"),
        ),
        patch(f"{_MAIN}.notify") as mock_notify,
        pytest.raises(SystemExit) as exc_info,
    ):
        run(db, "USB Numpad", "RFID Reader", 1)

    assert exc_info.value.code == 1
    mock_notify.assert_called_once()
    assert mock_notify.call_args.kwargs.get("urgency") == "critical"


# ---------------------------------------------------------------------------
# _resolve_or_exit
# ---------------------------------------------------------------------------


def test_resolve_or_exit_gibt_cli_val_zurueck() -> None:
    assert _resolve_or_exit(42, 7, "label") == 42


def test_resolve_or_exit_gibt_cfg_val_als_fallback() -> None:
    assert _resolve_or_exit(None, 7, "label") == 7


def test_resolve_or_exit_beendet_programm_wenn_beide_none(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        _resolve_or_exit(None, None, "mein-parameter")
    assert exc_info.value.code == 1
    assert "mein-parameter" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# _setup_file_logging
# ---------------------------------------------------------------------------


def _insert_log_dir(db: Path, log_dir_str: str | None) -> None:
    conn = open_connection(db)
    try:
        conn.execute(
            "INSERT INTO system_config "
            "(config_key, config_value_json, version, change_origin, "
            "changed_by_user_id, changed_at, reason) "
            "VALUES ('logging.log_dir', ?, 1, 'MIGRATION', NULL, '2025-01-01T00:00:00', NULL)",
            (json.dumps(log_dir_str),),
        )
    finally:
        conn.close()


@pytest.fixture
def clean_root_logger() -> Generator[logging.Logger, None, None]:
    """Root-Logger-State nach dem Test wiederherstellen."""
    root = logging.getLogger()
    handlers_before = list(root.handlers)
    level_before = root.level
    yield root
    for handler in list(root.handlers):
        if handler not in handlers_before:
            handler.close()
            root.removeHandler(handler)
    root.setLevel(level_before)


def test_setup_file_logging_ohne_konfiguration_kein_handler(
    tmp_path: Path, clean_root_logger: logging.Logger
) -> None:
    db = _make_db(tmp_path)
    handlers_before = list(clean_root_logger.handlers)
    _setup_file_logging(db)
    assert clean_root_logger.handlers == handlers_before


def test_setup_file_logging_db_mit_log_dir_erstellt_file_handler(
    tmp_path: Path, clean_root_logger: logging.Logger
) -> None:
    db = _make_db(tmp_path)
    log_dir = tmp_path / "logs"
    _insert_log_dir(db, str(log_dir))

    _setup_file_logging(db)

    file_handlers = [
        h for h in clean_root_logger.handlers
        if isinstance(h, logging.FileHandler)
        and "terminal_ui.log" in getattr(h, "baseFilename", "")
    ]
    assert len(file_handlers) == 1
    assert str(log_dir) in file_handlers[0].baseFilename


def test_setup_file_logging_db_null_value_kein_handler(
    tmp_path: Path, clean_root_logger: logging.Logger
) -> None:
    db = _make_db(tmp_path)
    _insert_log_dir(db, None)  # JSON null
    handlers_before = list(clean_root_logger.handlers)

    _setup_file_logging(db)

    assert clean_root_logger.handlers == handlers_before


def test_setup_file_logging_app_config_log_dir_vorrang_vor_db(
    tmp_path: Path, clean_root_logger: logging.Logger
) -> None:
    db = _make_db(tmp_path)
    log_dir = tmp_path / "config_logs"
    app_config = AppConfig(backup=BackupConfig(log_dir=log_dir))

    _setup_file_logging(db, app_config=app_config)

    file_handlers = [
        h for h in clean_root_logger.handlers
        if isinstance(h, logging.FileHandler)
        and "terminal_ui.log" in getattr(h, "baseFilename", "")
    ]
    assert len(file_handlers) == 1
    assert str(log_dir) in file_handlers[0].baseFilename


def test_setup_file_logging_fehler_loggt_warnung_kein_crash(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    clean_root_logger: logging.Logger,
) -> None:
    db = _make_db(tmp_path)
    _insert_log_dir(db, str(tmp_path / "logs"))

    with (
        caplog.at_level(logging.WARNING),
        patch("logging.FileHandler", side_effect=OSError("Permission denied")),
    ):
        _setup_file_logging(db)  # darf nicht werfen

    assert any("Logging-Konfiguration" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def test_main_alle_cli_args_ruft_run_auf(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    with (
        patch(
            "sys.argv",
            ["prog", "--db", str(db), "--numpad", "Numpad", "--rfid", "RFID", "--terminal-id", "1"],
        ),
        patch(f"{_MAIN}.find_config", return_value=None),
        patch(f"{_MAIN}.run") as mock_run,
    ):
        main()

    mock_run.assert_called_once_with(db, "Numpad", "RFID", 1, app_config=None)


def test_main_config_datei_laedt_werte_und_ruft_run_auf(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    config_toml = tmp_path / "config.toml"
    config_toml.write_text(
        f'[database]\npath = "{db}"\n\n[terminal]\nnumpad = "Numpad"\nrfid = "RFID"\nid = 1\n'
    )
    with (
        patch("sys.argv", ["prog", "--config", str(config_toml)]),
        patch(f"{_MAIN}.run") as mock_run,
    ):
        main()

    mock_run.assert_called_once()
    call_args = mock_run.call_args
    assert call_args.args[0] == db
    assert call_args.kwargs["app_config"] is not None


def test_main_defekte_config_datei_beendet_programm(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad_config = tmp_path / "bad.toml"
    bad_config.write_text("[ungueltig toml")
    with (
        patch("sys.argv", ["prog", "--config", str(bad_config)]),
        pytest.raises(SystemExit) as exc_info,
    ):
        main()

    assert exc_info.value.code == 1
    assert bad_config.name in capsys.readouterr().err


def test_main_fehlender_db_arg_beendet_programm(capsys: pytest.CaptureFixture[str]) -> None:
    with (
        patch("sys.argv", ["prog", "--numpad", "Numpad", "--rfid", "RFID", "--terminal-id", "1"]),
        patch(f"{_MAIN}.find_config", return_value=None),
        pytest.raises(SystemExit) as exc_info,
    ):
        main()

    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "database" in err or "--db" in err


# ---------------------------------------------------------------------------
# _log_system_event — severity-Parameter
# ---------------------------------------------------------------------------


def test_log_system_event_info_severity_wird_gespeichert(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    _log_system_event(
        db,
        "ADMIN_ACCESS_GRANTED",
        {"card_id": 1, "action": "STOP"},
        severity="INFO",
    )
    conn = open_connection(db)
    row = conn.execute(
        "SELECT severity FROM system_events WHERE event_type = 'ADMIN_ACCESS_GRANTED'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["severity"] == "INFO"


def test_log_system_event_warn_severity_wird_gespeichert(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    _log_system_event(
        db,
        "ADMIN_ACCESS_DENIED",
        {"uid_hash_prefix": "aabbccdd"},
        severity="WARN",
    )
    conn = open_connection(db)
    row = conn.execute(
        "SELECT severity FROM system_events WHERE event_type = 'ADMIN_ACCESS_DENIED'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["severity"] == "WARN"


# ---------------------------------------------------------------------------
# _should_continue
# ---------------------------------------------------------------------------


def test_should_continue_continue_gibt_true() -> None:
    assert _should_continue(CycleResult.CONTINUE, MagicMock()) is True


def test_should_continue_stop_gibt_false() -> None:
    assert _should_continue(CycleResult.STOP, MagicMock()) is False


def test_should_continue_restart_schliesst_reader_und_ruft_execv_auf() -> None:
    reader = MagicMock()
    with patch(f"{_MAIN}.os.execv") as mock_execv:
        _should_continue(CycleResult.RESTART, reader)
    reader.close.assert_called_once()
    mock_execv.assert_called_once()


# ---------------------------------------------------------------------------
# _handle_admin_action
# ---------------------------------------------------------------------------


def _insert_admin_card(db: Path, uid_hash: str, label: str | None = None) -> int:
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO admin_rfid_cards (uid_hash, label, active, created_at) "
        "VALUES (?, ?, 1, '2026-01-01T00:00:00') RETURNING id",
        (uid_hash, label),
    ).fetchone()
    conn.close()
    return int(row["id"])


def _system_events(db: Path, event_type: str) -> list[dict[str, object]]:
    conn = open_connection(db)
    rows = conn.execute(
        "SELECT event_type, severity, details_json FROM system_events "
        "WHERE event_type = ? ORDER BY id",
        (event_type,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@pytest.fixture
def no_sleep_clear() -> Generator[None, None, None]:
    with (
        patch("time.sleep"),
        patch(f"{_MAIN}._clear_screen"),
    ):
        yield


def test_handle_admin_action_bekannte_karte_stop_gibt_stop(
    tmp_path: Path, no_sleep_clear: None
) -> None:
    db = _make_db(tmp_path)
    uid_hash = "aabbccdd" * 8
    _insert_admin_card(db, uid_hash, label="Testkarte")

    sim = SimulatedHardwareReader()
    sim.inject_rfid_uid_hash(uid_hash)

    result = _handle_admin_action(AdminAction.STOP, sim, db, terminal_id=1)
    assert result == CycleResult.STOP


def test_handle_admin_action_bekannte_karte_restart_gibt_restart(
    tmp_path: Path, no_sleep_clear: None
) -> None:
    db = _make_db(tmp_path)
    uid_hash = "deadbeef" * 8
    _insert_admin_card(db, uid_hash, label="Neustarter")

    sim = SimulatedHardwareReader()
    sim.inject_rfid_uid_hash(uid_hash)

    result = _handle_admin_action(AdminAction.RESTART, sim, db, terminal_id=1)
    assert result == CycleResult.RESTART


def test_handle_admin_action_bekannte_karte_schreibt_access_granted(
    tmp_path: Path, no_sleep_clear: None
) -> None:
    db = _make_db(tmp_path)
    uid_hash = "11223344" * 8
    card_id = _insert_admin_card(db, uid_hash, label="Karte A")

    sim = SimulatedHardwareReader()
    sim.inject_rfid_uid_hash(uid_hash)

    _handle_admin_action(AdminAction.STOP, sim, db, terminal_id=2)

    events = _system_events(db, "ADMIN_ACCESS_GRANTED")
    assert len(events) == 1
    assert events[0]["severity"] == "INFO"
    details = json.loads(str(events[0]["details_json"]))
    assert details["card_id"] == card_id
    assert details["action"] == "STOP"


def test_handle_admin_action_unbekannte_karte_gibt_continue(
    tmp_path: Path, no_sleep_clear: None
) -> None:
    db = _make_db(tmp_path)

    sim = SimulatedHardwareReader()
    sim.inject_rfid_uid_hash("unbekannter_hash")

    result = _handle_admin_action(AdminAction.STOP, sim, db, terminal_id=1)
    assert result == CycleResult.CONTINUE


def test_handle_admin_action_unbekannte_karte_schreibt_access_denied(
    tmp_path: Path, no_sleep_clear: None
) -> None:
    db = _make_db(tmp_path)

    sim = SimulatedHardwareReader()
    sim.inject_rfid_uid_hash("unbekannt_xyz")

    _handle_admin_action(AdminAction.RESTART, sim, db, terminal_id=1)

    events = _system_events(db, "ADMIN_ACCESS_DENIED")
    assert len(events) == 1
    assert events[0]["severity"] == "WARN"


def test_handle_admin_action_lesefehler_gibt_continue(
    tmp_path: Path, no_sleep_clear: None
) -> None:
    db = _make_db(tmp_path)
    sim = SimulatedHardwareReader()

    result = _handle_admin_action(AdminAction.STOP, sim, db, terminal_id=1)
    assert result == CycleResult.CONTINUE


def test_handle_admin_action_lesefehler_schreibt_kein_system_event(
    tmp_path: Path, no_sleep_clear: None
) -> None:
    db = _make_db(tmp_path)
    sim = SimulatedHardwareReader()

    _handle_admin_action(AdminAction.STOP, sim, db, terminal_id=1)

    conn = open_connection(db)
    count = conn.execute("SELECT COUNT(*) FROM system_events").fetchone()[0]
    conn.close()
    assert count == 0


# ---------------------------------------------------------------------------
# _run_one_cycle — CycleResult-Rückgabewert + AdminActionRequest
# ---------------------------------------------------------------------------


def test_run_one_cycle_erfolg_gibt_continue(
    tmp_path: Path, no_sleep_no_clear: None
) -> None:
    db = _make_db(tmp_path)
    reader = _make_mock_reader()
    monitor = _make_mock_monitor()

    with (
        patch(f"{_MAIN}.process_booking", return_value=MagicMock()),
        patch(f"{_MAIN}.format_feedback", return_value="OK"),
    ):
        result = _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    assert result == CycleResult.CONTINUE


def test_run_one_cycle_domain_error_gibt_continue(
    tmp_path: Path, no_sleep_no_clear: None
) -> None:
    db = _make_db(tmp_path)
    reader = _make_mock_reader()
    monitor = _make_mock_monitor()

    with patch(f"{_MAIN}.process_booking", side_effect=UnknownCardError("x")):
        result = _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    assert result == CycleResult.CONTINUE


def test_run_one_cycle_exception_gibt_continue(
    tmp_path: Path, no_sleep_no_clear: None
) -> None:
    db = _make_db(tmp_path)
    reader = _make_mock_reader()
    monitor = _make_mock_monitor()

    with patch(f"{_MAIN}.process_booking", side_effect=RuntimeError("boom")):
        result = _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    assert result == CycleResult.CONTINUE


def test_run_one_cycle_admin_action_request_delegiert_an_handle(
    tmp_path: Path, no_sleep_no_clear: None
) -> None:
    db = _make_db(tmp_path)
    monitor = _make_mock_monitor()
    reader = MagicMock()
    reader.read_next.return_value = AdminActionRequest(action=AdminAction.STOP)

    with patch(
        f"{_MAIN}._handle_admin_action",
        return_value=CycleResult.STOP,
    ) as mock_handle:
        result = _run_one_cycle(reader, db, terminal_id=1, monitor=monitor)

    assert result == CycleResult.STOP
    mock_handle.assert_called_once_with(AdminAction.STOP, reader, db, 1)
