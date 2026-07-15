# Handbuch `arbeitszeit` – Infrastructure

**Kapitel:** 6
**Version:** 1.1
**Stand:** Juli 2026
**Quelldatei:** `docs/02_anwender/module/handbuch_infrastructure.md`

## Zweck

Die Infrastrukturschicht enthält die technischen Implementierungen für
Konfiguration, Datenbank, Hardware, Export, Backup, Benachrichtigung,
Systemprüfung und Zeitüberwachung. Im Repository liegt sie unter
`src/arbeitszeit/infrastructure/`.

Im Schichtenmodell aus `pyproject.toml` befindet sich die Infrastruktur
zwischen Präsentation und Anwendung. Sie stellt damit konkrete technische
Adapter und Laufzeitdienste für die übrigen Schichten bereit.

## Aufbau

Unter `src/arbeitszeit/infrastructure/` sind folgende Bereiche belegt:

| Pfad | Aufgabe |
| --- | --- |
| `backup/` | Backup-Logik |
| `config_file.py` | Laden, Suchen und Schreiben der `config.toml` |
| `config_setup.py` | Unterstützende Logik für die Konfigurationseinrichtung |
| `db/` | Datenbankverbindung, Migrationen, Repositories und Datenzugriff |
| `export/` | Export- und Berichtsfunktionen |
| `hardware/` | Gerätezugriff und Hardwareports |
| `notification.py` | Benachrichtigungen |
| `system_check.py` | Systemprüfung |
| `time_monitor.py` | Überwachung der Systemzeit |

Diese Struktur zeigt, dass die Infrastrukturschicht nicht nur den
Datenbankzugriff enthält. Sie bündelt vielmehr die technischen
Außenbeziehungen und betrieblichen Hilfsdienste des Systems.

## Konfigurationsdatei

Die zentrale Unterstützung für `config.toml` ist in
`src/arbeitszeit/infrastructure/config_file.py` implementiert. Das Modul
definiert die Dataklassen `DatabaseConfig`, `TerminalConfig`, `BackupConfig`,
`AdminConfig` und `AppConfig`.

Die Suchfunktion `find_config()` prüft nacheinander die Umgebungsvariable
`ARBEITSZEIT_CONFIG`, den Pfad `~/.config/arbeitszeit/config.toml` und eine
lokale Datei `./config.toml`. Das Laden erfolgt über `load_config(...)` mit
`tomllib`; das Schreiben erfolgt über `write_config(...)`.

## Struktur der `config.toml`

Aus `_parse(...)`, `_terminal_section(...)`, `_backup_section(...)` und
`write_config(...)` ergeben sich folgende belegte Konfigurationsbereiche:

| Abschnitt | Felder |
| --- | --- |
| `[database]` | `path` |
| `[terminal]` | `id`, `numpad`, `rfid` |
| `[backup]` | `backup_dir`, `export_dir`, `log_dir` |
| `[admin]` | `user_id` |

Die Datei `config.toml.example` bestätigt dieselbe Grundstruktur und enthält
zusätzlich kommentierte Hinweise zur Suchreihenfolge und zum optionalen Feld
`admin.user_id`.

## Datenbankinfrastruktur

Ein eigener Datenbankbereich ist unter `src/arbeitszeit/infrastructure/db/`
vorhanden. Bereits aus den Importen in `show_config.py`, `terminal_ui/main.py`
und `admin_cli/main.py` sind mindestens `connection.open_connection`,
`migrations.run_migrations` und `repositories.SQLiteSystemConfigRepository`
belegt.

Die Datenbankverbindung wird in mehreren Laufzeitpfaden explizit geöffnet und
wieder geschlossen. Dazu zählen Konfigurationsanzeigen, Migrationen,
Systeminitialisierung, Logging-Fallbacks sowie das Lesen technischer
Systemparameter.

## Migrationen und Initialisierung

Die Admin-CLI führt vor der eigentlichen Befehlsausführung `run_migrations(conn)`
aus. Damit ist belegt, dass Datenbankschemaänderungen nicht nur über separate
Skripte, sondern auch beim Start administrativer Arbeitsabläufe berücksichtigt
werden.

Zusätzlich existieren im Repository ein Verzeichnis `migrations/` sowie das
Hilfsskript `scripts/init_db.py`. Daraus ist eine eigenständige
Migrations- und Initialisierungsinfrastruktur ableitbar, auch wenn dieses
Kapitel nicht jede einzelne Migrationsdatei im Detail behandelt.

## Hardwareanbindung

Für die Hardware ist ein eigener Bereich unter
`src/arbeitszeit/infrastructure/hardware/` vorhanden. Aus
`terminal_ui/main.py` sind die Komponenten `EvdevHardwareReader`,
`resolve_evdev_device`, `DeviceNotFoundError` und der Porttyp
`HardwareReader` belegt.

Die Hardwareinfrastruktur dient dem Zugriff auf Numpad- und RFID-Geräte.
Bereits aus der Initialisierung der Terminal-UI ist ersichtlich, dass Geräte
entweder über Namen oder über evdev-Bezug aufgelöst und anschließend in einen
konkreten Reader überführt werden.

## Logging und Benachrichtigung

Die Datei `notification.py` ist als eigener Infrastrukturbaustein vorhanden und
wird in der Terminal-UI für kritische Meldungen verwendet. Benachrichtigungen
werden dort bei nicht gefundenen Geräten sowie bei Systemfehlern ausgelöst.

Für dateibasiertes Logging enthält `_setup_file_logging()` in der Terminal-UI
die technische Anbindung an die Infrastruktur. Als Primärquelle für das
Logverzeichnis dient `config.toml`; falls dort kein Wert gesetzt ist, wird als
Rückwärtskompatibilitäts-Fallback der neueste Eintrag mit dem Schlüssel
`logging.log_dir` aus `system_config` gelesen.

## Systemprüfung

Die Datei `src/arbeitszeit/infrastructure/system_check.py` ist als eigener
Prüfbaustein vorhanden und wird sowohl von der Terminal-UI als auch indirekt
über die Systembefehle der Admin-CLI genutzt. In der Terminal-UI wird
`run_system_check(...)` vor Beginn des laufenden Betriebs ausgeführt.

Das Ergebnisobjekt wird dort über `result.overall_ok` und `result.checks`
ausgewertet. Bei Fehlern werden Name und Detail der einzelnen Prüfungen
verwendet, um Warnungen für den Betrieb auszugeben.

## Zeitüberwachung

Mit `src/arbeitszeit/infrastructure/time_monitor.py` ist eine eigene
Infrastruktur für Systemzeitüberwachung vorhanden. In der Terminal-UI werden
`SystemTimeMonitor` und `load_threshold_from_config(db_path)` importiert und
verwendet.

Vor dem laufenden Betrieb wird ein Monitor mit einem konfigurierten
Schwellwert initialisiert. Danach wird `monitor.check()` sowohl einmal zur
Initialisierung als auch vor jedem Buchungszyklus aufgerufen.

## Export und Berichte

Das Verzeichnis `src/arbeitszeit/infrastructure/export/` ist im Repository
vorhanden. Seine Existenz wird zusätzlich durch die in der Admin-CLI belegten
Berichtsbefehle für CSV- und PDF-Export funktional gestützt.

Konkrete Exportbefehle in der Präsentationsschicht sind unter anderem
`export-csv`, `export-csv-review-cases`, `export-pdf-day`, `export-pdf-week`,
`export-pdf-month` und `export-pdf-employee`. Daraus ist ableitbar, dass die
Infrastrukturschicht die technischen Exportmittel für diese Ausgaben
bereitstellt.

## Backup

Ein eigener Infrastrukturbereich `src/arbeitszeit/infrastructure/backup/` ist
vorhanden. Zusätzlich existiert mit `scripts/backup.py` ein separates Skript,
das auf eine nutzbare Backup-Infrastruktur im Paketbestand verweist.

In der Konfigurationsstruktur sind für Backups und angrenzende Betriebsdaten
die Felder `backup.backup_dir`, `backup.export_dir` und `backup.log_dir`
belegt. Damit ist die Infrastrukturschicht auch Träger relevanter
Pfadkonfigurationen für Sicherung, Export und Protokollierung.

## Zusammenspiel mit anderen Schichten

Die Infrastrukturschicht wird von der Präsentationsschicht in mehreren
kritischen Laufzeitpfaden direkt verwendet. Dazu gehören insbesondere
Konfigurationsauflösung, Datenbankzugriff, Migrationen, Systemchecks,
Benachrichtigungen, Hardwareinitialisierung und Zeitüberwachung.

Gleichzeitig zeigt die konfigurierte Schichtenreihenfolge in `pyproject.toml`,
dass diese technische Implementierungsschicht unterhalb der Präsentation und
oberhalb von Anwendung und Domäne verortet ist. Sie stellt damit die konkrete
technische Ausführung für fachliche und bedienungsnahe Abläufe bereit.

## Abgrenzung

Dieses Kapitel beschreibt ausschließlich die nachweisbar vorhandenen
Infrastrukturbausteine des Repository-Stands. Es beschreibt keine externen
Cloud-Dienste, keine Web-Backends und keine verteilte Infrastruktur, weil dafür
im eingelesenen Repository keine belastbare technische Grundlage belegt ist.

Ebenso werden hier keine weitergehenden Betriebsversprechen formuliert, die
nicht unmittelbar aus Quellcode, Paketstruktur oder Konfigurationsdateien
ableitbar sind. Wo nur die Existenz eines Bereichs oder die Verwendung über
Importe und Aufrufe belegt ist, bleibt die Beschreibung entsprechend auf diesen
nachweisbaren Umfang beschränkt.
