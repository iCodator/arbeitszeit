# Audit Phase 4 – Infrastruktur

Kurze Vorabantwort: **Phase 4 ist fachlich weitgehend vollständig umgesetzt und im Kern abgeschlossen**, aber nicht in jedem Detail streng planidentisch dokumentiert. Die größten Befunde betreffen keine offensichtlichen Implementierungslücken im Kernumfang, sondern **Pfad-/Dateinamensinkonsistenzen**, **spätere Plananpassungen**, **vor- bzw. nachgezogene Inhalte** und einzelne Punkte mit **Klärungsbedarf** rund um die formale Phasenzuordnung.[file:2][file:6][file:8]

## Sollbild Phase 4

Laut `phase4_planung.md` und `planung_gesamt.md` umfasst Phase 4 die Infrastruktur um die bereits vorhandene Domain- und Application-Schicht: Migrationen `0003` bis `0005`, das reale SQLite-Unit-of-Work, zehn Repository-Implementierungen, Hardware-Adapter, Backup, Export, Systemcheck sowie die zugehörigen Integrations- und E2E-Tests. Zusätzlich werden in Phase 4 die bereits in Phase 3 vorimplementierten Use Cases `ApproveSupplementUseCase` und `RejectSupplementUseCase` fachlich als Infrastruktur-abhängig vervollständigt, insbesondere hinsichtlich Migrationen, Rollenkonzept, Ruhezeitprüfung und vollständiger Persistenzkette.[file:2][file:6]

Zum Sollbild gehört außerdem eine Reihe expliziter Architekturentscheidungen: ISO-8601-TEXT in SQLite, Enum- und Bool-Mapping, ausschließlich parametrisierte SQL-Statements, `set_status()` mit atomischem History-Seiteneffekt, versioniertes `SystemConfigRepository`, EMPLOYEE-vor-GLOBAL bei Regelarbeitszeiten, `audit_conn` für Audit-Logging außerhalb des Haupt-Transaktionsrahmens sowie `report_queries.py` als alleinige Datenquelle für Exporte und Pflichtauswertungen. `system_check.py` ist laut aktualisiertem Plan **bereits Phase 4**, während `0006_system_events_application_error.sql` und die Erweiterung des `system_events`-Schemas zu Phase 5 gehören.[file:2][file:6]

## Istbild der Codebasis

Die exportierte Codebasis enthält die gesamte für Phase 4 erwartete Infrastrukturstruktur unter `src/arbeitszeit/infrastructure/`: `db/`, `db/repositories/`, `hardware/`, `backup/`, `export/`, `system_check.py` und `time_monitor.py`. Vorhanden sind außerdem die zugehörigen Tests unter `tests/integration/` und `tests/e2e/`, darunter `test_repositories.py`, `test_repositories_roundtrip.py`, `test_unit_of_work.py`, `test_hardware_evdev.py`, `test_hardware_simulator.py`, `test_export.py`, `test_csv_export.py`, `test_pdf.py`, `test_system_check.py`, `test_time_monitor.py`, `test_backup.py`, `test_booking_flow.py` und `test_supplement_flow.py`.[file:8]

Der Export zeigt zugleich, dass die **realen** Dateinamen teils von den im Prompt genannten Schreibweisen abweichen: vorhanden sind `admin_cli`, `evdev_reader.py`, `uid_hash.py`, `backup_service.py`, `report_queries.py`, `pdf_report_service.py`, `system_check.py` und `time_monitor.py`; nicht vorhanden sind dagegen die normalisierten Promptformen `admincli`, `evdevreader.py`, `uidhash.py`, `backupservice.py`, `reportqueries.py`, `pdfreportservice.py`, `systemcheck.py` und `timemonitor.py`. Maßgeblich für das Audit ist daher die reale Codebasis in `arbeitszeit.md`, nicht die verkürzte oder historisierte Benennung des Prompts.[file:2][file:8]

## Soll-/Ist-Abgleich je Prüffeld

### 1. Use-Case-Nachrüstungen Phase 4

`ApproveSupplementUseCase` und `RejectSupplementUseCase` sind im Export vorhanden, obwohl sie laut historischer Phase-3-Abgrenzung ursprünglich vorgezogene Inhalte waren. Für Phase 4 ist das konsistent, weil `phase4_planung.md` diese Use Cases als bereits vorhanden und fachlich in den Infrastrukturkontext integriert beschreibt; ein Mangel liegt hier nicht vor, aber die historische Phasenabgrenzung muss sauber erklärt bleiben.[file:2][file:6][file:8]

Die Rollenprüfung in schreibenden Use Cases sowie die Ruhezeitprüfung in `BookUseCase` werden in `phase4_planung.md` als Schritt 1b/1c eingeordnet, gleichzeitig aber bereits im realen Stand als vorhanden beschrieben. Das ist keine Implementierungslücke, sondern eine **nachträgliche Plananpassung** bzw. ein historischer Zwischenstand, der ohne erläuternde Notiz leicht wie ein Widerspruch wirkt.[file:2][file:6][file:8]

### 2. Migrationen und Schemafortschreibung

Die reale Codebasis enthält die Migrationen `0003_cleanup_booking_status.sql`, `0004_supplement_reject_fields_and_review_note.sql`, `0005_time_bookings_device_event_id.sql` und `0006_system_events_application_error.sql`. Laut Gesamtplanung gehören `0003` bis `0005` zu Phase 4, während `0006` erst Phase 5 zugeordnet ist; damit ist `0006` im heutigen Stand zwar vorhanden, aber **nicht originärer Phase-4-Lieferumfang**.[file:6][file:8]

Zugleich sind mehrere Prompt-Pfade formal falsch: tatsächlich vorhanden sind `0003_cleanup_booking_status.sql`, `0005_time_bookings_device_event_id.sql` und `0006_system_events_application_error.sql`, nicht `0003_cleanup_bookingstatus.sql`, `0005_timebookings_deviceeventid.sql` oder `0006_systemevents_applicationerror.sql`. Das ist ein reiner Dokumentations- bzw. Referenzfehler, aber für Audits relevant, weil falsche Dateinamen leicht Scheinkonflikte erzeugen.[file:8]

### 3. SQLite Unit of Work

`phase4_planung.md` beschreibt `SQLiteUnitOfWork` mit `BEGIN`, manuellem `COMMIT/ROLLBACK`, automatischem Rollback bei offener Transaktion und einem getrennten `audit_conn`-Muster im Autocommit-Modus. Der Export bestätigt `src/arbeitszeit/infrastructure/db/unit_of_work.py` und die zugehörigen Integrations-Tests `tests/integration/test_unit_of_work.py`, womit dieser Baustein im vorgesehenen Dateischnitt vorhanden ist.[file:2][file:8]

Die Planung markiert ausdrücklich, dass das commit-or-rollback-Verhalten gegenüber einer älteren Planformulierung verschärft wurde und dass `audit_conn` nicht vom UoW gesteuert wird. Das ist kein Mangel, sondern eine **bewusste nachträgliche Plananpassung**, die architektonisch sauber dokumentiert ist; offener bleibt nur, dass ältere Plantexte ohne diese Ergänzung missverstanden werden könnten.[file:2][file:6]

### 4. Repository-Implementierungen

Die zehn Repository-Dateien unter `src/arbeitszeit/infrastructure/db/repositories/` sind im Export vollständig vorhanden. `phase4_planung.md` beschreibt dafür konkret `_helpers.py`, ISO-8601-Parsen, Enum-/Bool-Mapping, atomisches `set_status()`, Scope-Priorität in `WorkScheduleRepository`, versioniertes `SystemConfigRepository` ohne UPDATE und eine dateibasierte SQLite-Testbasis; der Export bestätigt die zugehörigen Modulpfade und Integrations-Tests.[file:2][file:8]

Wesentliche Abweichungen sind hier vor allem dokumentarisch: `SystemConfigRepository.set_current()` wird im Plan zutreffend als fertiges Infrastrukturstück beschrieben, zugleich aber mit dem klaren Hinweis, dass die **operative Nutzung** erst in Phase 5 über Admin-Funktionen erfolgt. Das ist wichtig, weil „Repository implementiert" sonst fälschlich als „vollständig fachlich freigeschaltete Konfigurationsfunktion" gelesen werden könnte.[file:2][file:6]

### 5. Hardware-Schicht

Die reale Hardware-Schicht ist unter `src/arbeitszeit/infrastructure/hardware/` vorhanden mit `ports.py`, `evdev_reader.py`, `simulator.py` und `uid_hash.py`. `phase4_planung.md` dokumentiert zudem die fachlich wichtige Trennung zwischen RFID-Zeichenmapping in `map_rfid_key()` und Buchungsart-Mapping über `_NUMPAD_TO_BOOKING_TYPE`, was einen zuvor missverständlichen Plantext korrigiert.[file:2][file:8]

Ein echter Implementierungsmangel ist aus der Referenzlage nicht belegbar. Klar zu kennzeichnen ist aber, dass Schritt 6 **nur die Leseschicht** liefert und noch keine vollständige betriebliche Ende-zu-Ende-Kette für `device_events`; diese operative Verkettung ist bewusst in spätere Betriebsschichten ausgelagert und deshalb als Abgrenzung, nicht als Lücke, zu bewerten.[file:2][file:6]

### 6. Backup-Schicht

`src/arbeitszeit/infrastructure/backup/backup_service.py` ist im Export vorhanden; `phase4_planung.md` beschreibt `SQLiteBackupService` mit lokalem Backup, NAS-Sync, Restore, Audit-Logging, `integrity_check` und 19 E2E-Tests in `tests/e2e/test_backup.py`. Besonders wichtig ist der explizite Nachtrag, dass Exportdateien inzwischen in das Backup einbezogen sind und `scripts/backup.py` dafür einen `--export-dir`-Parameter erhalten hat.[file:2][file:6][file:8]

Hier bleibt vor allem **Betriebsdokumentationsbedarf**: `rsync --archive --delete` ist für ein Spiegelziel konsistent, birgt aber Archivierungsrisiko, wenn der NAS als Langzeitarchiv statt nur als Mirror verstanden wird. Laut Planung ist das kein Codefehler, sondern ein Punkt, der in der Betriebs- und Restore-Dokumentation eindeutig festgelegt werden muss.[file:2][file:6]

### 7. Export-Schicht

Die Exportmodule `report_queries.py`, `csv_exporter.py` und `pdf_report_service.py` sind real vorhanden. Planung und Gesamtplan beschreiben sie als umgesetzt, testabgedeckt und architektonisch zentral, wobei `report_queries.py` die alleinige fachliche Wahrheitsquelle für CSV, PDF und spätere UI-Auswertungen sein muss; diese Struktur ist im Export konsistent abgebildet.[file:2][file:6][file:8]

Auch hier fallen eher Terminologie- und Pfadthemen auf als Code-Lücken: Die Promptformen `reportqueries.py` und `pdfreportservice.py` sind falsch, korrekt sind `report_queries.py` und `pdf_report_service.py`. Zudem ist `list_open_review_cases_in_period(...)` in der Phase-4-Planung explizit vorhanden, obwohl ältere Texte teils nur `list_open_review_cases()` nannten; das ist als Planfortschreibung, nicht als Mangel, zu werten.[file:2][file:6][file:8]

### 8. Systemcheck und Zeitmonitor

`system_check.py` ist laut aktualisierter Phase-4-Planung bereits in Phase 4 fertiggestellt und mit 17 Integrationstests abgedeckt. Der Export bestätigt `src/arbeitszeit/infrastructure/system_check.py` sowie `tests/integration/test_system_check.py`; außerdem zeigen die Testausschnitte aus `arbeitszeit.md`, dass `SELFTEST_OK` und `SELFTEST_FAIL` tatsächlich das relevante `system_events`-Vokabular sind.[file:2][file:8]

`time_monitor.py` ist ebenfalls im Export vorhanden und `tests/integration/test_time_monitor.py` existiert. Gleichzeitig beschreibt `planung_gesamt.md` den V3-Punkt „Systemzeitprotokollierung“ an einer Stelle noch als spätestens Phase 5 bzw. ergänzenden Schritt, während `arbeitszeit.md` bereits konkrete Integrationstests für `SystemTimeMonitor` mit `TIME_JUMP_DETECTED` zeigt; das ist eine **nachträgliche Plananpassung** bzw. ein dokumentierter Vorzug des heutigen Stands, aber kein Hinweis auf einen Mangel.[file:6][file:8]

### 9. Testabdeckung Phase 4

Die für Phase 4 typischen Integrations- und E2E-Tests sind in der Codebasis vorhanden. `phase4_planung.md` nennt für die Infrastrukturkernschritte 10 UoW-Tests, Repository- und Roundtrip-Tests, 7 EVDEV-Tests, 14 Simulator-Tests, 18 Export-Tests, 15 CSV-Tests, 20 PDF-Tests, 17 Systemcheck-Tests und 19 Backup-E2E-Tests; der Export bestätigt die entsprechenden Dateimodule.[file:2][file:8]

Formal inkonsistent ist nur ein Teil der Dateireferenzen im Prompt: korrekt heißen die Dateien `test_system_check.py` und `test_time_monitor.py`, nicht `test_systemcheck.py` oder `test_timemonitor.py`. Inhaltlich ist die Testbasis eher **weiter** als der historische Phase-4-Plan, nicht schwächer.[file:2][file:8]

## 1. Förmliches Review-Protokoll

| Befund | Risiko | Empfehlung | betroffene Datei(en) | Kategorie | Priorität |
|---|---|---|---|---|---|
| Phase 4 ist im Kern fachlich vollständig umgesetzt: Infrastrukturpakete, zentrale Repositorys, Unit of Work, Hardware-, Backup-, Export- und Systemcheck-Module sind im Export vorhanden. [file:2][file:6][file:8] | Niedrig. [file:2][file:6] | Als abgeschlossenen Kernbestand festhalten. [file:2][file:6] | `src/arbeitszeit/infrastructure/**`, `tests/integration/**`, `tests/e2e/test_backup.py` [file:8] | kein Mangel | niedrig |
| `0006_system_events_application_error.sql` ist in der aktuellen Codebasis vorhanden, gehört laut Gesamtplanung aber zu Phase 5, nicht originär zu Phase 4. [file:6][file:8] | Mittel; falsche Phasenzuordnung kann Review- und Abnahmefehler erzeugen. [file:6] | In Audit und Planung klar als späteren Zusatz kennzeichnen. [file:6][file:8] | `migrations/0006_system_events_application_error.sql`, `tests/test_migrations.py` [file:8] | vorgezogene/spätere Erweiterung | hoch |
| Mehrere im Prompt genannte Pfade und Dateinamen stimmen nicht mit der realen Codebasis überein, etwa `admincli`, `evdevreader.py`, `uidhash.py`, `backupservice.py`, `reportqueries.py`, `pdfreportservice.py`, `systemcheck.py`, `timemonitor.py`. [file:8] | Hoch; falsche Pfade verfälschen jede Folgeprüfung. [file:8] | Alle Audit- und Planvorlagen auf reale Pfade der Exportbasis umstellen. [file:8] | mehrere Module in `presentation/`, `infrastructure/`, `tests/integration/` [file:8] | reine Dokumentationsungenauigkeit | kritisch |
| Die Prompt-Migrationsnamen `0003_cleanup_bookingstatus.sql`, `0005_timebookings_deviceeventid.sql`, `0006_systemevents_applicationerror.sql` sind formal falsch; real vorhanden sind die Unterstrichvarianten mit vollständigen Wörtern. [file:8] | Mittel. [file:8] | Nur reale Dateinamen verwenden; historische Alias nur ergänzend nennen. [file:8] | `migrations/0003_cleanup_booking_status.sql`, `0005_time_bookings_device_event_id.sql`, `0006_system_events_application_error.sql` [file:8] | reine Dokumentationsungenauigkeit | hoch |
| Rollenprüfung in schreibenden Use Cases und Ruhezeitprüfung im `BookUseCase` erscheinen in den Plantexten teils als Phase-4-Nachrüstung, sind im realen Stand aber bereits vorhanden und teils schon in Phase 3 vorgezogen dokumentiert. [file:2][file:6][file:8] | Mittel; historischer Soll-/Ist-Abgleich wird unscharf. [file:2][file:6] | Als nachträgliche Plananpassung bzw. vorgezogenen Bestand explizit markieren. [file:2][file:6] | `src/arbeitszeit/application/use_cases/book_time.py`, `approve_supplement.py`, `reject_supplement.py` [file:8] | nachträgliche Plananpassung | mittel |
| `SQLiteUnitOfWork` mit commit-or-rollback und `audit_conn` ist konsistent dokumentiert, weicht aber bewusst von älteren, vereinfachten Planformulierungen ab. [file:2][file:6] | Mittel; ohne Kontext droht Fehlinterpretation der Transaktionssemantik. [file:2][file:6] | Die verschärfte Endfassung als maßgeblich deklarieren; ältere Beschreibung nur historisch aufführen. [file:2][file:6] | `src/arbeitszeit/infrastructure/db/unit_of_work.py`, `tests/integration/test_unit_of_work.py` [file:8] | nachträgliche Plananpassung | hoch |
| Backup über `rsync --archive --delete` ist technisch konsistent, erfordert aber klare Betriebsdefinition, ob NAS Spiegelziel oder Langzeitarchiv ist. [file:2][file:6] | Mittel bis hoch; Fehlverständnisse gefährden Archivierungsstrategie. [file:2][file:6] | Betriebsdokumentation um eindeutige Mirror-vs.-Archiv-Regel ergänzen. [file:2][file:6] | `src/arbeitszeit/infrastructure/backup/backup_service.py`, `scripts/backup.py` [file:8] | Ambiguität/Klärungsbedarf | hoch |
| Exportdateien sind laut aktualisierter Planung inzwischen im Backup enthalten; das wird als erledigter Nachtrag beschrieben, nicht als offene Lücke. [file:2][file:6] | Niedrig. [file:2][file:6] | Als geschlossenen Nachtrag dokumentieren, nicht erneut als offen listen. [file:2][file:6] | `src/arbeitszeit/infrastructure/backup/backup_service.py`, `scripts/backup.py`, `tests/e2e/test_backup.py` [file:8] | nachträgliche Plananpassung | niedrig |
| `system_check.py` ist plan- und codekonform Phase 4; `time_monitor.py` ist im Code bereits vorhanden, obwohl ältere Gesamtplanstellen Systemzeitprotokollierung teilweise noch später verorteten. [file:2][file:6][file:8] | Mittel; Phasenzuordnung der Betriebsfunktionen kann missverstanden werden. [file:2][file:6] | `planung_gesamt.md` um klaren Nachtrag ergänzen, dass `SystemTimeMonitor` im heutigen Stand bereits real existiert. [file:6][file:8] | `src/arbeitszeit/infrastructure/system_check.py`, `time_monitor.py`, `tests/integration/test_system_check.py`, `test_time_monitor.py` [file:8] | nachträgliche Plananpassung | mittel |
| Für Repositorys, Exporte, Hardware und Systemcheck sind im Sollbild keine harten Kernlücken belegbar; die Codebasis wirkt eher weiter als der historische Zwischenstand. [file:2][file:6][file:8] | Niedrig. [file:2][file:6] | Keine Rückbauten; nur phasenscharf dokumentieren. [file:2][file:6] | mehrere Infrastrukturmodule [file:8] | kein Mangel | niedrig |

## 2. Pfad- und Dateinamenprüfung

| Referenz im Plan/Prompt | tatsächlicher korrekter Pfad/Dateiname | Bewertung | Korrekturhinweis |
|---|---|---|---|
| `src/arbeitszeit/application/` | `src/arbeitszeit/application/` [file:8] | korrekt | keine Korrektur |
| `src/arbeitszeit/application/use_cases/` | `src/arbeitszeit/application/use_cases/` [file:8] | korrekt | keine Korrektur |
| `src/arbeitszeit/infrastructure/db/` | `src/arbeitszeit/infrastructure/db/` [file:8] | korrekt | keine Korrektur |
| `src/arbeitszeit/infrastructure/db/repositories/` | `src/arbeitszeit/infrastructure/db/repositories/` [file:8] | korrekt | keine Korrektur |
| `src/arbeitszeit/infrastructure/hardware/` | `src/arbeitszeit/infrastructure/hardware/` [file:8] | korrekt | keine Korrektur |
| `src/arbeitszeit/infrastructure/backup/` | `src/arbeitszeit/infrastructure/backup/` [file:8] | korrekt | keine Korrektur |
| `src/arbeitszeit/infrastructure/export/` | `src/arbeitszeit/infrastructure/export/` [file:8] | korrekt | keine Korrektur |
| `src/arbeitszeit/presentation/admincli/` | `src/arbeitszeit/presentation/admin_cli/` [file:8] | falsch im Prompt | Unterstrich verwenden; reale Codebasis ist `admin_cli` |
| `migrations/0001_schema.sql` | `migrations/0001_schema.sql` [file:8] | korrekt | keine Korrektur |
| `migrations/0002_seed_defaults.sql` | `migrations/0002_seed_defaults.sql` [file:8] | korrekt | keine Korrektur |
| `migrations/0003_cleanup_bookingstatus.sql` | `migrations/0003_cleanup_booking_status.sql` [file:8] | falsch im Prompt | `_booking_status` statt `bookingstatus` |
| `migrations/0004_supplement_reject_fields_and_review_note.sql` | `migrations/0004_supplement_reject_fields_and_review_note.sql` [file:8] | korrekt | keine Korrektur |
| `migrations/0005_timebookings_deviceeventid.sql` | `migrations/0005_time_bookings_device_event_id.sql` [file:8] | falsch im Prompt | vollständige Unterstrichschreibweise verwenden |
| `migrations/0006_systemevents_applicationerror.sql` | `migrations/0006_system_events_application_error.sql` [file:8] | falsch im Prompt | vollständige Unterstrichschreibweise verwenden |
| `tests/test_migrations.py` | `tests/test_migrations.py` [file:8] | korrekt | keine Korrektur |
| `tests/application/test_book_time.py` | `tests/application/test_book_time.py` [file:8] | korrekt | keine Korrektur |
| `tests/application/test_register_supplement.py` | `tests/application/test_register_supplement.py` [file:8] | korrekt | keine Korrektur |
| `tests/application/test_correct_booking.py` | `tests/application/test_correct_booking.py` [file:8] | korrekt | keine Korrektur |
| `tests/application/test_manage_work_schedule.py` | `tests/application/test_manage_work_schedule.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_repositories.py` | `tests/integration/test_repositories.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_repositories_roundtrip.py` | `tests/integration/test_repositories_roundtrip.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_unit_of_work.py` | `tests/integration/test_unit_of_work.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_hardware_evdev.py` | `tests/integration/test_hardware_evdev.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_hardware_simulator.py` | `tests/integration/test_hardware_simulator.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_export.py` | `tests/integration/test_export.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_csv_export.py` | `tests/integration/test_csv_export.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_pdf.py` | `tests/integration/test_pdf.py` [file:8] | korrekt | keine Korrektur |
| `tests/integration/test_systemcheck.py` | `tests/integration/test_system_check.py` [file:8] | falsch im Prompt | reale Datei hat Unterstrich: `system_check` |
| `tests/integration/test_timemonitor.py` | `tests/integration/test_time_monitor.py` [file:8] | falsch im Prompt | reale Datei hat Unterstrich: `time_monitor` |
| `tests/e2e/test_backup.py` | `tests/e2e/test_backup.py` [file:8] | korrekt | keine Korrektur |
| `tests/e2e/test_booking_flow.py` | `tests/e2e/test_booking_flow.py` [file:8] | korrekt | keine Korrektur |
| `tests/e2e/test_supplement_flow.py` | `tests/e2e/test_supplement_flow.py` [file:8] | korrekt | keine Korrektur |
| `evdevreader.py` | `evdev_reader.py` [file:8] | falsch im Prompt | reale Snake-Case-Schreibweise nutzen |
| `uidhash.py` | `uid_hash.py` [file:8] | falsch im Prompt | reale Snake-Case-Schreibweise nutzen |
| `backupservice.py` | `backup_service.py` [file:8] | falsch im Prompt | reale Snake-Case-Schreibweise nutzen |
| `reportqueries.py` | `report_queries.py` [file:8] | falsch im Prompt | reale Snake-Case-Schreibweise nutzen |
| `pdfreportservice.py` | `pdf_report_service.py` [file:8] | falsch im Prompt | reale Snake-Case-Schreibweise nutzen |
| `systemcheck.py` | `system_check.py` [file:8] | falsch im Prompt | reale Snake-Case-Schreibweise nutzen |
| `timemonitor.py` | `time_monitor.py` [file:8] | falsch im Prompt | reale Snake-Case-Schreibweise nutzen |

## 3. Priorisierte To-do-Liste

- **Kritisch:** Alle Audit- und Planvorlagen auf reale Pfade und Dateinamen der aktuellen Codebasis korrigieren; betroffen sind insbesondere `admin_cli`, `evdev_reader.py`, `uid_hash.py`, `backup_service.py`, `report_queries.py`, `pdf_report_service.py`, `system_check.py`, `time_monitor.py`, `test_system_check.py`, `test_time_monitor.py`, `0003_cleanup_booking_status.sql`, `0005_time_bookings_device_event_id.sql`, `0006_system_events_application_error.sql`; Zielzustand: keine Folgeprüfung referenziert mehr nicht existente Pfade.[file:8]
- **Hoch:** In `planung_gesamt.md` Phase-4/Phase-5-Abgrenzung für `0006_system_events_application_error.sql` und `time_monitor.py` explizit nachschärfen; Zielzustand: klar dokumentiert, was originärer Phase-4-Umfang ist und was später hinzugekommen ist.[file:6][file:8]
- **Hoch:** In `planung_gesamt.md` und `phase4_planung.md` historische Zwischenstände zu Rollenprüfung, Ruhezeitprüfung und `ApproveSupplementUseCase`/`RejectSupplementUseCase` mit einem klaren Nachtragsvermerk versehen; Zielzustand: kein scheinbarer Widerspruch mehr zwischen „Phase 3 vorimplementiert“ und „Phase 4 vervollständigt“. [file:2][file:6]
- **Hoch:** Betriebsdokumentation für Backup/NAS präzisieren; Zielzustand: eindeutig festgelegt, ob `sync_to_nas()` als Mirror oder als Archivpfad zu verstehen ist und wie Restore plus Exportdateien organisatorisch zu behandeln sind.[file:2][file:6]
- **Mittel:** Testübersichten phasenscharf markieren; Zielzustand: Integrations- und E2E-Tests sind sauber zwischen originärem Phase-4-Kern und späteren Ergänzungen getrennt nachvollziehbar.[file:2][file:6][file:8]

## 4. Förmliches Umsetzungsprotokoll

### Arbeitspaket 1 — Pfad- und Dateireferenzen bereinigen

- **Priorität:** kritisch.[file:8]
- **Umfang:** Auditvorlagen, Planungsdokumente, interne Referenztabellen.[file:2][file:6]
- **Maßnahme:** Alle nicht realen Prompt- und Aliaspfade durch die reale Export-Schreibweise ersetzen; historische Namensformen nur ergänzend in Klammern nennen.[file:8]
- **Akzeptanzkriterien:** Jeder im Dokument genannte Pfad ist 1:1 im Verzeichnisbaum von `arbeitszeit.md` auffindbar.[file:8]
- **Erforderliche Testfälle:** manueller Abgleich gegen den Verzeichnisbaum in `arbeitszeit.md`.[file:8]

### Arbeitspaket 2 — Phasenabgrenzung 4 vs. 5 schärfen

- **Priorität:** hoch.[file:6][file:8]
- **Umfang:** `planung_gesamt.md`, optional Querhinweise in `phase4_planung.md`.[file:2][file:6]
- **Maßnahme:** `0006_system_events_application_error.sql`, `time_monitor.py` und zugehörige Tests explizit als späteren oder vorgezogenen Umfang kennzeichnen, je nach gewünschter Historisierung.[file:6][file:8]
- **Akzeptanzkriterien:** Ein Leser kann ohne Zusatzwissen erkennen, welche Teile originär Phase 4 waren und welche erst im heutigen Stand darüber hinausgehen.[file:6][file:8]
- **Erforderliche Testfälle:** Dokumentationsprüfung gegen `arbeitszeit.md`; kein Code-Test erforderlich.[file:8]

### Arbeitspaket 3 — Historische Plananpassungen kenntlich machen

- **Priorität:** hoch.[file:2][file:6]
- **Umfang:** `planung_gesamt.md`, `phase4_planung.md`.[file:2][file:6]
- **Maßnahme:** Rollenprüfung, Ruhezeitprüfung, vorimplementierte `ApproveSupplementUseCase`/`RejectSupplementUseCase` und verschärfte UoW-Semantik als nachträglich konkretisierte Endfassung markieren.[file:2][file:6]
- **Akzeptanzkriterien:** Keine Passage erweckt mehr den Eindruck, der Code weiche widersprüchlich vom Plan ab, wenn tatsächlich nur der Plan fortgeschrieben wurde.[file:2][file:6]
- **Erforderliche Testfälle:** Querabgleich mit `arbeitszeit.md` und den genannten Testmodulen.[file:2][file:8]

### Arbeitspaket 4 — Betriebsdokumentation Backup/Restore konkretisieren

- **Priorität:** hoch.[file:2][file:6]
- **Umfang:** Betriebs- oder Administrationsdokumentation, ggf. ergänzende Hinweise bei `scripts/backup.py`.[file:2][file:8]
- **Maßnahme:** Mirror-vs.-Archiv-Entscheidung für NAS schriftlich festlegen, Restore-Verhalten für Exportdateien explizit beschreiben, organisatorische Restore-Schritte dokumentieren.[file:2][file:6]
- **Akzeptanzkriterien:** Es ist eindeutig beschrieben, ob `--delete` fachlich gewollt ist und wie Exportartefakte nach Restore behandelt werden.[file:2][file:6]
- **Erforderliche Testfälle:** vorhandene E2E-Tests `tests/e2e/test_backup.py` als technische Absicherung referenzieren; optional ergänzende Admin-Doku-Checkliste.[file:2][file:8]

### Arbeitspaket 5 — Testinventar historisieren

- **Priorität:** mittel.[file:2][file:6]
- **Umfang:** Testübersichten in `phase4_planung.md` und/oder ergänzende Review-Matrix.[file:2]
- **Maßnahme:** Kennzeichnen, welche Integrations- und E2E-Tests originär Phase 4 belegen und welche den heutigen erweiterten Stand absichern, etwa `test_time_monitor.py` oder Phase-5-nahe Systemevent-Erweiterungen.[file:6][file:8]
- **Akzeptanzkriterien:** Testabdeckung ist phasenbezogen auditierbar, ohne den heutigen Gesamtstand zu verkleinern.[file:2][file:6][file:8]
- **Erforderliche Testfälle:** keine neuen Code-Tests; Inventarprüfung genügt.[file:8]

## 5. Abschlussbewertung

**Ist Phase 4 fachlich vollständig?** Ja, im Kern ja. Die in `phase4_planung.md` beschriebenen Infrastrukturbausteine – Migrationen bis `0005`, SQLite-Unit-of-Work, Repositorys, Hardware-Leseschicht, Backup, Export, Systemcheck und deren Testbasis – sind im heutigen Exportstand vorhanden.[file:2][file:8]

**Ist Phase 4 planidentisch vollständig?** Weitgehend, aber nicht vollständig planidentisch im engen historischen Sinn. Der reale Stand enthält bereits spätere oder vorgezogene Bestandteile wie `0006_system_events_application_error.sql`, `time_monitor.py` und historisch früher als ursprünglich gedachte Rollen-/Ruhezeitlogik; das ist überwiegend als Planfortschreibung oder spätere Erweiterung zu bewerten, nicht als Implementierungsfehler.[file:2][file:6][file:8]

**Welche Punkte sind offen?** Offen im engeren Sinn sind vor allem Dokumentations- und Betriebsklarstellungen: exakte Phasenabgrenzung zu Phase 5, eindeutige Einordnung von `time_monitor.py`, sowie die organisatorische Festlegung der NAS-Spiegelung vs. Archivierung. Ein harter technischer Kernmangel der Phase-4-Infrastruktur ist auf Basis der vorliegenden Referenzdateien nicht sicher belegbar.[file:2][file:6][file:8]

**Welche Punkte sind nur dokumentarisch zu korrigieren?** Vor allem die falschen Prompt-Pfade und Dateinamen, die historische Zuordnung vorimplementierter oder nachgezogener Inhalte, sowie die saubere Kennzeichnung realer Exportpfade in allen Reviews und Plänen. Genau dort liegt der größte Bereinigungsbedarf für einen revisionsfähigen Phase-4-Stand.[file:2][file:6][file:8]
