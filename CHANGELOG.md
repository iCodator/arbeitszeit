# Changelog

Alle nennenswerten Änderungen werden in dieser Datei dokumentiert.  
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

---

## [Bereinigung: alle mypy-Fehler in tests/ behoben] – 2026-07-15

### Geändert

- `tests/application/fakes.py`: alle `dataclasses.replace(..., id=self._next_id)` auf
  `XxxId(self._next_id)` umgestellt; `FakeDeviceEventRepository.add` auf
  `TerminalId | None` / `-> DeviceEventId` angepasst; `_check_protocol_compliance`
  nutzt eindeutige Variablennamen statt `_`; `list[dict]` → `list[dict[str, Any]]`.

- Alle 36 Testdateien in `tests/`: fehlende `-> None`-Rückgabetypen ergänzt,
  `CaptureFixture` → `CaptureFixture[str]`, `row["id"]` → `int(row["id"])`,
  rohe `int`-Literal-IDs mit Domain-ID-Konstruktoren gewrappt (`EmployeeId(x)` etc.),
  `FakeUnitOfWork`-Übergaben an Use-Cases via `cast(UnitOfWork, uow)` typsicher gemacht,
  Fixture-Signaturen vollständig annotiert, `None`-Guards für optionale DB-Abfragen ergänzt.

- `tests/integration/test_export.py`: Import von `BookingRow` etc. von
  `report_queries` (kein Re-Export) auf `arbeitszeit.application.queries` korrigiert.

**Ergebnis:** `python -m mypy src/ tests/ --ignore-missing-imports` meldet
0 Fehler in 130 Quelldateien. 723/723 Tests bestehen.

---

## [Migration Schritt 2: zentrales config.toml-Test-Fixture] – 2026-07-15

### Hinzugefügt

- `tests/helpers.py` (neu, `__version__` 1.0): reine Hilfsfunktion
  `make_config_toml(tmp_path, *, database_path, rfid, numpad, backup_dir,
  export_dir, log_dir, admin_user_id, filename)` → `Path`. Konstruiert intern
  `AppConfig` aus den Keyword-Argumenten und ruft `write_config()` auf — keine
  manuellen TOML-Strings.

- `tests/conftest.py` (neu, `__version__` 1.0): pytest-Fixture `make_config_toml`
  (function-scope), das `helpers.make_config_toml` mit dem aktuellen `tmp_path`
  als Factory zurückgibt. Damit repo-weit in allen Tests verfügbar.

### Geändert

- `tests/integration/test_reports_cli.py`: `from collections.abc import Callable`
  ergänzt. `test_cli_run_config_toml_wirkt_bis_export_befehl` ersetzt manuellen
  f-String-TOML-Block durch `make_config_toml(database_path=db,
  export_dir=config_export_dir, admin_user_id=admin_id)`. Testverhalten unverändert.
  `__version__` auf 1.1 erhöht.

---

## [Migration Schritt 1: config.toml-Fallback für export_dir in reports.py] – 2026-07-15

### Geändert

- `presentation/admin_cli/reports.py`: `_get_export_dir` erhält optionalen
  Parameter `app_config: AppConfig | None = None`. Ist `app_config.backup.export_dir`
  gesetzt, wird es als export_dir verwendet (Vorrang vor DB). DB-Fallback bleibt
  erhalten. Fehlermeldung bei fehlendem export_dir nennt jetzt beide Quellen.
  Alle 6 Export-Cmd-Funktionen erhalten `app_config: AppConfig | None = None`
  und übergeben es an `_get_export_dir`. `AppConfig` importiert.
  `__version__` auf 1.1 erhöht.

- `presentation/admin_cli/main.py`: Die 6 Export-Lambdas
  (`export-csv`, `export-csv-review-cases`, `export-pdf-day`, `export-pdf-week`,
  `export-pdf-month`, `export-pdf-employee`) übergeben nun `app_config=app_config`
  an die jeweilige Cmd-Funktion. `__version__` auf 1.3 erhöht.

### Hinzugefügt

- `tests/integration/test_reports_cli.py`: `__version__` 1.0 eingeführt.
  Neue Imports: `AppConfig`, `BackupConfig` aus `config_file`, `run as cli_run`
  aus `admin_cli/main`. 4 neue Tests: `test_get_export_dir_config_hat_vorrang_vor_db`
  (config.toml-Wert gewinnt bei gesetztem DB-Wert), `test_get_export_dir_db_fallback_wenn_export_dir_none`
  (DB-Fallback wenn `export_dir=None` in AppConfig), `test_cmd_export_csv_verwendet_app_config_export_dir`
  (kein DB-Wert, app_config-Pfad landet im Mock-Aufruf), `test_cli_run_config_toml_wirkt_bis_export_befehl`
  (Ende-zu-Ende via `cli_run` mit `--config`, kein `--db`, kein `--user-id`).

---

## [Feature: Admin-CLI cards assign – config.toml-Fallback für --rfid] – 2026-07-15

### Geändert

- `presentation/admin_cli/employees.py`: `_validate_uid_source` und
  `_resolve_uid_hash` erhalten neu den Parameter `rfid_device: str | None`
  statt `args.rfid` direkt zu lesen. `cmd_cards_assign` berechnet
  `rfid_device = args.rfid or (app_config.terminal.rfid if app_config else None)`
  und übergibt ihn. Fehlermeldung bei fehlendem RFID-Gerät nennt jetzt auch
  `[terminal] rfid in config.toml`. `AppConfig` importiert.
  `__version__` auf 1.2 erhöht.

- `presentation/admin_cli/main.py`: Lambda für `("cards", "assign")` übergibt
  nun `app_config=app_config` an `cmd_cards_assign`.
  `__version__` auf 1.2 erhöht.

### Hinzugefügt

- `tests/integration/test_employees.py`: Alle bestehenden Aufrufe von
  `_validate_uid_source` und `_resolve_uid_hash` auf neue Signaturen angepasst.
  4 neue Tests: `test_validate_uid_source_ohne_rfid_und_ohne_config` (prüft
  Fehlermeldung mit "config.toml"), `test_validate_uid_source_config_rfid_ausreichend`
  (rfid_device als str reicht), `test_resolve_uid_hash_config_fallback` (prüft
  dass rfid_device an resolve_evdev_device übergeben wird),
  `test_cmd_cards_assign_scan_verwendet_config_rfid` (Ende-zu-Ende via CLI mit
  config.toml ohne --rfid). `__version__` auf 1.1 erhöht.

---

## [Typkorrektur reject_supplement.py: int → UserAccountId] – 2026-07-14

### Geändert

- `application/use_cases/reject_supplement.py`: Parameter `user_id` in
  `_assert_can_reject` und `rejected_by_user_id` in `_resolve_review_case` von
  `int` auf `UserAccountId` korrigiert. Import von `UserAccountId` ergänzt.
  `__version__` auf 1.2 erhöht.

---

## [Tests: Domain-Coverage 97% → 99%] – 2026-07-14

### Hinzugefügt

- `tests/domain/test_booking_rules.py`: 2 neue Tests. `test_come_nach_go_bei_noch_offener_pause`
  deckt den bislang ungetestetem Zweig in `_validate_come` ab (open_work=False, open_break=True —
  z.B. Altdaten mit GO während offener Pause). `test_come_nach_vollstaendigem_kommen_gehen_zyklus`
  deckt den Erfolgsfall nach abgeschlossenem COME→GO-Zyklus ab. Alle Funktionen mit `-> None`
  annotiert. `__version__ = "1.0"` ergänzt.

- `tests/domain/test_compliance_checks.py`: 3 neue Tests für pathologische Buchungsfolgen
  (Altdaten/manuelle Importe): BREAK_START ohne vorangehenden COME, BREAK_END ohne BREAK_START,
  GO ohne COME — alle drei dokumentieren das graceful-degradation-Verhalten von `_work_stats`.
  `TimeBookingId`/`EmployeeId` korrekt konstruiert, alle Funktionen annotiert,
  `ComplianceFlag` importiert. `__version__ = "1.0"` ergänzt.

---

## [Refactoring: reject_supplement.py execute CC 10 → 3] – 2026-07-14

### Geändert

- `application/use_cases/reject_supplement.py`: `execute` (CC 10) in drei
  Methoden aufgeteilt. `_assert_can_reject(user_id)` (CC 4) kapselt die
  Berechtigungsprüfung (Existenz, Aktivität, Rolle). `_resolve_review_case(
  supplement, rejected_by_user_id, reason)` (CC 5) kapselt die For-Schleife
  über offene ReviewCases und deren Schließung. `execute` selbst ist damit CC 3.
  `Supplement` zur Entity-Importliste ergänzt. `__version__` auf 1.1 erhöht.

---

## [Refactoring: config_setup.py setup_config CC 10 → 5] – 2026-07-14

### Geändert

- `infrastructure/config_setup.py`: `setup_config` (CC 10) in fünf Teilfunktionen
  aufgeteilt. Die drei vorhandenen Closures `_path_field` (CC 4), `_str_field`
  (CC 3), `_int_field` (CC 6) auf Modulebene gehoben. Zwei neue Extraktionen:
  `_init_config(config_path)` (CC 3) kapselt das Laden der bestehenden Config
  mit Status-Label; `_collect_db_hints(db_path)` (CC 4) liest Migrations­hinweise
  aus DB und gibt Statusmeldung aus. `setup_config` selbst ist damit CC 5.
  `__version__` auf 1.1 erhöht.

### Hinzugefügt

- `tests/infrastructure/test_config_setup.py`: 18 neue Tests (26 gesamt) für die
  fünf extrahierten Funktionen sowie zuvor unabgedeckte Pfade: CLI-Override für
  `_str_field` und `_int_field`, `except ValueError` in `_int_field`,
  `_collect_db_hints` ohne Einträge (False-Zweig), `_read_db_hints` mit Exception
  und falschem Wert, `setup_config` mit `KeyboardInterrupt`. Coverage 89% → 100%.
  `import pytest`, `__version__` auf 1.1 erhöht.

---

## [Refactoring: config_file.py write_config CC 11 → 3] – 2026-07-14

### Geändert

- `infrastructure/config_file.py`: `write_config` (CC 11) in drei Teilfunktionen
  aufgeteilt. `_q()` als `_toml_string` auf Modulebene gehoben (CC 1).
  `_terminal_section(config)` (CC 5) kapselt die drei Terminal-Felder plus
  Leerabschnitt-Prüfung. `_backup_section(config)` (CC 5) analog für
  Backup-Felder. `write_config` selbst ist damit CC 3. `__version__` auf 1.1
  erhöht.
- `tests/infrastructure/test_config_file.py`: Typannotationen auf alle
  vorbestehenden Testfunktionen nachgerüstet; `__version__ = "1.0"` und
  Modulkommentar ergänzt.

### Hinzugefügt

- `tests/infrastructure/test_config_file.py`: 11 neue Tests für die extrahierten
  Hilfsfunktionen — 4× `_toml_string` (Normalwert, Anführungszeichen, Backslash,
  Path-Objekt), 4× `_terminal_section` (leer, nur id, alle Felder, ohne id),
  3× `_backup_section` (leer, nur backup_dir, alle Felder). Coverage bleibt 100%.

---

## [Tests: admin_cli/main.py Coverage 74% → 100%] – 2026-07-14

### Geändert

- `presentation/admin_cli/main.py`: `if __name__ == "__main__":` mit
  `# pragma: no cover` markiert. `__version__` auf 1.1 erhöht.

### Hinzugefügt

- `tests/integration/test_admin_cli_main.py` (neu, `__version__ = "1.0"`):
  10 Tests für Fehler-Initialisierungspfade der CLI.
  Abgedeckte Pfade: `_load_app_config` ohne Config-Fund (Zeile 23),
  ungültige TOML-Datei (Zeilen 26–28); `_resolve_db_path` mit Config-Pfad
  (Zeile 34), ohne DB-Quelle (Zeilen 36–41); `_resolve_user_id` mit gültiger
  ENV `ADMIN_USER_ID` (Zeilen 49–52), ungültiger ENV (Zeilen 53–58),
  `admin.user_id` aus Config (Zeile 60), ohne Quelle (Zeilen 62–67);
  `_dispatch` mit `cmd=None` (False-Zweig Zeile 223).

---

## [Refactoring: domain/entities.py ReviewCase CC 11 → 6, WorkScheduleVersion CC 10 → 5] – 2026-07-14

### Geändert

- `domain/entities.py`: Validierungslogik aus `__post_init__` in private Methoden
  ausgelagert — analog zum bestehenden `Supplement`-Muster.
  `WorkScheduleVersion.__post_init__` (CC 9) → `_validate_scope` (CC 5) +
  `_validate_time_window` (CC 5) + `__post_init__` (CC 1).
  `ReviewCase.__post_init__` (CC 10) → `_validate_open_status` (CC 3) +
  `_validate_closed_status` (CC 6) + `__post_init__` (CC 3).
  Fachliche Semantik vollständig unverändert. Coverage 98% bleibt erhalten.
  `__version__` auf 1.1 erhöht.

---

## [Refactoring + Tests: export/csv_exporter.py CC 12 → 6, Coverage 81% → 99%] – 2026-07-14

### Geändert

- `infrastructure/export/csv_exporter.py`: `_day_stats` (CC 12) in vier Funktionen
  aufgeteilt: `_close_work_phase` (CC 2), `_close_break_phase` (CC 2),
  `_accumulate_phase_times` (CC 6, Zustandsmaschine), `_count_booking_statuses`
  (CC 5, Statuszählung), `_day_stats` (CC 1, Koordinator). Außerdem fehlendes
  `export_dir.mkdir()` in `export_review_cases` ergänzt. `__version__` auf 1.1 erhöht.

### Hinzugefügt

- `tests/integration/test_csv_export.py`: 16 neue Tests (31 gesamt, vorher 15).
  Abgedeckte Pfade: BREAK_END-Dauer aus BREAK_START, BREAK_END ohne BREAK_START
  (opener=None), WARN- und NEEDS_REVIEW-Statuszählung, Phasenwechsel ohne
  vorangehende öffnende Buchung (BREAK_START ohne COME, BREAK_END ohne BREAK_START,
  GO ohne COME), `now=None`-Zweige in allen drei Export-Funktionen, vollständige
  Abdeckung von `export_review_cases` (Dateiname, Inhalt, Leerfall,
  fehlender Buchungsbezug, Hinweistext, employee_id-Filter). Vorbestehende
  mypy-Fehler (28 fehlende Annotationen, `dict` ohne Typparameter, `Returning Any`)
  mitbehoben. `__version__ = "1.0"` ergänzt.

---

## [Refactoring + Tests: admin_cli/employees.py CC 12 → 5, Coverage 71% → 100%] – 2026-07-14

### Geändert

- `presentation/admin_cli/employees.py`: `cmd_cards_assign` (CC 12) in drei
  Funktionen aufgeteilt: `_validate_uid_source` (CC 5, Eingangsvalidierung),
  `_resolve_uid_hash` (CC 5, Kartensuche/Scan), `cmd_cards_assign` (CC 2,
  Koordinator). `__version__` auf 1.1 erhöht.

### Hinzugefügt

- `tests/integration/test_employees.py`: 15 neue Tests (23 gesamt, vorher 8).
  Abgedeckte Pfade: `employees list` leer, alle 3 Validierungsfehler in
  `_validate_uid_source`, alle Hardware-Fehlerpfade in `_resolve_uid_hash`
  (DeviceNotFoundError, HardwareTimeoutError, EmptyUidError, OSError) sowie
  der Scan-Erfolgspfad, DomainError in `cmd_cards_assign`/`replace`/`deactivate`.
  Vorbestehende mypy-Fehler (fehlende Annotationen, `dict` ohne Typparameter,
  `Returning Any`) mitbehoben. `__version__ = "1.0"` ergänzt.

---

## [Tests: terminal_ui/main.py Coverage 66% → 99%] – 2026-07-14

### Geändert

- `presentation/terminal_ui/main.py`: `__main__`-Block in `def main()` extrahiert,
  damit Unit-Tests möglich sind. `if __name__ == "__main__":` mit `# pragma: no cover`.
  `import argparse` auf Modulebene verschoben. `__version__` auf 1.1 erhöht.

### Hinzugefügt

- `tests/integration/test_terminal_ui_main.py`: 13 neue Tests ergänzt (25 gesamt,
  vorher 12). Abgedeckte Pfade: `_resolve_or_exit` (alle 3 Zweige), `_setup_file_logging`
  (DB-Pfad, JSON-null-Wert, app_config-Vorrang, Fehlerbehandlung), `run()` mit
  `DeviceNotFoundError`, `main()` (CLI-Argumente, config.toml-Laden, defekte Config,
  fehlender Pflichtparameter). `CaptureFixture`-Annotationen auf `[str]` präzisiert
  (vorbestehende mypy-Fehler mitbehoben). `__version__ = "1.0"` ergänzt.

---

## [Refactoring: cmd_system_backup CC 15 → max. 6] – 2026-07-14

### Geändert

- `presentation/admin_cli/system.py`: `cmd_system_backup` (CC 15) in drei
  Hilfsfunktionen aufgeteilt: `_resolve_backup_dir` (CC 4), `_resolve_export_dir`
  (CC 5), `_run_nas_sync` (CC 6). Koordinator `cmd_system_backup` hat nun CC 3.
- `presentation/admin_cli/system.py`: `__version__` auf 1.1 erhöht.

---

## [Bugfix: ResourceWarning SQLite-Verbindungen] – 2026-07-14

### Behoben

- `tests/e2e/test_supplement_flow.py`: `_make_uow()` öffnete pro Aufruf 2 SQLite-Verbindungen
  ohne sie zu schließen (13 Aufrufe = 26 `ResourceWarning: unclosed database` in pytest).
  `_make_uow` wurde zu einem `@contextmanager` umgebaut, der beide Verbindungen im
  `finally`-Block schließt. Alle 10 Aufrufstellen auf `with _make_uow(db) as uow:` umgestellt.

### Geändert

- `tests/e2e/test_supplement_flow.py`: `__version__ = "1.0"` ergänzt.

---

## [Codequalität: ruff-Bereinigung] – 2026-07-14

### Behoben

- 2 ruff-E501-Fehler (`line too long`) in `tests/integration/test_hardware_evdev.py`
  (Zeilen 271 und 300): langen `patch()`-Aufruf auf mehrere Zeilen umgebrochen.

### Geändert

- `tests/integration/test_hardware_evdev.py`: `__version__ = "1.0"` nachgepflegt
  (beim initialen Versionierungs-Lauf ausgelassen).

---

## [Typkorrektur & Abschluss] – 2026-07-14

### Behoben
- 4 mypy-Fehler (`[type-arg]`) in `schedule.py`: bare `list`-Annotationen in
  `_partition_by_scope`, `_print_global_section`, `_print_employee_section`
  und `_print_scope_hint` durch `list[sqlite3.Row]` ersetzt.

### Geändert
- `schedule.py`: `__version__` auf `1.1` erhöht.

---

## [Konfigurationspflege & Versionierung] – 2026-07-14

### Hinzugefügt
- `src/arbeitszeit/infrastructure/config_setup.py` mit gemeinsamer
  Interaktionslogik für `scripts/setup.py` und `admin_cli system setup`.
- `admin_cli system setup` als neuer Subcommand zur interaktiven Pflege der
  `config.toml` (ADMIN/TECH); nutzt dieselbe Logik wie `scripts/setup.py`.
- `setup_config()` verarbeitet DB-Migrationspfade (`backup.backup_dir`,
  `export.export_dir`, `logging.log_dir`) als optionale Hinweise.
- `resolve_config_write_path()` bestimmt den Schreibpfad nach der Priorität:
  explizit → vorhandene Datei → XDG-Standard (`~/.config/arbeitszeit/config.toml`).
- `__version__ = "1.0"` in allen 70 Produktionsmodulen und Skripten.
- 3 neue Integrationstests in `tests/integration/test_system_cli.py`:
  `test_app_config_backup_dir_wird_verwendet`,
  `test_app_config_hat_vorrang_vor_db_backup_dir`,
  `test_setup_schreibt_config_toml`.

### Geändert
- `scripts/setup.py` vollständig neu geschrieben: schreibt ausschließlich
  `config.toml`, liest keine DB-Werte mehr — nur noch als Migrationshinweise.
- `scripts/backup.py` liest `backup_dir` und `export_dir` bevorzugt aus
  `config.toml` statt aus der DB.
- `scripts/show_config.py` zeigt jetzt zwei klar getrennte Abschnitte:
  `config.toml` und `DB (system_config)`.
- `cmd_system_backup()` bevorzugt `app_config.backup.backup_dir` vor dem
  DB-Wert `backup.backup_dir`.
- `cmd_system_check()` akzeptiert jetzt `app_config` als Keyword-Parameter.

---

## [Konfiguration & Terminalbetrieb] – 2026-07-14

### Hinzugefügt
- `src/arbeitszeit/infrastructure/config_file.py` mit `AppConfig` sowie den
  Teilkonfigurationen `DatabaseConfig`, `TerminalConfig`, `BackupConfig` und
  `AdminConfig`.
- Funktionen `load_config()`, `find_config()` und `write_config()` für eine
  dateibasierte TOML-Konfiguration.
- `config.toml.example` als Vorlage für die lokale Konfiguration.
- `tests/infrastructure/test_config_file.py` mit 15 Tests für Lade-, Such- und
  Schreibverhalten der neuen Konfigurationsdatei.
- Dateibasierte Fehlerprotokollierung der Terminal-UI in
  `terminal_ui.log` über `logging.log_dir`.
- Detailliertere Buchungsrückmeldungen in der Terminal-UI mit Vorname,
  Nachname, Buchungsart und Buchungszeitpunkt.
- `setup.py --log-dir` zur Konfiguration des Log-Verzeichnisses.

### Geändert
- `terminal_ui` unterstützt jetzt `--config`; `--db`, `--numpad`, `--rfid` und
  `--terminal-id` können aus `config.toml` übernommen werden.
- `terminal_ui.run()` akzeptiert jetzt den Keyword-Parameter `app_config`.
- `_setup_file_logging()` bevorzugt das Log-Verzeichnis aus `config.toml`.
- `admin_cli` unterstützt jetzt `--config`; `--db` kann aus `config.toml`
  übernommen werden.
- `_resolve_user_id()` nutzt jetzt die Priorität
  CLI → `ADMIN_USER_ID` → `config.toml`.
- `system_check.py` liest Pfadkonfigurationen nicht mehr aus
  `_REQUIRED_CONFIG_KEYS`, sondern prüft sie über einen eigenen
  `_check_config_file_paths()`-Schritt.
- `test_system_check._make_db()` wurde von nicht mehr benötigten
  Deployment-Schlüsseln bereinigt.

### Behoben
- Fremdschlüsselproblem der Terminal-UI bei leerer `terminals`-Tabelle:
  `_ensure_terminal_exists()` legt den Terminal-Datensatz jetzt per
  `INSERT OR IGNORE` an.
- Fehlerbehandlung in `_run_one_cycle()`: Exceptions werden jetzt mit
  `logging.exception()` und vollständigem Traceback protokolliert.
- `_log_system_event()` enthält jetzt mehr Detailinformationen für
  Fehleranalysen im Betrieb.

---

## [Hardware & Dokumentation] – 2026-07-08 bis 2026-07-14

### Hinzugefügt
- `resolve_evdev_device()` zur Auflösung von evdev-Geräten über stabile
  Gerätenamen statt nur über `/dev/input/eventX`-Pfade.
- Direkter RFID-Scan für `cards assign` über `--scan --rfid` als Alternative
  zu `--uid-hash`.
- `scan_rfid_uid_hash()` in `evdev_reader.py` zum einmaligen Einlesen eines
  RFID-Hashes direkt vom Lesegerät.
- `docs/03_installation_technik/hardware.md` zur Dokumentation lokaler
  evdev-Gerätepfade und Gerätenamen.
- `docs/04_betrieb/handbuch_backup_restore.md` als Betriebshandbuch für
  Backup- und Restore-Abläufe.
- Neue HTML-Exporte der zentralen Dokumente mit gemeinsamer CSS-Datei
  `docs/arbeitszeit_docs.css`.

### Geändert
- `--numpad` und `--rfid` akzeptieren jetzt sowohl stabile Gerätenamen als auch
  direkte Gerätepfade.
- Handbuch, Befehlsreferenz und Installationsanleitung wurden auf die Nutzung
  stabiler evdev-Gerätenamen aktualisiert.
- Die Dokumentation von `cards assign` beschreibt jetzt den direkten RFID-Scan
  sowie den bisherigen Weg über `--uid-hash`.
- Installationsanleitungen und Handbücher wurden versioniert fortgeschrieben;
  ältere Fassungen wurden in `docs/archive/` abgelegt.
- Die Datei
  `docs/03_installation_technik/handbuch_rollen_cli_ergaenzung_v1_0.md`
  wurde in
  `docs/03_installation_technik/handbuch_rollen_cli_ergaenzung.md`
  umbenannt.
- Veraltete HTML-Dateien mit `*_arbeitszeit.html` wurden entfernt und durch
  aktuelle Exporte ersetzt.
- Dateireferenzen in mehreren Markdown-Dokumenten wurden an aktuelle
  Dateinamen angepasst.

### Behoben
- Veraltete oder inkonsistente Dokumentationspfade in Handbuch und
  Installationsanleitung wurden bereinigt.

---

## [Qualität, Refactoring & Tests] – 2026-07-03 bis 2026-07-05

### Hinzugefügt
- Deutlich ausgebaute Testabdeckung für mehrere unterabgedeckte Module,
  darunter `_intervals.py`, `_auth.py`, `reports.py`, `schedule.py`,
  `bookings.py`, `terminal_ui/main.py`, `notification.py`,
  `admin_cli/system.py` und `evdev_reader.py`.
- Isolierte Tests für `_check_ntp()` über gemockte `timedatectl`-Aufrufe.
- Zusätzliche Tests für `terminal_ui/main.run()` mit Fokus auf Systemcheck,
  Reader-Lebenszyklus und Signalbehandlung.

### Geändert
- Mehrere Methoden und Funktionen wurden zur Reduktion zyklomatischer
  Komplexität refaktoriert, unter anderem:
  - `ManageWorkScheduleUseCase.execute`
  - `ApproveSupplementUseCase.execute`
  - `CorrectBookingUseCase.execute`
  - `validate_booking_sequence`
  - `_read_rfid_uid`
  - `cmd_schedule_show`
- Doppelte Bewertungslogik für Buchungen wurde in das neue Modul
  `application/use_cases/_booking_evaluation.py` ausgelagert.
- Die Audit-Benennung wurde so geändert, dass Uhrzeitanteile in Verzeichnis-
  und Dateinamen aufgenommen werden.
- Subprocess-Aufrufe wurden durch dokumentierte `# nosec`-Begründungen für
  Bandit-Funde ergänzt.

### Behoben
- Bare-`except: pass`-Stellen wurden durch explizites Warning-Logging mit
  `exc_info=True` ersetzt.
- Sicherheitsproblem durch partielle Executable-Pfade: `rsync`, `notify-send`
  und `timedatectl` werden jetzt über absolute Pfade aufgerufen.
- NTP-abhängige Testinstabilität in Container- und CI-Umgebungen wurde durch
  Testisolation beseitigt.
- Weitere kleinere Qualitätsprobleme wie Whitespace-Fehler,
  Import-Reihenfolgen und nicht benötigte Suppressionen wurden bereinigt.

---

## [Dokumentationsprüfung & Bereinigung] – 2026-07-03

### Hinzugefügt
- Umfangreiche Prüfberichte für Handbuch, Präsentationsschicht,
  Installationskapitel, Audit-Status, `show_config.py`, CONTRIBUTING,
  Regelwerk, Pflichtenheft-Anlage, Datenbankschema, Domain-,
  Application- und Infrastructure-Handbuch sowie Datenschutz- und
  Betriebsdokumente.
- `docs/07_pruefberichte/dokumentations_inventar.md` als vollständige
  Übersicht aller Markdown- und HTML-Dokumentationsdateien.
- Wiederherstellung des Archivdokuments
  `docs/archive/pflichtenheft_arbeitszeit_v5.md`.
- Prüfberichte zur Migration von Pflichtenheft-Referenzen und zur Korrektur
  dokumentarischer Widersprüche.

### Geändert
- Die Dokumentationsstruktur unter `docs/` wurde umfassend in nummerierte
  Themenordner neu gegliedert.
- 100+ interne Querverweise wurden an die neue Struktur angepasst.
- Das Gesamthandbuch wurde schrittweise mit den geprüften Modulhandbüchern
  synchronisiert.
- ADR-Referenzen, Betriebsdokumentation, VVT, Sicherheitsdokumentation,
  Restore-Checkliste, Rollenzuweisung, Hardware-Inbetriebnahme-Protokoll,
  Aufbewahrungs- und Löschkonzept sowie Planungsdokumente wurden auf den
  tatsächlichen Code- und Dokumentationsstand korrigiert.
- Relative Pfade zu `.claude/`-Dateien im Prüfbericht-Inventar wurden
  berichtigt.
- HTML-Versionen von Handbuch, Befehlsreferenz und Installationsanleitung
  wurden neu erzeugt und gegen ihre Markdown-Quellen geprüft.

### Behoben
- Doppelte Prüfberichtsverzeichnisse mit Encoding-Fehlern wurden bereinigt.
- Tote oder falsche Referenzen in ADRs, Sicherheitsdokumentation und
  Inventarlisten wurden entfernt oder korrigiert.
- Mehrere fachliche Fehlbehauptungen in der Dokumentation wurden durch
  belegte, vorsichtigere Formulierungen ersetzt.

---

## [Admin-GUI, CLI & Fachlogik] – 2026-07-01 bis 2026-07-03

### Hinzugefügt
- Admin-GUI auf Basis von `tkinter/ttk` zur Verwaltung ohne Kommandozeile,
  mit Tabs für Mitarbeiter, Karten, Benutzer, Regelzeiten und System.
- `tests/presentation/test_admin_gui_controller.py` mit 21 Tests nach
  Controller-Extraktion.
- Neue Use Cases für schreibende Operationen in den Bereichen Mitarbeiter,
  RFID-Karten und Benutzerkonten:
  - `manage_employees.py`
  - `manage_rfid_cards.py`
  - `manage_user_accounts.py`
- Neue Query-DTOs in `application/queries.py` zur CQRS-Symmetrie.
- `export-csv-review-cases` zum CSV-Export offener Prüffälle.
- NTP-Prüfung im `system_check` via `timedatectl`.
- `docs/domain/enums.md` und `docs/infrastructure/evdev_reader.md`.

### Geändert
- Schreibende Admin-CLI-Operationen für Mitarbeiter, Karten und Benutzerkonten
  laufen jetzt über die Anwendungsschicht statt über direkte SQL-Zugriffe.
- `schedule set` unterstützt jetzt optional `--employee-id`.
- PDF-Exportbefehle nutzen jetzt benannte Optionen (`--date`, `--year`,
  `--week`, `--month`) statt Positionsargumente.
- Rollenprüfungen wurden in `presentation/admin_cli/_auth.py`
  zentralisiert.
- Dokumentation von README, CONTRIBUTING, Handbuch,
  Installationsanleitung und Befehlsreferenz wurde auf den aktuellen
  Funktionsstand gebracht.
- `verify_hardware.py` zeigt den vollständigen SHA-256-Hash an und nutzt
  projektweit konsistente Hash-Bildung.
- `show_config.py` wurde dokumentiert.

### Behoben
- `system backup` signalisiert NAS-Sync-Fehler jetzt mit `sys.exit(1)`.
- Warnhinweis bei ungefilterten Großmengen in `open-bookings` und
  `open-review-cases` ergänzt.
- Mehrere Python-2-artige `except`-Schreibweisen wurden auf den
  Python-3-Stil umgestellt.
- Fehlender `simpledialog`-Import in `admin_gui/main.py` ergänzt.
- Typprobleme und Verbindungsprüfungen in `admin_gui/main.py` abgesichert.
- Hilfe-Dialog-Typannotation von `tk.Widget` auf `tk.Misc` korrigiert.
- Lücken und Fehler in Befehlsreferenz und Installationsanleitung wurden
  schrittweise korrigiert.

### Entfernt
- Die Admin-GUI wurde am 2026-07-03 aus dem `main`-Zweig entfernt und in den
  separaten Entwicklungszweig `admin_gui` ausgelagert.
- Zugehörige GUI-Verweise wurden aus README, CONTRIBUTING, Handbuch,
  Installationsanleitung und Verzeichnisstruktur entfernt.

---

## [Pflichtenheft v6 & Dokumentationsaufbau] – 2026-06-30 bis 2026-07-01

### Hinzugefügt
- Vollständige Befehlsreferenz als `befehlsreferenz_arbeitszeit.md`.
- HTML-Version der Installationsanleitung.
- Modularisierte Handbuchstruktur mit getrennten Kapiteldateien für
  Overview, Installation, Presentation, Application Layer, Domain,
  Infrastructure und Audit.
- `docs/SECURITY.md` zur Beschreibung des Sicherheitsmodells.
- ADR-Dokumente für CQRS-Lesezugriffe und Presentation/Infrastructure-
  Importregeln.
- `docs/informelles/session_abschluss_und_klarstellungen_2026-06-11.md`
  als Zusammenführung mehrerer Einzeldokumente.

### Geändert
- Pflichtenheft wurde von Version 5 auf Version 6 angehoben.
- Aktive Referenzen im Repository wurden von `pflichtenheft_arbeitszeit_v5.md`
  auf `pflichtenheft_arbeitszeit_v6.md` umgestellt; historische Artefakte
  blieben bewusst unverändert.
- Installationsanleitung wurde laienverständlicher ausgebaut und um
  LUKS-Festplattenverschlüsselung als Pflichtvoraussetzung ergänzt.
- README und CONTRIBUTING wurden auf aktuelle Struktur, Skripte,
  Dev-Abhängigkeiten und Dokumentationsdateien aktualisiert.
- `planung_gesamt.md` und weitere Planungsdokumente wurden von Diff-Artefakten
  und veralteten Pfaden bereinigt.
- Die `docs/`-Struktur wurde reorganisiert; ADRs und Nachweise wurden in
  eigene Unterverzeichnisse verschoben.

### Behoben
- Die Installationsanleitung wurde mehrfach gegen den tatsächlichen Ablauf
  korrigiert, unter anderem für `verify_hardware.py`, UID-Hash-Beschaffung,
  `setup.py` und `evtest`.
- Fehlende oder falsche Befehlsaufrufe in der Dokumentation wurden berichtigt.

---

## [Audit-Tooling & Entwicklerwerkzeuge] – 2026-06-16 bis 2026-06-29

### Hinzugefügt
- `scripts/generate_audit_notes.py` zur automatischen Auswertung von
  Audit-Reportdateien.
- `run_audit.sh` ruft am Ende automatisch `generate_audit_notes.py` auf.
- Datierte Unterverzeichnisse für Audit-Reports unter `docs/audits/reports/`.
- `scripts/verify_hardware.py` als Hardware-Smoke-Test für RFID-Reader und
  Numpad.
- `scripts/show_config.py` zur Anzeige von `system_config`-Einträgen.
- `domain/value_objects.py` mit starken `NewType`-IDs für zentrale Domänen-
  und Infrastrukturobjekte.
- `tests/presentation/` mit Unit-Tests für `terminal_ui/booking_loop.py`.
- `import-linter`-Konfiguration zur Verifikation des Layer-Contracts.
- `ruff`, `black`, `isort` und strikte `mypy`-Konfiguration in
  `pyproject.toml`.

### Geändert
- `run_audit.sh` läuft jetzt trotz Befunden vollständig durch und erzeugt
  alle Reports zuverlässig.
- Report-Dateinamen und Coverage-/Lint-Konfigurationen wurden vereinheitlicht.
- `docs/audits/` wurde aus dem Git-Tracking entfernt und in `.gitignore`
  aufgenommen.
- `.claude/` wurde aktiviert, bereinigt und um Frontmatter ergänzt.
- Die Admin-CLI-Dispatch-Logik wurde von einer tiefen `if/elif`-Kette auf
  eine Dispatch-Tabelle umgestellt.

### Behoben
- Bandit-Warnung in `migrations.py` durch korrekte `nosec`-Schreibweise
  beseitigt.
- 40 mypy-Fehler und weitere Typprobleme wurden systematisch behoben.
- 14 Ruff-Fehler sowie spätere Line-Length-, Import- und Stilprobleme
  wurden beseitigt.
- Mehrere Audit-Empfehlungen zu B017, B608 und E501 wurden umgesetzt.
- Duplizierte TOML-Sektionen und Konfigurationsfehler in `pyproject.toml`
  wurden bereinigt.

---

## [Audit & Dokumentation] – 2026-06-13

### Hinzugefügt
- Audit-Bericht `docs/audits/audit_arbeitszeit_v1_2026-06-13_09-04.md` mit Phasenbewertung 1–5,
  GO/NO-GO-Matrix, Befundklassifikation und priorisierter To-do-Liste.
- Dokumentation der Migrationshistorie zu `BookingStatus` (Entfernung der Werte
  `POSSIBLE_*` und `MANUAL_ENTRY` aus `time_bookings.current_status` durch
  `migrations/0003_cleanup_booking_status.sql`) als fachlich relevantes
  Änderungsprotokoll.
- Verweis in der Projektdokumentation auf die Audit-Evidenzgrenzen
  (`docs/informelles/audit_evidenzgrenzen_v1.md`) und die Nachtragsmatrix
  (`docs/informelles/nachtragsmatrix_phasen_v1.md`) als ergänzende Nachweise
  für Pflichtenheft v5.
- Betriebsdokumentation nachgezogen und nach `docs/betrieb/` überführt:
  `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` mit erweiterten
  Hinweisen zu Zeitmonitor, Passwort-Hashing und Rollenmodell.
- Neues Aufbewahrungs- und Löschkonzept für die Praxis:
  `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md`.
- Neues Datenschutz- und TOM-Dokument (inkl. Backup-Rahmen):
  `docs/betrieb/datenschutz_und_tom_arbeitszeit_v1_0.md`.
- Neue betriebliche Rollenzuweisung für ADMIN/REVIEWER/TECH:
  `docs/betrieb/rollenzuweisung_arbeitszeit_v1_0.md`.

### Geändert
- Abschnitt „Betrieb & Rechtliches“ im `README.md` inhaltlich an den
  Audit-Bericht angepasst (explizite Hinweise auf organisatorische Auflagen
  zu Rollenzuweisung, Aufbewahrungs- und Löschkonzept, Datenschutz- und
  Backup-Unterlagen, Betriebsfreigabe-Protokoll).
- Klarstellung in der Dokumentation, dass die ArbZG-Prüfhilfen auf der
  Netto-Arbeitszeit basieren und als fachliche Indikatoren (nicht als
  rechtsverbindliche Bewertung) zu verstehen sind.
- `docs/informelles/planung_gesamt.md`: Referenzen auf
  `anlage_einhaltung_pflichtenheft_v2.md` präzisiert (Root-Anlage v1 und
  Archiv-Version unter `docs/archive/`).

---

## [Audit & Dokumentation] – 2026-06-11 bis 2026-06-12

### Hinzugefügt
- `users reactivate`, `users change-role`, `users bootstrap` in der Admin-CLI
- device_events-Produktionspfad: RFID_SCAN-Record (Autocommit) vor `BookUseCase` —
  Audit-Trail bleibt auch bei Buchungsfehler erhalten
- `SQLiteDeviceEventRepository` + `DeviceEventRepository`-Protokoll
- Betriebsdokumentation (`betriebsdokumentation_arbeitszeit_v1_1.md`, 12 Abschnitte)
- Phasenübergreifende Nachtragsmatrix (44 Artefakte mit Phasenzuordnung und Belegen)
- Revisionsfeste Testmatrix (406 Tests, Pflichtenheft v5 §16-Abdeckung)
- Installationsanleitung v2.0 (Markdown + HTML)
- Handbuch v2.0 (Markdown + HTML)
- Pflichtenheft v5 und Regelwerk v5

### Geändert
- Python-Zielversion auf 3.14 angehoben
- Alle Phasenpläne auf Pflichtenheft v5 / Regelwerk v5 aktualisiert
- `init_db.py` auf `argparse` (`--db`-Flag) umgestellt

### Behoben
- `FakeUnitOfWork` commit-or-rollback-Semantik korrigiert
  (`if not self.committed` statt `if exc_type is not None`)
- `_REQUIRED_CONFIG_KEYS` um `backup.backup_dir` und `export.export_dir` ergänzt
- `ValidationResult` aus `booking_rules.py` entfernt (war toter Code)

---

## [Phase 5: Präsentation] – 2026-05-26 bis 2026-05-27

### Hinzugefügt
- `presentation/terminal_ui/` — Buchungsschleife (RFID + Numpad, `_run_one_cycle()`)
- `presentation/admin_cli/` — vollständige Admin-Kommandozeile
  - Mitarbeiterverwaltung (`employees add/list/deactivate`)
  - Zeitbuchungen, Korrekturen, Nachtragsgenehmigung
  - Exporte (CSV, PDF) mit Zeitraumfilter
  - Benutzerkontenverwaltung (`users add/list/deactivate`)
- `infrastructure/time_monitor.py` — Systemzeitüberwachung
  (`TIME_JUMP_DETECTED` / `MANUAL_TIME_CHANGE_DETECTED`)
- `migrations/0006_system_events_application_error.sql` —
  `APPLICATION_ERROR` als neuer Systemereignistyp
- `scripts/setup.py` — interaktive Erstkonfiguration

### Behoben
- PDF-Intervalle auf halb-offene UTC-Intervalle umgestellt
- CSV-Intervallbildung vereinheitlicht
- `open_bookings` und `open_review_cases` mit `--from`/`--to`-Zeitraumfilter versehen

---

## [Phase 4: Infrastruktur] – 2026-05-22 bis 2026-05-26

### Hinzugefügt
- `SQLiteUnitOfWork` mit commit-or-rollback-Semantik und separater `audit_conn`
- 10 SQLite-Repositories mit Roundtrip-Integrationstests
- `infrastructure/hardware/` — `evdev`-Reader (RFID + Numpad) + `SimulatedHardwareReader`
- `infrastructure/backup/backup_service.py`:
  - Lokales SQLite-Backup (timestamped)
  - NAS-Spiegelung via `rsync --archive --delete`
  - `restore_from(restore_exports=True)` für vollständige Wiederherstellung
- `infrastructure/export/` — `report_queries.py`, `csv_exporter.py`,
  `pdf_report_service.py` (vier Berichtstypen)
- `infrastructure/system_check.py` — Systemcheck (DB, Config, NAS, FK-Konsistenz)
- `scripts/backup.py` — Backup-Skript mit optionalem `--export-dir`
- `migrations/0003_cleanup_booking_status.sql` — `POSSIBLE_*`-Werte aus
  `time_bookings.current_status` entfernt (korrigiert historische BookingStatus-
  Inkonsistenz aus `0001_schema.sql`; bereinigt durch Phase-4-Migration)
- `migrations/0004_supplement_reject_fields_and_review_note.sql` —
  Ablehnung formal von Genehmigung getrennt; Notizfeld für Prüffälle
- `migrations/0005_time_bookings_device_event_id.sql` — Schemavorbereitung
  `device_event_id` (operative Nutzung: Phase-5-Nacharbeit)
- Rollenprüfung (ADMIN / REVIEWER / TECH) in allen schreibenden Use Cases
- Ruhezeitprüfung (§5 ArbZG) und Regelzeitfenster-Check in `BookUseCase`
- WAL-Modus, `busy_timeout`, Autocommit-Garantie für `audit_conn` explizit belegt

### Geändert
- Audit-Log rollback-resistent (schreibt über separate Verbindung außerhalb der UoW-Transaktion)
- `BookingStatus` auf 6 orthogonale Werte reduziert; Compliance-Zustand über `ReviewCaseType`

---

## [Phase 3: Application] – 2026-05-22

### Hinzugefügt
- `UnitOfWork`-Protokoll + `FakeUnitOfWork` (In-Memory-Testdouble)
- Commands / Results für alle Use Cases
- `BookUseCase` — COME / GO / BREAK mit Audit-Log und Buchungssequenzprüfung
- `ManageWorkScheduleUseCase` — Regelarbeitszeitverwaltung mit Versionierung
- `RegisterSupplementUseCase` — Nachtragsantrag einreichen
- `CorrectBookingUseCase` — Buchungskorrektur mit selektiver Review-Case-Schließung
- `ApproveSupplementUseCase` / `RejectSupplementUseCase`
  (für Phase 4 geplant, in Phase 3 vorgezogen)
- 109 Application-Tests

---

## [Phase 2: Domäne] – 2026-05-21

### Hinzugefügt
- `domain/enums.py` — 11 StrEnum-Klassen (`BookingType`, `BookingStatus`,
  `UserRole`, `ReviewCaseType` u. a.)
- `domain/entities.py` — 9 frozen `@dataclass` (`Employee`, `TimeBooking`,
  `WorkScheduleVersion`, `UserAccount` u. a.)
- `domain/errors.py` — `DomainError` + 9 Subklassen
- `domain/audit_events.py` — zentraler Ereignistyp-Katalog
- `domain/services/booking_rules.py` — Buchungssequenzprüfung
- `domain/services/compliance_checks.py` — ArbZG-Prüfhilfen §3 / §4 / §5
  (`check_break_compliance`, `check_max_hours`, `check_rest_period`)
- `domain/ports/repositories.py` — 10 Repository-Protokolle
- 67 Domain-Tests

---

## [Phase 1: Grundgerüst] – 2026-05-21

### Hinzugefügt
- `migrations/0001_schema.sql` — Initialschema: 16 Tabellen, 17 Indizes,
  `schema_migrations`-Versionsverfolgung
- `migrations/0002_seed_defaults.sql` — Regelarbeitszeiten Mo–Fr,
  `system_config`-Defaults
- `infrastructure/db/connection.py` — SQLite-Verbindung (WAL, `row_factory`, PRAGMAs)
- `infrastructure/db/migrations.py` — Glob-Runner mit Idempotenz und Rollback-Sicherung
- `scripts/init_db.py` — Datenbankinitialisierung
- 12 Migrationstests
