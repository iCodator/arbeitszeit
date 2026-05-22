# Pflichtenheft Projekt arbeitszeit – Version 2

## 1. Dokumentzweck

Dieses Pflichtenheft beschreibt die verbindlichen fachlichen, technischen, organisatorischen, datenschutzbezogenen und betrieblichen Anforderungen an das Projekt **arbeitszeit**.[cite:185][cite:328][cite:333][cite:335] Es dient als Arbeits- und Abnahmegrundlage für Entwicklung, Einführung, Betrieb, Prüfung und Weiterentwicklung des Systems.[cite:185]

## 2. Ziel des Systems

**arbeitszeit** ist ein lokales elektronisches Zeiterfassungssystem für eine Zahnarztpraxis.[cite:185] Es soll Arbeitszeitdaten objektiv, verlässlich und zugänglich erfassen und für die Praxis nachvollziehbar auswertbar machen.[cite:327][cite:328]

Das System soll echte Buchungen dokumentieren, Auffälligkeiten erkennen, gesetzlich relevante Prüffälle kennzeichnen und berechtigten Personen nachvollziehbare Korrekturen ermöglichen.[cite:185][cite:333][cite:339]

## 3. Geltungsbereich

Das System dient der Zeiterfassung von Beschäftigten der Zahnarztpraxis.[cite:185] Nicht Gegenstand des Systems sind Lohnabrechnung, Urlaubsplanung, Dienstplanung oder vollständige Personalverwaltung.[cite:185]

## 4. Rechts- und Regelrahmen

Das System muss so ausgestaltet sein, dass ein objektives, verlässliches und zugängliches Arbeitszeiterfassungssystem unterstützt wird.[cite:327][cite:328] Zusätzlich muss die Praxis mit Hilfe des Systems die Einhaltung von Vorgaben zu Höchstarbeitszeit, Ruhepausen und Ruhezeit überwachen können.[cite:333][cite:336][cite:339]

Für das Projekt sind insbesondere relevant:[cite:327][cite:333][cite:335]

- Pflicht zur Arbeitszeiterfassung,[cite:327][cite:328]
- Arbeitszeitgesetz zu Höchstarbeitszeit, Ruhepausen und Ruhezeit,[cite:333][cite:336][cite:339]
- Datenschutzrecht für Beschäftigtendaten.[cite:332][cite:335]

## 5. Nutzerrollen

Mindestens folgende Rollen sind vorzusehen:[cite:185][cite:335]

- Mitarbeiter,
- Admin,
- Prüfer,
- technische Betreuung.[cite:185]

Die Rechte dieser Rollen sind verbindlich zu trennen.[cite:335] Ein Mitarbeiter darf keine administrativen Änderungen an Benutzern, Karten, Regelzeiten oder Korrekturen ausführen.[cite:185]

## 6. Normalablauf der Zeiterfassung

Der verbindliche Standardablauf ist:[cite:185]

1. Buchungsart am USB-Numpad wählen.
2. RFID-Chip an den Reader halten.[cite:186]
3. RFID-ID einlesen.
4. Karte und Benutzer prüfen.
5. Buchungsfolge prüfen.
6. Buchung speichern oder verwerfen.
7. Prüfstatus setzen, wenn erforderlich.
8. Export und Backup optional aktualisieren.[cite:185]

## 7. Funktionale Kernanforderungen

### 7.1 Buchungsarten

Das System muss mindestens diese Buchungsarten unterstützen:[cite:185]

- `Kommen`
- `Gehen`
- `Pause Start`
- `Pause Ende`

### 7.2 Erfassung von Beginn, Ende und Dauer

Das System muss Beginn und Ende der Arbeitszeit sowie Unterbrechungen erfassen.[cite:327][cite:328] Die Dauer der täglichen Arbeitszeit muss aus den gespeicherten Daten nachvollziehbar und auswertbar ableitbar sein.[cite:328]

### 7.3 RFID-Zuordnung

RFID-Karten müssen aktiv, bekannt und einem aktiven Benutzer zugeordnet sein.[cite:185] Unbekannte oder inaktive Karten dürfen keine reguläre Buchung auslösen.[cite:185]

### 7.4 Plausibilitätsprüfung

Das System muss unplausible Buchungsfolgen erkennen und verwerfen oder mindestens als auffällig markieren.[cite:185]

### 7.5 Offene Buchungen

Das System muss offene Buchungen erkennen und kennzeichnen.[cite:185] Eine offene Buchung darf nicht automatisch in eine endgültige künstliche Abschlussbuchung umgewandelt werden.[cite:185]

### 7.6 Prüfstatus

Buchungen und Prüffälle müssen mindestens folgende Statuswerte nutzen können:[cite:185]

- `OK`
- `OPEN`
- `WARN`
- `NEEDS_REVIEW`
- `CORRECTED`
- `CLOSED_WITH_NOTE`

Zusätzlich sollen Kennzeichnungen für mögliche gesetzliche Verstöße vorgesehen werden, z.B.:[cite:185][cite:333]

- `POSSIBLE_BREAK_VIOLATION`
- `POSSIBLE_REST_VIOLATION`
- `POSSIBLE_MAX_HOURS_VIOLATION`

### 7.7 Korrekturen und Nachträge

Das System muss Korrekturen und Nachträge unterscheiden können.[cite:185] Korrekturen und Nachträge müssen jeweils begründet und protokolliert werden.[cite:185]

### 7.8 Regelarbeitszeiten

Das System muss die Regelarbeitszeiten pro Wochentag verwalten und administrativ änderbar machen.[cite:185] Änderungen müssen in der Datenbank gespeichert und protokolliert werden.[cite:185]

Die initialen Zeiten sind:[cite:185]

| Tag | Beginn | Ende |
|---|---:|---:|
| Montag | 07:30 | 18:00 |
| Dienstag | 07:30 | 18:00 |
| Mittwoch | 07:30 | 18:00 |
| Donnerstag | 07:30 | 14:00 |
| Freitag | 07:30 | 16:00 |

### 7.9 Prüflogik Arbeitszeitgesetz

Das System muss Prüfhinweise für folgende Sachverhalte erzeugen können:[cite:333][cite:336][cite:339]

- mehr als 6 Stunden ohne Pause,[cite:336]
- mehr als 9 Stunden ohne ausreichende Gesamtpause,[cite:333][cite:336]
- mehr als 8 Stunden werktägliche Arbeitszeit,[cite:333][cite:339]
- mehr als 10 Stunden tägliche Arbeitszeit,[cite:333][cite:339]
- Unterschreitung der 11-stündigen Ruhezeit zwischen zwei Arbeitstagen.[cite:333][cite:339]

Diese Prüfungen erzeugen Warnungen oder Prüfstatus, ersetzen aber keine juristische Einzelfallprüfung.[cite:185]

### 7.10 Selbsttest

Das System muss Konfiguration, Geräteverfügbarkeit, NAS-Erreichbarkeit, Datenbankerreichbarkeit und Grundkonsistenz prüfen können.[cite:185]

### 7.11 Export

Das System muss Export- und Berichtsfunktionen für Gesamt, Tag, Woche, Monat und einzelne Mitarbeiter bereitstellen. Es muss dabei mindestens CSV-Exporte für die Weiterverarbeitung sowie PDF-Berichte für druckbare Auswertungen erzeugen können.[^1]

Mindestens folgende Anforderungen sind vorzusehen:[^1]

- CSV-Exporte für detaillierte Buchungsdaten sowie für verdichtete Tages-, Wochen- und Monatsauswertungen.[^1]
- PDF-Berichte für Tages-, Wochen- und Monatsauswertungen sowie für einzelne Mitarbeiter.[^1]
- Angabe von Zeitraum, Erstellungszeitpunkt und eindeutiger Zuordnung zu Mitarbeiter oder Praxis in jedem Export oder Bericht.[^1]
- In detaillierten Exporten mindestens: Mitarbeiterkennung oder Mitarbeitername, Datum, Uhrzeit, Buchungsart, ableitbare Dauer, Status, Kennzeichnung von Korrekturen oder Nachträgen sowie relevante Prüfflags.[^1]
- In verdichteten Berichten mindestens: summierte Arbeitszeit, Anzahl und Dauer der Pausen, Anzahl offener Buchungen, Anzahl von Warn- und Prüfstatus sowie Anzahl von Korrekturen und Nachträgen im jeweiligen Zeitraum.[^1]
- In PDF-Berichten zusätzlich kurze erläuternde Hinweise zu offenen Buchungen, Korrekturen, Nachträgen und relevanten Prüfhinweisen, ohne die tabellarische Lesbarkeit zu beeinträchtigen.[^2][^1]
- Nachvollziehbare Benennung und Ablage der Exportdateien in einem definierten Exportverzeichnis.[^1]
- Einbeziehung der Exportdateien in das Schutz-, Backup- und Archivierungskonzept.[^1]


### 7.12 Pflichtauswertungen

Das System muss Pflichtauswertungen bereitstellen, mit denen offene, auffällige, korrigierte und nachgetragene Sachverhalte gezielt geprüft und nachvollzogen werden können. Die Auswertungen müssen nach Zeitraum und Mitarbeiter filterbar sein und sowohl in der Anwendung einsehbar als auch exportierbar sein.[^2][^1]

Mindestens folgende Pflichtauswertungen sind vorzusehen:[^1]

- offene Buchungen und offene Pausen,[^2][^1]
- Korrekturen mit Bezug auf alten und neuen Zustand, Begründung, korrigierende Person und Zeitstempel,[^2][^1]
- Nachträge mit Kennzeichnung als nachträglich erfasster Datensatz, Begründung und Freigabebezug, soweit vorgesehen,[^2][^1]
- mögliche Pausenverstöße,[^2][^1]
- mögliche Ruhezeitverstöße,[^2][^1]
- mögliche Überschreitungen der täglichen Arbeitszeit,[^2][^1]
- Buchungen außerhalb des Regelzeitfensters,[^2][^1]
- Buchungen und Vorgänge mit Warn- oder Prüfstatus.[^2][^1]

Die Pflichtauswertungen müssen mindestens den betroffenen Mitarbeiter, Datum oder Zeitraum, den jeweiligen Prüf- oder Statusgrund sowie den aktuellen Bearbeitungs- oder Klärungsstand enthalten. Sie müssen so gestaltet sein, dass berechtigte Personen offene und auffällige Fälle regelmäßig prüfen, dokumentieren und nachverfolgen können.[^2][^1]

## 8. Nichtfunktionale Anforderungen

### 8.1 Robustheit

Das System muss auch bei Gerätefehlern, NAS-Ausfall und Bedienfehlern ohne stillen Datenverlust arbeiten.[cite:185]

### 8.2 Nachvollziehbarkeit

Alle relevanten Ereignisse, Warnungen, Korrekturen, Regelzeitänderungen und Administrationsvorgänge müssen protokolliert werden.[cite:185]

### 8.3 Resilienz

Das System muss transaktionssicher schreiben, Wiederanlauf nach Störungen ermöglichen und ein geordnetes Backup-/Restore-Verfahren vorsehen.[cite:185][cite:309]

### 8.4 Datensparsamkeit

Es dürfen nur die für Zeiterfassung, Prüfung, Korrektur, Nachweis und Verwaltung erforderlichen Daten verarbeitet werden.[cite:332][cite:335]

## 9. Technische Anforderungen

### 9.1 Plattform

Zielplattform ist Lubuntu oder ein vergleichbares Linux-System auf einem dedizierten Terminalgerät.[cite:187]
### 9.2 Komponenten

Erforderlich sind mindestens:[^1]

- Python 3,[^1]
- SQLite,[^1]
- RFID-Reader,[^1]
- separates USB-Numpad,[^1]
- optionale NAS-Anbindung,[^1]
- Bibliothek `evdev`,[^1]
- eine geeignete Komponente zur Erzeugung von PDF-Berichten.[^1]


### 9.3 Systemzeit

Die Systemzeit muss zuverlässig synchronisiert werden, z.B. per NTP.[cite:185] Manuelle Zeitänderungen oder erkannte Zeitsprünge müssen protokolliert werden.[cite:185]

### 9.4 Energieverhalten

Das System soll im Betrieb nicht in Suspend wechseln.[cite:276][cite:280] Der Bildschirm darf abgeschaltet werden, der Rechner muss aber sofort buchungsbereit bleiben.[cite:276]

## 10. Datenmodell

Das Datenmodell muss mindestens folgende Tabellen oder gleichwertige Strukturen abbilden:[cite:185]

- Benutzer,
- RFID-Karten,
- Buchungen,
- Buchungskorrekturen,
- Nachträge,
- Prüfstatus oder Prüffälle,
- Regelarbeitszeiten,
- Systemkonfiguration,
- Audit-Log.[cite:185]

## 11. Datenschutz und Zugriffsschutz

Das System verarbeitet Beschäftigtendaten und muss deshalb organisatorisch und technisch geschützt werden.[cite:332][cite:335]

Es sind mindestens vorzusehen:[cite:185][cite:335]

- Rollen- und Rechtekonzept,
- Schutz der Datenbankdatei,
- Schutz der Exportverzeichnisse,
- Schutz der NAS-Backups,
- restriktiver Zugriff auf Admin-Befehle.

## 12. Aufbewahrung, Archivierung und Löschung

Arbeitszeitdaten müssen mindestens 2 Jahre aufbewahrt werden.[cite:332] Technische Protokolle, Backups und Exportdateien sind nach einem definierten Archivierungs- und Löschkonzept zu behandeln.[cite:332][cite:335]

Eine physische Löschung fachlich relevanter Buchungen darf im Normalfall nicht erfolgen; stattdessen sind Status- und Korrekturmechanismen zu verwenden.[cite:185]

## 13. Fallback- und Notfallbetrieb

Für Geräteausfall oder Terminalausfall muss ein Notfallverfahren vorgesehen werden.[cite:185][cite:332] Dieses muss mindestens umfassen:[cite:185]

- manuelle Noterfassung,
- späteren Nachtrag als gekennzeichneten Datensatz,
- Begründungspflicht,
- Prüfung und Freigabe durch berechtigte Person.[cite:185]

## 14. Backup und Restore

Backups auf NAS müssen möglich sein.[cite:185] Restore-Vorgänge müssen definiert, protokolliert und regelmäßig testweise geprüft werden.[cite:185]

## 15. Organisatorische Anforderungen

Die Praxis muss verbindlich festlegen:[cite:185]

- wer Admin ist,
- wer Prüfer ist,
- wer Regelarbeitszeiten ändern darf,
- wer Korrekturen freigibt,
- wer Nachträge eingeben darf,
- wie oft offene Fälle geprüft werden,
- wie oft mögliche Verstöße kontrolliert werden,
- wie oft Backups und Restore getestet werden.[cite:185]

## 16. Testanforderungen

Zusätzlich zu den bisherigen Tests müssen mindestens diese Szenarien geprüft werden:[cite:185][cite:333][cite:339]

- mehr als 6 Stunden ohne Pause,
- mehr als 9 Stunden ohne ausreichende Pause,
- Arbeitszeit über 8 Stunden,
- Arbeitszeit über 10 Stunden,
- Unterschreitung der Ruhezeit,
- Systemzeitabweichung,
- Notfallnachtrag,
- Restore-Test mit echtem Backup,
- Auswertung offener und auffälliger Fälle.[cite:185]

## 17. Abnahmekriterien

Das System ist nur dann abnahmefähig, wenn zusätzlich zu den bisherigen Kriterien auch diese Punkte nachweisbar erfüllt sind:[cite:185]

- gesetzlich relevante Prüfhilfen für Pause, Ruhezeit und Höchstarbeitszeit funktionieren,[cite:333][cite:336][cite:339]
- Rollen und Rechte sind organisatorisch definiert,[cite:335]
- Aufbewahrungs- und Löschkonzept ist schriftlich festgelegt,[cite:332]
- Fallback-Prozess ist dokumentiert,[cite:185]
- Restore wurde praktisch getestet,[cite:185]
- offene und auffällige Fälle sind auswertbar.[cite:185]
