# Code-Audit arbeitszeit – Stand 2026-06-16 10:16

## Überblick

- Codebasis: ca. 5,4 KLoC (SLOC) / 5,6 KLoC (LOC) in `src/arbeitszeit/`, 66 Quelldateien
- Architektur: Clean Architecture mit vier Schichten — `domain`, `application`, `infrastructure`, `presentation`
- Testabdeckung gesamt: **78 %** (406 Tests grün)

---

## Linting (Ruff)

- Gesamtanzahl Befunde: **63**
- Konfiguration: `select = ["E", "F", "W", "I", "B"]`, `line-length = 88`

### Hauptkategorien

| Code | Anzahl | Beschreibung |
| --- | --- | --- |
| E501 | 59 | Zeile zu lang (> 88 Zeichen) |
| B017 | 4 | `pytest.raises(Exception)` – zu generisch |

### Hinweis

Alle E501-Befunde betreffen überwiegend SQL-Strings und Kommentare in Integrationstests.
Die B017-Befunde befinden sich in `tests/application/test_book_time.py`,
`tests/e2e/test_backup.py` und `tests/test_migrations.py`.

---

## Typprüfung (Mypy)

- Konfiguration: `strict = true`, `python_version = "3.14"`
- **Fehler insgesamt: 0**

```
Success: no issues found in 66 source files
```

Alle Typannotationen sind vollständig und konsistent. Strict-Mode aktiv.

---

## Komplexität (Radon CC)

- Analysierte Blöcke: 346
- Durchschnittliche Komplexität: **A (2.71)**

### Hotspots (CC ≥ 10)

| Datei | Block | CC | Grad |
| --- | --- | --- | --- |
| `domain/entities.py` | `Supplement` | 19 | C |
| `domain/entities.py` | `Supplement.__post_init__` | 18 | C |
| `application/use_cases/approve_supplement.py` | `ApproveSupplementUseCase.execute` | 15 | C |
| `application/use_cases/book_time.py` | `_evaluate_booking` | 14 | C |
| `domain/services/booking_rules.py` | `validate_booking_sequence` | 14 | C |
| `presentation/admin_cli/schedule.py` | `cmd_schedule_show` | 14 | C |
| `application/use_cases/approve_supplement.py` | `_evaluate_booking` | 14 | C |
| `application/use_cases/manage_work_schedule.py` | `ManageWorkScheduleUseCase.execute` | 13 | C |
| `infrastructure/hardware/evdev_reader.py` | `_read_rfid_uid` | 13 | C |
| `infrastructure/export/csv_exporter.py` | `_day_stats` | 12 | C |
| `application/use_cases/correct_booking.py` | `CorrectBookingUseCase.execute` | 11 | C |
| `domain/entities.py` | `ReviewCase` | 11 | C |
| `domain/entities.py` | `WorkScheduleVersion` | 10 | B |
| `domain/entities.py` | `ReviewCase.__post_init__` | 10 | B |
| `application/use_cases/reject_supplement.py` | `RejectSupplementUseCase.execute` | 10 | B |
| `presentation/admin_cli/system.py` | `cmd_system_backup` | 10 | B |

### Hinweis

Die Hotspots in `entities.py` und Use Cases spiegeln inhärente fachliche Komplexität
(ArbZG-Prüfregeln, Supplement-Genehmigungslogik) wider — kein unmittelbarer Refactoring-Bedarf.
`_dispatch` in `admin_cli/main.py` wurde bereits von E(38) auf A(3) reduziert.

---

## Architektur (import-linter)

- Konfiguration: 4-Schicht-Contract `presentation → infrastructure → application → domain`
- Analysierte Dateien: 66, Abhängigkeiten: 160
- **Verstöße: 0**

```
Contracts: 1 kept, 0 broken.
```

---

## Security (Bandit)

- Konfiguration: `bandit -r src`
- Funde: **HIGH: 0 / MEDIUM: 1 / LOW: 8**

### Befunde

| Schwere | Konfidenz | ID | Datei | Zeile | Beschreibung |
| --- | --- | --- | --- | --- | --- |
| MEDIUM | LOW | B608 | `infrastructure/db/migrations.py` | 38 | SQL-Injektion via String-Konstruktion |
| LOW | HIGH | B404 | `infrastructure/backup/backup_service.py` | 4 | `subprocess`-Modul importiert |
| LOW | HIGH | B607 | `infrastructure/backup/backup_service.py` | 72 | Prozess mit partiellem Pfad gestartet |
| LOW | HIGH | B603 | `infrastructure/backup/backup_service.py` | 72 | `subprocess`-Aufruf ohne Shell |
| LOW | HIGH | B110 | `infrastructure/hardware/evdev_reader.py` | 184 | `try/except/pass` |
| LOW | HIGH | B110 | `infrastructure/hardware/evdev_reader.py` | 188 | `try/except/pass` |
| LOW | HIGH | B110 | `infrastructure/system_check.py` | 246 | `try/except/pass` |
| LOW | HIGH | B110 | `infrastructure/time_monitor.py` | 101 | `try/except/pass` |
| LOW | HIGH | B110 | `presentation/terminal_ui/main.py` | 59 | `try/except/pass` |

### Bewertung

- **B608** (`migrations.py:38`): Falsch-Positiv. Der eingebettete Wert ist eine
  validierte 4-stellige Versionsnummer (Zifferncheck Z.31–32). Kein echter Injektionsvektor.
- **B404/B607/B603** (`backup_service.py`): `rsync` wird ohne Shell aufgerufen,
  kein User-Input im Pfad. Bekanntes, akzeptiertes Design.
- **B110** (5×): Bewusste Robustheitsentscheidungen in Hardware- und Infrastrukturpfaden.
  `time_monitor._log` (Z.83) wurde bereits durch `logging.warning` ersetzt;
  Z.101 ist ein stiller Config-Fallback.

---

## Tests & Coverage

- Framework: pytest, Abdeckungsmessung via `pytest-cov`
- **Gesamt-Coverage: 78 %** (2 440 gemessene Zeilen, 538 nicht abgedeckt)
- 406 Tests grün

### Module mit Coverage < 60 %

| Datei | Coverage | Grund |
| --- | --- | --- |
| `infrastructure/hardware/evdev_reader.py` | 26 % | Echthardware-Pfade, nur mit physischem Gerät testbar |
| `presentation/admin_cli/system.py` | 25 % | CLI-Commands ohne dedizierte Integrationstests |
| `presentation/admin_cli/employees.py` | 28 % | CLI-Commands ohne dedizierte Integrationstests |
| `presentation/admin_cli/schedule.py` | 32 % | CLI-Commands ohne dedizierte Integrationstests |
| `presentation/admin_cli/_intervals.py` | 29 % | Nur indirekt über Reports-Commands genutzt |
| `presentation/admin_cli/reports.py` | 35 % | CSV/PDF-Export-Commands |
| `presentation/admin_cli/bookings.py` | 46 % | Buchungs- und Nachtragsbefehle |
| `presentation/terminal_ui/main.py` | 49 % | Hauptschleife, Signalhandler, Startup-Pfad |

### Gut abgedeckt (≥ 90 %)

Gesamte Domain-Schicht, alle Repositories, `backup_service`, `time_monitor`,
`booking_loop` — die fachliche Kernlogik ist vollständig getestet.

---

## Empfehlungen

1. **Ruff E501 (59 Funde):** `black` einmalig auf den gesamten Quellcode anwenden
   oder `line-length` in der Ruff-Konfiguration auf 100–120 anheben, falls
   lange SQL-Strings und Kommentare bewusst beibehalten werden sollen.

2. **Ruff B017 (4 Funde):** `pytest.raises(Exception)` durch den konkreten
   Ausnahmetyp ersetzen (`pytest.raises(sqlite3.OperationalError)` o. ä.).

3. **Radon-Hotspots:** `Supplement.__post_init__` (CC=18) und
   `ApproveSupplementUseCase.execute` (CC=15) könnten in kleinere
   Hilfsfunktionen aufgeteilt werden, falls die Wartbarkeit sinkt.

4. **Coverage Admin-CLI (25–49 %):** Integrationstests für die häufig genutzten
   CLI-Befehle (`employees`, `schedule`, `bookings`) ergänzen. Die `system.py`-
   Befehle (Backup, Systemcheck) sind durch E2E-Tests bereits indirekt abgedeckt.

5. **Bandit B608:** `nosec`-Kommentar mit Begründung ergänzen, damit der Befund
   bei künftigen Scans dokumentiert als akzeptiert erscheint.
