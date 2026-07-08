# Handbuch `arbeitszeit`

**Version:** 1.4
**Stand:** Juli 2026
**Projekt:** Lokales Zeiterfassungssystem für eine Zahnarztpraxis

Dieses Handbuch fasst alle sieben Kapiteldateien des Projekts `arbeitszeit` in
einem einzigen, durchgängig lesbaren Dokument zusammen. Jedes Kapitel ist
vollständig und unverändert aus der jeweiligen Quelldatei übernommen; es
wurde lediglich die Überschriftenhierarchie um eine Ebene verschoben, damit
sich alle Kapitel konsistent unter den Kapitel-Überschriften einordnen.

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
  - [Terminal-UI (`terminal_ui/`)](#terminal-ui-terminalui)
  - [Admin-CLI (`admin_cli/`)](#admin-cli-admincli)
  - [Domain: `employees` und `cards`](#domain-employees-und-cards)
  - [Domain: `bookings`](#domain-bookings)
  - [Domain: `schedule`](#domain-schedule)
  - [Domain: `reports`](#domain-reports)
  - [Domain: `system`](#domain-system)
  - [Domain: `users`](#domain-users)
  - [Zeitraum-Hilfsfunktionen (`_intervals.py`)](#zeitraum-hilfsfunktionen-intervalspy)
- [Kapitel 4: Anwendungsschicht](#kapitel-4-anwendungsschicht)
  - [4.1 Überblick und Einordnung](#41-überblick-und-einordnung)
  - [4.2 Commands — Eingabe-DTOs (`commands.py`)](#42-commands-eingabe-dtos-commandspy)
  - [4.3 Results — Ausgabe-DTOs schreibender Operationen (`results.py`)](#43-results-ausgabe-dtos-schreibender-operationen-resultspy)
  - [4.4 Queries — Lesende Abfrage-DTOs (`queries.py`)](#44-queries-lesende-abfrage-dtos-queriespy)
  - [4.5 Unit of Work — Transaktionsprotokoll (`unit_of_work.py`)](#45-unit-of-work-transaktionsprotokoll-unitofworkpy)
  - [4.6 Use Cases im Detail](#46-use-cases-im-detail)
  - [4.7 Querschnittliche Entwurfsprinzipien](#47-querschnittliche-entwurfsprinzipien)
  - [4.8 Erweiterungshinweise](#48-erweiterungshinweise)
  - [4.9 Hinweis zu admin-CLI-Befehlen](#49-hinweis-zu-admin-cli-befehlen)
- [Kapitel 5: Domain-Modell](#kapitel-5-domain-modell)
  - [Überblick und Designprinzip](#überblick-und-designprinzip)
  - [Value Objects – Starke ID-Typen](#value-objects-starke-id-typen)
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
  - [Backup (`backup/backup_service.py`)](#backup-backupbackupservicepy)
  - [Systemüberwachung](#systemüberwachung)
  - [Querverbindungen und Architekturprinzipien](#querverbindungen-und-architekturprinzipien)
- [Kapitel 7: Audit und Prüfstatus](#kapitel-7-audit-und-prüfstatus)
  - [Sicher belegt](#sicher-belegt)
  - [Nicht überbehaupten](#nicht-überbehaupten)
  - [Empfohlene nächste Prüfungen](#empfohlene-nächste-prüfungen)

## Kapitel 1: Übersicht

**Quelle:** `handbuch_overview.md`

### Zweck

`arbeitszeit` ist ein lokal betriebenes Zeiterfassungssystem für eine
Zahnarztpraxis. Die Anwendung verwendet SQLite als einzige Datenbank und trennt
Fachlogik, Infrastruktur und Benutzeroberflächen klar voneinander.

Aus dem Repository eindeutig belegt sind ein Terminalmodus für den operativen
Buchungsbetrieb sowie eine Admin-CLI für
Verwaltungsaufgaben.

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

---

## Kapitel 2: Installation

**Quelle:** `handbuch_installation.md`

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

RFID-Karte zuweisen:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  --user-id 1 \
  cards assign \
  --employee-id 1 \
  --uid-hash <HASH>
```

### Funktionstest

```bash
pytest
pytest tests/test_migrations.py
pytest --cov=arbeitszeit
```

---

## Kapitel 3: Präsentationsschicht

**Quelle:** `handbuch_presentation.md`

### Überblick und Aufbau

Die Präsentationsschicht ist die äußerste Schale des Systems und bildet
die einzige Schnittstelle zwischen Benutzer (oder Administrator) und der
darunterliegenden Fach- und Anwendungslogik. Sie enthält keine
Geschäftslogik, sondern übersetzt ausschließlich Benutzereingaben in
Kommandos der Anwendungsschicht und gibt Ergebnisse als lesbare Texte
aus. Das Paket gliedert sich in zwei eigenständige Untermodule:

- `presentation/terminal_ui/` – operativer Buchungsbetrieb (Endlosschleife, RFID + Numpad)
- `presentation/admin_cli/` – administrative Verwaltung (Kommandozeile, rollenbasiert)

---

### Terminal-UI (`terminal_ui/`)

#### Zweck und Betriebsmodus

Die Terminal-UI ist der im laufenden Praxisbetrieb aktive Prozess. Sie
startet beim Systemstart als Endlosschleife und wartet kontinuierlich auf
Hardware-Eingaben: zuerst Auswahl der Buchungsart über das Numpad, dann
RFID-Kartenscan. Der Prozess reagiert auf `SIGTERM` und `SIGINT`
(Strg+C) mit einem sauberen Graceful Shutdown.

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
aber der Buchungsbetrieb wird **nicht** abgebrochen — die Praxis soll
arbeitsfähig bleiben. Fehlerdetails werden in der Tabelle
`system_events` gespeichert.

#### Buchungszyklus (`booking_loop.py`)

Jeder Buchungszyklus läuft in drei Schritten ab:

1. **Numpad-Eingabe:** Der Mitarbeiter wählt die Buchungsart (Kommen,
   Gehen, Pause-Start, Pause-Ende) über das USB-Numpad.
2. **RFID-Scan:** Das System wartet auf den Kartenscan. Das Timeout ist
   konfigurierbar über `booking.grace_seconds_after_numpad_select` in
   `system_config` (Standardwert: 5 Sekunden).
3. **Buchungsverarbeitung:** Das Geräteereignis (`RFID_SCAN`) wird
   **vor** dem eigentlichen `BookUseCase`-Aufruf in `device_events`
   gespeichert — absichtlich, damit auch fachlich gescheiterte Buchungen
   (z. B. unbekannte Karte) lückenlos protokolliert bleiben.

#### Feedback-Ausgabe

Nach jeder Buchung gibt das Terminal eine einzeilige Rückmeldung aus.

| Status | Ausgabe |
| --- | --- |
| `OPEN` / `OK` | `Buchung erfasst.` |
| `WARN` | `Buchung erfasst — Hinweis: Regelzeitabweichung festgestellt.` |
| `NEEDS_REVIEW` | `Buchung erfasst — Prüfpflicht: Manuelle Überprüfung erforderlich.` |

#### Domänenfehler-Behandlung

Bekannte Domänenfehler werden in menschenlesbare Meldungen übersetzt und
ausgegeben, ohne den Prozess zu beenden:

| Fehlerklasse | Anzeige |
| --- | --- |
| `UnknownCardError` | `Karte nicht erkannt.` |
| `InactiveCardError` | `Karte deaktiviert.` |
| `InactiveEmployeeError` | `Mitarbeiter inaktiv.` |
| `InvalidBookingSequenceError` | `Ungültige Buchungsreihenfolge.` |
| `OpenPhaseConflictError` | `Offene Phase — bitte zuerst abschließen.` |

Unerwartete Ausnahmen werden in `system_events` protokolliert; der
Betrieb läuft weiter.

---

### Admin-CLI (`admin_cli/`)

#### Zweck

Die Admin-CLI ist das Verwaltungswerkzeug für Administratoren und
technisches Personal. Sie wird als `admin`-Programm gestartet, erfordert
immer die Datenbankdatei (`--db`) und eine Benutzer-ID (`--user-id`
oder Umgebungsvariable `ADMIN_USER_ID`), und verteilt alle Aufrufe über
eine zentrale Dispatch-Tabelle an spezialisierte Handler-Module.

#### Grundaufruf

```bash
admin --db /pfad/zur/datenbank.db --user-id 1 <domain> <subcommand> [optionen]
```

Alternativ zur `--user-id`-Option kann die Umgebungsvariable
`ADMIN_USER_ID` gesetzt werden. Die einzige Ausnahme ist
`users bootstrap` — dieser Befehl benötigt keine Benutzer-ID, da noch
kein Admin existiert.

#### Rollenmodell

Alle schreibenden Operationen prüfen die Rolle des aufrufenden Benutzers
direkt gegen die Tabelle `user_accounts`. Es gibt drei Rollen:

| Rolle | Erlaubte Bereiche |
| --- | --- |
| `ADMIN` | Alle Operationen (Lesen + Schreiben) |
| `REVIEWER` | Berichte, Buchungsüberprüfung, Nachträge genehmigen/ablehnen |
| `TECH` | Systemcheck, Backup |

Lesende Operationen (z. B. `employees list`, `users list`) sind ohne
Rolleneinschränkung nutzbar.

---

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
| `cards assign --employee-id … --uid-hash …` | Neue RFID-Karte einem Mitarbeiter zuweisen | `ADMIN` |
| `cards replace --old-card-id … --uid-hash …` | Verlorene/defekte Karte ersetzen (alte Karte erhält Status `REPLACED`) | `ADMIN` |
| `cards deactivate <id>` | Karte auf Status `INACTIVE` setzen | `ADMIN` |

Jede schreibende Operation wird mit einem `_audit(…)`-Eintrag in
`audit_log` protokolliert. Verwendete Ereignistypen:
`EMPLOYEE_CREATED`, `EMPLOYEE_DEACTIVATED`, `CARD_ASSIGNED`,
`CARD_REPLACED`, `CARD_DEACTIVATED`.

---

### Domain: `bookings`

Buchungskorrekturen und Nachträge laufen vollständig über Use Cases der
Anwendungsschicht — die Rollenprüfung erfolgt dort, die CLI übernimmt
nur Fehlerformatierung und Ausgabe.

| Befehl | Beschreibung |
| --- | --- |
| `bookings correct --booking-id … --type … --at … --reason …` | Bestehende Buchung korrigieren; erzeugt einen neuen Korrektur-Datensatz und setzt die alte Buchung auf `CORRECTED` |
| `bookings supplement --employee-id … --type … --at … --reason …` | Nachträgliche Buchung erfassen; erzeugt automatisch einen Prüffall (`review_case`) |
| `bookings approve-supplement --supplement-id …` | Nachtrag freigeben → Buchung wird wirksam |
| `bookings reject-supplement --supplement-id … --reason …` | Nachtrag ablehnen |

Das `--at`-Argument erwartet ISO-8601-Format (z. B.
`2026-07-01T08:00:00`). Fehlt die Zeitzone, wird UTC angenommen.

---

### Domain: `schedule`

Die Regelarbeitszeit wird versioniert gespeichert; jede Änderung erzeugt
eine neue Version und schließt die Vorgängerversion.

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `schedule set --weekday 1-7 --start HH:MM --end HH:MM --from YYYY-MM-DD [--employee-id ID]` | Regelarbeitszeit setzen — global oder mitarbeiterspezifisch | `ADMIN` ¹ |
| `schedule show` | Alle aktiven Versionen anzeigen (global + mitarbeiterspezifisch) | `ADMIN`, `REVIEWER` |

¹ Ohne `--employee-id` wird eine globale Version (`ScopeType.GLOBAL`) gesetzt; mit
`--employee-id` eine mitarbeiterspezifische Ausnahme (`ScopeType.EMPLOYEE`). Die
`ADMIN`-Prüfung erfolgt im `ManageWorkScheduleUseCase` (Anwendungsschicht), nicht
in der CLI. `schedule show` prüft die Rolle direkt in der CLI (`_require_admin_or_reviewer`).

---

### Domain: `reports`

Alle Report-Befehle erfordern `ADMIN`- oder `REVIEWER`-Rolle. Das
Export-Verzeichnis wird aus `system_config` (Schlüssel
`export.export_dir`) gelesen.

#### Export-Befehle

| Befehl | Beschreibung |
| --- | --- |
| `reports export-csv --from … --to … [--employee-id …]` | Zwei CSV-Dateien: Detailbuchungen + verdichtete Übersicht |
| `reports export-pdf-day --date YYYY-MM-DD` | Tagesbericht als PDF |
| `reports export-pdf-week --year YYYY --week WW` | Wochenbericht (ISO-Woche) als PDF |
| `reports export-pdf-month --year YYYY --month MM` | Monatsbericht als PDF |
| `reports export-pdf-employee --employee-id … --from … --to …` | Mitarbeiterbericht als PDF |
| `reports export-csv-review-cases --from … --to … [--employee-id …]` | Offene Prüffälle als CSV exportieren |

#### Pflichtauswertungen

| Befehl | Beschreibung |
| --- | --- |
| `reports open-bookings [--from … --to …] [--employee-id …]` | Buchungen mit Status `OPEN` ¹ |
| `reports warn-cases --from … --to … [--employee-id …]` | Buchungen mit Status `WARN` oder `NEEDS_REVIEW` |
| `reports corrections --from … --to … [--employee-id …]` | Alle Korrekturen im Zeitraum |
| `reports supplements --from … --to … [--employee-id …]` | Alle Nachträge im Zeitraum |
| `reports open-review-cases [--from … --to …] [--employee-id …]` | Offene Prüffälle ¹ |

¹ Wird `--from`/`--to` weggelassen und liefert die Abfrage mehr als 50
Einträge, erscheint ein Hinweis auf stderr, den Zeitraum einzugrenzen.

---

### Domain: `system`

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `system check` | Systemcheck auslösen; gibt Detailstatus aller Prüfpunkte aus; Exitcode 0 = OK, 1 = Fehler | `ADMIN`, `TECH` |
| `system backup` | Manuelles Backup der SQLite-Datenbank auslösen; bei aktivierter NAS-Synchronisation (`backup.nas_enabled`) wird das Backup auch auf den NAS-Pfad kopiert | `ADMIN`, `TECH` |

Der Backup-Dienst liest Zielverzeichnis und NAS-Pfad aus `system_config`.
Schlägt die NAS-Synchronisation fehl, endet der Prozess mit Exitcode 1 —
das lokale Backup ist zu diesem Zeitpunkt bereits erfolgreich erstellt.

---

### Domain: `users`

Passwörter werden mit PBKDF2-HMAC-SHA256 und 260.000 Iterationen gehasht
(DSGVO Art. 32). Das Klartextpasswort wird nach der Ausgabe nirgends
gespeichert.

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `users bootstrap --username … [--password …]` | Erstes Administratorkonto anlegen (nur wenn noch kein aktiver Admin existiert) | — |
| `users add --username … --role … [--employee-id …] [--password …]` | Neues Benutzerkonto anlegen | `ADMIN` |
| `users list` | Alle Konten tabellarisch auflisten | keine |
| `users deactivate --user-id …` | Benutzerkonto deaktivieren | `ADMIN` |
| `users reactivate --user-id …` | Benutzerkonto reaktivieren | `ADMIN` |
| `users change-role --user-id … --role …` | Rolle eines Kontos ändern | `ADMIN` |

Wird `--password` weggelassen, generiert das System ein sicheres
zufälliges Passwort und zeigt es **einmalig** auf der Konsole an.

---

### Zeitraum-Hilfsfunktionen (`_intervals.py`)

Alle Datums-/Zeitraumberechnungen in der Admin-CLI verwenden ausschließlich
die drei Funktionen aus
`src/arbeitszeit/presentation/admin_cli/_intervals.py`. Eigene
Ad-hoc-Konstruktionen aus Benutzereingaben sind verboten, um
UTC-Normalisierung und halboffene Intervalle `[from_dt, to_dt)`
sicherzustellen.

| Funktion | Beschreibung |
| --- | --- |
| `day_interval(day)` | `[day 00:00 UTC, next_day 00:00 UTC)` |
| `week_interval(year, week)` | ISO-Woche: Montag 00:00 UTC bis Montag+7 00:00 UTC |
| `month_interval(year, month)` | Erster bis (exklusiv) erster des Folgemonats, UTC |

---

## Kapitel 4: Anwendungsschicht

**Quelle:** `handbuch_application_layer.md`

Die Anwendungsschicht ist das Herzstück der fachlichen Steuerung. Sie vermittelt
zwischen der Präsentationsschicht (UI, Terminal-Handler) und der Domänenschicht
(Geschäftsregeln, Entitäten). Sie enthält **keine** SQL-Logik, **keine**
Hardware-Zugriffe und **keine** UI-Elemente — ausschließlich Ablaufsteuerung,
Validierung und Koordination.

---

### 4.1 Überblick und Einordnung

Das Paket folgt dem **CQRS-Prinzip** (Command Query Responsibility Segregation):
Schreibende Operationen werden über *Commands* und *Use Cases* gesteuert,
lesende Operationen über *Query-DTOs*. Beide Seiten sind strikt getrennt,
sodass sie unabhängig voneinander weiterentwickelt und getestet werden können.

```text
src/arbeitszeit/application/
├── __init__.py            # leer — kein impliziter Re-Export
├── commands.py            # Eingabe-DTOs für alle schreibenden Operationen
├── queries.py             # Ausgabe-DTOs für lesende Abfragen (CQRS-Read)
├── results.py             # Ausgabe-DTOs für schreibende Operationen
├── unit_of_work.py        # Transaktion-Protokoll (Protocol-Klasse)
└── use_cases/
    ├── __init__.py
    ├── approve_supplement.py   # Nachtrag freigeben → erzeugt Buchung
    ├── book_time.py            # Buchung via RFID-Terminal
    ├── correct_booking.py      # Manuelle Korrektur durch Admin/Reviewer
    ├── manage_employees.py     # Mitarbeiter anlegen/deaktivieren
    ├── manage_rfid_cards.py    # RFID-Karten zuweisen/ersetzen/deaktivieren
    ├── manage_user_accounts.py # Benutzerkonten verwalten / Bootstrap-Admin
    ├── manage_work_schedule.py # Regelarbeitszeit ändern
    ├── register_supplement.py  # Nachtrag erfassen (Status: PENDING)
    └── reject_supplement.py    # Nachtrag ablehnen
```

---

### 4.2 Commands — Eingabe-DTOs (`commands.py`)

Commands sind **unveränderliche Datenbehälter** (`frozen=True, slots=True`),
die alle für eine Operation notwendigen Parameter bündeln. Sie enthalten keine
Logik. Die Use Cases konsumieren Commands als einzigen Eingabeparameter.

| Command-Klasse | Zweck |
|---|---|
| `BookCommand` | RFID-Buchung vom Terminal (Kommen/Gehen/Pause) |
| `CreateSupplementCommand` | Nachtrag durch Admin/Reviewer erfassen |
| `CreateCorrectionCommand` | Bestehende Buchung korrigieren |
| `ApproveSupplementCommand` | Nachtrag genehmigen |
| `RejectSupplementCommand` | Nachtrag ablehnen (mit Begründung) |
| `ChangeWorkScheduleCommand` | Regelarbeitszeit für Wochentag/Scope setzen |
| `CreateEmployeeCommand` | Mitarbeiter anlegen (ADMIN) |
| `DeactivateEmployeeCommand` | Mitarbeiter deaktivieren (ADMIN) |
| `AssignRfidCardCommand` | RFID-Karte einem Mitarbeiter zuweisen (ADMIN) |
| `ReplaceRfidCardCommand` | RFID-Karte ersetzen (ADMIN) |
| `DeactivateRfidCardCommand` | RFID-Karte deaktivieren (ADMIN) |
| `CreateUserAccountCommand` | Benutzerkonto anlegen (ADMIN) |
| `DeactivateUserAccountCommand` | Benutzerkonto deaktivieren (ADMIN) |
| `ReactivateUserAccountCommand` | Benutzerkonto reaktivieren (ADMIN) |
| `ChangeUserRoleCommand` | Rolle eines Benutzerkontos ändern (ADMIN) |
| `BootstrapAdminCommand` | Ersten Admin-Account anlegen (kein Actor erforderlich) |

Alle Commands importieren ihre Value-Object-Typen (z. B. `EmployeeId`,
`TerminalId`) aus `arbeitszeit.domain.value_objects`, um Typsicherheit
ohne Primitive Obsession zu gewährleisten.

---

### 4.3 Results — Ausgabe-DTOs schreibender Operationen (`results.py`)

Jeder Use Case gibt ein typisiertes Result-Objekt zurück. Results sind ebenfalls
`frozen` und `slots`-optimiert. Sie enthalten nur die IDs und Status-Werte, die
die Präsentationsschicht für Rückmeldungen oder Folgeverarbeitungen benötigt.

| Result-Klasse | Enthaltene Felder |
|---|---|
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

Void-Use-Cases (Deactivate/Reactivate/ChangeRole) geben `None` zurück — kein
eigenes Result-Objekt, da die Präsentationsschicht keine Rückgabedaten benötigt.

---

### 4.4 Queries — Lesende Abfrage-DTOs (`queries.py`)

Die Query-DTOs bilden die CQRS-Leseseite ab. Sie definieren die Zeilenstruktur
für Berichte und Listen, ohne selbst SQL auszuführen. Die eigentlichen
Datenbankabfragen liegen in der Infrastrukturschicht
(`infrastructure/export/report_queries.py`).

| Row-Klasse | Verwendungszweck |
|---|---|
| `BookingRow` | Buchungsliste mit Mitarbeiterzuordnung für Berichte |
| `CorrectionRow` | Korrekturprotokoll mit altem und neuem Zustand (interne Referenz auf Regelwerk v3 §12) |
| `SupplementRow` | Nachtragsliste mit Freigabestatus (interne Referenz auf Regelwerk v3 §13/§19) |
| `ReviewCaseRow` | Offene oder aktive Prüffälle (interne Referenz auf Pflichtenheft v3 §7.6/§7.12) |

Die Trennung von Command- und Query-Typen stellt sicher, dass
Präsentationsmodule **keine** Infrastruktur-Klassen importieren müssen.

---

### 4.5 Unit of Work — Transaktionsprotokoll (`unit_of_work.py`)

`UnitOfWork` ist ein **Protocol** (strukturelles Typing, kein Erben nötig).
Es fasst alle Repository-Referenzen unter einem gemeinsamen Transaktionskontext
zusammen und garantiert atomare Schreiboperationen.

```python
with self._uow:
    # Alle Lese- und Schreiboperationen hier
    self._uow.commit()
```

Die in `UnitOfWork` definierten Repositories:

- `employee_repo` — Mitarbeiterstammdaten
- `user_account_repo` — Benutzerkonten (mit Rollen)
- `rfid_card_repo` — RFID-Karten und deren Status
- `time_booking_repo` — Zeitbuchungen (Kommen/Gehen/Pause)
- `work_schedule_repo` — Regelarbeitszeitversionen
- `review_case_repo` — Prüffälle
- `supplement_repo` — Nachträge
- `booking_correction_repo` — Buchungskorrekturen
- `audit_log_repo` — Unveränderliches Audit-Protokoll
- `system_config_repo` — Systemeinstellungen
- `device_event_repo` — Geräteereignisse (Terminal, Numpad)

> **Wichtig:** Das Audit-Log wird nach `commit()` geschrieben (nicht davor).
> Diese Reihenfolge ist im Anwendungscode durchgängig umgesetzt. Details zur
> konkreten Verbindungs- und Transaktionsimplementierung liegen in der
> Infrastrukturschicht.

---

### 4.6 Use Cases im Detail

#### 4.6.1 `BookUseCase` — Terminalbuchung (`book_time.py`)

Dieser Use Case verarbeitet jede RFID-Buchung vom Terminal. Er ist der am
häufigsten ausgeführte Use Case im Tagesbetrieb.

**Ablauf:**

1. RFID-Karte per `uid_hash` nachschlagen
2. Bei unbekannter Karte → Audit-Eintrag `BOOKING_REJECTED_UNKNOWN_CARD` + `UnknownCardError`
3. Bei inaktiver Karte → Audit-Eintrag `BOOKING_REJECTED_INACTIVE_CARD` + `InactiveCardError`
4. Mitarbeiter laden und Aktivstatus prüfen
5. Tagesbuchungen laden, Buchungsreihenfolge validieren (`validate_booking_sequence`)
6. Regelarbeitszeit prüfen → ggf. `ComplianceFlag(OUTSIDE_SCHEDULE_WINDOW, WARN)` setzen
7. Compliance-Checks durchführen: Pausenpflicht, Höchstarbeitszeit, Ruhezeit
8. Buchung speichern mit berechnetem Status (`OPEN` / `OK` / `WARN` / `NEEDS_REVIEW`)
9. Prüffälle für jeden `ComplianceFlag` anlegen
10. `commit()` → Audit-Log `TIME_BOOKED` schreiben
11. `BookResult` zurückgeben

**Statuslogik der Buchung:**

| Status | Bedingung |
|---|---|
| `OPEN` | Buchungstyp ist `COME` oder `BREAK_START` |
| `OK` | Keine Compliance-Verstöße |
| `WARN` | Mindestens ein Flag ohne `CRITICAL`-Schwere |
| `NEEDS_REVIEW` | Mindestens ein Flag mit `CRITICAL`-Schwere |

**Ablehnungspfade und SQLite-Locks:**

In den Ablehnungspfaden (unbekannte/inaktive Karte) darf vor dem
Audit-Log-Schreibvorgang **keine** andere Schreiboperation auf der
Hauptverbindung stattgefunden haben. Nur SELECTs sind vor dem ersten
Audit-Write erlaubt. Diese Invariante muss bei Erweiterungen gewahrt bleiben.

---

#### 4.6.2 `CorrectBookingUseCase` — Buchungskorrektur (`correct_booking.py`)

Ermöglicht berechtigten Benutzern (Rolle `ADMIN` oder `REVIEWER`), eine
bestehende Buchung nachträglich zu ändern.

**Ablauf:**

1. Berechtigungsprüfung des handelnden Benutzers
2. Originalbuchung und zugehörigen Mitarbeiter laden
3. `BookingCorrection`-Datensatz anlegen (Vorher/Nachher-Snapshot)
4. Status der Originalbuchung auf `CORRECTED` setzen
5. Offene Prüffälle des Mitarbeiters durchsuchen:
   - Prüffälle mit `booking_id == original` und korrigierbarem Typ → Status `RESOLVED`
6. `commit()` → Audit-Log `BOOKING_CORRECTED` schreiben
7. `CorrectionResult` zurückgeben

**Korrigierbare Prüffalltypen** (`_CORRECTABLE_CASE_TYPES`):
`OPEN_WORK_PHASE`, `OPEN_BREAK_PHASE`, `IMPLAUSIBLE_SEQUENCE`,
`POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`,
`POSSIBLE_MAX_HOURS_VIOLATION`, `OUTSIDE_SCHEDULE_WINDOW`.

Nicht durch Buchungskorrektur schließbar: `MANUAL_ENTRY_REVIEW`,
`UNKNOWN_CARD_ATTEMPT`, `INACTIVE_CARD_ATTEMPT`, `TIME_ANOMALY`.

---

#### 4.6.3 `RegisterSupplementUseCase` — Nachtrag erfassen (`register_supplement.py`)

Erfasst eine nachträglich einzutragende Buchung (z. B. vergessenes Einstempeln).
Der Nachtrag wird zunächst im Status `PENDING` angelegt — er erzeugt noch
**keine** Buchung in `time_bookings`.

**Ablauf:**

1. Berechtigungsprüfung (`ADMIN` oder `REVIEWER`)
2. Mitarbeiter laden und Aktivstatus prüfen
3. Falls `related_booking_id` angegeben: Existenz der Originalbuchung sicherstellen
4. `Supplement`-Datensatz mit Status `PENDING` anlegen
5. Prüffall `MANUAL_ENTRY_REVIEW` (Schwere `INFO`) anlegen
6. `commit()` → Audit-Log `SUPPLEMENT_CREATED` schreiben
7. `SupplementResult` zurückgeben

---

#### 4.6.4 `ApproveSupplementUseCase` — Nachtrag freigeben (`approve_supplement.py`)

Genehmigt einen ausstehenden Nachtrag und überführt ihn in eine echte
Buchung mit vollständiger Compliance-Prüfung.

**Ablauf:**

1. Berechtigungsprüfung (`ADMIN` oder `REVIEWER`)
2. Nachtrag laden, Status muss `PENDING` sein (sonst `ValidationError`)
3. Mitarbeiter laden und prüfen
4. Nachtrag in `approved` überführen (`supplement_repo.approve`)
5. Zugehörigen Prüffall `MANUAL_ENTRY_REVIEW` auf `RESOLVED` schließen
6. Buchungsreihenfolge validieren (wie bei Terminal-Buchung)
7. Regelarbeitszeit und Compliance-Checks durchführen
8. Neue `TimeBooking` mit Source `MANUAL` anlegen
9. Folge-Prüffälle aus Compliance-Flags anlegen
10. `commit()` → Audit-Log `SUPPLEMENT_APPROVED` schreiben
11. `ApproveSupplementResult` zurückgeben

---

#### 4.6.5 `RejectSupplementUseCase` — Nachtrag ablehnen (`reject_supplement.py`)

Lehnt einen ausstehenden Nachtrag ab, ohne eine Buchung zu erzeugen.

**Ablauf:**

1. Berechtigungsprüfung (`ADMIN` oder `REVIEWER`)
2. Nachtrag laden, Status muss `PENDING` sein
3. Nachtrag auf `rejected` setzen (`supplement_repo.reject`)
4. Ggf. zugehörigen Prüffall `MANUAL_ENTRY_REVIEW` mit Status
   `CLOSED_WITH_NOTE` und der Ablehnungsbegründung schließen
5. `commit()` → Audit-Log `SUPPLEMENT_REJECTED` schreiben
6. `RejectSupplementResult` zurückgeben

---

#### 4.6.6 `ManageWorkScheduleUseCase` — Regelarbeitszeit (`manage_work_schedule.py`)

Ändert die Regelarbeitszeit für einen Wochentag, entweder global (alle
Mitarbeiter) oder mitarbeiterspezifisch. Nur Benutzer mit Rolle `ADMIN`
dürfen diesen Use Case ausführen.

**Ablauf:**

1. Berechtigungsprüfung (`ADMIN` — strikt, kein `REVIEWER`)
2. Aktuell gültige Version für Wochentag/Scope laden
3. Konfliktprüfung: existiert bereits eine Version mit gleichem `valid_from`
   → `ConflictError`
4. Rückwärtseinfüge-Schutz: existiert eine spätere Version → `ValidationError`
5. Aktuelle Version schließen (`valid_until = valid_from - 1 Tag`)
6. Neue `WorkScheduleVersion` anlegen
7. `commit()` → Audit-Log `WORK_SCHEDULE_CHANGED` schreiben
   (enthält Vorher/Nachher-Snapshot)
8. `WorkScheduleChangeResult` zurückgeben

---

#### 4.6.7 Mitarbeiterverwaltung (`manage_employees.py`)

Beide Use Cases erfordern `ADMIN`-Rolle.

**`CreateEmployeeUseCase`**

1. Berechtigungsprüfung (`ADMIN`)
2. Duplikat-Personalnummer unter aktiven Mitarbeitern prüfen → `ConflictError`
3. `Employee`-Entität anlegen via `EmployeeRepository.add()`
4. `commit()` → Audit-Log `EMPLOYEE_CREATED` schreiben
5. `CreateEmployeeResult(employee_id)` zurückgeben

**`DeactivateEmployeeUseCase`**

1. Berechtigungsprüfung (`ADMIN`)
2. Existenz prüfen → `NotFoundError`
3. `EmployeeRepository.deactivate()` aufrufen
4. `commit()` → Audit-Log `EMPLOYEE_DEACTIVATED` schreiben

---

#### 4.6.8 RFID-Kartenverwaltung (`manage_rfid_cards.py`)

Alle drei Use Cases erfordern `ADMIN`-Rolle.

**`AssignRfidCardUseCase`**

1. Berechtigungsprüfung (`ADMIN`)
2. Mitarbeiter-Existenz prüfen → `NotFoundError`
3. UID-Duplikat prüfen → `ConflictError`
4. Neue `RfidCard` mit Status `ACTIVE` anlegen
5. `commit()` → Audit-Log `CARD_ASSIGNED` schreiben
6. `AssignRfidCardResult(card_id)` zurückgeben

**`ReplaceRfidCardUseCase`**

1. Berechtigungsprüfung (`ADMIN`)
2. Alte Karte laden → `NotFoundError`
3. UID-Duplikat prüfen → `ConflictError`
4. Neue `RfidCard` mit Status `ACTIVE` anlegen
5. Alte Karte auf `REPLACED` setzen (`replaced_by_card_id`, `valid_until = today`)
6. `commit()` → Audit-Log `CARD_REPLACED` schreiben
7. `ReplaceRfidCardResult(new_card_id)` zurückgeben

**`DeactivateRfidCardUseCase`**

1. Berechtigungsprüfung (`ADMIN`)
2. Karte laden → `NotFoundError`
3. Status auf `INACTIVE` setzen
4. `commit()` → Audit-Log `CARD_DEACTIVATED` schreiben

---

#### 4.6.9 Benutzerkontenverwaltung (`manage_user_accounts.py`)

**`CreateUserAccountUseCase`** (ADMIN)

1. Berechtigungsprüfung (`ADMIN`)
2. Rolle prüfen: nur `ADMIN`, `REVIEWER`, `TECH` erlaubt → `ValidationError`
3. Username-Duplikat prüfen → `ConflictError`
4. Konto anlegen via `UserAccountRepository.add(account, password_hash)`
5. `commit()` → Audit-Log `USER_ACCOUNT_CREATED` schreiben
6. `CreateUserAccountResult(user_id)` zurückgeben

**`DeactivateUserAccountUseCase`** / **`ReactivateUserAccountUseCase`** (ADMIN)

Je: Berechtigungsprüfung → Existenzprüfung → Statusänderung → `commit()` →
Audit-Log (`USER_ACCOUNT_DEACTIVATED` / `USER_ACCOUNT_REACTIVATED`).

**`ChangeUserRoleUseCase`** (ADMIN)

Prüft zusätzlich, dass die neue Rolle in der erlaubten Menge
`{ADMIN, REVIEWER, TECH}` liegt, andernfalls `ValidationError`.
Audit-Log `USER_ACCOUNT_ROLE_CHANGED` enthält alte und neue Rolle.

**`BootstrapAdminUseCase`** (kein Actor)

Sonderfall: kein `acting_user_id` im Command. Prüft via `has_active_admin()`,
ob bereits ein aktiver Admin existiert → `ConflictError`. Prüft zusätzlich,
ob der gewünschte Username bereits vergeben ist → `ConflictError`. Legt den
ersten Admin-Account an; im Audit-Log wird `USER_ACCOUNT_CREATED` mit
`user_id = saved.id` (Self-Reference) und dem Zusatzfeld `bootstrap: true`
verwendet. Gibt `BootstrapAdminResult(user_id, username)` zurück.

---

### 4.7 Querschnittliche Entwurfsprinzipien

#### Berechtigungsprüfung

Alle manuellen Use Cases prüfen zu Beginn die Benutzerrolle (via `get_by_id`
des handelnden Accounts) und werfen `PermissionDeniedError`, bevor sie auf
das jeweilige Zielobjekt zugreifen:

- `ADMIN` + `REVIEWER`: Korrektur, Nachtrag (erfassen/genehmigen/ablehnen)
- Nur `ADMIN`: Regelzeitänderung, Mitarbeiterverwaltung, Kartenverwaltung,
  Benutzerkontenverwaltung
- Kein Actor: `BootstrapAdminUseCase` (Existenzprüfung ersetzt Rollencheck)
- Kein Rollencheck: Terminal-Buchungen (`BookUseCase`) — die RFID-Karte ist
  das Authentifikationsmittel des Mitarbeiters

#### Audit-Log-Konsistenz

**Erfolgspfade:** Das Audit-Log wird nach dem `commit()` geschrieben.
Diese Reihenfolge ist eine bewusste Architekturentscheidung und im
Anwendungscode durchgängig umgesetzt.

**Ablehnungspfade (`BookUseCase`):** Die Ereignisse
`BOOKING_REJECTED_UNKNOWN_CARD` und `BOOKING_REJECTED_INACTIVE_CARD` werden
in Pfaden geschrieben, in denen vor dem Audit-Write keine andere
Schreiboperation auf der Hauptverbindung erfolgt.

#### Unveränderlichkeit der DTOs

Alle Commands und Results sind `@dataclass(frozen=True, slots=True)`.
`frozen=True` verhindert versehentliche Mutation nach der Erzeugung.
`slots=True` reduziert Speicherbedarf und beschleunigt Attributzugriffe.

#### Fehlertypen

| Fehlerklasse | Bedeutung |
|---|---|
| `PermissionDeniedError` | Fehlende Berechtigung der handelnden Person |
| `NotFoundError` | Entität (Mitarbeiter, Buchung, Nachtrag) nicht gefunden |
| `InactiveCardError` | RFID-Karte ist gesperrt oder deaktiviert |
| `InactiveEmployeeError` | Mitarbeiter ist nicht mehr aktiv |
| `UnknownCardError` | RFID-UID ist im System nicht registriert |
| `ValidationError` | Fachliche Verletzung (z. B. falscher Status) |
| `ConflictError` | Doppelter Eintrag (z. B. doppelte Regelzeitversion) |

---

### 4.8 Erweiterungshinweise

- **Neuer Use Case:** Neue Datei in `use_cases/`, entsprechendes Command in
  `commands.py` und Result in `results.py` ergänzen. `UnitOfWork` in
  `unit_of_work.py` nur erweitern, wenn ein neues Repository benötigt wird.
- **Neue Abfragesicht:** Neue `*Row`-Klasse in `queries.py` definieren;
  die SQL-Implementierung gehört in `infrastructure/export/report_queries.py`.
- **Compliance-Regel hinzufügen:** Neue Prüffunktion in
  `domain/services/compliance_checks.py`, dann in `_evaluate_booking()` der
  betroffenen Use Cases aufrufen.
- **Reihenfolge beim Audit-Log nie ändern:** Der Commit muss vor dem
  Audit-Log-Schreibvorgang erfolgen.

---

### 4.9 Hinweis zu admin-CLI-Befehlen

Eine vollständige Liste der über die Admin-CLI aufrufbaren Befehlsgruppen
(`employees`, `cards`, `bookings`, `schedule`, `reports`, `system`, `users`)
und der einzelnen Befehle ist nicht Bestandteil dieses Kapitels, da sie zur
Präsentationsschicht gehört. Diese Zuordnung wird in `handbuch_presentation.md`
dokumentiert, um Doppelpflege zu vermeiden.

---

## Kapitel 5: Domain-Modell

**Quelle:** `handbuch_domain.md`

### Überblick und Designprinzip

Das Domain-Modell ist der fachliche Kern des Systems `arbeitszeit`. Es enthält ausschließlich
Geschäftslogik und keinerlei Abhängigkeiten zu Datenbank, Hardware oder UI. Die Schicht ist
nach dem Prinzip **Domain-Driven Design (DDD)** aufgebaut: Entitäten, Value Objects,
Enumerationen, Fehlertypen und Domain Services sind klar voneinander getrennt.
Alle Dateien liegen unter `src/arbeitszeit/domain/`.

```text
src/arbeitszeit/domain/
├── __init__.py          # leer – kein öffentliches Re-Export
├── audit_events.py      # Katalog aller Audit-Log-Eventnamen
├── entities.py          # Entitäten (frozen dataclasses)
├── enums.py             # Alle StrEnum-Typen des Systems
├── errors.py            # Domänenfehler-Hierarchie
├── value_objects.py     # Starke ID-Typen via NewType
├── ports/
│   └── repositories.py  # Repository-Protokolle (Interfaces)
└── services/
    ├── booking_rules.py      # Buchungssequenz-Validierung
    └── compliance_checks.py  # ArbZG-Prüfhilfen
```

---

### Value Objects – Starke ID-Typen

**Datei:** `src/arbeitszeit/domain/value_objects.py`

Alle Primärschlüssel im System sind keine bloßen `int`-Werte, sondern eigene Typen,
die mit `typing.NewType` erzeugt werden:

| ID-Typ                  | Bedeutung                              |
|-------------------------|----------------------------------------|
| `EmployeeId`            | Mitarbeiter-Datensatz                  |
| `UserAccountId`         | Benutzerkonto (Login)                  |
| `RfidCardId`            | RFID-Karte                             |
| `TerminalId`            | Buchungsterminal (Hardware)            |
| `TimeBookingId`         | Zeitbuchung (COME/GO/Pause)            |
| `WorkScheduleVersionId` | Version einer Regelarbeitszeit         |
| `ReviewCaseId`          | Prüffall                               |
| `SupplementId`          | Nachtrag                               |
| `BookingCorrectionId`   | Korrektur einer Buchung                |
| `DeviceEventId`         | Geräteereignis (RFID-Scan, Numpad)     |
| `AuditLogEntryId`       | Eintrag im Audit-Log                   |

**Warum NewType?** Obwohl zur Laufzeit alle IDs schlichte `int`-Werte sind, behandelt
`mypy` sie als inkompatible Typen. Ein versehentlicher Aufruf wie
`booking_repo.get_by_id(employee.id)` wird damit bereits statisch als Typfehler
erkannt – ohne jeglichen Laufzeit-Overhead. Da alle ID-Typen Subtypen von `int` sind,
können sie ohne Konvertierung als SQL-Parameter übergeben werden.

---

### Enumerationen

**Datei:** `src/arbeitszeit/domain/enums.py`

Alle Zustands- und Klassenangaben des Systems sind als `StrEnum` definiert.
Das bedeutet: Die Enum-Werte sind gleichzeitig ihre eigene String-Darstellung
(z. B. `BookingType.COME == "COME"`), was die direkte Speicherung in SQLite
ohne separate Konvertierung ermöglicht.

#### Buchungstypen (`BookingType`)

| Wert          | Bedeutung              |
|---------------|------------------------|
| `COME`        | Arbeitsbeginn          |
| `GO`          | Arbeitsende            |
| `BREAK_START` | Pausenbeginn           |
| `BREAK_END`   | Pausenende             |

#### Buchungsstatus (`BookingStatus`)

| Wert               | Bedeutung                                        |
|--------------------|--------------------------------------------------|
| `OK`               | Buchung geprüft und regelkonform                 |
| `OPEN`             | Automatisch erzeugt, noch nicht abgeschlossen    |
| `WARN`             | Auffälligkeit, Prüfung empfohlen                 |
| `NEEDS_REVIEW`     | Prüffall wurde angelegt                          |
| `CORRECTED`        | Buchung wurde nachträglich korrigiert            |
| `CLOSED_WITH_NOTE` | Abgeschlossen mit Begründungsnotiz               |

#### Prüffall-Typen (`ReviewCaseType`)

| Wert                           | Bedeutung                                     |
|--------------------------------|-----------------------------------------------|
| `OPEN_WORK_PHASE`              | Keine abschließende GO-Buchung vorhanden      |
| `OPEN_BREAK_PHASE`             | Keine BREAK_END-Buchung vorhanden             |
| `OUTSIDE_SCHEDULE_WINDOW`      | Buchung außerhalb der Regelarbeitszeit        |
| `POSSIBLE_BREAK_VIOLATION`     | Möglicher Verstoß gegen §4 ArbZG (Pausen)     |
| `POSSIBLE_REST_VIOLATION`      | Möglicher Verstoß gegen §5 ArbZG (Ruhezeit)   |
| `POSSIBLE_MAX_HOURS_VIOLATION` | Möglicher Verstoß gegen §3 ArbZG (10h-Grenze) |
| `IMPLAUSIBLE_SEQUENCE`         | Buchungsreihenfolge ist fachlich unplausibel  |
| `UNKNOWN_CARD_ATTEMPT`         | Unbekannte RFID-Karte wurde gescannt          |
| `INACTIVE_CARD_ATTEMPT`        | Deaktivierte RFID-Karte wurde gescannt        |
| `TIME_ANOMALY`                 | Zeitstempel weicht stark von Normalwerten ab  |
| `MANUAL_ENTRY_REVIEW`          | Manuell erfasster Eintrag muss geprüft werden |

#### Weitere Enumerationen

| Enum               | Werte                                                | Verwendung                             |
|--------------------|------------------------------------------------------|----------------------------------------|
| `ReviewCaseStatus` | `OPEN`, `IN_REVIEW`, `RESOLVED`, `CLOSED_WITH_NOTE`  | Workflow eines Prüffalls               |
| `ReviewSeverity`   | `INFO`, `WARN`, `CRITICAL`                           | Schweregrad eines Prüffalls            |
| `CardStatus`       | `ACTIVE`, `INACTIVE`, `REPLACED`, `LOST`             | Status einer RFID-Karte                |
| `UserRole`         | `EMPLOYEE`, `ADMIN`, `REVIEWER`, `TECH`              | Berechtigungsstufe                     |
| `BookingSource`    | `TERMINAL`, `MANUAL`, `IMPORT`                       | Herkunft einer Zeitbuchung             |
| `ChangeOrigin`     | `SYSTEM_SEED`, `ADMIN_UI`, `MIGRATION`               | Herkunft einer Systemänderung          |
| `ApprovalStatus`   | `PENDING`, `APPROVED`, `REJECTED`                    | Genehmigungsstatus eines Nachtrags     |
| `ScopeType`        | `GLOBAL`, `EMPLOYEE`                                 | Geltungsbereich einer Regelarbeitszeit |

---

### Entitäten

**Datei:** `src/arbeitszeit/domain/entities.py`

Alle Entitäten sind als `@dataclass(frozen=True)` definiert. Das bedeutet: Einmal
erzeugte Entitätsobjekte sind unveränderlich (immutable). Zustandsänderungen werden
nicht durch Mutation, sondern durch neue Datenbankoperationen über die Repositories
ausgedrückt. Entitäten mit fachlichen Invarianten validieren diese in `__post_init__`.

#### `Employee` – Mitarbeiter

Repräsentiert einen Mitarbeiter der Praxis.

| Feld           | Typ          | Pflicht | Beschreibung                                    |
|----------------|--------------|---------|-------------------------------------------------|
| `id`           | `EmployeeId` | ja      | Datenbankschlüssel                              |
| `personnel_no` | `str`        | ja      | Personalnummer (darf nicht leer sein)           |
| `first_name`   | `str`        | ja      | Vorname                                         |
| `last_name`    | `str`        | ja      | Nachname                                        |
| `is_active`    | `bool`       | ja      | Aktiv-Status; inaktive Mitarbeiter dürfen nicht buchen |

**Invariante:** `personnel_no` darf nicht leer oder nur Leerzeichen sein.

---

#### `UserAccount` – Benutzerkonto

Repräsentiert ein Anmeldekonto (z. B. für Admins oder Reviewer). Ein Benutzerkonto
kann optional mit einem Mitarbeiter verknüpft sein.

| Feld          | Typ                  | Beschreibung                       |
|---------------|----------------------|------------------------------------|
| `id`          | `UserAccountId`      | Datenbankschlüssel                 |
| `employee_id` | `EmployeeId \| None` | Optionaler Mitarbeiterbezug        |
| `username`    | `str`                | Anmeldename (darf nicht leer sein) |
| `role`        | `UserRole`           | Berechtigungsstufe                 |
| `is_active`   | `bool`               | Ob das Konto aktiv ist             |

---

#### `RfidCard` – RFID-Karte

Repräsentiert eine physische RFID-Karte, die einem Mitarbeiter zugeordnet ist.

| Feld                  | Typ                   | Beschreibung                             |
|-----------------------|-----------------------|------------------------------------------|
| `id`                  | `RfidCardId`          | Datenbankschlüssel                       |
| `employee_id`         | `EmployeeId`          | Zugehöriger Mitarbeiter                  |
| `uid_hash`            | `str`                 | Hash der RFID-UID                        |
| `status`              | `CardStatus`          | Aktueller Kartenstatus                   |
| `valid_from`          | `date`                | Gültigkeitsbeginn                        |
| `valid_until`         | `date \| None`        | Gültigkeitsende (None = unbefristet)     |
| `replaced_by_card_id` | `RfidCardId \| None`  | Nachfolgekarte bei Ersatz                |

**Invariante:** `valid_until` darf nicht vor `valid_from` liegen.

---

#### `TimeBooking` – Zeitbuchung

Das zentrale Kernobjekt des Systems. Jede Stempelung (Kommen, Gehen, Pause) erzeugt
eine `TimeBooking`-Instanz.

| Feld              | Typ                      | Beschreibung                                   |
|-------------------|--------------------------|------------------------------------------------|
| `id`              | `TimeBookingId`          | Datenbankschlüssel                             |
| `employee_id`     | `EmployeeId`             | Buchender Mitarbeiter                          |
| `booking_type`    | `BookingType`            | Art der Buchung (COME/GO/BREAK_START/BREAK_END) |
| `booked_at`       | `datetime`               | Zeitstempel der Buchung                        |
| `source`          | `BookingSource`          | Herkunft (Terminal, Manuell, Import)           |
| `status`          | `BookingStatus`          | Aktueller Prüfstatus                           |
| `terminal_id`     | `TerminalId \| None`     | Terminal, das die Buchung erzeugt hat          |
| `rfid_card_id`    | `RfidCardId \| None`     | Verwendete RFID-Karte                          |
| `device_event_id` | `DeviceEventId \| None`  | Zugehöriges Geräteereignis                     |
| `note`            | `str \| None`            | Optionale Freitextnotiz                        |

---

#### `WorkScheduleVersion` – Regelarbeitszeit

Speichert die Soll-Arbeitszeiten, die entweder global für alle Mitarbeiter oder
individuell pro Mitarbeiter für einen bestimmten Wochentag und Zeitraum gelten.

| Feld                 | Typ                       | Beschreibung                         |
|----------------------|---------------------------|--------------------------------------|
| `scope_type`         | `ScopeType`               | `GLOBAL` oder `EMPLOYEE`             |
| `scope_employee_id`  | `EmployeeId \| None`      | Nur bei `EMPLOYEE`-Scope gesetzt     |
| `weekday`            | `int`                     | ISO-Wochentag: 1=Montag … 7=Sonntag  |
| `start_time`         | `time`                    | Beginn der Regelarbeitszeit          |
| `end_time`           | `time`                    | Ende der Regelarbeitszeit            |
| `valid_from`         | `date`                    | Gültigkeitsbeginn dieser Version     |
| `valid_until`        | `date \| None`            | Gültigkeitsende (None = aktuell gültig) |
| `change_origin`      | `ChangeOrigin`            | Wer/was die Änderung ausgelöst hat   |
| `changed_by_user_id` | `UserAccountId \| None`   | Ausführendes Benutzerkonto           |

**Invarianten:** `start_time` muss vor `end_time` liegen; `scope_type` und
`scope_employee_id` müssen konsistent sein; `weekday` muss 1–7 (ISO) betragen;
`valid_until` darf nicht vor `valid_from` liegen.

---

#### `ReviewCase` – Prüffall

Repräsentiert einen fachlichen Auffälligkeitsbefund, der durch automatische
Compliance-Checks oder manuelle Auslösung entsteht und einen Bearbeitungsworkflow
durchläuft.

| Feld                | Typ                      | Beschreibung                                  |
|---------------------|--------------------------|-----------------------------------------------|
| `id`                | `ReviewCaseId`           | Datenbankschlüssel                            |
| `employee_id`       | `EmployeeId`             | Betroffener Mitarbeiter                       |
| `case_type`         | `ReviewCaseType`         | Art der Auffälligkeit                         |
| `severity`          | `ReviewSeverity`         | Schweregrad: INFO / WARN / CRITICAL           |
| `status`            | `ReviewCaseStatus`       | Workflow-Status (OPEN → IN_REVIEW → RESOLVED) |
| `description`       | `str`                    | Beschreibung der Auffälligkeit                |
| `booking_id`        | `TimeBookingId \| None`  | Betroffene Zeitbuchung (sofern zuordenbar)    |
| `created_at`        | `datetime`               | Zeitpunkt der Fallanlage                      |
| `closed_at`         | `datetime \| None`       | Zeitpunkt des Abschlusses                     |
| `closed_by_user_id` | `UserAccountId \| None`  | Benutzer, der den Fall abgeschlossen hat      |
| `note`              | `str \| None`            | Pflicht bei `CLOSED_WITH_NOTE`                |

**Invariante:** Offene Fälle (`OPEN`, `IN_REVIEW`) dürfen keine Schließungsdaten
haben; abgeschlossene Fälle (`RESOLVED`, `CLOSED_WITH_NOTE`) müssen sie haben.
`CLOSED_WITH_NOTE` erfordert zusätzlich eine nicht-leere Begründung.

---

#### `Supplement` – Nachtrag

Repräsentiert eine nachträglich erfasste Zeitbuchung (z. B. vergessene Stempelung),
die durch ein Benutzerkonto genehmigt oder abgelehnt werden muss.

Der Workflow verläuft immer in einer Richtung:

```text
PENDING  →  APPROVED
         →  REJECTED
```

**Invarianten:** Je nach `approval_status` müssen die entsprechenden Felder
(`approved_by_user_id`, `approved_at`, `rejected_by_user_id`, `rejected_at`)
gesetzt bzw. leer sein. `approved_at` und `rejected_at` dürfen nicht vor
`recorded_at` liegen.

---

#### `BookingCorrection` – Buchungskorrektur

Speichert den vollständigen Vorher-/Nachher-Vergleich einer Buchungskorrektur
als unveränderlichen Audit-Trail.

| Feld                   | Typ              | Beschreibung                    |
|------------------------|------------------|---------------------------------|
| `original_booking_id`  | `TimeBookingId`  | Die korrigierte Originalbuchung |
| `corrected_by_user_id` | `UserAccountId`  | Ausführendes Benutzerkonto      |
| `reason`               | `str`            | Begründung der Korrektur (Pflicht) |
| `old_booking_type`     | `BookingType`    | Ursprünglicher Buchungstyp      |
| `old_booked_at`        | `datetime`       | Ursprünglicher Zeitstempel      |
| `new_booking_type`     | `BookingType`    | Neuer Buchungstyp               |
| `new_booked_at`        | `datetime`       | Neuer Zeitstempel               |

**Invariante:** `created_at` darf nicht vor `old_booked_at` liegen.

---

#### `AuditLogEntry` – Audit-Log-Eintrag

Repräsentiert einen unveränderlichen Protokolleintrag für revisionssichere
Nachvollziehbarkeit aller systemrelevanten Ereignisse.

| Feld           | Typ                     | Beschreibung                                         |
|----------------|-------------------------|------------------------------------------------------|
| `id`           | `AuditLogEntryId`       | Datenbankschlüssel                                   |
| `event_type`   | `str`                   | Konstantenname aus `audit_events.py`                 |
| `object_type`  | `str`                   | Tabellenname (snake_case) oder Systembezeichner      |
| `object_id`    | `int`                   | Polymorph: Row-ID aus der betroffenen Tabelle        |
| `user_id`      | `UserAccountId \| None` | Auslösendes Benutzerkonto (ggf. kein Konto)          |
| `employee_id`  | `EmployeeId \| None`    | Betroffener Mitarbeiter (ggf. nicht personenbezogen) |
| `event_at`     | `datetime`              | Zeitstempel des protokollierten Ereignisses          |
| `details_json` | `str`                   | Kontextdaten als JSON-String                         |

---

### Domänenfehler

**Datei:** `src/arbeitszeit/domain/errors.py`

Alle Fehler, die bei Verletzung fachlicher Regeln ausgelöst werden, erben von
`DomainError`. Jeder Fehlertyp trägt einen maschinenlesbaren `code`-String,
der in Logs und der Benutzeroberfläche ausgewertet werden kann.

| Fehlerklasse                  | Code                       | Auslöser                                             |
|-------------------------------|----------------------------|------------------------------------------------------|
| `DomainError`                 | `DOMAIN_ERROR`             | Basisklasse; direkt oder abgeleitet                  |
| `UnknownCardError`            | `UNKNOWN_CARD`             | Gescannte RFID-Karte ist im System unbekannt         |
| `InactiveCardError`           | `INACTIVE_CARD`            | Gescannte RFID-Karte ist deaktiviert                 |
| `InactiveEmployeeError`       | `INACTIVE_EMPLOYEE`        | Mitarbeiter ist deaktiviert                          |
| `InvalidBookingSequenceError` | `INVALID_BOOKING_SEQUENCE` | Buchungsfolge verletzt Sequenzregeln                 |
| `OpenPhaseConflictError`      | `OPEN_PHASE_CONFLICT`      | Konflikt mit einer offenen Arbeits- oder Pausenphase |
| `PermissionDeniedError`       | `PERMISSION_DENIED`        | Fehlende Berechtigung für die Aktion                 |
| `ValidationError`             | `VALIDATION_ERROR`         | Fachliche Validierung schlug fehl                    |
| `NotFoundError`               | `NOT_FOUND`                | Gesuchtes Objekt existiert nicht                     |
| `ConflictError`               | `CONFLICT`                 | Datenbankkonflikt (z. B. doppelte Buchung)           |

Alle Fehlerklassen akzeptieren einen optionalen `message`-String sowie beliebige
Schlüsselwort-Argumente als `context`-Dictionary für strukturierte Fehlerdiagnose.

---

### Repository-Protokolle (Ports)

**Datei:** `src/arbeitszeit/domain/ports/repositories.py`

Das Domain-Modell kennt keine konkrete Datenbank. Stattdessen definiert es
**Protokolle** (Python `typing.Protocol`) für jeden Repository-Typ. Die SQLite-
Implementierungen in der Infrastrukturschicht müssen diese Protokolle erfüllen,
ohne dass das Domain-Modell sie importiert – klassische Dependency Inversion.

| Protokoll                    | Zuständigkeit                                          |
|-----------------------------|---------------------------------------------------------|
| `EmployeeRepository`        | Mitarbeiter lesen und schreiben                        |
| `UserAccountRepository`     | Benutzerkonten lesen und schreiben                     |
| `RfidCardRepository`        | RFID-Karten lesen und schreiben (inkl. UID-Hash-Lookup) |
| `TimeBookingRepository`     | Buchungen schreiben, lesen, Status setzen              |
| `WorkScheduleRepository`    | Regelarbeitszeiten verwalten (Versionen, Gültigkeit)   |
| `ReviewCaseRepository`      | Prüffälle anlegen und abschließen                      |
| `SupplementRepository`      | Nachträge verwalten (PENDING → APPROVED/REJECTED)      |
| `BookingCorrectionRepository` | Korrekturen anlegen und lesen                        |
| `AuditLogRepository`        | Audit-Einträge persistent schreiben                    |
| `DeviceEventRepository`     | Geräteereignisse (RFID-Scans) protokollieren           |
| `SystemConfigRepository`    | Systemkonfiguration lesen und schreiben                |

> **Wichtiger Sonderfall – `AuditLogRepository`:** Die Implementierung muss
> Audit-Einträge **auch dann persistent speichern**, wenn die übergeordnete
> Transaktion (UnitOfWork) zurückgerollt wird. Grund: Abweisungen von
> unbekannten oder inaktiven Karten sind auditpflichtig und dürfen nicht
> zusammen mit dem fehlgeschlagenen Buchungsvorgang verloren gehen. In den
> Repository-Kommentaren ist für die SQLite-Implementierung eine separate
> `autocommit`-Verbindung als Implementierungshinweis dokumentiert.

#### Besonderheit `WorkScheduleRepository.list_versions`

```text
scope_employee_id=None  → ausschließlich GLOBAL-Versionen
scope_employee_id=<id>  → ausschließlich EMPLOYEE-Versionen für diesen MA
Niemals beide Scopes gemischt.
Rückgabe aufsteigend nach valid_from sortiert.
```

#### Besonderheit `TimeBookingRepository.list_for_employee_on_day`

Die Rückgabe muss **aufsteigend nach `booked_at`** sortiert sein, da alle
nachgelagerten Compliance-Prüfungen eine chronologische Reihenfolge voraussetzen.

---

### Domain Services

#### Buchungssequenz-Validierung

**Datei:** `src/arbeitszeit/domain/services/booking_rules.py`

Die Funktion `validate_booking_sequence(booking_type, day_bookings)` stellt sicher,
dass eine neue Buchung zur bisherigen Tagesfolge passt. Sie wirft bei verletzter
Sequenz `InvalidBookingSequenceError` oder `OpenPhaseConflictError` und arbeitet
zustandslos auf den übergebenen Listen – kein Datenbankzugriff. `day_bookings` ist
eine chronologisch sortierte `Sequence[BookingType]`, nicht eine Liste vollständiger
`TimeBooking`-Entitäten.

**Erlaubte Übergänge:**

| Neuer Typ      | Bedingung für Zulässigkeit                    |
|----------------|-----------------------------------------------|
| `COME`         | Keine offene Arbeitsphase, keine offene Pause |
| `GO`           | Offene Arbeitsphase vorhanden; keine offene Pause |
| `BREAK_START`  | Offene Arbeitsphase vorhanden; keine offene Pause |
| `BREAK_END`    | Offene Pause vorhanden                        |

**Erster Eintrag des Tages** darf ausschließlich `COME` sein; `GO`, `BREAK_START`
und `BREAK_END` als erste Buchung des Tages sind immer ungültig.

**Fehler-Mapping:**

| Situation                                 | Geworfener Fehler               |
|-------------------------------------------|---------------------------------|
| GO/BREAK_START/BREAK_END als Erstbuchung  | `InvalidBookingSequenceError`   |
| COME bei offener Arbeitsphase             | `InvalidBookingSequenceError`   |
| COME bei offener Pause                    | `InvalidBookingSequenceError`   |
| GO ohne offene Arbeitsphase               | `InvalidBookingSequenceError`   |
| GO bei offener Pause                      | `OpenPhaseConflictError`        |
| BREAK_START ohne offene Arbeitsphase      | `InvalidBookingSequenceError`   |
| BREAK_START bei offener Pause             | `InvalidBookingSequenceError`   |
| BREAK_END ohne offene Pause               | `InvalidBookingSequenceError`   |

---

#### ArbZG-Compliance-Prüfungen

**Datei:** `src/arbeitszeit/domain/services/compliance_checks.py`

Drei zustandslose Prüffunktionen erzeugen `ComplianceFlag`-Objekte, wenn
arbeitszeitrechtliche Schwellwerte überschritten werden. Jedes Flag enthält
einen `ReviewCaseType` und einen `ReviewSeverity`-Wert.

> **Hinweis:** Die Prüfungen arbeiten auf der **Netto-Arbeitszeit** (Gesamtdauer
> der Arbeitsphasen abzüglich aller erfassten Pausen). Sie ersetzen keine
> rechtsverbindliche Einzelfallbewertung, sondern dienen als fachliche Prüfhilfe.

##### `check_break_compliance(day_bookings)` – §4 ArbZG

| Bedingung                                     | Schweregrad |
|-----------------------------------------------|-------------|
| Ununterbrochener Arbeitsblock > 6 Stunden     | `WARN`      |
| Netto > 9h mit weniger als 45 min Gesamtpause | `CRITICAL`  |
| Netto > 6h mit weniger als 30 min Gesamtpause | `WARN`      |

##### `check_max_hours(day_bookings)` – §3 ArbZG

| Bedingung                      | Schweregrad |
|--------------------------------|-------------|
| Netto-Arbeitszeit > 10 Stunden | `CRITICAL`  |
| Netto-Arbeitszeit > 8 Stunden  | `WARN`      |

##### `check_rest_period(last_go, next_come)` – §5 ArbZG

| Bedingung                                     | Schweregrad |
|-----------------------------------------------|-------------|
| Ruhezeit zwischen GO und nächstem COME < 11h  | `CRITICAL`  |

---

### Audit-Event-Katalog

**Datei:** `src/arbeitszeit/domain/audit_events.py`

Um Tippfehler in Audit-Log-Einträgen zu verhindern, sind alle `event_type`-Strings
zentral als Modulkonstanten definiert. Kein Use Case oder Infrastrukturkomponente darf
freie String-Literale für `event_type` verwenden.

| Konstante                        | Ereignis                                  |
|----------------------------------|-------------------------------------------|
| `TIME_BOOKED`                    | Zeitbuchung erfolgreich gespeichert       |
| `BOOKING_REJECTED_UNKNOWN_CARD`  | Buchung abgewiesen – Karte unbekannt      |
| `BOOKING_REJECTED_INACTIVE_CARD` | Buchung abgewiesen – Karte inaktiv        |
| `BOOKING_CORRECTED`              | Buchung nachträglich korrigiert           |
| `SUPPLEMENT_CREATED`             | Nachtrag erfasst                          |
| `SUPPLEMENT_APPROVED`            | Nachtrag genehmigt                        |
| `SUPPLEMENT_REJECTED`            | Nachtrag abgelehnt                        |
| `WORK_SCHEDULE_CHANGED`          | Regelarbeitszeit geändert                 |
| `EMPLOYEE_CREATED`               | Mitarbeiter angelegt                      |
| `EMPLOYEE_DEACTIVATED`           | Mitarbeiter deaktiviert                   |
| `CARD_ASSIGNED`                  | RFID-Karte einem Mitarbeiter zugewiesen   |
| `CARD_REPLACED`                  | RFID-Karte ersetzt (alte Karte auf REPLACED) |
| `CARD_DEACTIVATED`               | RFID-Karte deaktiviert                    |
| `USER_ACCOUNT_CREATED`           | Benutzerkonto angelegt                    |
| `USER_ACCOUNT_DEACTIVATED`       | Benutzerkonto deaktiviert                 |
| `USER_ACCOUNT_REACTIVATED`       | Benutzerkonto reaktiviert                 |
| `USER_ACCOUNT_ROLE_CHANGED`      | Rolle eines Benutzerkontos geändert       |
| `BACKUP_CREATED`                 | Datenbank-Backup erstellt                 |
| `BACKUP_SYNCED_TO_NAS`           | Backup erfolgreich auf NAS übertragen     |
| `BACKUP_SYNC_FAILED`             | Backup-Übertragung auf NAS fehlgeschlagen |
| `RESTORE_COMPLETED`              | Datenbank-Wiederherstellung abgeschlossen |

---

### Zusammenspiel der Domain-Schicht

Das folgende Ablaufdiagramm zeigt, wie ein typischer RFID-Buchungsvorgang die
Domain-Schicht durchläuft:

```text
[RFID-Scan am Terminal]
        │
        ▼
  RfidCardRepository.get_active_by_uid_hash()
        │
   ┌────┴────┐
   │ Karte   │ nein → UnknownCardError / InactiveCardError
   │ bekannt?│        → AuditLogRepository.add() (autocommit!)
   │ aktiv?  │
   └────┬────┘
        │ ja
        ▼
  EmployeeRepository.get_by_id()
        │
  InactiveEmployeeError? → Fehler
        │
        ▼
  TimeBookingRepository.list_for_employee_on_day()
        │
        ▼
  validate_booking_sequence()   ← booking_rules.py
        │
  Fehler? → InvalidBookingSequenceError / OpenPhaseConflictError
        │
        ▼
  TimeBookingRepository.add()
        │
        ▼
  check_break_compliance()      ← compliance_checks.py
  check_max_hours()
        │
  Flags? → ReviewCaseRepository.add()
        │
        ▼
  AuditLogRepository.add(TIME_BOOKED)
```

Jede Schicht kommuniziert ausschließlich über die in `ports/repositories.py`
definierten Protokolle. Die Domain kennt weder SQLite noch RFID-Hardware.

---

## Kapitel 6: Infrastrukturschicht

**Quelle:** `handbuch_infrastructure.md`

### Überblick und Zweck

Die Infrastrukturschicht ist die unterste technische Ebene des Systems `arbeitszeit`.
Sie übersetzt die fachlichen Anforderungen der Domain- und Anwendungsschicht in
konkrete Betriebsmittel: SQLite-Datenbankzugriffe, Hardware-Kommunikation, Dateiexporte,
Backups und Systemüberwachung.

**Grundregel:** Alle anderen Schichten (Domain, Application) dürfen die Infrastruktur
nutzen, aber niemals von ihr abhängen. Die Infrastruktur kennt die Domain, nicht umgekehrt.
Für **schreibende** Operationen gilt dies ausnahmslos: jede Zustandsänderung läuft über
einen Use Case in `application/use_cases/`. Für **lesende** Direktzugriffe aus der
Admin-CLI (`presentation/admin_cli/`) auf `infrastructure/` besteht eine dokumentierte
Ausnahme (ADR-002, `docs/adr/adr-cqrs-lesezugriff.md`); zusätzlich enthält
`employees.py` als separat dokumentierter Grenzfall auch einige direkte
Schreibzugriffe ohne Use Case.

#### Verzeichnisstruktur

```text
src/arbeitszeit/infrastructure/
├── __init__.py
├── notification.py          # Desktop-Benachrichtigung
├── system_check.py          # Selbsttest beim Start
├── time_monitor.py          # Zeitsprung-Erkennung
├── backup/
│   └── backup_service.py    # Lokales Backup + NAS-Sync
├── db/
│   ├── connection.py        # SQLite-Verbindung mit PRAGMAs
│   ├── migrations.py        # Schema-Migration aus SQL-Dateien
│   ├── unit_of_work.py      # Transaktionscontroller + Repositories
│   └── repositories/        # Ein Repository pro Entität (11 Klassen)
├── export/
│   ├── csv_exporter.py      # Detail- und Verdichtungsexport (CSV)
│   ├── pdf_report_service.py# Tages-/Wochen-/Monats-/Mitarbeiterberichte (PDF)
│   └── report_queries.py    # Gemeinsame Abfrageschicht für alle Exportkanäle
└── hardware/
    ├── ports.py             # Protokoll-Definitionen (Protocol-Klassen)
    ├── uid_hash.py          # SHA-256-Hash der RFID-UID
    ├── evdev_reader.py      # Physischer RFID-Reader + Numpad (evdev)
    └── simulator.py         # In-Memory-Simulator für Tests
```

---

### Datenbankzugriff (`db/`)

#### Verbindungsaufbau — `db/connection.py`

Alle Datenbankverbindungen werden ausschließlich über `open_connection(db_path)` geöffnet.
Die Funktion setzt vier SQLite-PRAGMAs, die für den Betrieb zwingend erforderlich sind:

| PRAGMA | Wert | Begründung |
|---|---|---|
| `isolation_level` | `None` | Manuelle Transaktionskontrolle (kein Autocommit-Fallback) |
| `journal_mode` | `WAL` | Gleichzeitige Lese-/Schreibzugriffe (audit_conn + Haupt-Transaktion) |
| `foreign_keys` | `ON` | Referenzielle Integrität auf Datenbankebene |
| `busy_timeout` | `5000 ms` | 5 Sekunden Wartezeit bei Lock-Konflikt statt sofortigem Fehler |

Die Verbindung liefert immer `sqlite3.Row`-Objekte zurück, sodass Spalten
per Namen abrufbar sind (`row["employee_id"]` statt `row[0]`).

#### Migrationen — `db/migrations.py`

Das Schema wird ausschließlich durch nummerierte SQL-Dateien im Verzeichnis
`migrations/` gesteuert (Format: `NNNN_beschreibung.sql`).

`run_migrations(conn)` arbeitet folgendes Schema ab:

1. Bereits angewandte Versionen aus `schema_migrations` laden.
2. SQL-Dateien aufsteigend durchlaufen; bekannte Versionen überspringen.
3. Jede Migration und ihre Registrierung in `schema_migrations` in **einer einzigen
   Transaktion** ausführen — entweder beides oder keines wird geschrieben.
4. Bei Fehler: `conn.rollback()`, dann Ausnahme weiterwerfen.

Der Versionsstring wird durch `version.isdigit() and len(version) == 4` validiert,
bevor er in den SQL-String eingebettet wird (kein SQL-Injection-Risiko).

#### Unit of Work — `db/unit_of_work.py`

`SQLiteUnitOfWork` ist der einzige Einstiegspunkt für Use-Cases, die Datenbankänderungen
vornehmen. Er bündelt alle elf Repositories unter einem gemeinsamen Transaktions-Context-Manager:

```python
with SQLiteUnitOfWork(conn, audit_conn=audit_conn) as uow:
    uow.time_booking_repo.add(booking)
    uow.audit_log_repo.add(entry)
    uow.commit()   # explizit notwendig — __exit__ rollt sonst zurück
```

**Transaktionssemantik:** `__exit__` rollt **immer** zurück, sofern kein explizites
`commit()` aufgerufen wurde — auch ohne Exception. Eine vergessene Bestätigung
persistiert damit nie stillschweigend.

**Audit-Connection:** Die optionale `audit_conn` wird ausschließlich für Audit-Log-Einträge
verwendet und muss mit `isolation_level=None` (Autocommit) geöffnet sein.
Dadurch bleiben Audit-Einträge auch nach einem Rollback der Haupt-Transaktion erhalten.
Ohne `audit_conn` fällt das Audit-Log auf die Haupt-Verbindung zurück —
Einträge, die vor einem Rollback erzeugt wurden, gehen dann verloren.

#### Repositories — `db/repositories/`

Jede Domänen-Entität besitzt genau ein Repository. Alle Repositories folgen demselben
Muster: Konstruktor nimmt `conn: sqlite3.Connection`; eine repository-eigene, individuell
benannte Hilfsfunktion nach dem Muster `_row_to_*` (z. B. `_row_to_booking`,
`_row_to_employee`, `_row_to_card`) wandelt `sqlite3.Row` in das Domänenobjekt um. Die
meisten zeitstempelverarbeitenden Repositories normalisieren Zeitstempel dabei über
`_helpers._parse_dt()` auf UTC; `SQLiteAuditLogRepository`, `SQLiteSystemConfigRepository`
und `SQLiteDeviceEventRepository` verwenden diese Hilfsfunktion nicht.

| Repository-Klasse | Tabelle | Kernmethoden |
|---|---|---|
| `SQLiteTimeBookingRepository` | `time_bookings` | `add`, `get_by_id`, `list_for_employee_on_day`, `list_open_for_employee`, `list_between`, `set_status` |
| `SQLiteEmployeeRepository` | `employees` | `add`, `get_by_id`, `get_active_by_personnel_no`, `deactivate` |
| `SQLiteRfidCardRepository` | `rfid_cards` | `add`, `get_by_uid_hash`, `get_active_by_uid_hash`, `get_by_id`, `set_status` |
| `SQLiteUserAccountRepository` | `user_accounts` | `add(account, password_hash)`, `get_by_id`, `get_by_username`, `deactivate`, `reactivate`, `set_role`, `has_active_admin` |
| `SQLiteWorkScheduleRepository` | `work_schedule_versions` | `add`, `close_version`, `get_effective`, `list_versions` |
| `SQLiteReviewCaseRepository` | `review_cases` | `add`, `list_open_for_employee`, `resolve` |
| `SQLiteBookingCorrectionRepository` | `booking_corrections` | `add`, `list_for_booking` |
| `SQLiteSupplementRepository` | `supplements` | `add`, `get_by_id`, `list_pending`, `approve`, `reject` |
| `SQLiteAuditLogRepository` | `audit_log` | `add` (immer via `audit_conn` mit Autocommit) |
| `SQLiteSystemConfigRepository` | `system_config` | `get_current`, `set_current` |
| `SQLiteDeviceEventRepository` | `device_events` | `add` |

**Statushistorie:** `set_status` im `SQLiteTimeBookingRepository` schreibt jeden
Statuswechsel zusätzlich in `booking_status_history` — der vollständige Verlauf
jeder Buchung ist damit lückenlos rekonstruierbar.

**Konfigurationsversionierung:** `SQLiteSystemConfigRepository.set_current` erstellt
bei jeder Änderung einen neuen Datensatz mit inkrementierter `version`-Nummer.
Der aktuelle Wert ist stets der Datensatz mit dem höchsten `version`-Wert.

**Zeitzonenregel:** `list_for_employee_on_day` erwartet einen UTC-Kalendertag.
Die Anwendungsschicht ist verantwortlich, den lokalen Arbeitstag vor dem Aufruf
in UTC zu normalisieren.

---

### Hardware-Abstraktion (`hardware/`)

#### Protokolldefinition — `hardware/ports.py`

Alle Hardware-Komponenten kommunizieren ausschließlich über das `HardwareReader`-Protocol
(PEP 544). Der Rückgabetyp jeder Buchungsanforderung ist `RawBookingRequest`:

```python
@dataclass(frozen=True)
class RawBookingRequest:
    booking_type: BookingType  # COME | GO | BREAK_START | BREAK_END
    uid_hash: str              # SHA-256-Hash der Karten-UID
    occurred_at: datetime      # UTC-Zeitstempel nach vollständiger UID-Lesung
```

Zusätzlich definiert `ports.py` zwei Fehlerfälle:
- `EmptyUidError`: RFID-Reader lieferte leere oder nicht mappbare UID.
- `HardwareTimeoutError`: UID-Lesung überschritt das Zeitlimit (Standard: 5 Sekunden).

#### UID-Hashing — `hardware/uid_hash.py`

Die Roh-UID des RFID-Lesers (Hex-String oder Dezimalfolge) wird **nie direkt gespeichert**.
`hash_uid(raw_uid)` berechnet den SHA-256-Hash als Hex-String:

```python
hashlib.sha256(raw_uid.encode()).hexdigest()
```

Dieser Hash ist der einzige Bezeichner, der in die Datenbank gelangt (`rfid_cards.uid_hash`).
Damit ist die physische Karten-UID aus dem Datenbankinhalt nicht rückrechenbar.

#### Physischer Reader — `hardware/evdev_reader.py`

`EvdevHardwareReader` liest Buchungsanfragen von zwei unabhängigen USB-HID-Geräten:

1. **USB-Numpad** (`/dev/input/event*`): Tasten 1–4 (KP-Variante und normale Ziffern)
   wählen den Buchungstyp (COME/GO/BREAK_START/BREAK_END).
2. **RFID-Reader** (`/dev/input/event*`): Liefert die Karten-UID als Hex-Zeichenfolge,
   abgeschlossen durch Enter. Nicht-Hex-Zeichen werden ignoriert.

**Ablauf eines `read_next()`-Aufrufs:**
1. `_read_booking_type()` blockiert unbegrenzt bis zu einer gültigen Numpad-Taste
   (Idle-Wartezustand, kein Timeout — Timeout-Logik gehört in die aufrufende Schicht).
2. `_read_rfid_uid()` liest die UID mit einem konfigurierbaren Timeout (Standard: 5 s).
3. `occurred_at` wird erst nach vollständiger UID-Lesung gesetzt.
4. `hash_uid()` berechnet den Hash; das `RawBookingRequest`-Objekt wird zurückgegeben.

Geräte werden mit `grab=True` exklusiv belegt, damit keine anderen Prozesse
(z. B. der Desktop) dieselben Tastenanschläge empfangen.

**Voraussetzung:** Der Systemprozess benötigt Lesezugriff auf `/dev/input/event*`
(Gruppe `input` oder udev-Regel).

Die Funktion `map_rfid_key(keycode, shift_active)` ist eigenständig testbar
ohne physische Hardware (enthält die gesamte Filterlogik).

#### Simulator — `hardware/simulator.py`

`SimulatedHardwareReader` implementiert dasselbe `HardwareReader`-Protocol wie der
physische Reader und ermöglicht Tests ohne Hardware:

```python
reader = SimulatedHardwareReader()
reader.inject(BookingType.COME, uid_hash="abc123...")
request = reader.read_next()  # liefert das injizierte Ereignis
```

Die interne Queue ist eine `deque`; `pending` gibt die Anzahl noch nicht abgerufener
Ereignisse zurück. `read_next()` auf leerer Queue wirft `RuntimeError`.

---

### Export (`export/`)

#### Gemeinsame Abfrageschicht — `export/report_queries.py`

**Alle** Exportkanäle (CSV, PDF, UI-Pflichtauswertungen) nutzen ausschließlich die
Funktionen in `report_queries.py`. Für die Admin-CLI (`presentation/admin_cli/reports.py`)
besteht hierzu eine dokumentierte Ausnahme von der Schichtentrennung, wonach lesende
Direktzugriffe auf `report_queries.py` zulässig sind (ADR-002,
`docs/adr/adr-cqrs-lesezugriff.md`).

Öffentliche Abfragefunktionen:

| Funktion | Ergebnis |
|---|---|
| `list_bookings(conn, from_dt, to_dt, employee_id?)` | Alle Buchungen im Zeitraum, aufsteigend nach `booked_at` |
| `list_open_bookings(conn, employee_id?)` | Buchungen mit Status OPEN (kein Zeitraum) |
| `list_warn_bookings(conn, from_dt, to_dt, employee_id?)` | Buchungen mit Status WARN oder NEEDS_REVIEW |
| `list_open_bookings_in_period(conn, from_dt, to_dt, employee_id?)` | Offene Buchungen im Zeitraum (§7.12) |
| `list_corrections(conn, from_dt, to_dt, employee_id?)` | Korrekturen nach `corrected_at` |
| `list_supplements(conn, from_dt, to_dt, employee_id?)` | Nachträge nach `event_at` |
| `list_open_review_cases(conn, employee_id?)` | Offene Prüffälle (OPEN + IN_REVIEW, kein Zeitraum) |
| `list_open_review_cases_in_period(conn, from_dt, to_dt, employee_id?)` | Offene Prüffälle im Zeitraum (§7.12) |
| `list_review_cases_for_booking(conn, booking_id)` | Alle Prüffälle zu einer bestimmten Buchung |
| `get_employee_identity(conn, employee_id)` | `(personnel_no, employee_name)` — Fallback bei fehlendem Datensatz |

Alle Zeitraumbeschränkungen verwenden das halboffene Intervall `[from_dt, to_dt)`.

#### CSV-Export — `export/csv_exporter.py`

Drei Exportfunktionen erzeugen CSV-Dateien nach Pflichtenheft §7.11:

**Detailexport** (`export_detail`): Eine Zeile pro Buchung.

Felder: `buchungs_id`, `mitarbeiter_nr`, `mitarbeiter_name`, `datum`, `uhrzeit`,
`buchungsart`, `status`, `quelle`, `ist_nachtrag`, `ist_korrigiert`, `dauer_minuten`

- `dauer_minuten` wird aus dem Tagesverlauf abgeleitet: GO = Minuten seit letztem COME;
  BREAK_END = Minuten seit letztem BREAK_START; COME/BREAK_START = leer.
- Nachträge (`source=MANUAL`) werden mit `ist_nachtrag=ja` gekennzeichnet.

**Verdichtungsexport** (`export_condensed`): Eine Zeile pro Mitarbeiter und Kalendertag.

Felder: `mitarbeiter_nr`, `mitarbeiter_name`, `datum`, `nettoarbeitszeit_minuten`,
`nettopausenzeit_minuten`, `pausenanzahl`, `anzahl_buchungen`, `offene_buchungen`,
`warn_buchungen`, `pruefpflicht_buchungen`, `korrekturen`, `nachtraege`

Die Tagesstatistik `_day_stats()` arbeitet als Zustandsmaschine:
- Nettoarbeitszeit = Summe aller Arbeitsphasen (COME→BREAK_START und BREAK_END→GO).
- Pausen werden nicht zur Arbeitszeit gezählt.
- Korrekturen werden am `corrected_at`-Tag, Nachträge am `event_at`-Tag gezählt.

**Prüffallexport** (`export_review_cases`): Eine Zeile pro offenem Prüffall.

**Dateinamenschema:**

```text
export_detail_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
export_verdichtet_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
```

Der `export_dir`-Pfad wird von der aufrufenden Schicht aus `system_config`
gelesen und direkt übergeben.

#### PDF-Berichte — `export/pdf_report_service.py`

Vier Berichtsfunktionen erzeugen A4-PDFs via `reportlab` (Pflichtenheft §7.11):

| Funktion | Dateiname | Zeitraum |
|---|---|---|
| `create_daily_report(conn, day, export_dir)` | `bericht_tag_YYYY-MM-DD_…Z.pdf` | Ein Kalendertag (alle Mitarbeiter) |
| `create_weekly_report(conn, year, week, export_dir)` | `bericht_woche_YYYY-WNN_…Z.pdf` | ISO-Woche (alle Mitarbeiter) |
| `create_monthly_report(conn, year, month, export_dir)` | `bericht_monat_YYYY-MM_…Z.pdf` | Kalendermonat (alle Mitarbeiter) |
| `create_employee_report(conn, employee_id, from_dt, to_dt, export_dir)` | `bericht_mitarbeiter_NNNN_…_…Z.pdf` | Freier Zeitraum (ein Mitarbeiter) |

Jeder Bericht enthält fünf inhaltliche Abschnitte:
1. **Buchungen** — Tabelle aller Buchungen im Zeitraum
2. **Korrekturen** — Alter Zustand, neuer Zustand, Begründung, Zeitstempel
3. **Nachträge** — Buchungsart, Ereigniszeitpunkt, Begründung, Freigabestatus
4. **Offene Prüffälle** — Typ, Schwere, Beschreibung, Erkennungszeitpunkt
5. **Erläuterungen** — Bedeutung der Status-Codes (OPEN, WARN, NEEDS_REVIEW,
   Nachträge, Korrekturen)

---

### Backup (`backup/backup_service.py`)

`SQLiteBackupService` verwaltet lokale Sicherungskopien und optionale NAS-Synchronisation.

#### Methoden

**`create_local_backup()`**: Erstellt ein Online-Backup via SQLite-Backup-API
(`sqlite3.Connection.backup()`). Die Quelldatenbank bleibt während des Backups
vollständig lesbar und schreibbar — kein Sperren, kein Downtime.

- Dateiname: `arbeitszeit_YYYYMMDDTHHMMSSZ.db`
- Falls `export_dir` gesetzt: Exportdateien werden nach `backup_dir/exports/` kopiert
  und vom nachfolgenden NAS-Sync mitgenommen.
- Ergebnis wird in `audit_log` mit Ereignistyp `BACKUP_CREATED` protokolliert.

**`sync_to_nas(nas_path)`**: Synchronisiert `backup_dir/` → NAS via `rsync --archive --delete`.

- Schlägt die Synchronisation fehl, wird `BACKUP_SYNC_FAILED` mit Returncode,
  Befehlszeile und stderr ins Audit-Log geschrieben; die Ausnahme wird
  weitergereicht. `cmd_system_backup` in der Präsentationsschicht fängt diese
  Ausnahme und endet mit Exitcode 1 (das lokale Backup ist zu diesem Zeitpunkt
  bereits vollständig erstellt).
- Erfolg wird mit `BACKUP_SYNCED_TO_NAS` protokolliert.

**`restore_from(backup_path, restore_exports?)`**: Stellt die Datenbank aus einer
Backup-Datei wieder her.

- Vorbedingung: Keine offenen Verbindungen zur Zieldatenbank beim Aufruf.
- Führt nach dem Restore `PRAGMA integrity_check` aus; schlägt dieser fehl,
  wird `RuntimeError` geworfen.
- Mit `restore_exports=True` und gesetztem `export_dir`: Exportdateien werden
  aus `backup_dir/exports/` zurück in `export_dir` kopiert.
- Ergebnis wird als `RESTORE_COMPLETED` ins Audit-Log der **wiederhergestellten**
  Datenbank geschrieben.

**`run(nas_path?)`**: Kombinierte Hilfsmethode — erstellt lokales Backup und
synchronisiert optional zum NAS; gibt `BackupResult` zurück.

**NAS-Erreichbarkeitsprüfung (Designentscheidung):** Das System prüft den
NAS-Mount-Punkt ausschließlich per `Path.exists()` und `os.access(..., os.W_OK)`.
Kein Netzwerk-Ping oder TCP-Verbindungstest — ein vorübergehend nicht erreichbares
NAS (Neustart, Wartung) soll keinen `SELFTEST_FAIL` auslösen.

---

### Systemüberwachung

#### Selbsttest — `system_check.py`

`run_system_check(db_path, numpad_path?, rfid_path?)` prüft beim Systemstart
sechs Bereiche und schreibt das Gesamtergebnis als `SELFTEST_OK` oder `SELFTEST_FAIL`
in `system_events`:

| Prüfbereich | Was wird geprüft |
|---|---|
| `db_access` | Datenbankverbindung öffenbar; alle erwarteten Migrationsversionen angewendet |
| `config_keys` | Sechs Pflicht-Konfigurationsschlüssel in `system_config` vorhanden |
| `nas_reachability` | NAS-Pfad existiert und ist schreibbar (nur wenn `backup.nas_enabled=true`) |
| `fk_consistency` | `PRAGMA foreign_key_check` meldet keine verwaisten Fremdschlüsselreferenzen |
| `ntp_sync` | NTP via `timedatectl` aktiv und synchronisiert |
| `device_availability` | Numpad und RFID-Gerätepfade existieren und sind lesbar |

Jeder Bereich liefert ein `CheckResult(name, ok, detail)`. Das `SystemCheckResult`
aggregiert alle Checks; `overall_ok` ist `True` genau dann, wenn alle Checks bestanden sind.

#### Zeitsprung-Erkennung — `time_monitor.py`

`SystemTimeMonitor` erkennt Uhrzeitänderungen durch Gegenüberstellung von
Wall-Clock (`datetime.now(timezone.utc)`) und monotoner Uhr (`time.monotonic()`):

```text
diff = actual_wall_ts - (last_wall_ts + mono_elapsed)
```

- `|diff| > threshold` (Standard: 60 Sekunden): Zeitsprung erkannt.
- `diff > 0`: Vorwärtssprung → Ereignistyp `TIME_JUMP_DETECTED`
  (NTP-Korrektur oder manuelle Vorstellung).
- `diff < 0`: Rückwärtssprung → Ereignistyp `MANUAL_TIME_CHANGE_DETECTED`
  (fast immer manuell).

Der Schwellenwert filtert NTP-Drift (typisch < 1 s/Stunde) heraus.
`load_threshold_from_config(db_path)` liest den Wert aus `system_config`
(Schlüssel `time_monitor.jump_threshold_seconds`); Fallback: 60 Sekunden.

Beide Clock-Funktionen sind per Dependency-Injection ersetzbar (`_wall_clock`,
`_mono_clock`), was Unit-Tests ohne Systemzeit-Manipulation ermöglicht.

#### Desktop-Benachrichtigung — `notification.py`

`notify(title, body, urgency?)` sendet eine Desktop-Benachrichtigung via `notify-send`
(Pflichtenheft §7.10: Systemzustand muss dem Betreiber sichtbar sein).

- Dringlichkeitsstufen: `"low"` | `"normal"` | `"critical"`
- **Fail-Safe:** `FileNotFoundError` (notify-send nicht installiert) und
  `TimeoutExpired` werden still ignoriert; ein `logging.debug`-Eintrag wird erzeugt.
- Sonstige Ausnahmen erzeugen einen `logging.warning`-Eintrag.
- Voraussetzung: Paket `libnotify-bin` (auf Lubuntu/Linux Mint standardmäßig vorhanden).

---

### Querverbindungen und Architekturprinzipien

#### Abhängigkeitsrichtung

```text
Application/Domain
       ↓
  infrastructure/
  ├── db/           ← nutzt domain.entities, domain.enums, domain.ports
  ├── export/       ← nutzt application.queries, domain.enums
  ├── hardware/     ← nutzt domain.enums
  ├── backup/       ← nutzt domain.audit_events, domain.entities
  └── system_check/ ← nutzt infrastructure.db.connection
```

Alle Repositories implementieren die in `domain/ports/repositories.py` definierten
Abstract-Base-Interfaces — die Fachlogik kennt daher nur das Interface, nie die
SQLite-Implementierung.

#### Nicht delegierte Verantwortlichkeiten

Die Infrastrukturschicht übernimmt bewusst **keine** Zuständigkeit für:
- Fachliche Validierung (gehört in die Domain- oder Anwendungsschicht).
- Timeout-Logik für den Numpad-Idle-Wartezustand (gehört in die Betriebsschicht).
- NTP-Synchronisation (Aufgabe des Betriebssystems / systemd).
- Authentifizierung und Autorisierung (Anwendungsschicht).

#### Testbarkeit

Alle sicherheitskritischen und zustandsbehafteten Teile sind ohne physische Hardware testbar:
- `SimulatedHardwareReader` implementiert dasselbe Protocol wie `EvdevHardwareReader`.
- `map_rfid_key()` ist eine pure Funktion ohne Gerätezugriff.
- `SystemTimeMonitor` akzeptiert injizierbare Clock-Callbacks.
- Repositories arbeiten auf jeder `sqlite3.Connection`; eine Verwendung von
  In-Memory-Datenbanken (`:memory:`) ist im Repository nicht belegt — die Testsuite
  nutzt durchgängig dateibasierte Datenbanken über `tmp_path` (nicht verifizierbar).

---

## Kapitel 7: Audit und Prüfstatus

**Quelle:** `handbuch_audit.md`

### Code-Audit (`run_audit.sh` und `scripts/generate_audit_notes.py`)

`run_audit.sh` ist ein ausführbares Shell-Skript im Repository-Wurzelverzeichnis
(56 Zeilen). Es führt nacheinander folgende Analyse-Tools gegen `src/arbeitszeit`
aus und schreibt deren Rohausgaben in ein datumsbezogenes Unterverzeichnis
`docs/audits/reports/<DATUM>/` (Datum im Format `YYYY-MM-DD`):

| Tool | Zweck | Ausgabedatei |
|---|---|---|
| `ruff check` | Linting | `ruff-report.txt` |
| `mypy` | Typprüfung | `mypy-report.txt` |
| `radon cc -s -a` | Zyklomatische Komplexität | `radon-cc.txt` |
| `radon raw` | Rohmetriken (LOC, Kommentare) | `radon-raw.txt` |
| `lint-imports` | Architektur-Contract (import-linter) | `import-linter.txt` |
| `bandit -r ... -f json` | Security-Analyse | `bandit-report.json` |
| `pytest --cov=arbeitszeit` | Tests und Testabdeckung | `coverage.xml`, `htmlcov/`, `pytest.txt` |

Aufruf:

```bash
bash run_audit.sh
```

Das Skript verwendet `set -uo pipefail` und bewusst **nicht** `set -e`: Ein
Kommentar im Skript begründet dies damit, dass die Analyse-Tools bei
Befunden mit Exit-Code 1 zurückkehren können, ohne dass der Gesamtlauf
abgebrochen werden soll. Entsprechend sind die Aufrufe von `ruff`, `mypy`,
`lint-imports`, `bandit` und `pytest` jeweils mit `|| true` abgesichert;
lediglich die beiden `radon`-Aufrufe besitzen kein `|| true`.

Am Ende jedes Laufs ruft `run_audit.sh` automatisch
`scripts/generate_audit_notes.py` auf, das die Rohdaten einliest und eine
versionierte Markdown-Zusammenfassung erzeugt:

```bash
python scripts/generate_audit_notes.py \
    --report-dir docs/audits/reports/<DATUM> \
    --output docs/audits/reports/audit-notes-<DATUM>.md
```

`scripts/generate_audit_notes.py` (596 Zeilen) unterstützt folgende Parameter:

| Parameter | Bedeutung | Standard |
|---|---|---|
| `--report-dir <PFAD>` | Verzeichnis mit den Rohdaten von `run_audit.sh` | `docs/audits/reports` |
| `--output <PFAD>` | Ausgabedatei | `<report-dir>/audit-notes-<DATUM>.md` |

Jeder Parser des Skripts liefert bei fehlender Quelldatei `{"available": False}`
zurück, statt Werte zu schätzen oder zu erfinden. Der erzeugte Bericht ist in
folgender fester Abschnittsreihenfolge aufgebaut:

1. **Überblick** – Codebasisgröße in KLoC (aus `radon raw`) sowie Testanzahl,
   aufgeschlüsselt nach `tests/domain/`, `tests/application/`,
   `tests/integration/` und `tests/e2e/` (gezählt werden Dateien nach dem
   Muster `test_*.py`, ohne `conftest.py`/`__init__.py`).
2. **Linting (Ruff)** – Gesamtanzahl der Befunde sowie gesondert ausgewiesene
   Kategorien `E501` (line-too-long), `F401` (unused-import) und die
   `B`-Serie (Bugbear).
3. **Typprüfung (Mypy)** – bei Erfolg „Fehler insgesamt: 0“ mit Anzahl der
   geprüften Quelldateien; bei Fehlern die Gesamtzahl sowie bis zu 5
   Beispielzeilen.
4. **Komplexität (Radon)** – Durchschnittswert und -note der zyklomatischen
   Komplexität sowie eine Tabelle aller „Hotspots“ mit CC ≥ 10
   (Datei, Block, CC-Wert).
5. **Architektur (import-linter)** – Anzahl geprüfter Contracts, Anzahl
   Verstöße sowie Detailzeilen zu Verstößen.
6. **Security (Bandit)** – Anzahl der Funde nach Schweregrad (High/Medium/Low),
   gescannte LOC, `nosec`-Marker sowie eine Tabelle aller HIGH- und
   MEDIUM-Funde (ID, Datei, Zeile, Beschreibung).
7. **Tests & Coverage** – Gesamt-Coverage in Prozent (aus `coverage.xml`,
   Cobertura-Format) sowie eine Tabelle der Dateien mit Coverage unter 60 %.
8. **Maßnahmenplan** – dynamisch erzeugte, priorisierte Liste offener
   Maßnahmen. Ein Eintrag wird jeweils nur aufgenommen, wenn die zugehörige
   Bedingung zutrifft:
   1. Bandit-Funde mit Schweregrad HIGH oder MEDIUM in Summe > 0
   2. import-linter-Verstöße (`broken`) > 0
   3. Mypy meldet keinen Erfolg und Gesamtfehleranzahl > 0
   4. Ruff-Gesamtbefunde > 0
   5. Radon-Hotspots mit CC ≥ 15 (bis zu drei Blocknamen werden genannt)
   6. Gesamt-Coverage < 80 % (der zugehörige Maßnahmentext verweist dabei auf
      die Anzahl der Dateien mit Coverage < 60 %, wie sie im Abschnitt
      „Tests & Coverage“ ausgewiesen werden)

   Treffen keine der Bedingungen zu, gibt der Bericht den Text
   „_Keine offenen Maßnahmen identifiziert – alle Checks bestanden._“ aus.

> ⚠️ `run_audit.sh` benötigt zusätzlich installierte Tools (`mypy`, `radon`,
> `bandit`), die in `pyproject.toml` unter `[project.optional-dependencies]`
> (Gruppe `dev`) nicht als Pflichtabhängigkeiten geführt sind. Dort sind nur
> `pytest`, `pytest-cov`, `pypdf`, `ruff` und `import-linter` gelistet.

Die von den Analyse-Tools verwendete Konfiguration ist in `pyproject.toml`
hinterlegt:

- `[tool.ruff]`: `line-length = 100`, `target-version = "py314"`,
  `[tool.ruff.lint] select = ["E", "F", "W", "I", "B"]`, `ignore = []`;
  ausgeschlossen sind `.git`, `.venv`, `__pycache__` und
  `docs/audits/reports`.
- `[tool.mypy]`: `python_version = "3.14"`, `strict = true`,
  `disallow_incomplete_defs = true`, `disallow_untyped_defs = true`,
  `ignore_missing_imports = true`, `warn_unused_ignores = true`,
  `warn_return_any = true`; ausgeschlossen sind `^\.venv/` und
  `^docs/audits/reports/`.
- `[tool.importlinter]`: ein Contract „Clean Architecture -
  Layer-Abhaengigkeiten“ vom Typ `layers` mit der Schichtreihenfolge
  `arbeitszeit.presentation` → `arbeitszeit.infrastructure` →
  `arbeitszeit.application` → `arbeitszeit.domain`.

> ℹ️ Im Repository liegen zwei Audit-bezogene Verzeichnisse nebeneinander:
> `docs/audits/reports/` enthält die Rohdaten eines abgeschlossenen Laufs vom
> 16.06.2026 (`ruff-report.txt`, `mypy-report.txt`, `radon-cc.txt`,
> `radon-raw.txt`, `import-linter.txt`, `bandit-report.json`,
> `coverage.xml`, `pytest.txt`) – dieser Pfad entspricht weiterhin dem in
> `run_audit.sh` fest codierten `BASE_DIR="docs/audits/reports"`.
> `docs/08_planung_intern/audits/` enthält demgegenüber ältere, manuell
> erstellte Audit-Berichte (`audit_arbeitszeit_v1_*.md`) sowie eine bereits
> gerenderte Fassung `reports/audit-notes-2026-06-16.md`. Eine Datei
> `audit-notes-2026-06-16.md` direkt unter `docs/audits/reports/` (dem von
> `run_audit.sh` erzeugten Standardpfad) existiert im aktuellen
> Repository-Stand nicht.

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
  (Details siehe Abschnitt „Code-Audit" oben)

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
