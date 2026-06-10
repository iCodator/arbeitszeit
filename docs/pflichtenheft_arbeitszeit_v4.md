# Pflichtenheft Projekt arbeitszeit – Version 4

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
- Arbeitsschutzgesetz (ArbSchG), insbesondere § 3 Abs. 1 und Abs. 2 Nr. 1, als Grundlage der Pflicht des Arbeitgebers, geeignete organisatorische Maßnahmen zum Schutz der Beschäftigten zu treffen (einschließlich eines Systems zur Arbeitszeiterfassung),[^ArbSchG]
- Datenschutzrecht für Beschäftigtendaten.[^5][^6][^7]

Für den Betrieb in einer Zahnarztpraxis ist zusätzlich die IT-Sicherheitsrichtlinie nach § 75b SGB V in der jeweils gültigen Fassung zu beachten. Die dort geforderten technischen und organisatorischen Maßnahmen zur IT-Sicherheit (z.B. Benutzer- und Rechteverwaltung, Backup-Konzept, Protokollierung, Schutz der Praxis-IT) sind bei der Einführung und dem Betrieb des Systems zu berücksichtigen.[^ITSICHER]

## 5. Nutzerrollen

Mindestens folgende Rollen sind vorzusehen:

- Mitarbeiter,
- Admin,
- Prüfer,
- technische Betreuung.

Die Rechte dieser Rollen sind verbindlich zu trennen. Ein Mitarbeiter darf keine administrativen Änderungen an Benutzern, Karten, Regelzeiten oder Korrekturen ausführen.

## 6. Normalablauf der Zeiterfassung

Der verbindliche Standardablauf ist:

1. Buchungsart am USB-Numpad wählen.
2. RFID-Chip an den Reader halten.
3. RFID-ID einlesen.
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

### 7.5 Offene Buchungen

Das System muss offene Buchungen erkennen und kennzeichnen. Eine offene Buchung darf nicht automatisch in eine endgültige künstliche Abschlussbuchung umgewandelt werden.

### 7.6 Prüfstatus

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

### 7.7 Korrekturen und Nachträge

Das System muss Korrekturen und Nachträge unterscheiden können. Korrekturen und Nachträge müssen jeweils begründet und protokolliert werden.

### 7.8 Regelarbeitszeiten

Das System muss die Regelarbeitszeiten pro Wochentag verwalten und administrativ änderbar machen. Änderungen müssen in der Datenbank gespeichert und protokolliert werden.

Die initialen Zeiten sind:

| Tag        | Beginn | Ende  |
|-----------|-------:|------:|
| Montag    | 07:30  | 18:00 |
| Dienstag  | 07:30  | 18:00 |
| Mittwoch  | 07:30  | 18:00 |
| Donnerstag| 07:30  | 14:00 |
| Freitag   | 07:30  | 16:00 |

### 7.9 Prüflogik Arbeitszeitgesetz

Das System muss Prüfhinweise für folgende Sachverhalte auf Basis der derzeit geltenden Regelungen des Arbeitszeitgesetzes (ArbZG) erzeugen können:

- mehr als 6 Stunden ohne Pause,[^3]
- mehr als 9 Stunden ohne ausreichende Gesamtpause,[^3]
- mehr als 8 Stunden werktägliche Arbeitszeit,[^2]
- mehr als 10 Stunden tägliche Arbeitszeit,[^2]
- Unterschreitung der 11-stündigen Ruhezeit zwischen zwei Arbeitstagen.[^4]

Diese Prüfungen erzeugen Warnungen oder Prüfstatus, ersetzen aber keine juristische Einzelfallprüfung.

Die oben genannten Prüfungen orientieren sich an der derzeit geltenden Rechtslage nach Arbeitszeitgesetz (ArbZG) und den dazu ergangenen Entscheidungen. Sollten künftig ergänzende oder abweichende gesetzliche Vorgaben insbesondere zur wöchentlichen Höchstarbeitszeit in Kraft treten, ist das System so ausgelegt, dass zusätzlich entsprechende Wochenprüfungen implementiert werden können (z.B. durchschnittliche Wochenarbeitszeit gemäß neuer gesetzlicher Vorgaben).

### 7.10 Selbsttest

Das System muss Konfiguration, Geräteverfügbarkeit, NAS-Erreichbarkeit, Datenbankerreichbarkeit und Grundkonsistenz prüfen können.

### 7.11 Export

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

### 7.12 Pflichtauswertungen

Das System muss Pflichtauswertungen bereitstellen, mit denen offene, auffällige, korrigierte und nachgetragene Sachverhalte gezielt geprüft und nachvollzogen werden können. Die Auswertungen müssen nach Zeitraum und Mitarbeiter filterbar sein und sowohl in der Anwendung einsehbar als auch exportierbar sein.

Mindestens folgende Pflichtauswertungen sind vorzusehen:

- offene Buchungen und offene Pausen,
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

### 8.3 Resilienz

Das System muss transaktionssicher schreiben, Wiederanlauf nach Störungen ermöglichen und ein geordnetes Backup-/Restore-Verfahren vorsehen.

### 8.4 Datensparsamkeit

Es dürfen nur die für Zeiterfassung, Prüfung, Korrektur, Nachweis und Verwaltung erforderlichen Daten verarbeitet werden.[^5][^6][^7]

## 9. Technische Anforderungen

### 9.1 Plattform

Zielplattform ist Lubuntu oder ein vergleichbares Linux-System auf einem dedizierten Terminalgerät.

### 9.2 Komponenten

Erforderlich sind mindestens:

- Python 3,
- SQLite,
- RFID-Reader,
- separates USB-Numpad,
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

Die Verarbeitung der Arbeitszeitdaten erfolgt ausschließlich lokal auf der Praxis-IT-Infrastruktur. Es findet keine produktive Verarbeitung oder Auswertung von Arbeitszeitdaten in externen Rechenzentren oder Cloud-Diensten statt.

Für Zwecke der Datensicherung werden verschlüsselte Backups erstellt. Diese werden lokal (z.B. auf einem NAS) und optional zusätzlich in einem externen Cloud-Speicher abgelegt. Vor der Übertragung in einen Cloud-Speicher werden sämtliche Backup-Daten clientseitig mit einem in der Praxis verwalteten Schlüssel verschlüsselt. Der Cloud-Speicher dient ausschließlich als technisches Backup-Medium; ein Zugriff auf personenbezogene Arbeitszeitdaten in entschlüsselter Form findet außerhalb der Praxis-IT nicht statt.

Wird ein externer Cloud-Speicher für Backups genutzt, so ist der Cloud-Anbieter als Auftragsverarbeiter gemäß Art. 28 DSGVO vertraglich zu binden. Serverstandorte, technische und organisatorische Maßnahmen (TOM) des Anbieters sowie das Lösch- bzw. Rotationskonzept sind in der Datenschutzdokumentation der Praxis festzuhalten.

## 12. Aufbewahrung, Archivierung und Löschung

Arbeitszeitdaten müssen mindestens 2 Jahre aufbewahrt werden.[^8] Technische Protokolle, Backups und Exportdateien sind nach einem definierten Archivierungs- und Löschkonzept zu behandeln.

Eine physische Löschung fachlich relevanter Buchungen darf im Normalfall nicht erfolgen; stattdessen sind Status- und Korrekturmechanismen zu verwenden.

Das Backup-Konzept muss so gestaltet sein, dass gesetzliche Aufbewahrungsfristen und Löschpflichten (einschließlich der Grundsätze der Datenminimierung und Speicherbegrenzung nach Art. 5 DSGVO) eingehalten werden können. Hierzu ist ein Rotationskonzept für Backups vorzusehen, in dem definiert wird, nach welchen Zeiträumen Sicherungen überschrieben oder gelöscht werden. Backups werden ausschließlich zu Wiederherstellungszwecken genutzt und nicht produktiv ausgewertet.

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
- wie oft Backups und Restore getestet werden,
- wie das System in das IT-Sicherheitskonzept der Praxis nach § 75b SGB V (IT-Sicherheitsrichtlinie) eingebunden ist (insbesondere Benutzer- und Rechteverwaltung, Backup-Konzept, Protokollierung und physische/technische Schutzmaßnahmen).

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
- Auswertung offener und auffälliger Fälle.

## 17. Abnahmekriterien

Das System ist nur dann abnahmefähig, wenn zusätzlich zu den bisherigen Kriterien auch diese Punkte nachweisbar erfüllt sind:

- gesetzlich relevante Prüfhilfen für Pause, Ruhezeit und Höchstarbeitszeit funktionieren,[^2][^3][^4]
- Rollen und Rechte sind organisatorisch definiert,
- Aufbewahrungs- und Löschkonzept ist schriftlich festgelegt,
- Fallback-Prozess ist dokumentiert,
- Restore wurde praktisch getestet,
- offene und auffällige Fälle sind auswertbar.

## 18. Versionshistorie

- Version 4 (2026-06-10): Ergänzung zu Arbeitsschutzgesetz (ArbSchG) als Grundlage der Zeiterfassungspflicht, Klarstellung der Prüflogik zu Tages- und möglichen künftigen Wochenprüfungen, Konkretisierung der Datenschutz- und Backup-Anforderungen (lokale Verarbeitung, verschlüsselte Backups lokal und in der Cloud, Auftragsverarbeitung nach Art. 28 DSGVO) sowie Einbindung in das IT-Sicherheitskonzept nach § 75b SGB V.
- Version 3: Erste konsolidierte Fassung der fachlichen und rechtlichen Anforderungen.

## Fußnoten

[^1]: Bundesarbeitsgericht, Beschluss vom 13.09.2022 – 1 ABR 22/21; ergänzend EuGH, Urteil vom 14.05.2019 – C-55/18, zur Pflicht eines objektiven, verlässlichen und zugänglichen Systems zur Arbeitszeiterfassung.
[^2]: Arbeitszeitgesetz (ArbZG) § 3 Arbeitszeit der Arbeitnehmer, <https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html>.
[^3]: Arbeitszeitgesetz (ArbZG) § 4 Ruhepausen, <https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html>.
[^4]: Arbeitszeitgesetz (ArbZG) § 5 Ruhezeit, <https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html>.
[^5]: DSGVO Art. 5 Grundsätze für die Verarbeitung personenbezogener Daten.
[^6]: DSGVO Art. 32 Sicherheit der Verarbeitung.
[^7]: Bundesdatenschutzgesetz (BDSG) § 26 Datenverarbeitung für Zwecke des Beschäftigungsverhältnisses, <https://www.gesetze-im-internet.de/bdsg_2018/__26.html>.
[^8]: Arbeitszeitgesetz (ArbZG) § 16 Aushang und Arbeitszeitnachweise, <https://www.gesetze-im-internet.de/arbzg/__16.html>.
[^ArbSchG]: Arbeitsschutzgesetz (ArbSchG) § 3 Grundpflichten des Arbeitgebers, insbesondere Abs. 1 und Abs. 2 Nr. 1 (Organisation der Maßnahmen des Arbeitsschutzes).
[^ITSICHER]: IT-Sicherheitsrichtlinie für Arzt- und Zahnarztpraxen nach § 75b SGB V in der jeweils gültigen Fassung (KBV/KZBV).