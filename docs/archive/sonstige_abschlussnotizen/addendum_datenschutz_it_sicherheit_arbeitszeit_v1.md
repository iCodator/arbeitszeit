# Addendum Datenschutz und IT-Sicherheit – Projekt arbeitszeit (Version 1)

Dieses Addendum ergänzt das Pflichtenheft „arbeitszeit – Version 4“ um spezifische Anforderungen und Festlegungen zu Datenschutz und IT-Sicherheit. Es richtet sich insbesondere an Praxisinhaber, technische Betreuung, Datenschutzbeauftragte und ggf. externe IT-Dienstleister.

## 1. Zweck und Geltungsbereich

Das System **arbeitszeit** verarbeitet personenbezogene Arbeitszeitdaten von Beschäftigten einer Zahnarztpraxis. Dieses Addendum konkretisiert, wie die Vorgaben aus DSGVO, BDSG sowie der IT-Sicherheitsrichtlinie für (zahn-)ärztliche Praxen bei Planung, Einführung und Betrieb des Systems einzuhalten sind.[^DSGVO][^BDSG][^ITR]

Es bezieht sich auf:

- die lokale produktive Nutzung des Systems in der Praxis,
- die Speicherung der Daten im lokalen Datenbanksystem,
- die Erstellung und Aufbewahrung von Backups (lokal und in der Cloud).

## 2. Rechtsgrundlagen und Verantwortlichkeit

Verantwortlicher im Sinne der DSGVO ist der Praxisinhaber bzw. die Praxisbetreiberin.[^DSGVO]

Die Verarbeitung der Arbeitszeitdaten erfolgt auf Grundlage von:

- **Art. 6 Abs. 1 lit. c DSGVO** (Erfüllung rechtlicher Pflichten, insbesondere aus ArbZG und Arbeitsschutzrecht),
- **Art. 6 Abs. 1 lit. f DSGVO** (berechtigtes Interesse an Nachweis und Organisation von Arbeitszeiten),
- **Art. 88 DSGVO i.V.m. § 26 BDSG** (Datenverarbeitung für Zwecke des Beschäftigungsverhältnisses).

Die Pflicht zur objektiven, verlässlichen und zugänglichen Zeiterfassung ergibt sich aus der Rechtsprechung des EuGH und des BAG sowie aus Arbeitsschutz- und Arbeitszeitrecht.[^BAG][^ARBSCHG][^ARBZG]

## 3. Datenkategorien und Grundsätze der Datenverarbeitung

### 3.1 Verarbeitete Datenkategorien

Das System verarbeitet insbesondere:

- Mitarbeiterkennung (Name oder pseudonymisierte Kennung),
- Zuordnung von RFID-Karten zu Mitarbeitern,
- Buchungsdaten (Datum, Uhrzeit, Buchungsart wie Kommen/Gehen/Pause),
- abgeleitete Zeitwerte (Dauer, Summen je Tag/Woche/Monat),
- Status- und Prüfflags (z.B. offene Buchungen, mögliche Verstöße),
- Korrektur- und Nachtragsinformationen (Wer? Wann? Warum?).

Es werden **keine biometrischen Daten** (z.B. Fingerabdruck, Gesichtserkennung) verarbeitet.

### 3.2 Datenschutzgrundsätze

Die Verarbeitung folgt den Grundsätzen nach Art. 5 DSGVO (Rechtmäßigkeit, Zweckbindung, Datenminimierung, Richtigkeit, Speicherbegrenzung, Integrität und Vertraulichkeit).[^DSGVO]

Insbesondere gilt:

- Es werden nur solche Daten verarbeitet, die für Zeiterfassung, Prüfung, Korrektur, Nachweis und Verwaltung der Arbeitszeiten erforderlich sind.
- Die Daten werden vor unbefugtem Zugriff geschützt und – wo technisch sinnvoll – verschlüsselt gespeichert.
- Aufbewahrungsfristen und Lösch-/Rotationskonzepte werden so gestaltet, dass die gesetzlichen Vorgaben (ArbZG, DSGVO, BDSG) eingehalten werden.

## 4. Systemarchitektur: Lokalbetrieb und Backups

### 4.1 Strikt lokale produktive Verarbeitung

Die produktive Verarbeitung und Auswertung der Arbeitszeitdaten erfolgt ausschließlich:

- auf einem dedizierten Praxis-Terminal (z.B. Lubuntu-System) und
- im lokalen Datenbanksystem (z.B. SQLite) der Praxis.

Es findet **keine produktive Verarbeitung** von Arbeitszeitdaten in externen Rechenzentren oder Cloud-Diensten statt. Die Daten verbleiben für alle operativen Zwecke in der Umgebung der Zahnarztpraxis.

### 4.2 Backups (lokal und Cloud)

Zur Sicherstellung von Verfügbarkeit und Wiederherstellbarkeit (Art. 32 DSGVO) werden regelmäßige Backups erstellt:

1. **Lokale Backups**  
   - Speicherung auf einem lokalen, geschützten Datenträger (z.B. NAS im Praxisnetz).  
   - Zugriff nur für berechtigte Administratoren und technische Betreuung.

2. **Cloud-Backups (optional)**  
   - Zusätzliche Ablage verschlüsselter Backups in einem externen Cloud-Speicher (z.B. für Katastrophenfälle wie Brand/Einbruch in der Praxis).  
   - Vor Übertragung in die Cloud werden sämtliche Backup-Daten **clientseitig verschlüsselt**, d.h. der Verschlüsselungsschlüssel wird ausschließlich in der Praxis verwaltet.  
   - Im Cloud-Speicher liegen die Daten ausschließlich in verschlüsselter Form vor. Eine Entschlüsselung ist nur nach Rücktransfer in die Praxisumgebung möglich.[^CLOUD]

Die Cloud dient ausschließlich als **technisches Backup-Medium**, nicht als produktives System. Eine direkte Auswertung von Arbeitszeitdaten in der Cloud findet nicht statt.

## 5. Auftragsverarbeitung und Cloud-Anbieter

Wird ein externer Cloud-Speicher genutzt, ist der Anbieter als **Auftragsverarbeiter** nach Art. 28 DSGVO zu behandeln.[^AVV]

Es sind mindestens zu regeln:

- Abschluss eines **Auftragsverarbeitungsvertrags (AVV)** mit klarer Zweckbindung „Backup-Speicherung“,
- Beschreibung der technischen und organisatorischen Maßnahmen (TOM) des Anbieters,
- Serverstandorte (bevorzugt EU/EWR),
- Regelungen zu Unterauftragsnehmern,
- Lösch- und Rotationskonzept auf Seiten des Anbieters.

Die Praxis dokumentiert in ihrer Datenschutzdokumentation:

- den gewählten Cloud-Anbieter,
- die eingesetzte Verschlüsselungslösung (z.B. clientseitige Verschlüsselung, Schlüssellänge, Schlüsselverwaltung),
- das Backup- und Wiederherstellungsszenario (z.B. Intervalle, Test-Restores).

## 6. Zugriffsschutz und Rollen

Der Zugriff auf Arbeitszeitdaten ist strikt rollenbasiert zu organisieren:

- **Mitarbeiter**  
  - Kein Zugriff auf Rohdaten anderer Mitarbeiter.  
  - Einsicht nur in eigene Auswertungen, soweit organisatorisch vorgesehen.

- **Admin**  
  - Technische Administration (Benutzerverwaltung, RFID-Karten, Regelzeiten, Backup/Restore).  
  - Kein unbegrenzter Zugriff auf Inhaltsdaten ohne dienstlichen Anlass.

- **Prüfer**  
  - Zugriff auf Auswertungen, Prüffälle und Protokolle in dem Umfang, der für die Erfüllung arbeitsrechtlicher Kontroll- und Dokumentationspflichten erforderlich ist.

- **Technische Betreuung**  
  - Zugriff auf Systemparameter, Logs und Backups im Rahmen der Wartung, jedoch nach Möglichkeit ohne Einsicht in personenbezogene Detaildaten (z.B. durch Pseudonymisierung oder rollenbasierte Einschränkungen).

Zugriffe, insbesondere administrativ-technische, sind soweit möglich zu protokollieren (Audit-Log).

## 7. Speicherfristen und Lösch-/Rotationskonzept

### 7.1 Produktive Daten

Arbeitszeitdaten werden mindestens 2 Jahre aufbewahrt, um gesetzlichen Dokumentationspflichten nach dem Arbeitszeitgesetz zu entsprechen.[^ARBZGZEIT][^ZEITDOKU]  
Eine längere Aufbewahrung kann erforderlich sein, wenn arbeitsrechtliche Auseinandersetzungen, Prüfungen oder andere berechtigte Interessen bestehen; in diesen Fällen ist dies zu dokumentieren.

Eine physische Löschung fachlich relevanter Buchungen im produktiven System erfolgt im Regelfall nicht. Stattdessen werden Status- und Korrekturmechanismen verwendet (z.B. Kennzeichnung als korrigiert, Nachtrag mit Begründung).

### 7.2 Backups

Backups enthalten personenbezogene Daten und unterliegen daher ebenfalls den Grundsätzen der Speicherbegrenzung und Datenminimierung.[^BACKUPDSGVO]

Das Backup-Konzept muss:

- klare **Rotationsfristen** vorsehen (z.B. tägliche, wöchentliche und monatliche Sicherungen, die nach definierten Zeiträumen überschrieben werden),
- sicherstellen, dass Daten nach Ablauf der jeweiligen Aufbewahrungsfristen nicht mehr in Backup-Historien neu auftauchen (z.B. durch Überschreiben/Löschen alter Sicherungen),
- regeln, dass Backups ausschließlich für Wiederherstellungszwecke verwendet werden und nicht als „zweites Produktivsystem“ dienen.

Die konkreten Fristen (z.B. wie viele Generationen täglicher/wöchentlicher/monatlicher Backups vorgehalten werden) sind in der IT-Dokumentation der Praxis festzulegen und regelmäßig zu überprüfen.

## 8. Transparenz und Rechte der Beschäftigten

Beschäftigte sind in geeigneter Form über die Zeiterfassung und die Verarbeitung ihrer Daten zu informieren (z.B. in einem Merkblatt, per Aushang oder im Arbeitsvertrag bzw. einer ergänzenden Vereinbarung).[^^INFOPF]

Die Information sollte enthalten:

- Zweck der Zeiterfassung,
- Art der erhobenen Daten,
- Zugriffsberechtigte,
- Aufbewahrungsdauer,
- Hinweis auf mögliche Prüf- und Auswertungszwecke (z.B. zur Einhaltung des ArbZG),
- Hinweise zur Wahrnehmung ihrer Rechte (Auskunft, Berichtigung, ggf. Einschränkung der Verarbeitung).

Beschäftigte haben insbesondere das Recht auf:

- **Auskunft** über die zu ihrer Person gespeicherten Arbeitszeitdaten,
- **Berichtigung** unrichtiger Daten (i.d.R. über Korrekturprozesse mit Begründung und Freigabe),
- ggf. **Einschränkung der Verarbeitung** oder **Löschung**, soweit dem keine gesetzlichen Aufbewahrungspflichten entgegenstehen.[^DSGVO]

## 9. IT-Sicherheitsanforderungen in der Zahnarztpraxis

Die Zahnarztpraxis ist verpflichtet, die jeweils gültige IT-Sicherheitsrichtlinie für (zahn-)ärztliche Praxen umzusetzen.[^ITR]  
Das System **arbeitszeit** ist Teil dieser Praxis-IT und muss entsprechend eingebunden werden:

- Integration in das Praxis-IT-Sicherheitskonzept (Rollen, Rechte, Netzinfrastruktur),
- Härtung des Zeiterfassungsterminals (z.B. Benutzerkonten, Updates, physischer Zugriffsschutz),
- Berücksichtigung von Anforderungen an Protokollierung, Backup, Wiederanlauf und Notfallplanung,
- regelmäßige Tests von Backup- und Restore-Verfahren,
- Schulung der Mitarbeiter in der Bedienung des Systems und im sicheren Umgang mit Zugangsmitteln (RFID-Karten, Passwörter).

## 10. Notfall- und Wiederherstellungskonzept

Das Notfallkonzept umfasst:

- Verfahren bei Ausfall des Zeiterfassungsterminals (manuelle Noterfassung, späterer Nachtrag als gekennzeichnete Buchung),
- Vorgehen bei Verlust oder Kompromittierung von RFID-Karten (Sperrung, Neuausgabe),
- Wiederherstellung aus lokalen und/oder Cloud-Backups,
- Dokumentation und Prüfung von Restore-Tests (z.B. mindestens einmal jährlich).

Restore-Tests müssen sicherstellen, dass:

- Backups technisch lesbar sind,
- Entschlüsselung (bei Cloud-Backups) verlässlich funktioniert,
- die Daten nach dem Restore fachlich konsistent und auswertbar sind.

---

## Versionsstand

- Addendum Version 1 (2026-06-10): Erstmals erstellt, basierend auf Pflichtenheft „arbeitszeit – Version 4“ und aktueller Rechtslage zu Arbeitszeiterfassung, Datenschutz und IT-Sicherheit in Zahnarztpraxen (Stand 2026).

---

[^DSGVO]: Datenschutz-Grundverordnung (DSGVO), insbesondere Art. 5, 6, 24, 25, 32 und 88.
[^BDSG]: Bundesdatenschutzgesetz (BDSG), insbesondere § 26 Datenverarbeitung für Zwecke des Beschäftigungsverhältnisses.
[^BAG]: Bundesarbeitsgericht, Beschluss vom 13.09.2022 – 1 ABR 22/21; EuGH, Urteil vom 14.05.2019 – C-55/18.
[^ARBSCHG]: Arbeitsschutzgesetz (ArbSchG), insbesondere § 3 Grundpflichten des Arbeitgebers.
[^ARBZG]: Arbeitszeitgesetz (ArbZG), insbesondere §§ 3, 4, 5, 16.
[^ARBZGZEIT]: Arbeitszeitgesetz (ArbZG) § 16 Abs. 2 zu Arbeitszeitnachweisen.
[^ZEITDOKU]: Aktuelle Fachinformationen zur Dokumentation von Arbeitszeiten und Aufbewahrungsfristen (z.B. BAG-/BMAS-Informationen).
[^ITR]: IT-Sicherheitsrichtlinie für (zahn-)ärztliche Praxen nach aktuell gültiger gesetzlicher Grundlage (vormals § 75b, jetzt § 390 SGB V), mit Umsetzungspflicht ab 2. Januar 2026.
[^CLOUD]: Fachinformationen zu DSGVO-konformem Cloud-Backup (clientseitige Verschlüsselung, AV-Vertrag, EU-Standort).
[^AVV]: Art. 28 DSGVO – Auftragsverarbeitung; dazu Orientierungshilfen der Aufsichtsbehörden.
[^BACKUPDSGVO]: Hinweise der Aufsichtsbehörden zur Löschung in Backups und zur praktischen Umsetzung von Speicherbegrenzung.
[^^INFOPF]: Informationspflichten nach Art. 13 und 14 DSGVO gegenüber Betroffenen.