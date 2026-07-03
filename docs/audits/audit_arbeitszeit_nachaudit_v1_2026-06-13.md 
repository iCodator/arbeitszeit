# Nachaudit-Bericht: Projekt arbeitszeit

**Datum:** 2026-06-13  
**Uhrzeit:** 10:15 CEST  
**Auditor:** KI-Auditor (Perplexity / GPT-5.1)  
**Repo:** iCodator/arbeitszeit  

---

## 1. Ausgangslage

- Grundlage dieses Nachaudits ist der Audit-Bericht `docs/audits/audit_arbeitszeit_v1_2026-06-13_09-04.md` (Phasen 1–5, Befund-IDs P1-01 … P5-06, K/H/M/N).  
- Ziel des Nachaudits ist **nicht** eine erneute Vollprüfung des Codes, sondern die Feststellung, welche im Audit benannten Befunde seitdem im Repo adressiert wurden und welche **organisatorischen** Punkte weiterhin offen sind.  

---

## 2. Umgesetzte technische und dokumentarische Befunde

Die folgenden Befunde gelten auf Basis der vorliegenden Artefakte als **geschlossen**:

### Phase 1

- **P1-02 / M-01 – BookingStatus-Historie dokumentiert**  
  - In `docs/informelles/migrationsuebersicht_notiz_v1.md` ist ergänzt, dass `0001_schema.sql` ursprünglich `POSSIBLE_*` und `MANUAL_ENTRY` als BookingStatus-Werte enthielt und dies durch `0003_cleanup_booking_status.sql` korrigiert wurde.  
  - In `CHANGELOG.md` (Abschnitt „Phase 4: Infrastruktur“) ist die Bereinigung der historischen BookingStatus-Inkonsistenz explizit erwähnt.  

- **P1-04 / H-01 – Referenz auf Anlage-Einhaltung Pflichtenheft**  
  - `docs/informelles/planung_gesamt.md` referenziert nun konsistent:
    - `anlage_einhaltung_pflichtenheft.md` im Projektwurzel-Verzeichnis (Version 1),  
    - `docs/archive/anlage_einhaltung_pflichtenheft_v2.md` als archivierte Version (Pflichtenheft v4).  
  - Der vorher unklare Verweis ist damit aufgeklärt und dokumentiert.  

### Phase 2

- **P2-01 / M-02 – Netto-ArbZG-Prüflogik dokumentiert**  
  - In `src/arbeitszeit/domain/services/compliance_checks.py` ist ein Modul-Docstring ergänzt, der klarstellt:
    - Alle Prüfungen arbeiten auf Basis der Netto-Arbeitszeit (Arbeitsphasen minus Pausen).  
    - §4 ArbZG bezieht sich auf Brutto-Anwesenheitszeit.  
    - Die implementierten Checks sind fachliche Prüfhilfen und ersetzen keine rechtsverbindliche Bewertung.  

- **P2-02 / M-03 – BREAK_START nach GO explizit gemacht**  
  - In `booking_rules.py` ist kommentiert, dass der Check „BREAK_START ohne offene Arbeitsphase“ auch den Fall „BREAK_START direkt nach GO“ abdeckt.  
  - In den Domänentests existiert bereits ein Testfall, der diesen Fall abdeckt.  

- **P2-04 / N-02 – Wochenprüfung als Backlog**  
  - In `docs/informelles/planung_gesamt.md` ist dokumentiert, dass eine kumulative Wochenarbeitszeitprüfung nach ArbZG §3 derzeit nicht implementiert ist und bewusst als Backlog-Thema geführt wird.  

### Phase 3

- **P3-03 / H-04 – Rollenlose Terminal-Buchung dokumentiert**  
  - In `src/arbeitszeit/application/use_cases/book_time.py` ist im `BookUseCase.execute()` ein Kommentar ergänzt, dass:
    - Terminal-Buchungen keine explizite `UserRole` prüfen,  
    - die Authentifikation über eine gültige RFID-Karte erfolgt,  
    - Admin-/Reviewer-/Tech-Aktionen ihre Rollenprüfung separat durchführen.  
  - In `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` (Abschnitt 3.1) ist die Designentscheidung zur rollenlosen Terminal-Buchung ebenfalls beschrieben.  

### Phase 4

- **time_monitor – Fehler nicht mehr stumm geschluckt**  
  - In `src/arbeitszeit/infrastructure/time_monitor.py` wird ein Fehler beim Protokollieren des Zeitmonitors nicht mehr mit `except Exception: pass` unterdrückt, sondern als Warnung geloggt. Damit ist das Risiko eines „unsichtbar defekten“ Monitors reduziert.  

### Phase 5

- **P5-02 / H-03 – PBKDF2-Hashing dokumentiert**  
  - In `src/arbeitszeit/presentation/admin_cli/user_accounts.py` ist beim Passwort-Hashing ein Kommentar ergänzt:
    - PBKDF2-HMAC-SHA256, zufälliger Salt, erhöhte Iterationszahl.  
    - Hinweis auf DSGVO Art. 32 und den Einsatzkontext (lokales Praxis-System).  
  - In `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` ist die Passwort-Hashing-Strategie beschrieben.  

### Querschnitt / neue Betriebsdokumente

- **Neue Betriebsdokumentation (Version 1.1)**  
  - `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` ersetzt den vorherigen informellen Stand, ergänzt um:
    - Hinweise zu Zeitmonitor-Fehlerbehandlung,  
    - Erläuterung der Netto-Arbeitszeit-Prüfungen,  
    - Beschreibung des Passwort-Hashings.  

- **Neues Aufbewahrungs- und Löschkonzept**  
  - `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` beschreibt:
    - Datenkategorien,  
    - Aufbewahrungsfristen (insbesondere Arbeitszeitdaten, Exporte),  
    - Prinzip „Deaktivierung statt physischer Löschung“ für produktive Datensätze,  
    - Verantwortlichkeiten und Löschprotokollierung.  

- **Neues Datenschutz- und TOM-Dokument (inkl. Backup)**  
  - `docs/betrieb/datenschutz_und_tom_arbeitszeit_v1_0.md` fasst zusammen:
    - Beschreibung der Verarbeitung (Arbeitszeit, Zwecke),  
    - technische Maßnahmen (lokale Installation, Passwort-Hashing, Protokollierung, Backup),  
    - organisatorische Maßnahmen (Rollenmodell, Schulung, Umgang mit Betroffenenrechten),  
    - Bezug auf ggf. erforderliche AV-Verträge.  

- **Neue Rollenzuweisung**  
  - `docs/betrieb/rollenzuweisung_arbeitszeit_v1_0.md` definiert:
    - Struktur für die namentliche Zuordnung von ADMIN/REVIEWER/TECH,  
    - Änderungsprotokoll für Rollenwechsel,  
    - Inkrafttreten mit Unterschriften.  

- **CHANGELOG angepasst**  
  - `CHANGELOG.md` enthält einen neuen Abschnitt „Audit & Dokumentation – 2026-06-13“, der die oben genannten Dokumente und Korrekturen explizit aufführt.  

---

## 3. Weiterhin offene organisatorische Punkte

Folgende Punkte liegen **außerhalb des Codes** und gelten weiterhin als nicht abgeschlossen:

1. **K-01 – Datenschutzunterlagen der Praxis**  
   - Abschluss und Ablage tatsächlicher AV-Verträge (falls Cloud-/NAS-Dienstleister mit Personenbezug eingesetzt werden).  
   - Ergänzung bzw. Integration des neuen Datenschutz-/TOM-Dokuments in das allgemeine Datenschutzkonzept der Praxis.  
   - Ggf. Aktualisierung des Verzeichnisses von Verarbeitungstätigkeiten.  

2. **K-02 – Aufbewahrungs- und Löschkonzept formell verabschieden**  
   - Das Dokument `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` ist inhaltlich vorbereitet, muss aber:
     - von der Praxisleitung geprüft,  
     - ggf. mit (Fach-)Beratung abgestimmt,  
     - unterschrieben und für verbindlich erklärt werden.  

3. **K-03 – Organisatorische Rollenzuweisung konkretisieren**  
   - `docs/betrieb/rollenzuweisung_arbeitszeit_v1_0.md` ist strukturell vorhanden, enthält aber noch keine konkreten Namen und Daten.  
   - Die Praxis muss:
     - ADMIN/REVIEWER/TECH namentlich benennen,  
     - Inkrafttreten dokumentieren,  
     - Änderungen laufend im Änderungsprotokoll nachführen.  

4. **Restore-Test im Realbetrieb dokumentieren (P5-06)**  
   - Ein technischer Restore-Prozess ist implementiert; der Unittest existiert.  
   - Ein tatsächlich durchgeführter Restore-Test auf der Zielhardware mit Protokoll (Wer, Wann, Ergebnis) liegt weiterhin nicht als Repo-Artefakt vor.  

5. **Formale Betriebsfreigabe**  
   - Es gibt weiterhin kein separates, unterschriebenes Betriebsfreigabe-Dokument der Praxis, das Technik, Datenschutz und Organisation zusammenführt und das System für den produktiven Einsatz freigibt.  

---

## 4. Bewertung und Empfehlung

### Technische Seite

- Alle im ursprünglichen Audit identifizierten **technischen Mängel bzw. Dokumentationslücken** im Code und in der projektnahen Dokumentation gelten mit Stand 2026-06-13 als behoben oder explizit dokumentiert.  
- Es bestehen keine bekannten, unbehandelten Soll-Ist-Abweichungen mehr innerhalb der Phasen 1–5, soweit sie technische Artefakte betreffen.  

**Bewertung Technik:** GO (keine weiteren Auflagen aus dem Nachaudit).  

### Organisatorische Seite

- Durch die neuen Dokumente in `docs/betrieb/` sind die im Audit adressierten organisatorischen Themen (Aufbewahrung/Löschung, Datenschutz/TOM, Rollenzuweisung) formal strukturiert, aber noch nicht durch Unterschriften und konkrete Namen „gelebt“.  
- Die tatsächliche Umsetzung bleibt Aufgabe der Praxis (Management, Datenschutz, ggf. externe Beratung).  

**Bewertung Organisation:** GO mit Auflagen  
(Abschluss AV-Verträge, Unterschriften und Ausfüllung der drei neuen Betriebsdokumente, dokumentierter Restore-Test, formale Betriebsfreigabe).  

---

## 5. Schlussfolgerung Nachaudit

- Ein **erneutes Vollaudit** des Repos ist zum jetzigen Zeitpunkt **nicht erforderlich**, da die festgestellten technischen Befunde adressiert wurden und die organisatorischen Anforderungen in eigenständige Dokumente überführt sind.  
- Für eine **rechtssichere produktive Nutzung** des Systems durch die Zahnarztpraxis sind folgende Schritte noch zwingend zu empfehlen:
  1. Ausfüllen und Unterschreiben der drei Betriebsdokumente in `docs/betrieb/`.  
  2. Dokumentation eines mindestens einmalig durchgeführten Restore-Tests.  
  3. Erstellung und Unterzeichnung eines Betriebsfreigabeprotokolls, das auf Pflichtenheft, Regelwerk, Audit und die drei Betriebsdokumente Bezug nimmt.  

Solange diese Punkte nicht abgearbeitet und unterschrieben sind, ist das System technisch abnahmefähig, organisatorisch aber noch nicht vollständig freigegeben.