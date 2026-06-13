# Aufbewahrungs- und Löschkonzept – arbeitszeit

**Version:** 1.0  
**Praxis:** ____________________________________________  
**Standort:** __________________________________________  
**Datum:** ____ / ____ / 20____  

---

## 1. Zweck und Geltungsbereich

Dieses Dokument regelt Aufbewahrung, Archivierung und Löschung von Daten, die mit
dem lokalen Zeiterfassungssystem **„arbeitszeit“** in der Zahnarztpraxis
erfasst und verarbeitet werden.

Es gilt für:

- alle Mitarbeiter:innen der Praxis,
- alle mit dem System „arbeitszeit“ erfassten Arbeitszeitdaten,
- alle zugehörigen Protokoll- und Systemdaten (z. B. Audit-Log, system_events).

---

## 2. Rechtsgrundlagen und Rahmen

- Arbeitszeitgesetz (ArbZG), insbesondere § 16 ArbZG (Aufzeichnungspflicht)
- ggf. Tarifverträge / Betriebsvereinbarungen (falls vorhanden)
- Datenschutz-Grundverordnung (DSGVO), insbesondere Art. 5, Art. 17, Art. 32
- Bundesdatenschutzgesetz (BDSG) in der jeweils gültigen Fassung

Die Pflicht zur Aufbewahrung dienstlicher Arbeitszeitnachweise steht einer
vollständigen physischen Löschung aller Datensätze regelmäßig entgegen. Stattdessen
wird mit **Status**, Einschränkung der Verarbeitung und technischen Schutzmaßnahmen
gearbeitet.

---

## 3. Datenkategorien im System „arbeitszeit“

Folgende Datenkategorien werden unterschieden:

1. **Arbeitszeitdaten**
   - Kommen/Gehen/Pause-Buchungen
   - Nachträge, Korrekturen, Prüfvermerke
2. **Mitarbeiter-Stammdaten**
   - Name, Personalnummer, Beschäftigungsstatus
3. **Benutzerkonten-Daten**
   - Benutzername, gehashte Passwörter, Rolle (ADMIN/REVIEWER/TECH)
4. **Technische Protokolle**
   - Audit-Log, system_events, device_events
5. **Exportdaten**
   - CSV/PDF-Auswertungen, die außerhalb der Datenbank erzeugt werden

---

## 4. Aufbewahrungsfristen

### 4.1 Arbeitszeitdaten

- **Reguläre Aufbewahrungsfrist:** mindestens **2 Jahre** nach dem jeweiligen
  Kalenderjahr der Entstehung, in Anlehnung an § 16 Abs. 2 ArbZG.
- **Praktische Umsetzung:** Daten in der Datenbank werden nicht physisch gelöscht,
  sondern verbleiben dauerhaft, werden aber nach Ablauf von **5 Jahren** nur noch
  bei berechtigtem Bedarf ausgewertet (z. B. behördliche Prüfung, arbeitsrechtliche
  Auseinandersetzung).

### 4.2 Mitarbeiter-Stammdaten

- Während des Beschäftigungsverhältnisses: aktive Nutzung im System.
- Nach Beendigung des Beschäftigungsverhältnisses:
  - Deaktivierung der Zuordnung im System (z. B. Deaktivierung RFID-Karte, Kennzeichnung
    als „inaktiv“).
  - Mindestaufbewahrung der arbeitszeitrelevanten Daten: 2 Jahre, praktische
    Aufbewahrung von bis zu 5 Jahren, wenn arbeitsrechtliche Auseinandersetzungen
    nicht ausgeschlossen sind.
  - Danach Prüfung, ob ein berechtigter Aufbewahrungsgrund weiter besteht.

### 4.3 Benutzerkonten-Daten

- Solange das Benutzerkonto für Administration/Prüfung benötigt wird.
- Nach Ausscheiden oder Rollenwechsel:
  - Deaktivierung des Benutzerkontos (kein Login mehr möglich).
  - Keine physische Löschung von Audit-Log-Einträgen, um Nachvollziehbarkeit zu
    gewährleisten.

### 4.4 Technische Protokolle (Audit-Log, system_events, device_events)

- Mindestens 2 Jahre, faktisch solange das System produktiv im Einsatz ist.
- Löschung/Anonymisierung nur, sofern keine gesetzlichen oder
  nachweisbezogenen Gründe entgegenstehen.

### 4.5 Exporte (CSV/PDF)

- Exporte können zusätzliche Risiken bergen (z. B. Ablage auf Fileservern).
- Standardaufbewahrungsfrist der Praxis für solche Dokumente:
  - **5 Jahre**, sofern nicht kürzere Fristen vereinbart oder längere Aufbewahrung
    aus Gründen der Beweisführung erforderlich ist.
- Verantwortlich für Archivierung und Löschung: siehe Abschnitt 7.

---

## 5. Löschung, Deaktivierung und Anonymisierung

### 5.1 Prinzip „so wenig wie möglich, so viel wie nötig“

- Primär werden Konten und Mitarbeiter-Datensätze **deaktiviert**, nicht physisch
  gelöscht, um die Nachvollziehbarkeit von Arbeitszeiten und Admin-Aktionen zu
  erhalten.
- Eine vollständige Löschung einzelner Buchungssätze erfolgt nur in begründeten
  Ausnahmefällen (z. B. fehlerhafte Testdaten in einer realen Produktiv-Datenbank,
  sofern rechtlich zulässig).

### 5.2 Vorgaben für Löschvorgänge

- **Produktiv-Datenbank:** keine routinemäßige physische Löschung einzelner
  Arbeitszeitdatensätze; stattdessen:
  - Kennzeichnung von Korrekturen über Korrektur-Mechanismen,
  - deaktivierte Mitarbeiter-/Benutzerkonten.
- **Exporte:** nach Ablauf der internen Aufbewahrungsfrist werden Exportdateien
  in definierten Zyklen gelöscht (siehe Abschnitt 7).

---

## 6. Backups und Wiederherstellung

- Backups enthalten regelmäßig vollständige Kopien der Datenbank und ggf. Exporte.
- Löschkonzepte sind **auch für Backups** zu berücksichtigen:
  - Rotationskonzept (z. B. tägliche Backups der letzten X Tage, wöchentliche
    Backups der letzten Y Wochen).
  - Sicherstellung, dass alte Datenträger, auf denen personenbezogene Daten
    gespeichert sind, vor Wiederverwendung oder Entsorgung sicher gelöscht
    werden.

Konkretes Rotationschema:  
- Tägliche Sicherungen: ___ Tage  
- Wöchentliche Sicherungen: ___ Wochen  
- Monatliche Sicherungen (falls genutzt): ___ Monate  

---

## 7. Verantwortlichkeiten

Verantwortlich für die Umsetzung dieses Konzepts ist:

- **Datenschutz-Verantwortliche/r der Praxis:** __________________________  
- **Technische Verantwortung (IT/Betrieb):** _____________________________  

Aufgaben:

- Überwachung der Einhaltung der Aufbewahrungsfristen,
- Entscheidung über Lösch- oder Anonymisierungsmaßnahmen im Einzelfall,
- Dokumentation von Löschvorgängen, insbesondere bei Sonderfällen.

---

## 8. Dokumentation von Löschvorgängen

Für außergewöhnliche Löschvorgänge (insbesondere außerhalb des regulären
Rotations-/Archivierungskonzepts) wird ein Löschprotokoll geführt mit:

- Datum und Uhrzeit,
- verantwortliche Person,
- betroffene Datenkategorie (z. B. Export, Backup, Testdaten),
- Begründung,
- technische Methode (z. B. sichere Löschung, Überschreiben, physische Zerstörung),
- Bestätigung der Durchführung.

---

## 9. Inkrafttreten und Überprüfung

Dieses Aufbewahrungs- und Löschkonzept tritt am **____ / ____ / 20____** in Kraft.

Es wird mindestens alle **2 Jahre** oder bei wesentlichen Änderungen der
Rechtslage bzw. der Systemarchitektur überprüft und bei Bedarf angepasst.

---

**Unterschrift Praxisleitung:** _______________________________ Datum: ______________

**Unterschrift Datenschutz-Verantwortliche/r:** ______________ Datum: ______________