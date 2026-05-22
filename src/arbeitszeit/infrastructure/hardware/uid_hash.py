import hashlib


def hash_uid(raw_uid: str) -> str:
    """SHA-256-Hash des rohen RFID-UIDs (Hex-String oder Dezimalfolge vom Leser)."""
    return hashlib.sha256(raw_uid.encode()).hexdigest()
