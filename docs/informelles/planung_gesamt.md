# Implementierungsplan: arbeitszeit

## Kontext

Die Dokumente unter `docs/informelles/` dokumentieren eine vollständige Design-Session für das Zeiterfassungssystem. Sie enthalten alle Entscheidungen zu Domänenmodell, Datenbankschema, Projektstruktur, Use-Cases und Testschnitt – alles abgestimmt auf das Pflichtenheft v3 und das Regelwerk v3.

**Verbindliche Referenzdokumente:** `docs/pflichtenheft_arbeitszeit_v3.md`, `docs/regelwerk_arbeitszeit_v3.md`

---

## Was die Dokumente festgelegt haben

### 01 – Fachlicher Kern
- Zentrum ist die **unveränderliche Buchung** (`Zeitbuchung`), nicht die „Tagesarbeitszeit"
- Offene Fälle werden **nicht automatisch geschlossen** – immer explizite Klärung
- Trennung: TerminalEreignis → Zeitbuchung (erst nach Prüfung)

### 02 – ER-Modell (5 Ebenen)
| Ebene | Entitäten |
| --- | --- |
| Person | `employees`, `user_accounts`, `rfid_cards` |
| Erfassung | `terminals`, `time_bookings`, `device_events` |
| Prüfung | `review_cases`, `review_case_actions`, `booking_status_history` |
| Änderung | `booking_corrections`, `supplements`, `work_schedule_versions` |
| Nachweis | `audit_log`, `system_events`, `system_config` |

### 03–09 – SQLite DDL
- **15 Tabellen** mit FK-Constraints, CHECK-Constraints, Indizes
- `work_schedule_versions` + `system_config`: Herkunftsfeld `change_origin` (`SYSTEM_SEED` / `ADMIN_UI` / `MIGRATION`) – KEIN künstlicher Bootstrap-User
- Komplexe Prüfregeln absichtlich **nicht in SQLite** – gehören in Python-Domänenlogik
- `system_events`-Tabelle: für Betriebsereignisse inkl. Systemzeitprotokollierung (§9.3/Regelwerk v3 §21)
- **Aufbewahrungsprinzip** (Pflichtenheft v3 §12/Regelwerk v3 §18): Fachlich relevante Buchungen werden nie physisch gelöscht; Klärung ausschließlich über Status (CORRECTED, CLOSED_WITH_NOTE), Korrekturen oder Archivierung. Aufbewahrungsfrist mind. 2 Jahre (ArbZG §16). Berichte, Pflichtauswertungen und Exportdateien nach definiertem Archivierungs-/Löschkonzept behandeln.

### 11 – 4 Kern-Use-Cases
| Use-Case | Transaktion umfasst |
| --- | --- |
| `buchen()` | `device_events`, `time_bookings`, `booking_status_history`, `review_cases`, `audit_log` |
| `nachtrag_anlegen()` | `supplements`, `review_cases`, `audit_log` |
| `korrektur_anlegen()` | `booking_corrections`, `time_bookings`, `booking_status_history`, `review_cases`, `audit_log` |
| `regelarbeitszeit_ändern()` | `work_schedule_versions` (alt schließen + neu), `audit_log` |

---

## Implementierungsreihenfolge

### Phase 1 – Grundgerüst ✓ abgeschlossen

Umgesetzt:
- `pyproject.toml`, `src/`-Layout, `tests/`, `.gitignore`, `.python-version`
- `migrations/0001_schema.sql` – finale DDL, enthält `schema_migrations`
- `migrations/0002_seed_defaults.sql` – Regelzeiten + System-Config-Defaults
- `infrastructure/db/connection.py` – `isolation_level=None`, `PRAGMA foreign_keys = ON`, `row_factory`
- `infrastructure/db/migrations.py` – `executescript()` mit `BEGIN/COMMIT`, Versionsvalidierung vor f-String
- `scripts/init_db.py`
- `tests/test_migrations.py` – 6 Tests (grün)

---

### Phase 2 – Domäne ✓ abgeschlossen

Umgesetzt unter `src/arbeitszeit/domain/`:

**`enums.py`** — 11 `StrEnum`-Klassen:
`BookingType`, `BookingStatus`, `ReviewCaseType`, `ReviewCaseStatus`, `ReviewSeverity`,
`CardStatus`, `UserRole` (EMPLOYEE / ADMIN / **REVIEWER** / TECH), `BookingSource`,
`ChangeOrigin`, `ApprovalStatus`, `ScopeType` (GLOBAL / EMPLOYEE)

**`errors.py`** — `DomainError`-Basis + 9 Subklassen:
`UnknownCardError`, `InactiveCardError`, `InactiveEmployeeError`, `InvalidBookingSequenceError`, `OpenPhaseConflictError`,
`PermissionDeniedError`, `ValidationError`, `NotFoundError`, `ConflictError`

**`entities.py`** — 9 frozen `@dataclass`-Entitäten mit `__post_init__`-Invarianten:

| Entität | Felder (Auswahl) | Invariante |
| --- | --- | --- |
| `Employee` | `first_name`, `last_name` | — |
| `UserAccount` | `employee_id: int \| None` | — |
| `RfidCard` | `valid_from`, `valid_until`, `replaced_by_card_id` | `valid_until >= valid_from` |
| `TimeBooking` | `rfid_card_id`, `note` | — |
| `WorkScheduleVersion` | `scope_type: ScopeType`, `scope_employee_id` | Scope-Konsistenz + Datumsreihenfolge |
| `ReviewCase` | `description`, `closed_at`, `closed_by_user_id` | Status ↔ Schließungsdaten |
| `Supplement` | `event_at`, `recorded_at`, `related_booking_id`, `approved_by_user_id`, `approved_at` | `ApprovalStatus` ↔ Freigabedaten |
| `BookingCorrection` | `old_booking_type`, `old_booked_at`, `new_booking_type`, `new_booked_at` | — |
| `AuditLogEntry` | `object_type`, `object_id`, `employee_id`, `event_at`, `details_json` | — |

**`services/booking_rules.py`** — `validate_booking_sequence()`, `ValidationResult`

**`services/compliance_checks.py`** — `check_break_compliance()`, `check_max_hours()`, `check_rest_period()`, `ComplianceFlag`

V3 §7.9 / ArbZG §3/4/5 — alle fünf Prüfhilfen sind Pflichtanforderung:
- `check_break_compliance`: >6h ohne Pause (ArbZG §4 Abs.1) UND >9h ohne ausreichende Gesamtpause (ArbZG §4 Abs.1) — beide Schwellen explizit prüfen
- `check_max_hours`: >8h werktäglich (WARN, ArbZG §3) und >10h täglich (NEEDS_REVIEW/CRITICAL, ArbZG §3)
- `check_rest_period`: <11h Ruhezeit zwischen zwei Arbeitstagen (ArbZG §5) — in Phase 3 bewusst auf Phase 4 verschoben, weil Vortages-Kontext fehlt; **V3 §7.9 Pflichtanforderung, kein optionaler Punkt**

V3-Design-Entscheidung (Regelwerk v3 §11): Die Statuswerte POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION und MANUAL_ENTRY werden im System nicht als BookingStatus-Werte realisiert, sondern über eigene Typen:
- POSSIBLE_* Compliance-Fälle → ReviewCase mit ReviewCaseType (z. B. BREAK_COMPLIANCE_ISSUE, REST_PERIOD_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION) und ReviewSeverity — abfragbar über ReviewCaseRepository
- MANUAL_ENTRY (manuelle Herkunft) → BookingSource.MANUAL auf der TimeBooking — kombinierbar mit jedem Status (WARN, OK, NEEDS_REVIEW)
Diese Trennung ist fachlich ausdrucksstärker (Status und Herkunft orthogonal) und V3-konform, weil report_queries.py alle Fakten daraus korrekt ableitet (Regelwerk v3 §11: konsistente Ableitung für Berichte und Pflichtauswertungen).

**Harte Bedingung für V3-Konformität:** Diese Ableitungsstrategie ist nur dann regelwerkskonform, wenn `report_queries.py` die einzige und zentrale Wahrheitsquelle für alle Ausgabekanäle ist — UI-Pflichtauswertungen, CSV-Export, PDF-Berichte und Filterlogik müssen alle auf denselben normierten Projektionen beruhen. Direkte Ad-hoc-Queries außerhalb von `report_queries.py` sind architektonisch verboten. Konsistenz wird durch Integrationstests gegen alle Ausgabekanäle verifiziert (Phase 4/8e, Phase 5).

**`ports/repositories.py`** — 10 `Protocol`-Interfaces:
- `EmployeeRepository`: `get_by_id`, `get_active_by_personnel_no`
- `UserAccountRepository`: `get_by_id`, `get_by_username`
- `RfidCardRepository`: `get_by_uid_hash` (beliebiger Status), `get_active_by_uid_hash`, `get_by_id`
- `TimeBookingRepository`: `add`, `get_by_id`, `list_for_employee_on_day`, `list_open_for_employee`, `list_between`, `set_status(booking_id, status, reason=None, changed_by_user_id=None)`
- `WorkScheduleRepository`: `add`, `close_version(version_id, valid_until)`, `get_effective(weekday, on_date, employee_id=None)`, `list_versions(weekday=None, scope_employee_id=None)`
- `ReviewCaseRepository`: `add`, `list_open_for_employee`, `resolve(case_id, status, closed_by_user_id, note=None)`
- `SupplementRepository`: `add`, `get_by_id`, `list_pending`, `approve`, `reject`
- `BookingCorrectionRepository`: `add`, `list_for_booking`
- `AuditLogRepository`: `add`
- `SystemConfigRepository`: `get_current`

**Tests** (44 gesamt, alle grün):
- `tests/domain/test_booking_rules.py` – 10 Tests
- `tests/domain/test_compliance_checks.py` – 9 Tests
- `tests/domain/test_entities.py` – 19 Invariantentests

---

### Phase 3 – Application ✓ abgeschlossen

#### Architekturentscheidungen (festgelegt vor Implementierungsstart)

**BookingStatus-Semantik** — Status beschreibt die einzelne Buchung, nicht den Tagesstatus:
| Buchungstyp | Status | Bedingung |
| --- | --- | --- |
| COME | immer `OPEN` | Arbeitsphase beginnt, bleibt offen |
| BREAK_START | immer `OPEN` | Pause beginnt, bleibt offen |
| BREAK_END | `OK` | Pause konsistent geschlossen, keine relevanten Flags im projizierten Tagesverlauf |
| BREAK_END | `WARN` / `NEEDS_REVIEW` | Compliance-Flags nach Einfügen der Buchung in den projizierten Tagesverlauf |
| GO | `OK` | keine Compliance-Flags |
| GO | `WARN` | Flags mittlerer Schwere (ReviewSeverity.WARN) |
| GO | `NEEDS_REVIEW` | Flags kritischer Schwere oder ungewöhnliche Konstellation |
| — | `CORRECTED` | ausschließlich durch `CorrectBookingUseCase`, nie durch `BookUseCase` |
| — | `CLOSED_WITH_NOTE` | administrativ geschlossen mit Begründung, kein Korrektur-Ersatz — z. B. offene Buchung durch Admin-Klärung abgeschlossen (Regelwerk v3 §11) |

`WARN` = Hinweis-Funktion, kein zwingender Human-Review.
`NEEDS_REVIEW` = zwingend in die Prüf-Pipeline.

**booking_status_history** — Infrastruktur-Seiteneffekt:
`time_booking_repo.set_status(booking_id, status, reason, changed_by_user_id)` schreibt
`time_bookings.current_status` und `booking_status_history` in einer DB-Transaktion.
Kein eigener `BookingStatusHistoryRepository`-Port in der Application-Schicht.

**device_event_id** — Verantwortungsteilung:
- Hardware-/Infrastruktur-Schicht erzeugt `device_events` vor Use-Case-Aufruf.
- `BookCommand.device_event_id: int | None` wird 1:1 an `TimeBooking.device_event_id` durchgereicht.
- Kein eigener Port. Fakes führen das Feld im In-Memory-Store mit (Dummy-Wert genügt).
- Schema-Spalte `time_bookings.device_event_id` wird in Phase 4 per Migration ergänzt.

**FakeUnitOfWork.__exit__** — ruft `rollback()` bei Exception, damit Tests reales Transaktionsverhalten widerspiegeln.

**Autorisierungsmuster** — Rollenprüfung in schreibenden Use Cases (Pflichtenheft v3 §5 / Regelwerk v3 §16)

Phase 3 hat keine Rollenprüfung implementiert (Fakes, kein UserAccountRepository-Aufruf in Use Cases). Phase 4/Schritt 1c zieht explizite Rollenprüfung in alle schreibenden Use Cases nach. `PermissionDeniedError` ist bereits in `errors.py` vorhanden.

Muster: `user = user_account_repo.get_by_id(acting_user_id)` → `if user is None or user.role not in ALLOWED_ROLES: raise PermissionDeniedError(...)`

| Use Case | Erlaubte Rollen | Prüf-ID |
| --- | --- | --- |
| `RegisterSupplementUseCase` | ADMIN, REVIEWER | `recorded_by_user_id` |
| `ApproveSupplementUseCase` | REVIEWER, ADMIN | `approving_user_id` (neu: `ApproveSupplementCommand`) |
| `RejectSupplementUseCase` | REVIEWER, ADMIN | `rejecting_user_id` (neu: `RejectSupplementCommand`) |
| `CorrectBookingUseCase` | ADMIN, REVIEWER | `corrected_by_user_id` |
| `ManageWorkScheduleUseCase` | ADMIN | `changed_by_user_id` (muss non-null sein) |
| Backup/Restore | TECH, ADMIN | Betriebsebene (Phase 5) |

**Neue Commands** (zu `application/commands.py` ergänzen):

`ApproveSupplementCommand` — `@dataclass(frozen=True, slots=True)`:

- `supplement_id: int`
- `approving_user_id: int`

`RejectSupplementCommand` — `@dataclass(frozen=True, slots=True)`:

- `supplement_id: int`
- `rejecting_user_id: int`
- `reason: str`

---

#### Zielstruktur
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
    └── book_time.py
tests/application/
    ├── __init__.py
    ├── fakes.py
    ├── test_manage_work_schedule.py
    ├── test_register_supplement.py
    ├── test_correct_booking.py
    └── test_book_time.py
```

---

#### Implementierungsreihenfolge

**Schritt 1 – `application/unit_of_work.py`**

`UnitOfWork`-Protocol mit Context-Manager-Support (alle 10 Repositories):
```python
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
```

**Schritt 2 – `application/commands.py`**

Alle Commands als `@dataclass(frozen=True, slots=True)`:

`BookCommand`:
- `uid_hash: str` — RFID-Hash vom Terminal
- `terminal_id: int`
- `booking_type: BookingType` — am USB-Numpad gewählt, bevor Karte gelesen wird
- `booked_at: datetime`
- `device_event_id: int | None` — von Hardware-Schicht gesetzt, Use Case reicht durch
- `source: BookingSource = BookingSource.TERMINAL`

`CreateSupplementCommand`:
- `employee_id: int`
- `related_booking_id: int | None`
- `booking_type: BookingType`
- `event_at: datetime`
- `recorded_at: datetime`
- `reason: str`
- `recorded_by_user_id: int`

`CreateCorrectionCommand`:
- `original_booking_id: int`
- `corrected_by_user_id: int`
- `reason: str`
- `new_booking_type: BookingType`
- `new_booked_at: datetime`

`ChangeWorkScheduleCommand`:
- `scope_type: ScopeType`
- `scope_employee_id: int | None`
- `weekday: int` — 1=Mo bis 7=So (ISO-Wochentag, konsistent mit `isoweekday()`)
- `start_time: time`
- `end_time: time`
- `valid_from: date`
- `change_origin: ChangeOrigin`
- `changed_by_user_id: int | None`
- `reason: str | None`

**Schritt 3 – `application/results.py`**

Alle Results als `@dataclass(frozen=True, slots=True)`:

`BookResult`:
- `booking_id: int`
- `status: BookingStatus`
- `follow_up_case_ids: tuple[int, ...]`

`SupplementResult`:
- `supplement_id: int`
- `review_case_id: int | None`

`CorrectionResult`:
- `correction_id: int`
- `updated_booking_id: int`
- `review_case_id: int | None`

`WorkScheduleChangeResult`:
- `new_version_id: int`
- `superseded_version_id: int | None`

**Schritt 4 – `tests/application/fakes.py`**

In-Memory-Implementierungen aller 10 Repository-Interfaces.
Jedes Fake: `dict[int, Entity]` + Auto-Inkrement-ID.
`FakeUnitOfWork`:
- `committed: bool`, `rolled_back: bool` als Testflags
- `__exit__` ruft `rollback()` bei Exception
- `FakeTimeBookingRepository.set_status()`: aktualisiert Entity via `dataclasses.replace()`;
  kein separater History-Eintrag (Infrastruktur-Seiteneffekt gehört nicht in Fakes)
- `FakeWorkScheduleRepository.get_effective()`: EMPLOYEE-Scope hat Vorrang vor GLOBAL
- `FakeWorkScheduleRepository.close_version()`: `dataclasses.replace()` löst `__post_init__`
  aus → `valid_until < valid_from` schlägt fehl (Invariante wird in Fakes geprüft)

**Schritt 5 – `use_cases/manage_work_schedule.py`**

`ManageWorkScheduleUseCase(uow: UnitOfWork)` mit `execute(cmd: ChangeWorkScheduleCommand) -> WorkScheduleChangeResult`:
1. `work_schedule_repo.get_effective(weekday, valid_from, scope_employee_id)` → `current`
2. `ConflictError` wenn `current.valid_from == cmd.valid_from` (unabhängig von Zeiten)
3. `ValidationError` wenn für denselben Scope (`scope_type` + `scope_employee_id`) und denselben Wochentag bereits eine Version mit `valid_from > cmd.valid_from` existiert — `list_versions(weekday=cmd.weekday, scope_employee_id=cmd.scope_employee_id)` filtert den relevanten Scope, keine globale Sperre
4. `current` schließen: `close_version(current.id, cmd.valid_from - timedelta(days=1))`
   → erst schließen, dann neue Version anlegen; nie zwei gleichzeitig wirksame Versionen
5. Neue `WorkScheduleVersion` anlegen, `work_schedule_repo.add()`
6. `AuditLogEntry` anlegen
7. `uow.commit()`, `WorkScheduleChangeResult` zurückgeben

Testfälle:
- Neue Version wird angelegt → `new_version_id > 0`, `uow.committed`
- Bestehende Version wird geschlossen → `valid_until = new_valid_from - 1 Tag`
- Gleiche `valid_from`, andere Zeiten → `ConflictError`
- Identische Version → `ConflictError`
- Rückwärts-Insertion → `ValidationError`
- Audit-Log-Eintrag vorhanden

**Schritt 6 – `use_cases/register_supplement.py`**

`RegisterSupplementUseCase(uow: UnitOfWork)` mit `execute(cmd: CreateSupplementCommand) -> SupplementResult`:
1. `employee_repo.get_by_id()` → `NotFoundError` bei unbekanntem Mitarbeiter
2. `Supplement` mit `ApprovalStatus.PENDING` anlegen, `supplement_repo.add()`
3. `ReviewCase(MANUAL_ENTRY_REVIEW)` anlegen — standardmäßig, nicht optional
4. `AuditLogEntry` anlegen — in derselben Transaktion
5. `uow.commit()`, `SupplementResult` zurückgeben

Freigabe/Ablehnung: `supplement_repo.approve()` / `reject()` stets zusammen mit `AuditLogEntry` in einer Transaktion.

**Architekturhinweis Freigabe:** Wenn ein genehmigter Nachtrag eine echte `TimeBooking` erzeugt (`ApproveSupplementUseCase`), muss diese Buchung dieselbe Statuslogik durchlaufen wie eine Terminalbuchung (OPEN/OK/WARN/NEEDS_REVIEW, projizierter Tagesverlauf). Nachträge dürfen fachlich nicht schwächer geprüft werden als Echtzeitbuchungen. `source = BookingSource.MANUAL`, eigener `AuditLogEntry`. **`ApproveSupplementUseCase` ist ein Pflichtbestandteil (Phase 4/Schritt 1) — niemals als reines `supplement_repo.approve()` ohne Buchungslogik umsetzen.**

Testfälle: Unbekannter Mitarbeiter → `NotFoundError`; Nachtrag erstellt + Review Case vorhanden; `approval_status = PENDING`; Audit-Log-Eintrag vorhanden.

**Schritt 7 – `use_cases/correct_booking.py`**

`CorrectBookingUseCase(uow: UnitOfWork)` mit `execute(cmd: CreateCorrectionCommand) -> CorrectionResult`:
1. `time_booking_repo.get_by_id()` → `NotFoundError` bei nicht existierender Buchung
2. `BookingCorrection` anlegen, `booking_correction_repo.add()` — speichert `old_booking_type`, `old_booked_at`, `new_booking_type`, `new_booked_at`
3. `time_booking_repo.set_status(booking.id, CORRECTED, reason=cmd.reason, changed_by_user_id=cmd.corrected_by_user_id)`
4. Offene `ReviewCase` **mit passendem `booking_id`** schließen — nicht pauschal alle
5. `AuditLogEntry` anlegen
6. `uow.commit()`, `CorrectionResult` zurückgeben

**Korrekturmodell:** Die ursprüngliche `TimeBooking`-Zeile wird **nicht physisch verändert** — sie erhält nur Status `CORRECTED`. Der neue Zustand (`new_booking_type`, `new_booked_at`) ist ausschließlich über `BookingCorrectionRepository.list_for_booking(booking_id)` abfragbar. `report_queries.py` projiziert beide Zustände (alt/neu + Begründung + Person + Zeitstempel) für Berichte und Pflichtauswertungen. Kein direktes Überschreiben von `time_bookings`.

Testfälle: Buchung nicht gefunden → `NotFoundError`; Status = CORRECTED; `BookingCorrection`-Datensatz enthält alte und neue Felder vollständig; nur fachlich passende Review Cases werden geschlossen; Audit-Log vorhanden.

**Schritt 8 – `use_cases/book_time.py`**

`BookUseCase(uow: UnitOfWork)` mit `execute(cmd: BookCommand) -> BookResult`:

1. `rfid_card_repo.get_by_uid_hash(cmd.uid_hash)` → `None`: `AuditLogEntry` schreiben (`event_type="BOOKING_REJECTED_UNKNOWN_CARD"`), dann `UnknownCardError` raisen; `status != ACTIVE`: `AuditLogEntry` schreiben (`event_type="BOOKING_REJECTED_INACTIVE_CARD"`), dann `InactiveCardError` raisen. **Abweisungsprotokoll:** Abgewiesene Buchungsversuche sind auditpflichtig — Protokolleintrag auch bei Fehler, damit Missbrauchsversuche nachvollziehbar bleiben.
2. `employee_repo.get_by_id(card.employee_id)` → `employee.is_active == False`: `InactiveEmployeeError`
3. `time_booking_repo.list_for_employee_on_day(employee.id, cmd.booked_at.date())` → `day_bookings`
4. `validate_booking_sequence(cmd.booking_type, day_bookings)` → `InvalidBookingSequenceError` / `OpenPhaseConflictError`
5. Buchungsstatus bestimmen (siehe Tabelle oben):
   - COME / BREAK_START → `OPEN`
   - GO / BREAK_END → Compliance-Flags aus projiziertem Tagesverlauf auswerten
     (Basis: `day_bookings + [neues_booking_objekt]`):
     `flags = check_break_compliance(projected) + check_max_hours(projected)`
     Ruhezeitprüfung (`check_rest_period`) erfordert Vortages-Kontext → auf Phase 4 verschoben.
     **V3 §7.9 Pflichtanforderung (ArbZG §5), keine optionale Lücke:**
     Phase 4 integriert: `prev = time_booking_repo.list_for_employee_on_day(employee.id, date - 1)`
     `flags += check_rest_period(projected, prev)` — Testfall V3 §16 "Ruhezeitverletzung" erforderlich.
     Regelzeitfenster-Check (alle Buchungsarten): `schedule = work_schedule_repo.get_effective(weekday, on_date, employee_id)` — liegt `cmd.booked_at.time()` außerhalb `[schedule.start_time, schedule.end_time]`, wird ein WARN-Flag (`OUTSIDE_SCHEDULED_WINDOW`) erzeugt; kein eigener `ReviewCaseType` erforderlich, Auswertung über `report_queries.py`.
     kein Flag → `OK`; WARN-Flag → `WARN`; CRITICAL-Flag → `NEEDS_REVIEW`
6. `TimeBooking` mit ermitteltem Status + `device_event_id` anlegen, `time_booking_repo.add()`
7. Pro ComplianceFlag einen `ReviewCase` anlegen, `review_case_repo.add()`
8. `AuditLogEntry` anlegen
9. `uow.commit()`, `BookResult(booking_id, status, follow_up_case_ids)` zurückgeben

Testfälle:
- COME-Buchung → `status = OPEN`, `follow_up_case_ids` leer
- Unbekannte RFID-UID → `UnknownCardError` + Audit-Log-Eintrag `BOOKING_REJECTED_UNKNOWN_CARD`
- Inaktive Karte → `InactiveCardError` + Audit-Log-Eintrag `BOOKING_REJECTED_INACTIVE_CARD`
- Aktive Karte, inaktiver Mitarbeiter → `InactiveEmployeeError`
- Erste Tagesbuchung als GO → `InvalidBookingSequenceError`
- BREAK_END ohne offene Pause → `InvalidBookingSequenceError`
- COME nach offenem COME → `InvalidBookingSequenceError`
- GO bei offener Pause → `OpenPhaseConflictError`
- GO nach > 8h → `status = WARN`, `follow_up_case_ids` nicht leer, Buchung wird trotzdem gespeichert
- GO nach > 10h → `status = NEEDS_REVIEW`, `follow_up_case_ids` nicht leer
- COME außerhalb Regelzeitfenster → WARN-Flag im projizierten Verlauf

#### Verifikation
- `pytest tests/domain/` → 44 Tests grün (Regression Phase 2)
- `pytest tests/application/` → alle Use-Case-Tests grün
- `pytest tests/` → alle Tests grün inkl. Migrationen

---

### Phase 4 – Infrastruktur ← aktuelle Phase

#### Fehlersemantik (bereits in Phase 3 vereinheitlicht)
In allen Use Cases gilt: `employee is None` → `NotFoundError`; `not employee.is_active` → `InactiveEmployeeError`.
Gilt für `BookUseCase`, `CorrectBookingUseCase`, `RegisterSupplementUseCase` und künftig `ApproveSupplementUseCase`.

---

**Schritt 1 – `use_cases/approve_supplement.py` + `reject_supplement.py`**

`ApproveSupplementUseCase` — genehmigter Nachtrag erzeugt **zwingend** eine `TimeBooking` (Pflichtbestandteil, nicht optional):

1. `user_account_repo.get_by_id(cmd.approving_user_id)` → `None` oder Rolle nicht in {REVIEWER, ADMIN}: `PermissionDeniedError`
2. `supplement_repo.get_by_id()` → `NotFoundError`
3. `approval_status == PENDING` prüfen → sonst `ValidationError`
4. `employee_repo.get_by_id()` → `None`: `NotFoundError`; inaktiv: `InactiveEmployeeError`
5. `supplement_repo.approve()`; offenen `MANUAL_ENTRY_REVIEW`-Fall schließen
6. Tagesbuchungen laden; Vortagesbuchungen laden; `_evaluate_booking()` auf projizierten Verlauf inkl. `check_rest_period` (V3 §7.9); `TimeBooking` mit `source=MANUAL` anlegen
7. Pro `ComplianceFlag` einen `ReviewCase` anlegen
8. `AuditLogEntry` (`event_type="SUPPLEMENT_APPROVED"`); `uow.commit()`

**Pflicht:** Bloße `supplement_repo.approve()` ohne Buchungserzeugung ist fachlich unvollständig — immer vollständige Statuslogik (OPEN/OK/WARN/NEEDS_REVIEW) und eigenen AuditLogEntry erzeugen.

`RejectSupplementUseCase`:

1. `user_account_repo.get_by_id(cmd.rejecting_user_id)` → `None` oder Rolle nicht in {REVIEWER, ADMIN}: `PermissionDeniedError`
2. `get_by_id()` → `NotFoundError`; `PENDING`-Check → `ValidationError`
3. `supplement_repo.reject()`; `MANUAL_ENTRY_REVIEW`-Fall schließen (Status `CLOSED_WITH_NOTE`)
4. `AuditLogEntry` (`event_type="SUPPLEMENT_REJECTED"`, `reason` im JSON); `uow.commit()`

Beide Use Cases: Tests gegen Fakes; kein Commit bei Fehler.

---

**Schritt 1b – Ruhezeitprüfung in `BookUseCase` integrieren (V3 §7.9 Pflichtanforderung)**

Ergänzung in `use_cases/book_time.py` nach Migration 0005 und SQLite-Repo-Integration:
- Bei GO/BREAK_END: `prev_day = time_booking_repo.list_for_employee_on_day(employee.id, cmd.booked_at.date() - timedelta(days=1))`
- `flags += check_rest_period(projected, prev_day)`
- FakeTimeBookingRepository unterstützt bereits `list_for_employee_on_day` → Fake-Test ohne DB möglich
- Neuer Testfall in `tests/application/test_book_time.py`: GO nach <11h Ruhezeit → `POSSIBLE_REST_VIOLATION` ReviewCase + Status WARN oder NEEDS_REVIEW
- Deckt V3 §16 Testpflicht "Unterschreitung der Ruhezeit" ab

---

##### Schritt 1c – Rollenprüfung in alle schreibenden Use Cases integrieren

Nachrüstung der Autorisierung aus dem Autorisierungsmuster (Phase 3 Architekturentscheidungen) in alle noch nicht abgesicherten Use Cases:

- `RegisterSupplementUseCase`: `user_account_repo.get_by_id(cmd.recorded_by_user_id)` → Rolle in {ADMIN, REVIEWER}
- `CorrectBookingUseCase`: `user_account_repo.get_by_id(cmd.corrected_by_user_id)` → Rolle in {ADMIN, REVIEWER}
- `ManageWorkScheduleUseCase`: `user_account_repo.get_by_id(cmd.changed_by_user_id)` → Rolle ADMIN; `changed_by_user_id` darf nicht `None` sein

`ApproveSupplementUseCase` und `RejectSupplementUseCase` erhalten ihre Rollenprüfung bereits in Schritt 1 (s. o.).
Neue Testfälle in `tests/application/` für jede Prüfung: `PermissionDeniedError` bei falscher Rolle und bei `None`.

---

**Schritt 2 – Migration `0005`**
`device_event_id INTEGER` als nullable Spalte in `time_bookings` ergänzen (FK auf `device_events.id`), per Table-Rebuild (SQLite-Einschränkung).
(Migration `0004` wurde bereits für `rejected_by_user_id`/`rejected_at` + `review_cases.note` verwendet.)

---

**Schritt 3 – `infrastructure/db/unit_of_work.py`**

`SQLiteUnitOfWork` implementiert das `UnitOfWork`-Protocol. Transaktionsrahmen:
```python
def __enter__(self):
    self._conn.execute("BEGIN")
    self._transaction_open = True
    return self

def commit(self):
    self._conn.execute("COMMIT")
    self._transaction_open = False
    # kein sofortiges BEGIN — nächste Transaktion startet beim nächsten __enter__

def rollback(self):
    self._conn.execute("ROLLBACK")
    self._transaction_open = False

def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is not None and self._transaction_open:
        self.rollback()
    # _transaction_open-Flag verhindert ROLLBACK nach bereits erfolgtem commit();
    # Fehler nach commit() sollen in Tests klar sichtbar bleiben.
```

---

**Schritt 4 – `infrastructure/db/repositories/`**
10 Repository-Implementierungen gegen echte SQLite-DB:
- Datetimes als ISO-8601-TEXT; Enums als `.value`; Booleans als INTEGER 0/1
- Ausschließlich Parameterized Statements (`?`-Syntax)
- `RETURNING id` nach INSERT (SQLite ≥ 3.35)
- `WorkScheduleRepository.get_effective`: EMPLOYEE-Scope vor GLOBAL (2-Stufen-Query)
- `WorkScheduleRepository.close_version()`: `valid_until ≥ valid_from` zusätzlich prüfen
- `TimeBookingRepository.set_status()`: zuerst `SELECT current_status` → kein Ergebnis → `NotFoundError` (kein stilles Nichtstun); dann UPDATE + INSERT in `booking_status_history` atomar
- `SystemConfigRepository.set_current()`: INSERT, nie UPDATE — stets mit `AuditLogEntry` in einer Transaktion
- `list_for_employee_on_day()`: Bereichsquery mit `>= day_start` und `< next_day` (Index-kompatibel, nicht `DATE()`)

---

**Schritt 5 – `tests/integration/`**

Fixture: In-Memory-SQLite + `run_migrations()` in `conftest.py`.
Testprinzip: echte INSERT/SELECT-Roundtrips, keine Mocks.

Zusätzlicher Pflicht-Testfall für `WorkScheduleRepository`:
- Zwei gültige EMPLOYEE-Versionen für denselben Mitarbeiter/Wochentag →
  `get_effective` wählt die neuere; dokumentiert, dass Mehrfachgültigkeit
  zwar durch Use Case + Datenkonsistenz verhindert wird, die Infrastruktur
  aber dennoch deterministisch selektiert.

---

**Schritt 6 – `infrastructure/hardware/`**
evdev-Integration (RFID + Numpad), zunächst gegen Simulator.

**Schritt 7 – `infrastructure/backup/`**
SQLite-Backup + NAS-Sync. Trigger: zeitgesteuerter Job (systemd-Timer/cron) + optional manuell auslösbar. **Kein Backup nach jedem `commit()`** — koppelt Schreibpfad und Sicherung zu eng; das Pflichtenheft verlangt regelmäßige Sicherung, nicht Commit-synchrone. Restore-Tests in `tests/e2e/`.
Audit-Logging: BACKUP_CREATED, BACKUP_SYNCED_TO_NAS, BACKUP_SYNC_FAILED (mit cmd/stderr), RESTORE_COMPLETED. Deckt V3 §14/§20 und Regelwerk v3 §20 + V3 §16 "Restore-Test mit echtem Backup" ab.
**Sicherungsumfang (Regelwerk v3 §17/§18/§20):** Neben der SQLite-Datenbankdatei werden auch Exportdateien (CSV + PDF aus `export.export_dir`) in die Sicherung einbezogen. Entscheidung: Exportdateien sind auditpflichtige Ausgabedokumente — Verlust wäre nachweispflichtig. Das Backup-Skript sichert `export_dir` zusammen mit der DB-Datei auf denselben NAS-Pfad.

**Offener V3-Punkt – Systemzeitprotokollierung (Pflichtenheft v3 §9.3 / Regelwerk v3 §21):**
NTP-Synchronisation ist Betriebsvoraussetzung. Zeitsprünge und manuelle Uhrzeitänderungen müssen protokolliert und fachlich geprüft werden. Umsetzung: `system_events`-Tabelle (bereits im Schema) für Zeitsprung-Events. Noch nicht als eigener Schritt eingeplant — spätestens in Phase 5 (Betriebsschicht) oder als Phase 4 ergänzender Schritt ergänzen. Deckt V3 §16 Testpflicht "Systemzeitabweichung" ab.

**Schritt 8 – `infrastructure/export/`**
Kein Excel/openpyxl. PDF-Bibliothek: **reportlab** (rein Python, stabil, tabellarisch, keine externen Binaries, Linux-kompatibel).

Kernprinzip (Regelwerk v3 §11): alle Exportwege nutzen dieselbe Ableitungsschicht.

Zielstruktur:

- `report_queries.py` — gemeinsame Datenselektion + fachliche Projektion (filterbar nach Zeitraum + Mitarbeiter)
- `csv_exporter.py` — detaillierter + verdichteter CSV-Export
- `pdf_report_service.py` — Tages-/Wochen-/Monats-/Mitarbeiterberichte (reportlab)

**8a – report_queries.py:** normierte Datenstrukturen für offene Fälle, Warnsachverhalte, Prüfhinweise und statusbasierte Prüffälle (WARN, NEEDS_REVIEW, POSSIBLE_*, OPEN, CORRECTED, CLOSED_WITH_NOTE), Korrekturen (alt/neu + Begründung + Person + Zeitstempel), Nachträge (als nachträglich erfasster Datensatz gekennzeichnet, Begründung, Freigabebezug soweit vorgesehen), Regelzeitfenster-Verstöße. Gemeinsame Grundlage für CSV, PDF und UI-Pflichtauswertungen.

**8b – csv_exporter.py:** detaillierter CSV (MA-Kennung/-name, Datum, Uhrzeit, Buchungsart, Dauer, Status, Korrektur-/Nachtragskennzeichnung, Prüfflags) + verdichteter CSV (summierte Arbeitszeit, Pausenanzahl/-dauer, offene Buchungen, Warn-/Prüfstatus-Anzahl, Korrekturen/Nachträge). Nachvollziehbare Dateibenennung + Ablage in system_config: export.export_dir.

**8c – pdf_report_service.py:** Tages-/Wochen-/Monats-/Mitarbeiterberichte mit Zeitraum, Erstellungszeitpunkt, Praxis-/Mitarbeiterzuordnung, Korrekturen (alt/neu + Begründung + Person + Zeitstempel), Nachträge als nachträglich erfasster Datensatz gekennzeichnet, Statuswerte konsistent via report_queries.py.

**8d – Pflichtauswertungen** (Pflichtenheft v3 §7.12): offene Buchungen/Pausen, Korrekturen, Nachträge, mögliche Pausen-/Ruhezeit-/Höchstarbeitszeitverstöße, Regelzeitfenster-Verstöße, Warn-/Prüfstatus-Fälle. Filterbar nach Zeitraum + Mitarbeiter; als CSV exportierbar; später in App einsehbar (Phase 5). Exportdateien in Backup-/Archivierungskonzept einbezogen (Regelwerk v3 §17/§18/§20).

**8e – Tests:** `tests/integration/test_export.py` (CSV-Roundtrips, Filterlogik, Korrektur-/Nachtragskennzeichnung, OPEN/WARN-Ableitung) + `tests/integration/test_pdf.py` (PDF-Erzeugung, Seitenanzahl, Schlüsselfelder). Pflichtfall: "Auswertung offener und auffälliger Fälle" (Pflichtenheft v3 §16).

---

**Schritt 9 – Selbsttest/Systemcheck (`infrastructure/system_check.py`)**

Pflichtenheft v3 §7.10 — muss spätestens mit Phase 4 fertiggestellt sein (nicht erst in Phase 5):

- Konfigurationsprüfung: alle erforderlichen `system_config`-Keys vorhanden
- Geräteverfügbarkeit: evdev-Gerät (RFID-Reader + Numpad) erreichbar
- NAS-Erreichbarkeit: Backup-Zielpfad mountbar/schreibbar
- Datenbankzugriff: SQLite-Datei öffenbar, Migrationsstand aktuell
- Grundkonsistenz: keine offenen Transactions, keine verwaisten Fremdschlüssel

Ergebnis wird in `system_events` (`event_type='SYSTEM_CHECK'`) protokolliert. Aufrufbar manuell und als Startprüfung beim Systemstart.

---

### Phase 5 – Präsentation

**Schritt 1 – `presentation/terminal_ui/`**
Operativer Buchungsbetrieb (Numpad + RFID-Feedback). Buchungsart kommt ausschließlich vom USB-Numpad (Pflichtenheft v3 §6/Regelwerk v3 §3 — kein System-Input, keine Tastatur).

**Schritt 2 – `presentation/admin_cli/`**
Administrative Pflege (Mitarbeiter, Karten, Korrekturen). Rollenprüfung gem. Pflichtenheft v3 §5/Regelwerk v3 §16 (Mitarbeiter/Admin/Prüfer/Tech strikt getrennt).

**Schritt 3 – Pflichtauswertungen in App einsehbar (Pflichtenheft v3 §7.12)**
Pflichtauswertungen aus Phase 4/8d müssen in der Anwendung einsehbar sein — nicht nur als exportierbare CSV. Alle acht Pflichtauswertungskategorien (offene Buchungen/Pausen, Korrekturen, Nachträge, Pausen-/Ruhezeit-/Höchstarbeitszeit-Verstöße, Regelzeitfenster-Verstöße, Warn-/Prüfstatus-Fälle) per UI darstellbar, filterbar nach Zeitraum und Mitarbeiter.

**Schritt 4 – Selbsttest im UI integrieren (Pflichtenheft v3 §7.10)**
`infrastructure/system_check.py` ist in Phase 4/Schritt 9 fertiggestellt. Phase 5 ergänzt lediglich den UI-Aufrufpunkt: Systemcheck manuell aus Admin-CLI auslösbar; Ergebnis in der UI sichtbar (nicht nur in system_events).

---

### Testaufteilung

| Verzeichnis | Inhalt |
| --- | --- |
| `tests/domain/` | Domänenregeln, Invarianten (Phase 2) ✓ |
| `tests/application/` | Use-Case-Tests mit Fake-Repos (Phase 3) ✓ |
| `tests/integration/` | Repository-Implementierungen gegen echte SQLite-DB (Phase 4) |
| `tests/e2e/` | Vollständige Abläufe: Kommen/Gehen, vergessene Pause, Nachtrag, Restore (Phase 5) |
| `tests/test_migrations.py` | Migrationsrunner (Phase 1) ✓ |

> Kein `shared/` oder `common/`-Paket vorab — erst wenn echter Querschnittscode entsteht.

### V3 §16 Testpflicht-Abdeckung

| V3 §16 Pflichtszenario | Abdeckung | Status |
| --- | --- | --- |
| mehr als 6h ohne Pause | `tests/domain/test_compliance_checks.py` | ✓ |
| mehr als 9h ohne ausreichende Gesamtpause | `tests/domain/test_compliance_checks.py` | ✓ |
| Arbeitszeit über 8h | `tests/domain/test_compliance_checks.py` + `tests/application/test_book_time.py` | ✓ |
| Arbeitszeit über 10h | `tests/domain/test_compliance_checks.py` + `tests/application/test_book_time.py` | ✓ |
| Unterschreitung Ruhezeit (<11h) | `tests/application/test_book_time.py` — nach Phase 4/Schritt 1b | offen |
| Systemzeitabweichung | nach Systemzeitprotokollierung (Phase 5) | offen |
| Notfallnachtrag | `tests/application/test_register_supplement.py` | ✓ |
| Restore-Test mit echtem Backup | `tests/e2e/test_backup.py` | ✓ |
| Auswertung offener und auffälliger Fälle | `tests/integration/test_export.py` (Phase 4/8e) | offen |
