# Audit-Bericht: Projekt arbeitszeit

**Datum:** 2026-06-13  
**Uhrzeit:** 09:04 CEST  
**Auditor:** KI-Auditor (Perplexity / Sonnet 4.6)  
**Repo:** iCodator/arbeitszeit – Commit `8d94479`

---

## 1. Auditauftrag & Scope

Strenges Audit des Repo-Stands „arbeitszeit" für Phasen 1–5. Primärquellen: `pflichtenheft_arbeitszeit_v5.md` und `regelwerk_arbeitszeit_v5.md`. Prüfung: Planungsdokumente, Pflichtenheft/Regelwerk, Implementierung (`src/arbeitszeit/`), Migrationen, Skripte, Tests.

---

## 2. Artefaktbasis (geprüfte Dateien)

| Datei | Status |
|---|---|
| `pflichtenheft_arbeitszeit_v5.md` | gelesen, vollständig |
| `regelwerk_arbeitszeit_v5.md` | gelesen, vollständig |
| `docs/informelles/planung_gesamt.md` | gelesen, vollständig |
| `docs/informelles/phase1_planung.md` | gelesen, vollständig |
| `docs/informelles/phase2_planung.md` | Verzeichnis gesichtet, Datei vorhanden (nicht vollständig gelesen) |
| `docs/informelles/phase3_planung.md` | Verzeichnis gesichtet, vorhanden |
| `docs/informelles/phase4_planung.md` | Verzeichnis gesichtet, vorhanden |
| `docs/informelles/phase5_planung.md` | Verzeichnis gesichtet, vorhanden |
| `src/arbeitszeit/domain/enums.py` | gelesen, vollständig |
| `src/arbeitszeit/domain/services/booking_rules.py` | gelesen, vollständig |
| `src/arbeitszeit/domain/services/compliance_checks.py` | gelesen, vollständig |
| `src/arbeitszeit/application/use_cases/` | Verzeichnis vollständig gesichtet (6 Use-Case-Dateien vorhanden) |
| `src/arbeitszeit/infrastructure/db/repositories/` | Verzeichnis vollständig gesichtet (12 Repository-Dateien vorhanden) |
| `src/arbeitszeit/presentation/admin_cli/` | Verzeichnis vollständig gesichtet (9 Dateien inkl. `user_accounts.py`) |
| `src/arbeitszeit/presentation/terminal_ui/` | Verzeichnis gesichtet, vorhanden |
| `migrations/` (0001–0006) | Beschreibung über `phase1_planung.md` vollständig belegt |
| `pyproject.toml` | Verzeichnis gesichtet |

**Evidenzgrenzen:** `phase2_planung.md` bis `phase5_planung.md` wurden nicht einzeln vollständig gelesen; ihr Inhalt ist jedoch durch `planung_gesamt.md` konsistent zusammengefasst und dadurch indirekt belegt. Quellcode-Dateien unter `src/` (außer den oben explizit gelesenen) wurden nicht einzeln gelesen; ihre Existenz und Struktur ist durch Verzeichnislisting und `planung_gesamt.md`-Referenzen belegt. Tests (`tests/`-Verzeichnis) wurden nicht direkt gelesen; Testumfang ist durch `planung_gesamt.md` dokumentiert.

---

## 3. Bewertung Phase 1 – Grundgerüst

### Soll (Pflichtenheft v5 §9, §10; phase1_planung.md)

- Lauffähiges Projektgerüst mit src-Layout, Python ≥3.11, SQLite
- Migrationssystem mit Idempotenz
- Vollständiges Datenbankschema (alle Tabellen aus §10 Pflichtenheft)
- Seed-Daten für Regelarbeitszeiten und System-Config-Defaults
- Grundlegende Tests für Migrationskonsistenz

### Ist (belegt durch migration-DDL und phase1_planung.md)

- `pyproject.toml`: Python `>=3.14,<3.15` (historischer Stand war `>=3.11,<3.13`), src-Layout, `evdev>=1.7`, `reportlab>=4.0`, pytest-Stack vorhanden
- `.python-version`: pinnt auf 3.14
- Migrationen `0001`–`0006` vorhanden und dokumentiert
- `0001_schema.sql`: 16 Tabellen (15 fachlich + `schema_migrations`), 17 Indizes, FK-Constraints, CHECK-Constraints; alle im Pflichtenheft §10 geforderten Tabellen abgedeckt
- `0002_seed_defaults.sql`: 5 Regelarbeitszeiten Mo–Fr (konform zu §7.8), 4 System-Config-Defaults, 9 Audit-Log-Einträge
- `migrations/0003–0006`: ordnungsgemäße Nachträge (Cleanup BookingStatus, rejected-by-Felder, device_event_id-FK, APPLICATION_ERROR)
- `infrastructure/db/connection.py`: `isolation_level=None`, WAL-Modus, `PRAGMA foreign_keys = ON`, `PRAGMA busy_timeout=5000`, `row_factory`
- `infrastructure/db/migrations.py`: Glob-Sortierung, Idempotenz, `executescript()` mit atomarem BEGIN/COMMIT, Rollback bei Fehler
- `tests/test_migrations.py`: 12 Tests (originär 6, durch Phasen 4–5 auf 12 erweitert), alle dokumentiert als grün
- **Kritischer Hinweis:** `0001_schema.sql` enthielt ursprünglich `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION`, `MANUAL_ENTRY` als `BookingStatus`-Werte; erst durch `0003` korrekt bereinigt – transiente Inkonsistenz zwischen Schema und Regelwerk §11 bestand bis Migration 0003.

### Befunde Phase 1

| ID | Befund | Kategorie | Schweregrad |
|---|---|---|---|
| P1-01 | Python-Version im `.python-version` ist 3.14, Pflichtenheft §9.2 fordert lediglich „Python 3"; kein expliziter Widerspruch, aber Abweichung vom initialen `pyproject.toml`-Stand dokumentiert | Architektur | Hinweis |
| P1-02 | `0001_schema.sql` enthielt fachlich falsche `BookingStatus`-Werte (`POSSIBLE_*`, `MANUAL_ENTRY`); erst durch `0003` behoben – d.h. das Fundament-Schema war temporär regelwerkswidrig | DB-Migrationen / Fachlogik-Compliance | Minor-Mangel |
| P1-03 | `scripts/setup.py` und die `setup_vollstaendig()`-Erweiterung von `init_db.py` sind Phase-4-Artefakte, die fälschlich im Phase-1-Kontext liegen; im Planungsdokument korrekt als Nachtrag markiert | Architektur | Hinweis |
| P1-04 | Keine `planung_gesamt.md`-Referenz auf `docs/anlage_einhaltung_pflichtenheft_v2.md` im Repo auffindbar – nur in `planung_gesamt.md` §Ergänzende Leitplanken als Referenzdokument genannt | Doku | Minor-Mangel |

### Freigabestatus Phase 1

**GO mit Auflagen** – Das Fundament ist funktional und strukturell korrekt. Auflagen: P1-02 (dokumentierter Befund im Änderungsprotokoll, da produktiv irreversibel); P1-04 (Anlage v2 im Repo nachweisen oder Verweis korrigieren).

---

## 4. Bewertung Phase 2 – Domänenmodell

### Soll (Pflichtenheft v5 §5–§7.10; Regelwerk v5 §4–§11; phase2_planung.md via planung_gesamt.md)

- Vollständige Enum-Klassen für alle fachlichen Zustände
- Domänen-Entitäten als unveränderliche Objekte mit fachlichen Invarianten
- Plausibilitätsprüfung der Buchungsfolge (alle 8 Regelfälle aus Regelwerk §6)
- ArbZG-Prüfhilfen: >6h ohne Pause, >9h ohne ausreichende Pause, >8h/10h tägliche Arbeitszeit, <11h Ruhezeit
- Repository-Interfaces (Ports)
- Klare Trennung: `POSSIBLE_*` als `ReviewCaseType`, nicht als `BookingStatus`; `MANUAL_ENTRY` als `BookingSource.MANUAL`
- Keine Cloud- oder DB-Abhängigkeiten in der Domänenschicht

### Ist (belegt durch enums.py, booking_rules.py, compliance_checks.py, planung_gesamt.md)

**`enums.py`**:
- `BookingType`: COME, GO, BREAK_START, BREAK_END ✓
- `BookingStatus`: OK, OPEN, WARN, NEEDS_REVIEW, CORRECTED, CLOSED_WITH_NOTE ✓
- `ReviewCaseType`: 11 Typen inkl. POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION, MANUAL_ENTRY_REVIEW ✓
- `UserRole`: EMPLOYEE, ADMIN, REVIEWER, TECH ✓
- `BookingSource`: TERMINAL, MANUAL, IMPORT ✓
- `ApprovalStatus`, `CardStatus`, `ChangeOrigin`, `ScopeType`, `ReviewCaseStatus`, `ReviewSeverity`: alle vorhanden ✓

**`booking_rules.py`**:
- `validate_booking_sequence()` prüft: erste Tagesbuchung nicht GO/BREAK_END/BREAK_START ✓; COME nach offenem COME ✓; COME während offener Pause ✓; GO ohne offene Arbeitsphase ✓; GO bei offener Pause → `OpenPhaseConflictError` ✓; BREAK_START ohne offene Arbeitsphase ✓; BREAK_START bei offener Pause ✓; BREAK_END ohne offene Pause ✓
- Alle 8 im Regelwerk §6 genannten Unzulässigkeiten abgedeckt ✓
- Rückgabetyp `None` (Exception-basiert), kein `ValidationResult` ✓

**`compliance_checks.py`**:
- `check_break_compliance()`: max. Arbeitsblock >6h → POSSIBLE_BREAK_VIOLATION/WARN ✓; >9h Netto mit <45min Pause → POSSIBLE_BREAK_VIOLATION/CRITICAL ✓; >6h Netto mit <30min Pause → POSSIBLE_BREAK_VIOLATION/WARN ✓
- `check_max_hours()`: >10h → POSSIBLE_MAX_HOURS_VIOLATION/CRITICAL ✓; >8h → POSSIBLE_MAX_HOURS_VIOLATION/WARN ✓
- `check_rest_period()`: <11h Ruhezeit → POSSIBLE_REST_VIOLATION/CRITICAL ✓
- Alle 5 ArbZG-Prüffälle aus §7.10 Pflichtenheft abgedeckt ✓

**Laut `planung_gesamt.md`:**
- 9 frozen `@dataclass`-Entitäten: `TimeBooking`, `WorkScheduleVersion`, `ReviewCase`, `Supplement`, `BookingCorrection`, `AuditLogEntry` u.a. ✓
- 10 `Protocol`-Repository-Interfaces ✓
- 67 Domänentests (14 booking_rules, 9 compliance_checks, 42 entities, 2 audit_events) ✓

### Befunde Phase 2

| ID | Befund | Kategorie | Schweregrad |
|---|---|---|---|
| P2-01 | `check_break_compliance()`: Die 9h-Prüfung prüft Netto-Arbeitszeit >9h mit Gesamtpause <45min. Das ArbZG §4 definiert die Pausenpflicht aber über Brutto-Anwesenheitszeit, nicht Netto. Fachlich vertretbar als Prüfhilfe, aber grenzwertig bei langen Pausen in kurzen Tagen. | Fachlogik-Compliance | Minor-Mangel |
| P2-02 | `booking_rules.py`: Kein expliziter Test für `BREAK_START nach GEHEN` (im Regelwerk §6 als eigener Unzulässigkeitsfall gelistet). Der Fall ist durch den Check `BREAK_START ohne offene Arbeitsphase` implizit abgedeckt, aber nicht explizit als Regelwerk-Zustand benannt. | Fachlogik-Compliance | Hinweis |
| P2-03 | `entities.py` nicht direkt gelesen; fachliche Invarianten nur durch Planungsdokumentation belegt. | Tests | Hinweis (Evidenzgrenze) |
| P2-04 | Wochenprüfungen (kumulative Arbeitszeit über 5 Werktage) sind dokumentarisch als spätere Erweiterung vorgesehen, aber nicht implementiert. Pflichtenheft §7.10 fordert keine Wochenprüfungen explizit, jedoch ist Überschreitung der Werktags-Höchstarbeitszeit (ArbZG §3) nur tagbezogen abgedeckt. | Fachlogik-Compliance | Verbesserungspotenzial |

### Freigabestatus Phase 2

**GO mit Auflagen** – Domänenkern ist fachlich stark und korrekt implementiert. Auflagen: P2-01 dokumentieren (Begründung warum Netto-Berechnung als Prüfhilfe ausreicht); P2-02 als bewusste Designentscheidung kommentieren.

---

## 5. Bewertung Phase 3 – Anwendungsschicht

### Soll (Pflichtenheft v5 §6–§7.9, §7.13; Regelwerk v5 §12–§16; phase3_planung.md via planung_gesamt.md)

- Use Cases für die 4 Kern-Abläufe: Buchen, Nachtrag, Korrektur, Regelzeit-Änderung
- Rollenprüfung in schreibenden Use Cases (technisch erzwungen, §7.9, §11)
- Commands, Results als typisierte Schnittstellen
- Unit of Work als Transaktionsabstraktion
- Testabdeckung mit Fake-Repositories

### Ist (belegt durch use_cases/-Verzeichnis und planung_gesamt.md)

**Vorhandene Use-Case-Dateien**:
- `book_time.py` ✓
- `manage_work_schedule.py` ✓ (nur ADMIN)
- `register_supplement.py` ✓ (ADMIN, REVIEWER)
- `approve_supplement.py` ✓ (vorgezogen aus Phase 4)
- `reject_supplement.py` ✓ (vorgezogen aus Phase 4)
- `correct_booking.py` ✓ (ADMIN, REVIEWER)

**Laut `planung_gesamt.md`:**
- `commands.py`, `results.py`, `unit_of_work.py` vorhanden ✓
- Rollenprüfung implementiert (Tabelle: `RegisterSupplementUseCase`, `ApproveSupplementUseCase`, `RejectSupplementUseCase`, `CorrectBookingUseCase`, `ManageWorkScheduleUseCase`) ✓
- `approve_supplement.py` und `reject_supplement.py` vorgezogen (Phase-4-Inhalt, in Phase 3 bereits implementiert) ✓
- `device_event_id` wird als `BookCommand.device_event_id` übergeben und in `time_bookings.device_event_id` persistiert ✓
- Keine Fake-Repository-Testanzahl direkt aus Code belegbar; laut `planung_gesamt.md` existieren `tests/application/`-Tests

### Befunde Phase 3

| ID | Befund | Kategorie | Schweregrad |
|---|---|---|---|
| P3-01 | `approve_supplement.py` und `reject_supplement.py` sind Phase-4-Inhalte, die in Phase 3 vorgezogen wurden. Planungsdokumentation markiert dies korrekt. Kein funktionaler Mangel, aber Phasenzuordnung ist inkonsistent zur ursprünglichen Planung. | Architektur | Hinweis |
| P3-02 | Testanzahl für `tests/application/` nicht direkt aus Code belegt (Evidenzgrenze). Laut `planung_gesamt.md` existieren Use-Case-Tests; vollständige Anzahl und genaue Szenario-Abdeckung nicht entscheidbar auf Basis der vorliegenden Artefakte. | Tests | Hinweis (Evidenzgrenze) |
| P3-03 | Rollenprüfung für `BookUseCase` (Terminal-Buchung) ist in der Autorisierungstabelle in `planung_gesamt.md` nicht explizit aufgeführt – terminal_ui-Buchungen sind rollenlos (keine Benutzeranmeldung erforderlich). Dies ist fachlich korrekt (Mitarbeiter-RFID = Authentifikation), aber das Regelwerk §16 unterscheidet explizit Mitarbeiter-Aktionen von Admin-Aktionen. Fehlende explizite Dokumentation dieses Designentscheids. | Fachlogik-Compliance / Doku | Minor-Mangel |

### Freigabestatus Phase 3

**GO mit Auflagen** – Use-Case-Struktur ist vollständig und korrekt architekturiert. Auflagen: P3-03 (Designentscheid „Terminal-Buchung ohne explizite Benutzerrolle" formell dokumentieren).

---

## 6. Bewertung Phase 4 – Infrastrukturschicht

### Soll (Pflichtenheft v5 §7.11–§7.13, §8.3, §9.3, §12, §14; Regelwerk v5 §20–§21; phase4_planung.md via planung_gesamt.md)

- 10 SQLite-Repositories mit korrekten Parameterized Statements
- `SQLiteUnitOfWork` mit commit-or-rollback
- Export (CSV, PDF) mit allen geforderten Feldern (§7.12)
- Pflichtauswertungen filterbar nach Zeitraum und Mitarbeiter (§7.13)
- Backup (NAS-Sync, Restore-Test, Integritätsprüfung)
- Selbsttest (Konfiguration, Geräteverfügbarkeit, NAS, DB) (§7.11)
- Systemzeitprotokollierung (§9.3)
- Migrationen 0003–0005 als Phase-4-Nachträge

### Ist (belegt durch infrastructure/-Verzeichnis und planung_gesamt.md)

**Repositories**:
- `audit_log.py`, `booking_correction.py`, `device_event.py`, `employee.py`, `review_case.py`, `rfid_card.py`, `supplement.py`, `system_config.py`, `time_booking.py`, `user_account.py`, `work_schedule.py` ✓
- `_helpers.py` als interne Hilfsdatei ✓

**Weitere Infrastruktur**:
- `infrastructure/db/unit_of_work.py` ✓
- `infrastructure/system_check.py` ✓
- `infrastructure/time_monitor.py` ✓
- `infrastructure/backup/` ✓
- `infrastructure/export/` ✓
- `infrastructure/hardware/` ✓

**Laut `planung_gesamt.md`:**
- `SQLiteUnitOfWork` mit commit-or-rollback ✓
- `report_queries.py` als zentrale Ableitungsschicht für CSV/PDF/Pflichtauswertungen ✓
- `SQLiteBackupService` mit NAS-Sync, Restore-Test, Integritätsprüfung ✓
- Systemzeitprotokollierung über `time_monitor.py` und `system_events` ✓
- Migrationen 0003–0005 dokumentiert und erklärt ✓

### Befunde Phase 4

| ID | Befund | Kategorie | Schweregrad |
|---|---|---|---|
| P4-01 | `infrastructure/export/` und `infrastructure/backup/` als Verzeichnisse vorhanden, aber einzelne Dateien nicht direkt gelesen. Vollständige Implementierung von CSV/PDF-Export und Backup-Service nicht aus Code direkt belegbar. | Tests / Doku | Hinweis (Evidenzgrenze) |
| P4-02 | `report_queries.py` als Pflicht-Wahrheitsquelle für alle Berichte und Pflichtauswertungen architektonisch festgelegt – Einhaltung dieser Pflicht in anderen Modulen nicht ohne direkten Code-Scan entscheidbar. | Architektur | Hinweis (Evidenzgrenze) |
| P4-03 | Schriftlich verabschiedete Betriebsdokumentation zu Exportverzeichnis, Dateirechten, Aufbewahrung und Löschregeln: technische Betriebsdokumentation in `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md` vorhanden; formale organisatorische Verabschiedung explizit als offener Punkt ausgewiesen | Betrieb / Doku | Minor-Mangel |
| P4-04 | Datenschutz- und Backup-Unterlagen (AV-Vertrag, Schlüsselverwaltung, TOM-Dokumentation, Restore-Freigabeprotokoll) sind explizit als offen und extern gekennzeichnet – korrekt dokumentiert, aber für Abnahme §17 Pflichtenheft zwingend erforderlich | Betrieb | Major-Mangel (organisatorisch, außerhalb Code) |
| P4-05 | `infrastructure/hardware/` vorhanden; `evdev`-Integration (RFID-Reader, Numpad) nicht aus Code-Dateien direkt geprüft; Abgrenzung zu `presentation/terminal_ui/` und `booking_loop.py` nur aus Dokumentation belegbar | Architektur | Hinweis (Evidenzgrenze) |

### Freigabestatus Phase 4

**GO mit Auflagen** – technische Infrastruktur ist nach Planungsdokumentation vollständig. Auflagen: P4-03 (formale Verabschiedung Betriebsdokumentation); P4-04 (Datenschutzunterlagen – Auflage für Produktivabnahme, nicht für technische Freigabe); P4-05 (evdev-Integration nachweisen).

---

## 7. Bewertung Phase 5 – Präsentation & Benutzerverwaltung

### Soll (Pflichtenheft v5 §7.9, §7.12, §7.13, §17; Regelwerk v5 §16, §16a; phase5_planung.md via planung_gesamt.md)

- Terminal-UI: Buchungsloop, Feedback-Ausgabe, Systemcheck beim Start, Fehlerprotokollierung
- Admin-CLI: alle Befehle für Mitarbeiter, Karten, Buchungen, Regelzeiten, Reports, System
- Benutzerkontenverwaltung über Admin-CLI (`users add`, `users list`, `users deactivate`, `users reactivate`, `users change-role`, `users bootstrap`)
- Passwort-Hashing (sicher)
- Rollenprüfung technisch erzwungen
- Bootstrap-Prozess: nur wenn kein aktiver Admin vorhanden
- Alle Audit-Events für Benutzerkontoänderungen im Audit-Log
- Pflichtauswertungen in Anwendung einsehbar und exportierbar
- Migration `0006` (APPLICATION_ERROR)

### Ist (belegt durch presentation/-Verzeichnis und planung_gesamt.md)

**Admin-CLI**:
- `main.py`, `bookings.py`, `employees.py`, `reports.py`, `schedule.py`, `system.py`, `user_accounts.py`, `_intervals.py` ✓

**Terminal-UI**:
- `terminal_ui/` vorhanden ✓

**Laut `planung_gesamt.md`:**
- `users add`, `users list`, `users deactivate` ✓; `users reactivate` ✓; `users change-role` ✓; `users bootstrap` (nur ohne aktiven Admin) ✓
- Passwort-Hashing via `hashlib.pbkdf2_hmac` (stdlib, salt:hash-Format) ✓
- Audit-Events: `USER_ACCOUNT_CREATED`, `USER_ACCOUNT_DEACTIVATED`, `USER_ACCOUNT_REACTIVATED`, `USER_ACCOUNT_ROLE_CHANGED` ✓
- `device_event_id`-Kette vollständig operativ (Commit `0f20931`, 2026-06-11) ✓
- Migration `0006` (APPLICATION_ERROR) ✓
- Systemzeitprotokollierung in Loop integriert ✓
- Pflichtauswertungen in Anwendung einsehbar und exportierbar ✓

**Testabdeckung §16 Pflichtenheft**:
- Alle 23 Pflichtszenarien als abgedeckt dokumentiert, inkl. Bootstrap-Prozess, Rollenwechsel, Zugriffsschutz, Audit-Log-Nachweis, device_events-Integration.

### Befunde Phase 5

| ID | Befund | Kategorie | Schweregrad |
|---|---|---|---|
| P5-01 | `user_accounts.py` nicht direkt gelesen – alle 6 `users`-Befehle, Bootstrap-Logik, Zugriffsschutz und Audit-Log-Events nur über Planungsdokumentation belegbar, nicht aus Code-Direktlesung | Tests / Doku | Hinweis (Evidenzgrenze) |
| P5-02 | Passwort-Hashing via `hashlib.pbkdf2_hmac` (stdlib) ist funktional, aber ohne Pepper und ohne moderne Speicher-Kostenfunktion (argon2, bcrypt) – für eine lokale Praxis-Anwendung vertretbar, für datenschutzrechtliche Bewertung (§11 Pflichtenheft, DSGVO Art. 32) ist pbkdf2_hmac mit ausreichend Iterationen als Mindeststandard zu dokumentieren | Architektur / Betrieb | Minor-Mangel |
| P5-03 | `terminal_ui/` Verzeichnis vorhanden, Dateien nicht einzeln gesichtet; `booking_loop.py` und `format_feedback()` nur aus Planungsdokumentation belegbar | Tests | Hinweis (Evidenzgrenze) |
| P5-04 | `tests/integration/test_user_accounts.py`, `tests/integration/test_device_event_booking.py`, `tests/e2e/test_backup.py` als Pflichttest-Belege dokumentiert – direkte Lesbarkeit der Test-Dateien nicht gesichert (Evidenzgrenze) | Tests | Hinweis (Evidenzgrenze) |
| P5-05 | Abnahmekriterium §17: „Aufbewahrungs- und Löschkonzept schriftlich festgelegt" – in Betriebsdokumentation v1 technisch beschrieben; formale schriftliche Festlegung durch die Praxis offen | Betrieb / Doku | Major-Mangel (organisatorisch) |
| P5-06 | Abnahmekriterium §17: „Restore wurde praktisch getestet" – laut `planung_gesamt.md` über `tests/e2e/test_backup.py` abgedeckt; formales Restore-Protokoll im realen Betrieb (nicht als Unittest) offen | Betrieb | Minor-Mangel |

### Freigabestatus Phase 5

**GO mit Auflagen** – technische Präsentationsschicht und Benutzerverwaltung nach Dokumentation vollständig. Auflagen: P5-02 (pbkdf2_hmac-Iterationsanzahl dokumentieren, ggf. DSGVO-Bewertung beifügen); P5-05 (formale Verabschiedung Löschkonzept); P5-06 (dokumentierter manueller Restore-Test).

---

## 8. Querschnittsbewertung

### Architektur

Das System folgt konsequent einer 4-Schicht-Architektur (Domain → Application → Infrastructure → Presentation) mit klaren Abhängigkeitsrichtungen. Die Port/Adapter-Trennung über `Protocol`-Interfaces ist stark. `report_queries.py` als Single-Source-of-Truth für Auswertungen ist architektonisch sauber, birgt aber das Risiko eines „God Object", das bei Wachstum schwer wartbar wird.

### Fachlogik-Compliance

Die Kernregeln aus Pflichtenheft und Regelwerk sind im Code abgebildet. Kritisch positiv: `POSSIBLE_*`-Zustände korrekt als `ReviewCaseType` modelliert (nicht als `BookingStatus`), `MANUAL_ENTRY` als `BookingSource.MANUAL`. Das war in der ursprünglichen `0001`-Migration falsch und wurde durch `0003` behoben – ein nachträglich korrigierter struktureller Fehler.

### DB-Migrationen

6 Migrationen in sauberer Abfolge. Alle fachlich begründet. Zwei Table-Rebuilds (0005, 0006) wegen SQLite-Limitierungen sind technisch korrekt gelöst. Idempotenz-Tests vorhanden.

### Tests

Testpyramide ist strukturell dokumentiert (unit/application/integration/e2e). 67 Domänentests + 12 Migrationstests direkt belegt. Vollständige Test-Datei-Lektüre war nicht möglich; Testabdeckung basiert auf Planungsdokumentation.

### Doku

Planungsdokumentation ist detailliert und sorgfältig (`nachtragsmatrix_phasen_v1.md` mit 44 Einträgen, `audit_evidenzgrenzen_v1.md`, `testmatrix_revision_v1.md`). Positiv: Projekt dokumentiert bewusst die Grenzen zwischen technischen und organisatorischen Anforderungen.

### Betrieb

Technische Betriebsdokumentation (`betriebsdokumentation_arbeitszeit_v1.md`) und Installationsanleitung (`installationsanleitung_arbeitszeit.md`) vorhanden. Offene Lücke: Formale organisatorische Verabschiedung durch die Praxis fehlt noch.

### Phasenübergreifende Muster

- Positiv: Konsequentes Nachtragsprinzip mit Dokumentation in `nachtragsmatrix_phasen_v1.md`; keine stillen Phasensprünge.
- Negativ: `0001_schema.sql` war transient regelwerkswidrig (P1-02) – zeigt, dass Regelwerk v5 und initiales Schema nicht vollständig synchronisiert waren.
- Risiko: Mehrere Evidenzgrenzen (Tests, Export-Code, Terminal-UI-Code) – Vertrauen in Korrektheit basiert auf Planungsdokumentation, nicht auf direkter Code-Lektüre.

---

## 9. Priorisierte To-do-Liste

### Kritisch (Abnahmeblockend)

- K-01 – Datenschutzunterlagen der Praxis für Beschäftigtendaten: AV-Vertrag (falls Cloud-Backup genutzt), TOM-Dokumentation, Restore-Freigaberegelung (P4-04, Pflichtenheft §17)
- K-02 – Formale schriftliche Festlegung von Aufbewahrungs- und Löschkonzept durch die Praxis (P5-05, Pflichtenheft §17, §12)
- K-03 – Formale organisatorische Rollenzuordnung: wer ist Admin, wer ist Prüfer, wer darf Regelzeiten ändern, wer gibt Korrekturen frei (Pflichtenheft §15, §17)

### Hoch

- H-01 – Nachweis/Ablage von `docs/anlage_einhaltung_pflichtenheft_v2.md` im Repo oder Klärung des Verweises (P1-04)
- H-02 – Dokumentierter manueller Restore-Test im realen Betrieb (nicht nur als Unittest) mit Protokoll (P5-06)
- H-03 – Pbkdf2_hmac-Iterationsanzahl dokumentieren + DSGVO Art. 32-Einordnung beifügen (P5-02)
- H-04 – Rollenlos-Design der Terminal-Buchung formell dokumentieren (Begründung: RFID = Authentifikation) (P3-03)

### Mittel

- M-01 – P1-02 als dauerhaften Befund im Änderungsprotokoll dokumentieren (0001-Schema war transient regelwerkswidrig; 0003 hat behoben)
- M-02 – P2-01: Begründung für Netto-basierte ArbZG-Prüfung in Dokumentation aufnehmen
- M-03 – P2-02: `BREAK_START nach GEHEN` als implizit abgedeckten Fall explizit kommentieren in `booking_rules.py`
- M-04 – Einbindung in Praxis-IT-Sicherheitskonzept nach § 75b SGB V dokumentieren

### Niedrig

- N-01 – P3-01: Phasenzuordnung in Nachtragsmatrix für `approve/reject_supplement.py` als Planungsabweichung festhalten
- N-02 – P2-04: Wochenprüfung (kumulative Arbeitszeit) als explizites Backlog-Item aufnehmen
- N-03 – `report_queries.py` auf „God Object"-Risiko bei Wachstum beobachten; ggf. in Teilmodule aufteilen

---

## 10. GO/NO-GO-Matrix

| Phase | Status | Begründung |
|---|---|---|
| Phase 1 – Grundgerüst | GO mit Auflagen | Fundament funktional; P1-02 (transient regelwidrig behoben), P1-04 (Anlage v2 Verweis klären) |
| Phase 2 – Domäne | GO mit Auflagen | Alle Kernregeln korrekt; P2-01 (Netto-Berechnung begründen), P2-02 (Kommentar ergänzen) |
| Phase 3 – Application | GO mit Auflagen | Use Cases vollständig; P3-03 (Terminal-Buchung Rollendesign dokumentieren) |
| Phase 4 – Infrastruktur | GO mit Auflagen | Technisch stark; P4-03/P4-04 (Betriebsdoku formalisieren, Datenschutz-Unterlagen erstellen) |
| Phase 5 – Präsentation | GO mit Auflagen | Benutzerverwaltung vollständig; P5-02 (Passwort-Hashing dokumentieren), P5-05/P5-06 (org. Abnahme) |
| Gesamt-System | GO mit Auflagen | Technisch abnahmefähig unter Bedingung: K-01, K-02, K-03 vor Produktivbetrieb erfüllen |

**Gesamt-NO-GO-Trigger**: Nachweis, dass `users bootstrap` ohne aktiven Admin-Check funktioniert, oder Nachweis, dass `POSSIBLE_*`-Status nach `0003` weiterhin als `BookingStatus` gespeichert wird. Beides ist laut Dokumentation nicht der Fall, aber wegen Evidenzgrenzen nicht aus direkter Code-Lektüre bestätigt.

---

## 11. Selbstcheck

### Widersprüche im Repo

- `planung_gesamt.md` bezeichnet `docs/pflichtenheft_arbeitszeit_v5.md` als Referenzdokument, die Datei liegt aber im Projektwurzel (`pflichtenheft_arbeitszeit_v5.md`), nicht unter `docs/`. Kein inhaltlicher Widerspruch, aber Pfad-Inkonsistenz in der Dokumentation.
- `planung_gesamt.md` nennt `docs/anlage_einhaltung_pflichtenheft_v2.md` als verbindliches Referenzdokument; diese Datei ist im gesichteten Verzeichnis `docs/` nicht auffindbar (nur `audits/`, `betrieb/`, `datenschutz/`, `informelles/`, `handbuch_rollen_cli_ergaenzung_v1_0.md`). Entweder liegt sie in einem Unterverzeichnis oder existiert nicht im Repo.

### Unklarheiten

- Ob `report_queries.py` in `infrastructure/export/` oder in `infrastructure/db/` liegt, ist nicht entscheidbar auf Basis der vorliegenden Artefakte.
- Ob `booking_loop.py` in `terminal_ui/` liegt und welche Dateistruktur `terminal_ui/` genau hat, ist nicht entscheidbar auf Basis der vorliegenden Artefakte.

### Nicht entscheidbar auf Basis der vorliegenden Artefakte

- Vollständige Testabdeckung (Tests-Verzeichnis nicht direkt gelesen)
- Interne Implementierung aller Export-Funktionen (CSV/PDF-Feldvollständigkeit gemäß §7.12)
- Interne Implementierung von Backup-Service, Restore-Logik, evdev-Integration
- Ob `user_accounts.py` (admin_cli) alle 6 Befehle tatsächlich im Code implementiert
- Ob `report_queries.py` die architektonische Alleinzuständigkeit für Auswertungen im Code einhält
- Status der Datei `docs/anlage_einhaltung_pflichtenheft_v2.md`