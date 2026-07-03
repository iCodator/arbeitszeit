# Code-Audit arbeitszeit – Stand 2026-06-16 11:47

<!-- meta: generated_at=2026-06-16T09:47:07Z -->

## Überblick

- Codebasis: ca. 5.2 KLoC (SLOC) im Paket `arbeitszeit`
- Tests: 4 unit (domain) | 7 application | 14 integration | 3 e2e

## Linting (Ruff)

- Gesamtanzahl Probleme: **0**
- Hauptkategorien:
  - E501 (line-too-long): 0
  - F401 (unused-import): 0
  - B-Serie (bugbear): 0

## Typprüfung (Mypy)

- Fehler insgesamt: **0**
- 66 Quelldateien geprüft, keine Typfehler
- Typische Muster: –

## Komplexität (Radon)

- Durchschnittliche CC: **A (2.61)**, 352 Blöcke analysiert
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

- High: **0** / Medium: **1** / Low: 8
- LOC gescannt: 5384
- Kritische Stellen (HIGH + MEDIUM):

  | ID | Datei | Zeile | Beschreibung |
  |----|-------|:-----:|-------------|
  | `B608` | `infrastructure/db/migrations.py` | 40 | Possible SQL injection vector through string-based query con |

## Tests & Coverage

- Gesamt-Coverage: **80.9 %** (1982 / 2451 Zeilen)
- Dateien mit Coverage < 60 %:

  | Datei | Coverage |
  |-------|:--------:|
  | `presentation/admin_cli/system.py` | 25 % |
  | `infrastructure/hardware/evdev_reader.py` | 26 % |
  | `presentation/admin_cli/_intervals.py` | 29 % |
  | `presentation/admin_cli/schedule.py` | 32 % |
  | `presentation/admin_cli/reports.py` | 35 % |
  | `presentation/admin_cli/bookings.py` | 46 % |
  | `presentation/terminal_ui/main.py` | 49 % |

## Maßnahmenplan

1. Security-Funde mit HIGH/MEDIUM-Schwere priorisiert beheben (0 HIGH, 1 MEDIUM).
