# Strukturierte Änderungsanalyse: RFID-only-Umstellung

**Analysebasis:** `planung_gesamt.md` (Ist-Stand), `planung_rfid.md` (Zielbild),
vollständige Codebasis auf Branch `feature/RFID_ONLY`

---

## 1. Kurzüberblick: Ist-Stand vs. RFID-Zielbild

**Ist-Stand:** Das Terminal erwartet zwei sequenzielle Hardware-Eingaben pro
Buchung: zuerst die Buchungstyp-Auswahl über das NumPad (Taste 1–4 →
COME/GO/BREAK\_START/BREAK\_END), dann den RFID-Scan zur Mitarbeiteridentifikation.
Der Buchungstyp ist damit eine explizite Benutzereingabe.
`validate_booking_sequence()` prüft, ob der vom Benutzer gewählte Typ mit dem
bisherigen Tagesverlauf vereinbar ist.

**Zielbild:** Das Terminal akzeptiert ausschließlich RFID-Scans. Der Buchungstyp
wird systemseitig aus dem aktuellen Tageszustand des Mitarbeiters abgeleitet
(Zustandsautomat mit 5 Zuständen und 4 Übergängen). Ein fünfter Scan am selben
Kalendertag ist fachlich unzulässig und wird als Exception behandelt, nicht als
Buchung. Das NumPad und alle daran hängenden Codepfade werden vollständig
entfernt.

Die Änderung ist kein kleineres Refactoring — sie betrifft den Eingabe- und
Ableitungspfad durch alle Schichten: Hardware, Infrastruktur, Buchungsschleife,
Domänendienst und Präsentationsschicht.

---

## 2. Fachliche Delta-Analyse

### 2.1 Regeln, die unverändert bleiben

- **Unveränderliche Buchung als Kern:** Buchungen werden nicht modifiziert;
  Klärung erfolgt über Status, Korrekturen oder Nachträge. Bleibt vollständig
  gültig.
- **Buchungstypen COME/GO/BREAK\_START/BREAK\_END:** Alle vier Typen bleiben
  bestehen; sie werden künftig nur anders erzeugt.
- **device\_events-Kette:** RFID\_SCAN-Record vor BookUseCase-Aufruf,
  `device_event_id` in `time_bookings`. Diese Architektur bleibt vollständig
  gültig. Im Zielbild wird `device_events.payload_json` den abgeleiteten
  (nicht mehr gewählten) Buchungstyp enthalten.
- **Statusmodell:** OPEN/OK/WARN/NEEDS\_REVIEW/CORRECTED/CLOSED\_WITH\_NOTE.
  Unverändert.
- **Compliance-Prüfungen:** `check_break_compliance()`, `check_max_hours()`,
  `check_rest_period()` — inhaltlich unverändert.
- **Administrative Korrektur- und Nachtragspfade:** Bleiben vollständig erhalten;
  werden im Zielbild der einzige zulässige Korrektureinstieg am Terminal.
- **Audit-Log-Pflicht:** Alle Buchungen, Ablehnungen und Exceptions müssen
  nachvollziehbar protokolliert sein. Gilt unverändert, wird im Zielbild um den
  neuen Exception-Typ „Tagesüberbuchung" erweitert.
- **Offene Fälle werden nicht automatisch geschlossen:** Bleibt gültig. Ein
  unvollständiger Tagesablauf (z. B. Zustand 3 ohne 4. Scan/Gehen) muss
  administrativ geklärt werden.
- **Tagesbezug der Zustandslogik:** Das RFID-Planungsdokument spezifiziert
  explizit, dass die Zustandslogik pro Mitarbeitendem und Kalendertag gilt.
  Das entspricht dem bestehenden `list_for_employee_on_day()`-Muster in
  `time_booking_repo`.

### 2.2 Regeln, die sich grundlegend ändern

| Bereich | Ist-Stand | Zielbild |
| --- | --- | --- |
| **Buchungstyp-Quelle** | Explizite NumPad-Eingabe des Mitarbeiters | Systemseitig aus Tageszustand abgeleitet |
| **Eingabereihenfolge** | NumPad → RFID | RFID (einzige Eingabe) |
| **Rolle von `validate_booking_sequence()`** | Prüft, ob ein vorgegebener Typ zulässig ist | Muss um Ableitungsfunktion ergänzt oder ersetzt werden |
| **Interaktionsmodell** | Mitarbeiter wählt bewusst Buchungstyp | Mitarbeiter hat keine Wahl; System entscheidet |
| **Terminalfeedback** | Buchungstyp-Menü wird angezeigt, dann Ergebnis | Nur Ergebnis (abgeleiteter Typ + ggf. Fehlermeldung) |

### 2.3 Regelergänzungen und -präzisierungen

- **Neue fachliche Entität: Tageszustandsautomat.** Der Zustand pro
  Mitarbeitendem und Kalendertag (`0–4`) ist im bestehenden System nicht explizit
  modelliert — er ist implizit aus den Tagesbuchungen ableitbar. Im Zielbild muss
  eine Funktion `derive_booking_state(day_bookings)` → `int` (0–4) existieren,
  auf deren Basis dann `derive_next_booking_type(state)` →
  `BookingType | Exception` entschieden wird.
- **Neuer Exception-Typ: Tagesüberbuchung.** Eine 5. Buchung am selben Tag ist
  im aktuellen Code **kein explizit behandelter Fall.** `validate_booking_sequence()`
  würde bei einem 5. COME-Versuch nach vollständigem Tagesablauf (Zustand 4)
  **keinen Fehler werfen**, weil `open_work=False` und `open_break=False` — die
  `_validate_come`-Prüfung schlägt in diesem Fall nicht an. Dieser Fall muss neu
  implementiert werden.
- **Exception-Logging-Pflicht.** `planung_rfid.md` definiert spezifische
  Pflichtfelder für Exception-Logs (Zeitstempel, RFID-Referenz, Mitarbeiterreferenz
  falls auflösbar, Exception-Typ, Fehlermeldung, Kontext). Diese Detailtiefe ist
  im aktuellen System für `UnknownCardError` bereits durch `audit_log` abgedeckt,
  für den neuen „Tagesüberbuchung"-Fall aber neu.
- **Doppelscan-Entprellung.** In `planung_rfid.md` als optional markiert. Im
  Ist-Stand existiert kein Debounce-Mechanismus.

### 2.4 Fachliche Spannungen

**Spannung 1 — Offene Fälle vs. strikter Ablauf:**
Das bestehende Modell hält offen: „Offene Fälle werden nicht automatisch
geschlossen." Im RFID-Zielbild beginnt ein neuer Kalendertag stets bei Zustand 0.
Das bedeutet: Endet ein Arbeitstag in Zustand 1, 2 oder 3 (fehlende Buchungen),
bleibt der Review-Case offen — der neue Tag startet trotzdem bei Kommen. Das ist
kompatibel, solange der Kalendertagswechsel die Basis bildet und nicht eine
Zustandsbereinigung erzwungen wird. Kein Konflikt, aber eine explizite Klärung
ist angeraten.

**Spannung 2 — `OpenPhaseConflictError` wird unerreichbar:**
Diese Fehlerklasse existiert für den Fall „GO bei offener Pause" (wenn jemand
manuell GO wählt, obwohl BREAK\_START aktiv ist). Im RFID-Zielbild kann diese
Situation nicht mehr eintreten, weil der 3. Scan immer BREAK\_END ableitet und
der 4. Scan immer GO. `OpenPhaseConflictError` und die zugehörige Meldung in
`_DOMAIN_MESSAGES` werden toter Code. Entfernen ist klar, schafft aber einen
klaren Bruch mit bestehendem Testcode.

**Spannung 3 — `validate_booking_sequence()` und ihre Tests:**
Die Funktion prüft, ob ein **vorgegebener** Buchungstyp zulässig ist. Im
RFID-Zielbild wird kein Typ mehr vorgegeben — er wird abgeleitet. Die Funktion
verliert ihre ursprüngliche Rolle als Eingabevalidierung. Ob sie als interne
Konsistenzprüfung im neuen Ableitungspfad weiter genutzt werden kann oder
vollständig ersetzt wird, ist aus dem Planungsdokument nicht eindeutig ableitbar.

---

## 3. Architektur- und Code-Delta

### 3.1 Präsentationsschicht: `presentation/terminal_ui/`

**`main.py`**

| Element | Ist-Stand | Änderungsbedarf |
| --- | --- | --- |
| `_BUCHUNGSARTEN` (Textblock) | Zeigt NumPad-Menü | Vollständig entfernen |
| `run(numpad_device, rfid_device, ...)` | Nimmt NumPad-Gerätename als Pflichtparameter | `numpad_device` entfernen |
| `resolve_evdev_device(numpad_device)` in `run()` | Löst NumPad-Pfad auf | Entfernen |
| `run_system_check(..., numpad_path=...)` | Prüft NumPad-Gerät | `numpad_path`-Parameter entfällt |
| `grace_conn`-Block (Zeilen 223–230) | Liest `booking.grace_seconds_after_numpad_select` aus DB | Vollständig entfernen |
| `EvdevHardwareReader(numpad_path=..., ...)` | Initialisiert NumPad + RFID | `numpad_path` entfällt; `rfid_timeout` evtl. weiter relevant |
| `argparse --numpad` | CLI-Option für NumPad-Gerät | Entfernen |
| `_DOMAIN_MESSAGES[OpenPhaseConflictError]` | `"Offene Phase — bitte zuerst abschließen."` | Entfernen (Fehler wird unerreichbar) |
| `_run_one_cycle()` | Ruft `print(_BUCHUNGSARTEN)` auf | Zeile entfernen |

**`booking_loop.py`**

| Element | Ist-Stand | Änderungsbedarf |
| --- | --- | --- |
| `process_booking()` | Ruft `reader.read_next()` → bekommt `booking_type` aus Hardware | Muss Tageszustand aus DB ermitteln und Typ ableiten, bevor `BookCommand` gebaut wird |
| `payload_json` in device\_events | Enthält `"booking_type": request.booking_type.value` | Inhalt ändert sich: Typ ist jetzt abgeleitet, nicht eingegeben |
| `BookCommand(booking_type=request.booking_type, ...)` | Typ kommt vom Reader | Typ kommt aus Zustandsableitung |

Der Ableitungsschritt (Tageszustand ermitteln → nächster Typ) muss in
`booking_loop.py` oder einem neuen Domänendienst vor dem `BookUseCase`-Aufruf
eingefügt werden.

### 3.2 Infrastruktur: `infrastructure/hardware/`

**`evdev_reader.py`**

| Element | Ist-Stand | Änderungsbedarf |
| --- | --- | --- |
| `_NUMPAD_TO_BOOKING_TYPE` | Mapping Taste → BookingType | Vollständig entfernen |
| `_read_booking_type()` | Blockiert auf NumPad-Eingabe | Vollständig entfernen |
| `EvdevHardwareReader.__init__(numpad_path, ...)` | Öffnet NumPad-Gerät | `numpad_path`-Parameter und `self._numpad` entfernen |
| `EvdevHardwareReader.close()` | Schließt beide Geräte | Nur noch RFID-Gerät schließen |
| `scan_rfid_uid_hash()` | Standalone-Funktion ohne NumPad | Bleibt unverändert |

**`ports.py`**

| Element | Ist-Stand | Änderungsbedarf |
| --- | --- | --- |
| `RawBookingRequest.booking_type` | Pflichtfeld, kommt vom NumPad | Feld entfällt; nur noch `uid_hash` und `occurred_at` relevant |
| `HardwareReader.read_next()` | Gibt `RawBookingRequest` mit `booking_type` zurück | Rückgabetyp muss `booking_type` verlieren oder ein neuer, schlankerer Rückgabetyp wird definiert |

Die Änderung von `RawBookingRequest` ist eine Schnittstellenänderung, die
`booking_loop.py`, alle Tests mit `SimulatedHardwareReader` und den evdev-Reader
selbst betrifft.

**`infrastructure/hardware/simulator.py`**

`SimulatedHardwareReader.inject()` nimmt derzeit `booking_type` als Parameter.
Fällt dieser weg, müssen alle Test-Setups angepasst werden, die
`inject(booking_type=...)` aufrufen.

**`infrastructure/system_check.py`**

- `_REQUIRED_CONFIG_KEYS` enthält `"booking.grace_seconds_after_numpad_select"` —
  dieser Key ist im Zielbild obsolet und muss entfernt werden.
- Parameter `numpad_path` entfällt aus `run_system_check()`.

**`infrastructure/config_file.py`**

- `TerminalConfig.numpad: str | None` — das Feld wird im Zielbild nicht mehr
  benötigt.
- Entsprechende Parsing-Zeile in `_parse()` und Schreib-Zeile in
  `_terminal_section()` ebenfalls.

**`infrastructure/db/repositories/system_config.py`**

- Der system\_config-Eintrag `booking.grace_seconds_after_numpad_select` in
  `migrations/0002_seed_defaults.sql` (vermutlich) wird obsolet.

### 3.3 Domänenschicht: `domain/`

| Element | Ist-Stand | Änderungsbedarf |
| --- | --- | --- |
| `validate_booking_sequence()` | Prüft vorgegebenen Typ | Neue Funktion `derive_booking_type(day_bookings)` fehlt vollständig |
| `OpenPhaseConflictError` | Für „GO bei offener Pause" | Wird im RFID-Zielbild unerreichbar; ggf. entfernen oder behalten (für administrativen Korrekturpfad?) |
| Kein 5.-Buchung-Handler | Kein expliziter Fall | Neuer Fehlertyp oder explizite Ausnahme erforderlich |
| `enums.py` / `errors.py` | 9 Fehlerklassen | Potenziell neuer Fehlertyp für Tagesüberbuchung nötig |

**Offener Punkt zur Weiterverwendung von `validate_booking_sequence()`:** Im neuen
Ableitungspfad könnte die Funktion als interne Absicherung dienen
(Konsistenzprüfung nach der Ableitung), oder sie wird vollständig durch die
Zustandslogik ersetzt. Das Planungsdokument spezifiziert dies nicht.

### 3.4 Anwendungsschicht: `application/`

| Element | Ist-Stand | Änderungsbedarf |
| --- | --- | --- |
| `BookCommand.booking_type` | Pflichtfeld, vom Terminal-Input | Bleibt Pflichtfeld, kommt nun aus Ableitung |
| `BookUseCase.execute()` | Ruft `validate_booking_sequence(cmd.booking_type, ...)` auf | Validierungslogik muss mit neuer Zustandsableitung kompatibel sein |
| Restliche Use Cases (Supplement, Correction, etc.) | Vollständig administrativ | Unverändert |

---

## 4. Test- und Nachweis-Delta

### 4.1 Tests mit eindeutigem NumPad-Bezug

| Testdatei | Betroffene Tests | Grund |
| --- | --- | --- |
| `tests/integration/test_hardware_evdev.py` | Alle Tests für `_NUMPAD_TO_BOOKING_TYPE`, `_read_booking_type`, `EvdevHardwareReader._numpad` | NumPad-Logik wird entfernt |
| `tests/integration/test_terminal_ui_main.py` | Tests für `--numpad`-CLI-Option, `run()` mit `numpad_device` | Parameter entfällt |

### 4.2 Tests mit `booking_type`-Injektion als Voraussetzung

| Testdatei | Problem | Umfang |
| --- | --- | --- |
| `tests/presentation/test_booking_loop.py` | Alle Tests rufen `SimulatedHardwareReader.inject(booking_type=...)` auf und übergeben explizit einen Buchungstyp. Im Zielbild liefert der Reader keinen Typ mehr. | Vollständige Überarbeitung erforderlich |
| `tests/application/test_book_time.py` | Baut `BookCommand(booking_type=...)` explizit. Bleibt syntaktisch korrekt, aber der Kontext ändert sich (Typ ist nicht mehr eine Eingabe, sondern ein Ableitungsergebnis). | Prüfen, ob Tests fachlich noch korrekt sind |
| `tests/domain/test_booking_rules.py` | 14 Tests für `validate_booking_sequence()`. Bleiben relevant, falls die Funktion weiter genutzt wird; entfallen oder müssen angepasst werden, falls sie ersetzt wird. | Abhängig von Architekturentscheidung |
| `tests/e2e/test_booking_flow.py` | End-to-End-Buchungstest — prüft Ablauf über alle Schichten. Wenn `SimulatedHardwareReader` umgebaut wird, betrifft das diesen Test. | Anpassungsbedarf |

### 4.3 Tests, die unverändert bleiben

| Testdatei | Begründung |
| --- | --- |
| `tests/domain/test_compliance_checks.py` | Reine Prüflogik, unabhängig vom Eingabemodell |
| `tests/domain/test_entities.py` | Domänen-Invarianten, keine Eingabebezüge |
| `tests/domain/test_audit_events.py` | Audit-Event-Definitionen |
| `tests/application/test_correct_booking.py` | Administrativer Korrekturpfad bleibt unverändert |
| `tests/application/test_register_supplement.py` | Nachtrag bleibt unverändert |
| `tests/application/test_approve_supplement.py` | Administrativ, unverändert |
| `tests/application/test_reject_supplement.py` | Administrativ, unverändert |
| `tests/integration/test_device_event_booking.py` | Prüft device\_event-Verkettung; bleibt konzeptionell gültig, muss aber ohne `booking_type`-Injection im Reader umgeschrieben werden |
| `tests/integration/test_repositories*.py` | Infrastruktur-Tests |
| `tests/e2e/test_backup.py` | Betriebstest, unabhängig |
| `tests/test_migrations.py` | Migrationstest, nur bei Schemaänderung betroffen |

### 4.4 Neue Testpflichten aus dem Zielbild

`planung_rfid.md` definiert folgende Testfälle, für die derzeit kein dedizierter
Test existiert:

| Szenario | Status |
| --- | --- |
| 4 Scans = COME, BREAK\_START, BREAK\_END, GO (vollständiger Normalfall ohne Typpflicht) | Fehlt |
| 5. Scan am selben Tag → Exception mit Logeintrag | Fehlt vollständig |
| Tageswechsel → erster Scan → wieder COME | Fehlt |
| Mehrere Mitarbeitende: unabhängige Zustandsfolgen | Fehlt als dedizierter Test |
| Optionaler Doppelscan-Fall | Fehlt (nur optional) |

### 4.5 Pflichtenheft-Bezug (§16)

Die Testmatrix in `docs/betrieb/nachweise/testmatrix_revision_v1.md` wurde für
das bestehende Modell erstellt. Folgende Pflichtszenarien werden durch die
RFID-Umstellung inhaltlich berührt:

- Die bisher formulierten Szenarien für Buchungsfolgen
  (COME→BREAK\_START→BREAK\_END→GO) bleiben inhaltlich gültig, aber ihr Testpfad
  ändert sich (kein expliziter `booking_type`-Input mehr).
- Der neue Fall „5. Buchung = Exception" ist als Pflichtszenario nicht in der
  aktuellen Testmatrix enthalten und muss ergänzt werden.
- „Unbekannter RFID-Key → keine Buchung" ist bereits abgedeckt
  (`test_device_event_booking.py`), bleibt gültig.

---

## 5. Dokumentations-Delta

| Dokument | Anpassungsbedarf | Begründung |
| --- | --- | --- |
| `docs/pflichtenheft_arbeitszeit_v6.md` | **Hoch** | §7.10 (Terminal-Bedienung) beschreibt NumPad-Interaktion. Terminalbedienung ohne NumPad ist eine grundlegende Änderung der Anforderungsbeschreibung. |
| `docs/regelwerk_arbeitszeit_v5.md` | **Hoch** | Regeln zu Buchungstyp-Auswahl, Sequenzprüfung und Fehlerbehandlung müssen RFID-only-Semantik abbilden. |
| `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` | **Hoch** | Beschreibt Terminalinteraktion, Gerätekonfiguration (NumPad-Gerät), Fehlverhalten. Alle NumPad-Referenzen veralten. |
| `docs/betrieb/nachweise/testmatrix_revision_v1.md` | **Hoch** | Neue Pflichtszenarien (5. Buchung, Tageswechsel, Zustandsableitung) fehlen; NumPad-bezogene Szenarien werden obsolet. |
| `docs/adr/device_event_architekturentscheidung_v1.md` | **Mittel** | Das ADR beschreibt den Ablauf NumPad → RFID → device\_event. Die Kausalkette ändert sich auf RFID → Zustandsableitung → device\_event. |
| `docs/betrieb/nachweise/nachtragsmatrix_phasen_v1.md` | **Mittel** | Artefakte der NumPad-Entfernung und der Zustandsautomaten-Implementierung sind als neue Phase/Increment zu dokumentieren. |
| `anlage_einhaltung_pflichtenheft.md` (v1) | **Mittel** | Verweist auf implementierte Pflichtanforderungen. Muss nach Umstellung auf Aktualität geprüft werden. |
| `docs/02_anwender/handbuch.md` | **Mittel** | Kapitel zur Terminalbedienung. NumPad-Beschreibung entfernen; neuen RFID-only-Ablauf beschreiben. |
| `config.toml` (Systemkonfiguration) | **Mittel** | Eintrag `[terminal] numpad` und system\_config-Key `booking.grace_seconds_after_numpad_select` werden obsolet. |
| `docs/03_installation_technik/befehlsreferenz.md` | **Niedrig** | Falls `--numpad`-CLI-Option dort dokumentiert ist. |

---

## 6. Offene Fragen und Unsicherheiten

**F1 — Verbleib von `validate_booking_sequence()` im RFID-Zielbild:**
Die Funktion validiert einen vorgegebenen Buchungstyp. Im RFID-Zielbild gibt es
keinen vorgegebenen Typ mehr — er wird abgeleitet. Es ist unklar, ob die Funktion
(a) als interne Konsistenzprüfung nach der Ableitung weiter genutzt wird,
(b) durch den Zustandsautomaten vollständig ersetzt wird oder (c) nur für den
administrativen Korrekturpfad (der weiterhin explizite Typen verarbeitet) relevant
bleibt. Aus Code und Planungsdokument lässt sich kein eindeutiger Schluss ziehen.

**F2 — 5. Buchung und bestehende Fehlerklasse:**
Der aktuelle Code würde eine 5. COME-Buchung nach vollständigem Tagesablauf
(COME, BREAK\_START, BREAK\_END, GO) nicht als Fehler erkennen —
`validate_booking_sequence(COME, [COME, BREAK_START, BREAK_END, GO])` würde keinen
`InvalidBookingSequenceError` werfen, weil `open_work=False` und `open_break=False`.
Ob hierfür ein neuer Fehlertyp eingeführt wird oder die bestehende Klasse
angepasst wird, ist offen.

**F3 — Verbleib von `OpenPhaseConflictError`:**
Diese Fehlerklasse ist im RFID-Zielbild fachlich unerreichbar (der Zustandsautomat
verhindert die auslösende Situation). Sie bleibt aber im administrativen
Korrekturpfad potenziell relevant (wenn ein Admin einen GO-Eintrag für eine
Buchung anlegt, bei der noch eine Pause offen ist). Ob die Klasse entfernt oder
nur aus dem Terminalpfad entfernt wird, ist nicht geklärt.

**F4 — Tatsächliche heutige Behandlung mehrfacher Buchungen an einem Tag:**
`planung_gesamt.md` dokumentiert keine explizite Begrenzung auf 4 Buchungen pro
Tag. Der Code zeigt, dass `validate_booking_sequence()` eine 5. Buchung (COME
nach GO) unter bestimmten Umständen zulässt (s. F2). Das tatsächliche Verhalten
bei 5+ Buchungen im Produktionsbetrieb ist aus Code und Dokumenten nicht
vollständig rekonstruierbar.

**F5 — Schichtmodelle und Mitternachtsübergang:**
`planung_rfid.md` schließt Schichtmodelle über Mitternacht explizit aus. Die
bestehende Codebasis enthält keine explizite Regelung für diesen Fall. Es ist
unklar, ob der aktuelle Code bei einer Buchung nach Mitternacht (die logisch zum
Vortag gehört) korrekt reagiert oder ob dieser Fall als offene Lücke bestehen
bleibt.

**F6 — Rolle des `system_config`-Keys `booking.grace_seconds_after_numpad_select`:**
Dieser Key steuert den RFID-Timeout nach einer NumPad-Auswahl. Im RFID-Zielbild
entfällt die NumPad-Selektion. Es ist unklar, ob ein analoger Timeout-Mechanismus
für den reinen RFID-Scan (z. B. Entprellung) benötigt wird oder ob der Key
ersatzlos entfernt werden kann. Der Key ist in `0002_seed_defaults.sql` als
Seed-Wert eingetragen; ein Migrations-Schritt wäre nötig, wenn er aus dem Schema
entfernt werden soll.

**F7 — Zustandsmodell-Persistenz:**
`planung_rfid.md` beschreibt Zustände 0–4 als Anforderung. Ob diese als neue
Spalte/Tabelle im Datenbankschema persistiert werden oder ob sie bei jedem Scan
live aus den Tagesbuchungen abgeleitet werden, ist nicht festgelegt. Die
bestehende Architektur nutzt ausschließlich Live-Ableitung
(`list_for_employee_on_day()`). Eine explizite Zustandstabelle würde eine neue
Migration erfordern.
