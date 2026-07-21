# Abschlussdokument RFID-only-Umstellung

## Zielbild

Die Terminalbedienung wurde von einem zweistufigen Ablauf mit NumPad und anschließendem RFID-Scan auf ein RFID-only-Modell umgestellt. Die Buchungsart wird nicht mehr manuell gewählt, sondern systemseitig aus Tageszustand, Sollzeit und zulässiger Buchungssequenz abgeleitet.[file:259][file:314]

## Umgesetzte Schritte

### 1. NumPad-Entfernung

Die NumPad-Logik wurde vollständig aus Hardware, Ports, Konfiguration, CLI und Simulator entfernt. Damit existiert kein technischer Pfad mehr, in dem Mitarbeitende am Terminal einen Buchungstyp explizit auswählen.[file:259]

### 2. Positionsbasierte RFID-Ableitung

Die Grundlogik der Buchungstyp-Ableitung wurde auf eine positionsbasierte Sequenz umgestellt: `COME → BREAK_START → BREAK_END → GO`. Gleichzeitig wird ein unzulässiger zusätzlicher Scan nach abgeschlossenem Tagesmodell als Sequenzfehler behandelt.[file:259]

### 3. Sollzeitregel für Kurztage

Für Tage mit einer gültigen Sollarbeitszeit von höchstens 6 Stunden wird der zweite Scan als `GO` statt `BREAK_START` interpretiert. Grundlage ist die je Wochentag wirksame `WorkScheduleVersion`, deren Sollzeit sich aus `end_time - start_time` ergibt.[file:314][web:316]

### 3a. Abschlusslogik für Kurztage

Kurztage mit Sollzeit ≤ 6 Stunden erlauben maximal zwei reguläre Buchungen (`COME`, `GO`). Eine dritte Buchung an einem solchen Tag wird nicht als regulärer Buchungstyp verarbeitet, sondern analog zur fünften Buchung im Langtag-Modell als Sequenzfehler behandelt.[web:316]

### 4. Entfernung des RFID-Read-Timeouts

Das frühere `_RFID_READ_TIMEOUT` wurde vollständig entfernt, da es fachlich an das historische NumPad-Zeitfenster gekoppelt war. Im RFID-only-Modell erfolgt das Polling kontinuierlich; verbleibende interne Warteintervalle dienen nur noch der technischen Reaktivität des Readers.[file:259]

### 5. Anti-Doppel-Scan-Schutz

Ein technischer Entprellungsmechanismus verhindert, dass unmittelbare Mehrfach-Scans derselben Karte innerhalb eines kurzen Intervalls als mehrere Buchungen verarbeitet werden. Diese Logik liegt bewusst im Hardware-Layer und verändert die fachliche Domänenlogik nicht.[file:259]

## Ergebnisbild

Die RFID-only-Zustandslogik ist jetzt in drei Ebenen sauber getrennt:

- **Hardware-/Reader-Ebene:** kontinuierliches Polling und Entprellung.
- **Anwendungslogik:** Ableitung des nächsten Buchungstyps aus Tageszustand und Sollzeit.
- **Domänenlogik:** Prüfung von Sequenzfehlern, Pausen- und Arbeitszeit-Compliance.[file:257][file:259][file:314]

Für Langtage mit Sollzeit > 6 Stunden gilt damit ein 4er-Modell (`COME`, `BREAK_START`, `BREAK_END`, `GO`), für Kurztage mit Sollzeit ≤ 6 Stunden ein 2er-Modell (`COME`, `GO`). Zusätzliche Buchungen außerhalb dieser Modelle werden konsistent als Ausnahmefälle behandelt.[web:316][file:314]

## Offene Punkte

Nach dem aktuellen Stand der Umsetzung ist die RFID-only-Migration fachlich geschlossen. Offene Punkte bestehen nur noch dort, wo außerhalb des hier betrachteten Scopes weitere Dokumentations-, Nachweis- oder Betriebsartefakte angepasst werden müssen.[file:257][file:259]
