# Faktenprüfung: Vorkommen von `OpenPhaseConflictError` und `validate_booking_sequence`

## Vorkommen von `OpenPhaseConflictError`

- [domain/errors.py:28](../../src/arbeitszeit/domain/errors.py) — **Definition** — Klasse `OpenPhaseConflictError(DomainError)`
- [domain/services/booking_rules.py:8](../../src/arbeitszeit/domain/services/booking_rules.py) — **Import** — innerhalb von `booking_rules.py`
- [domain/services/booking_rules.py:43](../../src/arbeitszeit/domain/services/booking_rules.py) — **Aufruf (raise)** — in `_validate_go()`: `raise OpenPhaseConflictError("GO bei offener Pause: Pause zuerst schließen.")`
- [presentation/terminal_ui/main.py:22](../../src/arbeitszeit/presentation/terminal_ui/main.py) — **Import** — in `main.py`
- [presentation/terminal_ui/main.py:60](../../src/arbeitszeit/presentation/terminal_ui/main.py) — **Verwendung** — Eintrag in `_DOMAIN_MESSAGES`-Dict zur Fehlermeldungsanzeige am Terminal
- [tests/domain/test_booking_rules.py:13](../../tests/domain/test_booking_rules.py) — Import (Test)
- [tests/domain/test_booking_rules.py:60](../../tests/domain/test_booking_rules.py) — Aufruf (Test)
- [tests/application/test_book_time.py:33](../../tests/application/test_book_time.py) — Import (Test)
- [tests/application/test_book_time.py:222](../../tests/application/test_book_time.py) — Aufruf (Test)
- [tests/application/test_approve_supplement.py:39](../../tests/application/test_approve_supplement.py) — Import (Test)
- [tests/application/test_approve_supplement.py:234](../../tests/application/test_approve_supplement.py) — Aufruf (Test) — `pytest.raises(OpenPhaseConflictError)` bei `ApproveSupplementUseCase.execute()`
- [tests/integration/test_terminal_ui_main.py:20](../../tests/integration/test_terminal_ui_main.py) — Import (Test)
- [tests/integration/test_terminal_ui_main.py:206](../../tests/integration/test_terminal_ui_main.py) — Aufruf (Test) — `side_effect=OpenPhaseConflictError(...)`

## Vorkommen von `validate_booking_sequence`

- [domain/services/booking_rules.py:12](../../src/arbeitszeit/domain/services/booking_rules.py) — **Definition** — Funktion `validate_booking_sequence(booking_type, day_bookings) -> None`
- [application/use_cases/book_time.py:25](../../src/arbeitszeit/application/use_cases/book_time.py) — **Import** — in `book_time.py`
- [application/use_cases/book_time.py:104](../../src/arbeitszeit/application/use_cases/book_time.py) — **Aktiver Aufruf** — in `BookUseCase.execute()`
- [application/use_cases/approve_supplement.py:27](../../src/arbeitszeit/application/use_cases/approve_supplement.py) — **Import** — in `approve_supplement.py`
- [application/use_cases/approve_supplement.py:56](../../src/arbeitszeit/application/use_cases/approve_supplement.py) — **Aktiver Aufruf** — in `ApproveSupplementUseCase.execute()`
- [tests/domain/test_booking_rules.py:15](../../tests/domain/test_booking_rules.py) — Import (Test)
- [tests/domain/test_booking_rules.py:20–109](../../tests/domain/test_booking_rules.py) — Aufrufe (Test, 14 Stück)

## Aktive Aufrufpfade (nur produktiver Code, keine Tests)

**Terminal-/Buchungspfad: ja**

`validate_booking_sequence()` wird in `BookUseCase.execute()` aufgerufen
([book_time.py:104](../../src/arbeitszeit/application/use_cases/book_time.py)).
`BookUseCase` wird aus `booking_loop.py` aufgerufen. `OpenPhaseConflictError`
kann darüber ausgelöst werden (über `_validate_go()` →
[booking_rules.py:43](../../src/arbeitszeit/domain/services/booking_rules.py)).

**Administrativer Korrekturpfad:**

- `CorrectBookingUseCase.execute()`
  ([correct_booking.py:49](../../src/arbeitszeit/application/use_cases/correct_booking.py)):
  Kein Aufruf von `validate_booking_sequence()` oder `OpenPhaseConflictError`.
  Der Use Case führt keine Sequenz- oder Phasenprüfung durch.
- `RegisterSupplementUseCase`:
  Kein Aufruf von `validate_booking_sequence()` oder `OpenPhaseConflictError`.
  Keine Sequenzprüfung.
- `ApproveSupplementUseCase.execute()`
  ([approve_supplement.py:56](../../src/arbeitszeit/application/use_cases/approve_supplement.py)):
  Aktiver Aufruf von `validate_booking_sequence()`. `OpenPhaseConflictError`
  kann darüber ausgelöst werden — der Testfall
  [test_approve_supplement.py:234](../../tests/application/test_approve_supplement.py)
  belegt dies explizit.
- `RejectSupplementUseCase`:
  Kein Aufruf von `validate_booking_sequence()` oder `OpenPhaseConflictError`.
  Keine Sequenzprüfung.
- `ManageWorkScheduleUseCase`:
  Kein Aufruf von `validate_booking_sequence()` oder `OpenPhaseConflictError`.
  Keine Sequenzprüfung.

**Sonstiger Pfad: nein** — es gibt keine weiteren produktiven Aufrufstellen
außerhalb der beiden genannten Use Cases.

## Ergebnis

`OpenPhaseConflictError` wird im produktiven Code ausschließlich in
`_validate_go()` ([booking_rules.py:43](../../src/arbeitszeit/domain/services/booking_rules.py))
geraised. Diese Funktion ist über `validate_booking_sequence()` erreichbar,
das an genau zwei Stellen im produktiven Code aufgerufen wird: in
`BookUseCase.execute()` ([book_time.py:104](../../src/arbeitszeit/application/use_cases/book_time.py),
Terminal-/Buchungspfad) und in `ApproveSupplementUseCase.execute()`
([approve_supplement.py:56](../../src/arbeitszeit/application/use_cases/approve_supplement.py),
administrativer Pfad). `CorrectBookingUseCase`, `RegisterSupplementUseCase`,
`RejectSupplementUseCase` und `ManageWorkScheduleUseCase` enthalten weder einen
Aufruf von `validate_booking_sequence()` noch eine andere Sequenz- oder
Phasenprüfung. `OpenPhaseConflictError` ist damit im administrativen
Korrekturpfad ausschließlich über `ApproveSupplementUseCase` erreichbar —
nicht über `CorrectBookingUseCase` oder andere administrative Use Cases.
