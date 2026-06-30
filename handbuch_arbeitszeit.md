# Handbuch – Arbeitszeiterfassung `arbeitszeit`

**Version:** 1.2  
**Stand:** Juni 2026  
**Basis:** Repository `iCodator/arbeitszeit`  
**Änderungen gegenüber 1.1:** Fehlende Beispielaufrufe ergänzt (`employees deactivate`, `cards deactivate`, `cards replace`, `users change-role`, `users deactivate`, `users reactivate`); optionale Parameter `setup.py` dokumentiert; Umgebungsvariable `ADMIN_USER_ID` ergänzt; Projektstruktur vervollständigt; `scripts/verify_hardware.py`, `scripts/generate_audit_notes.py` und `run_audit.sh` aufgenommen.

> ⚠️ **Wichtiger Hinweis:** Dieses Handbuch wurde anhand des tatsächlich überprüften Repository-Inhalts bereinigt. Aussagen, die aus den gelesenen Dateien nicht sicher belegbar waren, wurden entfernt, abgeschwächt oder ausdrücklich als nicht vollständig verifiziert gekennzeichnet.

---

## 1. Projektübersicht

`arbeitszeit` ist ein lokal betriebenes Zeiterfassungssystem für eine Zahnarztpraxis. Die Anwendung verwendet SQLite als einzige Datenbank und enthält getrennte Bereiche für Fachlogik, Infrastruktur und Benutzeroberflächen.

Aus dem Repository eindeutig belegt sind ein Terminalmodus für den operativen Buchungsbetrieb sowie eine Admin-CLI für Verwaltungsaufgaben.

---

## 2. Systemvoraussetzungen

### Betriebssystem

Die Projektunterlagen und die Installationsdokumentation beziehen sich auf Linux Mint und Lubuntu.

### Python-Version

Die verbindliche Python-Anforderung steht in `pyproject.toml`:

```toml
requires-python = ">=3.14,<3.15"
```

Damit ist für die Installation Python 3.14 erforderlich.

**Prüfung der installierten Version:**

```bash
python3.14 --version
```

> ⚠️ `python3 --version` allein ist nicht ausreichend, wenn auf dem System eine andere Python-Hauptversion als 3.14 als Standard eingerichtet ist.

### Python-Abhängigkeiten

**Laufzeitabhängigkeiten:**

| Paket | Mindestversion | Zweck |
|---|---|---|
| `evdev` | `>=1.7` | Zugriff auf Linux-Eingabegeräte |
| `reportlab` | `>=4.0` | PDF-Erzeugung |

**Entwicklungsabhängigkeiten:**

| Paket | Mindestversion | Zweck |
|---|---|---|
| `pytest` | `>=8.0` | Testausführung |
| `pytest-cov` | `>=5.0` | Coverage |
| `pypdf` | `>=4.0` | PDF-Prüfung in Tests |
| `ruff` | `>=0.6` | Linting |
| `import-linter` | `>=2.0` | Architekturprüfung |

### Zusätzliche Systempakete

Für die Installation werden laut Installationsanleitung zusätzliche Systempakete benötigt:

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

### Hardware

Sicher belegt sind folgende Hardware-Komponenten im Projektkontext:

- RFID-Reader als USB-HID-Gerät
- USB-Numpad als Eingabegerät

Die Gerätedateien werden unter Linux über `/dev/input/event*` angesprochen.

> ⚠️ Aussagen zu spezifischer Zielhardware wie „Raspberry Pi" sind aus den hier überprüften Dateien nicht sicher belegbar und werden daher nicht als gesicherte Systemeigenschaft aufgeführt.

---

## 3. Installation

Der Installationsablauf basiert auf den vorhandenen Skripten `scripts/init_db.py` und `scripts/setup.py` sowie auf der Installationsdokumentation im Repository.

### Repository klonen

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
```

### Virtuelle Umgebung erstellen

Wenn Python 3.14 explizit installiert wurde, sollte die virtuelle Umgebung mit dieser Version erstellt werden:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

### Abhängigkeiten installieren

```bash
pip install -e .[dev]
```

### Datenbank initialisieren

```bash
python scripts/init_db.py
```

Der Datenbankpfad kann optional mit `--db` angegeben werden (Standard: `arbeitszeit.db`).

Das Skript führt Migrationen aus. Die Migrationsversionen werden aus den Dateinamen im Verzeichnis `migrations/` abgeleitet und daher vierstellig ausgegeben.

**Typische Ausgabe:**

```text
Migration 0001 angewendet.
Migration 0002 angewendet.
Migration 0003 angewendet.
Migration 0004 angewendet.
Migration 0005 angewendet.
Migration 0006 angewendet.
⚠  Ersteinrichtung noch erforderlich:
   python scripts/setup.py --db arbeitszeit.db
```

### Ersteinrichtung

Das Skript `scripts/setup.py` setzt deployment-spezifische Konfigurationswerte in `system_config`, insbesondere:

- `backup.backup_dir`
- `export.export_dir`

`scripts/setup.py` bricht ab, wenn die Datenbankdatei noch nicht existiert.

Die Reihenfolge ist zwingend:

1. `scripts/init_db.py`
2. `scripts/setup.py`

**Interaktiver Aufruf** (das Skript fragt fehlende Pfade ab):

```bash
python scripts/setup.py --db arbeitszeit.db
```

**Nicht-interaktiver Aufruf** (für automatisierte Deployments):

```bash
python scripts/setup.py \
    --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
    --export-dir /var/exports/arbeitszeit
```

Bereits konfigurierte Schlüssel werden beim erneuten Aufruf übersprungen (idempotent).

### Ersten ADMIN anlegen

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    users bootstrap \
    --username adminname
```

Wird kein Passwort angegeben, erzeugt das System ein Passwort und zeigt es einmalig an.

### Weitere Benutzerkonten anlegen

Die Admin-CLI erlaubt für reguläre Benutzerkonten nur diese Rollen:

- `ADMIN`
- `REVIEWER`
- `TECH`

**Minimalbeispiel** (Pflichtparameter):

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users add \
    --username pruefer01 \
    --role REVIEWER
```

`users add` unterstützt zusätzlich diese optionalen Parameter:

| Parameter | Bedeutung |
|---|---|
| `--employee-id <INT>` | Verknüpfter Mitarbeiter-Datensatz (optional) |
| `--password <TEXT>` | Passwort im Klartext; wird gehasht gespeichert. Wird dieser Parameter weggelassen, generiert das System ein Passwort und zeigt es einmalig an. |

### Mitarbeiter anlegen

Mitarbeiter werden nicht über `users add`, sondern über `employees add` angelegt:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    employees add \
    --personnel-no M001 \
    --first-name Maria \
    --last-name Mustermann
```

### Mitarbeiter deaktivieren

`employees deactivate` erwartet die Mitarbeiter-ID als **positionales Argument** (kein `--id`-Flag):

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    employees deactivate 3
```

### RFID-Karte zuweisen

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    cards assign \
    --employee-id 1 \
    --uid-hash <HASH>
```

> ⚠️ Die Admin-CLI erwartet bereits einen vorhandenen `--uid-hash`. Der genaue technische Workflow zur erstmaligen Ermittlung dieses Hashwerts ist aus den hier überprüften Dateien nicht vollständig belegbar und sollte nicht genauer behauptet werden, als es die Codebasis hergibt.

### RFID-Karte ersetzen

`cards replace` deaktiviert die alte Karte und legt eine neue aktive Karte für denselben Mitarbeiter an:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    cards replace \
    --old-card-id 2 \
    --uid-hash <NEUER_HASH>
```

| Parameter | Bedeutung |
|---|---|
| `--old-card-id <INT>` | Datenbank-ID der zu ersetzenden Karte (Pflicht) |
| `--uid-hash <TEXT>` | Hash-Wert der neuen Karte (Pflicht) |

### RFID-Karte deaktivieren

`cards deactivate` erwartet die Karten-ID als **positionales Argument** (kein `--id`-Flag):

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    cards deactivate 2
```

### Funktionstest

```bash
pytest
pytest tests/test_migrations.py
pytest --cov=arbeitszeit
```

---

## 4. Projektstruktur

Aus dem Repository klar belegt ist folgende Hauptstruktur:

```text
arbeitszeit/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── run_audit.sh
├── test_booking_loop.py
├── installationsanleitung_arbeitszeit.md
├── handbuch_arbeitszeit.md
├── migrations/
│   ├── 0001_schema.sql
│   ├── 0002_seed_defaults.sql
│   ├── 0003_cleanup_booking_status.sql
│   ├── 0004_supplement_reject_fields_and_review_note.sql
│   ├── 0005_time_bookings_device_event_id.sql
│   └── 0006_system_events_application_error.sql
├── scripts/
│   ├── backup.py
│   ├── generate_audit_notes.py
│   ├── init_db.py
│   ├── setup.py
│   ├── show_config.py
│   └── verify_hardware.py
├── docs/
├── src/
│   └── arbeitszeit/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── presentation/
│           ├── admin_cli/
│           └── terminal_ui/
└── tests/
```

### Schichten

In `pyproject.toml` ist außerdem eine Architekturprüfung mit `import-linter` hinterlegt. Daraus geht hervor, dass das Projekt diese Schichten trennt:

- `arbeitszeit.presentation`
- `arbeitszeit.infrastructure`
- `arbeitszeit.application`
- `arbeitszeit.domain`

Diese Struktur entspricht einer Clean-Architecture-orientierten Trennung.

---

## 5. Benutzeroberflächen

### Terminal-UI

Der Einstiegspunkt für den operativen Buchungsbetrieb ist:

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
    --db arbeitszeit.db \
    --numpad /dev/input/eventX \
    --rfid /dev/input/eventY \
    --terminal-id 1
```

Die Parameter `--db`, `--numpad`, `--rfid` und `--terminal-id` sind Pflichtparameter.

Die Terminal-UI führt beim Start einen Systemcheck aus und reagiert auf `SIGINT` und `SIGTERM` mit einem sauberen Beenden.

### Admin-CLI

Der Einstiegspunkt für die administrative Oberfläche ist:

```bash
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db <unterbefehl>
```

`--db` ist bei der Admin-CLI verpflichtend.

Für die meisten schreibenden Operationen ist zusätzlich `--user-id` erforderlich. Eine Ausnahme ist `users bootstrap`, da vor dem ersten Administratorkonto noch kein Admin existiert.

**Alternative zu `--user-id`:** Die Benutzer-ID kann statt als Kommandozeilenargument auch über die Umgebungsvariable `ADMIN_USER_ID` übergeben werden. Das ist nützlich für Shell-Skripte und automatisierte Abläufe:

```bash
export ADMIN_USER_ID=1
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    users list
```

`--user-id` hat Vorrang vor `ADMIN_USER_ID`, wenn beide gesetzt sind.

---

## 6. Rollenmodell

Aus der tatsächlich überprüften Admin-CLI ergibt sich folgendes belastbare Rollenbild:

| Rolle | In der Admin-CLI als Benutzerkonto anlegbar | Bemerkung |
|---|---|---|
| `ADMIN` | Ja | Vollzugriff für administrative Schreiboperationen |
| `REVIEWER` | Ja | Rolle vorhanden |
| `TECH` | Ja | Rolle vorhanden |
| `EMPLOYEE` | Nein, nicht über `users add` | Mitarbeiter werden separat über `employees` verwaltet |

> ⚠️ Aussagen darüber, welche Rolle fachlich exakt welche Use Cases ausführen darf, sollten nur dann detaillierter dokumentiert werden, wenn die betreffenden Befehle und ihre Zugriffsprüfungen vollständig gelesen wurden. Aus den hier gesicherten Dateien ist sicher belegt, dass schreibende Benutzerkonten- und Mitarbeiteroperationen ADMIN-Rechte verlangen.

---

## 7. Backup und Systembetrieb

### Backup-Skript

Das Repository enthält `scripts/backup.py`.

Der Aufruf unterstützt diese Parameter:

| Parameter | Bedeutung | Standard |
|---|---|---|
| `--db` | Pfad zur Datenbankdatei | `arbeitszeit.db` |
| `--backup-dir` | Zielverzeichnis für Backups | `backups/` |
| `--export-dir` | optionales Exportverzeichnis | keiner |

Beispiel:

```bash
python scripts/backup.py \
    --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
    --export-dir /var/exports/arbeitszeit
```

### NAS-Konfiguration

`scripts/backup.py` liest zusätzlich Konfigurationswerte aus `system_config`:

- `backup.nas_enabled`
- `backup.nas_path`

Daraus ist belegt, dass NAS-Synchronisation konfigurierbar vorgesehen ist.

> ⚠️ Eine vollständige Beschreibung des Restore-Prozesses oder einer eigenen Restore-CLI ist aus den hier überprüften Dateien nicht sicher belegbar und wird deshalb nicht weiter konkretisiert.

---

## 8. Hilfs- und Diagnoseskripte

### Hardware-Smoke-Test (`scripts/verify_hardware.py`)

Dieses Skript prüft USB-Numpad und RFID-Reader in drei Stufen: Gerätedatei-Zugriff, Numpad-Tastendruck und RFID-Karten-Scan. Es wird typischerweise einmalig bei Erstinbetriebnahme oder nach Hardware-Tausch aufgerufen, **bevor** der Terminal-UI-Dienst gestartet wird.

**Verfügbare Gerätedateien auflisten:**

```bash
python scripts/verify_hardware.py --list
```

**Vollständiger Test mit direkter Gerätangabe:**

```bash
python scripts/verify_hardware.py \
    --numpad /dev/input/event3 \
    --rfid /dev/input/event4
```

**Interaktive Geräteauswahl** (kein Argument — Skript fragt nach):

```bash
python scripts/verify_hardware.py
```

**Nur Gerätezugriff prüfen, ohne Tastendruck- und Karten-Test:**

```bash
python scripts/verify_hardware.py \
    --numpad /dev/input/event3 \
    --rfid /dev/input/event4 \
    --skip-interactive
```

Das Skript gibt im Erfolgsfall den ermittelten SHA-256-Hash der RFID-UID aus. Dieser Wert kann direkt als `--uid-hash` bei `cards assign` verwendet werden.

| Parameter | Bedeutung |
|---|---|
| `--numpad <PFAD>` | Gerätedatei des USB-Numpads |
| `--rfid <PFAD>` | Gerätedatei des RFID-Readers |
| `--list` | Nur verfügbare Eingabegeräte auflisten, dann beenden |
| `--skip-interactive` | Tastendruck- und Karten-Tests überspringen |

> ⚠️ `--numpad` und `--rfid` müssen entweder beide angegeben oder beide weggelassen werden. Wird nur einer der beiden gesetzt, bricht das Skript mit einem Fehler ab.

### Code-Audit (`run_audit.sh` und `scripts/generate_audit_notes.py`)

`run_audit.sh` führt alle Analyse-Tools aus (Ruff, Mypy, Radon, import-linter, Bandit, pytest+Coverage) und legt die Rohdaten in `docs/audits/reports/<DATUM>/` ab.

```bash
bash run_audit.sh
```

`scripts/generate_audit_notes.py` liest diese Rohdaten und erzeugt eine strukturierte Markdown-Zusammenfassung (`audit-notes-<DATUM>.md`):

```bash
python scripts/generate_audit_notes.py
```

Alternativ mit explizitem Report-Verzeichnis und Ausgabedatei:

```bash
python scripts/generate_audit_notes.py \
    --report-dir docs/audits/reports/2026-06-30 \
    --output docs/audits/audit-notes-2026-06-30.md
```

| Parameter | Bedeutung | Standard |
|---|---|---|
| `--report-dir <PFAD>` | Verzeichnis mit den Rohdaten von `run_audit.sh` | `docs/audits/reports` |
| `--output <PFAD>` | Ausgabedatei | `<report-dir>/audit-notes-<DATUM>.md` |

> ⚠️ `run_audit.sh` benötigt zusätzlich installierte Tools (`mypy`, `radon`, `bandit`), die nicht in `pyproject.toml` als Pflichtabhängigkeiten geführt sind.

---

## 9. Gelesene Admin-CLI-Befehle

Aus `src/arbeitszeit/presentation/admin_cli/main.py` sind folgende Befehlsgruppen eindeutig belegt:

- `employees`
- `cards`
- `bookings`
- `schedule`
- `reports`
- `system`
- `users`

Aus dem Dispatch in `main.py` sind unter anderem diese konkreten Befehle belegt:

- `employees list`
- `employees add`
- `employees deactivate`
- `cards assign`
- `cards replace`
- `cards deactivate`
- `bookings correct`
- `bookings supplement`
- `bookings approve-supplement`
- `bookings reject-supplement`
- `schedule set`
- `schedule show`
- `reports export-csv`
- `reports export-pdf-day`
- `reports export-pdf-week`
- `reports export-pdf-month`
- `reports export-pdf-employee`
- `reports open-bookings`
- `reports warn-cases`
- `reports corrections`
- `reports supplements`
- `reports open-review-cases`
- `system check`
- `system backup`
- `users add`
- `users list`
- `users deactivate`
- `users reactivate`
- `users change-role`
- `users bootstrap`

Diese Liste ist belastbar, weil sie direkt aus dem Dispatch der gelesenen `main.py` stammt.

### Beispielaufrufe für Benutzerkonten-Verwaltung

**Benutzerkonto deaktivieren:**

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users deactivate \
    --user-id 3
```

> ⚠️ Hier erscheint `--user-id` zweimal: das erste Mal (global, vor dem Unterbefehl) ist die ID des **aufrufenden** Admins; das zweite Mal (nach `users deactivate`) ist die ID des **Zielkontos**, das deaktiviert werden soll.

**Benutzerkonto reaktivieren:**

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users reactivate \
    --user-id 3
```

**Rolle eines Benutzerkontos ändern:**

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users change-role \
    --user-id 3 \
    --role REVIEWER
```

---

## 10. Datenbank und Migrationen

Sicher belegt ist das Vorhandensein dieser Migrationsdateien:

- `0001_schema.sql`
- `0002_seed_defaults.sql`
- `0003_cleanup_booking_status.sql`
- `0004_supplement_reject_fields_and_review_note.sql`
- `0005_time_bookings_device_event_id.sql`
- `0006_system_events_application_error.sql`

Die Migrationslogik in `src/arbeitszeit/infrastructure/db/migrations.py` verarbeitet Dateinamen im Muster `0001_*.sql` und speichert die vierstellige Versionsnummer in `schema_migrations`.

---

## 11. Was sicher belegt ist

Die folgenden Aussagen sind durch die tatsächlich gelesenen Dateien abgesichert:

- Python-Anforderung `>=3.14,<3.15`
- Paketabhängigkeiten aus `pyproject.toml`
- Trennung in `presentation`, `infrastructure`, `application`, `domain`
- Vorhandensein von `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py`
- Bootstrap des ersten Administratorkontos
- Zulässige Rollen für `users add`: `ADMIN`, `REVIEWER`, `TECH`
- Mitarbeiterverwaltung über `employees add`
- `employees deactivate` und `cards deactivate` erfordern **positionale** ID-Argumente
- `cards replace` erfordert `--old-card-id` und `--uid-hash`
- `users deactivate`, `users reactivate` und `users change-role` erfordern ein eigenes `--user-id` für das Zielkonto
- Kartenzuweisung über `cards assign --uid-hash`
- Terminal-UI mit Pflichtparametern `--db`, `--numpad`, `--rfid`, `--terminal-id`
- Admin-CLI mit verpflichtendem `--db`; Benutzer-ID alternativ über `ADMIN_USER_ID`
- `setup.py` unterstützt nicht-interaktiven Aufruf mit `--backup-dir` und `--export-dir`
- Vierstellige Migrationsversionen `0001` bis `0006`
- NAS-bezogene Konfigurationsschlüssel im Backup-Skript
- `scripts/verify_hardware.py` für Hardware-Smoke-Tests
- `run_audit.sh` + `scripts/generate_audit_notes.py` für Code-Audit

---

## 12. Was nicht überbehauptet werden sollte

Die folgenden Punkte sollten in einer technischen Dokumentation nur dann detailliert dargestellt werden, wenn ihre Implementierung vollständig gelesen und verifiziert wurde:

- genaue interne RFID-Hash-Bildung und zugehörige Dateipfade, sofern diese nicht direkt gelesen wurden
- konkrete Restore-Abläufe und Restore-Befehle
- konkrete `system_events`-Ereignistypen außerhalb der nachweislich gelesenen Stellen
- exakte Inhalte nicht gelesener Module oder Verzeichnisse
- Hardware-Aussagen zu Plattformen, die im gelesenen Code nicht ausdrücklich genannt sind

---

## 13. Empfehlungen

Für eine vollständige, dauerhaft belastbare Dokumentation sollten als nächstes diese Teile gezielt separat geprüft werden:

1. `migrations/0001_schema.sql` im Volltext für die exakte Datenbankdokumentation
2. `src/arbeitszeit/domain/enums.py` für belastbare Dokumentation der Enums
3. `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` für belastbare Hardwarebeschreibung
4. `scripts/show_config.py` nur dann dokumentieren, wenn seine Optionen und Ausgabeformate tatsächlich gelesen wurden
5. Admin-CLI-Unterdateien (`bookings.py`, `reports.py`, `schedule.py`, `system.py`) für vollständige Befehls- und Rollenbeschreibung

---

*Bereinigte und korrigierte Fassung des Handbuchs auf Basis des überprüften Repository-Stands `iCodator/arbeitszeit`*
