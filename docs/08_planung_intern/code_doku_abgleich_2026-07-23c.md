# Quellcode–Dokumentation-Abgleich: `admin_cli` und `terminal_ui` (Revision 3)

**Stand:** 2026-07-23
**Geprüfte Quellen:** Quellcode-Stand HEAD (`main`), Dokumentation Stand Juli 2026
**Prüfumfang:** `admin_cli` (11 Quelldateien), `terminal_ui` (3 Quelldateien),
Hilfsskripte (3 Dateien), Infrastruktur-Helfer (3 Dateien), Migrationen (9 SQL-Dateien),
Befehlsreferenz, Installationsanleitung, Handbuch (Hauptdokument),
16 Modul-Dokumentationsdateien

---

## 1. Analyse-Grundlage

### 1.1 Neue Quellcode-Sachverhalte seit Revision 2

Seit Revision 2 (2026-07-23b) wurden folgende Änderungen am Quellcode vorgenommen,
die neue Prüfpunkte erzeugen:

**Migration 0008** (`0008_remove_booking_status_closed_with_note.sql`):
Entfernt `CLOSED_WITH_NOTE` aus dem `CHECK`-Constraint von
`time_bookings.current_status` und `booking_status_history.new_status`.
Der Wert war laut SQL-Kommentar nie von einem Use Case gesetzt worden und
ist fachlich nicht vorgesehen.

**Migration 0009** (`0009_audit_log_chain_hash.sql`):
Fügt `chain_hash TEXT` zur Tabelle `audit_log` hinzu
(`ALTER TABLE audit_log ADD COLUMN chain_hash TEXT`).
Bestehende Einträge erhalten `chain_hash = NULL`;
neue Einträge erhalten einen HMAC-SHA256-Hash als Kettensignatur.

**Neuer Admin-CLI-Befehl `audit verify-chain`** (`audit.py` v1.1):
Prüft die HMAC-SHA256-Kettensignatur des gesamten Audit-Logs.
Bei gebrochener Kette gibt er **alle** fehlerhaften IDs aus:

```python
print(
    f"FEHLER: {len(broken)} Eintrag(-einträge) mit ungültigem Kettenhash: IDs {broken}",
    file=sys.stderr,
)
```

Exit-Code 1 bei fehlendem `AUDIT_HMAC_KEY` oder bei mindestens einem
ungültigen Eintrag.

**Neuer Systemcheck** (`system_check.py` v1.3):
`_check_audit_hmac_key()` ist die achte und letzte Prüfung in `run_system_check()`.

### 1.2 Globales Argument `--db` — Syntaxregel

Das Argument `--db` ist ausschließlich am Top-Level-Parser
(`admin_cli/main.py` v1.5) registriert. Es muss daher **vor** dem Domain-Namen stehen:

```bash
# korrekt (befehlsreferenz.md v1.7, handbuch.md v2.2):
azadmin --db arbeitszeit.db system check
azadmin --db arbeitszeit.db audit open-shifts

# fehlerhaft — scheitert mit "unrecognized arguments: --db":
azadmin system check --db arbeitszeit.db
azadmin audit open-shifts --db arbeitszeit.db
```

Befehlsreferenz (v1.7) und Handbuch (v2.2) verwenden durchgängig die korrekte Form
und können als Vorbilder für Syntaxbeispiele in Modul-Dokumentationen dienen.

---

## 2. Befunde: Befehlsreferenz und Installationsanleitung

**Befehlsreferenz** (`docs/03_installation_technik/befehlsreferenz.md` v1.7):
BESTÄTIGT — alle `--db`-Beispiele korrekt positioniert, alle Befehle, Argumente
und Rollenzuordnungen korrekt.

**Installationsanleitung** (`docs/03_installation_technik/installationsanleitung.md` v1.9):
BESTÄTIGT — keine Fehler.

---

## 3. Befunde: Handbuch (`docs/02_anwender/handbuch.md`)

### F05 — HINWEIS: Versionstabelle endet bei v1.9

**Fundstelle:** Abschnitt „Versionsvermerk" am Dokumentende

**Dokumentation behauptet:** Dokumentheader `**Version:** 2.2`. Der letzte
Eintrag in der Versionstabelle ist `v1.9 | 2026-07-20`.
Die Versionen v2.0, v2.1 und v2.2 fehlen vollständig in der Tabelle.

**Tatsächlicher Code:** Nicht zutreffend (rein dokumentinterne Inkonsistenz).

**Auswirkung:** Die Änderungshistorie seit v1.9 ist nicht nachvollziehbar.

---

## 4. Befunde: Modul-Dokumentation (`docs/02_anwender/module/`)

### 4.01 `handbuch_overview_it.md` (v1.1)

#### F07 — HINWEIS: Migrationszählung widersprüchlich und veraltet

**Fundstellen:** Fließtext (Abschnitt „Datenbankmigrationen") und Verzeichnisbaum

**Dokumentation behauptet:**

- Fließtext: „7 Migrationen"
- Verzeichnisbaum: `migrations/ # 0001–0006`

**Tatsächlicher Code:** Das Verzeichnis `migrations/` enthält 9 Dateien:
`0001_schema.sql` bis `0009_audit_log_chain_hash.sql`.

**Auswirkung:** Fließtext und Verzeichnisbaum nennen beide falsche Zählstände
und widersprechen sich zusätzlich gegenseitig.

### 4.02 `handbuch_presentation_it.md` (v1.3)

#### F01-A — FEHLER: `--db` nach Subcommand in drei Beispielen

**Fundstellen:**

| Zeile | Falsche Syntax |
| --- | --- |
| 178 | `azadmin system check --db arbeitszeit.db` |
| 179 | `azadmin system backup --db arbeitszeit.db` |
| 215 | `azadmin audit open-shifts --db arbeitszeit.db` |

**Tatsächlicher Code** (`admin_cli/main.py` v1.5):
`--db` ist am Top-Level-Parser registriert und muss vor dem Domain-Namen stehen.
Alle drei Beispiele scheitern mit `unrecognized arguments: --db`.

**Auswirkung:** Übernommene Beispiele funktionieren nicht.

#### F03 — FEHLER: Terminal-UI-Initialisierungsreihenfolge fehlerhaft

**Fundstelle:** Abschnitt „Initialisierungsschritte", Zeilen 239–244

**Dokumentation behauptet (6 Schritte innerhalb von `run()`):**

1. `resolve_evdev_device()`
2. `run_system_check()`
3. `_ensure_terminal_exists()`
4. `_setup_file_logging()`
5. `load_threshold_from_config(db_path)`
6. `DebouncedHardwareReader(EvdevHardwareReader(...))`

**Tatsächlicher Code** (`terminal_ui/main.py` v1.7):

`_setup_file_logging()` wird in `main()` aufgerufen, **bevor** `run()` startet —
nicht als Schritt 4 innerhalb von `run()`.

Innerhalb von `run()` fehlen drei Schritte, die die Dokumentation nicht aufführt:

- Nach Schritt 3: Registrierung der Signal-Handler für `SIGTERM` und `SIGINT`
  (setzen `running = False` für sauberes Beenden der Endlosschleife)
- Nach dem aktuellen Schritt 5 (`load_threshold_from_config()`):
  Instanziierung von `SystemTimeMonitor()`
- Unmittelbar danach: erster Aufruf von `monitor.check()` zur Basiszeitpunkt-Setzung
  (vor dem Start der Buchungsschleife)

**Auswirkung:** Entwickler erhalten ein falsches Bild der Initialisierungsreihenfolge.
Signal-Handler-Registrierung und Zeitüberwachungsinitialisierung fehlen vollständig.

### 4.03 `handbuch_audit_it.md` (v1.3)

#### F01-B — FEHLER: `--db` nach Subcommand in drei Beispielen

**Fundstellen:**

| Zeile | Falsche Syntax |
| --- | --- |
| 83 | `azadmin system check --db arbeitszeit.db` |
| 123 | `azadmin audit open-shifts --db arbeitszeit.db [--days N]` |
| 164 | `azadmin audit verify-chain --db arbeitszeit.db` |

**Tatsächlicher Code** (`admin_cli/main.py` v1.5):
`--db` muss vor dem Domain-Namen stehen. Alle drei Beispiele scheitern
mit `unrecognized arguments: --db`.

**Auswirkung:** Übernommene Beispiele funktionieren nicht.

#### F02 — FEHLER: `audit verify-chain` gibt ALLE fehlerhaften IDs aus

**Fundstelle:** Tabelle „Szenario / Exit-Code / Ausgabe", Zeile 177

**Dokumentation behauptet:**

> `Mindestens ein Hash stimmt nicht überein | 1 | Fehlermeldung mit erstem fehlerhaften Eintrag`

**Tatsächlicher Code** (`audit.py` v1.1, Zeilen 155–160):

```python
print(
    f"FEHLER: {len(broken)} Eintrag(-einträge) mit ungültigem Kettenhash: IDs {broken}",
    file=sys.stderr,
)
```

Die Variable `broken` ist eine Liste aller ungültigen IDs. Die Ausgabe nennt
Gesamtanzahl und vollständige Liste — **nicht** nur den ersten fehlerhaften Eintrag.

**Auswirkung:** Administratoren, die die Dokumentation lesen, unterschätzen das
mögliche Ausmaß einer Integritätsverletzung des Audit-Logs.

### 4.04 `handbuch_infrastructure_it.md` (v1.3)

#### F06 — HINWEIS: `debounce.py` fehlt im Verzeichnisbaum

**Fundstelle:** Abschnitt „Verzeichnisstruktur", Zeilen 18–34

**Dokumentation behauptet:**

```text
hardware/
└── evdev_reader.py
```

**Tatsächlicher Code:** Das Verzeichnis `src/arbeitszeit/infrastructure/hardware/`
enthält zwei Dateien: `evdev_reader.py` (v1.4) und `debounce.py` (v1.0,
`DebouncedHardwareReader`).

`debounce.py` wird im Fließtext desselben Dokuments (Abschnitt „Doppel-Scan-Schutz",
Zeilen 155–170) korrekt beschrieben — lediglich der Verzeichnisbaum ist unvollständig.

**Auswirkung:** Der Verzeichnisbaum vermittelt ein unvollständiges Bild der Modulstruktur.

### 4.05 `handbuch_infrastructure_laien.md` (v1.1)

#### F01-D — FEHLER: `--db` nach Subcommand in zwei Beispielen

**Fundstellen:**

| Zeile | Falsche Syntax |
| --- | --- |
| 54 | `azadmin system backup --db arbeitszeit.db` |
| 72 | `azadmin system check --db arbeitszeit.db` |

**Tatsächlicher Code** (`admin_cli/main.py` v1.5):
`--db` muss vor dem Domain-Namen stehen. Beide Beispiele scheitern
mit `unrecognized arguments: --db`.

**Auswirkung:** Praxisleitung oder Verwaltung, die diese Befehle ausführen,
erhalten eine Fehlermeldung.

### 4.06 `handbuch_audit_laien.md` (v1.2)

#### F01-C — FEHLER: `--db` nach Subcommand in drei Beispielen

**Fundstellen:**

| Zeile | Falsche Syntax |
| --- | --- |
| 31 | `azadmin system check --db arbeitszeit.db` |
| 60 | `azadmin audit open-shifts --db arbeitszeit.db` |
| 68 | `azadmin audit open-shifts --db arbeitszeit.db --days 90` |

**Tatsächlicher Code** (`admin_cli/main.py` v1.5):
`--db` muss vor dem Domain-Namen stehen. Alle drei Beispiele scheitern
mit `unrecognized arguments: --db`.

**Auswirkung:** Praxisleitung oder Verwaltung, die diese Befehle ausführen,
erhalten eine Fehlermeldung.

### 4.07 `handbuch_datenbankschema_it.md` (v1.1)

#### F04 — FEHLER: Schema-Dokumentation veraltet (fehlt Migrationen 0008 und 0009)

**Fundstellen:** Dokumentheader (Zeile 7), Migrationsübersicht (Zeilen 19–27),
Abschnittsüberschrift (Zeile 31), Tabelle `time_bookings` (Zeile 107),
Tabelle `booking_status_history` (Zeile 129), Tabelle `audit_log` (Zeilen 329–344)

**Dokumentation behauptet:**

- Zeile 7: `Quelldateien: migrations/0001_schema.sql bis migrations/0007_remove_numpad_grace_config.sql`
- Zeile 31: „Tabellen im finalen Zustand (nach Migration 0007)"
- Zeile 107: `current_status` CHECK enthält u. a. `'CLOSED_WITH_NOTE'`
- Zeile 129: `new_status` CHECK enthält u. a. `'CLOSED_WITH_NOTE'`
- Tabelle `audit_log` (Zeilen 329–344): keine Spalte `chain_hash`

**Tatsächlicher Code:** Es existieren 9 Migrationen (0001–0009).

Migration 0008 (`0008_remove_booking_status_closed_with_note.sql`) entfernt
`CLOSED_WITH_NOTE` aus:

- `time_bookings.current_status` — gültige Werte danach:
  `'OK'`, `'OPEN'`, `'WARN'`, `'NEEDS_REVIEW'`, `'CORRECTED'`
- `booking_status_history.new_status` — gültige Werte danach:
  `'OK'`, `'OPEN'`, `'WARN'`, `'NEEDS_REVIEW'`, `'CORRECTED'`, `'MANUAL_ENTRY'`

Migration 0009 (`0009_audit_log_chain_hash.sql`):
`ALTER TABLE audit_log ADD COLUMN chain_hash TEXT;`

**Auswirkung:** Das Dokument beschreibt CHECK-Constraints mit `CLOSED_WITH_NOTE`,
der in produktiven Datenbanken (nach Migration 0008) nicht mehr gültig ist.
Die `chain_hash`-Spalte, über die `audit verify-chain` die HMAC-Kettensignatur
prüft, ist nicht dokumentiert. Entwickler, die das Dokument als Referenz nutzen,
erhalten ein veraltetes Bild des Datenbankschemas.

### 4.08 `handbuch_datenbankschema_laien.md` (v1.0)

#### F01-E — FEHLER: `--db` nach Subcommand

**Fundstelle:** Abschnitt „Backup und Wiederherstellung", Codeblock (Zeile 40)

**Dokumentation:** `azadmin system backup --db arbeitszeit.db`

**Tatsächlicher Code** (`admin_cli/main.py` v1.5):
`--db` muss vor dem Domain-Namen stehen.
Befehl scheitert mit `unrecognized arguments: --db`.

**Auswirkung:** Praxisleitung oder Verwaltung, die diesen Befehl ausführen,
erhalten eine Fehlermeldung.

### 4.09 `handbuch_presentation_laien.md` (v1.3)

#### F01-F — FEHLER: `--db` nach Subcommand

**Fundstelle:** Abschnitt „Offene Vortagsschichten prüfen", Zeile 170

**Dokumentation:** `azadmin audit open-shifts --db arbeitszeit.db`

**Tatsächlicher Code** (`admin_cli/main.py` v1.5):
`--db` muss vor dem Domain-Namen stehen.
Befehl scheitert mit `unrecognized arguments: --db`.

**Auswirkung:** Praxisleitung oder Verwaltung, die diesen Befehl ausführen,
erhalten eine Fehlermeldung.

### Bestätigte Dokumente ohne Befund

| Dokument | Version | Ergebnis |
| --- | --- | --- |
| `handbuch_overview_laien.md` | v1.2 | BESTÄTIGT |
| `handbuch_application_it.md` | v1.1 | BESTÄTIGT |
| `handbuch_application_laien.md` | v1.1 | BESTÄTIGT |
| `handbuch_domain_it.md` | v1.1 | BESTÄTIGT |
| `handbuch_domain_laien.md` | v1.1 | BESTÄTIGT |
| `handbuch_show_config_it.md` | v1.1 | BESTÄTIGT |
| `handbuch_show_config_laien.md` | v1.1 | BESTÄTIGT |

---

## 5. Handlungsvorschläge

### Priorität 0 — sofort beheben (Befehle scheitern)

| ID | Datei | Maßnahme |
| --- | --- | --- |
| F01-A | `handbuch_presentation_it.md` | Zeilen 178, 179, 215: `--db` vor den Domain-Namen verschieben |
| F01-B | `handbuch_audit_it.md` | Zeilen 83, 123, 164: `--db` vor den Domain-Namen verschieben |
| F01-C | `handbuch_audit_laien.md` | Zeilen 31, 60, 68: `--db` vor den Domain-Namen verschieben |
| F01-D | `handbuch_infrastructure_laien.md` | Zeilen 54, 72: `--db` vor den Domain-Namen verschieben |
| F01-E | `handbuch_datenbankschema_laien.md` | Zeile 40: `--db` vor den Domain-Namen verschieben |
| F01-F | `handbuch_presentation_laien.md` | Zeile 170: `--db` vor den Domain-Namen verschieben |

Korrekte Form für alle betroffenen Befehle:

```bash
azadmin --db arbeitszeit.db system check
azadmin --db arbeitszeit.db system backup
azadmin --db arbeitszeit.db audit open-shifts [--days N]
azadmin --db arbeitszeit.db audit open-shifts --days 90
azadmin --db arbeitszeit.db audit verify-chain
```

### Priorität 1 — bald beheben (inhaltlich falsch)

| ID | Datei | Maßnahme |
| --- | --- | --- |
| F02 | `handbuch_audit_it.md` | Zeile 177: „erstem fehlerhaften Eintrag" → „allen fehlerhaften Einträgen (Gesamtanzahl und vollständige ID-Liste)" |
| F03 | `handbuch_presentation_it.md` | Initialisierungsschritte neu formulieren: `_setup_file_logging()` entfernen (läuft in `main()` vor `run()`); Signal-Handler-Registrierung ergänzen; `SystemTimeMonitor()`-Instanziierung und `monitor.check()`-Aufruf als fehlende Schritte vor dem Reader-Setup ergänzen |
| F04 | `handbuch_datenbankschema_it.md` | Migrationsübersicht um 0008 und 0009 ergänzen; `time_bookings.current_status` und `booking_status_history.new_status` ohne `CLOSED_WITH_NOTE` aktualisieren; `audit_log`-Tabelle um Spalte `chain_hash TEXT` ergänzen; Abschnittüberschrift und Header von „nach Migration 0007" auf „nach Migration 0009" aktualisieren |

### Priorität 2 — bei Gelegenheit (Präzision und Vollständigkeit)

| ID | Datei | Maßnahme |
| --- | --- | --- |
| F05 | `handbuch.md` | Versionstabelle um v2.0, v2.1 und v2.2 ergänzen |
| F06 | `handbuch_infrastructure_it.md` | `debounce.py` im Verzeichnisbaum unter `hardware/` ergänzen |
| F07 | `handbuch_overview_it.md` | Fließtext und Verzeichnisbaum auf 9 Migrationen (0001–0009) aktualisieren |

---

## 6. Übersichtstabelle

| ID | Datei | Befund | Schwere | Status |
| --- | --- | --- | --- | --- |
| F01-A | `handbuch_presentation_it.md` | `--db` nach Subcommand (3 Stellen: Z. 178, 179, 215) | FEHLER P0 | erledigt 2026-07-23 |
| F01-B | `handbuch_audit_it.md` | `--db` nach Subcommand (3 Stellen: Z. 83, 123, 164) | FEHLER P0 | erledigt 2026-07-23 |
| F01-C | `handbuch_audit_laien.md` | `--db` nach Subcommand (3 Stellen: Z. 31, 60, 68) | FEHLER P0 | erledigt 2026-07-23 |
| F01-D | `handbuch_infrastructure_laien.md` | `--db` nach Subcommand (2 Stellen: Z. 54, 72) | FEHLER P0 | erledigt 2026-07-23 |
| F01-E | `handbuch_datenbankschema_laien.md` | `--db` nach Subcommand (1 Stelle: Z. 40) | FEHLER P0 | erledigt 2026-07-23 |
| F01-F | `handbuch_presentation_laien.md` | `--db` nach Subcommand (1 Stelle: Z. 170) | FEHLER P0 | erledigt 2026-07-23 |
| F02 | `handbuch_audit_it.md` | `verify-chain`: Ausgabe nennt alle IDs, nicht nur den ersten | FEHLER P1 | erledigt 2026-07-23 |
| F03 | `handbuch_presentation_it.md` | Terminal-UI-Initialisierungsreihenfolge fehlerhaft | FEHLER P1 | erledigt 2026-07-23 |
| F04 | `handbuch_datenbankschema_it.md` | Schema nach 0007 veraltet; 0008 und 0009 fehlen | FEHLER P1 | erledigt 2026-07-23 |
| F05 | `handbuch.md` | Versionstabelle endet bei v1.9, obwohl Dokument v2.2 | HINWEIS P2 | erledigt 2026-07-23 |
| F06 | `handbuch_infrastructure_it.md` | `debounce.py` fehlt im Verzeichnisbaum | HINWEIS P2 | erledigt 2026-07-23 |
| F07 | `handbuch_overview_it.md` | Migrationszählung: Text „7", Baum „0001–0006", tatsächlich 9 | HINWEIS P2 | erledigt 2026-07-23 |

---

## 7. Gesamtzählung und Qualitätsurteil

**Befunde gesamt:** 12 (9 FEHLER, 3 HINWEISE)

- P0-FEHLER (Befehl scheitert): 6 Einträge — 13 konkrete Stellen in 6 Dokumenten
- P1-FEHLER (inhaltlich falsch): 3 Einträge
- P2-HINWEISE (Präzision): 3 Einträge

**Betroffene Dokumente:** 10 von 19 geprüften Dokumenten

**Unverändert korrekte Dokumente (9):**
`befehlsreferenz.md`, `installationsanleitung.md`, `handbuch_overview_laien.md`,
`handbuch_application_it.md`, `handbuch_application_laien.md`,
`handbuch_domain_it.md`, `handbuch_domain_laien.md`,
`handbuch_show_config_it.md`, `handbuch_show_config_laien.md`

**Qualitätsurteil:**

Die Revision-2-Korrekturen (2026-07-23b) haben alle 20 dort dokumentierten Befunde
beseitigt — ein vollständiger und disziplinierter Korrekturdurchgang.

Die vorliegende Revision 3 offenbart einen systemic verbreiteten Syntaxfehler
bei der `--db`-Positionierung: 13 Stellen in 6 Dokumenten zeigen identisch
falsche Beispiele. Ursache ist vermutlich eine fehlerhafte Vorlage, die beim
Erstellen oder Überarbeiten mehrerer Modul-Dokumente kopiert wurde. Befehlsreferenz
(v1.7) und Handbuch (v2.2) sind davon nicht betroffen und können als korrektes
Vorlagemuster für Syntaxbeispiele dienen.

Die inhaltlichen Fehler F02–F04 haben einen anderen Ursprung: Migrationen 0008
und 0009 sowie die neuen Ausgabedetails von `audit verify-chain` wurden nach
dem Erstellen der betroffenen Dokumente eingeführt. Die Dokumentation spiegelt
die aktuelle Codebasis dort nicht wider.

Der Fehler F03 (Terminal-UI-Initialisierungsreihenfolge) ist der einzige Befund,
der eine inhaltlich falsche Beschreibung einer bestehenden Implementierung darstellt —
`_setup_file_logging()` wird im Dokument falsch platziert, und drei tatsächliche
Initialisierungsschritte fehlen vollständig.
