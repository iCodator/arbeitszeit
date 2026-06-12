# Audit-Bericht Repository `iCodator/arbeitszeit`

**Datum:** 2026-06-12  
**Uhrzeit:** 13:58

## 1. Auditauftrag & Scope

Strenges Audit des aktuellen Repo-Stands für das Softwareprojekt `arbeitszeit` auf Basis ausschließlich der im Repository enthaltenen Artefakte. Geprüft wurden Planungsdokumente, Pflichtenheft/Regelwerk im Repo, Implementierung unter `src/arbeitszeit/`, Migrationen unter `migrations/`, Skripte unter `scripts/` sowie Tests unter `tests/`.

Prüfmaßstab je Phase 1–5:
- Soll: dokumentierte Anforderungen und Phasenplanung
- Ist: belegte Umsetzung im aktuellen Repo-Stand
- Soll–Ist: Erfüllung, Abweichung, Vorziehen/Nachziehen, Veraltung
- Freigabe: GO / GO mit Auflagen / NO-GO

Nicht belegbare Aussagen werden als „nicht entscheidbar auf Basis der vorliegenden Artefakte“ ausgewiesen.

## 2. Artefaktbasis

Wesentliche geprüfte Dateien:

- Planung: `docs/informelles/planung_gesamt.md`, `docs/informelles/phase1_planung.md`, `docs/informelles/phase2_planung.md`, `docs/informelles/phase3_planung.md`, `docs/informelles/phase4_planung.md`, `docs/informelles/phase5_planung.md`
- Weitere interne Nachweise: `docs/informelles/testmatrix_revision_v1.md`, `docs/informelles/device_event_architekturentscheidung_v1.md`, `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md`, `docs/informelles/nachtragsmatrix_phasen_v1.md`, `docs/informelles/audit_evidenzgrenzen_v1.md`
- Regelwerke im Repo: `pflichtenheft_arbeitszeit_v5.md`, `regelwerk_arbeitszeit_v5.md`
- Migrationen: `migrations/0001_schema.sql` bis `migrations/0006_system_events_application_error.sql`
- Skripte: `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py`
- Implementierung: Dateien unter `src/arbeitszeit/domain/`, `src/arbeitszeit/application/`, `src/arbeitszeit/infrastructure/`, `src/arbeitszeit/presentation/`
- Tests: `tests/test_migrations.py`, `tests/domain/*`, `tests/application/*`, `tests/integration/*`, `tests/e2e/*`

## 3. Bewertung Phase 1

### Soll

Phase 1 fordert laut `docs/informelles/phase1_planung.md` ein lauffähiges Fundament ohne Domänenlogik oder Use Cases: Projektgerüst, Migrationssystem, SQLite-Verbindungsaufbau, Initialisierungsskript, Migrationen `0001` und `0002` sowie ursprüngliche Migrations-Tests. Spätere Migrationen `0003` bis `0006` und erweiterte Tests sind ausdrücklich als Nachträge späterer Phasen dokumentiert.

### Ist

Im Repo vorhanden sind das Projektgerüst, `migrations/0001_schema.sql` bis `0006_system_events_application_error.sql`, `src/arbeitszeit/infrastructure/db/connection.py`, `src/arbeitszeit/infrastructure/db/migrations.py`, `scripts/init_db.py`, zusätzlich `scripts/setup.py` sowie `tests/test_migrations.py`. `scripts/init_db.py` enthält bereits die spätere Vollständigkeitsprüfung `setup_vollstaendig()`, also mehr als den originären Phase-1-Umfang. `tests/integration/test_init_db.py` existiert zusätzlich als späterer Integrationsnachweis.

### Befunde

1. **Erfüllt** – Das originäre Fundament ist vollständig belegbar: Migrationskette, Verbindungsaufbau, Runner und Initialisierungsskript sind vorhanden.  
   Kategorie: Architektur  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase1_planung.md`, `migrations/0001_schema.sql`, `migrations/0002_seed_defaults.sql`, `src/arbeitszeit/infrastructure/db/connection.py`, `src/arbeitszeit/infrastructure/db/migrations.py`, `scripts/init_db.py`, `tests/test_migrations.py`

2. **Abweichung dokumentiert und nachvollziehbar** – Der aktuelle Stand enthält gegenüber dem originären Phasenziel zusätzliche Migrationen `0003`–`0006` und erweiterte Tests. Das ist keine Lücke, sondern eine nachträglich dokumentierte Fortschreibung des Fundaments.  
   Kategorie: Doku  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase1_planung.md`, `docs/informelles/planung_gesamt.md`, `migrations/0003_cleanup_booking_status.sql`, `migrations/0004_supplement_reject_fields_and_review_note.sql`, `migrations/0005_time_bookings_device_event_id.sql`, `migrations/0006_system_events_application_error.sql`, `tests/test_migrations.py`

3. **Vorziehung/Nachziehung sauber kenntlich gemacht** – `scripts/setup.py` und die erweiterte Logik in `scripts/init_db.py` gehören laut Planung nicht mehr zum originären Phase-1-Kern, sind aber im Repo vorhanden und als spätere Ergänzungen beschrieben.  
   Kategorie: Doku  
   Schweregrad: Minor-Mangel  
   Belege: `docs/informelles/phase1_planung.md`, `docs/informelles/planung_gesamt.md`, `scripts/init_db.py`, `scripts/setup.py`

### Freigabestatus

**GO** – Phase 1 ist im aktuellen Repo-Stand fachlich und technisch übererfüllt. Auflagefrei bezogen auf das Fundament; lediglich die historische Abgrenzung zwischen originärem Phase-1-Kern und späteren Nachträgen muss bei externen Abnahmen sauber mitgeführt werden.

## 4. Bewertung Phase 2

### Soll

Phase 2 fordert laut `docs/informelles/phase2_planung.md` ein vollständiges, infrastrukturfreies Domänenmodell mit Enums, Fehlerklassen, Entitäten, Businessregeln, Compliance-Prüfungen und Repository-Protokollen. Datenbankzugriffe und Application-Use-Cases sind explizit nicht Teil der Phase.

### Ist

Unter `src/arbeitszeit/domain/` sind `enums.py`, `errors.py`, `entities.py`, `audit_events.py`, `ports/repositories.py` sowie die Services `booking_rules.py` und `compliance_checks.py` vorhanden. Unter `tests/domain/` liegen die zugehörigen Tests `test_entities.py`, `test_booking_rules.py`, `test_compliance_checks.py` und `test_audit_events.py` vor.

### Befunde

1. **Erfüllt** – Die Zielstruktur aus der Planung ist im Repo vorhanden, einschließlich des in der Planung als sinnvolle Ergänzung dokumentierten `audit_events.py`.  
   Kategorie: Architektur  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase2_planung.md`, `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/domain/errors.py`, `src/arbeitszeit/domain/entities.py`, `src/arbeitszeit/domain/audit_events.py`, `src/arbeitszeit/domain/ports/repositories.py`, `src/arbeitszeit/domain/services/booking_rules.py`, `src/arbeitszeit/domain/services/compliance_checks.py`

2. **Erfüllt mit dokumentierter Planabweichung** – Das Domänenmodell ist gegenüber älteren Planfassungen präzisiert: `BookingStatus` ist bereinigt, `POSSIBLE_*` sind als `ReviewCaseType` modelliert, `MANUAL_ENTRY` als `BookingSource.MANUAL`. Diese Abweichung ist in der Planung ausdrücklich nachgeführt und im Code konsistent umgesetzt.  
   Kategorie: Fachlogik-Compliance  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase2_planung.md`, `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/domain/services/compliance_checks.py`

3. **Erfüllt** – Die Testabdeckung der Domänenschicht ist vorhanden; die Zahl und Tiefe der Tests liegen laut Planung über dem ursprünglichen Planansatz.  
   Kategorie: Tests  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase2_planung.md`, `tests/domain/test_entities.py`, `tests/domain/test_booking_rules.py`, `tests/domain/test_compliance_checks.py`, `tests/domain/test_audit_events.py`

4. **Grenze korrekt beschrieben** – Ob die fachlichen Anforderungen des Pflichtenhefts vollständig materiell erfüllt sind, ist für Phase 2 allein nicht abschließend entscheidbar, weil die eigentliche operative Integration laut Planung erst mit Application-, Infrastruktur- und Berichtsschicht nachgewiesen wird.  
   Kategorie: Doku  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase2_planung.md`, `docs/informelles/planung_gesamt.md`

### Freigabestatus

**GO** – Phase 2 ist im Repo vollständig und konsistent umgesetzt.

## 5. Bewertung Phase 3

### Soll

Phase 3 fordert laut `docs/informelles/phase3_planung.md` die Application-Schicht mit `UnitOfWork`, Commands, Results, Fakes und den Use Cases `book_time`, `register_supplement`, `correct_booking`, `manage_work_schedule`. Laut Planung wurden `approve_supplement` und `reject_supplement` bereits vorgezogen. Rollenprüfung, Statuslogik, ReviewCase-Anlage und Audit-Logging sind fachlich mitzubelegen.

### Ist

Unter `src/arbeitszeit/application/` liegen `unit_of_work.py`, `commands.py`, `results.py` und die sechs Use-Case-Dateien vor. Unter `tests/application/` liegen die zugehörigen Testdateien einschließlich `test_fake_unit_of_work.py`. Die Struktur entspricht dem dokumentierten Zielbild. Phase-4-Inhalte `approve_supplement.py` und `reject_supplement.py` sind tatsächlich bereits in der Application-Schicht vorhanden.

### Befunde

1. **Erfüllt** – Die geplanten Artefakte der Application-Schicht sind vollständig vorhanden.  
   Kategorie: Architektur  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase3_planung.md`, `src/arbeitszeit/application/unit_of_work.py`, `src/arbeitszeit/application/commands.py`, `src/arbeitszeit/application/results.py`, `src/arbeitszeit/application/use_cases/book_time.py`, `src/arbeitszeit/application/use_cases/register_supplement.py`, `src/arbeitszeit/application/use_cases/correct_booking.py`, `src/arbeitszeit/application/use_cases/manage_work_schedule.py`, `src/arbeitszeit/application/use_cases/approve_supplement.py`, `src/arbeitszeit/application/use_cases/reject_supplement.py`

2. **Erfüllt mit Vorziehung** – `approve_supplement` und `reject_supplement` sind gegenüber dem originären Phasenkern vorgezogen implementiert und getestet. Die Planung weist diese Vorziehung offen aus; im Audit ist dies deshalb nicht als Mangel, sondern als dokumentierte Vorziehung zu werten.  
   Kategorie: Doku  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase3_planung.md`, `tests/application/test_approve_supplement.py`, `tests/application/test_reject_supplement.py`

3. **Abweichung gegenüber älterem Transaktionsverständnis** – Die Phase-3-Planung dokumentiert selbst die Korrektur des früheren Verständnisses „alle Fachobjekte + AuditLogEntry in einem commit“ hin zu `uow.commit()` vor separatem Audit-Write wegen SQLite-Locking mit `audit_conn`. Damit ist eine historische Planabweichung vorhanden, aber technisch begründet und im Repo nachgeführt.  
   Kategorie: Architektur  
   Schweregrad: Minor-Mangel  
   Belege: `docs/informelles/phase3_planung.md`, `src/arbeitszeit/application/use_cases/book_time.py`, `src/arbeitszeit/infrastructure/db/unit_of_work.py`

4. **Erfüllt** – Rollenprüfungen sind laut Planung bereits in Phase 3 implementiert; ob jede einzelne Rollenentscheidung exakt den externen Dokumenten entspricht, ist auf Basis der hier geprüften Phasenplanung und des Codes weitgehend belegbar. Ein vollständiger Abgleich gegen jede einzelne Normstelle in `pflichtenheft_arbeitszeit_v5.md` und `regelwerk_arbeitszeit_v5.md` wurde in diesem Bericht nicht ausformuliert; insoweit nicht entscheidbar auf Basis der vorliegenden Artefakte in dieser Verdichtung.  
   Kategorie: Fachlogik-Compliance  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase3_planung.md`, `src/arbeitszeit/application/use_cases/register_supplement.py`, `src/arbeitszeit/application/use_cases/correct_booking.py`, `src/arbeitszeit/application/use_cases/manage_work_schedule.py`, `src/arbeitszeit/application/use_cases/approve_supplement.py`, `src/arbeitszeit/application/use_cases/reject_supplement.py`

### Freigabestatus

**GO mit Auflagen** – Technisch ist Phase 3 umgesetzt. Auflage: Bei formaler Abnahme muss die transaktionale Sonderbehandlung des Audit-Logs als verbindliche Architekturentscheidung mitgeführt werden, damit keine falsche Erwartung einer Ein-Transaktions-Semantik fortgeschrieben wird.

## 6. Bewertung Phase 4

### Soll

Phase 4 fordert laut `docs/informelles/phase4_planung.md` die Infrastruktur mit SQLite-Repositories, `SQLiteUnitOfWork`, Hardware-Adaptern, Backup-Service, Export-Schicht, Pflichtauswertungen, Systemcheck sowie die dazugehörigen Integrations- und E2E-Tests. Migrationen `0004` und `0005` sind Teil dieser Phase; `device_event_id` soll schematisch und später auch produktiv nutzbar sein.

### Ist

Unter `src/arbeitszeit/infrastructure/` sind die Unterbereiche `db`, `hardware`, `backup`, `export`, `system_check.py` und `time_monitor.py` vorhanden. Im DB-Bereich existieren `unit_of_work.py` sowie Repositories für Audit-Log, BookingCorrection, DeviceEvent, Employee, ReviewCase, RFID-Card, Supplement, SystemConfig, TimeBooking, UserAccount und WorkSchedule. Unter `tests/integration/` und `tests/e2e/` sind die in der Planung genannten Themenfelder breit abgedeckt; zusätzlich ist `tests/integration/test_device_event_booking.py` vorhanden.

### Befunde

1. **Erfüllt** – Die SQLite-Infrastruktur ist vollständig vorhanden und strukturell sogar breiter als in älteren Phase-4-Zielbildern, insbesondere durch `device_event.py` und zusätzliche Integrationstests.  
   Kategorie: Architektur  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase4_planung.md`, `src/arbeitszeit/infrastructure/db/unit_of_work.py`, `src/arbeitszeit/infrastructure/db/repositories/*.py`, `tests/integration/test_repositories.py`, `tests/integration/test_repositories_roundtrip.py`, `tests/integration/test_unit_of_work.py`

2. **Erfüllt mit Nachführung** – Die Planung nennt `test_repositories.py`, `test_repositories_roundtrip.py`, `test_unit_of_work.py`, Hardware-, Export- und PDF-Tests; tatsächlich sind diese vorhanden, dazu weitere Dateien wie `test_init_db.py`, `test_user_accounts.py`, `test_device_event_booking.py`, `test_time_monitor.py`. Das zeigt lebendige Nachpflege, aber auch, dass die Phasendokumente regelmäßig nachgeführt werden mussten.  
   Kategorie: Tests  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase4_planung.md`, `tests/integration/conftest.py`, `tests/integration/test_init_db.py`, `tests/integration/test_user_accounts.py`, `tests/integration/test_device_event_booking.py`, `tests/integration/test_time_monitor.py`

3. **Erfüllt mit dokumentierter Lenkungsänderung** – Die Phase-4-Planung beschreibt mehrfach bewusst korrigierte Formulierungen, etwa dateibasierte statt In-Memory-Testdatenbank, `audit_conn`-Muster, operative Trennung von Haupttransaktion und Audit-Log. Das ist fachlich nachvollziehbar, aber ein Zeichen dafür, dass frühe Planfassungen nicht in allen Architekturdetails tragfähig waren.  
   Kategorie: Doku  
   Schweregrad: Minor-Mangel  
   Belege: `docs/informelles/phase4_planung.md`, `tests/integration/conftest.py`, `tests/integration/test_unit_of_work.py`

4. **Erfüllt** – Export, Backup und Systemcheck sind als Infrastrukturbausteine im Repo vorhanden; die zugehörigen Skripte `scripts/backup.py` und `scripts/setup.py` stützen den operativen Einsatz.  
   Kategorie: Betrieb  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase4_planung.md`, `src/arbeitszeit/infrastructure/backup/backup_service.py`, `src/arbeitszeit/infrastructure/export/report_queries.py`, `src/arbeitszeit/infrastructure/export/csv_exporter.py`, `src/arbeitszeit/infrastructure/export/pdf_report_service.py`, `src/arbeitszeit/infrastructure/system_check.py`, `scripts/backup.py`, `scripts/setup.py`, `tests/e2e/test_backup.py`, `tests/integration/test_export.py`, `tests/integration/test_csv_export.py`, `tests/integration/test_pdf.py`, `tests/integration/test_system_check.py`

5. **Teilweise nur repo-intern belegbar** – Ob Backup-/Restore-Betrieb, NAS-Nutzung und Aufbewahrungsregeln im Zielbetrieb organisatorisch korrekt umgesetzt sind, ist nicht entscheidbar auf Basis der vorliegenden Artefakte. Das Repo enthält technische und dokumentarische Vorarbeiten, aber keinen operativen Praxisnachweis.  
   Kategorie: Betrieb  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/planung_gesamt.md`, `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md`, `src/arbeitszeit/infrastructure/backup/backup_service.py`, `scripts/backup.py`

### Freigabestatus

**GO mit Auflagen** – Phase 4 ist technisch stark umgesetzt. Auflagen: Die dokumentierten Architekturkorrekturen sind bei jeder Abnahme mitzulesen; zudem bleiben betriebliche Wirksamkeit und organisatorische Schutzmaßnahmen außerhalb des Repos gesondert nachzuweisen.

## 7. Bewertung Phase 5

### Soll

Phase 5 fordert laut `docs/informelles/phase5_planung.md` die Präsentationsschicht mit `presentation/terminal_ui/` und `presentation/admin_cli/`, die vollständige Terminal-Buchungskette, Admin-Befehle für Mitarbeiter/Karten/Buchungen/Reports/System, Pflichtauswertungen in der Anwendung, Integration des Selbsttests und Systemzeitprotokollierung. Die Phase beschreibt außerdem die produktive Verkettung `device_events` → `BookCommand.device_event_id` → `time_bookings.device_event_id`.

### Ist

Unter `src/arbeitszeit/presentation/terminal_ui/` liegen `main.py` und `booking_loop.py`. Unter `src/arbeitszeit/presentation/admin_cli/` liegen `_intervals.py`, `bookings.py`, `employees.py`, `main.py`, `reports.py`, `schedule.py`, `system.py` und zusätzlich `user_accounts.py`. Unter `tests/e2e/` liegen `test_booking_flow.py` und `test_supplement_flow.py`. Unter `tests/integration/` existieren zusätzlich `test_device_event_booking.py`, `test_time_monitor.py` und `test_user_accounts.py`.

### Befunde

1. **Erfüllt** – Terminal-UI und Admin-CLI sind in der geplanten Grundstruktur vorhanden.  
   Kategorie: Architektur  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase5_planung.md`, `src/arbeitszeit/presentation/terminal_ui/main.py`, `src/arbeitszeit/presentation/terminal_ui/booking_loop.py`, `src/arbeitszeit/presentation/admin_cli/main.py`, `src/arbeitszeit/presentation/admin_cli/bookings.py`, `src/arbeitszeit/presentation/admin_cli/employees.py`, `src/arbeitszeit/presentation/admin_cli/reports.py`, `src/arbeitszeit/presentation/admin_cli/schedule.py`, `src/arbeitszeit/presentation/admin_cli/system.py`

2. **Übererfüllt gegenüber Basiszielbild** – Zusätzlich zu den in der Phase-5-Zielstruktur aufgeführten Modulen existiert `src/arbeitszeit/presentation/admin_cli/user_accounts.py` samt zugehörigen Integrationstests. Das deckt die in `planung_gesamt.md` nachgeführte Benutzerkontenverwaltung ab und ist im aktuellen Repo positiv zu bewerten.  
   Kategorie: Fachlogik-Compliance  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/planung_gesamt.md`, `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, `tests/integration/test_user_accounts.py`

3. **Erfüllt mit wesentlicher Nachführung** – Die produktive `device_event_id`-Verkettung ist in den Planungsdokumenten als nachgeführte Architekturentscheidung beschrieben und wird zusätzlich durch `tests/integration/test_device_event_booking.py` belegt. Damit ist ein früher offener Punkt im jetzigen Repo-Stand geschlossen.  
   Kategorie: Architektur  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase5_planung.md`, `docs/informelles/planung_gesamt.md`, `docs/informelles/device_event_architekturentscheidung_v1.md`, `src/arbeitszeit/presentation/terminal_ui/booking_loop.py`, `tests/integration/test_device_event_booking.py`

4. **Erfüllt** – Die Systemzeitprotokollierung ist im Repo als eigener Infrastrukturbaustein und mit Tests vorhanden; die Planung weist die Integration in den Terminal-Loop aus.  
   Kategorie: Betrieb  
   Schweregrad: Hinweis  
   Belege: `docs/informelles/phase5_planung.md`, `src/arbeitszeit/infrastructure/time_monitor.py`, `src/arbeitszeit/presentation/terminal_ui/main.py`, `tests/integration/test_time_monitor.py`

5. **Minor-Mangel in der Plan-/Abnahmestabilität** – Die Phase-5-Planung dokumentiert mehrere „nachgeführte Code-Review-Korrekturen“ und eine historische Testzahlangabe, die nicht mehr dem Gesamtstand entspricht. Das spricht nicht gegen die Umsetzung, aber gegen einen ganz stabilen Planstand im Sinne revisionsarmer Dokumentation.  
   Kategorie: Doku  
   Schweregrad: Minor-Mangel  
   Belege: `docs/informelles/phase5_planung.md`, `docs/informelles/planung_gesamt.md`

6. **Nicht vollständig entscheidbar** – Ob die CLI-Befehle in allen Fällen nutzer- und betriebssicher sind, ist auf Basis der vorliegenden Artefakte nur teilweise entscheidbar; es liegen Code und Tests vor, aber kein separater Abnahmebericht aus realem Praxisbetrieb im Repo.  
   Kategorie: Betrieb  
   Schweregrad: Hinweis  
   Belege: `src/arbeitszeit/presentation/admin_cli/*.py`, `tests/e2e/test_booking_flow.py`, `tests/e2e/test_supplement_flow.py`, `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md`

### Freigabestatus

**GO mit Auflagen** – Phase 5 ist im Repo umgesetzt und teilweise übererfüllt. Auflagen: Für eine revisionsfeste Gesamtfreigabe müssen reale Betriebsfreigaben, organisatorische Rollenzuordnungen und Praxisdokumentation außerhalb des Repos gesondert geführt werden.

## 8. Querschnittsbewertung

Phasenübergreifend zeigt das Repo ein hohes Maß an Umsetzungstiefe, Testbreite und dokumentierter Nachpflege. Besonders positiv sind die saubere Trennung von Domäne, Application, Infrastruktur und Präsentation sowie die explizite Dokumentation von Vorziehungen und Nachträgen.

Auffällig ist zugleich ein wiederkehrendes Muster: Mehrere frühe Planannahmen wurden später technisch korrigiert oder präzisiert, insbesondere bei Audit-Transaktionen, Testdatenbank-Semantik, `device_event_id`-Verkettung, Statusmodell und Systemereignissen. Das ist im Repo offen dokumentiert und daher beherrscht, mindert aber die Revisionsruhe der Dokumentation.

Weiteres Muster: Der aktuelle Repo-Stand ist erkennbar weiter als manche ursprünglichen Phasenbeschreibungen. Dadurch entsteht kein Umsetzungsdefizit, wohl aber ein Audit-Risiko, wenn externe Prüfer ohne Nachtragsmatrix nur die älteren Phasenbilder lesen.

## 9. Priorisierte To-do-Liste

### kritisch

- Keine kritische technische Umsetzungslücke im aktuellen Repo-Stand belegbar.

### hoch

- Formale Abnahmeunterlagen außerhalb des Repos nachziehen bzw. separat versioniert führen: Betriebsfreigaben, organisatorische Rollen- und Verantwortungszuordnung, Restore-/Backup-Freigaben, Praxis-IT-Sicherheitskonzept-Anbindung.  
  Kategorie: Betrieb  
  Schweregrad: Major-Mangel  
  Belege: `docs/informelles/planung_gesamt.md`, `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md`, `docs/informelles/audit_evidenzgrenzen_v1.md`

- Bei externer Revision immer die Nachtrags-/Evidenzdokumente gemeinsam mit den Phasenplänen ausliefern, damit Vorziehungen und Planänderungen nicht fälschlich als Inkonsistenzen gewertet werden.  
  Kategorie: Doku  
  Schweregrad: Major-Mangel  
  Belege: `docs/informelles/nachtragsmatrix_phasen_v1.md`, `docs/informelles/audit_evidenzgrenzen_v1.md`, `docs/informelles/planung_gesamt.md`

### mittel

- Historische Phasenpläne mit stabilen Verweisen auf den Endstand ergänzen oder konsolidieren, um Mehrdeutigkeiten zu Transaktionsmodell, Testzählungen und Scope-Abgrenzungen weiter zu reduzieren.  
  Kategorie: Doku  
  Schweregrad: Verbesserungspotenzial  
  Belege: `docs/informelles/phase1_planung.md`, `docs/informelles/phase3_planung.md`, `docs/informelles/phase4_planung.md`, `docs/informelles/phase5_planung.md`

- Prüfen, ob für externe Auditoren ein eigener „Release-/Abnahme-Stand“-Schnitt dokumentiert werden sollte, um den stark fortgeschriebenen Hauptplan von einer formalen Freigabedokumentation zu trennen.  
  Kategorie: Doku  
  Schweregrad: Verbesserungspotenzial  
  Belege: `docs/informelles/planung_gesamt.md`, `docs/informelles/testmatrix_revision_v1.md`

### niedrig

- Technische und organisatorische Artefakte mit konsistenter Versionskennzeichnung versehen, damit spätere Audits weniger Interpretationsarbeit benötigen.  
  Kategorie: Doku  
  Schweregrad: Verbesserungspotenzial  
  Belege: `docs/informelles/*.md`

## 10. GO/NO-GO-Matrix

| Bereich | Status | Begründung |
|---|---|---|
| Phase 1 | GO | Fundament vorhanden, spätere Nachträge klar dokumentiert. |
| Phase 2 | GO | Domänenmodell vollständig und getestet. |
| Phase 3 | GO mit Auflagen | Application-Schicht vollständig; Transaktions-/Audit-Sonderlogik muss bei Abnahme mitgeführt werden. |
| Phase 4 | GO mit Auflagen | Infrastruktur breit umgesetzt; betriebliche Wirksamkeit nur teilweise repo-intern nachweisbar. |
| Phase 5 | GO mit Auflagen | Präsentationsschicht und End-to-End-Flüsse vorhanden; organisatorische Praxisfreigaben extern nachzuweisen. |
| Gesamt-System | GO mit Auflagen | Technisch im Repo freigabefähig; revisionsfeste Gesamtfreigabe benötigt ergänzende organisatorische Nachweise außerhalb des Repos. |

## 11. Selbstcheck

- Widerspruch geprüft: `planung_gesamt.md` und die Phasenpläne dokumentieren Nachträge, Vorziehungen und Korrekturen überwiegend offen; echte unaufgelöste Repo-Widersprüche wurden im auditierbaren Kern nicht festgestellt.
- Unklarheit: Der vollständige inhaltliche Soll-Ist-Abgleich jeder Einzelvorgabe aus `pflichtenheft_arbeitszeit_v5.md` und `regelwerk_arbeitszeit_v5.md` wurde in diesem Bericht nicht normstellenweise ausformuliert. Soweit daraus weitergehende Detailaussagen abgeleitet würden, wäre dies nicht entscheidbar auf Basis der vorliegenden Artefakte in dieser Berichtstiefe.
- Unklarheit: Aussagen zur tatsächlichen Produktivnutzung in einer Zahnarztpraxis, zu Hardware unter realer Zielumgebung und zu organisatorischen Verantwortlichkeiten sind nicht entscheidbar auf Basis der vorliegenden Artefakte.
- Widerspruchsrisiko: Historische Phasenbeschreibungen und aktueller Repo-Endstand sind nicht immer identisch, jedoch überwiegend durch Nachtragsdokumente erklärt.
- Ergebnis dieses Selbstchecks: Der Bericht ist für den aktuellen Repo-Stand als revisionsnaher technischer Audit-Bericht verwendbar, jedoch nicht als Ersatz für organisatorische Freigabe- und Betriebsnachweise.
