# Datenschutz und technische/organisatorische Maßnahmen (TOM) – arbeitszeit

**Version:** 1.0  
**Praxis:** ____________________________________________  
**Standort:** __________________________________________  
**Datum:** ____ / ____ / 20____  

---

## 1. Zweck und Geltungsbereich

Dieses Dokument beschreibt die wesentlichen technischen und organisatorischen
Maßnahmen (TOM) der Zahnarztpraxis im Zusammenhang mit dem Einsatz des lokalen
Zeiterfassungssystems **„arbeitszeit“** im Sinne von Art. 32 DSGVO.

Es ergänzt vorhandene Datenschutzdokumente (Verzeichnis von Verarbeitungstätigkeiten,
Datenschutzkonzept, TOM-Dokumentation, ggf. AV-Verträge).

---

## 2. Beschreibung der Verarbeitung

- **Verarbeitungstätigkeit:** Erfassung und Auswertung von Arbeitszeiten der
  Mitarbeiter:innen der Praxis.
- **Zweck:** Erfüllung arbeitszeitrechtlicher Pflichten, interne Einsatzplanung,
  Nachweis gegenüber Behörden bei Kontrollen.
- **Datenkategorien:** Arbeitszeitdaten, Mitarbeiterstammdaten, Benutzerkonten,
  Protokolldaten (Audit-Log, system_events, device_events).

---

## 3. Verantwortlichkeiten

- **Verantwortlicher i. S. d. DSGVO:**  
  Zahnarztpraxis ________________________________________________

- **Datenschutzbeauftragte/r (sofern bestellt):**  
  Name: ________________________________________________

- **Technische Gesamtverantwortung für „arbeitszeit“:**  
  Name/Funktion: ______________________________________

---

## 4. Technische Maßnahmen

### 4.1 Systemarchitektur und Zugriff

- Lokale Installation (kein Cloud-Backend).
- Zugriff auf Datenbank und Exporte nur von autorisierten Arbeitsplätzen mit
  entsprechend geschützten Benutzerkonten (Betriebssystemebene).
- Admin-CLI ist nur mit gültigem Admin-Account nutzbar.

### 4.2 Passwort-Hashing

- Passwörter von Admin/Reviewer/Tech-Konten werden **nicht im Klartext**
  gespeichert.
- Die Anwendung verwendet PBKDF2-HMAC-SHA256 mit zufälligem Salt und erhöhter
  Iterationszahl (siehe Quellcode `presentation/admin_cli/user_accounts.py`).
- Zweck: Erhöhung der Sicherheit bei unbefugtem Zugriff auf die Datenbankdatei.
- **Praxisentscheidung:** Die gewählte Konfiguration wird als angemessene Maßnahme
  nach Art. 32 DSGVO für eine lokale Einzelplatzanwendung eingestuft.

### 4.3 Protokollierung (Audit-Log, system_events)

- Wichtige Änderungen (Benutzerkonten, Korrekturen, Nachträge, Systemereignisse)
  werden im Audit-Log bzw. in `system_events` protokolliert.
- Ziel: Nachvollziehbarkeit von Zugriffen und Änderungen, Erkennen auffälliger
  Aktivitäten.
- Protokolle sind nur für berechtigte Personen einsehbar.

### 4.4 Backup und Wiederherstellung

- Regelmäßige lokale Backups der Datenbank (siehe separates Backup-Konzept).
- Optionale NAS-Spiegelung, soweit betrieblich vorgesehen.
- Zugriff auf Backups ist auf befugte Personen beschränkt.
- Medien mit personenbezogenen Daten werden bei Entsorgung sicher gelöscht bzw.
  vernichtet.

---

## 5. Organisatorische Maßnahmen

### 5.1 Rollen- und Berechtigungskonzept

- Rollenmodelle in der Anwendung:
  - **ADMIN** – vollumfängliche technische/administrative Rechte.
  - **REVIEWER** – fachliche Prüfung und Genehmigung/ Ablehnung von Nachträgen.
  - **TECH** – technische Konfiguration, eingeschränkte fachliche Rechte.
- Die konkrete Zuordnung von Personen zu Rollen ist in einem separaten
  Dokument „Rollenzuweisung – arbeitszeit“ geregelt.
- Regel: Ein Admin-Account wird nur an Personen vergeben, die ausdrücklich
  dazu befugt sind.

### 5.2 Schulung und Sensibilisierung

- Mitarbeiter:innen werden über die Zwecke der Arbeitszeiterfassung und die
  zulässige Nutzung informiert.
- Personen mit Admin-/Reviewer-/Tech-Rollen werden zusätzlich über ihre
  besonderen Verantwortlichkeiten geschult.

### 5.3 Umgang mit Betroffenenrechten

- Anfragen von Mitarbeiter:innen zu ihren Daten (Auskunft, Berichtigung etc.)
  werden über definierte Prozesse bearbeitet.
- Technisch können Arbeitszeitdaten im System eingesehen, korrigiert und
  ergänzt werden; vollständige Löschung erfolgt nur, wenn rechtlich zulässig
  und dokumentiert (siehe Aufbewahrungs- und Löschkonzept).

---

## 6. Externe Dienstleister und AV-Verträge

- Sofern Cloud-Backup oder externe IT-Dienstleister eingesetzt werden:
  - Prüfung, ob die Dienstleister personenbezogene Daten erhalten oder Zugriff
    erhalten könnten.
  - Abschluss eines Auftragsverarbeitungsvertrages (AV-Vertrag) nach Art. 28 DSGVO
    mit entsprechenden TOM.
- Die konkrete Liste der Dienstleister und die AV-Verträge werden in einem
  gesonderten Verzeichnis geführt.

---

## 7. Risikoabschätzung (Kurzfassung)

- **Hauptszenarien:**
  - Unbefugter Zugriff auf die Datenbankdatei oder Backups.
  - Verlust/Diebstahl von Exporten.
  - Missbrauch administrativer Konten.
- **Minderung durch getroffene Maßnahmen:**
  - Lokale Speicherung, eingeschränkter Zugriff auf Systeme.
  - Passwort-Hashing und Rollenmodell.
  - Protokollierung von administrativen Aktionen.
  - Backup- und Löschkonzepte.

Eine ausführliche Risikoanalyse kann bei Bedarf in einem eigenen Dokument
(DSFA oder internes Risiko-Assessment) erfolgen.

---

## 8. Inkrafttreten und Überprüfung

Dieses Dokument tritt am **____ / ____ / 20____** in Kraft und wird mindestens
alle **2 Jahre** oder bei wesentlichen Änderungen der Technik oder Rechtslage
überprüft.

---

**Unterschrift Praxisleitung:** _______________________________ Datum: ______________  

**Unterschrift Datenschutzbeauftragte/r (falls vorhanden):** ______________ Datum: ______________