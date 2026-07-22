__version__ = "1.0"

from datetime import datetime
from zoneinfo import ZoneInfo

_BERLIN = ZoneInfo("Europe/Berlin")


def to_local(dt: datetime) -> datetime:
    """Konvertiert einen UTC-Zeitstempel in die Berliner Lokalzeit.

    Voraussetzung: *dt* muss timezone-aware sein (UTC empfohlen).
    Rückgabe ist immer in Europe/Berlin — unabhängig vom System-Timezone.
    """
    return dt.astimezone(_BERLIN)
