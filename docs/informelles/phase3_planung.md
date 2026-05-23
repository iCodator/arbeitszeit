# Planung Phase 3 – Application

Stand: 2026-05-21. Alle Entscheidungen aus der Design-Session phase3_01.md / phase3_02.md
sowie den Klärungsgesprächen sind hier eingearbeitet.

---

## Architekturentscheidungen

### BookingStatus-Semantik

Der Status beschreibt die einzelne Buchung, nicht den Gesamtstatus des Tages.

| Buchungstyp  | Status        | Bedingung                                                   |
|--------------|---------------|-------------------------------------------------------------|
| COME         | OPEN          | immer – Arbeitsphase beginnt, bleibt offen                  |
| BREAK_START  | OPEN          | immer – Pause beginnt, bleibt offen                         |
| BREAK_END    | OK            | Pause konsistent geschlossen, keine relevanten Flags im projizierten Tagesverlauf |
| BREAK_END    | WARN/NEEDS_REVIEW | Compliance-Flags nach Einfuegen der Buchung in den projizierten Tagesverlauf  |
| GO           | OK            | keine Compliance-Flags                                      |
| GO           | WARN          | Flags mittlerer Schwere (ReviewSeverity.WARN)               |
| GO           | NEEDS_REVIEW  | Flags kritischer Schwere oder ungewöhnliche Konstellation   |
| –            | CORRECTED     | ausschließlich durch CorrectBookingUseCase, nie BookUseCase |

WARN = Hinweis-Funktion, kein zwingender Human-Review.
NEEDS_REVIEW = zwingend in die Prüf-Pipeline.

Die offene Arbeitsphase nach BREAK_END hängt an der COME-Buchung, nicht an BREAK_END.


### booking_status_history – Infrastruktur-Seiteneffekt

time_booking_repo.set_status(booking_id, status, reason, changed_by_user_id) schreibt
time_bookings.current_status und booking_status_history in einer DB-Transaktion.
Kein eigener BookingStatusHistoryRepository-Port in der Application-Schicht.

Konsequenz: FakeTimeBookingRepository.set_status() aktualisiert nur die Entity per
dataclasses.replace(); kein History-Eintrag in Fakes (ist Infrastruktur-Verhalten).


### device_event_id – Verantwortungsteilung

- Hardware-/Infrastruktur-Schicht erzeugt device_events vor dem Use-Case-Aufruf.
- BookCommand.device_event_id: int | None wird 1:1 an TimeBooking.device_event_id
  durchgereicht. Kein eigener Port.
- Fakes führen das Feld im In-Memory-Store mit (Dummy-Wert oder None genügt).
- Schema-Spalte time_bookings.device_event_id wird in Phase 4 per Migration 0004
  ergänzt. In Phase 3 bleibt das Feld rein domaininternem Charakter.


### FakeUnitOfWork.__exit__

Ruft rollback() bei Exception, damit Tests das reale Transaktionsverhalten
widerspiegeln und nicht zu freundlich sind.


### Transaktionsregel

Alle schreibenden Use-Case-Vorgänge (Buchung, Nachtrag, Korrektur, Regelzeitänderung)
enden mit genau einem uow.commit(), der alle Fachobjekte + AuditLogEntry zusammenfasst.
supplement_repo.approve() / reject() ebenfalls immer mit AuditLogEntry in einer Transaktion.


---

## Vorbereitungen (bereits umgesetzt, vor Phase-3-Start)

- BookingStatus bereinigt: nur OK, OPEN, WARN, NEEDS_REVIEW, CORRECTED, CLOSED_WITH_NOTE
  (POSSIBLE_*-Werte und MANUAL_ENTRY NICHT als BookingStatus-Werte realisiert;
   Compliance via ReviewCase + Severity, Herkunft via BookingSource.MANUAL.
   V3-Design-Entscheidung: Regelwerk v3 §11 verlangt diese Werte als auswertbare
   fachliche Zustände — die Anforderung ist erfüllt, aber über ReviewCase und
   BookingSource statt als BookingStatus-Enum. Status und Herkunft sind orthogonal
   kombinierbar: MANUAL+WARN, MANUAL+OK etc. sind so möglich.)
- Migration 0003: Schema-CHECK-Constraints in time_bookings und booking_status_history
  entsprechend bereinigt
- TimeBookingRepository.update_status -> set_status(booking_id, status, reason, changed_by_user_id)
- InactiveEmployeeError in errors.py ergänzt
- errors.py: 9 Subklassen (inkl. InactiveEmployeeError)


---

## Zielstruktur

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
    └── book_time.py

tests/application/
├── __init__.py
├── fakes.py
├── test_manage_work_schedule.py
├── test_register_supplement.py
├── test_correct_booking.py
└── test_book_time.py


---

## Implementierungsreihenfolge

Reihenfolge bewusst von einfach nach komplex: book_time zuletzt, weil es die meiste
fachliche Last trägt (Kartenstatus, Mitarbeiterstatus, Sequenzprüfung, Compliance,
Statuslogik, ReviewCases, AuditLog).


### Schritt 1 – application/unit_of_work.py

UnitOfWork-Protocol mit Context-Manager-Support (alle 10 Repositories):

    class UnitOfWork(Protocol):
        employee_repo: EmployeeRepository
        user_account_repo: UserAccountRepository
        rfid_card_repo: RfidCardRepository
        time_booking_repo: TimeBookingRepository
        work_schedule_repo: WorkScheduleRepository
        review_case_repo: ReviewCaseRepository
        supplement_repo: SupplementRepository
        booking_correction_repo: BookingCorrectionRepository
        audit_log_repo: AuditLogRepository
        system_config_repo: SystemConfigRepository

        def commit(self) -> None: ...
        def rollback(self) -> None: ...
        def __enter__(self) -> "UnitOfWork": ...
        def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...


### Schritt 2 – application/commands.py

Alle Commands als @dataclass(frozen=True, slots=True).

BookCommand:
  uid_hash: str                          # RFID-Hash vom Terminal
  terminal_id: int
  booking_type: BookingType              # am Numpad gewählt, bevor Karte gelesen wird
  booked_at: datetime
  device_event_id: int | None            # von Hardware-Schicht gesetzt, Use Case reicht durch
  source: BookingSource = TERMINAL

CreateSupplementCommand:
  employee_id: int
  related_booking_id: int | None
  booking_type: BookingType
  event_at: datetime
  recorded_at: datetime
  reason: str
  recorded_by_user_id: int

CreateCorrectionCommand:
  original_booking_id: int
  corrected_by_user_id: int
  reason: str
  new_booking_type: BookingType
  new_booked_at: datetime

ChangeWorkScheduleCommand:
  scope_type: ScopeType
  scope_employee_id: int | None
  weekday: int              # 1=Mo bis 7=So (ISO-Wochentag, isoweekday())
  start_time: time
  end_time: time
  valid_from: date
  change_origin: ChangeOrigin
  changed_by_user_id: int | None
  reason: str | None


### Schritt 3 – application/results.py

Alle Results als @dataclass(frozen=True, slots=True).

BookResult:
  booking_id: int
  status: BookingStatus
  follow_up_case_ids: tuple[int, ...]

SupplementResult:
  supplement_id: int
  review_case_id: int | None

CorrectionResult:
  correction_id: int
  updated_booking_id: int
  review_case_id: int | None

WorkScheduleChangeResult:
  new_version_id: int
  superseded_version_id: int | None


### Schritt 4 – tests/application/fakes.py

In-Memory-Implementierungen aller 10 Repository-Interfaces.
Jedes Fake: dict[int, Entity] + Auto-Inkrement-ID.

FakeUnitOfWork:
  committed: bool
  rolled_back: bool
  __exit__ ruft rollback() bei Exception

FakeTimeBookingRepository.set_status():
  aktualisiert Entity per dataclasses.replace(); kein History-Eintrag
  (Infrastruktur-Seiteneffekt gehört nicht in Fakes)

FakeWorkScheduleRepository.get_effective():
  EMPLOYEE-Scope hat Vorrang vor GLOBAL

FakeWorkScheduleRepository.close_version():
  dataclasses.replace() loest __post_init__ aus
  -> valid_until < valid_from schlaegt fehl (Invariante wird in Fakes geprueft)


### Schritt 5 – use_cases/manage_work_schedule.py

ManageWorkScheduleUseCase(uow).execute(cmd) -> WorkScheduleChangeResult:

1. work_schedule_repo.get_effective(weekday, valid_from, scope_employee_id) -> current
2. ConflictError wenn current.valid_from == cmd.valid_from (unabhaengig von Zeiten)
3. ValidationError wenn fuer denselben Scope (scope_type + scope_employee_id) und
   denselben Wochentag bereits eine Version mit valid_from > cmd.valid_from existiert
   (Rueckwaerts-Insertion wuerde Ueberlappung erzeugen)
   -> list_versions(weekday=cmd.weekday, scope_employee_id=cmd.scope_employee_id)
      filtert bereits auf den relevanten Scope; keine globale Sperre
4. current schliessen: close_version(current.id, cmd.valid_from - timedelta(days=1))
   -> zuerst schliessen, dann neue Version anlegen; nie zwei gleichzeitig wirksame
      Versionen, auch nicht transient innerhalb der Transaktion
5. Neue WorkScheduleVersion anlegen, work_schedule_repo.add()
6. AuditLogEntry anlegen
7. uow.commit(), WorkScheduleChangeResult zurueckgeben

Testfaelle:
  - Neue Version wird angelegt -> new_version_id > 0, uow.committed
  - Bestehende Version wird geschlossen -> valid_until = new_valid_from - 1 Tag
  - Gleiche valid_from, andere Zeiten -> ConflictError
  - Identische Version -> ConflictError
  - Rueckwaerts-Insertion -> ValidationError
  - Audit-Log-Eintrag vorhanden


### Schritt 6 – use_cases/register_supplement.py

RegisterSupplementUseCase(uow).execute(cmd) -> SupplementResult:

1. employee_repo.get_by_id() -> NotFoundError bei unbekanntem Mitarbeiter
2. Supplement mit ApprovalStatus.PENDING anlegen, supplement_repo.add()
3. ReviewCase(MANUAL_ENTRY_REVIEW) anlegen – standardmaessig, nicht optional
4. AuditLogEntry anlegen – in derselben Transaktion
5. uow.commit(), SupplementResult zurueckgeben

Freigabe/Ablehnung: supplement_repo.approve() / reject() stets mit AuditLogEntry
in einer Transaktion – nie einzeln.

Architekturhinweis Freigabe:
Wenn ein genehmigter Nachtrag eine echte TimeBooking erzeugt (ApproveSupplementUseCase),
muss diese Buchung dieselbe Statuslogik durchlaufen wie eine Terminalbuchung:
OPEN/OK/WARN/NEEDS_REVIEW basierend auf dem projizierten Tagesverlauf.
Nachtraege duerfen fachlich nicht schwaecher geprueft werden als Echtzeitbuchungen.
Die Buchung erhaelt source = BookingSource.MANUAL und einen eigenen AuditLogEntry.

WICHTIG: Die blosse Repo-Freigabe (supplement_repo.approve()) ist kein fachlich
vollstaendiger Freigabeprozess. ApproveSupplementUseCase ist ein eigener geplanter
Use Case (Phase 3b oder Phase 4), der neben der Statusaenderung des Supplements
auch die Buchungserzeugung mit vollstaendiger Statuslogik und Auditierung umfasst.
Niemals als reines approve() ohne Buchungslogik umsetzen.

Testfaelle:
  - Unbekannter Mitarbeiter -> NotFoundError
  - Nachtrag erstellt + ReviewCase vorhanden
  - approval_status = PENDING, approved_by = None
  - Audit-Log-Eintrag vorhanden


### Schritt 7 – use_cases/correct_booking.py

CorrectBookingUseCase(uow).execute(cmd) -> CorrectionResult:

1. time_booking_repo.get_by_id() -> NotFoundError bei nicht existierender Buchung
2. BookingCorrection anlegen, booking_correction_repo.add()
   speichert old_booking_type, old_booked_at, new_booking_type, new_booked_at
3. time_booking_repo.set_status(booking.id, CORRECTED, reason=cmd.reason,
   changed_by_user_id=cmd.corrected_by_user_id)
4. Offene ReviewCase mit passendem booking_id schliessen – nicht pauschal alle
5. AuditLogEntry anlegen
6. uow.commit(), CorrectionResult zurueckgeben

Korrekturmodell: Die urspruengliche TimeBooking-Zeile wird nicht physisch
veraendert – sie erhaelt nur Status CORRECTED. Der neue Zustand (new_booking_type,
new_booked_at) ist ausschliesslich ueber BookingCorrectionRepository.
list_for_booking(booking_id) abfragbar. report_queries.py projiziert beide
Zustaende (alt/neu + Begruendung + Person + Zeitstempel) fuer Pflichtauswertungen.

Testfaelle:
  - Buchung nicht gefunden -> NotFoundError
  - Status = CORRECTED nach Korrektur
  - BookingCorrection-Datensatz enthaelt alte und neue Felder vollstaendig
  - Nur fachlich passende Review Cases werden geschlossen
  - Andere Review Cases desselben Mitarbeiters bleiben OPEN
  - Audit-Log-Eintrag vorhanden


### Schritt 8 – use_cases/book_time.py

BookUseCase(uow).execute(cmd) -> BookResult:

1. rfid_card_repo.get_by_uid_hash(cmd.uid_hash)
   -> None: UnknownCardError
   -> status != ACTIVE: InactiveCardError

2. employee_repo.get_by_id(card.employee_id)
   -> employee.is_active == False: InactiveEmployeeError

3. time_booking_repo.list_for_employee_on_day(employee.id, cmd.booked_at.date())
   -> day_bookings

4. validate_booking_sequence(cmd.booking_type, day_bookings)
   -> InvalidBookingSequenceError / OpenPhaseConflictError

5. Buchungsstatus bestimmen:
   COME, BREAK_START -> status = OPEN (immer)
   GO, BREAK_END:
     projected = day_bookings + [neues_booking_objekt]
     flags = check_break_compliance(projected) + check_max_hours(projected)
     Grundlage ist der projizierte Tagesverlauf nach Einfuegen der neuen Buchung.
     Pflichtenheft v3 §7.9 (ArbZG §5) verlangt zusaetzlich Pruefhinweise zur
     Ruhezeitunterschreitung (<11h zwischen letztem GO und naechstem COME).
     check_rest_period() benoetigt Buchungsdaten des Vortages, die in Phase 3 noch
     nicht aus dem UnitOfWork abgerufen werden -> Ruhezeitpruefung verschoben auf
     Phase 4/Schritt 1b. Dort folgt:
     prev = time_booking_repo.list_for_employee_on_day(employee.id, date - 1 Tag)
     flags += check_rest_period(projected, prev)
     V3 §7.9 PFLICHTANFORDERUNG (ArbZG §5) – keine optionale Erweiterung.
     Offene Testpflicht V3 §16: "Unterschreitung der Ruhezeit" erst nach Phase 4/Schritt 1b.
     kein Flag     -> OK
     WARN-Flag     -> WARN
     CRITICAL-Flag -> NEEDS_REVIEW

6. TimeBooking mit ermitteltem Status + device_event_id anlegen,
   time_booking_repo.add()

7. Pro ComplianceFlag einen ReviewCase anlegen, review_case_repo.add()

8. AuditLogEntry anlegen

9. uow.commit(), BookResult(booking_id, status, follow_up_case_ids) zurueckgeben

Testfaelle:
  - COME-Buchung -> status = OPEN, follow_up_case_ids leer
  - Unbekannte RFID-UID -> UnknownCardError
  - Inaktive Karte -> InactiveCardError
  - Aktive Karte, inaktiver Mitarbeiter -> InactiveEmployeeError
  - Erste Tagesbuchung als GO -> InvalidBookingSequenceError
  - BREAK_END ohne offene Pause -> InvalidBookingSequenceError
  - COME nach offenem COME -> InvalidBookingSequenceError
  - GO bei offener Pause -> OpenPhaseConflictError
  - GO nach >8h -> status = WARN, follow_up_case_ids nicht leer, Buchung gespeichert
  - GO nach >10h -> status = NEEDS_REVIEW, follow_up_case_ids nicht leer


---

## Verifikation

  pytest tests/domain/       # 44 Tests gruen (Regression Phase 2)
  pytest tests/application/  # alle Use-Case-Tests gruen
  pytest tests/               # alle Tests gruen inkl. Migrationen


## V3 §16 Testpflicht-Abdeckung nach Phase 3

  >6h ohne Pause              -> test_compliance_checks.py  (gruen)
  >9h ohne ausreichende Pause -> test_compliance_checks.py  (gruen)
  >8h Arbeitszeit             -> test_compliance_checks.py + test_book_time.py  (gruen)
  >10h Arbeitszeit            -> test_compliance_checks.py + test_book_time.py  (gruen)
  Ruhezeitverletzung          -> OFFEN (Phase 4/Schritt 1b, V3 §7.9 Pflicht)
  Systemzeitabweichung        -> OFFEN (Phase 5, Regelwerk v3 §21)
  Notfallnachtrag             -> test_register_supplement.py  (gruen)
  Restore-Test                -> tests/e2e/test_backup.py  (gruen nach Phase 4/7)
  Auswertung offener Faelle   -> OFFEN (Phase 4/8e)
