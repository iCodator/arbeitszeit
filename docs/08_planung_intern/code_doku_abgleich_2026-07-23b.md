# Quellcode–Dokumentation-Abgleich: `admin_cli` und `terminal_ui` (Revision 2)

**Stand:** 2026-07-23
**Geprüfte Quellen:** Quellcode-Stand HEAD (`main`), Dokumentation Stand Juli 2026
**Prüfumfang:** `admin_cli` (11 Dateien), `terminal_ui` (3 Dateien),
Hilfsskripte (3 Dateien), Infrastruktur-Helfer (3 Dateien),
Befehlsreferenz, Installationsanleitung, Handbuch (Hauptdokument),
16 Modul-Dokumentationsdateien

---

## 1. Analyse-Grundlage

### 1.1 Admin-CLI (`admin_cli`)

**Quelldateien:** `src/arbeitszeit/presentation/admin_cli/`

**Globale Argumente** (`main.py` v1.5):

| Argument | Pflicht | Bemerkung |
| --- | --- | --- |
| `--config PATH` | nein | Pfad zu `config.toml` |
| `--db PATH` | nein | expliziter Datenbankpfad |
| `--user-id ID` | nein | Prio: CLI > `ADMIN_USER_ID` > config.toml |
| `--admin-password PASSWORT` | nein | Standard: `getpass` interaktiv |

Passwort bei `users add` und `users bootstrap` wird auf **stderr** ausgegeben:
`print(f"Generiertes Passwort (einmalig sichtbar): {password}", file=sys.stderr)`

**Subcommands (34 Befehle in 8 Domänen):**

| Domäne | Befehle | Rollenprüfung |
| --- | --- | --- |
| `employees` | `list`, `add`, `deactivate` | `list`: keine; `add`/`deactivate`: ADMIN via Use Case |
| `cards` | `assign`, `replace`, `deactivate` | ADMIN via Use Case |
| `bookings` | `correct`, `supplement`, `approve-supplement`, `reject-supplement` | ADMIN/REVIEWER via Use Case |
| `schedule` | `set`, `show` | `set`: ADMIN via Use Case; `show`: `require_admin_or_reviewer()` |
| `reports` | `export-csv`, `export-csv-review-cases`, `export-pdf-day`, `export-pdf-week`, `export-pdf-month`, `export-pdf-employee`, `open-bookings`, `warn-cases`, `corrections`, `supplements`, `open-review-cases` | `require_admin_or_reviewer()` |
| `system` | `check`, `backup`, `setup` | `require_admin_or_tech()` |
| `users` | `add`, `list`, `deactivate`, `reactivate`, `change-role`, `bootstrap` | `list`/`bootstrap`: keine CLI-Rollenprüfung; restliche: ADMIN via Use Case |
| `audit` | `open-shifts`, `verify-chain` | `require_admin_or_reviewer()` |

**Wichtige Argument-Details:**

- `employees deactivate`: **positionales** Argument `id` (nicht `--employee-id`)
- `cards deactivate`: **positionales** Argument `id` (nicht `--card-id`)
- `users bootstrap`: Argument `--password` (nicht `--password-hash`)
- `reports export-*`: **kein** `--output`; Ausgabepfad aus `export_dir` in config
- `reports warn-cases`, `corrections`, `supplements`: `--from` und `--to` sind **Pflicht**
- `reports open-bookings`, `open-review-cases`: `--from`/`--to` optional

**Umgebungsvariablen:**

| Variable | Verwendungsstelle | Fehlt sie |
| --- | --- | --- |
| `RFID_PEPPER` | HMAC-SHA256-Hash der Karten-UID | `ValueError` beim ersten Scan |
| `AUDIT_HMAC_KEY` | HMAC-Kettenintegrität beim Schreiben ins Audit-Log | `ValueError`; Systemcheck meldet `SELFTEST_FAIL` |
| `ADMIN_USER_ID` | Fallback für `--user-id` in Admin-CLI | kein Fehler, nur Warnung/Abbruch wenn kein user_id gefunden |
| `ARBEITSZEIT_CONFIG` | Suchreihenfolge für `config.toml` | kein Fehler; Fallback greift |

**Exit-Codes Admin-CLI:** 0 = Erfolg, 1 = Fehler (Authentifizierung, Domänenfehler, fehlende Argumente)

### 1.2 Terminal-UI (`terminal_ui`)

**Quelldateien:** `src/arbeitszeit/presentation/terminal_ui/`

**Argumente** (`main.py` v1.7):

| Argument | Pflicht | Bemerkung |
| --- | --- | --- |
| `--config PATH` | nein | Pfad zu `config.toml` |
| `--db PATH` | nein | expliziter Datenbankpfad |
| `--rfid GERÄTPFAD` | nein | Pfad zum RFID-Reader |
| `--terminal-id INT` | nein | Terminal-ID |

Kein `--numpad`-Argument — weder in `main.py` noch in `config_file.py`.

**Laufzeitverhalten:**

- `SIGTERM` und `SIGINT`: beide abgefangen, `running = False` für sauberes Beenden
- Nach erfolgreicher Buchung: `time.sleep(2)` (2-Sekunden-Pause)
- Systemcheck vor der Buchungsschleife; blockiert **nicht** bei Fehlern

**Fehlermeldungen** (`booking_loop.py` v1.2, `_DOMAIN_MESSAGES`):

| Ausnahme | Angezeigte Meldung |
| --- | --- |
| `UnknownCardError` | `Karte nicht erkannt.` |
| `InactiveCardError` | `Karte deaktiviert.` |
| `InactiveEmployeeError` | `Mitarbeiter inaktiv.` |
| `InvalidBookingSequenceError` | `Ungültige Buchungsreihenfolge.` |
| `OpenPhaseConflictError` | `Offene Phase — bitte zuerst abschließen.` |

**Doppel-Scan-Schutz:** `DebouncedHardwareReader`, `DEBOUNCE_SECONDS = 3.0` s

### 1.3 Hilfsskripte

**`scripts/setup.py` (v1.1):** Argumente: `--config`, `--db`, `--terminal-id`,
`--rfid`, `--admin-user-id`, `--backup-dir`, `--export-dir`, `--log-dir`.
Kein `--numpad`.

**`scripts/show_config.py` (v1.1):** Argumente: `--db` (Pflicht), `--config`,
`--all-versions`, `--json`. Zeigt `database.path`, `terminal.id`,
`terminal.rfid`, `backup.backup_dir`, `backup.export_dir`, `backup.log_dir`,
`admin.user_id`. Kein `terminal.numpad`.

**`scripts/verify_hardware.py` (v1.2):** Argumente: `--rfid`, `--list`,
`--skip-interactive`. Kein `--numpad`. Zwei Prüfstufen: Stufe 1 =
Gerätedatei (`check_device_access`), Stufe 2 = RFID-Karten-Scan
(`test_rfid`, Timeout 15 s). Exit-Codes: 0 = alle ok, 1 = Fehler,
2 = evdev nicht installiert.

**Systemcheck** (`system_check.py` v1.3): Reihenfolge der 8 Prüfungen
in `run_system_check()`:

1. `_check_db_access`
2. `_check_config_keys`
3. `_check_nas`
4. `_check_fk_consistency`
5. `_check_config_file_paths`
6. `_check_ntp`
7. `_check_devices`
8. `_check_audit_hmac_key`

**Konfigurationstypen** (`config_file.py` v1.2):

| Klasse | Felder (tatsächliche Typen) |
| --- | --- |
| `DatabaseConfig` | `path: Path \| None` |
| `TerminalConfig` | `id: int \| None`, `rfid: str \| None` |
| `BackupConfig` | `backup_dir: Path \| None`, `export_dir: Path \| None`, `log_dir: Path \| None` |
| `AdminConfig` | `user_id: int \| None` |

---

## 2. Befunde: Befehlsreferenz (`docs/03_installation_technik/befehlsreferenz.md`)

### BR-01 — FEHLER: `verify_hardware.py` mit nicht existierendem `--numpad`

**Fundstelle:** Abschnitt `scripts/verify_hardware.py` (befehlsreferenz.md v1.7)

**Dokumentation behauptet:**

> Das Skript enthält zusätzlich eine Numpad-Testfunktion (`--numpad`) für
> Diagnosezwecke.

Syntax-Block zeigt `[--numpad <GERÄTEPFAD>]` als Argument.
Tabelle listet `--numpad` mit Beschreibung auf.
Hinweis: „`--numpad` und `--rfid` müssen stets gemeinsam angegeben werden;
eines allein ist ein Fehler."

**Tatsächlicher Code** (`scripts/verify_hardware.py` v1.2):

Das Skript hat **kein** `--numpad`-Argument. `argparse`-Setup (Zeilen 321–335)
registriert nur: `--rfid`, `--list`, `--skip-interactive`. Weder der
Argument-Parser noch der Ablauf enthalten Numpad-Logik. Das Skript
unterstützt ausschließlich RFID-Tests.

**Auswirkung:** Jeder Versuch, `--numpad` zu übergeben, führt zu einem
`unrecognized arguments`-Fehler von argparse. Die gegenseitige Abhängigkeit
`--numpad + --rfid` ist nicht implementiert.

---

Alle anderen Abschnitte der Befehlsreferenz sind korrekt: alle 34 Subcommands,
Rollenzuordnungen, globale Argumente inklusive `--admin-password`,
Umgebungsvariablen-Tabelle, Exit-Codes und stderr-Ausgabe des generierten
Passworts.

---

## 3. Befunde: Installationsanleitung (`docs/03_installation_technik/installationsanleitung.md`)

**BESTÄTIGT — keine Fehler gefunden.**

Geprüfte Inhalte:

- Terminal-UI-Aufruf mit `--rfid`, ohne `--numpad` ✓
- `scripts/setup.py`-Argumente ohne `--numpad` ✓
- `scripts/verify_hardware.py` mit korrekten Argumnten (`--rfid`, `--list`,
  `--skip-interactive`), ohne `--numpad` ✓
- Zwei Prüfstufen (Gerätezugriff + RFID-Scan, 15-s-Timeout) ✓
- `RFID_PEPPER` und `AUDIT_HMAC_KEY` korrekt als Pflicht-Umgebungsvariablen
  beschrieben ✓

---

## 4. Befunde: Handbuch (`docs/02_anwender/handbuch.md`)

**BESTÄTIGT — keine Fehler gefunden.**

Geprüfte Inhalte:

- Kapitel 9.2 (Systemcheck): listet korrekt 8 Prüfpunkte einschließlich
  „Sicherheitsschlüssel `AUDIT_HMAC_KEY` gesetzt" ✓
- Kapitel 9.5 (Audit-Log prüfen): beide Befehle (`audit verify-chain` und
  `audit open-shifts`) korrekt dokumentiert ✓
- Kapitel 3: `employees deactivate` und `cards deactivate` korrekt mit
  positivem Argument (z. B. `employees deactivate 5`) ✓
- Kapitel 4.2: Doppel-Scan-Schutz korrekt mit „3 Sekunden" ✓
- Kapitel 10.5: `systemctl stop` sendet Stoppsignal, das Terminal
  beendet sich sauber ✓

---

## 5. Befunde: Modul-Dokumentation (`docs/02_anwender/module/`)

### 5.01 `handbuch_overview_it.md` (v1.1) — BESTÄTIGT

Kein Befund im Scope.

### 5.02 `handbuch_overview_laien.md` (v1.1)

#### MD-01 — FEHLER: `export-pdf-month` mit nicht existierendem `--output`

**Fundstelle:** Abschnitt „Womit werden Berichte erstellt?", Zeilen 50–51

**Dokumentation:**

```bash
azadmin reports export-pdf-month --year 2026 --month 7 \
  --output /tmp/bericht_juli.pdf
```

**Code:** `reports.py` v1.2, `pdf_month`-Parser (Zeile 324–326):
nur `--year` und `--month` registriert. Kein `--output`. Ausgabepfad
wird aus `export_dir` (config.toml / system_config) bestimmt.

#### MD-02 — FEHLER: `export-csv` ohne Pflichtargumente und mit `--output`

**Fundstelle:** Abschnitt „Womit werden Berichte erstellt?", Zeilen 53–54

**Dokumentation:**

```bash
azadmin reports export-csv --output /tmp/buchungen.csv
```

**Code:** `csv_cmd`-Parser (Zeilen 307–310): `--from` und `--to` sind
**Pflicht** (`required=True`); `--output` existiert nicht.
Das Beispiel würde mit zwei Fehlern scheitern.

### 5.03 `handbuch_application_it.md` (v1.2) — BESTÄTIGT

Kein Befund im Scope.

### 5.04 `handbuch_application_laien.md` (v1.1) — BESTÄTIGT

Kein Befund im Scope.

### 5.05 `handbuch_domain_it.md` (v1.1) — BESTÄTIGT

Außerhalb des Prüfscopes (keine CLI/Terminal-UI-Inhalte).

### 5.06 `handbuch_domain_laien.md` (v1.0) — BESTÄTIGT

Außerhalb des Prüfscopes.

### 5.07 `handbuch_infrastructure_it.md` (v1.2)

#### MD-03 — HINWEIS: `DatabaseConfig.path` als `str | None` dokumentiert

**Fundstelle:** Tabelle „Dataklassen", Zeile `DatabaseConfig`

**Dokumentation:** `path: str \| None`

**Code** (`config_file.py` v1.2): `path: Path | None` — ein
`pathlib.Path`-Objekt, keine Zeichenkette.

#### MD-04 — HINWEIS: `BackupConfig`-Felder als `str | None` dokumentiert

**Fundstelle:** Tabelle „Dataklassen", Zeile `BackupConfig`

**Dokumentation:** `backup_dir: str \| None`, `export_dir: str \| None`,
`log_dir: str \| None`

**Code** (`config_file.py` v1.2): alle drei Felder sind `Path | None`.

#### MD-05 — HINWEIS: Reihenfolge der Systemchecks 7 und 8 vertauscht

**Fundstelle:** Tabelle „Die 8 Prüfungen" in `handbuch_infrastructure_it.md`

**Dokumentation:** Nr. 7 = `_check_audit_hmac_key`,
Nr. 8 = `_check_devices`

**Code** (`system_check.py` v1.3, Zeilen 70–73):

```python
checks.append(_check_config_file_paths(app_config))   # 5
checks.append(_check_ntp())                            # 6
checks.append(_check_devices(rfid_path))               # 7
checks.append(_check_audit_hmac_key())                 # 8
```

Die tatsächliche Reihenfolge ist umgekehrt: Nr. 7 = `_check_devices`,
Nr. 8 = `_check_audit_hmac_key`.

### 5.08 `handbuch_infrastructure_laien.md` (v1.1) — BESTÄTIGT

Kein Befund.

### 5.09 `handbuch_datenbankschema_it.md` — außerhalb Scope

Nicht tiefgehend geprüft (kein CLI/Terminal-UI-Bezug).

### 5.10 `handbuch_datenbankschema_laien.md` — außerhalb Scope

Nicht tiefgehend geprüft.

### 5.11 `handbuch_audit_it.md` (v1.2)

#### MD-06 — HINWEIS: `audit verify-chain` nicht dokumentiert

**Fundstelle:** Abschnitt „Admin-CLI" (Ende des Dokuments)

Das Dokument hat einen Abschnitt „Admin-CLI: audit open-shifts" (Zeilen
116–155). Ein entsprechender Abschnitt „Admin-CLI: audit verify-chain"
fehlt.

**Code** (`audit.py` v1.1): `cmd_audit_verify_chain()` liest
`AUDIT_HMAC_KEY` aus der Umgebung und prüft die gesamte HMAC-Kette des
Audit-Logs. Bei fehlendem Schlüssel oder gebrochener Kette: Exit 1.
Der Befehl ist mit `require_admin_or_reviewer()` gesichert.

#### MD-07 — HINWEIS: Reihenfolge der Systemchecks 7 und 8 vertauscht

Identisch mit MD-05. Die Tabelle „Die 8 Prüfungen" zeigt
`_check_audit_hmac_key` an Nr. 7 und `_check_devices` an Nr. 8.
Code-Reihenfolge ist umgekehrt.

### 5.12 `handbuch_audit_laien.md` (v1.1)

#### MD-08 — FEHLER: Systemcheck mit 7 statt 8 Prüfungen

**Fundstelle:** Abschnitt „Was wird geprüft?", Einleitungssatz und Tabelle

**Dokumentation:** „prüft automatisch 7 Punkte" — Tabelle listet 7 Einträge
(db_access, config_keys, nas, fk_consistency, config_file_paths, ntp,
device_availability). Die `AUDIT_HMAC_KEY`-Prüfung (`_check_audit_hmac_key`)
fehlt vollständig.

**Code** (`system_check.py` v1.3): 8 Prüfungen, die achte ist
`_check_audit_hmac_key` (prüft ob `AUDIT_HMAC_KEY` gesetzt und nicht leer).

Hinweis: `handbuch.md` (Kapitel 9.2) und `handbuch_infrastructure_it.md`
listen korrekt 8 Prüfungen auf. Nur die Laien-Variante ist veraltet.

### 5.13 `handbuch_presentation_it.md` (v1.3)

#### MD-09 — FEHLER: `audit verify-chain` fehlt in der Befehls-Tabelle

**Fundstelle:** Abschnitt „audit", Tabelle der audit-Befehle

**Dokumentation:** Tabelle listet nur `audit open-shifts`.

**Code** (`audit.py` v1.1): beide Befehle `audit open-shifts` und
`audit verify-chain` sind registriert und mit `require_admin_or_reviewer()`
gesichert.

#### MD-10 — FEHLER: `system check` als „7 Checks" beschrieben

**Fundstelle:** Tabelle der system-Befehle

**Dokumentation:** `| system check | Systemprüfung ausführen (7 Checks) |`

**Code** (`system_check.py` v1.3): 8 Prüfungen. Vgl. MD-08.

#### MD-11 — FEHLER: Beispiel `users bootstrap` mit `--password-hash`

**Fundstelle:** Abschnitt „users", Beispielblock

**Dokumentation:**

```bash
azadmin users bootstrap --username admin --password-hash <hash>
```

**Code** (`user_accounts.py` v1.1, Zeilen für `bootstrap`):

```python
boot.add_argument("--password", default=None, ...)
```

Das Argument heißt `--password`, nicht `--password-hash`. Das Beispiel
würde mit `unrecognized arguments: --password-hash` scheitern.

#### MD-12 — FEHLER: `export-pdf-month` mit nicht existierendem `--output`

**Fundstelle:** Abschnitt „reports", Beispielblock

**Dokumentation:**

```bash
azadmin reports export-pdf-month --year 2026 --month 7 \
  --output /tmp/juli2026.pdf
```

**Code:** Kein `--output`-Argument. Vgl. MD-01.

#### MD-13 — HINWEIS: `--admin-password` fehlt in Tabelle „Globale Optionen"

**Fundstelle:** Tabelle „Globale Optionen"

**Dokumentation:** Zeigt `--config`, `--db`, `--user-id` — kein
`--admin-password`.

**Code** (`main.py` v1.5): `--admin-password` ist registriert.
In der `befehlsreferenz.md` korrekt dokumentiert; im IT-Modul-Handbuch
fehlt der Eintrag.

#### MD-14 — HINWEIS: Fehlermeldungen im Terminal nicht wortgetreu

**Fundstelle:** Tabelle „Domänenfehler-Meldungen" (oder äquivalente
Auflistung)

| Dokumentation | Tatsächliche Meldung im Code |
| --- | --- |
| Unbekannte Karte | Karte nicht erkannt. |
| Deaktivierte Karte | Karte deaktiviert. |
| Inaktiver Mitarbeitender | Mitarbeiter inaktiv. |
| Ungültige Buchungsfolge | Ungültige Buchungsreihenfolge. |
| Offene Pause — erst Pause beenden | Offene Phase — bitte zuerst abschließen. |

Die Dokumentation gibt sinngemäße Beschreibungen, nicht die exakten
UI-Texte aus `_DOMAIN_MESSAGES` in `booking_loop.py` v1.2.

### 5.14 `handbuch_presentation_laien.md` (v1.2)

#### MD-15 — FEHLER: `employees deactivate` mit `--employee-id` statt positivem Argument

**Fundstelle:** Abschnitt „Mitarbeitende verwalten", Zeile 49

**Dokumentation:**

```bash
azadmin employees deactivate --employee-id 5
```

**Code** (`employees.py` v1.3):

```python
deact.add_argument("id", type=int)
```

`deactivate` erwartet ein **positionales** Argument. Die korrekte Syntax
lautet `azadmin employees deactivate 5`.

#### MD-16 — FEHLER: `cards deactivate` mit `--card-id` statt positivem Argument

**Fundstelle:** Abschnitt „RFID-Karten verwalten", Zeile 62

**Dokumentation:**

```bash
azadmin cards deactivate --card-id 7
```

**Code** (`employees.py` v1.3, cards-Abschnitt):

```python
deact_card.add_argument("id", type=int)
```

Die korrekte Syntax lautet `azadmin cards deactivate 7`.

#### MD-17 — FEHLER: `reports warn-cases` ohne Pflichtargumente `--from`/`--to`

**Fundstelle:** Abschnitt „Berichte", Zeile 93

**Dokumentation:**

```bash
azadmin reports warn-cases
```

**Code** (`reports.py` v1.2, Zeilen 339–342):

```python
wc.add_argument("--from", required=True, dest="from_date", ...)
wc.add_argument("--to", required=True, dest="to_date", ...)
```

`--from` und `--to` sind für `warn-cases` **Pflicht**. Der Befehl ohne
diese Argumente scheitert mit argparse-Fehler.

#### MD-18 — FEHLER: `export-pdf-month` mit `--output`

**Fundstelle:** Abschnitt „Berichte", Zeilen 99–100

Identisch mit MD-01 und MD-12. `--output` existiert nicht.

#### MD-19 — FEHLER: `export-csv` ohne Pflichtargumente und mit `--output`

**Fundstelle:** Abschnitt „Berichte", Zeile 103

Identisch mit MD-02. `--output` existiert nicht; `--from`/`--to` sind
Pflicht.

### 5.15 `handbuch_show_config_it.md` (v1.2) — BESTÄTIGT

Alle Argumente, Felder und Beschreibungen stimmen mit dem Code überein.
Kein `terminal.numpad` dokumentiert.

### 5.16 `handbuch_show_config_laien.md` (v1.1) — BESTÄTIGT

Kein Befund.

---

## 6. Handlungsvorschläge

### Priorität 0 — sofort beheben (Befehle würden scheitern)

| ID | Datei | Maßnahme |
| --- | --- | --- |
| BR-01 | `befehlsreferenz.md` | `--numpad`-Beschreibung und Hinweis vollständig entfernen; Argumente-Tabelle auf `--rfid`, `--list`, `--skip-interactive` korrigieren |
| MD-11 | `handbuch_presentation_it.md` | Beispiel `--password-hash` → `--password` korrigieren |
| MD-15 | `handbuch_presentation_laien.md` | `employees deactivate --employee-id 5` → `employees deactivate 5` |
| MD-16 | `handbuch_presentation_laien.md` | `cards deactivate --card-id 7` → `cards deactivate 7` |
| MD-17 | `handbuch_presentation_laien.md` | `warn-cases` um `--from TT.MM.JJJJ --to TT.MM.JJJJ` ergänzen |
| MD-01, MD-12, MD-18 | `handbuch_overview_laien.md`, `handbuch_presentation_it.md`, `handbuch_presentation_laien.md` | `--output`-Argument aus allen `export-pdf-month`-Beispielen entfernen; Hinweis „Pfad aus export_dir" ergänzen |
| MD-02, MD-19 | `handbuch_overview_laien.md`, `handbuch_presentation_laien.md` | `export-csv`: `--output` entfernen, `--from`/`--to` als Pflichtargumente ergänzen |

### Priorität 1 — bald beheben (inhaltlich falsch, aber kein sofortiger Laufzeitfehler)

| ID | Datei | Maßnahme |
| --- | --- | --- |
| MD-08 | `handbuch_audit_laien.md` | Einleitungssatz „7 Punkte" → „8 Punkte"; Tabelle um `AUDIT_HMAC_KEY`-Prüfung ergänzen |
| MD-09 | `handbuch_presentation_it.md` | `audit verify-chain` in die Befehls-Tabelle aufnehmen |
| MD-10 | `handbuch_presentation_it.md` | `system check (7 Checks)` → `(8 Checks)` |
| MD-06 | `handbuch_audit_it.md` | Neuen Abschnitt „Admin-CLI: audit verify-chain" ergänzen (analog zu `open-shifts`): Berechtigung ADMIN/REVIEWER, Argumente keine, Exit-Code 1 bei fehlendem Key oder gebrochener Kette |

### Priorität 2 — bei Gelegenheit korrigieren (Präzision)

| ID | Datei | Maßnahme |
| --- | --- | --- |
| MD-03 | `handbuch_infrastructure_it.md` | `DatabaseConfig.path: str \| None` → `Path \| None` |
| MD-04 | `handbuch_infrastructure_it.md` | `BackupConfig`-Felder: `str \| None` → `Path \| None` |
| MD-05 | `handbuch_infrastructure_it.md` | Tabellen-Reihenfolge: Nr. 7 = `_check_devices`, Nr. 8 = `_check_audit_hmac_key` |
| MD-07 | `handbuch_audit_it.md` | Identische Korrektur wie MD-05 |
| MD-13 | `handbuch_presentation_it.md` | `--admin-password` in Tabelle „Globale Optionen" aufnehmen |
| MD-14 | `handbuch_presentation_it.md` | Fehlermeldungen auf exakte UI-Texte aus `_DOMAIN_MESSAGES` aktualisieren |

---

## 7. Übersichtstabelle

| ID | Datei | Typ | Schwere | Status |
| --- | --- | --- | --- | --- |
| BR-01 | `befehlsreferenz.md` | `--numpad` in `verify_hardware.py` | FEHLER | Priorität 0 |
| MD-01 | `handbuch_overview_laien.md` | `export-pdf-month --output` | FEHLER | Priorität 0 |
| MD-02 | `handbuch_overview_laien.md` | `export-csv --output` + fehlende Pflichtargs | FEHLER | Priorität 0 |
| MD-03 | `handbuch_infrastructure_it.md` | `DatabaseConfig.path` Typ `str` statt `Path` | HINWEIS | Priorität 2 |
| MD-04 | `handbuch_infrastructure_it.md` | `BackupConfig`-Felder Typ `str` statt `Path` | HINWEIS | Priorität 2 |
| MD-05 | `handbuch_infrastructure_it.md` | Checks 7/8 in Tabelle vertauscht | HINWEIS | Priorität 2 |
| MD-06 | `handbuch_audit_it.md` | `audit verify-chain` nicht dokumentiert | HINWEIS | Priorität 1 |
| MD-07 | `handbuch_audit_it.md` | Checks 7/8 in Tabelle vertauscht | HINWEIS | Priorität 2 |
| MD-08 | `handbuch_audit_laien.md` | Systemcheck „7 Punkte" statt 8 | FEHLER | Priorität 1 |
| MD-09 | `handbuch_presentation_it.md` | `audit verify-chain` fehlt in Tabelle | FEHLER | Priorität 1 |
| MD-10 | `handbuch_presentation_it.md` | `system check (7 Checks)` statt 8 | FEHLER | Priorität 1 |
| MD-11 | `handbuch_presentation_it.md` | `--password-hash` statt `--password` | FEHLER | Priorität 0 |
| MD-12 | `handbuch_presentation_it.md` | `export-pdf-month --output` | FEHLER | Priorität 0 |
| MD-13 | `handbuch_presentation_it.md` | `--admin-password` fehlt in Globale Optionen | HINWEIS | Priorität 2 |
| MD-14 | `handbuch_presentation_it.md` | Fehlermeldungen nicht wortgetreu | HINWEIS | Priorität 2 |
| MD-15 | `handbuch_presentation_laien.md` | `employees deactivate --employee-id` statt positional | FEHLER | Priorität 0 |
| MD-16 | `handbuch_presentation_laien.md` | `cards deactivate --card-id` statt positional | FEHLER | Priorität 0 |
| MD-17 | `handbuch_presentation_laien.md` | `warn-cases` ohne Pflichtargs `--from`/`--to` | FEHLER | Priorität 0 |
| MD-18 | `handbuch_presentation_laien.md` | `export-pdf-month --output` | FEHLER | Priorität 0 |
| MD-19 | `handbuch_presentation_laien.md` | `export-csv --output` + fehlende Pflichtargs | FEHLER | Priorität 0 |

**Gesamtzählung:** 13 FEHLER, 7 HINWEISE, alle anderen Abschnitte BESTÄTIGT.

**Fehler nach Priorität:** 9 × Priorität 0, 4 × Priorität 1, 0 × Priorität 2

**Hinweise nach Priorität:** 0 × Priorität 0, 1 × Priorität 1, 6 × Priorität 2
