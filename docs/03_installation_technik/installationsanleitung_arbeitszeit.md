# Installationsanleitung `arbeitszeit`

**Version:** 1.0
**Stand:** Juli 2026
**Zielgruppe:** Laien ohne Linux- oder Programmiererfahrung
**Projekt:** Lokales Zeiterfassungssystem für eine Zahnarztpraxis

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
eine verantwortliche Person (Administrator) Mitarbeiterdaten, Karten,
Berichte und Sicherungen verwalten kann.

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
erweiterten Rechten (wie ein Administrator unter Windows) auszuführen.
Nach der Eingabe eines Befehls mit `sudo` wirst du nach deinem
Benutzerpasswort gefragt. Beim Tippen des Passworts erscheinen aus
Sicherheitsgründen keine Zeichen auf dem Bildschirm — das ist normal.

### Zeilen mit `$` oder `#`

In manchen Anleitungen im Internet stehen vor Befehlen Zeichen wie `$`
oder `#`. Diese Zeichen gehören **nicht** zum Befehl und dürfen nicht
mitkopiert werden. In dieser Anleitung wurden solche Zeichen bewusst
weggelassen — du kannst jeden Befehl in den grauen Kästen exakt so
kopieren, wie er dort steht.

## Was du vorher benötigst

- Einen Rechner mit **Linux Mint** oder **Lubuntu**, bereits installiert
  und einsatzbereit
- **LUKS-Festplattenverschlüsselung aktiviert** — zwingend erforderlich
  (Details und Prüfung: Schritt 0)
- Eine Internetverbindung (nur für die Installation selbst benötigt)
- Administratorrechte auf dem Rechner (also ein Benutzerkonto, mit dem
  `sudo`-Befehle funktionieren)
- Ausreichend Zeit — plane für die komplette Ersteinrichtung etwa
  30 bis 60 Minuten ein
- Optional, aber für den Betrieb notwendig: ein RFID-Kartenlesegerät und
  ein USB-Numpad, beide über USB angeschlossen

---

## Schritt 0: LUKS-Festplattenverschlüsselung sicherstellen

### Warum ist das zwingend?

`arbeitszeit` verarbeitet personenbezogene Daten (Namen, Arbeitszeiten)
von Mitarbeitenden. Die **DSGVO (Art. 32)** und das
**BDSG** verpflichten zur Anwendung geeigneter technischer
Schutzmaßnahmen. Ohne Festplattenverschlüsselung sind diese Daten bei
Diebstahl oder Verlust des Rechners ungeschützt lesbar.

**LUKS (Linux Unified Key Setup)** ist der Standardmechanismus zur
Festplattenverschlüsselung unter Linux. Die Verschlüsselung muss
**vor** der Installation von `arbeitszeit` aktiv sein — eine
nachträgliche Einrichtung ist ohne Datenverlust nicht möglich.

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
bevor `arbeitszeit` eingerichtet werden darf (siehe nächster Abschnitt).

### LUKS bei der Neuinstallation aktivieren

Beim Installieren von Linux Mint oder Lubuntu:

1. Im Installationsschritt „Installationsart" die Option
   **„Festplatte löschen und Linux Mint installieren"**
   (bzw. „… Lubuntu installieren") wählen.
2. Den Haken setzen bei
   **„Das neue System zur Sicherheit verschlüsseln"**
   (bei Ubuntu/Lubuntu: „Encrypt the new … installation for security").
3. Ein **starkes Verschlüsselungspasswort** festlegen und sicher
   verwahren. Dieses Passwort wird bei jedem Systemstart abgefragt.
   Geht es verloren, sind alle Daten auf dem Rechner unwiederbringlich
   verloren.

> **Hinweis:** Das Verschlüsselungspasswort für LUKS ist
> **unabhängig** vom Benutzerpasswort des Betriebssystems. Beide
> müssen sicher und getrennt aufbewahrt werden.

---

## Schritt 1: System aktuell halten

Bevor irgendetwas installiert wird, sollte das Betriebssystem auf den
neuesten Stand gebracht werden. Öffne dazu das Terminal und gib ein:

```bash
sudo apt update
sudo apt upgrade -y
```

**Was passiert hier?** Der erste Befehl prüft, welche Softwarepakete
aktualisiert werden können. Der zweite Befehl installiert diese
Aktualisierungen tatsächlich. Das `-y` sorgt dafür, dass Rückfragen
automatisch mit „Ja" beantwortet werden, damit der Vorgang nicht
unterbrochen wird.

Dieser Schritt kann je nach Internetverbindung und Systemzustand einige
Minuten dauern. Warte, bis die Eingabeaufforderung wieder erscheint und
du erneut einen Befehl eintippen kannst.

## Schritt 2: Python installieren

Das System `arbeitszeit` benötigt eine ganz bestimmte Version der
Programmiersprache Python, nämlich **Python 3.14**. Viele
Linux-Installationen bringen eine ältere Version mit, deshalb muss
Python 3.14 gegebenenfalls zusätzlich installiert werden.

Prüfen, ob Python 3.14 bereits vorhanden ist:

```bash
python3.14 --version
```

Falls als Antwort etwas wie `Python 3.14.x` erscheint, ist dieser Schritt
bereits erledigt und du kannst zu Schritt 3 weitergehen. Erscheint
stattdessen eine Fehlermeldung wie `command not found` (Befehl nicht
gefunden), muss Python 3.14 noch installiert werden:

```bash
sudo apt update
sudo apt install -y python3.14 python3.14-venv python3.14-tk python3-pip
```

**Was passiert hier?** Es werden vier Programmteile installiert:
Python selbst, ein Werkzeug zum Anlegen isolierter „virtueller
Umgebungen" (dazu gleich mehr), das Grafik-Modul `tkinter` für die
grafische Verwaltungsoberfläche und der Python-Paketmanager `pip`, mit
dem später zusätzliche Software-Bausteine installiert werden.

Anschließend die Version erneut prüfen:

```bash
python3.14 --version
```

## Schritt 3: Zusätzliche Systempakete installieren

Einige Teile von `arbeitszeit` (insbesondere die Anbindung an den
RFID-Leser und das Numpad) benötigen zusätzliche Bausteine, die nicht in
Python selbst enthalten sind:

```bash
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

**Was passiert hier?** Dieser Befehl installiert Werkzeuge zum
Übersetzen von Programmcode (`build-essential`), Systemheader für den
laufenden Kernel (`linux-headers`) sowie Entwicklungsdateien für Python
(`python3-dev`).

## Schritt 4: Programmcode herunterladen

Wechsle zunächst in ein Verzeichnis, in dem das Projekt abgelegt werden
soll, zum Beispiel dein Home-Verzeichnis:

```bash
cd ~
```

Falls noch nicht vorhanden, wird zusätzlich das Versionsverwaltungsprogramm
`git` benötigt, mit dem der Programmcode heruntergeladen wird:

```bash
sudo apt install -y git
```

Lade nun den Programmcode herunter:

```bash
git clone https://github.com/iCodator/arbeitszeit.git
```

**Was passiert hier?** Der Befehl `git clone` lädt eine vollständige
Kopie des Projekts aus dem Internet auf deinen Rechner herunter. Danach
existiert bei dir ein neuer Ordner namens `arbeitszeit`.

Wechsle in diesen neuen Ordner:

```bash
cd arbeitszeit
```

Ab jetzt musst du dich in diesem Ordner befinden, damit die folgenden
Befehle funktionieren. Falls du das Terminal zwischendurch schließt,
musst du diesen `cd arbeitszeit`-Schritt (ggf. mit vollständigem Pfad,
z. B. `cd ~/arbeitszeit`) wiederholen.

## Schritt 5: Virtuelle Umgebung einrichten

Eine „virtuelle Umgebung" ist ein abgeschlossener Bereich, in dem
zusätzliche Python-Bausteine installiert werden, ohne das restliche
System zu verändern. Das schützt sowohl `arbeitszeit` als auch andere
Programme auf dem Rechner vor Konflikten.

Virtuelle Umgebung anlegen:

```bash
python3.14 -m venv .venv
```

Virtuelle Umgebung aktivieren:

```bash
source .venv/bin/activate
```

**Woran erkennst du den Erfolg?** Nach dem Aktivieren erscheint vor der
Eingabeaufforderung im Terminal die Kennzeichnung `(.venv)`. Das zeigt
dir, dass du dich jetzt „innerhalb" der virtuellen Umgebung befindest.

**Wichtiger Hinweis:** Diese Aktivierung gilt nur für das aktuell
geöffnete Terminal-Fenster. Öffnest du ein neues Fenster oder startest
den Rechner neu, musst du Schritt 5 (nur den Aktivierungsbefehl, nicht
das Anlegen) erneut ausführen, bevor du mit `arbeitszeit` arbeitest.

## Schritt 6: Abhängigkeiten installieren

Jetzt werden die zusätzlichen Software-Bausteine installiert, die
`arbeitszeit` zum Laufen benötigt (zum Beispiel für die
Hardware-Anbindung und die PDF-Erzeugung):

```bash
pip install -e .[dev]
```

**Was passiert hier?** `pip` liest die Datei `pyproject.toml` im
Projektordner und installiert alle dort aufgeführten Software-Bausteine
automatisch. Das kann je nach Rechner und Internetverbindung einige
Minuten dauern. Am Ende sollte eine Meldung erscheinen, die mit
`Successfully installed` beginnt.

## Schritt 7: Datenbank anlegen

`arbeitszeit` speichert alle Daten in einer lokalen Datenbankdatei
(keine Cloud, keine externen Server). Diese Datenbank muss beim
allerersten Start einmalig angelegt werden:

```bash
python scripts/init_db.py
```

**Was passiert hier?** Es wird eine neue Datei namens `arbeitszeit.db`
im aktuellen Ordner erzeugt und mit der benötigten Struktur (Tabellen)
gefüllt. Am Bildschirm siehst du eine Liste angewendeter Migrationen,
zum Beispiel:

```text
Migration 0001 angewendet.
Migration 0002 angewendet.
Migration 0003 angewendet.
Migration 0004 angewendet.
Migration 0005 angewendet.
Migration 0006 angewendet.
```

Am Ende erscheint zusätzlich ein Hinweis, dass eine Ersteinrichtung noch
erforderlich ist — das ist der nächste Schritt.

## Schritt 8: Ersteinrichtung durchführen

Nach dem Anlegen der Datenbank müssen noch grundlegende Einstellungen
festgelegt werden, etwa wo Berichte und Sicherungen abgelegt werden
sollen:

```bash
python scripts/setup.py --db arbeitszeit.db
```

**Was passiert hier?** Das Programm fragt dich nach dem
Backup-Verzeichnis und dem Exportverzeichnis für Berichte. Gib jeweils
einen absoluten Pfad ein (z. B. `/var/backups/arbeitszeit`) und bestätige
mit `Enter`. Eine leere Eingabe wird nicht akzeptiert — das Programm
wiederholt die Frage, bis du einen Pfad angegeben hast.

Willst du diese Angaben lieber direkt beim Aufruf festlegen, statt
Fragen zu beantworten, geht das auch so:

```bash
python scripts/setup.py \
  --db arbeitszeit.db \
  --backup-dir /var/backups/arbeitszeit \
  --export-dir /var/exports/arbeitszeit
```

Dieser Schritt kann bei Bedarf mehrfach ausgeführt werden — bereits
festgelegte Einstellungen werden dabei nicht doppelt abgefragt.

## Schritt 9: Zugriff auf RFID-Reader und Numpad einrichten

RFID-Reader und Numpad sind unter Linux normale USB-Eingabegeräte. Damit
`arbeitszeit` diese Geräte auslesen darf, benötigt das Programm
Leserechte auf die entsprechenden Gerätedateien im Ordner
`/dev/input/`.

Prüfe zunächst, welche Geräte angeschlossen sind:

```bash
ls -l /dev/input/event*
```

**Was siehst du hier?** Eine Liste von Gerätedateien mit Namen wie
`event0`, `event1` und so weiter. Welche davon zu RFID-Reader und
Numpad gehören, lässt sich am einfachsten mit folgendem Befehl
herausfinden:

```bash
cat /proc/bus/input/devices
```

Diese Ausgabe zeigt zu jedem angeschlossenen Gerät einen Namen (z. B.
„HID Keyboard" für den RFID-Leser, der sich wie eine Tastatur verhält)
sowie den zugehörigen Gerätepfad unter `Handlers`.

Damit dein Benutzerkonto diese Geräte lesen darf, muss es zur Gruppe
`input` hinzugefügt werden:

```bash
sudo usermod -aG input $USER
```

**Wichtig:** Nach diesem Befehl musst du dich einmal ab- und wieder
anmelden (oder den Rechner neu starten), damit die Gruppenmitgliedschaft
wirksam wird. Ohne diesen Neustart der Sitzung funktioniert der
Hardwarezugriff nicht, auch wenn der Befehl selbst keine Fehlermeldung
zeigt.

## Schritt 10: Ersten Administrator anlegen

Bevor das System genutzt werden kann, muss ein erstes
Administrator-Benutzerkonto angelegt werden. Dieses Konto darf später
alle Verwaltungsaufgaben durchführen.

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  users bootstrap \
  --username adminname
```

Ersetze `adminname` durch einen Benutzernamen deiner Wahl (zum Beispiel
den Namen der Praxisleitung). Wird kein Passwort mit angegeben, erzeugt
das System automatisch ein sicheres Passwort und zeigt es **einmalig**
im Terminal an.

**Sehr wichtig:** Notiere dieses angezeigte Passwort sofort an einem
sicheren Ort (zum Beispiel in einem Passwort-Manager oder einem
verschlossenen Umschlag). Es wird aus Sicherheitsgründen nirgends
gespeichert und kann später nicht erneut angezeigt werden.

## Schritt 11: Mitarbeitende und Karten anlegen

Nachdem das Administrator-Konto existiert, können weitere Konten,
Mitarbeitende und RFID-Karten eingerichtet werden. Die Zahl `1` in den
folgenden Befehlen steht für die Benutzer-ID des gerade angelegten
Administrators (bei der ersten Einrichtung normalerweise `1`).

Weiteres Benutzerkonto anlegen (zum Beispiel für die Berichtsprüfung):

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  users add \
  --username pruefer01 \
  --role REVIEWER
```

Mitarbeiter anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  employees add \
  --personnel-no M001 \
  --first-name Maria \
  --last-name Mustermann
```

Ersetze `M001`, `Maria` und `Mustermann` durch die tatsächliche
Personalnummer und den Namen der jeweiligen Person. Dieser Befehl muss
für jede Mitarbeiterin und jeden Mitarbeiter einzeln wiederholt werden.

RFID-Karte einer Mitarbeiterin bzw. einem Mitarbeiter zuweisen:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  cards assign \
  --employee-id 1 \
  --uid-hash <HASH>
```

Den benötigten `<HASH>`-Wert für eine bestimmte Karte ermittelst du mit
dem Hardware-Testscript. Stelle sicher, dass die virtuelle Umgebung aktiv
ist (`(.venv)` im Prompt), und führe aus:

```bash
python scripts/verify_hardware.py \
  --numpad /dev/input/eventX \
  --rfid /dev/input/eventY
```

(`eventX` und `eventY` durch die in Schritt 9 ermittelten Gerätepfade
ersetzen. **Beide Argumente sind Pflicht** — das Script bricht ab, wenn
nur eines angegeben wird.)

Das Script durchläuft drei Stufen:

1. Gerätezugriff prüfen
2. Numpad-Test: Drücke eine der Tasten 1–4 auf dem Numpad.
3. RFID-Test: Halte die Karte an den RFID-Leser.

Nach dem Karten-Scan zeigt das Script unter anderem:

```text
SHA-256-Hash:    abc123def456…  (wie in DB gespeichert)
```

Kopiere diesen Hash-Wert und setze ihn als `<HASH>` im obigen
`cards assign`-Befehl ein.

## Schritt 12: Funktionstest durchführen

Um sicherzugehen, dass die Installation vollständig und korrekt
abgeschlossen ist, kannst du die automatisierten Tests des Projekts
ausführen:

```bash
pytest
```

**Woran erkennst du Erfolg?** Am Ende der Ausgabe steht eine
Zusammenfassung wie `X passed` (grün dargestellt). Steht dort
stattdessen `failed` (rot), ist etwas bei der Installation
schiefgelaufen — wende dich in diesem Fall an die im Abschnitt
„Häufige Probleme" beschriebenen Lösungen oder an die technisch
verantwortliche Person.

Gezielt nur die Datenbank-Migrationen testen:

```bash
pytest tests/test_migrations.py
```

## Schritt 13: Terminal-Betrieb starten

Für den täglichen Buchungsbetrieb wird ein eigener Prozess gestartet,
der dauerhaft im Hintergrund läuft und auf Numpad- und
RFID-Eingaben wartet:

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db arbeitszeit.db \
  --numpad /dev/input/eventX \
  --rfid /dev/input/eventY \
  --terminal-id 1
```

Ersetze `eventX` und `eventY` durch die in Schritt 9 ermittelten
tatsächlichen Gerätepfade für Numpad und RFID-Reader.

**Wie beende ich den Terminal-Betrieb?** Mit der Tastenkombination
`Strg` + `C` im entsprechenden Terminal-Fenster. Das Programm beendet
sich dabei sauber, ohne Daten zu verlieren.

Für den echten Praxisbetrieb sollte dieser Befehl automatisch beim
Systemstart ausgeführt werden (zum Beispiel über einen systemd-Dienst).
Die Einrichtung eines solchen automatischen Starts ist nicht Teil dieser
Installationsanleitung und sollte gemeinsam mit der technisch
verantwortlichen Person erfolgen.

## Schritt 14: Grafische Verwaltungsoberfläche (Admin-GUI) starten

Neben der Admin-CLI steht eine **grafische Verwaltungsoberfläche** zur
Verfügung. Sie zeigt dieselben Funktionen in Fensterform und eignet sich
besonders für Personen, die lieber mit der Maus als mit Textbefehlen
arbeiten.

### Voraussetzung prüfen

Das Grafik-Modul `python3.14-tk` wurde bereits in Schritt 2 installiert.
Prüfe, ob es verfügbar ist:

```bash
python3.14 -c "import tkinter; print('tkinter OK')"
```

Erscheint `tkinter OK`, kann die GUI gestartet werden. Erscheint
stattdessen eine Fehlermeldung, lies bitte den Abschnitt „Häufige
Probleme" am Ende dieser Anleitung.

### GUI starten

Stelle sicher, dass die virtuelle Umgebung aktiv ist (`(.venv)` im
Prompt), und führe aus:

```bash
python -m arbeitszeit.presentation.admin_gui.main
```

Es öffnet sich ein Fenster mit einem Verbindungsdialog. Trage dort den
Datenbankpfad und deine Benutzer-ID ein und klicke auf **Verbinden**.

Alternativ kannst du beide Angaben direkt beim Aufruf übergeben:

```bash
python -m arbeitszeit.presentation.admin_gui.main \
  --db arbeitszeit.db \
  --user-id 1
```

### Bedienung

Die GUI ist in fünf Reiter (Tabs) unterteilt:

| Reiter | Funktion |
| --- | --- |
| 👥 Mitarbeiter | Mitarbeitende anlegen und deaktivieren |
| 💳 Karten | RFID-Karten zuweisen, ersetzen und deaktivieren |
| 👤 Benutzer | Benutzerkonten anlegen, deaktivieren, reaktivieren, Rolle ändern; Bootstrap für ersten Administrator |
| 📅 Regelzeiten | Aktive Regelarbeitszeiten anzeigen |
| ⚙ System | Systemcheck auslösen und Backup erstellen |

**Hilfstext zu jedem Element:** Bewege den Mauszeiger über eine
Schaltfläche oder ein Eingabefeld und halte ihn kurz still — es erscheint
automatisch ein ausführlicher Erklärungstext.

**Tastaturkürzel:** Drücke `F1` für die Kurzanleitung oder öffne das
Menü `Hilfe → Tastenkürzel` für eine vollständige Übersicht.

**Wie beende ich die GUI?** Schließe das Fenster wie jedes andere
Programm (roter Schließen-Knopf oder `Alt` + `F4`).

> **Hinweis:** Buchungskorrekturen, Nachträge und Berichte sind derzeit
> nur über die Admin-CLI verfügbar (siehe `befehlsreferenz_arbeitszeit.md`).
> Die GUI deckt die täglichen Verwaltungsaufgaben ab — für erweiterte
> Auswertungen nutze die CLI.

## Häufige Probleme und Lösungen

| Problem | Mögliche Ursache | Lösung |
| --- | --- | --- |
| `command not found: python3.14` | Python 3.14 ist nicht installiert | Schritt 2 wiederholen |
| `Permission denied` beim Start der Terminal-UI | Benutzerkonto ist nicht Mitglied der Gruppe `input` | Schritt 9 wiederholen, danach abmelden und neu anmelden |
| Virtuelle Umgebung zeigt kein `(.venv)` an | Aktivierungsbefehl aus Schritt 5 wurde nicht (erneut) ausgeführt | `source .venv/bin/activate` im Projektordner ausführen |
| `ModuleNotFoundError` bei Programmstart | Abhängigkeiten wurden nicht installiert oder virtuelle Umgebung ist nicht aktiv | Schritt 5 und Schritt 6 erneut durchgehen |
| Karte wird nicht erkannt | Karte ist noch keinem Mitarbeiter zugewiesen | Schritt 11 (Kartenzuweisung) durchführen |
| `pytest` zeigt `failed` an | Installation unvollständig oder fehlerhaft | Schritte 2 bis 6 erneut prüfen, bei Bedarf Hilfe holen |
| GUI startet nicht / `No module named '_tkinter'` | `python3.14-tk` ist nicht installiert | `sudo apt install python3.14-tk` ausführen, danach GUI erneut starten |
| GUI-Fenster öffnet sich, aber ist leer | Virtuelle Umgebung war beim GUI-Start nicht aktiv | `source .venv/bin/activate` ausführen, dann GUI neu starten |

## Kurzglossar für Einsteiger

- **Terminal / Kommandozeile:** Fenster zur Texteingabe von Befehlen,
  Alternative zur Maussteuerung.
- **`sudo`:** Ausführung eines Befehls mit Administratorrechten.
- **Repository:** Der komplette Programmcode-Ordner eines Projekts.
- **Virtuelle Umgebung:** Ein abgeschlossener Bereich für
  Python-Software, der das restliche System nicht beeinflusst.
- **Migration:** Ein automatisierter Schritt, der die Struktur der
  Datenbank anlegt oder erweitert.
- **RFID:** Funktechnik zur kontaktlosen Identifikation, hier über eine
  Mitarbeiterkarte.
- **Admin-CLI:** Die Verwaltungsoberfläche für Administratorinnen und
  Administratoren, bedienbar über Textbefehle.
- **Admin-GUI:** Die grafische Verwaltungsoberfläche — dieselben
  Funktionen wie die Admin-CLI, aber mit Fenstern, Schaltflächen und
  Hilfstexten statt Textbefehlen.
- **tkinter:** Das in Python eingebaute Grafik-Modul, das die Admin-GUI
  antreibt. Auf Linux wird es als separates Paket (`python3.14-tk`)
  bereitgestellt.
- **Terminal-UI:** Der dauerhaft laufende Prozess, über den
  Mitarbeitende ihre Arbeitszeiten buchen.

## Wo finde ich weitere Informationen?

Nach erfolgreicher Installation liefert das ausführliche
`handbuch_arbeitszeit.md` (bzw. dessen HTML-Version) eine vollständige
Beschreibung aller Bedienfunktionen, insbesondere der Admin-CLI-Befehle
für Mitarbeiterverwaltung, Berichte, Systemprüfung und Backups.
