# Planung Phase 3 – Application (abgeschlossen)

Stand: 2026-05-21. Alle Entscheidungen aus der Design-Session phase3_01.md / phase3_02.md
sowie den Klärungsgesprächen sind hier eingearbeitet.

---

## Architekturentscheidungen

### BookingStatus-Semantik

Der Status beschreibt die einzelne Buchung, nicht den Gesamtstatus des Tages.

| Buchungstyp  | Status            | Bedingung                                                    |
|--------------|-------------------|--------------------------------------------------------------|
| COME         | OPEN              | immer – Arbeitsphase beginnt, bleibt offen                   |
| BREAK_START  | OPEN              | immer – Pause beginnt, bleibt offen                          |
| BREAK_END    | OK                | Pause konsistent geschlossen, keine Compliance-Flags         |
| BREAK_END    | WARN/NEEDS_REVIEW | Compliance-Flags nach Einfügen in den projizierten Verlauf   |
| GO           | OK                | keine Compliance-Flags                                       |
| GO           | WARN              | Flags mittlerer Schwere (ReviewSeverity.WARN)                |
| GO           | NEEDS_REVIEW      | Flags kritischer Schwere oder ungewöhnliche Konstellation    |
| –            | CORRECTED         | ausschließlich durch CorrectBookingUseCase, nie BookUseCase  |

WARN = Hinweis-Funktion, kein zwingender Human-Review.
NEEDS_REVIEW = zwingend in die Prüf-Pipeline.


### booking_status_history – Infrastruktur-Seiteneffekt

`time_booking_repo.set_status(booking_id, status, reason, changed_by_user_id)` schreibt
`time_bookings.current_status` und `booking_status_history` in einer DB-Transaktion.
Kein eigener `BookingStatusHistoryRepository`-Port in der Application-Schicht.
`FakeTimeBookingRepository.set_status()` aktualisiert nur die Entity per
`dataclasses.replace()` – kein History-Eintrag in Fakes (Infrastruktur-Verhalten).


### device_event_id – Verantwortungsteilung

Hardware-/Infrastruktur-Schicht erzeugt `device_events` vor dem Use-Case-Aufruf.
`BookCommand.device_event_id: int | None` wird 1:1 an `TimeBooking.device_event_id`
durchgereicht. Schema-Spalte `time_bookings.device_event_id` wurde über Migration 0005
ergänzt (Plan nannte irrtümlich 0004).


### FakeUnitOfWork.__exit__

Ruft `rollback()` bei Exception, damit Tests das reale Transaktionsverhalten
widerspiegeln.


### Transaktionsregel

Alle schreibenden Use-Case-Vorgänge folgen dem Muster:
Fachobjekte schreiben → `uow.commit()` → `audit_log_repo.add()` via auditconn.

Grund: `auditconn` ist eine separate SQLite-Verbindung im Autocommit-Modus.
Solange die Haupttransaktion noch einen RESERVED-Lock hält, kann `auditconn`
trotz WAL nicht schreiben. Der `AuditLogEntry` wird daher stets __nach__
`uow.commit()` geschrieben, nicht davor.
(Historischer Plantext lautete „alle Fachobjekte + AuditLogEntry in einem commit" —
durch E2E-/Integrationstests als SQLite-Locking-Problem erkannt und korrigiert.)


---

## Vorbereitungen (bereits vor Phase-3-Start umgesetzt)

- `BookingStatus` bereinigt: nur OK, OPEN, WARN, NEEDS_REVIEW, CORRECTED, CLOSED_WITH_NOTE
- Migration 0003: CHECK-Constraints in `time_bookings` und `booking_status_history` bereinigt
- `TimeBookingRepository.update_status` → `set_status(booking_id, status, reason, changed_by_user_id)`
- `InactiveEmployeeError` in `errors.py` ergänzt


---

## Zielstruktur (Ist-Stand)

```
src/arbeitszeit/application/
├── __init__.py
├── unit_of_work.py
├── commands.py
├── results.py
└── use_cases/
    ├── __init__.py
    ├── manage_work_schedule.py
    ├── register_supplement.py
    ├── correct_booking.py
    ├── book_time.py
    ├── approve_supplement.py   ← Phase 4 vorimplementiert in Phase 3
    └── reject_supplement.py    ← Phase 4 vorimplementiert in Phase 3

tests/application/
├── __init__.py
├── fakes.py
├── test_manage_work_schedule.py
├── test_register_supplement.py
├── test_correct_booking.py
├── test_book_time.py
├── test_approve_supplement.py   ← Phase 4 vorimplementiert in Phase 3
└── test_reject_supplement.py    ← Phase 4 vorimplementiert in Phase 3
```


---

## Implementierte Komponenten

### unit_of_work.py

`UnitOfWork` als `typing.Protocol` mit allen 10 Repository-Attributen:
`employee_repo`, `user_account_repo`, `rfid_card_repo`, `time_booking_repo`,
`work_schedule_repo`, `review_case_repo`, `supplement_repo`,
`booking_correction_repo`, `audit_log_repo`, `system_config_repo`
+ `commit()`, `rollback()`, `__enter__()`, `__exit__()`


### commands.py

Alle Commands als `@dataclass(frozen=True, slots=True)`.

Geplante Phase-3-Commands:

- `BookCommand`: uid_hash, terminal_id, booking_type, booked_at,
  device_event_id: int | None, source: BookingSource = TERMINAL
- `CreateSupplementCommand`: employee_id, related_booking_id: int | None,
  booking_type, event_at, recorded_at, reason, recorded_by_user_id
- `CreateCorrectionCommand`: original_booking_id, corrected_by_user_id,
  reason, new_booking_type, new_booked_at
- `ChangeWorkScheduleCommand`: scope_type, scope_employee_id: int | None,
  weekday (1=Mo–7=So), start_time, end_time, valid_from,
  change_origin, changed_by_user_id: int | None, reason: str | None

Vorimplementierte Phase-4-Commands:

- `ApproveSupplementCommand`: supplement_id, approving_user_id
- `RejectSupplementCommand`: supplement_id, rejected_by_user_id, reason


### results.py

Alle Results als `@dataclass(frozen=True, slots=True)`.

Geplante Phase-3-Results:

- `BookResult`: booking_id, status: BookingStatus, follow_up_case_ids: tuple[int, ...]
- `SupplementResult`: supplement_id, review_case_id: int | None
- `CorrectionResult`: correction_id, updated_booking_id, review_case_id: int | None
- `WorkScheduleChangeResult`: new_version_id, superseded_version_id: int | None

Vorimplementierte Phase-4-Results:

- `ApproveSupplementResult`: supplement_id, booking_id, booking_status,
  follow_up_case_ids: tuple[int, ...]
- `RejectSupplementResult`: supplement_id, review_case_id: int | None


### tests/application/fakes.py

In-Memory-Implementierungen aller 10 Repository-Interfaces.
`FakeUnitOfWork` mit `committed: bool`, `rolled_back: bool`, Rollback bei Exception.
`FakeTimeBookingRepository.set_status()`: `dataclasses.replace()`, kein History-Eintrag.
`FakeWorkScheduleRepository.get_effective()`: EMPLOYEE-Scope hat Vorrang vor GLOBAL.
Typkompatibilitätsprüfung am Dateiende.


---

## Use Cases

### manage_work_schedule.py

`ManageWorkScheduleUseCase(uow).execute(cmd) → WorkScheduleChangeResult`

1. Rollenprüfung: `changed_by_user_id` nicht None, User existiert, aktiv, Rolle ADMIN
   → `PermissionDeniedError` sonst
2. `get_effective(weekday, valid_from, scope_employee_id)` → current
3. `ConflictError` wenn `current.valid_from == cmd.valid_from`
4. `ValidationError` wenn eine bestehende Version `valid_from > cmd.valid_from` hat
   (Rückwärts-Insertion)
5. `close_version(current.id, cmd.valid_from - timedelta(days=1))`
6. Neue `WorkScheduleVersion` anlegen, `work_schedule_repo.add()`
7. `uow.commit()`
8. `AuditLogEntry` (audit_events.WORK_SCHEDULE_CHANGED)  ← nach commit, via auditconn

Rollenprüfung in Phase 3 bereits implementiert (Plan sah Phase 4/Schritt 1c vor).


### register_supplement.py

`RegisterSupplementUseCase(uow).execute(cmd) → SupplementResult`

1. Rollenprüfung: Rolle in {ADMIN, REVIEWER}
2. `employee_repo.get_by_id()` → `NotFoundError`; inaktiv → `InactiveEmployeeError`
3. `related_booking_id`: wenn gesetzt, Buchung muss existieren → `NotFoundError`
4. `Supplement(..., approval_status=PENDING)` anlegen
5. `ReviewCase(MANUAL_ENTRY_REVIEW)` immer anlegen
6. `uow.commit()`
7. `AuditLogEntry` (audit_events.SUPPLEMENT_CREATED)  ← nach commit, via auditconn

Rollenprüfung in Phase 3 bereits implementiert.


### correct_booking.py

`CorrectBookingUseCase(uow).execute(cmd) → CorrectionResult`

1. Rollenprüfung: Rolle in {ADMIN, REVIEWER}
2. `time_booking_repo.get_by_id()` → `NotFoundError`
3. Mitarbeiter-Lookup → `NotFoundError`; inaktiv → `InactiveEmployeeError`
4. `BookingCorrection` anlegen (old_booking_type, old_booked_at, new_booking_type, new_booked_at)
5. `set_status(booking.id, CORRECTED, ...)`
6. Selektive ReviewCase-Schließung: nur `_CORRECTABLE_CASE_TYPES`
   (OPEN_WORK_PHASE, OPEN_BREAK_PHASE, IMPLAUSIBLE_SEQUENCE, POSSIBLE_BREAK_VIOLATION,
   POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION, OUTSIDE_SCHEDULE_WINDOW).
   MANUAL_ENTRY_REVIEW bleibt offen (gehört zum Nachtragsprozess).
7. `uow.commit()`
8. `AuditLogEntry` (audit_events.BOOKING_CORRECTED)  ← nach commit, via auditconn

Rollenprüfung in Phase 3 bereits implementiert.


### book_time.py

`BookUseCase(uow).execute(cmd) → BookResult`

1. Karte prüfen: unbekannt → AuditLog + `UnknownCardError`;
   inaktiv → AuditLog + `InactiveCardError`
2. Mitarbeiter: `NotFoundError`; inaktiv → `InactiveEmployeeError`
3. `list_for_employee_on_day(...)` → day_bookings
4. `validate_booking_sequence(...)` → `InvalidBookingSequenceError` / `OpenPhaseConflictError`
5. Status bestimmen: COME/BREAK_START → OPEN; GO/BREAK_END:
   - `check_break_compliance(projected)` + `check_max_hours(projected)`
   - `check_rest_period(last_go, next_come)` mit Vortagesbuchungen
     (Plan: deferred auf Phase 4/Schritt 1b — tatsächlich in Phase 3 implementiert)
   - Regelzeitfenster-Check: `get_effective(...)` → außerhalb → OUTSIDE_SCHEDULE_WINDOW ReviewCase
     (Plan: nicht explizit für Phase 3 — tatsächlich in Phase 3 implementiert)
   - kein Flag → OK; WARN-Flag → WARN; CRITICAL-Flag → NEEDS_REVIEW
6. `TimeBooking` mit Status + `device_event_id` anlegen
7. Pro `ComplianceFlag` einen `ReviewCase` anlegen
8. `uow.commit()`
9. `AuditLogEntry` (audit_events.TIME_BOOKED)  ← nach commit, via auditconn


### approve_supplement.py (Phase 4, in Phase 3 vorimplementiert)

`ApproveSupplementUseCase(uow).execute(cmd) → ApproveSupplementResult`

1. Rollenprüfung: Rolle in {REVIEWER, ADMIN}
2. `get_by_id()` → `NotFoundError`; nicht PENDING → `ValidationError`
3. Mitarbeiter: `NotFoundError`; inaktiv → `InactiveEmployeeError`
4. `supplement_repo.approve()`
5. MANUAL_ENTRY_REVIEW-Fall schließen (RESOLVED)
6. Tagesbuchungen + Vortagesbuchungen laden; vollständige Statuslogik wie in BookUseCase
   (source=BookingSource.MANUAL); TimeBooking anlegen
7. Pro ComplianceFlag ReviewCase anlegen
8. `uow.commit()`
9. `AuditLogEntry` (audit_events.SUPPLEMENT_APPROVED)  ← nach commit, via auditconn


### reject_supplement.py (Phase 4, in Phase 3 vorimplementiert)

`RejectSupplementUseCase(uow).execute(cmd) → RejectSupplementResult`

1. Rollenprüfung: Benutzer nicht gefunden (`None`), inaktiv oder Rolle nicht in {REVIEWER, ADMIN} → `PermissionDeniedError`
2. `get_by_id()` → `NotFoundError`; nicht PENDING → `ValidationError`
3. `supplement_repo.reject()`
4. Wenn `supplement.related_booking_id is not None`: den passenden `MANUAL_ENTRY_REVIEW`-Fall
   (`case.booking_id == supplement.related_booking_id`) mit `CLOSED_WITH_NOTE` schließen.
   Ist `related_booking_id` None, bleibt kein Fall zu schließen.
5. `uow.commit()`
6. `AuditLogEntry` (audit_events.SUPPLEMENT_REJECTED mit reason)  ← nach commit, via auditconn


---

## Rollenprüfung (Pflichtenheft v3 §5 / Regelwerk v3 §16)

Plan sah Nachrüstung in Phase 4/Schritt 1c vor — tatsächlich bereits in Phase 3 umgesetzt.

| Use Case                  | Erlaubte Rollen    |
|---------------------------|--------------------|
| ManageWorkScheduleUseCase | ADMIN              |
| RegisterSupplementUseCase | ADMIN, REVIEWER    |
| CorrectBookingUseCase     | ADMIN, REVIEWER    |
| ApproveSupplementUseCase  | REVIEWER, ADMIN    |
| RejectSupplementUseCase   | REVIEWER, ADMIN    |
| BookUseCase               | keine (via Karte)  |


---

## Testverteilung Phase 3

```
tests/application/test_manage_work_schedule.py  – 20 Tests
tests/application/test_register_supplement.py   – 17 Tests
tests/application/test_correct_booking.py       – 15 Tests
tests/application/test_book_time.py             – 21 Tests
tests/application/test_approve_supplement.py    – 21 Tests  (Phase 4 vorimpl.)
tests/application/test_reject_supplement.py     – 13 Tests  (Phase 4 vorimpl.)
Gesamt tests/application/                       – 107 Tests
```


---

## Verifikation

```
pytest tests/domain/       # 63 Tests grün (Phase 2)
pytest tests/application/  # 107 Tests grün
pytest tests/              # alle Tests grün inkl. Migrationen
```


---

## V3 §16 Testpflicht-Abdeckung nach Phase 3

```
>6h ohne Pause              → test_compliance_checks.py  (grün)
>9h ohne ausreichende Pause → test_compliance_checks.py  (grün)
>8h Arbeitszeit             → test_compliance_checks.py + test_book_time.py  (grün)
>10h Arbeitszeit            → test_compliance_checks.py + test_book_time.py  (grün)
Ruhezeitverletzung <11h     → test_book_time.py  (grün — in Phase 3 vorimpl.)
Systemzeitabweichung        → OFFEN (Phase 5, Regelwerk v3 §21)
Notfallnachtrag             → test_register_supplement.py  (grün)
Restore-Test                → tests/e2e/test_backup.py  (Phase 4/7)
Auswertung offener Fälle    → test_export.py / test_pdf.py  (Phase 4/8)
```
