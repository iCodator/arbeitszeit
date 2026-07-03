# Prüfbericht: docs/verzeichnisstruktur_arbeitszeit.md

## Gesamteinschätzung

Das Dokument beschreibt die Verzeichnisstruktur des Projekts im Grundaufbau korrekt (Schichtenarchitektur Domain → Application → Infrastructure → Presentation, Trennung von `migrations/`, `scripts/`, `docs/`, `tests/`). Der Abgleich mit der tatsächlichen Repository-Struktur zeigt jedoch zahlreiche Lücken: Es fehlen mehrere Root-Dateien, Unterverzeichnisse in `docs/`, Module in `application/`, `infrastructure/` und `presentation/` sowie Testdateien. Der gravierendste Befund betrifft `docs/informelles/`: Von den 16 dort beschriebenen Dateien liegen nur 2 tatsächlich in diesem Verzeichnis; die übrigen befinden sich in `docs/archive/`, `docs/adr/` bzw. `docs/betrieb/nachweise/`. Zudem sind die Beschreibungen zu `bookings.py` und zur `hardware/`-Exportschnittstelle sachlich falsch. Alle Korrekturen wurden direkt im Dokument umgesetzt.

## Befunde

### Wurzelverzeichnis

- Aussage: Root enthält u. a. `run_audit.sh` als letzten Eintrag, ohne `befehlsreferenz_arbeitszeit.md`, `markdownlint.json` und `test_booking_loop.py` zu nennen.
  Status: inkorrekt
  Beleg: `ls` im Repository-Wurzelverzeichnis zeigt `befehlsreferenz_arbeitszeit.md`, `markdownlint.json` und `test_booking_loop.py` als vorhandene Root-Dateien.
  Bewertung: Drei Root-Dateien fehlten in der Aufzählung.
  Anpassungsvorschlag: Ergänzt (umgesetzt).

### `.claude/`

- Aussage: `.claude/` enthält ausschließlich `settings.json`.
  Status: inkorrekt
  Beleg: `ls .claude/` zeigt zusätzlich `claude.md`, `markdown-Rules.md`, `Markdown Syntax Documentation.pdf`, `audit/` und `rules/`.
  Bewertung: Die Beschreibung "ausschließlich" widerspricht dem tatsächlichen Inhalt.
  Anpassungsvorschlag: Beschreibung erweitert (umgesetzt).

### `docs/`-Übersicht

- Aussage: `docs/` ist "in drei thematische Unterverzeichnisse unterteilt sowie eine lose Datei auf Dokumentenebene".
  Status: inkorrekt
  Beleg: `ls docs/` zeigt zehn Unterverzeichnisse (`betrieb`, `datenschutz`, `domain`, `informelles`, `infrastructure`, `module`, `adr`, `archive`, `audits`, `pruefberichte`) sowie drei lose Dateien (`SECURITY.md`, `handbuch_rollen_cli_ergaenzung_v1_0.md`, `verzeichnisstruktur_arbeitszeit.md`).
  Bewertung: Zahl der Unterverzeichnisse und loser Dateien war deutlich zu niedrig angegeben.
  Anpassungsvorschlag: Übersicht korrigiert, alle Unterverzeichnisse benannt (umgesetzt).

### `docs/informelles/` (Hauptbefund)

- Aussage: `docs/informelles/` enthält 16 benannte Dateien (Phasenpläne, Abschlussnotizen, Architekturentscheidungen, Testmatrizen).
  Status: inkorrekt
  Beleg: `ls docs/informelles/` zeigt nur `planung_gesamt.md` und `session_abschluss_und_klarstellungen_2026-06-11.md`. Die übrigen 14 Dateien wurden per `find docs -iname "<datei>"` lokalisiert: `phase1_planung.md` bis `phase5_planung.md`, `abarbeitung_*_abschlussnotiz_v1.md`, `audit_evidenzgrenzen_v1.md`, `audit_klarstellungen_niedrig_v1.md`, `device_event_abschlussprotokoll_v1.md`, `migrationsuebersicht_notiz_v1.md`, `terminologie_harmonisierung_v1.md` liegen in `docs/archive/`; `device_event_architekturentscheidung_v1.md` liegt in `docs/adr/`; `nachtragsmatrix_phasen_v1.md`, `testmatrix_planabweichungen_v1.md`, `testmatrix_pruefbericht_v1.md`, `testmatrix_revision_v1.md` liegen in `docs/betrieb/nachweise/`.
  Bewertung: Massive Diskrepanz zwischen Dokumentbeschreibung und tatsächlichem Zustand des Verzeichnisses — 14 von 16 genannten Dateien befinden sich an anderer Stelle.
  Anpassungsvorschlag: Abschnitt komplett überarbeitet: tatsächlicher Inhalt (2 Dateien) benannt, korrekte Fundorte der übrigen Dokumente ergänzt (umgesetzt).

### `scripts/`

- Aussage: `scripts/` enthält vier Dateien (`init_db.py`, `setup.py`, `backup.py`, `generate_audit_notes.py`).
  Status: inkorrekt
  Beleg: `ls scripts/` zeigt zusätzlich `show_config.py` und `verify_hardware.py`.
  Bewertung: Zwei Skripte fehlten in der Aufzählung.
  Anpassungsvorschlag: Ergänzt (umgesetzt).

### `src/arbeitszeit/application/`

- Aussage: `application/` enthält `commands.py`, `results.py`, `unit_of_work.py`.
  Status: inkorrekt
  Beleg: `find src/arbeitszeit/application` zeigt zusätzlich `queries.py`.
  Bewertung: Datei fehlte; laut Docstring in `queries.py` handelt es sich um "Query-DTOs für die lesende Seite (CQRS-Read)".
  Anpassungsvorschlag: Ergänzt (umgesetzt).

- Aussage: `application/use_cases/` enthält sechs Use-Case-Dateien (ohne `manage_employees.py`, `manage_rfid_cards.py`, `manage_user_accounts.py`).
  Status: inkorrekt
  Beleg: `find src/arbeitszeit/application/use_cases` zeigt zusätzlich `manage_employees.py`, `manage_rfid_cards.py`, `manage_user_accounts.py`.
  Bewertung: Drei Use Cases fehlten in der Aufzählung.
  Anpassungsvorschlag: Ergänzt (umgesetzt).

### `src/arbeitszeit/infrastructure/`

- Aussage: `infrastructure/` (Modulebene) enthält nur `system_check.py` und `time_monitor.py`.
  Status: inkorrekt
  Beleg: `find src/arbeitszeit/infrastructure` zeigt zusätzlich `notification.py` (Desktop-Benachrichtigung via `notify-send`, laut Docstring Bezug auf "Pflichtenheft §7.10").
  Bewertung: Datei fehlte.
  Anpassungsvorschlag: Ergänzt (umgesetzt).

### `src/arbeitszeit/infrastructure/hardware/`

- Aussage: `ports.py` definiert das Interface `IDeviceReader`.
  Status: inkorrekt
  Beleg: `src/arbeitszeit/infrastructure/hardware/__init__.py` importiert `HardwareReader` (nicht `IDeviceReader`) sowie `EmptyUidError` und `HardwareTimeoutError` aus `ports.py`.
  Bewertung: Falscher Interface-Name.
  Anpassungsvorschlag: Korrigiert auf `HardwareReader` (umgesetzt).

- Aussage: `evdev_reader.py` implementiert `IDeviceReader` als konkrete Klasse (implizit `EvdevReader` genannt).
  Status: inkorrekt
  Beleg: `grep -n "^class " src/arbeitszeit/infrastructure/hardware/evdev_reader.py` zeigt die Klasse `EvdevHardwareReader(HardwareReader)`.
  Bewertung: Falscher Klassenname; auch im Testabschnitt (`tests/integration/test_hardware_evdev.py`) fälschlich als `EvdevReader` bezeichnet.
  Anpassungsvorschlag: An beiden Stellen auf `EvdevHardwareReader` korrigiert (umgesetzt).

- Aussage: `__init__.py` exportiert `EvdevReader` und `HardwareSimulator`.
  Status: inkorrekt
  Beleg: Der tatsächliche Inhalt von `__init__.py` exportiert `EmptyUidError`, `HardwareReader`, `HardwareTimeoutError`, `RawBookingRequest`, `SimulatedHardwareReader`, `hash_uid` (siehe `__all__`). Weder `EvdevReader` noch `HardwareSimulator` werden exportiert.
  Bewertung: Beide genannten Namen existieren im Modul nicht.
  Anpassungsvorschlag: Korrigiert auf die tatsächliche Exportliste (umgesetzt).

- Aussage: `uid_hash.py` erzeugt "einen einseitigen Hash der RFID-UID (SHA-256)" ohne Nennung der Funktion.
  Status: korrekt (Algorithmus), präzisiert
  Beleg: `uid_hash.py` verwendet `hashlib.sha256(raw_uid.encode()).hexdigest()` in der Funktion `hash_uid()`.
  Bewertung: Fachlich korrekt, Funktionsname ergänzt.
  Anpassungsvorschlag: Funktionsname `hash_uid()` ergänzt (umgesetzt).

### `src/arbeitszeit/presentation/admin_cli/`

- Aussage: `admin_cli/` enthält acht benannte Dateien (ohne `_auth.py`).
  Status: inkorrekt
  Beleg: `find src/arbeitszeit/presentation/admin_cli` zeigt zusätzlich `_auth.py` mit Docstring "CLI-seitige Rollenprüfung für lesende Operationen ohne Use Case".
  Bewertung: Datei fehlte.
  Anpassungsvorschlag: Ergänzt (umgesetzt).

- Aussage: `bookings.py` – "CLI-Kommandos zur Buchungsverwaltung: auflisten, korrigieren, Korrekturen anzeigen".
  Status: inkorrekt
  Beleg: Frühere Prüfung dieser Session (`docs/pruefberichte/pruefbericht_betriebsdokumentation.md`) hat bereits belegt, dass `bookings.py` nur die Unterbefehle `correct`, `supplement`, `approve-supplement`, `reject-supplement` besitzt; ein `list`-Unterbefehl existiert nicht. Buchungsübersichten liefert `reports.py` (`open-bookings` u. a.).
  Bewertung: "auflisten" und "Korrekturen anzeigen" sind für `bookings.py` sachlich falsch zugeordnet.
  Anpassungsvorschlag: Beschreibung auf tatsächliche Unterbefehle korrigiert (umgesetzt).

- Aussage: `reports.py` – "Monatsberichte als PDF oder CSV exportieren, Buchungsübersichten anzeigen" (ohne konkrete Unterbefehle).
  Status: nicht verifizierbar → präzisiert
  Beleg: Bereits in dieser Session verifizierte Unterbefehle: `export-csv`, `export-csv-review-cases`, `export-pdf-day/-week/-month/-employee`, `open-bookings`, `warn-cases`, `corrections`, `supplements`, `open-review-cases`.
  Bewertung: Beschreibung war unvollständig, aber nicht falsch; Präzisierung erhöht Nachvollziehbarkeit.
  Anpassungsvorschlag: Konkrete Unterbefehle ergänzt (umgesetzt).

- Aussage: `system.py` – "Systemcheck ausführen, Backup anstoßen, Migrationsstatus prüfen".
  Status: inkorrekt (Teilaspekt)
  Beleg: Frühere Prüfung dieser Session (`pruefbericht_betriebsdokumentation.md`) hat belegt: `system.py` besitzt nur die Unterbefehle `check` und `backup`; kein Migrationsstatus-Unterbefehl, kein Restore-Unterbefehl.
  Bewertung: "Migrationsstatus prüfen" ist als eigener Unterbefehl nicht belegt.
  Anpassungsvorschlag: Beschreibung auf die zwei tatsächlichen Unterbefehle reduziert, Hinweis auf fehlenden Restore-Unterbefehl ergänzt (umgesetzt).

### `src/arbeitszeit/presentation/admin_gui/` (fehlendes Verzeichnis)

- Aussage: Das Dokument erwähnt `admin_gui/` an keiner Stelle.
  Status: inkorrekt (Lücke)
  Beleg: `find src/arbeitszeit/presentation` zeigt das vollständige Unterverzeichnis `admin_gui/` mit `main.py` (Docstring: "Admin-GUI für arbeitszeit — tkinter/ttk-basierte Verwaltungsoberfläche").
  Bewertung: Eine komplette Presentation-Komponente fehlte in der Dokumentation.
  Anpassungsvorschlag: Neuer Abschnitt `src/arbeitszeit/presentation/admin_gui/` ergänzt (umgesetzt).

### `tests/`

- Aussage: Die Testsuite "unterteilt sich in vier Teststufen" (`domain`, `application`, `integration`, `e2e`).
  Status: inkorrekt
  Beleg: `find tests -maxdepth 1 -type d` zeigt zusätzlich `tests/presentation/` mit `test_booking_loop.py`.
  Bewertung: Fünfte Teststufe fehlte in Zählung und Aufzählung.
  Anpassungsvorschlag: Abschnitt `tests/presentation/` ergänzt, Zahl auf fünf korrigiert (umgesetzt).

- Aussage: `tests/application/` enthält acht benannte Dateien (ohne `test_manage_employees.py`, `test_manage_rfid_cards.py`, `test_manage_user_accounts.py`).
  Status: inkorrekt
  Beleg: `ls tests/application/*.py` zeigt zusätzlich `test_manage_employees.py`, `test_manage_rfid_cards.py`, `test_manage_user_accounts.py`.
  Bewertung: Drei Testdateien fehlten in der Aufzählung.
  Anpassungsvorschlag: Ergänzt (umgesetzt).

## Zusammenfassung der Korrekturen

1. Root-Verzeichnis: `befehlsreferenz_arbeitszeit.md`, `markdownlint.json`, `test_booking_loop.py` ergänzt.
2. `.claude/`: Beschreibung um `claude.md`, Regelquellen, `audit/` und `rules/` erweitert.
3. `docs/`-Übersicht: alle zehn Unterverzeichnisse benannt, lose Dateien (`SECURITY.md`, `verzeichnisstruktur_arbeitszeit.md`) ergänzt.
4. `docs/informelles/`: Abschnitt komplett neu gefasst — tatsächlicher Inhalt (2 Dateien) benannt, korrekte Fundorte der 14 fälschlich hier verorteten Dokumente ergänzt (`docs/archive/`, `docs/adr/`, `docs/betrieb/nachweise/`).
5. `scripts/`: `show_config.py` und `verify_hardware.py` ergänzt.
6. `application/`: `queries.py` ergänzt; `use_cases/manage_employees.py`, `manage_rfid_cards.py`, `manage_user_accounts.py` ergänzt.
7. `infrastructure/`: `notification.py` ergänzt.
8. `infrastructure/hardware/`: Interface-Name `IDeviceReader` → `HardwareReader` korrigiert; Klassenname `EvdevReader` → `EvdevHardwareReader` korrigiert (auch im Testabschnitt); Export-Liste der `__init__.py` korrigiert; Funktionsname `hash_uid()` ergänzt.
9. `presentation/admin_cli/`: `_auth.py` ergänzt; `bookings.py`-Beschreibung auf tatsächliche Unterbefehle korrigiert; `reports.py`- und `system.py`-Beschreibungen präzisiert bzw. korrigiert (kein Migrationsstatus-Unterbefehl).
10. `presentation/admin_gui/`: neuer Abschnitt ergänzt (bislang komplett fehlend).
11. `tests/`: Anzahl der Teststufen von vier auf fünf korrigiert, Abschnitt `tests/presentation/` ergänzt; `tests/application/` um drei fehlende Testdateien ergänzt.

## Offene Punkte

- Der im Dokumentkopf genannte Commit-Hash `9b9650a` als "aktueller Stand des main-Branches zum Zeitpunkt der Analyse" konnte als existierender Commit im Repository bestätigt werden (`git cat-file -e`), jedoch nicht verifiziert werden, ob er zum Erstellungszeitpunkt des Dokuments tatsächlich der jeweils aktuellste `main`-Stand war. Diese zeitliche Aussage bleibt nicht verifizierbar und wurde nicht verändert.
- Die Aussage "Das Wurzelverzeichnis enthält ausschließlich Dateien, keine weiteren Unterverzeichnisse außer den nachfolgend beschriebenen" wurde nicht beanstandet, da `ls -la` im Root tatsächlich keine weiteren Unterverzeichnisse außer `.claude/`, `docs/`, `migrations/`, `scripts/`, `src/`, `tests/` zeigt (versteckte Verzeichnisse wie `.git/`, `.pytest_cache/` sind Laufzeitartefakte bzw. Versionskontrolle und fallen nicht unter den fachlichen Beschreibungsanspruch des Dokuments).
