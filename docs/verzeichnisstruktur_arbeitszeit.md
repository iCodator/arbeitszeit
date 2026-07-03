# Verzeichnisstruktur – Projekt `arbeitszeit`

> Repository: [iCodator/arbeitszeit](https://github.com/iCodator/arbeitszeit)
> Stand: Commit `9b9650a` (aktueller Stand des `main`-Branches zum Zeitpunkt der Analyse)

---

## Übersicht

Das Projekt folgt einer strikten Schichtenarchitektur (Domain → Application → Infrastructure → Presentation), ergänzt durch eigenständige Verzeichnisse für Datenbank-Migrationen, Hilfsskripte, Dokumentation und Tests.

---

## Wurzelverzeichnis `/`

Das Wurzelverzeichnis enthält ausschließlich Dateien, keine weiteren Unterverzeichnisse außer den nachfolgend beschriebenen. Es beherbergt die Projektkonfiguration, die zentralen Dokumentationsdateien sowie ergänzende Markdown-Dokumente:

- `pyproject.toml` – Projektmetadaten und Abhängigkeiten (Build-System, pytest-Konfiguration, Entry Points)
- `.python-version` – legt die Python-Version für das Projekt fest (genutzt von `pyenv`)
- `.gitignore` – definiert vom Versionskontrollsystem zu ignorierende Dateien und Verzeichnisse
- `README.md` – Projekteinstieg, Kurzbeschreibung, Installationshinweise
- `CHANGELOG.md` – chronologische Aufzeichnung aller Versionsänderungen
- `CONTRIBUTING.md` – Richtlinien für Beiträge, Code-Stil und Entwicklungsworkflow
- `anlage_einhaltung_pflichtenheft.md` – Nachweisdokument, das die Erfüllung des Pflichtenhefts belegt
- `pflichtenheft_arbeitszeit_v6.md` – das vollständige Pflichtenheft v6 mit funktionalen und nicht-funktionalen Anforderungen
- `regelwerk_arbeitszeit_v5.md` – fachliche Regelsammlung v5 (Buchungsregeln, Pausenregelung, Gesetzeskonformität)
- `handbuch_arbeitszeit.md` – vollständiges Benutzerhandbuch in Markdown-Form
- `Handbuch - Arbeitszeiterfassung.html` – HTML-Export des Benutzerhandbuchs (browserlesbar)
- `installationsanleitung_arbeitszeit.md` – Schritt-für-Schritt-Installationsanleitung in Markdown
- `Installationsanleitung - Arbeitszeit.html` – HTML-Export der Installationsanleitung
- `befehlsreferenz_arbeitszeit.md` – vollständige Referenz aller Admin-CLI-Befehle
- `markdownlint.json` – Konfiguration für die Markdown-Lint-Prüfung der Dokumentation
- `run_audit.sh` – Shell-Skript zum Starten des Audit-Laufs (ruft das Audit-Skript in `scripts/` auf)
- `test_booking_loop.py` – auf Wurzelebene liegender Testmodul für die Terminal-UI-Buchungsschleife

---

## `.claude/`

Konfigurationsverzeichnis für den KI-Assistenten Claude (Anthropic). Enthält neben `settings.json` (projektspezifische Verhaltenseinstellungen, z. B. Erlaubnisregeln für Bash-Befehle) auch `claude.md` (projektspezifische Arbeitsanweisungen), die verbindlichen Regelquellen `markdown-Rules.md` und `Markdown Syntax Documentation.pdf` sowie die Unterverzeichnisse `audit/` und `rules/`.

---

## `docs/`

Sammlung aller **projektbegleitenden Dokumente**, die über den Quellcode hinausgehen. Das Verzeichnis enthält deutlich mehr als drei Unterverzeichnisse (u. a. `betrieb/`, `datenschutz/`, `informelles/`, `domain/`, `infrastructure/`, `module/`, `adr/`, `archive/`, `audits/`, `pruefberichte/`) sowie mehrere lose Dateien auf Dokumentenebene:

- `handbuch_rollen_cli_ergaenzung_v1_0.md` – Ergänzungsdokument zum Handbuch, das die Rollen und CLI-Kommandos beschreibt (v1.0)
- `verzeichnisstruktur_arbeitszeit.md` – das vorliegende Dokument zur Verzeichnisstruktur des Projekts
- `SECURITY.md` – Sicherheitsdokumentation (Härtungsmaßnahmen, Bedrohungsmodell, Audit-Ereignisse)

### `docs/betrieb/`

Enthält alle **betrieblichen und organisatorischen Dokumente** für den produktiven Einsatz des Systems. Diese Dateien richten sich an Systemadministratoren und Datenschutzverantwortliche:

- `betriebsdokumentation_arbeitszeit_v1_1.md` – vollständige Betriebsdokumentation v1.1: Systemarchitektur, Datenpfade, laufende Dienste, Wartungsaufgaben
- `betriebsfreigabe_protokoll.md` – formales Abnahmeprotokoll für die Betriebsfreigabe des Systems
- `hardware_inbetriebnahme_protokoll.md` – Protokoll zur physischen Inbetriebnahme von RFID-Reader und USB-Numpad
- `rollenzuweisung.md` – ausführliche Beschreibung der Benutzerrollen (Mitarbeiter, Admin, Praxisleitung) und ihrer Rechte
- `rollenzuweisung_arbeitszeit_v1_0.md` – kompakte Version der Rollenzuweisung (v1.0, älterer Stand)
- `datenschutz_und_tom_arbeitszeit_v1_0.md` – Dokumentation der technisch-organisatorischen Maßnahmen (TOM) gemäß DSGVO
- `aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` – Konzept zur gesetzeskonformen Aufbewahrung und Löschung von Arbeitszeitdaten
- `backup_zeitplan_und_automatisierung.md` – Beschreibung des Backup-Zeitplans, der Cron-Jobs und der Automatisierung
- `restore_checkliste.md` – Schritt-für-Schritt-Checkliste zur Wiederherstellung der Daten aus einem Backup

### `docs/datenschutz/`

Enthält das **Datenschutz-Verzeichnis der Verarbeitungstätigkeiten (VVT)** gemäß Art. 30 DSGVO:

- `vvt_arbeitszeit_v1.md` – Verzeichnis der Verarbeitungstätigkeiten v1: Zweck, Rechtsgrundlage, Datenkategorien, Speicherfristen, Empfänger und technische Schutzmaßnahmen für die Arbeitszeiterfassung

### `docs/informelles/`

Enthält **interne Arbeits- und Planungsdokumente**, die den Entwicklungsprozess begleiten, aber keinen normativen Charakter haben. Das Verzeichnis umfasst aktuell nur zwei Dateien:

- `planung_gesamt.md` – Gesamtübersicht aller Entwicklungsphasen und ihrer Meilensteine
- `session_abschluss_und_klarstellungen_2026-06-11.md` – Abschlussnotiz und Klarstellungen zu einer Bearbeitungssitzung

Die ursprünglich hier beschriebenen Dokumente liegen tatsächlich in anderen Verzeichnissen: Phasenpläne, Abschlussnotizen, `audit_evidenzgrenzen_v1.md`, `audit_klarstellungen_niedrig_v1.md`, `device_event_abschlussprotokoll_v1.md`, `migrationsuebersicht_notiz_v1.md` und `terminologie_harmonisierung_v1.md` befinden sich in `docs/archive/`; die Architekturentscheidung `device_event_architekturentscheidung_v1.md` liegt in `docs/adr/`; die Testmatrix- und Nachtragsdokumente `nachtragsmatrix_phasen_v1.md`, `testmatrix_planabweichungen_v1.md`, `testmatrix_pruefbericht_v1.md` und `testmatrix_revision_v1.md` befinden sich in `docs/betrieb/nachweise/`.

---

## `migrations/`

Enthält alle **SQL-Migrationsdateien** für die SQLite-Datenbank. Die Dateien werden sequenziell durch den Python-Migrationsrunner in `src/arbeitszeit/infrastructure/db/migrations.py` ausgeführt. Jede Datei hat eine fortlaufende numerische Präfixnummer, die die Ausführungsreihenfolge erzwingt:

- `0001_schema.sql` – initiales Datenbankschema: alle Tabellen, Indizes, Constraints und Trigger der ersten Version
- `0002_seed_defaults.sql` – Befüllung der Datenbank mit Standardwerten (z. B. Buchungstypen, Systemkonfiguration)
- `0003_cleanup_booking_status.sql` – bereinigt und normalisiert Buchungsstatus-Werte in bestehenden Datensätzen
- `0004_supplement_reject_fields_and_review_note.sql` – fügt Felder für Ablehnungsgrund und Prüfnotiz zur Nachtrags-Tabelle hinzu
- `0005_time_bookings_device_event_id.sql` – ergänzt die `time_bookings`-Tabelle um eine Fremdschlüsselspalte zur `device_events`-Tabelle
- `0006_system_events_application_error.sql` – fügt den Ereignistyp `application_error` zur `system_events`-Tabelle hinzu

---

## `scripts/`

Enthält eigenständige **Python-Hilfsskripte** für Betrieb und Einrichtung. Diese Skripte werden nicht als Teil des Anwendungspakets importiert, sondern direkt über die Kommandozeile aufgerufen:

- `init_db.py` – initialisiert eine neue SQLite-Datenbank: legt die Datenbankdatei an und führt alle Migrationen durch
- `setup.py` – interaktives Einrichtungsskript für die Erstinstallation (legt Konfigurationsdateien an, prüft Systemvoraussetzungen)
- `backup.py` – erstellt ein Backup der SQLite-Datenbankdatei in ein konfigurierbares Zielverzeichnis (inkl. Zeitstempel im Dateinamen)
- `generate_audit_notes.py` – analysiert die Datenbank und generiert maschinenlesbare Audit-Notizen für die Nachvollziehbarkeit von Buchungen und Korrekturen
- `show_config.py` – zeigt die aktuellen Schlüssel-Wert-Paare der Systemkonfiguration an
- `verify_hardware.py` – prüft die Erreichbarkeit und Funktion der angeschlossenen Hardware (RFID-Reader, Numpad)

---

## `src/`

Wurzelverzeichnis des Python-Pakets. Enthält ausschließlich das Unterverzeichnis `arbeitszeit/`, das das eigentliche installierbare Paket darstellt. Diese Struktur folgt dem `src`-Layout gemäß Python Packaging Guidelines.

### `src/arbeitszeit/`

Das **Hauptpaket** der Anwendung. Enthält `__init__.py` (leer, markiert das Paket) sowie vier Schicht-Unterverzeichnisse, die die Architektur widerspiegeln.

### `src/arbeitszeit/domain/`

Die **Fachlogik-Schicht** (Domain Layer). Enthält ausschließlich reinen Python-Code ohne Abhängigkeiten zu Datenbank, Hardware oder UI. Jede Änderung an dieser Schicht hat direkte fachliche Bedeutung:

- `entities.py` – Datenklassen der Fachdomäne: `Employee`, `TimeBooking`, `WorkSchedule`, `Supplement`, `RfidCard`, `UserAccount` u. a.
- `enums.py` – Aufzählungstypen der Domäne: Buchungstypen (Kommen/Gehen/Pause-Start/Pause-Ende), Buchungsstatus, Nachtragstypen
- `errors.py` – domänenspezifische Ausnahmen (z. B. `BookingNotAllowedError`, `EmployeeNotFoundError`)
- `audit_events.py` – Datenklassen für Audit-Ereignisse, die bei jeder schreibenden Domänenaktion erzeugt werden

#### `src/arbeitszeit/domain/ports/`

Definiert die **abstrakten Schnittstellen** (Ports im Sinne der Hexagonalarchitektur), über die die Domäne auf externe Ressourcen zugreift. Konkrete Implementierungen befinden sich in `infrastructure/`:

- `repositories.py` – abstrakte Repository-Interfaces für alle Entitäten: `IEmployeeRepository`, `ITimeBookingRepository`, `ISupplementRepository`, `IWorkScheduleRepository`, `IRfidCardRepository`, `IAuditLogRepository`, `IUserAccountRepository`, `IReviewCaseRepository`, `IDeviceEventRepository`, `ISystemConfigRepository`

#### `src/arbeitszeit/domain/services/`

Enthält **domänenspezifische Dienste**, die Geschäftsregeln kapseln, die sich nicht sinnvoll einer einzelnen Entität zuordnen lassen:

- `booking_rules.py` – prüft, ob eine neue Buchung regelkonform ist (z. B. kein doppeltes Kommen, kein Gehen ohne vorheriges Kommen)
- `compliance_checks.py` – prüft Buchungssequenzen auf Verstöße gegen gesetzliche Vorgaben (Mindestpause, maximale Arbeitszeit)

### `src/arbeitszeit/application/`

Die **Anwendungsschicht** (Application Layer). Orchestriert die Fachlogik durch Use Cases und kennt weder Datenbankdetails noch Hardware. Sie vermittelt zwischen Domäne und Infrastructure:

- `commands.py` – Eingabedatenklassen (Command Objects) für alle Use Cases: `BookTimeCommand`, `RegisterSupplementCommand`, `ApproveSupplementCommand` usw.
- `queries.py` – Query-DTOs für die lesende Seite (CQRS-Read): reine Datenstrukturen für Abfrageergebnisse, ohne SQL-Logik
- `results.py` – Ergebnisdatenklassen (Result Objects), die Use Cases an die aufrufende Schicht zurückgeben
- `unit_of_work.py` – abstraktes `IUnitOfWork`-Interface: definiert Transaktionsgrenzen und den Zugriff auf alle Repositories

#### `src/arbeitszeit/application/use_cases/`

Enthält einen Use Case pro Datei. Jeder Use Case implementiert genau einen fachlichen Anwendungsfall:

- `book_time.py` – **Kernfunktion**: verarbeitet eine RFID-Buchung (Kommen/Gehen/Pause), prüft Regelwerk, persistiert Buchung und Audit-Eintrag
- `correct_booking.py` – korrigiert eine vorhandene Buchung durch einen Admin-Nutzer (erstellt Korrekturdatensatz, kein Löschen)
- `register_supplement.py` – registriert einen Nachtragswunsch eines Mitarbeiters (z. B. vergessene Buchung)
- `approve_supplement.py` – genehmigt einen Nachtrag: validiert, erstellt Korrekturbuchung, schreibt Audit-Log
- `reject_supplement.py` – lehnt einen Nachtrag ab und speichert den Ablehnungsgrund
- `manage_work_schedule.py` – legt Soll-Arbeitszeiten (Wochenpläne) für Mitarbeiter an oder aktualisiert sie
- `manage_employees.py` – verwaltet Mitarbeiterdatensätze (Anlegen, Deaktivieren)
- `manage_rfid_cards.py` – verwaltet die Zuordnung von RFID-Karten zu Mitarbeitern
- `manage_user_accounts.py` – verwaltet Admin-Benutzerkonten (Anlegen, Passwortänderung, Rollenzuweisung)

### `src/arbeitszeit/infrastructure/`

Die **Infrastrukturschicht** (Infrastructure Layer). Enthält alle konkreten Implementierungen: Datenbankzugriff, Hardware-Anbindung, Export und Backup. Implementiert die in `domain/ports/` definierten Interfaces:

- `system_check.py` – prüft beim Systemstart, ob alle Voraussetzungen erfüllt sind (Datenbankdatei erreichbar, Migrationen aktuell, Hardware erkannt)
- `time_monitor.py` – Hintergrundüberwachung: erkennt Situationen, in denen Mitarbeiter ohne Ausbuchung die maximale Arbeitszeit überschreiten, und schreibt einen Warneintrag
- `notification.py` – sendet Desktop-Benachrichtigungen über `notify-send` (Stdlib-`subprocess`, kein zusätzliches Paket); schlägt still fehl, wenn `notify-send` nicht verfügbar ist

#### `src/arbeitszeit/infrastructure/backup/`

Implementierung des **Backup-Dienstes** innerhalb der Anwendungslogik:

- `backup_service.py` – kapselt die Backup-Logik: Kopieren der SQLite-Datei, Benennung mit Zeitstempel, optionale Komprimierung, Verwaltung der Aufbewahrungsanzahl

#### `src/arbeitszeit/infrastructure/db/`

Sämtliche **Datenbankzugriffe** auf SQLite. Implementiert die in `domain/ports/repositories.py` definierten Interfaces:

- `connection.py` – verwaltet die SQLite-Datenbankverbindung und aktiviert erforderliche PRAGMA-Einstellungen (z. B. Foreign Keys)
- `migrations.py` – Migrationsrunner: liest alle SQL-Dateien aus `migrations/`, prüft welche bereits angewendet wurden, führt ausstehende sequenziell aus
- `unit_of_work.py` – konkrete Implementierung von `IUnitOfWork`: verwaltet SQLite-Transaktionen (`BEGIN`, `COMMIT`, `ROLLBACK`) und stellt alle Repository-Instanzen bereit

##### `src/arbeitszeit/infrastructure/db/repositories/`

Enthält je eine Datei pro Repository-Implementierung. Jede Datei implementiert das zugehörige Interface aus `domain/ports/repositories.py`:

- `employee.py` – CRUD-Operationen für Mitarbeiterdatensätze
- `time_booking.py` – Lesen und Schreiben von Zeitbuchungen; enthält komplexe Abfragen (offene Buchungen, Buchungen je Zeitraum)
- `work_schedule.py` – Verwaltung der Soll-Arbeitszeitpläne (Wochenpläne, Gültigkeitszeiträume)
- `rfid_card.py` – Zuordnung von RFID-UIDs (gehasht) zu Mitarbeitern
- `supplement.py` – Persistenz von Nachtragsanträgen und ihrem Genehmigungsstatus
- `booking_correction.py` – Speicherung und Abfrage von Buchungskorrekturen (unveränderlicher Korrekturdatensatz)
- `review_case.py` – Verwaltung von Prüffällen, die eine manuelle Überprüfung durch die Praxisleitung erfordern
- `audit_log.py` – append-only Schreiben und Lesen des Audit-Logs (keine Update- oder Delete-Operationen)
- `device_event.py` – Persistenz von rohen Hardware-Ereignissen (RFID-Scan + Numpad-Auswahl) vor der eigentlichen Buchungsverarbeitung
- `system_config.py` – Lesen und Schreiben von Schlüssel-Wert-Paaren der Systemkonfiguration
- `user_account.py` – Verwaltung von Admin-Benutzerkonten (Benutzername, Passwort-Hash, Rolle)
- `_helpers.py` – interne Hilfsfunktionen, die von mehreren Repository-Klassen gemeinsam genutzt werden (nicht öffentliche API)

#### `src/arbeitszeit/infrastructure/export/`

Implementierung der **Exportfunktionen** für Berichte und Datenausgaben:

- `report_queries.py` – SQL-Abfragen für Berichtsdaten: aggregiert Arbeitszeiten, Pausen, Abweichungen und Nachträge je Mitarbeiter und Zeitraum
- `csv_exporter.py` – exportiert Buchungsdaten und Monatsberichte als CSV-Datei (für Lohnbuchhaltung oder Archivierung)
- `pdf_report_service.py` – erstellt formatierte PDF-Berichte (Monatsübersichten, Einzelnachweise) mittels ReportLab

#### `src/arbeitszeit/infrastructure/hardware/`

Anbindung der **physischen Eingabegeräte** über das Linux-`evdev`-Subsystem. Abstrahiert die Hardwaredetails hinter einheitlichen Interfaces:

- `ports.py` – abstrakte Hardware-Interfaces: `HardwareReader` (für RFID-Reader und Numpad) als Port-Definition, u. a. mit den Fehlerklassen `EmptyUidError` und `HardwareTimeoutError`
- `evdev_reader.py` – konkrete Implementierung `EvdevHardwareReader` des `HardwareReader`-Interfaces über `python-evdev`: liest Tastaturereignisse von RFID-Reader (USB-HID) und USB-Numpad, wandelt Scansequenzen in strukturierte Ereignisobjekte um
- `simulator.py` – Software-Simulator `SimulatedHardwareReader` für RFID-Reader und Numpad (ermöglicht Tests und Entwicklung ohne physische Hardware)
- `uid_hash.py` – erzeugt über `hash_uid()` einen einseitigen SHA-256-Hash der RFID-UID für die datenschutzkonforme Speicherung in der Datenbank
- `__init__.py` – exportiert `SimulatedHardwareReader`, `hash_uid`, `HardwareReader`, `EmptyUidError`, `HardwareTimeoutError` und `RawBookingRequest` als öffentliche API des Subpakets

### `src/arbeitszeit/presentation/`

Die **Präsentationsschicht** (Presentation Layer). Enthält alle Benutzerschnittstellen. Kennt Application-Layer und Infrastructure, aber nicht die Domäne direkt:

#### `src/arbeitszeit/presentation/terminal_ui/`

Die **Mitarbeiter-Schicht-Oberfläche** für den produktiven Dauerbetrieb am Praxisrechner. Läuft als Vollbildprozess und wartet auf RFID-Scans:

- `main.py` – Einstiegspunkt der Terminal-UI: initialisiert alle Abhängigkeiten (Datenbank, Hardware, Use Cases), startet den Booking-Loop
- `booking_loop.py` – Hauptschleife: wartet auf RFID-Scan, liest Buchungsart vom Numpad, delegiert an `book_time`-Use-Case, gibt taktiles/visuelles Feedback

#### `src/arbeitszeit/presentation/admin_cli/`

Die **Administrator-Kommandozeilenschnittstelle** (CLI, Programmname `admin`) für die Praxisleitung und den Systemadministrator:

- `main.py` – Einstiegspunkt und Kommando-Registrierung: fasst alle Befehlsgruppen zusammen, konfiguriert Dependency Injection
- `employees.py` – CLI-Kommandos zur Mitarbeiterverwaltung: anlegen, deaktivieren, RFID-Karte zuordnen
- `bookings.py` – CLI-Kommandos zur Buchungskorrektur und zu Nachträgen: `correct`, `supplement`, `approve-supplement`, `reject-supplement` (kein `list`-Unterbefehl; Buchungsübersichten liefert `reports.py`)
- `reports.py` – CLI-Kommandos zur Berichtsausgabe: Monatsberichte als PDF oder CSV exportieren (`export-csv`, `export-pdf-day/-week/-month/-employee`), Buchungsübersichten anzeigen (`open-bookings`, `warn-cases`, `corrections`, `supplements`, `open-review-cases`)
- `schedule.py` – CLI-Kommandos zur Verwaltung von Soll-Arbeitszeitplänen (Anlegen, Anzeigen, Aktualisieren)
- `system.py` – CLI-Kommandos für Systemfunktionen: Systemcheck ausführen, Backup anstoßen (kein eigenständiger Restore-Unterbefehl)
- `user_accounts.py` – CLI-Kommandos zur Verwaltung von Admin-Benutzerkonten: anlegen, Passwort ändern, Rollen zuweisen
- `_auth.py` – CLI-seitige Rollenprüfung für lesende Operationen ohne eigenen Use Case (z. B. `reports`, `schedule show`, `system`); schreibende Operationen prüfen die Rolle über die Use Cases der Anwendungsschicht (nicht öffentliche API)
- `_intervals.py` – interne Hilfsfunktionen zur Auswertung und Darstellung von Zeitintervallen in der CLI-Ausgabe (nicht öffentliche API)

---

## `tests/`

Enthält die gesamte **Testsuite** des Projekts. Die Struktur spiegelt die Architekturschichten des Quellcodes wider und unterteilt sich in fünf Teststufen:

- `test_migrations.py` – auf Wurzelebene: prüft die korrekte Ausführungsreihenfolge und Idempotenz aller Datenbankmigrationen

### `tests/domain/`

**Unit-Tests für die Domänenschicht.** Testen Entitäten, Dienste und Regelwerk isoliert ohne Datenbank oder Hardware:

- `test_entities.py` – Tests für alle Domänenentitäten (Zustandsübergänge, Validierungen, Berechnungen)
- `test_booking_rules.py` – Tests für die Buchungsregeln (erlaubte und verbotene Buchungsfolgen)
- `test_compliance_checks.py` – Tests für die gesetzlichen Compliance-Prüfungen (Pausenregeln, Maximalarbeitszeit)
- `test_audit_events.py` – Tests für die korrekte Erzeugung von Audit-Ereignissen

### `tests/application/`

**Unit-Tests für die Anwendungsschicht.** Verwenden ausschließlich In-Memory-Fakes statt echter Datenbank oder Hardware:

- `fakes.py` – vollständige In-Memory-Implementierungen aller Repository-Interfaces für Testzwecke (kein SQLite, kein Dateisystem)
- `test_book_time.py` – Tests für den `BookTime`-Use-Case (alle Regelzweige, Fehlerfälle, Audit-Log-Erzeugung)
- `test_correct_booking.py` – Tests für den `CorrectBooking`-Use-Case
- `test_register_supplement.py` – Tests für den `RegisterSupplement`-Use-Case
- `test_approve_supplement.py` – Tests für den `ApproveSupplement`-Use-Case (inkl. Ablehnungsszenarien)
- `test_reject_supplement.py` – Tests für den `RejectSupplement`-Use-Case
- `test_manage_work_schedule.py` – Tests für den `ManageWorkSchedule`-Use-Case
- `test_manage_employees.py` – Tests für den `ManageEmployees`-Use-Case
- `test_manage_rfid_cards.py` – Tests für den `ManageRfidCards`-Use-Case
- `test_manage_user_accounts.py` – Tests für den `ManageUserAccounts`-Use-Case
- `test_fake_unit_of_work.py` – prüft das korrekte Transaktionsverhalten der Fake-`UnitOfWork`-Implementierung

### `tests/integration/`

**Integrationstests** gegen echte SQLite-Datenbanken (im Speicher oder als temporäre Datei). Prüfen das Zusammenspiel von Repositories, Unit-of-Work, Hardware-Adaptern und Export-Diensten:

- `conftest.py` – pytest-Fixtures für alle Integrationstests (In-Memory-SQLite-Datenbank, initialisierte Migrationen)
- `test_repositories.py` – Tests aller Repository-Implementierungen gegen echte SQLite
- `test_repositories_roundtrip.py` – Round-Trip-Tests: schreiben und lesen derselben Datensätze zur Konsistenzprüfung
- `test_unit_of_work.py` – Tests für Commit- und Rollback-Verhalten der SQLite-UnitOfWork
- `test_init_db.py` – Tests für das Datenbankinitialisierungsskript
- `test_employees.py` – Integrationstests für Mitarbeiterverwaltung über die Admin-CLI
- `test_user_accounts.py` – Integrationstests für Benutzerkontenverwaltung über die Admin-CLI
- `test_export.py` – Integrationstests für den vollständigen Export-Workflow (Report-Queries bis PDF/CSV)
- `test_csv_export.py` – spezifische Integrationstests für den CSV-Export (Format, Felder, Sonderzeichen)
- `test_pdf.py` – spezifische Integrationstests für die PDF-Berichtserstellung (Inhalt, Struktur)
- `test_hardware_evdev.py` – Integrationstests für den `EvdevHardwareReader` (mit simulierten evdev-Events)
- `test_hardware_simulator.py` – Integrationstests für den Hardware-Simulator
- `test_device_event_booking.py` – Integrationstests für den vollständigen Pfad von Hardware-Ereignis bis Zeitbuchung
- `test_system_check.py` – Integrationstests für den Systemcheck (erkannte und nicht erkannte Fehlerszenarien)
- `test_time_monitor.py` – Integrationstests für den Zeitmonitor (Erkennung von Überschreitungen)

### `tests/e2e/`

**End-to-End-Tests** (E2E). Testen vollständige Anwendungsflüsse vom Aufruf des Use-Cases bis zur persistierten SQLite-Datenbank, inklusive Backup-Zyklus:

- `test_booking_flow.py` – vollständiger Buchungsfluss: RFID-Scan → Buchungsauswahl → Regelprüfung → Persistenz → Audit-Log
- `test_supplement_flow.py` – vollständiger Nachtragsfluss: Antrag → Genehmigung/Ablehnung → Korrekturbuchung
- `test_backup.py` – vollständiger Backup-Zyklus: Backup erstellen → Datei prüfen → Restore simulieren

### `tests/presentation/`

**Tests für die Präsentationsschicht:**

- `test_booking_loop.py` – Tests für die Buchungsschleife der Terminal-UI (`booking_loop.py`)
