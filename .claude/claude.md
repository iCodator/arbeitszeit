# CLAUDE.md – Entwicklungsmodus für das Projekt arbeitszeit

Dieses Dokument legt den verbindlichen Arbeitsrahmen für Claude bei der Entwicklung des Projekts `arbeitszeit` fest.
Es gilt für normale Entwicklungsarbeit, Fehlerbehebungen, Refactorings und Erweiterungen.

## 1. Projektkontext

Das Repository implementiert ein lokales Arbeitszeiterfassungssystem für eine Zahnarztpraxis.
Das System ist produktiv relevant, sicherheitsrelevant und fachlich sensibel.

Rahmenbedingungen:

- ausschließlicher lokaler Betrieb
- keine Cloud-Dienste
- keine externen Web-APIs
- SQLite als einzige produktive Datenbank
- RFID-Reader als USB-HID-Gerät
- separates USB-Numpad als Eingabegerät
- Betrieb unter Linux Mint oder Lubuntu
- Fokus auf Nachvollziehbarkeit, Stabilität, Wartbarkeit und rechtlich saubere Arbeitszeiterfassung

## 2. Verbindliche Zielsetzung

Jede Änderung muss diese Ziele unterstützen:

- fachlich korrekte Arbeitszeiterfassung
- rechtlich belastbare Nachvollziehbarkeit
- klare Trennung von Fachlogik, Infrastruktur und Bedienoberfläche
- robuste Verarbeitung von Eingaben und Fehlerfällen
- minimale Komplexität bei maximaler Verständlichkeit

Claude arbeitet in diesem Projekt nicht experimentell, sondern konservativ, präzise und risikobewusst.

## 3. Pflichtdateien vor Änderungen

Vor jeder größeren Änderung sind mindestens diese Dateien fachlich und technisch zu berücksichtigen:

- `pflichtenheft_arbeitszeit_v6.md`
- `regelwerk_arbeitszeit_v5.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `handbuch_arbeitszeit.md`
- `installationsanleitung_arbeitszeit.md`
- relevante Dateien unter `migrations/`
- relevante Tests unter `tests/`

Wenn Anforderungen unklar sind, haben die Projektdateien Vorrang vor Vermutungen.

## 4. Technischer Rahmen

Technische Randbedingungen des Projekts:

- Python 3.14
- Paketverwaltung und Konfiguration über `pyproject.toml`
- Laufzeitabhängigkeiten u. a. `evdev` und `reportlab`
- Qualitätswerkzeuge: `pytest`, `pytest-cov`, `ruff`, `mypy`, `import-linter`

Neue Abhängigkeiten dürfen nicht leichtfertig eingeführt werden.
Jede neue Abhängigkeit muss fachlich und technisch begründet sein.

## 5. Architektur

Die Projektstruktur folgt einer klaren Layered bzw. Clean Architecture:

- `src/arbeitszeit/domain`
- `src/arbeitszeit/application`
- `src/arbeitszeit/infrastructure`
- `src/arbeitszeit/presentation`

Verbindliche Import-Richtung:

`presentation -> infrastructure -> application -> domain`

Importe dürfen nur nach innen zeigen.
Kein innerer Layer darf einen äußeren Layer importieren.

### 5.1 Domain

- enthält reine Fachlogik
- enthält keine Hardware-, Datenbank-, Datei- oder UI-Abhängigkeiten
- modelliert Regeln, Zustände und fachliche Entscheidungen

### 5.2 Application

- enthält Use Cases, Orchestrierung und Schnittstellen
- koordiniert fachliche Abläufe
- kennt keine konkreten Infrastrukturdetails

### 5.3 Infrastructure

- enthält SQLite-Zugriff, Repositories, Migrationen, Hardware-Zugriff und PDF-Erzeugung
- implementiert technische Schnittstellen
- dupliziert keine Fachlogik

### 5.4 Presentation

- enthält UI-, CLI- oder sonstige Ein-/Ausgabelogik
- trifft keine eigenständigen Fachentscheidungen
- delegiert Regeln an tiefere Schichten

## 6. Arbeitsweise von Claude

Claude arbeitet nach diesem Standardablauf:

1. betroffene fachliche Regeln identifizieren
2. betroffene Layer und Module identifizieren
3. kleinste sinnvolle Änderung planen
4. Implementierung auf bestehende Architektur abstimmen
5. passende Tests ergänzen oder anpassen
6. Risiken und offene Punkte knapp benennen

Wenn Anforderungen oder Fachregeln nicht eindeutig sind, muss Claude zuerst nachfragen.
Keine stillschweigenden Annahmen bei sensibler Fachlogik.

## 7. Regeln für sicherheitsrelevante und produktive Änderungen

Dieses Projekt ist produktiv relevant.
Deshalb gilt:

- keine riskanten Schnelllösungen
- keine nicht nachvollziehbaren Seiteneffekte
- keine stillen Datenmanipulationen
- keine Workarounds, die Auditierbarkeit verschlechtern
- keine Änderungen, die nur „Tests grün machen“, aber fachlich unsauber sind

Bei Änderungen mit möglicher Auswirkung auf Arbeitszeiten, Korrekturen, Nachträge, Prüffälle oder Historie ist besonders konservativ vorzugehen.

## 8. Datenbankregeln

- SQLite ist die einzige produktive Datenbank
- Schemaänderungen nur über Dateien in `migrations/`
- keine manuellen, undokumentierten Strukturänderungen
- bestehende Daten sind zu schützen
- Migrationsverhalten muss reproduzierbar und testbar sein

Jede Datenbankänderung muss auch unter dem Gesichtspunkt der Nachvollziehbarkeit und Revisionssicherheit bewertet werden.

## 9. Hardware-Regeln

- RFID-Reader und Numpad sind reine Infrastrukturthemen
- Hardware-Zugriff ausschließlich in `infrastructure/`
- fachliche Entscheidungen nicht im Gerätetreiber treffen
- Eingaben validieren, normalisieren und robust behandeln
- Hardwarefehler explizit behandeln

## 10. Audit- und Nachvollziehbarkeitsregeln

Das System dient der Arbeitszeiterfassung und muss daher besonders nachvollziehbar sein.

Daraus folgen diese Grundsätze:

- jede fachlich relevante Änderung muss nachvollziehbar sein
- Korrekturen und Nachträge dürfen nicht als versteckte Überschreibungen umgesetzt werden
- Prüffälle müssen fachlich explizit behandelbar bleiben
- Historie darf nicht unkontrolliert verloren gehen
- Audit-relevante Informationen müssen konsistent und lesbar bleiben

## 11. Qualitätsregeln

Vor Abschluss relevanter Änderungen sind diese Qualitätsanforderungen einzuhalten:

- `ruff` ohne Fehler
- `mypy` ohne Fehler
- `pytest` für betroffene Bereiche erfolgreich
- `import-linter` ohne Architekturverletzungen

Neue öffentliche Funktionen und Methoden sind vollständig zu typannotieren.
Code soll klein, lesbar, präzise und wartbar bleiben.

## 12. Teststrategie

Tests sind auf der passenden Ebene zu ergänzen:

- Fachregeln: `tests/domain`
- Anwendungsfälle: `tests/application`
- Infrastruktur und Datenbank: `tests/integration`
- durchgängige Abläufe: `tests/e2e`
- Migrationen: `tests/test_migrations.py`

Claude soll nicht nur Code ändern, sondern immer auch die richtige Testebene mitdenken.

## 13. Was Claude vermeiden muss

- keine Cloud-Komponenten einführen
- keine zweite Datenbank einführen
- keine Layer-Verletzungen erzeugen
- keine Fachlogik in UI oder Infrastruktur verstecken
- keine unnötige Komplexität einführen
- keine Abhängigkeiten ohne Not ergänzen
- keine destruktiven Änderungen an Buchungs- oder Verlaufsdaten vorschlagen
- keine fachlich heiklen Annahmen ohne Rückfrage treffen

## 14. Commit- und Änderungsstil

- Änderungen klein und nachvollziehbar halten
- Refactoring, Fachlogikänderung und Formatierung nach Möglichkeit trennen
- Commit-Messages klar und präzise formulieren
- bei fachlich sensiblen Änderungen Zweck und Risiko klar benennen

## 15. Merksatz

Dieses Projekt ist eine produktive, lokale und fachlich sensible Anwendung.
Claude soll deshalb erst verstehen, dann nachfragen und anschließend die kleinste saubere, testbare und nachvollziehbare Änderung im Rahmen der vorhandenen Architektur umsetzen.
