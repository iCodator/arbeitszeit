# Prüfbericht: `docs/module/handbuch_audit.md` (Audit und Prüfstatus)

## Gesamteinschätzung

Dieses Kapitel unterscheidet sich strukturell von den übrigen Handbuchkapiteln: Es ist selbst eine Meta-Prüfliste mit den Abschnitten „Sicher belegt", „Nicht überbehaupten" und „Empfohlene nächste Prüfungen", keine klassische Nutzerdokumentation. Alle 18 unter „Sicher belegt" aufgeführten Einzelaussagen wurden gegen den Code verifiziert und sind vollständig korrekt. Der Abschnitt „Nicht überbehaupten" formuliert bewusst Zurückhaltung statt Tatsachenbehauptungen und ist daher nicht im klassischen Sinn prüfbar. Der Abschnitt „Empfohlene nächste Prüfungen" verweist auf konkret existierende Dateien. Substanzielle Fehler wurden nicht gefunden.

## Befunde (Abschnitt „Sicher belegt")

- Aussage: „Python-Anforderung `>=3.14,<3.15`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeile 9 (`requires-python = ">=3.14,<3.15"`)
  Bewertung: Wortgleich bestätigt.

- Aussage: „Paketabhängigkeiten aus `pyproject.toml`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen 10–22
  Bewertung: Abhängigkeiten existieren wie referenziert.

- Aussage: „Trennung in `presentation`, `infrastructure`, `application`, `domain`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen 105–110 (`[tool.importlinter.contracts]`, `layers = ["arbeitszeit.presentation", "arbeitszeit.infrastructure", "arbeitszeit.application", "arbeitszeit.domain"]`)
  Bewertung: Exakte Schichtnamen und Reihenfolge bestätigt.

- Aussage: „Vorhandensein von `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py`."
  Status: korrekt
  Beleg: Verzeichnisauflistung `scripts/` bestätigt alle drei Dateien.
  Bewertung: Bestätigt.

- Aussage: „Bootstrap des ersten Administratorkontos."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Zeilen 202–207 (`users_sub.add_parser("bootstrap", ...)`)
  Bewertung: Bestätigt.

- Aussage: „Zulässige Rollen für `users add`: `ADMIN`, `REVIEWER`, `TECH`."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Zeile 174 (`choices=["ADMIN", "REVIEWER", "TECH"]`)
  Bewertung: Exakt bestätigt.

- Aussage: „Mitarbeiterverwaltung über `employees add`."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/employees.py`, Zeile 140
  Bewertung: Bestätigt.

- Aussage: „`employees deactivate` und `cards deactivate` erfordern positionale IDs."
  Status: korrekt
  Beleg: `employees.py`, Zeile 146 (`deact.add_argument("id", type=int)`) und Zeile 161 (`deact_card.add_argument("id", type=int)`)
  Bewertung: Beide verwenden ein positionales Argument `id`, kein Options-Flag.

- Aussage: „`cards replace` erfordert `--old-card-id` und `--uid-hash`."
  Status: korrekt
  Beleg: `employees.py`, Zeilen 156–158
  Bewertung: Exakt bestätigt.

- Aussage: „`users deactivate`, `users reactivate` und `users change-role` erfordern ein eigenes `--user-id` für das Zielkonto."
  Status: korrekt
  Beleg: `user_accounts.py`, Zeilen 189–198: jeweils eigenes `--user-id`-Argument mit unterschiedlichem `dest` (`deactivate_user_id`, `reactivate_user_id`, `target_user_id`)
  Bewertung: Bestätigt, inklusive der Tatsache, dass dies ein separates Argument zum globalen `--user-id` des aufrufenden Admin-Kontos ist.

- Aussage: „Kartenzuweisung über `cards assign --uid-hash`."
  Status: korrekt
  Beleg: `employees.py`, Zeile 154
  Bewertung: Bestätigt.

- Aussage: „Terminal-UI mit Pflichtparametern `--db`, `--numpad`, `--rfid`, `--terminal-id`."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/terminal_ui/main.py`, Zeilen 146–149, alle vier mit `required=True`
  Bewertung: Exakt bestätigt.

- Aussage: „Admin-CLI mit verpflichtendem `--db`; Benutzer-ID alternativ über `ADMIN_USER_ID`."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/main.py`, Zeilen 39–44 (`--db`, `required=True`) und Zeilen 16–32 (`_resolve_user_id`: Fallback auf `os.environ.get("ADMIN_USER_ID")`)
  Bewertung: Bestätigt.

- Aussage: „`setup.py` unterstützt nicht-interaktiven Aufruf mit `--backup-dir` und `--export-dir`."
  Status: korrekt
  Beleg: `scripts/setup.py`, Zeilen 75–86
  Bewertung: Bestätigt.

- Aussage: „Vierstellige Migrationsversionen `0001` bis `0006`."
  Status: korrekt
  Beleg: Verzeichnis `migrations/` enthält genau `0001_schema.sql` bis `0006_system_events_application_error.sql`
  Bewertung: Bestätigt.

- Aussage: „NAS-bezogene Konfigurationsschlüssel im Backup-Skript."
  Status: korrekt
  Beleg: `scripts/backup.py`, Zeilen 7–8, 53–56 (`backup.nas_enabled`, `backup.nas_path`); `src/arbeitszeit/infrastructure/backup/backup_service.py`, Zeilen 70–96 (`sync_to_nas`)
  Bewertung: Bestätigt.

- Aussage: „`scripts/verify_hardware.py` für Hardware-Smoke-Tests."
  Status: korrekt
  Beleg: Datei existiert im Repository (`scripts/verify_hardware.py`, 16430 Bytes)
  Bewertung: Bestätigt.

- Aussage: „`run_audit.sh` und `scripts/generate_audit_notes.py` für Code-Audits."
  Status: korrekt
  Beleg: Beide Dateien existieren im Repository (`run_audit.sh` ausführbar, `scripts/generate_audit_notes.py`, 20047 Bytes)
  Bewertung: Bestätigt.

## Befunde (Abschnitt „Nicht überbehaupten")

Status: nicht anwendbar / korrekt im Sinne der Selbstbeschreibung
Bewertung: Dieser Abschnitt formuliert bewusst methodische Vorsicht (z. B. „genaue interne RFID-Hash-Bildung ... nur wenn vollständig gelesen") statt inhaltlicher Tatsachenbehauptungen. Er ist daher nicht im Sinne von „korrekt/inkorrekt gegenüber dem Code" prüfbar, sondern beschreibt eine Arbeitsregel für künftige Dokumentationsarbeit. Kein Widerspruch zum Code feststellbar.

## Befunde (Abschnitt „Empfohlene nächste Prüfungen")

- Aussage: Verweis auf `migrations/0001_schema.sql`, `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`, `scripts/show_config.py`, sowie `bookings.py`, `reports.py`, `schedule.py`, `system.py` im Admin-CLI.
  Status: korrekt
  Beleg: Alle genannten Dateien/Pfade existieren im Repository und wurden in früheren bzw. weiteren Prüfzyklen dieser Space-Historie bereits einzeln behandelt (`enums.py` und `evdev_reader.py` liegen bereits als eigene Prüfberichte vor).
  Bewertung: Die Empfehlungsliste ist technisch zutreffend; ein Teil der empfohlenen Prüfungen wurde in dieser Space-Historie bereits durchgeführt.

## Anpassungsvorschläge

Keine. Alle prüfbaren Aussagen des Kapitels sind durch das Repository vollständig belegt. Kein Korrekturbedarf.

## Nachtrag: Erweiterung um Abschnitt „Code-Audit“ (Juli 2026)

### Gesamteinschätzung

Auf Anfrage wurde `run_audit.sh` gezielt analysiert und das Kapitel um einen eigenen, ausführlichen Abschnitt „Code-Audit (`run_audit.sh` und `scripts/generate_audit_notes.py`)“ ergänzt (Version 1.0 → 1.1). Zuvor war `run_audit.sh` im Kapitel nur als einzelner Stichpunkt ohne technische Details geführt. Alle neu aufgenommenen Aussagen sind durch direktes Lesen von `run_audit.sh`, `scripts/generate_audit_notes.py` und `pyproject.toml` belegt.

### Befunde (neuer Abschnitt „Code-Audit")

- Aussage: „`run_audit.sh` ist ein ausführbares Shell-Skript im Repository-Wurzelverzeichnis (56 Zeilen).“
  Status: korrekt
  Beleg: `run_audit.sh`, Dateiattribute `-rwxr-xr-x`, Zeilenzahl 56 (vollständig gelesen).
  Bewertung: Bestätigt.

- Aussage: „Das Skript führt Ruff, Mypy, Radon (cc + raw), import-linter, Bandit und pytest+Coverage aus und schreibt die Rohdaten nach `docs/audits/reports/<DATUM>/`.“
  Status: korrekt
  Beleg: `run_audit.sh`, Zeilen 9–41 (`BASE_DIR="docs/audits/reports"`, `RUN_DIR="$BASE_DIR/$DATE"`, jeweilige Tool-Aufrufe mit `tee "$RUN_DIR/..."`).
  Bewertung: Bestätigt, inklusive exakter Dateinamen der Rohausgaben.

- Aussage: „Das Skript verwendet `set -uo pipefail`, bewusst ohne `set -e`, da Analyse-Tools mit Exit-Code 1 zurückkehren dürfen, ohne den Lauf abzubrechen.“
  Status: korrekt
  Beleg: `run_audit.sh`, Zeilen 2–5 (Kommentar) und Zeile 5 (`set -uo pipefail`).
  Bewertung: Wortgleich aus dem Skriptkommentar übernommen.

- Aussage: „Ruff, Mypy, import-linter, Bandit und pytest sind mit `|| true` abgesichert; die beiden Radon-Aufrufe nicht.“
  Status: korrekt
  Beleg: `run_audit.sh`, Zeilen 14, 17, 26, 29–30, 33–37 (`|| true`) gegenüber Zeilen 20, 23 (`radon cc`, `radon raw`, ohne `|| true`).
  Bewertung: Bestätigt durch Zeilenvergleich.

- Aussage: „`run_audit.sh` ruft am Ende automatisch `scripts/generate_audit_notes.py --report-dir "$RUN_DIR" --output "$BASE_DIR/audit-notes-$DATE.md"` auf.“
  Status: korrekt
  Beleg: `run_audit.sh`, Zeilen 39–41.
  Bewertung: Bestätigt.

- Aussage: „`scripts/generate_audit_notes.py` hat 596 Zeilen, unterstützt `--report-dir` (Standard `docs/audits/reports`) und `--output` (Standard `<report-dir>/audit-notes-<DATUM>.md`).“
  Status: korrekt
  Beleg: `scripts/generate_audit_notes.py`, vollständig gelesen (596 Zeilen); Argument-Parser-Definitionen für `--report-dir` und `--output`.
  Bewertung: Bestätigt.

- Aussage: „Jeder Parser liefert bei fehlender Quelldatei `{"available": False}` statt geschätzter Werte.“
  Status: korrekt
  Beleg: `scripts/generate_audit_notes.py`, Parserfunktionen `parse_ruff`, `parse_mypy`, `parse_radon_cc`, `parse_radon_raw`, `parse_import_linter`, `parse_bandit`, `parse_coverage` (jeweils früher Return bei nicht existierender Datei).
  Bewertung: Bestätigt.

- Aussage: „Der Bericht ist in acht fester Abschnittsreihenfolge aufgebaut: Überblick, Linting (Ruff), Typprüfung (Mypy), Komplexität (Radon), Architektur (import-linter), Security (Bandit), Tests & Coverage, Maßnahmenplan.“
  Status: korrekt
  Beleg: `scripts/generate_audit_notes.py`, Funktion `render()`, Zeilen 312–478 (Abschnitts-Überschriften in dieser Reihenfolge) sowie Zeilen 479–490 (Maßnahmenplan).
  Bewertung: Bestätigt einschließlich der jeweils dargestellten Inhalte (Hotspot-Tabelle CC ≥ 10, Bandit-Tabelle HIGH+MEDIUM, Coverage-Tabelle < 60 %).

- Aussage: „Der Maßnahmenplan prüft in dieser Reihenfolge: Bandit HIGH+MEDIUM > 0, import-linter-Verstöße > 0, Mypy-Fehler > 0 bei Misserfolg, Ruff-Gesamtbefunde > 0, Radon-Hotspots mit CC ≥ 15, Gesamt-Coverage < 80 %.“
  Status: korrekt
  Beleg: `scripts/generate_audit_notes.py`, Funktion `_build_actions()`, Zeilen 493–541, in exakt dieser Reihenfolge der `if`-Bedingungen.
  Bewertung: Bestätigt. Zusätzlich festgestellt: Der bei Coverage < 80 % erzeugte Maßnahmentext lautet wörtlich „Tests für Module mit Coverage < 60 % ergänzen“ (Zeile 537) – die Auslöseschwelle (80 %) und der im Text genannte Schwellenwert (60 %, identisch mit dem Schwellenwert der Tabelle „Dateien mit Coverage < 60 %“) weichen voneinander ab. Dies ist eine Beobachtung zum bestehenden Skriptverhalten, keine Handbuch-Falschaussage, da das Handbuch diesen Sachverhalt nun wörtlich wiedergibt.

- Aussage: „`run_audit.sh` benötigt zusätzlich installierte Tools (`mypy`, `radon`, `bandit`), die in `pyproject.toml` nicht als Pflichtabhängigkeiten unter `[project.optional-dependencies]` (Gruppe `dev`) geführt sind; dort stehen nur `pytest`, `pytest-cov`, `pypdf`, `ruff` und `import-linter`.“
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen `[project.optional-dependencies]` / `dev = [...]`.
  Bewertung: Bestätigt; entspricht zudem wortgleich einer bereits im Archiv (`docs/archive/handbuch/handbuch_arbeitszeit_v1.2.md`, Zeile 499) enthaltenen, unabhängig geprüften Aussage.

- Aussage: Konfigurationsdetails zu `[tool.ruff]`, `[tool.mypy]` und `[tool.importlinter]` (Line-Length 100, Python 3.14, strict-Mypy-Flags, Layer-Contract `presentation → infrastructure → application → domain`).
  Status: korrekt
  Beleg: `pyproject.toml`, Abschnitte `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.mypy]`, `[tool.importlinter]`, `[[tool.importlinter.contracts]]`.
  Bewertung: Bestätigt, wortgleiche Übernahme der Konfigurationswerte.

- Aussage: „Im Repository liegen zwei Audit-bezogene Verzeichnisse nebeneinander: `docs/audits/reports/` (Rohdaten vom 16.06.2026, entspricht dem in `run_audit.sh` fest codierten Pfad) und `docs/08_planung_intern/audits/` (ältere manuelle Berichte sowie eine gerenderte Fassung `reports/audit-notes-2026-06-16.md`); eine Datei `audit-notes-2026-06-16.md` direkt unter `docs/audits/reports/` existiert nicht.“
  Status: korrekt
  Beleg: Verzeichnisauflistung `docs/audits/reports/2026-06-16/` (7 Rohdateien, keine `.md`-Datei auf Ebene `docs/audits/reports/`) sowie `docs/08_planung_intern/audits/` (`audit_arbeitszeit_v1_2026-06-11_19-28.md`, `audit_arbeitszeit_v1_2026-06-12_13-58.md`, `audit_arbeitszeit_v1_2026-06-13_09-04.md`, `audit_arbeitszeit_nachaudit_v1_2026-06-13.md`, `reports/audit-notes-2026-06-16.md`).
  Bewertung: Bestätigt. Die Ursache (frühere Dokumentationsmigration, Commit `1100542`) wurde nicht weiter untersucht, da nicht Gegenstand der Anfrage; im Handbuch wird nur der verifizierte Ist-Zustand beschrieben, keine Ursachenzuschreibung.

### Offene Punkte

- Nicht verifiziert: ob der Lauf vom 16.06.2026 tatsächlich über `run_audit.sh` erzeugt wurde oder die Rohdateien anderweitig abgelegt wurden; das Handbuch trifft dazu keine Aussage.
- Nicht verifiziert: der genaue Zeitpunkt bzw. Commit, zu dem `docs/audits/reports/audit-notes-<DATUM>.md` (Standardausgabepfad von `run_audit.sh`) zuletzt existiert hat, falls überhaupt.

### Anpassungsvorschläge

Keine weiteren. Die Ergänzung ist vollständig durch Repository-Evidenz gedeckt; die bestehenden übrigen Abschnitte des Kapitels wurden nicht verändert.
