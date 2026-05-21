#!/usr/bin/env python3
"""CLI-Einstieg für Datenbankinitialisierung. Delegiert alles an migrations.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations


def main() -> None:
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("arbeitszeit.db")
    conn = open_connection(db_path)
    try:
        executed = run_migrations(conn)
    finally:
        conn.close()

    if executed:
        for version in executed:
            print(f"Migration {version} angewendet.")
    else:
        print("Keine neuen Migrationen.")


if __name__ == "__main__":
    main()
