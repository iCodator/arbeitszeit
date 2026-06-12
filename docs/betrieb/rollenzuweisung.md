# Rollenzuweisung und Zugriffsregelung

**Dokumenttyp:** Organisatorisches Formular / Einweisung und Rollenfestlegung  
**System:** arbeitszeit  
**Version:** 1.0  
**Stand:** 2026-06-12  
**Ablageort:** `docs/betrieb/rollenzuweisung.md`

> **Hinweis:** Dieses Formular dient als ausfüllbare Vorlage für die Praxis. Es muss vor Inbetriebnahme vollständig ausgefüllt, von den zuständigen Personen freigegeben und außerhalb des Repositories archiviert werden. Es ersetzt keine individuelle Rechtsberatung.

---

## 1. Zweck

Dieses Dokument legt die organisatorischen Rollen, Zuständigkeiten, Stellvertretungen und Zugriffsregeln für das System `arbeitszeit` verbindlich fest. Es dient zugleich als Nachweis der Einweisung und als Grundlage für die technisch erzwungene Rollen- und Rechtevergabe im System.

---

## 2. Verantwortliche Stelle

| Feld | Eintrag |
|---|---|
| Praxis / Verantwortliche Stelle | __________________________________________ |
| Anschrift | __________________________________________ |
| Ansprechpartner/in | __________________________________________ |
| Datum der Festlegung | __________________________________________ |
| Gültig ab | __________________________________________ |

---

## 3. Rollenmodell

Es gelten ausschließlich die folgenden Rollen im Administrations- und Prüfbetrieb:

- `ADMIN`.
- `REVIEWER`.
- `TECH`.

Mitarbeitende ohne diese Rollen dürfen keine administrativen Änderungen, keine Rollenwechsel und keine Systemkonfiguration vornehmen. Die technische Erfassung am Terminal bleibt hiervon unberührt.

---

## 4. Rolleninhaber

| Rolle | Name | Funktion in der Praxis | Benutzername im System | E-Mail / Telefon | Stellvertretung | Aktiv ab | Aktiv bis |
|---|---|---|---|---|---|---|---|
| ADMIN | __________________ | __________________ | __________________ | __________________ | __________________ | __________________ | __________________ |
| REVIEWER | __________________ | __________________ | __________________ | __________________ | __________________ | __________________ | __________________ |
| TECH | __________________ | __________________ | __________________ | __________________ | __________________ | __________________ | __________________ |

Wenn mehrere Personen dieselbe Rolle erhalten, ist jede Person separat aufzuführen.

---

## 5. Zuständigkeiten

### 5.1 ADMIN

Der ADMIN ist zuständig für:

- Anlegen, Aktivieren, Deaktivieren und Ändern von Benutzerkonten.
- Zuweisung und Änderung von Rollen.
- Verwaltung von Mitarbeitenden, RFID-Zuordnungen und Regelarbeitszeiten, soweit technisch vorgesehen.
- Freigabe oder Veranlassung von Korrekturen, sofern dies organisatorisch vorgesehen ist.
- Entscheidung über Berechtigungen im operativen Verwaltungsbetrieb.

### 5.2 REVIEWER

Der REVIEWER ist zuständig für:

- Prüfung offener und auffälliger Fälle.
- Bearbeitung und Freigabe von Nachträgen, soweit dafür freigegeben.
- Ablehnung oder Rückgabe unvollständiger Sachverhalte mit Begründung.
- Dokumentation fachlicher Prüfungen.

### 5.3 TECH

Der TECH ist zuständig für:

- Systemcheck.
- Backup und Restore im Rahmen der technischen Betreuung.
- Betriebssystem-, Hardware- und Verbindungsprüfung.
- Unterstützung bei Installation, Wartung und Fehleranalyse.

Der TECH darf keine fachlichen Freigaben, keine Rollenänderungen und keine inhaltlichen Korrekturen von Zeitdaten vornehmen, sofern dies nicht ausdrücklich zusätzlich als ADMIN-Berechtigung vergeben wurde.

---

## 6. Zugriffsregelung

| Tätigkeit | ADMIN | REVIEWER | TECH | Bemerkung |
|---|---:|---:|---:|---|
| Benutzerkonten anlegen/ändern/deaktivieren | Ja | Nein | Nein | Nur via Admin-CLI |
| Rollen ändern | Ja | Nein | Nein | Nur via Admin-CLI |
| Mitarbeitende anlegen/ändern | Ja | Nein | Nein | Nur wenn in der Praxis freigegeben |
| Offene Fälle prüfen | Ja | Ja | Nein | Fachliche Prüfung |
| Nachträge freigeben/ablehnen | Ja | Ja | Nein | Mit Begründung |
| Backup auslösen | Ja | Nein | Ja | Technische Funktion |
| Restore auslösen | Ja | Nein | Ja | Nur nach Freigabe |
| Systemcheck | Ja | Nein | Ja | Technische Funktion |
| Export erzeugen | Ja | Ja | Nein | Nur berechtigt |
| Regelarbeitszeiten ändern | Ja | Nein | Nein | Soweit organisatorisch festgelegt |

---

## 7. Einweisung

Hiermit wird bestätigt, dass die oben genannten Personen über ihre Aufgaben, Grenzen und Zugriffsrechte im System `arbeitszeit` eingewiesen wurden.

### 7.1 Einweisung ADMIN

| Feld | Eintrag |
|---|---|
| Name | __________________________________________ |
| Datum der Einweisung | __________________________________________ |
| Inhalt der Einweisung | Benutzerverwaltung, Rollen, Protokollierung, Korrekturen, Audit-Log |
| Durchgeführt von | __________________________________________ |
| Unterschrift ADMIN | __________________________________________ |
| Unterschrift Einweisende Person | __________________________________________ |

### 7.2 Einweisung REVIEWER

| Feld | Eintrag |
|---|---|
| Name | __________________________________________ |
| Datum der Einweisung | __________________________________________ |
| Inhalt der Einweisung | Prüfung offener Fälle, Nachträge, Begründungspflichten, Auswertungen |
| Durchgeführt von | __________________________________________ |
| Unterschrift REVIEWER | __________________________________________ |
| Unterschrift Einweisende Person | __________________________________________ |

### 7.3 Einweisung TECH

| Feld | Eintrag |
|---|---|
| Name | __________________________________________ |
| Datum der Einweisung | __________________________________________ |
| Inhalt der Einweisung | Systemcheck, Backup, Restore, Hardware, Fehleranalyse |
| Durchgeführt von | __________________________________________ |
| Unterschrift TECH | __________________________________________ |
| Unterschrift Einweisende Person | __________________________________________ |

---

## 8. Stellvertretung

| Rolle | Vertretung | Vertretungsumfang | Freigabedatum |
|---|---|---|---|
| ADMIN | __________________ | __________________ | __________________ |
| REVIEWER | __________________ | __________________ | __________________ |
| TECH | __________________ | __________________ | __________________ |

Vertretungen sind nur wirksam, wenn sie ausdrücklich dokumentiert und von der verantwortlichen Stelle freigegeben sind.

---

## 9. Datenschutz und Vertraulichkeit

Die Rolleninhaber verpflichten sich, personenbezogene Beschäftigtendaten nur im Rahmen ihrer Zuständigkeit zu verarbeiten. Zugriffe sind auf das notwendige Maß zu beschränken. Exportdateien, Backups und Datenbankdateien sind vor unbefugtem Zugriff zu schützen.

Besonders gilt:

- Keine Weitergabe von Benutzerkonten oder Passwörtern.
- Keine Nutzung gemeinsamer Konten ohne dokumentierte Freigabe.
- Keine Verarbeitung außerhalb des vorgesehenen Zwecks der Zeiterfassung und Verwaltung.

---

## 10. Widerruf / Änderung

| Feld | Eintrag |
|---|---|
| Anlass der Änderung | __________________________________________ |
| Betroffene Rolle | __________________________________________ |
| Wirksam ab | __________________________________________ |
| Genehmigt durch | __________________________________________ |
| Datum | __________________________________________ |
| Unterschrift | __________________________________________ |

Änderungen an Rollen oder Zugriffsrechten sind unverzüglich im System und in diesem Formular zu dokumentieren.

---

## 11. Nachweis der Einweisung

Die Praxis bestätigt, dass die Rollenverteilung bekanntgegeben, erläutert und dokumentiert wurde. Dieses Formular ist zusammen mit den übrigen Betriebsunterlagen aufzubewahren.

| Feld | Eintrag |
|---|---|
| Ort | __________________________________________ |
| Datum | __________________________________________ |
| Für die verantwortliche Stelle | __________________________________________ |
| Für die technische Betreuung | __________________________________________ |
| Für die fachliche Prüfung | __________________________________________ |

---

## 12. Bezug zu den Projektunterlagen

Dieses Formular ist inhaltlich auf die folgenden Unterlagen abgestimmt:

- `pflichtenheft_arbeitszeit_v5.md`.
- `regelwerk_arbeitszeit_v5.md`.
- `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md`.
- `docs/datenschutz/vvt_arbeitszeit_v1.md`.

---

## 13. Änderungshistorie

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 2026-06-12 | Erstfassung als organisatorisches Rollen- und Einweisungsformular |

---

## 14. Anleitung zur Pflege dieses Dokuments

### 14.1 Zuständigkeit

- Für die inhaltliche Pflege dieses Dokuments ist die Praxisleitung bzw. die benannte verantwortliche Stelle zuständig.
- Änderungen dürfen nur von Personen durchgeführt werden, die auch berechtigt sind, Rollen im System `arbeitszeit` zu vergeben oder zu entziehen.

### 14.2 Wann ist eine Aktualisierung erforderlich?

Dieses Dokument ist **unverzüglich** zu aktualisieren, wenn:

- eine neue Person als ADMIN, REVIEWER oder TECH hinzukommt,
- eine bestehende Rolle entzogen oder geändert wird,
- eine Stellvertretung eingerichtet, geändert oder aufgehoben wird,
- sich die Praxisstruktur so ändert, dass Zuständigkeiten neu zugeordnet werden müssen (z.B. Praxisübernahme, neue Standortstruktur).

Spätestens **einmal jährlich** ist eine Überprüfung fällig, ob alle Angaben (Rolleninhaber, Stellvertretungen, Kontaktdaten) noch korrekt sind.

### 14.3 Vorgehen bei Änderungen

1. **Fachliche Entscheidung treffen**  
   Praxisleitung entscheidet, welche Rolle welcher Person zugeordnet, geändert oder entzogen wird.

2. **Dokument anpassen**  
   - Betroffene Tabellenzeilen in den Abschnitten „Rolleninhaber“, „Stellvertretung“ und „Zuständigkeiten“ anpassen.
   - Abschnitt „Widerruf / Änderung“ ausfüllen (Anlass, betroffene Rolle, Wirksam ab, Genehmigt durch, Datum, Unterschrift).

3. **System anpassen**  
   - Entsprechende Änderung technisch im System `arbeitszeit` durchführen (Admin-CLI für Benutzerkonten und Rollen).
   - Prüfen, ob die technische Rollenvergabe mit diesem Dokument übereinstimmt.

4. **Unterschriften einholen**  
   - Änderungen durch die verantwortliche Stelle unterschreiben lassen.
   - Bei neuen Rolleninhabern Einweisungsabschnitt (ADMIN/REVIEWER/TECH) ausfüllen und unterschreiben lassen.

5. **Version und Historie aktualisieren**  
   - In der Änderungshistorie (Abschnitt „Änderungshistorie“) neue Zeile mit Version, Datum und kurzer Beschreibung der Änderung ergänzen.
   - Falls gewünscht, Dokumentversion hochzählen (z.B. von 1.0 auf 1.1).

### 14.4 Aufbewahrung und Zugriff

- Das unterschriebene Original dieses Dokuments ist in der Praxis zusammen mit den übrigen Betriebs- und Datenschutzunterlagen aufzubewahren.
- Eine Kopie kann im Repository oder in der internen Dateiablage geführt werden, sofern **klar erkennbar** ist, dass nur die unterschriebene Fassung rechtsverbindlich ist.
- Zugriff auf die vollständige, unterschriebene Fassung sollen nur Personen haben, die für Organisation, Datenschutz oder IT-Betrieb zuständig sind.

### 14.5 Abgleich mit anderen Dokumenten

Bei jeder inhaltlichen Änderung der Rollenverteilung ist zu prüfen, ob Anpassungen in folgenden Dokumenten erforderlich sind:

- `docs/datenschutz/vvt_arbeitszeit_v1.md` (VVT / Verantwortlichkeiten),
- `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md`,
- interne Dienst- oder Organisationsanweisungen (falls vorhanden).

Änderungen sind so zu dokumentieren, dass jederzeit nachvollziehbar ist, **wer** seit **wann** welche Rolle innehat und **wer** die Änderung freigegeben hat.