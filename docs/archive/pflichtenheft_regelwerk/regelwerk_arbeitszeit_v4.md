# Regelwerk Projekt arbeitszeit – Version 4

## 1. Zweck

Dieses Regelwerk definiert die verbindlichen Betriebs-, Prüf-, Korrektur- und Administrationsregeln für **arbeitszeit**. Es ergänzt das Pflichtenheft um konkrete fachliche Entscheidungsregeln.[cite:5]

## 2. Grundregel

Das System speichert reale Buchungen. Fehlende oder unplausible Sachverhalte werden nicht durch stille Systemannahmen ersetzt, sondern gekennzeichnet, protokolliert und administrativ geklärt.[cite:5]

## 3. Terminalbedienung

Der verbindliche Bedienablauf lautet:

1. Buchungsart wählen.
2. RFID-Chip scannen.

Andere Reihenfolgen gelten nicht als Standardprozess.

## 4. Zulässige Buchungsarten

Zugelassen sind nur:[cite:5]

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

Aktuelle Standard-Regelarbeitszeiten:[cite:5]

| Tag | Beginn | Ende |
|---|---:|---:|
| Montag | 07:30 | 18:00 |
| Dienstag | 07:30 | 18:00 |
| Mittwoch | 07:30 | 18:00 |
| Donnerstag | 07:30 | 14:00 |
| Freitag | 07:30 | 16:00 |

Diese Zeiten dienen als Prüfrahmen und nicht als automatische Endbuchung.[cite:5]

Änderungen dieser Zeiten dürfen nur durch berechtigte Personen erfolgen und müssen protokolliert werden.

## 8. Offene Buchungen

Eine offene Buchung liegt vor, wenn eine Arbeits- oder Pausenphase nicht abgeschlossen wurde. Offene Buchungen bleiben offen, bis sie durch reale Buchung, Nachtrag oder Korrektur geklärt wurden.[cite:5]

Offene Arbeits- und Pausenphasen müssen in Pflichtauswertungen gesondert als offene Fälle ausweisbar sein.[cite:5]

Die Umsetzung offener Fälle erfolgt über zentrale Pflichtauswertungen und normierte Reports. Ad-hoc-Auswertungen dürfen diese Einordnung fachlich nicht unterlaufen oder verdecken.

## 9. Warnregeln

Folgende Warnungen sind mindestens vorzusehen:[cite:5]

- offene Arbeitsphase nach Regelende,
- offene Pause nach Regelende,
- Buchung außerhalb des Regelzeitfensters,
- mögliche Pausenverletzung,
- mögliche Überschreitung der Höchstarbeitszeit,
- mögliche Unterschreitung der Ruhezeit.

Warnsachverhalte müssen in Pflichtauswertungen und Berichten als auswertbare Warnfälle erscheinen können.[cite:5]

## 10. Arbeitszeitgesetz-Prüfhilfen

Das System muss mindestens folgende fachliche Prüfhilfen erzeugen:[cite:5]

- Warnung bei mehr als 6 Stunden ohne Pause,
- Warnung bei mehr als 9 Stunden ohne ausreichende Pause,
- Warnung bei mehr als 8 Stunden täglicher Arbeitszeit,
- Eskalation bei mehr als 10 Stunden täglicher Arbeitszeit,
- Warnung bei weniger als 11 Stunden Ruhezeit bis zum nächsten Arbeitsbeginn.

Diese Prüfhilfen sind fachliche Indikatoren und ersetzen keine juristische Einzelfallbewertung.[cite:5]

Sollte der Gesetzgeber ergänzend eine wöchentliche Höchstarbeitszeit oder abweichende Prüfmaßstäbe einführen, können die fachlichen Prüfhilfen um entsprechende Wochenprüfungen ergänzt werden, ohne die bestehenden Tagesprüfungen zu verändern.

## 11. Prüfstatus

Folgende fachliche Zustände werden im System unterschieden. Sie sind die verbindliche Grundlage für Pflichtauswertungen, Berichte und normierte Hinweistexte.[cite:5]

**Buchungsstatus** (technisch: `BookingStatus`-Enum auf der Buchungsentität):

- `OK`
- `OPEN`
- `WARN`
- `NEEDS_REVIEW`
- `CORRECTED`
- `CLOSED_WITH_NOTE`

**Fachliche Hinweislagen und Herkunftskennzeichnung** — diese werden im System *nicht* als `BookingStatus`-Werte implementiert, sondern orthogonal modelliert (s. u.):

- `POSSIBLE_BREAK_VIOLATION`
- `POSSIBLE_REST_VIOLATION`
- `POSSIBLE_MAX_HOURS_VIOLATION`
- `MANUAL_ENTRY`

Die nachfolgend genannten fachlichen Hinweislagen `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION` und `MANUAL_ENTRY` werden im System nicht als Werte der Enum `BookingStatus` implementiert. Stattdessen erfolgt die Modellierung orthogonal: `POSSIBLE_…` als `ReviewCaseType` auf `ReviewCase`-Datensätzen, `MANUAL_ENTRY` als `BookingSource.MANUAL` auf der `TimeBooking` — kombinierbar mit jedem Buchungsstatus. Diese Trennung ist fachlich präziser und ermöglicht die konsistente Ableitung in Berichten und Pflichtauswertungen.

## 12. Korrekturen

Korrekturen sind zulässig, aber immer begründungspflichtig. Sie müssen alten Zustand, neuen Zustand, Begründung, korrigierende Person und Zeitstempel dokumentieren.[cite:5]

Korrekturen müssen in Pflichtauswertungen mit altem Zustand, neuem Zustand, Begründung, korrigierender Person und Zeitstempel nachvollziehbar ausweisbar sein.[cite:5]

## 13. Nachträge

Notfall- oder Nachtragsbuchungen müssen ausdrücklich als Nachtrag gekennzeichnet werden. Sie dürfen nicht als normale Echtzeitbuchung erscheinen.[cite:5]

Nachträge müssen in Pflichtauswertungen gesondert ausweisbar und als Nachtrag erkennbar sein.[cite:5]

## 14. Regel bei vergessenem Ausloggen

Wenn `Kommen` ohne `Gehen` bleibt, dann:

1. bleibt der Zustand offen,
2. nach Regelende wird gewarnt,
3. der Fall erhält mindestens `OPEN` oder `NEEDS_REVIEW`,
4. Klärung erfolgt administrativ,
5. Korrektur oder Nachtrag wird begründet dokumentiert.

Eine automatische endgültige `Gehen`-Buchung ist nicht zulässig.[cite:5]

## 15. Regel bei vergessener Pause

Wenn `Pause Start` ohne `Pause Ende` bleibt, wird analog verfahren:

- offener Status,
- Warnung,
- Prüfbedarf,
- dokumentierte Klärung.

## 16. Rollen- und Rechteprinzip

Mitarbeiter dürfen buchen. Admins dürfen Benutzer, Karten und Regelzeiten pflegen. Prüfer dürfen offene und auffällige Fälle bewerten. Technische Betreuung darf Backup, Restore und Systembetrieb verantworten.[cite:5]

Rechte dürfen nicht ungeprüft vermischt werden. Die Rollen- und Rechtevergabe ist Bestandteil des Praxis-IT-Sicherheitskonzepts und muss dort dokumentiert und regelmäßig überprüft werden.

## 17. Datenschutzregel

Es dürfen nur erforderliche Beschäftigtendaten verarbeitet werden. Zugriffe auf Datenbank, Berichte, Pflichtauswertungen, Export und Backup sind auf berechtigte Personen zu beschränken.[cite:5]

Die produktive Verarbeitung von Arbeitszeitdaten erfolgt ausschließlich lokal in der Praxisumgebung. Eine Verarbeitung oder Auswertung von Arbeitszeitdaten in externen Cloud-Diensten ist nicht zulässig. Cloud-Speicher dürfen ausschließlich als verschlüsselte Backup-Medien genutzt werden, sofern hierfür die datenschutzrechtlichen Vorgaben, insbesondere Auftragsverarbeitung und technische sowie organisatorische Maßnahmen, erfüllt sind.

## 18. Aufbewahrung und Löschung

Arbeitszeitdaten sind mindestens 2 Jahre aufzubewahren. Fachlich relevante Buchungen werden im Normalfall nicht physisch gelöscht, sondern durch Status, Korrektur oder Archivierung behandelt.[cite:5]

Berichte, Pflichtauswertungen und Exportdateien sind nach dem festgelegten Archivierungs- und Löschkonzept zu behandeln.[cite:5]

Das Archivierungs- und Löschkonzept umfasst auch Backups und Backup-Generationen (Rotationskonzept). Alte Sicherungen sind nach den festgelegten Fristen zu überschreiben oder zu löschen, wobei gesetzliche Aufbewahrungsfristen zu beachten sind.

## 19. Fallback-Regel

Bei Reader-, Terminal- oder Stromausfall gilt ein Notfallprozess mit manueller Erfassung und späterem gekennzeichnetem Nachtrag. Jeder Nachtrag ist begründungspflichtig.[cite:5]

## 20. Backup- und Restore-Regel

Backups sind regelmäßig zu erstellen. Restore darf nur berechtigt durchgeführt werden und muss protokolliert sowie regelmäßig testweise geprüft werden.[cite:5]

Backups werden primär lokal, zum Beispiel auf einem Praxis-NAS, gespeichert. Eine zusätzliche Ablage verschlüsselter Backups in einem externen Cloud-Speicher ist zulässig, sofern die Verschlüsselung vor Verlassen der Praxisumgebung erfolgt und der Cloud-Speicher ausschließlich als technisches Backup-Medium dient.

Soweit Berichte, Pflichtauswertungen oder Exportdateien Bestandteil des festgelegten Sicherungskonzepts sind, sind auch diese in Backup- und Restore-Prüfungen einzubeziehen.

## 21. Zeitregel

Die Systemzeit muss zuverlässig synchronisiert sein. Zeitsprünge oder manuelle Uhrzeitänderungen sind zu protokollieren und fachlich zu prüfen.[cite:5]

## 22. Prüfintervalle

Mindestens empfohlen sind:

- tägliche Prüfung offener Fälle anhand der Pflichtauswertungen,
- wöchentliche Prüfung möglicher Verstöße anhand der Pflichtauswertungen,
- regelmäßige Prüfung von Korrekturen und Nachträgen anhand der Pflichtauswertungen,
- regelmäßige Backup- und Restore-Kontrolle.

## 23. Leitregel

> Reale Buchungen haben Vorrang. Auffälligkeiten werden erkannt, dokumentiert und administrativ geklärt. Korrekturen, Nachträge und Regeländerungen müssen jederzeit nachvollziehbar bleiben. Fachliche Zustände müssen auch in Berichten und Pflichtauswertungen konsistent nachvollziehbar sein.[cite:5]

## 24. Versionshistorie

- **Version 4 (2026-06-10):** Präzisierung der Backup- und Restore-Regeln (lokal und optional verschlüsselte Cloud-Backups), Ergänzung zur Einbindung in das Praxis-IT-Sicherheitskonzept, Klarstellung zur ausschließlich lokalen produktiven Verarbeitung sowie Ergänzung zur möglichen zukünftigen Erweiterung um Wochenprüfungen bei unverändertem Tagesprüfungsstand.
- **Version 3:** Ursprüngliche konsolidierte Fassung der Betriebs-, Prüf-, Korrektur- und Administrationsregeln.
