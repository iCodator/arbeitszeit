import sqlite3
from pathlib import Path


def open_connection(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    # WAL reduziert Write-Lock-Konflikte zwischen parallel aktiven Verbindungen
    # (z. B. audit_conn vs. Haupt-Transaktion in SQLiteUnitOfWork).
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    # Bei Lock-Konflikt bis zu 5s warten statt sofort "database is locked" zu werfen.
    # Für Einzel-User-Betrieb ausreichend; verhindert stillen Audit-Log-Ausfall.
    conn.execute("PRAGMA busy_timeout=5000")
    return conn
