# Domänenschicht — technisches Referenzhandbuch

**Kapitel:** 2.1-IT
**Version:** 1.0
**Stand:** Juli 2026
**Zielgruppe:** Entwickler, Systemverantwortliche
**Quelldateien:** `src/arbeitszeit/domain/`

## Zweck der Domänenschicht

Die Domänenschicht enthält die fachliche Kernlogik des Systems: Entitäten,
Enumerationen, Fehlerklassen und Prüfregeln. Sie hat keine Abhängigkeit auf
Infrastruktur, Datenbank oder Präsentation — import-linter erzwingt diese
Grenze in `pyproject.toml`.

## Designprinzipien

Alle Entitäten sind als `@dataclass(frozen=True)` implementiert: unveränderlich,
hashbar, ohne Setter. Änderungen erzeugen immer neue Objekte.

Alle Enumerationen erben von `StrEnum`: die Werte sind direkt als Strings
verwendbar und in SQLite-Spalten speicherbar.

## Value Objects

Jede fachliche ID ist ein typisierter Wrapper um `int` aus
`domain/value_objects.py`:

| Typ | Verwendung |
| --- | --- |
| `EmployeeId` | Mitarbeitende |
| `UserAccountId` | Benutzerkonten |
| `RfidCardId` | RFID-Karten |
| `TimeBookingId` | Zeitbuchungen |
| `TerminalId` | Terminals |
| `SupplementId` | Nachträge |
| `ReviewCaseId` | Prüffälle |
| `BookingCorrectionId` | Buchungskorrekturen |
| `WorkScheduleVersionId` | Dienstplanversionen |
| `DeviceEventId` | Geräteereignisse |

## Entitäten

Quelldatei: `src/arbeitszeit/domain/entities.py`

### Employee

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `EmployeeId` | nein |
| `personnel_no` | `str` | nein |
| `first_name` | `str` | nein |
| `last_name` | `str` | nein |
| `is_active` | `bool` | nein |

### UserAccount

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `UserAccountId` | nein |
| `employee_id` | `EmployeeId \| None` | ja |
| `username` | `str` | nein |
| `role` | `UserRole` | nein |
| `is_active` | `bool` | nein |

### RfidCard

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `RfidCardId` | nein |
| `employee_id` | `EmployeeId` | nein |
| `uid_hash` | `str` | nein |
| `status` | `CardStatus` | nein |
| `valid_from` | `datetime` | nein |
| `valid_until` | `datetime \| None` | ja |
| `replaced_by_card_id` | `RfidCardId \| None` | ja |

### TimeBooking

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `TimeBookingId` | nein |
| `employee_id` | `EmployeeId` | nein |
| `booking_type` | `BookingType` | nein |
| `booked_at` | `datetime` | nein |
| `source` | `BookingSource` | nein |
| `status` | `BookingStatus` | nein |
| `terminal_id` | `TerminalId \| None` | ja |
| `rfid_card_id` | `RfidCardId \| None` | ja |
| `device_event_id` | `DeviceEventId \| None` | ja |
| `note` | `str \| None` | ja |

### WorkScheduleVersion

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `WorkScheduleVersionId` | nein |
| `scope_type` | `ScopeType` | nein |
| `scope_employee_id` | `EmployeeId \| None` | ja |
| `weekday` | `int` (1 = Mo, 7 = So) | nein |
| `start_time` | `time` | nein |
| `end_time` | `time` | nein |
| `valid_from` | `date` | nein |
| `valid_until` | `date \| None` | ja |
| `change_origin` | `ChangeOrigin` | nein |
| `changed_by_user_id` | `UserAccountId \| None` | ja |

### ReviewCase

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `ReviewCaseId` | nein |
| `employee_id` | `EmployeeId` | nein |
| `case_type` | `ReviewCaseType` | nein |
| `severity` | `ReviewSeverity` | nein |
| `status` | `ReviewCaseStatus` | nein |
| `description` | `str` | nein |
| `booking_id` | `TimeBookingId \| None` | ja |
| `created_at` | `datetime` | nein |
| `closed_at` | `datetime \| None` | ja |
| `closed_by_user_id` | `UserAccountId \| None` | ja |
| `note` | `str \| None` | ja |

### Supplement

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `SupplementId` | nein |
| `employee_id` | `EmployeeId` | nein |
| `related_booking_id` | `TimeBookingId \| None` | ja |
| `booking_type` | `BookingType` | nein |
| `event_at` | `datetime` | nein |
| `recorded_at` | `datetime` | nein |
| `reason` | `str` | nein |
| `recorded_by_user_id` | `UserAccountId` | nein |
| `approval_status` | `ApprovalStatus` | nein |
| `approved_by_user_id` | `UserAccountId \| None` | ja |
| `approved_at` | `datetime \| None` | ja |
| `rejected_by_user_id` | `UserAccountId \| None` | ja |
| `rejected_at` | `datetime \| None` | ja |

### BookingCorrection

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `BookingCorrectionId` | nein |
| `original_booking_id` | `TimeBookingId` | nein |
| `corrected_by_user_id` | `UserAccountId` | nein |
| `reason` | `str` | nein |
| `old_booking_type` | `BookingType` | nein |
| `old_booked_at` | `datetime` | nein |
| `new_booking_type` | `BookingType` | nein |
| `new_booked_at` | `datetime` | nein |
| `created_at` | `datetime` | nein |

### AuditLogEntry

Einträge im unveränderlichen Revisionsprotokoll; `id` ist ein einfacher `int`
(kein typisierter Wrapper).

| Feld | Typ | optional |
| --- | --- | --- |
| `id` | `int` | nein |
| `event_type` | `str` | nein |
| `object_type` | `str` | nein |
| `object_id` | `int` | nein |
| `user_id` | `UserAccountId \| None` | ja |
| `employee_id` | `EmployeeId \| None` | ja |
| `event_at` | `datetime` | nein |
| `details_json` | `str` | nein |

## Enumerationen

Quelldatei: `src/arbeitszeit/domain/enums.py`

### BookingType

| Wert | Bedeutung |
| --- | --- |
| `COME` | Kommen |
| `GO` | Gehen |
| `BREAK_START` | Pause beginnt |
| `BREAK_END` | Pause endet |

### BookingStatus

| Wert | Bedeutung |
| --- | --- |
| `OK` | regelkonforme, abgeschlossene Buchung |
| `OPEN` | offene Phase (nach COME oder BREAK_START) |
| `WARN` | ArbZG-Warnschwelle erreicht |
| `NEEDS_REVIEW` | ArbZG-Kritisch oder Anomalie — Prüffall angelegt |
| `CORRECTED` | nachträglich korrigiert |
| `CLOSED_WITH_NOTE` | mit Notiz geschlossen |

### ReviewCaseType

| Wert | Beschreibung |
| --- | --- |
| `OPEN_WORK_PHASE` | kein GO zum Ende des Tages |
| `OPEN_BREAK_PHASE` | kein BREAK_END zur offenen Pause |
| `OUTSIDE_SCHEDULE_WINDOW` | Buchung außerhalb des Dienstplanzeitfensters |
| `POSSIBLE_BREAK_VIOLATION` | Verdacht auf Verstoß gegen §4 ArbZG |
| `POSSIBLE_REST_VIOLATION` | Verdacht auf Unterschreitung der Ruhezeit (§5 ArbZG) |
| `POSSIBLE_MAX_HOURS_VIOLATION` | Verdacht auf Überschreitung der Höchstarbeitszeit (§3 ArbZG) |
| `IMPLAUSIBLE_SEQUENCE` | unplausible Buchungsreihenfolge |
| `UNKNOWN_CARD_ATTEMPT` | unbekannte RFID-Karte gelesen |
| `INACTIVE_CARD_ATTEMPT` | deaktivierte RFID-Karte gelesen |
| `TIME_ANOMALY` | zeitliche Unregelmäßigkeit |
| `MANUAL_ENTRY_REVIEW` | manuell angelegter Nachtrag wartet auf Prüfung |

### ReviewCaseStatus

| Wert | Bedeutung |
| --- | --- |
| `OPEN` | neu, noch unbearbeitet |
| `IN_REVIEW` | in Bearbeitung |
| `RESOLVED` | abgeschlossen |
| `CLOSED_WITH_NOTE` | mit Notiz geschlossen |

### ReviewSeverity

| Wert | Bedeutung |
| --- | --- |
| `INFO` | rein informativ |
| `WARN` | Warnung |
| `CRITICAL` | kritisch, Handlungsbedarf |

### CardStatus

| Wert | Bedeutung |
| --- | --- |
| `ACTIVE` | aktive Karte |
| `INACTIVE` | manuell deaktiviert |
| `REPLACED` | durch neue Karte ersetzt |
| `LOST` | als verloren gemeldet |

### UserRole

| Wert | Bedeutung |
| --- | --- |
| `EMPLOYEE` | kein CLI-Zugang; nicht über `CreateUserAccountUseCase` vergebbar |
| `REVIEWER` | kann Prüffälle bearbeiten und Nachträge genehmigen/ablehnen |
| `ADMIN` | Vollzugriff auf alle Use Cases |
| `TECH` | technischer Betrieb |

### BookingSource

| Wert | Bedeutung |
| --- | --- |
| `TERMINAL` | Buchung am RFID/Numpad-Terminal |
| `MANUAL` | manuell über Admin-CLI erfasst |
| `IMPORT` | importiert |

### ChangeOrigin

| Wert | Bedeutung |
| --- | --- |
| `SYSTEM_SEED` | durch Migrationsskript gesetzt |
| `ADMIN_UI` | über Admin-CLI geändert |
| `MIGRATION` | durch Datenbankmigrationslogik |

### ApprovalStatus

| Wert | Bedeutung |
| --- | --- |
| `PENDING` | wartet auf Entscheidung |
| `APPROVED` | genehmigt |
| `REJECTED` | abgelehnt |

### ScopeType

| Wert | Bedeutung |
| --- | --- |
| `GLOBAL` | gilt für alle Mitarbeitenden |
| `EMPLOYEE` | gilt nur für eine Person |

## Fehlerklassen

Quelldatei: `src/arbeitszeit/domain/errors.py`

Alle Klassen erben von `DomainError` (selbst eine `Exception`).

| Klasse | `code` | Auslöser |
| --- | --- | --- |
| `UnknownCardError` | `UNKNOWN_CARD` | RFID-Karte nicht im System registriert |
| `InactiveCardError` | `INACTIVE_CARD` | Karte ist INACTIVE, REPLACED oder LOST |
| `InactiveEmployeeError` | `INACTIVE_EMPLOYEE` | Mitarbeitender ist deaktiviert |
| `InvalidBookingSequenceError` | `INVALID_BOOKING_SEQUENCE` | Buchungstyp passt nicht zur Tageshistorie |
| `OpenPhaseConflictError` | `OPEN_PHASE_CONFLICT` | GO bei noch offener Pause |
| `PermissionDeniedError` | `PERMISSION_DENIED` | Use Case erfordert andere Rolle |
| `ValidationError` | `VALIDATION_ERROR` | ungültige Eingabedaten |
| `NotFoundError` | `NOT_FOUND` | Datensatz nicht vorhanden |
| `ConflictError` | `CONFLICT` | Konfliktsituation (z. B. doppelte uid_hash) |

## Domänen-Services

### Buchungssequenzregeln

Quelldatei: `src/arbeitszeit/domain/services/booking_rules.py`

`validate_booking_sequence(booking_type, day_bookings)` prüft, ob ein neuer
Buchungstyp zur chronologisch sortierten Tageshistorie eines Mitarbeitenden
passt. Alle Repository-Implementierungen müssen `list_for_employee_on_day`
chronologisch sortiert liefern.

| Neuer Buchungstyp | Verletzungsbedingung | Ausgelöster Fehler |
| --- | --- | --- |
| `COME` | offene Arbeitsphase vorhanden | `InvalidBookingSequenceError` |
| `GO` | keine offene Arbeitsphase | `InvalidBookingSequenceError` |
| `GO` | offene Pause vorhanden | `OpenPhaseConflictError` |
| `BREAK_START` | keine offene Arbeitsphase | `InvalidBookingSequenceError` |
| `BREAK_START` | offene Pause vorhanden | `InvalidBookingSequenceError` |
| `BREAK_END` | keine offene Pause | `InvalidBookingSequenceError` |
| GO / BREAK_START / BREAK_END | `day_bookings` ist leer (kein COME voraus) | `InvalidBookingSequenceError` |

Das erste Buchungsereignis des Tages muss immer `COME` sein.

### ArbZG-Compliance-Schwellenwerte

Quelldatei: `src/arbeitszeit/domain/services/compliance_checks.py`

Die Prüffunktionen liefern `ComplianceFlag`-Objekte mit `case_type` und
`severity`. `evaluate_booking()` in der Anwendungsschicht wertet diese Flags
aus und setzt den `BookingStatus`.

#### check_max_hours — §3 ArbZG

| Bedingung | Schwere |
| --- | --- |
| Netto-Arbeitszeit > 36 000 s (10 h) | `CRITICAL` |
| Netto-Arbeitszeit > 28 800 s (8 h) | `WARN` |

#### check_break_compliance — §4 ArbZG

| Bedingung | Schwere |
| --- | --- |
| Längste Dauerarbeitsphase > 21 600 s (6 h) | `WARN` |
| Netto > 32 400 s (9 h) und Gesamtpause < 2 700 s (45 min) | `CRITICAL` |
| Netto > 21 600 s (6 h) und Gesamtpause < 1 800 s (30 min) | `WARN` |

#### check_rest_period — §5 ArbZG

| Bedingung | Schwere |
| --- | --- |
| Abstand zwischen letztem GO des Vortags und erstem COME des Folgetags < 39 600 s (11 h) | `CRITICAL` |
