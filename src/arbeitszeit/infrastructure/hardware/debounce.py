"""Anti-Doppel-Scan-Schutz für RFID-Reader.

DebouncedHardwareReader wraps jeden HardwareReader und verwirft Scans derselben
Karte, die innerhalb von DEBOUNCE_SECONDS aufeinanderfolgen.

Fachliche Einordnung:
  DEBOUNCE_SECONDS ist kein ArbZG-Zeitlimit und hat keinen Einfluss auf die
  Tageslogik (Kurztag/Langtag, Buchungssequenz, Compliance-Prüfungen).
  Der Mechanismus dient ausschließlich dazu, technisches Rauschen durch
  mehrfaches kurzes Auflegen derselben Karte am RFID-Reader abzufangen.
  Verschiedene Karten können beliebig schnell nacheinander gescannt werden.
"""

__version__ = "1.0"

import logging
import time

from .ports import HardwareReader, RawBookingRequest

# Entprellungsfenster in Sekunden. Zwei Scans derselben Karte innerhalb
# dieses Abstands gelten als Doppel-Scan (technisches Rauschen).
DEBOUNCE_SECONDS: float = 3.0

_logger = logging.getLogger(__name__)


class DebouncedHardwareReader(HardwareReader):
    """Entprellt RFID-Scans: Doppel-Scans derselben Karte < DEBOUNCE_SECONDS werden verworfen.

    Wraps jeden beliebigen HardwareReader transparent. Die fachliche Buchungslogik
    sieht ausschließlich bereinigte Events. Verschiedene Karten können beliebig
    schnell nacheinander gelesen werden; die Sperre gilt nur pro uid_hash.
    """

    def __init__(self, reader: HardwareReader) -> None:
        self._reader = reader
        self._last_accepted: dict[str, float] = {}

    def read_next(self) -> RawBookingRequest:
        """Gibt den nächsten nicht-redundanten RFID-Scan zurück.

        Doppel-Scans (gleiche Karte, Abstand < DEBOUNCE_SECONDS) werden verworfen
        und als INFO geloggt; der Aufruf wartet dann auf den nächsten Event.
        """
        while True:
            request = self._reader.read_next()
            now = time.monotonic()
            last = self._last_accepted.get(request.uid_hash)
            if last is not None and (now - last) < DEBOUNCE_SECONDS:
                _logger.info(
                    "Doppel-Scan verworfen (Δt=%.2f s < %.1f s): uid_hash=%s…",
                    now - last,
                    DEBOUNCE_SECONDS,
                    request.uid_hash[:8],
                )
                continue
            self._last_accepted[request.uid_hash] = now
            return request

    def close(self) -> None:
        self._reader.close()
