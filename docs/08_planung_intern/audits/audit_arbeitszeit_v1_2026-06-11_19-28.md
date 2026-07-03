# Audit-Bericht Repository `iCodator/arbeitszeit`

**Datum:** 2026-06-11  
**Uhrzeit:** 19:28

## Auditauftrag und Scope

Gegenstand dieses Audits ist der aktuelle Repository-Stand des Projekts `iCodator/arbeitszeit`. Bewertet werden die Phasen 1 bis 5 anhand der im Repository vorhandenen Planungsunterlagen, fachlichen Referenzdokumente, Implementierungsartefakte, Migrationen, Skripte und Testdateien.

Die Prüfung basiert ausschließlich auf Artefakten aus dem Repository. Externe Quellen, Annahmen über die reale Praxisumgebung oder nicht im Repository nachweisbare Sachverhalte wurden nicht verwendet. Wo die Artefaktbasis keine belastbare Feststellung erlaubt, wird ausdrücklich formuliert: **„nicht entscheidbar auf Basis der vorliegenden Artefakte“**.

Geprüfte Artefaktgruppen:
- Planungsunterlagen unter `docs/informelles/`
- Fachliche Grundlagen `pflichtenheft_arbeitszeit_v*.md`, `regelwerk_arbeitszeit_v*.md`
- Quellcode unter `src/arbeitszeit/`
- SQL-Migrationen unter `migrations/`
- Hilfs- und Betriebs-Skripte unter `scripts/`
- Testartefakte unter `tests/`

## Artefaktbasis

Zentral ausgewertete Dateien und Verzeichnisse:

### Planung und Projektstand
- `docs/informelles/planung_gesamt.md`
- `docs/informelles/phase1_planung.md`
- `docs/informelles/phase2_planung.md`
- `docs/informelles/phase3_planung.md`
- `docs/informelles/phase4_planung.md`
- `docs/informelles/phase5_planung.md`

### Implementierung und Struktur
- `src/arbeitszeit/__init__.py`
- `src/arbeitszeit/domain/`
- `src/arbeitszeit/application/`
- `src/arbeitszeit/infrastructure/`
- `src/arbeitszeit/presentation/`

### Migrationen
- `migrations/0001_schema.sql`
- `migrations/0002_seed_defaults.sql`
- `migrations/0003_cleanup_booking_status.sql`
- `migrations/0004_supplement_reject_fields_and_review_note.sql`
- `migrations/0005_time_bookings_device_event_id.sql`
- `migrations/0006_system_events_application_error.sql`

### Skripte
- `scripts/init_db.py`
- `scripts/backup.py`
- `scripts/setup.py`

### Tests
- `tests/test_migrations.py`
- `tests/domain/`
- `tests/application/`
- `tests/integration/`
- `tests/e2e/`

## Phase-weise Bewertung

## Phase 1

### Sollbild

Phase 1 ist laut `docs/informelles/phase1_planung.md` und `docs/informelles/planung_gesamt.md` das Grundgerüst des Systems: Projektlayout, Migrationssystem, SQLite-Verbindungsaufbau, Initialisierungsskript und erste Datenbankkonsistenzprüfung. Originär zu Phase 1 gehören nur `migrations/0001_schema.sql`, `migrations/0002_seed_defaults.sql`, `infrastructure/db/connection.py`, `infrastructure/db/migrations.py`, `scripts/init_db.py` und die ursprünglichen Phase-1-Teile von `tests/test_migrations.py`.

### Istbild

Die Migrationskette ist heute bis `0006` erweitert; das Verzeichnis `migrations/` enthält sechs SQL-Dateien. `tests/test_migrations.py` ist weiterhin vorhanden, wird aber laut Planung inzwischen für die komplette Migrationskette 0001–0006 genutzt. Zusätzlich existieren spätere, auf Phase 1 aufbauende Artefakte wie `scripts/setup.py` und Integrations-Tests `tests/integration/test_init_db.py`, die laut Plan ausdrücklich nicht originär zu Phase 1 gehören.

### Befunde

1. **Befund 1/1-01**  
   - Kategorie: Dokumentation / Planung  
   - Schweregrad: Hinweis / Observation  
   - Einordnung: reine Dokumentationsfrage  
   - Betroffene Dateien: `docs/informelles/phase1_planung.md`, `docs/informelles/planung_gesamt.md`, `tests/test_migrations.py`  
   - Feststellung: Die Phase-1-Planung trennt sauber zwischen originärem Lieferumfang und späteren Nachträgen. Der heutige Teststand bündelt jedoch historische und spätere Migrationstests in einem gemeinsamen Modul. Das ist sachlich dokumentiert, aber für einen externen Prüfer nur dann eindeutig, wenn die historische Trennung aktiv mitgelesen wird.

2. **Befund 1/1-02**  
   - Kategorie: Dokumentation / Planung  
   - Schweregrad: Minor-Mangel  
   - Einordnung: reine Dokumentationsfrage  
   - Betroffene Dateien: `docs/informelles/phase1_planung.md`  
   - Feststellung: In `phase1_planung.md` wird am Ende ausdrücklich vermerkt, dass Pflichtenheft und Regelwerk „im Projektwurzel, nicht in docs/“ liegen. Ob die dort referenzierten Dateien im aktuellen Repository exakt unter diesen Namen existieren, ist auf Basis der vorliegenden, in diesem Audit gelesenen Artefakte nicht vollständig nachgewiesen. Daher ist die Referenzlage hier teilweise **nicht entscheidbar auf Basis der vorliegenden Artefakte**.

3. **Befund 1/1-03**  
   - Kategorie: Datenbank / Migrationen  
   - Schweregrad: OFI  
   - Einordnung: originär zu Phase 1  
   - Betroffene Dateien: `docs/informelles/phase1_planung.md`, `migrations/`  
   - Feststellung: Die Phase ist historisch konsistent dokumentiert, weil spätere Migrationen 0003–0006 ausdrücklich als Nachträge gekennzeichnet werden. Für Revisionszwecke wäre eine zusätzliche tabellarische Migrationsmatrix mit Spalten „historische Phase“, „aktueller Status“, „ersetzt/ergänzt durch“ jedoch klarer.

### Freigabestatus

**GO mit Auflagen**

Begründung: Der historische Kern von Phase 1 ist laut Planung abgeschlossen und das Fundament wird im Gesamtplan als umgesetzt beschrieben. Die Dokumentation ist grundsätzlich belastbar, aber die Vermischung von historischem und heutigem Teststand sowie die nur teilweise nachgewiesene Referenzlage zu den v5-Dokumenten sollten vor einer formalen Außenprüfung in einer kompakten Matrix zusammengeführt werden.

## Phase 2

### Sollbild

Phase 2 verlangt laut `docs/informelles/phase2_planung.md` ein vollständiges, infrastrukturfreies Domänenmodell mit Enums, Fehlerklassen, Entitäten, Domänenservices und Repository-Protocols. Die Zielstruktur umfasst insbesondere `src/arbeitszeit/domain/enums.py`, `errors.py`, `entities.py`, `audit_events.py`, `ports/repositories.py` und `services/booking_rules.py` sowie `services/compliance_checks.py`.

### Istbild

Die Gesamtplanung beschreibt `src/arbeitszeit/domain/` als abgeschlossen und nennt 67 grüne Domänentests. Das Repository enthält laut Struktur das Verzeichnis `src/arbeitszeit/domain/` und das Testverzeichnis `tests/domain/`. Auf Basis der in den Planungsdokumenten beschriebenen Zielstruktur und Testaufteilung ist der Domänenkern vorhanden; eine Vollprüfung jedes einzelnen Modulinhalts war im Rahmen der hier gelesenen Artefakte jedoch nur insoweit möglich, wie die Planungsdokumente den Ist-Stand bereits explizit nachführen.

### Befunde

1. **Befund 2/2-01**  
   - Kategorie: Fachlogik / Compliance  
   - Schweregrad: Hinweis / Observation  
   - Einordnung: originär zu Phase 2  
   - Betroffene Dateien: `docs/informelles/phase2_planung.md`, `docs/informelles/planung_gesamt.md`  
   - Feststellung: Die Phase-2-Dokumentation weist mehrere bewusste Abweichungen gegenüber dem Ursprungsplan aus, etwa die Bereinigung von `BookingStatus`, die Erweiterung von `ReviewCaseType`, `CardStatus` und die Umstellung von `BookingSource`. Diese Abweichungen sind nicht als Mangel zu werten, aber für eine formale Auditspur müssen sie als genehmigte Planfortschreibung verstanden werden, nicht als 1:1-Erfüllung des ursprünglichen Plans.

2. **Befund 2/2-02**  
   - Kategorie: Tests  
   - Schweregrad: OFI  
   - Einordnung: originär zu Phase 2  
   - Betroffene Dateien: `docs/informelles/phase2_planung.md`, `tests/domain/`  
   - Feststellung: Die Testabdeckung ist laut Planung gegenüber dem ursprünglichen Umfang deutlich ausgebaut. Positiv ist die tiefere Invariantenabdeckung; für externe Prüfbarkeit fehlt aber in den ausgewerteten Artefakten eine separate, revisionsfeste Matrix, die Phase-2-Mussanforderungen direkt auf konkrete Testfälle abbildet.

3. **Befund 2/2-03**  
   - Kategorie: Dokumentation / Planung  
   - Schweregrad: Minor-Mangel  
   - Einordnung: reine Dokumentationsfrage  
   - Betroffene Dateien: `docs/informelles/phase2_planung.md`  
   - Feststellung: Das Dokument spricht im Schlussabschnitt von „V4-Bezügen“, verweist aber zugleich auf `pflichtenheft_arbeitszeit_v5.md` und `regelwerk_arbeitszeit_v5.md`. Das ist kein fachlicher Widerspruch im Kern, aber terminologisch unsauber und für externe Leser missverständlich.

### Freigabestatus

**GO mit Auflagen**

Begründung: Phase 2 ist als historischer Domänenkern nach den Planungsunterlagen erfüllt. Auflagen betreffen hauptsächlich die bessere formale Nachweisführung der Planabweichungen und die saubere Verknüpfung von Mussanforderungen zu Tests.

## Phase 3

### Sollbild

Phase 3 verlangt laut `docs/informelles/phase3_planung.md` die Application-Schicht mit `UnitOfWork`, Commands, Results und Use Cases für Buchen, Nachtrag, Korrektur und Regelarbeitszeit. In derselben Planung wird ausdrücklich festgehalten, dass `approve_supplement.py` und `reject_supplement.py` bereits als Phase-4-Inhalte in Phase 3 vorimplementiert wurden.

### Istbild

`docs/informelles/phase3_planung.md` beschreibt die Zielstruktur der Application-Schicht als Ist-Stand, einschließlich der vorgezogenen Freigabe-/Ablehnungs-Use-Cases. `docs/informelles/phase4_planung.md` bestätigt, dass diese Use Cases in Phase 3 vorimplementiert wurden. Der heutige Stand ist damit gegenüber dem historischen Plan erweitert, aber innerhalb der Repo-Dokumentation ausdrücklich nachgeführt.

### Befunde

1. **Befund 3/3-01**  
   - Kategorie: Dokumentation / Planung  
   - Schweregrad: Hinweis / Observation  
   - Einordnung: vorgezogene Erweiterung  
   - Betroffene Dateien: `docs/informelles/phase3_planung.md`, `docs/informelles/phase4_planung.md`  
   - Feststellung: Die Freigabe-/Ablehnungs-Use-Cases für Nachträge sind planungsseitig eine vorgezogene Erweiterung aus Phase 4. Das ist transparent dokumentiert und daher kein Verstoß, erschwert aber eine phasenscharfe historische Bewertung ohne zusätzliche Konsolidierung.

2. **Befund 3/3-02**  
   - Kategorie: Architektur  
   - Schweregrad: Hinweis / Observation  
   - Einordnung: originär zu Phase 3  
   - Betroffene Dateien: `docs/informelles/phase3_planung.md`, `docs/informelles/phase4_planung.md`, `docs/informelles/phase5_planung.md`  
   - Feststellung: Das Transaktionsmodell wurde gegenüber einem älteren Plantext korrigiert: Fachobjekte werden vor Audit-Log committed, weil separate SQLite-Verbindungen sonst Locking-Probleme verursachen. Das ist nachvollziehbar dokumentiert, zeigt aber, dass historische Formulierungen in älteren Planständen ohne Mitlesen der Nachträge missverständlich wären.

3. **Befund 3/3-03**  
   - Kategorie: Fachlogik / Compliance  
   - Schweregrad: Minor-Mangel  
   - Einordnung: nachträglicher Nachtrag/Hotfix  
   - Betroffene Dateien: `docs/informelles/phase4_planung.md`, `docs/informelles/phase5_planung.md`  
   - Feststellung: Die Ruhezeitprüfung und die konsolidierte Rollenprüfung werden in Phase 4 als „bereits in Phase 3 implementiert“ nachgetragen. Für eine revisionsfähige Phasensicht wäre eine explizite Nachtragsliste innerhalb von Phase 3 selbst günstiger, damit nicht wesentliche Phase-3-Befunde nur aus späteren Phasendokumenten rekonstruiert werden müssen.

### Freigabestatus

**GO mit Auflagen**

Begründung: Die Application-Schicht ist nach der vorliegenden Planlage funktional erfüllt und durch spätere Phasendokumente konsistent fortgeschrieben. Auflagen bestehen in der Aufbereitung einer klaren Nachtragschronik, damit vorgezogene und nachgezogene Inhalte ohne Querlesen auditfest nachvollzogen werden können.

## Phase 4

### Sollbild

Phase 4 umfasst laut `docs/informelles/phase4_planung.md` die Infrastruktur: SQLite-Unit-of-Work, zehn Repository-Implementierungen, Hardware-Leseschicht, Backup, Export, Pflichtauswertungen und Systemcheck. Die Planung nennt dazu konkrete Verzeichnisse unter `src/arbeitszeit/infrastructure/`, Integrations-Tests unter `tests/integration/`, E2E-Tests für Backup sowie die Migrationen `0004` und `0005`.

### Istbild

Die Verzeichnisstruktur von `src/arbeitszeit/infrastructure/` enthält `backup/`, `db/`, `export/`, `hardware/`, `system_check.py` und `time_monitor.py`. Unter `tests/integration/` existieren die in Phase 4 beschriebenen Testgruppen sowie zusätzliche Dateien wie `test_device_event_booking.py`, `test_init_db.py` und `test_user_accounts.py`. `migrations/` enthält die in Phase 4 beschriebenen Nachtragsmigrationen 0004 und 0005. Damit ist Phase 4 in der Breite umgesetzt und heute teils über ihren ursprünglichen Kern hinaus erweitert.

### Befunde

1. **Befund 4/4-01**  
   - Kategorie: Architektur  
   - Schweregrad: Major-Mangel  
   - Einordnung: originär zu Phase 4 / offener Architekturpunkt  
   - Betroffene Dateien: `docs/informelles/phase4_planung.md`, `docs/informelles/phase5_planung.md`, `docs/informelles/planung_gesamt.md`, `migrations/0005_time_bookings_device_event_id.sql`  
   - Feststellung: Die `device_event_id`-Verkettung ist schema- und application-seitig vorbereitet, aber laut `phase5_planung.md` schreibt derzeit kein Produktionspfad `device_events` in die Datenbank. Für die geforderte lückenlose Herkunftskette von Hardwareereignis zu Buchung bleibt dies ein offener Architekturpunkt. Dieser Punkt ist im Repository offen benannt und daher kein verdeckter Mangel, aber für einen formalen Release mit Nachweisanspruch freigaberelevant.

2. **Befund 4/4-02**  
   - Kategorie: Datenbank / Migrationen  
   - Schweregrad: Hinweis / Observation  
   - Einordnung: nachträglicher Nachtrag/Hotfix  
   - Betroffene Dateien: `docs/informelles/phase4_planung.md`, `migrations/0003_cleanup_booking_status.sql`, `migrations/0004_supplement_reject_fields_and_review_note.sql`, `migrations/0005_time_bookings_device_event_id.sql`  
   - Feststellung: Die Planung dokumentiert sauber, dass 0001 noch ältere CHECK-Constraints und ein früheres Supplement-Modell enthielt und erst 0003–0005 auf den finalen Stand bereinigen. Das zeigt eine belastbare Evolutionsspur, zugleich aber auch, dass die finale Semantik erst aus der gesamten Migrationskette und nicht aus 0001 allein hervorgeht.

3. **Befund 4/4-03**  
   - Kategorie: Tests  
   - Schweregrad: Minor-Mangel  
   - Einordnung: reine Dokumentationsfrage  
   - Betroffene Dateien: `docs/informelles/phase4_planung.md`, `tests/integration/`  
   - Feststellung: Die Planung listet für Phase 4 einen bestimmten Integrations-Testbestand, der heutige Verzeichnisstand enthält aber zusätzliche Integrationsdateien. Das ist funktional positiv, aber phasenscharf nicht mehr eindeutig. Ohne zusätzliche Testmatrix lässt sich aus dem Verzeichnis allein nicht sofort ablesen, welche Tests historischer Phase-4-Kern und welche spätere Erweiterungen sind.

4. **Befund 4/4-04**  
   - Kategorie: Betrieb / Betriebskonzepte  
   - Schweregrad: Minor-Mangel  
   - Einordnung: reine Dokumentationsfrage / externe Auflage  
   - Betroffene Dateien: `docs/informelles/phase4_planung.md`, `docs/informelles/planung_gesamt.md`  
   - Feststellung: Die Planung trennt korrekt zwischen technischem Backup-Service und externer Betriebsintegration wie systemd/cron, Rotationskonzept und organisatorischen Backup-Regeln. Für eine formale Betriebsfreigabe bleibt dadurch jedoch ein dokumentierter Restbestand an außerhalb des Codes liegenden Auflagen bestehen.

### Freigabestatus

**GO mit Auflagen**

Begründung: Der infrastrukturelle Kern ist breit umgesetzt und im Repo ungewöhnlich detailliert dokumentiert. Die Freigabe ist jedoch an Auflagen gebunden, weil der offene `device_event_id`-Pfad sowie externe Betriebs- und Nachweispflichten nicht als vollständig erledigt gelten dürfen.

## Phase 5

### Sollbild

Phase 5 verlangt laut `docs/informelles/phase5_planung.md` die Präsentationsschicht mit `presentation/terminal_ui/` und `presentation/admin_cli/`, Pflichtauswertungen in der Anwendung, UI-Integration des Systemchecks und Systemzeitprotokollierung. Die Planung grenzt ausdrücklich ab, dass die operative Aktivierung der `device_event_id`-Verkettung nicht Teil des Phase-5-Abnahmesolls ist.

### Istbild

Die Projektstruktur enthält das Verzeichnis `src/arbeitszeit/presentation/`. `phase5_planung.md` beschreibt die Phase als vollständig abgeschlossen und nennt `tests/e2e/test_booking_flow.py` und `tests/e2e/test_supplement_flow.py` als zentrale E2E-Nachweise; diese Testdateien sind im Verzeichnis `tests/e2e/` vorhanden. Zusätzlich ist `time_monitor.py` im Infrastrukturverzeichnis vorhanden, was die in Phase 5 integrierte Systemzeitprotokollierung stützt.

### Befunde

1. **Befund 5/5-01**  
   - Kategorie: Architektur  
   - Schweregrad: Major-Mangel  
   - Einordnung: originär phasenübergreifend, in Phase 5 ausdrücklich ausgeklammert  
   - Betroffene Dateien: `docs/informelles/phase5_planung.md`, `docs/informelles/planung_gesamt.md`, `migrations/0005_time_bookings_device_event_id.sql`  
   - Feststellung: Die Phase 5 erklärt den nicht aktivierten `device_event_id`-Pfad ausdrücklich zum Nicht-Scope der Abnahme. Für eine reine Phasenabnahme ist das zulässig dokumentiert; für eine Gesamtbewertung des Systems bleibt der Punkt jedoch freigaberelevant und blockiert eine uneingeschränkte GO-Einstufung des Gesamtsystems.

2. **Befund 5/5-02**  
   - Kategorie: Dokumentation / Planung  
   - Schweregrad: Minor-Mangel  
   - Einordnung: reine Dokumentationsfrage  
   - Betroffene Dateien: `docs/informelles/phase5_planung.md`, `tests/e2e/`  
   - Feststellung: In `phase5_planung.md` werden ältere und neuere Testzählstände parallel geführt („361 Tests grün“, „heute 395“). Das ist nachvollziehbar historisiert, für externe Auditoren aber nur mit hoher Aufmerksamkeit eindeutig lesbar.

3. **Befund 5/5-03**  
   - Kategorie: Betrieb / Betriebskonzepte  
   - Schweregrad: Minor-Mangel  
   - Einordnung: externe Auflage  
   - Betroffene Dateien: `docs/informelles/phase5_planung.md`, `docs/informelles/planung_gesamt.md`  
   - Feststellung: Die Betriebsdokumentation zu Exportverzeichnis, Aufbewahrungsfrist und Löschkonzept wird in Phase 5 textlich festgelegt, aber zugleich als „kein Code“ bzw. organisatorische Regel beschrieben. Für den externen Prüfer ist damit positiv dokumentiert, dass diese Regeln existieren; ob sie formal verabschiedet und betrieblich umgesetzt sind, ist **nicht entscheidbar auf Basis der vorliegenden Artefakte**.

4. **Befund 5/5-04**  
   - Kategorie: Tests  
   - Schweregrad: OFI  
   - Einordnung: originär zu Phase 5  
   - Betroffene Dateien: `docs/informelles/phase5_planung.md`, `tests/e2e/`, `tests/integration/`  
   - Feststellung: Die Planung sagt ausdrücklich, dass es für die Präsentationsschicht keine Unit-Tests gibt, weil die Logik in Application und Infrastructure liegt. Das ist architektonisch plausibel; als Optimierung wäre eine knappe Testdesign-Notiz sinnvoll, die diese bewusste Nichtabdeckung formal begründet.

### Freigabestatus

**GO mit Auflagen**

Begründung: Die Präsentationsschicht ist laut Repository-Planung und Artefaktlage implementiert. Auflagen betreffen die externen Betriebsnachweise und den weiterhin offenen Ereignisverkettungspfad, der zwar nicht zum Phase-5-Scope erklärt wird, aber das Gesamtsystem betrifft.

## Querschnittsbewertung

### Architektur / Design

Die Soll-Architektur mit den Schichten Domain, Application, Infrastructure und Presentation ist in `docs/informelles/planung_gesamt.md` beschrieben und in der tatsächlichen Verzeichnisstruktur `src/arbeitszeit/domain/`, `application/`, `infrastructure/`, `presentation/` abgebildet. Diese Schichtentrennung ist einer der stärksten Punkte des Repository-Stands.

Wiederkehrendes Muster ist jedoch die planungsseitige Fortschreibung über mehrere Phasen hinweg: Inhalte werden vorgezogen, nachgezogen oder in späteren Phasendokumenten korrigiert. Das ist offen dokumentiert, erhöht aber den Interpretationsaufwand für externe Prüfer.

### Fachlogik und Compliance

Die Planungsunterlagen beschreiben eine konsistente Modellierung von Buchungen, Review-Fällen, Korrekturen, Nachträgen, Rollen, Audit-Log und Aufbewahrungsprinzip. Besonders positiv ist, dass die Dokumentation ausdrücklich klarstellt, welche fachlichen Konzepte orthogonal modelliert werden, etwa `BookingStatus` versus `ReviewCaseType` oder `BookingSource.MANUAL`.

Offen bleibt querschnittlich der produktive Nachweis einer vollständigen Verkettung von Hardware-Ereignis zu Buchung über `device_events` und `device_event_id`. Dieser Punkt ist dokumentiert, aber nicht abgeschlossen.

### Datenbank und Migrationen

Die Migrationskette 0001–0006 ist als Evolutionsspur nachvollziehbar dokumentiert. Positiv ist, dass spätere Korrekturen an Statusmodell, Supplement-Logik, `device_event_id` und `APPLICATION_ERROR` explizit nachgehalten werden.

Gleichzeitig ist für externe Prüfer wichtig: Der finale fachliche Stand ergibt sich nicht allein aus `0001_schema.sql`, sondern erst aus der gesamten Kette. Diese Struktur ist technisch legitim, sollte aber in einem formalen Auditbeiblatt nochmals verdichtet werden.

### Tests

Die Testlandschaft ist breit: `tests/test_migrations.py`, `tests/domain/`, `tests/application/`, `tests/integration/`, `tests/e2e/`. Die Planungsdokumente nennen durchgängig konkrete Testdateien und ordnen viele Pflichtszenarien den Testebenen zu.

Der zentrale Schwachpunkt ist nicht die Breite der Tests, sondern die Nachweisform: Historische Phasenstände und heutiger Teststand sind teilweise vermischt, und eine revisionsfeste Testmatrix wird in `planung_gesamt.md` selbst als offener Nachweispunkt benannt.

### Dokumentation und Betrieb

Die Dokumentation ist für ein Entwicklungsrepository ungewöhnlich detailliert und selbstkritisch. Positiv ist insbesondere die klare Kennzeichnung von Nachträgen, offenen Architekturpunkten und externen organisatorischen Pflichten.

Gerade diese Offenheit zeigt aber auch den Restaufwand: Betriebsdokumentation, Rollen- und Freigabeverantwortung, Testmatrix, produktiver `device_events`-Pfad sowie IT-Sicherheits- und Datenschutznachweise sind nicht vollständig durch die vorhandenen Code-Artefakte beweisbar.

## Priorisierte To-do-Liste

### Kritisch
- Offenen Architekturpunkt `device_events` / `device_event_id` entscheiden und entweder produktiv implementieren oder formell aus dem Sollbild herausnehmen; betroffen: `docs/informelles/planung_gesamt.md`, `docs/informelles/phase4_planung.md`, `docs/informelles/phase5_planung.md`, `migrations/0005_time_bookings_device_event_id.sql`.
- Revisionsfeste Testmatrix erstellen, die Muss-Anforderungen aus Pflichtenheft und Regelwerk direkt konkreten Tests zuordnet; betroffen: `docs/informelles/planung_gesamt.md`, `tests/`.

### Hoch
- Phasenübergreifende Nachtragsmatrix ergänzen, die für jedes Artefakt ausweist: historische Zielphase, tatsächliche Einführungsphase, spätere Änderungen; betroffen: `docs/informelles/phase1_planung.md` bis `docs/informelles/phase5_planung.md`, `docs/informelles/planung_gesamt.md`.
- Formale Betriebsdokumentation als freigabefähiges Artefakt separat ausweisen, statt nur in Plantexten zu beschreiben; betroffen: `docs/informelles/planung_gesamt.md`, `docs/informelles/phase4_planung.md`, `docs/informelles/phase5_planung.md`.

### Mittel
- Terminologie in den Phasenplänen harmonisieren, insbesondere V4/V5-Bezüge und historische Testzählstände; betroffen: `docs/informelles/phase2_planung.md`, `docs/informelles/phase5_planung.md`.
- Migrationsübersicht um eine kompakte Tabelle „fachliche Änderung pro Migration“ ergänzen; betroffen: `docs/informelles/phase1_planung.md`, `migrations/`.

### Niedrig
- Für die Präsentationsschicht eine kurze Testdesign-Notiz ergänzen, warum keine Unit-Tests vorgesehen sind; betroffen: `docs/informelles/phase5_planung.md`.
- Zusätzliche Kennzeichnung im Testverzeichnis oder in einer Übersicht, welche Tests historisch welcher Phase zuzuordnen sind; betroffen: `tests/`, `docs/informelles/planung_gesamt.md`.

## GO/NO-GO-Matrix

| Gegenstand | Status | Kurzbegründung |
|---|---|---|
| Phase 1 | GO mit Auflagen | Historischer Kern des Fundaments ist dokumentiert und nachgeführt; Auflagen betreffen Nachweisverdichtung und Referenzklarheit. |
| Phase 2 | GO mit Auflagen | Domänenkern laut Planung abgeschlossen; Auflagen betreffen formale Test- und Änderungsnachweise. |
| Phase 3 | GO mit Auflagen | Application-Schicht erfüllt, aber mit vorgezogenen und nachgezogenen Inhalten über mehrere Dokumente verteilt. |
| Phase 4 | GO mit Auflagen | Infrastruktur breit umgesetzt; offener `device_event_id`-Pfad und externe Betriebsauflagen verhindern ein vorbehaltloses GO. |
| Phase 5 | GO mit Auflagen | Präsentationsschicht implementiert; externe Betriebsnachweise und offener Ereignispfad bleiben relevant. |
| Gesamt-System | NO-GO | Für eine uneingeschränkte formale Gesamtfreigabe verbleiben mindestens der offene `device_events`-/`device_event_id`-Pfad sowie die fehlende revisionsfeste Testmatrix und externe Betriebsnachweise. |

## Selbstcheck

### Erkannte Widersprüche und Spannungen in den Planungsunterlagen

- `docs/informelles/phase2_planung.md` spricht im Schlussabschnitt von „V4-Bezügen“, verweist aber inhaltlich auf v5-Referenzdokumente.
- `docs/informelles/planung_gesamt.md` beschreibt Phase 3 in der Zielstruktur mit vier Use Cases, während `docs/informelles/phase3_planung.md` und `docs/informelles/phase4_planung.md` zusätzlich die vorgezogenen Use Cases `approve_supplement.py` und `reject_supplement.py` führen.
- `docs/informelles/phase4_planung.md` nennt an einer Stelle ältere Testzahlen und eine frühere Scope-Beschreibung; der heutige Verzeichnisstand enthält zusätzliche Integrationsdateien.
- `docs/informelles/phase5_planung.md` enthält parallel historische und heutige Testzählstände, was korrekt historisiert, aber nicht auf den ersten Blick eindeutig ist.

### Stellen mit nicht eindeutiger Aussage zwischen Plan und Code/Test

- Ob alle in Plantexten referenzierten Pflichtenheft-/Regelwerk-Dateien exakt unter den genannten Namen und Pfaden im aktuellen Repository liegen, ist im Rahmen der hier ausgewerteten Artefakte nicht vollständig belegt.
- Ob die in den Phasenplänen genannten Moduldateien in jeder Einzelheit exakt dem beschriebenen Inhalt entsprechen, ist nur insoweit entscheidbar, wie die Planungsdokumente selbst den Ist-Stand bereits nachgeführt haben; eine vollständige Zeile-für-Zeile-Verifikation aller Quellmodule wurde in diesem Audit nicht vorgenommen.
- Ob die in `tests/integration/` zusätzlich vorhandenen Dateien historisch Phase 4, Phase 5+ oder einem Nachtragsinkrement zuzuordnen sind, ist ohne ergänzende Testmatrix nicht immer sofort eindeutig.

### Punkte, die nicht entscheidbar auf Basis der vorliegenden Artefakte sind

- Ob organisatorische Betriebsregeln zu Export, Löschung, Backup, Restore, Rollen und IT-Sicherheit außerhalb des Repositorys formal verabschiedet und praktisch umgesetzt wurden.
- Ob die optionale Cloud- oder NAS-Backup-Einbindung organisatorisch und datenschutzrechtlich vollständig geregelt ist.
- Ob reale Zielhardware, reale Terminalgeräte und reale Praxisprozesse mit dem dokumentierten Stand bereits produktiv betrieben werden.
- Ob die offenen Architektur- und Nachweispunkte außerhalb des Repositorys bereits durch separate Freigabedokumente kompensiert wurden.

## Gesamturteil

Der aktuelle Repository-Stand ist fachlich und architektonisch stark, für ein internes Entwicklungsprojekt ungewöhnlich transparent dokumentiert und in den Phasen 1 bis 5 weitgehend konsistent fortgeschrieben. Für eine formale, externe Freigabe als Gesamtsystem reicht der Nachweisstand jedoch noch nicht aus, weil zentrale Querschnittsnachweise bewusst selbst als offen dokumentiert sind.

Das Haupthemmnis ist nicht ein verdeckter Qualitätsmangel im Code, sondern die noch offene formale Schließung von Architektur- und Nachweisfragen: insbesondere `device_events`/`device_event_id`, revisionsfeste Testmatrix sowie separate Betriebs- und Organisationsnachweise. Bis zu deren Schließung ist das Gesamturteil aus Audit-Sicht **NO-GO für das Gesamtsystem**, bei gleichzeitigem **GO mit Auflagen** für die historischen Phasen 1 bis 5.
