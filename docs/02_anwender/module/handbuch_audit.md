# Handbuch `arbeitszeit` – Audit und Prüfstatus

**Kapitel:** 7
**Version:** 1.1
**Stand:** Juli 2026
**Quelldatei:** `docs/module/handbuch_audit.md`

## Code-Audit (`run_audit.sh` und `scripts/generate_audit_notes.py`)

`run_audit.sh` ist ein ausführbares Shell-Skript im Repository-Wurzelverzeichnis
(56 Zeilen). Es führt nacheinander folgende Analyse-Tools gegen `src/arbeitszeit`
aus und schreibt deren Rohausgaben in ein datumsbezogenes Unterverzeichnis
`docs/audits/reports/<DATUM>/` (Datum im Format `YYYY-MM-DD`):

| Tool | Zweck | Ausgabedatei |
|---|---|---|
| `ruff check` | Linting | `ruff-report.txt` |
| `mypy` | Typprüfung | `mypy-report.txt` |
| `radon cc -s -a` | Zyklomatische Komplexität | `radon-cc.txt` |
| `radon raw` | Rohmetriken (LOC, Kommentare) | `radon-raw.txt` |
| `lint-imports` | Architektur-Contract (import-linter) | `import-linter.txt` |
| `bandit -r ... -f json` | Security-Analyse | `bandit-report.json` |
| `pytest --cov=arbeitszeit` | Tests und Testabdeckung | `coverage.xml`, `htmlcov/`, `pytest.txt` |

Aufruf:

```bash
bash run_audit.sh
```

Das Skript verwendet `set -uo pipefail` und bewusst **nicht** `set -e`: Ein
Kommentar im Skript begründet dies damit, dass die Analyse-Tools bei
Befunden mit Exit-Code 1 zurückkehren können, ohne dass der Gesamtlauf
abgebrochen werden soll. Entsprechend sind die Aufrufe von `ruff`, `mypy`,
`lint-imports`, `bandit` und `pytest` jeweils mit `|| true` abgesichert;
lediglich die beiden `radon`-Aufrufe besitzen kein `|| true`.

Am Ende jedes Laufs ruft `run_audit.sh` automatisch
`scripts/generate_audit_notes.py` auf, das die Rohdaten einliest und eine
versionierte Markdown-Zusammenfassung erzeugt:

```bash
python scripts/generate_audit_notes.py \
    --report-dir docs/audits/reports/<DATUM> \
    --output docs/audits/reports/audit-notes-<DATUM>.md
```

`scripts/generate_audit_notes.py` (596 Zeilen) unterstützt folgende Parameter:

| Parameter | Bedeutung | Standard |
|---|---|---|
| `--report-dir <PFAD>` | Verzeichnis mit den Rohdaten von `run_audit.sh` | `docs/audits/reports` |
| `--output <PFAD>` | Ausgabedatei | `<report-dir>/audit-notes-<DATUM>.md` |

Jeder Parser des Skripts liefert bei fehlender Quelldatei `{"available": False}`
zurück, statt Werte zu schätzen oder zu erfinden. Der erzeugte Bericht ist in
folgender fester Abschnittsreihenfolge aufgebaut:

1. **Überblick** – Codebasisgröße in KLoC (aus `radon raw`) sowie Testanzahl,
   aufgeschlüsselt nach `tests/domain/`, `tests/application/`,
   `tests/integration/` und `tests/e2e/` (gezählt werden Dateien nach dem
   Muster `test_*.py`, ohne `conftest.py`/`__init__.py`).
2. **Linting (Ruff)** – Gesamtanzahl der Befunde sowie gesondert ausgewiesene
   Kategorien `E501` (line-too-long), `F401` (unused-import) und die
   `B`-Serie (Bugbear).
3. **Typprüfung (Mypy)** – bei Erfolg „Fehler insgesamt: 0“ mit Anzahl der
   geprüften Quelldateien; bei Fehlern die Gesamtzahl sowie bis zu 5
   Beispielzeilen.
4. **Komplexität (Radon)** – Durchschnittswert und -note der zyklomatischen
   Komplexität sowie eine Tabelle aller „Hotspots“ mit CC ≥ 10
   (Datei, Block, CC-Wert).
5. **Architektur (import-linter)** – Anzahl geprüfter Contracts, Anzahl
   Verstöße sowie Detailzeilen zu Verstößen.
6. **Security (Bandit)** – Anzahl der Funde nach Schweregrad (High/Medium/Low),
   gescannte LOC, `nosec`-Marker sowie eine Tabelle aller HIGH- und
   MEDIUM-Funde (ID, Datei, Zeile, Beschreibung).
7. **Tests & Coverage** – Gesamt-Coverage in Prozent (aus `coverage.xml`,
   Cobertura-Format) sowie eine Tabelle der Dateien mit Coverage unter 60 %.
8. **Maßnahmenplan** – dynamisch erzeugte, priorisierte Liste offener
   Maßnahmen. Ein Eintrag wird jeweils nur aufgenommen, wenn die zugehörige
   Bedingung zutrifft:
   1. Bandit-Funde mit Schweregrad HIGH oder MEDIUM in Summe > 0
   2. import-linter-Verstöße (`broken`) > 0
   3. Mypy meldet keinen Erfolg und Gesamtfehleranzahl > 0
   4. Ruff-Gesamtbefunde > 0
   5. Radon-Hotspots mit CC ≥ 15 (bis zu drei Blocknamen werden genannt)
   6. Gesamt-Coverage < 80 % (der zugehörige Maßnahmentext verweist dabei auf
      die Anzahl der Dateien mit Coverage < 60 %, wie sie im Abschnitt
      „Tests & Coverage“ ausgewiesen werden)

   Treffen keine der Bedingungen zu, gibt der Bericht den Text
   „_Keine offenen Maßnahmen identifiziert – alle Checks bestanden._“ aus.

> ⚠️ `run_audit.sh` benötigt zusätzlich installierte Tools (`mypy`, `radon`,
> `bandit`), die in `pyproject.toml` unter `[project.optional-dependencies]`
> (Gruppe `dev`) nicht als Pflichtabhängigkeiten geführt sind. Dort sind nur
> `pytest`, `pytest-cov`, `pypdf`, `ruff` und `import-linter` gelistet.

Die von den Analyse-Tools verwendete Konfiguration ist in `pyproject.toml`
hinterlegt:

- `[tool.ruff]`: `line-length = 100`, `target-version = "py314"`,
  `[tool.ruff.lint] select = ["E", "F", "W", "I", "B"]`, `ignore = []`;
  ausgeschlossen sind `.git`, `.venv`, `__pycache__` und
  `docs/audits/reports`.
- `[tool.mypy]`: `python_version = "3.14"`, `strict = true`,
  `disallow_incomplete_defs = true`, `disallow_untyped_defs = true`,
  `ignore_missing_imports = true`, `warn_unused_ignores = true`,
  `warn_return_any = true`; ausgeschlossen sind `^\.venv/` und
  `^docs/audits/reports/`.
- `[tool.importlinter]`: ein Contract „Clean Architecture -
  Layer-Abhaengigkeiten“ vom Typ `layers` mit der Schichtreihenfolge
  `arbeitszeit.presentation` → `arbeitszeit.infrastructure` →
  `arbeitszeit.application` → `arbeitszeit.domain`.

> ℹ️ Im Repository liegen zwei Audit-bezogene Verzeichnisse nebeneinander:
> `docs/audits/reports/` enthält die Rohdaten eines abgeschlossenen Laufs vom
> 16.06.2026 (`ruff-report.txt`, `mypy-report.txt`, `radon-cc.txt`,
> `radon-raw.txt`, `import-linter.txt`, `bandit-report.json`,
> `coverage.xml`, `pytest.txt`) – dieser Pfad entspricht weiterhin dem in
> `run_audit.sh` fest codierten `BASE_DIR="docs/audits/reports"`.
> `docs/08_planung_intern/audits/` enthält demgegenüber ältere, manuell
> erstellte Audit-Berichte (`audit_arbeitszeit_v1_*.md`) sowie eine bereits
> gerenderte Fassung `reports/audit-notes-2026-06-16.md`. Eine Datei
> `audit-notes-2026-06-16.md` direkt unter `docs/audits/reports/` (dem von
> `run_audit.sh` erzeugten Standardpfad) existiert im aktuellen
> Repository-Stand nicht.

## Sicher belegt

Die folgenden Aussagen sind durch die tatsächlich gelesenen Dateien abgesichert:

- Python-Anforderung `>=3.14,<3.15`
- Paketabhängigkeiten aus `pyproject.toml`
- Trennung in `presentation`, `infrastructure`, `application`, `domain`
- Vorhandensein von `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py`
- Bootstrap des ersten Administratorkontos
- Zulässige Rollen für `users add`: `ADMIN`, `REVIEWER`, `TECH`
- Mitarbeiterverwaltung über `employees add`
- `employees deactivate` und `cards deactivate` erfordern positionale IDs
- `cards replace` erfordert `--old-card-id` und `--uid-hash`
- `users deactivate`, `users reactivate` und `users change-role` erfordern
  ein eigenes `--user-id` für das Zielkonto
- Kartenzuweisung über `cards assign --uid-hash`
- Terminal-UI mit Pflichtparametern `--db`, `--numpad`, `--rfid`,
  `--terminal-id`
- Admin-CLI mit verpflichtendem `--db`; Benutzer-ID alternativ über
  `ADMIN_USER_ID`
- `setup.py` unterstützt nicht-interaktiven Aufruf mit `--backup-dir` und
  `--export-dir`
- Vierstellige Migrationsversionen `0001` bis `0006`
- NAS-bezogene Konfigurationsschlüssel im Backup-Skript
- `scripts/verify_hardware.py` für Hardware-Smoke-Tests
- `run_audit.sh` und `scripts/generate_audit_notes.py` für Code-Audits
  (Details siehe Abschnitt „Code-Audit" oben)

## Nicht überbehaupten

Die folgenden Punkte sollten in einer technischen Dokumentation nur dann
detailliert dargestellt werden, wenn ihre Implementierung vollständig gelesen
und verifiziert wurde:

- genaue interne RFID-Hash-Bildung und zugehörige Dateipfade
- konkrete Restore-Abläufe und Restore-Befehle
- konkrete `system_events`-Ereignistypen außerhalb nachweislich gelesener
  Stellen
- exakte Inhalte nicht gelesener Module oder Verzeichnisse
- Hardware-Aussagen zu Plattformen, die im gelesenen Code nicht ausdrücklich
  genannt sind

## Empfohlene nächste Prüfungen

Für eine vollständige, dauerhaft belastbare Dokumentation sollten als nächstes
gezielt separat geprüft werden:

1. `migrations/0001_schema.sql` im Volltext für die exakte Datenbankdokumentation
2. `src/arbeitszeit/domain/enums.py` für belastbare Dokumentation der Enums
3. `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` für belastbare
   Hardwarebeschreibung
4. `scripts/show_config.py` nur dann dokumentieren, wenn seine Optionen und
   Ausgabeformate tatsächlich gelesen wurden
5. Admin-CLI-Unterdateien `bookings.py`, `reports.py`, `schedule.py` und
   `system.py` für vollständige Befehls- und Rollenbeschreibung
