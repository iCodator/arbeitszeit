# Betriebsfreigabe-Protokoll – System „arbeitszeit“

**System:** arbeitszeit  
**Dokumenttyp:** Betriebsfreigabe / Systemabnahme  
**Version:** 1.0  
**Stand:** 2026-06-12  
**Ablageort:** `docs/betrieb/betriebsfreigabe_protokoll.md`

> Dieses Protokoll dokumentiert die formale Freigabe des Zeiterfassungssystems
> „arbeitszeit“ für den Produktivbetrieb in der Zahnarztpraxis.
> Es ersetzt keine rechtliche Beratung, orientiert sich aber an üblichen Inhalten
> eines Abnahme- und Inbetriebnahmeprotokolls (Datum, Umfang, Tests, Mängel, Freigabe).[web:122][web:123][web:127]

---

## 1. Basisdaten

| Feld | Eintrag |
|---|---|
| Praxis / Verantwortliche Stelle | __________________________________________ |
| Standort(e) des Zeiterfassungsterminals | __________________________________________ |
| Projekt-/Systembezeichnung | arbeitszeit |
| Datum der Betriebsfreigabe | __________________________________________ |
| Version des Systems (pyproject.toml) | __________________________________________ |
| Datenbankschema-Stand (letzte Migration) | __________________________________________ |
| Verantwortliche Person (Praxisleitung) | __________________________________________ |
| Verantwortliche Person (technische Betreuung) | __________________________________________ |

---

## 2. Geltungsbereich der Freigabe

Diese Betriebsfreigabe gilt für:

- das Zeiterfassungsterminal / die Terminals an folgendem Standort / folgenden Standorten:  
  ________________________________________________________________________
- die eingesetzte Version des Systems `arbeitszeit` laut Abschnitt 1,
- die eingesetzte SQLite-Datenbank samt Schema und Konfiguration,
- die angeschlossene Hardware (RFID-Reader, USB-Numpad, Terminalgerät, NAS),
- die beschriebenen Prozesse zur Zeiterfassung, Korrektur, Nachtragsbearbeitung,
  Export und Backup, soweit in den Projektunterlagen dokumentiert.

---

## 3. Technische Voraussetzungen und Dokumente

### 3.1 Vorliegende Projektunterlagen

Bitte jeweils „Ja/Nein“ markieren und bei Bedarf die konkret verwendete Version eintragen.

| Dokument | Version / Datum | Liegt vor? | Bemerkung |
|---|---|---|---|
| Pflichtenheft `pflichtenheft_arbeitszeit_v6.md` | ______ | ☐ Ja ☐ Nein | __________________ |
| Regelwerk `regelwerk_arbeitszeit_v5.md` | ______ | ☐ Ja ☐ Nein | __________________ |
| Installationsanleitung `installationsanleitung_arbeitszeit.md` | ______ | ☐ Ja ☐ Nein | __________________ |
| Handbuch `handbuch_arbeitszeit.md` | ______ | ☐ Ja ☐ Nein | __________________ |
| Betriebsdokumentation `betriebsdokumentation_arbeitszeit_v1_1.md` | ______ | ☐ Ja ☐ Nein | __________________ |
| VVT `docs/datenschutz/vvt_arbeitszeit_v1.md` | ______ | ☐ Ja ☐ Nein | __________________ |
| Rollenzuweisung `docs/betrieb/rollenzuweisung.md` | ______ | ☐ Ja ☐ Nein | __________________ |
| Hardware-Inbetriebnahmeprotokoll `docs/betrieb/hardware_inbetriebnahme_protokoll.md` | ______ | ☐ Ja ☐ Nein | __________________ |
| CHANGELOG `CHANGELOG.md` (aktueller Stand) | ______ | ☐ Ja ☐ Nein | __________________ |

### 3.2 Systemkonfiguration geprüft

| Prüffrage | Ergebnis | Bemerkung |
|---|---|---|
| Datenbankpfad und Rechte korrekt gesetzt | ☐ Ja ☐ Nein | __________________ |
| `backup.backup_dir` und `export.export_dir` in `system_config` gesetzt | ☐ Ja ☐ Nein | __________________ |
| Terminal-IDs sinnvoll vergeben und dokumentiert | ☐ Ja ☐ Nein | __________________ |
| Zeitmonitor (`time_monitor.jump_threshold_seconds`) konfiguriert | ☐ Ja ☐ Nein | __________________ |

---

## 4. Testnachweise

### 4.1 Funktionale Tests

| Bereich | Prüfumfang | Ergebnis | OK? |
|---|---|---|---|
| Terminal-UI | Basisbuchungen (Kommen/Gehen/Pause), Anzeige, Fehlermeldungen | __________________ | ☐ Ja ☐ Nein |
| Admin-CLI | Mitarbeiter-, Benutzer-, Buchungs- und Nachtragsverwaltung | __________________ | ☐ Ja ☐ Nein |
| Prüf- und Auswertungsfunktionen | Pflichtauswertungen, Warnungen, Prüffälle | __________________ | ☐ Ja ☐ Nein |
| Exporte | CSV- und PDF-Exporte für Stichprobenzeiträume | __________________ | ☐ Ja ☐ Nein |

### 4.2 Infrastruktur- und Sicherheitstests

| Bereich | Prüfumfang | Ergebnis | OK? |
|---|---|---|---|
| Systemcheck | `system_check.py` mit produktiver Konfiguration ausgeführt | __________________ | ☐ Ja ☐ Nein |
| Backup | Lokales Backup erfolgreich erstellt | __________________ | ☐ Ja ☐ Nein |
| Restore-Test | Testrestore auf Testumgebung erfolgreich | __________________ | ☐ Ja ☐ Nein |
| NAS (falls verwendet) | Erreichbarkeit, Backup-Sync, Rechte geprüft | __________________ | ☐ Ja ☐ Nein |
| Hardware-Smoke-Tests | Siehe `hardware_inbetriebnahme_protokoll.md` | __________________ | ☐ Ja ☐ Nein |

### 4.3 Dokumentierte Tests

| Dokument / Referenz | Datum | Ergebnis |
|---|---|---|
| `docs/informelles/testmatrix_pruefbericht_v1.md` | __________ | __________________ |
| `docs/informelles/testmatrix_revision_v1.md` | __________ | __________________ |
| Sonstiger Testbericht | __________ | __________________ |

---

## 5. Rollen, Zuständigkeiten und Einweisung

| Prüffrage | Ergebnis | Bemerkung |
|---|---|---|
| Rollen `ADMIN`, `REVIEWER`, `TECH` organisatorisch festgelegt | ☐ Ja ☐ Nein | __________________ |
| Rollenzuweisung in `docs/betrieb/rollenzuweisung.md` ausgefüllt | ☐ Ja ☐ Nein | __________________ |
| Technische Umsetzung der Rollen im System geprüft | ☐ Ja ☐ Nein | __________________ |
| Einweisung ADMIN durchgeführt und dokumentiert | ☐ Ja ☐ Nein | __________________ |
| Einweisung REVIEWER durchgeführt und dokumentiert | ☐ Ja ☐ Nein | __________________ |
| Einweisung TECH (falls vorhanden) durchgeführt | ☐ Ja ☐ Nein | __________________ |

---

## 6. Datenschutz und IT-Sicherheit

| Prüffrage | Ergebnis | Bemerkung |
|---|---|---|
| VVT (Art. 30 DSGVO) für arbeitszeit erstellt und ausgefüllt | ☐ Ja ☐ Nein | __________________ |
| Einbindung in das IT-Sicherheitskonzept der Praxis (inkl. § 75b SGB V, falls relevant) dokumentiert | ☐ Ja ☐ Nein | __________________ |
| Dateisystemrechte für Datenbank und Exportverzeichnis geprüft | ☐ Ja ☐ Nein | __________________ |
| Konkretes Verfahren für Backup-Rotation und Aufbewahrung festgelegt | ☐ Ja ☐ Nein | __________________ |
| Verfahren bei Datenschutzvorfall (Art. 33/34 DSGVO) festgelegt | ☐ Ja ☐ Nein | __________________ |

---

## 7. Mängel, Abweichungen und Auflagen

Hier werden verbleibende Abweichungen dokumentiert sowie Auflagen, unter denen eine Freigabe trotzdem erteilt wird.

| Nr. | Beschreibung der Abweichung / des Mangels | Kategorie (fachlich/technisch/organisatorisch) | Schweregrad (niedrig/mittel/hoch) | Maßnahme | Frist | Verantwortlich |
|---|---|---|---|---|---|---|
| 1 | __________________ | __________ | _______ | __________________ | __________________ | __________________ |
| 2 | __________________ | __________ | _______ | __________________ | __________________ | __________________ |

☐ Es bestehen **keine** bekannten wesentlichen Mängel, die den Produktivbetrieb verhindern.  
☐ Es bestehen Mängel, die **innerhalb der oben genannten Fristen** zu beheben sind; der Betrieb wird unter diesen Auflagen freigegeben.

---

## 8. Erklärung zur Betriebsfreigabe

Hiermit wird erklärt:

1. Die oben beschriebenen Prüfungen wurden durchgeführt oder verantwortungsvoll stichprobenartig vorgenommen.  
2. Die für den Produktivbetrieb wesentlichen Funktionen von `arbeitszeit` sind auf der Zielumgebung lauffähig.  
3. Die organisatorischen Rahmenbedingungen (Rollen, Prozesse, Datenschutz) sind in der Praxis definiert.  
4. Die Praxis übernimmt die Verantwortung für den Betrieb des Systems im Rahmen der geltenden Gesetze
   (insbesondere ArbZG, DSGVO, BDSG).

> Diese Erklärung ersetzt keine rechtliche Beratung. Sie dokumentiert die interne Entscheidung
> der Praxis, das System `arbeitszeit` produktiv zu nutzen.

---

## 9. Unterschriften

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Praxisleitung / Verantwortliche Stelle | __________________ | __________________ | __________________ |
| Verantwortliche Person für Technik / IT | __________________ | __________________ | __________________ |
| (optional) Datenschutzverantwortliche Person | __________________ | __________________ | __________________ |

---

## 10. Wiederholte Betriebsfreigabe / Änderungen

Bei wesentlichen Änderungen (z.B. Major-Release, Umbau der Infrastruktur, Praxisumzug) kann eine erneute oder ergänzende Betriebsfreigabe notwendig sein.

| Anlass (z.B. Version 1.0.0, Hardwaretausch, OS-Upgrade) | Datum | Kurzbeschreibung der erneuten Prüfung | Ergebnis | Verantwortlich | Unterschrift |
|---|---|---|---|---|---|
| __________________ | __________________ | __________________ | ☐ freigegeben ☐ nicht freigegeben | __________________ | __________________ |
| __________________ | __________________ | __________________ | ☐ freigegeben ☐ nicht freigegeben | __________________ | __________________ |

---

## 11. Wann ist dieses Protokoll erneut zu verwenden?

Dieses Betriebsfreigabe-Protokoll ist nicht nur einmalig zu verwenden, sondern
bei bestimmten Änderungen erneut auszufüllen oder in Abschnitt 10 zu ergänzen.

Eine **erneute Betriebsfreigabe** (neues Protokoll oder Ergänzung zu Abschnitt 10)
ist erforderlich, wenn mindestens einer der folgenden Punkte zutrifft:

- **Neue Hauptversion des Systems**
  - Versionssprung im `pyproject.toml` im MAJOR-Teil (z.B. `0.9.x` → `1.0.0`
    oder `1.x` → `2.0.0`).
  - Einführung wesentlicher neuer Kernfunktionen oder Änderungen, die das bisherige
    Verhalten fachlich spürbar beeinflussen (z.B. neue ArbZG-Prüflogik).

- **Wechsel oder wesentliche Änderung der Hardware-Plattform**
  - Austausch des Terminalgeräts (PC/NUC/Thin Client).
  - Austausch des RFID-Readers oder USB-Numpads durch ein anderes Modell.
  - Änderung der Anschlussart mit möglichem Einfluss auf das Verhalten
    (z.B. neue Dockingstation, anderer USB-Hub).

- **Relevante Infrastrukturänderungen**
  - Umzug der SQLite-Datenbank auf ein anderes Laufwerk oder Dateisystem.
  - Einführung oder Wechsel der NAS-Lösung für Backups.
  - Wechsel des Betriebssystems oder Major-Upgrade (z.B. neue Linux-Hauptversion).
  - Änderung der Backup- und Restore-Strategie (Rotation, zusätzlicher Standort).

- **Bedeutende fachliche oder organisatorische Änderungen**
  - Anpassung der fachlichen Regeln zur Zeiterfassung oder den Prüffunktionen
    (Pausen, Ruhezeiten, Höchstarbeitszeiten).
  - Änderung des Rollen- oder Berechtigungskonzepts (z.B. neue Rollen, andere Zuständigkeiten).
  - Praxisumzug oder Eröffnung weiterer Standorte mit eigenen Terminals.
  - Wechsel der Praxisleitung / verantwortlichen Stelle mit neuer Zuständigkeitsverteilung.

- **Sicherheits- oder Datenschutzanlässe**
  - Schwerwiegender Sicherheits- oder Datenschutzvorfall, nach dem das System
    oder seine Konfiguration überarbeitet wurde.
  - Ergebnisse einer Datenschutz- oder IT-Sicherheitsprüfung, die wesentliche
    Maßnahmen am System erforderlich gemacht haben.

In Zweifelsfällen kann die Praxis entscheiden, ob eine kurze Ergänzung in
Abschnitt 10 („Wiederholte Betriebsfreigabe / Änderungen“) genügt oder ein neues,
vollständig ausgefülltes Protokoll angelegt wird.

---
## 12. Bezug zu anderen Dokumenten

Dieses Betriebsfreigabe-Protokoll steht in Zusammenhang mit:

- `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`
- `docs/datenschutz/vvt_arbeitszeit_v1.md`
- `docs/betrieb/rollenzuweisung.md`
- `docs/betrieb/hardware_inbetriebnahme_protokoll.md`
- `CHANGELOG.md` (Versionen / Releases)

Die unterschriebene Fassung ist zusammen mit diesen Unterlagen revisionssicher aufzubewahren.