# Prüfbericht: `docs/module/handbuch_installation.md` (Installation)

## Gesamteinschätzung

Das Installationskapitel ist zum überwiegenden Teil exakt durch das Repository belegt: Python-Version, Laufzeit- und Entwicklungsabhängigkeiten, alle admin_cli-Befehle samt Argumenten, die Migrationsreihenfolge inklusive der genauen Beispielausgabe (sechs Migrationen), `scripts/setup.py` mit `--backup-dir`/`--export-dir` und der Idempotenz-Aussage sowie der Hardwarebezug (RFID/USB-HID, USB-Numpad, `/dev/input/event*`) sind vollständig korrekt. Eine kleine Inkonsistenz besteht bei der Paketliste für `apt install`, die zwischen zwei aktiven Referenzdokumenten des Projekts abweicht. Substanzielle sachliche Fehler wurden nicht gefunden.

## Befunde

- Aussage: „Die verbindliche Python-Anforderung steht in `pyproject.toml`: `requires-python = \">=3.14,<3.15\"`. Damit ist für die Installation Python 3.14 erforderlich."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeile 9: `requires-python = ">=3.14,<3.15"`
  Bewertung: Wortgleich mit dem Repository-Wert bestätigt.

- Aussage: Laufzeitabhängigkeiten `evdev>=1.7`, `reportlab>=4.0`.
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen 10–13 (`dependencies = ["evdev>=1.7", "reportlab>=4.0"]`)
  Bewertung: Paketnamen und Mindestversionen stimmen exakt überein.

- Aussage: Entwicklungsabhängigkeiten `pytest>=8.0`, `pytest-cov>=5.0`, `pypdf>=4.0`, `ruff>=0.6`, `import-linter>=2.0`.
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen 15–22 (`[project.optional-dependencies] dev = [...]`)
  Bewertung: Alle fünf Pakete und Versionsangaben decken sich exakt mit `pyproject.toml`.

- Aussage: „RFID-Reader als USB-HID-Gerät" und „USB-Numpad als Eingabegerät", angesprochen über `/dev/input/event*`.
  Status: korrekt
  Beleg: `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`, Zeile 7 (Kommentar „Linux, physische Geräte unter /dev/input/event*"); `src/arbeitszeit/presentation/admin_gui/main.py`, Zeile 572 (`--numpad /dev/input/eventX --rfid /dev/input/eventY`); Modul liest „von zwei evdev-Geräten" (Zeile 2 desselben Moduls)
  Bewertung: Zwei getrennte evdev-Eingabegeräte (Numpad, RFID-Reader) sind im Code bestätigt.

- Aussage: „Zusätzliche Systempakete: `sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev`."
  Status: nicht verifizierbar (Inkonsistenz zwischen aktiven Referenzdokumenten)
  Beleg: `handbuch_arbeitszeit.md`, Zeile 177, und `docs/archive/installationsanleitung_arbeitszeit_V2.0.md`, Zeile 78, verwenden exakt dieselbe Paketliste ohne `git`. Die aktuell aktive `installationsanleitung_arbeitszeit.md`, Zeile 195, verwendet dagegen `sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev git` (mit zusätzlichem `git`-Paket).
  Bewertung: Das Repository selbst enthält zwei sich widersprechende aktive Aussagen zur benötigten Paketliste. Da unklar ist, welches Dokument als maßgeblich für dieses spezifische Detail gilt, kann nicht abschließend entschieden werden, ob `git` fehlt oder korrekt weggelassen wurde. Keine Korrektur ohne Klärung der maßgeblichen Quelle.
  Anpassungsvorschlag: Manuelle Klärung erforderlich, welches Dokument (`installationsanleitung_arbeitszeit.md` vs. `handbuch_arbeitszeit.md`/`handbuch_installation.md`) die aktuell gültige Paketliste vorgibt; ggf. Angleichung beider Stellen.

- Aussage: „Repository klonen: `git clone https://github.com/iCodator/arbeitszeit.git`", „Virtuelle Umgebung erstellen: `python3.14 -m venv .venv`", „Abhängigkeiten installieren: `pip install -e .[dev]`".
  Status: nicht verifizierbar
  Beleg: Diese Befehle sind Standard-Installationsschritte und nicht durch projektspezifische Konfigurationsdateien (z. B. CI-Workflows) im geprüften Rahmen bestätigt oder widerlegt worden.
  Bewertung: `pip install -e .[dev]` ist konsistent mit dem `[project.optional-dependencies] dev`-Extra aus `pyproject.toml`, eine explizite Belegstelle im Repository für den genauen Befehlswortlaut wurde jedoch nicht geprüft.

- Aussage: „Datenbank initialisieren: `python scripts/init_db.py`. Der Datenbankpfad kann optional mit `--db` angegeben werden. Standard ist `arbeitszeit.db`."
  Status: korrekt
  Beleg: `scripts/init_db.py`, Zeilen 29–34 (`parser.add_argument("--db", type=Path, default=Path("arbeitszeit.db"), ...)`)
  Bewertung: Argumentname und Standardwert exakt bestätigt.

- Aussage: Typische Ausgabe zeigt sechs angewendete Migrationen (0001–0006) gefolgt vom Hinweis auf `scripts/setup.py --db arbeitszeit.db`.
  Status: korrekt
  Beleg: `migrations/` enthält genau sechs Dateien: `0001_schema.sql`, `0002_seed_defaults.sql`, `0003_cleanup_booking_status.sql`, `0004_supplement_reject_fields_and_review_note.sql`, `0005_time_bookings_device_event_id.sql`, `0006_system_events_application_error.sql`; `scripts/init_db.py`, Zeilen 46–58, druckt genau diese Meldungsform inklusive Warnhinweis, wenn die Ersteinrichtung fehlt.
  Bewertung: Anzahl, Reihenfolge und exakter Ausgabetext stimmen mit dem Code überein.

- Aussage: „Die Reihenfolge ist zwingend: 1. `scripts/init_db.py` 2. `scripts/setup.py`."
  Status: korrekt
  Beleg: `scripts/setup.py`, Zeilen 90–93: Wenn die Datenbankdatei nicht existiert, bricht das Skript mit `Fehler: Datenbank nicht gefunden` und dem Hinweis „Bitte zuerst scripts/init_db.py ausführen." ab.
  Bewertung: Die zwingende Reihenfolge wird durch eine explizite Prüfung im Code erzwungen, nicht nur empfohlen.

- Aussage: Nicht-interaktiver Aufruf mit `--backup-dir` und `--export-dir`; „Bereits konfigurierte Schlüssel werden beim erneuten Aufruf übersprungen."
  Status: korrekt
  Beleg: `scripts/setup.py`, Zeilen 75–86 (Argumentdefinitionen `--backup-dir`, `--export-dir`); Zeilen 44–48 (`_configure_key`: wenn `existing_json is not None`, wird der Schlüssel mit „bereits konfiguriert (...) — übersprungen." übersprungen, ohne ihn zu ändern)
  Bewertung: Argumentnamen und Idempotenz-Verhalten exakt bestätigt.

- Aussage: Ersten ADMIN anlegen mit `users bootstrap --username adminname`.
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Zeilen 202–207 (`boot = users_sub.add_parser("bootstrap", ...)`, `boot.add_argument("--username", required=True, ...)`); `src/arbeitszeit/presentation/admin_cli/main.py`, Zeile 69, bestätigt zusätzlich, dass Bootstrap keine `--user-id` benötigt.
  Bewertung: Befehl, Argumentname und die fehlende Notwendigkeit von `--user-id` bei Bootstrap sind exakt belegt.

- Aussage: Weiteres Benutzerkonto anlegen mit `--user-id 1 users add --username pruefer01 --role REVIEWER`.
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Zeilen 170–177 (`add.add_argument("--username", required=True, ...)`, `add.add_argument("--role", required=True, choices=["ADMIN", "REVIEWER", "TECH"], ...)`); `main.py`, Zeile 52 (`--user-id` als globales Argument)
  Bewertung: Befehl, Argumentnamen und die Rollenoption `REVIEWER` stimmen exakt mit dem Code überein.

- Aussage: Mitarbeiter anlegen mit `employees add --personnel-no M001 --first-name Maria --last-name Mustermann`.
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/employees.py`, Zeilen 140–143 (`add.add_argument("--personnel-no", required=True)`, `--first-name`, `--last-name`)
  Bewertung: Alle drei Argumentnamen exakt bestätigt.

- Aussage: RFID-Karte zuweisen mit `cards assign --employee-id 1 --uid-hash <HASH>`.
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/employees.py`, Zeilen 152–154 (`assign = cards_sub.add_parser("assign", ...)`, `assign.add_argument("--employee-id", type=int, required=True)`, `assign.add_argument("--uid-hash", required=True)`)
  Bewertung: Befehl und beide Argumentnamen exakt bestätigt.

- Aussage: Funktionstest mit `pytest`, `pytest tests/test_migrations.py`, `pytest --cov=arbeitszeit`.
  Status: korrekt
  Beleg: `tests/test_migrations.py` existiert im Repository; `pyproject.toml`, Zeilen 39–41 (`[tool.coverage.run] source = ["arbeitszeit"]`) bestätigt die Sinnhaftigkeit von `--cov=arbeitszeit`.
  Bewertung: Testdatei existiert wie referenziert, Coverage-Quelle passt zur Projektkonfiguration.

## Anpassungsvorschläge (zusammengefasst)

Keine Korrektur mit eindeutiger Beleglage möglich. Der einzige Befund (Systempakete-Zeile) betrifft eine Inkonsistenz zwischen zwei aktiven Referenzdokumenten des Projekts selbst und erfordert eine Entscheidung, welches Dokument maßgeblich ist, bevor `handbuch_installation.md` angepasst werden kann.
