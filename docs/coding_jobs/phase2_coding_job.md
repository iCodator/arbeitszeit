# Programmieraufgabe Phase 2 – arbeitszeit

## Ziel

Implementiere **ausschließlich Phase 2** des Projekts `arbeitszeit`. Phase 2 umfasst die **Domänenschicht**: Enums, Domänenfehler, fachliche Entitäten, Prüfservices und Repository-Ports. Führe **keine** Aufgaben aus späteren Phasen aus. [planung_gesamt.md; phase2_planung_konkret.md]

Die Aufgabe ist erfolgreich abgeschlossen, wenn die Domäne fachlich vollständig modelliert ist, die zentralen Invarianten zuverlässig erzwingt und die zugehörigen Domänentests die Regeln reproduzierbar absichern. [planung_gesamt.md; phase2_planung_konkret.md]

## Strikte Grenzen

Arbeite streng innerhalb dieses Umfangs. **Nicht** Teil dieser Aufgabe sind insbesondere: [planung_gesamt.md; phase2_planung_konkret.md]

- Migrationen, Verbindungsaufbau und Initialisierung aus Phase 1, [planung_gesamt.md; phase2_planung_konkret.md]
- Commands, Results, Use Cases und Unit of Work aus Phase 3, [planung_gesamt.md; phase2_planung_konkret.md]
- Fake-Repositories für Application-Tests, [planung_gesamt.md; phase2_planung_konkret.md]
- echte SQLite-Repositories und Infrastruktur aus Phase 4, [planung_gesamt.md; phase2_planung_konkret.md]
- Export, PDF, Backup, Systemcheck und Hardware, [planung_gesamt.md; phase2_planung_konkret.md]
- Terminal-UI, Admin-CLI und Betriebsschicht aus Phase 5. [planung_gesamt.md; phase2_planung_konkret.md]

Wenn du an eine Stelle kommst, an der du Persistenz, CLI oder Anwendungsorchestrierung bräuchtest, stoppe. Diese Aufgabe endet an der klaren Grenze der Domänenschicht. [planung_gesamt.md; phase2_planung_konkret.md]

## Verbindlicher Lieferumfang

Erzeuge oder vervollständige exakt die folgenden Bestandteile unter `src/arbeitszeit/domain/` und `tests/domain/`: [planung_gesamt.md; phase2_planung_konkret.md]

- `enums.py` [planung_gesamt.md; phase2_planung_konkret.md]
- `errors.py` [planung_gesamt.md; phase2_planung_konkret.md]
- `entities.py` [planung_gesamt.md; phase2_planung_konkret.md]
- `services/booking_rules.py` [planung_gesamt.md; phase2_planung_konkret.md]
- `services/compliance_checks.py` [planung_gesamt.md; phase2_planung_konkret.md]
- `ports/repositories.py` [planung_gesamt.md; phase2_planung_konkret.md]
- `tests/domain/test_booking_rules.py` [phase2_planung_konkret.md]
- `tests/domain/test_compliance_checks.py` [phase2_planung_konkret.md]
- `tests/domain/test_entities.py` [phase2_planung_konkret.md]
- optional entsprechend der Gesamtplanung: `tests/domain/test_audit_events.py`. [planung_gesamt.md; phase2_planung_konkret.md]

## Aufgabenbeschreibung

### 1. Enums implementieren

Implementiere in `enums.py` die in der Gesamtplanung definierten 11 `StrEnum`-Klassen: [planung_gesamt.md; phase2_planung_konkret.md]

- `BookingType`,
- `BookingStatus`,
- `ReviewCaseType`,
- `ReviewCaseStatus`,
- `ReviewSeverity`,
- `CardStatus`,
- `UserRole`,
- `BookingSource`,
- `ChangeOrigin`,
- `ApprovalStatus`,
- `ScopeType`. [planung_gesamt.md; phase2_planung_konkret.md]

Achte darauf, dass die fachlich verbindlichen Status- und Rollenbegriffe aus Pflichtenheft und Regelwerk korrekt repräsentiert sind. [Pflichtenheft v4; Regelwerk v4; phase2_planung_konkret.md]
