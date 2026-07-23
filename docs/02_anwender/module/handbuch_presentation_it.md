# Präsentationsschicht — technisches Referenzhandbuch

**Kapitel:** 4-IT
**Version:** 1.3
**Stand:** Juli 2026
**Zielgruppe:** Entwickler, Systemverantwortliche
**Quelldateien:** `src/arbeitszeit/presentation/`

## Zweck der Präsentationsschicht

Die Präsentationsschicht ist die oberste Schicht im Schichtenmodell
(`presentation > infrastructure > application > domain`). Sie enthält
die beiden Benutzerschnittstellen: Admin-CLI und Terminal-UI.

## Verzeichnisstruktur

```text
src/arbeitszeit/presentation/
├── admin_cli/
│   ├── main.py         # Einstiegspunkt, Argument-Routing
│   ├── _auth.py        # Authentifizierungslogik
│   ├── _intervals.py   # Hilfsfunktionen für Zeitintervalle
│   ├── audit.py        # Audit-Abfragen (z. B. open-shifts)
│   ├── bookings.py     # Korrekturen und Nachträge
│   ├── employees.py    # Mitarbeitende und RFID-Karten
│   ├── reports.py      # Berichte und Exporte
│   ├── schedule.py     # Dienstplan
│   ├── system.py       # Systemfunktionen
│   └── user_accounts.py # Benutzerkonten
└── terminal_ui/
    ├── main.py         # Einstiegspunkt der Buchungsschleife
    └── booking_loop.py # Ablauf einzelner Buchungszyklen
```

## Admin-CLI

Einstiegspunkt: `src/arbeitszeit/presentation/admin_cli/main.py`

Aufruf ohne `[project.scripts]`-Eintrag:

```bash
python -m arbeitszeit.presentation.admin_cli.main [global] <bereich> <befehl> [args]
```

Empfohlener Alias:

```bash
alias azadmin='python -m arbeitszeit.presentation.admin_cli.main'
```

### Globale Optionen

| Option | Beschreibung |
| --- | --- |
| `--config PATH` | expliziter Pfad zur `config.toml` |
| `--db PATH` | expliziter Datenbankpfad |
| `--user-id INT` | Admin-Benutzer-ID |
| `--admin-password PASSWORT` | Admin-Passwort (Standard: interaktive Eingabe via `getpass`) |

### Auflösungsreihenfolge

**Datenbankpfad** (`_resolve_db_path()`):

1. `--db`-Argument
2. `config.toml [database] path`

**Benutzer-ID** (`_resolve_user_id()`):

1. `--user-id`-Argument
2. Umgebungsvariable `ADMIN_USER_ID`
3. `config.toml [admin] user_id`

Fehlt die Benutzer-ID nach allen drei Stufen, bricht die CLI mit
Fehlermeldung ab.

### Startverhalten

`run()` lädt Konfiguration, löst den Datenbankpfad auf, öffnet die
Verbindung und führt `run_migrations(conn)` vor jeder Befehlsausführung aus.

`users bootstrap` ist der einzige Befehl, der keine `--user-id` benötigt
(es gibt zu diesem Zeitpunkt noch keinen Administrator).

### Befehlsübersicht

#### employees

| Befehl | Beschreibung | Use Case |
| --- | --- | --- |
| `employees list` | Alle Mitarbeitenden auflisten | — (Read) |
| `employees add` | Neuen Mitarbeitenden anlegen | `CreateEmployeeUseCase` |
| `employees deactivate` | Mitarbeitenden deaktivieren | `DeactivateEmployeeUseCase` |

Beispiel:

```bash
azadmin employees add --personnel-no 042 --first-name Anna --last-name Muster
```

#### cards

| Befehl | Beschreibung | Use Case |
| --- | --- | --- |
| `cards assign` | RFID-Karte zuweisen | `AssignRfidCardUseCase` |
| `cards replace` | RFID-Karte ersetzen | `ReplaceRfidCardUseCase` |
| `cards deactivate` | RFID-Karte deaktivieren | `DeactivateRfidCardUseCase` |

Beispiel:

```bash
azadmin cards assign --employee-id 3 --uid-hash abc123def456
```

#### bookings

| Befehl | Beschreibung | Use Case |
| --- | --- | --- |
| `bookings correct` | Buchung korrigieren | `CorrectBookingUseCase` |
| `bookings supplement` | Nachtrag anlegen | `RegisterSupplementUseCase` |
| `bookings approve-supplement` | Nachtrag genehmigen | `ApproveSupplementUseCase` |
| `bookings reject-supplement` | Nachtrag ablehnen | `RejectSupplementUseCase` |

Beispiel:

```bash
azadmin bookings correct --booking-id 17 \
  --type GO --at "15.07.2026 17:30" --reason "Falsche Uhrzeit"
```

#### schedule

| Befehl | Beschreibung | Use Case |
| --- | --- | --- |
| `schedule set` | Dienstplan-Eintrag setzen | `ManageWorkScheduleUseCase` |
| `schedule show` | Aktuellen Dienstplan anzeigen | — (Read) |

Beispiel:

```bash
azadmin schedule set --weekday 1 --start 07:30 --end 18:00 --from 01.08.2026
```

#### reports

| Befehl | Beschreibung |
| --- | --- |
| `reports export-csv` | Buchungen als CSV exportieren |
| `reports export-csv-review-cases` | Prüffälle als CSV exportieren |
| `reports export-pdf-day` | Tagesbericht als PDF |
| `reports export-pdf-week` | Wochenbericht als PDF |
| `reports export-pdf-month` | Monatsbericht als PDF |
| `reports export-pdf-employee` | Mitarbeiterbericht als PDF |
| `reports open-bookings` | Offene Buchungsphasen anzeigen |
| `reports warn-cases` | Buchungen mit WARN-Status anzeigen |
| `reports corrections` | Korrekturen anzeigen |
| `reports supplements` | Nachträge anzeigen |
| `reports open-review-cases` | Offene Prüffälle anzeigen |

Beispiel:

```bash
azadmin reports export-pdf-month --year 2026 --month 7
```

Der Ausgabepfad wird aus dem `export_dir`-Eintrag in `config.toml` bestimmt.

#### system

| Befehl | Beschreibung |
| --- | --- |
| `system check` | Systemprüfung ausführen (8 Checks) |
| `system backup` | Backup erstellen und optional auf NAS synchronisieren |
| `system setup` | Konfiguration einrichten |

Beispiel:

```bash
azadmin system check --db arbeitszeit.db
azadmin system backup --db arbeitszeit.db
```

#### users

| Befehl | Beschreibung | Use Case |
| --- | --- | --- |
| `users add` | Benutzerkonto anlegen | `CreateUserAccountUseCase` |
| `users list` | Benutzerkonten auflisten | — (Read) |
| `users deactivate` | Benutzerkonto deaktivieren | `DeactivateUserAccountUseCase` |
| `users reactivate` | Benutzerkonto reaktivieren | `ReactivateUserAccountUseCase` |
| `users change-role` | Rolle ändern | `ChangeUserRoleUseCase` |
| `users bootstrap` | Ersten Admin-Account anlegen | `BootstrapAdminUseCase` |

Beispiel:

```bash
azadmin users bootstrap --username admin --password <passwort>
azadmin users add --username reviewer1 --role REVIEWER
```

#### audit

| Befehl | Beschreibung |
| --- | --- |
| `audit open-shifts` | Mitarbeitende mit offener Vortagsschicht anzeigen |
| `audit verify-chain` | HMAC-Kettensignatur des Audit-Logs prüfen |

Implementiert in `admin_cli/audit.py`. Liest Audit-Log-Einträge
mit `event_type = OPEN_SHIFT_PREVIOUS_DAY_DETECTED` und gibt
die betroffenen Mitarbeitenden mit letztem bekanntem Buchungstyp
und Zeitstempel aus.

Beispiel:

```bash
azadmin audit open-shifts --db arbeitszeit.db
```

## Terminal-UI

Einstiegspunkt: `src/arbeitszeit/presentation/terminal_ui/main.py`

### Startparameter

| Option | Beschreibung |
| --- | --- |
| `--config PATH` | expliziter Pfad zur `config.toml` |
| `--db PATH` | expliziter Datenbankpfad |
| `--rfid NAME` | Gerätename des RFID-Readers |
| `--terminal-id INT` | Terminal-ID für Buchungen |

Alle Werte werden mit `_resolve_or_exit()` aufgelöst: CLI-Argument hat Vorrang
vor `config.toml`-Wert. Fehlt ein Pflichtwert nach beiden Quellen, beendet
sich das Programm mit Fehlermeldung.

### Initialisierungsschritte

Vor der Buchungsschleife:

1. `resolve_evdev_device()` — RFID-Gerätepfad auflösen
2. `run_system_check()` — Prüfung (Fehler blockieren nicht)
3. `_ensure_terminal_exists()` — Terminal-Eintrag anlegen (`INSERT OR IGNORE`)
4. `_setup_file_logging()` — dateibasiertes Logging einrichten
5. `load_threshold_from_config(db_path)` — Zeitüberwachungs-Schwellwert laden
6. `DebouncedHardwareReader(EvdevHardwareReader(rfid_path=rfid_path))` — Reader mit 3-s-Entprellung initialisieren

### Buchungsschleife

Die Endlosschleife in `run()` führt bei jedem Durchlauf `_run_one_cycle()` aus:

1. `_clear_screen()` — Bildschirm leeren
2. `print(_SCAN_PROMPT)` — Aufforderung „Karte an das RFID-Lesegerät halten …" ausgeben
3. `monitor.check()` — Systemzeitüberwachung
4. `process_booking(reader, db_path, terminal_id)` — Buchungszyklus
5. `time.sleep(2)` — 2-Sekunden-Pause vor dem nächsten Zyklus

Bei einer erfolgreichen Buchung gibt `format_feedback(result)` eine
Bestätigung aus.

### Fehlerbehandlung und Signale

- Nicht behandelte Ausnahmen innerhalb eines Buchungszyklus beenden die Schleife
  **nicht** — stattdessen: Fehlermeldung auf `stderr`, Stacktrace-Log,
  Eintrag in `system_events` via `_log_system_event()`.
- Für `SIGTERM` und `SIGINT` sind Handler registriert, die die lokale
  Variable `running` auf `False` setzen und die Schleife beenden.

### Domänenfehler-Meldungen

| Fehler | Angezeigte Meldung (exakt) |
| --- | --- |
| `UnknownCardError` | `Karte nicht erkannt.` |
| `InactiveCardError` | `Karte deaktiviert.` |
| `InactiveEmployeeError` | `Mitarbeiter inaktiv.` |
| `InvalidBookingSequenceError` | `Ungültige Buchungsreihenfolge.` |
| `OpenPhaseConflictError` | `Offene Phase — bitte zuerst abschließen.` |
