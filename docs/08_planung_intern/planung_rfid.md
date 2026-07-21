# Planungsdokument: Umstellung der Zeiterfassung auf RFID-only

## Dokumentzweck

Dieses Dokument beschreibt die fachlichen und technischen Anforderungen für die Umstellung des bestehenden Projekts `arbeitszeit` auf ein RFID-only-Buchungsmodell. Es dient als belastbare Arbeitsgrundlage für Claude Code zur Analyse der bestehenden Codebase, zur Umsetzung der Änderungen und zur strukturierten Validierung der Ergebnisse.[cite:62][cite:79][cite:80]

Der Fokus liegt auf einer klaren Trennung zwischen Standardprozess, Ausnahmebehandlung und administrativer Korrektur. Diese Trennung entspricht gängigen Mustern in Zeiterfassungssystemen, in denen fehlerhafte oder unvollständige Buchungen nicht am Terminal, sondern in nachgelagerten Korrekturprozessen behandelt werden.[cite:62][cite:79][cite:83]

## Projektkontext

Es existiert ein bestehendes Projekt `arbeitszeit`, das bereits von Claude entwickelt wurde. Claude kennt die Codebase vollständig und übernimmt auch die Synchronisierung mit GitHub.

Im aktuellen System erfolgt die Mitarbeiterzuordnung über einen RFID-Key, der über einen RFID-Reader eingelesen wird. Zusätzlich wird der Buchungstyp derzeit über ein NumPad ausgewählt.

Die bisherige Eingabelogik soll grundlegend geändert werden:

- Die NumPad-Eingabe wird vollständig entfernt.
- RFID ist künftig die einzige Benutzerinteraktion am Terminal.
- Der Buchungstyp wird nicht mehr manuell ausgewählt, sondern systemseitig aus dem Tageszustand des Mitarbeiters abgeleitet.
- Abweichungen vom Standardablauf werden als Exceptions behandelt.
- Korrekturen sind ausschließlich administrativ erlaubt.

## Zielbild

Der Zielzustand ist ein Terminal, an dem Mitarbeitende ausschließlich ihren RFID-Key vorhalten. Das System erkennt den Mitarbeitenden, ermittelt seinen aktuellen Tageszustand und erzeugt daraus automatisch die nächste zulässige Buchung.

Es gibt keine Terminalbedienung mehr zur Auswahl von:

- Kommen
- Gehen
- Pause beginnen
- Pause beenden

Stattdessen wird die Buchungsart vollständig aus der Reihenfolge der Buchungen pro Mitarbeiter und Kalendertag bestimmt.

## Verbindliche Fachlogik

### Tagesmodell

Für jeden Mitarbeitenden ist pro Kalendertag genau eine Pause vorgesehen. Daraus ergibt sich diese feste Buchungsreihenfolge:

1. Erste Buchung des Tages = **Kommen**
2. Zweite Buchung des Tages = **Pause beginnen**
3. Dritte Buchung des Tages = **Pause beenden**
4. Vierte Buchung des Tages = **Gehen**

Eine fünfte oder weitere Buchung am selben Kalendertag ist fachlich unzulässig. Solche Buchungen dürfen nicht als reguläre Arbeitszeitbuchungen verarbeitet werden, sondern müssen als Exception behandelt werden.

### Zustandsmodell

Claude Code soll die Logik als klaren, testbaren Zustandsautomaten pro Mitarbeitendem und Kalendertag modellieren.

Zustände:

- `0 = keine Buchung vorhanden`
- `1 = gekommen`
- `2 = Pause aktiv`
- `3 = Pause beendet, Arbeit fortgesetzt`
- `4 = Arbeitstag beendet`

Verbindliche Zustandsübergänge:

- Zustand `0` + Scan -> buche `Kommen`, neuer Zustand `1`
- Zustand `1` + Scan -> buche `Pause beginnen`, neuer Zustand `2`
- Zustand `2` + Scan -> buche `Pause beenden`, neuer Zustand `3`
- Zustand `3` + Scan -> buche `Gehen`, neuer Zustand `4`
- Zustand `4` + Scan -> keine reguläre Buchung, sondern Exception

### Tagesbezug

Die Zustandslogik gilt immer **pro Mitarbeitendem und pro Kalendertag**. Mit Beginn eines neuen Kalendertags wird der Ablauf für den jeweiligen Mitarbeitenden auf den Startzustand zurückgesetzt.

Die erste gültige Buchung eines neuen Tages muss deshalb wieder als `Kommen` interpretiert werden. Schichtmodelle über Mitternacht hinweg sind nicht Bestandteil dieses Planungsvorhabens.

## Verbindliche Systemregeln

### Terminalinteraktion

Das Terminal darf ausschließlich RFID-basierte Eingaben verarbeiten. Eine manuelle Auswahl des Buchungstyps durch Mitarbeitende ist im Zielzustand nicht mehr zulässig.

Nach jedem gültigen RFID-Scan soll das System eine eindeutige Rückmeldung ausgeben:

- bei regulärer Buchung: Anzeige des ausgelösten Buchungstyps,
- bei Fehlerfall: Anzeige einer klaren Fehlermeldung.

### Exception-Regel

Alle Abweichungen vom Standardablauf sind als Exceptions zu behandeln und dürfen nicht direkt am Terminal aufgelöst werden. Zeiterfassungssysteme behandeln unplausible, unvollständige oder überschüssige Buchungen typischerweise als Fehler- bzw. Ausnahmefälle, die nachgelagert geprüft und korrigiert werden.[cite:79][cite:80][cite:82]

Mindestens folgende Fälle sind als Exceptions zu behandeln:

- fünfte oder weitere Buchung am selben Kalendertag,
- unbekannter oder keinem Mitarbeitenden zugeordneter RFID-Key,
- technisch ungültiger oder nicht lesbarer RFID-Input,
- optional: versehentliche Mehrfachscans in sehr kurzem Zeitabstand, falls eine Entprellung implementiert wird.

Für jede Exception gilt verbindlich:

- keine Erzeugung einer regulären Arbeitszeitbuchung,
- Ausgabe einer eindeutigen Fehlermeldung,
- Erzeugung eines Logeintrags,
- spätere administrative Prüfbarkeit.

### Administrative Korrektur

Fehlerhafte, fehlende oder unzulässige Buchungen dürfen ausschließlich administrativ korrigiert werden. Eine Korrektur am Terminal durch Mitarbeitende ist nicht zulässig. Das entspricht typischen Korrekturprozessen in professionellen Zeiterfassungssystemen.[cite:62][cite:79][cite:83]

Administrative Korrekturen sollen mindestens diese Fälle abdecken:

- fehlende Buchung ergänzen,
- unzulässige Zusatzbuchung entfernen oder neutralisieren,
- fehlerhaften Tagesverlauf berichtigen,
- Korrekturgrund dokumentieren,
- ausführende Person und Zeitpunkt nachvollziehbar festhalten.

Wenn in der bestehenden Anwendung bereits eine Verwaltungs- oder Backoffice-Funktion für Korrekturen existiert, soll Claude Code diese bevorzugt weiterverwenden oder gezielt erweitern.

## Umsetzungsauftrag für Claude Code

### Hauptaufgabe

Claude Code soll die bestehende Codebase des Projekts `arbeitszeit` analysieren und die Zeiterfassungslogik so umbauen, dass ausschließlich RFID-basierte Buchungen verarbeitet werden.

### Verbindliche Umsetzungsziele

1. Alle NumPad-bezogenen Bestandteile vollständig identifizieren.
2. NumPad-bezogene Funktionalität vollständig aus der aktiven Codebase entfernen.
3. Die neue RFID-only-Buchungslogik als klaren Tageszustandsautomaten implementieren.
4. Exceptions statt Sonderbehandlungen am Terminal einführen.
5. Administrative Korrekturmöglichkeiten erhalten oder gezielt vorbereiten.
6. Bestehende Tests anpassen und fehlende Tests ergänzen.
7. Änderungen sauber in die bestehende Architektur integrieren.
8. Änderungen wie bisher mit GitHub synchronisieren.

### Was ausdrücklich entfernt werden soll

Claude Code soll mindestens folgende NumPad-bezogenen Elemente entfernen oder refaktorieren:

- UI-Komponenten des NumPads,
- Event-Handler und Listener für NumPad-Eingaben,
- Mapping von Tasten auf Buchungstypen,
- Validierungen, die eine manuelle Buchungsauswahl erwarten,
- Konfigurationen, Defaults oder Feature-Flags für NumPad-Betrieb,
- Tests, Fixtures, Mocks und Dokumentation mit NumPad-Bezug,
- technisch überflüssige Abhängigkeiten.

Eine bloße Deaktivierung der Oberfläche ist nicht ausreichend. Ziel ist die vollständige Entfernung der NumPad-Logik aus der aktiven Anwendung.

### Was neu implementiert werden soll

Claude Code soll die neue Buchungslogik so implementieren, dass:

- der RFID-Scan nur noch die Mitarbeiteridentifikation und den Auslösezeitpunkt liefert,
- der Buchungstyp ausschließlich server- oder anwendungsseitig aus dem Tageszustand bestimmt wird,
- pro Mitarbeitendem und Tag exakt vier zulässige Buchungen existieren,
- jede weitere Buchung als Exception behandelt wird,
- die Lösung nachvollziehbar, modular und automatisiert testbar bleibt.

## Daten- und Logging-Anforderungen

### Buchungsdaten

Für jede reguläre Buchung sollen mindestens folgende Daten nachvollziehbar vorliegen:

- Mitarbeiterreferenz,
- RFID-Key oder technische Key-Referenz,
- Zeitstempel,
- Kalendertag,
- abgeleiteter Buchungstyp,
- Zustand vor Verarbeitung,
- Zustand nach Verarbeitung.

### Exception-Logging

Für jede Exception sollen mindestens folgende Daten erfasst werden:

- Zeitstempel,
- RFID-Referenz,
- Mitarbeiterreferenz, falls auflösbar,
- Exception-Typ,
- Fehlermeldung oder technische Beschreibung,
- relevanter Verarbeitungskontext.

### Auditierbarkeit administrativer Änderungen

Administrative Korrekturen sollen nachvollziehbar dokumentiert werden. Korrekturen in Zeiterfassungssystemen werden üblicherweise mit fachlichem Grund, Änderungszeitpunkt und Verantwortlichkeit dokumentiert.[cite:79][cite:80]

Mindestens folgende Angaben sollen bei administrativen Änderungen protokolliert werden:

- wer die Änderung ausgeführt hat,
- wann die Änderung ausgeführt wurde,
- welcher Ursprungszustand vorlag,
- welcher Zielzustand hergestellt wurde,
- welcher fachliche Grund dokumentiert wurde.

## Nicht-funktionale Anforderungen

### Wartbarkeit

Die neue Lösung soll einfacher, klarer und wartbarer sein als die bisherige Kombination aus RFID und NumPad. Historische Logikreste des alten Eingabemodells sollen konsequent entfernt werden.

### Testbarkeit

Die Zustandslogik muss so strukturiert sein, dass sie über automatisierte Tests eindeutig prüfbar ist. Insbesondere Standardabläufe, Grenzfälle und Exception-Fälle sollen separat testbar sein.

### Fehlertoleranz

Unerlaubte Zustandsübergänge dürfen nicht zu stillen Fehlbuchungen führen. Jeder unzulässige Fall soll sichtbar behandelt, protokolliert und administrativ nachbearbeitbar sein.[cite:82]

## Abgrenzung

Nicht Bestandteil dieses Planungsvorhabens sind:

- mehrere Pausen pro Tag,
- frei wählbare Buchungstypen am Terminal,
- Schichtmodelle über Mitternacht,
- Mitarbeitenden-Selbstkorrekturen am Terminal,
- ein Fallback über NumPad.

Wenn solche Anforderungen künftig relevant werden, sollen sie als separate Erweiterung behandelt werden.

## Abnahmekriterien

Die Umsetzung ist erfolgreich, wenn mindestens alle folgenden Kriterien erfüllt sind:

1. Am Terminal kann kein Buchungstyp mehr manuell ausgewählt werden.
2. Der erste gültige RFID-Scan eines Mitarbeitenden am Kalendertag erzeugt `Kommen`.
3. Der zweite gültige RFID-Scan erzeugt `Pause beginnen`.
4. Der dritte gültige RFID-Scan erzeugt `Pause beenden`.
5. Der vierte gültige RFID-Scan erzeugt `Gehen`.
6. Der fünfte gültige RFID-Scan erzeugt keine reguläre Buchung, sondern eine Exception mit Meldung und Logeintrag.
7. Unbekannte RFID-Keys erzeugen keine reguläre Buchung.
8. Korrekturen am Terminal sind nicht möglich.
9. Korrekturen sind ausschließlich administrativ möglich.
10. Der Tageswechsel setzt den Ablauf pro Mitarbeitendem korrekt zurück.
11. Die NumPad-Logik ist aus der aktiven Codebase entfernt.

## Empfohlene Testfälle für Claude Code

Claude Code soll die Umsetzung mindestens gegen folgende Fälle prüfen:

- **Normalfall:** vier Buchungen eines Mitarbeitenden an einem Tag -> `Kommen`, `Pause beginnen`, `Pause beenden`, `Gehen`
- **Überbuchung:** fünfte Buchung am selben Tag -> Exception
- **Neuer Tag:** erster Scan am Folgetag -> wieder `Kommen`
- **Mehrere Mitarbeitende:** unabhängige Zustandsfolgen pro Mitarbeitendem
- **Unbekannter RFID-Key:** keine reguläre Buchung, sondern Exception
- **Admin-Korrekturfall:** fehlerhafte Tagesfolge wird administrativ berichtigt
- **Optionaler Doppelscan-Fall:** definierte Behandlung bei sehr schnellen Mehrfachscans

## Arbeitsmodus für Claude Code

Claude Code soll dieses Dokument als verbindliche Arbeitsgrundlage verwenden und die Umsetzung entlang dieser Reihenfolge vornehmen:

1. Bestehende Codepfade für RFID und NumPad vollständig identifizieren.
2. Die aktuelle Buchungslogik und Datenflüsse analysieren.
3. Die neue Zustandslogik fachlich sauber in die bestehende Architektur einpassen.
4. NumPad-bezogene Logik vollständig entfernen.
5. Exception-Handling und Logging ergänzen oder anpassen.
6. Administrative Korrekturpfade erhalten oder anbinden.
7. Tests aktualisieren und erweitern.
8. Änderungen gegen die Abnahmekriterien prüfen.
9. Ergebnis sauber committen und mit GitHub synchronisieren.

## Hinweise zur Umsetzung

Für Claude Code ist besonders wichtig:

- bestehende Architekturkonventionen der Codebase beibehalten,
- keine parallele Alt-/Neu-Logik erzeugen,
- keine versteckten Rückfallpfade auf NumPad beibehalten,
- Fachlogik und Terminallogik sauber trennen,
- Änderungen nicht nur funktional, sondern auch strukturell bereinigen.

## Einsatz des Dokuments

Dieses Dokument ist als Planungs- und Steuerungsdokument gedacht. Es kann direkt als Referenz in einen Claude-Code-Prompt eingebunden oder Claude Code zusammen mit einem Umsetzungsauftrag übergeben werden.
