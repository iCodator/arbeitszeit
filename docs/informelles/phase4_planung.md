# Planung Phase 4 – Infrastruktur

Stand: 2026-05-23. Basiert auf Pflichtenheft v3 und Regelwerk v3.
Schritte 1–7d vollständig abgeschlossen (266 Tests grün). Schritt 8 (Export) offen.

---

## Ausgangslage nach Phase 3

Phase 3 hat folgende Ports und Use Cases fertiggestellt:

  src/arbeitszeit/application/
  ├── unit_of_work.py        UnitOfWork Protocol (10 Repos)
  ├── commands.py            BookCommand, CreateSupplementCommand,
  │                          CreateCorrectionCommand, ChangeWorkScheduleCommand
  ├── results.py             BookResult, SupplementResult,
  │                          CorrectionResult, WorkScheduleChangeResult
  └── use_cases/
      ├── book_time.py           BookUseCase
      ├── register_supplement.py RegisterSupplementUseCase
      ├── correct_booking.py     CorrectBookingUseCase
      ├── manage_work_schedule.py ManageWorkScheduleUseCase
      ├── approve_supplement.py  ApproveSupplementUseCase  (Phase 3b, erledigt)
      └── reject_supplement.py   RejectSupplementUseCase   (Phase 3b, erledigt)


---

## Architekturentscheidungen für Phase 4


### Datumsformat in SQLite

SQLite speichert alle Zeitwerte als TEXT im ISO-8601-Format:
  booked_at      -> "2025-03-10T08:00:00+00:00"  (datetime mit Timezone)
  valid_from     -> "2025-01-01"                  (date)
  start_time     -> "07:30"                       (time, timespec='minutes')

Lesen:  datetime.fromisoformat(row['booked_at'])
        date.fromisoformat(row['valid_from'])
        time.fromisoformat(row['start_time'])
Schreiben: dt.isoformat(), d.isoformat(), t.isoformat(timespec='minutes')

Alle Datetimes werden timezone-aware mit UTC gespeichert und gelesen.


### Enum-Mapping

Enums (StrEnum) werden als TEXT in SQLite gespeichert (der .value-String).
Schreiben: enum_instance.value
Lesen:     EnumClass(row['column_name'])


### Booleans

SQLite: INTEGER 0 oder 1.
Lesen:  bool(row['is_active'])
Schreiben: 1 if employee.is_active else 0


### SQL-Injection-Schutz

Alle Queries ausschliesslich mit Parameterized Statements (?-Syntax).
Niemals String-Interpolation in SQL-Strings.


### set_status() – Infrastruktur-Seiteneffekt

TimeBookingRepository.set_status(booking_id, status, reason, changed_by_user_id)
führt zwei Operationen atomisch aus:
  1. UPDATE time_bookings SET current_status = ? WHERE id = ?
  2. INSERT INTO booking_status_history (time_booking_id, old_status,
     new_status, reason, changed_by_user_id, changed_at) VALUES (...)

Die alte Status-Zeile muss vor dem UPDATE gelesen werden (SELECT current_status).
Dieser Seiteneffekt ist Infrastruktur-Verhalten und findet nicht in Fakes statt.


### SystemConfigRepository – kein UPDATE

set_current() schreibt immer eine neue Zeile (INSERT), nie UPDATE.
Konfigurationsänderungen sind versioniert; history bleibt erhalten.
Immer zusammen mit AuditLogEntry in einer UnitOfWork-Transaktion.


### WorkScheduleRepository – Scope-Priorität

get_effective(weekday, on_date, employee_id=None):
  1. Wenn employee_id angegeben: zuerst EMPLOYEE-Scope prüfen.
     SELECT ... WHERE scope_type = 'EMPLOYEE' AND scope_employee_id = ?
     AND weekday = ? AND valid_from <= ? AND (valid_until IS NULL OR valid_until >= ?)
     ORDER BY valid_from DESC LIMIT 1
  2. Falls kein EMPLOYEE-Treffer (oder employee_id ist None): GLOBAL-Scope.
  EMPLOYEE-Scope hat immer Vorrang vor GLOBAL.

close_version(version_id, valid_until):
  Prüft zusätzlich, dass valid_until >= valid_from der Version.
  Use Case berechnet (new_valid_from - 1 Tag); Repo sichert die Bedingung ab.


### ApproveSupplementUseCase – Buchungslogik obligatorisch

Ein genehmigter Nachtrag erzeugt zwingend eine TimeBooking mit:
  - source = BookingSource.MANUAL
  - vollständiger Compliance-Bewertung (_evaluate_booking aus book_time.py)
  - ReviewCases pro ComplianceFlag
  - eigenem AuditLogEntry (event_type="SUPPLEMENT_APPROVED")

Die blosse Statusänderung des Supplements (supplement_repo.approve()) ohne
Buchungserzeugung ist fachlich unvollständig. Niemals so umsetzen.


---

## Zielstruktur

  src/arbeitszeit/
  ├── application/             (Phase 3, abgeschlossen)
  └── infrastructure/
      ├── db/
      │   ├── unit_of_work.py      SQLiteUnitOfWork  ✓
      │   └── repositories/        10 Repos          ✓
      ├── hardware/                EvdevHardwareReader, Simulator  ✓
      ├── backup/                  SQLiteBackupService  ✓
      └── export/                  CSV + PDF  (Schritt 8, offen)

  tests/
  ├── application/             (Phase 3, abgeschlossen)
  ├── integration/
  │   ├── conftest.py          In-Memory-SQLite + Migrations-Fixture  ✓
  │   ├── test_repositories.py      ✓
  │   ├── test_repositories_roundtrip.py  ✓
  │   ├── test_unit_of_work.py      ✓
  │   └── test_hardware_simulator.py  ✓
  └── e2e/
      └── test_backup.py       16 Tests  ✓


---

## Fehlersemantik – bereits vereinheitlicht (Phase 3)

In allen Use Cases ist employee is None klar als NotFoundError behandelt
und not employee.is_active als InactiveEmployeeError. Gilt für:
  BookUseCase, CorrectBookingUseCase, RegisterSupplementUseCase
  (und ApproveSupplementUseCase ab Schritt 1 unten).
Diese Trennung ist Voraussetzung für konsistente Integrationstests in Phase 4.


---

## Implementierungsreihenfolge


### Schritt 1 – use_cases/approve_supplement.py  ✓ ERLEDIGT

Pflichtbestandteil: genehmigter Nachtrag erzeugt zwingend eine TimeBooking mit
vollständiger Compliance-Bewertung. Rollenprüfung (REVIEWER, ADMIN) in Schritt 7d
nachgezogen.


### Schritt 2 – use_cases/reject_supplement.py  ✓ ERLEDIGT

Rollenprüfung (REVIEWER, ADMIN) in Schritt 7d nachgezogen.


### Schritt 3 – Migration 0005  ✓ ERLEDIGT

device_event_id als nullable Spalte in time_bookings ergänzt.


### Schritt 4 – infrastructure/db/unit_of_work.py  ✓ ERLEDIGT

SQLiteUnitOfWork mit allen 10 Repos. BEGIN/COMMIT/ROLLBACK manuell.
rowcount-Prüfung in approve(), reject(), resolve() gegen stille No-Ops.


### Schritt 5 – infrastructure/db/repositories/  ✓ ERLEDIGT

10 Repository-Implementierungen. Integrationstests in tests/integration/.


### Schritt 6 – tests/integration/  ✓ ERLEDIGT

Fixture conftest.py + Roundtrip-Tests + rowcount-Tests +
Pflicht-Testfall WorkSchedule (zwei EMPLOYEE-Versionen, neuere gewinnt).


### Schritt 7 – infrastructure/hardware/  ✓ ERLEDIGT

HardwareReader-Protocol (@runtime_checkable), EvdevHardwareReader,
SimulatedHardwareReader, hash_uid(). EmptyUidError für leere UID.
Buchungsart kommt ausschliesslich vom externen USB-Numpad (kein Systeminput).


### Schritt 7b – infrastructure/backup/  ✓ ERLEDIGT

SQLiteBackupService: create_local_backup(), sync_to_nas(), restore_from(), run().
Audit-Logging via SQLiteAuditLogRepository (BACKUP_CREATED, BACKUP_SYNCED_TO_NAS,
BACKUP_SYNC_FAILED mit cmd+stderr, RESTORE_COMPLETED).
PRAGMA integrity_check nach Restore. FileNotFoundError bei fehlendem Backup.
16 e2e-Tests in tests/e2e/test_backup.py (inkl. Audit-Verifikation, Mock-Test).
Deckt V3 §14/§20 und Regelwerk v3 §20 ab. V3 §16-Testpflicht "Restore-Test mit
echtem Backup" ist durch tests/e2e/test_backup.py erfüllt.

Sicherungsumfang (Regelwerk v3 §17/§18/§20): Neben der SQLite-Datenbankdatei
werden Exportdateien (CSV + PDF aus system_config: export.export_dir) in die
Sicherung einbezogen. Exportdateien sind auditpflichtige Ausgabedokumente.
Backup-Skript sichert export_dir zusammen mit der DB-Datei auf denselben NAS-Pfad.


### Schritt 7c – BookUseCase vervollständigen  ✓ ERLEDIGT

(V3 §7.9 Pflichtanforderung / ArbZG §5 + Regelwerk v3 §5/§9/§10)

**Ruhezeitprüfung** in use_cases/book_time.py:

- Bei GO/BREAK_END Vortagesbuchungen laden:
    prev = time_booking_repo.list_for_employee_on_day(employee.id, date - 1 Tag)
- flags += check_rest_period(projected, prev)
- Analog in ApproveSupplementUseCase (Nachtragsbuchungen werden gleich geprüft)
- FakeTimeBookingRepository unterstützt list_for_employee_on_day bereits →
  Fake-Test ohne echte DB möglich

Neuer Testfall in tests/application/test_book_time.py:

- GO nach <11h Ruhezeit → REST_PERIOD_VIOLATION ReviewCase + status WARN/NEEDS_REVIEW

**Abweisungsprotokoll** (Regelwerk v3 §5):

- Unbekannte RFID-Karte: AuditLogEntry (BOOKING_REJECTED_UNKNOWN_CARD) vor Fehlerraising
- Inaktive Karte: AuditLogEntry (BOOKING_REJECTED_INACTIVE_CARD) vor Fehlerraising
- Abgewiesene Buchungsversuche sind auditpflichtig; kein commit() nötig für audit_log
  (Infrastruktur-Detail: AuditLog-INSERT kann in eigener Transaktion erfolgen)

Neuer Testfall: Abgewiesene Buchung erzeugt Audit-Log-Eintrag.

**Regelzeitfenster-Check** (Regelwerk v3 §9/§10):

- work_schedule_repo.get_effective(weekday, on_date, employee_id) aufrufen
- Liegt booked_at.time() ausserhalb [schedule.start_time, schedule.end_time]:
  WARN-Flag erzeugen, ReviewCase anlegen
- Neuer Testfall: COME ausserhalb Regelzeitfenster → WARN-Status

Deckt V3 §7.9 (ArbZG §5) und V3 §16-Testpflicht "Unterschreitung der Ruhezeit" ab.


### Schritt 7d – Rollenprüfung in alle schreibenden Use Cases integrieren  ✓ ERLEDIGT

(Pflichtenheft v3 §5 / Regelwerk v3 §16)

Nachrüstung der Autorisierung in bereits implementierte Use Cases:

- RegisterSupplementUseCase: user_account_repo.get_by_id(cmd.recorded_by_user_id)
  → Rolle in {ADMIN, REVIEWER}, sonst PermissionDeniedError
- CorrectBookingUseCase: user_account_repo.get_by_id(cmd.corrected_by_user_id)
  → Rolle in {ADMIN, REVIEWER}, sonst PermissionDeniedError
- ManageWorkScheduleUseCase: user_account_repo.get_by_id(cmd.changed_by_user_id)
  → Rolle ADMIN; changed_by_user_id darf nicht None sein

ApproveSupplementUseCase und RejectSupplementUseCase haben Rollenprüfung
bereits seit Schritt 1 (s. dort).

Neue Testfälle in tests/application/ für jede Prüfung:
PermissionDeniedError bei falscher Rolle und bei None.


### Offener V3-Punkt – Systemzeitprotokollierung  ← OFFEN

(Pflichtenheft v3 §9.3 / Regelwerk v3 §21)

NTP-Synchronisation ist Betriebsvoraussetzung (system_events-Tabelle vorhanden).
Zeitsprünge und manuelle Uhrzeitänderungen müssen erkannt, protokolliert und
fachlich geprüft werden.

Geplante Umsetzung (spätestens Phase 5 / Betriebsschicht):

- Systemzeit-Monitor erkennt Sprünge > Schwellenwert
- INSERT in system_events (event_type='CLOCK_JUMP', details_json mit Differenz)
- Optional: AuditLogEntry für prüfpflichtige Fälle

Deckt V3 §9.3, Regelwerk v3 §21 und V3 §16-Testpflicht "Systemzeitabweichung" ab.


---

## Schritt 8 – infrastructure/export/  ← IN ARBEIT

Kein Excel/openpyxl. PDF-Bibliothek: **reportlab** (rein Python, stabil,
tabellarische Verwaltungsberichte, keine externen Binaries, Linux-kompatibel).

Kernprinzip (Regelwerk v3 §11): Statuswerte, Warnfälle, Korrekturen,
Nachträge und offene Fälle kommen für alle Exportwege aus derselben
Ableitungsschicht — nicht drei verschiedene Implementierungen.

### Zielstruktur export/

  src/arbeitszeit/infrastructure/export/
  ├── report_queries.py      gemeinsame Datenselektion + fachliche Projektion
  ├── csv_exporter.py        detaillierter + verdichteter CSV-Export
  └── pdf_report_service.py  Tages-/Wochen-/Monats-/Mitarbeiterberichte (reportlab)


### Schritt 8a – report_queries.py (Datenbasis)

Gemeinsame Abfrage- und Projektionsschicht für alle Exportwege:

- Filterbar nach Zeitraum (von/bis) und Mitarbeiter (optional)
- Liefert normierte Datenstrukturen (dataclasses/namedtuples), keine rohen Rows
- Ableitung aus DB-Zuständen (Regelwerk v3 §11):
  - offene Buchungen und offene Pausen
  - Warnsachverhalte, Prüfhinweise und statusbasierte Prüffälle
    (WARN, NEEDS_REVIEW, POSSIBLE_*, OPEN, CORRECTED, CLOSED_WITH_NOTE)
  - Korrekturen mit altem/neuem Zustand, Begründung, Person, Zeitstempel
  - Nachträge mit Kennzeichnung als nachträglich erfasster Datensatz,
    Begründung und Freigabebezug, soweit vorgesehen
  - Buchungen außerhalb Regelzeitfenster
  - mögliche Pausen-/Ruhezeit-/Höchstarbeitszeitverstöße
- Identische Datengrundlage für CSV, PDF und spätere UI-Pflichtauswertungen


### Schritt 8b – csv_exporter.py

Detaillierter CSV-Export (Pflichtenheft v3 §7.11):

- MA-Kennung/-name, Datum, Uhrzeit, Buchungsart, ableitbare Dauer, Status,
  Korrektur-/Nachtragskennzeichnung, Prüfflags
- Verdichteter CSV-Export: summierte Arbeitszeit, Pausenanzahl/-dauer,
  Anzahl offener Buchungen, Warn-/Prüfstatus-Anzahl, Korrekturen/Nachträge
- Nachvollziehbare Benennung:
    export_detail_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
    export_verdichtet_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
- Ablage in Exportverzeichnis (system_config: export.export_dir)


### Schritt 8c – pdf_report_service.py

PDF-Berichte (Pflichtenheft v3 §7.11, Regelwerk v3 §12/§13):

- Tages-, Wochen-, Monats- und Mitarbeiterberichte
- Tabellarisch + kurze Erläuterungen zu offenen/auffälligen Fällen
- Pflichtfelder: Zeitraum, Erstellungszeitpunkt, Mitarbeiter-/Praxiszuordnung
- Korrekturen: alter/neuer Zustand, Begründung, Person, Zeitstempel
- Nachträge als Nachtrag erkennbar gekennzeichnet
- Statuswerte konsistent aus DB-Zuständen abgeleitet (via report_queries.py)
- Nachvollziehbare Benennung:
    bericht_tag_YYYY-MM-DD_YYYYMMDDTHHMMSSZ.pdf
    bericht_woche_YYYY-WNN_YYYYMMDDTHHMMSSZ.pdf
    bericht_monat_YYYY-MM_YYYYMMDDTHHMMSSZ.pdf
    bericht_mitarbeiter_NNNN_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.pdf


### Schritt 8d – Pflichtauswertungen (Pflichtenheft v3 §7.12)

Exportierbare Pflichtauswertungen über report_queries.py:

- Offene Buchungen und offene Pausen
- Korrekturen (alter/neuer Zustand, Begründung, Person, Zeitstempel)
- Nachträge (als Nachtrag gekennzeichnet, Begründung, Freigabebezug)
- Mögliche Pausenverstöße / Ruhezeitverstöße / Höchstarbeitszeitüberschreitungen
- Buchungen außerhalb Regelzeitfenster
- Buchungen und Vorgänge mit Warn- oder Prüfstatus

Alle Auswertungen: filterbar nach Zeitraum und Mitarbeiter, sowohl als
CSV exportierbar als auch später in App einsehbar (Phase 5 Präsentation).

Schutz und Archivierung (Regelwerk v3 §17/§18/§20):

- Exportverzeichnis in Zugriffsschutzkonzept einbezogen
- Exportdateien nach Archivierungs-/Löschkonzept behandeln
- Exportdateien in Backup-/Restore-Prüfungen einbeziehen


### Schritt 8e – Tests

  tests/integration/test_export.py  – CSV-Roundtrips gegen In-Memory-DB,
                                       Filterlogik, Korrektur-/Nachtrags-
                                       kennzeichnung, OPEN/WARN-Ableitung
  tests/integration/test_pdf.py     – PDF-Erzeugung, Seitenanzahl,
                                       Schlüsselfelder (Zeitraum, MA-Zuordnung)
  Pflichtfall: "Auswertung offener und auffälliger Fälle" (Pflichtenheft v3 §16)


---

## Schritt 9 – infrastructure/system_check.py  ← OFFEN

(Pflichtenheft v3 §7.10 — spätestens Phase 4, nicht erst Phase 5)

SystemCheck-Modul mit folgenden Prüfpunkten:

- Konfigurationsprüfung: alle erforderlichen system_config-Keys vorhanden
- Geräteverfügbarkeit: evdev-Gerät (RFID-Reader + Numpad) erreichbar
- NAS-Erreichbarkeit: Backup-Zielpfad mountbar/schreibbar
- Datenbankzugriff: SQLite-Datei öffenbar, Migrationsstand aktuell
- Grundkonsistenz: keine verwaisten Fremdschlüssel

Ergebnis wird in system_events (event_type='SYSTEM_CHECK') protokolliert.
Aufrufbar manuell und als Startprüfung beim Systemstart.
Phase 5 ergänzt nur den UI-Aufrufpunkt (manuell aus Admin-CLI auslosbar).


---

## Verifikation (laufend)

  pytest tests/                # 266 Tests grün (Stand 2026-05-23, nach Schritt 7d + Use-Case-Review)
  pytest tests/integration/    # Integrationstests grün
  python -m ruff check .       # keine Verstösse
