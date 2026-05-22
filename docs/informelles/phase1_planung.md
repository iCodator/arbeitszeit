Phase 1 – Grundgerüst (abgeschlossen)
======================================

Ziel
----
Lauffähiges Projektgerüst mit Migrationssystem und erster Datenbankkonsistenzprüfung.
Keine Domänenlogik, keine Anwendungsfälle – nur das Fundament.


Dateien und Entscheidungen
--------------------------

pyproject.toml
  - requires-python = ">=3.11,<3.13" (nicht 3.12, damit 3.11 und 3.12 abgedeckt)
  - src-Layout: Paket liegt unter src/arbeitszeit/
  - Abhängigkeiten: nur pytest, pytest-cov und ruff als dev-Deps
  - pytest: testpaths = ["tests"], pythonpath = ["src"]

.python-version
  - Pinnt auf 3.12 für lokale Entwicklung

.gitignore
  - Schließt .venv/, __pycache__/, *.db, *.db-journal aus
  - docs/informelles/ ist explizit ausgeschlossen (Planungsdokumente, kein Code)

Verzeichnisstruktur
  - src/arbeitszeit/           Paketroot
  - src/arbeitszeit/domain/    Phase 2
  - src/arbeitszeit/application/  Phase 3
  - src/arbeitszeit/infrastructure/  Phase 4
  - migrations/                SQL-Migrationsdateien
  - scripts/                   Initialisierungs- und Hilfsskripte
  - tests/                     Testwurzel


migrations/0001_schema.sql
  15 Tabellen (vollständiges DDL):

  Person-Ebene:
    employees         (id, personnel_no, first_name, last_name, is_active)
    user_accounts     (id, username, password_hash, role, employee_id FK nullable)
    rfid_cards        (id, uid_hash, employee_id FK, status, valid_from, valid_until,
                       replaced_by_card_id FK self-ref nullable)

  Erfassungs-Ebene:
    terminals         (id, name, location, is_active)
    device_events     (id, terminal_id FK, uid_hash, booking_type, event_at, raw_payload)
    time_bookings     (id, employee_id FK, booking_type, booked_at, source,
                       current_status, terminal_id FK nullable, rfid_card_id FK nullable,
                       device_event_id FK nullable, note)

  Prüf-Ebene:
    review_cases      (id, employee_id FK, case_type, severity, status, description,
                       booking_id FK nullable, note, created_at, closed_at,
                       closed_by_user_id FK nullable)
    review_case_actions  (id, case_id FK, user_id FK, action_type, note, acted_at)
    booking_status_history  (id, booking_id FK, old_status, new_status, reason,
                             changed_by_user_id FK nullable, changed_at)

  Änderungs-Ebene:
    booking_corrections  (id, original_booking_id FK, corrected_by_user_id FK,
                          reason, old_booking_type, old_booked_at,
                          new_booking_type, new_booked_at, created_at)
    supplements          (id, employee_id FK, related_booking_id FK nullable,
                          booking_type, event_at, recorded_at, reason,
                          recorded_by_user_id FK, approval_status,
                          approved_by_user_id FK nullable, approved_at,
                          rejected_by_user_id FK nullable, rejected_at)
    work_schedule_versions  (id, scope_type, scope_employee_id FK nullable,
                             weekday, start_time, end_time, valid_from, valid_until,
                             change_origin, changed_by_user_id FK nullable, reason)

  Nachweis-Ebene:
    audit_log         (id, event_type, object_type, object_id, user_id FK nullable,
                       employee_id FK nullable, event_at, details_json)
    system_events     (id, event_type, details_json, occurred_at)
    system_config     (id, config_key, value_json, change_origin,
                       changed_by_user_id FK nullable, changed_at, reason)
    schema_migrations (id, version, applied_at)

  Entscheidungen:
  - Komplexe Geschäftsregeln NICHT in SQLite (keine Trigger, keine komplexen
    CHECK-Constraints für fachliche Invarianten) – gehören in Python-Domänenlogik
  - work_schedule_versions + system_config: Feld change_origin (SYSTEM_SEED /
    ADMIN_UI / MIGRATION) – KEIN Bootstrap-User, kein künstlicher Dummy-Account
  - FK-Constraints sind eingeschaltet (PRAGMA foreign_keys = ON)


migrations/0002_seed_defaults.sql
  - Legt 5 globale Regelarbeitszeitversionen an (Mo–Fr, 07:30–16:00)
    mit change_origin = 'SYSTEM_SEED', valid_from = '2000-01-01'
  - Legt System-Config-Defaults an (max_daily_hours, min_break_minutes etc.)


infrastructure/db/connection.py
  open_connection(db_path: Path) -> sqlite3.Connection:
  - isolation_level=None  → SQLite im Autocommit-Modus, Transaktionen manuell
    per BEGIN/COMMIT/ROLLBACK gesteuert (keine implizite Transaktion durch Python)
  - PRAGMA foreign_keys = ON  → FK-Prüfung aktiv
  - row_factory = sqlite3.Row  → Spaltenzugriff per Name


infrastructure/db/migrations.py
  run_migrations(conn, migrations_dir):
  - Liest alle *.sql-Dateien aus migrations_dir, sortiert nach Dateiname
  - Prüft schema_migrations-Tabelle: nur noch nicht angewandte Versionen ausführen
  - Versionsvalidierung vor f-String-Interpolation (Eingabewert prüfen, bevor
    er in eine Query eingebaut wird – Vorsichtsmaßnahme gegen Injection)
  - Jede Migration läuft via executescript() mit eigenem BEGIN/COMMIT-Block
    → atomar pro Datei; teils ausgeführte Migrationen hinterlassen keinen
    Halbzustand


scripts/init_db.py
  - Öffnet Verbindung via open_connection()
  - Ruft run_migrations() auf
  - Gibt Rückmeldung an stdout


tests/test_migrations.py  (6 Tests, alle grün)
  Testfälle:
  1. Frische DB: alle Migrationen laufen durch, keine Exception
  2. Wiederholter Aufruf ist idempotent (keine Fehler bei Doppelaufruf)
  3. schema_migrations enthält die erwarteten Versionsnummern
  4. employees-Tabelle existiert (Schema-Smoke-Test)
  5. work_schedule_versions enthält 5 Seed-Einträge (Mo–Fr)
  6. FK-Constraint greift: INSERT mit ungültigem employee_id schlägt fehl


Testverteilung Phase 1
----------------------
tests/test_migrations.py  – 6 Tests (Migrationsrunner + Schema-Smoke)


V3-Bezüge
---------

Aufbewahrungsprinzip (Pflichtenheft v3 §12 / Regelwerk v3 §18):
  Keine physische Löschung fachlicher Buchungen. Klärung über Status
  (CORRECTED, CLOSED_WITH_NOTE), Korrekturen oder Archivierung.
  Aufbewahrungsfrist mindestens 2 Jahre (ArbZG §16 Abs. 2).

system_events-Tabelle (Pflichtenheft v3 §9.3 / Regelwerk v3 §21):
  Vorhanden im Schema (Nachweis-Ebene). Dient der Protokollierung von
  Betriebsereignissen – u. a. Systemzeitsprünge und manuelle
  Uhrzeitänderungen. Befüllung durch Infrastruktur-/Betriebsschicht.

Rollentrennung (Pflichtenheft v3 §5 / Regelwerk v3 §16):
  UserRole: EMPLOYEE / ADMIN / REVIEWER / TECH – strikt getrennte Rechte.
  Kein künstlicher Bootstrap-User; change_origin (SYSTEM_SEED / ADMIN_UI /
  MIGRATION) ersetzt administrativen Dummy-Account für Seeds/Migrationen.
