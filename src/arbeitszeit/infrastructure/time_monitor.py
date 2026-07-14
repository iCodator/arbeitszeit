"""Systemzeitprotokollierung: Erkennung von Zeitsprüngen und manuellen Uhrzeitänderungen.

Pflichtenheft v5 §9.3 / Regelwerk v5 §21.

Strategie: Monotone Clock (time.monotonic()) ist unabhängig von Systemuhranpassungen.
Durch Vergleich des Monoton-Deltas mit dem Wall-Clock-Delta lassen sich Sprünge erkennen:
- Vorwärtssprung (diff > threshold): TIME_JUMP_DETECTED (NTP-Korrektur oder Manuell)
- Rückwärtssprung (diff < -threshold): MANUAL_TIME_CHANGE_DETECTED (fast immer manuell)

Die NTP-Synchronisation ist Betriebsvoraussetzung und nicht Aufgabe dieser Schicht.
NTP-Drift (< 1s/Stunde) wird durch den konfigurierbaren Schwellenwert herausgefiltert.
"""

__version__ = "1.0"

import json
import logging
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from arbeitszeit.infrastructure.db.connection import open_connection


class SystemTimeMonitor:
    """Erkennt Zeitsprünge durch Gegenüberstellung von Wall-Clock und Monotonic-Clock."""

    def __init__(
        self,
        db_path: Path,
        threshold_seconds: float = 60.0,
        *,
        _wall_clock: Callable[[], datetime] | None = None,
        _mono_clock: Callable[[], float] | None = None,
    ) -> None:
        self._db_path = db_path
        self._threshold = threshold_seconds
        self._wall_clock = _wall_clock or (lambda: datetime.now(timezone.utc))
        self._mono_clock = _mono_clock or time.monotonic
        self._last_wall: datetime | None = None
        self._last_mono: float | None = None

    def check(self) -> None:
        """Nimmt Zeitsample; schreibt system_events-Eintrag bei erkanntem Sprung."""
        mono_now = self._mono_clock()
        wall_now = self._wall_clock()

        if self._last_wall is not None and self._last_mono is not None:
            mono_elapsed = mono_now - self._last_mono
            expected_wall_ts = self._last_wall.timestamp() + mono_elapsed
            actual_wall_ts = wall_now.timestamp()
            diff = actual_wall_ts - expected_wall_ts

            if abs(diff) > self._threshold:
                event_type = "MANUAL_TIME_CHANGE_DETECTED" if diff < 0 else "TIME_JUMP_DETECTED"
                self._log(event_type, diff, wall_now)

        self._last_wall = wall_now
        self._last_mono = mono_now

    def _log(self, event_type: str, diff_seconds: float, event_at: datetime) -> None:
        try:
            conn = open_connection(self._db_path)
            try:
                conn.execute(
                    "INSERT INTO system_events "
                    "(event_type, source, severity, event_at, details_json) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        event_type,
                        "time_monitor",
                        "WARN",
                        event_at.isoformat(),
                        json.dumps(
                            {"diff_seconds": round(diff_seconds, 3)},
                            ensure_ascii=False,
                        ),
                    ),
                )
            finally:
                conn.close()
        except Exception as exc:  # noqa: BLE001
            logging.warning("time_monitor._log fehlgeschlagen: %s", exc)


def load_threshold_from_config(db_path: Path, default: float = 60.0) -> float:
    """Liest time_monitor.jump_threshold_seconds aus system_config, Fallback: default."""
    try:
        conn = open_connection(db_path)
        try:
            row = conn.execute(
                "SELECT config_value_json FROM system_config "
                "WHERE config_key = 'time_monitor.jump_threshold_seconds' "
                "ORDER BY version DESC LIMIT 1"
            ).fetchone()
            if row is not None:
                return float(json.loads(row["config_value_json"]))
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        logging.warning(
            "load_threshold_from_config fehlgeschlagen, verwende Standard %.1f: %s",
            default,
            exc,
            exc_info=True,
        )
    return default
