# Handbuch – Arbeitszeiterfassung `arbeitszeit`

**Version:** 1.0 | **Stand:** Juni 2026 | **Basis:** Repository `iCodator/arbeitszeit`

---

## 1. Projektübersicht

### Was ist das System?

`arbeitszeit` ist ein **lokal betriebenes elektronisches Zeiterfassungssystem** für eine Zahnarztpraxis. Es erfasst Arbeitszeitdaten vollständig auf dem Praxisrechner – ohne Cloud-Anbindung, ohne externe Server. Die einzige Datenquelle ist eine SQLite-Datenbankdatei auf dem lokalen System.

**Quellen:** `README.md`, `pflichtenheft_arbeitszeit_v5.md`

### Zielgruppe

| Personengruppe | Aufgabe im System |
|---|---|
| Mitarbeiter/innen | Buchen Kommen, Gehen und Pausen über RFID-Chip am Terminal |
| Admin | Verwaltet Benutzerkonten, Mitarbeitende, RFID-Karten, Regelarbeitszeiten |
| Prüfer (REVIEWER) | Prüft offene und auffällige Fälle, bearbeitet Nachträge und Korrekturen |
| Technische Betreuung (TECH) | Führt Systemcheck, Backup und Restore aus |

**Quelle:** `pflichtenheft_arbeitszeit_v5.md`, Abschnitt 5

### Welche Probleme löst es?

- Rechtssichere, nachvollziehbare Erfassung von Arbeitsbeginn, -ende und Pausen gemäß BAG-Beschluss vom 13.09.2022 (1 ABR 22/21)
- Erkennung gesetzlicher Prüffälle (Pausenpflicht, Höchstarbeitszeit, Ruhezeit) nach ArbZG
- Lückenlose Protokollierung aller Buchungen, Korrekturen und Änderungen im Audit-Log
- Klarer Fallback-Prozess bei Geräteausfall (manuelle Noterfassung, später als Nachtrag)

**Quelle:** `pflichtenheft_arbeitszeit_v5.md`, Abschnitte 2, 4, 10

---

## 2. Systemvoraussetzungen

### Betriebssystem

- **Linux Mint** oder **Lubuntu** (aktuelle LTS-Version empfohlen)
- Benutzer mit `sudo`-Berechtigung
- Internetzugang für die Erstinstallation

**Quelle:** `installationsanleitung_arbeitszeit.md`, Abschnitt 2.1; `pflichtenheft_arbeitszeit_v5.md`, Abschnitt 9.1

### Python-Version

Die Datei `pyproject.toml` schreibt **Python `>=3.14,<3.15`** vor. Das ist die maßgebliche Angabe für die Installation.

Prüfen Sie die installierte Version vor der Installation:

```bash
python3 --version
```

**Quelle:** `pyproject.toml`, `installationsanleitung_arbeitszeit.md` Abschnitt 2.2

### Benötigte Hardware

| Hardware | Anschluss | Funktion |
|---|---|---|
| **RFID-Reader** | USB (HID-Keyboard-Emulation) | Liest Mitarbeiter-RFID-Chip; liefert UID als Tastatureingabe + Enter |
| **USB-Numpad** | USB (HID-Keyboard) | Tasten 1–4 für Buchungsauswahl |
| **Linux-PC / Raspberry Pi** | – | Betriebsrechner, läuft dauerhaft |
| **NAS (optional)** | Netzwerk | Backup-Ziel |

Beide Eingabegeräte erscheinen unter `/dev/input/event*` und werden über die `evdev`-Bibliothek angesteuert.

**Quelle:** `installationsanleitung_arbeitszeit.md` Abschnitt 2.4; `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`

### Abhängigkeiten aus `pyproject.toml`

**Laufzeitabhängigkeiten (werden immer installiert):**

| Paket | Mindestversion | Zweck |
|---|---|---|
| `evdev` | `>=1.7` | Zugriff auf Linux-Eingabegeräte (RFID, Numpad) |
| `reportlab` | `>=4.0` | Erzeugung von PDF-Berichten |

**Entwicklungsabhängigkeiten (mit `pip install -e .[dev]`):**

| Paket | Mindestversion | Zweck |
|---|---|---|
| `pytest` | `>=8.0` | Testausführung |
| `pytest-cov` | `>=5.0` | Code-Coverage-Messung |
| `pypdf` | `>=4.0` | PDF-Prüfung in Tests |
| `ruff` | `>=0.6` | Statische Code-Analyse (Linting) |

**Quelle:** `pyproject.toml`

### Zusätzliche Systempakete (Linux)

Da `evdev` aus C-Quellcode kompiliert wird, benötigt das System vor `pip install`:

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

**Quelle:** `installationsanleitung_arbeitszeit.md`, Abschnitt 3

---

## 3. Installation Schritt für Schritt

Der vollständige Installationsablauf laut `installationsanleitung_arbeitszeit.md` v2.0:

```
Systempakete → Repository → Venv → pip install → init_db.py → setup.py
→ ADMIN (Bootstrap) → REVIEWER/TECH anlegen → EMPLOYEE anlegen → Funktionstest → Starten
```

### Schritt 1 – Systempakete installieren

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev git
```

**Erfolgskontrolle:**
```bash
gcc --version
```
Gibt eine Versionsnummer aus? Dann ist der Compiler korrekt installiert.

### Schritt 2 – Repository herunterladen

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
```

**Erfolgskontrolle:**
```bash
ls arbeitszeit/
```
Sie sollten u. a. `pyproject.toml`, `scripts/`, `src/`, `tests/`, `README.md` sehen.

### Schritt 3 – Virtuelle Python-Umgebung erstellen und aktivieren

Eine **virtuelle Umgebung** (kurz: „venv") ist ein abgeschlossener Python-Bereich für dieses Projekt – unabhängig vom Rest des Systems. Das verhindert Konflikte mit anderen Python-Programmen.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Nach der Aktivierung erscheint `(.venv)` am Anfang der Eingabeaufforderung.

> 💡 **Tipp:** Die virtuelle Umgebung muss nach jedem Neustart des Terminals erneut aktiviert werden. Sie wird **nicht** automatisch aktiv.

### Schritt 4 – Python-Abhängigkeiten installieren

```bash
pip install -e .[dev]
```

Der Schalter `-e` steht für „editable" – Änderungen im `src/`-Verzeichnis wirken sofort.

**Erfolgskontrolle:**
```bash
pip show arbeitszeit
```
Zeigt Name `arbeitszeit`, Version `0.1.0` und den Pfad zum `src/`-Verzeichnis.

### Schritt 5 – Datenbank initialisieren

```bash
python scripts/init_db.py
```

Das Skript legt die Datenbankdatei `arbeitszeit.db` an und führt alle SQL-Migrationen durch.

**Typische Ausgabe:**
```
Migration 001 angewendet.
Migration 002 angewendet.
...
⚠  Ersteinrichtung noch erforderlich:
   python scripts/setup.py --db arbeitszeit.db
```

Abweichender Datenbankpfad (optional):
```bash
python scripts/init_db.py --db /pfad/zur/arbeitszeit.db
```

### Schritt 6 – Ersteinrichtung durchführen

```bash
python scripts/setup.py --db arbeitszeit.db
```

Das Skript fragt interaktiv nach dem **Backup-Verzeichnis** und dem **Exportverzeichnis**. Die angegebenen Verzeichnisse werden automatisch angelegt.

**Nicht-interaktiver Modus** (z. B. für automatisierte Einrichtung):
```bash
python scripts/setup.py --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
    --export-dir /var/exports/arbeitszeit
```

> ⚠️ **Reihenfolge zwingend:** `init_db.py` muss vor `setup.py` ausgeführt werden. `setup.py` prüft beim Start, ob die Datenbankdatei existiert, und bricht mit `Fehler: Datenbank nicht gefunden` ab, wenn nicht.

**Quelle:** `installationsanleitung_arbeitszeit.md`, Abschnitte 8 und 9

### Schritt 7 – Ersten Administrator anlegen (Bootstrap)

Dieser Schritt ist nur möglich, solange **kein** aktives ADMIN-Konto existiert.

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    users bootstrap \
    --username adminname
```

Wird kein `--password` angegeben, generiert das System ein sicheres Zufallspasswort:

```
Erstes Administratorkonto angelegt (ID 1).
Generiertes Passwort (einmalig sichtbar): xY3-mNpQ8rTz
```

> ⚠️ **Wichtig:** Das generierte Passwort wird **nur einmalig** angezeigt und ist nicht im Klartext in der Datenbank gespeichert. Notieren Sie es sofort sicher.

**Erfolgskontrolle:**
```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users list
```

### Schritt 8 – REVIEWER und TECH anlegen

```bash
# Prüfer anlegen
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users add \
    --username pruefer01 \
    --role REVIEWER

# Technische Betreuung anlegen
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users add \
    --username technik01 \
    --role TECH
```

> 💡 **Tipp:** Die Benutzer-ID des ausführenden Admins kann auch über die Umgebungsvariable `ADMIN_USER_ID` gesetzt werden:
> ```bash
> export ADMIN_USER_ID=1
> ```

### Schritt 9 – Mitarbeiter und RFID-Karten anlegen

> ⚠️ **Wichtiger Unterschied:** `EMPLOYEE` ist **kein** Benutzerkonto wie ADMIN, REVIEWER oder TECH. Mitarbeiter werden als Datensätze in der Tabelle `employees` angelegt und buchen ausschließlich per RFID-Chip – nicht per Login.

```bash
# Mitarbeiter anlegen
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    employees add \
    --personnel-no M001 \
    --first-name Maria \
    --last-name Mustermann

# RFID-Karte dem Mitarbeiter zuweisen
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    cards assign \
    --employee-id 1 \
    --uid-hash <SHA256-HASH-DER-KARTE>
```

Den SHA-256-Hash der RFID-Karte berechnet das System intern über `src/arbeitszeit/infrastructure/hardware/uid_hash.py` (SHA-256 der Roh-UID). Für die erstmalige Ermittlung: Terminal-UI im Testmodus starten und Protokoll auslesen.

### Schritt 10 – Funktionstest

```bash
pytest
pytest tests/test_migrations.py   # Migrationstests gezielt
pytest --cov=arbeitszeit          # Mit Coverage-Bericht
```

Alle Tests sollten mit `passed` abschließen, keine `FAILED`-Zeilen.

### Schritt 11 – Systemcheck

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    system check
```

**Quelle für alle Schritte:** `installationsanleitung_arbeitszeit.md`, Abschnitte 3–14

### Häufige Fehler und deren Behebung

| Fehlermeldung | Ursache | Lösung |
|---|---|---|
| `gcc: command not found` | C-Compiler fehlt (nötig für evdev) | `sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev` |
| `Python.h: No such file or directory` | Python-Entwicklerdateien fehlen | `sudo apt install -y python3-dev` |
| `Fehler: Datenbank nicht gefunden: arbeitszeit.db` | `setup.py` vor `init_db.py` ausgeführt | Zuerst `python scripts/init_db.py` ausführen |
| `Es existiert bereits ein aktives Administratorkonto. Bootstrap nicht möglich.` | Bootstrap zweimal ausgeführt | `users add --role ADMIN` mit bestehendem Admin verwenden |
| `Fehler: Zugriff verweigert. Aktion erfordert ADMIN-Rolle.` | `--user-id` gehört nicht zu einem aktiven Admin | `users list` ausführen, korrekte ID verwenden |
| `Fehler: Benutzername bereits vergeben.` | Benutzername existiert bereits | Anderen Benutzernamen wählen |
| Terminal-UI startet nicht: Gerätedatei nicht gefunden | Falscher Pfad für `--numpad` oder `--rfid` | `ls /dev/input/by-id/` oder `sudo evtest` zur Ermittlung |

**Quelle:** `installationsanleitung_arbeitszeit.md`, Abschnitt 15

---

## 4. Projektstruktur

### Verzeichnisbaum

```
arbeitszeit/                        ← Projektwurzel
├── .gitignore                      ← Git-Ausschlussliste
├── .python-version                 ← Python-Versionsangabe
├── pyproject.toml                  ← Paketdefinition, Abhängigkeiten, pytest-Konfiguration
├── README.md                       ← Kurzüberblick und Einstieg
├── pflichtenheft_arbeitszeit_v5.md ← Verbindliche fachliche & technische Anforderungen
├── regelwerk_arbeitszeit_v5.md     ← Fachliche Betriebs- und Prüfregeln
├── installationsanleitung_arbeitszeit.md ← Vollständige Installationsanleitung v2.0
│
├── migrations/                     ← SQL-Migrationsdateien (Datenbankschema)
│   ├── 0001_schema.sql             ← Vollständiges Datenbankschema (alle Tabellen)
│   ├── 0002_seed_defaults.sql      ← Standard-Grunddaten (Regelarbeitszeiten etc.)
│   ├── 0003_cleanup_booking_status.sql
│   ├── 0004_supplement_reject_fields_and_review_note.sql
│   ├── 0005_time_bookings_device_event_id.sql
│   └── 0006_system_events_application_error.sql
│
├── scripts/                        ← Hilfsskripte für Setup und Betrieb
│   ├── init_db.py                  ← Datenbank anlegen und Migrationen einspielen
│   ├── setup.py                    ← Ersteinrichtung (Backup-/Exportverzeichnis)
│   └── backup.py                   ← Backup manuell anstoßen
│
├── src/
│   └── arbeitszeit/                ← Python-Paket im src-Layout
│       ├── __init__.py
│       ├── domain/                 ← Fachlogik (kernste Schicht, kein Framework)
│       ├── application/            ← Anwendungsfälle (Use Cases)
│       ├── infrastructure/         ← Datenbank, Hardware, Export, Backup
│       └── presentation/           ← Benutzeroberflächen (Terminal-UI, Admin-CLI)
│
├── tests/                          ← Automatisierte Tests
│   └── test_migrations.py          ← Migrationstests (explizit belegt)
│
└── docs/                           ← Ergänzende Dokumentation
```

**Quelle:** `README.md`, Verzeichnislisting des Repositories

### Architekturprinzip – Die vier Schichten erklärt

Das System folgt einer **strikten Schichtenarchitektur** (auch „Clean Architecture" oder „Onion Architecture" genannt). Das bedeutet: Jede Schicht kennt nur die Schichten darunter – niemals darüber. Das schützt die Fachlogik vor technischen Änderungen.

```
┌──────────────────────────────────────┐
│  presentation/                       │  ← Was der Benutzer sieht (Terminal, CLI)
├──────────────────────────────────────┤
│  infrastructure/                     │  ← Technik: Datenbank, Hardware, Export
├──────────────────────────────────────┤
│  application/                        │  ← Was das System tun soll (Use Cases)
├──────────────────────────────────────┤
│  domain/                             │  ← Fachregeln (unabhängig von Technik)
└──────────────────────────────────────┘
```

**`domain/` – Das Herzstück**
Enthält alle fachlichen Objekte (`entities.py`), Aufzählungen (`enums.py`), Fehlerklassen (`errors.py`) und den Audit-Ereigniskatalog (`audit_events.py`). Diese Schicht hat **keine** Abhängigkeit zu Datenbank, Hardware oder Framework. Sie kann isoliert getestet werden.

**`application/` – Was das System tun soll**
Enthält die konkreten Anwendungsfälle (Use Cases): Buchung erfassen (`book_time.py`), Buchung korrigieren (`correct_booking.py`), Nachtrag erstellen (`register_supplement.py`), Nachtrag genehmigen (`approve_supplement.py`), Nachtrag ablehnen (`reject_supplement.py`), Regelarbeitszeit verwalten (`manage_work_schedule.py`). Außerdem: Kommandos (`commands.py`), Ergebnisse (`results.py`) und die Unit-of-Work-Abstraktion (`unit_of_work.py`).

**`infrastructure/` – Die Technikschicht**
Konkrete Umsetzung von Datenbankzugriff, Hardware-Lesern, Export und Backup. Enthält auch `system_check.py` (Systemprüfung vor Start) und `time_monitor.py` (Überwachung der Systemzeit).

**`presentation/` – Benutzeroberflächen**
- `terminal_ui/main.py`: Dauerbetrieb für Buchungen (Endlosschleife)
- `admin_cli/main.py`: Administrative Kommandozeile

**Quelle:** `README.md`, `src/arbeitszeit/`-Verzeichnislisting, `src/arbeitszeit/application/use_cases/`-Listing

---

## 5. Fachliches Regelwerk

### Buchungsarten

Laut `src/arbeitszeit/domain/enums.py` (Enum `BookingType`) sind genau vier Buchungsarten zulässig:

| Taste am Numpad | Interner Code | Bedeutung |
|:---:|---|---|
| **1** | `COME` | Kommen – Arbeitsbeginn |
| **2** | `GO` | Gehen – Arbeitsende |
| **3** | `BREAK_START` | Pause Start |
| **4** | `BREAK_END` | Pause Ende |

Andere Buchungsarten existieren im System nicht. Andere Tastencodes werden ignoriert.

**Quelle:** `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`

### Verbindlicher Bedienablauf

Der einzig gültige Standardablauf laut `regelwerk_arbeitszeit_v5.md` (Abschnitt 3):

1. **Buchungsart wählen** – Taste 1, 2, 3 oder 4 am USB-Numpad drücken
2. **RFID-Chip scannen** – Chip an den RFID-Reader halten

Andere Reihenfolgen gelten nicht als Standardprozess.

### Buchungsstatus (`BookingStatus`)

Jede Buchung trägt einen Status, der ihren Prüf- und Bearbeitungsstand anzeigt:

| Status | Bedeutung |
|---|---|
| `OK` | Buchung geprüft und in Ordnung |
| `OPEN` | Offene Buchung – Phase nicht abgeschlossen |
| `WARN` | Auffällig – Warnung liegt vor |
| `NEEDS_REVIEW` | Muss geprüft werden |
| `CORRECTED` | Wurde nachträglich korrigiert |
| `CLOSED_WITH_NOTE` | Abgeschlossen mit Begründungsnotiz |

**Quelle:** `src/arbeitszeit/domain/enums.py`, `regelwerk_arbeitszeit_v5.md` Abschnitt 11

### Prüffalltypen (`ReviewCaseType`)

Prüffälle werden **orthogonal** zu Buchungsstatus modelliert, d. h. als eigene Datensätze in der Tabelle `review_cases`. Folgende Typen sind im System definiert:

| Typ | Bedeutung |
|---|---|
| `OPEN_WORK_PHASE` | Offene Arbeitsphase |
| `OPEN_BREAK_PHASE` | Offene Pause |
| `OUTSIDE_SCHEDULE_WINDOW` | Buchung außerhalb Regelzeit |
| `POSSIBLE_BREAK_VIOLATION` | Möglicher Pausenverstoß (ArbZG §4) |
| `POSSIBLE_REST_VIOLATION` | Möglicher Ruhezeitverstoß (ArbZG §5) |
| `POSSIBLE_MAX_HOURS_VIOLATION` | Mögliche Überschreitung Höchstarbeitszeit (ArbZG §3) |
| `IMPLAUSIBLE_SEQUENCE` | Unplausible Buchungsfolge |
| `UNKNOWN_CARD_ATTEMPT` | Unbekannte RFID-Karte |
| `INACTIVE_CARD_ATTEMPT` | Inaktive RFID-Karte |
| `TIME_ANOMALY` | Zeitsprung oder Uhrzeitabweichung |
| `MANUAL_ENTRY_REVIEW` | Nachtrag zur Prüfung |

**Quelle:** `src/arbeitszeit/domain/enums.py`

### Schweregrade (`ReviewSeverity`)

| Schweregrad | Bedeutung |
|---|---|
| `INFO` | Informationshinweis |
| `WARN` | Warnung |
| `CRITICAL` | Kritisch, dringend zu klären |

### Plausibilitätsregeln

Folgende Buchungsfolgen sind unzulässig oder auffällig (aus `regelwerk_arbeitszeit_v5.md`, Abschnitt 6):

- `Kommen` nach `Kommen`
- `Gehen` nach `Gehen`
- `Pause Start` nach `Pause Start`
- `Pause Ende` ohne offene Pause
- `Pause Start` nach `Gehen`
- `Kommen` während offener Pause
- `Gehen` bei offener Pause ohne Klärung
- erste Tagesbuchung als `Gehen` oder `Pause Ende`

Das System verwirft oder markiert solche Buchungen – es schreibt sie niemals still als gültig in die Datenbank.

### Regelarbeitszeiten

Die Standardzeiten (aus `regelwerk_arbeitszeit_v5.md` Abschnitt 7 und `pflichtenheft_arbeitszeit_v5.md` Abschnitt 7.8) dienen als **Prüfrahmen**, nicht als automatische Endbuchung:

| Wochentag | Beginn | Ende |
|---|---:|---:|
| Montag | 07:30 | 18:00 |
| Dienstag | 07:30 | 18:00 |
| Mittwoch | 07:30 | 18:00 |
| Donnerstag | 07:30 | 14:00 |
| Freitag | 07:30 | 16:00 |

Änderungen dieser Zeiten dürfen nur durch berechtigte Personen (ADMIN) erfolgen und müssen protokolliert werden. Das System unterstützt sowohl globale Regelzeiten (`GLOBAL`) als auch mitarbeiterbezogene (`EMPLOYEE`), gespeichert in der Tabelle `work_schedule_versions`.

### Regel bei vergessenem Ausloggen

Bleibt `Kommen` ohne `Gehen` (laut `regelwerk_arbeitszeit_v5.md`, Abschnitt 14):

1. Zustand bleibt `OPEN`
2. Nach Regelende wird gewarnt
3. Prüfstatus mindestens `OPEN` oder `NEEDS_REVIEW`
4. Klärung erfolgt administrativ
5. Korrektur oder Nachtrag wird begründet dokumentiert

**Eine automatische endgültige `Gehen`-Buchung ist ausdrücklich nicht zulässig.**

### Regel bei vergessener Pause

Analog: offener Status, Warnung, Prüfbedarf, dokumentierte Klärung. Keine automatische Schließung.

**Quelle:** `regelwerk_arbeitszeit_v5.md`, Abschnitte 14 und 15

### ArbZG-Prüfhilfen

Das System erzeugt Prüfhinweise für (laut `regelwerk_arbeitszeit_v5.md`, Abschnitt 10):

| Sachverhalt | Rechtsgrundlage |
|---|---|
| Mehr als 6 Stunden ohne Pause → Warnung | ArbZG §4 |
| Mehr als 9 Stunden ohne ausreichende Pause → Warnung | ArbZG §4 |
| Mehr als 8 Stunden tägliche Arbeitszeit → Warnung | ArbZG §3 |
| Mehr als 10 Stunden tägliche Arbeitszeit → Eskalation | ArbZG §3 |
| Weniger als 11 Stunden Ruhezeit → Warnung | ArbZG §5 |

> ⚠️ Diese Prüfhilfen sind **fachliche Indikatoren**, keine automatische Rechtsprüfung. Sie ersetzen keine juristische Einzelfallbewertung.

---

## 6. Datenbank

### Überblick

Das System verwendet **SQLite** als einzige Datenquelle. Alle Tabellen, Beziehungen und Constraints sind in `migrations/0001_schema.sql` definiert.

### Tabellen im Überblick

| Tabelle | Zweck |
|---|---|
| `schema_migrations` | Versionierung der eingespielten Migrationen |
| `employees` | Mitarbeiterstammdaten |
| `user_accounts` | Benutzerkonten (ADMIN, REVIEWER, TECH, EMPLOYEE) |
| `rfid_cards` | RFID-Karten, Status und Mitarbeiterzuordnung |
| `terminals` | Terminalgeräte |
| `time_bookings` | Alle Zeitbuchungen |
| `booking_status_history` | Statusverlauf jeder Buchung |
| `booking_corrections` | Korrekturen mit altem/neuem Zustand |
| `supplements` | Nachträge (Notfall-/Nacherfassungen) |
| `review_cases` | Prüffälle (offene, auffällige, mögliche Verstöße) |
| `review_case_actions` | Aktionsprotokoll zu Prüffällen |
| `work_schedule_versions` | Regelarbeitszeiten (versioniert) |
| `system_config` | Systemkonfiguration (Backup-Dir, Export-Dir etc.) |
| `device_events` | Hardware-Ereignisse (Scans, Ablehnungen) |
| `system_events` | Systemereignisse (Selbsttest, Backup, NAS, Zeitsprünge) |
| `audit_log` | Revisionssicheres Protokoll aller fachlichen Vorgänge |

**Quelle:** `migrations/0001_schema.sql`

### Wichtige Tabellen im Detail

#### `employees` – Mitarbeiterstammdaten

| Spalte | Typ | Bedeutung |
|---|---|---|
| `id` | INTEGER PK | Interne ID |
| `personnel_no` | TEXT UNIQUE | Personalnummer (z. B. `M001`) |
| `first_name` | TEXT | Vorname |
| `last_name` | TEXT | Nachname |
| `active` | INTEGER (0/1) | Aktiv/Inaktiv |
| `employment_start` | TEXT (ISO-Datum) | Beschäftigungsbeginn |
| `employment_end` | TEXT (ISO-Datum) | Beschäftigungsende |
| `created_at` | TEXT | Erstellungszeitpunkt |
| `updated_at` | TEXT | Letzte Änderung |

#### `user_accounts` – Benutzerkonten

| Spalte | Typ | Bedeutung |
|---|---|---|
| `id` | INTEGER PK | Interne ID |
| `username` | TEXT UNIQUE | Benutzername |
| `password_hash` | TEXT | Passwort-Hash (kein Klartext) |
| `role` | TEXT | `EMPLOYEE`, `ADMIN`, `REVIEWER`, `TECH` |
| `employee_id` | INTEGER FK | Optionale Verknüpfung zu `employees` |
| `active` | INTEGER (0/1) | Aktiv/Inaktiv |
| `created_at` | TEXT | Erstellungszeitpunkt |
| `updated_at` | TEXT | Letzte Änderung |

#### `rfid_cards` – RFID-Karten

| Spalte | Typ | Bedeutung |
|---|---|---|
| `id` | INTEGER PK | Interne ID |
| `uid_hash` | TEXT UNIQUE | SHA-256-Hash der Karten-UID |
| `employee_id` | INTEGER FK | Zugehöriger Mitarbeiter |
| `status` | TEXT | `ACTIVE`, `INACTIVE`, `REPLACED`, `LOST` |
| `valid_from` | TEXT (ISO-Datum) | Gültig ab |
| `valid_until` | TEXT (ISO-Datum, nullable) | Gültig bis |
| `replaced_by_card_id` | INTEGER FK | Nachfolgekarte |

#### `time_bookings` – Zeitbuchungen

| Spalte | Typ | Bedeutung |
|---|---|---|
| `id` | INTEGER PK | Interne ID |
| `employee_id` | INTEGER FK | Mitarbeiter |
| `rfid_card_id` | INTEGER FK | Verwendete Karte |
| `booking_type` | TEXT | `COME`, `GO`, `BREAK_START`, `BREAK_END` |
| `booked_at` | TEXT (ISO-Datetime) | Buchungszeitpunkt |
| `source` | TEXT | `TERMINAL`, `MANUAL`, `IMPORT` |
| `terminal_id` | INTEGER FK | Terminal (nullable) |
| `current_status` | TEXT | Aktueller Buchungsstatus |
| `note` | TEXT (nullable) | Freitextnotiz |
| `created_at` | TEXT | Datensatz angelegt |

#### `audit_log` – Revisionssicheres Protokoll

| Spalte | Typ | Bedeutung |
|---|---|---|
| `id` | INTEGER PK | Interne ID |
| `event_type` | TEXT | Ereignistyp (aus `audit_events.py`) |
| `object_type` | TEXT | Betroffene Tabelle/Objekt (snake_case) |
| `object_id` | INTEGER | ID des betroffenen Datensatzes |
| `user_id` | INTEGER FK (nullable) | Ausführende Benutzer-ID |
| `employee_id` | INTEGER FK (nullable) | Betroffener Mitarbeiter |
| `event_at` | TEXT (ISO-Datetime) | Zeitpunkt des Ereignisses |
| `details_json` | TEXT | Detaildaten als JSON |

### Audit-Log – Ereigniskatalog

Der Katalog aller protokollierten Ereignisse ist in `src/arbeitszeit/domain/audit_events.py` zentralisiert (keine freien String-Literale, um Tippfehler zur Compile-Zeit zu fangen):

| Ereignis | Bedeutung |
|---|---|
| `TIME_BOOKED` | Buchung erfasst |
| `BOOKING_REJECTED_UNKNOWN_CARD` | Buchung wegen unbekannter Karte abgelehnt |
| `BOOKING_REJECTED_INACTIVE_CARD` | Buchung wegen inaktiver Karte abgelehnt |
| `BOOKING_CORRECTED` | Buchung korrigiert |
| `SUPPLEMENT_CREATED` | Nachtrag erstellt |
| `SUPPLEMENT_APPROVED` | Nachtrag genehmigt |
| `SUPPLEMENT_REJECTED` | Nachtrag abgelehnt |
| `WORK_SCHEDULE_CHANGED` | Regelarbeitszeit geändert |
| `USER_ACCOUNT_CREATED` | Benutzerkonto angelegt |
| `USER_ACCOUNT_DEACTIVATED` | Benutzerkonto deaktiviert |
| `USER_ACCOUNT_REACTIVATED` | Benutzerkonto reaktiviert |
| `USER_ACCOUNT_ROLE_CHANGED` | Rolle geändert |
| `BACKUP_CREATED` | Backup erstellt |
| `BACKUP_SYNCED_TO_NAS` | Backup auf NAS synchronisiert |
| `BACKUP_SYNC_FAILED` | NAS-Synchronisation fehlgeschlagen |
| `RESTORE_COMPLETED` | Restore abgeschlossen |

**Quelle:** `src/arbeitszeit/domain/audit_events.py`

### Migrations-Konzept

Migrationen sind **nummerierte SQL-Dateien** im Verzeichnis `migrations/`. Sie werden genau einmal und in aufsteigender Reihenfolge eingespielt. Die Tabelle `schema_migrations` speichert, welche Migrationen bereits angewendet wurden.

| Migration | Inhalt |
|---|---|
| `0001_schema.sql` | Vollständiges Datenbankschema (alle Tabellen, Indizes, Constraints) |
| `0002_seed_defaults.sql` | Standarddaten (Regelarbeitszeiten, initiale Konfiguration) |
| `0003_cleanup_booking_status.sql` | Bereinigung von Buchungsstatus-Werten |
| `0004_supplement_reject_fields_and_review_note.sql` | Ablehnungsfelder für Nachträge, Notizfeld für Prüffälle |
| `0005_time_bookings_device_event_id.sql` | Geräteereignis-Verknüpfung in Buchungen |
| `0006_system_events_application_error.sql` | Fehlertyp für Anwendungsfehler in Systemereignissen |

`scripts/init_db.py` führt die Migrationen beim Start aus. Bereits eingespielten Migrationen werden übersprungen.

**Quelle:** `migrations/`-Verzeichnis, `installationsanleitung_arbeitszeit.md` Abschnitt 8

---

## 7. Hardware-Anbindung

### RFID-Reader

Der RFID-Reader arbeitet als **USB-HID-Gerät** (verhält sich gegenüber dem Betriebssystem wie eine Tastatur). Er übermittelt die Karten-UID als Folge von Hex-Zeichen (`0–9`, `A–F`), abgeschlossen durch `Enter`.

**Verarbeitungsablauf:**
1. Reader sendet Hex-Zeichen als Tastencodes
2. `evdev_reader.py` filtert nur gültige Hex-Zeichen (Nicht-Hex wird ignoriert)
3. Bei `Enter` ist die UID vollständig
4. `uid_hash.py` berechnet `SHA256(raw_uid)` – dieser Hash wird in der Datenbank gespeichert, nicht die Roh-UID

**Timeout:** Nach Buchungstyp-Auswahl hat der Mitarbeiter **5 Sekunden** Zeit, den RFID-Chip zu halten. Bei Überschreitung wird `HardwareTimeoutError` ausgelöst.

**Gerätepfad ermitteln:**
```bash
ls /dev/input/by-id/
# oder
sudo evtest
```

**Quelle:** `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`, `src/arbeitszeit/infrastructure/hardware/uid_hash.py`

### USB-Numpad – Tastenbelegung

| Taste | Booking-Type | Bedeutung |
|:---:|---|---|
| `1` / `KP1` | `COME` | Kommen |
| `2` / `KP2` | `GO` | Gehen |
| `3` / `KP3` | `BREAK_START` | Pause Start |
| `4` / `KP4` | `BREAK_END` | Pause Ende |

Sowohl KP-Variante (Numpad-Taste) als auch normale Zifferntasten werden unterstützt. Alle anderen Tasten werden ignoriert.

Das Numpad blockiert unbegrenzt auf eine Buchungsauswahl – das ist beabsichtigt (Idle-Wartemodus).

**Quelle:** `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`, `_NUMPAD_TO_BOOKING_TYPE`-Dictionary

### Gerätezugriff (Berechtigungen)

Der Prozess benötigt **Lesezugriff** auf die Gerätedateien. Empfohlene Methoden:
- Benutzer der Gruppe `input` hinzufügen: `sudo usermod -aG input <benutzername>`
- Oder: udev-Regel anlegen

Das System öffnet die Geräte standardmäßig **exklusiv** (`grab=True`), d. h. keine anderen Prozesse können die Eingaben parallel empfangen (Kiosk-Betrieb).

**Quelle:** `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`

### Hardware-Simulator für Tests

Für Tests ohne physische Hardware existiert `src/arbeitszeit/infrastructure/hardware/simulator.py`. Er implementiert dieselbe `HardwareReader`-Schnittstelle (`ports.py`) und kann im Testbetrieb anstelle des echten Readers verwendet werden.

### Verhalten bei Hardware-Ausfall

Laut `pflichtenheft_arbeitszeit_v5.md` Abschnitt 13 und `regelwerk_arbeitszeit_v5.md` Abschnitt 19:

- Bei Reader-, Terminal- oder Stromausfall gilt ein **Notfallprozess**
- Manuelle Noterfassung auf Papier
- Später als **gekennzeichneter Nachtrag** (`BookingSource.MANUAL`) in das System eingeben
- Jeder Nachtrag ist **begründungspflichtig**
- Freigabe durch berechtigte Person (ADMIN oder REVIEWER) erforderlich

Die `system_events`-Tabelle protokolliert `DEVICE_UNAVAILABLE` und `DEVICE_RECOVERED`-Ereignisse.

---

## 8. Benutzeroberfläche / Bedienung

### System starten

**Terminal-UI (operativer Buchungsbetrieb):**
```bash
source .venv/bin/activate
python -m arbeitszeit.presentation.terminal_ui.main \
    --db arbeitszeit.db \
    --numpad /dev/input/eventX \
    --rfid /dev/input/eventY \
    --terminal-id 1
```

Die Terminal-UI läuft als **Endlosschleife** und führt beim Start automatisch einen Systemcheck durch. Sie beendet sich sauber bei `Strg+C` oder `SIGTERM`.

**Admin-CLI:**
```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    <unterbefehl>
```

**Quelle:** `installationsanleitung_arbeitszeit.md`, Abschnitt 14; `README.md`

### Typischer Tagesablauf (Mitarbeiter)

```
Morgens – Arbeitsbeginn:
1. Taste [1] am Numpad drücken  →  „Kommen" gewählt
2. RFID-Chip an Reader halten  →  Buchung wird gespeichert

Mittags – Pause beginnt:
1. Taste [3] am Numpad drücken  →  „Pause Start" gewählt
2. RFID-Chip an Reader halten  →  Buchung wird gespeichert

Nach der Pause – Weiterarbeit:
1. Taste [4] am Numpad drücken  →  „Pause Ende" gewählt
2. RFID-Chip an Reader halten  →  Buchung wird gespeichert

Abends – Arbeitsende:
1. Taste [2] am Numpad drücken  →  „Gehen" gewählt
2. RFID-Chip an Reader halten  →  Buchung wird gespeichert
```

**Wichtig:** Zuerst Taste drücken, dann Chip halten – nicht umgekehrt!

### Kurzreferenz Admin-CLI-Befehle

| Befehl | Zweck |
|---|---|
| `users bootstrap --username <name>` | Ersten Administrator anlegen |
| `users add --username <n> --role <r>` | Weiteren Benutzer anlegen |
| `users list` | Alle Benutzerkonten anzeigen |
| `employees add --personnel-no <p> --first-name <v> --last-name <n>` | Mitarbeiter anlegen |
| `employees list` | Alle Mitarbeiter anzeigen |
| `cards assign --employee-id <id> --uid-hash <hash>` | RFID-Karte zuweisen |
| `system check` | Systemcheck ausführen |
| `<befehl> --help` | Hilfe zu einem Unterbefehl |

> Vollständige Unterbefehle für `bookings`, `reports`, `schedule`, `users` sind in `src/arbeitszeit/presentation/admin_cli/` implementiert. Die genaue Syntax aller Unterbefehle ist mit `--help` abrufbar.

### Nachträge – Schritt-für-Schritt-Anleitung

Ein Nachtrag ist eine **nachträglich erfasste Buchung** (z. B. weil der Mitarbeiter vergessen hat zu buchen oder weil die Hardware ausgefallen war).

1. Admin-CLI starten
2. Nachtrag mit Buchungsart, Zeitpunkt und Begründung erfassen (Unterbefehl für Nachträge in `admin_cli/`)
3. Nachtrag wird mit `BookingSource.MANUAL` und `ApprovalStatus.PENDING` gespeichert
4. REVIEWER oder ADMIN prüft und genehmigt (`APPROVED`) oder lehnt ab (`REJECTED`)
5. Bei Genehmigung wird die Buchung als Nachtrag gekennzeichnet in der Datenbank übernommen
6. Audit-Log-Einträge `SUPPLEMENT_CREATED`, `SUPPLEMENT_APPROVED`/`SUPPLEMENT_REJECTED` werden automatisch angelegt

**Quelle:** `src/arbeitszeit/application/use_cases/register_supplement.py`, `approve_supplement.py`, `reject_supplement.py`, `regelwerk_arbeitszeit_v5.md` Abschnitt 13

### Korrekturen – Schritt-für-Schritt-Anleitung

Eine Korrektur ändert eine **bereits vorhandene Buchung** (z. B. falsche Uhrzeit, falscher Typ):

1. Admin-CLI starten
2. Korrektur-Befehl mit Buchungs-ID, neuem Wert und Begründung ausführen
3. Das System speichert in `booking_corrections`: alte Werte, neue Werte, Begründung, korrigierende Person, Zeitstempel
4. Die Originalbuchung erhält den Status `CORRECTED`
5. Audit-Log-Eintrag `BOOKING_CORRECTED` wird angelegt
6. Korrekturen sind in Pflichtauswertungen mit altem/neuem Zustand, Begründung, Person und Zeitstempel nachvollziehbar

**Physische Löschung von Buchungen ist nicht zulässig.** Stattdessen werden Status- und Korrekturmechanismen verwendet.

**Quelle:** `src/arbeitszeit/application/use_cases/correct_booking.py`, `regelwerk_arbeitszeit_v5.md` Abschnitt 12

### Rollen und was sie dürfen

| Aktion | ADMIN | REVIEWER | TECH | EMPLOYEE |
|---|:---:|:---:|:---:|:---:|
| Buchung am Terminal | – | – | – | ✓ |
| Benutzerkonten verwalten | ✓ | – | – | – |
| Mitarbeiterstammdaten verwalten | ✓ | – | – | – |
| RFID-Karten zuweisen | ✓ | – | – | – |
| Regelarbeitszeiten ändern | ✓ | – | – | – |
| Korrekturen durchführen | ✓ | ✓ | – | – |
| Nachträge freigeben/ablehnen | ✓ | ✓ | – | – |
| Prüffälle bearbeiten | ✓ | ✓ | – | – |
| Systemcheck | ✓ | – | ✓ | – |
| Backup/Restore | ✓ | – | ✓ | – |

**Quelle:** `regelwerk_arbeitszeit_v5.md`, Abschnitte 16 und 16a

---

## 9. Backup und Datensicherung

### Manuelles Backup anstoßen

```bash
python scripts/backup.py --db arbeitszeit.db --backup-dir /var/backups/arbeitszeit
```

Berechtigt für Backup und Restore sind ausschließlich Benutzer mit Rolle `ADMIN` oder `TECH`.

**Quelle:** `scripts/backup.py` (Existenz belegt), `regelwerk_arbeitszeit_v5.md` Abschnitt 20

### Backup-Verzeichnis

Das Backup-Verzeichnis wird während der Ersteinrichtung (`scripts/setup.py`) in der Tabelle `system_config` unter dem Schlüssel `backup.backup_dir` gespeichert.

### Audit-Log-Ereignisse für Backup

Das System protokolliert Backup-Vorgänge im Audit-Log (`src/arbeitszeit/domain/audit_events.py`):

- `BACKUP_CREATED` – lokales Backup erstellt
- `BACKUP_SYNCED_TO_NAS` – auf NAS synchronisiert
- `BACKUP_SYNC_FAILED` – NAS-Synchronisation fehlgeschlagen
- `RESTORE_COMPLETED` – Restore abgeschlossen

Die `system_events`-Tabelle enthält zusätzlich `DB_BACKUP_CREATED`, `DB_BACKUP_FAILED`, `RESTORE_STARTED`, `RESTORE_FINISHED`, `RESTORE_FAILED`, `NAS_REACHABLE`, `NAS_UNREACHABLE`.

### NAS-Backup-Konzept

Das Pflichtenheft (`pflichtenheft_arbeitszeit_v5.md`, Abschnitt 14) fordert NAS-Backups und definiert sie als Anforderung. Die Infrastrukturkomponente `src/arbeitszeit/infrastructure/backup/` ist vorhanden. Eine NAS-spezifische Konfigurationsoberfläche ist aus dem vorliegenden Quellcode-Stand nicht eindeutig ableitbar – bitte direkt im Backup-Modul prüfen.

### Restore

- Restore darf nur berechtigt durchgeführt werden (ADMIN oder TECH)
- Restore muss protokolliert werden (`RESTORE_COMPLETED` im Audit-Log)
- Restore muss regelmäßig testweise geprüft werden (laut `regelwerk_arbeitszeit_v5.md`, Abschnitt 20)

### Aufbewahrungsfristen

Arbeitszeitdaten müssen **mindestens 2 Jahre** aufbewahrt werden (ArbZG §16). Fachlich relevante Buchungen werden nicht physisch gelöscht, sondern über Status und Korrekturmechanismen behandelt.

**Quelle:** `regelwerk_arbeitszeit_v5.md` Abschnitt 18, `pflichtenheft_arbeitszeit_v5.md` Abschnitt 12

---

## 10. Tests

### Teststruktur

Das `tests/`-Verzeichnis ist vorhanden. Explizit belegt ist `tests/test_migrations.py`. Die `README.md` und `installationsanleitung_arbeitszeit.md` beschreiben die Teststruktur als gegliedert in:

- Unit-Tests (Domain, Application)
- Integrationstests
- End-to-End-Tests
- Migrationstests

Die genaue Dateistruktur unterhalb von `tests/` wurde im vorliegenden Abruf nicht vollständig aufgelistet. Für eine vollständige Übersicht: `ls tests/` im Projektverzeichnis.

### Tests ausführen

```bash
# Gesamte Testsuite
pytest

# Nur Migrationstests (besonders relevant nach Datenbankinitialisierung)
pytest tests/test_migrations.py

# Mit Coverage-Bericht
pytest --cov=arbeitszeit
```

**Quelle:** `pyproject.toml` (`[tool.pytest.ini_options]`), `installationsanleitung_arbeitszeit.md` Abschnitt 13

### pytest-Konfiguration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

Tests laufen über das `tests/`-Verzeichnis.

### Was laut Pflichtenheft getestet werden muss

`pflichtenheft_arbeitszeit_v5.md`, Abschnitt 16, definiert Pflichtszenarien:

- Mehr als 6 Stunden ohne Pause
- Mehr als 9 Stunden ohne ausreichende Pause
- Arbeitszeit über 8 Stunden / über 10 Stunden
- Unterschreitung der Ruhezeit
- Systemzeitabweichung
- Notfallnachtrag
- Restore-Test mit echtem Backup
- Bootstrap-Prozess (erster Administrator)
- Anlegen von REVIEWER- und TECH-Konten
- Zurückweisung ungültiger Rollenwerte und doppelter Benutzernamen
- Deaktivierung/Reaktivierung von Benutzerkonten
- Rollenwechsel
- Zugriffsschutz: Nicht-Admins dürfen keine Benutzerkonten ändern
- Protokollnachweis im Audit-Log

### Statische Code-Analyse

```bash
ruff check src/
```

`ruff` ist als Dev-Abhängigkeit in `pyproject.toml` konfiguriert.

---

## 11. Entwickler-Informationen

### Git-Workflow

Das Projekt verwendet Git für Versionierung. Repository: https://github.com/iCodator/arbeitszeit

Empfohlener Entwicklungsworkflow:
```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Architekturkonventionen

Das Projekt folgt strikten Schichtenregeln (`README.md`, Abschnitt „Entwicklungshinweise"):

- **Neue Funktionen** müssen der Schichtenaufteilung folgen
- Keine direkten Abhängigkeiten zwischen CLI, Hardware und Datenzugriff
- `domain/` darf nichts aus `infrastructure/` oder `presentation/` importieren
- Alle Audit-Ereignis-Typen sind zentral in `src/arbeitszeit/domain/audit_events.py` zu definieren – keine freien String-Literale
- Enum-Werte werden als `StrEnum` definiert (Python 3.11+)

### Datenbankentwicklung

- Neue Schemaänderungen als neue nummerierte SQL-Datei in `migrations/`
- Bestehende Migrationsdateien dürfen **nicht geändert** werden
- Jede Migration wird genau einmal eingespielt und in `schema_migrations` protokolliert

### Testen neuer Funktionen

- Hardwareabhängige Komponenten: `SimulatedHardwareReader` aus `src/arbeitszeit/infrastructure/hardware/simulator.py` verwenden
- Domain-Logik: direkt ohne Datenbankanbindung testbar
- Use Cases: über Abstraktion `unit_of_work.py` testbar

### Wichtige Einstiegspunkte

| Datei | Relevanz |
|---|---|
| `src/arbeitszeit/presentation/terminal_ui/main.py` | Operativer Buchungsbetrieb |
| `src/arbeitszeit/presentation/admin_cli/main.py` | Administration |
| `src/arbeitszeit/infrastructure/system_check.py` | Systemprüfung (wird beim Start der Terminal-UI aufgerufen) |
| `src/arbeitszeit/infrastructure/time_monitor.py` | Zeitüberwachung (Zeitsprünge, NTP-Abweichungen) |
| `src/arbeitszeit/domain/entities.py` | Alle Fachentitäten |
| `src/arbeitszeit/domain/enums.py` | Alle Aufzählungstypen |
| `src/arbeitszeit/domain/audit_events.py` | Zentraler Audit-Ereigniskatalog |

**Quelle:** `README.md`, `src/`-Verzeichnisstruktur

---

## 12. Rechtliche Hinweise

### Pflicht zur Arbeitszeiterfassung

Das System unterstützt die gesetzliche Pflicht zur Arbeitszeiterfassung gemäß:
- **BAG-Beschluss vom 13.09.2022 – 1 ABR 22/21**: Pflicht zur Einführung eines objektiven, verlässlichen und zugänglichen Systems zur Aufzeichnung der Arbeitszeit
- **EuGH-Urteil vom 14.05.2019 – C-55/18**: Grundlage für die europäische Anforderung

### Arbeitszeitgesetz (ArbZG)

| Paragraph | Inhalt | Systemprüfung |
|---|---|---|
| §3 | Werktägliche Arbeitszeit max. 8 Stunden, verlängerbar auf 10 Stunden | `POSSIBLE_MAX_HOURS_VIOLATION` |
| §4 | Ruhepausenregelung: ≥30 Min. bei >6h, ≥45 Min. bei >9h | `POSSIBLE_BREAK_VIOLATION` |
| §5 | Mindestruhezeit 11 Stunden zwischen Arbeitstagen | `POSSIBLE_REST_VIOLATION` |
| §16 | Aufzeichnungspflicht, mindestens 2 Jahre Aufbewahrung | Buchungsdaten in SQLite |

**Quelle:** `pflichtenheft_arbeitszeit_v5.md`, Abschnitt 4 und Fußnoten [^2]–[^4][^8]

### Datenschutz / DSGVO

Das System verarbeitet Beschäftigtendaten und muss deshalb organisatorisch und technisch geschützt werden:

| Rechtsgrundlage | Anforderung an das System |
|---|---|
| DSGVO Art. 5 | Datensparsamkeit: nur erforderliche Daten verarbeiten |
| DSGVO Art. 32 | Sicherheit der Verarbeitung (Zugriffsschutz, Verschlüsselung empfohlen) |
| BDSG §26 | Datenverarbeitung für Zwecke des Beschäftigungsverhältnisses |

Umgesetzte Schutzmaßnahmen laut `pflichtenheft_arbeitszeit_v5.md`, Abschnitt 11:
- Rollen- und Rechtekonzept (technisch erzwungen, nicht nur organisatorisch)
- Schutz der Datenbankdatei durch Dateisystemrechte
- Schutz der Exportverzeichnisse
- Schutz der NAS-Backups
- Restriktiver Zugriff auf Admin-Befehle

**Quelle:** `pflichtenheft_arbeitszeit_v5.md`, Abschnitt 11, Fußnoten [^5]–[^7]

### Aufbewahrung und Löschung

- Arbeitszeitdaten: **mindestens 2 Jahre** aufbewahren (ArbZG §16)
- Keine physische Löschung fachlich relevanter Buchungen im Normalbetrieb
- Stattdessen: Status- und Korrekturmechanismen
- Schriftlich festzulegendes Archivierungs- und Löschkonzept erforderlich

---

## 13. Vollständigkeitsprüfung

### Was sicher aus dem Repo belegt werden konnte

| Aussage | Quelle |
|---|---|
| Python-Versionsanforderung `>=3.14,<3.15` | `pyproject.toml` |
| Vier Buchungsarten: COME, GO, BREAK_START, BREAK_END | `src/arbeitszeit/domain/enums.py` |
| Vollständiges Datenbankschema (16 Tabellen) | `migrations/0001_schema.sql` |
| 6 Migrationsdateien vorhanden | `migrations/`-Verzeichnis |
| Hardware-Anbindung über evdev, 5s RFID-Timeout | `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` |
| SHA-256-Hashing der RFID-UIDs | `src/arbeitszeit/infrastructure/hardware/uid_hash.py` |
| Hardware-Simulator für Tests | `src/arbeitszeit/infrastructure/hardware/simulator.py` |
| 6 Use-Case-Dateien | `src/arbeitszeit/application/use_cases/` |
| Audit-Log-Ereigniskatalog (18 Ereignisse) | `src/arbeitszeit/domain/audit_events.py` |
| Alle Entitäten (Employee, UserAccount, RfidCard, TimeBooking, WorkScheduleVersion, ReviewCase, Supplement, BookingCorrection, AuditLogEntry) | `src/arbeitszeit/domain/entities.py` |
| Alle Enums (BookingType, BookingStatus, ReviewCaseType, ReviewCaseStatus, ReviewSeverity, CardStatus, UserRole, BookingSource, ChangeOrigin, ApprovalStatus, ScopeType) | `src/arbeitszeit/domain/enums.py` |
| Bootstrap-Prozess für ersten Admin | `installationsanleitung_arbeitszeit.md` |
| Standard-Regelarbeitszeiten (Mo–Fr) | `pflichtenheft_arbeitszeit_v5.md`, `regelwerk_arbeitszeit_v5.md` |
| ArbZG-Prüfschwellen | `regelwerk_arbeitszeit_v5.md` |
| Installationsschritte vollständig | `installationsanleitung_arbeitszeit.md` v2.0 |
| `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py` vorhanden | Verzeichnislisting `scripts/` |

### Was nicht eindeutig belegt werden konnte

| Aussage | Begründung |
|---|---|
| Vollständige Unterbefehls-Syntax der Admin-CLI | `src/arbeitszeit/presentation/admin_cli/`-Dateien wurden nicht im Detail gelesen; Struktur und Einstiegspunkt bekannt, vollständige Befehlsliste aber nicht belegt |
| Vollständige interne Teststruktur (`tests/`) | Nur `tests/test_migrations.py` explizit bestätigt; weitere Testdateien wurden nicht aufgelistet |
| Konkrete NAS-Konfiguration im Backup-Modul | `src/arbeitszeit/infrastructure/backup/` als Verzeichnis bekannt, Inhalt nicht gelesen |
| Vollständiger Inhalt von `docs/` | Verzeichnis bekannt, Dateien nicht gelistet |
| Konkrete Implementierung von `system_check.py` und `time_monitor.py` | Dateien bekannt (7 KB / 3 KB), Inhalt nicht gelesen |
| Vollständige Implementierung der Export-Funktionen | `src/arbeitszeit/infrastructure/export/` als Verzeichnis bekannt, Dateien nicht gelesen |
| Exaktes Protokoll von `scripts/backup.py` | Existenz und Aufruf bekannt, Code nicht gelesen |
| Rechtliche Vollständigkeit im Produktivbetrieb | Vom README selbst als „nicht eindeutig belegbar" eingestuft |

### Teile des Repos, die nicht gelesen werden konnten

Aufgrund des Abfragelimits wurden folgende Dateien/Verzeichnisse **nicht** im Detail gelesen:

- `src/arbeitszeit/presentation/admin_cli/` (alle Untermodule)
- `src/arbeitszeit/presentation/terminal_ui/` (alle Untermodule außer Haupteinstiegspunkt)
- `src/arbeitszeit/infrastructure/db/` (Repositories, Unit-of-Work-Implementierung)
- `src/arbeitszeit/infrastructure/export/` (CSV- und PDF-Export)
- `src/arbeitszeit/infrastructure/backup/` (Backup-Logik)
- `src/arbeitszeit/domain/ports/` und `src/arbeitszeit/domain/services/`
- `src/arbeitszeit/application/commands.py`, `results.py`, `unit_of_work.py` (nur Existenz bekannt)
- `tests/` (vollständige Unterstruktur)
- `docs/` (vollständiger Inhalt)
- `migrations/0002` bis `0006` (nur Dateinamen bekannt, außer `0001_schema.sql`)
- `.claude/` (Inhalt unbekannt)

### Empfehlungen zur Vervollständigung der Dokumentation

1. **Admin-CLI vollständig dokumentieren:** Alle Unterbefehle mit vollständiger Parametersyntax erfassen. `python -m arbeitszeit.presentation.admin_cli.main --help` liefert die Ausgangsbasis.
2. **Testabdeckung dokumentieren:** Coverage-Bericht (`pytest --cov=arbeitszeit`) erstellen und als Baseline festhalten.
3. **NAS-Backup konkret beschreiben:** Konfigurationsparameter, Netzwerkvoraussetzungen und Verbindungsprüfung dokumentieren.
4. **RFID-Hash-Ermittlung für neue Karten:** Den Prozess zur erstmaligen Ermittlung des SHA-256-Hashes einer neuen RFID-Karte in der Installationsanleitung ergänzen.
5. **`docs/`-Inhalt sichten:** Das `docs/`-Verzeichnis enthält möglicherweise ergänzende Dokumentation, die in dieses Handbuch einfließen sollte.
6. **Betriebsprozesse festlegen:** Laut `pflichtenheft_arbeitszeit_v5.md` Abschnitt 15 muss die Praxis schriftlich festlegen, wer welche Rollen hat, wie oft offene Fälle geprüft werden und wie oft Backups getestet werden. Dieses Betriebskonzept ist noch zu erstellen.

---

*Handbuch erstellt auf Basis des Repository-Stands `iCodator/arbeitszeit` (Commit `530ee9ee`) · Juni 2026*
