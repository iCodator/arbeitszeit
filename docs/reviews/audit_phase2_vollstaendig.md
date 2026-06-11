# Audit Phase 2 – Vollständiger Soll-Ist-Abgleich

**Erstellt:** 2026-06-11
**Prüfstand:** aktuelle Codebasis (395 Tests grün)
**Grundlage:** `phase2_planung.md`, `planung_gesamt.md`, `pflichtenheft_arbeitszeit_v5.md`, `regelwerk_arbeitszeit_v5.md`
**Laufnachweis:** `pytest tests/domain/` → 67/67 PASSED

---

## 1. Auditauftrag und Grundlagen

Phase 2 liefert das vollständige infrastrukturfreie Domänenmodell: Enums, Fehlerklassen,
Entities mit Invarianten, Businessregeln, Compliance-Checks und Repository-Protokolle.
Keine Datenbankzugriffe, keine Use Cases.

**Referenzdokumente:**

| Dokument | Pfad | Status |
| --- | --- | --- |
| `pflichtenheft_arbeitszeit_v5.md` | Projektwurzel | ✓ vorhanden |
| `regelwerk_arbeitszeit_v5.md` | Projektwurzel | ✓ vorhanden |
| `anlage_einhaltung_pflichtenheft_v2.md` | `docs/` | ✓ vorhanden |

---

## 2. Sollbild Phase 2

### Aus `phase2_planung.md` und `planung_gesamt.md`

7 Python-Module unter `src/arbeitszeit/domain/`:
`enums.py`, `errors.py`, `entities.py`, `audit_events.py`,
`services/booking_rules.py`, `services/compliance_checks.py`, `ports/repositories.py`

### Relevante Pflichtenheft-v5-Anforderungen

| § | Anforderung |
| --- | --- |
| §5 Nutzerrollen | Mindestens: Mitarbeiter, Admin, Prüfer, technische Betreuung |
| §6 Normalablauf | Numpad-Buchungsart → RFID → Prüfung → Speichern |
| §7.1 Buchungsarten | Kommen, Gehen, Pause Start, Pause Ende |
| §7.6 Prüfstatus | OK, OPEN, WARN, NEEDS_REVIEW, CORRECTED, CLOSED_WITH_NOTE |
| §7.10 ArbZG-Prüfhilfen | >6h ohne Pause, >9h unzureichende Pause, >8h, >10h, <11h Ruhezeit |
| §8.2 Nachvollziehbarkeit | Alle Administrationsvorgänge protokolliert |

---

## 3. Istbild je Liefergegenstand

### 3.1 `enums.py` — 11 StrEnum-Klassen

| Enum | Werte | Soll | Bewertung |
| --- | --- | --- | --- |
| `BookingType` | COME, GO, BREAK_START, BREAK_END | 4 Werte | ✓ |
| `BookingStatus` | OK, OPEN, WARN, NEEDS_REVIEW, CORRECTED, CLOSED_WITH_NOTE | 6 Werte | ✓ |
| `ReviewCaseType` | OPEN_WORK_PHASE, OPEN_BREAK_PHASE, OUTSIDE_SCHEDULE_WINDOW, POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION, IMPLAUSIBLE_SEQUENCE, UNKNOWN_CARD_ATTEMPT, INACTIVE_CARD_ATTEMPT, TIME_ANOMALY, MANUAL_ENTRY_REVIEW | 11 Werte (Plan: 4) | ✓ — bewusste Erweiterung |
| `ReviewCaseStatus` | OPEN, IN_REVIEW, RESOLVED, CLOSED_WITH_NOTE | 4 Werte | ✓ |
| `ReviewSeverity` | INFO, WARN, CRITICAL | 3 Werte | ✓ |
| `CardStatus` | ACTIVE, INACTIVE, REPLACED, LOST | 4 Werte | ✓ |
| `UserRole` | EMPLOYEE, ADMIN, REVIEWER, TECH | 4 Werte | ✓ |
| `BookingSource` | TERMINAL, MANUAL, IMPORT | 3 Werte (IMPORT statt SYSTEM) | ✓ — dokumentierte Abweichung |
| `ChangeOrigin` | SYSTEM_SEED, ADMIN_UI, MIGRATION | 3 Werte | ✓ |
| `ApprovalStatus` | PENDING, APPROVED, REJECTED | 3 Werte | ✓ |
| `ScopeType` | GLOBAL, EMPLOYEE | 2 Werte | ✓ |

**Pflichtenheft v5 §5:** `UserRole` bildet ADMIN, REVIEWER, TECH und EMPLOYEE ab. ✓
**Pflichtenheft v5 §7.1:** `BookingType` enthält alle 4 Buchungsarten. ✓
**Pflichtenheft v5 §7.6:** `BookingStatus` enthält alle 6 geforderten Statuswerte. ✓

### 3.2 `errors.py` — 10 Fehlerklassen

| Klasse | Basis | code | Soll | Bewertung |
| --- | --- | --- | --- | --- |
| `DomainError` | `Exception` | — | Basisklasse | ✓ |
| `UnknownCardError` | `DomainError` | `"UNKNOWN_CARD"` | ja | ✓ |
| `InactiveCardError` | `DomainError` | `"INACTIVE_CARD"` | ja | ✓ |
| `InactiveEmployeeError` | `DomainError` | `"INACTIVE_EMPLOYEE"` | ja | ✓ |
| `InvalidBookingSequenceError` | `DomainError` | `"INVALID_BOOKING_SEQUENCE"` | ja | ✓ |
| `OpenPhaseConflictError` | `DomainError` | `"OPEN_PHASE_CONFLICT"` | ja | ✓ |
| `PermissionDeniedError` | `DomainError` | `"PERMISSION_DENIED"` | ja | ✓ |
| `ValidationError` | `DomainError` | `"VALIDATION_ERROR"` | ja | ✓ |
| `NotFoundError` | `DomainError` | `"NOT_FOUND"` | ja | ✓ |
| `ConflictError` | `DomainError` | `"CONFLICT"` | ja | ✓ |

Alle 9 Subklassen vorhanden. `DomainError` hat `code`-Attribut, `message` und `context`-Dict. ✓

### 3.3 `entities.py` — 9 frozen @dataclass

Alle Entities: `@dataclass(frozen=True, slots=True)`, Invarianten in `__post_init__`.

| Entity | Felder | Invariante(n) | Bewertung |
| --- | --- | --- | --- |
| `Employee` | id, personnel_no, first_name, last_name, is_active | `personnel_no` nicht leer | ✓ |
| `UserAccount` | id, employee_id?, username, role: UserRole, is_active | `username` nicht leer | ✓ |
| `RfidCard` | id, employee_id, uid_hash, status: CardStatus, valid_from, valid_until?, replaced_by_card_id? | `valid_until >= valid_from` (wenn gesetzt) | ✓ |
| `TimeBooking` | id, employee_id, booking_type, booked_at, source, status, terminal_id?, rfid_card_id?, device_event_id?, note? | keine | ✓ |
| `WorkScheduleVersion` | id, scope_type, scope_employee_id?, weekday (1–7), start_time, end_time, valid_from, valid_until?, change_origin, changed_by_user_id? | GLOBAL→scope_emp=None; EMPLOYEE→scope_emp≠None; 1≤weekday≤7; start<end; valid_until≥valid_from | ✓ |
| `ReviewCase` | id, employee_id, case_type, severity, status, description, booking_id?, created_at, closed_at?, closed_by_user_id?, note? | OPEN/IN_REVIEW→kein closed; RESOLVED/CLOSED_WITH_NOTE→closed pflicht; CLOSED_WITH_NOTE→note nicht leer | ✓ |
| `Supplement` | id, employee_id, related_booking_id?, booking_type, event_at, recorded_at, reason, recorded_by_user_id, approval_status, approved_*/rejected_* | PENDING→alle None; APPROVED→approved_*≠None, rejected_*=None, approved_at≥recorded_at; REJECTED analog | ✓ |
| `BookingCorrection` | id, original_booking_id, corrected_by_user_id, reason, old_booking_type, old_booked_at, new_booking_type, new_booked_at, created_at | `created_at >= old_booked_at` | ✓ |
| `AuditLogEntry` | id, event_type: str, object_type, object_id, user_id?, employee_id?, event_at, details_json | keine | ✓ |

### 3.4 `audit_events.py` — 14 Konstanten

| Gruppe | Konstanten | Anzahl |
| --- | --- | --- |
| Domänen-Kern (originär Phase 2) | TIME_BOOKED, BOOKING_REJECTED_UNKNOWN_CARD, BOOKING_REJECTED_INACTIVE_CARD, BOOKING_CORRECTED, SUPPLEMENT_CREATED, SUPPLEMENT_APPROVED, SUPPLEMENT_REJECTED, WORK_SCHEDULE_CHANGED | 8 |
| Infrastruktur (Phase 4) | BACKUP_CREATED, BACKUP_SYNCED_TO_NAS, BACKUP_SYNC_FAILED, RESTORE_COMPLETED | 4 |
| Benutzerverwaltung (users-Modul) | USER_ACCOUNT_CREATED, USER_ACCOUNT_DEACTIVATED | 2 |
| **Gesamt** | | **14** |

Eindeutigkeit und Vollständigkeit: `test_audit_events.py` verifiziert beide Eigenschaften
maschinell — beide Tests grün. ✓

**Pflichtenheft v5 §8.2:** Administrationsvorgänge wie Anlegen/Deaktivieren von
Benutzerkonten werden als `USER_ACCOUNT_CREATED` / `USER_ACCOUNT_DEACTIVATED` im
Audit-Log protokolliert. ✓

### 3.5 `services/booking_rules.py`

| Eigenschaft | Soll | Ist | Bewertung |
| --- | --- | --- | --- |
| `validate_booking_sequence(booking_type, day_bookings)` | → `None` | ✓ Rückgabetyp `None` | ✓ |
| `ValidationResult` entfernt | ja | ✓ `ImportError` bei Import | ✓ |
| COME-erste-Buchung erlaubt | ja | ✓ | ✓ |
| GO ohne offene Phase → Fehler | ja | ✓ `InvalidBookingSequenceError` | ✓ |
| GO bei offener Pause → Konflikt | ja | ✓ `OpenPhaseConflictError` | ✓ |
| BREAK_START ohne offene Phase → Fehler | ja | ✓ | ✓ |
| BREAK_END ohne offene Pause → Fehler | ja | ✓ | ✓ |
| COME während offener Pause → Fehler | ja | ✓ | ✓ |

**Pflichtenheft v5 §7.4:** Unplausible Buchungsfolgen werden erkannt und verworfen. ✓

### 3.6 `services/compliance_checks.py`

| Funktion | Schwellen | ArbZG | Bewertung |
| --- | --- | --- | --- |
| `check_break_compliance(day_bookings)` | >6h ununterbrochen ohne Pause → WARN; >9h Nettozeit mit <45min Pause → CRITICAL; >6h Nettozeit mit <30min Pause → WARN | §4 | ✓ |
| `check_max_hours(day_bookings)` | >8h → WARN; >10h → CRITICAL | §3 | ✓ |
| `check_rest_period(last_go, next_come)` | <11h Ruhezeit → CRITICAL | §5 | ✓ |
| `ComplianceFlag` | `case_type: ReviewCaseType`, `severity: ReviewSeverity` | — | ✓ |

**Pflichtenheft v5 §7.10:** Alle 5 geforderten ArbZG-Prüfhilfen implementiert. ✓

### 3.7 `ports/repositories.py` — 10 Protocol-Interfaces

| Repository | Methoden | Bewertung |
| --- | --- | --- |
| `EmployeeRepository` | `get_by_id`, `get_active_by_personnel_no` | ✓ |
| `UserAccountRepository` | `get_by_id`, `get_by_username` | ✓ |
| `RfidCardRepository` | `get_by_uid_hash`, `get_active_by_uid_hash`, `get_by_id` | ✓ |
| `TimeBookingRepository` | `add`, `get_by_id`, `list_for_employee_on_day`, `list_open_for_employee`, `list_between`, `set_status` | ✓ |
| `WorkScheduleRepository` | `add`, `close_version`, `get_effective`, `list_versions` | ✓ |
| `ReviewCaseRepository` | `add`, `list_open_for_employee`, `resolve` | ✓ |
| `SupplementRepository` | `add`, `get_by_id`, `list_pending`, `approve`, `reject` | ✓ |
| `BookingCorrectionRepository` | `add`, `list_for_booking` | ✓ |
| `AuditLogRepository` | `add` | ✓ |
| `SystemConfigRepository` | `get_current`, `set_current` | ✓ |

### 3.8 Tests — 67 in 4 Dateien

**Laufnachweis:** 67/67 PASSED (ausgeführt am 2026-06-11)

| Datei | Tests | Prüfgegenstand |
| --- | --- | --- |
| `test_entities.py` | 42 | Employee (3), UserAccount (3), RfidCard (3), WorkScheduleVersion (8), ReviewCase (11), Supplement (12), BookingCorrection (2) |
| `test_booking_rules.py` | 14 | 10 Fehlerfälle (InvalidSequence, OpenPhaseConflict) + 4 Erfolgsfälle |
| `test_compliance_checks.py` | 9 | check_break_compliance (4), check_max_hours (3), check_rest_period (2) |
| `test_audit_events.py` | 2 | Eindeutigkeit der Werte, Katalogvollständigkeit |
| **Gesamt** | **67** | |

Planstand laut `planung_gesamt.md` vor diesem Audit: 63 Tests.
Tatsächlich: 67 (+4 Erfolgsfälle in `test_booking_rules.py` aus `phase2_coding_aufgabe`).

---

## 4. Negativbefund-Verzeichnis

| ID | Kategorie | Befund | Risiko | Behobene Korrektur |
| --- | --- | --- | --- | --- |
| D-01 | Dokumentationsfehler | `phase2_planung.md` Z. 326–327: falsche v5-Pfade mit `docs/`-Präfix | Mittel — falsche Pfade bei maschinellen Prüfungen | ✓ Pfade korrigiert |
| D-02 | Dokumentationsfehler | `planung_gesamt.md` Phase-2-Abschnitt: „63 Tests" statt 67; `test_booking_rules.py` „10 Tests" statt 14 | Mittel — Testanzahl verleitet zu falschem Abnahmestand | ✓ 67 / 14 korrigiert |
| D-03 | Dokumentationslücke | `phase2_planung.md` audit_events: 12 Konstanten beschrieben (8+4), Code hat 14 (+USER_ACCOUNT_CREATED, USER_ACCOUNT_DEACTIVATED) | Gering — Vollständigkeitsprüfung würde 2 Konstanten als undokumentiert zeigen | ✓ Benutzerverwaltungs-Events ergänzt |

**Keine weiteren Abweichungen gefunden.**

---

## 5. Abschlussbewertung

| Bereich | GO / NO-GO | Begründung |
| --- | --- | --- |
| Enums (11 Klassen) | **GO** | Alle Klassen und Werte korrekt; `BookingSource.IMPORT` statt `.SYSTEM` ist dokumentierte Abweichung |
| Errors (10 Klassen) | **GO** | Vollständige Hierarchie, alle code-Attribute vorhanden |
| Entities (9 @dataclass) | **GO** | Alle Felder und Invarianten korrekt implementiert und getestet |
| Pflichtenheft v5 §5 Nutzerrollen | **GO** | `UserRole` enthält alle 4 geforderten Rollen |
| Pflichtenheft v5 §7.1 Buchungsarten | **GO** | `BookingType` enthält alle 4 Buchungsarten |
| Pflichtenheft v5 §7.4 Plausibilitätsprüfung | **GO** | `booking_rules.py` erkennt alle ungültigen Sequenzen |
| Pflichtenheft v5 §7.6 Prüfstatus | **GO** | `BookingStatus` mit allen 6 geforderten Werten |
| Pflichtenheft v5 §7.10 ArbZG-Prüfhilfen | **GO** | Alle 5 Prüfhilfen (§3/§4/§5) implementiert |
| Pflichtenheft v5 §8.2 Nachvollziehbarkeit | **GO** | Audit-Events für alle Administrationsvorgänge vorhanden |
| Ports/Repositories (10 Protokolle) | **GO** | Alle 10 Interfaces mit vollständigen Methodensignaturen |
| Audit-Events (14 Konstanten) | **GO** | Vollständig; Eindeutigkeit und Katalog maschinell verifiziert |
| Testabdeckung | **GO** | 67/67 PASSED; alle Entity-Invarianten und Sequenzregeln getestet |
| Dokumentationspfade v5 | **GO** | D-01 behoben |
| Dokumentationskonsistenz | **GO** | D-02 und D-03 behoben |

**Phase 2 ist vollständig und korrekt implementiert.**
Alle drei Befunde (D-01–D-03) waren rein dokumentarischer Natur und wurden
direkt behoben. Es gibt keine funktionalen Abweichungen.
