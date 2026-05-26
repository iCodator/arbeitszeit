# Planung Phase 4 – Infrastruktur (teilweise offen)

Stand: 2026-05-26. 319 Tests grün.

Offen:

- Schritt 7: Exportdateien (CSV/PDF) fehlen im Backup (Pflichtenheft v3 §12/§14)
- Schritt 9: system_check noch nicht implementiert

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
│   └── uid_hash.py               hash_uid()  (map_rfid_key() liegt in evdev_reader.py)
├── backup/
│   └── backup_service.py         SQLiteBackupService, BackupResult
└── export/
    ├── report_queries.py          BookingRow, CorrectionRow, SupplementRow,
    │                              ReviewCaseRow + Abfragefunktionen
    ├── csv_exporter.py            export_detail(), export_condensed()
    └── pdf_report_service.py      create_daily/weekly/monthly/employee_report()

tests/integration/
├── conftest.py                   ephemere dateibasierte SQLite + Migrations-Fixture,
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
- Migration `0004_supplement_reject_fields_and_review_note.sql` – `rejected_by_user_id`/`rejected_at`
  in `supplements` + `note` in `review_cases` ergänzt (FK auf `user_accounts.id`).
- Migration `0005_time_bookings_device_event_id.sql` – `device_event_id INTEGER` FK
  in `time_bookings` per Table-Rebuild ergänzt. Kein Index auf `device_event_id` angelegt —
  war nicht gefordert, bewusst nicht weiter ausgebaut (keine Lücke, nur offen gelassene Optimierung).

Abgrenzung Schritt 2: Stellt ausschließlich die **Schemafähigkeit** her. Die vollständige operative
Nutzung (Hardware-Schicht erzeugt `device_events`, ID wird via `BookCommand.device_event_id`
durchgereicht) ist Teil der größeren Infrastrukturkette — nicht allein Aufgabe dieses Schritts.

Hinweis: Migration `0001` enthielt noch ältere CHECK-Constraints und ein früheres Supplement-Modell
(ohne `rejected_by_user_id`). Migration `0003` (Phase 3 Vorbereitung) bereinigt BookingStatus-CHECK;
Migrationen 0004–0005 bringen das Schema auf den finalen Stand, den diese Phase beschreibt.


### Schritt 3 – infrastructure/db/unit_of_work.py

`SQLiteUnitOfWork` mit allen 10 Repositories. Transaktionsrahmen:
BEGIN beim `__enter__`, manuelles COMMIT/ROLLBACK.

**commit-or-rollback** (bewusste Sicherheitsentscheidung, gegenüber Planformulierung verschärft):
`__exit__` führt Rollback aus, sobald `_transaction_open` noch True ist — unabhängig
davon, ob eine Exception vorliegt. Kein `commit()` → automatischer Rollback, auch ohne
Exception. `_transaction_open`-Flag verhindert ausschließlich Rollback nach erfolgreich
ausgeführtem `commit()`; Fehler nach `commit()` bleiben in Tests sichtbar. Stillschweigende
Persistenz bei vergessenem Commit ist damit strukturell ausgeschlossen.

`audit_conn`-Muster: `SQLiteUnitOfWork` kapselt nur die Haupttransaktion auf `conn`;
`audit_conn` wird nicht vom UoW gesteuert und bleibt dauerhaft in Autocommit. Audit-Einträge
überleben damit den Rollback der Haupttransaktion. `open_connection()` ist die einzige erlaubte
Stelle zur Erzeugung von `audit_conn` (PRAGMAs, WAL, busy_timeout). Ohne `audit_conn` fällt
das Audit-Log auf `conn` zurück; Einträge vor Rollback gehen verloren.

`rowcount`-Prüfung in `approve()`, `reject()`, `resolve()` gegen stille No-Ops.

10 Tests in `tests/integration/test_unit_of_work.py`:
- `test_commit_macht_daten_sichtbar` — Commit persistiert
- `test_rollback_verwirft_daten` — expliziter Rollback verwirft
- `test_exception_im_with_block_loest_rollback_aus` — Exception → Rollback
- `test_vergessenes_commit_rollt_automatisch_zurueck` — kein Commit → Rollback
- `test_kein_spurious_rollback_nach_commit` — kein zweiter Rollback nach Commit
- `test_transaction_open_flag_nach_commit_false` — Flag nach Commit False
- `test_transaction_open_flag_nach_rollback_false` — Flag nach Rollback False
- `test_mehrfache_transaktionen_hintereinander` — sequentielle Transaktionen unabhängig
- `test_audit_log_bleibt_nach_rollback_erhalten` — Audit-Eintrag überlebt Rollback auf conn
- `test_audit_log_schreibbar_waehrend_conn_nur_liest` — audit_conn unabhängig von conn-Zustand


### Schritt 4 – infrastructure/db/repositories/

10 Repository-Implementierungen. Alle mit:
- Parameterized Statements (`?`-Syntax)
- `RETURNING id` nach INSERT (SQLite ≥ 3.35)
- ISO-8601-Datetimes, `.value`-Enums, INTEGER-Booleans
- `_helpers.py` für `_parse_dt()`, `_parse_date()`, `_parse_time()`

`TimeBookingRepository.set_status()`: SELECT → UPDATE → INSERT atomar;
`NotFoundError` wenn Booking nicht existiert.

`WorkScheduleRepository.get_effective()`: EMPLOYEE-Scope vor GLOBAL (2-Stufen-Query).
Ist kein EMPLOYEE-Eintrag vorhanden, fällt das System automatisch auf GLOBAL zurück
(`test_get_effective_faellt_auf_global_zurueck` ✓). Gilt auch langfristig: Werden alle
mitarbeiterspezifischen Versionen geschlossen ohne neue anzulegen, greift wieder die
globale Praxisregel. Die Admin-CLI muss das kommunizieren.

`WorkScheduleRepository.list_versions(weekday=None, scope_employee_id=None)`:
`scope_employee_id=None` bedeutet **GLOBAL-Scope**, nicht „alle Scopes". Um alle Versionen
anzuzeigen (GLOBAL + alle Mitarbeiter), sind zwei separate Aufrufe nötig. Phase 5 Admin-CLI
muss das bei der Darstellung berücksichtigen.

`WorkScheduleRepository.close_version()`: prüft zusätzlich `valid_until >= valid_from`
→ `ValidationError` bei Verletzung. Test: `test_close_version_mit_ungueltigem_datum_wirft_validation_error` ✓

Überlappende Versionen: Der Repo-Code selbst hat keinen SQL-Constraint gegen gleichzeitig
gültige Versionen für denselben Scope/Wochentag. Die Invariante wird ausschließlich durch
`ManageWorkScheduleUseCase` (close_version vor add) sichergestellt. Das ist bewusst so — komplexe
Geschäftsregeln gehören in die Domänenlogik, nicht in SQLite-Constraints. Direktes Schreiben
an Use Cases vorbei (Ad-hoc-Skripte, manuelle DB-Eingriffe) würde diese Invariante verletzen.

`list_for_employee_on_day()`: Bereichsquery mit `>= day_start` und `< next_day`
(Index-kompatibel, nicht `DATE()`). Test: `test_time_booking_list_for_employee_on_day_filtert_nach_tag` ✓

**UTC-Tagesgrenze (Systemannahme):** `day_start` = `datetime(day.year, day.month, day.day, tzinfo=UTC)`.
Das gesamte System definiert „Kalendertag" als UTC-Tag. Use Cases normalisieren Zeitstempel
konsequent auf UTC vor dem Repo-Aufruf. Der Kommentar im Repo-Code hält das explizit fest und
darf nicht entfernt werden. Bei einer späteren Zeitzonenänderung müssten Buchungsnormalisierung
und alle Auswertungen konsistent angepasst werden.

`list_between(employee_id, from_dt, to_dt)`: halb-offenes Intervall `[from_dt, to_dt)` auf
`booked_at`. Buchungen exakt auf `to_dt` fallen nicht hinein — das ist bewusst und konsistent,
erfordert aber auf Aufruferseite konsequent `to_dt = exklusives Ende` (z. B. `next_day` statt
`end_of_day_inclusive`). Phase 5 soll Hilfsfunktionen für Standardzeiträume anbieten, damit
niemand Intervallgrenzen ad hoc baut (→ `phase5_planung.md`).

`SystemConfigRepository.set_current()`: immer INSERT, nie UPDATE — Versionshistorie bleibt erhalten.
INSERT-Semantik implizit belegt durch `test_system_config_set_current_zweimal_inkrementiert_version`:
zwei Aufrufe erzeugen zwei Zeilen mit Versionsnummern 1 und 2, was nur per INSERT möglich ist.

AuditLog-Kopplung bei `set_current()`: Die Planformulierung „immer zusammen mit AuditLogEntry
in einer Transaktion" ist eine **Verwendungsregel für Aufrufer** (Use Cases), nicht eine
Repository-interne Pflicht. Das Repository selbst schreibt bewusst kein AuditLog — das wäre
eine Kompetenzüberschreitung (Repositories kennen keine Use-Case-Semantik). Korrekte Lesart:
„Jeder Use Case, der `set_current()` aufruft, muss in derselben Transaktion auch einen
AuditLogEntry schreiben."

Kein aktueller Use Case ruft `set_current()` auf. „Repository fertig" bedeutet hier nicht
„Fachfunktion vollständig operativ verfügbar" — die operative Nutzung (Admin-Konfigurationsänderung
mit Audit) ist auf Phase 5 (Admin CLI) verschoben. Das ist kein Mangel in Schritt 4, sondern
die plangemäße Reihenfolge.


### Schritt 5 – tests/integration/

**Scope:** Schritt 5 umfasst ausschließlich die Repository/UoW-Integrationsbasis
(`test_repositories.py`, `test_repositories_roundtrip.py`, `test_unit_of_work.py`).
Export- und Hardware-Integrationstests gehören zu späteren Schritten 6–8.

**DB-Fixture:** Die Planung nennt „In-Memory-SQLite" — tatsächlich verwendet die
Testbasis eine dateibasierte temporäre Test-DB (`tmp_path / "test.db"`) via `open_connection()`
+ `run_migrations()`. Das ist technisch sinnvoller als `:memory:`, weil der `audit_conn`-Test
zwei Verbindungen auf dieselbe Datei benötigt. Korrekte Beschreibung: **„ephemere dateibasierte
SQLite-Testdatenbank mit Migrationen"**, nicht „In-Memory-SQLite".

Testprinzip: echte INSERT/SELECT-Roundtrips, keine Mocks.

**Fixture-Struktur:** `conftest.py` definiert `conn(tmp_path)`, `employee_id(conn)`,
`user_id(conn)` als gemeinsame Basis. Davon abweichend:

- `test_unit_of_work.py` definiert `conn(db_path)` + `audit_conn(db_path)` lokal —
  **technisch notwendig**, weil beide Verbindungen auf dieselbe Datei zeigen müssen
  (Autocommit-Verhalten von `audit_conn` setzt getrennte Verbindung voraus).
- `test_repositories.py` definiert eine eigene `conn`-Fixture — **technisch redundant**
  (identisch zu conftest), aber funktional korrekt.

Pflicht-Testfall WorkScheduleRepository: Zwei EMPLOYEE-Versionen für denselben
Mitarbeiter/Wochentag → `get_effective()` wählt neuere (deterministisch). Test ✓
(`test_workschedule_geteffective_zwei_employee_versionen_waehlt_neuere`)


### Schritt 6 – infrastructure/hardware/

`HardwareReader` als `@runtime_checkable Protocol`. `RawBookingRequest` als Datentransferobjekt.

Schritt 6 liefert die **Leseschicht** (Adapter + Simulation), persistiert aber noch keine
`device_events` — das vollständige betriebliche Orchestrierungsmodell (device_event erzeugen,
ID durchreichen) ist Teil der späteren Betriebsverkettung. Wer 4/6 isoliert liest, sollte
keine vollständige Ende-zu-Ende-Gerätekette erwarten.

`EvdevHardwareReader`: Echte EVDEV-Geräte, `EmptyUidError` für leere UID.
`SimulatedHardwareReader`: vollständige Simulation für Tests.
`hash_uid()` in `uid_hash.py`: SHA-256-Hash der UID.

**Wichtige Funktionsgrenzen (Ergebnis Code-Review):**

- `map_rfid_key()` in `evdev_reader.py` bildet HID-Keycodes auf **Hex-Zeichen** ab
  (für den RFID-UID-Aufbau Zeichen für Zeichen) — **nicht** „Numpad-Key → BookingType".
- Das Numpad-Mapping ist die Konstante `_NUMPAD_TO_BOOKING_TYPE: dict[str, BookingType]`
  (ebenfalls in `evdev_reader.py`); sie wird in `_read_booking_type()` ausgewertet.
  Diese Trennung war im Plantext missverständlich formuliert.
- Buchungsart kommt ausschließlich vom externen USB-Numpad (Pflichtenheft v3 §6 /
  Regelwerk v3 §3). Der verbindliche Ablauf „erst Buchungsart wählen, dann RFID lesen"
  ist im Code korrekt abgebildet.

`read_booking_type()` und `read_uid()` blockieren unbegrenzt; Timeout für Idle-Zustand,
Reconnect-Logik und Geräteausfallbehandlung sind bewusst in die aufrufende Betriebsschicht
(Phase 5/terminal_ui/) verlagert. Phase 5 muss diese Fälle explizit spezifizieren.

7 Adapter-Schnittstellen- und Logiktests (ohne physische EVDEV-Geräte, mapping- und
fehlerlogikfokussiert) in `test_hardware_evdev.py` + 14 Simulator-Tests in
`test_hardware_simulator.py`. Reale Gerätebesonderheiten bleiben bis zur Betriebsschicht
(Phase 5) durch manuelle Smoke-Tests auf Zielhardware zu verifizieren.


### Schritt 7 – infrastructure/backup/

`SQLiteBackupService`: `create_local_backup()`, `sync_to_nas()`, `restore_from()`, `run()`.
`BackupResult` als Ergebnisobjekt.

Audit-Logging über `_log_audit()` via `open_connection()` (eigene Verbindung, kein
Fremdkontext): BACKUP_CREATED, BACKUP_SYNCED_TO_NAS, BACKUP_SYNC_FAILED (mit
`returncode`, `cmd`, `stderr`), RESTORE_COMPLETED.

PRAGMA integrity_check nach Restore. `FileNotFoundError` bei fehlendem Backup.

`sync_to_nas()` nutzt `rsync --archive --delete`: striktes Spiegeln des lokalen
Backup-Verzeichnisses auf den NAS-Pfad. `--delete` entfernt am NAS-Ziel alles,
was lokal nicht mehr existiert. Das ist konsistent für einen Mirrors-Einsatz, aber
**archivierungskritisch**: Falls der NAS als längerfristige Ablage (nicht nur als
Spiegel) gedacht ist, müsste Archiv- und Mirror-Pfad getrennt oder `--delete`
bewusst deaktiviert werden. Diese Grenzziehung muss in der Betriebsdokumentation
explizit festgelegt sein (Regelwerk v3 §17/§18).

RESTORE_COMPLETED wird nach der Wiederherstellung in die **neu aktive (wiederhergestellte)**
Datenbank geschrieben, nicht in den Sicherungsstand. Das ist technisch sauber und
inhaltlich korrekt: Der Eintrag beschreibt den Ist-Zustand nach dem Restore. Die
Betriebsdokumentation muss festhalten, dass dieses Event nicht Teil des gesicherten
Altstands ist.

**Trigger/Betriebsebene:** Die Planung nennt „systemd-Timer/cron + optional manuell".
`scripts/backup.py` deckt die manuelle Auslösbarkeit ab. Der zeitgesteuerte Trigger
(systemd-Timer/cron-Konfiguration) ist kein Python-Artefakt und gehört zur
Betriebsintegration — Schritt 7 liefert Service + Script, nicht die
Deployment-Konfiguration.

16 e2e-Tests in `tests/e2e/test_backup.py` (inkl. Audit-Verifikation, Mock-NAS).
Deckt V3 §14/§20 und Regelwerk v3 §20 ab. V3 §16-Testpflicht „Restore-Test
mit echtem Backup" erfüllt (PRAGMA integrity_check explizit).

### Schritt 7 Nachtrag – Exportdateien in Backup einbeziehen  ← OFFEN

(Pflichtenheft v3 §12/§14, Regelwerk v3 §17/§18/§20)

`SQLiteBackupService` kennt aktuell nur `db_path` und `backup_dir`; Exportdateien
(CSV + PDF aus `export.export_dir`) werden nicht gesichert. Plan und Pflichtenheft
verlangen ihre Einbeziehung ausdrücklich — das ist eine reale Implementierungslücke,
keine Formulierungsfrage. Muss vor Phase-5-Start abgeschlossen sein.

Umfang:

- `SQLiteBackupService.__init__()` um optionalen `export_dir: Path | None`-Parameter
  erweitern
- `create_local_backup()`: Exportverzeichnis in das lokale Backup-Verzeichnis kopieren
  (z. B. `shutil.copytree` in ein Unterverzeichnis `exports/`)
- `sync_to_nas()` deckt das bereits ab, sobald `export_dir`-Inhalt im `backup_dir` liegt
- `scripts/backup.py`: `--export-dir`-Argument ergänzen
- `tests/e2e/test_backup.py`: Tests um Sicherung und Wiederauffinden von Exportdateien
  erweitern


### Schritt 1b – BookUseCase vervollständigen

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


### Schritt 1c – Rollenprüfung in alle schreibenden Use Cases

(Pflichtenheft v3 §5 / Regelwerk v3 §16)

- `RegisterSupplementUseCase`: Rolle in {ADMIN, REVIEWER}, sonst `PermissionDeniedError`
- `CorrectBookingUseCase`: Rolle in {ADMIN, REVIEWER}
- `ManageWorkScheduleUseCase`: Rolle ADMIN; `changed_by_user_id` darf nicht None sein
- `ApproveSupplementUseCase` / `RejectSupplementUseCase`: Rolle in {REVIEWER, ADMIN}

Testfälle: `PermissionDeniedError` bei falscher Rolle, bei unbekanntem Benutzer (`get_by_id()` → `None`)
und bei inaktivem Benutzer (`user.is_active == False`). Alle drei Fälle werden einheitlich mit
`PermissionDeniedError` abgewiesen — keine Unterscheidung nach Fehlerursache nach außen.


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

Detaillierter CSV-Spalten: `buchungs_id`, `mitarbeiter_nr`, `mitarbeiter_name`,
`datum`, `uhrzeit`, `buchungsart`, `status`, `quelle`, `ist_nachtrag`,
`ist_korrigiert`, `dauer_minuten`.

Verdichteter CSV-Spalten: `mitarbeiter_nr`, `mitarbeiter_name`, `datum`,
`nettoarbeitszeit_minuten`, `nettopausenzeit_minuten`, `pausenanzahl`,
`anzahl_buchungen`, `offene_buchungen`, `warn_buchungen`,
`pruefpflicht_buchungen`, `korrekturen`, `nachtraege`.

`_day_stats()` als Zustandsmaschine: Pausen korrekt aus Nettoarbeitszeit
herausgerechnet; `pausenanzahl` zählt BREAK_START-Ereignisse (also auch
noch offene Pausen); `nettopausenzeit_minuten` zählt nur abgeschlossene
Pausen (BREAK_START/BREAK_END-Paare).

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

Beide Varianten vorhanden:
- `list_open_review_cases()` — alle offenen Fälle ohne Zeitgrenze
  (sinnvoll für globale Prüfübersicht)
- `list_open_review_cases_in_period(from_dt, to_dt, employee_id=None)` —
  zeitraumgefiltert nach detected_at (Pflichtenheft v3 §7.12)


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
