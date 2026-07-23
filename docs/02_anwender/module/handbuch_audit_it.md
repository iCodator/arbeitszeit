# Audit und Codeprüfung — technisches Referenzhandbuch

**Kapitel:** 9-IT
**Version:** 1.2
**Stand:** Juli 2026
**Zielgruppe:** Entwickler, Systemverantwortliche
**Quelldateien:** `run_audit.sh`, `scripts/generate_audit_notes.py`,
`src/arbeitszeit/infrastructure/system_check.py`

## Zweck

Das Projekt unterscheidet zwei Arten von Prüfläufen:

1. **Statische Codeprüfung** (`run_audit.sh`) — Entwickler-Werkzeug für
   Codequalität, Typen, Sicherheit, Architektur und Testabdeckung.
2. **Laufzeit-Systemprüfung** (`system_check.py`) — Betriebsdiagnose,
   die vor jedem Terminalbetrieb und auf Abruf über die Admin-CLI ausgeführt
   wird.

## run_audit.sh — statische Codeprüfung

Das Skript liegt im Projektroot. Es führt folgende Werkzeuge nacheinander aus
und schreibt alle Ausgaben in ein Unterverzeichnis unter
`docs/audits/reports/<YYYY-MM-DD_HH-MM>/`.

### Shell-Einstellungen

```bash
set -uo pipefail
```

Kein `-e`: Werkzeuge dürfen mit Exit-Code 1 enden (`|| true`), ohne das
Skript abzubrechen. Der Exit-Code des Skripts selbst ist immer 0.

### Werkzeuge

| Werkzeug | Befehl | Ausgabedatei | Exit 1 erlaubt |
| --- | --- | --- | --- |
| ruff | `ruff check src/ tests/` | `ruff-report.txt` | ja |
| mypy | `mypy src/arbeitszeit/` | `mypy-report.txt` | ja |
| radon cc | `radon cc -s -a src/arbeitszeit` | `radon-cc.txt` | nein |
| radon raw | `radon raw src/arbeitszeit` | `radon-raw.txt` | nein |
| import-linter | `lint-imports` | `import-linter.txt` | ja |
| bandit | `bandit -r src/arbeitszeit -f json` | `bandit-report.json` | ja |
| pytest + coverage | `pytest --cov=arbeitszeit --cov-report=xml --cov-report=html` | `pytest.txt`, `coverage.xml`, `htmlcov/` | ja |
| generate_audit_notes | `python scripts/generate_audit_notes.py` | `audit-notes-<DATUM>.md` | nein |

Alle Ausgabedateien landen gemeinsam im datierten Unterverzeichnis:
`docs/audits/reports/2026-07-17_14-30/ruff-report.txt` usw.

### generate_audit_notes.py

Das Skript in `scripts/generate_audit_notes.py` ist ein Nachverarbeitungs-
werkzeug. Es liest die Ausgabedateien von ruff, mypy, radon, bandit und das
coverage-XML aus, aggregiert die Befunde und erzeugt eine strukturierte
Markdown-Zusammenfassung (`audit-notes-<DATUM>.md`) im selben Verzeichnis.

Dieses Skript ist ein Entwickler-Diagnosewerkzeug, kein Betriebswerkzeug
für das Praxispersonal.

### Architekturprüfung via import-linter

`lint-imports` prüft die Schichtengrenzen gemäß `pyproject.toml`:

```text
presentation > infrastructure > application > domain
```

Jede Schicht darf nur auf darunter liegende Schichten zugreifen.
Verstöße werden in `import-linter.txt` protokolliert.

## Laufzeit-Systemprüfung

Quelldatei: `src/arbeitszeit/infrastructure/system_check.py`

`run_system_check(db_path, *, rfid_path, app_config)` führt
8 Prüfungen aus. Das Ergebnis wird in `system_events` geschrieben:
`SELFTEST_OK` bei Erfolg, `SELFTEST_FAIL` bei mindestens einem Fehler.

### Aufruf über die Admin-CLI

```bash
azadmin system check --db arbeitszeit.db
```

### Aufruf automatisch im Terminalbetrieb

Die Terminal-UI ruft `run_system_check()` vor dem Start der Buchungsschleife
auf. Bei Fehlern gibt sie eine Warnung aus, blockiert den Buchungsbetrieb
aber **nicht**.

### Die 8 Prüfungen

| Nr. | Prüfung | Beschreibung |
| --- | --- | --- |
| 1 | `_check_db_access` | Migrationsstand: `schema_migrations` vs. `.sql`-Dateien in `migrations/` |
| 2 | `_check_config_keys` | 3 Pflicht-Keys in `system_config`: `app.timezone`, `backup.nas_enabled`, `backup.nas_path` |
| 3 | `_check_nas` | `Path.exists()` + `os.access(W_OK)` für den NAS-Pfad — kein Netzwerktest |
| 4 | `_check_fk_consistency` | `PRAGMA foreign_key_check` — prüft referenzielle Integrität aller Fremdschlüssel |
| 5 | `_check_config_file_paths` | `backup_dir` und `export_dir` müssen als Verzeichnisse existieren |
| 6 | `_check_ntp` | `/usr/bin/timedatectl show` (absoluter Pfad, kein `shell=True`), timeout 5 s; prüft `NTP=yes` und `NTPSynchronized=yes` |
| 7 | `_check_audit_hmac_key` | `AUDIT_HMAC_KEY` Umgebungsvariable gesetzt und nicht leer — fehlt sie, meldet der Systemcheck `SELFTEST_FAIL: audit_hmac_key` |
| 8 | `_check_devices` | `Path.exists()` + `os.access(R_OK)` für den RFID-Gerätepfad |

### Ergebnisauswertung

Das zurückgegebene Objekt hat `result.overall_ok` (bool) und `result.checks`
(Liste mit Name und Detail jeder Prüfung). Die Terminal-UI verwendet
`result.checks` zur Ausgabe von Warnmeldungen.

## Prüfberichte und Dokumentation

Abgeschlossene Audit-Läufe werden unter `docs/audits/reports/` abgelegt.
Der Bereich `docs/07_pruefberichte/` enthält die zugehörigen Prüfberichte.

## Admin-CLI: audit open-shifts

Quelldatei: `src/arbeitszeit/presentation/admin_cli/audit.py`

Berechtigung: `ADMIN` oder `REVIEWER`

```bash
azadmin audit open-shifts --db arbeitszeit.db [--days N]
```

| Option | Standard | Beschreibung |
| --- | --- | --- |
| `--days N` | 30 | Zeitraum rückwirkend in Tagen (muss > 0 sein) |

Der Befehl liest alle `OPEN_SHIFT_PREVIOUS_DAY_DETECTED`-Einträge aus
`audit_log` für den angegebenen Zeitraum und gibt sie tabellarisch aus:

```text
Offene Vortagsschichten — letzte 30 Tag(e):

  Erkannt am        Mitarbeiter               Vortag      Letzter Typ  Letzte Buchung
  ----------------  -------------------------  ----------  -----------  ----------------
  22.07.2026 08:03  Muster, Anna              2026-07-21  COME         21.07.2026 08:01

1 offene Vortagsschicht(en) in den letzten 30 Tag(en).
```

| Spalte | Quelle in `details_json` |
| --- | --- |
| `Erkannt am` | `event_at` des Audit-Eintrags |
| `Mitarbeiter` | `last_name`, `first_name` aus `employees` (JOIN) |
| `Vortag` | `previous_day_date` |
| `Letzter Typ` | `last_known_booking_type` |
| `Letzte Buchung` | `last_known_booking_at` |

Ein `OPEN_SHIFT_PREVIOUS_DAY_DETECTED`-Eintrag wird von `BookUseCase`
geschrieben, wenn der erste Scan eines Tages erkennt, dass am Vortag
Buchungen ohne abschließendes `GO` vorlagen. Der Befund blockiert keine
laufende Buchung und erzeugt keinen Review-Case — er erfordert manuelle
Nachbearbeitung durch die Praxisleitung.
