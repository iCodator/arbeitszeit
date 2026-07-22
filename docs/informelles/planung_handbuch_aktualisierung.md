# Plan: Schrittweise Handbuch-Aktualisierung

**Stand:** 2026-07-22
**Basis-Commits:** `0e4bc73` (letzter Docs-Stand) bis `d71b3b2` (HEAD)
**Ausgeschlossen:** `docs/08_planung_intern/`, `docs/09_diagramme/`

---

## Auslösende Commits (Codeänderungen)

| Commit | Beschreibung | Betrifft |
| --- | --- | --- |
| `4ea03c8` | NumPad entfernt — Buchungstyp positionsbasiert | Hardware, Präsentation, Infra, Installation |
| `da88fe8` | `booking.grace_seconds_after_numpad_select` entfernt | Config, Infra, Show-Config |
| `4358a18` | Offene Vortagsschicht: neues Audit-Event | Domain, Audit |
| `49fc17c` | `audit open-shifts` — neuer CLI-Befehl | Befehlsreferenz, Präsentation |
| `fcd4c93` | COME nach abgeschlossenem Tagesablauf abweisen | Domain |
| `374feb3` | 2. Scan Kurztag → GO statt BREAK\_START (§ 4 ArbZG) | Domain, Application |
| `553705a` | 3. Scan Kurztag → `InvalidBookingSequenceError` | Domain, Application |
| `ebd136f` | `_RFID_READ_TIMEOUT` entfernt — internes 1-s-Poll | Infra, Architektur |
| `1c70e6e` | `DebouncedHardwareReader` — 3-s-Entprellung | Infra, Präsentation |

---

## Schritt 1 — Kernhandbuch: Buchungsablauf korrigieren

**Priorität:** kritisch — enthält aktiv falsche Beschreibungen.

### 1.1 `docs/02_anwender/handbuch.md`

Falsch/veraltet:

- Zeile 73: „nimmt Buchungen per Numpad und RFID-Karte entgegen" → nur RFID
- Zeilen 134, 143: `numpad = "..."` in config.toml-Beispiel → entfernen
- Zeilen 269, 395 ff.: `--numpad "..."` in Startbefehlen → entfernen
- Zeilen 289–301: „Schritt 1 — Buchungsart auf dem Numpad wählen" → ersetzen durch positionsbasierte Ablaufbeschreibung (1. Scan → COME, 2. Scan → BREAK\_START usw.)
- Zeile 300–301: `booking.grace_seconds_after_numpad_select` → entfernen
- Zeile 685: „RFID-Reader und Numpad erreichbar" → nur RFID-Reader
- Zeile 713: „# Numpad und RFID-Reader interaktiv testen" → anpassen
- Zeile 832: „gibt Numpad und RFID-Reader frei" → nur RFID-Reader

Neu hinzuzufügen:

- Buchungsablauf neu: Karte auflegen → Buchungstyp automatisch bestimmt (COME→BREAK\_START→BREAK\_END→GO)
- Kurztag-Regel: bei Solldauer ≤ 6 h entfällt Pause (2. Scan → GO, 3. Scan → Fehlermeldung)
- DebouncedHardwareReader: Doppel-Scan-Schutz (3 s), für Anwender relevant als Hinweis „Karte einmal kurz aufhalten reicht"

---

## Schritt 2 — Modulhandbücher Präsentation

### 2.1 `docs/02_anwender/module/handbuch_presentation_laien.md`

- Zeile 145: „Numpad, halten anschließend ihre RFID-Karte vor den Reader" → Ablauf rein RFID, kein Numpad-Schritt mehr
- Buchungsablauf neu beschreiben: Karte einmal auflegen = eine Buchung

### 2.2 `docs/02_anwender/module/handbuch_presentation_it.md`

- Zeile 207: `--numpad NAME` aus CLI-Argumenttabelle entfernen
- Zeile 224: `booking.grace_seconds_after_numpad_select lesen` → entfernen
- `DebouncedHardwareReader` als neuen Wrapper in der Startsequenz ergänzen: `reader = DebouncedHardwareReader(EvdevHardwareReader(rfid_path=rfid_path))`
- Ablauf `run()` aktualisieren: kein `numpad_path`, kein grace-Wert
- Neuen CLI-Befehl `audit open-shifts` in Kontext Präsentationsschicht erwähnen (gehört zu `admin_cli/audit.py`)

---

## Schritt 3 — Modulhandbücher Infrastruktur

### 3.1 `docs/02_anwender/module/handbuch_infrastructure_it.md`

- Zeile 12: „RFID/Numpad-Hardware" → „RFID-Hardware"
- Zeile 46: `TerminalConfig`-Tabelle: `numpad: str | None` entfernen
- Zeile 75: config.toml-Beispiel: `numpad = "..."` entfernen
- Zeile 144: `EvdevHardwareReader`-Beschreibung: kein Numpad mehr
- Zeile 149: „initialisiert `EvdevHardwareReader` mit Numpad-Pfad" → nur RFID-Pfad; `DebouncedHardwareReader` als Wrapper ergänzen
- Zeile 183: `run_system_check(db_path, *, numpad_path, rfid_path, ...)` → `numpad_path` entfernen
- Zeile 190: Tabelle Pflicht-Keys: `booking.grace_seconds_after_numpad_select` entfernen (Pflicht-Keys jetzt: `app.timezone`, `backup.nas_enabled`, `backup.nas_path`)
- Zeile 195: `_check_devices`-Zeile: nur noch `rfid_path`, kein `numpad_path`
- Neuer Abschnitt: `DebouncedHardwareReader` — Klasse, Debounce-Fenster (3 s), `_last_accepted`-Mechanismus, Invariante (Timestamp nur bei Accept aktualisieren)
- Neuer Abschnitt: `_RFID_READ_TIMEOUT` entfernt, internes 1-s-Poll-Intervall in `_read_rfid_uid()`

### 3.2 `docs/02_anwender/module/handbuch_infrastructure_laien.md`

- Zeile 13: „RFID, Numpad" → nur RFID
- Zeile 29: config.toml-Beispiel: `numpad = "..."` entfernen
- Zeile 85: „RFID-Reader, Numpad" → nur RFID-Reader
- Doppel-Scan-Schutz laienverständlich erläutern: „Wird die Karte innerhalb von 3 Sekunden nochmals gehalten, ignoriert das System den zweiten Scan automatisch."

---

## Schritt 4 — Modulhandbücher Domain und Application

### 4.1 `docs/02_anwender/module/handbuch_domain_it.md`

- Zeile 251: `TERMINAL`-Beschreibung: „RFID/Numpad-Terminal" → „RFID-Terminal"
- Neuer Abschnitt Buchungssequenz-Logik:
  - Standardsequenz: COME → BREAK\_START → BREAK\_END → GO
  - Kurztag (Solldauer ≤ 6 h, § 4 ArbZG): COME → GO (kein BREAK), 3. Scan → `InvalidBookingSequenceError` mit „Kurztag"-Hinweis
  - COME nach abgeschlossenem Tagesablauf → `InvalidBookingSequenceError`
- `_derive_for_short_day()` und `_is_short_day()` als neue Helfer beschreiben
- Neues Audit-Event: `OPEN_SHIFT_PREVIOUS_DAY_DETECTED` — wann und wie ausgelöst

### 4.2 `docs/02_anwender/module/handbuch_domain_laien.md`

- Regelabschnitt „Buchungsreihenfolge" ergänzen: Kurztag-Ausnahme verständlich erklären
- „Warum kommt nach dem Kommen direkt das Gehen?" — laienverständliche Erklärung der § 4 ArbZG-Regel

### 4.3 `docs/02_anwender/module/handbuch_application_it.md`

- `derive_booking_type()` und neue Hilfsfunktionen dokumentieren
- Kurztag-Logik in Ablaufbeschreibung ergänzen

### 4.4 `docs/02_anwender/module/handbuch_application_laien.md`

- Buchungsablauf im Hintergrund: Kurztag-Variante ergänzen

---

## Schritt 5 — Modulhandbücher Audit und Show-Config

### 5.1 `docs/02_anwender/module/handbuch_audit_it.md`

- Zeile 76: `run_system_check(db_path, *, numpad_path, rfid_path, ...)` → `numpad_path` entfernen
- Zeile 97: Tabelle Pflicht-Keys: `booking.grace_seconds_after_numpad_select` entfernen
- Zeile 102: `_check_devices`-Zeile: nur noch RFID-Gerät
- Neues Audit-Event `OPEN_SHIFT_PREVIOUS_DAY_DETECTED` dokumentieren
- Neuen CLI-Befehl `audit open-shifts` dokumentieren (Signatur, Output-Format)

### 5.2 `docs/02_anwender/module/handbuch_audit_laien.md`

- Zeile 44: „RFID-Reader oder Numpad nicht erreichbar" → nur RFID-Reader
- Hinweis auf `audit open-shifts` für Praxisleitung ergänzen

### 5.3 `docs/02_anwender/module/handbuch_show_config_it.md`

- Zeile 99: `terminal.numpad` aus Konfigurationsschlüsselliste entfernen
- Zeile 123: `booking.grace_seconds_after_numpad_select 30` aus Beispielausgabe entfernen
- Zeile 170: `"terminal_numpad": "..."` aus JSON-Beispiel entfernen

### 5.4 `docs/02_anwender/module/handbuch_show_config_laien.md`

- Zeile 42: `booking.grace_seconds_after_numpad_select` aus Beispielausgabe entfernen
- Zeile 62: Tabelleneintrag für `booking.grace_seconds_after_numpad_select` entfernen

---

## Schritt 6 — Systemübersicht

### 6.1 `docs/02_anwender/module/handbuch_overview_laien.md`

- Zeile 19: „RFID-Karte oder Numpad" → nur RFID-Karte
- Zeile 32: Tabellenspalte „RFID-Karte + Numpad" → „RFID-Karte"

### 6.2 `docs/02_anwender/module/handbuch_overview_it.md`

- Hardware-Komponenten aktualisieren: kein Numpad
- `DebouncedHardwareReader` in der Komponentenübersicht ergänzen

---

## Schritt 7 — Datenbankschema

### 7.1 `docs/02_anwender/module/handbuch_datenbankschema_it.md`

- Zeile 269: `booking.grace_seconds_after_numpad_select` aus `system_config`-Beschreibung entfernen
- Ggf. Abschnitt `system_config`-Seed-Werte aktualisieren (Schlüssel existiert nach Migration `0007` nicht mehr)

---

## Schritt 8 — Befehlsreferenz

### 8.1 `docs/03_installation_technik/befehlsreferenz.md`

- Zeile 920: „und Numpad-Eingaben" → entfernen
- Zeile 928, 937: `--numpad` aus Startbefehl und Argumenttabelle entfernen
- Zeile 948: Numpad-Tastenbeschreibung ersetzen durch positionsbasierten Ablauf
- Zeilen 1008, 1021: `--numpad` aus `verify_hardware`-Befehl entfernen
- Zeilen 1056–1072: Numpad-Beschreibung in `verify_hardware` anpassen
- Neuer Abschnitt: `admin audit open-shifts` — Syntax, Optionen, Beispielausgabe

---

## Schritt 9 — Installationsanleitung

### 9.1 `docs/03_installation_technik/installationsanleitung.md`

- Zeile 44: „per RFID-Karte und Numpad" → nur RFID-Karte
- Zeile 95: Numpad aus Hardware-Voraussetzungen entfernen
- Zeile 382 ff.: `--numpad`-Argument aus Startbefehl-Beispielen entfernen
- Zeile 411: „Schritt 9: Zugriff auf RFID-Reader und Numpad" → nur RFID-Reader
- Zeilen 424, 429–430, 469 ff.: alle Numpad-Beispiele entfernen/anpassen
- Zeilen 493–494: Numpad-Smoke-Test → RFID-Smoke-Test anpassen
- Zeile 759: `terminal.numpad` aus config.toml-Beschreibung entfernen
- Zeile 764: `--numpad`-Erklärung entfernen

### 9.2 `docs/03_installation_technik/hardware.md`

- USB-Numpad-Abschnitt entfernen (Zeile 4 ff.)
- Nur noch RFID-Reader dokumentieren

---

## Schritt 10 — Betriebsdokumentation

### 10.1 `docs/04_betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`

- Zeile 98: `--numpad /dev/input/eventX` aus Startbefehl entfernen
- Zeile 103: „`--numpad` und `--rfid` sind Pflichtargumente" → nur `--rfid`
- Hardware-Beschreibung: Numpad entfernen
- Systemkomponenten: `DebouncedHardwareReader` ergänzen

### 10.2 `docs/04_betrieb/hardware_inbetriebnahme_protokoll.md`

- Zeile 10, 37, 47: USB-Numpad aus Hardware-Tabellen entfernen
- Zeile 69: „RFID-Reader und Numpad am echten Terminal" → nur RFID-Reader
- Zeilen 86, 94: Numpad-Schritte aus Smoke-Test entfernen
- Smoke-Test-Ablauf neu: Karte auflegen → automatischer Buchungstyp → Feedback

---

## Schritt 11 — Architektur-Dokumentation

### 11.1 `docs/06_architektur/infrastructure/evdev_reader.md`

- `_RFID_READ_TIMEOUT`-Beschreibung entfernen
- 1-s-internes-Poll-Intervall dokumentieren
- SIGTERM-Reaktion erklären (interner Loop, kein externer Timeout-Parameter)

### 11.2 `docs/06_architektur/infrastructure/ueberarbeiteter_abschnitt_evdev_reader.md`

- Komplett überarbeiten: Numpad-Beschreibung (Zeilen 7, 29, 79) entfernen
- Nur noch RFID-Karte als Eingabegerät
- Neuen Abschnitt `DebouncedHardwareReader` ergänzen (oder Verweis auf Diagramm)

---

## Schritt 12 — Datenschutz und Sicherheit

### 12.1 `docs/05_datenschutz_recht/SECURITY.md`

- Hardware-Beschreibung prüfen: Numpad entfernen falls vorhanden
- `DebouncedHardwareReader` im Bedrohungsmodell ggf. ergänzen (Entprellmechanismus als Schutz vor unbeabsichtigten Doppelbuchungen)

---

## Ausschlüsse (nicht aktualisieren)

| Dokument / Verzeichnis | Begründung |
| --- | --- |
| `docs/01_normativ/pflichtenheft_arbeitszeit_v6.md` | Normatives Dokument — nur mit expliziter fachlicher Freigabe ändern |
| `docs/01_normativ/regelwerk_arbeitszeit_v5.md` | Normatives Dokument — wie oben |
| `docs/01_normativ/anlage_einhaltung_pflichtenheft.md` | Abgeleitetes Normativdokument — prüfen, ob Numpad-Verweise enthalten, ggf. in separatem Schritt |
| `docs/07_pruefberichte/**` | Historische Prüfberichte — unveränderlich |
| `docs/04_betrieb/betriebsfreigabe_protokoll.md` | Formales Abnahmeprotokoll — historisches Dokument |
| `docs/04_betrieb/nachweise/**` | Testmatrix — historisch |
| `docs/audits/**` | Audit-Berichte — historisch |
| `docs/claude_coding/**` | Interne Arbeitsanweisungen |
| `docs/prompts/**` | Prompt-Vorlagen |
| `docs/04_betrieb/backup_zeitplan_und_automatisierung.md` | Nicht durch RFID-Änderungen berührt |
| `docs/04_betrieb/restore_checkliste.md` | Nicht berührt |
| `docs/04_betrieb/rollenzuweisung.md` | Nicht berührt |
| `docs/05_datenschutz_recht/vvt_arbeitszeit_v1.md` | Nicht berührt |
| `docs/05_datenschutz_recht/datenschutz_und_tom_arbeitszeit_v1_0.md` | Nicht berührt |
| `docs/05_datenschutz_recht/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` | Nicht berührt |
| `docs/06_architektur/adr/**` | Architekturentscheidungen — historisch korrekt |
| `docs/06_architektur/domain/enums.md` | Nicht berührt |

---

## Reihenfolge der Umsetzung

| Schritt | Dokumente | Grund |
| --- | --- | --- |
| 1 | `handbuch.md` | Einstiegspunkt, höchste Sichtbarkeit |
| 2 | `handbuch_presentation_*.md` | Buchungsablauf direkt sichtbar |
| 3 | `handbuch_infrastructure_*.md` | Hardware-Änderungen, DebouncedHardwareReader |
| 4 | `handbuch_domain_*.md`, `handbuch_application_*.md` | Kurztag-Regel, Buchungssequenz |
| 5 | `handbuch_audit_*.md`, `handbuch_show_config_*.md` | Audit-Events, Config-Keys |
| 6 | `handbuch_overview_*.md`, `handbuch_datenbankschema_it.md` | Systemübersicht, Schema |
| 7 | `befehlsreferenz.md` | CLI-Referenz, `audit open-shifts` |
| 8 | `installationsanleitung.md`, `hardware.md` | Installation ohne Numpad |
| 9 | `betriebsdokumentation_*.md`, `hardware_inbetriebnahme_protokoll.md` | Betrieb |
| 10 | `evdev_reader.md`, `ueberarbeiteter_abschnitt_evdev_reader.md` | Architektur |
| 11 | `SECURITY.md` | Sicherheitsmodell |
