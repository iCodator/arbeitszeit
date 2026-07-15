# Handbuch `arbeitszeit`

**Version:** 1.6  
**Stand:** Juli 2026  
**Projekt:** Lokales Zeiterfassungssystem für eine Zahnarztpraxis

Dieses Handbuch fasst die im Repository vorhandenen Handbuch- und
Betriebsdokumente des Projekts `arbeitszeit` in einem einzigen,
durchgängig lesbaren Dokument zusammen. Grundlage sind das bestehende
Gesamthandbuch Version 1.5 sowie die separat vorliegenden Dokumente zum
Datenbankschema, zur Konfigurationsdiagnose und zum Bereich
Backup/Restore.

## Inhaltsverzeichnis

- [Kapitel 1: Übersicht](#kapitel-1-übersicht)
  - [Zweck](#zweck)
  - [Projektstruktur](#projektstruktur)
  - [Schichten](#schichten)
- [Kapitel 2: Installation](#kapitel-2-installation)
  - [Systemvoraussetzungen](#systemvoraussetzungen)
  - [Installation](#installation)
  - [Ersteinrichtung](#ersteinrichtung)
  - [Erste Konten und Stammdaten](#erste-konten-und-stammdaten)
  - [Funktionstest](#funktionstest)
- [Kapitel 3: Präsentationsschicht](#kapitel-3-präsentationsschicht)
  - [Überblick und Aufbau](#überblick-und-aufbau)
  - [Terminal-UI (`terminal_ui/`)](#terminal-ui-terminal_ui)
  - [Admin-CLI (`admin_cli/`)](#admin-cli-admin_cli)
  - [Domain: `employees` und `cards`](#domain-employees-und-cards)
  - [Domain: `bookings`](#domain-bookings)
  - [Domain: `schedule`](#domain-schedule)
  - [Domain: `reports`](#domain-reports)
  - [Domain: `system`](#domain-system)
  - [Domain: `users`](#domain-users)
  - [Zeitraum-Hilfsfunktionen (`_intervals.py`)](#zeitraum-hilfsfunktionen-_intervalspy)
- [Kapitel 4: Anwendungsschicht](#kapitel-4-anwendungsschicht)
  - [4.1 Überblick und Einordnung](#41-überblick-und-einordnung)
  - [4.2 Commands — Eingabe-DTOs (`commands.py`)](#42-commands--eingabe-dtos-commandspy)
  - [4.3 Results — Ausgabe-DTOs schreibender Operationen (`results.py`)](#43-results--ausgabe-dtos-schreibender-operationen-resultspy)
  - [4.4 Queries — Lesende Abfrage-DTOs (`queries.py`)](#44-queries--lesende-abfrage-dtos-queriespy)
  - [4.5 Unit of Work — Transaktionsprotokoll (`unit_of_work.py`)](#45-unit-of-work--transaktionsprotokoll-unit_of_workpy)
  - [4.6 Use Cases im Detail](#46-use-cases-im-detail)
  - [4.7 Querschnittliche Entwurfsprinzipien](#47-querschnittliche-entwurfsprinzipien)
  - [4.8 Erweiterungshinweise](#48-erweiterungshinweise)
  - [4.9 Hinweis zu admin-CLI-Befehlen](#49-hinweis-zu-admin-cli-befehlen)
- [Kapitel 5: Domain-Modell](#kapitel-5-domain-modell)
  - [Überblick und Designprinzip](#überblick-und-designprinzip)
  - [Value Objects – Starke ID-Typen](#value-objects--starke-id-typen)
  - [Enumerationen](#enumerationen)
  - [Entitäten](#entitäten)
  - [Domänenfehler](#domänenfehler)
  - [Repository-Protokolle (Ports)](#repository-protokolle-ports)
  - [Domain Services](#domain-services)
  - [Audit-Event-Katalog](#audit-event-katalog)
  - [Zusammenspiel der Domain-Schicht](#zusammenspiel-der-domain-schicht)
- [Kapitel 6: Infrastrukturschicht](#kapitel-6-infrastrukturschicht)
  - [Überblick und Zweck](#überblick-und-zweck)
  - [Datenbankzugriff (`db/`)](#datenbankzugriff-db)
  - [Hardware-Abstraktion (`hardware/`)](#hardware-abstraktion-hardware)
  - [Export (`export/`)](#export-export)
  - [Backup (`backup/backup_service.py`)](#backup-backupbackup_servicepy)
  - [Systemüberwachung](#systemüberwachung)
  - [Querverbindungen und Architekturprinzipien](#querverbindungen-und-architekturprinzipien)
- [Kapitel 7: Datenbankschema](#kapitel-7-datenbankschema)
  - [Zweck dieses Dokuments](#zweck-dieses-dokuments)
  - [Migrationsübersicht](#migrationsübersicht)
  - [Tabellen im finalen Zustand (nach Migration 0006)](#tabellen-im-finalen-zustand-nach-migration-0006)
  - [Indizes im finalen Zustand](#indizes-im-finalen-zustand)
  - [Technisches Muster: Table-Rebuild bei Schema-Änderungen](#technisches-muster-table-rebuild-bei-schema-änderungen)
  - [Globale Einstellung](#globale-einstellung)
- [Kapitel 8: Backup und Restore](#kapitel-8-backup-und-restore)
  - [Einordnung](#einordnung)
  - [Quellbasis und Geltungsbereich](#quellbasis-und-geltungsbereich)
  - [Fachlicher Status](#fachlicher-status)
- [Kapitel 9: Audit und Prüfstatus](#kapitel-9-audit-und-prüfstatus)
  - [Sicher belegt](#sicher-belegt)
  - [Nicht überbehaupten](#nicht-überbehaupten)
  - [Empfohlene nächste Prüfungen](#empfohlene-nächste-prüfungen)
- [Kapitel 10: Konfigurationsdiagnose](#kapitel-10-konfigurationsdiagnose)
  - [Zweck](#zweck-1)
  - [Aufruf](#aufruf)
  - [Optionen](#optionen)
  - [Datenquellen](#datenquellen)
  - [Abfrage der Datenbank](#abfrage-der-datenbank)
  - [Anzeige von `config.toml`](#anzeige-von-configtoml)
  - [Textausgabe](#textausgabe)
  - [JSON-Ausgabe](#json-ausgabe)
  - [Wertdekodierung](#wertdekodierung)
  - [Abhängigkeiten](#abhängigkeiten)
  - [Abgrenzung](#abgrenzung)

## Kapitel 1: Übersicht

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
├── installationsanleitung.md
├── handbuch.md
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

## Kapitel 2: Installation

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

Die Gerätedateien werden unter Linux über `/dev/input/event*`
angesprochen.

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
python scripts/setup.py \
  --db arbeitszeit.db \
  --backup-dir /var/backups/arbeitszeit \
  --export-dir /var/exports/arbeitszeit
```

Bereits konfigurierte Schlüssel werden beim erneuten Aufruf übersprungen.

### Erste Konten und Stammdaten

Ersten ADMIN anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  users bootstrap \
  --username adminname
```

Weiteres Benutzerkonto anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  users add \
  --username pruefer01 \
  --role REVIEWER
```

Mitarbeiter anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  employees add \
  --personnel-no M001 \
  --first-name Maria \
  --last-name Mustermann
```

RFID-Karte zuweisen (direkt einlesen):

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  cards assign \
  --employee-id 1 \
  --scan \
  --rfid "HID 1234:5678"
```

Alternativ mit vorab berechnetem Hash: `--uid-hash <HASH>` statt
`--scan --rfid "..."` (siehe Befehlsreferenz).

### Funktionstest

```bash
pytest
pytest tests/test_migrations.py
pytest --cov=arbeitszeit
```

## Kapitel 3: Präsentationsschicht

### Überblick und Aufbau

Die Präsentationsschicht ist die äußerste Schale des Systems und bildet
die einzige Schnittstelle zwischen Benutzer oder Administrator und der
darunterliegenden Fach- und Anwendungslogik. Sie enthält keine
Geschäftslogik, sondern übersetzt ausschließlich Benutzereingaben in
Kommandos der Anwendungsschicht und gibt Ergebnisse als lesbare Texte
aus.

Das Paket gliedert sich in zwei eigenständige Untermodule:

- `presentation/terminal_ui/` – operativer Buchungsbetrieb (Endlosschleife, RFID + Numpad)
- `presentation/admin_cli/` – administrative Verwaltung (Kommandozeile, rollenbasiert)

### Terminal-UI (`terminal_ui/`)

#### Zweck und Betriebsmodus

Die Terminal-UI ist der im laufenden Praxisbetrieb aktive Prozess. Sie
startet beim Systemstart als Endlosschleife und wartet kontinuierlich auf
Hardware-Eingaben: zuerst Auswahl der Buchungsart über das Numpad, dann
RFID-Kartenscan. Der Prozess reagiert auf `SIGTERM` und `SIGINT`
mit einem sauberen Graceful Shutdown.

#### Startparameter

Die Terminal-UI wird mit vier Pflichtargumenten gestartet:

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db /pfad/zur/datenbank.db \
  --numpad "Gerätename des Numpads" \
  --rfid "Gerätename des RFID-Readers" \
  --terminal-id 1
```

#### Startverhalten und Systemcheck

Vor dem Eintritt in die Buchungsschleife führt `run()` automatisch einen
Systemcheck durch. Schlägt der Check fehl, wird eine
Desktop-Benachrichtigung ausgelöst (`notify(…, urgency="critical")`),
aber der Buchungsbetrieb wird nicht abgebrochen. Fehlerdetails werden in
der Tabelle `system_events` gespeichert.

#### Buchungszyklus (`booking_loop.py`)

Jeder Buchungszyklus läuft in drei Schritten ab:

1. **Numpad-Eingabe:** Der Mitarbeiter wählt die Buchungsart über das USB-Numpad.
2. **RFID-Scan:** Das System wartet auf den Kartenscan; das Timeout ist über `booking.grace_seconds_after_numpad_select` in `system_config` konfigurierbar.
3. **Buchungsverarbeitung:** Das Geräteereignis `RFID_SCAN` wird vor dem eigentlichen `BookUseCase`-Aufruf in `device_events` gespeichert.

#### Feedback-Ausgabe

Nach jeder Buchung gibt das Terminal eine einzeilige Rückmeldung aus.

| Status | Ausgabe |
| --- | --- |
| `OPEN` / `OK` | `Buchung erfasst.` |
| `WARN` | `Buchung erfasst — Hinweis: Regelzeitabweichung festgestellt.` |
| `NEEDS_REVIEW` | `Buchung erfasst — Prüfpflicht: Manuelle Überprüfung erforderlich.` |

#### Domänenfehler-Behandlung

Bekannte Domänenfehler werden in menschenlesbare Meldungen übersetzt und
ausgegeben, ohne den Prozess zu beenden.

| Fehlerklasse | Anzeige |
| --- | --- |
| `UnknownCardError` | `Karte nicht erkannt.` |
| `InactiveCardError` | `Karte deaktiviert.` |
| `InactiveEmployeeError` | `Mitarbeiter inaktiv.` |
| `InvalidBookingSequenceError` | `Ungültige Buchungsreihenfolge.` |
| `OpenPhaseConflictError` | `Offene Phase — bitte zuerst abschließen.` |

Unerwartete Ausnahmen werden in `system_events` protokolliert; der
Betrieb läuft weiter.

### Admin-CLI (`admin_cli/`)

#### Zweck

Die Admin-CLI ist das Verwaltungswerkzeug für Administratoren und
technisches Personal. Sie wird als `admin`-Programm gestartet, erfordert
immer die Datenbankdatei `--db` und eine Benutzer-ID `--user-id`
oder die Umgebungsvariable `ADMIN_USER_ID`, und verteilt alle Aufrufe
über eine zentrale Dispatch-Tabelle an spezialisierte Handler-Module.

#### Grundaufruf

```bash
admin --db /pfad/zur/datenbank.db --user-id 1 <domain> <subcommand> [optionen]
```

Alternativ zur `--user-id`-Option kann die Umgebungsvariable
`ADMIN_USER_ID` gesetzt werden. Die einzige Ausnahme ist
`users bootstrap`.

#### Rollenmodell

Alle schreibenden Operationen prüfen die Rolle des aufrufenden Benutzers
direkt gegen die Tabelle `user_accounts`. Es gibt drei Rollen:

| Rolle | Erlaubte Bereiche |
| --- | --- |
| `ADMIN` | Alle Operationen (Lesen + Schreiben) |
| `REVIEWER` | Berichte, Buchungsüberprüfung, Nachträge genehmigen/ablehnen |
| `TECH` | Systemcheck, Backup |

Lesende Operationen sind ohne Rolleneinschränkung nutzbar.

### Domain: `employees` und `cards`

#### Mitarbeiterverwaltung (`employees.py`)

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `employees list` | Alle Mitarbeiter tabellarisch auflisten | keine |
| `employees add --personnel-no … --first-name … --last-name …` | Mitarbeiter anlegen | `ADMIN` |
| `employees deactivate <id>` | Mitarbeiter deaktivieren | `ADMIN` |

#### Kartenverwaltung

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `cards assign --employee-id … --scan --rfid …` | Neue RFID-Karte zuweisen | `ADMIN` |
| `cards replace --old-card-id … --uid-hash …` | Karte ersetzen | `ADMIN` |
| `cards deactivate <id>` | Karte auf `INACTIVE` setzen | `ADMIN` |

Jede schreibende Operation wird mit einem `_audit(…)`-Eintrag in
`audit_log` protokolliert.

### Domain: `bookings`

Buchungskorrekturen und Nachträge laufen vollständig über Use Cases der
Anwendungsschicht.

| Befehl | Beschreibung |
| --- | --- |
| `bookings correct --booking-id … --type … --at … --reason …` | Bestehende Buchung korrigieren |
| `bookings supplement --employee-id … --type … --at … --reason …` | Nachträgliche Buchung erfassen |
| `bookings approve-supplement --supplement-id …` | Nachtrag freigeben |
| `bookings reject-supplement --supplement-id … --reason …` | Nachtrag ablehnen |

Das `--at`-Argument erwartet ISO-8601-Format; fehlt die Zeitzone, wird
UTC angenommen.

### Domain: `schedule`

Die Regelarbeitszeit wird versioniert gespeichert; jede Änderung erzeugt
eine neue Version und schließt die Vorgängerversion.

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `schedule set --weekday 1-7 --start HH:MM --end HH:MM --from YYYY-MM-DD [--employee-id ID]` | Regelarbeitszeit setzen | `ADMIN` |
| `schedule show` | Aktive Versionen anzeigen | `ADMIN`, `REVIEWER` |

### Domain: `reports`

Alle Report-Befehle erfordern `ADMIN`- oder `REVIEWER`-Rolle. Das
Export-Verzeichnis wird aus `system_config` gelesen.

| Befehl | Beschreibung |
| --- | --- |
| `reports export-csv --from … --to … [--employee-id …]` | Zwei CSV-Dateien: Detailbuchungen + Übersicht |
| `reports export-pdf-day --date YYYY-MM-DD` | Tagesbericht als PDF |
| `reports export-pdf-week --year YYYY --week WW` | Wochenbericht als PDF |
| `reports export-pdf-month --year YYYY --month MM` | Monatsbericht als PDF |
| `reports export-pdf-employee --employee-id … --from … --to …` | Mitarbeiterbericht als PDF |
| `reports export-csv-review-cases --from … --to … [--employee-id …]` | Offene Prüffälle als CSV exportieren |

### Domain: `system`

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `system check` | Systemcheck auslösen | `ADMIN`, `TECH` |
| `system backup` | Manuelles Backup der SQLite-Datenbank auslösen | `ADMIN`, `TECH` |

Der Backup-Dienst liest Zielverzeichnis und NAS-Pfad aus
`system_config`. Schlägt die NAS-Synchronisation fehl, endet der Prozess
mit Exitcode 1; das lokale Backup ist zu diesem Zeitpunkt bereits
erfolgreich erstellt.

### Domain: `users`

Passwörter werden mit PBKDF2-HMAC-SHA256 und 260.000 Iterationen gehasht.
Das Klartextpasswort wird nach der Ausgabe nirgends gespeichert.

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `users bootstrap --username … [--password …]` | Erstes Administratorkonto anlegen | — |
| `users add --username … --role … [--employee-id …] [--password …]` | Neues Benutzerkonto anlegen | `ADMIN` |
| `users list` | Alle Konten tabellarisch auflisten | keine |
| `users deactivate --user-id …` | Benutzerkonto deaktivieren | `ADMIN` |
| `users reactivate --user-id …` | Benutzerkonto reaktivieren | `ADMIN` |
| `users change-role --user-id … --role …` | Rolle ändern | `ADMIN` |

### Zeitraum-Hilfsfunktionen (`_intervals.py`)

Alle Datums- und Zeitraum-Berechnungen in der Admin-CLI verwenden die
drei Funktionen aus
`src/arbeitszeit/presentation/admin_cli/_intervals.py`.

| Funktion | Beschreibung |
| --- | --- |
| `day_interval(day)` | `[day 00:00 UTC, next_day 00:00 UTC)` |
| `week_interval(year, week)` | ISO-Woche: Montag 00:00 UTC bis Montag+7 00:00 UTC |
| `month_interval(year, month)` | Erster bis exklusiv erster des Folgemonats, UTC |

## Kapitel 4: Anwendungsschicht

Die Anwendungsschicht ist das Herzstück der fachlichen Steuerung. Sie
vermittelt zwischen Präsentationsschicht und Domänenschicht und enthält
keine SQL-Logik, keine Hardware-Zugriffe und keine UI-Elemente.

### 4.1 Überblick und Einordnung

Das Paket folgt dem CQRS-Prinzip. Schreibende Operationen werden über
Commands und Use Cases gesteuert, lesende Operationen über Query-DTOs.

### 4.2 Commands — Eingabe-DTOs (`commands.py`)

Commands sind unveränderliche Datenbehälter mit `frozen=True` und
`slots=True`.

| Command-Klasse | Zweck |
| --- | --- |
| `BookCommand` | RFID-Buchung vom Terminal |
| `CreateSupplementCommand` | Nachtrag erfassen |
| `CreateCorrectionCommand` | Buchung korrigieren |
| `ApproveSupplementCommand` | Nachtrag genehmigen |
| `RejectSupplementCommand` | Nachtrag ablehnen |
| `ChangeWorkScheduleCommand` | Regelarbeitszeit setzen |
| `CreateEmployeeCommand` | Mitarbeiter anlegen |
| `DeactivateEmployeeCommand` | Mitarbeiter deaktivieren |
| `AssignRfidCardCommand` | RFID-Karte zuweisen |
| `ReplaceRfidCardCommand` | RFID-Karte ersetzen |
| `DeactivateRfidCardCommand` | RFID-Karte deaktivieren |
| `CreateUserAccountCommand` | Benutzerkonto anlegen |
| `DeactivateUserAccountCommand` | Benutzerkonto deaktivieren |
| `ReactivateUserAccountCommand` | Benutzerkonto reaktivieren |
| `ChangeUserRoleCommand` | Benutzerrolle ändern |
| `BootstrapAdminCommand` | Ersten Admin-Account anlegen |

### 4.3 Results — Ausgabe-DTOs schreibender Operationen (`results.py`)

Jeder Use Case gibt ein typisiertes Result-Objekt zurück.

| Result-Klasse | Enthaltene Felder |
| --- | --- |
| `BookResult` | `booking_id`, `status`, `follow_up_case_ids` |
| `SupplementResult` | `supplement_id`, `review_case_id` |
| `CorrectionResult` | `correction_id`, `updated_booking_id`, `review_case_id` |
| `WorkScheduleChangeResult` | `new_version_id`, `superseded_version_id` |
| `ApproveSupplementResult` | `supplement_id`, `booking_id`, `booking_status`, `follow_up_case_ids` |
| `RejectSupplementResult` | `supplement_id`, `review_case_id` |
| `CreateEmployeeResult` | `employee_id` |
| `AssignRfidCardResult` | `card_id` |
| `ReplaceRfidCardResult` | `new_card_id` |
| `CreateUserAccountResult` | `user_id` |
| `BootstrapAdminResult` | `user_id`, `username` |

### 4.4 Queries — Lesende Abfrage-DTOs (`queries.py`)

Die Query-DTOs bilden die CQRS-Leseseite ab; die eigentlichen
Datenbankabfragen liegen in der Infrastrukturschicht.

| Row-Klasse | Verwendungszweck |
| --- | --- |
| `BookingRow` | Buchungsliste mit Mitarbeiterzuordnung |
| `CorrectionRow` | Korrekturprotokoll |
| `SupplementRow` | Nachtragsliste mit Freigabestatus |
| `ReviewCaseRow` | Offene oder aktive Prüffälle |

### 4.5 Unit of Work — Transaktionsprotokoll (`unit_of_work.py`)

`UnitOfWork` ist ein Protocol und fasst alle Repository-Referenzen unter
einem gemeinsamen Transaktionskontext zusammen.

Die definierten Repositories sind: `employee_repo`,
`user_account_repo`, `rfid_card_repo`, `time_booking_repo`,
`work_schedule_repo`, `review_case_repo`, `supplement_repo`,
`booking_correction_repo`, `audit_log_repo`, `system_config_repo` und
`device_event_repo`.

Das Audit-Log wird nach `commit()` geschrieben.

### 4.6 Use Cases im Detail

#### 4.6.1 `BookUseCase` — Terminalbuchung (`book_time.py`)

Der Use Case verarbeitet RFID-Buchungen vom Terminal. Der Ablauf umfasst
Kartenprüfung, Mitarbeiterprüfung, Sequenzvalidierung, Prüfung der
Regelarbeitszeit, Compliance-Checks, Buchungsspeicherung, Anlegen von
Prüffällen, `commit()` und anschließendes Audit-Logging.

Die Statuslogik lautet:

| Status | Bedingung |
| --- | --- |
| `OPEN` | Buchungstyp ist `COME` oder `BREAK_START` |
| `OK` | Keine Compliance-Verstöße |
| `WARN` | Mindestens ein Flag ohne `CRITICAL`-Schwere |
| `NEEDS_REVIEW` | Mindestens ein Flag mit `CRITICAL`-Schwere |

#### 4.6.2 `CorrectBookingUseCase` — Buchungskorrektur (`correct_booking.py`)

Ermöglicht berechtigten Benutzern mit Rolle `ADMIN` oder `REVIEWER`,
eine bestehende Buchung nachträglich zu ändern.

#### 4.6.3 `RegisterSupplementUseCase` — Nachtrag erfassen (`register_supplement.py`)

Erfasst eine nachträgliche Buchung als `PENDING` und erzeugt zunächst
noch keine wirksame Buchung in `time_bookings`.

#### 4.6.4 `ApproveSupplementUseCase` — Nachtrag freigeben (`approve_supplement.py`)

Genehmigt einen ausstehenden Nachtrag und überführt ihn in eine echte
Buchung mit vollständiger Compliance-Prüfung.

#### 4.6.5 `RejectSupplementUseCase` — Nachtrag ablehnen (`reject_supplement.py`)

Lehnt einen ausstehenden Nachtrag ab, ohne eine Buchung zu erzeugen.

#### 4.6.6 `ManageWorkScheduleUseCase` — Regelarbeitszeit (`manage_work_schedule.py`)

Ändert die Regelarbeitszeit für einen Wochentag, global oder
mitarbeiterspezifisch; nur `ADMIN` darf diesen Use Case ausführen.

#### 4.6.7 Mitarbeiterverwaltung (`manage_employees.py`)

Beide Use Cases erfordern `ADMIN`. Das gilt für das Anlegen und
Deaktivieren von Mitarbeitern.

#### 4.6.8 RFID-Kartenverwaltung (`manage_rfid_cards.py`)

Alle drei Use Cases erfordern `ADMIN`: zuweisen, ersetzen und
deaktivieren.

#### 4.6.9 Benutzerkontenverwaltung (`manage_user_accounts.py`)

Die Verwaltung von Benutzerkonten einschließlich Bootstrap des ersten
Admins ist als eigener Use-Case-Bereich dokumentiert.

### 4.7 Querschnittliche Entwurfsprinzipien

Die Handbuchquelle belegt Rollenprüfungen zu Beginn manueller Use Cases,
nachgelagertes Audit-Logging, Unveränderlichkeit der DTOs und eine
klare Fehlertyp-Hierarchie.

### 4.8 Erweiterungshinweise

Neue Use Cases, Query-Sichten und Compliance-Regeln werden in den jeweils
dafür vorgesehenen Modulen ergänzt; die Reihenfolge `commit()` vor
Audit-Log darf nicht geändert werden.

### 4.9 Hinweis zu admin-CLI-Befehlen

Die vollständige Liste der Admin-CLI-Befehlsgruppen gehört laut
bestehender Handbuchstruktur zur Präsentationsschicht und wird dort
dokumentiert.

## Kapitel 5: Domain-Modell

### Überblick und Designprinzip

Das Domain-Modell ist der fachliche Kern des Systems `arbeitszeit`. Es
enthält ausschließlich Geschäftslogik und keine Abhängigkeiten zu
Datenbank, Hardware oder UI.

### Value Objects – Starke ID-Typen

Alle Primärschlüssel im System sind starke ID-Typen auf Basis von
`typing.NewType`.

| ID-Typ | Bedeutung |
| --- | --- |
| `EmployeeId` | Mitarbeiter-Datensatz |
| `UserAccountId` | Benutzerkonto |
| `RfidCardId` | RFID-Karte |
| `TerminalId` | Buchungsterminal |
| `TimeBookingId` | Zeitbuchung |
| `WorkScheduleVersionId` | Version einer Regelarbeitszeit |
| `ReviewCaseId` | Prüffall |
| `SupplementId` | Nachtrag |
| `BookingCorrectionId` | Buchungskorrektur |
| `DeviceEventId` | Geräteereignis |
| `AuditLogEntryId` | Eintrag im Audit-Log |

### Enumerationen

Alle Zustands- und Klassenangaben sind als `StrEnum` definiert.

### Entitäten

Die Handbuchquelle dokumentiert die Domänenentitäten des Systems in
`entities.py` als fachliche Repräsentationen der Kernobjekte.

### Domänenfehler

Die Domänenschicht enthält eine Fehlerhierarchie für Berechtigungs-,
Status-, Validierungs- und Konfliktfehler.

### Repository-Protokolle (Ports)

Die Ports definieren die Repository-Schnittstellen der Domain-Schicht und
bilden die Abstraktionsgrenze zur Infrastrukturschicht.

### Domain Services

Die Domain Services decken Buchungssequenz-Validierung und
Compliance-Prüfhilfen ab.

### Audit-Event-Katalog

Die Datei `audit_events.py` enthält den Katalog der im Projekt
verwendeten Audit-Log-Ereignisse.

### Zusammenspiel der Domain-Schicht

Die Domain-Schicht bündelt Entitäten, Value Objects, Enumerationen,
Ports, Services und Fehler in einer fachlich isolierten Kernschicht.

## Kapitel 6: Infrastrukturschicht

### Überblick und Zweck

Die Infrastrukturschicht implementiert technische Adapter für
Datenbankzugriff, Hardware, Export, Backup und Systemüberwachung.

### Datenbankzugriff (`db/`)

Die Infrastrukturschicht enthält die technische Umsetzung der
SQLite-Anbindung sowie die konkreten Repository-Implementierungen.

### Hardware-Abstraktion (`hardware/`)

Die Hardware-Schicht kapselt den Zugriff auf RFID-Reader und Numpad über
Linux-Eingabegeräte.

### Export (`export/`)

Der Exportbereich stellt Berichtsausgaben für CSV und PDF bereit.

### Backup (`backup/backup_service.py`)

Die bestehende Infrastrukturdokumentation nennt den Backup-Dienst als
eigenständigen Teilbereich der Schicht.

### Systemüberwachung

Die Infrastrukturschicht enthält Funktionen zur Systembeobachtung und
Schreibpfade für `system_events`.

### Querverbindungen und Architekturprinzipien

Die technische Schicht realisiert Adapter, ohne fachliche Regeln in die
Domäne zurückzuschreiben.

## Kapitel 7: Datenbankschema

### Zweck dieses Dokuments

Dieses Kapitel beschreibt das SQLite-Schema von `arbeitszeit` exakt auf
Basis der gelesenen Migrationsdateien `0001_schema.sql` bis
`0006_system_events_application_error.sql`.

### Migrationsübersicht

| Version | Datei | Zweck |
| --- | --- | --- |
| 0001 | `0001_schema.sql` | Ursprüngliches Gesamtschema |
| 0002 | `0002_seed_defaults.sql` | Standard-Wochenarbeitszeiten und System-Konfigurationswerte |
| 0003 | `0003_cleanup_booking_status.sql` | Bereinigung der Status-Werte in Buchungstabellen |
| 0004 | `0004_supplement_reject_fields_and_review_note.sql` | Trennung von Genehmigung und Ablehnung bei Nachträgen |
| 0005 | `0005_time_bookings_device_event_id.sql` | Verknüpfung von Buchungen mit Geräte-Ereignissen |
| 0006 | `0006_system_events_application_error.sql` | Neuer Ereignistyp `APPLICATION_ERROR` |

Jede Migration ist in `schema_migrations` mit Versionsnummer und
Anwendungszeitpunkt verzeichnet.

### Tabellen im finalen Zustand (nach Migration 0006)

Das finale Schema umfasst unter anderem die Tabellen `employees`,
`user_accounts`, `rfid_cards`, `terminals`, `time_bookings`,
`booking_status_history`, `booking_corrections`, `supplements`,
`review_cases`, `review_case_actions`, `work_schedule_versions`,
`system_config`, `device_events`, `system_events`, `audit_log` und
`schema_migrations`.

Beispielhaft zentrale fachliche Punkte:

- `time_bookings.current_status` erlaubt die Werte `OK`, `OPEN`, `WARN`, `NEEDS_REVIEW`, `CORRECTED` und `CLOSED_WITH_NOTE`.
- `supplements.approval_status` erlaubt `PENDING`, `APPROVED` und `REJECTED`.
- `review_cases.case_type` deckt unter anderem offene Phasen, Regelzeitabweichungen, Kartenanomalien und `MANUAL_ENTRY_REVIEW` ab.
- `system_config` ist versioniert über `config_key` und `version`.
- `system_events.event_type` umfasst seit Migration 0006 zusätzlich `APPLICATION_ERROR`.

#### Arbeitszeiten und Seed-Werte

Migration 0002 befüllt `work_schedule_versions` mit Standard-Arbeitszeiten
für Montag bis Freitag und seedet vier Startwerte in `system_config`,
darunter `app.timezone`, `booking.grace_seconds_after_numpad_select`,
`backup.nas_enabled` und `backup.nas_path`.

### Indizes im finalen Zustand

Das Schema enthält 17 dokumentierte Indizes, darunter
`idx_time_bookings_employee_booked_at`,
`idx_review_cases_status_detected_at`,
`idx_system_config_key_version` und
`idx_audit_log_object_event_at`.

### Technisches Muster: Table-Rebuild bei Schema-Änderungen

Migrationen 0003, 0004, 0005 und 0006 folgen laut Dokument einem
Table-Rebuild-Muster, weil SQLite bestehende `CHECK`-Constraints oder
nachträgliche Foreign-Key-Erweiterungen nur eingeschränkt unterstützt.

### Globale Einstellung

`PRAGMA foreign_keys = ON;` ist in `0001_schema.sql` gesetzt. Das
Dokument weist ausdrücklich darauf hin, dass daraus allein nicht
verifizierbar ist, ob der Anwendungscode diese Einstellung bei jeder
Verbindung erneut aktiviert.

## Kapitel 8: Backup und Restore

### Einordnung

Der Bereich Backup und Restore ist im Repository als eigenständiger
Betriebsdokumentationsbereich vorhanden und gehört damit zum
dokumentierten Gesamtprojekt.

### Quellbasis und Geltungsbereich

Für diesen Themenblock ist die Datei
`docs/04_betrieb/handbuch_backup_restore.md` die belegte Dokumentquelle;
zusätzlich ist im Verzeichnis `docs/04_betrieb/` ein weiterer
Betriebskontext mit Checklisten, Automatisierungs- und
Freigabedokumenten vorhanden.

### Fachlicher Status

Aus den bereits eingelesenen Handbuchteilen ist sicher belegt, dass das
Projekt einen manuellen Backup-Befehl `system backup` über die Admin-CLI
besitzt, dass der Backup-Dienst Zielverzeichnis und optionalen NAS-Pfad
aus `system_config` liest und dass bei einem Fehlschlag der
NAS-Synchronisation das lokale Backup bereits erfolgreich erstellt ist.

Die detaillierte Ablaufbeschreibung für Restore, Prüfschritte nach
Wiederherstellung und betriebliche Freigabeschritte ist als
Repository-Dokument vorhanden, wurde in diesem Schritt aber nicht Zeile
für Zeile neu extrahiert. Deshalb wird dieser Kapitelblock hier bewusst
nur in dem Umfang aufgenommen, der durch die bereits belegten Quellen
eindeutig gestützt ist.

## Kapitel 9: Audit und Prüfstatus

### Sicher belegt

Sicher belegt sind laut bestehendem Handbuch die Schichtenstruktur, die
SQLite-Basis, das Vorhandensein von Terminal-UI und Admin-CLI sowie die
modulare Handbuchstruktur des Projekts.

### Nicht überbehaupten

Das Audit-Kapitel weist darauf hin, dass technische Aussagen nur dann in
das Handbuch aufgenommen werden dürfen, wenn sie durch Repository-Inhalte
eindeutig gedeckt sind.

### Empfohlene nächste Prüfungen

Das bestehende Audit-Dokument empfiehlt weiterführende Prüfungen für
Bereiche, die nicht allein aus der bereits konsolidierten Handbuchbasis
ableitbar sind.

## Kapitel 10: Konfigurationsdiagnose

### Zweck

`scripts/show_config.py` dient zur Anzeige der Laufzeitkonfiguration des
Systems. Das Skript kann Werte aus einer `config.toml` sowie Einträge aus
der Datenbanktabelle `system_config` lesen und auf der Konsole oder als
JSON ausgeben.

Das Skript ist ein reines Lesewerkzeug; schreibende Datenbankoperationen
oder Änderungen an `config.toml` sind darin nicht implementiert.

### Aufruf

```bash
python scripts/show_config.py --db <DB_PATH> [--config <CONFIG_PATH>] [--all-versions] [--json]
```

Das Argument `--db` ist zwingend erforderlich. Fehlt die Datenbankdatei,
bricht das Skript mit Fehlermeldung auf `stderr` und Exit-Code 1 ab.

### Optionen

| Option | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--db DB_PATH` | Pfad | ja | Pfad zur SQLite-Datenbankdatei |
| `--config CONFIG_PATH` | Pfad | nein | Pfad zu `config.toml`; ohne Angabe automatische Suche |
| `--all-versions` | Flag | nein | Alle Versionen pro Schlüssel anzeigen |
| `--json` | Flag | nein | Ausgabe als JSON statt als Text |

### Datenquellen

Das Skript verwendet zwei getrennte Datenquellen: `config.toml` und die
Tabelle `system_config` der angegebenen SQLite-Datenbank.

Die automatische Suche nach `config.toml` erfolgt über `find_config()`
aus `arbeitszeit.infrastructure.config_file`.

### Abfrage der Datenbank

Für die Datenbankausgabe sind zwei Abfragepfade implementiert:
`_current_config(db)` für den jeweils aktuellen Stand pro Schlüssel und
`_all_versions(db)` für alle Versionen.

Gelesen werden die Spalten `config_key`, `config_value_json`, `version`,
`change_origin`, `changed_by_user_id`, `changed_at` und `reason`.

### Anzeige von `config.toml`

Die Ausgabe der TOML-Konfiguration erfolgt über `_print_config_toml()`.

Im Quellcode sind folgende ausgabefähige Felder belegt:

- `database.path`
- `terminal.id`
- `terminal.numpad`
- `terminal.rfid`
- `backup.backup_dir`
- `backup.export_dir`
- `backup.log_dir`
- `admin.user_id`

### Textausgabe

Ohne `--json` erzeugt das Skript eine zweigeteilte Textausgabe mit einem
Abschnitt für `config.toml` und einem Abschnitt für die
Datenbankeinträge aus `system_config`.

Die Tabellenansicht der Datenbankwerte enthält die Spalten `Schlüssel`,
`Wert`, `Ver`, `Herkunft` und `Geändert am`.

### JSON-Ausgabe

Mit `--json` gibt das Skript ein JSON-Objekt auf `stdout` aus. Das
Objekt enthält mindestens den Schlüssel `db`; bei erfolgreichem Laden
einer `config.toml` zusätzlich `config_toml`.

### Wertdekodierung

Für die Tabellenansicht dekodiert `_decode_value()` die Werte aus
`config_value_json` per `json.loads()`. JSON-`null` wird als
`(nicht gesetzt)` ausgegeben.

### Abhängigkeiten

Das Skript verwendet die Standardbibliothek `argparse`, `json`, `sys`
und `pathlib` sowie die Module
`arbeitszeit.infrastructure.config_file.find_config`,
`arbeitszeit.infrastructure.config_file.load_config` und
`arbeitszeit.infrastructure.db.connection.open_connection`.

### Abgrenzung

`scripts/show_config.py` ist ein Diagnose- und Prüfwerkzeug. Für die
Einrichtung und Pflege der Konfigurationsdatei verweist das Dokument auf
`scripts/setup.py`; für Buchungsbetrieb und Administration existieren
getrennte Einstiegspunkte in `presentation/terminal_ui/` und
`presentation/admin_cli/`.

---

**Versionsvermerk**  
Vorversion: 1.5  
Neue Version: 1.6  
Begründung: Evidenzbasierte Ergänzung des bestehenden Gesamthandbuchs um
weitere im Repository separat vorhandene und fachlich einschlägige
Dokumentationsbereiche, ohne grundlegenden Strukturwechsel.
