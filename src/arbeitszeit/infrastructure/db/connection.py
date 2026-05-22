import sqlite3
from pathlib import Path


def open_connection(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
