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

        # version.isdigit() + len == 4 stellt sicher, dass der f-String
        # ausschließlich vier Dezimalziffern einbettet – kein Injection-Risiko.
        if not (version.isdigit() and len(version) == 4):
            raise ValueError(f"Ungültiger Migrationsname: {path.name!r}")

        sql = path.read_text(encoding="utf-8")
        # Migration-SQL und Versionsregistrierung in einer einzigen Transaktion,
        # damit "angewendet" und "registriert" untrennbar sind.
        # B608: `version` ist durch isdigit()+len==4 auf "0000"-"9999" beschraenkt
        # (kein SQL-Injektionsvektor moeglich).
        script = (  
            f"BEGIN;\n{sql}\n" # nosec B608
            f"INSERT INTO schema_migrations (version, applied_at)"
            f" VALUES ('{version}', datetime('now'));\n"
            f"COMMIT;"
        )
        try:
            conn.executescript(script)
        except Exception:
            conn.rollback()
            raise

        executed.append(version)
        applied.add(version)

    return executed
