# Phasenübergreifende Nachtragsmatrix

**Datum:** 2026-06-11  
**Grundlage:** `docs/claude_coding/claude_code_prompt_hoch_arbeitszeit_v1_2026-06-11_20-08.md`

**Zweck:** Dokumentiert für relevante Artefakte die historische Zielphase,
die tatsächliche Einführungsphase und spätere Änderungen. Belegpflicht gilt
für jede Zeile.

**Methodik:** Einträge basieren ausschließlich auf Angaben in Phasenplänen
(`phase?_planung.md`, `planung_gesamt.md`) sowie SQL-Kommentaren. Wo keine
belastbare Phasenzuordnung vorliegt, wird dies explizit markiert.

---

## Matrix

| Artefakt | Artefaktart | Historische Zielphase | Tatsächliche Einführungsphase | Spätere Änderungen | Änderungsart | Belegstellen | Kommentar |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `migrations/0001_schema.sql` | Migration | Phase 1 | Phase 1 | — | originär | phase1_planung.md Z.9 | 16 Tabellen, 17 Indizes |
| `migrations/0002_seed_defaults.sql` | Migration | Phase 1 | Phase 1 | — | originär | phase1_planung.md Z.10 | Regelarbeitszeiten + system_config-Defaults |
| `migrations/0003_cleanup_booking_status.sql` | Migration | Phase 4 | Phase 4 | — | nachgezogen | planung_gesamt.md Z.114; phase1_planung.md Migrationsübersicht | Bereinigung von Phase-1-Schema-Altlasten |
| `migrations/0004_supplement_reject_fields_and_review_note.sql` | Migration | Phase 4 | Phase 4 | — | nachgezogen | planung_gesamt.md Z.115 | Semantische Trennung Genehmigung/Ablehnung |
| `migrations/0005_time_bookings_device_event_id.sql` | Migration | Phase 4 | Phase 4 | Operative Nutzung Phase 4 nachgezogen (2026-06-11) | Vorbereitungspunkt; operative Nutzung Nachtrag | planung_gesamt.md Z.116; Commit `0f20931` | Schema vorbereitet Phase 4; Produktionspfad erst 2026-06-11 |
| `migrations/0006_system_events_application_error.sql` | Migration | Phase 5 | Phase 5 | — | nachgezogen | planung_gesamt.md Z.117 | APPLICATION_ERROR für Terminal-UI-Fehler |
| `src/arbeitszeit/domain/enums.py` | Domain-Modul | Phase 2 | Phase 2 | — | originär | phase2_planung.md „enums.py" | 11 StrEnum-Klassen |
| `src/arbeitszeit/domain/entities.py` | Domain-Modul | Phase 2 | Phase 2 | — | originär | phase2_planung.md „entities.py" | 9 frozen @dataclass |
| `src/arbeitszeit/domain/errors.py` | Domain-Modul | Phase 2 | Phase 2 | — | originär | phase2_planung.md „errors.py" | DomainError + 9 Subklassen |
| `src/arbeitszeit/domain/audit_events.py` | Domain-Modul | Phase 2 (Kern) | Phase 2 | USER_ACCOUNT_* Phase 5; REACTIVATED/ROLE_CHANGED Phase 5+ | nachgezogen | phase2_planung.md; phase5_planung.md users-Modul | Katalog wuchs mit Benutzerkonten-Modul |
| `src/arbeitszeit/domain/services/booking_rules.py` | Domain-Modul | Phase 2 | Phase 2 | ValidationResult entfernt (phase2_coding_aufgabe) | Dokumentationskorrektur | phase2_planung.md; phase2_coding_aufgabe | validate_booking_sequence() → None |
| `src/arbeitszeit/domain/services/compliance_checks.py` | Domain-Modul | Phase 2 | Phase 2 | — | originär | phase2_planung.md | check_break_compliance, check_max_hours, check_rest_period |
| `src/arbeitszeit/domain/ports/repositories.py` | Domain-Modul | Phase 2 | Phase 2 | DeviceEventRepository Phase 4 nachgezogen | nachgezogen | phase2_planung.md; Commit `0f20931` | 10 originäre Protokolle + 1 Nachtrag |
| `src/arbeitszeit/application/unit_of_work.py` | Application-Modul | Phase 3 | Phase 3 | device_event_repo Attribut nachgezogen (2026-06-11) | nachgezogen | phase3_planung.md; Commit `0f20931` | |
| `src/arbeitszeit/application/commands.py` | Application-Modul | Phase 3 | Phase 3 | ApproveSupplementCommand, RejectSupplementCommand Phase 3 vorimplementiert | vorgezogen | phase3_planung.md Z.135–138 | Phase-4-Commands in Phase 3 vorimplementiert |
| `src/arbeitszeit/application/results.py` | Application-Modul | Phase 3 | Phase 3 | ApproveSupplementResult, RejectSupplementResult Phase 3 vorimplementiert | vorgezogen | phase3_planung.md Z.152–157 | Phase-4-Results in Phase 3 vorimplementiert |
| `src/arbeitszeit/application/use_cases/book_time.py` | Application-Modul | Phase 3 | Phase 3 | Ruhezeitprüfung (Plan: Phase 4/1b) + Rollenzeitfenster in Phase 3 vorimplementiert | vorgezogen | phase3_planung.md Z.229–231; phase4_planung.md Schritt 1b | |
| `src/arbeitszeit/application/use_cases/approve_supplement.py` | Application-Modul | Phase 4 | Phase 3 vorimplementiert | — | vorgezogen | phase3_planung.md Z.102, 257; phase4_planung.md Z.25 | |
| `src/arbeitszeit/application/use_cases/reject_supplement.py` | Application-Modul | Phase 4 | Phase 3 vorimplementiert | — | vorgezogen | phase3_planung.md Z.103, 273; phase4_planung.md Z.26 | |
| `src/arbeitszeit/application/use_cases/manage_work_schedule.py` | Application-Modul | Phase 3 | Phase 3 | Rollenprüfung (Plan: Phase 4/1c) in Phase 3 vorimplementiert | vorgezogen | phase3_planung.md Z.198, 291 | |
| `src/arbeitszeit/infrastructure/db/connection.py` | Infrastructure-Modul | Phase 1 | Phase 1 | — | originär | phase1_planung.md | PRAGMAs, WAL, row_factory |
| `src/arbeitszeit/infrastructure/db/migrations.py` | Infrastructure-Modul | Phase 1 | Phase 1 | — | originär | phase1_planung.md | Glob-Runner, Idempotenz |
| `src/arbeitszeit/infrastructure/db/unit_of_work.py` | Infrastructure-Modul | Phase 4 | Phase 4 | device_event_repo Attribut nachgezogen (2026-06-11) | nachgezogen | phase4_planung.md; Commit `0f20931` | |
| `src/arbeitszeit/infrastructure/db/repositories/device_event.py` | Infrastructure-Modul | Phase 4 (Schemavorbereitung) | Phase 4 nachgezogen (2026-06-11) | — | nachgezogen | Commit `0f20931` | Neu erstellt; nicht in originalem Phase-4-Plan |
| `src/arbeitszeit/infrastructure/backup/backup_service.py` | Infrastructure-Modul | Phase 4 | Phase 4 | restore_exports-Parameter nachgezogen (phase4_coding_aufgabe) | nachgezogen | phase4_planung.md Schritt 7; Commit `84d9c1f` | |
| `src/arbeitszeit/infrastructure/export/report_queries.py` | Infrastructure-Modul | Phase 4 | Phase 4 | — | originär | phase4_planung.md Schritt 8a | Zentrale Wahrheitsquelle für Exporte |
| `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` | Infrastructure-Modul | Phase 4 | Phase 4 | rfid_timeout-Parameter nachgezogen | Nachtrag/Hotfix | phase4_planung.md Schritt 6 | |
| `src/arbeitszeit/infrastructure/system_check.py` | Infrastructure-Modul | Phase 4 | Phase 4 | backup.backup_dir + export.export_dir in _REQUIRED_CONFIG_KEYS nachgezogen | Nachtrag/Hotfix | phase4_planung.md Schritt 9 | |
| `src/arbeitszeit/infrastructure/time_monitor.py` | Infrastructure-Modul | Phase 5 | Phase 5 | — | originär | phase5_planung.md Schritt 5 | |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | Presentation-Modul | Phase 5 | Phase 5 | device_event_id-Verkettung nachgezogen (2026-06-11); _run_one_cycle-Extraktion (phase5_coding_aufgabe) | nachgezogen | phase5_planung.md; Commit `0f20931` | |
| `src/arbeitszeit/presentation/admin_cli/user_accounts.py` | Presentation-Modul | Phase 5 | Phase 5 | reactivate, change-role, bootstrap nach Phase-5-Abschluss | nachgezogen | phase5_planung.md; Commits `6079886` | Vollständig abgeschlossen |
| `scripts/init_db.py` | Script | Phase 1 (originär) | Phase 1 | setup_vollstaendig()-Prüfung Phase 4 nachgezogen | nachgezogen | phase1_planung.md; planung_gesamt.md Z.101 | Phase-4-Infrastruktur-Abhängigkeit |
| `scripts/setup.py` | Script | Phase 4 zugeordnet | Phase 4 zugeordnet (nachträglich zugeordnet) | — | nachgezogen | planung_gesamt.md Z.101–102 | Nicht originäre Phase 1; nutzt Phase-2/4-Importe |
| `scripts/backup.py` | Script | Phase 4 | Phase 4 | --export-dir-Argument nachgezogen | Nachtrag/Hotfix | phase4_planung.md Schritt 7 | |
| `tests/test_migrations.py` | Testmodul | Phase 1 (6 Tests) | Phase 1 | Phase-4-Tests +5; Phase-5-Tests +1 | nachgezogen | phase1_planung.md Testverteilung | 12 Tests gesamt |
| `tests/domain/test_booking_rules.py` | Testmodul | Phase 2 (10 Tests) | Phase 2 | +4 Erfolgsfall-Tests (phase2_coding_aufgabe) | nachgezogen | phase2_planung.md | 14 Tests gesamt |
| `tests/domain/test_audit_events.py` | Testmodul | Nicht im Original-Plan | Phase 2 | — | Nachtrag/Hotfix | phase2_planung.md: „neu, nicht im Plan" | 2 Tests |
| `tests/application/test_approve_supplement.py` | Testmodul | Phase 4 | Phase 3 vorimplementiert | — | vorgezogen | phase3_planung.md Z.112 | 21 Tests |
| `tests/application/test_reject_supplement.py` | Testmodul | Phase 4 | Phase 3 vorimplementiert | — | vorgezogen | phase3_planung.md Z.113 | 13 Tests |
| `tests/application/test_fake_unit_of_work.py` | Testmodul | Nicht im Original-Plan | Phase 3 nachgezogen | — | Nachtrag/Hotfix | phase3_coding_aufgabe | 2 Tests; FakeUnitOfWork-Semantik |
| `tests/integration/test_user_accounts.py` | Testmodul | Phase 5 | Phase 5 | — | originär | phase5_planung.md; test_user_accounts.py | 18 Tests |
| `tests/integration/test_device_event_booking.py` | Testmodul | Phase 4 nachgezogen | Phase 4 nachgezogen (2026-06-11) | — | nachgezogen | Commit `0f20931` | 3 Tests; nicht im Originalplan |
| `tests/integration/test_init_db.py` | Testmodul | nicht entscheidbar auf Basis der vorliegenden Artefakte | Phase 4+ | — | nicht entscheidbar auf Basis der vorliegenden Artefakte | Kein expliziter Planungseintrag | 5 Tests |
| `tests/e2e/test_booking_flow.py` | Testmodul | Phase 5 (10 Tests) | Phase 5 | +2 APPLICATION_ERROR-Tests (phase5_coding_aufgabe) | nachgezogen | phase5_planung.md | 12 Tests gesamt |
| `tests/e2e/test_backup.py` | Testmodul | Phase 4 (19 Tests) | Phase 4 | +3 restore_exports-Tests (phase4_coding_aufgabe) | nachgezogen | phase4_planung.md | 22 Tests gesamt |

---

## Explizit erkannte Phasenverschiebungen

### Vorgezogene Inhalte (in frühere Phase als geplant)

| Artefakt | Geplant | Tatsächlich | Beleg |
| --- | --- | --- | --- |
| `approve_supplement.py` / `reject_supplement.py` | Phase 4 | Phase 3 | phase3_planung.md Z.102–103 |
| `test_approve_supplement.py` / `test_reject_supplement.py` | Phase 4 | Phase 3 | phase3_planung.md Z.112–113 |
| Ruhezeitprüfung in `book_time.py` (Schritt 1b) | Phase 4 | Phase 3 | phase4_planung.md Schritt 1b |
| Rollenprüfung in Use Cases (Schritt 1c) | Phase 4 | Phase 3 | phase3_planung.md Z.198, 291 |

### Nachgezogene Inhalte (nach ursprünglichem Phasenabschluss ergänzt)

| Artefakt | Ursprüngliche Phase | Nachgezogen wann | Beleg |
| --- | --- | --- | --- |
| `migrations/0003–0006` | Phase 1-Fundament | Phase 4/5 | planung_gesamt.md Z.114–117 |
| `device_event_id` Produktionspfad | Phase 4 vorbereitet | 2026-06-11 | Commit `0f20931` |
| `restore_exports`-Parameter | Phase 4 | phase4_coding_aufgabe | Commit `84d9c1f` |
| `reactivate`, `change-role`, `bootstrap` | Phase 5 | post-Phase-5 | Commits `6079886` |
| `setup_vollstaendig()` in `init_db.py` | Phase 1 (originär) | Phase 4+ | planung_gesamt.md Z.101 |

### Spätere Test-Ergänzungen

| Testmodul | Originalstand | Ergänzung |
| --- | --- | --- |
| `test_migrations.py` | 6 Tests (Phase 1) | +5 Phase 4, +1 Phase 5 |
| `test_booking_rules.py` | 10 Tests (Phase 2) | +4 Erfolgsfall-Tests |
| `test_booking_flow.py` | 10 Tests (Phase 5) | +2 APPLICATION_ERROR-Tests |
| `test_backup.py` | 19 Tests (Phase 4) | +3 restore_exports-Tests |

### Reine Dokumentationskorrekturen

| Artefakt | Korrektur |
| --- | --- |
| Alle Phasenpläne v4→v5 | Referenzdokument-Updates (mehrere Sessions 2026-06-11) |
| `booking_rules.py` ValidationResult | Entfernt (phase2_coding_aufgabe); war toter Code |
| Transaktionsregel (phase3_planung.md) | commit-vor-audit korrekt dokumentiert |

---

## Nicht entscheidbar auf Basis der vorliegenden Artefakte

- **`tests/integration/test_init_db.py`:** Kein expliziter Phaseneintrag in
  phase1_planung.md oder phase4_planung.md. Datei testet `setup_vollstaendig()`,
  das als Phase-4+-Erweiterung eingeordnet wurde. Phasenzuordnung des Testmoduls
  selbst ist offen.
- **Originäre Phase von `scripts/setup.py`:** Datei existiert nicht in Phase-1-Plan,
  wurde aber als Betriebsscript entwickelt. planung_gesamt.md Z.101 ordnet sie
  nachträglich Phase 4 zu. Ob diese Zuordnung im ursprünglichen Design so geplant
  war, ist nicht eindeutig belegbar.

---

## Selbstcheck (A7)

- ✓ Historische Zielphasen belegt (Phasenpläne als Quelle)
- ✓ Tatsächliche Einführungsphasen belegbar (Phasenpläne + Commits)
- ✓ Spätere Änderungen von Erstimplementierung getrennt
- ✓ Vorgezogene/nachgezogene Inhalte erkennbar
- ✓ Keine erkannten Doppelerfassungen
- ⚠ `test_init_db.py`: Phasenzuordnung offen (s. Abschnitt oben)
