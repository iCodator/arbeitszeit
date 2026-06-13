# Changelog

Alle nennenswerten Änderungen werden in dieser Datei dokumentiert.  
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

---

## [Audit & Dokumentation] – 2026-06-11 bis 2026-06-12

### Hinzugefügt
- `users reactivate`, `users change-role`, `users bootstrap` in der Admin-CLI
- device_events-Produktionspfad: RFID_SCAN-Record (Autocommit) vor `BookUseCase` —
  Audit-Trail bleibt auch bei Buchungsfehler erhalten
- `SQLiteDeviceEventRepository` + `DeviceEventRepository`-Protokoll
- Betriebsdokumentation (`betriebsdokumentation_arbeitszeit_v1.md`, 12 Abschnitte)
- Phasenübergreifende Nachtragsmatrix (44 Artefakte mit Phasenzuordnung und Belegen)
- Revisionsfeste Testmatrix (406 Tests, Pflichtenheft v5 §16-Abdeckung)
- Installationsanleitung v2.0 (Markdown + HTML)
- Handbuch v2.0 (Markdown + HTML)
- Pflichtenheft v5 und Regelwerk v5

### Geändert
- Python-Zielversion auf 3.14 angehoben
- Alle Phasenpläne auf Pflichtenheft v5 / Regelwerk v5 aktualisiert
- `init_db.py` auf `argparse` (`--db`-Flag) umgestellt

### Behoben
- `FakeUnitOfWork` commit-or-rollback-Semantik korrigiert
  (`if not self.committed` statt `if exc_type is not None`)
- `_REQUIRED_CONFIG_KEYS` um `backup.backup_dir` und `export.export_dir` ergänzt
- `ValidationResult` aus `booking_rules.py` entfernt (war toter Code)

---

## [Phase 5: Präsentation] – 2026-05-26 bis 2026-05-27

### Hinzugefügt
- `presentation/terminal_ui/` — Buchungsschleife (RFID + Numpad, `_run_one_cycle()`)
- `presentation/admin_cli/` — vollständige Admin-Kommandozeile
  - Mitarbeiterverwaltung (`employees add/list/deactivate`)
  - Zeitbuchungen, Korrekturen, Nachtragsgenehmigung
  - Exporte (CSV, PDF) mit Zeitraumfilter
  - Benutzerkontenverwaltung (`users add/list/deactivate`)
- `infrastructure/time_monitor.py` — Systemzeitüberwachung
  (`TIME_JUMP_DETECTED` / `MANUAL_TIME_CHANGE_DETECTED`)
- `migrations/0006_system_events_application_error.sql` —
  `APPLICATION_ERROR` als neuer Systemereignistyp
- `scripts/setup.py` — interaktive Erstkonfiguration

### Behoben
- PDF-Intervalle auf halb-offene UTC-Intervalle umgestellt
- CSV-Intervallbildung vereinheitlicht
- `open_bookings` und `open_review_cases` mit `--from`/`--to`-Zeitraumfilter versehen

---

## [Phase 4: Infrastruktur] – 2026-05-22 bis 2026-05-26

### Hinzugefügt
- `SQLiteUnitOfWork` mit commit-or-rollback-Semantik und separater `audit_conn`
- 10 SQLite-Repositories mit Roundtrip-Integrationstests
- `infrastructure/hardware/` — `evdev`-Reader (RFID + Numpad) + `SimulatedHardwareReader`
- `infrastructure/backup/backup_service.py`:
  - Lokales SQLite-Backup (timestamped)
  - NAS-Spiegelung via `rsync --archive --delete`
  - `restore_from(restore_exports=True)` für vollständige Wiederherstellung
- `infrastructure/export/` — `report_queries.py`, `csv_exporter.py`,
  `pdf_report_service.py` (vier Berichtstypen)
- `infrastructure/system_check.py` — Systemcheck (DB, Config, NAS, FK-Konsistenz)
- `scripts/backup.py` — Backup-Skript mit optionalem `--export-dir`
- `migrations/0003_cleanup_booking_status.sql` — `POSSIBLE_*`-Werte aus
  `time_bookings.current_status` entfernt
- `migrations/0004_supplement_reject_fields_and_review_note.sql` —
  Ablehnung formal von Genehmigung getrennt; Notizfeld für Prüffälle
- `migrations/0005_time_bookings_device_event_id.sql` — Schemavorbereitung
  `device_event_id` (operative Nutzung: Phase-5-Nacharbeit)
- Rollenprüfung (ADMIN / REVIEWER / TECH) in allen schreibenden Use Cases
- Ruhezeitprüfung (§5 ArbZG) und Regelzeitfenster-Check in `BookUseCase`
- WAL-Modus, `busy_timeout`, Autocommit-Garantie für `audit_conn` explizit belegt

### Geändert
- Audit-Log rollback-resistent (schreibt über separate Verbindung außerhalb der UoW-Transaktion)
- `BookingStatus` auf 6 orthogonale Werte reduziert; Compliance-Zustand über `ReviewCaseType`

---

## [Phase 3: Application] – 2026-05-22

### Hinzugefügt
- `UnitOfWork`-Protokoll + `FakeUnitOfWork` (In-Memory-Testdouble)
- Commands / Results für alle Use Cases
- `BookUseCase` — COME / GO / BREAK mit Audit-Log und Buchungssequenzprüfung
- `ManageWorkScheduleUseCase` — Regelarbeitszeitverwaltung mit Versionierung
- `RegisterSupplementUseCase` — Nachtragsantrag einreichen
- `CorrectBookingUseCase` — Buchungskorrektur mit selektiver Review-Case-Schließung
- `ApproveSupplementUseCase` / `RejectSupplementUseCase`
  (für Phase 4 geplant, in Phase 3 vorgezogen)
- 109 Application-Tests

---

## [Phase 2: Domäne] – 2026-05-21

### Hinzugefügt
- `domain/enums.py` — 11 StrEnum-Klassen (`BookingType`, `BookingStatus`,
  `UserRole`, `ReviewCaseType` u. a.)
- `domain/entities.py` — 9 frozen `@dataclass` (`Employee`, `TimeBooking`,
  `WorkScheduleVersion`, `UserAccount` u. a.)
- `domain/errors.py` — `DomainError` + 9 Subklassen
- `domain/audit_events.py` — zentraler Ereignistyp-Katalog
- `domain/services/booking_rules.py` — Buchungssequenzprüfung
- `domain/services/compliance_checks.py` — ArbZG-Prüfhilfen §3 / §4 / §5
  (`check_break_compliance`, `check_max_hours`, `check_rest_period`)
- `domain/ports/repositories.py` — 10 Repository-Protokolle
- 67 Domain-Tests

---

## [Phase 1: Grundgerüst] – 2026-05-21

### Hinzugefügt
- `migrations/0001_schema.sql` — Initialschema: 16 Tabellen, 17 Indizes,
  `schema_migrations`-Versionsverfolgung
- `migrations/0002_seed_defaults.sql` — Regelarbeitszeiten Mo–Fr,
  `system_config`-Defaults
- `infrastructure/db/connection.py` — SQLite-Verbindung (WAL, `row_factory`, PRAGMAs)
- `infrastructure/db/migrations.py` — Glob-Runner mit Idempotenz und Rollback-Sicherung
- `scripts/init_db.py` — Datenbankinitialisierung
- 12 Migrationstests

## [Audit & Dokumentation] – 2026-06-13

### Hinzugefügt
- Abschnitt „Betrieb & Rechtliches“ im `README.md` mit Verweisen auf VVT,
  Betriebsdokumentation, Rollenzuweisung, Betriebsfreigabe-Protokoll,
  Hardware-Inbetriebnahmeprotokoll, Backup-Zeitplan und Restore-Checkliste.

### Geändert
- Dokumentationsstand an die neuen Betriebsdokumente unter `docs/datenschutz/`
  und `docs/betrieb/` angepasst.