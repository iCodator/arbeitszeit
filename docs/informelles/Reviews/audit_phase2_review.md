# Audit Phase 2 – Domain-Schicht: Soll-/Ist-Prüfung

Die Phase 2 ist **als Ganzes in einem Durchgang belastbar prüfbar**, weil die Prüfbasis den vollständigen Domain-Plan (`phase2_planung.md`), die phasenübergreifende Einordnung (`planung_gesamt.md`) und den exportierten Ist-Stand (`arbeitszeit.md`) gemeinsam abdeckt. Eine Unterteilung in Teilbereiche ist methodisch dennoch sauberer für die Darstellung, weil Enums, Fehler, Entities, Services, Ports und Domain-Tests unterschiedliche Reifegrade, Abweichungstypen und Phasengrenzen haben. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md) (Quelle: arbeitszeit.md)

Fachlich ist das Ergebnis insgesamt positiv: **Phase 2 ist im Kern vollständig und weitgehend planungskonform umgesetzt**, aber nicht in jedem Detail exakt wie ursprünglich geplant. Mehrere Punkte sind bewusst weiterentwickelt oder präzisiert worden, insbesondere die Orthogonalisierung von Booking-Status vs. ReviewCase-Typen, zusätzliche Invarianten in Entities, der erweiterte Audit-Event-Katalog und der gewachsene Testumfang. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md) (Quelle: arbeitszeit.md)

## 1. Sollbild Phase 2

Das verbindliche Sollbild für Phase 2 ist ein **vollständiges, infrastrukturfreies Domänenmodell** mit Enums, Fehlerklassen, Entities, Businessregeln, Compliance-Prüfungen und Repository-Protokollen; Datenbankzugriff, Use-Cases und Integrationslogik gehören ausdrücklich noch nicht dazu. Reale Zielpfade laut Planung sind `src/arbeitszeit/domain/__init__.py`, `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/domain/errors.py`, `src/arbeitszeit/domain/entities.py`, `src/arbeitszeit/domain/auditevents.py`, `src/arbeitszeit/domain/services/bookingrules.py`, `src/arbeitszeit/domain/services/compliancechecks.py`, `src/arbeitszeit/domain/ports/__init__.py`, `src/arbeitszeit/domain/ports/repositories.py` sowie die Domain-Tests unter `tests/domain/`. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md)

Zum Soll gehören 11 `StrEnum`-Klassen, eine DomainError-Basisklasse mit 9 Subklassen, 9 `dataclass(frozen=True, slots=True)`-Entities mit Invarianten, die Services `validatebookingsequence()`, `checkbreakcompliance()`, `checkmaxhours()` und `checkrestperiod()` sowie 10 Repository-Ports auf `typing.Protocol`-Basis. Für die Tests nennen die Planungsunterlagen die Dateien `tests/domain/testentities.py`, `tests/domain/testbookingrules.py`, `tests/domain/testcompliancechecks.py` und als später ergänzten, aber heute vorhandenen Zusatz `tests/domain/testauditevents.py`. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md)

## 2. Istbild Phase 2

`arbeitszeit.md` zeigt die Domain-Paketstruktur in der realen Codebasis mit `src/arbeitszeit/domain/…`, einem `services`-Unterpaket, einem `ports`-Unterpaket und den Testmodulen unter `tests/domain/`. Zudem sind in den exportierten Inhalten Domain-Entities, Domain-Errors, `auditevents`, die Services und die Domain-Tests tatsächlich enthalten. (Quelle: arbeitszeit.md)

Der Ist-Stand ist allerdings nicht mehr rein „historischer Phase-2-Stand“, sondern ein heute weitergewachsener Gesamtstand desselben Domänenkerns. Das betrifft vor allem zusätzliche oder präzisierte Invarianten, erweiterte Testtiefe, einen gewachsenen Audit-Event-Katalog sowie spätere Integrationsannahmen, die in den Planunterlagen schon eingeordnet, aber erst in Phase 3/4 operationalisiert werden. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md) (Quelle: arbeitszeit.md)

## 3. Förmliches Review-Protokoll

| Befund | Kategorie | Risiko | Empfehlung | betroffene Datei / betroffener Bereich | Priorität |
|---|---|---|---|---|---|
| Phase 2 ist als Domain-Kern vollständig geplant und im exportierten Ist-Stand mit Enums, Fehlern, Entities, Services, Ports und Domain-Tests vorhanden. | kein Befund | Niedrig; Folgephasen können auf dem Domänenkern aufsetzen. | Keine funktionale Korrektur nötig; Status in der Doku beibehalten. | Gesamtbereich `src/arbeitszeit/domain/`, `tests/domain/` | P3 |
| Die reale Paketstruktur `src/arbeitszeit/domain/`, `src/arbeitszeit/domain/services/`, `src/arbeitszeit/domain/ports/` und `tests/domain/` ist laut Planung konsistent mit dem Stand in `arbeitszeit.md`. | kein Befund | Niedrig; keine Strukturabbrüche zwischen Plan und Codeexport. | Reale Pfade in weiteren Audits unverändert verwenden. | Domain-Paketstruktur | P3 |
| `src/arbeitszeit/domain/enums.py` enthält laut Planung und Gesamtplan 11 `StrEnum`-Klassen; diese Zählung ist im Istbild konsistent dokumentiert. | kein Befund | Niedrig; zentrale Typbasis stabil. | Keine Änderung erforderlich. | `src/arbeitszeit/domain/enums.py` | P3 |
| `BookingStatus` wurde gegenüber älteren Planannahmen bewusst bereinigt und enthält final nur `OPEN`, `OK`, `WARN`, `NEEDSREVIEW`, `CORRECTED`, `CLOSEDWITHNOTE`; `POSSIBLE*` und `MANUALENTRY` sind ausdrücklich keine Statuswerte mehr. | vorgezogene Erweiterung | Niedrig fachlich, mittel dokumentarisch; Missverständnisse entstehen nur bei Lesern mit altem Planstand. | Diese Architekturentscheidung in allen Phase-2- und Phase-3-Dokumenten noch prominenter als finale Abweichung zum Ursprungsplan markieren. | `src/arbeitszeit/domain/enums.py`, Phase-2-Doku | P2 |
| `ReviewCaseType` ist gegenüber dem Ursprungsplan deutlich erweitert und nutzt finale Bezeichner wie `POSSIBLEBREAKVIOLATION` und `POSSIBLERESTVIOLATION` statt älterer Namen wie `BREAKCOMPLIANCEISSUE` bzw. `RESTPERIODVIOLATION`. | Planabweichung | Mittel; fachlich sinnvoll, aber bei historischer Rückverfolgung erklärungsbedürftig. | Historische Namensänderungen in einer Mapping-Tabelle dokumentieren. | `src/arbeitszeit/domain/enums.py`, `phase2_planung.md` | P2 |
| `CardStatus` enthält mit `REPLACED` einen zusätzlichen Wert gegenüber dem früheren Plan. | vorgezogene Erweiterung | Niedrig; fachlich plausibel, keine erkennbare Inkonsistenz. | Als bewusste Finalisierung statt stiller Abweichung dokumentieren. | `src/arbeitszeit/domain/enums.py` | P3 |
| `BookingSource` nutzt final `IMPORT` statt `SYSTEM`. | Planabweichung | Mittel; semantisch klein, aber für spätere Berichte und Repos relevant. | In der Dokumentation den ersetzten Altbezeichner ausdrücklich nennen. | `src/arbeitszeit/domain/enums.py`, `planung_gesamt.md` | P2 |
| `src/arbeitszeit/domain/errors.py` ist fachlich vollständig: `DomainError` plus 9 Subklassen sind laut Planung vorhanden. | kein Befund | Niedrig; Fehlersemantik ist tragfähig. | Keine Änderung erforderlich. | `src/arbeitszeit/domain/errors.py` | P3 |
| Die Fehlerklassen enthalten zusätzlich ein `code`-Attribut und `context`-Dict; das ist in der Planung als finaler Stand beschrieben, aber über den Minimal-Ursprungsplan hinaus präzisiert. | vorgezogene Erweiterung | Niedrig bis mittel; keine funktionale Gefahr, aber höherer API-Verbindlichkeitsgrad. | Diese Erweiterung in der Doku als stabilisierte Fehlerkonvention ausweisen. | `src/arbeitszeit/domain/errors.py` | P3 |
| `src/arbeitszeit/domain/entities.py` ist im Umfang vollständig: 9 Entities sind vorhanden und als `frozen`/`slots`-Dataclasses mit `__post_init__`-Invarianten dokumentiert. | kein Befund | Niedrig; Domain-Modell ist vollständig abgebildet. | Keine Änderung erforderlich. | `src/arbeitszeit/domain/entities.py` | P3 |
| Mehrere Entity-Invarianten gehen über frühere Planstände hinaus, etwa leere `personnelno`/`username`-Werte, `ReviewCase.note` bei `CLOSEDWITHNOTE`, zeitliche Plausibilität in `Supplement` und `BookingCorrection`. | erweiterte Umsetzung | Niedrig fachlich, positiv für Robustheit; nur Dokumentationsnachführung nötig. | Diese Zusatzinvarianten in einer Phase-2-Abweichungsliste explizit sammeln. | `src/arbeitszeit/domain/entities.py`, `tests/domain/testentities.py` | P2 |
| Bei `TimeBooking` ist keine zusätzliche Invariante auf Entity-Ebene definiert; laut Planung ist das bewusst, weil der Status im Use Case gesetzt wird. | kein Befund | Niedrig; Schichtenabgrenzung ist korrekt. | So belassen und in Reviews nicht als Lücke missverstehen. | `src/arbeitszeit/domain/entities.py` | P3 |
| `ReviewCase` verwendet im Plantext teils `detectedat`, im Codeexport taucht in Testbeispielen auch `createdat`-nahe Formulierungsreste auf; die exportierte Darstellung ist hier nicht durchgehend sauber lesbar. | Ambiguität/Klärungsbedarf | Mittel; Gefahr falscher Feldbenennung in Folgedokumenten oder Testbeschreibungen. | Feldnamen gegen den realen Entity-Code in `arbeitszeit.md` gezielt nachziehen und in der Dokumentation einheitlich als reale Schreibweise führen. | `src/arbeitszeit/domain/entities.py`, `tests/domain/testentities.py`, `arbeitszeit.md` | P1 |
| `src/arbeitszeit/domain/auditevents.py` ist laut Phase-2-Plan eine sinnvolle Ergänzung, war aber im Ursprungsplan noch nicht vorgesehen. | vorgezogene Erweiterung | Niedrig; reduziert String-Literale und verbessert Konsistenz. | Als bewusste Qualitätsverbesserung beibehalten. | `src/arbeitszeit/domain/auditevents.py` | P3 |
| Der Audit-Event-Katalog enthält nicht nur Domänenereignisse, sondern auch spätere Betriebs-/Backup-Ereignisse wie `BACKUPCREATED`, `BACKUPSYNCEDTONAS`, `BACKUPSYNCFAILED`, `RESTORECOMPLETED`. | vorgezogene Erweiterung | Mittel für Phasentrennung; der Katalog ist nützlich, aber nicht mehr rein originärer Phase-2-Bestand. | Im Audit- und Plantext trennen zwischen originärem Domain-Katalog und später ergänzten Infrastruktur-Ereignissen. | `src/arbeitszeit/domain/auditevents.py`, `tests/domain/testauditevents.py` | P2 |
| `src/arbeitszeit/domain/services/bookingrules.py` ist fachlich vorhanden und erfüllt die geplante Sequenzprüfung inkl. `InvalidBookingSequenceError` und `OpenPhaseConflictError`. | kein Befund | Niedrig; zentrale Buchungslogik vorhanden. | Keine funktionale Änderung nötig. | `src/arbeitszeit/domain/services/bookingrules.py` | P3 |
| `ValidationResult` ist als Dataclass dokumentiert, obwohl spätere Application-Use-Cases teils direkt Exceptions nutzen und die Statusbewertung außerhalb von `ValidationResult` fortführen; die Rolle dieses Rückgabetyps wirkt im heutigen Gesamtstand weniger zentral als der frühe Plan vermuten lässt. | Ambiguität/Klärungsbedarf | Mittel; API könnte missverständlich oder teilgenutzt wirken. | Prüfen und dokumentieren, ob `ValidationResult` bewusst Teil der stabilen Domain-API bleibt oder historisches Restmodell ist. | `src/arbeitszeit/domain/services/bookingrules.py` | P2 |
| `src/arbeitszeit/domain/services/compliancechecks.py` ist inhaltlich vollständig vorhanden und deckt `checkbreakcompliance`, `checkmaxhours` und `checkrestperiod` ab. | kein Befund | Niedrig; fachliche Pflichtprüfungen sind modelliert. | Keine funktionale Änderung erforderlich. | `src/arbeitszeit/domain/services/compliancechecks.py` | P3 |
| Die Planung fordert ausdrücklich, dass Ruhezeitprüfung in Phase 2 als Domänenfunktion vollständig sein darf, ihre Integration in den Buchungsfluss aber erst später erfolgt; dieser Phasenschnitt ist dokumentarisch sauber. | kein Befund | Niedrig; klare Abgrenzung zur Application-/Infrastructure-Schicht. | Diese Abgrenzung in Folgeaudits beibehalten. | `src/arbeitszeit/domain/services/compliancechecks.py`, Phasegrenze 2→4 | P3 |
| Die Signatur von `checkrestperiod()` wurde final auf zwei `datetime`-Werte (`lastgo`, `nextcome`) präzisiert und weicht damit vom früheren Listen-/Buchungsmodell ab. | Planabweichung | Mittel; API-Änderung ist sachlich sinnvoll, muss aber explizit historisiert bleiben. | Die finale Signatur in allen Architekturtexten und Beispielen vereinheitlichen. | `src/arbeitszeit/domain/services/compliancechecks.py`, `phase2_planung.md` | P2 |
| Die orthogonale Modellierung `BookingStatus` vs. `ReviewCaseType` vs. `BookingSource` ist in den Planungsunterlagen klar beschrieben und fachlich stark; sie ist ein positiver Ausbau gegenüber früheren Mischvorstellungen. | kein Befund | Niedrig; verbessert spätere Berichtsfähigkeit. | Unverändert beibehalten und weiterhin zentral dokumentieren. | `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/domain/services/compliancechecks.py` | P3 |
| `src/arbeitszeit/domain/ports/repositories.py` enthält laut Planung 10 `Protocol`-Interfaces; Umfang und Schnitt sind im Istbild konsistent dokumentiert. | kein Befund | Niedrig; Schnittstellenbasis für Phase 3/4 ist vollständig. | Keine Änderung erforderlich. | `src/arbeitszeit/domain/ports/repositories.py` | P3 |
| Der Port `SystemConfigRepository.setcurrent(...)` ist bereits im Domänenvertrag enthalten, obwohl die operative Nutzung laut Gesamtplanung erst später erfolgt. | vorgezogene Erweiterung | Niedrig; fachlich sinnvoll vorbereitet, kein Schaden. | Als vorbereitende Domänenschnittstelle für spätere Phasen kennzeichnen. | `src/arbeitszeit/domain/ports/repositories.py` | P3 |
| Die Domain-Tests unter `tests/domain/` sind vorhanden und namentlich konsistent mit der realen Zielstruktur `testentities.py`, `testbookingrules.py`, `testcompliancechecks.py`, `testauditevents.py`. | kein Befund | Niedrig; Testpfade sind konsistent. | Keine Änderung erforderlich. | `tests/domain/` | P3 |
| Der Testumfang ist deutlich über Plan gewachsen: 63 Tests statt historisch 38–44, darunter 42 Entity-Tests statt 19 und 2 Audit-Event-Tests zusätzlich. | erweiterte Umsetzung | Niedrig fachlich, positiv für Stabilität; nur Dokumentationspflege nötig. | In der Doku den Unterschied „Planstand“ vs. „heutige Testtiefe“ explizit tabellarisch ausweisen. | `tests/domain/testentities.py`, `tests/domain/testbookingrules.py`, `tests/domain/testcompliancechecks.py`, `tests/domain/testauditevents.py` | P2 |
| `tests/domain/testauditevents.py` ist heute Bestandteil des Domain-Testpakets, war aber laut Phase-2-Plan ursprünglich nicht vorgesehen. | vorgezogene Erweiterung | Niedrig; Testgewinn ohne fachliches Risiko. | Als nachträglich sinnvoll ergänzte Tests kennzeichnen. | `tests/domain/testauditevents.py` | P3 |
| `tests/domain/testentities.py` testet zusätzliche zeitliche Plausibilitäten für Supplements und BookingCorrections; das spricht für gute Domänenhärte, aber die Planung sollte diese gewachsene Tiefe expliziter widerspiegeln. | Dokumentationslücke | Niedrig bis mittel; Wartung profitiert von klarer Erwartungslage. | Die zusätzlichen Invarianten und Testfälle in `phase2_planung.md` nachtragen. | `tests/domain/testentities.py`, `phase2_planung.md` | P2 |
| Die Abgrenzung zu späteren Phasen ist insgesamt sauber: keine DB-Implementierungen in Phase 2, keine Use-Cases, keine Rollenprüfung und keine Integrationsnachweise werden fälschlich als originäre Phase-2-Bestandteile ausgegeben. | kein Befund | Niedrig; Phasenschnitt nachvollziehbar. | Keine Änderung erforderlich. | Phasegrenze 2→3/4 | P3 |
| Gleichzeitig enthalten die Planungsunterlagen bereits Querverweise auf spätere Integrationspflichten wie `reportqueries.py`, Ruhezeitintegration in Phase 4 und Rollenprüfung in Phase 3/4; das ist inhaltlich hilfreich, kann aber bei oberflächlicher Lektüre Phase-2-Umfang und Gesamtsystem vermischen. | Dokumentationslücke | Mittel; Leser könnten Phase 2 zu breit interpretieren. | Einen festen Abschnitt „Nicht Teil von Phase 2“ in `phase2_planung.md` optisch deutlicher ausbauen. | `phase2_planung.md`, `planung_gesamt.md` | P2 |

## 4. Priorisierte To-do-Liste

### P1 – sofort korrigieren

1. **Feldnamen in `ReviewCase`-Dokumentation und Testbeschreibung vereinheitlichen**; betroffene Dateien: `phase2_planung.md`, `arbeitszeit.md`, ggf. referenzierende Stellen in `planung_gesamt.md`; Zielzustand: reale Feldnamen und reale Signaturen sind überall identisch dokumentiert, ohne Mischformen wie `detectedat`/`createdat` in demselben fachlichen Kontext.
2. **Reale API von `checkrestperiod()` überall nachziehen**; betroffene Dateien: `phase2_planung.md`, `planung_gesamt.md`; Zielzustand: überall dieselbe finale Signatur auf Basis von `lastgo` und `nextcome`, keine veralteten Beschreibungen mit Listen-/Buchungsübergabe.

### P2 – zeitnah korrigieren

3. **Historische Enum-Umbenennungen dokumentieren**; betroffene Dateien: `phase2_planung.md`, `planung_gesamt.md`; Zielzustand: Mapping Altname → finaler Name für `BREAKCOMPLIANCEISSUE`/`POSSIBLEBREAKVIOLATION`, `RESTPERIODVIOLATION`/`POSSIBLERESTVIOLATION`, `SYSTEM`/`IMPORT`.
4. **Zusätzliche Entity-Invarianten explizit in Phase-2-Doku aufnehmen**; betroffene Dateien: `phase2_planung.md`; Zielzustand: leere Strings, Note-Pflicht bei `CLOSEDWITHNOTE`, zeitliche Plausibilitäten und ähnliche Nachschärfungen sind als finaler Stand dokumentiert.
5. **Originären vs. später gewachsenen Audit-Event-Katalog trennen**; betroffene Dateien: `phase2_planung.md`, `planung_gesamt.md`; Zielzustand: klar erkennbar, welche `auditevents` originär domänennah waren und welche erst durch spätere Infrastruktur-/Backup-Funktionen dazukamen.
6. **Gewachsene Domain-Testtiefe transparent machen**; betroffene Dateien: `phase2_planung.md`, `planung_gesamt.md`; Zielzustand: tabellarische Gegenüberstellung Planstand vs. heutiger Testbestand je Modul.
7. **Rolle von `ValidationResult` klären**; betroffene Dateien: `phase2_planung.md`, `src/arbeitszeit/domain/services/bookingrules.py` als referenzierter Bereich; Zielzustand: dokumentiert, ob `ValidationResult` Teil der stabilen öffentlichen Domain-API oder nur internes/teilgenutztes Modell ist.
8. **Abschnitt „Nicht Teil von Phase 2“ schärfen**; betroffene Dateien: `phase2_planung.md`; Zielzustand: klare Negativabgrenzung zu Repository-Implementierungen, Application-Use-Cases, Rollenprüfung, Report-Ableitung und Integrationsbeweisen.

### P3 – optional / dokumentarisch bereinigen

9. **CardStatus- und Error-Kontext-Erweiterungen als bewusste Finalisierung markieren**; betroffene Dateien: `phase2_planung.md`; Zielzustand: keine implizit „schleichenden“ API-Erweiterungen mehr, sondern sauber dokumentierte Finalversion.
10. **Reale Pfade der Domain-Testmodule in Folgeaudits unverändert normieren**; betroffene Dateien: spätere Auditdokumente; Zielzustand: konsistente Referenzen auf `tests/domain/testentities.py`, `tests/domain/testbookingrules.py`, `tests/domain/testcompliancechecks.py`, `tests/domain/testauditevents.py`.

## 5. Förmliches Umsetzungsprotokoll

### Arbeitspaket 1 – Dokumentationskonsistenz der Domain-API bereinigen

**Reihenfolge / Priorität:** zuerst, P1.

**Umsetzung:**
- `phase2_planung.md` und `planung_gesamt.md` auf finale Feld- und Signaturbezeichnungen prüfen.
- `ReviewCase`-Felder und `checkrestperiod()`-API an allen Stellen auf reale Benennung des heutigen Codes angleichen.
- Mischformen aus historischen und finalen Bezeichnern entfernen oder explizit als Historie markieren.

**Akzeptanzkriterien:**
- Kein Abschnitt nennt denselben Domänenbestandteil mit widersprüchlichen Feld- oder Parameternamen.
- Die Doku kann direkt als Referenz für Implementierung und Tests verwendet werden.

**Erforderliche Testfälle:**
- Redaktionsprüfung aller Erwähnungen von `ReviewCase` und `checkrestperiod()` in `phase2_planung.md` und `planung_gesamt.md`.
- Stichprobenabgleich gegen den exportierten Stand in `arbeitszeit.md`.

### Arbeitspaket 2 – Historische Planabweichungen transparent machen

**Reihenfolge / Priorität:** nach Arbeitspaket 1, P2.

**Umsetzung:**
- Eine Abschnittstabelle „Ursprungsplan vs. finaler Phase-2-Stand“ ergänzen.
- Darin mindestens aufnehmen: `BookingStatus`-Bereinigung, `ReviewCaseType`-Umbenennungen, `BookingSource IMPORT`, `CardStatus.REPLACED`, zusätzliche Entity-Invarianten, `auditevents.py`.
- Jeder Punkt erhält die Markierung „bewusste Finalisierung“, „spätere Ergänzung“ oder „Abweichung mit Klärungsbedarf“.

**Akzeptanzkriterien:**
- Ein Leser kann ohne Rückgriff auf ältere Prompts erkennen, welche Änderungen absichtlich gegenüber dem frühen Plan entstanden sind.
- Keine sinnvolle Finalisierung wirkt mehr wie ein versehentlicher Bruch.

**Erforderliche Testfälle:**
- Dokumentationsreview der Mapping-Tabelle.
- Vollständigkeitscheck gegen `phase2_planung.md` und `planung_gesamt.md`.

### Arbeitspaket 3 – Testbestand Phase 2 historisieren

**Reihenfolge / Priorität:** P2.

**Umsetzung:**
- Die Domain-Testmodule in `phase2_planung.md` mit Plan- und Ist-Testanzahl dokumentieren.
- Zusätzliche Testtiefe in `tests/domain/testentities.py` und `tests/domain/testauditevents.py` ausdrücklich benennen.
- Den Domain-Testbestand klar von Application-, Integration- und E2E-Tests späterer Phasen abgrenzen.

**Akzeptanzkriterien:**
- Die Testabdeckung von Phase 2 ist quantitativ und qualitativ nachvollziehbar.
- Zusätzliche Tests werden nicht als ungeplante Inkonsistenz, sondern als gewachsene Absicherung dargestellt.

**Erforderliche Testfälle:**
- Zählabgleich der Testmodule gemäß Planangaben.
- Querprüfung, dass keine Tests aus `tests/application/`, `tests/integration/` oder `tests/e2e/` fälschlich in Phase 2 eingerechnet werden.

### Arbeitspaket 4 – Phasengrenze 2 zu 3/4 explizit nachschärfen

**Reihenfolge / Priorität:** P2.

**Umsetzung:**
- In `phase2_planung.md` einen sichtbaren Abschnitt „Nicht Teil von Phase 2“ ausbauen.
- Dort explizit ausschließen: SQLite-Repositories, Unit of Work, Use-Cases, Rollenprüfung, Reportprojektionen, Exporte, Hardware-Anbindung und Integrationsbeweise.
- Bereits vorhandene Querverweise auf spätere Phasen nur noch als Folgephase markieren, nicht als implizite Phase-2-Verpflichtung.

**Akzeptanzkriterien:**
- Die Domäne ist als abgeschlossen, aber nicht als Gesamtsystem missverständlich.
- Folgephasen bleiben logisch anschlussfähig, ohne die Leistungsgrenze von Phase 2 zu verwischen.

**Erforderliche Testfälle:**
- Redaktionsprüfung aller Abschnitte mit Verweisen auf Phase 3/4.
- Audit-Stichprobe: Ein externer Leser muss nach der Lektüre korrekt benennen können, was Phase 2 liefert und was nicht.

## 6. Abschlussbewertung

**1. Ist Phase 2 in der aktuellen Codebasis vollständig bearbeitet?** Ja, im Sinn des Domänenkerns ist Phase 2 vollständig bearbeitet. Enums, Fehlerklassen, Entities, Domain-Services, Repository-Ports und Domain-Tests sind vorhanden und die Phase ist als fachliches Fundament belastbar. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md) (Quelle: arbeitszeit.md)

**2. Stimmt die aktuelle Codebasis in Bezug auf Phase 2 mit der Planung und Implementierungsplanung überein?** Weitgehend ja, aber nicht wortgleich zum frühen Planstand. Mehrere Bereiche wurden bewusst präzisiert oder erweitert, ohne den fachlichen Kern von Phase 2 zu verletzen. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md) (Quelle: arbeitszeit.md)

**3. Gibt es fachliche, strukturelle oder testbezogene Unstimmigkeiten, Lücken, Widersprüche oder Ambiguitäten?** Ja, vor allem dokumentarische: historische vs. finale Enum-Namen, die finale Signatur von `checkrestperiod()`, die gewachsene Rolle von `ValidationResult`, die Abgrenzung des Audit-Event-Katalogs und einzelne Benennungsunschärfen rund um `ReviewCase`. Harte funktionale Mängel der Domain-Schicht sind auf Basis der Unterlagen dagegen nicht erkennbar. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md) (Quelle: arbeitszeit.md)

**4. Welche Punkte sind korrekt umgesetzt, erweitert umgesetzt, abweichend umgesetzt oder klärungsbedürftig?** Korrekt umgesetzt sind Struktur, Grundmodell, Services, Ports und Testbasis. Erweitert umgesetzt sind zusätzliche Invarianten, Audit-Events und tiefere Tests; abweichend bzw. finalisiert umgesetzt sind einzelne Enum-Namen und API-Details; klärungsbedürftig bleiben vor allem Dokumentationskonsistenz und die genaue kommunikative Trennung von historischem Planstand und finalem Phase-2-Stand. (Quelle: phase2_planung.md) (Quelle: planung_gesamt.md) (Quelle: arbeitszeit.md)
