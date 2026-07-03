# Prüfbericht: `CONTRIBUTING.md`

## Gesamteinschätzung

Die Beitragsrichtlinien sind größtenteils präzise und decken sich mit Architektur, Entwicklungssetup, Commit-Konventionen und Branch-Strategie im Repository. Drei Unvollständigkeiten wurden gefunden: dieselbe fehlende `handbuch_show_config.md` in der Kapitel-Aufzählung wie in der README, ein fehlender Testordner in der Testebenen-Übersicht sowie ein falscher Pfad zur genannten Testmatrix-Datei.

## Befunde

- Aussage: Schichtenstruktur `domain`, `application`, `infrastructure`, `presentation` mit den genannten Zuständigkeiten (Fachmodell/Enums/Ports; Use-Cases/Commands/Unit-of-Work; SQLite/Hardware/Export/Backup/Systemcheck; Terminal-UI/Admin-CLI/Admin-GUI).
  Status: korrekt
  Beleg: Verzeichnisstruktur `src/arbeitszeit/domain/`, `application/`, `infrastructure/`, `presentation/` (inkl. `admin_gui/`) bestätigt in vorherigen Prüfzyklen dieser Space-Historie (Presentation- und Overview-Kapitel).
  Bewertung: Bestätigt.

- Aussage: „Zielversion laut `pyproject.toml`: `>=3.14,<3.15`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeile 9
  Bewertung: Bestätigt.

- Aussage: Setup-Schritte `git clone`, `venv`, `pip install -e .[dev]`, `python scripts/init_db.py`, `pytest`.
  Status: korrekt
  Beleg: `pyproject.toml`-Extra `dev` existiert; `scripts/init_db.py` existiert; `pytest` als Testrunner in `[tool.pytest.ini_options]` konfiguriert.
  Bewertung: Bestätigt.

- Aussage: „Spezifische HID-Hardware ... ist für die meisten Tests nicht erforderlich, da es Simulatoren gibt."
  Status: korrekt
  Beleg: `src/arbeitszeit/infrastructure/hardware/simulator.py` existiert.
  Bewertung: Bestätigt.

- Aussage: „Ruff als Linter/Format-Checker (siehe `pyproject.toml`)."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeile 20 (`"ruff>=0.6"` in Dev-Abhängigkeiten).
  Bewertung: Bestätigt.

- Aussage: „Testpfad ist in `pyproject.toml` als `tests` konfiguriert."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeile 33 (`testpaths = ["tests"]`)
  Bewertung: Bestätigt.

- Aussage: Testebenen `tests/domain/`, `tests/application/`, `tests/integration/`, `tests/e2e/`, `tests/test_migrations.py`.
  Status: inkorrekt (unvollständig)
  Beleg: Verzeichnis `tests/` enthält zusätzlich `tests/presentation/` mit realem Testinhalt (`test_booking_loop.py`, 2 Dateien inkl. `__init__.py`).
  Anpassungsvorschlag: `tests/presentation/` – Tests der Präsentationsschicht (z. B. Terminal-UI-Buchungsschleife) in die Aufzählung ergänzen.

- Aussage: Migrationen unter `migrations/`, ausgeführt von `scripts/init_db.py`, neue Migrationen z. B. `0007_beschreibung.sql`.
  Status: korrekt
  Beleg: `migrations/`-Verzeichnis mit `NNNN_beschreibung.sql`-Namensschema bestätigt (aktuell bis `0006_...`); `scripts/init_db.py` ruft `run_migrations()` auf.
  Bewertung: Bestätigt, inklusive korrekter Fortsetzung der Nummerierungslogik.

- Aussage: „HID-/evdev-Logik gehört nach `src/arbeitszeit/infrastructure/hardware/`."
  Status: korrekt
  Beleg: `evdev_reader.py` liegt exakt dort.
  Bewertung: Bestätigt.

- Aussage: `handbuch_arbeitszeit.md` wird aus Kapitel-Quelldateien unter `docs/module/` zusammengeführt: `handbuch_overview.md`, `handbuch_installation.md`, `handbuch_presentation.md`, `handbuch_application_layer.md`, `handbuch_domain.md`, `handbuch_infrastructure.md`, `handbuch_audit.md`.
  Status: inkorrekt (unvollständig)
  Beleg: `docs/module/` enthält zusätzlich `handbuch_show_config.md`, das in der Aufzählung fehlt.
  Anpassungsvorschlag: `handbuch_show_config.md` ergänzen (analog zur bereits umgesetzten Korrektur in `README.md`).

- Aussage: Relevante Dokumente für Datenschutz/Betrieb: `docs/datenschutz/vvt_arbeitszeit_v1.md`, `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`, `docs/betrieb/rollenzuweisung.md`.
  Status: korrekt
  Beleg: Alle drei Dateien existieren unter den angegebenen Pfaden.
  Bewertung: Bestätigt.

- Aussage: „Änderung kurz in einer Test-/Planungsmatrix dokumentieren (z. B. `docs/informelles/testmatrix_revision_v1.md`)."
  Status: inkorrekt
  Beleg: Die Datei `testmatrix_revision_v1.md` existiert im Repository, jedoch unter dem Pfad `docs/betrieb/nachweise/testmatrix_revision_v1.md`, nicht unter `docs/informelles/`. `docs/informelles/` existiert zwar als Verzeichnis, enthält aber `planung_gesamt.md` und `session_abschluss_und_klarstellungen_2026-06-11.md`, keine Testmatrix-Datei.
  Anpassungsvorschlag: Pfad auf `docs/betrieb/nachweise/testmatrix_revision_v1.md` korrigieren.

- Aussage: Pflichtenheft/Regelwerk-Referenz auf `pflichtenheft_arbeitszeit_v6.md` und `regelwerk_arbeitszeit_v5.md`.
  Status: korrekt
  Beleg: Beide Dateien existieren im Projekt-Root; die Referenz auf v6 (nicht v5) beim Pflichtenheft entspricht dem aktuellen Repository-Zustand (kein `pflichtenheft_arbeitszeit_v5.md` mehr im Root).
  Bewertung: Bestätigt.

- Aussage: „Die Versionsnummer wird in `pyproject.toml` unter `[project].version` gepflegt."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeile 7 (`version = "0.1.0"`) unter `[project]`.
  Bewertung: Bestätigt.

- Aussage: „`SECURITY.md`" wird als zukünftig zu ergänzende Datei bezeichnet.
  Status: korrekt
  Beleg: `SECURITY.md` existiert aktuell nicht im Repository-Root; die Formulierung „ggf. ... einem zukünftigen `SECURITY.md`" ist damit konsistent mit dem tatsächlichen Zustand.
  Bewertung: Bestätigt.

## Anpassungsvorschläge (zusammengefasst)

1. Abschnitt 5.2 (Testebenen): `tests/presentation/` ergänzen.
2. Abschnitt 10.1: `handbuch_show_config.md` in die Kapitel-Aufzählung ergänzen.
3. Abschnitt 9.2: Pfad zur Testmatrix von `docs/informelles/testmatrix_revision_v1.md` auf `docs/betrieb/nachweise/testmatrix_revision_v1.md` korrigieren.
