"""Zeitraum-Hilfsfunktionen für Admin-CLI und Terminal-UI.

Alle Aufrufer, die from_dt/to_dt an Repository-Methoden übergeben, müssen
diese Funktionen nutzen. Ad-hoc-Konstruktion aus Benutzereingaben ist verboten,
da UTC-Normalisierung und halboffene Intervalle [from_dt, to_dt) sonst nicht
garantiert werden können.
"""

__version__ = "1.0"

from datetime import date, datetime, timedelta, timezone


def day_interval(day: date) -> tuple[datetime, datetime]:
    """[day 00:00 UTC, next_day 00:00 UTC)"""
    from_dt = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    return from_dt, from_dt + timedelta(days=1)


def week_interval(year: int, week: int) -> tuple[datetime, datetime]:
    """ISO-Woche: Montag 00:00 UTC bis Montag+7 00:00 UTC (halboffenes Intervall)."""
    monday = date.fromisocalendar(year, week, 1)
    from_dt = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
    return from_dt, from_dt + timedelta(weeks=1)


def month_interval(year: int, month: int) -> tuple[datetime, datetime]:
    """Erster bis (exklusiv) erster des Folgemonats, UTC."""
    from_dt = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        to_dt = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        to_dt = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    return from_dt, to_dt
