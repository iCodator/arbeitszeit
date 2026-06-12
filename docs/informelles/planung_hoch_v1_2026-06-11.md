# Planung: Abarbeitung „hoch"-Priorität
## Grundlage: `docs/claude_coding/claude_code_prompt_hoch_arbeitszeit_v1_2026-06-11_20-08.md`

**Datum:** 2026-06-11  

---

## 0. Ist-Stand vor Ausführung

Keine der geforderten Deliverables existiert:
- `docs/informelles/nachtragsmatrix_phasen_v1.md` — fehlt
- `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md` — fehlt
- `docs/informelles/abarbeitung_hoch_abschlussnotiz_v1.md` — fehlt

Existierende Phasenpläne als Primärquellen:
- `phase1_planung.md` bis `phase5_planung.md` — alle vorhanden ✓
- `planung_gesamt.md` — vorhanden ✓

Bestätigte Artefakte im Repo (aus Filesystem-Scan):
- 6 Migrationsdateien (0001–0006)
- 3 Scripts (backup.py, init_db.py, setup.py)
- Domain: enums, entities, errors, audit_events, services/, ports/
- Infrastructure: db/ (repositories/, unit_of_work.py), backup/, export/, hardware/, system_check.py, time_monitor.py
- Presentation: terminal_ui/, admin_cli/
- Tests: test_migrations.py, domain/, application/, integration/, e2e/

---

## Teil A — Nachtragsmatrix (Phasen 1–5)

### A.1 Primärquellen und Methodik

Jede Zeile der Matrix wird durch **mindestens eine Belegstelle** aus den Phasenplänen
gedeckt. Keine Eintragung ohne Referenz. Wenn Phase-Zugehörigkeit nur indirekt
ableitbar ist: Kennzeichnung mit „nicht entscheidbar auf Basis der vorliegenden Artefakte".

**Belegquellen (in Priorität):**
1. Explizite Phasenzuordnung in `phase?_planung.md`
2. Aussagen in `planung_gesamt.md` (Implementierungsreihenfolge, Nachtragsabschnitte)
3. Migrations-Kommentare (Dateinamen-Konvention NNNN_name.sql)
4. Test-Dateinamen und -Zuordnungen in Planungsdokumenten

### A.2 Artefakt-Auswahl

Aufzunehmen (explizit phasenbezogen in den Plänen genannt):

**Migrationen:**
- `0001_schema.sql` — Phase 1 (originär)
- `0002_seed_defaults.sql` — Phase 1 (originär)
- `0003_cleanup_booking_status.sql` — Phase 4, nachgezogen (Beleg: planung_gesamt.md Z.114)
- `0004_supplement_reject_fields_and_review_note.sql` — Phase 4 (Beleg: Z.115)
- `0005_time_bookings_device_event_id.sql` — Phase 4 (Beleg: Z.116)
- `0006_system_events_application_error.sql` — Phase 5 (Beleg: Z.117)

**Scripts:**
- `scripts/init_db.py` — Phase 1 (originär), Erweiterung Phase 4 (setup_vollstaendig)
- `scripts/setup.py` — Phase 4 zugeordnet (Beleg: planung_gesamt.md Z.101–102)
- `scripts/backup.py` — Phase 4, Schritt 7

**Domain-Module:**
- `domain/enums.py` — Phase 2
- `domain/entities.py` — Phase 2
- `domain/errors.py` — Phase 2
- `domain/audit_events.py` — Phase 2 (Kern), Phase 4/5+ (USER_ACCOUNT_CREATED/-DEACTIVATED, USER_ACCOUNT_REACTIVATED/-ROLE_CHANGED)
- `domain/services/booking_rules.py` — Phase 2; Änderung: ValidationResult entfernt (phase2_coding_aufgabe)
- `domain/services/compliance_checks.py` — Phase 2
- `domain/ports/repositories.py` — Phase 2; Ergänzungen Phase 4 (DeviceEventRepository)

**Application-Module:**
- `application/unit_of_work.py` — Phase 3; Ergänzung device_event_repo
- `application/commands.py` — Phase 3; Vorimplementierung Phase-4-Commands
- `application/results.py` — Phase 3; Vorimplementierung Phase-4-Results
- `application/use_cases/book_time.py` — Phase 3; Phase-4-Erweiterungen (Ruhezeit, Rollenzeitfenster)
- `application/use_cases/register_supplement.py` — Phase 3
- `application/use_cases/correct_booking.py` — Phase 3
- `application/use_cases/manage_work_schedule.py` — Phase 3
- `application/use_cases/approve_supplement.py` — Phase 3 vorimplementiert (Phase-4-Inhalt)
- `application/use_cases/reject_supplement.py` — Phase 3 vorimplementiert

**Infrastructure-Module:**
- `infrastructure/db/connection.py` — Phase 1
- `infrastructure/db/migrations.py` — Phase 1
- `infrastructure/db/unit_of_work.py` — Phase 4; Ergänzung device_event_repo
- `infrastructure/db/repositories/` (10 Repos) — Phase 4
- `infrastructure/db/repositories/device_event.py` — Phase 4 nachgezogen (2026-06-11)
- `infrastructure/backup/backup_service.py` — Phase 4; restore_exports Erweiterung (phase4_coding_aufgabe)
- `infrastructure/export/report_queries.py` — Phase 4
- `infrastructure/export/csv_exporter.py` — Phase 4
- `infrastructure/export/pdf_report_service.py` — Phase 4
- `infrastructure/hardware/evdev_reader.py` — Phase 4; rfid_timeout-Erweiterung
- `infrastructure/hardware/simulator.py` — Phase 4
- `infrastructure/hardware/ports.py` — Phase 4
- `infrastructure/hardware/uid_hash.py` — Phase 4
- `infrastructure/system_check.py` — Phase 4 (Schritt 9)
- `infrastructure/time_monitor.py` — Phase 5

**Presentation-Module:**
- `presentation/terminal_ui/booking_loop.py` — Phase 5; device_event_id-Erweiterung (2026-06-11)
- `presentation/terminal_ui/main.py` — Phase 5; _run_one_cycle-Extraktion (phase5_coding_aufgabe)
- `presentation/admin_cli/main.py` — Phase 5
- `presentation/admin_cli/employees.py` — Phase 5
- `presentation/admin_cli/user_accounts.py` — Phase 5 (users add/list/deactivate/reactivate/change-role/bootstrap)

**Testmodule:**
- `tests/test_migrations.py` — Phase 1 (6 originäre Tests), Phase 4 (+5), Phase 5 (+1)
- `tests/domain/test_entities.py` — Phase 2 (42 Tests)
- `tests/domain/test_booking_rules.py` — Phase 2 (10→14 Tests nach phase2_coding_aufgabe)
- `tests/domain/test_compliance_checks.py` — Phase 2
- `tests/domain/test_audit_events.py` — Phase 2 (neu, nicht im Originalplan)
- `tests/application/fakes.py` — Phase 3; Ergänzung FakeDeviceEventRepository
- `tests/application/test_*.py` — Phase 3 (109 Tests)
- `tests/application/test_fake_unit_of_work.py` — Phase 3 (phase3_coding_aufgabe)
- `tests/integration/test_repositories.py` — Phase 4
- `tests/integration/test_device_event_booking.py` — Phase 4 nachgezogen (2026-06-11)
- `tests/integration/test_user_accounts.py` — Phase 5
- `tests/e2e/test_booking_flow.py` — Phase 5 (10→12 Tests nach phase5_coding_aufgabe)
- `tests/e2e/test_supplement_flow.py` — Phase 5
- `tests/e2e/test_backup.py` — Phase 4 (19→22 Tests nach phase4_coding_aufgabe)

**Nicht aufgenommen (mit Begründung):**
- Einzelne `__init__.py` — keine fachliche Phasenzuordnung in den Plänen
- `tests/integration/test_init_db.py` — Phase 4+, aber keine explizite Phasenzuordnung in Planungsdoku
- `_helpers.py` — interne Hilfsdatei ohne eigene Phasenzuordnung

### A.3 Matrix-Schema

Spalten: Artefakt | Artefaktart | Historische Zielphase | Tatsächliche Einführungsphase | Spätere Änderungen | Änderungsart | Belegstellen | Kommentar

### A.4 Deliverable

**Datei:** `docs/informelles/nachtragsmatrix_phasen_v1.md`

Pflichtabschnitte:
1. Titel, Datum, Zweck
2. Methodik (Belegpflicht, Kennzeichnung Unentscheidbarkeit)
3. Die Matrix (ca. 40+ Zeilen)
4. „Explizit erkannte Phasenverschiebungen" (vorgezogen / nachgezogen / Doku-Korrekturen)
5. „Nicht entscheidbar auf Basis der vorliegenden Artefakte"
6. Selbstcheck-Protokoll (A7)

---

## Teil B — Formale Betriebsdokumentation

### B.1 Primärquellen

| Quelle | Relevante Abschnitte |
|---|---|
| `phase4_planung.md` | Schritt 7 (Backup), Schritt 8 (Export), Schritt 9 (Systemcheck), Betriebsentscheidungen |
| `phase5_planung.md` | Terminal-UI-Betrieb, Admin-CLI, Systemzeitprotokollierung |
| `planung_gesamt.md` | V5-/V2-Abgleich offene Punkte, Betriebsentscheidungen |
| `scripts/backup.py` | Backup-/NAS-Logik, Parameter |
| `scripts/setup.py` | Ersteinrichtung, Deployment-Keys |
| `scripts/init_db.py` | Datenbankinitialisierung, Setup-Check |
| `infrastructure/backup/backup_service.py` | restore_from(), Restore-Semantik |
| `infrastructure/system_check.py` | Systemcheck-Prüfbereiche |
| `infrastructure/time_monitor.py` | Schwellenwert, Protokollierung |
| `presentation/admin_cli/` | Befehle, Rollenprüfung |
| `presentation/terminal_ui/main.py` | Startablauf, Fehlerprotokollierung |

### B.2 Inhaltliche Abgrenzung

**Im Code technisch belegt:** Backup, Restore, Export, Systemcheck, Zeitmonitor,
Admin-CLI-Befehle, Terminal-UI-Startablauf, Rollenprüfung

**Als Betriebsregel im Repo beschrieben:** NAS als Spiegelziel (nicht Archiv),
Exportverzeichnis als ADMIN-lesbar, 5-Jahres-Aufbewahrungsfrist Exporte,
RESTORE_COMPLETED-Semantik

**Als organisatorische Auflage außerhalb des Codes:** Restore-Freigabe durch berechtigte
Person, Prüfintervalle, IT-Sicherheitsverantwortlichkeit, AV-Verträge Cloud-Backup

### B.3 Deliverable

**Datei:** `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md`

Mindeststruktur gemäß Prompt (Abschnitte 1–11 laut B2), inkl. Freigabefähigkeitsstatus (B5)

### B.4 Planungsdokument-Verweise (B6)

Nach Erstellung des Betriebsdokuments: kurze sachliche Verweise ergänzen in:
- `planung_gesamt.md` — im Abschnitt offene Punkte / Betriebsdokumentation
- `phase4_planung.md` — bei Schritt 7 (Backup) und Schritt 9 (Systemcheck)
- `phase5_planung.md` — bei Terminal-UI-Abschnitt

---

## Ausführungsreihenfolge

```
1. Phasenpläne 1–5 vollständig lesen (A1) — bereits weitgehend bekannt
2. nachtragsmatrix_phasen_v1.md erstellen (A2–A7)
3. Betriebsrelevante Quellen lesen (B1): phase4_planung, phase5_planung, Scripts
4. betriebsdokumentation_arbeitszeit_v1.md erstellen (B2–B5)
5. Planungsdokument-Verweise ergänzen (A6, B6)
6. abarbeitung_hoch_abschlussnotiz_v1.md erstellen
7. Tests laufen lassen (keine Codeänderungen erwartet)
8. Commit + Push
```

---

## Verbotene Abkürzungen (aus Prompt)

- Nachtragsmatrix nur aus Plantext kopieren ohne Abgleich mit Artefakten
- Phasenhistorie glätten (Nachträge als originär darstellen)
- Betriebsdokumentation ohne Repo-Belege
- Organisatorische Freigabe behaupten ohne Nachweis
- Evidenzlücken mit Plausibilität füllen

---

## Definition of Done (8 Kriterien aus Prompt)

1. ☐ Belegorientierte Nachtragsmatrix existiert
2. ☐ Historische Zielphase, tatsächliche Einführungsphase, spätere Änderungen pro Artefakt
3. ☐ Vorgezogen/nachgezogen/Doku-Korrekturen erkennbar
4. ☐ Eigenständige Betriebsdokumentation existiert
5. ☐ Klare Trennung Technik / Regel / Auflage / Unentscheidbarkeit
6. ☐ Planungsdokumente um kurze Verweise ergänzt
7. ☐ Abschlussnotiz mit Restpunkten und Evidenzgrenzen
8. ☐ Nichts als „geregelt" / „freigegeben" dargestellt ohne Repo-Beleg
