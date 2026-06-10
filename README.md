# arbeitszeit

Lokales Zeiterfassungssystem für eine Zahnarztpraxis. Mitarbeiter buchen Arbeitszeiten
über ein physisches Terminal (USB-Numpad + RFID-Leser). Eine separate Admin-CLI verwaltet
Stammdaten, Berichte und den Betrieb.

Das System läuft vollständig lokal — kein externer Server, kein Cloud-Dienst. Daten werden
in einer SQLite-Datenbank gespeichert, Backups optional auf einen NAS gespiegelt.

---

## Funktionsumfang

### Terminal (Kiosk-Betrieb)

- Buchungserfassung: KOMMEN / GEHEN / PAUSE_ANFANG / PAUSE_ENDE via Numpad + RFID-Karte
- Automatische Compliance-Prüfung (ArbZG §3 Höchstarbeitszeit, §5 Ruhezeit, §4 Pausenregel)
- Protokollierung unbekannter und inaktiver Karten
- Systemzeitüberwachung (erkennt Zeitsprünge während Betrieb)

### Admin-CLI

- Mitarbeiter- und RFID-Kartenverwaltung
- Nachtragserfassung und Genehmigung / Ablehnung
- Buchungskorrekturen (Altstand bleibt erhalten, kein stilles Überschreiben)
- Regelarbeitszeitverwaltung (global und mitarbeiterspezifisch)
- Pflichtauswertungen als tabellarische In-App-Ansicht und CSV- / PDF-Export
- Manuelles Backup mit optionalem NAS-Sync
- Systemcheck auf einen Blick

---

## Voraussetzungen

- Python 3.14
- Linux (evdev für Hardware-Zugriff)
- USB-Numpad und RFID-Leser (für Terminal-Betrieb; Simulator für Tests vorhanden)

---

## Installation

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

Hinweise:

- Entwickelt für Python 3.14.
- Für den produktiven Terminal-Betrieb wird Linux mit `evdev` sowie passende USB-Hardware benötigt.
- Für lokale Tests kann der Hardware-Simulator verwendet werden.

---

## Ersteinrichtung

```bash
# 1. Datenbank initialisieren (Migrationen + Seed-Daten)
python scripts/init_db.py --db arbeitszeit.db

# 2. Deployment-spezifische Pfade konfigurieren (einmalig)
python scripts/setup.py --db arbeitszeit.db
#   → fragt interaktiv nach Backup-Verzeichnis und Export-Verzeichnis
#   Alternativ nicht-interaktiv:
python scripts/setup.py --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
    --export-dir /var/exports/arbeitszeit
```

---

## Rechtlicher Rahmen / Referenzdokumente

Die fachlichen, organisatorischen und rechtlichen Anforderungen des Projekts sind in
`docs/pflichtenheft_arbeitszeit_v3.md` und `docs/regelwerk_arbeitszeit_v3.md` festgelegt.

Diese Dokumente bilden die verbindliche Referenz für Arbeitszeiterfassung, Prüfhilfen,
Rollen- und Rechtekonzept, Aufbewahrung, Korrekturen, Nachträge sowie Backup- und
Restore-Prozesse.

---

## Betrieb

### Terminal-UI starten

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
    --db arbeitszeit.db \
    --numpad /dev/input/by-id/usb-numpad \
    --rfid   /dev/input/by-id/usb-rfid \
    --terminal-id 1
```

Das Terminal läuft als Endlosschleife und beendet sich sauber bei `SIGTERM` / `SIGINT`.

### Admin-CLI starten

```bash
# Benutzer-ID via Flag oder Umgebungsvariable ADMIN_USER_ID
python -m arbeitszeit.presentation.admin_cli.main --user-id 1 <Befehl>
```

**Übersicht der Befehle:**

| Gruppe | Befehl | Beschreibung |
| --- | --- | --- |
| `employees` | `list` | Alle Mitarbeiter anzeigen |
| | `add` | Mitarbeiter anlegen |
| | `deactivate` / `reactivate` | Status ändern |
| | `assign-card` / `replace-card` | RFID-Karte zuweisen |
| `bookings` | `supplement add` | Nachtrag anlegen |
| | `supplement approve` / `reject` | Nachtrag genehmigen / ablehnen |
| | `correct` | Buchung korrigieren |
| `schedule` | `show` | Aktuelle Regelarbeitszeiten |
| | `set` | Neue Regelarbeitszeit setzen |
| `reports` | `open-bookings` | Offene Buchungen |
| | `warn-cases` | Buchungen mit Prüfstatus |
| | `corrections` | Korrekturen |
| | `supplements` | Nachträge |
| | `open-review-cases` | Offene Prüffälle |
| | `export-csv` | Detail- und Verdichtet-Export als CSV |
| | `export-pdf-day` / `export-pdf-week` / `export-pdf-month` | PDF-Berichte |
| | `export-pdf-employee` | Mitarbeiterbericht als PDF |
| `system` | `check` | Systemcheck ausführen |
| | `backup` | Manuelles Backup erstellen |

Alle Befehle akzeptieren `--from` / `--to` für Zeitraumfilter (ISO-8601-Datum).

### Backup

```bash
python scripts/backup.py \
    --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit
```

NAS-Sync wird über `backup.nas_enabled` und `backup.nas_path` in `system_config` gesteuert
(via Admin-CLI oder direkt per SQL). Der NAS-Pfad wird als striktes Spiegelziel geführt
(`rsync --delete`), nicht als eigenständiges Langzeitarchiv.

---

## Architektur

```text
src/arbeitszeit/
├── domain/          Enums, Entities, Businessregeln, Compliance-Checks, Repository-Ports
├── application/     Use Cases, Commands, Results, Unit-of-Work-Protocol
├── infrastructure/  SQLite-Repos, UoW, Hardware-Adapter, Backup, Export, Systemcheck
└── presentation/
    ├── terminal_ui/ Kiosk-Schleife: Numpad → RFID → BookUseCase → Feedback
    └── admin_cli/   argparse-CLI für Verwaltung und Betrieb
```

**Wichtige Architekturentscheidungen:**

- Buchungen werden nie physisch gelöscht; Klärung erfolgt ausschließlich über Status
  (`CORRECTED`, `CLOSED_WITH_NOTE`) oder Korrekturobjekte.
- Audit-Log schreibt nach `uow.commit()` über eine separate `audit_conn`-Verbindung.
- `report_queries.py` ist die einzige Wahrheitsquelle für alle Berichte und Exporte.
- Compliance-Prüfungen laufen in der Domain-Schicht, nicht in SQLite.

---

## Datenbankschema

16 Tabellen in `migrations/0001_schema.sql` (15 fachliche + `schema_migrations`):

| Ebene | Tabellen |
| --- | --- |
| Person | `employees`, `user_accounts`, `rfid_cards` |
| Erfassung | `terminals`, `time_bookings`, `device_events` |
| Prüfung | `review_cases`, `review_case_actions`, `booking_status_history` |
| Änderung | `booking_corrections`, `supplements`, `work_schedule_versions` |
| Nachweis | `audit_log`, `system_events`, `system_config` |

Migrationen werden versioniert und idempotent über `scripts/init_db.py` angewendet.

---

## Tests

```bash
# Alle Tests
python -m pytest

# Mit Coverage
python -m pytest --cov=arbeitszeit --cov-report=term-missing
```

369 Tests in vier Ebenen:

| Verzeichnis | Inhalt |
| --- | --- |
| `tests/domain/` | Domänenregeln, Entity-Invarianten |
| `tests/application/` | Use Cases mit Fake-Repos |
| `tests/integration/` | Repositories und UoW gegen echte SQLite-DB |
| `tests/e2e/` | Vollständige Abläufe mit Hardware-Simulator |

---

## Projektstruktur

```text
arbeitszeit/
├── migrations/          SQL-Migrationen (0001–0006)
├── scripts/
│   ├── init_db.py       Datenbankinitialisierung
│   ├── setup.py         Ersteinrichtung (einmalig nach init_db.py)
│   └── backup.py        Backup-Script für systemd-Timer / cron
├── src/arbeitszeit/     Quellcode (siehe Architektur)
├── tests/               Testsuites
└── docs/
    ├── pflichtenheft_arbeitszeit_v3.md
    └── regelwerk_arbeitszeit_v3.md
```

---

## Lizenz

Privates Projekt — nicht zur öffentlichen Nutzung freigegeben.
