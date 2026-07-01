# Handbuch – Arbeitszeiterfassung `arbeitszeit`

**Version:** 2.0
**Stand:** Juli 2026
**Basis:** Zusammenführung der Kapitel-Module aus `docs/module/`

> Dieses Dokument ist die für Menschen lesbare Gesamtfassung des Handbuchs.
> Die einzelnen Kapitel werden als eigenständige, versionierte Quelldateien
> unter `docs/module/` gepflegt und hier zusammengeführt.

## Inhaltsverzeichnis

1. [Übersicht](#1-ubersicht)
2. [Installation](#2-installation)
3. [Presentation Layer](#3-presentation-layer)
4. [Application Layer](#4-application-layer)
5. [Domain Layer](#5-domain-layer)
6. [Infrastructure Layer](#6-infrastructure-layer)
7. [Audit und Prüfstatus](#7-audit-und-prufstatus)

---

<a name="1-ubersicht"></a>

## 1. Übersicht

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

### Zweck

`arbeitszeit` ist ein lokal betriebenes Zeiterfassungssystem für eine
Zahnarztpraxis. Die Anwendung verwendet SQLite als einzige Datenbank und trennt
Fachlogik, Infrastruktur und Benutzeroberflächen klar voneinander.

Aus dem Repository eindeutig belegt sind ein Terminalmodus für den operativen
Buchungsbetrieb sowie eine Admin-CLI für Verwaltungsaufgaben.

### Projektstruktur

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
├── scripts/
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

In `pyproject.toml` ist eine Architekturprüfung mit `import-linter`
hinterlegt. Daraus geht hervor, dass das Projekt diese Schichten trennt:

- `arbeitszeit.presentation`
- `arbeitszeit.infrastructure`
- `arbeitszeit.application`
- `arbeitszeit.domain`

Diese Struktur entspricht einer Clean-Architecture-orientierten Trennung.

---

<a name="2-installation"></a>

## 2. Installation

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

### Systemvoraussetzungen

#### Betriebssystem

Die Projektunterlagen und die Installationsdokumentation beziehen sich auf
Linux Mint und Lubuntu.

#### Python-Version

Die verbindliche Python-Anforderung steht in `pyproject.toml`:

```toml
requires-python = ">=3.14,<3.15"
```

Damit ist für die Installation Python 3.14 erforderlich.

Prüfung der installierten Version:

```bash
python3.14 --version
```

`python3 --version` allein ist nicht ausreichend, wenn auf dem System eine
andere Python-Hauptversion als 3.14 als Standard eingerichtet ist.

#### Python-Abhängigkeiten

Laufzeitabhängigkeiten:

| Paket | Mindestversion | Zweck |
| --- | --- | --- |
| `evdev` | `>=1.7` | Zugriff auf Linux-Eingabegeräte |
| `reportlab` | `>=4.0` | PDF-Erzeugung |

Entwicklungsabhängigkeiten:

| Paket | Mindestversion | Zweck |
| --- | --- | --- |
| `pytest` | `>=8.0` | Testausführung |
| `pytest-cov` | `>=5.0` | Coverage |
| `pypdf` | `>=4.0` | PDF-Prüfung in Tests |
| `ruff` | `>=0.6` | Linting |
| `import-linter` | `>=2.0` | Architekturprüfung |

#### Zusätzliche Systempakete

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

#### Hardware

Sicher belegt sind folgende Hardware-Komponenten im Projektkontext:

- RFID-Reader als USB-HID-Gerät
- USB-Numpad als Eingabegerät

Die Gerätedateien werden unter Linux über `/dev/input/event*` angesprochen.

### Installation

Repository klonen:

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
```

Virtuelle Umgebung erstellen:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

Abhängigkeiten installieren:

```bash
pip install -e .[dev]
```

Datenbank initialisieren:

```bash
python scripts/init_db.py
```

Der Datenbankpfad kann optional mit `--db` angegeben werden. Standard ist
`arbeitszeit.db`.

Typische Ausgabe:

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

Die Reihenfolge ist zwingend:

1. `scripts/init_db.py`
2. `scripts/setup.py`

Interaktiver Aufruf:

```bash
python scripts/setup.py --db arbeitszeit.db
```

Nicht-interaktiver Aufruf:

```bash
python scripts/setup.py   --db arbeitszeit.db   --backup-dir /var/backups/arbeitszeit   --export-dir /var/exports/arbeitszeit
```

Bereits konfigurierte Schlüssel werden beim erneuten Aufruf übersprungen.

### Erste Konten und Stammdaten

Ersten ADMIN anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   users bootstrap   --username adminname
```

Weiteres Benutzerkonto anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   users add   --username pruefer01   --role REVIEWER
```

Mitarbeiter anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   employees add   --personnel-no M001   --first-name Maria   --last-name Mustermann
```

RFID-Karte zuweisen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   cards assign   --employee-id 1   --uid-hash <HASH>
```

### Funktionstest

```bash
pytest
pytest tests/test_migrations.py
pytest --cov=arbeitszeit
```

---

<a name="3-presentation-layer"></a>

## 3. Presentation Layer

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

### Überblick

Die Presentation Layer umfasst die Benutzeroberflächen, über die das System
bedient wird. Im Repository sind dafür die Terminal-UI für den operativen
Buchungsbetrieb und die Admin-CLI für Verwaltungsaufgaben belegt.

### Terminal-UI

Einstiegspunkt für den operativen Buchungsbetrieb:

```bash
python -m arbeitszeit.presentation.terminal_ui.main   --db arbeitszeit.db   --numpad /dev/input/eventX   --rfid /dev/input/eventY   --terminal-id 1
```

Die Parameter `--db`, `--numpad`, `--rfid` und `--terminal-id` sind
Pflichtparameter.

Die Terminal-UI führt beim Start einen Systemcheck aus und reagiert auf
`SIGINT` und `SIGTERM` mit einem sauberen Beenden.

### Admin-CLI

Einstiegspunkt für die administrative Oberfläche:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   <unterbefehl>
```

`--db` ist bei der Admin-CLI verpflichtend.

Für die meisten schreibenden Operationen ist zusätzlich `--user-id`
erforderlich. Eine Ausnahme ist `users bootstrap`, da vor dem ersten
Administratorkonto noch kein Admin existiert.

Die Benutzer-ID kann alternativ über die Umgebungsvariable `ADMIN_USER_ID`
übergeben werden:

```bash
export ADMIN_USER_ID=1
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   users list
```

`--user-id` hat Vorrang vor `ADMIN_USER_ID`, wenn beide gesetzt sind.

---

<a name="4-application-layer"></a>

## 4. Application Layer

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

### Abgrenzung

Dieses Dokument beschreibt die belegten fachlichen Anwendungsfälle, soweit sie
über die Admin-CLI aufgerufen werden. Die Projektstruktur und Schichtentrennung
gehören nicht hierher, sondern in `handbuch_overview.md`.

### Befehlsgruppen

Aus `src/arbeitszeit/presentation/admin_cli/main.py` sind folgende
Befehlsgruppen eindeutig belegt:

- `employees`
- `cards`
- `bookings`
- `schedule`
- `reports`
- `system`
- `users`

### Belegte Anwendungsfälle

Aus dem Dispatch in `main.py` sind unter anderem diese konkreten Befehle
belegt:

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

### Beispiele

Mitarbeiter deaktivieren:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   employees deactivate 3
```

RFID-Karte ersetzen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   cards replace   --old-card-id 2   --uid-hash <NEUER_HASH>
```

Benutzerkonto deaktivieren:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   users deactivate   --user-id 3
```

Hier erscheint `--user-id` zweimal: das erste Mal für den aufrufenden Admin,
das zweite Mal für das Zielkonto.

---

<a name="5-domain-layer"></a>

## 5. Domain Layer

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

### Überblick

Die Domain Layer beschreibt die fachlichen Kernbegriffe und Regeln des Systems.
Auf Basis des überprüften Handbuchs sind insbesondere Rollen, Mitarbeiter,
RFID-Karten und Buchungskontexte fachlich belegt.

### Rollenmodell

Aus der tatsächlich überprüften Admin-CLI ergibt sich folgendes belastbare
Rollenbild:

| Rolle | In der Admin-CLI als Benutzerkonto anlegbar | Bemerkung |
| --- | --- | --- |
| `ADMIN` | Ja | Vollzugriff für administrative Schreiboperationen |
| `REVIEWER` | Ja | Rolle vorhanden |
| `TECH` | Ja | Rolle vorhanden |
| `EMPLOYEE` | Nein, nicht über `users add` | Mitarbeiter werden separat über `employees` verwaltet |

Aussagen darüber, welche Rolle fachlich exakt welche Use Cases ausführen darf,
sollten nur dann detaillierter dokumentiert werden, wenn die betreffenden
Befehle und ihre Zugriffsprüfungen vollständig gelesen wurden.

### Fachobjekte

Aus dem Handbuch sicher belegt sind mindestens diese fachlichen Objekte:

- Mitarbeiter
- Benutzerkonten
- RFID-Karten
- Buchungen
- Nachträge und Korrekturen
- Prüf- und Review-Fälle

### Vorsicht bei Detailaussagen

Die exakten Inhalte von Enums und weiteren Domain-Modulen sollten nur dann
feingranular dokumentiert werden, wenn die betreffenden Dateien vollständig
verifiziert wurden. Das betrifft insbesondere `src/arbeitszeit/domain/enums.py`.

---

<a name="6-infrastructure-layer"></a>

## 6. Infrastructure Layer

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

### Überblick

Die Infrastructure Layer umfasst Datenhaltung, Backup, Hardware-Anbindung und
betriebsnahe Hilfsskripte. Im überprüften Handbuch sind dafür insbesondere
SQLite, Migrationen, evdev-basierte Eingabegeräte und Backup-Skripte belegt.

### Datenbank und Migrationen

Sicher belegt ist das Vorhandensein dieser Migrationsdateien:

- `0001_schema.sql`
- `0002_seed_defaults.sql`
- `0003_cleanup_booking_status.sql`
- `0004_supplement_reject_fields_and_review_note.sql`
- `0005_time_bookings_device_event_id.sql`
- `0006_system_events_application_error.sql`

Die Migrationslogik in
`src/arbeitszeit/infrastructure/db/migrations.py` verarbeitet Dateinamen im
Muster `0001_*.sql` und speichert die vierstellige Versionsnummer in
`schema_migrations`.

### Backup und Systembetrieb

Das Repository enthält `scripts/backup.py`.

Der Aufruf unterstützt diese Parameter:

| Parameter | Bedeutung | Standard |
| --- | --- | --- |
| `--db` | Pfad zur Datenbankdatei | `arbeitszeit.db` |
| `--backup-dir` | Zielverzeichnis für Backups | `backups/` |
| `--export-dir` | optionales Exportverzeichnis | keiner |

Beispiel:

```bash
python scripts/backup.py   --db arbeitszeit.db   --backup-dir /var/backups/arbeitszeit   --export-dir /var/exports/arbeitszeit
```

`scripts/backup.py` liest zusätzlich Konfigurationswerte aus `system_config`:

- `backup.nas_enabled`
- `backup.nas_path`

Daraus ist belegt, dass NAS-Synchronisation konfigurierbar vorgesehen ist.

### Hardware und Diagnose

Das Skript `scripts/verify_hardware.py` prüft USB-Numpad und RFID-Reader in
drei Stufen: Gerätedatei-Zugriff, Numpad-Tastendruck und RFID-Karten-Scan.

Verfügbare Gerätedateien auflisten:

```bash
python scripts/verify_hardware.py --list
```

Vollständiger Test mit direkter Gerätangabe:

```bash
python scripts/verify_hardware.py   --numpad /dev/input/event3   --rfid /dev/input/event4
```

Nur Gerätezugriff prüfen:

```bash
python scripts/verify_hardware.py   --numpad /dev/input/event3   --rfid /dev/input/event4   --skip-interactive
```

Im Erfolgsfall gibt das Skript den ermittelten SHA-256-Hash der RFID-UID aus.
Dieser Wert kann direkt als `--uid-hash` bei `cards assign` verwendet werden.

### Audit-Werkzeuge

`run_audit.sh` führt Analyse-Tools aus und legt Rohdaten in
`docs/audits/reports/<DATUM>/` ab.

```bash
bash run_audit.sh
```

`scripts/generate_audit_notes.py` liest diese Rohdaten und erzeugt eine
strukturierte Markdown-Zusammenfassung.

```bash
python scripts/generate_audit_notes.py
```

---

<a name="7-audit-und-prufstatus"></a>

## 7. Audit und Prüfstatus

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

### Sicher belegt

Die folgenden Aussagen sind durch die tatsächlich gelesenen Dateien abgesichert:

- Python-Anforderung `>=3.14,<3.15`
- Paketabhängigkeiten aus `pyproject.toml`
- Trennung in `presentation`, `infrastructure`, `application`, `domain`
- Vorhandensein von `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py`
- Bootstrap des ersten Administratorkontos
- Zulässige Rollen für `users add`: `ADMIN`, `REVIEWER`, `TECH`
- Mitarbeiterverwaltung über `employees add`
- `employees deactivate` und `cards deactivate` erfordern positionale IDs
- `cards replace` erfordert `--old-card-id` und `--uid-hash`
- `users deactivate`, `users reactivate` und `users change-role` erfordern
  ein eigenes `--user-id` für das Zielkonto
- Kartenzuweisung über `cards assign --uid-hash`
- Terminal-UI mit Pflichtparametern `--db`, `--numpad`, `--rfid`,
  `--terminal-id`
- Admin-CLI mit verpflichtendem `--db`; Benutzer-ID alternativ über
  `ADMIN_USER_ID`
- `setup.py` unterstützt nicht-interaktiven Aufruf mit `--backup-dir` und
  `--export-dir`
- Vierstellige Migrationsversionen `0001` bis `0006`
- NAS-bezogene Konfigurationsschlüssel im Backup-Skript
- `scripts/verify_hardware.py` für Hardware-Smoke-Tests
- `run_audit.sh` und `scripts/generate_audit_notes.py` für Code-Audits

### Nicht überbehaupten

Die folgenden Punkte sollten in einer technischen Dokumentation nur dann
detailliert dargestellt werden, wenn ihre Implementierung vollständig gelesen
und verifiziert wurde:

- genaue interne RFID-Hash-Bildung und zugehörige Dateipfade
- konkrete Restore-Abläufe und Restore-Befehle
- konkrete `system_events`-Ereignistypen außerhalb nachweislich gelesener
  Stellen
- exakte Inhalte nicht gelesener Module oder Verzeichnisse
- Hardware-Aussagen zu Plattformen, die im gelesenen Code nicht ausdrücklich
  genannt sind

### Empfohlene nächste Prüfungen

Für eine vollständige, dauerhaft belastbare Dokumentation sollten als nächstes
gezielt separat geprüft werden:

1. `migrations/0001_schema.sql` im Volltext für die exakte Datenbankdokumentation
2. `src/arbeitszeit/domain/enums.py` für belastbare Dokumentation der Enums
3. `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` für belastbare
   Hardwarebeschreibung
4. `scripts/show_config.py` nur dann dokumentieren, wenn seine Optionen und
   Ausgabeformate tatsächlich gelesen wurden
5. Admin-CLI-Unterdateien `bookings.py`, `reports.py`, `schedule.py` und
   `system.py` für vollständige Befehls- und Rollenbeschreibung
