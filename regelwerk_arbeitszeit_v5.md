# Regelwerk Projekt arbeitszeit – Version 5.0

## 1. Zweck

Dieses Regelwerk definiert die verbindlichen Betriebs-, Prüf-, Korrektur- und Administrationsregeln für **arbeitszeit**. Es ergänzt das Pflichtenheft um konkrete fachliche Entscheidungsregeln.

## 2. Grundregel

Das System speichert reale Buchungen. Fehlende oder unplausible Sachverhalte werden nicht durch stille Systemannahmen ersetzt, sondern gekennzeichnet, protokolliert und administrativ geklärt.

## 3. Terminalbedienung

Der verbindliche Bedienablauf lautet:

1. Buchungsart wählen.
2. RFID-Chip scannen.

Andere Reihenfolgen gelten nicht als Standardprozess.

## 4. Zulässige Buchungsarten

Zugelassen sind nur:

- `Kommen`
- `Gehen`
- `Pause Start`
- `Pause Ende`

## 5. Karten- und Benutzerregeln

Nur aktive, bekannte Karten aktiver Benutzer erzeugen reguläre Buchungen. Unbekannte, inaktive oder ersetzte Karten werden protokolliert und nicht regulär verbucht.

## 6. Plausibilitätsregeln

Mindestens folgende Buchungsfolgen sind unzulässig oder auffällig:

- `Kommen` nach `Kommen`,
- `Gehen` nach `Gehen`,
- `Pause Start` nach `Pause Start`,
- `Pause Ende` ohne offene Pause,
- `Pause Start` nach `Gehen`,
- `Kommen` während offener Pause,
- `Gehen` bei offener Pause ohne Klärung,
- erste Tagesbuchung als `Gehen` oder `Pause Ende`.

## 7. Regelarbeitszeiten

Aktuelle Standard-Regelarbeitszeiten:

| Tag | Beginn | Ende |
|---|---:|---:|
| Montag | 07:30 | 18:00 |
| Dienstag | 07:30 | 18:00 |
| Mittwoch | 07:30 | 18:00 |
| Donnerstag | 07:30 | 14:00 |
| Freitag | 07:30 | 16:00 |

Diese Zeiten dienen als Prüfrahmen und nicht als automatische Endbuchung.

Änderungen dieser Zeiten dürfen nur durch berechtigte Personen erfolgen und müssen protokolliert werden.

## 8. Offene Buchungen

Eine offene Buchung liegt vor, wenn eine Arbeits- oder Pausenphase nicht abgeschlossen wurde. Offene Buchungen bleiben offen, bis sie durch reale Buchung, Nachtrag oder Korrektur geklärt wurden.

Offene Arbeits- und Pausenphasen müssen in Pflichtauswertungen gesondert als offene Fälle ausweisbar sein.

## 9. Warnregeln

Folgende Warnungen sind mindestens vorzusehen:

- offene Arbeitsphase nach Regelende,
- offene Pause nach Regelende,
- Buchung außerhalb des Regelzeitfensters,
- mögliche Pausenverletzung,
- mögliche Überschreitung der Höchstarbeitszeit,
- mögliche Unterschreitung der Ruhezeit.

Warnsachverhalte müssen in Pflichtauswertungen und Berichten als auswertbare Warnfälle erscheinen können.

## 10. Arbeitszeitgesetz-Prüfhilfen

Das System muss mindestens folgende fachliche Prüfhilfen erzeugen:

- Warnung bei mehr als 6 Stunden ohne Pause,
- Warnung bei mehr als 9 Stunden ohne ausreichende Pause,
- Warnung bei mehr als 8 Stunden täglicher Arbeitszeit,
- Eskalation bei mehr als 10 Stunden täglicher Arbeitszeit,
- Warnung bei weniger als 11 Stunden Ruhezeit bis zum nächsten Arbeitsbeginn.

Diese Prüfhilfen sind fachliche Indikatoren und ersetzen keine juristische Einzelfallbewertung.

## 11. Prüfstatus

Folgende fachliche Zustände werden im System unterschieden. Sie sind die verbindliche Grundlage für Pflichtauswertungen, Berichte und normierte Hinweistexte.

**Buchungsstatus** (technisch: `BookingStatus`-Enum auf der Buchungsentität):

- `OK`
- `OPEN`
- `WARN`
- `NEEDS_REVIEW`
- `CORRECTED`
- `CLOSED_WITH_NOTE`

**Fachliche Hinweislagen und Herkunftskennzeichnung** — diese werden im System *nicht* als `BookingStatus`-Werte implementiert, sondern orthogonal modelliert:

- `POSSIBLE_BREAK_VIOLATION`
- `POSSIBLE_REST_VIOLATION`
- `POSSIBLE_MAX_HOURS_VIOLATION`
- `MANUAL_ENTRY_REVIEW`

Die fachlichen Hinweislagen `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION` und `MANUAL_ENTRY_REVIEW` werden nicht als Werte der Enum `BookingStatus` implementiert. Stattdessen erfolgt die Modellierung orthogonal: `POSSIBLE_…` als `ReviewCaseType` auf `ReviewCase`-Datensätzen, `MANUAL_ENTRY_REVIEW` ebenfalls als `ReviewCaseType` auf `ReviewCase`-Datensätzen; zusätzlich kennzeichnet `BookingSource.MANUAL` auf der `TimeBooking` manuelle Erfassungen, kombinierbar mit jedem Buchungsstatus.

## 12. Korrekturen

Korrekturen sind zulässig, aber immer begründungspflichtig. Sie müssen alten Zustand, neuen Zustand, Begründung, korrigierende Person und Zeitstempel dokumentieren.

Korrekturen müssen in Pflichtauswertungen mit altem Zustand, neuem Zustand, Begründung, korrigierender Person und Zeitstempel nachvollziehbar ausweisbar sein.

## 13. Nachträge

Notfall- oder Nachtragsbuchungen müssen ausdrücklich als Nachtrag gekennzeichnet werden. Sie dürfen nicht als normale Echtzeitbuchung erscheinen.

Nachträge müssen in Pflichtauswertungen gesondert ausweisbar und als Nachtrag erkennbar sein.

## 14. Regel bei vergessenem Ausloggen

Wenn `Kommen` ohne `Gehen` bleibt, dann:

1. bleibt der Zustand offen,
2. nach Regelende wird gewarnt,
3. der Fall erhält mindestens `OPEN` oder `NEEDS_REVIEW`,
4. Klärung erfolgt administrativ,
5. Korrektur oder Nachtrag wird begründet dokumentiert.

Eine automatische endgültige `Gehen`-Buchung ist nicht zulässig.

## 15. Regel bei vergessener Pause

Wenn `Pause Start` ohne `Pause Ende` bleibt, wird analog verfahren:

- offener Status,
- Warnung,
- Prüfbedarf,
- dokumentierte Klärung.

## 16. Rollen- und Rechteprinzip

Mitarbeiter dürfen ausschließlich die für sie vorgesehenen Buchungsvorgänge am Terminal auslösen.

Admins dürfen Benutzerkonten, Rollen, Mitarbeiterstammdaten, RFID-Karten und Regelarbeitszeiten verwalten.

Prüfer dürfen offene und auffällige Fälle, Nachträge und Korrekturen im Rahmen ihrer fachlichen Zuständigkeit bearbeiten, jedoch keine Benutzerkonten, Rollen oder Systemkonfigurationen verwalten.

Die technische Betreuung darf Systemcheck, Backup, Restore und betriebsnahe Systemfunktionen ausführen, jedoch keine fachlichen Freigaben, Benutzerrollen oder Mitarbeiterstammdaten ändern.

Benutzerkonten mit den Rollen `ADMIN`, `REVIEWER` und `TECH` dürfen nur durch einen aktiven Benutzer mit Rolle `ADMIN` angelegt, geändert, deaktiviert oder reaktiviert werden.

Der erste aktive Administrator wird über einen gesonderten Bootstrap-Prozess eingerichtet.

Jede Änderung an Rolle oder Aktivstatus eines Benutzerkontos ist als Administrationsvorgang zu protokollieren.

## 16a. Benutzerkontenverwaltung

Benutzerkonten sind eigenständige Zugangsobjekte des Systems und nicht mit Mitarbeiterdatensätzen gleichzusetzen.

Ein Benutzerkonto kann optional einem Mitarbeiterdatensatz zugeordnet sein.

Für jedes Benutzerkonto sind Benutzername, Rolle, Aktivstatus und sicher gespeicherte Authentifizierungsdaten zu führen.

Doppelte Benutzernamen sind unzulässig.

Inaktive Benutzerkonten dürfen keine administrativen oder prüfenden Aktionen ausführen.

## 17. Datenschutzregel

Es dürfen nur erforderliche Beschäftigtendaten verarbeitet werden. Zugriffe auf Datenbank, Berichte, Pflichtauswertungen, Export und Backup sind auf berechtigte Personen zu beschränken.

## 18. Aufbewahrung und Löschung

Arbeitszeitdaten sind mindestens 2 Jahre aufzubewahren. Fachlich relevante Buchungen werden im Normalfall nicht physisch gelöscht, sondern durch Status, Korrektur oder Archivierung behandelt.

Berichte, Pflichtauswertungen und Exportdateien sind nach dem festgelegten Archivierungs- und Löschkonzept zu behandeln.

## 19. Fallback-Regel

Bei Reader-, Terminal- oder Stromausfall gilt ein Notfallprozess mit manueller Erfassung und späterem gekennzeichnetem Nachtrag. Jeder Nachtrag ist begründungspflichtig.

## 20. Backup- und Restore-Regel

Backups sind regelmäßig zu erstellen. Restore darf nur berechtigt durchgeführt werden und muss protokolliert sowie regelmäßig testweise geprüft werden.

Soweit Berichte, Pflichtauswertungen oder Exportdateien Bestandteil des festgelegten Sicherungskonzepts sind, sind auch diese in Backup- und Restore-Prüfungen einzubeziehen.

Berechtigt für Backup- und Restore-Funktionen sind ausschließlich Benutzer mit Rolle `ADMIN` oder `TECH`.

## 21. Zeitregel

Die Systemzeit muss zuverlässig synchronisiert sein. Zeitsprünge oder manuelle Uhrzeitänderungen sind zu protokollieren und fachlich zu prüfen.

## 22. Prüfintervalle

Mindestens empfohlen sind:

- tägliche Prüfung offener Fälle anhand der Pflichtauswertungen,
- wöchentliche Prüfung möglicher Verstöße anhand der Pflichtauswertungen,
- regelmäßige Prüfung von Korrekturen und Nachträgen anhand der Pflichtauswertungen,
- regelmäßige Backup- und Restore-Kontrolle.

## 23. Leitregel

> Reale Buchungen haben Vorrang. Auffälligkeiten werden erkannt, dokumentiert und administrativ geklärt. Korrekturen, Nachträge und Regeländerungen müssen jederzeit nachvollziehbar bleiben. Fachliche Zustände müssen auch in Berichten und Pflichtauswertungen konsistent nachvollziehbar sein.
