# Konkrete Planung Phase 2 – arbeitszeit

## Zweck

Dieses Dokument leitet aus der aktuellen Gesamtplanung die **konkrete Phase 2** für das Projekt `arbeitszeit` ab. Phase 2 umfasst die **Domänenschicht** und nur die Domänenschicht. Ziel ist die fachlich saubere Modellierung der zentralen Begriffe, Regeln, Fehlerfälle, Invarianten und Schnittstellen, auf denen spätere Application-, Infrastruktur- und Präsentationsschichten aufbauen. [planung_gesamt.md]

Die Phase-2-Planung steht im Kontext der aktuellen Referenzdokumente `docs/pflichtenheft_arbeitszeit_v4.md`, `docs/regelwerk_arbeitszeit_v4.md` und `docs/anlage_einhaltung_pflichtenheft_v2.md`. Dieses Dokument beschreibt den heute gültigen fachlichen Zuschnitt von Phase 2 und grenzt ihn ausdrücklich gegen Phase 1 sowie gegen spätere Phasen ab. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Zielbild Phase 2

Phase 2 liefert ein belastbares fachliches Kernmodell. Dazu gehören Enums, Domänenfehler, immutable Entitäten mit Invarianten, fachliche Prüfservices und Repository-Ports als abstrakte Schnittstellen. [planung_gesamt.md]

Phase 2 implementiert **keine** Datenbankzugriffe, **keine** Use Cases, **keine** CLI, **keine** Hardware-Anbindung und **keine** Exporte. Sie schafft ausschließlich die fachliche Grundlage, auf der diese späteren Ebenen regelkonform entwickelt werden können. [planung_gesamt.md]

## Verbindlicher Lieferumfang

Laut aktueller Gesamtplanung umfasst Phase 2 die folgenden Bestandteile unter `src/arbeitszeit/domain/` sowie zugehörige Tests: [planung_gesamt.md]

- `enums.py` mit 11 `StrEnum`-Klassen. [planung_gesamt.md]
- `errors.py` mit `DomainError` und 9 Subklassen. [planung_gesamt.md]
- `entities.py` mit 9 frozen `@dataclass`-Entitäten und `__post_init__`-Invarianten. [planung_gesamt.md]
- `services/booking_rules.py` mit `validate_booking_sequence()` und `ValidationResult`. [planung_gesamt.md]
- `services/compliance_checks.py` mit `check_break_compliance()`, `check_max_hours()`, `check_rest_period()` und `ComplianceFlag`. [planung_gesamt.md]
- `ports/repositories.py` mit 10 `Protocol`-Interfaces. [planung_gesamt.md]
- Domänentests unter `tests/domain/`. [planung_gesamt.md]

## Nicht Teil von Phase 2

Die folgenden Themen gehören **nicht** zu Phase 2: [planung_gesamt.md]

- Datenbankschema und Migrationen aus Phase 1. [planung_gesamt.md]
- Application-Use-Cases, Commands, Results und Unit of Work aus Phase 3. [planung_gesamt.md]
- echte SQLite-Repositories, Backup, Export, Systemcheck und Hardware aus Phase 4. [planung_gesamt.md]
- Terminal-UI, Admin-CLI und betriebliche Orchestrierung aus Phase 5. [planung_gesamt.md]

Phase 2 definiert also die Fachlogik, führt sie aber noch nicht mit echter Persistenz oder Benutzerinteraktion zusammen. [planung_gesamt.md]

## Fachliche Leitplanken

Die Domänenschicht muss den verbindlichen fachlichen Kern aus Pflichtenheft und Regelwerk sauber abbilden. Dazu gehören die Buchungsarten `Kommen`, `Gehen`, `Pause Start`, `Pause Ende`, die Statuswerte `OK`, `OPEN`, `WARN`, `NEEDS_REVIEW`, `CORRECTED`, `CLOSED_WITH_NOTE`, die Unterscheidung zwischen Korrekturen und Nachträgen sowie die arbeitszeitrechtlichen Prüfhilfen zu Pause, Höchstarbeitszeit und Ruhezeit. [Pflichtenheft v4] [Regelwerk v4]

Wichtig ist dabei die in der Gesamtplanung ausdrücklich festgehaltene orthogonale Modellierung: `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION` und `MANUAL_ENTRY` werden **nicht** als `BookingStatus` modelliert, sondern fachlich getrennt als Review-Case-Typen bzw. Herkunftskennzeichnung. [planung_gesamt.md] [Regelwerk v4]

## Konkrete Arbeitspakete

### 1. Enums definieren

In `enums.py` werden die verbindlichen fachlichen Enumerationen implementiert. Laut Gesamtplanung sind dies: [planung_gesamt.md]

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
- `ScopeType`. [planung_gesamt.md]

Die Enums müssen die im Pflichtenheft und Regelwerk verbindlich geforderten Zustände und Rollen so abbilden, dass spätere Schichten sie direkt verwenden können. [Pflichtenheft v4] [Regelwerk v4]

### 2. Domänenfehler definieren

In `errors.py` wird `DomainError` als Basisklasse definiert. Darauf aufbauend werden die in der Gesamtplanung genannten fachlichen Fehler implementiert: [planung_gesamt.md]

- `UnknownCardError`,
- `InactiveCardError`,
- `InactiveEmployeeError`,
- `InvalidBookingSequenceError`,
- `OpenPhaseConflictError`,
- `PermissionDeniedError`,
- `ValidationError`,
- `NotFoundError`,
- `ConflictError`. [planung_gesamt.md]

Diese Fehler bilden die spätere Sprache zwischen Domäne und Application-Schicht. Sie müssen deshalb fachlich präzise und stabil sein. [planung_gesamt.md]

### 3. Entitäten modellieren

In `entities.py` werden 9 frozen `@dataclass`-Entitäten modelliert: [planung_gesamt.md]

- `Employee`,
- `UserAccount`,
- `RfidCard`,
- `TimeBooking`,
- `WorkScheduleVersion`,
- `ReviewCase`,
- `Supplement`,
- `BookingCorrection`,
- `AuditLogEntry`. [planung_gesamt.md]

Die Entitäten müssen fachliche Invarianten in `__post_init__` durchsetzen. Laut Gesamtplanung sind insbesondere folgende Punkte relevant: [planung_gesamt.md]

- `RfidCard`: `valid_until >= valid_from`. [planung_gesamt.md]
- `WorkScheduleVersion`: Scope-Konsistenz und konsistente Datumsreihenfolge. [planung_gesamt.md]
- `ReviewCase`: Status und Schließungsdaten müssen zusammenpassen. [planung_gesamt.md]
- `Supplement`: Freigabestatus und Freigabedaten müssen konsistent sein. [planung_gesamt.md]

Die Entitäten dürfen keine Infrastruktur- oder Persistenzlogik enthalten. Sie repräsentieren nur den fachlichen Zustand. [planung_gesamt.md]

### 4. Buchungsfolgeregeln implementieren

In `services/booking_rules.py` wird `validate_booking_sequence()` implementiert. Diese Funktion prüft fachlich zulässige und unzulässige Buchungsfolgen auf Basis vorhandener Tagesbuchungen. [planung_gesamt.md]

Die Regeln müssen mit den Vorgaben aus dem Regelwerk übereinstimmen. Dazu gehören unter anderem unzulässige Konstellationen wie `Kommen` nach `Kommen`, `Pause Ende` ohne offene Pause, erste Tagesbuchung als `Gehen` oder `Pause Ende` und `Gehen` bei offener Pause. [Regelwerk v4]

Die Funktion muss Ergebnisse so zurückgeben, dass spätere Use Cases daraus fachlich korrekte Entscheidungen und Fehler ableiten können. [planung_gesamt.md]

### 5. Compliance-Prüfhilfen implementieren

In `services/compliance_checks.py` werden die fachlichen Prüfhilfen zur Arbeitszeit implementiert. [planung_gesamt.md]

Verpflichtend sind laut Gesamtplanung und Referenzdokumenten: [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

- `check_break_compliance()` für mehr als 6 Stunden ohne Pause und mehr als 9 Stunden ohne ausreichende Gesamtpause, [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- `check_max_hours()` für mehr als 8 Stunden werktägliche Arbeitszeit sowie Eskalation bei mehr als 10 Stunden, [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- `check_rest_period()` für weniger als 11 Stunden Ruhezeit zwischen zwei Arbeitstagen. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

Selbstkritische Abgrenzung: Die Gesamtplanung hält fest, dass die vollständige Nutzung der Ruhezeitprüfung in Echtfällen in Phase 3 zunächst noch auf Phase 4 verschoben wurde, weil dort Vortageskontext benötigt wird. Das ändert aber nichts daran, dass `check_rest_period()` selbst bereits in Phase 2 als Pflichtbestandteil der Domäne existieren muss. [planung_gesamt.md]

### 6. Repository-Ports definieren

In `ports/repositories.py` werden 10 `Protocol`-Interfaces definiert. Diese bilden die Verträge zwischen Domäne/Application und späterer Infrastruktur. [planung_gesamt.md]

Die Gesamtplanung nennt dafür: [planung_gesamt.md]

- `EmployeeRepository`,
- `UserAccountRepository`,
- `RfidCardRepository`,
- `TimeBookingRepository`,
- `WorkScheduleRepository`,
- `ReviewCaseRepository`,
- `SupplementRepository`,
- `BookingCorrectionRepository`,
- `AuditLogRepository`,
- `SystemConfigRepository`. [planung_gesamt.md]

Die Ports müssen exakt so präzise sein, dass spätere Fakes und SQLite-Repositories dieselbe Fachsprache sprechen. Gleichzeitig dürfen sie keine Implementierungsdetails der Infrastruktur vorwegnehmen. [planung_gesamt.md]

### 7. Domänentests schreiben

Unter `tests/domain/` werden die fachlichen Regeln und Invarianten abgesichert. Die Gesamtplanung dokumentiert für den heutigen Stand folgende Testmodule: [planung_gesamt.md]

- `test_booking_rules.py`, [planung_gesamt.md]
- `test_compliance_checks.py`, [planung_gesamt.md]
- `test_entities.py`, [planung_gesamt.md]
- `test_audit_events.py`. [planung_gesamt.md]

Für die konkrete Phase-2-Planung bedeutet das: Alle relevanten Invarianten, Buchungsfolgeregeln und Arbeitszeitprüfungen müssen testscharf beschrieben und abgesichert werden. Die Domäne darf nicht nur „plausibel wirken“, sondern muss ihre Fachregeln reproduzierbar beweisen. [planung_gesamt.md]

## Qualitätskriterien für den Phase-2-Abschluss

Phase 2 gilt erst dann als sauber abgeschlossen, wenn alle folgenden Punkte erfüllt sind: [planung_gesamt.md]

- Alle benötigten Enums sind fachlich vollständig und widerspruchsfrei modelliert. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- Domänenfehler bilden die relevanten fachlichen Fehlerfälle präzise ab. [planung_gesamt.md]
- Entitäten sind immutable modelliert und erzwingen ihre Invarianten zuverlässig. [planung_gesamt.md]
- Buchungsfolgeregeln erkennen unzulässige Sequenzen korrekt. [planung_gesamt.md] [Regelwerk v4]
- Compliance-Prüfhilfen decken Pause, Höchstarbeitszeit und Ruhezeit ab. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- Repository-Ports sind vollständig genug für spätere Phasen, ohne Infrastruktur vorwegzunehmen. [planung_gesamt.md]
- Die Domänentests belegen die Regeln nachvollziehbar und robust. [planung_gesamt.md]

## Bekannte Risiken und Selbstkritik

Ein zentrales Risiko ist die Vermischung von Domänenlogik und Infrastruktur. Phase 2 darf keine SQLite-Details, keine Repository-Implementierungen und keine Use-Case-Orchestrierung enthalten. Sobald die Domäne beginnt, Persistenz- oder CLI-Wissen zu tragen, ist die Phasengrenze verletzt. [planung_gesamt.md]

Ein weiteres Risiko ist die falsche Modellierung fachlicher Hinweislagen als `BookingStatus`. Die Gesamtplanung und das Regelwerk stellen ausdrücklich klar, dass `POSSIBLE_*`-Lagen und `MANUAL_ENTRY` orthogonal modelliert werden müssen. Diese Trennung ist keine optionale Designidee, sondern eine verbindliche Fachentscheidung. [planung_gesamt.md] [Regelwerk v4]

Ein drittes Risiko ist die Unterschätzung von Invarianten. Gerade `WorkScheduleVersion`, `ReviewCase`, `Supplement` und `RfidCard` müssen fehlerhafte Zustände bereits beim Erzeugen der Objekte abweisen. Spätere Schichten dürfen sich auf diese Garantien verlassen können. [planung_gesamt.md]

## Offene Punkte, die bewusst nicht in Phase 2 gezogen werden

Die folgenden Punkte sind wichtig, aber **nicht** Bestandteil der konkreten Phase-2-Umsetzung: [planung_gesamt.md]

- Application-Commands, Results, Use Cases und Unit of Work, [planung_gesamt.md]
- Fakes für Use-Case-Tests, [planung_gesamt.md]
- echte SQLite-Repositories, [planung_gesamt.md]
- `device_event_id`-Verkettung, [planung_gesamt.md] [Anlage v2]
- Backup, Export, PDF, Pflichtauswertungen und Systemcheck, [planung_gesamt.md]
- Terminal-UI, Admin-CLI und Betriebsschicht, [planung_gesamt.md]
- organisatorische Dokumentation, Testmatrix, Datenschutz- und IT-Sicherheitsnachweise. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Ergebnis

Die konkrete Phase 2 ist damit klar begrenzt: **fachliche Enums, Domänenfehler, immutable Entitäten mit Invarianten, Buchungsfolgeregeln, Arbeitszeit-Prüfhilfen, Repository-Ports und belastbare Domänentests**. Genau dieses Paket bildet laut aktueller Gesamtplanung den abgeschlossenen fachlichen Kern, auf den Phase 3 anschließend aufsetzt. [planung_gesamt.md]
