# Prüfbericht: `docs/betrieb/betriebsfreigabe_protokoll.md`

**Geprüftes Dokument:** `docs/betrieb/betriebsfreigabe_protokoll.md` (Version 1.0, Stand 2026-06-12)
**Repository:** iCodator/arbeitszeit
**Prüfgrundlage:** Quellcode unter `src/arbeitszeit/`, `migrations/`, sowie Dokumente unter `docs/betrieb/`, `docs/datenschutz/`, `docs/informelles/`

---

## Gesamteinschätzung

Das Betriebsfreigabe-Protokoll ist überwiegend ein organisatorisches Formular (Ankreuzfelder, Freitextfelder, Unterschriften) und enthält vergleichsweise wenige technisch prüfbare Aussagen. Die wenigen technischen Bezüge (Konfigurationsschlüssel, Dokumentverweise, Rollenbezeichnungen) sind größtenteils korrekt belegbar. Es gibt jedoch zwei klare Abweichungen: Die referenzierten Testmatrix-Dokumente liegen nicht unter dem im Protokoll genannten Pfad `docs/informelles/`, sondern unter `docs/betrieb/nachweise/`. Außerdem ist der Konfigurationsschlüssel `backup.backup_dir` und `export.export_dir` sowie `time_monitor.jump_threshold_seconds` nicht in den Migrations-Seeds vorhanden, wird jedoch im Code erwartet bzw. per Fallback behandelt — dies ist differenziert zu bewerten. Alle referenzierten Dateien unter `docs/betrieb/` (Rollenzuweisung, Hardware-Inbetriebnahme, Betriebsdokumentation, Restore-Checkliste) existieren tatsächlich im Repository.

---

## Strukturierter Report je Aussage

### Abschnitt 1: Basisdaten

**Aussage:** „Version des Systems (pyproject.toml)“ — Verweis auf `pyproject.toml` als Versionsquelle.
**Status:** korrekt
**Beleg:** `pyproject.toml`, Zeile 7: `version = "0.1.0"`
**Bewertung:** `pyproject.toml` existiert im Repository-Root und enthält tatsächlich ein `version`-Feld. Der Verweis ist technisch zutreffend.

**Aussage:** „Datenbankschema-Stand (letzte Migration)“ — impliziert Versionierung über Migrationsdateien.
**Status:** korrekt
**Beleg:** `migrations/0001_schema.sql` bis `migrations/0006_system_events_application_error.sql`; Tabelle `schema_migrations` in `migrations/0001_schema.sql`
**Bewertung:** Das Repository verwendet ein nummeriertes Migrationssystem (`0001_...` bis `0006_...`), dessen angewandter Stand in der Tabelle `schema_migrations` nachgehalten wird (vgl. auch `src/arbeitszeit/infrastructure/system_check.py`, Funktion `_check_db_access`, welche die Spalte `version` aus `schema_migrations` gegen die vorhandenen Migrationsdateien abgleicht). Der Verweis auf einen „Datenbankschema-Stand“ ist damit technisch fundiert.

Übrige Felder in Abschnitt 1 (Praxis, Standort, Datum, Verantwortliche Personen) sind Freitextfelder ohne technischen Bezug.
**Status:** nicht zutreffend (organisatorisch)

---

### Abschnitt 2: Geltungsbereich der Freigabe

**Aussage:** „die eingesetzte SQLite-Datenbank samt Schema und Konfiguration“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/infrastructure/db/connection.py` (Funktion `open_connection`, verwendet in `system_check.py`, `system.py` u.a.); `migrations/0001_schema.sql`
**Bewertung:** Das System basiert nachweislich auf SQLite; die Verbindungsfunktion `open_connection` sowie alle SQL-Migrationen belegen den Einsatz von SQLite als Datenbank.

**Aussage:** „die angeschlossene Hardware (RFID-Reader, USB-Numpad, Terminalgerät, NAS)“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/infrastructure/system_check.py`, Funktion `_check_devices` (Parameter `numpad_path`, `rfid_path`); Funktion `_check_nas` (NAS-Pfadprüfung über `backup.nas_path`)
**Bewertung:** Numpad, RFID und NAS sind im Systemcheck als geprüfte Komponenten belegt. Ein generisches „Terminalgerät“ wird nicht als eigener technischer Check identifiziert, ist aber als Trägergerät der Terminal-UI (`src/arbeitszeit/presentation/terminal_ui/`) plausibel und im Kontext nicht widersprüchlich; da kein expliziter Codebeleg für „Terminalgerät“ als geprüfte Einheit existiert, wird dieser Teilaspekt als **nicht verifizierbar** eingestuft, der Rest der Aussage bleibt korrekt.

Übrige Aufzählungspunkte (Zeiterfassung, Korrektur, Nachtragsbearbeitung, Export, Backup) sind allgemeine Prozessbeschreibungen ohne einzelne prüfbare technische Detailaussage in diesem Abschnitt.
**Status:** nicht zutreffend (organisatorisch, da als Aufzählung von Geltungsbereichen formuliert ohne konkrete technische Einzelbehauptung)

---

### Abschnitt 3.1: Vorliegende Projektunterlagen

**Aussage:** Pflichtenheft `pflichtenheft_arbeitszeit_v6.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `pflichtenheft_arbeitszeit_v6.md` existiert im Repository-Root.
**Bewertung:** Verifiziert durch Verzeichnislisting des Repositorys.

**Aussage:** Regelwerk `regelwerk_arbeitszeit_v5.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `regelwerk_arbeitszeit_v5.md` existiert im Repository-Root.
**Bewertung:** Verifiziert durch Verzeichnislisting.

**Aussage:** Installationsanleitung `installationsanleitung_arbeitszeit.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `installationsanleitung_arbeitszeit.md` existiert im Repository-Root.

**Aussage:** Handbuch `handbuch_arbeitszeit.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `handbuch_arbeitszeit.md` existiert im Repository-Root.

**Aussage:** Betriebsdokumentation `betriebsdokumentation_arbeitszeit_v1_1.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` existiert.

**Aussage:** VVT `docs/datenschutz/vvt_arbeitszeit_v1.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `docs/datenschutz/vvt_arbeitszeit_v1.md` existiert.

**Aussage:** Rollenzuweisung `docs/betrieb/rollenzuweisung.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `docs/betrieb/rollenzuweisung.md` existiert.

**Aussage:** Hardware-Inbetriebnahmeprotokoll `docs/betrieb/hardware_inbetriebnahme_protokoll.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `docs/betrieb/hardware_inbetriebnahme_protokoll.md` existiert.

**Aussage:** CHANGELOG `CHANGELOG.md` liegt vor.
**Status:** korrekt
**Beleg:** Datei `CHANGELOG.md` existiert im Repository-Root.

Die „Ja/Nein“- und „Bemerkung“-Ankreuzfelder selbst sind organisatorische Formularfelder.
**Status:** nicht zutreffend (organisatorisch)

---

### Abschnitt 3.2: Systemkonfiguration geprüft

**Aussage:** „Datenbankpfad und Rechte korrekt gesetzt“
**Status:** nicht zutreffend (organisatorisch) — reine Prüffrage ohne konkrete technische Detailbehauptung (Ankreuzfeld).

**Aussage:** „`backup.backup_dir` und `export.export_dir` in `system_config` gesetzt“
**Status:** inkorrekt (bezogen auf Seed-Daten) / korrekt (bezogen auf Code-Nutzung)
**Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py`, Funktion `cmd_system_backup` (Zeilen mit `SELECT config_value_json FROM system_config WHERE config_key = 'backup.backup_dir'` bzw. `'export.export_dir'`); `src/arbeitszeit/infrastructure/system_check.py`, `_REQUIRED_CONFIG_KEYS` (enthält `backup.backup_dir` und `export.export_dir`); jedoch: `migrations/0002_seed_defaults.sql` enthält als vorbelegte `system_config`-Einträge nur `app.timezone`, `booking.grace_seconds_after_numpad_select`, `backup.nas_enabled`, `backup.nas_path` — **kein** Seed-Eintrag für `backup.backup_dir` oder `export.export_dir`.
**Bewertung:** Die Aussage, dass diese beiden Schlüssel in `system_config` „gesetzt“ sein müssen, ist technisch korrekt in dem Sinn, dass Code (`system.py`, `system_check.py`) diese Schlüssel erwartet bzw. deren Fehlen als Fehler/FAIL behandelt. Sie sind jedoch **nicht** durch die Standard-Migration vorbelegt und müssen im Betrieb aktiv nachträglich in `system_config` eingetragen werden. Das Protokoll formuliert dies korrekt als Prüfpunkt („gesetzt“ = durch Betreiber zu prüfen), macht aber nicht explizit, dass hierfür kein automatischer Seed existiert. Insgesamt wird die Aussage als **korrekt** eingestuft, da sie als Prüffrage formuliert ist und keine falsche Tatsachenbehauptung über automatische Seed-Vorbelegung enthält.

**Aussage:** „Terminal-IDs sinnvoll vergeben und dokumentiert“
**Status:** nicht zutreffend (organisatorisch) — Formularprüffrage ohne technisch prüfbaren Einzelanspruch.

**Aussage:** „Zeitmonitor (`time_monitor.jump_threshold_seconds`) konfiguriert“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/infrastructure/time_monitor.py`, Funktion `load_threshold_from_config`: liest `SELECT config_value_json FROM system_config WHERE config_key = 'time_monitor.jump_threshold_seconds'` mit Fallback auf `default: float = 60.0`, falls kein Eintrag vorhanden ist.
**Bewertung:** Der Konfigurationsschlüssel existiert exakt unter diesem Namen im Code und wird für den Zeitmonitor verwendet. Hinweis: Dieser Schlüssel ist ebenfalls **nicht** in `migrations/0002_seed_defaults.sql` vorbelegt; der Code verwendet in diesem Fall jedoch einen expliziten Fallback-Wert (60 Sekunden), sodass das Fehlen des Schlüssels nicht zu einem Systemcheck-Fehler führt (er ist auch nicht in `_REQUIRED_CONFIG_KEYS` von `system_check.py` gelistet). Die Aussage im Protokoll ist als Prüffrage korrekt formuliert.

---

### Abschnitt 4.1: Funktionale Tests

**Aussage:** „Admin-CLI | Mitarbeiter-, Benutzer-, Buchungs- und Nachtragsverwaltung“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/employees.py` (Mitarbeiterverwaltung), `user_accounts.py` (Benutzerverwaltung), `bookings.py` (Buchungskorrekturen: `correct`, `supplement`, `approve-supplement`, `reject-supplement` gemäß `register_subcommands`)
**Bewertung:** Alle vier genannten Verwaltungsbereiche sind als eigenständige CLI-Module im Repository vorhanden und funktional voneinander abgegrenzt.

**Aussage:** „Prüf- und Auswertungsfunktionen | Pflichtauswertungen, Warnungen, Prüffälle“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/reports.py`, `register_subcommands`: Subcommands `warn-cases` („WARN/NEEDS_REVIEW-Buchungen anzeigen“), `open-review-cases` („Offene Prüffälle anzeigen“), `open-bookings`, `corrections`, `supplements`
**Bewertung:** Die genannten Funktionsklassen (Warnungen, Prüffälle) sind konkret als CLI-Subcommands in `reports.py` vorhanden.

**Aussage:** „Exporte | CSV- und PDF-Exporte für Stichprobenzeiträume“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/reports.py`: Subcommands `export-csv`, `export-csv-review-cases`, `export-pdf-day`, `export-pdf-week`, `export-pdf-month`, `export-pdf-employee`
**Bewertung:** Sowohl CSV- als auch PDF-Exportfunktionen sind mit mehreren Zeiträumen (Tag/Woche/Monat/Mitarbeiter) im Code belegt.

**Aussage:** „Terminal-UI | Basisbuchungen (Kommen/Gehen/Pause), Anzeige, Fehlermeldungen“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/domain/enums.py`, Klasse `BookingType`: `COME`, `GO`, `BREAK_START`, `BREAK_END`
**Bewertung:** Die genannten Buchungsarten (Kommen/Gehen/Pause-Start/Pause-Ende) entsprechen exakt den im `BookingType`-Enum definierten Werten.

---

### Abschnitt 4.2: Infrastruktur- und Sicherheitstests

**Aussage:** „Systemcheck | `system_check.py` mit produktiver Konfiguration ausgeführt“
**Status:** korrekt
**Beleg:** Datei `src/arbeitszeit/infrastructure/system_check.py` existiert und enthält die Funktion `run_system_check`.
**Bewertung:** Datei- und Funktionsname sind exakt belegt.

**Aussage:** „Backup | Lokales Backup erfolgreich erstellt“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py`, Funktion `cmd_system_backup`, ruft `SQLiteBackupService.create_local_backup()` auf (siehe `src/arbeitszeit/infrastructure/backup/backup_service.py`, Methode `create_local_backup`).
**Bewertung:** Die Funktion zur Erstellung eines lokalen Backups ist im Code klar nachvollziehbar vorhanden.

**Aussage:** „Restore-Test | Testrestore auf Testumgebung erfolgreich“
**Status:** korrekt (Funktionalität existiert), aber ohne CLI-Zugang
**Beleg:** `src/arbeitszeit/infrastructure/backup/backup_service.py`, Methode `restore_from` (Zeile 98 ff.), führt nach dem Restore `PRAGMA integrity_check` aus und protokolliert `RESTORE_COMPLETED` (`src/arbeitszeit/domain/audit_events.py`, Zeile 38). **Wichtiger Zusatzbefund:** `src/arbeitszeit/presentation/admin_cli/system.py` registriert ausschließlich die Subcommands `check` und `backup` (`ssub.add_parser("check", ...)`, `ssub.add_parser("backup", ...)`); ein `restore`-Subcommand ist in der Admin-CLI **nicht vorhanden**.
**Bewertung:** Die Aussage im Protokoll spricht nur allgemein von einem „Testrestore“ ohne einen konkreten CLI-Befehl zu benennen, daher ist sie als Formularprüffrage nicht direkt falsch. Da jedoch potenziell Verwechslungsgefahr besteht (ein Leser könnte einen `arbeitszeit-admin system restore`-Befehl erwarten), wird dies als technischer Hinweis vermerkt: Die Restore-Funktionalität existiert nur programmatisch (`BackupService.restore_from`), nicht als eigenständiger Admin-CLI-Subcommand.

**Aussage:** „NAS (falls verwendet) | Erreichbarkeit, Backup-Sync, Rechte geprüft“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/infrastructure/system_check.py`, Funktion `_check_nas`: prüft `backup.nas_enabled`, `backup.nas_path`, `Path.exists()` sowie `os.access(nas_path, os.W_OK)` (Schreibrecht). Der Kommentar in `_check_nas` stellt klar, dass **kein** aktiver Netzwerk-Ping/TCP-Test durchgeführt wird, sondern nur der Dateisystem-Mount-Punkt geprüft wird.
**Bewertung:** „Erreichbarkeit“ und „Rechte“ sind exakt durch `_check_nas` belegt. „Backup-Sync“ ist durch `SQLiteBackupService.sync_to_nas` (aufgerufen in `cmd_system_backup`) belegt. Die Aussage ist im Kern korrekt; zu beachten ist, dass „Erreichbarkeit“ im Code ausschließlich über Dateisystemzugriff (nicht Netzwerkprotokoll) geprüft wird — dies widerspricht der Protokollaussage aber nicht.

**Aussage:** „Hardware-Smoke-Tests | Siehe `hardware_inbetriebnahme_protokoll.md`“
**Status:** korrekt
**Beleg:** Datei `docs/betrieb/hardware_inbetriebnahme_protokoll.md` existiert im Repository.
**Bewertung:** Verweisziel ist vorhanden.

---

### Abschnitt 4.3: Dokumentierte Tests

**Aussage:** Referenz auf `docs/informelles/testmatrix_pruefbericht_v1.md`
**Status:** inkorrekt
**Beleg:** Datei existiert **nicht** unter `docs/informelles/`. Tatsächlicher Fundort im Repository: `docs/betrieb/nachweise/testmatrix_pruefbericht_v1.md`.
**Bewertung:** Der im Protokoll angegebene Pfad ist falsch; die Datei liegt unter einem anderen Verzeichnis (`docs/betrieb/nachweise/` statt `docs/informelles/`).
**Anpassungsvorschlag:** Pfad korrigieren zu `docs/betrieb/nachweise/testmatrix_pruefbericht_v1.md`.

**Aussage:** Referenz auf `docs/informelles/testmatrix_revision_v1.md`
**Status:** inkorrekt
**Beleg:** Datei existiert **nicht** unter `docs/informelles/`. Tatsächlicher Fundort: `docs/betrieb/nachweise/testmatrix_revision_v1.md`.
**Bewertung:** Gleicher Fehler wie oben — falscher Verzeichnispfad im Protokoll.
**Anpassungsvorschlag:** Pfad korrigieren zu `docs/betrieb/nachweise/testmatrix_revision_v1.md`.

(Hinweis: `docs/informelles/` existiert im Repository, enthält jedoch nur `planung_gesamt.md` und `session_abschluss_und_klarstellungen_2026-06-11.md`, nicht die genannten Testmatrix-Dateien.)

---

### Abschnitt 5: Rollen, Zuständigkeiten und Einweisung

**Aussage:** „Rollen `ADMIN`, `REVIEWER`, `TECH` organisatorisch festgelegt“
**Status:** korrekt
**Beleg:** `src/arbeitszeit/domain/enums.py`, Klasse `UserRole(StrEnum)`: enthält exakt `EMPLOYEE`, `ADMIN`, `REVIEWER`, `TECH`.
**Bewertung:** Alle drei genannten administrativen Rollen (`ADMIN`, `REVIEWER`, `TECH`) sind im Code als gültige Enum-Werte vorhanden. Zusätzlich existiert die im Protokoll nicht erwähnte Rolle `EMPLOYEE`.

**Aussage:** „Rollenzuweisung in `docs/betrieb/rollenzuweisung.md` ausgefüllt“
**Status:** korrekt (Existenz des Verweisziels) / organisatorisch (Ausfüllstatus)
**Beleg:** Datei `docs/betrieb/rollenzuweisung.md` existiert und beschreibt inhaltlich exakt die Rollen `ADMIN`, `REVIEWER`, `TECH` sowie `EMPLOYEE` (Abschnitt „Rollenmodell“ der Datei).
**Bewertung:** Verweisziel korrekt; ob die Datei „ausgefüllt“ ist, ist eine organisatorische Prüffrage.

**Aussage:** „Technische Umsetzung der Rollen im System geprüft“
**Status:** korrekt (technische Umsetzung existiert)
**Beleg:** `src/arbeitszeit/presentation/admin_cli/_auth.py`, Funktionen `require_admin_or_reviewer` und `require_admin_or_tech`: prüfen `role` aus `user_accounts` gegen `("ADMIN", "REVIEWER")` bzw. `("ADMIN", "TECH")`.
**Bewertung:** Die Rollenprüfung ist im Code konkret als Zugriffskontrolle implementiert und belegbar.

Übrige Zeilen (Einweisung ADMIN/REVIEWER/TECH durchgeführt) sind organisatorische Prüffragen ohne technischen Bezug.
**Status:** nicht zutreffend (organisatorisch)

---

### Abschnitt 6: Datenschutz und IT-Sicherheit

Alle Zeilen dieses Abschnitts (VVT erstellt, IT-Sicherheitskonzept, Dateisystemrechte, Backup-Rotation, Datenschutzvorfall-Verfahren) sind als Ja/Nein-Prüffragen mit Bemerkungsfeld formuliert, ohne konkrete, gegen den Code prüfbare technische Einzelbehauptung.
**Status:** nicht zutreffend (organisatorisch)

Hinweis: Der Verweis auf „VVT (Art. 30 DSGVO)“ bezieht sich sachlich korrekt auf die vorhandene Datei `docs/datenschutz/vvt_arbeitszeit_v1.md` (siehe Abschnitt 3.1), diese Existenz wurde dort bereits verifiziert.

---

### Abschnitt 7–11 (Mängel, Erklärung, Unterschriften, Wiederholte Freigabe, Wann erneut verwenden)

Diese Abschnitte bestehen ausschließlich aus Freitextfeldern, Ankreuzoptionen, Unterschriftenfeldern und allgemeinen organisatorischen Kriterien (z. B. „Neue Hauptversion des Systems“, „Wechsel der Hardware-Plattform“) ohne konkrete, im Code nachprüfbare technische Einzelaussage.
**Status:** nicht zutreffend (organisatorisch)

Einzige technisch anknüpfbare Detailaussage:

**Aussage:** „Versionssprung im `pyproject.toml` im MAJOR-Teil (z.B. `0.9.x` → `1.0.0` oder `1.x` → `2.0.0`)“
**Status:** korrekt
**Beleg:** `pyproject.toml`, Zeile 7: `version = "0.1.0"`
**Bewertung:** Der Verweis auf `pyproject.toml` als Ort der Versionsnummer ist korrekt; die aktuelle Version (`0.1.0`) bestätigt, dass das Versionsschema (MAJOR.MINOR.PATCH) im Projekt tatsächlich verwendet wird.

---

### Abschnitt 12: Bezug zu anderen Dokumenten

**Aussage:** Verweis auf `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`
**Status:** korrekt
**Beleg:** Datei existiert im Repository unter genau diesem Pfad.

**Aussage:** Verweis auf `docs/datenschutz/vvt_arbeitszeit_v1.md`
**Status:** korrekt
**Beleg:** Datei existiert im Repository unter genau diesem Pfad.

**Aussage:** Verweis auf `docs/betrieb/rollenzuweisung.md`
**Status:** korrekt
**Beleg:** Datei existiert im Repository unter genau diesem Pfad.

**Aussage:** Verweis auf `docs/betrieb/hardware_inbetriebnahme_protokoll.md`
**Status:** korrekt
**Beleg:** Datei existiert im Repository unter genau diesem Pfad.

**Aussage:** Verweis auf `CHANGELOG.md`
**Status:** korrekt
**Beleg:** Datei existiert im Repository-Root.

**Zusatzbefund (nicht im Dokument selbst benannt, aber im Kontext relevant):** Weitere thematisch verwandte Dokumente wie `docs/betrieb/restore_checkliste.md` und `docs/betrieb/backup_zeitplan_und_automatisierung.md` existieren ebenfalls im Repository, werden jedoch in Abschnitt 12 des Betriebsfreigabe-Protokolls **nicht** als Querverweis aufgeführt, obwohl das Protokoll in Abschnitt 4.2 inhaltlich auf Restore- und Backup-Themen Bezug nimmt.
**Status:** nicht verifizierbar, ob dies eine bewusste Auslassung ist (keine Bewertungsgrundlage im Repository, ob Vollständigkeit der Liste in Abschnitt 12 beabsichtigt war).

---

## Zusammenfassung der Kernbefunde

1. **Falsche Pfadangaben bei Testnachweisen:** Die in Abschnitt 4.3 referenzierten Dateien `testmatrix_pruefbericht_v1.md` und `testmatrix_revision_v1.md` liegen tatsächlich unter `docs/betrieb/nachweise/`, nicht unter dem im Protokoll genannten `docs/informelles/`. Dies ist der einzige klar belegte inhaltliche Fehler im Dokument.
2. **CLI-Rollenlogik korrekt abgebildet:** Die Rollen `ADMIN`, `REVIEWER`, `TECH` sind exakt im `UserRole`-Enum (`src/arbeitszeit/domain/enums.py`) sowie in der Zugriffskontrolle (`_auth.py`) belegt; die Rolle `EMPLOYEE` bleibt im Protokoll unerwähnt, was aber sachlich nicht falsch ist, da diese Rolle nicht Teil der administrativen Rollen ist.
3. **Systemcheck- und Backup/Restore-Aussagen sind konsistent zum Code**, mit der Präzisierung, dass Restore-Funktionalität (`BackupService.restore_from`) im Repository existiert, aber **kein** eigenständiger `restore`-Subcommand in der Admin-CLI (`system.py`, nur `check`/`backup`) vorhanden ist.
4. **Konfigurationsschlüssel `backup.backup_dir`, `export.export_dir` und `time_monitor.jump_threshold_seconds`** werden zwar im Code (`system.py`, `system_check.py`, `time_monitor.py`) verwendet bzw. als Pflichtschlüssel (`_REQUIRED_CONFIG_KEYS`) geprüft, sind aber **nicht** durch die Standard-Seed-Migration (`migrations/0002_seed_defaults.sql`) vorbelegt und müssen operativ nachgetragen werden — das Protokoll formuliert dies korrekt als Prüfpunkt, ohne diesen Unterschied explizit zu benennen.
5. **Alle in Abschnitt 12 gelisteten Dokumentverweise existieren** tatsächlich im Repository unter den angegebenen Pfaden; das Dokument ist in seiner Grundstruktur überwiegend organisatorisch und enthält im Verhältnis zum Umfang wenige, aber überwiegend korrekte technische Einzelaussagen.
