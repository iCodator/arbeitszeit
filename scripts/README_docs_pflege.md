# Projektspezifische Dokumentationspflege für `arbeitszeit`

Dieses Set ist auf einen lokalen Einzelentwickler-Workflow zugeschnitten:

- Entwicklung lokal auf dem eigenen Rechner,
- Unterstützung durch KI, z. B. Claude Code,
- Push nach GitHub erst nach lokaler Prüfung,
- GitHub Actions nur als zweite Absicherung.

## Wichtige Abgrenzung

`docs/archive/` dient ausschließlich der historischen Nachvollziehbarkeit.
Dieses Verzeichnis ist für die Prüfung aktueller Dokumente bewusst irrelevant und
wird durch das Skript nicht als Quelle für die aktuelle Dokumentationsqualität
herangezogen.

## Empfohlener lokaler Ablauf

1. Lokale Änderung am Code oder an den Handbüchern vornehmen.
2. Claude Code nur mit klar abgegrenztem Auftrag verwenden, z. B. Abschnitt prüfen,
   Abschnitt überarbeiten, Commit-Text formulieren.
3. Vor jedem Commit lokal ausführen:

   `bash ./scripts/run_docs_maintenance.sh .`

4. Fehler immer beheben.
5. Warnungen bewusst manuell prüfen.
6. Erst danach committen und nach GitHub pushen.

## Was das Skript prüft

Das Skript ist explizit auf die aktuelle `arbeitszeit`-Struktur zugeschnitten.
Es prüft unter anderem:

- Existenz der aktuellen Doku-Hauptbereiche unter `docs/`,
- Existenz von `docs/02_anwender/module/`,
- Existenz von `README.md`, `pyproject.toml` und `run_audit.sh`,
- pro Markdown-Datei genau ein H1,
- Pflichtfelder `Kapitel`, `Version`, `Stand`, `Quelldatei`,
- Übereinstimmung von `Quelldatei` mit dem realen Dateipfad,
- parsebare Versionsangabe im Format `X.Y`,
- weiche Warnungen für lange Zeilen,
- weiche Warnungen für Bare-URLs,
- weiche Warnungen für referenzierte Repository-Pfade,
- Präsenz wichtiger projektbezogener Einstiegspunkte wie
  `src/arbeitszeit/presentation/admin_cli/main.py`,
  `src/arbeitszeit/presentation/terminal_ui/main.py`,
  `src/arbeitszeit/infrastructure/scripts/show_config.py`,
  `src/arbeitszeit/infrastructure/config_file.py`.

## Was das Skript bewusst nicht tut

Das Skript trifft keine fachlichen Wahrheitsaussagen über Inhalte ganzer Kapitel.
Es ersetzt also keine kapitelweise inhaltliche Prüfung gegen die Codebasis.

Es tut bewusst auch Folgendes nicht:

- keine Auswertung von `docs/archive/` für aktuelle Qualitätsaussagen,
- keine automatische Übernahme historischer Versionen,
- keine automatische Erhöhung von Versionsnummern,
- keine freie Interpretation unklarer Dokumentaussagen,
- keine Vollprüfung der semantischen Korrektheit ganzer Kapitel.

## Rolle von Claude Code

Claude Code sollte in diesem Projekt als kontrolliertes Hilfsmittel verwendet werden,
nicht als autonomer Autor kompletter Handbücher ohne Prüfschritt.

Sinnvolle Aufgaben sind:

- beleggestützte Prüfberichte erstellen,
- einzelne Kapitel überarbeiten,
- Formulierungen vorsichtiger und präziser machen,
- Commit-Texte formulieren,
- gezielte Diff- oder Metadatenprüfungen unterstützen.

Nicht sinnvoll ist:

- große ungezielte Neufassungen ohne Repository-Abgleich,
- Aussagen über aktuelle Funktionalität nur aus Archivdokumenten,
- Vermischung von aktueller Doku und historischem Archivbestand.

## GitHub Actions

Eine passende Workflow-Datei führt nach Push oder Pull Request dieselbe lokale
Prüflogik erneut in GitHub aus. GitHub ist hier aber nur zweite Verteidigungslinie.
Die primäre Qualitätssicherung soll lokal auf dem Entwicklungsrechner stattfinden.
