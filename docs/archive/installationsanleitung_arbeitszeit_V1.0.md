# Installationsanleitung für arbeitszeit - v1.0

Diese Anleitung erklärt Schritt für Schritt, wie das Zeiterfassungssystem **arbeitszeit** auf einem Linux-Rechner installiert wird. Das Ziel ist eine einfache Ersteinrichtung auch für Personen, die nicht täglich mit Python-Projekten arbeiten. Die Anwendung läuft vollständig lokal, speichert ihre Daten in einer SQLite-Datenbank und benötigt keinen Cloud-Dienst.

## Worum es bei arbeitszeit geht

`arbeitszeit` ist ein lokales Zeiterfassungssystem für eine Zahnarztpraxis. Mitarbeiter buchen Zeiten über ein physisches Terminal mit USB-Numpad und RFID-Leser; zusätzlich gibt es eine Admin-Konsole für Stammdaten, Berichte, Korrekturen, Nachträge, Backups und Systemprüfungen.

## Voraussetzungen

Vor der Installation sollte der Rechner folgende Grundvoraussetzungen erfüllen:

- Linux-System, zum Beispiel Linux Mint oder Lubuntu.
- Python 3.11, 3.12 oder 3.13.
- Git zum Herunterladen des Quellcodes.
- Für den späteren Echtbetrieb: ein USB-RFID-Leser und ein separates USB-Numpad.

### Zusätzliche Systempakete

Bevor die Python-Abhängigkeiten installiert werden, müssen auf dem System einige Entwicklungswerkzeuge vorhanden sein. Das ist wichtig, weil das Paket `evdev` nativen Code enthält und deshalb beim Installieren kompiliert werden muss.

Bitte installieren Sie **immer** diese drei Pakete bzw. Paketgruppen:

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

Dabei gilt:

- `build-essential` installiert unter anderem `gcc` und `make`, also die grundlegenden Werkzeuge zum Kompilieren von Programmen.
- `linux-headers-$(uname -r)` installiert die Header-Dateien für den aktuell laufenden Linux-Kernel, die bei hardwarenahen Python-Paketen benötigt werden können.
- `python3-dev` installiert die Python-Entwicklerdateien wie `Python.h`, die für Python-Erweiterungen mit C-Anteilen gebraucht werden.

Mit diesem Befehl können Sie prüfen, ob der Compiler vorhanden ist:

```bash
gcc --version
```

Wenn eine Versionsnummer angezeigt wird, ist der Compiler korrekt installiert.

## Projekt herunterladen

Laden Sie das Projekt aus GitHub herunter und wechseln Sie in das Projektverzeichnis:

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
```

`git clone` erstellt dabei eine lokale Kopie des gesamten Projekts auf Ihrem Rechner.

## Virtuelle Python-Umgebung anlegen

Für Python-Projekte ist es sinnvoll, eine sogenannte virtuelle Umgebung zu verwenden. Dadurch werden die benötigten Pakete nur für dieses Projekt installiert und nicht systemweit verteilt.

Erstellen und aktivieren Sie die virtuelle Umgebung so:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Wenn die Aktivierung erfolgreich war, erscheint meist `(.venv)` am Anfang der Terminalzeile.

## Python-Abhängigkeiten installieren

Installieren Sie nun das Projekt mit seinen Entwicklungswerkzeugen:

```bash
pip install -e ".[dev]"
```

Dieser Befehl installiert das Projekt im sogenannten „editable“-Modus. Änderungen am Quellcode werden dadurch direkt aus dem Projektordner verwendet. Zusätzlich werden die in `pyproject.toml` definierten Laufzeit- und Entwicklungsabhängigkeiten installiert, unter anderem `evdev`, `reportlab`, `pytest`, `pytest-cov`, `pypdf` und `ruff`.

## Datenbank initialisieren

Nach der Paketinstallation muss die lokale SQLite-Datenbank angelegt werden. Dafür ist im Projekt ein Skript vorgesehen:

```bash
python scripts/init_db.py --db arbeitszeit.db
```

Dieses Skript erstellt die Datenbankdatei `arbeitszeit.db` und führt die versionierten Migrationen aus. Dabei werden das Schema und die Standarddaten eingerichtet.

Wenn keine Fehler auftreten, ist die Datenbank anschließend einsatzbereit.

## Ersteinrichtung ausführen

Nach der Datenbankinitialisierung muss einmalig die betriebliche Grundkonfiguration gesetzt werden. Dazu gehören insbesondere Verzeichnisse für Backups und Exporte.

### Interaktive Einrichtung

Wenn Sie die Pfade beim Start eingeben möchten, verwenden Sie:

```bash
python scripts/setup.py --db arbeitszeit.db
```

Das Skript fragt dann die benötigten Pfade nacheinander ab und legt die Verzeichnisse bei Bedarf automatisch an.

### Nicht-interaktive Einrichtung

Wenn Sie die Pfade direkt angeben möchten, verwenden Sie zum Beispiel:

```bash
python scripts/setup.py --db arbeitszeit.db --backup-dir /data/backups/arbeitszeit --export-dir /data/exports/arbeitszeit
```

Das ist besonders praktisch, wenn die Installation dokumentiert oder mehrfach auf ähnlichen Systemen wiederholt werden soll.

## Anwendung starten

Das Projekt bietet zwei Hauptbetriebsarten: die Terminal-Oberfläche für die eigentliche Zeiterfassung und die Admin-CLI für Verwaltung und Auswertung.

### Terminal-UI starten

Für den Kiosk- bzw. Terminalbetrieb wird die Terminal-Oberfläche gestartet:

```bash
python -m arbeitszeit.presentation.terminal_ui.main --db arbeitszeit.db --numpad /dev/input/by-id/usb-numpad --rfid /dev/input/by-id/usb-rfid --terminal-id 1
```

Dabei müssen die Gerätepfade zu Ihrem tatsächlichen USB-Numpad und RFID-Leser passen. Die Terminal-Anwendung läuft als Schleife und beendet sich sauber bei `SIGTERM` oder `SIGINT`.

### Admin-CLI starten

Für Verwaltungsaufgaben wird die Admin-CLI verwendet:

```bash
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1
```

Über diese Oberfläche lassen sich unter anderem Mitarbeiter verwalten, RFID-Karten zuweisen, Korrekturen und Nachträge bearbeiten, Regelarbeitszeiten pflegen, Pflichtauswertungen abrufen, Exporte erzeugen, Backups anstoßen und ein Systemcheck durchführen.

## Wichtige Admin-Befehle

Die folgenden Befehlsgruppen sind laut Projektdokumentation vorgesehen:

| Bereich | Beispielbefehle | Zweck |
|---|---|---|
| `employees` | `list`, `add`, `deactivate`, `reactivate` | Mitarbeiter verwalten. |
| `cards` | `assign-card`, `replace-card` | RFID-Karten zuordnen oder ersetzen. |
| `bookings` | `supplement add`, `supplement approve`, `supplement reject`, `correct` | Nachträge und Korrekturen bearbeiten. |
| `schedule` | `show`, `set` | Regelarbeitszeiten anzeigen oder ändern. |
| `reports` | `open-bookings`, `warn-cases`, `corrections`, `supplements`, `open-review-cases`, `export-csv`, `export-pdf-daily`, `export-pdf-weekly`, `export-pdf-monthly` | Auswertungen und Exporte erzeugen. |
| `system` | `check`, `backup` | Systemprüfung und manuelles Backup. |

Viele Berichte akzeptieren zusätzlich Zeitfilter über `--from` und `--to` im ISO-8601-Format.

## Backup manuell ausführen

Ein manuelles Backup kann mit folgendem Skript erstellt werden:

```bash
python scripts/backup.py --db arbeitszeit.db --backup-dir /var/backups/arbeitszeit
```

Optional kann zusätzlich ein Exportverzeichnis angegeben werden. Ein möglicher NAS-Sync wird über die Systemkonfiguration gesteuert und dient als Spiegelziel, nicht als eigenständiges Langzeitarchiv.

## Funktionstest nach der Installation

Nach der Installation empfiehlt sich ein kurzer Test. So lässt sich früh erkennen, ob Python-Pakete, Datenbank und Projektstruktur korrekt eingerichtet sind.

Sinnvolle Prüfschritte sind:

1. Virtuelle Umgebung aktivieren.
2. Testlauf starten:

```bash
python -m pytest
```

Im Projekt sind mehrere Testebenen vorgesehen: Domain-Tests, Application-Tests, Integrations-Tests und End-to-End-Tests.

## Typische Fehler und Lösungen

### Fehler: `x86_64-linux-gnu-gcc` nicht gefunden

Wenn bei `pip install -e ".[dev]"` eine Meldung wie `command 'x86_64-linux-gnu-gcc' failed: No such file or directory` erscheint, fehlt der C-Compiler. Installieren Sie in diesem Fall die Pflichtpakete aus dem Abschnitt „Zusätzliche Systempakete“.

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

Danach aktivieren Sie die virtuelle Umgebung erneut und starten die Installation noch einmal:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

### Fehler: `Python.h: No such file or directory`

Diese Meldung weist darauf hin, dass die Python-Entwicklerdateien fehlen. Auch dieser Fall wird durch die Installation von `python3-dev` behoben.

```bash
sudo apt install -y python3-dev
```

### Fehler: Datenbankdatei nicht gefunden

Wenn `scripts/setup.py` meldet, dass die Datenbank nicht gefunden wurde, wurde `scripts/init_db.py` noch nicht ausgeführt. Initialisieren Sie zuerst die Datenbank und wiederholen Sie danach die Einrichtung.

## Reihenfolge in Kurzform

Für eine Standardinstallation reicht meistens diese Reihenfolge:

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev

git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/init_db.py --db arbeitszeit.db
python scripts/setup.py --db arbeitszeit.db
```

Danach können je nach Bedarf entweder die Terminal-UI oder die Admin-CLI gestartet werden.
