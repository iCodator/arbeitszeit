# Code-Audit arbeitszeit – Stand 2026-07-03 17:03

<!-- meta: generated_at=2026-07-03T15:03:51Z -->

## Überblick

- Codebasis: ca. 7.0 KLoC (SLOC) im Paket `arbeitszeit`
- Tests: 4 unit (domain) | 10 application | 14 integration | 3 e2e

## Linting (Ruff)

- Gesamtanzahl Probleme: **84**
- Hauptkategorien:
  - E501 (line-too-long): 55
  - F401 (unused-import): 10
  - B-Serie (bugbear): 0
  - E402: 13
  - F821: 3
  - I001: 3

## Typprüfung (Mypy)

- Fehler insgesamt: **31**
- Typische Muster:
  - `src/arbeitszeit/presentation/admin_gui/main.py:118: error: Unused "type: ignore" comment  [unused-ignore]`
  - `src/arbeitszeit/presentation/admin_gui/main.py:122: error: Unused "type: ignore" comment  [unused-ignore]`
  - `src/arbeitszeit/presentation/admin_gui/main.py:189: error: Argument 4 has incompatible type "**dict[str, int]"; expected "Mapping[str, Any] | None"  [arg-type]`
  - `src/arbeitszeit/presentation/admin_gui/main.py:189: error: Argument 4 has incompatible type "**dict[str, int]"; expected "Misc"  [arg-type]`
  - `src/arbeitszeit/presentation/admin_gui/main.py:202: error: Argument 4 has incompatible type "**dict[str, int]"; expected "Mapping[str, Any] | None"  [arg-type]`

## Komplexität (Radon)

- Durchschnittliche CC: **A (2.55)**, 497 Blöcke analysiert
- Hotspots (CC ≥ 10):

  | Datei | Block | CC |
  |-------|-------|:--:|
  | `domain/services/booking_rules.py` | `validate_booking_sequence` | 14 |
  | `application/use_cases/book_time.py` | `_evaluate_booking` | 14 |
  | `application/use_cases/approve_supplement.py` | `_evaluate_booking` | 14 |
  | `presentation/admin_cli/schedule.py` | `cmd_schedule_show` | 14 |
  | `infrastructure/hardware/evdev_reader.py` | `EvdevHardwareReader._read_rfid_uid` | 13 |
  | `application/use_cases/manage_work_schedule.py` | `ManageWorkScheduleUseCase.execute` | 13 |
  | `infrastructure/export/csv_exporter.py` | `_day_stats` | 12 |
  | `domain/entities.py` | `ReviewCase` | 11 |
  | `application/use_cases/correct_booking.py` | `CorrectBookingUseCase.execute` | 11 |
  | `application/use_cases/approve_supplement.py` | `ApproveSupplementUseCase.execute` | 11 |
  | `domain/entities.py` | `WorkScheduleVersion` | 10 |
  | `domain/entities.py` | `ReviewCase.__post_init__` | 10 |
  | `application/use_cases/reject_supplement.py` | `RejectSupplementUseCase.execute` | 10 |
  | `presentation/admin_cli/system.py` | `cmd_system_backup` | 10 |

## Architektur (import-linter)

- Contracts geprüft: 1
- Verstöße: **0**

## Security (Bandit)

- High: **0** / Medium: **1** / Low: 14
- LOC gescannt: 7299
- Kritische Stellen (HIGH + MEDIUM):

  | ID | Datei | Zeile | Beschreibung |
  |----|-------|:-----:|-------------|
  | `B608` | `infrastructure/db/migrations.py` | 40 | Possible SQL injection vector through string-based query con |

## Tests & Coverage

- Gesamt-Coverage: **62.0 %** (2235 / 3604 Zeilen)
- Dateien mit Coverage < 60 %:

  | Datei | Coverage |
  |-------|:--------:|
  | `presentation/admin_gui/main.py` | 0 % |
  | `infrastructure/hardware/evdev_reader.py` | 26 % |
  | `presentation/admin_cli/system.py` | 27 % |
  | `presentation/admin_cli/_intervals.py` | 29 % |
  | `presentation/admin_cli/schedule.py` | 33 % |
  | `infrastructure/notification.py` | 33 % |
  | `presentation/admin_cli/_auth.py` | 33 % |
  | `presentation/admin_cli/reports.py` | 36 % |
  | `presentation/terminal_ui/main.py` | 47 % |
  | `presentation/admin_cli/bookings.py` | 47 % |

## Maßnahmenplan

1. Security-Funde mit HIGH/MEDIUM-Schwere priorisiert beheben (0 HIGH, 1 MEDIUM).
2. Typfehler beheben (31 Fehler in Mypy-Prüfung).
3. Linting-Fehler beheben (84 Befunde in Ruff-Prüfung).
4. Tests für Module mit Coverage < 60 % ergänzen (10 Dateien betroffen, Gesamt-Coverage: 62.0 %).
