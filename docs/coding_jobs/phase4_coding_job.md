# Programmieraufgabe Phase 4 – arbeitszeit

## Quellenbasis

Diese Aufgabe basiert auf den Dateien `phase4_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

## Ziel

Implementiere **ausschließlich Phase 4** des Projekts `arbeitszeit`. Phase 4 umfasst die **Infrastruktur-Schicht**: echte SQLite-Repositories, echte `UnitOfWork`-Integration, ergänzende Migrationen, Export, Backup/Restore, Hardware-Anbindung, Systemcheck sowie Integrations- und E2E-nahe Tests. Diese Zieldefinition folgt aus `phase4_planung_konkret.md` und `planung_gesamt.md`.

Die Aufgabe ist erfolgreich abgeschlossen, wenn die bisher abstrakten oder per Fakes getesteten Fachabläufe gegen reale Persistenz und reale Infrastrukturdienste arbeiten, ohne bereits die Präsentationsschicht aus Phase 5 umzusetzen. Diese Phasengrenze wird in `phase4_planung_konkret.md` ausdrücklich gezogen.

## Strikte Grenzen

Arbeite streng innerhalb dieses Umfangs. **Nicht** Teil dieser Aufgabe sind insbesondere:

- das initiale Projekt- und Migrationsfundament aus Phase 1,
- die reine Domänenschicht aus Phase 2,
- die isolierte Use-Case-Orchestrierung mit Fakes aus Phase 3, soweit sie bereits existiert,
- Terminal-UI, Admin-CLI und betriebliche Orchestrierung aus Phase 5.

Diese Grenzen ergeben sich aus `phase4_planung_konkret.md` und `planung_gesamt.md`. Wenn Bedienoberfläche, Kommandozeilenworkflow oder vollständige Betriebsintegration nötig würden, stoppe an der Grenze der Infrastruktur-Schicht.

## Verbindlicher Lieferumfang

Erzeuge oder vervollständige mindestens die folgenden Bestandteile:

- `src/arbeitszeit/application/use_cases/approve_supplement.py`
- `src/arbeitszeit/application/use_cases/reject_supplement.py`
- Anpassungen an `src/arbeitszeit/application/use_cases/book_time.py` zur Ruhezeitintegration und vollständigen Rollenprüfung
- `migrations/0003_cleanup_booking_status.sql`
- `migrations/0004_supplement_reject_fields_and_review_note.sql`
- `migrations/0005_time_bookings_device_event_id.sql`
- `src/arbeitszeit/infrastructure/db/unit_of_work.py`
- `src/arbeitszeit/infrastructure/db/repositories/`
- `src/arbeitszeit/infrastructure/hardware/`
- `src/arbeitszeit/infrastructure/backup/`
- `src/arbeitszeit/infrastructure/export/report_queries.py`
- `src/arbeitszeit/infrastructure/export/csv_exporter.py`
- `src/arbeitszeit/infrastructure/export/pdf_report_service.py`
- `src/arbeitszeit/infrastructure/system_check.py`
- Integrations- und E2E-Tests unter `tests/integration/` und `tests/e2e/`

Quellen: `phase4_planung_konkret.md`, `planung_gesamt.md`.

## Aufgabenbeschreibung

### 1. Ergänzende Supplement-Use-Cases implementieren

Implementiere `ApproveSupplementUseCase` und `RejectSupplementUseCase` als echte fachliche Abläufe auf Basis der vorhandenen Application- und Repository-Verträge.

Für `ApproveSupplementUseCase` ist zwingend umzusetzen:
- Rollenprüfung auf `REVIEWER` oder `ADMIN`,
- Laden und Validieren des Supplements,
- Prüfen auf `PENDING`,
- Validierung des betroffenen Mitarbeiters,
- fachliche Freigabe des Supplements,
- Schließen des offenen `MANUAL_ENTRY_REVIEW`-Falls,
- Erzeugen einer echten `TimeBooking` mit vollständiger Statuslogik,
- Erzeugen neuer `ReviewCase`-Einträge pro `ComplianceFlag`,
- Commit und Audit-Eintrag.

Für `RejectSupplementUseCase` ist umzusetzen:
- Rollenprüfung auf aktiven `REVIEWER` oder `ADMIN`,
- Laden und Validieren des Supplements,
- Prüfen auf `PENDING`,
- fachliche Ablehnung via Repository,
- Schließen eines passenden `MANUAL_ENTRY_REVIEW`-Falls, falls `related_booking_id` existiert,
- Commit und Audit-Eintrag.

Wichtig: Eine reine `supplement_repo.approve()`-Operation ohne tatsächliche Buchungserzeugung ist fachlich unvollständig und unzulässig. Quellen: `phase4_planung_konkret.md`, `planung_gesamt.md`.

### 2. Ruhezeitprüfung operativ in `BookUseCase` integrieren

Erweitere `BookUseCase`, sodass die operative Ruhezeitprüfung mit Vortageskontext vollständig integriert wird.

Pflichtschritte:
- Vortagesbuchungen laden,
- letzten `GO`-Zeitpunkt des Vortags bestimmen,
- ersten `COME`-Zeitpunkt des projizierten Verlaufs bestimmen,
- `check_rest_period(last_go, first_come)` aufrufen,
- resultierende Prüffälle in Statusbewertung und `ReviewCase`-Erzeugung einbeziehen.

Diese Lücke wird in `phase4_planung_konkret.md` ausdrücklich als Pflichtschluss zu `Pflichtenheft v4` und `Regelwerk v4` beschrieben.

### 3. Rollenprüfung in alle schreibenden Use Cases vervollständigen

Sorge dafür, dass alle noch offenen schreibenden Use Cases die einheitliche Rollenprüfung verwenden.

Das betrifft insbesondere:
- `RegisterSupplementUseCase`
- `CorrectBookingUseCase`
- `ManageWorkScheduleUseCase`
- `ApproveSupplementUseCase`
- `RejectSupplementUseCase`

Die Prüfung muss Existenz, Aktivität und erlaubte Rolle einheitlich über `PermissionDeniedError` behandeln. Quellen: `phase4_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4`.

### 4. Migrationsstand auf finalen Phase-4-Schema-Stand bringen

Implementiere die maßgeblichen Phase-4-Migrationen:
- `0003_cleanup_booking_status.sql`
- `0004_supplement_reject_fields_and_review_note.sql`
- `0005_time_bookings_device_event_id.sql`

Inhaltlich müssen diese Migrationen laut `phase4_planung_konkret.md` und `planung_gesamt.md` Folgendes leisten:
- Bereinigung früherer `BookingStatus`-CHECK-Constraints,
- Ergänzung von `rejected_by_user_id` und `rejected_at` in `supplements`,
- Ergänzung eines `note`-Felds in `review_cases`,
- Ergänzung von `device_event_id` in `time_bookings`.

Wichtig: `device_event_id` wird damit schemafähig vorbereitet. Die vollständige produktive Verkettung über echte `device_events` bleibt laut `planung_gesamt.md` und `Anlage v2` dennoch offen und darf hier nicht überbehauptet werden.

### 5. Echte `SQLiteUnitOfWork` implementieren

Implementiere in `infrastructure/db/unit_of_work.py` die reale DB-gebundene `UnitOfWork`.

Pflicht ist:
- `BEGIN` beim Eintritt,
- `COMMIT` bei explizitem Commit,
- `ROLLBACK` bei offener Transaktion im Exit,
- commit-or-rollback-Sicherheitssemantik statt stiller Persistenz,
- Berücksichtigung des `audit_conn`-Musters.

Das `audit_conn`-Muster muss sicherstellen, dass Audit-Einträge Rollbacks der Haupttransaktion überleben können. Quellen: `phase4_planung_konkret.md`, `planung_gesamt.md`.

### 6. SQLite-Repositories implementieren

Implementiere unter `infrastructure/db/repositories/` die 10 echten Repository-Implementierungen gegen SQLite.

Pflichtanforderungen:
- ISO-8601-TEXT für Datetimes,
- Enums als `.value`,
- Booleans als INTEGER 0/1,
- ausschließlich parametrisierte Statements,
- `RETURNING id` nach INSERT,
- korrekte Scope-Priorität bei `WorkScheduleRepository.get_effective()`,
- strenges Verhalten bei `TimeBookingRepository.set_status()`,
- halb-offene Intervalle in Zeitbereichsqueries.

Die Repositories müssen die Fachverträge aus Phase 2/3 real auf die Datenbank abbilden, ohne Geschäftsregeln aus der Domäne in SQL zu verlagern. Quellen: `phase4_planung_konkret.md`, `planung_gesamt.md`.

### 7. Integrationsbasis und Repository-Tests aufbauen

Erstelle unter `tests/integration/` eine belastbare Integrationsbasis mit dateibasierter Test-SQLite.

Pflicht ist die Abdeckung von:
- Repositories,
- Repository-Roundtrips,
- `SQLiteUnitOfWork`,
- Scope- und Versionslogik,
- Status- und History-Updates,
- `audit_conn`-/Rollback-Verhalten.

Wichtig: Verwende **keine** reine In-Memory-SQLite, da laut `phase4_planung_konkret.md` und `planung_gesamt.md` für `audit_conn` mehrere Verbindungen auf dieselbe Datei nötig sind.

### 8. Hardware-Bausteine vorbereiten

Implementiere unter `infrastructure/hardware/` die evdev-nahe Leseschicht gegen Simulatoren und Adaptertests.

Bleibe strikt auf der Phase-4-Leseschicht. Implementiere **nicht** bereits die vollständige betriebliche Orchestrierung oder den realen produktiven `device_events`-Persistenzpfad. Diese Abgrenzung ist in `phase4_planung_konkret.md`, `planung_gesamt.md` und `Anlage v2` ausdrücklich festgehalten.

### 9. Backup/Restore implementieren

Implementiere unter `infrastructure/backup/` die SQLite-Backup- und NAS-Sync-Logik.

Pflichtpunkte:
- manuell auslösbares Backup-Skript,
- Audit-Logging für Backup-/Sync-/Restore-Ereignisse,
- `PRAGMA integrity_check` nach Restore,
- E2E-Restore-Tests,
- optionales Mitsichern von Exportdateien über `export_dir`.

Wichtig: Ein Rotationskonzept oder die vollständige Datenschutz-/Betriebsdokumentation sind **nicht** Teil dieser Coding-Aufgabe. Diese Grenzen stehen in `phase4_planung_konkret.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

### 10. Export- und Pflichtauswertungsschicht implementieren

Implementiere unter `infrastructure/export/`:
- `report_queries.py`
- `csv_exporter.py`
- `pdf_report_service.py`

Zentrales Prinzip: **Alle** Ausgabekanäle müssen auf derselben normierten Ableitungsschicht beruhen. Die CLI oder andere spätere Schichten dürfen keine eigene Ableitungslogik ergänzen. Diese Vorgabe ergibt sich aus `phase4_planung_konkret.md`, `planung_gesamt.md` und `Regelwerk v4`.

Pflichtumfang:
- normierte Queries für Buchungen, Korrekturen, Nachträge und Review Cases,
- CSV-Export detailliert und verdichtet,
- PDF-Berichte für Tages-, Wochen-, Monats- und Mitarbeiterberichte,
- Pflichtauswertungen für offene Buchungen, Korrekturen, Nachträge, Warn- und Review-Fälle.

### 11. Selbsttest/Systemcheck implementieren

Implementiere in `infrastructure/system_check.py` einen technischen Selbsttest.

Prüfbereiche:
- Konfigurationsprüfung,
- Geräteverfügbarkeit,
- NAS-Erreichbarkeit,
- Datenbankzugriff,
- Grundkonsistenz via `PRAGMA foreign_key_check`.

Die Ergebnisse sind als `SELFTEST_OK` oder `SELFTEST_FAIL` in `system_events` zu protokollieren. Quellen: `phase4_planung_konkret.md`, `planung_gesamt.md`.

## Akzeptanzkriterien

Die Aufgabe ist nur dann erfüllt, wenn alle folgenden Kriterien erfüllt sind:

- Ergänzende Supplement-Use-Cases sind fachlich korrekt implementiert.
- Die Ruhezeitprüfung ist operativ in reale Buchungsabläufe integriert.
- Rollenprüfung ist in allen schreibenden Use Cases konsistent umgesetzt.
- Das reale Schema entspricht dem finalen Phase-4-Migrationsstand.
- `SQLiteUnitOfWork` und echte Repositories arbeiten korrekt zusammen.
- Backup/Restore, Export, Pflichtauswertungen und Systemcheck sind technisch funktionsfähig und testgestützt.
- Die zentrale Ableitungsschicht (`report_queries.py`) ist die einzige fachliche Wahrheitsquelle für Ausgaben.
- Die Integrations- und E2E-Tests decken die kritischen Infrastrukturpfade nachvollziehbar ab.

Quellen: `phase4_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4`.

## Arbeitsweise

Arbeite akribisch, konservativ und selbstkritisch.

- Verwechsle nicht „schemafähig vorbereitet“ mit „betrieblich vollständig geschlossen“.
- Behaupte keine vollständige produktive `device_events`-Verkettung.
- Verlagere keine Fachregeln aus Domäne oder Use Cases in ad-hoc-SQL.
- Ersetze keine organisatorischen Nachweise durch Codebehauptungen.

Diese Leitplanken folgen aus `phase4_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

## Explizite Nicht-Ziele

Folgende Dinge dürfen **nicht** umgesetzt werden:

- Terminal-UI und Admin-CLI,
- vollständige betriebliche Orchestrierung der Hardware-Schicht,
- vollständige produktive `device_events`-Kette, soweit sie laut Plan offen bleibt,
- spätere Systemzeitüberwachung über `time_monitor.py`,
- organisatorische Nachweise wie Testmatrix, AV-Vertrag, IT-Sicherheitskonzept oder Praxisfreigaben.

Quellen: `phase4_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4`, `Anlage v2`.

## Ergebnisformat

Liefere am Ende ausschließlich den Phase-4-Code für reale Infrastruktur, Migrationen, Integrations-/E2E-nahe Tests und die ergänzten Use Cases. Führe **keine** Phase-5-Arbeiten aus und dokumentiere sauber, wo die Phase-4-Grenze bewusst eingehalten wurde. Grundlage: `phase4_planung_konkret.md`, `planung_gesamt.md`.
