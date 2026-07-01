# arbeitszeit

Lokales Zeiterfassungssystem für eine Zahnarztpraxis mit Python, SQLite, Terminal-Oberfläche und angebundener HID-Hardware für Buchungen.

## Kurzüberblick

- `arbeitszeit` ist ein lokal betriebenes Zeiterfassungssystem als Python-Paket im `src`-Layout.
- Das Repository richtet sich an Betreiber und Mitentwickler eines Zeiterfassungssystems für eine kleine Praxisumgebung.
- Technisch prägend sind eine getrennte Schichtenstruktur (`domain`, `application`, `infrastructure`, `presentation`), SQLite-Migrationen, CLI-/Terminal-Einstiegspunkte sowie evdev-basierte Hardwareanbindung.
- Die vorhandenen Dokumente und Module beziehen sich auf Linux-Betrieb mit lokalen Dateien statt Cloud-Backend.
- Der Projektstand wirkt auf Nachvollziehbarkeit, Prüfbarkeit und klar getrennte Verantwortlichkeiten zwischen Fachlogik, Datenbank, Export, Backup und Hardware ausgelegt.

## Zweck und Einsatzbereich

Das Projekt dient der lokalen Arbeitszeiterfassung in einer Zahnarztpraxis. Aus Paketbeschreibung, Dokumentation und Modulstruktur geht hervor, dass Buchungen, Korrekturen, Nachträge, Berichte, Backups und Systemprüfungen in einem lokal betriebenen System zusammengeführt werden sollen.

Die Struktur des Repositories legt einen Betrieb auf Linux-Systemen mit SQLite-Datenbank und angebundenen Eingabegeräten nahe. Die Umsetzung ist dabei nicht als Cloud-Anwendung organisiert, sondern als lokal auszuführendes Python-Projekt mit Skripten, Migrationen und getrennten Oberflächen für Terminalbetrieb und Administration.

## Systemumfang

| Bereich | Beschreibung | Status |
|---|---|---|
| Terminalbetrieb | Terminal-Einstiegspunkt für den operativen Buchungsbetrieb mit Endlosschleife, Systemcheck und Hardware-Lesern über `src/arbeitszeit/presentation/terminal_ui/main.py`. | vorhanden |
| Admin-CLI | Separate Admin-Oberfläche mit Modulen für Buchungen, Mitarbeitende, Berichte, Dienstplan, System und Benutzerkonten unter `src/arbeitszeit/presentation/admin_cli/`. | vorhanden |
| Fachlogik | Fachobjekte, Fehler, Enums, Audit-Ereignisse und Domänen-Services unter `src/arbeitszeit/domain/`. | vorhanden |
| Use-Cases | Anwendungsfälle für Buchen, Korrigieren, Nachträge, Genehmigen/Ablehnen von Ergänzungen sowie Mitarbeiter-, Karten- und Benutzerkontenverwaltung unter `src/arbeitszeit/application/use_cases/`. | vorhanden |
| Datenbank | SQLite-Anbindung, Repository-Schicht, Unit-of-Work und SQL-Migrationen unter `src/arbeitszeit/infrastructure/db/` und `migrations/`. | vorhanden |
| Hardware | evdev-basierter Reader für Numpad und RFID-Reader sowie Simulator unter `src/arbeitszeit/infrastructure/hardware/`. | vorhanden |
| Exporte | CSV-Export, PDF-Berichtserzeugung und Report-Abfragen unter `src/arbeitszeit/infrastructure/export/`. | vorhanden |
| Backups | Backup-Service im Paket und separates Skript `scripts/backup.py`. | vorhanden |
| Admin-GUI | Grafische Verwaltungsoberfläche (tkinter/ttk) unter `src/arbeitszeit/presentation/admin_gui/main.py` — alle Tabs für Mitarbeiter, Karten, Benutzer, Regelzeiten und System mit Tooltips, Bestätigungsdialogen und Hilfe-Menü. | vorhanden |
| NAS-Backup | rsync-basierter NAS-Sync in `src/arbeitszeit/infrastructure/backup/backup_service.py`; Fehlschlag endet mit Exit 1, lokales Backup bleibt erhalten. | vorhanden |
| Rechtliche Vollständigkeit im Produktivbetrieb | Das Zielbild wird in den Fach- und Projektdokumenten beschrieben, ist als Gesamteigenschaft des aktuellen Repostands aber nicht vollständig allein aus Codepfaden belegbar. | nicht eindeutig belegbar |

## Technik und Rahmenbedingungen

| Thema | Wert |
|---|---|
| Programmiersprache | Python |
| Python-Version | `>=3.14,<3.15` in `pyproject.toml`; zusätzlich liegt `.python-version` im Repository vor |
| Paketname | `arbeitszeit` |
| Paketversion | `0.1.0` |
| Datenbank | SQLite |
| Hardwarebezug | evdev, USB-HID-Eingabegeräte für Numpad und RFID-Reader |
| Betriebsart | lokal ausgeführtes Python-Projekt mit Dateien, Skripten und lokaler Datenbank |
| Externe Dienste | keine externen Dienste im `pyproject.toml` ausgewiesen |
| Kernabhängigkeiten | `evdev`, `reportlab` |
| Dev-Abhängigkeiten | `pytest`, `pytest-cov`, `pypdf`, `ruff` |

## Projektstruktur

| Pfad | Bedeutung |
|---|---|
| [`pyproject.toml`](pyproject.toml) | Paketdefinition, Abhängigkeiten und pytest-Konfiguration. |
| [`src/arbeitszeit/`](src/arbeitszeit) | Python-Paket im `src`-Layout. |
| [`src/arbeitszeit/domain/`](src/arbeitszeit/domain) | Fachmodell, Fehlerklassen, Enums, Audit-Ereignisse und Ports/Services. |
| [`src/arbeitszeit/application/`](src/arbeitszeit/application) | Befehle, Ergebnisse, Unit-of-Work-Abstraktion und Use-Cases. |
| [`src/arbeitszeit/infrastructure/db/`](src/arbeitszeit/infrastructure/db) | SQLite-Verbindung, Migrationen, Repositories und konkrete Unit-of-Work. |
| [`src/arbeitszeit/infrastructure/hardware/`](src/arbeitszeit/infrastructure/hardware) | Hardwarezugriff für evdev-Geräte, UID-Hashing und Simulator. |
| [`src/arbeitszeit/infrastructure/export/`](src/arbeitszeit/infrastructure/export) | CSV- und PDF-Export sowie Berichtabfragen. |
| [`src/arbeitszeit/infrastructure/backup/`](src/arbeitszeit/infrastructure/backup) | Backup-Logik im Anwendungspaket. |
| [`src/arbeitszeit/presentation/terminal_ui/`](src/arbeitszeit/presentation/terminal_ui) | Einstiegspunkt und Buchungsschleife für den Terminalbetrieb. |
| [`src/arbeitszeit/presentation/admin_cli/`](src/arbeitszeit/presentation/admin_cli) | Administrative CLI-Module für Pflege, Auswertung und Systemfunktionen. |
| [`src/arbeitszeit/presentation/admin_gui/`](src/arbeitszeit/presentation/admin_gui) | Grafische Verwaltungsoberfläche (tkinter/ttk) — Alternative zur Admin-CLI ohne Kommandozeilenkenntnisse. |
| [`scripts/`](scripts) | Hilfsskripte für Setup, Datenbankinitialisierung und Backup. |
| [`migrations/`](migrations) | SQL-Migrationsdateien zur Schema- und Dateninitialisierung. |
| [`tests/`](tests) | Teststruktur für Domain, Application, Integration, End-to-End und Migrationen. |
| [`docs/`](docs) | Zusätzliche Dokumentation im Repository. |
| [`docs/module/`](docs/module) | Kapitel-Quelldateien des Handbuchs (`handbuch_overview.md`, `handbuch_installation.md`, `handbuch_presentation.md`, `handbuch_application_layer.md`, `handbuch_domain.md`, `handbuch_infrastructure.md`, `handbuch_audit.md`), aus denen `handbuch_arbeitszeit.md` zusammengeführt wird. |

Wichtige Einstiegspunkte sind insbesondere [`src/arbeitszeit/presentation/terminal_ui/main.py`](src/arbeitszeit/presentation/terminal_ui/main.py), [`src/arbeitszeit/presentation/admin_cli/main.py`](src/arbeitszeit/presentation/admin_cli/main.py), [`src/arbeitszeit/presentation/admin_gui/main.py`](src/arbeitszeit/presentation/admin_gui/main.py), [`scripts/init_db.py`](scripts/init_db.py) und [`scripts/setup.py`](scripts/setup.py).

## Installation und lokales Setup

Für die Inbetriebnahme existiert mit der Datei [`installationsanleitung_arbeitszeit.md`](installationsanleitung_arbeitszeit.md) bereits eine eigene Installationsdokumentation. Für den README-Einstieg reichen die Grundschritte unten.

1. Repository klonen.
2. In das Projektverzeichnis wechseln.
3. Virtuelle Umgebung erstellen und aktivieren.
4. Abhängigkeiten installieren.
5. Datenbank initialisieren bzw. Setup ausführen.

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python scripts/init_db.py
```

Ob zusätzlich `scripts/setup.py` oder weitere Installationsschritte nötig sind, sollte vor einem Produktiveinsatz mit der separaten Installationsanleitung abgeglichen werden.

## Starten und Testen

### Starten

| Zweck | Befehl | Bedeutung |
|---|---|---|
| Terminalbetrieb starten | `python -m arbeitszeit.presentation.terminal_ui.main --db <pfad> --numpad <event-pfad> --rfid <event-pfad> --terminal-id <id>` | Startet die Endlosschleife für operative Buchungen mit Datenbank, Numpad, RFID-Reader und Terminal-ID. |
| Admin-GUI starten | `python -m arbeitszeit.presentation.admin_gui.main [--db <pfad>] [--user-id <id>]` | Öffnet die grafische Verwaltungsoberfläche (tkinter). Ohne Argumente erscheint ein Verbindungsdialog. |
| Admin-CLI starten | `python -m arbeitszeit.presentation.admin_cli.main --db <pfad>` | Startet die administrative Kommandozeilenoberfläche mit Datenbankpfad. |
| Datenbank initialisieren | `python scripts/init_db.py` | Führt die vorgesehene Initialisierung der lokalen Datenbank aus. |
| Setup ausführen | `python scripts/setup.py` | Führt projektbezogene Setup-Schritte aus, soweit im Skript implementiert. |
| Backup anstoßen | `python scripts/backup.py` | Startet den Backup-Ablauf über das bereitgestellte Hilfsskript. |

### Testen

| Zweck | Befehl | Bedeutung |
|---|---|---|
| Gesamte Testsuite | `pytest` | Führt die in `pyproject.toml` auf `tests` konfigurierte Testsuite aus. |
| Testabdeckung mit Coverage | `pytest --cov=arbeitszeit` | Nutzt die im Projekt vorgesehenen Dev-Abhängigkeiten für Coverage-Auswertung. |
| Nur Migrationstests | `pytest tests/test_migrations.py` | Prüft die Migrationen gezielt über die vorhandene Testdatei. |

## Wichtige Skripte und Einstiegspunkte

| Datei/Modul | Zweck | Wann relevant |
|---|---|---|
| [`scripts/init_db.py`](scripts/init_db.py) | Initialisiert die Datenbank bzw. stößt den Migrationspfad für ein neues System an. | Beim ersten lokalen Setup oder bei Neuaufbau einer Instanz. |
| [`scripts/setup.py`](scripts/setup.py) | Bündelt Setup-Aufgaben außerhalb des eigentlichen Paketstarts. | Beim vorbereitenden Einrichten eines Systems. |
| [`scripts/backup.py`](scripts/backup.py) | Startet den Backup-Ablauf per Hilfsskript. | Für manuelle oder geplante Sicherungen. |
| [`src/arbeitszeit/presentation/terminal_ui/main.py`](src/arbeitszeit/presentation/terminal_ui/main.py) | Einstiegspunkt des operativen Terminalbetriebs. | Für den laufenden Buchungsbetrieb mit Hardware. |
| [`src/arbeitszeit/presentation/admin_cli/main.py`](src/arbeitszeit/presentation/admin_cli/main.py) | Einstiegspunkt der administrativen CLI. | Für Pflege, Auswertung und Systemverwaltung über Kommandozeile. |
| [`src/arbeitszeit/presentation/admin_gui/main.py`](src/arbeitszeit/presentation/admin_gui/main.py) | Einstiegspunkt der grafischen Verwaltungsoberfläche (tkinter/ttk). | Für Administration ohne Kommandozeilenkenntnisse. |
| [`scripts/verify_hardware.py`](scripts/verify_hardware.py) | Interaktiver Hardware-Smoke-Test; gibt SHA-256-Hash einer gescannten RFID-Karte aus. | Bei Inbetriebnahme und Kartenzuweisung. |
| [`src/arbeitszeit/infrastructure/system_check.py`](src/arbeitszeit/infrastructure/system_check.py) | Prüft sechs systemnahe Bereiche (DB, Config, NAS, FK, NTP, Geräte). | Bei Inbetriebnahme, Diagnose und Fehlersuche. |
| [`src/arbeitszeit/infrastructure/time_monitor.py`](src/arbeitszeit/infrastructure/time_monitor.py) | Überwacht die Systemzeit und greift in den Buchungsablauf ein. | Wenn Zeitabweichungen oder Plausibilitätsprüfungen relevant sind. |

## Hardwarebezug

Die Hardware-Anbindung ist im Repository konkret über `evdev` umgesetzt. Das Modul [`src/arbeitszeit/infrastructure/hardware/evdev_reader.py`](src/arbeitszeit/infrastructure/hardware/evdev_reader.py) beschreibt zwei Eingabegeräte: ein USB-Numpad zur Auswahl des Buchungstyps per Taste `1` bis `4` sowie einen RFID-Reader, der seine UID als HID-Tastatureingabe mit Abschluss durch `Enter` liefert.

Aus dem Modul gehen außerdem Linux-Gerätedateien unter `/dev/input/event*`, notwendiger Lesezugriff auf die Gerätedateien und ein konfigurierbarer Timeout für den RFID-Lesevorgang hervor. Für Tests ist zusätzlich ein Simulator unter [`src/arbeitszeit/infrastructure/hardware/simulator.py`](src/arbeitszeit/infrastructure/hardware/simulator.py) vorhanden.

## Entwicklungshinweise

Die Paketstruktur zeigt eine bewusste Trennung zwischen Fachlogik, Anwendungsfällen, Infrastruktur und Präsentationsschicht. Neue Funktionen sollten sich an dieser Aufteilung orientieren und nicht direkt zwischen CLI, Hardware und Datenzugriff vermischen.

Für die lokale Entwicklung sind die Dev-Abhängigkeiten in `pyproject.toml` hinterlegt. Tests laufen über `pytest`, statische Prüfungen sind mit `ruff` vorgesehen, und die vorhandenen Testordner decken Unit-, Integrations-, End-to-End- und Migrationstests ab.

## Grenzen und offener Stand

Eindeutig belegt sind die Paketstruktur, die vorhandenen Einstiegspunkte, die SQLite-Migrationsbasis, die evdev-Hardwareanbindung, Export- und Backup-Bausteine sowie die Teststruktur. Ebenfalls klar sichtbar sind Module für Nachträge, Korrekturen, Berichte, Benutzerkonten, Systemprüfung und Zeitüberwachung.

Nicht jeder fachliche Zielanspruch aus den Projektdokumenten lässt sich bereits als vollständig nachgewiesene Gesamteigenschaft des aktuellen Repositorystands formulieren. Das betrifft insbesondere pauschale Aussagen zur vollständigen rechtlichen Absicherung im Produktiveinsatz, zu konkreten Betriebsprozessen in einer Praxisumgebung und zu NAS-spezifischen Backup-Abläufen, soweit diese nicht unmittelbar im Code oder in klar zuordenbaren Konfigurationsdateien implementiert sind.

## Betrieb & Rechtliches

Für den produktiven Betrieb in einer Praxisumgebung sind neben Code und Tests
insbesondere folgende Unterlagen relevant:

- **Datenschutz / DSGVO**
  - `docs/datenschutz/vvt_arbeitszeit_v1.md`
    Verzeichnis von Verarbeitungstätigkeiten nach Art. 30 DSGVO, inkl. Rechtsgrundlagen,
    TOM, Betroffenenrechte und DSFA-Einschätzung.

- **Betrieb allgemein**
  - `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`
    Betriebsdokumentation mit Systemübersicht, Rollen, Backup/Restore, Prüfkonzept und
    Grenzen des Repositorystands.
  - `docs/betrieb/betriebsfreigabe_protokoll.md`
    Vorlage für die formale Betriebsfreigabe / Systemabnahme (Tests, Mängel,
    Unterschriften, erneute Freigabe).

- **Rollen und Verantwortlichkeiten**
  - `docs/betrieb/rollenzuweisung.md`
    Organisatorische Rollenzuweisung (ADMIN / REVIEWER / TECH) inkl. Einweisungs- und
    Pflegeanleitung.

- **Hardware & Infrastruktur**
  - `docs/betrieb/hardware_inbetriebnahme_protokoll.md`
    Inbetriebnahme- und Smoke-Test-Protokoll für das Zielterminal mit RFID-Reader,
    USB-Numpad und (optional) NAS.

- **Backup & Wiederherstellung**
  - `docs/betrieb/backup_zeitplan_und_automatisierung.md`
    Backup-Zeitplan und Beispiele für Automatisierung (cron, systemd-timer) inkl.
    Verantwortlichkeiten und Aufbewahrungsstrategie.
  - `docs/betrieb/restore_checkliste.md`
    Operative Checkliste für Restore-Fälle (Freigabe, Durchführung, Prüfung,
    Nachdokumentation).

Diese Dokumente sind bewusst als Vorlagen gestaltet und müssen in der jeweiligen
Praxisumgebung ausgefüllt, freigegeben und außerhalb des Repositories revisionssicher
aufbewahrt werden.

## Weiterführende Dokumentation

- [`handbuch_arbeitszeit.md`](handbuch_arbeitszeit.md) / [`handbuch_arbeitszeit.html`](handbuch_arbeitszeit.html) – vollständiges Handbuch (konsolidiert aus `docs/module/`).
- [`befehlsreferenz_arbeitszeit.md`](befehlsreferenz_arbeitszeit.md) – Schnellreferenz aller Admin-CLI-Befehle, Terminal-UI und Hilfsskripte.
- [`installationsanleitung_arbeitszeit.md`](installationsanleitung_arbeitszeit.md) / [`installationsanleitung_arbeitszeit.html`](installationsanleitung_arbeitszeit.html) – Installationsanleitung für Laien.
- [`pflichtenheft_arbeitszeit_v5.md`](pflichtenheft_arbeitszeit_v5.md) – Pflichtenheft zum Projektkontext und Zielbild.
- [`regelwerk_arbeitszeit_v5.md`](regelwerk_arbeitszeit_v5.md) – Regelwerk mit fachlichem Rahmen.
- [`docs/module/`](docs/module) – Kapitel-Quelldateien, aus denen `handbuch_arbeitszeit.md` zusammengeführt wird.
- [`docs/`](docs) – weiterer Dokumentationsordner mit ergänzenden Unterlagen.
