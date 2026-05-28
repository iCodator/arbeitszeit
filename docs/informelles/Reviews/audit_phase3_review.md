# Audit Phase 3 – Application-Schicht

Kurze Vorabantwort: **Ja, Phase 3 ist auf Basis der vorliegenden Unterlagen vollständig analysierbar**. Die Referenzlage aus `phase3_planung.md`, `planung_gesamt.md`, `pflichtenheft_arbeitszeit_v3.md`, `regelwerk_arbeitszeit_v3.md` und dem Codeexport `arbeitszeit.md` ist ausreichend konsistent, um Sollbild, Istbild und Phasenabgrenzung belastbar zu prüfen. Für die eigentliche Bewertung ist eine Unterteilung nach Dateien und Use Cases dennoch fachlich sauberer, weil mehrere Inhalte bereits über den originären Phase-3-Umfang hinaus in Richtung Phase 4 vorgezogen wurden.[file:1][file:6][file:7][file:8][file:9]

## Sollbild Phase 3

Phase 3 umfasst laut Planung die **Application-Schicht** mit `commands.py`, `results.py`, `unit_of_work.py`, In-Memory-Fakes, den Kern-Use-Cases `book_time.py`, `register_supplement.py`, `correct_booking.py` und `manage_work_schedule.py` sowie zugehörigen Tests unter `tests/application/`. Gleichzeitig dokumentiert die Planung ausdrücklich, dass `approve_supplement.py`, `reject_supplement.py` und deren Tests bereits in Phase 3 **vorimplementiert** wurden, obwohl sie originär Phase 4 zuzuordnen sind.[file:1][file:6]

Fachlich verlangt Phase 3 die Orchestrierung der Domänenregeln aus Phase 2: Karten- und Mitarbeiterprüfung, Sequenzprüfung, Statusbildung, Nachträge, Korrekturen, Regelarbeitszeitänderungen, Audit-Log-Verhalten sowie testbare Unit-of-Work-Transaktionen. Pflichtenheft und Regelwerk fordern dabei insbesondere Rollen- und Rechteabgrenzung, Erfassung echter Buchungen, Kennzeichnung statt stiller Korrektur, Prüfhinweise zu Arbeitszeitgesetz-Themen und vollständige Protokollierung relevanter Vorgänge.[file:1][file:7][file:9]

## Istbild der Codebasis

Die exportierte Codebasis enthält die geplante Application-Struktur tatsächlich unter `src/arbeitszeit/application/` mit `commands.py`, `results.py`, `unit_of_work.py` und allen sechs Use-Case-Dateien. Ebenso vorhanden sind `tests/application/fakes.py` sowie alle sechs zugehörigen Testmodule, also auch die in der Planung als vorgezogene Phase-4-Bestandteile gekennzeichneten Tests für Genehmigung und Ablehnung von Nachträgen.[file:8]

Auffällig ist, dass `arbeitszeit.md` die **realen aktuellen Dateinamen** in Python-Snake-Case mit Unterstrichen zeigt, etwa `book_time.py`, `approve_supplement.py`, `unit_of_work.py`, `audit_events.py`, `booking_rules.py` und `compliance_checks.py`. Der Nutzerprompt nennt dagegen die in der Arbeitsumgebung früher verwendeten Normalformen ohne Unterstriche wie `booktime.py`, `approvesupplement.py`, `unitofwork.py`, `auditevents.py`, `bookingrules.py` und `compliancechecks.py`; für die Prüfung maßgeblich ist daher der reale Exportstand aus `arbeitszeit.md`.[file:1][file:8]

## Soll-/Ist-Bewertung je Bereich

| Befund | Risiko | Empfehlung | Betroffene Datei | Kategorie |
|---|---|---|---|---|
| Phase 3 ist als Kernumfang funktional vollständig vorhanden: `commands.py`, `results.py`, `unit_of_work.py`, die vier originären Use Cases und `tests/application/fakes.py` sind im Export vorhanden und entsprechen dem geplanten Umfang. [file:1][file:6][file:8] | Niedrig; kein fachlicher Blocker für Folgephasen. [file:1][file:6] | Als historisch abgeschlossenen Kernbestand markieren. [file:1][file:6] | `src/arbeitszeit/application/commands.py`, `results.py`, `unit_of_work.py`, `use_cases/*.py`, `tests/application/fakes.py` [file:8] | kein Befund |
| Die Planung dokumentiert `approve_supplement.py` und `reject_supplement.py` explizit als **Phase-4-Vorimplementierung in Phase 3**; sie sind in der Codebasis enthalten und getestet. [file:1][file:6][file:8] | Mittel; ohne Kennzeichnung würden diese Inhalte fälschlich als originärer Phase-3-Lieferumfang bewertet. [file:1][file:6] | In Dokumentation und Reviews strikt als vorgezogene Erweiterung ausweisen. [file:1][file:6] | `src/arbeitszeit/application/use_cases/approve_supplement.py`, `reject_supplement.py`, `tests/application/test_approve_supplement.py`, `test_reject_supplement.py` [file:8] | vorgezogene Erweiterung |
| Die reale Paket- und Dateibenennung weicht vom Prompt und von älteren Normalformen ab: im Export stehen `use_cases`, `unit_of_work.py`, `book_time.py`, `audit_events.py`, `booking_rules.py`, `compliance_checks.py`; die Planunterlage zeigt teils frühere oder normalisierte Schreibweisen. [file:1][file:8] | Mittel; erhöht Dokumentations- und Reviewrisiko, weil Dateireferenzen sonst an der realen Codebasis vorbeigehen. [file:1][file:8] | Planungsdokumente und Auditvorlagen auf die realen Exportpfade vereinheitlichen, historische Schreibweisen nur noch als Alias nennen. [file:1][file:8] | mehrere Pfade in `src/arbeitszeit/application/`, `src/arbeitszeit/domain/`, `tests/application/` [file:8] | Dokumentationsfehler |
| `BookUseCase` enthält Ruhezeitprüfung mit Vortagesbuchungen bereits in Phase 3, obwohl der frühere Planstand diese Funktion auf Phase 4 verschoben hatte; die aktualisierte Phase-3-Planung benennt diese Vorziehung ausdrücklich. [file:1][file:6][file:8] | Niedrig bis mittel; fachlich positiv, aber für historische Abgrenzung relevant. [file:1][file:6] | Als bewusst vorgezogene Erweiterung dokumentieren, nicht als Mangel. [file:1][file:6] | `src/arbeitszeit/application/use_cases/book_time.py`, `tests/application/test_book_time.py` [file:8] | vorgezogene Erweiterung |
| `BookUseCase` erzeugt auch einen `OUTSIDE_SCHEDULE_WINDOW`-Prüffall bereits in Phase 3; die Planung bezeichnet das als nicht ursprünglich explizit vorgesehen, aber tatsächlich implementiert. [file:1][file:8] | Niedrig; kein Fachfehler, aber Phasenabgrenzung wird unschärfer. [file:1] | In Phase-3-Dokumentation explizit als vorgezogene Präzisierung kennzeichnen. [file:1] | `src/arbeitszeit/application/use_cases/book_time.py`, `tests/application/test_book_time.py` [file:8] | vorgezogene Erweiterung |
| Die Rollenprüfung ist in `ManageWorkScheduleUseCase`, `RegisterSupplementUseCase`, `CorrectBookingUseCase`, `ApproveSupplementUseCase` und `RejectSupplementUseCase` bereits implementiert, obwohl `planung_gesamt.md` einen älteren Zwischenstand erwähnt, nach dem diese Nachrüstung erst in Phase 4/Schritt 1c kommen sollte. [file:1][file:6][file:8] | Mittel; ohne Quellenvergleich entsteht ein scheinbarer Widerspruch zwischen Planung und Code. [file:1][file:6] | In der Gesamtplanung einen klaren Hinweis ergänzen, dass diese Autorisierung bereits in Phase 3 vorgezogen und dort verifiziert wurde. [file:1][file:6] | `src/arbeitszeit/application/use_cases/manage_work_schedule.py`, `register_supplement.py`, `correct_booking.py`, `approve_supplement.py`, `reject_supplement.py` [file:8] | Ambiguität / Klärungsbedarf |
| Die Transaktionsregel aus `phase3_planung.md` („Use Case endet mit genau einem `uow.commit()`, der alle Fachobjekte plus AuditLogEntry zusammenfasst“) passt nicht mehr vollständig zum realen Stand, weil die Codebasis nach späterem Erkenntnisgewinn das Muster **commit vor Audit-Log** nutzt, um SQLite-Lock-Probleme mit `auditconn` zu vermeiden. [file:1][file:6][file:8] | Hoch; dies ist eine echte Dokumentationsabweichung an einer kritischen Architekturstelle mit Einfluss auf Fehleranalyse und Folgedesign. [file:1][file:6][file:8] | Phase-3-Dokumentation mit einem Nachtragsvermerk aktualisieren: historischer Plantext vs. realer Endstand nach E2E-/Integrationskorrektur klar trennen. [file:1][file:6][file:8] | alle schreibenden Use Cases, insbesondere `book_time.py`, `approve_supplement.py`; architektonisch auch übrige Application-Use-Cases [file:8] | Dokumentationsfehler |
| Die Planung beschreibt `FakeUnitOfWork.__exit__` als „Rollback bei Exception“; der reale Integrationsstand des echten `SQLiteUnitOfWork` ist strenger und rollt jede noch offene Transaktion beim Verlassen zurück. Das ist in `planung_gesamt.md` später ausdrücklich festgehalten, aber in `phase3_planung.md` noch verkürzt. [file:1][file:6][file:8] | Mittel; kann falsche Erwartungen an Transaktionssemantik und Tests erzeugen. [file:1][file:6] | In der Phase-3-Unterlage deutlich zwischen Fake-Verhalten und realer UoW-Semantik unterscheiden. [file:1][file:6] | `src/arbeitszeit/application/unit_of_work.py`, `tests/application/fakes.py`, angrenzend `src/arbeitszeit/infrastructure/db/unit_of_work.py` [file:8] | Dokumentationsfehler |
| Die Testbasis unter `tests/application/` ist breiter als der originäre Phase-3-Kern, weil auch vorgezogene Phase-4-Use-Cases und zusätzliche Autorisierungs- und Restzeitfälle enthalten sind. [file:1][file:6][file:8] | Mittel; ohne Kennzeichnung wird Testabdeckung historisch falsch zugeordnet. [file:1][file:6] | Testmatrix in Phase 3 in „originär“ und „vorgezogen“ aufteilen. [file:1][file:6] | `tests/application/test_approve_supplement.py`, `test_reject_supplement.py`, Teile von `test_book_time.py` [file:8] | Dokumentationslücke |
| Die Pflichten aus Pflichtenheft und Regelwerk zu echter Buchungserfassung, Plausibilitätsprüfung, Nachträgen, Korrekturen, Rollenabgrenzung und Auditierbarkeit werden in der Application-Schicht erkennbar umgesetzt. [file:7][file:8][file:9] | Niedrig; kein negativer Befund. [file:7][file:9] | Keine Korrektur nötig; nur phasenscharf dokumentieren. [file:7][file:8][file:9] | gesamte Application-Schicht [file:8] | kein Befund |

## Detaillierte Fachbewertung

### 1. Commands, Results, Unit of Work

`src/arbeitszeit/application/commands.py`, `results.py` und `unit_of_work.py` entsprechen dem geplanten Phase-3-Grundgerüst; zusätzlich enthalten `commands.py` und `results.py` bereits die Phase-4-Erweiterungen für Genehmigung und Ablehnung von Nachträgen. Das ist kein Mangel, sondern eine sauber belegte Vorziehung, muss aber historisch ausdrücklich getrennt werden.[file:1][file:6][file:8]

Die Pfadangaben sind zugleich ein Dokumentationsthema: real vorhanden sind `unit_of_work.py` und `use_cases/`, nicht `unitofwork.py` bzw. `usecases/`. Für Folgeaudits sollte ausschließlich diese reale Schreibweise verwendet werden, damit Review, Navigation und spätere Änderungsprotokolle konsistent bleiben.[file:1][file:8]

### 2. BookUseCase

`src/arbeitszeit/application/use_cases/book_time.py` deckt Kartenprüfung, Mitarbeiterprüfung, Sequenzprüfung, Statusermittlung, Compliance-Flag-Erzeugung, Review-Case-Anlage und Auditierung ab und ist damit fachlich klar im Soll. Darüber hinaus enthält der Use Case bereits Ruhezeitprüfung mit Vortageskontext sowie den Regelzeitfenster-Fall `OUTSIDE_SCHEDULE_WINDOW`, was über den älteren ursprünglichen Phase-3-Zuschnitt hinausgeht, aber in den aktuellen Unterlagen bereits als realer Ist-Stand dokumentiert wird.[file:1][file:6][file:8]

Ein echter Dokumentationsbruch liegt bei der Transaktionsbeschreibung: Die Planung spricht noch von `uow.commit()` gemeinsam mit Audit-Log, während der reale spätere Stand wegen SQLite-Locking `commit` vor separatem Audit-Log-Schreiben nutzt. Das ist architektonisch plausibel, muss aber im Phase-3-Audit als nachträgliche Korrektur des ursprünglichen Modells festgehalten werden.[file:1][file:6][file:8]

### 3. RegisterSupplementUseCase

`src/arbeitszeit/application/use_cases/register_supplement.py` erfüllt die fachlichen Anforderungen: Rollenprüfung, Mitarbeiterprüfung, optionaler Bezug auf bestehende Buchung, Anlegen eines `PENDING`-Nachtrags, verpflichtender `MANUAL_ENTRY_REVIEW`-Prüffall und Auditierung. Damit ist der Kern der Nachtragserfassung Phase-3-konform umgesetzt.[file:1][file:7][file:8][file:9]

Weil Rollenprüfung im älteren Gesamtplan teilweise noch als späterer Nachrüstpunkt auftaucht, ist hier keine Codeabweichung, sondern eine Planungsunschärfe festzustellen. Die aktuelle Phase-3-Planung passt bereits zum Code und sollte gegenüber älteren Formulierungen als maßgeblich gelten.[file:1][file:6][file:8]

### 4. CorrectBookingUseCase

`src/arbeitszeit/application/use_cases/correct_booking.py` entspricht dem Sollbild besonders gut: alte und neue Werte werden in einer Korrekturentität festgehalten, die Ursprungsbuchung wird nur auf `CORRECTED` gesetzt, und es werden nur fachlich passende Review Cases geschlossen. Die Planung hebt ausdrücklich hervor, dass `MANUAL_ENTRY_REVIEW` offen bleiben muss; genau diese Selektivität ist laut Codeexport und Tests vorhanden.[file:1][file:6][file:8]

Das ist fachlich wichtig für Nachvollziehbarkeit und Regelwerkskonformität, weil Korrektur und Nachtrag unterschiedliche Prozesse bleiben müssen. Hier liegt deshalb kein Mangel vor, sondern ein gut umgesetzter Kernbestand von Phase 3.[file:7][file:8][file:9]

### 5. ManageWorkScheduleUseCase

`src/arbeitszeit/application/use_cases/manage_work_schedule.py` bildet den geplanten Ablauf ab: ADMIN-Prüfung, Ermittlung wirksamer Version, Konflikt- und Rückwärtsprüfung, Schließen der alten Version, Anlegen der neuen Version, Auditierung und Commit. Auch die Scope-Lokalität global vs. mitarbeiterbezogen ist laut Planung und Testlage ausdrücklich berücksichtigt.[file:1][file:6][file:8]

Kein Mangel ist erkennbar; zu bereinigen ist hier vor allem die Dokumentation historischer Phasenzuordnung der Rollenprüfung. Der Code ist weiter als der ältere Plantext, aber nicht fachlich widersprüchlich.[file:1][file:6][file:8]

### 6. Approve/RejectSupplementUseCase

`src/arbeitszeit/application/use_cases/approve_supplement.py` und `reject_supplement.py` sind in der realen Codebasis vorhanden, getestet und laut aktueller Phase-3-Planung bewusst als Phase-4-Funktionalität bereits vorimplementiert. Sie dürfen deshalb bei der Antwort auf „Ist Phase 3 vollständig?“ nicht als zwingender originärer Kernbestand gewertet werden, wohl aber als dokumentierter Mehrumfang.[file:1][file:6][file:8]

Auch hier ist der größte Punkt nicht der Code, sondern die saubere Kennzeichnung: Ohne explizite Phasenmarkierung wirkt die Codebasis größer als der ursprüngliche Lieferumfang. Für Abnahme und Historisierung sollte deshalb klar zwischen „Phase 3 abgeschlossen“ und „Phase 4 teilweise vorgezogen“ unterschieden werden.[file:1][file:6][file:8]

### 7. Tests

`tests/application/` ist insgesamt stark ausgebaut und deckt Kern- und Erweiterungsfälle umfassend ab. Für die historische Phasenbewertung muss aber zwischen originären Phase-3-Tests und vorgezogenen Phase-4-Tests unterschieden werden, insbesondere bei `test_approve_supplement.py`, `test_reject_supplement.py` und den bereits enthaltenen Ruhezeitfällen in `test_book_time.py`.[file:1][file:6][file:8]

Die Testbasis ist damit **fachlich stark**, aber **dokumentarisch nicht phasenscharf genug ausgewiesen**. Das ist kein Ausführungsfehler, sondern Bereinigungsbedarf in der Projekt- und Reviewdokumentation.[file:1][file:6][file:8]

## A. Förmliches Review-Protokoll

| Befund | Kategorie | Risiko | Empfehlung | betroffene Datei / betroffener Bereich | Priorität |
|---|---|---|---|---|---|
| Originärer Phase-3-Kern ist implementiert und testseitig abgedeckt. [file:1][file:6][file:8] | kein Befund | Niedrig. [file:1][file:6] | Als historisch erfüllt festhalten. [file:1][file:6] | Application-Kernmodule und Kern-Tests [file:8] | niedrig |
| `approve_supplement.py` und `reject_supplement.py` samt Tests sind vorgezogene Phase-4-Bestandteile. [file:1][file:6][file:8] | vorgezogene Erweiterung | Mittel; falsche Phasenzuordnung möglich. [file:1][file:6] | In allen Übersichten explizit als vorgezogen markieren. [file:1][file:6] | `src/arbeitszeit/application/use_cases/approve_supplement.py`, `reject_supplement.py`, `tests/application/test_approve_supplement.py`, `test_reject_supplement.py` [file:8] | hoch |
| Ruhezeitprüfung und Regelzeitfensterprüfung sind in `book_time.py` bereits real vorhanden, obwohl der ältere Planstand dies teils später verortete. [file:1][file:6][file:8] | vorgezogene Erweiterung | Mittel; historische Bewertung wird unscharf. [file:1][file:6] | Als dokumentierte Vorziehung ausweisen, nicht zurückbauen. [file:1][file:6] | `src/arbeitszeit/application/use_cases/book_time.py`, `tests/application/test_book_time.py` [file:8] | mittel |
| Plantext zur Transaktionsregel ist gegenüber dem realen Endstand überholt, weil das Audit-Log wegen `auditconn` nach dem Commit geschrieben wird. [file:1][file:6][file:8] | Dokumentationsfehler | Hoch; Architekturverständnis und Fehlersuche können sonst in die falsche Richtung laufen. [file:1][file:6][file:8] | Phase-3-Planung um Nachtragsvermerk ergänzen und historischen Plantext vom heutigen Endstand trennen. [file:1][file:6][file:8] | alle schreibenden Use Cases, Transaktionsbeschreibung Phase 3 [file:8] | kritisch |
| Reale Pfade und Dateinamen weichen von älteren/normalisierten Referenzen ab. [file:1][file:8] | Dokumentationsfehler | Mittel; Reviewfehler und falsche Dateiverweise. [file:1][file:8] | Nur noch reale Pfade in allen Audit- und Planvorlagen verwenden. [file:1][file:8] | gesamte Pfadreferenzierung | hoch |
| Rollenprüfung ist im Code bereits früher umgesetzt als in Teilen der Gesamtplanung beschrieben. [file:1][file:6][file:8] | Ambiguität / Klärungsbedarf | Mittel; erzeugt scheinbaren Widerspruch zwischen Plan und Ist. [file:1][file:6] | Gesamtplanung mit klarer Historisierungsnotiz aktualisieren. [file:1][file:6] | mehrere Use Cases | mittel |
| Testbasis ist umfassend, aber nicht klar nach originärem Phase-3-Anteil und vorgezogenen Erweiterungen getrennt dokumentiert. [file:1][file:6][file:8] | Dokumentationslücke | Mittel; erschwert Auditierbarkeit und Abnahmehistorie. [file:1][file:6] | Testmatrix je Phase ergänzen. [file:1][file:6] | `tests/application/` [file:8] | hoch |

## B. Priorisierte To-do-Liste

- **P1**: Phase-3-Dokumentation zur Transaktionsregel korrigieren; in `phase3_planung.md` und ergänzend in `planung_gesamt.md` klarstellen, dass der heutige Endstand `uow.commit()` vor dem Schreiben über `auditconn` nutzt; Zielzustand: historische Planannahme und realer korrigierter Endstand sind explizit getrennt dokumentiert.[file:1][file:6][file:8]
- **P1**: Alle Audit- und Planreferenzen auf reale Dateinamen umstellen; betroffen sind insbesondere Pfadangaben zu `unit_of_work.py`, `use_cases/`, `book_time.py`, `approve_supplement.py`, `reject_supplement.py`, `audit_events.py`, `booking_rules.py`, `compliance_checks.py`; Zielzustand: keine Reviewvorlage verweist mehr auf nicht reale Pfade der aktuellen Codebasis.[file:1][file:8]
- **P2**: Phase-3-Unterlagen um eine saubere Abgrenzung „originärer Kernbestand“ vs. „in Phase 3 vorgezogene Phase-4-Inhalte“ ergänzen; betroffen sind `phase3_planung.md` und `planung_gesamt.md`; Zielzustand: `approve_supplement.py`, `reject_supplement.py`, Ruhezeitprüfung und Regelzeitfensterprüfung sind eindeutig klassifiziert.[file:1][file:6][file:8]
- **P2**: Rollenprüfungs-Historie bereinigen; in `planung_gesamt.md` den älteren Nachrüstverweis so kommentieren, dass der reale Stand „bereits in Phase 3 implementiert“ nicht mehr widersprüchlich wirkt; Zielzustand: kein Leser interpretiert die Autorisierungslage mehr als offenen Punkt von Phase 4.[file:1][file:6][file:8]
- **P3**: Testmatrix für `tests/application/` ergänzen; Zielzustand: pro Testdatei ist erkennbar, ob sie originär Phase 3 oder vorgezogener späterer Umfang ist.[file:1][file:6][file:8]

## C. Förmliches Umsetzungsprotokoll

### Arbeitspaket 1 — Transaktionsdokumentation bereinigen

- **Priorität:** kritisch.[file:1][file:6][file:8]
- **Umfang:** `phase3_planung.md`, `planung_gesamt.md`.[file:1][file:6]
- **Maßnahme:** Abschnitt zur Transaktionsregel und zum Audit-Log um historischen Planstand plus heutigen korrigierten Endstand ergänzen; explizit dokumentieren, dass `auditconn` wegen SQLite-Locking ein Commit vor dem Audit-Write erfordert.[file:1][file:6][file:8]
- **Akzeptanzkriterien:** Die Dokumentation enthält keinen Satz mehr, der behauptet, alle Fachobjekte **und** AuditLogEntry würden immer gemeinsam in einem einzigen Commit der Haupttransaktion landen, ohne die spätere Architekturkorrektur zu erwähnen.[file:1][file:6][file:8]
- **Erforderliche Testfälle:** Kein neuer Code-Test zwingend; Dokumentationsabgleich gegen `tests/integration/test_unit_of_work.py` und gegen die realen Use-Case-Dateien reicht aus.[file:6][file:8]
- **Anpassungsart:** Dokumentation.[file:1][file:6]

### Arbeitspaket 2 — Phasenabgrenzung Phase 3 vs. Phase 4 schärfen

- **Priorität:** hoch.[file:1][file:6]
- **Umfang:** `phase3_planung.md`, `planung_gesamt.md`.[file:1][file:6]
- **Maßnahme:** Tabelle ergänzen, die originären Phase-3-Umfang, in Phase 3 vorgezogene Erweiterungen und explizit spätere Phase-4-Inhalte trennt.[file:1][file:6]
- **Akzeptanzkriterien:** `approve_supplement.py`, `reject_supplement.py`, `test_approve_supplement.py`, `test_reject_supplement.py`, Ruhezeitprüfung in `book_time.py` und Regelzeitfensterprüfung sind jeweils eindeutig klassifiziert.[file:1][file:6][file:8]
- **Erforderliche Testfälle:** Dokumentationsprüfung gegen `arbeitszeit.md`; keine Codeänderung erforderlich.[file:8]
- **Anpassungsart:** Dokumentation.[file:1][file:6]

### Arbeitspaket 3 — Pfad- und Modulreferenzen vereinheitlichen

- **Priorität:** hoch.[file:1][file:8]
- **Umfang:** alle Review- und Planunterlagen mit Application-Bezug.[file:1][file:6]
- **Maßnahme:** historische oder normalisierte Bezeichnungen nur noch in Klammern nennen; primär immer reale Exportpfade aus `arbeitszeit.md` verwenden, etwa `src/arbeitszeit/application/use_cases/book_time.py` statt `src/arbeitszeit/application/usecases/booktime.py`.[file:1][file:8]
- **Akzeptanzkriterien:** Kein Verweis in den Unterlagen zeigt mehr auf einen nicht vorhandenen Pfad der aktuellen Codebasis.[file:8]
- **Erforderliche Testfälle:** manueller Link-/Pfadabgleich gegen den Verzeichnisbaum in `arbeitszeit.md`.[file:8]
- **Anpassungsart:** Dokumentation.[file:1][file:6][file:8]

### Arbeitspaket 4 — Testinventar historisieren

- **Priorität:** mittel.[file:1][file:6]
- **Umfang:** `phase3_planung.md`, optional ergänzende Review-Matrix.[file:1]
- **Maßnahme:** `tests/application/` in Kern-Phase-3-Tests und vorgezogene Erweiterungstests aufspalten; soweit sinnvoll Testfälle mit fachlicher Herkunft markieren.[file:1][file:6][file:8]
- **Akzeptanzkriterien:** Bei jeder Testdatei ist nachvollziehbar, ob sie den originären Phase-3-Abschluss belegt oder bereits spätere Erweiterungen absichert.[file:1][file:6][file:8]
- **Erforderliche Testfälle:** keine neuen Code-Tests; Inventarprüfung genügt.[file:8]
- **Anpassungsart:** Dokumentation.[file:1][file:6]

## Abschlussbewertung

Eine vollständige Analyse von Phase 3 ist auf Basis der vorliegenden Unterlagen möglich, weil Sollbild, Gesamtplanung, Fachanforderungen und realer Codeexport zusammen eine belastbare Prüfbasis ergeben. Für die fachliche Sauberkeit ist die Unterteilung nach Commands/Results/UoW, einzelnen Use Cases und Testbestand dennoch sinnvoller, weil genau dort die Unterschiede zwischen originärem Phase-3-Kern, vorgezogenen Erweiterungen und später nachgezogener Dokumentationskorrektur sichtbar werden.[file:1][file:6][file:7][file:8][file:9]

Historisch ist Phase 3 **im Kern abgeschlossen**. Die heutige Codebasis ist mit der Phase-3-Planung **weitgehend konsistent**, aber nicht in jeder Formulierung dokumentationsscharf, weil spätere Erkenntnisse zur Transaktionsarchitektur sowie vorgezogene Inhalte aus Phase 4 nicht überall sauber genug nachgetragen wurden.[file:1][file:6][file:8]

Der wesentliche Bereinigungsbedarf liegt daher **nicht primär im Code**, sondern in der Dokumentation: reale Pfade vereinheitlichen, vorgezogene Erweiterungen explizit kennzeichnen, Transaktionsregel historisch korrekt nachziehen und Testabdeckung phasenscharf ausweisen. Danach wäre Phase 3 nicht nur technisch, sondern auch revisionsfähig dokumentiert.[file:1][file:6][file:8]
