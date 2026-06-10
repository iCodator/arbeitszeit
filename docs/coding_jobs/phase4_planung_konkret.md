# Konkrete Planung Phase 4 – arbeitszeit

## Zweck

Dieses Dokument leitet aus der aktuellen Gesamtplanung die **konkrete Phase 4** für das Projekt `arbeitszeit` ab. Phase 4 umfasst die **Infrastruktur-Schicht**: echte SQLite-Repositories, echte `UnitOfWork`-Integration, ergänzende Migrationen, Export, Backup/Restore, Hardware-Anbindung, Systemcheck und zugehörige Integrations- und E2E-Tests. [planung_gesamt.md]

Phase 4 setzt auf den abgeschlossenen Phasen 1 bis 3 auf. Ziel ist, die zuvor abstrakt geplanten oder per Fakes getesteten Fachabläufe auf reale Persistenz, reale Systemintegration und betriebsnahe Schnittstellen zu übertragen, ohne bereits die finale Präsentationsschicht aus Phase 5 vorauszusetzen. [planung_gesamt.md]

Die Phase-4-Planung steht im Kontext der aktuellen Referenzdokumente `docs/pflichtenheft_arbeitszeit_v4.md`, `docs/regelwerk_arbeitszeit_v4.md` und `docs/anlage_einhaltung_pflichtenheft_v2.md`. Dieses Dokument beschreibt den heute gültigen fachlichen Zuschnitt von Phase 4 und grenzt ihn ausdrücklich gegen frühere Phasen und gegen die Präsentationsschicht aus Phase 5 ab. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Zielbild Phase 4

Phase 4 überführt die bisherige Architektur in eine **real integrierte technische Infrastruktur**. Die Phase schließt insbesondere die echte SQLite-Anbindung, Backup/Restore, Exporte, Pflichtauswertungen, Selbsttest und die Grundlage für Hardwareintegration. [planung_gesamt.md]

Gleichzeitig zeigt die Gesamtplanung, dass Phase 4 nicht nur „Anschluss von Infrastruktur“ ist, sondern auch Korrektur- und Nachschärfungsphase: Bestimmte frühe Modell- oder Migrationsentscheidungen werden hier bewusst migrationsbasiert bereinigt, und bisher nur vorbereitete Fachfunktionen werden operativ geschlossen. [planung_gesamt.md]

## Verbindlicher Lieferumfang

Laut aktueller Gesamtplanung umfasst Phase 4 mindestens die folgenden Themenblöcke: [planung_gesamt.md]

- Ergänzende Application-Use-Cases `approve_supplement.py` und `reject_supplement.py`. [planung_gesamt.md]
- Integration der Ruhezeitprüfung in `BookUseCase`. [planung_gesamt.md]
- Nachrüstung der Rollenprüfung in alle noch offenen schreibenden Use Cases. [planung_gesamt.md]
- Migration `0005_time_bookings_device_event_id.sql` sowie im Gesamtstand auch die Phase-4-Migrationen `0003_cleanup_booking_status.sql` und `0004_supplement_reject_fields_and_review_note.sql`. [planung_gesamt.md]
- `infrastructure/db/unit_of_work.py`. [planung_gesamt.md]
- `infrastructure/db/repositories/` mit 10 SQLite-Repositories. [planung_gesamt.md]
- Integrationsbasis unter `tests/integration/`. [planung_gesamt.md]
- `infrastructure/hardware/`. [planung_gesamt.md]
- `infrastructure/backup/`. [planung_gesamt.md]
- `infrastructure/export/` mit `report_queries.py`, `csv_exporter.py`, `pdf_report_service.py`. [planung_gesamt.md]
- `infrastructure/system_check.py`. [planung_gesamt.md]

Die Gesamtplanung dokumentiert außerdem mehrere nachgezogene Korrekturen innerhalb von Phase 4, etwa zum finalen Schema-Stand, zur Ableitungsschicht und zur Pflichtfallabdeckung. Diese gehören zur konkreten Phase-4-Planung dazu. [planung_gesamt.md]

## Nicht Teil von Phase 4

Die folgenden Themen gehören **nicht** zur konkreten Phase-4-Umsetzung: [planung_gesamt.md]

- das initiale Projekt- und Migrationsfundament aus Phase 1, [planung_gesamt.md]
- die reine Domänenschicht aus Phase 2, [planung_gesamt.md]
- die isolierte Use-Case-Orchestrierung mit Fakes aus Phase 3, [planung_gesamt.md]
- Terminal-UI, Admin-CLI und betriebliche Orchestrierung aus Phase 5. [planung_gesamt.md]

Selbstkritische Abgrenzung: Phase 4 baut zwar bereits Hardware-, Backup- und Exportbausteine, aber noch nicht die vollständige Endanwenderführung. Alles, was primär Präsentation, Kommandozeilenbedienung oder Betriebsloop ist, bleibt Phase 5 vorbehalten. [planung_gesamt.md]

## Fachliche Leitplanken

Phase 4 muss die Anforderungen aus Pflichtenheft und Regelwerk nicht nur abstrakt vorbereiten, sondern in reale technische Mechanismen übersetzen. Dazu gehören insbesondere: [Pflichtenheft v4] [Regelwerk v4]

- Rollen- und Rechteprinzip, [Pflichtenheft v4] [Regelwerk v4]
- Pflichtauswertungen und konsistente Berichte, [Pflichtenheft v4] [Regelwerk v4]
- Protokollierung von Backup, Restore, Selbsttest und Systemereignissen, [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- Aufbewahrungs- und Archivierungsprinzip ohne stilles Löschen fachlich relevanter Buchungen, [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- Zeitprotokollierungsfähigkeit über `system_events` als Grundlage der späteren Systemzeitüberwachung. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

## Konkrete Arbeitspakete

### 1. Ergänzende Supplement-Use-Cases implementieren

In Phase 4 werden `ApproveSupplementUseCase` und `RejectSupplementUseCase` als echte fachliche Abläufe ergänzt. [planung_gesamt.md]

Für `ApproveSupplementUseCase` ist laut Gesamtplanung zwingend umzusetzen: [planung_gesamt.md]
- Rollenprüfung auf `REVIEWER` oder `ADMIN`, [planung_gesamt.md]
- Laden und Validieren des Supplements, [planung_gesamt.md]
- Prüfen auf `PENDING`, [planung_gesamt.md]
- Validierung des betroffenen Mitarbeiters, [planung_gesamt.md]
- fachliche Freigabe des Supplements, [planung_gesamt.md]
- Schließen des offenen `MANUAL_ENTRY_REVIEW`-Falls, [planung_gesamt.md]
- Erzeugen einer echten `TimeBooking` mit vollständiger Statuslogik, [planung_gesamt.md]
- Erzeugen neuer `ReviewCase`-Einträge pro `ComplianceFlag`, [planung_gesamt.md]
- Commit und Audit-Eintrag. [planung_gesamt.md]

Wichtig ist die explizite Vorgabe der Gesamtplanung: Eine reine `supplement_repo.approve()`-Operation ohne tatsächliche Buchungserzeugung wäre fachlich unvollständig und ist nicht zulässig. [planung_gesamt.md]

Für `RejectSupplementUseCase` sind umzusetzen: [planung_gesamt.md]
- Rollenprüfung auf aktiven `REVIEWER` oder `ADMIN`, [planung_gesamt.md]
- Laden und Validieren des Supplements, [planung_gesamt.md]
- Prüfen auf `PENDING`, [planung_gesamt.md]
- fachliche Ablehnung via Repository, [planung_gesamt.md]
- Schließen eines passenden `MANUAL_ENTRY_REVIEW`-Falls, falls `related_booking_id` existiert, [planung_gesamt.md]
- Commit und Audit-Eintrag. [planung_gesamt.md]

### 2. Ruhezeitprüfung operativ in `BookUseCase` integrieren

Die Gesamtplanung hält ausdrücklich fest, dass `check_rest_period()` fachlich schon in Phase 2 existierte, operativ im Buchungsablauf aber erst in Phase 4 vollständig integriert wird. [planung_gesamt.md]

Konkret bedeutet das: [planung_gesamt.md]
- Vortagesbuchungen laden, [planung_gesamt.md]
- letzten `GO`-Zeitpunkt des Vortags bestimmen, [planung_gesamt.md]
- ersten `COME`-Zeitpunkt des projizierten Verlaufs bestimmen, [planung_gesamt.md]
- `check_rest_period(last_go, first_come)` aufrufen, [planung_gesamt.md]
- resultierende Prüffälle als `ReviewCase` und Statusbewertung in den Ablauf einbeziehen. [planung_gesamt.md]

Dieser Schritt schließt eine explizit als Pflichtanforderung benannte Lücke zu Pflichtenheft §7.9 und Regelwerk §10. [Pflichtenheft v4] [Regelwerk v4]

### 3. Rollenprüfung in alle schreibenden Use Cases vervollständigen

Laut Gesamtplanung wird die Autorisierung in Phase 4 systematisch auf alle noch offenen schreibenden Use Cases nachgezogen. [planung_gesamt.md]

Das betrifft insbesondere: [planung_gesamt.md]
- `RegisterSupplementUseCase`, [planung_gesamt.md]
- `CorrectBookingUseCase`, [planung_gesamt.md]
- `ManageWorkScheduleUseCase`, [planung_gesamt.md]
- sowie die neuen `ApproveSupplementUseCase` und `RejectSupplementUseCase`. [planung_gesamt.md]

Die Prüfung muss jeweils Existenz, Aktivität und erlaubte Rolle einheitlich über `PermissionDeniedError` behandeln. [planung_gesamt.md]

### 4. Migrationsstand auf finalen Phase-4-Schema-Stand bringen

Die konkrete Phase-4-Planung muss sauber zwischen originärem Plantext und tatsächlichem finalen Stand unterscheiden. Im heutigen Gesamtstand gehören zu den maßgeblichen Phase-4-Migrationen: [planung_gesamt.md]

- `0003_cleanup_booking_status.sql`, [planung_gesamt.md]
- `0004_supplement_reject_fields_and_review_note.sql`, [planung_gesamt.md]
- `0005_time_bookings_device_event_id.sql`. [planung_gesamt.md]

Inhaltlich bewirken diese Migrationen laut Gesamtplanung: [planung_gesamt.md]
- Bereinigung früherer BookingStatus-CHECK-Constraints, [planung_gesamt.md]
- Ergänzung von `rejected_by_user_id` und `rejected_at` in `supplements`, [planung_gesamt.md]
- Ergänzung eines `note`-Felds in `review_cases`, [planung_gesamt.md]
- Ergänzung von `device_event_id` in `time_bookings`. [planung_gesamt.md]

Selbstkritische Präzisierung: Die Spalte `device_event_id` ist damit schemafähig vorbereitet, aber die vollständige betriebliche Verkettung über echte `device_events` bleibt laut Gesamtplanung auch danach noch nicht operativ geschlossen. [planung_gesamt.md] [Anlage v2]

### 5. Echte `SQLiteUnitOfWork` implementieren

In `infrastructure/db/unit_of_work.py` wird die reale DB-gebundene `UnitOfWork` implementiert. [planung_gesamt.md]

Die Gesamtplanung verlangt: [planung_gesamt.md]
- `BEGIN` beim Eintritt, [planung_gesamt.md]
- `COMMIT` bei explizitem Commit, [planung_gesamt.md]
- `ROLLBACK` bei offener Transaktion im Exit, [planung_gesamt.md]
- commit-or-rollback-Sicherheitssemantik statt stiller Persistenz. [planung_gesamt.md]

Außerdem ist das `audit_conn`-Muster zu berücksichtigen: Die Haupttransaktion läuft auf `conn`, während Audit-Logging auf einer separaten Verbindung im Autocommit-Modus erfolgen kann, damit Audit-Einträge Rollbacks der Haupttransaktion überleben. [planung_gesamt.md]

### 6. SQLite-Repositories implementieren

Unter `infrastructure/db/repositories/` werden die 10 echten Repository-Implementierungen gegen SQLite gebaut. [planung_gesamt.md]

Die Gesamtplanung nennt hierfür zahlreiche fachlich relevante Anforderungen, unter anderem: [planung_gesamt.md]
- ISO-8601-TEXT für Datetimes, [planung_gesamt.md]
- Enums als `.value`, [planung_gesamt.md]
- Booleans als INTEGER 0/1, [planung_gesamt.md]
- ausschließlich parametrisierte Statements, [planung_gesamt.md]
- `RETURNING id` nach INSERT, [planung_gesamt.md]
- korrekte Scope-Priorität bei `WorkScheduleRepository.get_effective()`, [planung_gesamt.md]
- strenges Verhalten bei `TimeBookingRepository.set_status()`, [planung_gesamt.md]
- halb-offene Intervalle in Zeitbereichsqueries. [planung_gesamt.md]

Die Repositories müssen die Fachverträge aus Phase 2/3 real auf die Datenbank abbilden, ohne Geschäftsregeln aus der Domäne in SQL zu verlagern, wo die Gesamtplanung diese bewusst in Domäne oder Use Cases belässt. [planung_gesamt.md]

### 7. Integrationsbasis und Repository-Tests aufbauen

Unter `tests/integration/` wird die Integrationsbasis mit dateibasierter Test-SQLite aufgebaut. Die Gesamtplanung präzisiert, dass hier **keine** reine In-Memory-SQLite, sondern eine ephemere dateibasierte Datenbank genutzt wird, weil für `audit_conn` mehrere Verbindungen auf dieselbe Datei nötig sind. [planung_gesamt.md]

Verpflichtend sind Integrations- und Roundtrip-Tests für: [planung_gesamt.md]
- Repositories, [planung_gesamt.md]
- Repository-Roundtrips, [planung_gesamt.md]
- `SQLiteUnitOfWork`. [planung_gesamt.md]

### 8. Hardware-Bausteine vorbereiten

Unter `infrastructure/hardware/` wird die evdev-Integration aufgebaut, zunächst gegen Simulatoren und Adaptertests. [planung_gesamt.md]

Die Gesamtplanung grenzt klar ab: [planung_gesamt.md]
- Phase 4 liefert die Leseschicht, [planung_gesamt.md]
- aber noch **nicht** die vollständige betriebliche Orchestrierung, [planung_gesamt.md]
- und noch **nicht** den realen produktiven `device_events`-Persistenzpfad. [planung_gesamt.md] [Anlage v2]

### 9. Backup/Restore implementieren

Unter `infrastructure/backup/` wird die SQLite-Backup- und NAS-Sync-Logik umgesetzt. [planung_gesamt.md]

Pflichtpunkte laut Gesamtplanung: [planung_gesamt.md]
- manuell auslösbares Backup-Skript, [planung_gesamt.md]
- Audit-Logging für Backup/Sync/Restore-Ereignisse, [planung_gesamt.md]
- `PRAGMA integrity_check` nach Restore, [planung_gesamt.md]
- E2E-Restore-Tests, [planung_gesamt.md]
- optionales Mitsichern von Exportdateien über `export_dir`. [planung_gesamt.md]

Wichtig ist die Selbstkritik der Gesamtplanung: Ein Rotationskonzept und die volle datenschutzrechtliche/betriebliche Dokumentation sind damit **nicht automatisch** gelöst. Diese bleiben laut Anlage v2 und Pflichtenheft v4 teilweise betriebliche Nachweispunkte. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

### 10. Export- und Pflichtauswertungsschicht implementieren

Unter `infrastructure/export/` werden `report_queries.py`, `csv_exporter.py` und `pdf_report_service.py` umgesetzt. [planung_gesamt.md]

Zentrales Architekturprinzip ist laut Gesamtplanung und Regelwerk: **alle** Ausgabekanäle müssen auf derselben normierten Ableitungsschicht beruhen. [planung_gesamt.md] [Regelwerk v4]

Dazu gehören in Phase 4: [planung_gesamt.md]
- normierte Queries für Buchungen, Korrekturen, Nachträge und Review Cases, [planung_gesamt.md]
- CSV-Export detailliert und verdichtet, [planung_gesamt.md]
- PDF-Berichte für Tages-, Wochen-, Monats- und Mitarbeiterberichte, [planung_gesamt.md]
- Pflichtauswertungen für offene Buchungen, Korrekturen, Nachträge, Warn- und Review-Fälle. [planung_gesamt.md] [Pflichtenheft v4]

Selbstkritische Präzisierung: Gerade hier wäre es fachlich gefährlich, Abkürzungen über Ad-hoc-Queries zu gehen. Die Gesamtplanung verbietet dies faktisch, weil sonst die Konsistenz zwischen UI, CSV, PDF und Prüfübersichten verloren ginge. [planung_gesamt.md] [Regelwerk v4]

### 11. Selbsttest/Systemcheck implementieren

In `infrastructure/system_check.py` wird ein technischer Selbsttest umgesetzt. [planung_gesamt.md]

Die Gesamtplanung nennt als Prüfbereiche: [planung_gesamt.md]
- Konfigurationsprüfung, [planung_gesamt.md]
- Geräteverfügbarkeit, [planung_gesamt.md]
- NAS-Erreichbarkeit, [planung_gesamt.md]
- Datenbankzugriff, [planung_gesamt.md]
- Grundkonsistenz via `PRAGMA foreign_key_check`. [planung_gesamt.md]

Die Ergebnisse werden als `SELFTEST_OK` oder `SELFTEST_FAIL` in `system_events` protokolliert. [planung_gesamt.md]

## Qualitätskriterien für den Phase-4-Abschluss

Phase 4 gilt erst dann als sauber abgeschlossen, wenn alle folgenden Punkte erfüllt sind: [planung_gesamt.md]

- Ergänzende Supplement-Use-Cases sind fachlich korrekt implementiert. [planung_gesamt.md]
- Die Ruhezeitprüfung ist operativ in reale Buchungsabläufe integriert. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- Rollenprüfung ist in allen schreibenden Use Cases konsistent umgesetzt. [planung_gesamt.md]
- Das reale Schema entspricht dem finalen Phase-4-Migrationsstand. [planung_gesamt.md]
- `SQLiteUnitOfWork` und echte Repositories arbeiten korrekt zusammen. [planung_gesamt.md]
- Backup/Restore, Export, Pflichtauswertungen und Systemcheck sind technisch funktionsfähig und testgestützt. [planung_gesamt.md]
- Die zentrale Ableitungsschicht (`report_queries.py`) ist die einzige fachliche Wahrheitsquelle für Ausgaben. [planung_gesamt.md] [Regelwerk v4]
- Die Integrations- und E2E-Tests decken die kritischen Infrastrukturpfade nachvollziehbar ab. [planung_gesamt.md]

## Bekannte Risiken und Selbstkritik

Ein zentrales Risiko ist die Verwechslung von „schemafähig vorbereitet“ mit „betrieblich vollständig geschlossen“. Das gilt besonders für `device_event_id`: Die Migration schafft das Feld, aber die Gesamtplanung benennt den vollständigen produktiven Verkettungspfad weiterhin als offen. [planung_gesamt.md] [Anlage v2]

Ein weiteres Risiko liegt in der Konsistenz der Ableitungsschicht. Sobald CSV, PDF oder Pflichtauswertungen fachlich abweichende Query-Logik nutzen, wäre die Regelwerkskonformität verletzt. Phase 4 muss deshalb strikt an der gemeinsamen `report_queries.py` hängen. [planung_gesamt.md] [Regelwerk v4]

Ein drittes Risiko ist die Überschätzung des technischen Fertigstellungsgrads im Verhältnis zu organisatorischen Nachweisen. Auch wenn Backup, Exporte und lokale Verarbeitung technisch umgesetzt sind, bleiben laut Pflichtenheft v4 und Anlage v2 weiterhin offene Praxisunterlagen wie Rotationskonzept, AV-Vertrag, Rollenfestlegung, IT-Sicherheitskonzept und revisionsfeste Testmatrix. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Offene Punkte, die bewusst nicht in Phase 4 gezogen werden

Die folgenden Punkte sind wichtig, aber **nicht** Bestandteil der konkreten Phase-4-Umsetzung: [planung_gesamt.md]

- Terminal-UI und Admin-CLI, [planung_gesamt.md]
- vollständige betriebliche Orchestrierung der Hardware-Schicht, [planung_gesamt.md] [Anlage v2]
- vollständige produktive `device_events`-Kette, soweit sie laut Gesamtplanung offen bleibt, [planung_gesamt.md] [Anlage v2]
- spätere Systemzeitüberwachung über `time_monitor.py`, [planung_gesamt.md]
- organisatorische Nachweise wie Testmatrix, AV-Vertrag, IT-Sicherheitskonzept oder Praxisfreigaben. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Ergebnis

Die konkrete Phase 4 ist damit klar begrenzt: **echte DB-Integration, echte Repositories, ergänzte Use Cases, Phase-4-Migrationen, Backup/Restore, Export, Pflichtauswertungen, Systemcheck, Hardware-Leseschicht und belastbare Integrations-/E2E-Tests**. Genau dieses Paket bildet laut aktueller Gesamtplanung den real integrierten Infrastrukturkern unterhalb der Präsentationsschicht. [planung_gesamt.md]
