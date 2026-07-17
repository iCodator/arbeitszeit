# Infrastrukturschicht — technisches Referenzhandbuch

**Kapitel:** 6-IT
**Version:** 1.0
**Stand:** Juli 2026
**Zielgruppe:** Entwickler, Systemverantwortliche
**Quelldateien:** `src/arbeitszeit/infrastructure/`

## Zweck der Infrastrukturschicht

Die Infrastrukturschicht enthält alle technischen Adapter: Datenbankzugriff,
RFID/Numpad-Hardware, Konfigurationsdatei, Backup, Systemprüfung und
Zeitüberwachung. Sie implementiert die Repository-Protokolle der Domänenschicht
und liegt im Schichtenmodell zwischen Anwendung und Präsentation.

## Verzeichnisstruktur

```text
src/arbeitszeit/infrastructure/
├── backup/
│   └── backup_service.py
├── db/
│   ├── connection.py
│   ├── migrations.py
│   └── repositories.py
├── export/
│   └── report_queries.py
├── hardware/
│   └── evdev_reader.py
├── config_file.py
├── config_setup.py
├── notification.py
├── system_check.py
└── time_monitor.py
```

## Konfigurationsdatei

Quelldatei: `src/arbeitszeit/infrastructure/config_file.py`

### Dataklassen

| Klasse | Felder |
| --- | --- |
| `DatabaseConfig` | `path: str \| None` |
| `TerminalConfig` | `id: int \| None`, `numpad: str \| None`, `rfid: str \| None` |
| `BackupConfig` | `backup_dir: str \| None`, `export_dir: str \| None`, `log_dir: str \| None` |
| `AdminConfig` | `user_id: int \| None` |
| `AppConfig` | database, terminal, backup, admin |

### Suchpfad von find_config()

1. Umgebungsvariable `ARBEITSZEIT_CONFIG`
2. `~/.config/arbeitszeit/config.toml`
3. `./config.toml` (Working-Directory)

`find_config()` gibt den ersten existierenden Pfad zurück oder `None`.

### Laden und Schreiben

- `load_config(path)` — liest via `tomllib`, gibt `AppConfig` zurück
- `write_config(path, config)` — schreibt alle gesetzten Felder zurück

`find_config()` wird in Admin-CLI, Terminal-UI und `show_config.py`
genutzt, um die Konfigurationsdatei ohne expliziten Pfad zu finden.

### TOML-Struktur

```toml
[database]
path = "/var/data/arbeitszeit.db"

[terminal]
id = 1
numpad = "Usb KeyBoard Usb KeyBoard"
rfid = "Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader"

[backup]
backup_dir = "/var/backups/arbeitszeit"
export_dir = "/var/exports/arbeitszeit"
log_dir = "/var/log/arbeitszeit"

[admin]
# user_id = 1  # optional; Fallback für --user-id / ADMIN_USER_ID
```

## Datenbankinfrastruktur

Quelldatei: `src/arbeitszeit/infrastructure/db/`

### Verbindung

`connection.open_connection(path)` öffnet eine SQLite-Verbindung.
`PRAGMA foreign_keys = ON` muss pro Verbindung aktiviert werden — das
PRAGMA ist in SQLite verbindungsweit, nicht persistent.

### Migrationen

`migrations.run_migrations(conn)` wendet alle ausstehenden SQL-Dateien aus
`migrations/` an und trägt sie in `schema_migrations` ein. Die Admin-CLI
führt Migrationen bei jedem Start vor der Befehlsausführung aus.

### SQLite-Repositories (11 Klassen)

Quelldatei: `src/arbeitszeit/infrastructure/db/repositories.py`

Alle Klassen implementieren die gleichnamigen Protokollklassen aus
`domain/ports/repositories.py`.

| Klasse | Protokoll |
| --- | --- |
| `SQLiteEmployeeRepository` | `EmployeeRepository` |
| `SQLiteUserAccountRepository` | `UserAccountRepository` |
| `SQLiteRfidCardRepository` | `RfidCardRepository` |
| `SQLiteTimeBookingRepository` | `TimeBookingRepository` |
| `SQLiteWorkScheduleRepository` | `WorkScheduleRepository` |
| `SQLiteReviewCaseRepository` | `ReviewCaseRepository` |
| `SQLiteSupplementRepository` | `SupplementRepository` |
| `SQLiteBookingCorrectionRepository` | `BookingCorrectionRepository` |
| `SQLiteAuditLogRepository` | `AuditLogRepository` |
| `SQLiteDeviceEventRepository` | `DeviceEventRepository` |
| `SQLiteSystemConfigRepository` | `SystemConfigRepository` |

`SQLiteAuditLogRepository.add()` verwendet eine separate Autocommit-Verbindung,
damit Audit-Einträge auch bei Rollback der Haupttransaktion erhalten bleiben.

`SQLiteTimeBookingRepository.list_for_employee_on_day()` muss chronologisch
sortierte Ergebnisse liefern — Compliance-Checks und Sequenzprüfung setzen
das voraus.

### Read-Abfragen

`infrastructure/export/report_queries.py` enthält die SQL-Logik für die
Read-Seite (CQRS). Die Ergebnisse werden als `BookingRow`, `CorrectionRow`,
`SupplementRow` und `ReviewCaseRow` (definiert in `application/queries.py`)
zurückgegeben.

## Hardwareanbindung

Quelldatei: `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`

| Symbol | Aufgabe |
| --- | --- |
| `EvdevHardwareReader` | liest Ereignisse von Numpad und RFID-Reader via `evdev` |
| `resolve_evdev_device(name)` | sucht ein `/dev/input/event*`-Gerät anhand des Namens |
| `HardwareReader` | Protokollklasse (Port der Domänenschicht) |
| `DeviceNotFoundError` | ausgelöst wenn das Gerät nicht gefunden wird |

Die Terminal-UI initialisiert `EvdevHardwareReader` mit Numpad-Pfad,
RFID-Pfad und einem Timeout-Wert aus `system_config`.

## Backup-Service

Quelldatei: `src/arbeitszeit/infrastructure/backup/backup_service.py`

### create_local_backup()

- Nutzt die SQLite Backup-API (`sqlite3.Connection.backup()`) — die DB bleibt
  während des Backups lesbar und schreibbar (Online-Backup)
- Dateiname: `arbeitszeit_<UTC-Zeitstempel>.db`
- Kopiert optional das Export-Verzeichnis in das Backup-Verzeichnis

### sync_to_nas()

- Ruft `/usr/bin/rsync --archive --delete` auf
- Bei Fehler: Audit-Log-Eintrag schreiben und Exception re-raisen
- Das lokale Backup ist zu diesem Zeitpunkt bereits vollständig

### restore_from(backup_path)

- Nutzt ebenfalls die SQLite Backup-API (in umgekehrter Richtung)
- Führt nach dem Restore `PRAGMA integrity_check` durch

### run()

- Führt `create_local_backup()` und ggf. `sync_to_nas()` aus
- Gibt `BackupResult` zurück

## Systemprüfung

Quelldatei: `src/arbeitszeit/infrastructure/system_check.py`

`run_system_check(db_path, *, numpad_path, rfid_path, app_config)` führt
7 Prüfungen aus und schreibt `SELFTEST_OK` oder `SELFTEST_FAIL` in die
Tabelle `system_events`.

| Prüfung | Beschreibung |
| --- | --- |
| `_check_db_access` | Vergleicht `schema_migrations`-Tabelle mit `.sql`-Dateien in `migrations/` |
| `_check_config_keys` | Prüft 4 Pflicht-Keys: `app.timezone`, `booking.grace_seconds_after_numpad_select`, `backup.nas_enabled`, `backup.nas_path` |
| `_check_nas` | Prüft `Path.exists()` und `os.access(W_OK)` — kein Netzwerktest |
| `_check_fk_consistency` | Führt `PRAGMA foreign_key_check` aus |
| `_check_config_file_paths` | Prüft, ob `backup_dir` und `export_dir` existieren |
| `_check_ntp` | Führt `/usr/bin/timedatectl show` aus (absoluter Pfad, kein `shell=True`), timeout 5 s; prüft `NTP=yes` und `NTPSynchronized=yes` |
| `_check_devices` | Prüft `Path.exists()` und `os.access(R_OK)` für `numpad_path` und `rfid_path` |

Die Terminal-UI führt `run_system_check()` vor dem Start der Buchungsschleife
aus. Bei Fehlern wird eine Warnung ausgegeben; der Buchungsbetrieb wird
**nicht** mit `sys.exit()` blockiert.

## Zeitüberwachung

Quelldatei: `src/arbeitszeit/infrastructure/time_monitor.py`

`SystemTimeMonitor` überwacht die Systemzeit während des Terminalbetriebs.
`load_threshold_from_config(db_path)` liest den Schwellwert aus der Datenbank.
`monitor.check()` wird einmal vor der Schleife und danach vor jedem
Buchungszyklus aufgerufen.

## Logging und Benachrichtigung

- `_setup_file_logging()` in der Terminal-UI richtet dateibasiertes Logging ein.
  Primärquelle für `log_dir` ist `config.toml`; bei fehlendem Wert wird als
  Fallback `logging.log_dir` aus `system_config` gelesen.
- `notification.py` — wird bei kritischen Meldungen (Geräte nicht gefunden,
  Systemfehler) ausgelöst.
- Nicht behandelte Ausnahmen in einem Buchungszyklus führen zu einem Eintrag in
  `system_events` via `_log_system_event()`.
