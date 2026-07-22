__version__ = "1.1"

import hmac
import os


def hash_uid(raw_uid: str) -> str:
    """HMAC-SHA256-Hash des rohen RFID-UIDs mit Pepper aus RFID_PEPPER-Umgebungsvariable."""
    pepper = os.environ.get("RFID_PEPPER")
    if not pepper:
        raise ValueError("Umgebungsvariable RFID_PEPPER ist nicht gesetzt.")
    return hmac.new(pepper.encode(), raw_uid.encode(), "sha256").hexdigest()
