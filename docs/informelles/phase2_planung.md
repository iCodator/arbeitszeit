Phase 2 – Domäne (abgeschlossen)
=================================

Ziel
----
Vollständiges, infrastrukturfreies Domänenmodell: Enums, Fehler, Entitäten,
Businessregeln und Repository-Protokolle. Keine Datenbank, keine Anwendungsfälle.


Zielstruktur
------------
src/arbeitszeit/domain/
├── __init__.py
├── enums.py
├── errors.py
├── entities.py
├── ports/
│   ├── __init__.py
│   └── repositories.py
└── services/
    ├── __init__.py
    ├── booking_rules.py
    └── compliance_checks.py


enums.py  – 11 StrEnum-Klassen
-------------------------------
Alle Enums erben von StrEnum (Python 3.11+), sodass .value ein String ist
und JSON-Serialisierung ohne Konvertierung möglich wird.

BookingType       COME, GO, BREAK_START, BREAK_END
BookingStatus     OPEN, OK, WARN, NEEDS_REVIEW, CORRECTED, CLOSED_WITH_NOTE
                  (CLOSED_WITH_NOTE wurde in Phase 3 ergänzt; V3 Regelwerk §11)
ReviewCaseType    MANUAL_ENTRY_REVIEW, POSSIBLE_MAX_HOURS_VIOLATION,
                  BREAK_COMPLIANCE_ISSUE, REST_PERIOD_VIOLATION
ReviewCaseStatus  OPEN, IN_REVIEW, RESOLVED, CLOSED_WITH_NOTE
ReviewSeverity    INFO, WARN, CRITICAL
CardStatus        ACTIVE, INACTIVE, LOST
UserRole          EMPLOYEE, ADMIN, REVIEWER, TECH
BookingSource     TERMINAL, MANUAL, SYSTEM
ChangeOrigin      SYSTEM_SEED, ADMIN_UI, MIGRATION
ApprovalStatus    PENDING, APPROVED, REJECTED
ScopeType         GLOBAL, EMPLOYEE


errors.py  – 1 Basisklasse + 9 Subklassen
------------------------------------------
DomainError(Exception)
  __init__(message="", **context): speichert context-Dict für strukturierte
  Fehlerinformation ohne String-Parsing durch den Aufrufer

UnknownCardError(DomainError)      RFID-Hash unbekannt
InactiveCardError(DomainError)     Karte bekannt, aber nicht ACTIVE
InactiveEmployeeError(DomainError) Mitarbeiter ist inaktiv
InvalidBookingSequenceError(DomainError)  fachlich unzulässige Buchungsfolge
OpenPhaseConflictError(DomainError)  Offene Phase bei GO (Pause nicht geschlossen)
PermissionDeniedError(DomainError) Autorisierungsfehler
ValidationError(DomainError)       Allgemeiner Validierungsfehler
NotFoundError(DomainError)         Entität nicht gefunden
ConflictError(DomainError)         Kollision (z.B. gleiche valid_from)


entities.py  – 9 frozen Dataclasses
--------------------------------------
Alle Entitäten: @dataclass(frozen=True, slots=True).
Invarianten werden in __post_init__ geprüft und werfen ValueError.
Fachliche Checks (Buchungsfolge, Compliance) gehören in services/, nicht hier.

Employee
  id, personnel_no, first_name, last_name, is_active: bool
  Keine Invariante – alle Felder orthogonal.

UserAccount
  id, username, password_hash, role: UserRole, employee_id: int | None
  Keine Invariante – employee_id None erlaubt (System-Accounts).

RfidCard
  id, uid_hash, employee_id, status: CardStatus,
  valid_from: date, valid_until: date | None,
  replaced_by_card_id: int | None
  Invariante: valid_until >= valid_from (wenn valid_until gesetzt).

TimeBooking
  id, employee_id, booking_type: BookingType, booked_at: datetime,
  source: BookingSource, status: BookingStatus,
  terminal_id: int | None, rfid_card_id: int | None,
  device_event_id: int | None, note: str | None
  Keine Invariante – Status wird durch Use Case gesetzt.

WorkScheduleVersion
  id, scope_type: ScopeType, scope_employee_id: int | None,
  weekday: int (0=Mo–6=So), start_time: time, end_time: time,
  valid_from: date, valid_until: date | None,
  change_origin: ChangeOrigin, changed_by_user_id: int | None,
  reason: str | None
  Invarianten:
  - scope_type == EMPLOYEE → scope_employee_id nicht None
  - scope_type == GLOBAL  → scope_employee_id muss None sein
  - end_time > start_time
  - valid_until >= valid_from (wenn valid_until gesetzt)

ReviewCase
  id, employee_id, case_type: ReviewCaseType, severity: ReviewSeverity,
  status: ReviewCaseStatus, description: str,
  booking_id: int | None, note: str | None,
  created_at: datetime, closed_at: datetime | None,
  closed_by_user_id: int | None
  Invariante: Status-Konsistenz mit Schließungsdaten:
  - OPEN / IN_REVIEW → closed_at und closed_by_user_id müssen None sein
  - RESOLVED / CLOSED_WITH_NOTE → closed_at und closed_by_user_id müssen gesetzt sein

Supplement
  id, employee_id, related_booking_id: int | None,
  booking_type: BookingType, event_at: datetime, recorded_at: datetime,
  reason: str, recorded_by_user_id: int, approval_status: ApprovalStatus,
  approved_by_user_id: int | None, approved_at: datetime | None,
  rejected_by_user_id: int | None, rejected_at: datetime | None
  Invarianten (ApprovalStatus ↔ Freigabe-/Ablehnungsdaten):
  - PENDING   → approved_* und rejected_* alle None
  - APPROVED  → approved_by_user_id und approved_at gesetzt, rejected_* None
  - REJECTED  → rejected_by_user_id und rejected_at gesetzt, approved_* None

BookingCorrection
  id, original_booking_id, corrected_by_user_id, reason: str,
  old_booking_type: BookingType, old_booked_at: datetime,
  new_booking_type: BookingType, new_booked_at: datetime,
  created_at: datetime
  Keine Invariante – historischer Datensatz, alle Felder pflichtend.

AuditLogEntry
  id, event_type: str, object_type: str, object_id: int,
  user_id: int | None, employee_id: int | None,
  event_at: datetime, details_json: str
  Keine Invariante – Nachweis-Datensatz, write-once.


services/booking_rules.py
--------------------------
validate_booking_sequence(booking_type, day_bookings: Sequence[BookingType])
  → ValidationResult | raises InvalidBookingSequenceError | OpenPhaseConflictError

Regeln (day_bookings in chronologischer Reihenfolge):
  Leere Liste:
    COME → akzeptiert (erste Tagesbuchung)
    GO / BREAK_START / BREAK_END → InvalidBookingSequenceError

  COME:
    offene Arbeitsphase vorhanden → InvalidBookingSequenceError
    offene Pause vorhanden        → InvalidBookingSequenceError

  GO:
    keine offene Arbeitsphase → InvalidBookingSequenceError
    offene Pause vorhanden    → OpenPhaseConflictError (Pause zuerst schließen)

  BREAK_START:
    keine offene Arbeitsphase → InvalidBookingSequenceError
    offene Pause vorhanden    → InvalidBookingSequenceError

  BREAK_END:
    keine offene Pause        → InvalidBookingSequenceError

Hilfsfunktionen:
  _has_open_work(day_bookings) → bool   (COME ohne folgendes GO)
  _has_open_break(day_bookings) → bool  (BREAK_START ohne folgendes BREAK_END)

ValidationResult: @dataclass(frozen=True)
  accepted: bool, initial_status: BookingStatus,
  reason_code: str | None, follow_up_case_types: tuple[ReviewCaseType, ...]
  (Hinweis: initial_status und follow_up_case_types werden im Use Case
   nicht ausgewertet; Status und Compliance werden in _evaluate_booking
   bestimmt. ValidationResult ist primär ein Acknowledge-Objekt.)


services/compliance_checks.py
------------------------------
Drei Prüffunktionen; alle nehmen eine projizierte Buchungsliste
(Tagesbuchungen + neue Buchung als Placeholder) entgegen.
Alle fünf ArbZG-Prüfhilfen aus Pflichtenheft v3 §7.9 sind Pflichtanforderung.

check_break_compliance(bookings: list[TimeBooking]) → list[ComplianceFlag]
  Prüft zwei separate ArbZG §4-Schwellen (beide Pflicht laut V3 §7.9):

  1. >6h Arbeitszeit ohne jede Pause (ArbZG §4 Abs. 1, erste Schwelle)
  2. >9h Arbeitszeit ohne ausreichende Gesamtpause (ArbZG §4 Abs. 1, zweite Schwelle)

  Erzeugt BREAK_COMPLIANCE_ISSUE bei Unterschreitung.

check_max_hours(bookings: list[TimeBooking]) → list[ComplianceFlag]
  Prüft zwei separate ArbZG §3-Schwellen (beide Pflicht laut V3 §7.9):

  1. >8h werktäglich → WARN-Flag (ArbZG §3: Regelmaximum)
  2. >10h täglich → CRITICAL-Flag (ArbZG §3: absolutes Maximum)

  Erzeugt POSSIBLE_MAX_HOURS_VIOLATION bei Überschreitung.

check_rest_period(bookings_today, bookings_yesterday: list[TimeBooking])
  → list[ComplianceFlag]
  Prüft: Ruhezeit zwischen letztem GO gestern und erstem COME heute ≥ 11h.
  Erzeugt REST_PERIOD_VIOLATION bei Unterschreitung (ArbZG §5).
  V3 §7.9 PFLICHTANFORDERUNG – nicht optional.
  Deferred auf Phase 4 (Vortages-Kontext fehlt in Phase 3);
  Integration in BookUseCase + ApproveSupplementUseCase nach Schritt 1b Phase 4.

ComplianceFlag: @dataclass(frozen=True)
  case_type: ReviewCaseType, severity: ReviewSeverity, description: str

V3-Design-Entscheidung (Regelwerk v3 §11):
  POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION
  und MANUAL_ENTRY werden nicht als BookingStatus-Werte realisiert, sondern:
  - POSSIBLE_*: ReviewCase mit ReviewCaseType + ReviewSeverity (abfragbar, auswertbar)
  - MANUAL_ENTRY: BookingSource.MANUAL auf TimeBooking (kombinierbar mit OK/WARN/NEEDS_REVIEW)
  Diese Trennung ist fachlich ausdrucksstärker (Status und Herkunft orthogonal) und
  V3-konform: report_queries.py leitet alle Fakten konsistent ab (Regelwerk v3 §11).


ports/repositories.py  – 10 Protocol-Interfaces
-------------------------------------------------
Alle als typing.Protocol definiert. Keine Basisklasse, keine Vererbung.
Infrastruktur-Implementierungen in Phase 4; Fake-Implementierungen in
tests/application/fakes.py.

EmployeeRepository
  get_by_id(id) → Employee | None
  get_active_by_personnel_no(no) → Employee | None

UserAccountRepository
  get_by_id(id) → UserAccount | None
  get_by_username(username) → UserAccount | None

RfidCardRepository
  get_by_uid_hash(hash) → RfidCard | None          (beliebiger Status)
  get_active_by_uid_hash(hash) → RfidCard | None   (nur ACTIVE)
  get_by_id(id) → RfidCard | None

TimeBookingRepository
  add(booking) → TimeBooking
  get_by_id(id) → TimeBooking | None
  list_for_employee_on_day(id, day) → list[TimeBooking]
  list_open_for_employee(id) → list[TimeBooking]
  list_between(id, from_dt, to_dt) → list[TimeBooking]
  set_status(id, status, reason=None, changed_by_user_id=None) → None

WorkScheduleRepository
  add(version) → WorkScheduleVersion
  close_version(id, valid_until) → None
  get_effective(weekday, on_date, employee_id=None) → WorkScheduleVersion | None
    EMPLOYEE-Scope hat Vorrang vor GLOBAL
  list_versions(weekday=None, scope_employee_id=None) → list[WorkScheduleVersion]

ReviewCaseRepository
  add(case) → ReviewCase
  list_open_for_employee(id) → list[ReviewCase]
    (Status OPEN oder IN_REVIEW)
  resolve(case_id, status, closed_by_user_id, note=None) → None
    status: Literal[RESOLVED, CLOSED_WITH_NOTE]

SupplementRepository
  add(supplement) → Supplement
  get_by_id(id) → Supplement | None
  list_pending() → list[Supplement]
  approve(id, approved_by_user_id, approved_at) → None
  reject(id, rejected_by_user_id, rejected_at) → None

BookingCorrectionRepository
  add(correction) → BookingCorrection
  list_for_booking(booking_id) → list[BookingCorrection]

AuditLogRepository
  add(entry) → AuditLogEntry

SystemConfigRepository
  get_current(config_key) → str | None
  set_current(key, value_json, change_origin, changed_by_user_id, changed_at,
              reason=None) → None


Testverteilung Phase 2
-----------------------
tests/domain/test_entities.py        – 19 Invariantentests
tests/domain/test_booking_rules.py   – 10 Tests
tests/domain/test_compliance_checks.py – 9 Tests (inkl. check_rest_period)
Gesamt: 38 Tests (+ 6 Migrations = 44 aus der ursprünglichen Planungsnotiz;
  tatsächlich 53 domain+migration Tests nach Erweiterungen in Phase 3)
