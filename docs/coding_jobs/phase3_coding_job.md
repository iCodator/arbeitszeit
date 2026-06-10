# Programmieraufgabe Phase 3 – arbeitszeit

## Quellenbasis

Diese Aufgabe basiert auf den Dateien `phase3_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

## Ziel

Implementiere **ausschließlich Phase 3** des Projekts `arbeitszeit`. Phase 3 umfasst die **Application-Schicht**: Commands, Results, `UnitOfWork` als Abstraktion, die vier zentralen Use Cases sowie In-Memory-Fakes für Application-Tests. Grundlage dieser Aufgabenabgrenzung sind `phase3_planung_konkret.md` und `planung_gesamt.md`.

Die Aufgabe ist erfolgreich abgeschlossen, wenn die fachlichen Abläufe für Buchen, Nachtrag, Korrektur und Regelarbeitszeitänderung vollständig in der Application-Schicht orchestriert sind, ohne echte SQLite-Infrastruktur, Export, Hardware oder Benutzeroberflächen einzuführen. Diese Zielgrenze wird in `phase3_planung_konkret.md` und `planung_gesamt.md` ausdrücklich gezogen.

## Strikte Grenzen

Arbeite streng innerhalb dieses Umfangs. **Nicht** Teil dieser Aufgabe sind insbesondere:

- echte SQLite-Repositories und echte DB-`UnitOfWork` aus Phase 4 (`phase3_planung_konkret.md`, `planung_gesamt.md`),
- Migrationen und DB-Grundgerüst aus Phase 1 (`phase3_planung_konkret.md`, `planung_gesamt.md`),
- Domänenmodellierung aus Phase 2, soweit sie nicht nur verwendet wird (`phase3_planung_konkret.md`),
- Backup, Restore, Export, PDF, Report-Queries und Systemcheck aus Phase 4 (`phase3_planung_konkret.md`),
- Terminal-UI, Admin-CLI und betriebliche Orchestrierung aus Phase 5 (`phase3_planung_konkret.md`).

Sobald SQL, evdev, Dateisystemzugriff, Exportdateien, echte DB-Transaktionen oder CLI-Ausgabe nötig wären, ist die Phasengrenze verletzt. Diese Abgrenzung ist in `phase3_planung_konkret.md` und `planung_gesamt.md` ausdrücklich festgelegt.

## Verbindlicher Lieferumfang

Erzeuge oder vervollständige mindestens die folgenden Bestandteile:

- `src/arbeitszeit/application/unit_of_work.py` (`phase3_planung_konkret.md`, `planung_gesamt.md`)
- `src/arbeitszeit/application/commands.py` (`phase3_planung_konkret.md`, `planung_gesamt.md`)
- `src/arbeitszeit/application/results.py` (`phase3_planung_konkret.md`, `planung_gesamt.md`)
- `src/arbeitszeit/application/use_cases/manage_work_schedule.py` (`phase3_planung_konkret.md`, `planung_gesamt.md`)
- `src/arbeitszeit/application/use_cases/register_supplement.py` (`phase3_planung_konkret.md`, `planung_gesamt.md`)
- `src/arbeitszeit/application/use_cases/correct_booking.py` (`phase3_planung_konkret.md`, `planung_gesamt.md`)
- `src/arbeitszeit/application/use_cases/book_time.py` (`phase3_planung_konkret.md`, `planung_gesamt.md`)
- `tests/application/fakes.py` (`phase3_planung_konkret.md`, `planung_gesamt.md`)
- `tests/application/test_manage_work_schedule.py` (`phase3_planung_konkret.md`)
- `tests/application/test_register_supplement.py` (`phase3_planung_konkret.md`)
- `tests/application/test_correct_booking.py` (`phase3_planung_konkret.md`)
- `tests/application/test_book_time.py` (`phase3_planung_konkret.md`)

Optional vorbereitet werden dürfen `ApproveSupplementCommand` und `RejectSupplementCommand`, aber **nicht** deren vollständige Use Cases. Diese Präzisierung ergibt sich aus `phase3_planung_konkret.md` und `planung_gesamt.md`.

## Aufgabenbeschreibung

### 1. `UnitOfWork`-Abstraktion definieren

Implementiere in `application/unit_of_work.py` das `UnitOfWork`-Protocol mit Context-Manager-Support. Es muss Zugriff auf alle für Phase 3 benötigten Repository-Ports geben. Dies wird in `phase3_planung_konkret.md` und `planung_gesamt.md` konkret vorgegeben.

Pflichtbestandteile:
- `employee_repo`
- `user_account_repo`
- `rfid_card_repo`
- `time_booking_repo`
- `work_schedule_repo`
- `review_case_repo`
- `supplement_repo`
- `booking_correction_repo`
- `audit_log_repo`
- `system_config_repo`
- `commit()`
- `rollback()`
- `__enter__()`
- `__exit__()`

Quelle für diese Liste: `phase3_planung_konkret.md`, `planung_gesamt.md`.

### 2. Commands modellieren

Implementiere in `application/commands.py` alle Commands als frozen Dataclasses mit `slots=True`. Diese Form wird in `phase3_planung_konkret.md` ausdrücklich verlangt.

Verbindlich sind:
- `BookCommand`
- `CreateSupplementCommand`
- `CreateCorrectionCommand`
- `ChangeWorkScheduleCommand`
- optional vorbereitbar: `ApproveSupplementCommand`, `RejectSupplementCommand`

Wichtig: Die eigentlichen Freigabe-/Ablehnungs-Use-Cases gehören noch nicht in Phase 3. Diese Grenze ist in `phase3_planung_konkret.md` und `planung_gesamt.md` ausdrücklich dokumentiert.

### 3. Results modellieren

Implementiere in `application/results.py` die Ergebnisobjekte als frozen Dataclasses mit `slots=True`.

Verbindlich sind:
- `BookResult`
- `SupplementResult`
- `CorrectionResult`
- `WorkScheduleChangeResult`

Die Result-Objekte müssen fachliche Ergebnisse transportieren, ohne Infrastrukturdetails offenzulegen. Quelle: `phase3_planung_konkret.md`, `planung_gesamt.md`.

### 4. Fakes für Application-Tests implementieren

Implementiere in `tests/application/fakes.py` In-Memory-Implementierungen aller benötigten Repository-Ports sowie `FakeUnitOfWork`.

Verpflichtende Anforderungen:
- Speicherung je Repository in `dict[int, Entity]` plus Auto-Inkrement-ID,
- `FakeUnitOfWork` mit `committed` und `rolled_back`,
- Rollback bei Exception in `__exit__()`,
- `FakeTimeBookingRepository.set_status()` über `dataclasses.replace()`,
- `FakeWorkScheduleRepository.get_effective()` mit Vorrang von EMPLOYEE vor GLOBAL,
- `FakeWorkScheduleRepository.close_version()` muss Entitätsinvarianten respektieren.

Diese Vorgaben stammen aus `phase3_planung_konkret.md` und `planung_gesamt.md`. Simuliere **keine** Infrastruktur-Seiteneffekte wie echtes `booking_status_history`-Persistieren.

### 5. `ManageWorkScheduleUseCase` implementieren

Implementiere in `application/use_cases/manage_work_schedule.py` den Use Case zum Ändern von Regelarbeitszeiten.

Verbindlicher Ablauf:
1. Bestehende wirksame Version laden.
2. `ConflictError`, wenn `current.valid_from == cmd.valid_from`.
3. `ValidationError`, wenn für denselben Scope und Wochentag bereits eine spätere Version existiert.
4. Vorherige Version schließen.
5. Neue Version anlegen.
6. `AuditLogEntry` anlegen.
7. Commit ausführen und `WorkScheduleChangeResult` zurückgeben.

Zusätzlich gilt bereits in Phase 3 die Rollenprüfung: Nur `ADMIN` darf diesen Use Case ausführen; `changed_by_user_id` darf nicht `None` sein. Quellen: `phase3_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4`.

### 6. `RegisterSupplementUseCase` implementieren

Implementiere in `application/use_cases/register_supplement.py` den Use Case zum Anlegen eines Nachtrags.

Verbindlicher Ablauf:
1. Mitarbeiter laden, sonst `NotFoundError`.
2. `Supplement` mit `ApprovalStatus.PENDING` anlegen.
3. `ReviewCase(MANUAL_ENTRY_REVIEW)` immer anlegen.
4. `AuditLogEntry` anlegen.
5. Commit ausführen und `SupplementResult` zurückgeben.

Zusätzlich gilt die Rollenprüfung: `recorded_by_user_id` muss einem aktiven Benutzer mit Rolle `ADMIN` oder `REVIEWER` entsprechen. Quellen: `phase3_planung_konkret.md`, `planung_gesamt.md`, `Regelwerk v4`.

### 7. `CorrectBookingUseCase` implementieren

Implementiere in `application/use_cases/correct_booking.py` den Use Case für Korrekturen.

Verbindlicher Ablauf:
1. Ursprungsbuchung laden, sonst `NotFoundError`.
2. `BookingCorrection` mit altem und neuem Zustand anlegen.
3. Ursprungsbuchung auf `CORRECTED` setzen.
4. Nur passende offene Review Cases schließen.
5. `AuditLogEntry` anlegen.
6. Commit ausführen und `CorrectionResult` zurückgeben.

Die Ursprungsbuchung darf **nicht** fachwidrig überschrieben werden. Der neue Zustand lebt ausschließlich in `BookingCorrection`. Quellen: `phase3_planung_konkret.md`, `planung_gesamt.md`, `Regelwerk v4`.

### 8. `BookUseCase` implementieren

Implementiere in `application/use_cases/book_time.py` den zentralen Buchungs-Use-Case.

Verbindlicher Ablauf:
1. RFID-Karte laden; unbekannte oder inaktive Karte führt zu `UnknownCardError` bzw. `InactiveCardError`, jeweils mit Audit-Pflicht.
2. Mitarbeiter laden; inaktiver Mitarbeiter führt zu `InactiveEmployeeError`.
3. Tagesbuchungen laden.
4. Buchungsfolge validieren; Fehler führen zu `InvalidBookingSequenceError` oder `OpenPhaseConflictError`.
5. Status bestimmen:
   - `COME` und `BREAK_START` → `OPEN`
   - `GO` und `BREAK_END` → Bewertung des projizierten Verlaufs mit `check_break_compliance()` und `check_max_hours()`
6. Buchung anlegen.
7. Pro `ComplianceFlag` einen `ReviewCase` anlegen.
8. `AuditLogEntry` anlegen.
9. Commit ausführen und `BookResult` zurückgeben.

Wichtig: Die vollständige Integration von `check_rest_period()` gehört laut `phase3_planung_konkret.md` und `planung_gesamt.md` **noch nicht** zum verpflichtenden Kern von Phase 3, weil dafür Vortageskontext benötigt wird und dies erst in Phase 4 operativ geschlossen wird.

### 9. Application-Tests implementieren

Erstelle unter `tests/application/` belastbare Use-Case-Tests gegen die Fakes.

Mindestens abzudecken sind:
- Commit-/Rollback-Verhalten,
- Rollenprüfung,
- Konflikt- und Fehlerfälle,
- Statuswechsel,
- Erzeugung von Review Cases,
- korrekte Behandlung von Korrekturen und Nachträgen.

Diese Testziele ergeben sich aus `phase3_planung_konkret.md` und `planung_gesamt.md`.

## Akzeptanzkriterien

Die Aufgabe ist nur dann erfüllt, wenn alle folgenden Kriterien erfüllt sind:

- `UnitOfWork`, Commands und Results sind vollständig und konsistent modelliert (`phase3_planung_konkret.md`, `planung_gesamt.md`).
- Fakes erlauben realistische, aber reine In-Memory-Tests (`phase3_planung_konkret.md`, `planung_gesamt.md`).
- `ManageWorkScheduleUseCase`, `RegisterSupplementUseCase`, `CorrectBookingUseCase` und `BookUseCase` setzen die dokumentierten fachlichen Abläufe korrekt um (`phase3_planung_konkret.md`, `planung_gesamt.md`).
- Rollenprüfungen in den schreibenden Phase-3-Use-Cases sind integriert (`phase3_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4`).
- `BookUseCase` behandelt Status und Review Cases fachlich korrekt auf Basis der in Phase 3 verfügbaren Prüfhilfen (`phase3_planung_konkret.md`, `planung_gesamt.md`).
- Die Korrekturlogik überschreibt keine Ursprungsbuchung fachwidrig (`phase3_planung_konkret.md`, `Regelwerk v4`).
- Application-Tests belegen Commit-/Rollback-Verhalten, Fehlerfälle und Fachlogik nachvollziehbar (`phase3_planung_konkret.md`, `planung_gesamt.md`).

## Arbeitsweise

Arbeite akribisch, konservativ und selbstkritisch.

- Erfinde keine Infrastrukturdetails, die laut Planung erst in Phase 4 kommen.
- Ziehe keine UI-, CLI- oder Hardwarelogik vor.
- Behaupte nicht, dass die operative Ruhezeitintegration bereits vollständig abgeschlossen ist.
- Ersetze keine organisatorischen Nachweise durch Codebehauptungen.

Diese Vorsichtsregeln ergeben sich aus `phase3_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

## Explizite Nicht-Ziele

Folgende Dinge dürfen **nicht** umgesetzt werden:

- echte SQLite-Repositories und echte DB-`UnitOfWork`,
- vollständig implementierte `ApproveSupplementUseCase`- und `RejectSupplementUseCase`-Abläufe,
- vollständige operative Ruhezeitintegration im realen Datenzugriff,
- Backup, Restore, Export, PDF, Pflichtauswertungen und Systemcheck,
- Hardware-Integration und `device_events`-Persistenzpfad,
- Terminal-UI, Admin-CLI und betriebliche Orchestrierung,
- organisatorische Dokumentation, Testmatrix, Datenschutz- und IT-Sicherheitsnachweise.

Quellen: `phase3_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4`, `Anlage v2`.

## Ergebnisformat

Liefere am Ende ausschließlich den Phase-3-Code für Application-Schicht und Application-Tests. Führe **keine** Phase-4- oder Phase-5-Arbeiten aus und dokumentiere sauber, wo die Phase-3-Grenze bewusst eingehalten wurde. Grundlage: `phase3_planung_konkret.md`, `planung_gesamt.md`.
