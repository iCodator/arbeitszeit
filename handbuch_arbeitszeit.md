# Handbuch – Arbeitszeiterfassung `arbeitszeit`

**Version:** 1.1  
**Stand:** Juni 2026  
**Basis:** Repository `iCodator/arbeitszeit`

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

> ⚠️ Aussagen zu spezifischer Zielhardware wie „Raspberry Pi“ sind aus den hier überprüften Dateien nicht sicher belegbar und werden daher nicht als gesicherte Systemeigenschaft aufgeführt.

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

```bash
python scripts/setup.py --db arbeitszeit.db
```

Das Skript setzt deployment-spezifische Konfigurationswerte in `system_config`, insbesondere:

- `backup.backup_dir`
- `export.export_dir`

Die Reihenfolge ist zwingend:

1. `scripts/init_db.py`
2. `scripts/setup.py`

`scripts/setup.py` bricht ab, wenn die Datenbankdatei noch nicht existiert.

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

Beispiel:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users add \
    --username pruefer01 \
    --role REVIEWER
```

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
├── installationsanleitung_arbeitszeit.md
├── handbuch_arbeitszeit.md
├── migrations/
├── scripts/
├── src/
│   └── arbeitszeit/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── presentation/
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

## 8. Gelesene Admin-CLI-Befehle

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

---

## 9. Datenbank und Migrationen

Sicher belegt ist das Vorhandensein dieser Migrationsdateien:

- `0001_schema.sql`
- `0002_seed_defaults.sql`
- `0003_cleanup_booking_status.sql`
- `0004_supplement_reject_fields_and_review_note.sql`
- `0005_time_bookings_device_event_id.sql`
- `0006_system_events_application_error.sql`

Die Migrationslogik in `src/arbeitszeit/infrastructure/db/migrations.py` verarbeitet Dateinamen im Muster `0001_*.sql` und speichert die vierstellige Versionsnummer in `schema_migrations`.

---

## 10. Was sicher belegt ist

Die folgenden Aussagen sind durch die tatsächlich gelesenen Dateien abgesichert:

- Python-Anforderung `>=3.14,<3.15`
- Paketabhängigkeiten aus `pyproject.toml`
- Trennung in `presentation`, `infrastructure`, `application`, `domain`
- Vorhandensein von `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py`
- Bootstrap des ersten Administratorkontos
- Zulässige Rollen für `users add`: `ADMIN`, `REVIEWER`, `TECH`
- Mitarbeiterverwaltung über `employees add`
- Kartenzuweisung über `cards assign --uid-hash`
- Terminal-UI mit Pflichtparametern `--db`, `--numpad`, `--rfid`, `--terminal-id`
- Admin-CLI mit verpflichtendem `--db`
- Vierstellige Migrationsversionen `0001` bis `0006`
- NAS-bezogene Konfigurationsschlüssel im Backup-Skript

---

## 11. Was nicht überbehauptet werden sollte

Die folgenden Punkte sollten in einer technischen Dokumentation nur dann detailliert dargestellt werden, wenn ihre Implementierung vollständig gelesen und verifiziert wurde:

- genaue interne RFID-Hash-Bildung und zugehörige Dateipfade, sofern diese nicht direkt gelesen wurden
- konkrete Restore-Abläufe und Restore-Befehle
- konkrete `system_events`-Ereignistypen außerhalb der nachweislich gelesenen Stellen
- exakte Inhalte nicht gelesener Module oder Verzeichnisse
- Hardware-Aussagen zu Plattformen, die im gelesenen Code nicht ausdrücklich genannt sind

---

## 12. Empfehlungen

Für eine vollständige, dauerhaft belastbare Dokumentation sollten als nächstes diese Teile gezielt separat geprüft werden:

1. `migrations/0001_schema.sql` im Volltext für die exakte Datenbankdokumentation
2. `src/arbeitszeit/domain/enums.py` für belastbare Dokumentation der Enums
3. `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` für belastbare Hardwarebeschreibung
4. `scripts/show_config.py` nur dann dokumentieren, wenn seine Optionen und Ausgabeformate tatsächlich gelesen wurden
5. Admin-CLI-Unterdateien (`bookings.py`, `reports.py`, `schedule.py`, `system.py`) für vollständige Befehls- und Rollenbeschreibung

---

*Bereinigte Fassung des Handbuchs auf Basis des überprüften Repository-Stands `iCodator/arbeitszeit`*
