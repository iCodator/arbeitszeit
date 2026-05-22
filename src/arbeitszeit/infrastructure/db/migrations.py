import sqlite3
from pathlib import Path

_MIGRATIONS_DIR = Path(__file__).resolve().parents[4] / "migrations"


def _applied_versions(conn: sqlite3.Connection) -> set[str]:
    try:
        rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    except sqlite3.OperationalError:
        return set()
    return {str(row["version"]) for row in rows}


def run_migrations(
    conn: sqlite3.Connection,
    migrations_dir: Path | None = None,
) -> list[str]:
    if migrations_dir is None:
        migrations_dir = _MIGRATIONS_DIR
    executed: list[str] = []
    applied = _applied_versions(conn)

    for path in sorted(migrations_dir.glob("[0-9][0-9][0-9][0-9]_*.sql")):
        version = path.name.split("_", maxsplit=1)[0]
        if version in applied:
            continue

        if not (version.isdigit() and len(version) == 4):
            raise ValueError(f"Ungültiger Migrationsname: {path.name!r}")

        sql = path.read_text(encoding="utf-8")
        try:
            conn.executescript(f"BEGIN;\n{sql}\nCOMMIT;")
        except Exception:
            conn.rollback()
            raise

        conn.execute(
            "INSERT INTO schema_migrations (version, applied_at) "
            "VALUES (?, datetime('now'))",
            (version,),
        )

        executed.append(version)
        applied.add(version)

    return executed
