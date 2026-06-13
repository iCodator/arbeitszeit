# Restore-Checkliste – System „arbeitszeit“

**System:** arbeitszeit  
**Dokumenttyp:** Operative Restore-Checkliste  
**Version:** 1.0  
**Stand:** 2026-06-13  
**Empfohlener Ablageort im Repository:** `docs/betrieb/restore_checkliste.md`

> Diese Checkliste dient der kontrollierten Wiederherstellung des Systems `arbeitszeit` aus einem Backup. Sie ergänzt die Betriebsdokumentation, die Backup-Dokumentation und das Betriebsfreigabe-Protokoll. Sie ist bewusst knapp gehalten und für den operativen Einsatz gedacht.

---

## 1. Zweck

Die Checkliste soll sicherstellen, dass ein Restore nur geplant, dokumentiert und nachvollziehbar durchgeführt wird. Ziel ist nicht nur die technische Wiederherstellung, sondern auch die saubere organisatorische Freigabe und Nachdokumentation.

---

## 2. Voraussetzungen vor dem Restore

| Prüffrage | Ja/Nein | Bemerkung |
|---|---|---|
| Es liegt ein konkreter Restore-Anlass vor (z. B. Datenverlust, Hardwaredefekt, beschädigte DB). | ☐ Ja ☐ Nein | __________________ |
| Die Durchführung wurde von der verantwortlichen Stelle freigegeben. | ☐ Ja ☐ Nein | __________________ |
| Das zu verwendende Backup wurde eindeutig identifiziert. | ☐ Ja ☐ Nein | __________________ |
| Das Datum/Uhrzeit des Backups ist bekannt. | ☐ Ja ☐ Nein | __________________ |
| Es ist klar, ob auch Exportdateien wiederhergestellt werden sollen. | ☐ Ja ☐ Nein | __________________ |
| Der aktuelle Ist-Zustand wurde vor dem Restore zusätzlich gesichert. | ☐ Ja ☐ Nein | __________________ |
| Die Rollen/Zuständigkeiten für den Restore sind geklärt (`ADMIN` / `TECH`). | ☐ Ja ☐ Nein | __________________ |

---

## 3. Restore-Freigabe

| Feld | Eintrag |
|---|---|
| Anlass des Restore | __________________________________________ |
| Freigabe erteilt durch | __________________________________________ |
| Datum / Uhrzeit der Freigabe | __________________________________________ |
| Durchführende Person | __________________________________________ |
| Verwendetes Backup | __________________________________________ |
| Restore mit Exportdateien? | ☐ Ja ☐ Nein |

> Restore-Vorgänge sollen nur durch berechtigte Personen und nur nach dokumentierter Freigabe durchgeführt werden.

---

## 4. Technische Durchführung

### 4.1 Vorbereitung

| Schritt | Erledigt | Bemerkung |
|---|---|---|
| Anwendung / Terminalbetrieb gestoppt | ☐ Ja ☐ Nein | __________________ |
| Admin-CLI / sonstige Zugriffe beendet | ☐ Ja ☐ Nein | __________________ |
| Aktuelle Datenbankkopie vor Restore erstellt | ☐ Ja ☐ Nein | __________________ |
| Relevante Log-/Fehlerhinweise gesichert | ☐ Ja ☐ Nein | __________________ |

### 4.2 Wiederherstellung

| Schritt | Erledigt | Bemerkung |
|---|---|---|
| Restore aus identifiziertem Backup durchgeführt | ☐ Ja ☐ Nein | __________________ |
| Falls vorgesehen: Exportdateien mit wiederhergestellt | ☐ Ja ☐ Nein | __________________ |
| Schreib-/Leserechte der wiederhergestellten Dateien geprüft | ☐ Ja ☐ Nein | __________________ |
| Anwendung wieder gestartet | ☐ Ja ☐ Nein | __________________ |

---

## 5. Funktionsprüfung nach Restore

| Prüfung | Ergebnis | OK? |
|---|---|---|
| Datenbank lässt sich öffnen | __________________ | ☐ Ja ☐ Nein |
| Terminal-UI startet fehlerfrei | __________________ | ☐ Ja ☐ Nein |
| Admin-CLI startet fehlerfrei | __________________ | ☐ Ja ☐ Nein |
| Stichprobenhafte Buchungen / Mitarbeiterdaten vorhanden | __________________ | ☐ Ja ☐ Nein |
| Systemcheck erfolgreich oder plausibel | __________________ | ☐ Ja ☐ Nein |
| Backup-/Exportpfade weiterhin korrekt | __________________ | ☐ Ja ☐ Nein |
| Restore-Ereignis dokumentiert | __________________ | ☐ Ja ☐ Nein |

---

## 6. Bewertung des Restore-Ergebnisses

| Feld | Eintrag |
|---|---|
| Restore erfolgreich? | ☐ Ja ☐ Nein |
| Einschränkungen / offene Punkte | __________________________________________ |
| Weitere Maßnahmen erforderlich? | ☐ Ja ☐ Nein |
| Falls ja: welche? | __________________________________________ |

---

## 7. Nachdokumentation

Nach dem Restore sind mindestens folgende Unterlagen zu prüfen bzw. zu ergänzen:

- `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`
- `docs/betrieb/betriebsfreigabe_protokoll.md` (Abschnitt Wiederholte Betriebsfreigabe / Änderungen)
- `docs/betrieb/backup_zeitplan_und_automatisierung.md` (falls das Restore auf Backup-Probleme hinweist)
- internes Störungs- oder Maßnahmenprotokoll der Praxis

---

## 8. Abschluss und Unterschriften

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Durchführende Person | __________________ | __________________ | __________________ |
| Verantwortliche Stelle / Freigabe | __________________ | __________________ | __________________ |
| Optional: technische Prüfung | __________________ | __________________ | __________________ |

---

## 9. Änderungshistorie

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 2026-06-13 | Erstfassung Restore-Checkliste |
