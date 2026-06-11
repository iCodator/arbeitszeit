# Audit Phase 1 – Vollständiger Soll-Ist-Abgleich

**Erstellt:** 2026-06-11
**Prüfstand:** aktuelle Codebasis (395 Tests grün)
**Grundlage:** `phase1_planung.md`, `planung_gesamt.md`, `pflichtenheft_arbeitszeit_v5.md`, `regelwerk_arbeitszeit_v5.md`
**Laufnachweis:** `pytest tests/test_migrations.py` → 12/12 PASSED

---

## 1. Auditauftrag und Grundlagen

Phase 1 liefert das Projektfundament: Datenbankschema, Migrationssystem, Seed-Daten,
SQLite-Verbindung, Initialisierungsskript und den originären Testbestand.

Dieses Audit prüft jeden Liefergegenstand aus `phase1_planung.md` gegen den echten
Codestand und gleicht ihn mit den Anforderungen aus Pflichtenheft v5 und Regelwerk v5
ab. Alle Fakten sind direkt aus den Quelldateien belegt.

**Referenzdokumente für dieses Audit:**

| Dokument | Pfad | Status |
| --- | --- | --- |
| `pflichtenheft_arbeitszeit_v5.md` | Projektwurzel (`./`) | ✓ vorhanden |
| `regelwerk_arbeitszeit_v5.md` | Projektwurzel (`./`) | ✓ vorhanden |
| `anlage_einhaltung_pflichtenheft_v2.md` | `docs/` | ✓ vorhanden |

> **Befund D-01:** `phase1_planung.md` (Zeilen 333–334) referenziert die v5-Dokumente
> als `docs/pflichtenheft_arbeitszeit_v5.md` und `docs/regelwerk_arbeitszeit_v5.md`.
> Die Dateien liegen jedoch im **Projektwurzel**, nicht in `docs/`. Pfadangaben
> in der Planungsdokumentation sind damit falsch.

---

## 2. Sollbild Phase 1

### 2.1 Originärer Lieferumfang (aus `planung_gesamt.md`)

Migrationen 0001/0002 + 6 originäre Tests:

- `pyproject.toml`, `src/`-Layout, `tests/`, `.gitignore`, `.python-version`
- `migrations/0001_schema.sql` — vollständiges DDL, enthält `schema_migrations`
- `migrations/0002_seed_defaults.sql` — Regelzeiten + System-Config-Defaults
- `infrastructure/db/connection.py` — `isolation_level=None`, `PRAGMA foreign_keys=ON`, `row_factory`
- `infrastructure/db/migrations.py` — `executescript()` mit `BEGIN/COMMIT`, Versionsvalidierung
- `scripts/init_db.py` — Initialisierungsskript
- `tests/test_migrations.py` — ursprünglich 6 Testfälle

Spätere Nachträge (nicht Phase-1-Kern):
- `migrations/0003–0006` (Phase 4/5)
- 6 weitere Tests für 0004–0006 (Phase 4/5)

### 2.2 Anforderungen aus Pflichtenheft v5

Für Phase 1 direkt relevante §§:

| § | Anforderung |
| --- | --- |
| §10 Datenmodell | Benutzer, RFID-Karten, Buchungen, Korrekturen, Nachträge, Prüffälle, Regelzeiten, Systemkonfig, Audit-Log |
| §8.3 Resilienz | Transaktionssicher schreiben, Wiederanlauf, Backup/Restore-Vorbereitung |
| §12 Aufbewahrung | Mindestens 2 Jahre; keine physische Löschung fachlicher Buchungen |

### 2.3 Anforderungen aus Regelwerk v5

| § | Anforderung |
| --- | --- |
| §2 Grundregel | Reale Buchungen, keine stillen Systemannahmen |
| §18 Aufbewahrung | 2 Jahre, keine physische Löschung |
| §20 Backup/Restore | Grundlage im Schema vorhanden; Restore nur berechtigt |

---

## 3. Istbild je Liefergegenstand

### 3.1 Projektgerüst

| Liefergegenstand | Soll | Ist | Bewertung |
| --- | --- | --- | --- |
| `pyproject.toml` vorhanden | ja | ✓ vorhanden | OK |
| `requires-python` | `>=3.11,<3.13` (historisch) | `>=3.14,<3.15` (aktuell) | OK — historisch korrekt markiert |
| `src/`-Layout | `src/arbeitszeit/` als Paketroot | ✓ | OK |
| `evdev>=1.7`, `reportlab>=4.0` als Runtime-Deps | ja | ✓ | OK |
| `pytest>=8.0` als Dev-Dep | ja | ✓ | OK |
| `.python-version` | `3.14` | `3.14` | OK |
| `.gitignore` | `.venv/`, `__pycache__/`, `*.db`, Caches, `dist/`, `build/` | ✓ alle enthalten | OK |
| `docs/informelles/` nicht ausgeschlossen | ja | ✓ nicht in `.gitignore` | OK |

### 3.2 `migrations/0001_schema.sql`

**Tabellen** — Soll: 16 (15 fachliche + `schema_migrations`) — Ist: **16** ✓

| Ebene | Tabellen |
| --- | --- |
| Meta | `schema_migrations` |
| Person | `employees`, `user_accounts`, `rfid_cards` |
| Erfassung | `terminals`, `time_bookings`, `device_events` |
| Prüfung | `review_cases`, `review_case_actions`, `booking_status_history` |
| Änderung | `booking_corrections`, `supplements`, `work_schedule_versions` |
| Nachweis | `audit_log`, `system_events`, `system_config` |

Pflichtenheft v5 §10 fordert: Benutzer, RFID-Karten, Buchungen, Korrektionen, Nachträge,
Prüffälle, Regelarbeitszeiten, Systemkonfiguration, Audit-Log. **Alle 9 geforderten
Strukturkategorien sind abgebildet.** ✓

**Indizes** — Soll: 17 — Ist: **17** ✓ (direkt aus `grep -c "^CREATE INDEX"` bestätigt)

Vollständige Index-Liste (alle 17 vorhanden):

```
idx_audit_log_employee_event_at
idx_audit_log_object_event_at
idx_booking_corrections_booking_corrected_at
idx_booking_status_history_booking_changed_at
idx_device_events_occurred_at
idx_review_case_actions_case_created_at
idx_review_cases_employee_detected_at
idx_review_cases_status_detected_at
idx_rfid_cards_employee_status
idx_supplements_approval_status
idx_supplements_employee_event_at
idx_system_config_key_version
idx_system_events_event_at
idx_time_bookings_employee_booked_at
idx_time_bookings_status_booked_at
idx_user_accounts_employee_id
idx_work_schedule_versions_scope_weekday_valid_from
```

**Aufbewahrungsprinzip (Pflichtenheft v5 §12 / Regelwerk v5 §18):**
Das Schema enthält Status-Felder (`current_status`, `approval_status`) und
Korrekturtabellen (`booking_corrections`, `supplements`) statt physischer Löschung.
Keine `DELETE`-Trigger im Schema. **Prinzip architektonisch verankert.** ✓

**Resilienz (Pflichtenheft v5 §8.3):**
Schema enthält `schema_migrations` als Versionstabelle — atomare Migration
via `executescript` gewährleistet. ✓

### 3.3 `migrations/0002_seed_defaults.sql`

| Kategorie | Soll | Ist | Bewertung |
| --- | --- | --- | --- |
| `work_schedule_versions` | 5 globale Einträge Mo–Fr | ✓ 5 Einträge: Wochentage 1–5 | OK |
| Mo–Mi: 07:30–18:00 | ja | ✓ | OK |
| Do: 07:30–14:00 | ja | ✓ | OK |
| Fr: 07:30–16:00 | ja | ✓ | OK |
| `change_origin = 'SYSTEM_SEED'` | ja | ✓ | OK |
| `changed_by_user_id = NULL` | ja | ✓ | OK |
| `system_config` Keys | 4 Defaults | ✓ 4 Einträge | OK |
| `app.timezone` = `"Europe/Berlin"` | ja | ✓ | OK |
| `booking.grace_seconds_after_numpad_select` = `30` | ja | ✓ | OK |
| `backup.nas_enabled` = `false` | ja | ✓ | OK |
| `backup.nas_path` = `null` | ja | ✓ | OK |
| `audit_log` Seed-Einträge | 9 (5+4) | ✓ SELECT-INSERT für alle Seed-Zeilen | OK |

### 3.4 `infrastructure/db/connection.py`

| PRAGMA / Einstellung | Soll | Ist | Bewertung |
| --- | --- | --- | --- |
| `isolation_level=None` | ja | ✓ `sqlite3.connect(db_path, isolation_level=None)` | OK |
| `PRAGMA foreign_keys = ON` | ja | ✓ | OK |
| `PRAGMA journal_mode=WAL` | ja | ✓ | OK |
| `PRAGMA busy_timeout=5000` | ja | ✓ | OK |
| `row_factory = sqlite3.Row` | ja | ✓ | OK |

Alle PRAGMAs exakt wie in `phase1_planung.md` gefordert. ✓

**Resilienz (Pflichtenheft v5 §8.3):** WAL-Modus reduziert Lock-Konflikte zwischen
parallelen Verbindungen (conn + audit_conn). `busy_timeout=5000` verhindert sofortigen
Absturz bei kurzen Lock-Konflikten. ✓

### 3.5 `infrastructure/db/migrations.py`

| Eigenschaft | Soll | Ist | Bewertung |
| --- | --- | --- | --- |
| Glob-Pattern | `[0-9][0-9][0-9][0-9]_*.sql` | ✓ | OK |
| Versionsvalidierung | `version.isdigit() and len(version) == 4` | ✓ (vor f-String) | OK |
| Atomarität | `executescript()` mit `BEGIN/COMMIT` je Migration | ✓ | OK |
| Idempotenz | Prüfung gegen `schema_migrations` vor Ausführung | ✓ | OK |
| Rollback bei Fehler | `conn.rollback(); raise` | ✓ | OK |
| Kein `schema_migrations`-Eintrag bei Fehler | ja | ✓ (Exception vor INSERT) | OK |
| Default-Migrations-Verzeichnis | relativ zum Package-Pfad (`parents[4]/migrations`) | ✓ | OK |

### 3.6 `scripts/init_db.py`

| Eigenschaft | Soll | Ist | Bewertung |
| --- | --- | --- | --- |
| `--db`-Flag per argparse | ja | ✓ | OK |
| Default `arbeitszeit.db` | ja | ✓ | OK |
| Migrationen ausführen via `run_migrations()` | ja | ✓ | OK |
| `setup_vollstaendig()` prüft `backup.backup_dir` + `export.export_dir` | ja | ✓ | OK |
| Fall A: neue Migrationen + Setup fehlt → Warnung + Hinweis auf `setup.py` | ja | ✓ | OK |
| Fall B: keine neuen Migrationen + Setup ok → „System betriebsbereit." | ja | ✓ | OK |
| Fall C: keine neuen Migrationen + Setup fehlt → Warnung + Hinweis | ja | ✓ | OK |

### 3.7 `scripts/setup.py`

| Eigenschaft | Soll | Ist | Bewertung |
| --- | --- | --- | --- |
| `--db`-Flag | ja | ✓ | OK |
| `--backup-dir` + `--export-dir` (nicht-interaktiv) | ja | ✓ | OK |
| Interaktive Pfad-Eingabe als Fallback | ja | ✓ (`_prompt_path()`) | OK |
| Idempotenz (bereits konfigurierte Keys überspringen) | ja | ✓ | OK |
| `ChangeOrigin.MIGRATION` für Seed-ähnlichen Eintrag | ja | ✓ | OK |
| Korrekte Abschlussmeldung (Terminal-UI + Admin-CLI) | ja | ✓ | OK |
| Prüfung ob DB existiert vor Ausführung | ja | ✓ (`sys.exit(1)` wenn fehlt) | OK |

### 3.8 `tests/test_migrations.py`

**Laufnachweis:** 12/12 PASSED (ausgeführt am 2026-06-11)

| Test-Name | Phasenzuordnung | Status |
| --- | --- | --- |
| `test_leere_db_wird_vollstaendig_migriert` | Phase 1 (originär) | ✓ |
| `test_erneutes_ausfuehren_ist_idempotent` | Phase 1 (originär) | ✓ |
| `test_seed_daten_vorhanden_nach_migration` | Phase 1 (originär) | ✓ |
| `test_audit_log_enthaelt_seed_eintraege` | Phase 1 (originär) | ✓ |
| `test_schema_migrations_enthaelt_genau_die_erwarteten_versionen` | Phase 1 (originär) | ✓ |
| `test_fehlgeschlagene_migration_hinterlaesst_keinen_schema_migrations_eintrag` | Phase 1 (originär) | ✓ |
| `test_migration_0004_fuegt_neue_spalten_ein` | Phase 4 | ✓ |
| `test_migration_0005_fuegt_device_event_id_ein` | Phase 4 | ✓ |
| `test_migration_0005_erhaelt_time_bookings_foreign_keys_und_indizes` | Phase 4 | ✓ |
| `test_migration_0005_datensatz_bleibt_erhalten` | Phase 4 | ✓ |
| `test_wiederholte_ausfuehrung_erzeugt_keine_doppelten_seed_daten` | Phase 4/5 | ✓ |
| `test_migration_0006_application_error_event_type_verfuegbar` | Phase 5 | ✓ |

Phasenverteilung: 6 originäre Phase-1-Tests + 5 Phase-4-Tests + 1 Phase-5-Test = 12 gesamt. ✓

---

## 4. Negativbefund-Verzeichnis

| ID | Kategorie | Befund | Risiko | Empfehlung |
| --- | --- | --- | --- | --- |
| D-01 | Dokumentationsfehler | `phase1_planung.md` Z. 333–334 referenziert `docs/pflichtenheft_arbeitszeit_v5.md` und `docs/regelwerk_arbeitszeit_v5.md`, aber Dateien liegen im **Projektwurzel** (`./`) | Mittel — bei maschinellen Pfadprüfungen falscher Pfad | Pfade in `phase1_planung.md` korrigieren: `pflichtenheft_arbeitszeit_v5.md` (ohne `docs/`-Präfix) |

**Keine weiteren Abweichungen gefunden.** Alle anderen geprüften Eigenschaften
stimmen mit dem Soll überein.

---

## 5. Abschlussbewertung

| Bereich | GO / NO-GO | Begründung |
| --- | --- | --- |
| Schema (Tabellen + Indizes) | **GO** | 16 Tabellen, 17 Indizes — vollständig und korrekt |
| Pflichtenheft v5 §10 Datenmodell | **GO** | Alle 9 geforderten Strukturkategorien abgebildet |
| Pflichtenheft v5 §8.3 Resilienz | **GO** | WAL, busy_timeout, atomare Migrationen, Rollback |
| Pflichtenheft v5 §12 / Regelwerk v5 §18 Aufbewahrung | **GO** | Keine physische Löschung, Status-Mechanismus vorhanden |
| Regelwerk v5 §20 Backup-Grundlage | **GO** | Schema und Seed bereitet Backup/Restore vor |
| Seed-Daten | **GO** | 5+4+9 Einträge exakt wie dokumentiert |
| Connection-PRAGMAs | **GO** | Alle 4 PRAGMAs + `row_factory` korrekt gesetzt |
| Migrations-Runner | **GO** | Glob, Validierung, Atomarität, Idempotenz, Rollback |
| Init-Script | **GO** | Fälle A/B/C, `--db`-Flag, `setup_vollstaendig()` |
| Setup-Script | **GO** | Interaktiv + nicht-interaktiv, idempotent |
| Testabdeckung | **GO** | 12/12 Tests grün, alle 6 Phase-1-Kernszenarien abgedeckt |
| Dokumentationspfade v5 | **NO-GO** | Befund D-01: falsche Pfadangaben für v5-Dokumente |

**Phase 1 ist technisch vollständig und korrekt implementiert.**
Der einzige offene Punkt (D-01) ist ein rein dokumentarischer Pfadfehler ohne
Auswirkung auf die Funktionalität. Er ist behebbar durch eine Einzeilanpassung
in `phase1_planung.md`.
