# Handbuch `arbeitszeit` – Presentation

**Kapitel:** 4
**Version:** 1.1
**Stand:** Juli 2026
**Quelldatei:** `docs/02_anwender/module/handbuch_presentation.md`

## Zweck

Die Präsentationsschicht bündelt die Benutzerschnittstellen des Systems.
Im Repository ist sie unter `src/arbeitszeit/presentation/` organisiert und
enthält zwei getrennte Oberflächen: `admin_cli` und `terminal_ui`.

Diese Trennung ist nicht nur eine Verzeichnisstruktur, sondern Teil des
architektonischen Schichtenmodells. In `pyproject.toml` ist die
Präsentationsschicht ausdrücklich als oberste Ebene der konfigurierten
Layer-Struktur hinterlegt.

## Aufbau

Unter `src/arbeitszeit/presentation/` sind folgende Teilbereiche belegt:

| Pfad | Aufgabe |
| --- | --- |
| `src/arbeitszeit/presentation/admin_cli/` | Administrative Kommandozeilenschnittstelle |
| `src/arbeitszeit/presentation/terminal_ui/` | Operative Terminaloberfläche für Buchungen |

Die Präsentationsschicht enthält damit zwei unterschiedliche Zugangswege zum
System. Die Admin-CLI ist auf Verwaltung und Auswertung ausgelegt, während die
Terminal-UI für den laufenden Buchungsbetrieb mit Eingabegeräten vorgesehen
ist.

## Admin-CLI

Der Einstiegspunkt der administrativen Oberfläche liegt in
`src/arbeitszeit/presentation/admin_cli/main.py`. Das Modul definiert eine
Argumentstruktur mit den globalen Optionen `--config`, `--db` und `--user-id`
sowie eine Unterbefehlsstruktur über `argparse`.

Registriert werden Unterbefehle aus den Modulen `employees`, `bookings`,
`schedule`, `reports`, `system` und `user_accounts`. Die Befehlsausführung
wird in `_dispatch()` über eine Zuordnungstabelle auf konkrete Handlerfunktionen
abgebildet.

## Auflösung der Eingaben

Die Admin-CLI lädt eine optionale `config.toml` über `_load_app_config()`.
Dabei wird entweder ein explizit übergebener Pfad verwendet oder eine Datei
über `find_config()` gesucht.

Für den Datenbankpfad gilt laut `_resolve_db_path()` die Reihenfolge:
CLI-Argument `--db`, danach `config.toml`. Für die Benutzer-ID gilt laut
`_resolve_user_id()` die Reihenfolge: `--user-id`, dann Umgebungsvariable
`ADMIN_USER_ID`, dann `config.toml`; fehlt danach weiterhin ein Wert, beendet
sich das Programm mit einer Fehlermeldung.

## Startverhalten der Admin-CLI

Nach dem Parsen der Argumente lädt `run()` zunächst die Konfiguration und
ermittelt den Datenbankpfad. Anschließend wird für fast alle Befehle eine
Datenbankverbindung geöffnet, `run_migrations(conn)` ausgeführt und danach die
jeweilige Operation gestartet.

Eine Sonderbehandlung existiert für `users bootstrap`. Dieser Pfad benötigt
laut Kommentar keine Benutzer-ID, weil es zu diesem Zeitpunkt noch keinen
Administrator geben kann. Auch in diesem Fall werden jedoch Migrationen vor der
Befehlsausführung gestartet.

## Themenbereiche der Admin-CLI

Aus `main.py` ergeben sich folgende Themenbereiche mit belegten Befehlen:

| Bereich | Belegte Befehle |
| --- | --- |
| `employees` | `list`, `add`, `deactivate` |
| `cards` | `assign`, `replace`, `deactivate` |
| `bookings` | `correct`, `supplement`, `approve-supplement`, `reject-supplement` |
| `schedule` | `set`, `show` |
| `reports` | `export-csv`, `export-csv-review-cases`, `export-pdf-day`, `export-pdf-week`, `export-pdf-month`, `export-pdf-employee`, `open-bookings`, `warn-cases`, `corrections`, `supplements`, `open-review-cases` |
| `system` | `check`, `backup`, `setup` |
| `users` | `add`, `list`, `deactivate`, `reactivate`, `change-role`, `bootstrap` |

Die Präsentationsschicht der Admin-CLI bildet damit einen breiten Teil der
administrativen Bedienung ab. Die Befehle selbst liegen in getrennten Modulen,
werden aber zentral über `main.py` verbunden.

## Terminal-UI

Der Einstiegspunkt des Terminalbetriebs liegt in
`src/arbeitszeit/presentation/terminal_ui/main.py`. Das Modul beschreibt sich
selbst als Einstiegspunkt für die Endlosschleife des operativen
Buchungsbetriebs.

Die Kommandozeilenparameter sind `--config`, `--db`, `--numpad`, `--rfid` und
`--terminal-id`. Die Werte werden nach dem Laden einer optionalen
`config.toml` mit `_resolve_or_exit()` in der Priorität CLI-Wert vor
Konfigurationswert aufgelöst; fehlt ein Pflichtwert, wird das Programm mit
Fehlerausgabe beendet.

## Ablauf des Terminalbetriebs

Die Funktion `run()` ist der zentrale Ablauf der Terminaloberfläche. Vor dem
Start der Endlosschleife werden zunächst die Eingabegeräte über
`resolve_evdev_device()` aufgelöst.

Danach wird `run_system_check()` ausgeführt. Wenn der Systemcheck Fehler
meldet, wird zwar eine Warnung ausgegeben und eine Benachrichtigung ausgelöst,
der Buchungsbetrieb wird jedoch laut Kommentar ausdrücklich nicht mit
`sys.exit()` blockiert.

## Initialisierung im Terminalbetrieb

Vor dem eigentlichen Buchungszyklus werden weitere Systemschritte ausgeführt:

- `_ensure_terminal_exists()` legt den Terminaleintrag in der Tabelle
  `terminals` bei Bedarf mit `INSERT OR IGNORE` an.
- `_setup_file_logging()` richtet dateibasiertes Logging ein.
- `load_threshold_from_config(db_path)` liefert den Schwellwert für die
  Zeitüberwachung.
- `SQLiteSystemConfigRepository(...).get_current(...)` liest den Wert für
  `booking.grace_seconds_after_numpad_select`.
- `EvdevHardwareReader(...)` wird mit Numpad-, RFID- und Timeoutwerten
  initialisiert.

Diese Initialisierung zeigt, dass die Terminal-UI nicht nur eine Eingabeschicht
ist, sondern mehrere Infrastrukturbausteine orchestriert.

## Buchungsschleife

Im laufenden Betrieb verarbeitet die Endlosschleife wiederholt
`_run_one_cycle(...)`. Dabei wird zuerst `monitor.check()` aufgerufen und danach
`process_booking(reader, db_path, terminal_id)` ausgeführt.

Das Ergebnis einer erfolgreichen Buchung wird über `format_feedback(...)`
ausgegeben. Für mehrere Domänenfehler sind feste Benutzermeldungen hinterlegt,
unter anderem für unbekannte Karten, deaktivierte Karten, inaktive
Mitarbeitende, ungültige Buchungsfolgen und offene Phasenkonflikte.

## Fehlerbehandlung und Signale

Nicht behandelte Ausnahmen innerhalb eines Buchungszyklus führen nicht zum
sofortigen Abbruch der Endlosschleife. Stattdessen wird eine Fehlermeldung auf
`stderr` ausgegeben, ein Stacktrace protokolliert und über `_log_system_event()`
ein Eintrag in `system_events` geschrieben.

Für den kontrollierten Stopp registriert `run()` Handler für `SIGTERM` und
`SIGINT`. Die Schleife läuft dabei nur solange die lokale Variable `running`
auf `True` steht; beim Signalempfang wird sie auf `False` gesetzt.

## Beteiligte Module

Aus der Präsentationsschicht sind folgende Dateien unmittelbar belegt:

| Pfad | Rolle |
| --- | --- |
| `src/arbeitszeit/presentation/admin_cli/main.py` | zentraler Einstiegspunkt der Admin-CLI |
| `src/arbeitszeit/presentation/admin_cli/employees.py` | Mitarbeitenden- und Kartenbefehle |
| `src/arbeitszeit/presentation/admin_cli/bookings.py` | Buchungskorrekturen und Ergänzungen |
| `src/arbeitszeit/presentation/admin_cli/schedule.py` | Dienstplanfunktionen |
| `src/arbeitszeit/presentation/admin_cli/reports.py` | Berichte und Exporte |
| `src/arbeitszeit/presentation/admin_cli/system.py` | Systemfunktionen |
| `src/arbeitszeit/presentation/admin_cli/user_accounts.py` | Benutzerkontenverwaltung |
| `src/arbeitszeit/presentation/admin_cli/_auth.py` | unterstützende Authentifizierungslogik |
| `src/arbeitszeit/presentation/admin_cli/_intervals.py` | Hilfslogik für Intervalle |
| `src/arbeitszeit/presentation/terminal_ui/main.py` | Einstiegspunkt des Terminalbetriebs |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | Ablauf der einzelnen Buchungszyklen |

Die Präsentationsschicht ist damit nicht auf reine Befehlsdefinitionen
reduziert. Sie enthält sowohl die äußeren Einstiegspunkte als auch
bedienungsnahe Ablaufsteuerung.

## Einordnung

Die im Repository belegte Präsentationsschicht dient als Übersetzer zwischen
Benutzereingaben und den tieferen Schichten des Systems. Sowohl die Admin-CLI
als auch die Terminal-UI greifen auf Anwendungs-, Infrastruktur- und
Domänenmodule zu, bleiben dabei aber als separate Benutzerschnittstellen
organisiert.

Nicht belegt ist in dieser Schicht eine grafische Desktop- oder
Weboberfläche. Die vorhandenen Präsentationsmodule sind ausschließlich auf
Kommandozeile und terminalnahen Betrieb ausgerichtet.
