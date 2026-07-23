# Quellcode–Dokumentation-Abgleich: `admin_cli` und `terminal_ui`

**Stand:** 2026-07-23
**Methode:** Vollständige Lektüre aller Python-Dateien unter
`src/arbeitszeit/presentation/admin_cli/` (11 Dateien) und
`src/arbeitszeit/presentation/terminal_ui/` (3 Dateien) sowie der vier
zu prüfenden Dokumentationsdateien. Ergänzend wurden
`scripts/setup.py`, `scripts/show_config.py`, `scripts/verify_hardware.py`,
`src/arbeitszeit/infrastructure/config_file.py`,
`src/arbeitszeit/infrastructure/config_setup.py` und
`src/arbeitszeit/infrastructure/system_check.py` gelesen.

---

## 1. Analyse-Grundlage

### 1.1 Admin-CLI (`src/arbeitszeit/presentation/admin_cli/`)

**Einstiegspunkt:** `main.py` (v1.5)
**Domains / Unterbefehle:** `employees`, `cards`, `bookings`, `schedule`,
`reports`, `system`, `users`, `audit` — insgesamt 32 Befehle und Unterbefehle.

**Globale Argumente:**

| Argument | Pflicht | Beschreibung |
| --- | --- | --- |
| `--config` | nein | Pfad zu `config.toml` |
| `--db` | bedingt | Datenbankpfad (wenn nicht via `config.toml`) |
| `--user-id` | bedingt | Benutzer-ID (CLI > `ADMIN_USER_ID` > `config.toml`) |
| `--admin-password` | nein | Admin-Passwort; Standard: `getpass` |

**Umgebungsvariablen (admin_cli):**

| Variable | Pflicht | Beschreibung |
| --- | --- | --- |
| `ADMIN_USER_ID` | nein | Fallback für `--user-id` |
| `AUDIT_HMAC_KEY` | für `audit verify-chain` | HMAC-Schlüssel für Kettenprüfung |

**Exit-Codes:** 0 = Erfolg, 1 = Fehler (alle Fälle: fehlende Berechtigung,
ungültige Eingabe, Datenbankfehler, fehlende Umgebungsvariable u. a.);
Sonderfall `system check`: explizit `sys.exit(0)` / `sys.exit(1)`.

**stdout vs. stderr:**
- stdout: alle Erfolgsmeldungen, Tabellen, Export-Pfade, Audit-Ausgaben
- stderr: Fehlermeldungen, `"Hinweis: N Einträge…"` (> 50 Einträge ungefiltert),
  `"Generiertes Passwort (einmalig sichtbar): …"` bei `users bootstrap` /
  `users add` ohne `--password`

### 1.2 Terminal-UI (`src/arbeitszeit/presentation/terminal_ui/`)

**Einstiegspunkt:** `main.py` (v1.7), `booking_loop.py` (v1.2)

**CLI-Argumente:**

| Argument | Pflicht | Auflösung |
| --- | --- | --- |
| `--config` | nein | expliziter Pfad zu `config.toml` |
| `--db` | bedingt | CLI > `config.toml [database] path` |
| `--rfid` | bedingt | CLI > `config.toml [terminal] rfid` |
| `--terminal-id` | bedingt | CLI > `config.toml [terminal] id` |

Kein `--numpad`-Argument. `AppConfig.TerminalConfig` hat die Felder
`id` und `rfid` — kein `numpad`-Feld (seit Migration 0007,
RFID-only-Umstellung).

**Umgebungsvariablen (terminal_ui):**

| Variable | Pflicht | Beschreibung |
| --- | --- | --- |
| `RFID_PEPPER` | ja | HMAC-SHA256-Schlüssel für Karten-UID-Hashing; fehlt → `ValueError` |
| `AUDIT_HMAC_KEY` | ja | HMAC-SHA256-Schlüssel für Audit-Log-Kettenintegrität; fehlt → `ValueError` beim Schreiben; Systemcheck meldet `SELFTEST_FAIL` |
| `ARBEITSZEIT_CONFIG` | nein | Alternativer Pfad zu `config.toml` |

**Systemcheck beim Start:** 8 Prüfungen:
`db_access`, `config_keys`, `nas_reachability`, `fk_consistency`,
`config_file_paths`, `ntp_sync`, `audit_hmac_key`, `device_availability`.

**Exit-Codes:** 1 bei fehlendem Pflicht-CLI-Argument oder Ladefehler,
0 (implizit) bei sauberem SIGTERM/SIGINT. Systemcheck-Fehler erzeugen
**keinen** Exit — Betrieb läuft weiter.

### 1.3 Wichtige Hilfsskripte

- `scripts/setup.py` (v1.1) — Ersteinrichtung und Pflege von `config.toml`.
  Ruft `config_setup.py::setup_config()` auf.
- `scripts/show_config.py` — Zeigt aktuelle Konfiguration aus `config.toml`
  und `system_config`.
- `scripts/verify_hardware.py` — Interaktiver Hardware-Smoke-Test für
  USB-Numpad und RFID-Reader.

---

## 2. Befunde: Quellcode-Bugs

> **Hinweis:** Diese Abschnitt beschreibt Fehler im Quellcode selbst,
> keine Dokumentationsfehler. Sie werden hier aufgeführt, weil sie
> direkt mit Dokumentations-Abweichungen zusammenhängen.

### Bug 1 — `scripts/setup.py`: TypeError bei jedem Aufruf (KRITISCH)

**Datei:** `scripts/setup.py`, Zeile 112
**Code:**
```python
setup_config(
    config_path,
    ...
    cli_numpad=args.numpad,   # ← nicht akzeptierter Parameter
    ...
)
```
**Ursache:** `config_setup.py::setup_config()` hat keinen `cli_numpad`-Parameter
(Signatur hat: `cli_db_path`, `cli_terminal_id`, `cli_rfid`, `cli_admin_user_id`,
`cli_backup_dir`, `cli_export_dir`, `cli_log_dir`). Das Argument wurde bei der
RFID-only-Umstellung (Migration 0007) aus `setup_config()` entfernt, aber
nicht aus `setup.py`.

**Folge:** **Jeder** Aufruf von `scripts/setup.py` schlägt mit
`TypeError: setup_config() got an unexpected keyword argument 'cli_numpad'`
fehl — auch wenn `--numpad` nicht übergeben wird (da `args.numpad = None`
trotzdem als Schlüsselwortargument übergeben wird).

**Betrifft:** Installationsanleitung Schritt 8 und 9.

---

### Bug 2 — `scripts/show_config.py`: AttributeError bei jedem Aufruf (KRITISCH)

**Datei:** `scripts/show_config.py`, Zeilen 146–147 und 231
**Code:**
```python
if cfg.terminal.numpad is not None:
    rows.append(("terminal.numpad", cfg.terminal.numpad))
```
**Ursache:** `TerminalConfig` (mit `slots=True`) hat kein `numpad`-Attribut —
nur `id` und `rfid`. Dieses Feld wurde bei der RFID-only-Umstellung
aus `config_file.py::TerminalConfig` entfernt, aber nicht aus `show_config.py`.

**Folge:** **Jeder** Aufruf von `scripts/show_config.py` schlägt mit
`AttributeError: 'TerminalConfig' object has no attribute 'numpad'` fehl.

**Betrifft:** Handbuch Abschnitt 9.3 ("Aktuelle Konfiguration anzeigen").

---

### Hintergrund beider Bugs

Migration `0007_remove_numpad_grace_config.sql` hat die RFID-only-Umstellung
vollzogen. Dabei wurde `numpad` aus `AppConfig.TerminalConfig` und dem
Parsing in `config_file.py` entfernt, sowie `--numpad` aus `terminal_ui.main`
und `config_setup.py::setup_config()`. Allerdings wurden `scripts/setup.py`
und `scripts/show_config.py` nicht vollständig bereinigt.

---

## 3. Befunde: Befehlsreferenz (`docs/03_installation_technik/befehlsreferenz.md`, v1.7)

Die Befehlsreferenz ist insgesamt gut gepflegt. Die folgenden Punkte wurden
identifiziert:

### BR-1 — `scripts/setup.py`: Fehlendes `--numpad`-Argument

**Fundstelle:** Abschnitt `scripts/setup.py`, Argumenttabelle

**Befund:** Die Argumenttabelle enthält kein `--numpad`. Das Argument
ist in `scripts/setup.py` (Zeile 61) vorhanden und wird als
`cli_numpad=args.numpad` weitergegeben — was den TypeError (Bug 1)
auslöst.

**Bewertung:** Die Befehlsreferenz verhält sich pragmatisch korrekt:
Ein funktionsloses Argument zu dokumentieren wäre irreführender als es
wegzulassen. Kein unmittelbarer Korrekturbedarf in der Befehlsreferenz
— Korrekturbedarf liegt im Quellcode.

---

### BR-2 — `scripts/setup.py`: Kein Hinweis auf Defekt

**Fundstelle:** Abschnitt `scripts/setup.py`

**Befund:** `scripts/setup.py` ist aufgrund von Bug 1 komplett nicht
ausführbar. Die Befehlsreferenz dokumentiert es als funktionierendes
Werkzeug ohne Einschränkungshinweis.

**Auswirkung:** Nutzende, die sich auf die Befehlsreferenz verlassen,
stoßen auf einen unerwarteten Python-Absturz.

---

### BR-3 — `scripts/show_config.py`: Kein Hinweis auf Defekt

**Fundstelle:** Abschnitt `scripts/show_config.py`

**Befund:** `scripts/show_config.py` ist aufgrund von Bug 2 komplett
nicht ausführbar. Die Befehlsreferenz dokumentiert es als funktionierendes
Werkzeug.

**Auswirkung:** Handbuch Abschnitt 9.3 und Befehlsreferenz empfehlen
`python scripts/show_config.py --db datenbank.db`, was mit AttributeError
fehlschlägt.

---

### BR-4 — `employees list`: Rolle unklar

**Fundstelle:** Rollenübersicht-Tabelle (Zeile `employees list`)

**Befund:** Die Rollenübersicht vermerkt „keine" für `employees list`.
Der Quellcode bestätigt das: `employees list` läuft ohne Rollen-
oder Passwortprüfung durch. Dies ist korrekt dokumentiert.

**Bewertung:** Kein Befund, Übereinstimmung bestätigt.

---

### BR-5 — Korrekte Darstellung von `users list`

**Fundstelle:** Rollenübersicht-Tabelle (Zeile `users list`)

**Befund:** Rolle „keine" — Quellcode bestätigt: kein Auth erforderlich.

**Bewertung:** Kein Befund, Übereinstimmung bestätigt.

---

## 4. Befunde: Installationsanleitung (`docs/03_installation_technik/installationsanleitung.md`, v1.8)

### IA-1 — Vorwort: "RFID-Karte und Numpad" für Buchungen (FEHLER)

**Fundstelle:** Abschnitt „Was du am Ende dieser Anleitung hast"

**Text:**
> mit dem Mitarbeitende per RFID-Karte und Numpad ihre Arbeitszeiten
> buchen können

**Befund:** Die `terminal_ui` nutzt für Buchungen ausschließlich den
RFID-Reader. Ein USB-Numpad wird im Buchungsbetrieb nicht verwendet —
`AppConfig.TerminalConfig` hat kein `numpad`-Feld, `terminal_ui.main`
hat kein `--numpad`-Argument, `booking_loop.py` verarbeitet keine
Numpad-Ereignisse.

**Auswirkung:** Nutzende beschaffen und verkabeln ein USB-Numpad, das
für den Buchungsbetrieb nicht benötigt wird.

---

### IA-2 — Schritt 8: `setup.py --numpad` crasht (FEHLER, KRITISCH)

**Fundstelle:** Schritt 8, Abschnitt „Beispiel für einen nicht-interaktiven Aufruf"

**Betroffene Zeilen:**
```bash
python scripts/setup.py \
  --db arbeitszeit.db \
  --terminal-id 1 \
  --numpad "USB Numpad" \    ← löst TypeError aus
  ...
```

**Befund:** Dieser Aufruf schlägt immer mit
`TypeError: setup_config() got an unexpected keyword argument 'cli_numpad'`
fehl (Bug 1). Die Installation ist nach diesem Schritt blockiert.

---

### IA-3 — Schritt 9: `setup.py --numpad` crasht (FEHLER, KRITISCH)

**Fundstelle:** Schritt 9, Abschnitt „Trage jetzt die ermittelten Gerätenamen
in `config.toml` ein"

**Betroffene Zeilen:**
```bash
python scripts/setup.py \
  --numpad "Gerätename Numpad" \    ← löst TypeError aus
  --rfid "Gerätename RFID-Reader"
```

**Befund:** Gleicher Bug 1. Jeder Aufruf von `scripts/setup.py` schlägt
fehl, unabhängig davon ob `--numpad` übergeben wird oder nicht.

---

### IA-4 — Schritt 9: `config.toml` speichert kein `terminal.numpad` (FEHLER)

**Fundstelle:** Schritt 9, Abschnitt über das Eintragen von Gerätenamen

**Befund:** `TerminalConfig` hat kein `numpad`-Feld. Selbst wenn `setup.py`
nicht defekt wäre, würde ein Numpad-Name nicht in `config.toml` geschrieben
— das Feld existiert in der Datenstruktur nicht.

**Auswirkung:** Die Anweisung, einen Numpad-Namen in die Konfiguration
einzutragen, ist strukturell unwirksam.

---

### IA-5 — Schritt 10: Numpad-Test ohne Betriebsrelevanz (HINWEIS)

**Fundstelle:** Schritt 10, Abschnitt „Hardware testen"

**Befund:** `scripts/verify_hardware.py` testet ein USB-Numpad korrekt
(Tasten 1–4 mit korrekter Beschriftung „Kommen / Gehen / Pause Start /
Pause Ende"). Der Test an sich ist nicht fehlerhaft.

Das Numpad wird im laufenden Buchungsbetrieb (`terminal_ui`) aber gar
nicht verwendet. Die Beschriftung der Tasten im Installationstest
(„1 = Kommen, 2 = Gehen") könnte Nutzende zu dem Schluss verleiten,
das Numpad werde für Buchungen benötigt.

**Auswirkung:** Keine Fehlfunktion im Test selbst; jedoch erhöhter
Aufwand und potenzielle Verwirrung bei der Installation.

---

### IA-6 — Schritt 13 Ausgabe-Beispiel: `stderr`-Hinweis fehlt (HINWEIS)

**Fundstelle:** Schritt 13, Ausgabe-Beispiel `users bootstrap`

**Text:**
```text
Erstes Administratorkonto angelegt (ID 1).
Generiertes Passwort (einmalig sichtbar): <zufälliges Passwort>
```

**Befund:** Das generierte Passwort wird auf **stderr**, nicht auf stdout
ausgegeben (Quellcode: `file=sys.stderr`). Skripte oder Automation,
die die Ausgabe von stdout lesen, erhalten das Passwort nicht.
Die Anleitung enthält keinen Hinweis darauf. (Die Befehlsreferenz v1.7
enthält den Hinweis korrekt.)

**Priorität:** niedrig — für Laien-Installationsanleitung nicht sicherheitskritisch.

---

## 5. Befunde: Handbuch (`docs/02_anwender/handbuch.md`, v2.1)

### HB-1 — Abschnitt 9.2: `audit_hmac_key` fehlt in Systemcheck-Liste (FEHLER)

**Fundstelle:** Kapitel 9, Abschnitt 9.2 „Systemcheck"

**Dokumentierter Text (7 Prüfungen):**
- Datenbankzugriff
- Pflichteinstellungen in der Datenbank
- NAS-Erreichbarkeit (wenn aktiviert)
- Datenbankintegrität (Fremdschlüssel)
- Dateipfade aus `config.toml`
- Zeitsynchronisation der Systemuhr (NTP)
- RFID-Reader erreichbar

**Tatsächliche Prüfungen (8):**
`_check_db_access`, `_check_config_keys`, `_check_nas`,
`_check_fk_consistency`, `_check_config_file_paths`, `_check_ntp`,
**`_check_audit_hmac_key`** ← fehlt, `_check_devices`

**Auswirkung:** Der SELFTEST-Fehler `SELFTEST_FAIL: audit_hmac_key` ist
für Administrierende nicht nachvollziehbar — das Handbuch kennt diese
Prüfung nicht.

---

### HB-2 — Abschnitt 4.1: Zweites Start-Beispiel inkonsistent (HINWEIS)

**Fundstelle:** Kapitel 4, Abschnitt 4.1 „Terminal starten"

**Betroffener Text:**
> Wenn `config.toml` vollständig ausgefüllt ist, reicht:
>
> ```bash
> python -m arbeitszeit.presentation.terminal_ui.main \
>   --db /pfad/zur/datenbank.db
> ```

**Befund:** Wenn `config.toml` vollständig ist, enthält sie auch
`[database] path`. `--db` wäre dann nicht erforderlich — und korrekt
wäre ein Aufruf via `--config`:
```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --config ~/.config/arbeitszeit/config.toml
```

Der Aufruf mit `--db` funktioniert technisch (er überschreibt `config.toml`),
ist aber semantisch nicht das, was der Einleitungstext beschreibt.

---

### HB-3 — Abschnitt 9.3: `show_config.py` crasht (FEHLER, durch Bug 2)

**Fundstelle:** Kapitel 9, Abschnitt 9.3 „Konfiguration einrichten oder prüfen"

**Text:**
```bash
python scripts/show_config.py --db datenbank.db
```

**Befund:** Dieser Befehl schlägt immer mit `AttributeError` fehl
(Bug 2 — `cfg.terminal.numpad` existiert nicht).

---

## 6. Befunde: Module-Dokumentation (`docs/02_anwender/module/`)

### MD-1 — `handbuch_audit_it.md`: „7 Prüfungen" statt 8 (FEHLER)

**Fundstelle:** `handbuch_audit_it.md`, Zeile 77 und Tabelle „Die 7 Prüfungen"

**Befund:** Die Datei beschreibt 7 Systemcheck-Prüfungen und listet
diese in einer Tabelle auf. Der Quellcode (`system_check.py`) führt
jedoch 8 Prüfungen aus — die 8. Prüfung `_check_audit_hmac_key` fehlt
in der Dokumentation.

**Auswirkung:** Technische Nutzerinnen können einen
`SELFTEST_FAIL: audit_hmac_key`-Fehler nicht dieser Dokumentation zuordnen.

---

### MD-2 — Keine Modul-Dokumentation für `RFID_PEPPER` und `AUDIT_HMAC_KEY`

**Fundstelle:** Alle Dateien in `docs/02_anwender/module/`

**Befund:** Die Umgebungsvariablen `RFID_PEPPER` und `AUDIT_HMAC_KEY`
werden in keiner Modul-Dokumentation erwähnt. Beide sind Pflicht-Variablen
mit sofortigem `ValueError`-Abbruch bei fehlendem Wert:
- `RFID_PEPPER`: in `hash_uid()` (`infrastructure/hardware/`)
- `AUDIT_HMAC_KEY`: in `_write()` (`infrastructure/db/repositories/audit_log.py`)

`handbuch_infrastructure_it.md` wäre der passende Ort, beide zu beschreiben.

**Bewertung:** Geringes Risiko, da `befehlsreferenz.md` diese Variablen
korrekt dokumentiert. Vollständigkeit in Modul-Docs wäre aber wünschenswert.

---

### MD-3 — `handbuch_infrastructure_it.md`: `TerminalConfig` korrekt (bestätigt)

**Befund:** Die Dokumentation zeigt `TerminalConfig | id: int | None, rfid: str | None`
— korrekt, ohne `numpad`. Übereinstimmung mit Quellcode bestätigt.

---

### MD-4 — Modul-Docs insgesamt: Kein Verweis auf Setup-Bug

**Befund:** Keine der Modul-Dateien verweist auf den defekten Zustand
von `scripts/setup.py` und `scripts/show_config.py`. Dies ist kein
Fehler der Modul-Docs, sondern ein Quellcode-Problem — aber relevant
für den Gesamtbild.

---

## 7. Handlungsvorschläge

### Priorität 0 — Sofort (blockiert Betrieb / Installation)

**A) Bug 1 beheben: `scripts/setup.py::setup_config()` TypeError**

- `scripts/setup.py`: `cli_numpad=args.numpad` aus dem `setup_config()`-Aufruf
  entfernen (Zeile 112).
- `scripts/setup.py`: `--numpad`-Argument aus `argparse` entfernen
  (Zeilen 61–65), da `config_setup.py` und `TerminalConfig` es nicht
  mehr unterstützen.
- Alternativ: `config_setup.py::setup_config()` und `TerminalConfig` um
  `numpad` erweitern — nur wenn die Numpad-Unterstützung in der
  Terminal-UI reaktiviert werden soll (was aktuell nicht der Fall ist).

**B) Bug 2 beheben: `scripts/show_config.py` AttributeError**

- `scripts/show_config.py`: Zeilen 146–147 (`cfg.terminal.numpad`) entfernen.
- Zeile 231 (`"terminal_numpad": cfg.terminal.numpad`) ebenfalls entfernen
  (JSON-Ausgabepfad).

---

### Priorität 1 — Sofort (Installationsanleitung funktionsunfähig)

**C) Installationsanleitung: Numpad-Referenzen bereinigen**

Folgende Stellen anpassen:

1. Vorwort: „RFID-Karte und Numpad" → „RFID-Karte"
2. Schritt 8: `--numpad "USB Numpad"` aus dem Beispielaufruf entfernen.
   Die Aufzählung der Einstellungen von `setup.py` um „Gerätename für
   das Numpad (`--numpad`)" bereinigen.
3. Schritt 9: gesamten `--numpad`-Aufruf für `setup.py` entfernen oder
   auf den reinen `--rfid`-Aufruf reduzieren.
4. Schritt 10: Entscheidung treffen (→ Frage D unten).

**D) Klärung: Soll Schritt 10 (Numpad-Hardware-Test) erhalten bleiben?**

Das USB-Numpad ist im Buchungsbetrieb nicht erforderlich. Optionen:

- **Option 1 (empfohlen):** Schritt 10 auf rein RFID-Test reduzieren;
  Numpad-Test entfernen. Die Anleitung beschreibt nur Hardware, die
  tatsächlich in Betrieb geht.
- **Option 2:** Schritt 10 als optionalen Diagnose-Schritt kennzeichnen
  mit dem expliziten Hinweis, dass das Numpad nur im Hardware-Test,
  nicht im Buchungsbetrieb verwendet wird.

---

### Priorität 2 — Zeitnah

**E) Handbuch Abschnitt 9.2: `audit_hmac_key`-Prüfung ergänzen**

Systemcheck-Liste um achten Punkt erweitern:
- `AUDIT_HMAC_KEY` nicht gesetzt — Audit-Log ohne HMAC-Integritätsschutz

**F) `handbuch_audit_it.md`: „7 Prüfungen" → „8 Prüfungen"**

Zeile 77, Tabellenüberschrift und Tabellenzeilen anpassen.
Neue Zeile:

| 8 | `_check_audit_hmac_key` | `AUDIT_HMAC_KEY` Umgebungsvariable gesetzt und nicht leer |

**G) Handbuch Abschnitt 9.3: Hinweis auf `show_config.py`-Defekt**

Bis Bug 2 behoben ist: temporären Hinweis ergänzen, dass
`scripts/show_config.py` aktuell nicht lauffähig ist.
Nach Bugfix: Hinweis entfernen.

---

### Priorität 3 — Nächste Revision

**H) Handbuch Abschnitt 4.1: Zweites Start-Beispiel korrigieren**

```bash
# Statt:
python -m arbeitszeit.presentation.terminal_ui.main \
  --db /pfad/zur/datenbank.db

# Besser:
python -m arbeitszeit.presentation.terminal_ui.main \
  --config ~/.config/arbeitszeit/config.toml
```

**I) `handbuch_infrastructure_it.md`: `RFID_PEPPER` und `AUDIT_HMAC_KEY` ergänzen**

Neuer Abschnitt „Pflicht-Umgebungsvariablen" mit Beschreibung beider
Schlüssel, ihrer Verwendungsstelle im Code und der Konsequenz
ihres Fehlens (ValueError).

**J) Installationsanleitung Schritt 13: `stderr`-Hinweis bei Passwortausgabe**

Ergänzen, dass das generierte Passwort auf stderr erscheint — relevant
für automatisierte Setups.

---

## 8. Übersichtstabelle

| ID | Datei | Typ | Schwere | Status |
| --- | --- | --- | --- | --- |
| Bug 1 | `scripts/setup.py` | Quellcode-Bug | kritisch | behoben 2026-07-23 |
| Bug 2 | `scripts/show_config.py` | Quellcode-Bug | kritisch | behoben 2026-07-23 |
| BR-2 | `befehlsreferenz.md` | fehlender Hinweis | mittel | entfällt (Bug behoben) |
| BR-3 | `befehlsreferenz.md` | fehlender Hinweis | mittel | entfällt (Bug behoben) |
| IA-1 | `installationsanleitung.md` | Inhaltsfehler | mittel | erledigt 2026-07-23 |
| IA-2 | `installationsanleitung.md` | Inhaltsfehler | kritisch | erledigt 2026-07-23 |
| IA-3 | `installationsanleitung.md` | Inhaltsfehler | kritisch | erledigt 2026-07-23 |
| IA-4 | `installationsanleitung.md` | Inhaltsfehler | mittel | erledigt 2026-07-23 |
| IA-5 | `installationsanleitung.md` | Hinweis | niedrig | erledigt 2026-07-23 (Option 1) |
| IA-6 | `installationsanleitung.md` | Hinweis | niedrig | erledigt 2026-07-23 |
| HB-1 | `handbuch.md` | Inhaltsfehler | mittel | erledigt 2026-07-23 |
| HB-2 | `handbuch.md` | Hinweis | niedrig | erledigt 2026-07-23 |
| HB-3 | `handbuch.md` | Inhaltsfehler (Bug 2) | kritisch | entfällt (Bug behoben) |
| MD-1 | `handbuch_audit_it.md` | Inhaltsfehler | mittel | erledigt 2026-07-23 |
| MD-2 | `module/*.md` | Vollständigkeit | niedrig | erledigt 2026-07-23 |
