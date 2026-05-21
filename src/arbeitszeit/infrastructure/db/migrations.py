import sqlite3
from pathlib import Path

_MIGRATIONS_DIR = Path(__file__).parents[4] / "migrations"

_ALL_MIGRATIONS = [
    "0001_schema.sql",
    "0002_seed_defaults.sql",
]


def _applied_versions(conn: sqlite3.Connection) -> set[str]:
    try:
        rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
        return {row[0] for row in rows}
    except sqlite3.OperationalError:
        return set()


def run_migrations(conn: sqlite3.Connection) -> list[str]:
    applied = _applied_versions(conn)
    executed: list[str] = []

    for filename in _ALL_MIGRATIONS:
        version = filename.split("_", maxsplit=1)[0]
        if version in applied:
            continue

        sql = (_MIGRATIONS_DIR / filename).read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations (version, applied_at) VALUES (?, datetime('now'))",
            (version,),
        )
        conn.commit()
        executed.append(version)

    return executed
