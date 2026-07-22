# Pflichtenheft Projekt arbeitszeit

| Feld | Wert |
| --- | --- |
| Version | 6.1 |
| Stand | 2026-07-22 |
| Status | aktiv |
| Ablöst | pflichtenheft_arbeitszeit_v6.md |
| Verantwortlich | Praxisleitung / technische Betreuung |

## 1. Dokumentzweck

Dieses Pflichtenheft beschreibt die verbindlichen fachlichen, technischen, organisatorischen, datenschutzbezogenen und betrieblichen Anforderungen an das Projekt **arbeitszeit**. Es dient als Arbeits- und Abnahmegrundlage für Entwicklung, Einführung, Betrieb, Prüfung und Weiterentwicklung des Systems.

## 2. Ziel des Systems

**arbeitszeit** ist ein lokales elektronisches Zeiterfassungssystem für eine Zahnarztpraxis. Es soll Arbeitszeitdaten objektiv, verlässlich und zugänglich erfassen und für die Praxis nachvollziehbar auswertbar machen.[^1]

Das System soll echte Buchungen dokumentieren, Auffälligkeiten erkennen, gesetzlich relevante Prüffälle kennzeichnen und berechtigten Personen nachvollziehbare Korrekturen ermöglichen.

## 3. Geltungsbereich

Das System dient der Zeiterfassung von Beschäftigten der Zahnarztpraxis. Nicht Gegenstand des Systems sind Lohnabrechnung, Urlaubsplanung, Dienstplanung oder vollständige Personalverwaltung.

## 4. Rechts- und Regelrahmen

Das System muss so ausgestaltet sein, dass ein objektives, verlässliches und zugängliches Arbeitszeiterfassungssystem unterstützt wird.[^1] Zusätzlich muss die Praxis mit Hilfe des Systems die Einhaltung von Vorgaben zu Höchstarbeitszeit, Ruhepausen und Ruhezeit überwachen können.[^2][^3][^4]

Für das Projekt sind insbesondere relevant:

- Pflicht zur Arbeitszeiterfassung,[^1]
- Arbeitszeitgesetz zu Höchstarbeitszeit, Ruhepausen und Ruhezeit,[^2][^3][^4]
- Datenschutzrecht für Beschäftigtendaten.[^5][^6][^7]

Zum Zeitpunkt der Erstellung dieses Dokuments liegt ein Referentenentwurf zur Novellierung des Arbeitszeitgesetzes vor, der u. a. eine grundsätzlich elektronische Erfassungspflicht sowie ergänzende Aufbewahrungs- und Auskunftsregelungen vorsieht. Dieser Entwurf ist noch nicht in Kraft getreten; der vorliegende Rechts- und Regelrahmen ist bei Verabschiedung einer entsprechenden Gesetzesänderung zu aktualisieren.[^9]

## 5. Nutzerrollen

Mindestens folgende Rollen sind vorzusehen:

- Mitarbeiter,
- Admin,
- Prüfer,
- technische Betreuung.

Die Rechte dieser Rollen sind verbindlich zu trennen. Ein Mitarbeiter darf keine administrativen Änderungen an Benutzern, Karten, Regelzeiten oder Korrekturen ausführen.

## 6. Normalablauf der Zeiterfassung

Der verbindliche Standardablauf ist:

1. RFID-Chip an den Reader halten.
2. RFID-ID einlesen.
3. Buchungstyp anhand der Scanreihenfolge im Tagesablauf ableiten.
4. Karte und Benutzer prüfen.
5. Buchungsfolge prüfen.
6. Buchung speichern oder verwerfen.
7. Prüfstatus setzen, wenn erforderlich.
8. Export und Backup optional aktualisieren.

## 7. Funktionale Kernanforderungen

### 7.1 Buchungsarten

Das System muss mindestens diese Buchungsarten unterstützen:

- `Kommen`
- `Gehen`
- `Pause Start`
- `Pause Ende`

### 7.2 Erfassung von Beginn, Ende und Dauer

Das System muss Beginn und Ende der Arbeitszeit sowie Unterbrechungen erfassen. Die Dauer der täglichen Arbeitszeit muss aus den gespeicherten Daten nachvollziehbar und auswertbar ableitbar sein.[^1]

### 7.3 RFID-Zuordnung

RFID-Karten müssen aktiv, bekannt und einem aktiven Benutzer zugeordnet sein. Unbekannte oder inaktive Karten dürfen keine reguläre Buchung auslösen.

### 7.4 Plausibilitätsprüfung

Das System muss unplausible Buchungsfolgen erkennen und verwerfen oder mindestens als auffällig markieren.

Das System muss Mehrfacherfassungen derselben RFID-Karte innerhalb kurzer Zeit erkennen und verwerfen (Doppel-Scan-Schutz).

### 7.5 Kurztag-Regelung

Bei Schichten von bis zu 6 Stunden ist nach § 4 ArbZG keine Ruhepause erforderlich.[^3] Das System muss diese Regelung bei der Buchungstyp-Ableitung berücksichtigen: Beträgt die bis zum zweiten Scan verstrichene Zeit höchstens 6 Stunden, gilt dieser Scan als Gehen-Buchung. Ein dritter Scan innerhalb desselben Arbeitstages ist in diesem Fall als ungültig abzuweisen.

### 7.6 Offene Buchungen

Das System muss offene Buchungen erkennen und kennzeichnen. Eine offene Buchung darf nicht automatisch in eine endgültige künstliche Abschlussbuchung umgewandelt werden.

### 7.7 Prüfstatus

Buchungen und Prüffälle müssen mindestens folgende Statuswerte nutzen können:

- `OK`
- `OPEN`
- `WARN`
- `NEEDS_REVIEW`
- `CORRECTED`
- `CLOSED_WITH_NOTE`

Zusätzlich sollen Kennzeichnungen für mögliche gesetzliche Verstöße vorgesehen werden, z.B.:

- `POSSIBLE_BREAK_VIOLATION`
- `POSSIBLE_REST_VIOLATION`
- `POSSIBLE_MAX_HOURS_VIOLATION`

### 7.8 Korrekturen und Nachträge

Das System muss Korrekturen und Nachträge unterscheiden können. Korrekturen und Nachträge müssen jeweils begründet und protokolliert werden.

### 7.9 Regelarbeitszeiten

Das System muss die Regelarbeitszeiten pro Wochentag verwalten und administrativ änderbar machen. Änderungen müssen in der Datenbank gespeichert und protokolliert werden.

Die initialen Zeiten sind:

| Tag | Beginn | Ende |
|---|---:|---:|
| Montag | 07:30 | 18:00 |
| Dienstag | 07:30 | 18:00 |
| Mittwoch | 07:30 | 18:00 |
| Donnerstag | 07:30 | 14:00 |
| Freitag | 07:30 | 16:00 |

### 7.10 Benutzer- und Rollenverwaltung

Das System muss die lokale Verwaltung von Benutzerkonten für administrative und prüfende Rollen unterstützen.

Benutzerkonten müssen mindestens für die Rollen `ADMIN`, `REVIEWER` und `TECH` anlegbar, aktivierbar, deaktivierbar und änderbar sein.

Die Verwaltung dieser Benutzerkonten muss über eine lokale Admin-CLI möglich sein; direkte SQL-Eingriffe dürfen kein regulärer Betriebsprozess sein.

Für jedes Benutzerkonto müssen mindestens Benutzername, Rolle, Aktivstatus, Passwort-Hash und optional eine Verknüpfung zu einem Mitarbeiterdatensatz verwaltet werden.

Die zulässigen Rollenwerte müssen mindestens `ADMIN`, `REVIEWER` und `TECH` umfassen; die Rechte dieser Rollen sind verbindlich zu trennen.

Das System muss einen dokumentierten Bootstrap-Prozess zur erstmaligen Einrichtung eines ersten aktiven Administratorkontos vorsehen. Dieser Bootstrap-Prozess darf nur nutzbar sein, solange noch kein aktives Administratorkonto vorhanden ist.

Änderungen an Benutzerkonten, Rollen und Aktivstatus müssen revisionssicher protokolliert werden.

Die Rechteprüfung für Benutzer- und Rollenverwaltung muss technisch in der Anwendung erzwungen werden und darf nicht nur organisatorisch beschrieben sein.

### 7.11 Prüflogik Arbeitszeitgesetz

Das System muss Prüfhinweise für folgende Sachverhalte erzeugen können:

- mehr als 6 Stunden ohne Pause,[^3]
- mehr als 9 Stunden ohne ausreichende Gesamtpause,[^3]
- mehr als 8 Stunden werktägliche Arbeitszeit,[^2]
- mehr als 10 Stunden tägliche Arbeitszeit,[^2]
- Unterschreitung der 11-stündigen Ruhezeit zwischen zwei Arbeitstagen.[^4]

Diese Prüfungen erzeugen Warnungen oder Prüfstatus, ersetzen aber keine juristische Einzelfallprüfung.

### 7.12 Selbsttest

Das System muss Konfiguration, Geräteverfügbarkeit, NAS-Erreichbarkeit, Datenbankerreichbarkeit und Grundkonsistenz prüfen können.

### 7.13 Export

Das System muss Export- und Berichtsfunktionen für Gesamt, Tag, Woche, Monat und einzelne Mitarbeiter bereitstellen. Es muss dabei mindestens CSV-Exporte für die Weiterverarbeitung sowie PDF-Berichte für druckbare Auswertungen erzeugen können.

Mindestens folgende Anforderungen sind vorzusehen:

- CSV-Exporte für detaillierte Buchungsdaten sowie für verdichtete Tages-, Wochen- und Monatsauswertungen.
- PDF-Berichte für Tages-, Wochen- und Monatsauswertungen sowie für einzelne Mitarbeiter.
- Angabe von Zeitraum, Erstellungszeitpunkt und eindeutiger Zuordnung zu Mitarbeiter oder Praxis in jedem Export oder Bericht.
- In detaillierten Exporten mindestens: Mitarbeiterkennung oder Mitarbeitername, Datum, Uhrzeit, Buchungsart, ableitbare Dauer, Status, Kennzeichnung von Korrekturen oder Nachträgen sowie relevante Prüfflags.
- In verdichteten Berichten mindestens: summierte Arbeitszeit, Anzahl und Dauer der Pausen, Anzahl offener Buchungen, Anzahl von Warn- und Prüfstatus sowie Anzahl von Korrekturen und Nachträgen im jeweiligen Zeitraum.
- In PDF-Berichten zusätzlich kurze erläuternde Hinweise zu offenen Buchungen, Korrekturen, Nachträgen und relevanten Prüfhinweisen, ohne die tabellarische Lesbarkeit zu beeinträchtigen.
- Nachvollziehbare Benennung und Ablage der Exportdateien in einem definierten Exportverzeichnis.
- Einbeziehung der Exportdateien in das Schutz-, Backup- und Archivierungskonzept.

### 7.14 Pflichtauswertungen

Das System muss Pflichtauswertungen bereitstellen, mit denen offene, auffällige, korrigierte und nachgetragene Sachverhalte gezielt geprüft und nachvollzogen werden können. Die Auswertungen müssen nach Zeitraum und Mitarbeiter filterbar sein und sowohl in der Anwendung einsehbar als auch exportierbar sein.

Mindestens folgende Pflichtauswertungen sind vorzusehen:

- offene Buchungen und offene Pausen,
- offene Vortagsschichten (vergessene Abmeldung am Vortag),
- Korrekturen mit Bezug auf alten und neuen Zustand, Begründung, korrigierende Person und Zeitstempel,
- Nachträge mit Kennzeichnung als nachträglich erfasster Datensatz, Begründung und Freigabebezug, soweit vorgesehen,
- mögliche Pausenverstöße,
- mögliche Ruhezeitverstöße,
- mögliche Überschreitungen der täglichen Arbeitszeit,
- Buchungen außerhalb des Regelzeitfensters,
- Buchungen und Vorgänge mit Warn- oder Prüfstatus.

Die Pflichtauswertungen müssen mindestens den betroffenen Mitarbeiter, Datum oder Zeitraum, den jeweiligen Prüf- oder Statusgrund sowie den aktuellen Bearbeitungs- oder Klärungsstand enthalten. Sie müssen so gestaltet sein, dass berechtigte Personen offene und auffällige Fälle regelmäßig prüfen, dokumentieren und nachverfolgen können.

## 8. Nichtfunktionale Anforderungen

### 8.1 Robustheit

Das System muss auch bei Gerätefehlern, NAS-Ausfall und Bedienfehlern ohne stillen Datenverlust arbeiten.

### 8.2 Nachvollziehbarkeit

Alle relevanten Ereignisse, Warnungen, Korrekturen, Regelzeitänderungen und Administrationsvorgänge müssen protokolliert werden.

Als relevante Administrationsvorgänge gelten insbesondere das Anlegen, Ändern, Aktivieren, Deaktivieren und Rollenwechseln von Benutzerkonten sowie die erstmalige Einrichtung eines Administratorkontos.

### 8.3 Resilienz

Das System muss transaktionssicher schreiben, Wiederanlauf nach Störungen ermöglichen und ein geordnetes Backup-/Restore-Verfahren vorsehen.

### 8.4 Datensparsamkeit

Es dürfen nur die für Zeiterfassung, Prüfung, Korrektur, Nachweis und Verwaltung erforderlichen Daten verarbeitet werden.[^5][^7]

## 9. Technische Anforderungen

### 9.1 Plattform

Zielplattform ist Lubuntu oder ein vergleichbares Linux-System auf einem dedizierten Terminalgerät.

### 9.2 Komponenten

Erforderlich sind mindestens:

- Python 3,
- SQLite,
- RFID-Reader,
- optionale NAS-Anbindung,
- Bibliothek `evdev`,
- eine geeignete Komponente zur Erzeugung von PDF-Berichten.

### 9.3 Systemzeit

Die Systemzeit muss zuverlässig synchronisiert werden, z.B. per NTP. Manuelle Zeitänderungen oder erkannte Zeitsprünge müssen protokolliert werden.

### 9.4 Energieverhalten

Das System soll im Betrieb nicht in Suspend wechseln. Der Bildschirm darf abgeschaltet werden, der Rechner muss aber sofort buchungsbereit bleiben.

## 10. Datenmodell

Das Datenmodell muss mindestens folgende Tabellen oder gleichwertige Strukturen abbilden:

- Benutzer,
- RFID-Karten,
- Buchungen,
- Buchungskorrekturen,
- Nachträge,
- Prüfstatus oder Prüffälle,
- Regelarbeitszeiten,
- Systemkonfiguration,
- Audit-Log.

## 11. Datenschutz und Zugriffsschutz

Das System verarbeitet Beschäftigtendaten und muss deshalb organisatorisch und technisch geschützt werden.[^5][^6][^7]

Es sind mindestens vorzusehen:

- Rollen- und Rechtekonzept,
- Schutz der Datenbankdatei,
- Schutz der Exportverzeichnisse,
- Schutz der NAS-Backups,
- restriktiver Zugriff auf Admin-Befehle.

Der Zugriff auf Befehle zur Benutzer- und Rollenverwaltung ist auf berechtigte Benutzer mit Administrationsrolle zu beschränken. Rollen dürfen nur über definierte Anwendungsfunktionen geändert werden.

## 12. Aufbewahrung, Archivierung und Löschung

Arbeitszeitdaten müssen mindestens 2 Jahre aufbewahrt werden. Für die über die werktägliche Arbeitszeit hinausgehende (Mehr-)Arbeitszeit ergibt sich diese Frist unmittelbar aus § 16 Abs. 2 ArbZG;[^8] für die übrige, im Rahmen der Zeiterfassungspflicht zu dokumentierende Arbeitszeit wird dieselbe Frist als Vorsorgemaßnahme im Sinne der Nachweispflicht zugrunde gelegt.[^1] Technische Protokolle, Backups und Exportdateien sind nach einem definierten Archivierungs- und Löschkonzept zu behandeln.

Eine physische Löschung fachlich relevanter Buchungen darf im Normalfall nicht erfolgen; stattdessen sind Status- und Korrekturmechanismen zu verwenden.

## 13. Fallback- und Notfallbetrieb

Für Geräteausfall oder Terminalausfall muss ein Notfallverfahren vorgesehen werden. Dieses muss mindestens umfassen:

- manuelle Noterfassung,
- späteren Nachtrag als gekennzeichneten Datensatz,
- Begründungspflicht,
- Prüfung und Freigabe durch berechtigte Person.

## 14. Backup und Restore

Backups auf NAS müssen möglich sein. Restore-Vorgänge müssen definiert, protokolliert und regelmäßig testweise geprüft werden.

## 15. Organisatorische Anforderungen

Die Praxis muss verbindlich festlegen:

- wer Admin ist,
- wer Prüfer ist,
- wer Regelarbeitszeiten ändern darf,
- wer Korrekturen freigibt,
- wer Nachträge eingeben darf,
- wie oft offene Fälle geprüft werden,
- wie oft mögliche Verstöße kontrolliert werden,
- wie oft Backups und Restore getestet werden.

## 16. Testanforderungen

Zusätzlich zu den bisherigen Tests müssen mindestens diese Szenarien geprüft werden:

- mehr als 6 Stunden ohne Pause,
- mehr als 9 Stunden ohne ausreichende Pause,
- Arbeitszeit über 8 Stunden,
- Arbeitszeit über 10 Stunden,
- Unterschreitung der Ruhezeit,
- Systemzeitabweichung,
- Notfallnachtrag,
- Restore-Test mit echtem Backup,
- Auswertung offener und auffälliger Fälle,
- erstmalige Einrichtung eines ersten Administratorkontos über den definierten Bootstrap-Prozess,
- Anlegen eines Benutzerkontos mit Rolle `REVIEWER`,
- Anlegen eines Benutzerkontos mit Rolle `TECH`,
- Zurückweisung ungültiger Rollenwerte,
- Zurückweisung doppelter Benutzernamen,
- Deaktivierung und Reaktivierung eines Benutzerkontos,
- Rollenwechsel eines bestehenden Benutzerkontos,
- Zugriffsschutz: Nicht-Administratoren dürfen keine Benutzer- oder Rollenänderung ausführen,
- Protokollnachweis im Audit-Log für Anlage, Änderung, Deaktivierung und Rollenwechsel.

## 17. Abnahmekriterien

Das System ist nur dann abnahmefähig, wenn zusätzlich zu den bisherigen Kriterien auch diese Punkte nachweisbar erfüllt sind:

- gesetzlich relevante Prüfhilfen für Pause, Ruhezeit und Höchstarbeitszeit funktionieren,[^2][^3][^4]
- Rollen und Rechte sind organisatorisch definiert,
- die Benutzer- und Rollenverwaltung für `ADMIN`, `REVIEWER` und `TECH` über die Admin-CLI funktionsfähig umgesetzt ist,
- Rollen und Rechte technisch erzwungen werden,
- der Bootstrap-Prozess für den ersten Administrator dokumentiert und praktisch testbar ist,
- alle Benutzer- und Rollenänderungen im Audit-Log nachvollziehbar nachweisbar sind,
- Aufbewahrungs- und Löschkonzept ist schriftlich festgelegt,
- Fallback-Prozess ist dokumentiert,
- Restore wurde praktisch getestet,
- offene und auffällige Fälle sind auswertbar.

## Änderungshistorie

| Version | Datum | Inhalt |
| --- | --- | --- |
| 6.1 | 2026-07-22 | § 6: Numpad-Schritt entfernt, Buchungstyp per Scanreihenfolge; § 7.4: Doppel-Scan-Schutz; neu § 7.5 Kurztag-Regelung (§ 4 ArbZG); § 7.14: offene Vortagsschichten; § 9.2: USB-Numpad entfernt |
| 6.0 | 2026-07-03 | Rechtskonformitätskorrekturen (Fußnoten, ArbSchG-Grundlage); Fußnote 9 (Referentenentwurf ArbZG-Novelle) ergänzt; Versionswechsel v5→v6 |
| 5.0 | 2026-06-11 | Benutzer- und Rollenverwaltung (§ 7.9): Bootstrap-Prozess, Audit-Log-Pflicht, Rollenwechsel; Testanforderungen und Abnahmekriterien erweitert |
| 4.0 | 2026-06-10 | Prüflogik Arbeitszeitgesetz präzisiert; IT-Sicherheitsrichtlinie ergänzt; Datenschutz-Addendum ausgegliedert |
| 3.0 | 2026-05-22 | Erstfassung als versioniertes Pflichtenheft; Rechts- und Regelrahmen, Datenmodell, Backup/Restore, Abnahmekriterien |

## Fußnoten

[^1]: Bundesarbeitsgericht, Beschluss vom 13.09.2022 – 1 ABR 22/21, hergeleitet aus § 3 Abs. 2 Nr. 1 Arbeitsschutzgesetz (ArbSchG) in unionsrechtskonformer Auslegung; ergänzend EuGH, Urteil vom 14.05.2019 – C-55/18, zur Pflicht eines objektiven, verlässlichen und zugänglichen Systems zur Arbeitszeiterfassung.
[^2]: Arbeitszeitgesetz (ArbZG) § 3 Arbeitszeit der Arbeitnehmer, [https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html](https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html).
[^3]: Arbeitszeitgesetz (ArbZG) § 4 Ruhepausen, [https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html](https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html).
[^4]: Arbeitszeitgesetz (ArbZG) § 5 Ruhezeit, [https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html](https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html).
[^5]: DSGVO Art. 5 Grundsätze für die Verarbeitung personenbezogener Daten.
[^6]: DSGVO Art. 32 Sicherheit der Verarbeitung.
[^7]: Bundesdatenschutzgesetz (BDSG) § 26 Datenverarbeitung für Zwecke des Beschäftigungsverhältnisses, [https://www.gesetze-im-internet.de/bdsg_2018/__26.html](https://www.gesetze-im-internet.de/bdsg_2018/__26.html).
[^8]: Arbeitszeitgesetz (ArbZG) § 16 Aushang und Arbeitszeitnachweise, [https://www.gesetze-im-internet.de/arbzg/__16.html](https://www.gesetze-im-internet.de/arbzg/__16.html). Die gesetzliche Aufbewahrungsfrist von mindestens zwei Jahren gilt nach dem Gesetzeswortlaut ausdrücklich für die über die werktägliche Arbeitszeit des § 3 Satz 1 ArbZG hinausgehende Arbeitszeit (Mehrarbeit) sowie für das Verzeichnis nach § 7 Abs. 7 ArbZG.
[^9]: Referentenentwurf des Bundesministeriums für Arbeit und Soziales zur Änderung des Arbeitszeitgesetzes und anderer Vorschriften, Stand Juni 2026 (noch nicht in Ressortabstimmung, Kabinettsbeschluss oder Bundestagsverfahren abgeschlossen; noch nicht geltendes Recht).
