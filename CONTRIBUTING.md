# Beitragsrichtlinien für „arbeitszeit“

Dieses Dokument beschreibt die technischen und organisatorischen Leitlinien für Beiträge zum Projekt **arbeitszeit**.

Ziel ist eine nachvollziehbare, robuste und langfristig wartbare Codebasis mit klarer Trennung von Fachlogik, Infrastruktur und Präsentation.

---

## 1. Zielgruppe dieses Dokuments

Dieses Dokument richtet sich an:

- die Hauptentwicklerin / den Hauptentwickler des Projekts,
- weitere Entwicklerinnen und Entwickler, die Änderungen einbringen,
- Personen, die Fehleranalysen oder Refactorings durchführen.

---

## 2. Architekturgrundsätze

Das Projekt verwendet ein `src`-Layout mit einer Schichtenstruktur:

- `src/arbeitszeit/domain/`
  Fachmodell, Enums, Fehler, Audit-Ereignisse, Ports/Interfaces.

- `src/arbeitszeit/application/`
  Use-Cases, Commands, Result-Objekte, Unit-of-Work-Abstraktionen.

- `src/arbeitszeit/infrastructure/`
  Konkrete Implementierungen (SQLite, Hardware, Export, Backup, Systemcheck).

- `src/arbeitszeit/presentation/`
  Terminal-UI, Admin-CLI und Admin-GUI (tkinter), keine direkte Datenbank- oder Hardwarelogik.

**Grundregeln:**

- Domain kennt keine Infrastruktur- oder Präsentationsdetails.
- Application hängt nur von Domain, nicht von Infrastruktur.
- Infrastructure implementiert Ports aus Domain/Application, kennt aber keine Präsentationsdetails.
- Presentation verwendet Use-Cases (Application) und Infrastruktur über definierte Schnittstellen.

Neue Funktionen sind so zu entwerfen, dass diese Trennung erhalten bleibt.

---

## 3. Entwicklungsumgebung

### 3.1 Python-Version

- Zielversion laut `pyproject.toml`: `>=3.14,<3.15`.
- Entwickelt wird unter Linux (Mint / Lubuntu).

### 3.2 Setup für Entwicklung

Empfohlene Schritte:

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python scripts/init_db.py
pytest
```

Spezifische HID-Hardware (RFID-Reader, Numpad) ist für die meisten Tests nicht erforderlich, da es Simulatoren gibt.

---

## 4. Code-Stil und Formatierung

### 4.1 Allgemeines

- Schreibe klaren, gut lesbaren Python-Code.
- Bevorzuge kleine, gut benannte Funktionen und Klassen.
- Keine Geschäftslogik in CLI- oder UI-Code – immer über Use-Cases.

### 4.2 Ruff

Das Projekt verwendet `ruff` als Linter/Format-Checker (siehe `pyproject.toml`).

Typischer Aufruf:

```bash
ruff check src tests
```

Erwartung:

- Commits unter `main` sollen ruff-clean sein (keine neuen Verstöße).
- Bestehende Altverstöße können schrittweise bereinigt werden, neue werden nicht eingeführt.

---

## 5. Tests

### 5.1 Test-Framework

- Tests laufen mit `pytest`.
- Testpfad ist in `pyproject.toml` als `tests` konfiguriert.

Ausführung:

```bash
pytest
```

Für Coverage:

```bash
pytest --cov=arbeitszeit
```

### 5.2 Testebenen

Struktur von `tests/`:

- `tests/domain/` – reine Domain-Logik.
- `tests/application/` – Use-Cases, Commands, Ergebnisobjekte.
- `tests/integration/` – Interaktion zwischen Application und Infrastructure.
- `tests/e2e/` – End-to-End-Szenarien (z.B. komplette Buchungsläufe).
- `tests/presentation/` – Tests der Präsentationsschicht (z.B. Terminal-UI-Buchungsschleife).
- `tests/test_migrations.py` – Prüfung der SQL-Migrationen.

Regel:

- Jede neue fachliche Funktionalität benötigt mindestens einen passenden Test.
- Fehlerkorrekturen sollten nach Möglichkeit einen Regressions-Test erhalten.

---

## 6. Datenbank / Migrationen

### 6.1 Migrationen

- Migrationen liegen unter `migrations/` und werden von `scripts/init_db.py` ausgeführt.
- Neue Schemaänderungen erhalten eine neue numerische Migration, z.B. `0007_beschreibung.sql`.
- Bestehende Migrationen werden nicht nachträglich geändert, sobald sie in `main` gelandet sind.
- Migrationen sollen möglichst idempotent sein.

### 6.2 Tests für Migrationen

Nach Schemaänderungen:

```bash
pytest tests/test_migrations.py
```

Sicherstellen, dass:

- eine frische DB mit allen Migrationen erzeugt werden kann,
- Upgrade von bestehenden Ständen möglich bleibt,
- die Schemaerwartungen der Domain-/Application-Schicht erfüllt sind.

---

## 7. Hardware und Systemnähe

### 7.1 Hardware-Schicht

- HID-/evdev-Logik gehört nach `src/arbeitszeit/infrastructure/hardware/`.
- Terminal-UI und Admin-CLI greifen nur über abstrahierte Interfaces auf Hardware zu.

### 7.2 Simulatoren

Für Tests ohne reale Hardware:

- `infrastructure/hardware/simulator.py` verwenden.
- Tests so schreiben, dass sie ohne echte `/dev/input/event*`-Geräte laufen.

Keine Hardcodierung von produktiven Gerätpfaden in Code oder Tests.

---

## 8. Commit-Stil

### 8.1 Sprache und Präfixe

- Commit-Messages in **deutscher Sprache**.
- Präfixe (angelehnt an konventionelle Commits):

  - `feat:` – neue Funktionalität
  - `fix:` – Fehlerkorrektur
  - `docs:` – Dokumentation
  - `refactor:` – Umbau ohne fachliche Änderung
  - `test:` – Tests ergänzt/geändert
  - `chore:` – Aufräumen, CI, Hilfsskripte

Beispiele:

- `feat: Nachtragsworkflow für Wochenenden ergänzt`
- `fix: Prüfstatus bei offenen Pausen korrigiert`
- `docs: Betriebsdokumentation um Backup-Anleitung erweitert`
- `test: e2e-Szenario für Ruhezeitverstoß ergänzt`

### 8.2 Inhalt eines Commits

- Ein Commit = eine kohärente Änderung.
- Keine Vermischung von großem Refactoring und fachlicher Änderung.
- Keine reinen Format-Commits, sofern sie nicht explizit Teil eines Refactoring-Schritts sind.

---

## 9. Umgang mit Fachlogik

### 9.1 Pflichtenheft / Regelwerk

Änderungen, die Anforderungen aus

- `pflichtenheft_arbeitszeit_v6.md` oder
- `regelwerk_arbeitszeit_v5.md`

betreffen, sind zu prüfen auf:

1. Anpassung des Pflichtenhefts/Regelwerks nötig?
2. Ergänzung in `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` sinnvoll?
3. Bedarf für neue Test-/Auditnotizen?

Fachliche Regeln werden nicht stillschweigend nur im Code geändert.

### 9.2 Compliance-Logik

Prüfungen zu ArbZG (Höchstarbeitszeit, Pausen, Ruhezeiten):

- Änderungen nur nach klarer fachlicher Begründung.
- Immer mit passenden Tests (inkl. Grenzfälle).
- Änderung kurz in einer Test-/Planungsmatrix dokumentieren (z.B. `docs/betrieb/nachweise/testmatrix_revision_v1.md`).

---

## 10. Dokumentation

### 10.1 README / Handbuch

- `README.md` erklärt technischen Einstieg und Struktur.
- `handbuch_arbeitszeit.md` / HTML-Version dokumentieren Betrieb und Bedienung.
- `handbuch_arbeitszeit.md` wird aus den Kapitel-Quelldateien unter `docs/module/`
  (`handbuch_overview.md`, `handbuch_installation.md`, `handbuch_presentation.md`,
  `handbuch_application_layer.md`, `handbuch_domain.md`, `handbuch_infrastructure.md`,
  `handbuch_audit.md`, `handbuch_show_config.md`) zusammengeführt. Inhaltliche Änderungen erfolgen zuerst im
  jeweiligen Kapitel-Modul unter `docs/module/` und werden anschließend in die
  zusammengeführte Gesamtdatei `handbuch_arbeitszeit.md` übernommen.

Bei Änderungen an Bedienabläufen, CLI-Optionen, Terminal-UI:

- README/Handbuch überprüfen und bei Bedarf anpassen.
- Installationsanleitung (`installationsanleitung_arbeitszeit.md`) ggf. mitziehen.

### 10.2 Datenschutz und Betrieb

Relevante Dokumente:

- `docs/datenschutz/vvt_arbeitszeit_v1.md`
- `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`
- `docs/betrieb/rollenzuweisung.md`

Änderungen an Rollen, Zugriffslogik, Export, Backup oder Audit sollten – falls relevant – dort nachgeführt werden.

---

## 11. Fehlerberichte und Änderungen

### 11.1 Fehlerberichte

Ein sinnvoller Fehlerbericht enthält:

- kurze Beschreibung,
- erwartetes vs. tatsächliches Verhalten,
- betroffene Komponente (z.B. „Admin-CLI Bookings“, „Terminal-UI“, „Backup“),
- Schritte zur Reproduktion,
- relevante Log- oder Fehlermeldungen.

### 11.2 Änderungen (Branches / PRs)

Empfohlener Aufbau:

1. Beschreibung: Was ändert sich, warum?
2. Betroffene Module: Domain / Application / Infrastructure / Presentation.
3. Tests: Welche Tests wurden ergänzt/geändert?
4. Dokumentation: Was musste angepasst werden?

---

## 12. Sicherheit und Datenschutz

Bei sicherheitsrelevanten Änderungen (Zugriffsrechte, Passwortspeicherung, Exportpfade):

- besonders sorgfältig prüfen,
- ggf. Hinweise in `docs/datenschutz/` oder einem zukünftigen `SECURITY.md` ergänzen,
- niemals echte Zugangsdaten, Produktivpfade oder personenbezogene Daten committen.

---

## 13. Kontakt

Interner Ansprechpartner für Beiträge und Architekturentscheidungen:

- *(Name / Kontakt der Hauptentwicklerin bzw. des Hauptentwicklers eintragen)*

Änderungen mit Auswirkungen auf Recht, Datenschutz oder Organisation sind mit der Praxisleitung bzw. der verantwortlichen Stelle abzustimmen.

---

## 14. Branch-Strategie und Release-Tagging

### 14.1 Branch-Strategie (einfaches Modell)

Dieses Projekt wird überwiegend allein gepflegt. Es wird daher ein bewusst einfaches Branch-Modell verwendet:

- `main` enthält den jeweils stabilen Stand.
- Für Änderungen, die größer sind als ein Kleinst-Fix, wird ein kurzer Branch angelegt:
  - `feature/<kurze-beschreibung>` für neue Funktionen
    z.B. `feature/nachtrags-workflow`
  - `fix/<kurze-beschreibung>` für Fehlerkorrekturen
    z.B. `fix/ruhezeit-pruefung`

Typischer Ablauf:

```bash
git checkout main
git pull origin main
git checkout -b feature/neue-arbeitszeitpruefung
# ... Änderungen vornehmen, testen ...
git commit -m "feat: neue Arbeitszeitprüfung für Samstage"
git checkout main
git pull origin main
git merge feature/neue-arbeitszeitpruefung
git push origin main
git branch -d feature/neue-arbeitszeitpruefung
```

Regeln:

- `main` soll immer lauffähigen Code enthalten.
- Direkt-Commits auf `main` sind für kleine, klar überschaubare Änderungen zulässig (z.B. Dokumentation, Tippfehler-Fixes).
- Für größere fachliche Änderungen und alles mit Migrationen wird ein Feature-/Fix-Branch verwendet.
- Branches werden nach erfolgreichem Merge wieder gelöscht, um das Repository übersichtlich zu halten.

### 14.2 Versionierung (SemVer light)

Versionierung erfolgt nach einem vereinfachten semantischen Schema:

- `MAJOR.MINOR.PATCH` (z.B. `0.2.1`)

Richtlinien:

- **MAJOR**: Inkompatible Änderungen (z.B. DB-Schema-Änderungen, die alte Stände nicht mehr direkt nutzbar machen).
- **MINOR**: Neue Funktionen, die abwärtskompatibel sind.
- **PATCH**: Fehlerkorrekturen und kleine Verbesserungen ohne Verhaltensbruch.

Die Versionsnummer wird in `pyproject.toml` unter `[project].version` gepflegt. Für das Projektstadium vor produktiver Abnahme können weiterhin `0.x.y`-Versionen verwendet werden.

### 14.3 Release-Tags

Wichtige stabile Stände werden in `main` getaggt:

```bash
git checkout main
git pull origin main
# Version in pyproject.toml anpassen, Tests laufen lassen
git tag -a v0.2.0 -m "Release 0.2.0 – erweiterte Nachtragsfunktionen"
git push origin v0.2.0
```

Empfehlung:

- Tags als `vMAJOR.MINOR.PATCH`, z.B. `v0.1.0`, `v0.2.0`.
- Vor dem Tag:
  - Versionsnummer aktualisieren,
  - `pytest` und `ruff check` laufen lassen,
  - CHANGELOG/Dokumentation aktualisieren.
