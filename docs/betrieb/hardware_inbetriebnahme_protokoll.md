# Hardware-Inbetriebnahme- und Smoke-Test-Protokoll – arbeitszeit

**System:** arbeitszeit  
**Dokumenttyp:** Inbetriebnahme- und Abnahmeprotokoll Hardware  
**Version:** 1.0  
**Stand:** 2026-06-12  
**Ablageort:** `docs/betrieb/hardware_inbetriebnahme_protokoll.md`

> Dieses Formular dient als Vorlage für die Erstinbetriebnahme und wesentliche Änderungen
> der Hardware-Umgebung (RFID-Reader, USB-Numpad, Terminalgerät, NAS).
> Es ist vollständig auszufüllen und unterschrieben aufzubewahren.

---

## 1. Praxis und Systemumgebung

| Feld | Eintrag |
|---|---|
| Praxis / Standort | __________________________________________ |
| Adresse | __________________________________________ |
| Bezeichnung des Zeiterfassungsterminals | __________________________________________ |
| Hardware-Typ (PC / Thin Client / NUC / …) | __________________________________________ |
| Betriebssystem / Version | __________________________________________ |
| Datum der Inbetriebnahme | __________________________________________ |
| Verantwortliche Person (Praxisleitung) | __________________________________________ |
| Verantwortliche Person (technische Betreuung) | __________________________________________ |

---

## 2. Hardware-Komponenten

### 2.1 Überblick

| Komponente | Hersteller / Modell | Seriennummer | Anschluss | Bemerkung |
|---|---|---|---|---|
| RFID-Reader | __________________ | __________________ | USB | __________________ |
| USB-Numpad | __________________ | __________________ | USB | __________________ |
| Terminal-Display | __________________ | __________________ | HDMI/DP | __________________ |
| Netzwerk (LAN/WLAN) | __________________ | __________________ | RJ45/WLAN | __________________ |
| NAS (für Backup) | __________________ | __________________ | IP / Pfad | __________________ |

### 2.2 Gerätedateien (Linux)

| Komponente | Gerätedatei (evdev) | Leserechte geprüft | Bemerkung |
|---|---|---|---|
| RFID-Reader | `/dev/input/event____` | ☐ Ja ☐ Nein | __________________ |
| USB-Numpad | `/dev/input/event____` | ☐ Ja ☐ Nein | __________________ |

> Hinweis: Die Zuordnung der Gerätedateien ist durch `evtest` oder vergleichbare
> Werkzeuge zu prüfen. Die Identifikation sollte im technischen Notizbuch festgehalten werden.

---

## 3. Systemkonfiguration arbeitszeit

| Konfigurationspunkt | Wert | Prüfergebnis |
|---|---|---|
| Pfad zur SQLite-Datenbank (`--db`) | __________________ | ☐ OK ☐ nicht OK |
| Terminal-ID (`--terminal-id`) | __________________ | ☐ OK ☐ nicht OK |
| `backup.backup_dir` (system_config) | __________________ | ☐ OK ☐ nicht OK |
| `export.export_dir` (system_config) | __________________ | ☐ OK ☐ nicht OK |
| `time_monitor.jump_threshold_seconds` | __________________ | ☐ OK ☐ nicht OK |
| NAS-Pfad für Backup (falls genutzt) | __________________ | ☐ OK ☐ nicht OK |

---

## 4. Smoke-Test – Terminal-UI

**Ziel:** Nachweis, dass Buchungen mit RFID-Reader und Numpad am echten Terminal
grundsätzlich funktionieren, ohne jedes Detail fachlich zu prüfen.

### 4.1 Testvorbereitung

| Punkt | Erledigt | Bemerkung |
|---|---|---|
| Test-Mitarbeiter im System angelegt | ☐ Ja ☐ Nein | __________________ |
| Test-RFID-Karte dem Mitarbeiter zugeordnet | ☐ Ja ☐ Nein | __________________ |
| Terminal-UI mit korrekten Parametern gestartet | ☐ Ja ☐ Nein | `python -m arbeitszeit.presentation.terminal_ui.main --db … --terminal-id …` |

### 4.2 Testfälle

1. **Kommen-Buchung**

| Schritt | Beobachtung | OK? |
|---|---|---|
| Numpad-Taste für „Kommen“ gedrückt | ____________________________________ | ☐ Ja ☐ Nein |
| RFID-Karte an Reader gehalten | ____________________________________ | ☐ Ja ☐ Nein |
| Buchungsbestätigung im Terminal angezeigt | ____________________________________ | ☐ Ja ☐ Nein |

2. **Gehen-Buchung**

| Schritt | Beobachtung | OK? |
|---|---|---|
| Numpad-Taste für „Gehen“ gedrückt | ____________________________________ | ☐ Ja ☐ Nein |
| RFID-Karte an Reader gehalten | ____________________________________ | ☐ Ja ☐ Nein |
| Buchungsbestätigung im Terminal angezeigt | ____________________________________ | ☐ Ja ☐ Nein |

3. **Pause Start / Pause Ende**

| Testfall | Beobachtung | OK? |
|---|---|---|
| „Pause Start“ + Karte | ____________________________________ | ☐ Ja ☐ Nein |
| „Pause Ende“ + Karte | ____________________________________ | ☐ Ja ☐ Nein |

4. **Unbekannte Karte**

| Schritt | Beobachtung | OK? |
|---|---|---|
| Unbekannte/gesperrte Karte scannen | Meldung „unbekannte Karte“ o. ä. | ☐ Ja ☐ Nein |

### 4.3 Prüfung der Datenspeicherung

| Prüfung | Ergebnis | OK? |
|---|---|---|
| Testbuchungen im Admin-CLI sichtbar (`bookings list`) | __________________ | ☐ Ja ☐ Nein |
| device_events-Einträge vorhanden | __________________ | ☐ Ja ☐ Nein |
| system_events ohne Fehler während des Tests | __________________ | ☐ Ja ☐ Nein |

---

## 5. Smoke-Test – Admin-CLI

**Ziel:** Nachweis, dass grundlegende Administrationsfunktionen am Zielsystem lauffähig sind.

| Test | Befehl | Ergebnis | OK? |
|---|---|---|---|
| Systemcheck | `python -m arbeitszeit.infrastructure.system_check --db …` | __________________ | ☐ Ja ☐ Nein |
| Mitarbeiterliste | `python -m arbeitszeit.presentation.admin_cli.main --db … employees list` | __________________ | ☐ Ja ☐ Nein |
| Buchungsübersicht Test-Mitarbeiter | `… bookings list --employee …` | __________________ | ☐ Ja ☐ Nein |
| CSV-Export | `… reports export csv …` | __________________ | ☐ Ja ☐ Nein |
| PDF-Export | `… reports export pdf …` | __________________ | ☐ Ja ☐ Nein |

---

## 6. Smoke-Test – Backup und NAS (falls vorhanden)

| Test | Befehl / Vorgehen | Ergebnis | OK? |
|---|---|---|---|
| Lokales Backup erstellt | `python scripts/backup.py --db … --backup-dir …` | __________________ | ☐ Ja ☐ Nein |
| Backup-Datei im Backup-Verzeichnis sichtbar |  | __________________ | ☐ Ja ☐ Nein |
| NAS-Spiegelung (falls konfiguriert) | `python scripts/backup.py … --nas-path …` | __________________ | ☐ Ja ☐ Nein |
| NAS-Verzeichnis enthält aktuelle Sicherung |  | __________________ | ☐ Ja ☐ Nein |

---

## 7. Abweichungen und Maßnahmen

Hier sind alle Abweichungen (Fehler, Auffälligkeiten) zu dokumentieren sowie
die vereinbarten Maßnahmen:

| Nr. | Abweichung | Schweregrad (niedrig/mittel/hoch) | Maßnahme | Verantwortlich | Frist | Erledigt am |
|---|---|---|---|---|---|---|
| 1 | __________________ | _______ | __________________ | __________________ | __________________ | __________________ |
| 2 | __________________ | _______ | __________________ | __________________ | __________________ | __________________ |

---

## 8. Abnahme der Hardware-Inbetriebnahme

Mit den folgenden Unterschriften wird bestätigt, dass:

- die oben beschriebenen Tests durchgeführt wurden,
- die grundlegende Funktion von Terminal-UI, Admin-CLI, Backup und (falls vorhanden) NAS
  auf der Zielhardware nachgewiesen wurde,
- offene Abweichungen und Maßnahmen dokumentiert sind.

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Praxisleitung / Verantwortliche Stelle | __________________ | __________________ | __________________ |
| Technische Betreuung | __________________ | __________________ | __________________ |
| (optional) Datenschutzverantwortliche Person | __________________ | __________________ | __________________ |

---

## 9. Wiederholte Tests / Änderungen

Bei relevanten Änderungen an Hardware, Betriebssystem oder Netzwerkkonfiguration
ist dieses Protokoll zu aktualisieren oder ein neues Protokoll anzulegen.

| Anlass (z.B. Austausch Reader, OS-Upgrade) | Datum | Kurzbeschreibung der erneut durchgeführten Tests | Verantwortlich | Unterschrift |
|---|---|---|---|---|
| __________________ | __________________ | __________________ | __________________ | __________________ |
| __________________ | __________________ | __________________ | __________________ | __________________ |

---

## 10. Bezug zu weiteren Dokumenten

Dieses Protokoll ist fachlich verknüpft mit:

- `docs/informelles/betriebsdokumentation_arbeitszeit_v1.md`
- `docs/datenschutz/vvt_arbeitszeit_v1.md`
- `docs/betrieb/rollenzuweisung.md`
- `CHANGELOG.md` (Abschnitte zur Hardware-/Infrastrukturphase)

Es ist zusammen mit diesen Unterlagen aufzubewahren.