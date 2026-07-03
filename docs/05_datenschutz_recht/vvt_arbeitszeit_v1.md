# Verzeichnis von Verarbeitungstätigkeiten (VVT)

**Gemäß Art. 30 Abs. 1 DSGVO**

---

| Feld | Wert |
|---|---|
| **Dokument** | `docs/datenschutz/vvt_arbeitszeit_v1.md` |
| **Version** | 1.0 |
| **Stand** | 2026-06-12 |
| **Erstellt von** | *(Name des Verantwortlichen einsetzen)* |
| **Geprüft am** | *(Datum einsetzen)* |
| **Nächste Überprüfung** | *(Datum einsetzen, spätestens jährlich)* |

> **Hinweis:** Dieses Dokument ist eine Vorlage auf Basis der technischen Umsetzung des Systems `arbeitszeit` (Stand: `pflichtenheft_arbeitszeit_v6.md`, `regelwerk_arbeitszeit_v5.md`). Alle mit *(…)* gekennzeichneten Felder sind vor Inbetriebnahme durch die verantwortliche Stelle auszufüllen und zu unterzeichnen. Das ausgefüllte Dokument ist **außerhalb des Repositories** sicher aufzubewahren.

---

## 1. Verantwortlicher (Art. 30 Abs. 1 lit. a DSGVO)

| Feld | Wert |
|---|---|
| Name / Bezeichnung der Praxis | *(vollständiger Name der Zahnarztpraxis)* |
| Straße, Hausnummer | *(Anschrift)* |
| PLZ, Ort | *(PLZ, Ort)* |
| Telefon | *(Telefonnummer)* |
| E-Mail | *(E-Mail-Adresse)* |
| Vertretungsberechtigte Person | *(Name, Funktion)* |

---

## 2. Datenschutzbeauftragter (Art. 30 Abs. 1 lit. a i.V.m. Art. 37 DSGVO)

Zahnarztpraxen sind nach § 38 BDSG und Art. 37 DSGVO in der Regel **nicht verpflichtet**, einen Datenschutzbeauftragten zu benennen, sofern weniger als 20 Personen ständig mit der automatisierten Verarbeitung personenbezogener Daten befasst sind. Dennoch empfiehlt sich die Benennung einer datenschutzverantwortlichen Person im Betrieb.

| Feld | Wert |
|---|---|
| DSB vorhanden? | *(Ja / Nein)* |
| Name (falls vorhanden) | *(Name)* |
| Kontaktdaten (falls vorhanden) | *(E-Mail / Telefon)* |

---

## 3. Zweck der Verarbeitung (Art. 30 Abs. 1 lit. b DSGVO)

Das System `arbeitszeit` verarbeitet personenbezogene Daten der Beschäftigten ausschließlich für folgende Zwecke:

1. **Erfüllung der gesetzlichen Pflicht zur Arbeitszeiterfassung** gemäß BAG-Beschluss vom 13.09.2022 – 1 ABR 22/21 sowie EuGH C-55/18.
2. **Überwachung der Einhaltung von Höchstarbeitszeiten, Ruhepausen und Ruhezeiten** gemäß ArbZG §§ 3, 4, 5.
3. **Nachweis und Dokumentation** der tatsächlichen Arbeitszeiten gegenüber Behörden und im Prüfungsfall.
4. **Betriebsinterne Auswertung** der Arbeitszeiten zur Lohn- und Dienstplanung.

Eine Verwendung der Daten zu anderen Zwecken (z.B. Leistungsbewertung, Verhaltenskontrolle) ist **unzulässig** und findet nicht statt.

---

## 4. Rechtsgrundlage der Verarbeitung (Art. 30 Abs. 1 lit. b DSGVO)

| Rechtsgrundlage | Norm | Anmerkung |
|---|---|---|
| Erfüllung einer rechtlichen Verpflichtung | Art. 6 Abs. 1 lit. c DSGVO i.V.m. ArbZG § 16 Abs. 2 | Pflicht zur Aufzeichnung der Arbeitszeiten |
| Beschäftigungsverhältnis | Art. 6 Abs. 1 lit. b DSGVO, § 26 Abs. 1 BDSG | Verarbeitung zur Durchführung des Arbeitsverhältnisses |

---

## 5. Kategorien betroffener Personen (Art. 30 Abs. 1 lit. c DSGVO)

- Angestellte der Zahnarztpraxis (Vollzeit, Teilzeit, Aushilfen)
- Auszubildende, soweit im System erfasst

Die Mitarbeiter werden im System durch einen internen Mitarbeiterdatensatz repräsentiert. RFID-Chip-UIDs werden vor Speicherung **gehasht** (keine Klartextspeicherung der Hardware-UID).

---

## 6. Kategorien personenbezogener Daten (Art. 30 Abs. 1 lit. c DSGVO)

| Datenkategorie | Konkrete Daten | Speicherort |
|---|---|---|
| Identifikationsdaten | Vorname, Nachname, internes Kürzel | SQLite-Datenbank (`employees`-Tabelle) |
| Authentifizierungsdaten (Admin/Prüfer) | Benutzername, Passwort-Hash (PBKDF2-HMAC-SHA256, 260.000 Iterationen, Zufallssalt) | SQLite-Datenbank (`user_accounts`-Tabelle) |
| Zeiterfassungsdaten | Buchungszeitpunkt, Buchungsart (Kommen/Gehen/Pause), Buchungsstatus | SQLite-Datenbank (`time_bookings`-Tabelle) |
| RFID-Kennung | Gehashte RFID-UID (kein Klartext) | SQLite-Datenbank (`rfid_cards`-Tabelle) |
| Korrekturen und Nachträge | Alter/neuer Zustand, Begründung, Zeitstempel, ausführende Person | SQLite-Datenbank (`booking_corrections`, `supplements`) |
| Audit-Log-Daten | Administrationsvorgänge, Rollenänderungen, Systemereignisse | SQLite-Datenbank (`audit_log`, `system_events`) |
| Hardware-Rohereignisse | Gerätescan-Zeitstempel, Terminal-ID (kein personenbezogener Inhalt im Klartext) | SQLite-Datenbank (`device_events`-Tabelle) |

**Besondere Kategorien (Art. 9 DSGVO):** Es werden keine Gesundheitsdaten, biometrischen Daten oder sonstige besondere Kategorien personenbezogener Daten verarbeitet. RFID-UIDs sind Hardware-Identifikatoren ohne biometrischen Charakter.

---

## 7. Empfänger oder Kategorien von Empfängern (Art. 30 Abs. 1 lit. d DSGVO)

| Empfänger | Zweck | Rechtsgrundlage |
|---|---|---|
| Praxisinhaber / Admin | Systemverwaltung, Auswertung | § 26 BDSG, Art. 6 Abs. 1 lit. b/c DSGVO |
| Prüfer (Reviewer) | Prüfung offener Fälle, Nachtragsgenehmigung | § 26 BDSG |
| Technische Betreuung (Tech) | Systemcheck, Backup, Restore | Berechtigtes Interesse, § 26 BDSG |
| Steuerberater / Lohnbüro | Aufbereitung Lohnabrechnung (CSV-Export) | Art. 6 Abs. 1 lit. b/c DSGVO, ggf. AV-Vertrag erforderlich |
| Behörden (z.B. Finanzamt, Arbeitsbehörde) | Auf gesetzliche Anforderung | Art. 6 Abs. 1 lit. c DSGVO |

> **Hinweis Auftragsverarbeitung:** Wird ein externer Steuerberater, ein Lohnbüro oder ein externer IT-Dienstleister mit Zugriff auf die Datenbank oder Exporte beauftragt, ist ein **Auftragsverarbeitungsvertrag (AVV)** gemäß Art. 28 DSGVO abzuschließen.

Drittlandübermittlungen (Art. 44 ff. DSGVO): **Keine.** Das System ist lokal betrieben; keine Übermittlung an Cloud-Dienste oder Empfänger außerhalb der EU/des EWR.

---

## 8. Löschfristen (Art. 30 Abs. 1 lit. f DSGVO)

| Datenkategorie | Aufbewahrungsfrist | Rechtsgrundlage | Löschverfahren |
|---|---|---|---|
| Zeiterfassungsdaten (Buchungen) | 2 Jahre | ArbZG § 16 Abs. 2 | Archivierung oder geordnete Löschung nach Fristablauf; **keine physische Löschung** aktiver Buchungen im Normalbetrieb |
| Korrekturen und Nachträge | 2 Jahre (zusammen mit Buchungsdaten) | ArbZG § 16 Abs. 2 | Wie Buchungsdaten |
| Audit-Log / Systemereignisse | 2 Jahre | Nachvollziehbarkeitsgebot | Geordnete Archivierung |
| Export- und PDF-Dateien | 5 Jahre (empfohlen) | § 147 AO, § 257 HGB analog (Lohnunterlagen) | Geordnete Löschung nach Fristablauf, Verzeichnis der gelöschten Exporte führen |
| Backup-Dateien | Entspricht Aufbewahrungsfrist der enthaltenen Daten | — | Rotation nach festgelegtem Backup-Konzept |
| Benutzerkonto-Daten (nach Austritt) | Bis Ende der Aufbewahrungsfrist der zugehörigen Buchungsdaten, dann Pseudonymisierung | § 26 BDSG | Deaktivierung sofort bei Austritt; Löschung nach Fristende |

> **Hinweis:** Die Löschung muss **dokumentiert** werden. Ein Löschprotokoll ist zu führen und aufzubewahren.

---

## 9. Technische und organisatorische Maßnahmen (TOM) nach Art. 32 DSGVO

### 9.1 Vertraulichkeit

| Maßnahme | Umsetzung im System |
|---|---|
| Zugriffskontrolle | Rollenbasiertes Berechtigungskonzept (ADMIN / REVIEWER / TECH); technisch erzwungen in der Anwendung |
| Dateisystemschutz | Die SQLite-Datenbankdatei ist mit restriktiven Dateisystem-Berechtigungen zu versehen (empfohlen: `chmod 600`, Eigentümer: Betriebssystem-Konto des Anwendungsbenutzers) |
| Exportverzeichnisschutz | Exportverzeichnis ist auf Betriebssystem-Ebene auf berechtigte Nutzer zu beschränken |
| Passwortschutz | Administratorkennwörter werden ausschließlich als sicherer Hash gespeichert (kein Klartext) |
| RFID-UID-Schutz | Hardware-UIDs werden gehasht gespeichert; keine Klartextspeicherung der Chip-Kennung |
| Physischer Zugang | Das Terminalgerät ist in einem nicht öffentlich zugänglichen Bereich aufzustellen oder physisch zu sichern |

### 9.2 Integrität

| Maßnahme | Umsetzung im System |
|---|---|
| Transaktionssicherheit | SQLite im WAL-Modus; alle Buchungen und Korrekturen sind transaktionsgesichert |
| Unveränderlichkeit von Originalbuchungen | Fachlich relevante Buchungen werden nicht physisch gelöscht; Korrekturen sind als Korrekturen gekennzeichnet |
| Audit-Log | Alle Administrationsvorgänge, Rollenänderungen und Systemereignisse werden revisionssicher protokolliert |
| Zeitüberwachung | Systemzeit-Sprünge und manuelle Zeitänderungen werden erkannt und in `system_events` protokolliert |

### 9.3 Verfügbarkeit und Belastbarkeit

| Maßnahme | Umsetzung im System |
|---|---|
| Backup | Regelmäßige lokale Sicherung der SQLite-Datenbank; optionale NAS-Spiegelung |
| Wiederherstellung | Dokumentiertes Restore-Verfahren (`SQLiteBackupService.restore_from()`, programmatisch, kein eigenständiges CLI-Flag) mit Protokollierung |
| Fallback bei Geräteausfall | Schriftliche Notfallerfassung und gekennzeichneter Nachtrag (Regelwerk v5 §19) |
| Systemcheck | Regelmäßige Selbstprüfung über `system_check.py` |

### 9.4 Datensparsamkeit (Art. 5 Abs. 1 lit. c DSGVO)

- Es werden ausschließlich die für den Zweck der Zeiterfassung und deren Nachweis erforderlichen Daten erhoben.
- Keine Erfassung von Standortdaten, biometrischen Daten oder sonstigen für den Zweck nicht notwendigen Informationen.
- Keine Verhaltens- oder Leistungsüberwachung über den Zeiterfassungszweck hinaus.

---

## 10. Betroffenenrechte (Art. 12–22 DSGVO)

Beschäftigte haben folgende Rechte, die auf Anfrage durch die verantwortliche Stelle zu gewähren sind:

| Recht | Norm | Umsetzungshinweis |
|---|---|---|
| Auskunft | Art. 15 DSGVO | Auf Anfrage: Auskunft über gespeicherte Buchungsdaten des jeweiligen Mitarbeiters via Admin-CLI-Export |
| Berichtigung | Art. 16 DSGVO | Über Korrektur-/Nachtragsfunktion der Admin-CLI, mit Begründungspflicht |
| Löschung | Art. 17 DSGVO | Eingeschränkt durch gesetzliche Aufbewahrungspflichten (ArbZG); nach Fristablauf geordnete Löschung |
| Einschränkung der Verarbeitung | Art. 18 DSGVO | Im Einzelfall durch Admin-Eingriff; Begründung und Dokumentation erforderlich |
| Widerspruch | Art. 21 DSGVO | Eingeschränkt, da Verarbeitung auf gesetzlicher Pflicht beruht |
| Datenübertragbarkeit | Art. 20 DSGVO | CSV-Export der eigenen Buchungsdaten auf Anfrage möglich |

Anfragen sind schriftlich an die verantwortliche Stelle zu richten. Die Frist zur Beantwortung beträgt einen Monat (Art. 12 Abs. 3 DSGVO).

---

## 11. Datenschutz-Folgenabschätzung (DSFA) nach Art. 35 DSGVO

Eine DSFA ist gemäß Art. 35 Abs. 1 DSGVO durchzuführen, wenn die Verarbeitung voraussichtlich ein **hohes Risiko** für die Rechte und Freiheiten natürlicher Personen zur Folge hat.

Bewertung für das System `arbeitszeit`:

| Kriterium | Einschätzung |
|---|---|
| Systematische Überwachung von Beschäftigten | Zeiterfassung als gesetzliche Pflicht; keine darüber hinausgehende Verhaltensüberwachung → **niedriges bis mittleres Risiko** |
| Verarbeitung besonderer Kategorien (Art. 9) | Keine → **kein erhöhtes Risiko** |
| Umfang der Verarbeitung | Kleine Praxis, geringe Anzahl Beschäftigte → **niedriges Risiko** |
| Lokale Verarbeitung ohne Cloud | Kein Drittlandtransfer, kein Internet-Zugriff → **risikomindernder Faktor** |

**Ergebnis:** Bei bestimmungsgemäßem Betrieb (lokale Verarbeitung, kleiner Personenkreis, kein Cloud-Einsatz) ist eine DSFA nach aktuellem Stand **voraussichtlich nicht zwingend erforderlich**. Diese Einschätzung ist bei Änderung des Systemumfangs, der Anzahl der Beschäftigten oder der Verarbeitungsweise zu überprüfen.

> *(Einschätzung durch verantwortliche Stelle bestätigt am: _______________ / Unterschrift: _______________)* 

---

## 12. Meldepflicht bei Datenschutzverletzungen (Art. 33–34 DSGVO)

Bei einer Verletzung der Sicherheit personenbezogener Daten (z.B. Diebstahl des Terminalgeräts, unbefugter Zugriff auf die Datenbankdatei oder Backups) gilt:

- **Meldung an die zuständige Aufsichtsbehörde** innerhalb von **72 Stunden** nach Bekanntwerden (Art. 33 DSGVO).
- **Benachrichtigung der betroffenen Beschäftigten**, wenn ein hohes Risiko für deren Rechte und Freiheiten besteht (Art. 34 DSGVO).
- **Zuständige Aufsichtsbehörde in Bayern:** Bayerisches Landesamt für Datenschutzaufsicht (BayLDA), Promenade 18, 91522 Ansbach, [https://www.lda.bayern.de](https://www.lda.bayern.de)

Vorfälle sind intern zu dokumentieren (Art. 33 Abs. 5 DSGVO).

---

## 13. IT-Sicherheitskonzept (Hinweis §75b SGB V)

Zahnarztpraxen sind nach § 75b SGB V verpflichtet, technische Mindeststandards der IT-Sicherheit einzuhalten, soweit sie an die Telematikinfrastruktur (TI) angebunden sind.

Für das System `arbeitszeit` gilt:

- Das System ist **nicht Teil der Telematikinfrastruktur** und nicht direkt §75b-pflichtig.
- Es ist jedoch **in das praxisweite IT-Sicherheitskonzept einzubeziehen**, da es personenbezogene Beschäftigtendaten verarbeitet.
- Mindestmaßnahmen: aktuelles Betriebssystem (Linux Mint/Lubuntu mit Sicherheitsupdates), Passwortschutz für Betriebssystem-Benutzerkonten, verschlüsselte Festplatte empfohlen, physische Zugangssicherung des Terminalgeräts.

> *(Einbindung in praxisweites IT-Sicherheitskonzept dokumentiert am: _______________ / Verantwortliche Person: _______________)* 

---

## 14. Unterschriften und Freigabe

| Funktion | Name | Datum | Unterschrift |
|---|---|---|---|
| Verantwortliche Stelle (Praxisinhaber/in) | *(Name)* | *(Datum)* | __________________ |
| Datenschutzbeauftragte/r (falls vorhanden) | *(Name)* | *(Datum)* | __________________ |
| Technische Betreuung / Ersteller | *(Name)* | *(Datum)* | __________________ |

---

## 15. Änderungshistorie

| Version | Datum | Änderung | Geändert von |
|---|---|---|---|
| 1.0 | 2026-06-12 | Erstversion auf Basis `pflichtenheft_arbeitszeit_v5.md` und `regelwerk_arbeitszeit_v5.md` | *(Name)* |

---

*Grundlage: `pflichtenheft_arbeitszeit_v6.md` §§ 4, 8.4, 11, 12; `regelwerk_arbeitszeit_v5.md` §§ 17, 18; DSGVO Art. 5, 6, 13, 15–22, 25, 30, 32, 33–35; BDSG § 26; ArbZG §§ 3, 4, 5, 16.*
