# Installationsanleitung `arbeitszeit`

**Version:** 1.5
**Stand:** Juli 2026
**Zielgruppe:** Laien ohne Linux- oder Programmiererfahrung
**Projekt:** Lokales Zeiterfassungssystem für eine Zahnarztpraxis

## Umgesetzte Änderungen

Die Installationsanleitung wurde an den aktuellen Stand der Codebase angepasst. Dabei wurden insbesondere die aktuelle Rolle von `scripts/setup.py`, die Nutzung von `config.toml`, die verfügbaren CLI-Parameter sowie der empfohlene Start der Admin-CLI und der Terminal-UI korrigiert bzw. präzisiert. [cite:20][cite:21][cite:26][cite:29]

## Geänderter Abschnitt in finalem Markdown

## Für wen ist diese Anleitung?

Diese Anleitung richtet sich an Personen, die das System `arbeitszeit` auf
einem Rechner in der Praxis **installieren** sollen, aber keine oder nur
wenig Erfahrung mit Linux, der Kommandozeile oder Programmierung haben.
Jeder Schritt wird einzeln erklärt, inklusive dem, was der jeweilige Befehl
bewirkt und woran man erkennt, dass er erfolgreich war.

Wenn an einer Stelle etwas nicht funktioniert, ist das kein Grund zur Sorge:
Am Ende dieser Anleitung findest du einen Abschnitt mit den häufigsten
Fehlern und ihren Lösungen.

## Was du am Ende dieser Anleitung hast

Nach dem vollständigen Durchlaufen dieser Anleitung ist auf dem Rechner
ein lauffähiges Zeiterfassungssystem eingerichtet, mit dem Mitarbeitende
per RFID-Karte und Numpad ihre Arbeitszeiten buchen können, und mit dem
eine verantwortliche Person Mitarbeiterdaten, Karten, Berichte und
Sicherungen verwalten kann.

Außerdem ist eine lokale Konfigurationsdatei `config.toml` eingerichtet,
über die Datenbankpfad, Gerätezuordnung, Backup- und Exportverzeichnisse
sowie das Log-Verzeichnis zentral verwaltet werden. [cite:20][cite:21][cite:29]

## Was du vorher wissen solltest

### Was ist die Kommandozeile (Terminal)?

Die Kommandozeile (auch „Terminal" genannt) ist ein Fenster, in das man
Textbefehle eintippt, statt mit der Maus zu klicken. Das mag zunächst
ungewohnt wirken, ist aber bei diesem System notwendig, weil es bewusst
schlank und ohne grafische Oberfläche gebaut wurde. Jeder Befehl in dieser
Anleitung wird in einem grauen Kasten dargestellt und kann durch Markieren
und Kopieren übernommen werden.

Das Terminal öffnest du unter Linux Mint oder Lubuntu meist über die
Tastenkombination `Strg` + `Alt` + `T`, alternativ über das Anwendungsmenü
(Suche nach „Terminal").

### Was bedeutet `sudo`?

`sudo` steht für „Superuser do" und erlaubt es, einen Befehl mit
erweiterten Rechten auszuführen. Nach der Eingabe eines Befehls mit `sudo`
wirst du nach deinem Benutzerpasswort gefragt. Beim Tippen des Passworts
erscheinen aus Sicherheitsgründen keine Zeichen auf dem Bildschirm — das
ist normal.

### Zeilen mit `$` oder `#`

In manchen Anleitungen im Internet stehen vor Befehlen Zeichen wie `$`
oder `#`. Diese Zeichen gehören **nicht** zum Befehl und dürfen nicht
mitkopiert werden. In dieser Anleitung wurden solche Zeichen bewusst
weggelassen — du kannst jeden Befehl in den grauen Kästen exakt so
kopieren, wie er dort steht.

## Was du vorher benötigst

- Einen Rechner mit **Linux Mint** oder **Lubuntu**, bereits installiert
  und einsatzbereit.
- **LUKS-Festplattenverschlüsselung aktiviert** — zwingend erforderlich
  (Details und Prüfung: Schritt 0).
- Eine Internetverbindung (nur für die Installation selbst benötigt).
- Administratorrechte auf dem Rechner (also ein Benutzerkonto, mit dem
  `sudo`-Befehle funktionieren).
- Ausreichend Zeit — plane für die komplette Ersteinrichtung etwa
  30 bis 60 Minuten ein.
- Optional, aber für den Betrieb notwendig: ein RFID-Kartenlesegerät und
  ein USB-Numpad, beide über USB angeschlossen.

---

## Schritt 0: LUKS-Festplattenverschlüsselung sicherstellen

### Warum ist das zwingend?

`arbeitszeit` verarbeitet personenbezogene Daten von Mitarbeitenden.
Ohne Festplattenverschlüsselung wären diese Daten bei Diebstahl oder
Verlust des Rechners ungeschützt lesbar.

**LUKS (Linux Unified Key Setup)** ist der Standardmechanismus zur
Festplattenverschlüsselung unter Linux. Die Verschlüsselung muss
**vor** der Installation von `arbeitszeit` aktiv sein — eine
nachträgliche Einrichtung ist praktisch nur über eine Neuinstallation
sauber möglich.

### Prüfen, ob LUKS bereits aktiv ist

```bash
lsblk -o NAME,TYPE,FSTYPE
```

In der Ausgabe nach Einträgen vom Typ `crypt` suchen:

```text
NAME          TYPE  FSTYPE
sda           disk
└─sda1        part  crypto_LUKS
  └─dm-0      crypt ext4
```

Erscheint in der Spalte `TYPE` der Wert `crypt`, ist LUKS aktiv —
du kannst mit Schritt 1 fortfahren.

Erscheint **kein** Eintrag vom Typ `crypt`, ist die Festplatte
**nicht** verschlüsselt. Das System muss **neu installiert** werden,
bevor `arbeitszeit` eingerichtet werden darf.

### LUKS bei der Neuinstallation aktivieren

Beim Installieren von Linux Mint oder Lubuntu:

1. Im Installationsschritt „Installationsart" die Option
   **„Festplatte löschen und Linux Mint installieren"**
   (bzw. „… Lubuntu installieren") wählen.
2. Den Haken setzen bei
   **„Das neue System zur Sicherheit verschlüsseln"**.
3. Ein **starkes Verschlüsselungspasswort** festlegen und sicher
   verwahren. Dieses Passwort wird bei jedem Systemstart abgefragt.

> **Hinweis:** Das Verschlüsselungspasswort für LUKS ist
> **unabhängig** vom Benutzerpasswort des Betriebssystems.

---

## Schritt 1: System aktuell halten

Bevor irgendetwas installiert wird, sollte das Betriebssystem auf den
neuesten Stand gebracht werden:

```bash
sudo apt update
sudo apt upgrade -y
```

Der erste Befehl aktualisiert die Paketlisten. Der zweite Befehl
installiert alle verfügbaren Aktualisierungen.

## Schritt 2: Python installieren

Das System `arbeitszeit` benötigt **Python 3.14**. Das ist im Projekt
explizit festgelegt: `requires-python = ">=3.14,<3.15"`, und auch die
Datei `.python-version` enthält `3.14`. [cite:15][cite:16]

Prüfen, ob Python 3.14 bereits vorhanden ist:

```bash
python3.14 --version
```

Falls eine Ausgabe wie `Python 3.14.x` erscheint, ist dieser Schritt
bereits erledigt. Erscheint stattdessen eine Fehlermeldung wie
`command not found`, installiere Python 3.14 zusätzlich:

```bash
sudo apt update
sudo apt install -y python3.14 python3.14-venv python3-pip
```

Anschließend die Version erneut prüfen:

```bash
python3.14 --version
```

## Schritt 3: Zusätzliche Systempakete installieren

Einige Teile von `arbeitszeit` benötigen zusätzliche Pakete, insbesondere
für `evdev` und die Geräteprüfung:

```bash
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev evtest
```

Diese Pakete werden für das Bauen und Nutzen der Hardware-Anbindung sowie
für die Geräteidentifikation mit `evtest` benötigt. Das Python-Projekt
selbst deklariert `evdev` als feste Laufzeitabhängigkeit. [cite:15]

## Schritt 4: Programmcode herunterladen

Wechsle zunächst in ein Verzeichnis, in dem das Projekt abgelegt werden
soll, zum Beispiel dein Home-Verzeichnis:

```bash
cd ~
```

Falls `git` noch nicht installiert ist:

```bash
sudo apt install -y git
```

Lade nun den Programmcode herunter:

```bash
git clone https://github.com/iCodator/arbeitszeit.git
```

Danach in den Projektordner wechseln:

```bash
cd arbeitszeit
```

## Schritt 5: Virtuelle Umgebung einrichten

Virtuelle Umgebung anlegen:

```bash
python3.14 -m venv .venv
```

Virtuelle Umgebung aktivieren:

```bash
source .venv/bin/activate
```

Nach dem Aktivieren erscheint vor der Eingabeaufforderung im Terminal die
Kennzeichnung `(.venv)`.

## Schritt 6: Abhängigkeiten installieren

Jetzt werden die Python-Abhängigkeiten des Projekts installiert:

```bash
pip install -e .[dev]
```

Dieser Befehl liest `pyproject.toml` und installiert sowohl die
Projektabhängigkeiten als auch die im `dev`-Extra definierten Test- und
Entwicklungswerkzeuge. Dazu gehören unter anderem `evdev`, `reportlab`,
`pytest`, `pytest-cov`, `pypdf`, `ruff` und `import-linter`. [cite:15]

## Schritt 7: Datenbank anlegen

`arbeitszeit` verwendet eine lokale SQLite-Datenbank. Beim ersten Start
müssen die Migrationen ausgeführt werden:

```bash
python scripts/init_db.py
```

`init_db.py` legt dabei standardmäßig die Datei `arbeitszeit.db` an,
führt alle vorhandenen Migrationen aus und gibt jede erfolgreich
angewendete Migration einzeln aus. Im Repository sind aktuell die
Migrationen `0001` bis `0006` enthalten. [cite:18][cite:19]

Eine typische Ausgabe sieht so aus:

```text
Migration 0001 angewendet.
Migration 0002 angewendet.
Migration 0003 angewendet.
Migration 0004 angewendet.
Migration 0005 angewendet.
Migration 0006 angewendet.
⚠  Ersteinrichtung noch erforderlich:
   python scripts/setup.py --db arbeitszeit.db
```

Das `⚠`-Symbol bedeutet hier **keinen Fehler**, sondern den Hinweis,
dass danach noch die Konfiguration erstellt werden muss. Genau dieses
Verhalten ist im Script `scripts/init_db.py` implementiert. [cite:19]

## Schritt 8: Ersteinrichtung und `config.toml` erstellen

Dieser Schritt richtet **nicht** mehr nur einzelne Werte in der Datenbank
ein. Das aktuelle `scripts/setup.py` erstellt und pflegt die zentrale
Konfigurationsdatei `config.toml`. Das ist seit der im Changelog
beschriebenen Umstellung der offizielle Konfigurationsweg. [cite:20][cite:21]

Einfacher interaktiver Start:

```bash
python scripts/setup.py --db arbeitszeit.db
```

Dabei wird eine `config.toml` geschrieben. Der Schreibpfad wird automatisch
ermittelt: bevorzugt eine bereits vorhandene Konfigurationsdatei, sonst der
XDG-Standardpfad `~/.config/arbeitszeit/config.toml`. [cite:20][cite:21]

### Welche Werte werden eingerichtet?

`setup.py` unterstützt unter anderem diese Einstellungen: [cite:20]

- Datenbankpfad (`--db` beziehungsweise `database.path` in der Konfiguration).
- Terminal-ID (`--terminal-id`).
- Gerätename für das Numpad (`--numpad`).
- Gerätename für den RFID-Reader (`--rfid`).
- Benutzer-ID eines Administrators (`--admin-user-id`).
- Backup-Verzeichnis (`--backup-dir`).
- Exportverzeichnis (`--export-dir`).
- Log-Verzeichnis (`--log-dir`).

### Beispiel für einen nicht-interaktiven Aufruf

```bash
python scripts/setup.py \
  --db arbeitszeit.db \
  --terminal-id 1 \
  --numpad "USB Numpad" \
  --rfid "HID 1234:5678" \
  --admin-user-id 1 \
  --backup-dir /var/backups/arbeitszeit \
  --export-dir /var/exports/arbeitszeit \
  --log-dir /var/log/arbeitszeit
```

Wenn Werte bereits vorhanden sind, dient das Script auch zur späteren
Pflege der Konfiguration. Laut Changelog liest es frühere DB-Werte nur
noch als **Migrationshinweise**, schreibt aber selbst in die
`config.toml`. [cite:20][cite:21]

### Was zeigt das Script am Ende an?

Nach erfolgreicher Ausführung gibt `setup.py` Startbeispiele für die
Terminal-UI und die Admin-CLI aus, jeweils auf Basis von `--config`. [cite:20]

## Schritt 9: Zugriff auf RFID-Reader und Numpad einrichten

RFID-Reader und Numpad erscheinen unter Linux als Eingabegeräte. Um ihre
Gerätenamen zu ermitteln, führe aus:

```bash
sudo evtest
```

Beispielausgabe:

```text
/dev/input/event0:  Power Button
/dev/input/event3:  USB Numpad
/dev/input/event4:  HID 1234:5678
```

Wichtig ist vor allem der **Gerätename** nach dem Doppelpunkt, zum
Beispiel `USB Numpad` oder `HID 1234:5678`. Das Projekt unterstützt
inzwischen ausdrücklich stabile Gerätenamen als Eingabe für `--numpad`
und `--rfid`; zusätzlich werden weiterhin auch direkte Gerätepfade
akzeptiert. [cite:21][cite:29][cite:30]

Damit dein Benutzerkonto die Eingabegeräte lesen darf, zur Gruppe
`input` hinzufügen:

```bash
sudo usermod -aG input $USER
```

Danach einmal ab- und wieder anmelden oder den Rechner neu starten.

## Schritt 10: Erstes Administratorkonto anlegen

Bevor das System genutzt werden kann, muss ein erstes
Administrator-Benutzerkonto angelegt werden.

### Direkter Aufruf mit Datenbankpfad

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  users bootstrap \
  --username adminname
```

Der Bootstrap-Pfad ist im Code ausdrücklich als Sonderfall ohne
vorherige `--user-id` implementiert. [cite:26][cite:27]

### Alternativ über die Konfigurationsdatei

Wenn Schritt 8 bereits eine `config.toml` geschrieben hat und darin der
Datenbankpfad gesetzt ist, kann stattdessen auch mit `--config`
gearbeitet werden:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --config ~/.config/arbeitszeit/config.toml \
  users bootstrap \
  --username adminname
```

Bei Erfolg erscheint eine Ausgabe in dieser Form:

```text
Erstes Administratorkonto angelegt (ID 1).
Generiertes Passwort (einmalig sichtbar): <zufälliges Passwort>
```

Genau diese Meldungen werden in `user_accounts.py` ausgegeben. [cite:27]

## Schritt 11: Mitarbeitende und Karten anlegen

Nach dem Administrator-Konto können weitere Benutzer, Mitarbeitende und
RFID-Karten angelegt werden.

### Weiteres Benutzerkonto anlegen

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  users add \
  --username pruefer01 \
  --role REVIEWER
```

Die Rollen `ADMIN`, `REVIEWER` und `TECH` sind im Code als erlaubte
Werte für `users add` registriert. [cite:27]

### Mitarbeiter anlegen

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  employees add \
  --personnel-no M001 \
  --first-name Maria \
  --last-name Mustermann
```

Die Parameter `--personnel-no`, `--first-name` und `--last-name` sind im
Subcommand `employees add` genau so definiert. [cite:30]

### RFID-Karte direkt einlesen und zuweisen

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  cards assign \
  --employee-id 1 \
  --scan \
  --rfid "HID 1234:5678"
```

Der Code verlangt für diesen Weg genau die Kombination `--scan` und
`--rfid`. Danach erscheint die Meldung `Bitte Karte an den RFID-Reader
halten …`. [cite:30]

Bei erfolgreicher Zuordnung erscheint:

```text
Karte zugewiesen (ID 1).
```

### Alternative: UID-Hash getrennt ermitteln

Falls der direkte Scan im `cards assign`-Befehl nicht genutzt werden
soll, kann das Hardware-Testscript verwendet werden:

```bash
python scripts/verify_hardware.py \
  --numpad /dev/input/eventX \
  --rfid /dev/input/eventY
```

Danach kann der ermittelte UID-Hash mit `--uid-hash <HASH>` an
`cards assign` übergeben werden. Das Changelog dokumentiert für dieses
Script die Ausgabe des vollständigen SHA-256-Hashes. [cite:17][cite:21]

### Hinweis zur Nutzung von `--config`

Auch alle oben gezeigten Admin-CLI-Aufrufe können statt mit `--db` mit
`--config` arbeiten, sofern die Konfigurationsdatei bereits vollständig
vorliegt. Die Admin-CLI unterstützt `--config` offiziell, und der
Datenbankpfad kann daraus übernommen werden. [cite:21][cite:26]

## Schritt 12: Funktionstest durchführen

Zum Prüfen der Installation können die automatisierten Tests ausgeführt
werden:

```bash
pytest
```

Die Projektkonfiguration legt `tests` als Testverzeichnis fest. [cite:15]

Wenn nur gezielt ein Teil geprüft werden soll, können einzelne Testdateien
unter `tests/` ausgeführt werden. Der genaue Dateiname sollte dabei vorab
im Repository geprüft werden, da diese Anleitung nur belegte Pfade nennen
soll.

## Schritt 13: Terminal-Betrieb starten

Die Terminal-UI unterstützt heute zwei Wege: direkte Übergabe aller Werte
oder Start über die zentrale `config.toml`. Der Code priorisiert dabei
CLI-Werte vor Konfigurationswerten. [cite:29]

### Direkter Start mit allen Parametern

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db arbeitszeit.db \
  --numpad "USB Numpad" \
  --rfid "HID 1234:5678" \
  --terminal-id 1
```

### Empfohlener Start über `config.toml`

Wenn Schritt 8 bereits alle Werte geschrieben hat, genügt in der Regel:

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --config ~/.config/arbeitszeit/config.toml
```

Die Terminal-UI liest dann `database.path`, `terminal.numpad`,
`terminal.rfid` und `terminal.id` aus der Konfiguration. Genau dieses
Verhalten ist in `terminal_ui/main.py` implementiert und im Changelog
beschrieben. [cite:21][cite:29]

### Gerätenamen statt Gerätepfade

Für `--numpad` und `--rfid` sind stabile Gerätenamen ausdrücklich
vorgesehen. Vor dem Start werden diese Namen intern über
`resolve_evdev_device()` in konkrete Gerätepfade aufgelöst. [cite:29][cite:30]

### Wie wird der Betrieb beendet?

Mit `Strg` + `C` im Terminal. Die Terminal-UI behandelt `SIGINT` und
`SIGTERM` ausdrücklich kontrolliert. [cite:29]

## Häufige Probleme und Lösungen

| Problem | Mögliche Ursache | Lösung |
| --- | --- | --- |
| `command not found: python3.14` | Python 3.14 ist nicht installiert | Schritt 2 wiederholen. |
| `Permission denied` beim Start der Terminal-UI | Benutzerkonto ist nicht Mitglied der Gruppe `input` | Schritt 9 wiederholen, danach abmelden und neu anmelden. |
| Terminal-UI startet nicht: Gerät nicht gefunden | Gerätename ist falsch oder das Gerät ist nicht angeschlossen | Schritt 9 erneut ausführen und den Gerätenamen exakt übernehmen. [cite:29] |
| `ModuleNotFoundError` bei Programmstart | Abhängigkeiten wurden nicht installiert oder virtuelle Umgebung ist nicht aktiv | Schritt 5 und Schritt 6 erneut durchgehen. |
| `Fehler: DB-Pfad erforderlich` in der Admin-CLI | Weder `--db` noch eine passende `config.toml` ist vorhanden | `--db` angeben oder Schritt 8 korrekt abschließen. [cite:26] |
| `Fehler: --scan erfordert --rfid` | Beim Karten-Scan fehlt die Reader-Angabe | `cards assign` mit `--scan --rfid "<Gerätename>"` ausführen. [cite:30] |
| Terminal-UI meldet fehlende Konfiguration | `--config` wurde verwendet, aber `config.toml` enthält nicht alle Pflichtwerte | Schritt 8 erneut ausführen und fehlende Werte ergänzen. [cite:20][cite:29] |

## Kurzglossar für Einsteiger

- **Terminal / Kommandozeile:** Fenster zur Texteingabe von Befehlen.
- **`sudo`:** Ausführung eines Befehls mit Administratorrechten.
- **Repository:** Der komplette Programmcode-Ordner eines Projekts.
- **Virtuelle Umgebung:** Ein abgeschlossener Bereich für Python-Pakete.
- **Migration:** Ein automatisierter Schritt, der die Datenbankstruktur
  anlegt oder erweitert.
- **RFID:** Funktechnik zur kontaktlosen Identifikation.
- **Admin-CLI:** Textbasierte Verwaltungsoberfläche des Systems.
- **Terminal-UI:** Der laufende Buchungsprozess für den Praxisbetrieb.
- **`config.toml`:** Zentrale Konfigurationsdatei für Datenbank, Geräte,
  Verzeichnisse und weitere Laufzeitwerte. [cite:20][cite:21][cite:29]

## Wo finde ich weitere Informationen?

Weitere technische Dokumentation liegt im Repository unter `docs/` in den
entsprechenden Themenordnern. Diese Aussage ist direkt durch die
Verzeichnisstruktur des Repositorys belegt. [cite:11][cite:12][cite:14]

## Vorgenommene Änderungen mit Belegbasis

- Schritt 8 vollständig auf das aktuelle `config.toml`-Modell umgestellt; Grundlage sind `scripts/setup.py` und die zugehörigen Changelog-Einträge. [cite:20][cite:21]
- Die Parameter `--log-dir`, `--terminal-id`, `--numpad`, `--rfid` und `--admin-user-id` in der Ersteinrichtung ergänzt. [cite:20]
- Für Admin-CLI und Terminal-UI die inzwischen unterstützte Nutzung von `--config` ergänzt. [cite:21][cite:26][cite:29]
- Die gezeigten Befehle für `users bootstrap`, `users add`, `employees add` und `cards assign` gegen die tatsächlichen Subcommand-Definitionen geprüft und sprachlich präzisiert. [cite:27][cite:30]
- Den unpräzisen Verweis auf ein einzelnes `handbuch.md` entfernt und durch einen belegbaren Verweis auf `docs/` ersetzt. [cite:11][cite:12][cite:14]

## Offene Punkte, die weiterhin nicht verifizierbar sind

- Die genaue Ausgabeformatierung von `scripts/verify_hardware.py` wurde nicht vollständig aus dem Quellcode geprüft; belegt ist jedoch über das Changelog, dass der vollständige SHA-256-Hash ausgegeben wird. [cite:17][cite:21]
- Konkrete Einzeldateinamen innerhalb von `tests/` wurden in dieser Überarbeitung bewusst nicht behauptet, soweit sie nicht direkt verifiziert wurden. [cite:15]
