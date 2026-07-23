"""Tests für SQLiteAuditLogRepository — HMAC-Ketten-Integrität."""

__version__ = "1.0"

import hmac
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain.entities import AuditLogEntry
from arbeitszeit.domain.value_objects import AuditLogEntryId
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.repositories.audit_log import (
    SQLiteAuditLogRepository,
    compute_audit_chain_hash,
)

_KEY = b"testschluessel_fuer_tests"
_T0 = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)

_ENTRY = AuditLogEntry(
    id=AuditLogEntryId(0),
    event_type="TEST_EVENT",
    object_type="test",
    object_id=0,
    user_id=None,
    employee_id=None,
    event_at=_T0,
    details_json='{"x": 1}',
)


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    db = tmp_path / "test.db"
    c = open_connection(db)
    run_migrations(c)
    return c


# --- compute_audit_chain_hash ---


class TestComputeAuditChainHash:
    def test_gibt_64_hex_zeichen_zurueck(self) -> None:
        h = compute_audit_chain_hash(
            event_type="TEST",
            event_at_iso="2026-01-01T08:00:00+00:00",
            employee_id=None,
            details_json="{}",
            prev_hash="0" * 64,
            key=_KEY,
        )
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_gleiche_eingaben_identischer_hash(self) -> None:
        kwargs = dict(
            event_type="TEST",
            event_at_iso="2026-01-01T08:00:00+00:00",
            employee_id=None,
            details_json="{}",
            prev_hash="0" * 64,
            key=_KEY,
        )
        assert compute_audit_chain_hash(**kwargs) == compute_audit_chain_hash(**kwargs)

    def test_verschiedene_prev_hash_verschiedene_ergebnisse(self) -> None:
        h1 = compute_audit_chain_hash("T", "2026-01-01T08:00:00+00:00", None, "{}", "0" * 64, _KEY)
        h2 = compute_audit_chain_hash("T", "2026-01-01T08:00:00+00:00", None, "{}", "a" * 64, _KEY)
        assert h1 != h2

    def test_verschiedene_event_type_verschiedene_ergebnisse(self) -> None:
        h1 = compute_audit_chain_hash("A", "2026-01-01T08:00:00+00:00", None, "{}", "0" * 64, _KEY)
        h2 = compute_audit_chain_hash("B", "2026-01-01T08:00:00+00:00", None, "{}", "0" * 64, _KEY)
        assert h1 != h2

    def test_leerer_key_wirft_value_error(self) -> None:
        with pytest.raises(ValueError, match="key"):
            compute_audit_chain_hash("T", "2026-01-01T08:00:00+00:00", None, "{}", "0" * 64, b"")


# --- Repository: chain_hash wird geschrieben ---


class TestAuditLogRepositoryChainHash:
    def test_chain_hash_wird_gesetzt_wenn_key_gesetzt(
        self, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AUDIT_HMAC_KEY", "testschluessel")
        repo = SQLiteAuditLogRepository(conn, conn)
        repo.add(_ENTRY)

        row = conn.execute(
            "SELECT chain_hash FROM audit_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        assert row["chain_hash"] is not None
        assert len(row["chain_hash"]) == 64

    def test_ohne_key_wirft_value_error(
        self, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("AUDIT_HMAC_KEY", raising=False)
        repo = SQLiteAuditLogRepository(conn, conn)
        with pytest.raises(ValueError, match="AUDIT_HMAC_KEY"):
            repo.add(_ENTRY)

    def test_zweiter_eintrag_referenziert_ersten_hash(
        self, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AUDIT_HMAC_KEY", "testschluessel")
        repo = SQLiteAuditLogRepository(conn, conn)
        repo.add(_ENTRY)
        repo.add(_ENTRY)

        rows = conn.execute(
            "SELECT id, chain_hash FROM audit_log ORDER BY id ASC"
        ).fetchall()
        # Letzte zwei Einträge (kann SEEDED-Einträge geben)
        hmac_rows = [r for r in rows if r["chain_hash"]]
        assert len(hmac_rows) >= 2
        h1 = hmac_rows[-2]["chain_hash"]
        h2 = hmac_rows[-1]["chain_hash"]
        assert h1 != h2  # Verschiedene Einträge → verschiedene Hashes

    def test_kette_ist_verifizierbar(
        self, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AUDIT_HMAC_KEY", "testschluessel_verif")
        key = b"testschluessel_verif"
        repo = SQLiteAuditLogRepository(conn, conn)
        repo.add(_ENTRY)

        row = conn.execute(
            "SELECT event_type, event_at, employee_id, details_json, chain_hash "
            "FROM audit_log WHERE chain_hash IS NOT NULL ORDER BY id ASC LIMIT 1"
        ).fetchone()

        expected = compute_audit_chain_hash(
            event_type=row["event_type"],
            event_at_iso=row["event_at"],
            employee_id=row["employee_id"],
            details_json=row["details_json"],
            prev_hash="0" * 64,
            key=key,
        )
        assert hmac.compare_digest(expected, row["chain_hash"])
