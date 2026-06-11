"""Integrationstests für admin_cli users-Befehle."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.presentation.admin_cli import user_accounts
from arbeitszeit.presentation.admin_cli.main import run as cli_run


def _make_db(tmp_path: Path) -> Path:
    db = tmp_path / "arbeitszeit.db"
    conn = open_connection(db)
    run_migrations(conn)
    conn.close()
    return db


def _seed_admin(db: Path) -> int:
    """Legt einen Bootstrap-Admin direkt in die DB ein und gibt seine ID zurück."""
    conn = open_connection(db)
    row = conn.execute(
        "INSERT INTO user_accounts "
        "(username, password_hash, role, employee_id, active, created_at, updated_at) "
        "VALUES ('bootstrap_admin', 'x', 'ADMIN', NULL, 1, '2026-01-01', '2026-01-01') "
        "RETURNING id"
    ).fetchone()
    conn.close()
    return row["id"]


def _count_user_accounts(db: Path) -> int:
    conn = open_connection(db)
    n = conn.execute("SELECT COUNT(*) FROM user_accounts").fetchone()[0]
    conn.close()
    return n


def _get_user(db: Path, username: str) -> dict | None:
    conn = open_connection(db)
    row = conn.execute(
        "SELECT id, username, role, active FROM user_accounts WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# --- users add ---


def test_users_add_admin_legt_konto_an(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "neuer_admin", "--role", "ADMIN",
        "--password", "geheim123",
    ])
    user = _get_user(db, "neuer_admin")
    assert user is not None
    assert user["role"] == "ADMIN"
    assert user["active"] == 1


def test_users_add_reviewer(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "pruef1", "--role", "REVIEWER",
        "--password", "geheim",
    ])
    user = _get_user(db, "pruef1")
    assert user is not None
    assert user["role"] == "REVIEWER"


def test_users_add_tech(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "tech1", "--role", "TECH",
        "--password", "geheim",
    ])
    assert _get_user(db, "tech1")["role"] == "TECH"


def test_users_add_passwort_wird_gehasht(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "hash_test", "--role", "ADMIN",
        "--password", "klartext123",
    ])
    conn = open_connection(db)
    row = conn.execute(
        "SELECT password_hash FROM user_accounts WHERE username = 'hash_test'"
    ).fetchone()
    conn.close()
    assert row["password_hash"] != "klartext123"
    assert ":" in row["password_hash"]  # salt:hash Format


def test_users_add_doppelter_username_schlaegt_fehl(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "doppelt", "--role", "ADMIN",
        "--password", "pw",
    ])
    with pytest.raises(SystemExit):
        cli_run([
            "--db", str(db), "--user-id", str(admin_id),
            "users", "add", "--username", "doppelt", "--role", "REVIEWER",
            "--password", "pw",
        ])


def test_users_add_employee_rolle_nicht_erlaubt(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    with pytest.raises(SystemExit):
        cli_run([
            "--db", str(db), "--user-id", str(admin_id),
            "users", "add", "--username", "emp1", "--role", "EMPLOYEE",
            "--password", "pw",
        ])


def test_users_add_erstellt_audit_log_eintrag(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "audit_test", "--role", "ADMIN",
        "--password", "pw",
    ])
    conn = open_connection(db)
    row = conn.execute(
        "SELECT event_type, details_json FROM audit_log "
        "WHERE event_type = 'USER_ACCOUNT_CREATED'"
    ).fetchone()
    conn.close()
    assert row is not None
    details = json.loads(row["details_json"])
    assert details["username"] == "audit_test"
    assert details["role"] == "ADMIN"


def test_users_add_nicht_admin_wird_abgewiesen(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    # Reviewer anlegen
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "reviewer1", "--role", "REVIEWER",
        "--password", "pw",
    ])
    reviewer = _get_user(db, "reviewer1")
    with pytest.raises(SystemExit):
        cli_run([
            "--db", str(db), "--user-id", str(reviewer["id"]),
            "users", "add", "--username", "neues_konto", "--role", "ADMIN",
            "--password", "pw",
        ])


# --- users deactivate ---


def test_users_deactivate_setzt_active_auf_0(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "zum_deaktivieren", "--role", "TECH",
        "--password", "pw",
    ])
    user = _get_user(db, "zum_deaktivieren")
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "deactivate", "--user-id", str(user["id"]),
    ])
    assert _get_user(db, "zum_deaktivieren")["active"] == 0


def test_users_deactivate_erstellt_audit_log_eintrag(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "deact_audit", "--role", "REVIEWER",
        "--password", "pw",
    ])
    user = _get_user(db, "deact_audit")
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "deactivate", "--user-id", str(user["id"]),
    ])
    conn = open_connection(db)
    row = conn.execute(
        "SELECT event_type FROM audit_log WHERE event_type = 'USER_ACCOUNT_DEACTIVATED'"
    ).fetchone()
    conn.close()
    assert row is not None


# --- users reactivate ---


def test_users_reactivate_setzt_active_auf_1(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "reaktiv_test", "--role", "REVIEWER", "--password", "pw",
    ])
    user = _get_user(db, "reaktiv_test")
    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "deactivate", "--user-id", str(user["id"])])
    assert _get_user(db, "reaktiv_test")["active"] == 0

    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "reactivate", "--user-id", str(user["id"])])
    assert _get_user(db, "reaktiv_test")["active"] == 1


def test_users_reactivate_bereits_aktiv_kein_fehler(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run([
        "--db", str(db), "--user-id", str(admin_id),
        "users", "add", "--username", "schon_aktiv", "--role", "TECH", "--password", "pw",
    ])
    user = _get_user(db, "schon_aktiv")
    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "reactivate", "--user-id", str(user["id"])])  # bereits aktiv → kein Fehler
    assert _get_user(db, "schon_aktiv")["active"] == 1


def test_users_reactivate_erstellt_audit_log_eintrag(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "add", "--username", "audit_react", "--role", "REVIEWER", "--password", "pw"])
    user = _get_user(db, "audit_react")
    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "deactivate", "--user-id", str(user["id"])])
    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "reactivate", "--user-id", str(user["id"])])
    conn = open_connection(db)
    row = conn.execute(
        "SELECT event_type FROM audit_log WHERE event_type = 'USER_ACCOUNT_REACTIVATED'"
    ).fetchone()
    conn.close()
    assert row is not None


# --- users change-role ---


def test_users_change_role_aendert_rolle(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "add", "--username", "rolle_test", "--role", "REVIEWER", "--password", "pw"])
    user = _get_user(db, "rolle_test")
    assert user["role"] == "REVIEWER"

    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "change-role", "--user-id", str(user["id"]), "--role", "TECH"])
    assert _get_user(db, "rolle_test")["role"] == "TECH"


def test_users_change_role_ungueltige_rolle_schlaegt_fehl(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    with pytest.raises(SystemExit):
        cli_run(["--db", str(db), "--user-id", str(admin_id),
                 "users", "change-role", "--user-id", str(admin_id), "--role", "EMPLOYEE"])


def test_users_change_role_erstellt_audit_log_eintrag(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "add", "--username", "audit_role", "--role", "REVIEWER", "--password", "pw"])
    user = _get_user(db, "audit_role")
    cli_run(["--db", str(db), "--user-id", str(admin_id),
             "users", "change-role", "--user-id", str(user["id"]), "--role", "TECH"])
    conn = open_connection(db)
    row = conn.execute(
        "SELECT event_type, details_json FROM audit_log WHERE event_type = 'USER_ACCOUNT_ROLE_CHANGED'"
    ).fetchone()
    conn.close()
    assert row is not None
    details = json.loads(row["details_json"])
    assert details["old_role"] == "REVIEWER"
    assert details["new_role"] == "TECH"


# --- users bootstrap ---


def test_users_bootstrap_legt_ersten_admin_an(tmp_path):
    db = _make_db(tmp_path)
    cli_run(["--db", str(db),
             "users", "bootstrap", "--username", "erster_admin", "--password", "geheim"])
    user = _get_user(db, "erster_admin")
    assert user is not None
    assert user["role"] == "ADMIN"
    assert user["active"] == 1


def test_users_bootstrap_schlaegt_fehl_wenn_admin_existiert(tmp_path):
    db = _make_db(tmp_path)
    admin_id = _seed_admin(db)
    with pytest.raises(SystemExit):
        cli_run(["--db", str(db),
                 "users", "bootstrap", "--username", "zweiter_admin", "--password", "pw"])
