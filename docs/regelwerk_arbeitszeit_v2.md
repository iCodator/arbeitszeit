# Regelwerk Projekt arbeitszeit – Version 2

## 1. Zweck

Dieses Regelwerk definiert die verbindlichen Betriebs-, Prüf-, Korrektur- und Administrationsregeln für **arbeitszeit**.[cite:185] Es ergänzt das Pflichtenheft um konkrete fachliche Entscheidungsregeln.[cite:185]

## 2. Grundregel

Das System speichert reale Buchungen.[cite:185] Fehlende oder unplausible Sachverhalte werden nicht durch stille Systemannahmen ersetzt, sondern gekennzeichnet, protokolliert und administrativ geklärt.[cite:185]

## 3. Terminalbedienung

Der verbindliche Bedienablauf lautet:[cite:185]

1. Buchungsart wählen.
2. RFID-Chip scannen.[cite:186]

Andere Reihenfolgen gelten nicht als Standardprozess.[cite:185]

## 4. Zulässige Buchungsarten

Zugelassen sind nur:[cite:185]

- `Kommen`
- `Gehen`
- `Pause Start`
- `Pause Ende`

## 5. Karten- und Benutzerregeln

Nur aktive, bekannte Karten aktiver Benutzer erzeugen reguläre Buchungen.[cite:185] Unbekannte, inaktive oder ersetzte Karten werden protokolliert und nicht regulär verbucht.[cite:185]

## 6. Plausibilitätsregeln

Mindestens folgende Buchungsfolgen sind unzulässig oder auffällig:[cite:185]

- `Kommen` nach `Kommen`,
- `Gehen` nach `Gehen`,
- `Pause Start` nach `Pause Start`,
- `Pause Ende` ohne offene Pause,
- `Pause Start` nach `Gehen`,
- `Kommen` während offener Pause,
- `Gehen` bei offener Pause ohne Klärung,
- erste Tagesbuchung als `Gehen` oder `Pause Ende`.[cite:185]

## 7. Regelarbeitszeiten

Aktuelle Standard-Regelarbeitszeiten:[cite:185]

| Tag | Beginn | Ende |
|---|---:|---:|
| Montag | 07:30 | 18:00 |
| Dienstag | 07:30 | 18:00 |
| Mittwoch | 07:30 | 18:00 |
| Donnerstag | 07:30 | 14:00 |
| Freitag | 07:30 | 16:00 |

Diese Zeiten dienen als Prüfrahmen und nicht als automatische Endbuchung.[cite:185]

Änderungen dieser Zeiten dürfen nur durch berechtigte Personen erfolgen und müssen protokolliert werden.[cite:185]

## 8. Offene Buchungen

Eine offene Buchung liegt vor, wenn eine Arbeits- oder Pausenphase nicht abgeschlossen wurde.[cite:185] Offene Buchungen bleiben offen, bis sie durch reale Buchung, Nachtrag oder Korrektur geklärt wurden.[cite:185]

## 9. Warnregeln

Folgende Warnungen sind mindestens vorzusehen:[cite:185]

- offene Arbeitsphase nach Regelende,
- offene Pause nach Regelende,
- Buchung außerhalb des Regelzeitfensters,
- mögliche Pausenverletzung,
- mögliche Überschreitung der Höchstarbeitszeit,
- mögliche Unterschreitung der Ruhezeit.[cite:185][cite:333][cite:336][cite:339]

## 10. Arbeitszeitgesetz-Prüfhilfen

Das System muss mindestens folgende fachliche Prüfhilfen erzeugen:[cite:333][cite:336][cite:339]

- Warnung bei mehr als 6 Stunden ohne Pause,[cite:336]
- Warnung bei mehr als 9 Stunden ohne ausreichende Pause,[cite:333][cite:336]
- Warnung bei mehr als 8 Stunden täglicher Arbeitszeit,[cite:333][cite:339]
- Eskalation bei mehr als 10 Stunden täglicher Arbeitszeit,[cite:333][cite:339]
- Warnung bei weniger als 11 Stunden Ruhezeit bis zum nächsten Arbeitsbeginn.[cite:333][cite:339]

Diese Prüfhilfen sind fachliche Indikatoren und ersetzen keine juristische Einzelfallbewertung.[cite:185]

## 11. Prüfstatus

Mindestens folgende Statuswerte gelten:[cite:185]

- `OK`
- `OPEN`
- `WARN`
- `NEEDS_REVIEW`
- `CORRECTED`
- `CLOSED_WITH_NOTE`
- `POSSIBLE_BREAK_VIOLATION`
- `POSSIBLE_REST_VIOLATION`
- `POSSIBLE_MAX_HOURS_VIOLATION`
- `MANUAL_ENTRY`[cite:185]

## 12. Korrekturen

Korrekturen sind zulässig, aber immer begründungspflichtig.[cite:185] Sie müssen alten Zustand, neuen Zustand, Begründung, korrigierende Person und Zeitstempel dokumentieren.[cite:185]

## 13. Nachträge

Notfall- oder Nachtragsbuchungen müssen ausdrücklich als Nachtrag gekennzeichnet werden.[cite:185] Sie dürfen nicht als normale Echtzeitbuchung erscheinen.[cite:185]

## 14. Regel bei vergessenem Ausloggen

Wenn `Kommen` ohne `Gehen` bleibt, dann:[cite:185]

1. bleibt der Zustand offen,
2. nach Regelende wird gewarnt,
3. der Fall erhält mindestens `OPEN` oder `NEEDS_REVIEW`,
4. Klärung erfolgt administrativ,
5. Korrektur oder Nachtrag wird begründet dokumentiert.[cite:185]

Eine automatische endgültige `Gehen`-Buchung ist nicht zulässig.[cite:185]

## 15. Regel bei vergessener Pause

Wenn `Pause Start` ohne `Pause Ende` bleibt, wird analog verfahren:[cite:185]

- offener Status,
- Warnung,
- Prüfbedarf,
- dokumentierte Klärung.[cite:185]

## 16. Rollen- und Rechteprinzip

Mitarbeiter dürfen buchen.[cite:185] Admins dürfen Benutzer, Karten und Regelzeiten pflegen.[cite:185] Prüfer dürfen offene und auffällige Fälle bewerten.[cite:185] Technische Betreuung darf Backup, Restore und Systembetrieb verantworten.[cite:185]

Rechte dürfen nicht ungeprüft vermischt werden.[cite:335]

## 17. Datenschutzregel

Es dürfen nur erforderliche Beschäftigtendaten verarbeitet werden.[cite:332][cite:335] Zugriffe auf Datenbank, Export und Backup sind auf berechtigte Personen zu beschränken.[cite:335]

## 18. Aufbewahrung und Löschung

Arbeitszeitdaten sind mindestens 2 Jahre aufzubewahren.[cite:332] Fachlich relevante Buchungen werden im Normalfall nicht physisch gelöscht, sondern durch Status, Korrektur oder Archivierung behandelt.[cite:185]

## 19. Fallback-Regel

Bei Reader-, Terminal- oder Stromausfall gilt ein Notfallprozess mit manueller Erfassung und späterem gekennzeichnetem Nachtrag.[cite:185] Jeder Nachtrag ist begründungspflichtig.[cite:185]

## 20. Backup- und Restore-Regel

Backups sind regelmäßig zu erstellen.[cite:185] Restore darf nur berechtigt durchgeführt werden und muss protokolliert sowie regelmäßig testweise geprüft werden.[cite:185]

## 21. Zeitregel

Die Systemzeit muss zuverlässig synchronisiert sein.[cite:185] Zeitsprünge oder manuelle Uhrzeitänderungen sind zu protokollieren und fachlich zu prüfen.[cite:185]

## 22. Prüfintervalle

Mindestens empfohlen sind:[cite:185]

- tägliche Prüfung offener Fälle,
- wöchentliche Prüfung möglicher Verstöße,
- regelmäßige Prüfung von Korrekturen und Nachträgen,
- regelmäßige Backup- und Restore-Kontrolle.[cite:185]

## 23. Leitregel

> Reale Buchungen haben Vorrang. Auffälligkeiten werden erkannt, dokumentiert und administrativ geklärt. Korrekturen, Nachträge und Regeländerungen müssen jederzeit nachvollziehbar bleiben.[cite:185]
