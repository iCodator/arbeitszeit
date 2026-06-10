# Konkrete Planung Phase 3 – arbeitszeit

## Zweck

Dieses Dokument leitet aus der aktuellen Gesamtplanung die **konkrete Phase 3** für das Projekt `arbeitszeit` ab. Phase 3 umfasst die **Application-Schicht**: Commands, Results, Unit of Work als Abstraktion, Use Cases und testbare In-Memory-Fakes für die Application-Tests. [planung_gesamt.md]

Phase 3 verbindet die in Phase 2 definierte Domänenlogik mit fachlichen Abläufen, ohne bereits echte SQLite-Repositories, Exportlogik, Hardware, Backup oder Benutzeroberflächen einzuführen. Ziel ist eine saubere Orchestrierung fachlicher Prozesse, klar getrennt von Infrastruktur und Präsentation. [planung_gesamt.md]

Die Phase-3-Planung steht im Kontext der aktuellen Referenzdokumente `docs/pflichtenheft_arbeitszeit_v4.md`, `docs/regelwerk_arbeitszeit_v4.md` und `docs/anlage_einhaltung_pflichtenheft_v2.md`. Dieses Dokument beschreibt den heute gültigen fachlichen Zuschnitt von Phase 3 und grenzt ihn ausdrücklich gegen Phase 1, Phase 2 und spätere Phasen ab. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Zielbild Phase 3

Phase 3 liefert eine vollständige, testbare Application-Schicht. Sie übersetzt Benutzer- oder Systemabsichten in fachlich korrekte Abläufe: Buchen, Nachtrag anlegen, Korrektur anlegen und Regelarbeitszeit ändern. [planung_gesamt.md]

Wesentlich ist dabei: Die Use Cases arbeiten **nur** gegen Abstraktionen. Persistenz, Audit-Storage, Hardware, CLI und echte DB-Transaktionen werden noch nicht mit realer Infrastruktur umgesetzt. Stattdessen werden Fakes verwendet, um die Fachlogik isoliert und reproduzierbar zu testen. [planung_gesamt.md]

## Verbindlicher Lieferumfang

Laut aktueller Gesamtplanung umfasst Phase 3 die folgenden Bestandteile: [planung_gesamt.md]

- `application/unit_of_work.py` mit `UnitOfWork`-Protocol. [planung_gesamt.md]
- `application/commands.py` mit allen Phase-3-Commands. [planung_gesamt.md]
- `application/results.py` mit den Ergebnisobjekten der Use Cases. [planung_gesamt.md]
- `application/use_cases/` mit `manage_work_schedule.py`, `register_supplement.py`, `correct_booking.py`, `book_time.py`. [planung_gesamt.md]
- `tests/application/fakes.py` mit In-Memory-Implementierungen der Repository-Ports und `FakeUnitOfWork`. [planung_gesamt.md]
- `tests/application/` mit Use-Case-Tests. [planung_gesamt.md]

Die Gesamtplanung dokumentiert zusätzlich, dass bestimmte ursprünglich später gedachte Autorisierungsregeln bereits in Phase 3 vollständig aufgenommen wurden. Diese gehören deshalb in die konkrete Phase-3-Planung hinein. [planung_gesamt.md]

## Nicht Teil von Phase 3

Die folgenden Themen gehören **nicht** zu Phase 3: [planung_gesamt.md]

- echte SQLite-Repositories und echte DB-Unit-of-Work aus Phase 4, [planung_gesamt.md]
- Migrationen und DB-Grundgerüst aus Phase 1, [planung_gesamt.md]
- Domänenmodellierung aus Phase 2, [planung_gesamt.md]
- Backup, Restore, Export, PDF, Report-Queries und Systemcheck aus Phase 4, [planung_gesamt.md]
- Terminal-UI, Admin-CLI und betriebliche Orchestrierung aus Phase 5. [planung_gesamt.md]

Phase 3 darf außerdem nicht versehentlich bereits Infrastrukturwissen in die Use Cases ziehen. Sobald SQL, evdev, CLI-Ausgabe oder Dateisystemlogik auftaucht, ist die Phasengrenze verletzt. [planung_gesamt.md]

## Fachliche Leitplanken

Die Application-Schicht muss die verbindlichen Regeln aus Pflichtenheft und Regelwerk über klar abgegrenzte Use Cases umsetzen. Dazu gehören insbesondere Buchungsarten, Plausibilitätsprüfung, offene Buchungen ohne Auto-Close, Prüfstatus, Korrekturen, Nachträge, Regelarbeitszeiten und Rollentrennung. [Pflichtenheft v4] [Regelwerk v4]

Wichtig ist die in der Gesamtplanung dokumentierte Statussemantik: Der `BookingStatus` beschreibt die **einzelne Buchung**, nicht den gesamten Tag. `WARN` und `NEEDS_REVIEW` ergeben sich aus fachlicher Bewertung des projizierten Verlaufs; `CORRECTED` und `CLOSED_WITH_NOTE` werden nur in den dafür vorgesehenen Prozessen gesetzt. [planung_gesamt.md] [Regelwerk v4]

## Konkrete Arbeitspakete

### 1. `UnitOfWork`-Abstraktion definieren

In `application/unit_of_work.py` wird das `UnitOfWork`-Protocol implementiert. Es muss Context-Manager-Support bieten und Zugriff auf alle für die Phase-3-Use-Cases benötigten Repositories geben. [planung_gesamt.md]

Die Gesamtplanung nennt hierfür die Repositories aus Phase 2, darunter `employee_repo`, `user_account_repo`, `rfid_card_repo`, `time_booking_repo`, `work_schedule_repo`, `review_case_repo`, `supplement_repo`, `booking_correction_repo`, `audit_log_repo` und `system_config_repo`. Außerdem gehören `commit()`, `rollback()`, `__enter__()` und `__exit__()` dazu. [planung_gesamt.md]

### 2. Commands modellieren

In `application/commands.py` werden alle Commands als frozen Dataclasses mit `slots=True` modelliert. [planung_gesamt.md]

Laut Gesamtplanung gehören dazu: [planung_gesamt.md]

- `BookCommand`,
- `CreateSupplementCommand`,
- `CreateCorrectionCommand`,
- `ChangeWorkScheduleCommand`,
- `ApproveSupplementCommand`,
- `RejectSupplementCommand`. [planung_gesamt.md]

Selbstkritische Präzisierung: Auch wenn `ApproveSupplementCommand` und `RejectSupplementCommand` im Fließtext bei Phase 3 als „neu ergänzen“ beschrieben werden, werden ihre eigentlichen Use Cases erst in Phase 4 umgesetzt. Für die konkrete Phase-3-Planung heißt das: Die Command-Definitionen dürfen bereits angelegt werden, die fachliche Orchestrierung der Freigabe/Ablehnung gehört aber noch nicht zum verpflichtenden Kern von Phase 3. [planung_gesamt.md]

### 3. Results modellieren

In `application/results.py` werden die Ergebnisobjekte der Use Cases als frozen Dataclasses mit `slots=True` modelliert. [planung_gesamt.md]

Verbindlich sind laut Gesamtplanung: [planung_gesamt.md]

- `BookResult`,
- `SupplementResult`,
- `CorrectionResult`,
- `WorkScheduleChangeResult`. [planung_gesamt.md]

Diese Ergebnisobjekte müssen den fachlichen Output der Use Cases stabil und ohne Infrastrukturdetails transportieren. [planung_gesamt.md]

### 4. Fakes für Application-Tests implementieren

In `tests/application/fakes.py` werden In-Memory-Implementierungen aller benötigten Repository-Ports erstellt. Jede Fake-Implementierung arbeitet laut Gesamtplanung mit `dict[int, Entity]` plus Auto-Inkrement-ID. [planung_gesamt.md]

Besonders wichtig sind: [planung_gesamt.md]

- `FakeUnitOfWork` mit `committed` und `rolled_back` als Testflags, [planung_gesamt.md]
- Rollback bei Exception in `__exit__()`, [planung_gesamt.md]
- `FakeTimeBookingRepository.set_status()` über `dataclasses.replace()`, [planung_gesamt.md]
- `FakeWorkScheduleRepository.get_effective()` mit Vorrang von EMPLOYEE- vor GLOBAL-Scope, [planung_gesamt.md]
- `FakeWorkScheduleRepository.close_version()` so, dass Invarianten tatsächlich geprüft bleiben. [planung_gesamt.md]

Die Fakes dürfen keine Infrastruktur-Seiteneffekte simulieren, die laut Gesamtplanung bewusst erst in späteren Phasen zur Infrastruktur gehören, etwa echtes `booking_status_history`-Persistieren in einer Datenbank. [planung_gesamt.md]

### 5. `ManageWorkScheduleUseCase` implementieren

In `application/use_cases/manage_work_schedule.py` wird der Use Case zum Ändern von Regelarbeitszeiten implementiert. [planung_gesamt.md]

Die Gesamtplanung gibt die fachlichen Schritte explizit vor: [planung_gesamt.md]

1. Bestehende wirksame Version laden. [planung_gesamt.md]
2. `ConflictError`, wenn `current.valid_from == cmd.valid_from`. [planung_gesamt.md]
3. `ValidationError`, wenn für denselben Scope und Wochentag bereits eine spätere Version existiert. [planung_gesamt.md]
4. Vorherige Version schließen. [planung_gesamt.md]
5. Neue Version anlegen. [planung_gesamt.md]
6. `AuditLogEntry` anlegen. [planung_gesamt.md]
7. Commit ausführen und Ergebnis zurückgeben. [planung_gesamt.md]

Zusätzlich ist laut Gesamtplanung bereits in Phase 3 eine Rollenprüfung vorgesehen: Nur `ADMIN` darf diesen Use Case ausführen, und `changed_by_user_id` darf nicht `None` sein. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

### 6. `RegisterSupplementUseCase` implementieren

In `application/use_cases/register_supplement.py` wird der Use Case zum Anlegen eines Nachtrags implementiert. [planung_gesamt.md]

Verbindliche Schritte laut Gesamtplanung: [planung_gesamt.md]

1. Mitarbeiter laden, bei unbekanntem Mitarbeiter `NotFoundError`. [planung_gesamt.md]
2. `Supplement` mit `ApprovalStatus.PENDING` anlegen. [planung_gesamt.md]
3. `ReviewCase(MANUAL_ENTRY_REVIEW)` anlegen, standardmäßig und nicht optional. [planung_gesamt.md]
4. Commit ausführen und `SupplementResult` zurückgeben. [planung_gesamt.md]
5. `AuditLogEntry` anlegen. [planung_gesamt.md]

Auch hier gilt bereits die Rollenprüfung: `recorded_by_user_id` muss einem aktiven Benutzer mit Rolle `ADMIN` oder `REVIEWER` entsprechen. [planung_gesamt.md] [Regelwerk v4]

### 7. `CorrectBookingUseCase` implementieren

In `application/use_cases/correct_booking.py` wird der Use Case für Korrekturen implementiert. [planung_gesamt.md]

Verbindliche Schritte laut Gesamtplanung: [planung_gesamt.md]

1. Ursprungsbuchung laden, sonst `NotFoundError`. [planung_gesamt.md]
2. `BookingCorrection` mit altem und neuem Zustand anlegen. [planung_gesamt.md]
3. Ursprungsbuchung auf `CORRECTED` setzen. [planung_gesamt.md]
4. Nur passende offene Review Cases zur Buchung schließen. [planung_gesamt.md]
5. `AuditLogEntry` anlegen. [planung_gesamt.md]
6. Commit ausführen und `CorrectionResult` zurückgeben. [planung_gesamt.md]

Auch hier gilt die Rollenprüfung: `corrected_by_user_id` muss zu `ADMIN` oder `REVIEWER` gehören. [planung_gesamt.md] [Regelwerk v4]

Wichtig ist die Modellgrenze: Die ursprüngliche `TimeBooking` wird **nicht** überschrieben, sondern nur auf `CORRECTED` gesetzt; der neue Zustand lebt in `BookingCorrection`. Diese fachliche Entscheidung muss der Use Case respektieren. [planung_gesamt.md] [Regelwerk v4]

### 8. `BookUseCase` implementieren

In `application/use_cases/book_time.py` wird der zentrale Buchungs-Use-Case implementiert. [planung_gesamt.md]

Die Gesamtplanung beschreibt den Ablauf detailliert: [planung_gesamt.md]

1. RFID-Karte laden; unbekannte oder inaktive Karte führt zu `UnknownCardError` bzw. `InactiveCardError`, jeweils mit Audit-Pflicht. [planung_gesamt.md]
2. Mitarbeiter laden; inaktiver Mitarbeiter führt zu `InactiveEmployeeError`. [planung_gesamt.md]
3. Tagesbuchungen laden. [planung_gesamt.md]
4. Buchungsfolge validieren; Fehler führen zu `InvalidBookingSequenceError` oder `OpenPhaseConflictError`. [planung_gesamt.md]
5. Status bestimmen: [planung_gesamt.md]
   - `COME` / `BREAK_START` → `OPEN`, [planung_gesamt.md]
   - `GO` / `BREAK_END` → Bewertung des projizierten Verlaufs mit `check_break_compliance()` und `check_max_hours()`. [planung_gesamt.md]
6. Buchung anlegen. [planung_gesamt.md]
7. Pro `ComplianceFlag` einen `ReviewCase` anlegen. [planung_gesamt.md]
8. Commit ausführen und `BookResult` zurückgeben. [planung_gesamt.md]
9. `AuditLogEntry` anlegen. [planung_gesamt.md]

Selbstkritische Präzisierung: Die Gesamtplanung hält fest, dass die vollständige Integration der Ruhezeitprüfung (`check_rest_period`) in den Buchungsablauf erst in Phase 4 nachgezogen wurde, weil dafür Vortageskontext benötigt wird. Für Phase 3 darf diese Prüfung deshalb **noch nicht** als vollständig integrierter Buchungsbestandteil behauptet werden. [planung_gesamt.md]

Außerdem wird der Regelzeitfenster-Check in der Gesamtplanung im Phase-3-Bereich bereits als gewünschte Bewertungslogik beschrieben. Gleichzeitig ist klar, dass die vollständige Infrastruktur und spätere Reports erst später kommen. Für Phase 3 ist deshalb konservativ zu planen: Der Use Case soll so strukturiert sein, dass diese Bewertung fachlich anschlussfähig ist, ohne Phase 4-Funktionen vorwegzunehmen. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

### 9. Application-Tests implementieren

Unter `tests/application/` werden Use-Case-Tests gegen die Fakes implementiert. [planung_gesamt.md]

Die Gesamtplanung nennt als Zielstruktur: [planung_gesamt.md]

- `test_manage_work_schedule.py`,
- `test_register_supplement.py`,
- `test_correct_booking.py`,
- `test_book_time.py`. [planung_gesamt.md]

Die Tests müssen nicht nur Erfolgsfälle, sondern insbesondere Fehlerpfade, Rollenprüfungen, Statusübergänge, Review-Case-Erzeugung und Commit-/Rollback-Verhalten abdecken. [planung_gesamt.md]

## Qualitätskriterien für den Phase-3-Abschluss

Phase 3 gilt erst dann als sauber abgeschlossen, wenn alle folgenden Punkte erfüllt sind: [planung_gesamt.md]

- `UnitOfWork`, Commands und Results sind vollständig und konsistent modelliert. [planung_gesamt.md]
- Fakes erlauben realistische, aber reine In-Memory-Tests der Use Cases. [planung_gesamt.md]
- `ManageWorkScheduleUseCase`, `RegisterSupplementUseCase`, `CorrectBookingUseCase` und `BookUseCase` setzen die dokumentierten fachlichen Abläufe korrekt um. [planung_gesamt.md]
- Rollenprüfungen in den schreibenden Phase-3-Use-Cases sind integriert. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- `BookUseCase` behandelt Status und Review Cases fachlich korrekt auf Basis der in Phase 3 verfügbaren Prüfhilfen. [planung_gesamt.md]
- Die Korrekturlogik überschreibt keine Ursprungsbuchung fachwidrig. [planung_gesamt.md] [Regelwerk v4]
- Application-Tests belegen Commit-/Rollback-Verhalten, Fehlerfälle und Fachlogik nachvollziehbar. [planung_gesamt.md]

## Bekannte Risiken und Selbstkritik

Ein zentrales Risiko ist die Vermischung von Use-Case-Orchestrierung mit Infrastruktur. Phase 3 darf zwar Audit-Einträge fachlich erzeugen, aber keine echte SQLite-Transaktionssemantik, keine Exportdateien und keine Hardwarepfade implementieren. [planung_gesamt.md]

Ein weiteres Risiko ist die Überdehnung des `BookUseCase`. Die Gesamtplanung selbst dokumentiert, dass die vollständige Ruhezeitintegration und weitere Infrastrukturdetails erst in Phase 4 geschlossen wurden. Phase 3 muss deshalb sauber zwischen „fachlich vorbereitet“ und „vollständig operativ umgesetzt“ unterscheiden. [planung_gesamt.md]

Ein drittes Risiko ist die ungenaue Rollenprüfung. Die Gesamtplanung fordert bereits in Phase 3 für schreibende Use Cases die Prüfung auf Existenz, Aktivität und erlaubte Rolle. Diese Vereinheitlichung darf nicht auf Phase 4 verschoben werden. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

## Offene Punkte, die bewusst nicht in Phase 3 gezogen werden

Die folgenden Punkte sind wichtig, aber **nicht** Bestandteil der konkreten Phase-3-Umsetzung: [planung_gesamt.md]

- echte SQLite-Repositories und echte DB-Unit-of-Work, [planung_gesamt.md]
- `ApproveSupplementUseCase` und `RejectSupplementUseCase` als vollständig implementierte Freigabe-/Ablehnungsprozesse, [planung_gesamt.md]
- vollständige operative Ruhezeitintegration im realen Datenzugriff, [planung_gesamt.md]
- Backup, Restore, Export, PDF, Pflichtauswertungen und Systemcheck, [planung_gesamt.md]
- Hardware-Integration und `device_events`-Persistenzpfad, [planung_gesamt.md] [Anlage v2]
- Terminal-UI, Admin-CLI und betriebliche Orchestrierung, [planung_gesamt.md]
- organisatorische Dokumentation, Testmatrix, Datenschutz- und IT-Sicherheitsnachweise. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Ergebnis

Die konkrete Phase 3 ist damit klar begrenzt: **Application-Schicht mit Commands, Results, UnitOfWork-Abstraktion, In-Memory-Fakes, vier zentralen Use Cases und belastbaren Application-Tests**. Genau dieses Paket bildet laut aktueller Gesamtplanung die fachlich vollständige Orchestrierung oberhalb der Domäne und unterhalb der Infrastruktur. [planung_gesamt.md]
