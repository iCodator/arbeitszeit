# Code-Audit arbeitszeit – Stand 2026-06-16 09:09

<!-- meta: generated_at=2026-06-16T09:09:03Z -->

## Überblick

- Codebasis: ca. 5.4 KLoC (SLOC) im Paket `arbeitszeit`
- Tests: 4 unit (domain) | 7 application | 14 integration | 3 e2e

## Linting (Ruff)

- Gesamtanzahl Probleme: **65**
- Hauptkategorien:
  - E501 (line-too-long): 65
  - F401 (unused-import): 0
  - B-Serie (bugbear): 0

## Typprüfung (Mypy)

- Fehler insgesamt: **0**
- 66 Quelldateien geprüft, keine Typfehler
- Typische Muster: –

## Komplexität (Radon)

- Durchschnittliche CC: **A (2.71)**, 346 Blöcke analysiert
- Hotspots (CC ≥ 10):

  | Datei | Block | CC |
  |-------|-------|:--:|
  | `domain/entities.py` | `Supplement` | 19 |
  | `domain/entities.py` | `Supplement.__post_init__` | 18 |
  | `application/use_cases/approve_supplement.py` | `ApproveSupplementUseCase.execute` | 15 |
  | `domain/services/booking_rules.py` | `validate_booking_sequence` | 14 |
  | `application/use_cases/book_time.py` | `_evaluate_booking` | 14 |
  | `application/use_cases/approve_supplement.py` | `_evaluate_booking` | 14 |
  | `presentation/admin_cli/schedule.py` | `cmd_schedule_show` | 14 |
  | `infrastructure/hardware/evdev_reader.py` | `EvdevHardwareReader._read_rfid_uid` | 13 |
  | `application/use_cases/manage_work_schedule.py` | `ManageWorkScheduleUseCase.execute` | 13 |
  | `infrastructure/export/csv_exporter.py` | `_day_stats` | 12 |
  | `domain/entities.py` | `ReviewCase` | 11 |
  | `application/use_cases/correct_booking.py` | `CorrectBookingUseCase.execute` | 11 |
  | `domain/entities.py` | `WorkScheduleVersion` | 10 |
  | `domain/entities.py` | `ReviewCase.__post_init__` | 10 |
  | `application/use_cases/reject_supplement.py` | `RejectSupplementUseCase.execute` | 10 |
  | `presentation/admin_cli/system.py` | `cmd_system_backup` | 10 |

## Architektur (import-linter)

- _(Report nicht verfügbar – lint-imports nicht ausgeführt)_

## Security (Bandit)

- High: **0** / Medium: **1** / Low: 8
- LOC gescannt: 5568
- Kritische Stellen (HIGH + MEDIUM):

  | ID | Datei | Zeile | Beschreibung |
  |----|-------|:-----:|-------------|
  | `B608` | `infrastructure/db/migrations.py` | 38 | Possible SQL injection vector through string-based query con |

## Tests & Coverage

- Gesamt-Coverage: **36.4 %** (893 / 2451 Zeilen)
- Dateien mit Coverage < 60 %:

  | Datei | Coverage |
  |-------|:--------:|
  | `application/use_cases/book_time.py` | 0 % |
  | `infrastructure/time_monitor.py` | 0 % |
  | `infrastructure/hardware/__init__.py` | 0 % |
  | `infrastructure/hardware/evdev_reader.py` | 0 % |
  | `infrastructure/hardware/ports.py` | 0 % |
  | `infrastructure/hardware/simulator.py` | 0 % |
  | `infrastructure/hardware/uid_hash.py` | 0 % |
  | `presentation/terminal_ui/booking_loop.py` | 0 % |
  | `presentation/terminal_ui/main.py` | 0 % |
  | `domain/services/booking_rules.py` | 14 % |
  | `infrastructure/export/csv_exporter.py` | 15 % |
  | `infrastructure/export/pdf_report_service.py` | 19 % |
  | `domain/services/compliance_checks.py` | 22 % |
  | `application/use_cases/approve_supplement.py` | 22 % |
  | `presentation/admin_cli/system.py` | 25 % |
  | `infrastructure/system_check.py` | 26 % |
  | `infrastructure/backup/backup_service.py` | 26 % |
  | `infrastructure/export/report_queries.py` | 26 % |
  | `presentation/admin_cli/user_accounts.py` | 28 % |
  | `presentation/admin_cli/_intervals.py` | 29 % |
  | `infrastructure/db/unit_of_work.py` | 31 % |
  | `presentation/admin_cli/schedule.py` | 32 % |
  | `application/use_cases/correct_booking.py` | 33 % |
  | `application/use_cases/manage_work_schedule.py` | 34 % |
  | `presentation/admin_cli/reports.py` | 35 % |
  | `application/use_cases/reject_supplement.py` | 35 % |
  | `infrastructure/db/repositories/work_schedule.py` | 38 % |
  | `application/use_cases/register_supplement.py` | 39 % |
  | `domain/entities.py` | 42 % |
  | `infrastructure/db/repositories/time_booking.py` | 43 % |
  | `presentation/admin_cli/bookings.py` | 46 % |
  | `infrastructure/db/repositories/_helpers.py` | 50 % |
  | `infrastructure/db/repositories/supplement.py` | 52 % |
  | `infrastructure/db/repositories/booking_correction.py` | 52 % |
  | `infrastructure/db/repositories/user_account.py` | 53 % |
  | `infrastructure/db/repositories/employee.py` | 54 % |
  | `infrastructure/db/repositories/rfid_card.py` | 56 % |
  | `infrastructure/db/repositories/review_case.py` | 58 % |
  | `infrastructure/db/repositories/system_config.py` | 58 % |

## Maßnahmenplan

1. Security-Funde mit HIGH/MEDIUM-Schwere priorisiert beheben (0 HIGH, 1 MEDIUM).
2. Linting-Fehler beheben (65 Befunde in Ruff-Prüfung).
3. Komplexe Funktionen refaktorieren (CC ≥ 15): `Supplement`, `Supplement.__post_init__`, `ApproveSupplementUseCase.execute`.
4. Tests für Module mit Coverage < 60 % ergänzen (39 Dateien betroffen, Gesamt-Coverage: 36.4 %).
