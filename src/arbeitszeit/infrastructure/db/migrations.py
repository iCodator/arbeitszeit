import sqlite3
from pathlib import Path

_MIGRATIONS_DIR = Path(__file__).resolve().parents[4] / "migrations"


def _migration_files() -> list[Path]:
    return sorted(_MIGRATIONS_DIR.glob("[0-9][0-9][0-9][0-9]_*.sql"))


def _applied_versions(conn: sqlite3.Connection) -> set[str]:
    try:
        rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    except sqlite3.OperationalError:
        return set()
    return {str(row["version"]) for row in rows}


def run_migrations(conn: sqlite3.Connection) -> list[str]:
    executed: list[str] = []
    applied = _applied_versions(conn)

    for path in _migration_files():
        version = path.name.split("_", maxsplit=1)[0]
        if version in applied:
            continue

        sql = path.read_text(encoding="utf-8")
        version_insert = (
            "INSERT INTO schema_migrations (version, applied_at) "
            f"VALUES ('{version}', datetime('now'))"
        )
        script = f"BEGIN;\n{sql}\n{version_insert};\nCOMMIT;"

        try:
            conn.executescript(script)
        except Exception:
            conn.rollback()
            raise

        executed.append(version)
        applied.add(version)

    return executed
