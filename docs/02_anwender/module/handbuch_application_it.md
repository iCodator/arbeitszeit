# Anwendungsschicht — technisches Referenzhandbuch

**Kapitel:** 3-IT
**Version:** 1.0
**Stand:** Juli 2026
**Zielgruppe:** Entwickler, Systemverantwortliche
**Quelldateien:** `src/arbeitszeit/application/`

## Zweck der Anwendungsschicht

Die Anwendungsschicht orchestriert Use Cases: Sie empfängt Commands,
prüft Berechtigungen, ruft Domänenregeln auf, persistiert über das
Unit of Work und schreibt den Audit-Log. Sie enthält keine SQL-Logik
und keine UI-Logik.

## CQRS-Aufteilung

| Seite | Datei | Inhalt |
| --- | --- | --- |
| Write | `commands.py` | 16 Command-DTOs |
| Write | `results.py` | 11 Result-DTOs |
| Write | `use_cases/` | Use-Case-Klassen |
| Read | `queries.py` | 4 Query-Row-DTOs |

Die Ausführung der Read-Abfragen (SQL-Logik) liegt in
`infrastructure/export/report_queries.py`. Die Row-Typen selbst
haben keine DB-Abhängigkeit und werden in `queries.py` definiert,
damit Präsentationsmodule keine Infrastructure-Klassen importieren müssen.

## Unit of Work

Quelldatei: `src/arbeitszeit/application/unit_of_work.py`

Das `UnitOfWork`-Protokoll bündelt alle 11 Repositories in einer
Transaktion:

| Attribut | Repository-Protokoll |
| --- | --- |
| `employee_repo` | `EmployeeRepository` |
| `user_account_repo` | `UserAccountRepository` |
| `rfid_card_repo` | `RfidCardRepository` |
| `time_booking_repo` | `TimeBookingRepository` |
| `work_schedule_repo` | `WorkScheduleRepository` |
| `review_case_repo` | `ReviewCaseRepository` |
| `supplement_repo` | `SupplementRepository` |
| `booking_correction_repo` | `BookingCorrectionRepository` |
| `audit_log_repo` | `AuditLogRepository` |
| `system_config_repo` | `SystemConfigRepository` |
| `device_event_repo` | `DeviceEventRepository` |

`commit()` muss vor dem Schreiben des Audit-Logs aufgerufen werden.
`AuditLogRepository.add()` verwendet eine separate Autocommit-Verbindung
und schreibt auch bei Rollback der Haupttransaktion.

## Buchungsbewertung

Quelldatei: `src/arbeitszeit/application/use_cases/_booking_evaluation.py`

`evaluate_booking(booking_type, projected, prev_bookings, extra_flags)`
bestimmt den `BookingStatus` einer neuen Buchung:

| Bedingung | BookingStatus |
| --- | --- |
| `booking_type` ist `COME` oder `BREAK_START` | `OPEN` |
| Mind. ein `CRITICAL`-ComplianceFlag | `NEEDS_REVIEW` |
| Mind. ein `WARN`-ComplianceFlag (kein CRITICAL) | `WARN` |
| Keine Compliance-Flags | `OK` |

Für GO und BREAK_END werden `check_break_compliance` und
`check_max_hours` auf die projizierten Tagesbuchungen angewendet.
Wenn `prev_bookings` übergeben wird, prüft die Funktion zusätzlich
die Ruhezeit via `check_rest_period`.

## Use Cases

### BookUseCase

Quelldatei: `use_cases/book_time.py`

**Berechtigung:** keine Rollprüfung — die Karte dient als Authentifizierung.

**Ablauf:**

1. RFID-Karte anhand `uid_hash` suchen → `UnknownCardError` bei nicht gefunden
2. Karte muss `ACTIVE` sein → `InactiveCardError` sonst
3. Mitarbeitenden laden → `NotFoundError` bei fehlendem Datensatz
4. Mitarbeitender muss aktiv sein → `InactiveEmployeeError` sonst
5. `validate_booking_sequence()` aufrufen → ggf. `InvalidBookingSequenceError`
   oder `OpenPhaseConflictError`
6. `TimeBooking` persistieren
7. `evaluate_booking()` aufrufen → `BookingStatus` und `ComplianceFlag`-Liste
8. Bei Compliance-Flags: `ReviewCase`-Objekte anlegen
9. `commit()`, dann Audit-Log-Eintrag schreiben
10. `BookResult` zurückgeben

**Command:** `BookCommand` (uid_hash, terminal_id, booking_type, booked_at,
device_event_id, source)

**Result:** `BookResult` (booking_id, status, follow_up_case_ids,
employee_first_name, employee_last_name, booking_type, booked_at)

### RegisterSupplementUseCase

Quelldatei: `use_cases/register_supplement.py`

**Berechtigung:** `ADMIN` oder `REVIEWER`

Legt einen Nachtrag mit `approval_status = PENDING` an.
Erzeugt automatisch einen `ReviewCase` vom Typ `MANUAL_ENTRY_REVIEW`.

**Command:** `CreateSupplementCommand`

**Result:** `SupplementResult` (supplement_id, review_case_id)

### ApproveSupplementUseCase

Quelldatei: `use_cases/approve_supplement.py`

**Berechtigung:** `ADMIN` oder `REVIEWER`

Genehmigt einen Nachtrag. Prüft, dass `approval_status == PENDING` und
der Mitarbeitende aktiv ist. Nach Genehmigung wird die Buchung aus dem
Nachtrag angelegt, `evaluate_booking()` aufgerufen und ggf.
`ReviewCase`-Objekte erzeugt.

**Command:** `ApproveSupplementCommand` (supplement_id, approving_user_id)

**Result:** `ApproveSupplementResult` (supplement_id, booking_id,
booking_status, follow_up_case_ids)

### RejectSupplementUseCase

Quelldatei: `use_cases/reject_supplement.py`

**Berechtigung:** `ADMIN` oder `REVIEWER`

Lehnt einen Nachtrag ab. Prüft, dass `approval_status == PENDING`.
Schließt den zugehörigen `MANUAL_ENTRY_REVIEW`-Prüffall.

**Command:** `RejectSupplementCommand` (supplement_id, rejected_by_user_id,
reason)

**Result:** `RejectSupplementResult` (supplement_id, review_case_id)

### CorrectBookingUseCase

Quelldatei: `use_cases/correct_booking.py`

**Berechtigung:** `ADMIN` oder `REVIEWER`

Korrigiert eine bestehende Buchung. Nur für bestimmte Prüffalltypen
zulässig (`_CORRECTABLE_CASE_TYPES`):

| Korrigierbar | Nicht korrigierbar |
| --- | --- |
| `OPEN_WORK_PHASE` | `MANUAL_ENTRY_REVIEW` |
| `OPEN_BREAK_PHASE` | `UNKNOWN_CARD_ATTEMPT` |
| `IMPLAUSIBLE_SEQUENCE` | `INACTIVE_CARD_ATTEMPT` |
| `POSSIBLE_BREAK_VIOLATION` | `TIME_ANOMALY` |
| `POSSIBLE_REST_VIOLATION` | — |
| `POSSIBLE_MAX_HOURS_VIOLATION` | — |
| `OUTSIDE_SCHEDULE_WINDOW` | — |

**Command:** `CreateCorrectionCommand` (original_booking_id,
corrected_by_user_id, reason, new_booking_type, new_booked_at)

**Result:** `CorrectionResult` (correction_id, updated_booking_id,
review_case_id)

### CreateEmployeeUseCase

Quelldatei: `use_cases/manage_employees.py`

**Berechtigung:** `ADMIN`

Prüft: `personnel_no` muss systemweit eindeutig sein.

**Command:** `CreateEmployeeCommand` (acting_user_id, personnel_no,
first_name, last_name)

**Result:** `CreateEmployeeResult` (employee_id)

### DeactivateEmployeeUseCase

Quelldatei: `use_cases/manage_employees.py`

**Berechtigung:** `ADMIN`

**Command:** `DeactivateEmployeeCommand` (acting_user_id, employee_id)

**Result:** keine (None)

### AssignRfidCardUseCase

Quelldatei: `use_cases/manage_rfid_cards.py`

**Berechtigung:** `ADMIN`

Prüft: `uid_hash` muss systemweit eindeutig sein.

**Command:** `AssignRfidCardCommand` (acting_user_id, employee_id, uid_hash)

**Result:** `AssignRfidCardResult` (card_id)

### ReplaceRfidCardUseCase

Quelldatei: `use_cases/manage_rfid_cards.py`

**Berechtigung:** `ADMIN`

Setzt alte Karte auf `REPLACED`, legt neue Karte an.
Prüft: neue `uid_hash` muss eindeutig sein.

**Command:** `ReplaceRfidCardCommand` (acting_user_id, old_card_id, uid_hash)

**Result:** `ReplaceRfidCardResult` (new_card_id)

### DeactivateRfidCardUseCase

Quelldatei: `use_cases/manage_rfid_cards.py`

**Berechtigung:** `ADMIN`

**Command:** `DeactivateRfidCardCommand` (acting_user_id, card_id)

**Result:** keine (None)

### CreateUserAccountUseCase

Quelldatei: `use_cases/manage_user_accounts.py`

**Berechtigung:** `ADMIN`

Prüft: `username` muss eindeutig sein. Erlaubte Rollen:
`{ADMIN, REVIEWER, TECH}` — `EMPLOYEE` kann **nicht** zugewiesen werden.

**Command:** `CreateUserAccountCommand` (acting_user_id, username,
password_hash, role, employee_id)

**Result:** `CreateUserAccountResult` (user_id)

### DeactivateUserAccountUseCase

Quelldatei: `use_cases/manage_user_accounts.py`

**Berechtigung:** `ADMIN`

**Command:** `DeactivateUserAccountCommand` (acting_user_id, target_user_id)

**Result:** keine (None)

### ReactivateUserAccountUseCase

Quelldatei: `use_cases/manage_user_accounts.py`

**Berechtigung:** `ADMIN`

**Command:** `ReactivateUserAccountCommand` (acting_user_id, target_user_id)

**Result:** keine (None)

### ChangeUserRoleUseCase

Quelldatei: `use_cases/manage_user_accounts.py`

**Berechtigung:** `ADMIN`

**Command:** `ChangeUserRoleCommand` (acting_user_id, target_user_id, new_role)

**Result:** keine (None)

### BootstrapAdminUseCase

Quelldatei: `use_cases/manage_user_accounts.py`

**Berechtigung:** keine Rollprüfung. Schlägt fehl, wenn bereits ein aktiver
Admin vorhanden ist.

**Command:** `BootstrapAdminCommand` (username, password_hash)

**Result:** `BootstrapAdminResult` (user_id, username)

### ManageWorkScheduleUseCase

Quelldatei: `use_cases/manage_work_schedule.py`

**Berechtigung:** `ADMIN`

Legt eine neue `WorkScheduleVersion` an. Rückwärtiges Einfügen (neues
`valid_from` liegt vor bestehendem) ist nicht erlaubt. Bei Konflikt
mit gleichem `valid_from` für denselben Scope und Wochentag wird ein
`ConflictError` ausgelöst.

**Command:** `ChangeWorkScheduleCommand` (scope_type, scope_employee_id,
weekday, start_time, end_time, valid_from, change_origin,
changed_by_user_id, reason)

**Result:** `WorkScheduleChangeResult` (new_version_id,
superseded_version_id)

## Command-DTOs (Vollständige Liste)

Quelldatei: `src/arbeitszeit/application/commands.py`

Alle Commands sind `@dataclass(frozen=True, slots=True)`.

| Klasse | Felder (Kurzform) |
| --- | --- |
| `BookCommand` | uid_hash, terminal_id, booking_type, booked_at, device_event_id, source |
| `CreateSupplementCommand` | employee_id, related_booking_id, booking_type, event_at, recorded_at, reason, recorded_by_user_id |
| `CreateCorrectionCommand` | original_booking_id, corrected_by_user_id, reason, new_booking_type, new_booked_at |
| `ApproveSupplementCommand` | supplement_id, approving_user_id |
| `RejectSupplementCommand` | supplement_id, rejected_by_user_id, reason |
| `ChangeWorkScheduleCommand` | scope_type, scope_employee_id, weekday, start_time, end_time, valid_from, change_origin, changed_by_user_id, reason |
| `CreateEmployeeCommand` | acting_user_id, personnel_no, first_name, last_name |
| `DeactivateEmployeeCommand` | acting_user_id, employee_id |
| `AssignRfidCardCommand` | acting_user_id, employee_id, uid_hash |
| `ReplaceRfidCardCommand` | acting_user_id, old_card_id, uid_hash |
| `DeactivateRfidCardCommand` | acting_user_id, card_id |
| `CreateUserAccountCommand` | acting_user_id, username, password_hash, role, employee_id |
| `DeactivateUserAccountCommand` | acting_user_id, target_user_id |
| `ReactivateUserAccountCommand` | acting_user_id, target_user_id |
| `ChangeUserRoleCommand` | acting_user_id, target_user_id, new_role |
| `BootstrapAdminCommand` | username, password_hash |

## Result-DTOs (Vollständige Liste)

Quelldatei: `src/arbeitszeit/application/results.py`

Alle Results sind `@dataclass(frozen=True, slots=True)`.

| Klasse | Felder (Kurzform) |
| --- | --- |
| `BookResult` | booking_id, status, follow_up_case_ids, employee_first_name, employee_last_name, booking_type, booked_at |
| `SupplementResult` | supplement_id, review_case_id |
| `CorrectionResult` | correction_id, updated_booking_id, review_case_id |
| `WorkScheduleChangeResult` | new_version_id, superseded_version_id |
| `ApproveSupplementResult` | supplement_id, booking_id, booking_status, follow_up_case_ids |
| `RejectSupplementResult` | supplement_id, review_case_id |
| `CreateEmployeeResult` | employee_id |
| `AssignRfidCardResult` | card_id |
| `ReplaceRfidCardResult` | new_card_id |
| `CreateUserAccountResult` | user_id |
| `BootstrapAdminResult` | user_id, username |

## Query-Row-DTOs (Read-Seite)

Quelldatei: `src/arbeitszeit/application/queries.py`

Alle Rows sind `@dataclass(frozen=True)`. SQL-Logik liegt in
`infrastructure/export/report_queries.py`.

| Klasse | Felder (Kurzform) |
| --- | --- |
| `BookingRow` | booking_id, employee_id, personnel_no, employee_name, booking_type, booked_at, source, status, is_manual |
| `CorrectionRow` | correction_id, booking_id, employee_id, personnel_no, employee_name, old_booking_type, old_booked_at, new_booking_type, new_booked_at, reason, corrected_by_user_id, corrected_at |
| `SupplementRow` | supplement_id, employee_id, personnel_no, employee_name, booking_type, event_at, recorded_at, reason, approval_status, related_booking_id, approved_by_user_id, approved_at |
| `ReviewCaseRow` | case_id, employee_id, personnel_no, employee_name, case_type, severity, status, booking_id, description, detected_at, note |
