Phase 1 – Grundgerüst (abgeschlossen)
======================================

Historischer Lieferumfang Phase 1 (originaler Abschlussstand)
--------------------------------------------------------------

Originär zu Phase 1 gehörten ausschließlich:

- migrations/0001_schema.sql — vollständiges Datenbankschema (15 fachliche Tabellen + schema_migrations = 16)
- migrations/0002_seed_defaults.sql — Regelarbeitszeiten und System-Config-Defaults
- infrastructure/db/connection.py — SQLite-Verbindungsfunktion mit PRAGMAs
- infrastructure/db/migrations.py — Migrationsrunner (executescript, Idempotenz)
- scripts/init_db.py — Initialisierungsskript
- tests/test_migrations.py — ursprünglich 6 Testfälle (Tests 1–5 + 10, s. u.)

Migrationen 0003–0006 und die zugehörigen Testfälle 6–9, 11, 12 wurden in
Phase 4 (Schritte 4/2, 4/5) und Phase 5 (Schritt 1) nachgereicht. Sie bauen
auf demselben Fundament auf und laufen heute im selben Testmodul mit.

Heutiger Endstand der Migrationskette: Migrationen 0001–0006, 12 Tests.


Ziel
----
Lauffähiges Projektgerüst mit Migrationssystem und erster Datenbankkonsistenzprüfung.
Keine Domänenlogik, keine Anwendungsfälle – nur das Fundament.


Dateien und Entscheidungen
--------------------------

pyproject.toml

  - requires-python = ">=3.11,<3.13"
  - src-Layout: Paket liegt unter src/arbeitszeit/
  - Runtime-Abhängigkeiten: evdev>=1.7, reportlab>=4.0
  - Dev-Dependencies: pytest>=8.0, pytest-cov>=5.0, pypdf>=4.0, ruff>=0.6
    (pypdf in Phase 4/8c für PDF-Inhaltstests ergänzt)
  - pytest: testpaths = ["tests"]

.python-version
  - Pinnt auf 3.14 für lokale Entwicklung

.gitignore
  - Schließt .venv/, __pycache__/, *.db, *.db-shm, *.db-wal aus
  - .pytest_cache/, .ruff_cache/, .mypy_cache/, dist/, build/
  - docs/informelles/ ist NICHT ausgeschlossen – Planungsdokumente werden versioniert

Verzeichnisstruktur
  - src/arbeitszeit/           Paketroot
  - src/arbeitszeit/domain/    Phase 2
  - src/arbeitszeit/application/  Phase 3
  - src/arbeitszeit/infrastructure/  Phase 4
  - migrations/                SQL-Migrationsdateien
  - scripts/                   Initialisierungs- und Hilfsskripte
  - tests/                     Testwurzel


migrations/0001_schema.sql
  16 Tabellen (vollständiges DDL, inkl. schema_migrations):

  schema_migrations  (version TEXT PK, applied_at TEXT)
    — kein id-Feld; version ist der Primary Key

  Person-Ebene:
    employees         (id, personnel_no, first_name, last_name,
                       active INTEGER CHECK 0/1,
                       employment_start, employment_end, created_at, updated_at)
                       CHECK: employment_end >= employment_start (wenn beide nicht NULL)
    user_accounts     (id, username, password_hash,
                       role TEXT CHECK ('EMPLOYEE','ADMIN','REVIEWER','TECH'),
                       employee_id FK nullable, active INTEGER, created_at, updated_at)
    rfid_cards        (id, uid_hash UNIQUE, employee_id FK, status CHECK, valid_from,
                       valid_until, replaced_by_card_id FK self-ref nullable, created_at)
                       CHECK: valid_until >= valid_from (wenn nicht NULL)

  Erfassungs-Ebene:
    terminals         (id, terminal_code UNIQUE, hostname, location_text,
                       active INTEGER CHECK 0/1, created_at)
    device_events     (id, event_type CHECK, terminal_id FK nullable,
                       rfid_uid_hash, payload_json, occurred_at,
                       related_time_booking_id FK nullable)
                       event_type: NUMPAD_INPUT, RFID_SCAN, UNKNOWN_CARD,
                                   INACTIVE_CARD, CARD_ASSIGNMENT_FAILURE,
                                   BOOKING_ACCEPTED, BOOKING_REJECTED
    time_bookings     (id, employee_id FK, rfid_card_id FK nullable,
                       booking_type CHECK ('COME','GO','BREAK_START','BREAK_END'),
                       booked_at, source CHECK ('TERMINAL','MANUAL','IMPORT'),
                       terminal_id FK nullable, current_status CHECK, note, created_at)
                       current_status-Werte: OK, OPEN, WARN, NEEDS_REVIEW, CORRECTED,
                         CLOSED_WITH_NOTE, POSSIBLE_BREAK_VIOLATION,
                         POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION,
                         MANUAL_ENTRY
                       Hinweis: device_event_id wurde NICHT in 0001 angelegt –
                         erst durch Migration 0005 nachgereicht (Phase 4)

  Prüf-Ebene:
    review_cases      (id, employee_id FK, time_booking_id FK nullable,
                       case_type CHECK, status CHECK, severity CHECK,
                       detected_at, description, closed_at, closed_by_user_id FK nullable)
                       case_type: OPEN_WORK_PHASE, OPEN_BREAK_PHASE,
                         OUTSIDE_SCHEDULE_WINDOW, POSSIBLE_BREAK_VIOLATION,
                         POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION,
                         IMPLAUSIBLE_SEQUENCE, UNKNOWN_CARD_ATTEMPT,
                         INACTIVE_CARD_ATTEMPT, TIME_ANOMALY, MANUAL_ENTRY_REVIEW
                       status: OPEN, IN_REVIEW, RESOLVED, CLOSED_WITH_NOTE
                       severity: INFO, WARN, CRITICAL
                       CHECK: status OPEN/IN_REVIEW → closed_at/closed_by NULL;
                              RESOLVED/CLOSED_WITH_NOTE → beide NOT NULL
                       Hinweis: note-Spalte wurde NICHT in 0001 angelegt –
                         erst durch Migration 0004 nachgereicht (Phase 4)
    review_case_actions  (id, review_case_id FK, action_type CHECK,
                          note, performed_by_user_id FK, created_at)
                          action_type: CREATED, COMMENT_ADDED, STATUS_CHANGED,
                            CORRECTION_LINKED, SUPPLEMENT_LINKED, CLOSED, REOPENED
    booking_status_history  (id, time_booking_id FK, old_status, new_status CHECK,
                              reason, changed_by_user_id FK nullable, changed_at)

  Änderungs-Ebene:
    booking_corrections  (id, time_booking_id FK, old_values_json TEXT,
                          new_values_json TEXT, reason, corrected_by_user_id FK,
                          corrected_at)
                          Alter und neuer Zustand als JSON-Dokument gespeichert,
                          nicht als separate Felder
    supplements          (id, employee_id FK, related_time_booking_id FK nullable,
                          booking_type CHECK, event_at, recorded_at, reason,
                          recorded_by_user_id FK, approval_status CHECK,
                          approved_by_user_id FK nullable, approved_at)
                          approval_status: PENDING, APPROVED, REJECTED
                          CHECK: PENDING → approved_by/at NULL;
                                 APPROVED/REJECTED → beide NOT NULL
                          Hinweis: rejected_by_user_id, rejected_at wurden NICHT in
                            0001 angelegt – erst durch Migration 0004 (Phase 4)
    work_schedule_versions  (id, scope_type CHECK ('GLOBAL','EMPLOYEE'),
                             scope_employee_id FK nullable, weekday INTEGER 1–7,
                             start_time, end_time, valid_from, valid_until,
                             change_origin CHECK, changed_by_user_id FK nullable,
                             changed_at, reason)
                             CHECK: GLOBAL → scope_employee_id NULL;
                                    EMPLOYEE → NOT NULL
                             CHECK: valid_until >= valid_from (wenn nicht NULL)
                             change_origin: SYSTEM_SEED, ADMIN_UI, MIGRATION

  Nachweis-Ebene:
    audit_log         (id, event_type, object_type, object_id,
                       user_id FK nullable, employee_id FK nullable,
                       event_at, details_json NOT NULL)
    system_events     (id, event_type CHECK, source, severity CHECK ('INFO','WARN','ERROR'),
                       event_at, details_json, related_object_type, related_object_id)
                       event_type: SELFTEST_OK, SELFTEST_FAIL, DB_BACKUP_CREATED,
                         DB_BACKUP_FAILED, RESTORE_STARTED, RESTORE_FINISHED,
                         RESTORE_FAILED, NAS_REACHABLE, NAS_UNREACHABLE,
                         TIME_JUMP_DETECTED, MANUAL_TIME_CHANGE_DETECTED,
                         DEVICE_UNAVAILABLE, DEVICE_RECOVERED,
                         APPLICATION_START, APPLICATION_STOP
    system_config     (id, config_key, config_value_json, version INTEGER,
                       change_origin CHECK, changed_by_user_id FK nullable,
                       changed_at, reason)
                       UNIQUE (config_key, version) — Versionierung statt UPDATE

  Indizes (11):
    idx_user_accounts_employee_id
    idx_rfid_cards_employee_status
    idx_time_bookings_employee_booked_at
    idx_time_bookings_status_booked_at
    idx_booking_status_history_booking_changed_at
    idx_booking_corrections_booking_corrected_at
    idx_supplements_employee_event_at
    idx_supplements_approval_status
    idx_review_cases_status_detected_at
    idx_review_cases_employee_detected_at
    idx_review_case_actions_case_created_at
    idx_system_config_key_version
    idx_device_events_occurred_at
    idx_system_events_event_at

  Entscheidungen:
  - Komplexe Geschäftsregeln NICHT in SQLite (keine Trigger, keine komplexen
    CHECK-Constraints für fachliche Invarianten) – gehören in Python-Domänenlogik
  - work_schedule_versions + system_config: change_origin (SYSTEM_SEED/ADMIN_UI/MIGRATION)
    – KEIN Bootstrap-User, kein künstlicher Dummy-Account
  - FK-Constraints aktiv: PRAGMA foreign_keys = ON
  - system_config: INSERT statt UPDATE (Versionierung über version-Spalte)


migrations/0002_seed_defaults.sql
  work_schedule_versions – 5 globale Einträge (Mo–Fr):
    Mo (1): 07:30–18:00    Do (4): 07:30–14:00
    Di (2): 07:30–18:00    Fr (5): 07:30–16:00
    Mi (3): 07:30–18:00
    valid_from = '2026-01-01', valid_until = NULL
    change_origin = 'SYSTEM_SEED', changed_by_user_id = NULL

  system_config – 4 Defaults:
    app.timezone                              = "Europe/Berlin"
    booking.grace_seconds_after_numpad_select = 30
    backup.nas_enabled                        = false
    backup.nas_path                           = null

  audit_log – automatisch befüllt:
    Je ein SEEDED-Eintrag für jede work_schedule_versions-Zeile (5)
    Je ein SEEDED-Eintrag für jede system_config-Zeile (4)
    → insgesamt 9 Audit-Einträge nach 0002

Spätere Nachträge auf Basis desselben Fundaments
  (nicht originär Phase 1; laufen heute in test_migrations.py mit)

  migrations/0003–0005 (Phase 4):

  0003_cleanup_booking_status.sql
    Bereinigt CHECK-Constraint in time_bookings.current_status und
    booking_status_history.new_status: entfernt die transient genutzten
    Status POSSIBLE_*, MANUAL_ENTRY (bleiben als ReviewCaseType, nicht BookingStatus)

  0004_supplement_reject_fields_and_review_note.sql
    supplements: rejected_by_user_id FK, rejected_at ergänzt;
                 CHECK aktualisiert (REJECTED → rejected_by_user_id/at NOT NULL)
    review_cases: note TEXT ergänzt

  0005_time_bookings_device_event_id.sql
    time_bookings: device_event_id INTEGER FK auf device_events(id) ergänzt
    (Table-Rebuild wegen SQLite-Einschränkung bei ALTER TABLE ... ADD CONSTRAINT)

  migration/0006 (Phase 5, Schritt 1/Befund 5/1-06):

  0006_system_events_application_error.sql
    system_events: CHECK-Constraint um APPLICATION_ERROR erweitert
    (Table-Rebuild; APPLICATION_ERROR wird von terminal_ui/main.py für
    unerwartete Laufzeitfehler genutzt)


infrastructure/db/connection.py
  open_connection(db_path: Path) -> sqlite3.Connection:
  - isolation_level=None  → Autocommit-Modus, Transaktionen manuell gesteuert
  - PRAGMA foreign_keys = ON
  - PRAGMA journal_mode=WAL
  - PRAGMA busy_timeout=5000
  - row_factory = sqlite3.Row  → Spaltenzugriff per Name


infrastructure/db/migrations.py
  run_migrations(conn, migrations_dir):

  - Liest alle `NNNN_*.sql`-Dateien (Glob: `[0-9][0-9][0-9][0-9]_*.sql`), sortiert nach Dateiname
  - Prüft schema_migrations: nur noch nicht angewandte Versionen ausführen
  - Versionsvalidierung vor Query-Konstruktion (version.isdigit() + len == 4)
  - Jede Migration via executescript() mit eigenem BEGIN/COMMIT-Block → atomar
  - Exception → rollback(); kein schema_migrations-Eintrag für fehlgeschlagene Version


scripts/init_db.py
  - Öffnet Verbindung via open_connection()
  - Ruft run_migrations() auf
  - Akzeptiert optionales db_path-Argument
  - Gibt Rückmeldung an stdout


tests/test_migrations.py  (12 Tests, alle grün; Gesamtmigrations-Test)

  Originäre Phase-1-Testfälle (6 Tests):
    test_leere_db_wird_vollstaendig_migriert
      Alle Migrationen 0001–0006 laufen durch, keine Exception
      (ursprünglich 0001–0002; mit jeder neuen Migration fortgeschrieben)
    test_erneutes_ausfuehren_ist_idempotent
      Wiederholter run_migrations()-Aufruf ist fehlerfrei
    test_seed_daten_vorhanden_nach_migration
      work_schedule_versions enthält 5 Einträge, system_config enthält 4
    test_audit_log_enthaelt_seed_eintraege
      audit_log enthält genau 9 Einträge (5 + 4 aus 0002)
    test_schema_migrations_enthaelt_genau_die_erwarteten_versionen
      Einträge für 0001–0006 vorhanden, keine unbekannten Versionen
      (ursprünglich 0001–0002; mit jeder neuen Migration fortgeschrieben)
    test_fehlgeschlagene_migration_hinterlaesst_keinen_schema_migrations_eintrag
      Rollback-Verhalten bei fehlerhafter SQL-Datei

  Später hinzugekommen — Phase 4 (Migrationen 0004/0005, 5 Tests):
    test_migration_0004_fuegt_neue_spalten_ein
      rejected_by_user_id, rejected_at in supplements; note in review_cases
    test_migration_0005_fuegt_device_event_id_ein
      device_event_id-Spalte in time_bookings vorhanden
    test_migration_0005_erhaelt_time_bookings_foreign_keys_und_indizes
      FK-Constraints und Indizes nach Table-Rebuild intakt
    test_migration_0005_datensatz_bleibt_erhalten
      Vorhandene Zeilen überleben den Table-Rebuild
    test_wiederholte_ausfuehrung_erzeugt_keine_doppelten_seed_daten
      Idempotenz der Seed-Daten (kein doppeltes INSERT)

  Später hinzugekommen — Phase 5 (Migration 0006, 1 Test):
    test_migration_0006_application_error_event_type_verfuegbar
      APPLICATION_ERROR ist als event_type in system_events eintragbar


Testverteilung Phase 1
----------------------
tests/test_migrations.py  – 12 Tests gesamt (ursprünglich 6; Phase 4 fügte 5 hinzu,
                             Phase 5 fügte 1 hinzu für Migration 0006)


V4-Bezüge
---------

Aufbewahrungsprinzip (Pflichtenheft v4 §12 / Regelwerk v4 §18):
  Keine physische Löschung fachlicher Buchungen. Klärung über Status
  (CORRECTED, CLOSED_WITH_NOTE), Korrekturen oder Archivierung.
  Aufbewahrungsfrist mindestens 2 Jahre (ArbZG §16 Abs. 2).

system_events-Tabelle (Pflichtenheft v4 §9.3 / Regelwerk v4 §21):
  Vorhanden im Schema. Dient der Protokollierung von Betriebsereignissen –
  u. a. Systemzeitsprünge (TIME_JUMP_DETECTED, MANUAL_TIME_CHANGE_DETECTED)
  und Selbsttests (SELFTEST_OK, SELFTEST_FAIL). Befüllung durch
  Infrastruktur-/Betriebsschicht (Phase 4/Schritt 9).

Rollentrennung (Pflichtenheft v4 §5 / Regelwerk v4 §16):
  UserRole: EMPLOYEE / ADMIN / REVIEWER / TECH – strikt getrennte Rechte.
  Kein Bootstrap-User; change_origin (SYSTEM_SEED / ADMIN_UI / MIGRATION)
  ersetzt administrativen Dummy-Account für Seeds/Migrationen.


---

## V4-Bezüge und organisatorische Auflagen

Verbindliche Referenzdokumente: `docs/pflichtenheft_arbeitszeit_v4.md`,
`docs/regelwerk_arbeitszeit_v4.md`, `docs/anlage_einhaltung_pflichtenheft_v2.md`.

Was diese Phase technisch leistet und was als externe organisatorische Auflagen
(ArbSchG §3, IT-Sicherheitsrichtlinie §75b SGB V, Betriebsdokumentation, revisionsfeste
Testmatrix) außerhalb des Codes verbleibt, ist in `planung_gesamt.md` Abschnitt
„Offene Praxis- und Nachweispflichten" beschrieben.
