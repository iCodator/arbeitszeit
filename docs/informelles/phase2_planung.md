Phase 2 – Domäne (abgeschlossen)
=================================

Ziel
----
Vollständiges, infrastrukturfreies Domänenmodell: Enums, Fehler, Entitäten,
Businessregeln und Repository-Protokolle. Keine Datenbank, keine Anwendungsfälle.


Zielstruktur
------------

```
src/arbeitszeit/domain/
├── __init__.py
├── enums.py
├── errors.py
├── entities.py
├── audit_events.py
├── ports/
│   ├── __init__.py
│   └── repositories.py
└── services/
    ├── __init__.py
    ├── booking_rules.py
    └── compliance_checks.py
```


enums.py – 11 StrEnum-Klassen
------------------------------
Alle Enums erben von StrEnum (Python 3.11+).

- `BookingType`       COME, GO, BREAK_START, BREAK_END
- `BookingStatus`     OPEN, OK, WARN, NEEDS_REVIEW, CORRECTED, CLOSED_WITH_NOTE
- `ReviewCaseType`    OPEN_WORK_PHASE, OPEN_BREAK_PHASE, OUTSIDE_SCHEDULE_WINDOW,
                      POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION,
                      POSSIBLE_MAX_HOURS_VIOLATION, IMPLAUSIBLE_SEQUENCE,
                      UNKNOWN_CARD_ATTEMPT, INACTIVE_CARD_ATTEMPT,
                      TIME_ANOMALY, MANUAL_ENTRY_REVIEW
- `ReviewCaseStatus`  OPEN, IN_REVIEW, RESOLVED, CLOSED_WITH_NOTE
- `ReviewSeverity`    INFO, WARN, CRITICAL
- `CardStatus`        ACTIVE, INACTIVE, REPLACED, LOST
- `UserRole`          EMPLOYEE, ADMIN, REVIEWER, TECH
- `BookingSource`     TERMINAL, MANUAL, IMPORT
- `ChangeOrigin`      SYSTEM_SEED, ADMIN_UI, MIGRATION
- `ApprovalStatus`    PENDING, APPROVED, REJECTED
- `ScopeType`         GLOBAL, EMPLOYEE

Finaler Phase-2-Stand (Abweichungen gegenüber Ursprungsplan):

- `BookingStatus` enthält ausschließlich: OPEN, OK, WARN, NEEDS_REVIEW,
  CORRECTED, CLOSED_WITH_NOTE. Fachliche Hinweislagen (POSSIBLE_BREAK_VIOLATION,
  POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION) und Herkunftskennzeichnung
  (MANUAL_ENTRY) sind KEINE BookingStatus-Werte. Ihre Realisierung erfolgt orthogonal:
  POSSIBLE_* → ReviewCaseType; MANUAL_ENTRY → BookingSource.MANUAL. (→ AP 1)
- `ReviewCaseType`: Plan nannte nur 4 Werte (MANUAL_ENTRY_REVIEW,
  POSSIBLE_MAX_HOURS_VIOLATION, BREAK_COMPLIANCE_ISSUE, REST_PERIOD_VIOLATION);
  tatsächlich 11 Werte implementiert. Finale Bezeichner: `POSSIBLE_BREAK_VIOLATION`
  und `POSSIBLE_REST_VIOLATION` (nicht BREAK_COMPLIANCE_ISSUE/REST_PERIOD_VIOLATION).
- `CardStatus`: REPLACED ergänzt (Plan hatte nur ACTIVE, INACTIVE, LOST).
- `BookingSource`: IMPORT statt SYSTEM.


errors.py – 1 Basisklasse + 9 Subklassen
-----------------------------------------

- `DomainError(Exception)` — mit `code`-Attribut und `context`-Dict
- `UnknownCardError(DomainError)` — RFID-Hash unbekannt
- `InactiveCardError(DomainError)` — Karte bekannt, aber nicht ACTIVE
- `InactiveEmployeeError(DomainError)` — Mitarbeiter ist inaktiv
- `InvalidBookingSequenceError(DomainError)` — fachlich unzulässige Buchungsfolge
- `OpenPhaseConflictError(DomainError)` — offene Phase bei GO
- `PermissionDeniedError(DomainError)` — Autorisierungsfehler
- `ValidationError(DomainError)` — allgemeiner Validierungsfehler
- `NotFoundError(DomainError)` — Entität nicht gefunden
- `ConflictError(DomainError)` — Kollision (z. B. gleiche valid_from)


entities.py – 9 frozen @dataclass
----------------------------------
Alle: `@dataclass(frozen=True, slots=True)`.
Invarianten in `__post_init__`, werfen `ValueError`.

**Employee**
  id, personnel_no, first_name, last_name, is_active: bool
  Invariante: `personnel_no` darf nicht leer oder nur Leerzeichen sein.
  (Plan: „Keine Invariante" — tatsächlich vorhanden.)

**UserAccount**
  id, username, password_hash, role: UserRole, employee_id: int | None, is_active: bool
  Invariante: `username` darf nicht leer oder nur Leerzeichen sein.
  (Plan: „Keine Invariante" — tatsächlich vorhanden.)

**RfidCard**
  id, uid_hash, employee_id, status: CardStatus,
  valid_from: date, valid_until: date | None, replaced_by_card_id: int | None
  Invariante: `valid_until >= valid_from` (wenn gesetzt).

**TimeBooking**
  id, employee_id, booking_type: BookingType, booked_at: datetime,
  source: BookingSource, status: BookingStatus,
  terminal_id: int | None, rfid_card_id: int | None,
  device_event_id: int | None, note: str | None
  Keine Invariante — Status wird durch Use Case gesetzt.

**WorkScheduleVersion**
  id, scope_type: ScopeType, scope_employee_id: int | None,
  weekday: int (1=Mo–7=So), start_time: time, end_time: time,
  valid_from: date, valid_until: date | None,
  change_origin: ChangeOrigin, changed_by_user_id: int | None, reason: str | None
  Invarianten:
  - GLOBAL → scope_employee_id muss None sein
  - EMPLOYEE → scope_employee_id darf nicht None sein
  - weekday muss zwischen 1 und 7 liegen
  - end_time > start_time
  - valid_until >= valid_from (wenn gesetzt)

**ReviewCase**
  id, employee_id, case_type: ReviewCaseType, severity: ReviewSeverity,
  status: ReviewCaseStatus, description: str,
  booking_id: int | None, note: str | None,
  created_at: datetime,  ← Python-Entity-Feld (DB-Spalte heißt detected_at; SQLiteReviewCaseRepository mappt detected_at → created_at)
  closed_at: datetime | None,
  closed_by_user_id: int | None
  Invarianten:
  - OPEN / IN_REVIEW → closed_at und closed_by_user_id müssen None sein
  - RESOLVED / CLOSED_WITH_NOTE → closed_at und closed_by_user_id müssen gesetzt sein
  - CLOSED_WITH_NOTE → note darf nicht leer sein

**Supplement**
  id, employee_id, related_booking_id: int | None,
  booking_type: BookingType, event_at: datetime, recorded_at: datetime,
  reason: str, recorded_by_user_id: int, approval_status: ApprovalStatus,
  approved_by_user_id: int | None, approved_at: datetime | None,
  rejected_by_user_id: int | None, rejected_at: datetime | None
  Invarianten:
  - PENDING → alle approved_* und rejected_* None
  - APPROVED → approved_by_user_id und approved_at gesetzt, rejected_* None;
               approved_at >= recorded_at
  - REJECTED → rejected_by_user_id und rejected_at gesetzt, approved_* None;
               rejected_at >= recorded_at

**BookingCorrection**
  id, original_booking_id, corrected_by_user_id, reason: str,
  old_booking_type: BookingType, old_booked_at: datetime,
  new_booking_type: BookingType, new_booked_at: datetime,
  created_at: datetime
  Invariante: created_at >= old_booked_at (Korrektur kann nicht vor Original liegen).
  (Plan: „Keine Invariante" — tatsächlich vorhanden.)

**AuditLogEntry**
  id, event_type: str, object_type: str, object_id: int,
  user_id: int | None, employee_id: int | None,
  event_at: datetime, details_json: str
  Keine Invariante — Nachweis-Datensatz, write-once.


audit_events.py
---------------
Zentraler Katalog aller Audit-Event-Typ-Konstanten (nicht im Ursprungsplan, sinnvolle Ergänzung).

Domänen-Kern-Events (originär Phase 2):
  TIME_BOOKED, BOOKING_REJECTED_UNKNOWN_CARD, BOOKING_REJECTED_INACTIVE_CARD,
  BOOKING_CORRECTED, SUPPLEMENT_CREATED, SUPPLEMENT_APPROVED, SUPPLEMENT_REJECTED,
  WORK_SCHEDULE_CHANGED.

Infrastruktur-Events (später ergänzt, Phase 4/Schritt 9b):
  BACKUP_CREATED, BACKUP_SYNCED_TO_NAS, BACKUP_SYNC_FAILED, RESTORE_COMPLETED.

Verhindert freie String-Literale im Code (Regelwerk v3 §11-konform).


services/booking_rules.py
--------------------------

`validate_booking_sequence(booking_type, day_bookings: Sequence[TimeBooking])`
→ `ValidationResult` | raises `InvalidBookingSequenceError` | `OpenPhaseConflictError`

Regeln (day_bookings in chronologischer Reihenfolge):

- Leere Liste: COME → akzeptiert; GO/BREAK_START/BREAK_END → InvalidBookingSequenceError
- COME: offene Arbeitsphase oder offene Pause vorhanden → InvalidBookingSequenceError
- GO: keine offene Arbeitsphase → InvalidBookingSequenceError;
      offene Pause → OpenPhaseConflictError
- BREAK_START: keine offene Arbeitsphase oder offene Pause vorhanden → InvalidBookingSequenceError
- BREAK_END: keine offene Pause → InvalidBookingSequenceError

Hilfsfunktionen: `_has_open_work(day_bookings)`, `_has_open_break(day_bookings)`

`ValidationResult`: @dataclass(frozen=True)
  accepted: bool, initial_status: BookingStatus,
  reason_code: str | None, follow_up_case_types: tuple[ReviewCaseType, ...]


services/compliance_checks.py
------------------------------
Pflichtanforderung Pflichtenheft v3 §7.9 (ArbZG §3/4/5).

`ComplianceFlag`: @dataclass(frozen=True)
  case_type: ReviewCaseType, severity: ReviewSeverity

`check_break_compliance(day_bookings: Sequence[TimeBooking]) → list[ComplianceFlag]`
  Nutzt `_work_stats()` für Nettoarbeitszeit, Gesamtpause, längsten ununterbrochenen Block.
  Zwei Schwellen (beide Pflicht, ArbZG §4):
  - >6h ununterbrochener Block ohne Pause → POSSIBLE_BREAK_VIOLATION, WARN
  - >9h Nettoarbeitszeit mit <45min Gesamtpause → POSSIBLE_BREAK_VIOLATION, CRITICAL
  - >6h Nettoarbeitszeit mit <30min Gesamtpause → POSSIBLE_BREAK_VIOLATION, WARN
  (Plan nannte `BREAK_COMPLIANCE_ISSUE` als case_type — tatsächlich `POSSIBLE_BREAK_VIOLATION`.)

`check_max_hours(day_bookings: Sequence[TimeBooking]) → list[ComplianceFlag]`
  Zwei Schwellen (ArbZG §3):
  - >10h Nettoarbeitszeit → POSSIBLE_MAX_HOURS_VIOLATION, CRITICAL
  - >8h Nettoarbeitszeit → POSSIBLE_MAX_HOURS_VIOLATION, WARN

`check_rest_period(last_go: datetime, next_come: datetime) → list[ComplianceFlag]`
  Finale Domänenschnittstelle: nimmt zwei datetime-Objekte entgegen (letzter GO-Zeitpunkt,
  nächster COME-Zeitpunkt) — nicht zwei Buchungslisten wie ursprünglich geplant.
  <11h zwischen letztem GO und nächstem COME → POSSIBLE_REST_VIOLATION, CRITICAL (ArbZG §5).
  V3 §7.9 Pflichtanforderung. Integration in BookUseCase + ApproveSupplementUseCase
  nach Phase 4/Schritt 1b.

Verbindliche Architekturentscheidung (Regelwerk v3 §11):
  POSSIBLE_* werden als ReviewCase (ReviewCaseType + ReviewSeverity) abgebildet,
  nicht als BookingStatus-Werte. MANUAL_ENTRY → BookingSource.MANUAL. Beide Dimensionen
  sind orthogonal zu BookingStatus. report_queries.py ist die einzige Ableitungsquelle
  für alle Ausgabekanäle (CSV, PDF, UI-Pflichtauswertungen). Direkte Ad-hoc-Queries
  außerhalb von report_queries.py sind architektonisch verboten.


ports/repositories.py – 10 Protocol-Interfaces
-----------------------------------------------
Alle als `typing.Protocol`. Infrastruktur-Implementierungen in Phase 4.

**EmployeeRepository**
  `get_by_id(id) → Employee | None`
  `get_active_by_personnel_no(no) → Employee | None`

**UserAccountRepository**
  `get_by_id(id) → UserAccount | None`
  `get_by_username(username) → UserAccount | None`

**RfidCardRepository**
  `get_by_uid_hash(hash) → RfidCard | None`         (beliebiger Status)
  `get_active_by_uid_hash(hash) → RfidCard | None`  (nur ACTIVE)
  `get_by_id(id) → RfidCard | None`

**TimeBookingRepository**
  `add(booking) → TimeBooking`
  `get_by_id(id) → TimeBooking | None`
  `list_for_employee_on_day(id, day) → list[TimeBooking]`  (chronologisch sortiert)
  `list_open_for_employee(id) → list[TimeBooking]`
  `list_between(id, from_dt, to_dt) → list[TimeBooking]`
  `set_status(id, status, reason=None, changed_by_user_id=None) → None`

**WorkScheduleRepository**
  `add(version) → WorkScheduleVersion`
  `close_version(id, valid_until) → None`
  `get_effective(weekday, on_date, employee_id=None) → WorkScheduleVersion | None`
    EMPLOYEE-Scope hat Vorrang vor GLOBAL
  `list_versions(weekday=None, scope_employee_id=None) → list[WorkScheduleVersion]`

**ReviewCaseRepository**
  `add(case) → ReviewCase`
  `list_open_for_employee(id) → list[ReviewCase]`  (Status OPEN oder IN_REVIEW)
  `resolve(case_id, status, closed_by_user_id, note=None) → None`

**SupplementRepository**
  `add(supplement) → Supplement`
  `get_by_id(id) → Supplement | None`
  `list_pending() → list[Supplement]`
  `approve(id, approved_by_user_id, approved_at) → None`
  `reject(id, rejected_by_user_id, rejected_at) → None`

**BookingCorrectionRepository**
  `add(correction) → BookingCorrection`
  `list_for_booking(booking_id) → list[BookingCorrection]`

**AuditLogRepository**
  `add(entry) → AuditLogEntry`

**SystemConfigRepository**
  `get_current(config_key) → str | None`
  `set_current(key, value_json, change_origin, changed_by_user_id, changed_at, reason=None) → None`


Testverteilung Phase 2
-----------------------

```
tests/domain/test_entities.py          – 42 Tests  (Plan: 19)
tests/domain/test_booking_rules.py     – 10 Tests  (Plan: 10 ✓)
tests/domain/test_compliance_checks.py –  9 Tests  (Plan:  9 ✓)
tests/domain/test_audit_events.py      –  2 Tests  (neu, nicht im Plan)
Gesamt tests/domain/                   – 63 Tests  (Plan: 38/44)
```

test_entities.py hat 42 statt 19 Tests — tiefere Invarianten-Abdeckung,
insbesondere Supplement-Freigabe-/Ablehnungsdaten mit Zeitlichkeitsprüfung
und zusätzliche Edge Cases für ReviewCase und WorkScheduleVersion.


Abgrenzung Phase-2-Leistungsumfang vs. Gesamtsystem
-----------------------------------------------------

Phase 2 schließt den Domänenkern fachlich ab: Enums, Entitäten, Businessregeln,
Compliance-Checks und Repository-Protokolle liegen vollständig vor.

Was Phase 2 allein nicht leistet:

- Die vollständige Berichtskonsistenz (normierte Projektion aller Status, Korrekturen
  und Nachträge für Pflichtauswertungen) ist erst im Zusammenspiel mit
  report_queries.py (Phase 4/Schritt 8a) abschließend nachgewiesen.
- Die Ruhezeitprüfung check_rest_period() ist in Phase 2 als Domänenfunktion
  vollständig; ihre Integration in den Buchungsfluss erfolgt erst in Phase 4/Schritt 1b,
  weil der Vortages-Kontext erst durch den TimeBookingRepository-Port verfügbar wird.
- Rollenprüfung in Use Cases gehört zur Application-Schicht (Phase 3/4), nicht Phase 2.

Ein Reviewer darf „Phase 2 vollständig" lesen als: Domänenkern abgeschlossen,
Invarianten getestet, Protokolle definiert — nicht als: Gesamtsystem auslieferbar.
