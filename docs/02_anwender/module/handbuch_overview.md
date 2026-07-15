# Handbuch `arbeitszeit` – Übersicht

**Kapitel:** 1
**Version:** 1.1
**Stand:** Juli 2026
**Quelldatei:** `docs/02_anwender/module/handbuch_overview.md`

## Zweck

`arbeitszeit` ist ein lokal betriebenes Zeiterfassungssystem für eine
Zahnarztpraxis. Das Python-Paket ist im `src`-Layout organisiert und verwendet
laut Paketkonfiguration SQLite als Datenbank.

Aus dem Repository eindeutig belegt sind ein Terminalmodus für den operativen
Buchungsbetrieb, eine Admin-CLI für Verwaltungsaufgaben sowie zusätzliche
Hilfsskripte für Initialisierung, Konfiguration, Backup und Hardwareprüfung.

## Systemcharakteristik

Die Paketdefinition beschreibt `arbeitszeit` als lokales
Zeiterfassungssystem für eine Zahnarztpraxis. Als Laufzeitabhängigkeiten sind
`evdev` und `reportlab` eingetragen. Die unterstützte Python-Version ist in
`pyproject.toml` mit `>=3.14,<3.15` festgelegt.

Die Konfiguration erfolgt nicht ausschließlich über Kommandozeilenargumente.
Das Repository enthält zusätzlich eine zentrale Unterstützung für
`config.toml`, einschließlich Suchreihenfolge, Ladevorgang und Schreiblogik.
Eine Beispielkonfiguration liegt als `config.toml.example` vor.

## Projektstruktur

Aus dem Repository klar belegt ist folgende Hauptstruktur:

```text
arbeitszeit/
├── .claude/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── config.toml.example
├── docs/
│   ├── 01_normativ/
│   ├── 02_anwender/
│   ├── 03_installation_technik/
│   ├── 04_betrieb/
│   ├── 05_datenschutz_recht/
│   ├── 06_architektur/
│   ├── 07_pruefberichte/
│   ├── 08_planung_intern/
│   └── archive/
├── migrations/
├── pyproject.toml
├── run_audit.sh
├── scripts/
├── src/
│   └── arbeitszeit/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── presentation/
│           ├── admin_cli/
│           └── terminal_ui/
├── test_booking_loop.py
├── tests/
└── uv.lock
```

Die Verzeichnisstruktur unter `docs/` zeigt, dass die Projektdokumentation in
mehrere fachliche Bereiche gegliedert ist. Das Anwenderhandbuch liegt unter
`docs/02_anwender/`; die zugehörigen Kapiteldateien liegen unter
`docs/02_anwender/module/`.

## Schichtenmodell

In `pyproject.toml` ist eine Architekturprüfung mit `import-linter`
hinterlegt. Daraus geht hervor, dass das Projekt diese Schichten trennt:

- `arbeitszeit.presentation`
- `arbeitszeit.infrastructure`
- `arbeitszeit.application`
- `arbeitszeit.domain`

Diese Schichten sind auch als reale Paketstruktur unter `src/arbeitszeit/`
vorhanden. Innerhalb der Präsentationsschicht sind zwei getrennte Oberflächen
belegt: `presentation/terminal_ui` für den operativen Terminalbetrieb und
`presentation/admin_cli` für Verwaltungsfunktionen.

## Einstiegspunkte

Im Repository sind folgende Einstiegspunkte und Hilfsskripte belegt:

| Pfad | Aufgabe |
| --- | --- |
| `src/arbeitszeit/presentation/terminal_ui/main.py` | Einstiegspunkt für den operativen Buchungsbetrieb |
| `src/arbeitszeit/presentation/admin_cli/main.py` | Einstiegspunkt für die administrative Kommandozeile |
| `scripts/init_db.py` | Initialisierung der Datenbank |
| `scripts/setup.py` | Einrichtung und Pflege der `config.toml` |
| `scripts/show_config.py` | Anzeige von `config.toml` und `system_config`-Einträgen |
| `scripts/backup.py` | Auslösen des Backup-Ablaufs |
| `scripts/verify_hardware.py` | Prüfung der angeschlossenen Eingabegeräte |

Die Übersicht zeigt, dass das System nicht nur aus einem Laufzeitprogramm
besteht, sondern aus mehreren Werkzeugen für Betrieb, Diagnose und
Einrichtung. Diese Werkzeuge greifen auf dieselbe Paketbasis unter
`src/arbeitszeit/` zu.

## Konfiguration

Die Konfigurationsdatei wird zentral über
`src/arbeitszeit/infrastructure/config_file.py` unterstützt. Dort sind
Suchreihenfolge, Datentypen und die Struktur der Konfigurationsabschnitte
implementiert.

Belegt sind die Abschnitte `[database]`, `[terminal]`, `[backup]` und
`[admin]`. Die Beispielkonfiguration enthält unter anderem Pfadangaben für
Datenbank, Backup, Export und Logverzeichnis sowie Einstellungen für
Terminal-ID, Numpad und RFID-Reader.

## Technische Merkmale

Aus README, Paketdefinition und Modulstruktur sind folgende technische
Merkmale eindeutig ableitbar:

- lokale Ausführung als Python-Projekt ohne im Paket definierte Cloud-Dienste
- SQLite-basierte Datenhaltung
- evdev-basierte Hardwareanbindung für Eingabegeräte
- getrennte Oberflächen für Terminalbetrieb und Administration
- zusätzliche Infrastruktur für Export, Backup, Systemprüfung und
  Zeitüberwachung

Die eigentliche Hardware- und Betriebslogik ist nicht Bestandteil dieses
Übersichtskapitels, wird aber durch die vorhandenen Infrastruktur- und
Präsentationsmodule klar vorbereitet.
