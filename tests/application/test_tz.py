__version__ = "1.0"

import sys
from datetime import datetime, time, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.application.use_cases._tz import to_local


def test_to_local_cest_sommerzeit() -> None:
    """2025-06-16 06:00 UTC = 08:00 CEST (UTC+2, Sommerzeit)."""
    utc_dt = datetime(2025, 6, 16, 6, 0, tzinfo=timezone.utc)
    assert to_local(utc_dt).time() == time(8, 0)


def test_to_local_cet_winterzeit() -> None:
    """2025-03-10 08:00 UTC = 09:00 CET (UTC+1, Winterzeit)."""
    utc_dt = datetime(2025, 3, 10, 8, 0, tzinfo=timezone.utc)
    assert to_local(utc_dt).time() == time(9, 0)


def test_to_local_dst_uebergang_wochentag() -> None:
    """2025-06-15 22:30 UTC (Sonntag) = 00:30 CEST Montag (isoweekday=1)."""
    utc_dt = datetime(2025, 6, 15, 22, 30, tzinfo=timezone.utc)
    local_dt = to_local(utc_dt)
    assert local_dt.isoweekday() == 1  # Montag
    assert local_dt.time() == time(0, 30)
