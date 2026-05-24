# Planung Phase 4 – Infrastruktur (abgeschlossen)

Stand: 2026-05-24. Schritte 1–8e vollständig abgeschlossen (319 Tests grün).
Schritt 9 (system_check) offen.

---

## Ausgangslage nach Phase 3

Phase 3 hat folgende Ports und Use Cases fertiggestellt:

```
src/arbeitszeit/application/
├── unit_of_work.py        UnitOfWork Protocol (10 Repos)
├── commands.py            BookCommand, CreateSupplementCommand,
│                          CreateCorrectionCommand, ChangeWorkScheduleCommand,
│                          ApproveSupplementCommand, RejectSupplementCommand
├── results.py             BookResult, SupplementResult, CorrectionResult,
│                          WorkScheduleChangeResult, ApproveSupplementResult,
│                          RejectSupplementResult
└── use_cases/
    ├── book_time.py               BookUseCase
    ├── register_supplement.py     RegisterSupplementUseCase
    ├── correct_booking.py         CorrectBookingUseCase
    ├── manage_work_schedule.py    ManageWorkScheduleUseCase
    ├── approve_supplement.py      ApproveSupplementUseCase  (Phase 3 vorimpl.)
    └── reject_supplement.py       RejectSupplementUseCase   (Phase 3 vorimpl.)
```


---

## Architekturentscheidungen für Phase 4


### Datumsformat in SQLite

SQLite speichert alle Zeitwerte als TEXT im ISO-8601-Format:

```
booked_at      → "2025-03-10T08:00:00+00:00"  (datetime mit Timezone)
valid_from     → "2025-01-01"                  (date)
start_time     → "07:30"                       (time, timespec='minutes')
```

Lesen: `datetime.fromisoformat(row['booked_at'])`, `date.fromisoformat(...)`,
`time.fromisoformat(...)`. Schreiben: `.isoformat()` / `.isoformat(timespec='minutes')`.
Alle Datetimes timezone-aware mit UTC.


### Enum-Mapping

Enums (StrEnum) als TEXT gespeichert (`.value`-String).
Lesen: `EnumClass(row['column_name'])`. Schreiben: `enum_instance.value`.


### Booleans

SQLite: INTEGER 0 oder 1. Lesen: `bool(row['is_active'])`. Schreiben: `1 if x else 0`.


### SQL-Injection-Schutz

Ausschließlich Parameterized Statements (`?`-Syntax). Niemals String-Interpolation.


### set_status() – Infrastruktur-Seiteneffekt

`TimeBookingRepository.set_status(booking_id, status, reason, changed_by_user_id)`
führt zwei Operationen atomisch aus:

1. `SELECT current_status` (für History-Eintrag + NotFoundError bei fehlendem Datensatz)
2. `UPDATE time_bookings SET current_status = ? WHERE id = ?`
3. `INSERT INTO booking_status_history (...)`

Dieser Seiteneffekt ist Infrastruktur-Verhalten und findet nicht in Fakes statt.


### SystemConfigRepository – kein UPDATE

`set_current()` schreibt immer eine neue Zeile (INSERT), nie UPDATE.
Konfigurationsänderungen sind versioniert; History bleibt erhalten.
Immer zusammen mit AuditLogEntry in einer UnitOfWork-Transaktion.


### WorkScheduleRepository – Scope-Priorität

`get_effective(weekday, on_date, employee_id=None)`:

1. Wenn `employee_id` angegeben: EMPLOYEE-Scope zuerst prüfen.
   `ORDER BY valid_from DESC LIMIT 1`
2. Falls kein EMPLOYEE-Treffer (oder `employee_id` ist None): GLOBAL-Scope.
   EMPLOYEE-Scope hat immer Vorrang vor GLOBAL.

`close_version(version_id, valid_until)` prüft zusätzlich `valid_until >= valid_from`.


### ApproveSupplementUseCase – Buchungslogik obligatorisch

Ein genehmigter Nachtrag erzeugt zwingend eine TimeBooking mit:
- `source = BookingSource.MANUAL`
- vollständiger Compliance-Bewertung (identische Logik wie BookUseCase)
- ReviewCases pro ComplianceFlag
- eigenem AuditLogEntry (`event_type="SUPPLEMENT_APPROVED"`)

Bloße `supplement_repo.approve()` ohne Buchungserzeugung ist fachlich
unvollständig. Niemals so umsetzen.


---

## Zielstruktur (Ist-Stand)

```
src/arbeitszeit/infrastructure/
├── __init__.py
├── db/
│   ├── unit_of_work.py           SQLiteUnitOfWork
│   └── repositories/
│       ├── _helpers.py           Parsing-Hilfsfunktionen (datetime/date/time)
│       ├── audit_log.py          SQLiteAuditLogRepository
│       ├── booking_correction.py SQLiteBookingCorrectionRepository
│       ├── employee.py           SQLiteEmployeeRepository
│       ├── review_case.py        SQLiteReviewCaseRepository
│       ├── rfid_card.py          SQLiteRfidCardRepository
│       ├── supplement.py         SQLiteSupplementRepository
│       ├── system_config.py      SQLiteSystemConfigRepository
│       ├── time_booking.py       SQLiteTimeBookingRepository
│       ├── user_account.py       SQLiteUserAccountRepository
│       └── work_schedule.py      SQLiteWorkScheduleRepository
├── hardware/
│   ├── ports.py                  HardwareReader (Protocol), RawBookingRequest
│   ├── evdev_reader.py           EvdevHardwareReader
│   ├── simulator.py              SimulatedHardwareReader
│   └── uid_hash.py               hash_uid(), map_rfid_key()
├── backup/
│   └── backup_service.py         SQLiteBackupService, BackupResult
└── export/
    ├── report_queries.py          BookingRow, CorrectionRow, SupplementRow,
    │                              ReviewCaseRow + Abfragefunktionen
    ├── csv_exporter.py            export_detail(), export_condensed()
    └── pdf_report_service.py      create_daily/weekly/monthly/employee_report()

tests/integration/
├── conftest.py                   In-Memory-SQLite + Migrations-Fixture,
│                                 employee_id- und user_id-Fixtures
├── test_repositories.py          15 Tests
├── test_repositories_roundtrip.py  23 Tests
├── test_unit_of_work.py          10 Tests
├── test_hardware_evdev.py        7 Tests
├── test_hardware_simulator.py    14 Tests
├── test_export.py                18 Tests  (report_queries + Pflichtfall)
├── test_csv_export.py            15 Tests
└── test_pdf.py                   20 Tests

tests/e2e/
└── test_backup.py                16 Tests
```


---

## Fehlersemantik – vereinheitlicht (Phase 3)

In allen Use Cases gilt: `employee is None` → `NotFoundError`;
`not employee.is_active` → `InactiveEmployeeError`. Gilt für BookUseCase,
CorrectBookingUseCase, RegisterSupplementUseCase, ApproveSupplementUseCase.


---

## Implementierte Komponenten


### Schritte 1–2: Use Cases + Migration

- `approve_supplement.py` / `reject_supplement.py` – in Phase 3 vorimplementiert.
  Rollenprüfung (REVIEWER, ADMIN) direkt enthalten.
- Migration `0005_time_bookings_device_event_id.sql` – `device_event_id INTEGER` FK
  in `time_bookings` per Table-Rebuild ergänzt.


### Schritt 3 – infrastructure/db/unit_of_work.py

`SQLiteUnitOfWork` mit allen 10 Repositories. Transaktionsrahmen:
BEGIN beim `__enter__`, manuelles COMMIT/ROLLBACK. `__exit__` ruft `rollback()`
bei Exception. `_transaction_open`-Flag verhindert ROLLBACK nach bereits erfolgtem
`commit()`. `rowcount`-Prüfung in `approve()`, `reject()`, `resolve()` gegen
stille No-Ops.


### Schritt 4 – infrastructure/db/repositories/

10 Repository-Implementierungen. Alle mit:
- Parameterized Statements (`?`-Syntax)
- `RETURNING id` nach INSERT (SQLite ≥ 3.35)
- ISO-8601-Datetimes, `.value`-Enums, INTEGER-Booleans
- `_helpers.py` für `_parse_dt()`, `_parse_date()`, `_parse_time()`

`TimeBookingRepository.set_status()`: SELECT → UPDATE → INSERT atomar;
`NotFoundError` wenn Booking nicht existiert.

`WorkScheduleRepository.get_effective()`: EMPLOYEE-Scope vor GLOBAL
(2-Stufen-Query); `list_versions()` filterbar nach Wochentag + scope_employee_id.

`list_for_employee_on_day()`: Bereichsquery mit `>= day_start` und `< next_day`
(Index-kompatibel, nicht `DATE()`).


### Schritt 5 + 6 – tests/integration/

Fixture `conn`: In-Memory-SQLite + `run_migrations()`. Testprinzip: echte
INSERT/SELECT-Roundtrips, keine Mocks.

Pflicht-Testfall WorkScheduleRepository: Zwei EMPLOYEE-Versionen für denselben
Mitarbeiter/Wochentag → `get_effective()` wählt neuere (deterministisch).


### Schritt 7 – infrastructure/hardware/

`HardwareReader` als `@runtime_checkable Protocol`. `RawBookingRequest` als Datentransferobjekt.
`EvdevHardwareReader`: Echte EVDEV-Geräte, `EmptyUidError` für leere UID.
`SimulatedHardwareReader`: vollständige Simulation für Tests.
`hash_uid()`: SHA-256-Hash der UID; `map_rfid_key()`: Numpad-Key → BookingType.
Buchungsart kommt ausschließlich vom externen USB-Numpad (kein Systeminput,
Pflichtenheft v3 §6 / Regelwerk v3 §3).

7 Integrationstests (evdev, Simulator-unabhängig) + 14 Simulator-Tests.


### Schritt 7b – infrastructure/backup/

`SQLiteBackupService`: `create_local_backup()`, `sync_to_nas()`, `restore_from()`, `run()`.
`BackupResult` als Ergebnisobjekt.

Audit-Logging: BACKUP_CREATED, BACKUP_SYNCED_TO_NAS, BACKUP_SYNC_FAILED
(mit cmd + stderr), RESTORE_COMPLETED via SQLiteAuditLogRepository.

PRAGMA integrity_check nach Restore. `FileNotFoundError` bei fehlendem Backup.

Sicherungsumfang (Regelwerk v3 §17/§18/§20): SQLite-Datei + Exportdateien
(CSV + PDF aus `system_config: export.export_dir`). Exportdateien sind
auditpflichtige Ausgabedokumente; Backup-Skript sichert `export_dir` zusammen
mit der DB-Datei auf denselben NAS-Pfad.

16 e2e-Tests in `tests/e2e/test_backup.py` (inkl. Audit-Verifikation, Mock-NAS).
Deckt V3 §14/§20 und Regelwerk v3 §20 ab. V3 §16-Testpflicht „Restore-Test
mit echtem Backup" erfüllt.


### Schritt 7c – BookUseCase vervollständigen

(V3 §7.9 Pflichtanforderung / ArbZG §5)

Ruhezeitprüfung in `use_cases/book_time.py`: Bei GO/BREAK_END Vortagesbuchungen
laden; `flags += check_rest_period(last_go_dt, next_come_dt)`.
Analog in `ApproveSupplementUseCase`.

Testfall in `tests/application/test_book_time.py`:
GO nach < 11h Ruhezeit → POSSIBLE_REST_VIOLATION ReviewCase + status NEEDS_REVIEW.

Abweisungsprotokoll (Regelwerk v3 §5): unbekannte/inaktive Karte →
AuditLogEntry (BOOKING_REJECTED_UNKNOWN_CARD / _INACTIVE_CARD) vor Fehler-Raising.

Regelzeitfenster-Check: `work_schedule_repo.get_effective(weekday, on_date, employee_id)`;
liegt `booked_at.time()` außerhalb `[start_time, end_time]` → OUTSIDE_SCHEDULE_WINDOW
ReviewCase mit WARN-Flag.

Deckt V3 §16-Testpflicht „Unterschreitung der Ruhezeit" ab.


### Schritt 7d – Rollenprüfung in alle schreibenden Use Cases

(Pflichtenheft v3 §5 / Regelwerk v3 §16)

- `RegisterSupplementUseCase`: Rolle in {ADMIN, REVIEWER}, sonst `PermissionDeniedError`
- `CorrectBookingUseCase`: Rolle in {ADMIN, REVIEWER}
- `ManageWorkScheduleUseCase`: Rolle ADMIN; `changed_by_user_id` darf nicht None sein
- `ApproveSupplementUseCase` / `RejectSupplementUseCase`: Rolle in {REVIEWER, ADMIN}

Testfälle: `PermissionDeniedError` bei falscher Rolle und bei None.


### Offener V3-Punkt – Systemzeitprotokollierung  ← auf Phase 5 verschoben

(Pflichtenheft v3 §9.3 / Regelwerk v3 §21)

`system_events`-Tabelle bereits im Schema vorhanden.
Zeitsprünge und manuelle Uhrzeitänderungen müssen erkannt (TIME_JUMP_DETECTED,
MANUAL_TIME_CHANGE_DETECTED), protokolliert und fachlich geprüft werden.
Umsetzung in Phase 5 (Betriebsschicht). Deckt V3 §16-Testpflicht
„Systemzeitabweichung" ab.


---

## Schritt 8 – infrastructure/export/ (8a ✓ 8b ✓ 8c ✓ 8d ✓ 8e ✓)

Kein Excel/openpyxl. PDF-Bibliothek: **reportlab** (rein Python, stabil,
tabellarisch, keine externen Binaries, Linux-kompatibel).

Kernprinzip (Regelwerk v3 §11): Alle Exportwege (CSV, PDF, Pflichtauswertungen)
nutzen ausschließlich `report_queries.py` als Datenquelle. Direkte Ad-hoc-Queries
außerhalb dieser Schicht sind architektonisch verboten.


### Schritt 8a – report_queries.py

Öffentliche Datenstrukturen: `BookingRow`, `CorrectionRow`, `SupplementRow`,
`ReviewCaseRow` (frozen dataclasses).

Zwei orthogonale Dimensionen werden bewusst getrennt abgefragt:

**BookingStatus-Dimension** (OPEN, WARN, NEEDS_REVIEW, CORRECTED, CLOSED_WITH_NOTE):
- `list_bookings(conn, from_dt, to_dt, employee_id=None) → list[BookingRow]`
- `list_open_bookings(conn, employee_id=None) → list[BookingRow]`
- `list_warn_bookings(conn, from_dt, to_dt, employee_id=None) → list[BookingRow]`

**ReviewCaseType-Dimension** (POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION,
POSSIBLE_MAX_HOURS_VIOLATION, OUTSIDE_SCHEDULE_WINDOW, OPEN_WORK_PHASE …):
- `list_open_review_cases(conn, employee_id=None) → list[ReviewCaseRow]`
- `list_review_cases_for_booking(conn, booking_id) → list[ReviewCaseRow]`

POSSIBLE_* sind ReviewCaseTypes, keine BookingStatus-Werte.
Diese Dimensionen sind orthogonal (Regelwerk v3 §11).

**Weitere Funktionen:**
- `list_corrections(conn, from_dt, to_dt, employee_id=None) → list[CorrectionRow]`
- `list_supplements(conn, from_dt, to_dt, employee_id=None) → list[SupplementRow]`
- `get_employee_identity(conn, employee_id) → tuple[str, str]`
  (personnel_no, full_name) — einzige erlaubte Identitätsabfrage außerhalb Repos

18 Integrationstests in `test_export.py` inkl. Pflichtfall
„Auswertung offener und auffälliger Fälle" (V3 §16).


### Schritt 8b – csv_exporter.py

`export_detail(conn, from_dt, to_dt, export_dir, employee_id=None, now=None) → Path`
`export_condensed(conn, from_dt, to_dt, export_dir, employee_id=None, now=None) → Path`

Detaillierter CSV: MA-Kennung/-name, Datum, Uhrzeit, Buchungsart, ableitbare Dauer,
Status, Korrektur-/Nachtragskennzeichnung, Prüfflags.
Verdichteter CSV: summierte Netto-Arbeitszeit, Pausenanzahl/-dauer, offene
Buchungen, Warn-/Prüfstatus-Anzahl, Korrekturen/Nachträge.

`_day_stats()` als Zustandsmaschine (Pausen korrekt aus Nettoarbeitszeit
herausgerechnet).

Dateinamen:
```
export_detail_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
export_verdichtet_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
```

15 Integrationstests in `test_csv_export.py`.


### Schritt 8c – pdf_report_service.py

`create_daily_report(conn, day, export_dir, now=None) → Path`
`create_weekly_report(conn, year, week, export_dir, now=None) → Path`
`create_monthly_report(conn, year, month, export_dir, now=None) → Path`
`create_employee_report(conn, employee_id, from_dt, to_dt, export_dir, now=None) → Path`

Pflichtabschnitte: Buchungen, Korrekturen, Nachträge, Offene Prüffälle, Erläuterungen.
`_HINWEISE`-Block: erläutert OPEN, WARN, NEEDS_REVIEW, Nachträge, Korrekturen
(Pflichtenheft v3 §7.11). `get_employee_identity()` zentral aus `report_queries.py`
– kein Ad-hoc-Query in `pdf_report_service` (Regelwerk v3 §11).

Dateinamen:
```
bericht_tag_YYYY-MM-DD_YYYYMMDDTHHMMSSZ.pdf
bericht_woche_YYYY-WNN_YYYYMMDDTHHMMSSZ.pdf
bericht_monat_YYYY-MM_YYYYMMDDTHHMMSSZ.pdf
bericht_mitarbeiter_NNNN_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.pdf
```

20 Tests in `test_pdf.py` (Dateinamen, valides PDF, Pflichtabschnitte,
Erläuterungen, Robustheit ohne Buchungen, Robustheit mit
Korrekturen/Nachträgen/Prüffällen ohne Buchungen).

Aufgeschobene Feinarbeit (nicht abnahmeblockierend):
- String-Truncation (`reason[:40]`, `description[:50]`) durch
  `Paragraph(text, _STYLES["Normal"])` in Tabellenzellen ersetzen
  → automatischer Zeilenumbruch, kein Informationsverlust
- `list_open_review_cases()` zeigt zeitraumunabhängig alle offenen Fälle;
  falls zeitgefilterte Sicht gewünscht: neue Funktion ergänzen


### Schritt 8d – Pflichtauswertungen

(Pflichtenheft v3 §7.12)

Alle acht Kategorien über `report_queries.py` + `csv_exporter.py` abgedeckt:

- Offene Buchungen/Pausen → `list_open_bookings()`
- Korrekturen → `list_corrections()`
- Nachträge → `list_supplements()`
- Mögliche Pausen-/Ruhezeit-/Höchstarbeitszeitverstöße → `list_open_review_cases()`
  (ReviewCaseType POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION,
  POSSIBLE_MAX_HOURS_VIOLATION)
- Buchungen außerhalb Regelzeitfenster → `list_open_review_cases()`
  (ReviewCaseType OUTSIDE_SCHEDULE_WINDOW)
- Warn-/Prüfstatus-Fälle → `list_warn_bookings()`

Alle Auswertungen: filterbar nach Zeitraum und Mitarbeiter, als CSV exportierbar.
In-App-Ansicht: Phase 5 (Präsentation).

Schutz und Archivierung (Regelwerk v3 §17/§18/§20): Exportverzeichnis im
Zugriffsschutz- und Archivierungskonzept; Exportdateien in Backup einbezogen
(Schritt 7b).


### Schritt 8e – Tests

```
tests/integration/test_export.py    – 18 Tests  (report_queries, Filterlogik,
                                                   Pflichtfall V3 §16)
tests/integration/test_csv_export.py – 15 Tests  (CSV-Roundtrips, Korrekturen,
                                                   Nachträge, Verdichtung)
tests/integration/test_pdf.py       – 20 Tests  (PDF-Erzeugung, Inhaltsprüfung,
                                                   Pflichtabschnitte)
```


---

## Schritt 9 – infrastructure/system_check.py  ← OFFEN

(Pflichtenheft v3 §7.10 — spätestens Phase 4, nicht erst Phase 5)

SystemCheck-Modul mit folgenden Prüfpunkten:

- Konfigurationsprüfung: alle erforderlichen `system_config`-Keys vorhanden
- Geräteverfügbarkeit: evdev-Gerät (RFID-Reader + Numpad) erreichbar
- NAS-Erreichbarkeit: Backup-Zielpfad mountbar/schreibbar
- Datenbankzugriff: SQLite-Datei öffenbar, Migrationsstand aktuell
- Grundkonsistenz: keine verwaisten Fremdschlüssel

Ergebnis wird in `system_events` (`event_type='SYSTEM_CHECK'`) protokolliert.
Aufrufbar manuell und als Startprüfung beim Systemstart.
Phase 5 ergänzt nur den UI-Aufrufpunkt (manuell aus Admin-CLI auslösbar).


---

## Verifikation

```
pytest tests/test_migrations.py   –  11 Tests  (Phase 1)
pytest tests/domain/              –  63 Tests  (Phase 2)
pytest tests/application/         – 107 Tests  (Phase 3)
pytest tests/integration/         – 122 Tests  (Phase 4)
pytest tests/e2e/                 –  16 Tests  (Phase 4)
pytest tests/                     – 319 Tests grün gesamt
```


---

## V3 §16 Testpflicht-Abdeckung nach Phase 4

```
>6h ohne Pause              → test_compliance_checks.py  (grün)
>9h ohne ausreichende Pause → test_compliance_checks.py  (grün)
>8h Arbeitszeit             → test_compliance_checks.py + test_book_time.py  (grün)
>10h Arbeitszeit            → test_compliance_checks.py + test_book_time.py  (grün)
Ruhezeitverletzung <11h     → test_book_time.py  (grün)
Systemzeitabweichung        → OFFEN  (Phase 5, Regelwerk v3 §21)
Notfallnachtrag             → test_register_supplement.py  (grün)
Restore-Test                → tests/e2e/test_backup.py  (grün)
Auswertung offener Fälle    → test_export.py  (grün)
```
