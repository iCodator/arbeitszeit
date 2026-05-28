# Handbuch arbeitszeit

**arbeitszeit** ist ein lokales Zeiterfassungssystem für eine Zahnarztpraxis. Es erfasst Arbeitsbeginn, Arbeitsende und Pausen über ein Terminal mit USB-Numpad und RFID-Karte. Die Verwaltung erfolgt getrennt über eine Admin-CLI.[file:15][file:14]

Dieses Handbuch erklärt das System in einfacher Sprache. Es richtet sich an Praxisinhaber, Verwaltung, Prüfer und technisch verantwortliche Personen, nicht an Entwickler.[file:14][file:13]

## Zweck des Systems

Das System soll Arbeitszeiten **objektiv, verlässlich und nachvollziehbar** erfassen. Es speichert echte Buchungen, erkennt Auffälligkeiten und unterstützt die Praxis dabei, offene oder problematische Fälle zu prüfen und sauber zu dokumentieren.[file:14][file:13]

Nicht Teil des Systems sind Lohnabrechnung, Urlaubsplanung, Dienstplanung oder eine vollständige Personalverwaltung. Dafür ist das System bewusst nicht ausgelegt.[file:14]

## Grundprinzip

Der normale Ablauf ist einfach:

1. Buchungsart am Numpad wählen.
2. RFID-Chip an den Reader halten.
3. Das System prüft Karte, Mitarbeiter und Buchungsfolge.
4. Die Buchung wird gespeichert oder als auffällig markiert.[file:14][file:13]

Wichtig ist: Das System speichert reale Vorgänge. Fehlende oder unplausible Situationen werden nicht still „geradegebogen“, sondern als offen, auffällig oder prüfpflichtig gekennzeichnet.[file:13][file:9]

## Beteiligte Rollen

Im Projekt sind vier Rollen vorgesehen:[file:14][file:13]

- **Mitarbeiter** buchen ihre Zeiten.
- **Admin** verwaltet Benutzer, Karten, Regelarbeitszeiten und den Betrieb.
- **Prüfer** bewertet offene oder auffällige Fälle.
- **Technische Betreuung** ist für Systembetrieb, Backup und Restore zuständig.[file:14][file:13]

Diese Rechte sollen sauber getrennt sein. Ein normaler Mitarbeiter darf keine administrativen Änderungen an Benutzern, Karten, Regelzeiten oder Korrekturen durchführen.[file:14]

## Schrittweise Einrichtung

Die Einrichtung sollte immer in einer festen Reihenfolge erfolgen. So wird vermieden, dass später Buchungen an fehlenden Geräten, fehlenden Benutzerkonten oder nicht zugeordneten Karten scheitern.[file:14][file:13][file:15]

Empfohlene Reihenfolge:

1. Software installieren.
2. Datenbank initialisieren.
3. Lokale Pfade konfigurieren.
4. Geräte anschließen und prüfen.
5. Mitarbeiter anlegen.
6. Administrator anlegen.
7. Prüfer anlegen.
8. RFID-Karten zuweisen.
9. Regelarbeitszeiten prüfen.
10. Systemcheck durchführen.[file:15][file:14][file:9]

## Installation in Kurzform

Für die Installation sind Python, Linux und die benötigte Hardware erforderlich. Das Projekt wird lokal aus dem Git-Repository installiert.[file:15][file:14]

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Danach wird die Datenbank eingerichtet und die lokalen Pfade werden konfiguriert:[file:15]

```bash
python scripts/init_db.py --db arbeitszeit.db
python scripts/setup.py --db arbeitszeit.db
```

## Einrichtung der Geräte

Für den Terminal-Betrieb werden zwei USB-Geräte benötigt: ein RFID-Reader und ein separates numerisches USB-Numpad. Beide werden unter Linux über `evdev` angesprochen.[file:15][file:14][file:6]

### Schritt 1: Geräte anschließen

- RFID-Reader per USB anschließen.
- Numerisches USB-Numpad per USB anschließen.
- Den Terminal-Rechner neu erkennen lassen, falls nötig durch erneutes Einstecken oder Neustart.[file:14][file:15]

### Schritt 2: Gerätepfade konkret ermitteln

Für den Start der Terminal-Oberfläche werden zwei echte Linux-Gerätepfade benötigt: einer für das Numpad und einer für den RFID-Reader. Die Anwendung erwartet diese Pfade später als Werte für `--numpad` und `--rfid`.[file:15][file:6]

#### Variante A: Stabile Pfade unter `/dev/input/by-id/` verwenden

Diese Variante ist im Alltag am besten geeignet, weil die Pfade in der Regel stabiler sind als `event0`, `event1` oder `event2`.[file:15]

1. Beide Geräte per USB anschließen.[file:15]
2. Verfügbare Eingabegeräte anzeigen:

```bash
ls -l /dev/input/by-id/
```

3. In der Ausgabe nach zwei Einträgen suchen, die zu Numpad und RFID-Reader passen. Häufig enthalten die Namen Begriffe wie `kbd`, `keypad`, `Keyboard`, `Reader` oder den Herstellernamen.
4. Den vollständigen Pfad notieren, also zum Beispiel:

```text
/dev/input/by-id/usb-Logitech_USB_Keyboard-event-kbd
/dev/input/by-id/usb-ACS_ACR1281_1S_Dual_Reader-event-kbd
```

Wenn mehrere ähnliche Einträge sichtbar sind, sollte immer der Pfad mit `event-kbd` verwendet werden, weil die Terminal-Anwendung über `evdev` auf Eingabegeräte zugreift.[file:15][file:6]

#### Variante B: Gerät über Ein- und Ausstecken identifizieren

Wenn unklar ist, welcher Eintrag zu welchem Gerät gehört, hilft der Vergleich vor und nach dem Einstecken.

1. Vor dem Einstecken ausführen:

```bash
ls -l /dev/input/by-id/
```

2. Gerät einstecken, zum Beispiel nur das Numpad.
3. Den Befehl erneut ausführen.
4. Der neue Eintrag gehört zu diesem Gerät.
5. Dasselbe danach mit dem RFID-Reader wiederholen.

So lässt sich ohne Rätselraten sauber unterscheiden, welcher Pfad zum Numpad und welcher zum RFID-Gerät gehört.

#### Variante C: Technische Detailanzeige verwenden

Falls `/dev/input/by-id/` nicht ausreicht, kann zusätzlich die Geräteliste im Kernel geprüft werden:

```bash
cat /proc/bus/input/devices
```

Dort erscheinen Gerätename und zugehörige Event-Zuordnung. Das hilft besonders dann, wenn mehrere tastaturähnliche Geräte angeschlossen sind.

### Schritt 3: Gerätepfade im Startbefehl eintragen

Sobald beide Pfade bekannt sind, werden sie direkt im Startbefehl der Terminal-Oberfläche eingetragen. `--numpad` bekommt den Pfad des numerischen USB-Numpads, `--rfid` den Pfad des RFID-Readers.[file:15][file:6]

Beispiel mit echten Pfaden:

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
    --db arbeitszeit.db \
    --numpad /dev/input/by-id/usb-Logitech_USB_Keyboard-event-kbd \
    --rfid /dev/input/by-id/usb-ACS_ACR1281_1S_Dual_Reader-event-kbd \
    --terminal-id 1
```

Dabei gilt:

- Hinter `--numpad` steht immer der Pfad des Numpads.
- Hinter `--rfid` steht immer der Pfad des RFID-Readers.
- `--terminal-id` ist die interne Kennung des Terminals und nicht der Gerätepfad.[file:15][file:9]

Wenn der Startbefehl später dauerhaft verwendet werden soll, sollte genau dieser Befehl in eine Startdatei, ein Shell-Skript oder einen systemd-Service übernommen werden. Die Anwendung liest die Gerätepfade laut Startcode direkt aus den Parametern `--numpad` und `--rfid` ein.[file:6]

### Schritt 4: Funktion der Geräte prüfen

Nach dem Anschließen sollte ein Systemcheck ausgeführt werden. Der Systemcheck kann Konfiguration, Geräteverfügbarkeit, NAS-Erreichbarkeit, Datenbankzugriff und Grundkonsistenz prüfen.[file:14][file:9]

Wichtig ist außerdem die Bedienreihenfolge am Terminal: zuerst Buchungsart wählen, dann RFID-Chip scannen. Andere Reihenfolgen gelten nicht als Standardprozess.[file:14][file:13]

## Einrichtung der Mitarbeiter

Mitarbeiter sind die Personen, deren Arbeitszeiten erfasst werden. Ohne angelegte Mitarbeiter und zugewiesene RFID-Karten ist keine reguläre Buchung möglich.[file:14][file:13]

### Schritt 1: Mitarbeiterdaten festlegen

Vor dem Anlegen sollten mindestens diese Angaben vorliegen:[file:14][file:9]

- Personalnummer
- Vorname
- Nachname
- Aktiv-Status
- optional Beschäftigungsbeginn und Beschäftigungsende

### Schritt 2: Mitarbeiter anlegen

Die Admin-CLI enthält dafür die Befehlsgruppe `employees`. Laut README stehen mindestens `list`, `add`, `deactivate` und `reactivate` zur Verfügung.[file:15]

Praxisregel: Nur aktive Mitarbeiter sollten für die normale Zeiterfassung freigeschaltet sein. Inaktive Mitarbeiter oder beendete Beschäftigungsverhältnisse dürfen nicht unbemerkt weiter regulär buchen.[file:14][file:13]

### Schritt 3: RFID-Karte zuweisen

Nach dem Anlegen eines Mitarbeiters muss eine RFID-Karte zugeordnet werden. Dafür sind in der Admin-CLI laut README die Funktionen `assign-card` und `replace-card` vorgesehen.[file:15]

Nur aktive, bekannte Karten aktiver Benutzer erzeugen reguläre Buchungen. Unbekannte, inaktive oder ersetzte Karten werden protokolliert und nicht regulär verbucht.[file:14][file:13]

## Einrichtung des Administrators

Ein Administrator verwaltet Benutzer, Karten, Regelarbeitszeiten und Systembetrieb. Diese Rolle ist organisatorisch besonders wichtig, weil sie tief in das System eingreifen kann.[file:14][file:13]

### Schritt 1: Verantwortliche Person festlegen

Die Praxis sollte verbindlich festlegen, wer Admin ist. Diese Zuordnung gehört laut Pflichtenheft zu den organisatorischen Anforderungen.[file:14]

### Schritt 2: Benutzerkonto mit Admin-Rechten anlegen

Im Datenmodell sind Benutzerkonten getrennt von Mitarbeitern vorgesehen. Benutzerkonten werden in `user_accounts` geführt, Rollen sind dort technisch getrennt hinterlegt.[file:9][file:6]

Für die Bedienung der Admin-CLI wird eine Benutzer-ID benötigt. Laut README kann diese per `--user-id` oder über die Umgebungsvariable `ADMIN_USER_ID` übergeben werden.[file:15]

### Schritt 3: Admin nur gezielt verwenden

Admin-Rechte sollten nicht im Alltag für normale Buchungen genutzt werden. Sie sind für Verwaltung, Pflege, Korrekturen, Regelarbeitszeiten, Berichte, Systemcheck und Backup gedacht.[file:15][file:13][file:14]

## Einrichtung des Prüfers

Ein Prüfer bewertet offene oder auffällige Fälle. Diese Rolle ist wichtig, damit Warnungen und prüfpflichtige Fälle nicht nur angezeigt, sondern auch tatsächlich bearbeitet werden.[file:14][file:13]

### Schritt 1: Verantwortliche Person festlegen

Die Praxis sollte schriftlich festlegen, wer Prüfer ist und wie oft offene oder auffällige Fälle geprüft werden. Diese organisatorische Festlegung wird im Pflichtenheft ausdrücklich verlangt.[file:14][file:13]

### Schritt 2: Benutzerkonto mit Prüfer-Rechten anlegen

Die Rolle `REVIEWER` ist im System als eigene Benutzerrolle vorgesehen. Sie ist von `ADMIN`, `EMPLOYEE` und `TECH` getrennt.[file:9][file:6]

### Schritt 3: Prüffälle regelmäßig bearbeiten

Der Prüfer soll insbesondere offene Buchungen, Warnfälle, Korrekturen, Nachträge und offene Review-Cases auswerten. Dafür stehen in der Admin-CLI Berichte und Pflichtauswertungen zur Verfügung, zum Beispiel `open-bookings`, `warn-cases`, `corrections`, `supplements` und `open-review-cases`.[file:15][file:14][file:13]

## Regelarbeitszeiten prüfen

Das System verwaltet Regelarbeitszeiten pro Wochentag. Diese Zeiten dienen als Prüfrahmen, aber nicht als automatische Buchung.[file:14][file:13]

Aktuell sind folgende Standardzeiten vorgesehen:[file:14][file:13]

| Tag | Beginn | Ende |
|---|---:|---:|
| Montag | 07:30 | 18:00 |
| Dienstag | 07:30 | 18:00 |
| Mittwoch | 07:30 | 18:00 |
| Donnerstag | 07:30 | 14:00 |
| Freitag | 07:30 | 16:00 |

Diese Zeiten sollten vor dem Produktivstart geprüft werden. Änderungen dürfen nur durch berechtigte Personen erfolgen und müssen protokolliert werden.[file:13][file:14]

## Was Mitarbeiter buchen können

Das System kennt vier Buchungsarten:[file:14][file:13]

- `Kommen`
- `Gehen`
- `Pause Start`
- `Pause Ende`

Andere Eingaben sind im Standardbetrieb nicht vorgesehen. Die normale Reihenfolge ist immer: zuerst Buchungsart wählen, dann RFID-Chip scannen.[file:13][file:14]

## Typische Buchungssituationen

### Arbeitsbeginn

Ein Mitarbeiter wählt `Kommen` und hält danach den RFID-Chip an den Leser. Das System speichert den Arbeitsbeginn, wenn Karte und Buchungsfolge gültig sind.[file:14][file:13]

### Pause

Für eine Pause wird zuerst `Pause Start` und nach Rückkehr `Pause Ende` gebucht. So kann die Pausenzeit später sauber nachvollzogen und ausgewertet werden.[file:14]

### Arbeitsende

Zum Feierabend wird `Gehen` gebucht. Erst damit ist der Arbeitstag regulär abgeschlossen.[file:14][file:13]

## Was das System prüft

Das System prüft nicht nur, ob eine Buchung technisch ankommt, sondern auch, ob sie fachlich plausibel ist. Dazu gehören Kartenprüfung, Benutzerstatus, Buchungsreihenfolge und gesetzlich relevante Hinweise.[file:14][file:13]

Mindestens folgende Auffälligkeiten oder Prüfhilfen sind vorgesehen:[file:14][file:13]

- Mehr als 6 Stunden ohne Pause.
- Mehr als 9 Stunden ohne ausreichende Gesamtpause.
- Mehr als 8 Stunden tägliche Arbeitszeit.
- Mehr als 10 Stunden tägliche Arbeitszeit.
- Weniger als 11 Stunden Ruhezeit bis zum nächsten Arbeitsbeginn.
- Buchungen außerhalb des Regelzeitfensters.
- Offene Arbeits- oder Pausenphasen.

Diese Hinweise helfen der Praxis bei der Prüfung. Sie ersetzen aber keine juristische Einzelfallbewertung.[file:14][file:13]

## Bedeutung der Statuswerte

Das System verwendet mehrere Statuswerte, damit Auffälligkeiten klar erkennbar bleiben.[file:14][file:13]

| Status | Bedeutung |
|---|---|
| `OK` | Die Buchung ist unauffällig. |
| `OPEN` | Es fehlt noch ein Abschluss, zum Beispiel `Gehen` oder `Pause Ende`. |
| `WARN` | Die Buchung ist auffällig und sollte angesehen werden. |
| `NEEDS_REVIEW` | Der Fall ist prüfpflichtig und muss aktiv bearbeitet werden. |
| `CORRECTED` | Die ursprüngliche Buchung wurde später korrigiert. |
| `CLOSED_WITH_NOTE` | Ein offener oder auffälliger Fall wurde mit Begründung abgeschlossen. |

Für Laien wichtig: `OPEN` bedeutet nicht automatisch Fehler, sondern zunächst nur „noch nicht abgeschlossen“. `NEEDS_REVIEW` bedeutet dagegen, dass eine berechtigte Person den Fall bewusst prüfen muss.[file:13][file:9]

## Offene Buchungen

Eine offene Buchung liegt vor, wenn ein Beginn ohne passendes Ende bleibt, zum Beispiel `Kommen` ohne `Gehen` oder `Pause Start` ohne `Pause Ende`.[file:14][file:13]

Das System darf solche Fälle nicht einfach automatisch abschließen. Stattdessen bleiben sie offen, werden sichtbar ausgewertet und müssen später administrativ geklärt werden.[file:14][file:13][file:9]

## Vergessene Buchungen

Wenn ein Mitarbeiter das Ausloggen vergisst, wird nicht künstlich ein Feierabend eingetragen. Der Fall bleibt offen, wird nach Regelende auffällig und muss später mit Begründung geklärt werden.[file:13][file:14]

Dasselbe gilt für vergessene Pausenenden. Auch hier wird nicht still ergänzt, sondern dokumentiert und geprüft.[file:13]

## Korrekturen

Korrekturen sind erlaubt, aber nur mit Begründung. Dabei bleibt der alte Stand erhalten, und der neue Stand wird nachvollziehbar als Korrektur dokumentiert.[file:15][file:13][file:14]

Das ist wichtig für die Nachvollziehbarkeit: Das System überschreibt nicht einfach heimlich alte Daten. Es zeigt, was vorher gespeichert war, was geändert wurde, wer die Änderung durchgeführt hat und wann das passiert ist.[file:13][file:9]

## Nachträge

Nachträge sind Buchungen, die nicht in Echtzeit am Terminal erfasst wurden, sondern später manuell eingetragen werden. Typische Gründe sind Geräteausfall, vergessene Buchung oder Notfallbetrieb.[file:14][file:13]

Ein Nachtrag muss als Nachtrag erkennbar bleiben. Er darf nicht so aussehen, als wäre er ursprünglich normal am Terminal entstanden.[file:13][file:14]

## Berichte und Auswertungen

Das System stellt Berichte und Pflichtauswertungen bereit. Dazu gehören mindestens offene Buchungen, Korrekturen, Nachträge, Warnfälle und offene Prüffälle.[file:15][file:14]

Berichte können als CSV oder PDF exportiert werden. Sie sollen Zeitraum, Erstellungszeitpunkt und eine eindeutige Zuordnung zu Mitarbeiter oder Praxis enthalten.[file:14][file:6]

## Backup und Wiederherstellung

Backups können lokal erstellt und optional auf ein NAS gespiegelt werden. Der NAS-Pfad ist als Spiegelziel gedacht, nicht als eigenständiges Langzeitarchiv.[file:15][file:6]

Eine Wiederherstellung aus Backup muss definiert, protokolliert und regelmäßig getestet werden. Backup und Restore gehören ausdrücklich zum Betriebskonzept des Systems.[file:14][file:13][file:6]

## Datenschutz und Sicherheit

Das System verarbeitet Beschäftigtendaten. Deshalb müssen Datenbank, Exportverzeichnisse, Backups und Admin-Zugänge organisatorisch und technisch geschützt werden.[file:14][file:13]

Es sollen nur die Daten verarbeitet werden, die für Zeiterfassung, Prüfung, Korrektur, Nachweis und Verwaltung erforderlich sind. Rechte dürfen nicht ungeprüft vermischt werden.[file:14][file:13]

## Aufbewahrung

Arbeitszeitdaten müssen mindestens 2 Jahre aufbewahrt werden. Fachlich relevante Buchungen sollen im Normalfall nicht physisch gelöscht, sondern über Status, Korrektur oder Archivierung behandelt werden.[file:14][file:13][file:9]

Auch Berichte, Pflichtauswertungen und Exportdateien müssen in ein klares Archivierungs- und Löschkonzept einbezogen werden.[file:14][file:13]

## Wichtige Projektdateien

Für den Betrieb und das Verständnis des Systems sind vor allem diese Dateien wichtig:[file:15][file:9][file:6]

- `README.md` – technischer Überblick und Startanleitung.
- `docs/pflichtenheft_arbeitszeit_v3.md` – verbindliche Anforderungen an das System.
- `docs/regelwerk_arbeitszeit_v3.md` – fachliche Betriebs- und Entscheidungsregeln.
- `planung_gesamt.md` – Umsetzungs- und Architekturplan.
- `scripts/init_db.py` – richtet die Datenbank ein.
- `scripts/setup.py` – fragt wichtige Verzeichnisse für den Betrieb ab.
- `scripts/backup.py` – erstellt Backups.

## Praxisbeispiel

Eine Mitarbeiterin kommt morgens, bucht `Kommen`, geht mittags in Pause, bucht `Pause Start`, kommt zurück und bucht `Pause Ende`, und bucht am Abend `Gehen`. Das ist der normale, vollständige Ablauf.[file:14][file:13]

Vergisst sie am Abend `Gehen`, bleibt der Fall offen. Das System ergänzt den Feierabend nicht automatisch, sondern zeigt den Fall später als offen oder prüfbedürftig an, bis eine berechtigte Person ihn mit Begründung klärt.[file:13][file:14]

## Zusammenfassung für Nichttechniker

Das System soll nicht „schönrechnen“, sondern sauber dokumentieren. Es speichert echte Buchungen, kennzeichnet Probleme sichtbar und sorgt dafür, dass Korrekturen, Nachträge und Prüfungen nachvollziehbar bleiben.[file:13][file:14][file:9]

Gerade für eine kleine Praxis ist das wichtig: Die Bedienung am Terminal bleibt einfach, während die Verwaltung und Prüfung getrennt und sauber dokumentiert erfolgen.[file:15][file:14]
