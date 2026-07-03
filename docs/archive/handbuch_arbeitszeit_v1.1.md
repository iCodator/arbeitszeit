Handbuch arbeitszeit – Printversion v1.1
  

  Zum Inhalt springen
  
    
      
## Inhaltsverzeichnis

      
        - Einführung

        - Rollen und Grundprinzip

        - Installation und Grundsetup

        - Geräte einrichten

        - Technische Betreuung einrichten

        - Administrator einrichten

        - Prüfer einrichten

        - Mitarbeiter einrichten

        - Regelbetrieb und Buchungen

        - Prüfungen, Status und Sonderfälle

        - Berichte, Backup und Datenschutz

        - Projektdateien und Nutzungshinweise

      
    

    
      
        Handbuch
        
# arbeitszeit

        Lokales Zeiterfassungssystem für eine Zahnarztpraxis mit Terminalbetrieb, Admin-CLI, Prüfprozessen und lokalem Backup.

        
          
            Dokumenttyp
            Benutzer- und Betriebshandbuch in druckoptimierter HTML-Fassung mit Sprungmarken.

          
          
            Stand
            Juni 2026, basierend auf `README.md`, `docs/informelles/planung_gesamt.md`, `docs/pflichtenheft_arbeitszeit_v4.md`, `docs/regelwerk_arbeitszeit_v4.md` und `docs/addendum_datenschutz_it_sicherheit_arbeitszeit_v1.md`.

          
        
      

      
        
## Inhaltsverzeichnis

        
          - 1. Einführung

          - 2. Rollen und Grundprinzip

          - 3. Installation und Grundsetup

          - 4. Geräte einrichten

          - 5. Technische Betreuung einrichten

          - 6. Administrator einrichten

          - 7. Prüfer einrichten

          - 8. Mitarbeiter einrichten

          - 9. Regelbetrieb und Buchungen

          - 10. Prüfungen, Status und Sonderfälle

          - 11. Berichte, Backup und Datenschutz

          - 12. Projektdateien und Nutzungshinweise

        
      

      
        
## 1. Einführung

        arbeitszeit ist ein lokales Zeiterfassungssystem für eine Zahnarztpraxis. Es erfasst Arbeitsbeginn, Arbeitsende und Pausen über ein Terminal mit USB-Numpad und RFID-Karte. Die Verwaltung erfolgt getrennt über eine Admin-CLI.

        Dieses Handbuch erklärt das System in einfacher Sprache. Es richtet sich an Praxisinhaber, Verwaltung, Prüfer und technisch verantwortliche Personen, nicht an Entwickler.

        
          
### Zweck des Systems

          Das System soll Arbeitszeiten objektiv, verlässlich und nachvollziehbar erfassen. Es speichert echte Buchungen, erkennt Auffälligkeiten und unterstützt die Praxis dabei, offene oder problematische Fälle zu prüfen und sauber zu dokumentieren.

          Nicht Teil des Systems sind Lohnabrechnung, Urlaubsplanung, Dienstplanung oder eine vollständige Personalverwaltung. Dafür ist das System bewusst nicht ausgelegt.

        
      

      
        
## 2. Rollen und Grundprinzip

        
### Grundprinzip

        
          - Buchungsart am Numpad wählen.

          - RFID-Chip an den Reader halten.

          - Das System prüft Karte, Mitarbeiter und Buchungsfolge.

          - Die Buchung wird gespeichert oder als auffällig markiert.

        
        Wichtig ist: Das System speichert reale Vorgänge. Fehlende oder unplausible Situationen werden nicht still „geradegebogen“, sondern als offen, auffällig oder prüfpflichtig gekennzeichnet.

        
### Beteiligte Rollen

        
          - Mitarbeiter buchen ihre Zeiten.

          - Admin verwaltet Benutzer, Karten, Regelarbeitszeiten und den Betrieb.

          - Prüfer bewertet offene oder auffällige Fälle.

          - Technische Betreuung ist für Systembetrieb, Backup und Restore zuständig.

        
        Ein normaler Mitarbeiter darf keine administrativen Änderungen an Benutzern, Karten, Regelzeiten oder Korrekturen durchführen. Rechte dürfen nicht ungeprüft vermischt werden.

        
### Empfohlene Reihenfolge der Einrichtung

        
          - Software installieren.

          - Datenbank initialisieren.

          - Lokale Pfade konfigurieren.

          - Geräte anschließen und prüfen.

          - Technische Betreuung festlegen.

          - Administrator festlegen und einrichten.

          - Prüfer festlegen und einrichten.

          - Mitarbeiter anlegen.

          - RFID-Karten zuweisen.

          - Regelarbeitszeiten prüfen.

          - Systemcheck durchführen.

        
      

      
        
## 3. Installation und Grundsetup

        Für die Installation sind Python, Linux und die benötigte Hardware erforderlich. Das Projekt wird lokal aus dem Git-Repository installiert.

```
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

        Danach wird die Datenbank eingerichtet und die lokalen Pfade werden konfiguriert.

```
python scripts/init_db.py --db arbeitszeit.db
python scripts/setup.py --db arbeitszeit.db
```

      

      
        
## 4. Geräte einrichten

        Für den Terminal-Betrieb werden zwei USB-Geräte benötigt: ein RFID-Reader und ein separates numerisches USB-Numpad.

        
### Schritt 1: Geräte anschließen

        
          - RFID-Reader per USB anschließen.

          - Numerisches USB-Numpad per USB anschließen.

          - Den Terminal-Rechner bei Bedarf neu erkennen lassen.

        
        
### Schritt 2: Gerätepfade konkret ermitteln

```
ls -l /dev/input/by-id/
```

        Danach die passenden Pfade für Numpad und RFID-Reader notieren. Nach Möglichkeit den Eintrag mit `event-kbd` verwenden.

```
/dev/input/by-id/usb-Logitech_USB_Keyboard-event-kbd
/dev/input/by-id/usb-ACS_ACR1281_1S_Dual_Reader-event-kbd
```

        Falls nötig, kann zusätzlich die technische Detailanzeige verwendet werden:

```
cat /proc/bus/input/devices
```

        
### Schritt 3: Gerätepfade im Startbefehl eintragen

```
python -m arbeitszeit.presentation.terminal_ui.main \
    --db arbeitszeit.db \
    --numpad /dev/input/by-id/usb-Logitech_USB_Keyboard-event-kbd \
    --rfid /dev/input/by-id/usb-ACS_ACR1281_1S_Dual_Reader-event-kbd \
    --terminal-id 1
```

        
          - Hinter `--numpad` steht immer der Pfad des Numpads.

          - Hinter `--rfid` steht immer der Pfad des RFID-Readers.

          - `--terminal-id` ist die interne Kennung des Terminals und nicht der Gerätepfad.

        
        
### Schritt 4: Funktion der Geräte prüfen

        Nach dem Anschließen sollte ein Systemcheck ausgeführt werden. Wichtig ist außerdem die Bedienreihenfolge am Terminal: zuerst Buchungsart wählen, dann RFID-Chip scannen.

      

      
        
## 5. Technische Betreuung einrichten

        Die technische Betreuung ist für Systembetrieb, Backup, Restore und technische Stabilität zuständig.

        
### Schritt 1: Zuständigkeit schriftlich festlegen

        Festzuhalten sind mindestens Backup, Restore, Systemcheck, Geräteprüfung und Fehlerbehandlung.

        
### Schritt 2: Benutzerkonto mit Technik-Rolle einrichten

        Das Konto wird per direkter Datenbankoperation angelegt (einmalige Einrichtungsaufgabe):

        
          - Benutzername, zum Beispiel `tech1`

          - Passwort-Hash (von der technischen Betreuung selbst erzeugt)

          - Rolle `TECH`

          - aktiv = ja

          - optional ohne direkte Mitarbeiterzuordnung

        
        
### Schritt 3: Backup-Pfade festlegen

```
python scripts/setup.py --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
    --export-dir /var/exports/arbeitszeit
```

        
### Schritt 4: Backup praktisch testen

```
python scripts/backup.py \
    --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit
```

        
### Schritt 5: Systemcheck regelmäßig ausführen

```
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 3 system check
```

        
### Schritt 6: Restore-Prozess dokumentieren und üben

        Eine gute Minimaldokumentation enthält Speicherort der Backups, Berechtigung für Restore, Reihenfolge der Wiederherstellung, Prüfschritte und Datum des letzten Restore-Tests.

      

      
        

## 6. Administrator einrichten

        Ein Administrator verwaltet Benutzer, Karten, Regelarbeitszeiten und Systembetrieb.

        
### Schritt 1: Verantwortliche Person verbindlich festlegen

        
          - Name der verantwortlichen Person

          - Vertretung bei Abwesenheit

          - ab welchem Datum die Rolle gilt

          - welche Aufgaben die Person konkret übernehmen darf

        
        
### Schritt 2: Benutzerkonto anlegen

        Benutzerkonten werden per direkter Datenbankoperation eingetragen. Das ist eine einmalige Einrichtungsaufgabe der technischen Betreuung. Benötigt werden:

        
          - Benutzername, zum Beispiel `admin1`

          - Passwort-Hash (wird von der technischen Betreuung erzeugt)

          - Rolle `ADMIN`

          - aktiv = ja

          - optional Verknüpfung zu einer Mitarbeiterperson

        
        Nach der Einrichtung erhält die Person eine numerische Benutzer-ID, mit der sie die Admin-CLI aufruft.

        
### Schritt 3: Admin-ID dokumentieren

        
          - Benutzerkonto anlegen lassen (technische Betreuung).

          - Zugeteilte Benutzer-ID notieren.

          - Diese ID in der internen Dokumentation festhalten.

          - CLI künftig mit genau dieser ID starten.

        

```
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 system check
```

        
### Schritt 4: Admin-Funktionen prüfen

        
          - `employees list`

          - `schedule show`

          - `reports open-bookings`

          - `system check`

          - `system backup`

        
        
### Schritt 5: Admin-Rechte nicht für Alltagsbuchungen verwenden

        Admin-Rechte sollten nicht im Alltag für normale Zeiterfassung genutzt werden. Sie sind für Verwaltung, Pflege, Korrekturen, Regelarbeitszeiten, Berichte, Systemcheck und Backup gedacht.

      

      
        

## 7. Prüfer einrichten

        Ein Prüfer bewertet offene oder auffällige Fälle.

        
### Schritt 1: Prüfer organisatorisch benennen

        
          - wer Hauptprüfer ist

          - wer vertreten darf

          - in welchem Rhythmus geprüft wird

          - wo Prüfergebnisse dokumentiert werden

        
        
### Schritt 2: Benutzerkonto mit Prüfer-Rolle einrichten

        Wie beim Admin richtet die technische Betreuung das Konto per direkter Datenbankoperation ein:

        
          - Benutzername, zum Beispiel `pruefer1`

          - Passwort-Hash (wird von der technischen Betreuung erzeugt)

          - Rolle `REVIEWER`

          - aktiv = ja

          - optional Verknüpfung zu einer Mitarbeiterperson

        
        
### Schritt 3: Prüfer-ID dokumentieren

        Wie beim Admin braucht auch der Prüfer eine Benutzer-ID für die Admin-CLI. Diese ID sollte intern dokumentiert und nur für Prüftätigkeiten verwendet werden.

        
### Schritt 4: Prüffunktionen testen

        Hinweis: Auswertungen mit Zeitraumfilter erfordern zwingend `--from` und `--to` (Datum im Format `JJJJ-MM-TT`).

```
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 2 reports open-bookings
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 2 reports warn-cases --from 2026-06-01 --to 2026-06-30
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 2 reports corrections --from 2026-06-01 --to 2026-06-30
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 2 reports supplements --from 2026-06-01 --to 2026-06-30
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 2 reports open-review-cases
```

        
### Schritt 5: Prüfintervalle verbindlich festlegen

        Mindestens empfohlen sind tägliche Prüfungen offener Fälle, wöchentliche Prüfungen möglicher Verstöße sowie regelmäßige Prüfungen von Korrekturen und Nachträgen.

      

      
        

## 8. Mitarbeiter einrichten

        Mitarbeiter sind die Personen, deren Arbeitszeiten erfasst werden. Ohne angelegte Mitarbeiter und zugewiesene RFID-Karten ist keine reguläre Buchung möglich.

        
### Schritt 1: Stammdaten vorbereiten

        
          - Personalnummer, zum Beispiel `E001`

          - Vorname

          - Nachname

          - Aktiv-Status

          - optional Beschäftigungsbeginn

          - optional Beschäftigungsende

        
        
### Schritt 2: Mitarbeiterliste prüfen

```
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 employees list
```

        
### Schritt 3: Mitarbeiter anlegen

        
          - Mit einem Admin-Konto anmelden.

          - Prüfen, ob die Person schon existiert.

          - Mitarbeiter mit Personalnummer, Vorname und Nachname anlegen.

          - Kontrollieren, dass der Mitarbeiter als aktiv geführt wird.

        

```
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 employees add --help
```

        
### Schritt 4: RFID-Karte zuweisen

        
          - Neue RFID-Karte bereitlegen.

          - Mitarbeiter-ID notieren.

          - Kartenzuweisung mit Admin-Rechten durchführen.

          - Eine Testbuchung am Terminal machen.

          - Prüfen, ob die Buchung regulär gespeichert wird.

        

```
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 cards assign --help
```

        
### Schritt 5: Statusänderungen sauber pflegen

        Wenn ein Mitarbeiter ausscheidet oder vorübergehend nicht mehr buchen soll, wird der Status mit `employees deactivate` geändert und nicht einfach unsichtbar gelöscht. Soll die Karte gesperrt werden, gibt es `cards deactivate`.

      

      
        
## 9. Regelbetrieb und Buchungen

        
### Regelarbeitszeiten prüfen

        
          
            TagBeginnEnde
          
          
            Montag07:3018:00
            Dienstag07:3018:00
            Mittwoch07:3018:00
            Donnerstag07:3014:00
            Freitag07:3016:00
          
        
        Diese Zeiten dienen als Prüfrahmen, aber nicht als automatische Buchung.

        
### Was Mitarbeiter buchen können

        
          - `Kommen`

          - `Gehen`

          - `Pause Start`

          - `Pause Ende`

        
        
### Typische Buchungssituationen

        Ein Mitarbeiter wählt `Kommen` und hält danach den RFID-Chip an den Leser. Für eine Pause wird zuerst `Pause Start` und nach Rückkehr `Pause Ende` gebucht. Zum Feierabend wird `Gehen` gebucht.

      

      
        
## 10. Prüfungen, Status und Sonderfälle

        
### Was das System prüft

        
          - Mehr als 6 Stunden ohne Pause.

          - Mehr als 9 Stunden ohne ausreichende Gesamtpause.

          - Mehr als 8 Stunden tägliche Arbeitszeit.

          - Mehr als 10 Stunden tägliche Arbeitszeit.

          - Weniger als 11 Stunden Ruhezeit bis zum nächsten Arbeitsbeginn.

          - Buchungen außerhalb des Regelzeitfensters.

          - Offene Arbeits- oder Pausenphasen.

        
        
### Bedeutung der Statuswerte

        
          
            StatusBedeutung
          
          
            `OK`Die Buchung ist unauffällig.
            `OPEN`Es fehlt noch ein Abschluss.
            `WARN`Die Buchung ist auffällig und sollte angesehen werden.
            `NEEDS_REVIEW`Der Fall ist prüfpflichtig und muss aktiv bearbeitet werden.
            `CORRECTED`Die ursprüngliche Buchung wurde später korrigiert.
            `CLOSED_WITH_NOTE`Ein Fall wurde mit Begründung abgeschlossen.
          
        
        
### Offene Buchungen

        Eine offene Buchung liegt vor, wenn ein Beginn ohne passendes Ende bleibt.

        
### Vergessene Buchungen

        Wenn ein Mitarbeiter das Ausloggen vergisst, wird nicht künstlich ein Feierabend eingetragen.

        
### Korrekturen

        Korrekturen sind erlaubt, aber nur mit Begründung. Dabei bleibt der alte Stand erhalten.

        
### Nachträge

        Nachträge sind Buchungen, die nicht in Echtzeit am Terminal erfasst wurden, sondern später manuell eingetragen werden.

      

      
        
## 11. Berichte, Backup und Datenschutz

        
### Berichte und Auswertungen

        Das System stellt Berichte und Pflichtauswertungen bereit. Dazu gehören mindestens offene Buchungen, Korrekturen, Nachträge, Warnfälle und offene Prüffälle.

        Berichte können als CSV oder PDF exportiert werden.

        
### Backup und Wiederherstellung

        Backups können lokal erstellt und optional auf ein NAS gespiegelt werden. Eine Wiederherstellung aus Backup muss definiert, protokolliert und regelmäßig getestet werden.

        
### Datenschutz und Sicherheit

        Das System verarbeitet Beschäftigtendaten. Deshalb müssen Datenbank, Exportverzeichnisse, Backups und Admin-Zugänge organisatorisch und technisch geschützt werden.

        
### Aufbewahrung

        Arbeitszeitdaten müssen mindestens 2 Jahre aufbewahrt werden. Fachlich relevante Buchungen sollen im Normalfall nicht physisch gelöscht werden.

      

      
        
## 12. Projektdateien und Nutzungshinweise

        
### Wichtige Projektdateien

        
          - `README.md` – technischer Überblick und Startanleitung.

          - `docs/pflichtenheft_arbeitszeit_v4.md` – verbindliche Anforderungen an das System.

          - `docs/regelwerk_arbeitszeit_v4.md` – fachliche Betriebs- und Entscheidungsregeln.

          - `docs/addendum_datenschutz_it_sicherheit_arbeitszeit_v1.md` – Datenschutz und IT-Sicherheit für die Zahnarztpraxis (DSGVO, BDSG, IT-Sicherheitsrichtlinie §75b SGB V).

          - `docs/anlage_einhaltung_pflichtenheft_v2.md` – Nachweis der fachlichen Anforderungserfüllung.

          - `docs/informelles/planung_gesamt.md` – Umsetzungs- und Architekturplan (für technische Betreuung).

          - `scripts/init_db.py` – richtet die Datenbank ein.

          - `scripts/setup.py` – fragt wichtige Verzeichnisse für den Betrieb ab.

          - `scripts/backup.py` – erstellt Backups.

        
        
### Praxisbeispiel

        Eine Mitarbeiterin kommt morgens, bucht `Kommen`, geht mittags in Pause, bucht `Pause Start`, kommt zurück und bucht `Pause Ende`, und bucht am Abend `Gehen`.

        Vergisst sie am Abend `Gehen`, bleibt der Fall offen. Das System ergänzt den Feierabend nicht automatisch, sondern zeigt den Fall später als offen oder prüfbedürftig an.

        
### Hinweise zur Nutzung dieses Handbuchs

        Dieses Handbuch ist bewusst laienverständlich geschrieben. Für technische Details, genaue CLI-Parameter und Entwicklungsfragen sind vor allem `README.md`, `docs/informelles/planung_gesamt.md`, `docs/pflichtenheft_arbeitszeit_v4.md` und `docs/regelwerk_arbeitszeit_v4.md` maßgeblich.

      
    
  
  
    arbeitszeit · Handbuch · Stand Juni 2026 · Pflichtenheft v4 / Regelwerk v4
