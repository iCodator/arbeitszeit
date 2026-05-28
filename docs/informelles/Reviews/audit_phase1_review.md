# Audit Phase 1 – Abgleich aktuelle Codebasis vs. Planungsunterlagen

Dieses Audit kommt zu dem Ergebnis, dass **Phase 1 historisch im Kern abgeschlossen** ist, weil das Fundament aus Projektgerüst, Verbindungsaufbau, Migrationsrunner, Initialisierungsskript, Seed-Migration und den originären Migrationstests in der heutigen Codebasis nachweisbar vorhanden ist. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md)

Die heutige Codebasis ist zugleich **nur teilweise konsistent als Phase-1-Stand dokumentiert**, weil dieselben Dateien inzwischen deutlich über den originären Lieferumfang hinausgewachsen sind und die Planungsdokumente historische, normalisierte und reale Dateinamen nebeneinander führen, was ohne ausdrückliche Gegenüberstellung missverständlich werden kann. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md)

## 1. Förmliches Review-Protokoll

| Befund | Risiko | Empfehlung | Betroffene Datei |
|---|---|---|---|
| Der originäre Phase-1-Lieferumfang ist in den Planungsunterlagen klar als Fundament aus `pyproject.toml`, `.python-version`, `.gitignore`, `migrations/0001schema.sql`, `migrations/0002seeddefaults.sql`, `src/arbeitszeit/infrastructure/db/connection.py`, `src/arbeitszeit/infrastructure/db/migrations.py`, `scripts/initdb.py` und `tests/testmigrations.py` beschrieben. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Niedrig; der historische Umfang ist fachlich nachvollziehbar. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Diese Liste als verbindliche Phase-1-Referenz in einer kompakten Projektübersicht wiederholen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | `phase1_planung.md`, `planung_gesamt.md` |
| Die reale Codebasis verwendet die Schreibweisen `migrations/0001schema.sql`, `migrations/0002seeddefaults.sql`, `scripts/initdb.py` und `tests/testmigrations.py`; dies ist mit der Prüfvorgabe konsistent, weicht aber von älteren normalisierten Schreibweisen mit Unterstrichen ab. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Mittel; bei Audits und Folgeprompts drohen Fehlreferenzen auf nicht existierende Pfade. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Historische/normalisierte Namen nur noch in Klammern nennen und die realen Pfade stets voranstellen. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | `phase1_planung.md`, `arbeitszeit.md` |
| `pyproject.toml` ist in der Codebasis vorhanden und enthält laut Export das erwartete Paket- und Test-Setup; zugleich sind dort heutige Dev-Abhängigkeiten wie `pypdf` sichtbar, die laut Planung erst später ergänzt wurden. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Niedrig bis mittel; ohne historischen Hinweis könnte man spätere Ergänzungen fälschlich Phase 1 zuschreiben. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | In der Doku explizit zwischen „originär Phase 1“ und „heutiger Stand derselben Datei“ unterscheiden. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | `pyproject.toml`, `phase1_planung.md` |
| `.python-version` und `.gitignore` gehören laut Phase-1-Plan zum Fundament; im bereitgestellten Codeexport sind sie nicht als ausgeschriebene Quellblöcke sichtbar, aber sie sind als Soll-Bestandteile dokumentiert. (Quelle: phase1_planung.md) | Mittel; der Audit-Nachweis ist hier dokumentbasiert, nicht codeblockbasiert. (Quelle: phase1_planung.md) | In `arbeitszeit.md` einen kurzen Dateibaum oder Rohtext dieser Dateien ergänzen, damit der Ist-Nachweis unmittelbarer wird. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | `.python-version`, `.gitignore`, `arbeitszeit.md` |
| `migrations/0001schema.sql` ist historisch Teil von Phase 1, bildet aber laut Planung nicht den heutigen Finalzustand des Schemas ab: ältere Booking-Status-CHECKs sowie das frühere Supplement-Modell wurden später über `0003` und `0004` bereinigt; `deviceeventid` kam erst mit `0005` hinzu. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Mittel; eine rein statische Prüfung von `0001` ohne Migrationskette würde zu Fehlurteilen über den Phase-1-Abschluss führen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Phase-1-Audits immer als Fundament plus historische Einordnung der Folgemigrationen formulieren. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | `migrations/0001schema.sql`, `migrations/0003cleanupbookingstatus.sql`, `migrations/0004supplementrejectfieldsandreviewnote.sql`, `migrations/0005timebookingsdeviceeventid.sql` |
| `migrations/0002seeddefaults.sql` ist fachlich ein originärer Phase-1-Bestandteil; Seed-Inhalte mit 5 globalen Arbeitszeitversionen, 4 `systemconfig`-Defaults und 9 `auditlog`-Einträgen sind in den Planungsunterlagen ausdrücklich festgelegt und werden durch die heutigen Migrationstests weiterhin abgesichert. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Niedrig; der Seed-Zweck ist nachvollziehbar und testbar. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Die Seed-Werte zusätzlich in einer kompakten Referenztabelle dokumentieren, damit spätere Anpassungen sofort als Sollabweichung sichtbar werden. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | `migrations/0002seeddefaults.sql`, `tests/testmigrations.py` |
| `src/arbeitszeit/infrastructure/db/connection.py` erfüllt laut Planung die vorgesehenen Kernpunkte `isolation_level=None`, `PRAGMA foreign_keys=ON`, `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000` und `row_factory=sqlite3.Row`; der Codeexport beschreibt genau diese Einstellungen. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Niedrig; das Phase-1-Fundament für SQLite-Verbindungen ist konsistent dokumentiert. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Diese PRAGMAs als nicht verhandelbare Invariante zentral dokumentieren, weil spätere Module darauf aufbauen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | `src/arbeitszeit/infrastructure/db/connection.py` |
| `src/arbeitszeit/infrastructure/db/migrations.py` ist als versionierter, idempotenter Runner geplant und im Export entsprechend beschrieben: Glob auf `NNNN*.sql`, Prüfung gegen `schemamigrations`, Versionsvalidierung vor Query-Konstruktion und atomare Ausführung per `executescript` mit `BEGIN/COMMIT`. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | Niedrig; die Architektur entspricht dem geplanten Migrationsmodell. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | Die Validierungsregeln für Versionsnummern im Kommentar direkt an der Funktion belassen, um unbeabsichtigte Lockerungen zu vermeiden. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | `src/arbeitszeit/infrastructure/db/migrations.py` |
| Die Planunterlagen fordern Transaktionssicherheit und korrektes `schemamigrations`-Verhalten; der heutige Testbestand deckt genau dies ab, unter anderem mit dem Fall, dass eine fehlgeschlagene Migration keinen Eintrag in `schemamigrations` hinterlässt. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Niedrig; die Kerninvariante ist explizit abgesichert. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Diesen Testfall im Dokument als Phase-1-Schlüsselnachweis besonders hervorheben. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | `src/arbeitszeit/infrastructure/db/migrations.py`, `tests/testmigrations.py` |
| `scripts/initdb.py` ist als dünner CLI-Einstieg geplant und im Codeexport genau so beschrieben: Verbindung öffnen, `runmigrations()` aufrufen, Verbindung schließen, angewendete Versionen oder „Keine neuen Migrationen“ ausgeben. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Niedrig; der Umfang bleibt phase-1-gerecht schlank. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | Den historischen Alias mit Unterstrich nur noch dokumentarisch erwähnen, nicht mehr als primären Pfad. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md) | `scripts/initdb.py` |
| `tests/testmigrations.py` enthält heute laut Planung und Codeexport 12 Tests und prüft die gesamte Kette `0001` bis `0006`; originär Phase 1 waren jedoch nur 6 Tests für `0001` und `0002`. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | Hoch für historische Fehlklassifikation; spätere Migrationen könnten irrtümlich als Phase-1-Lieferumfang bewertet werden. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | Das Testmodul in der Dokumentation explizit in „originärer Phase-1-Anteil“ und „spätere Erweiterungen“ aufteilen, auch wenn die Datei technisch gemeinsam bleibt. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | `tests/testmigrations.py`, `phase1_planung.md`, `planung_gesamt.md` |
| Laut `planung_gesamt.md` und `phase1_planung.md` gehören `migrations/0003cleanupbookingstatus.sql`, `migrations/0004supplementrejectfieldsandreviewnote.sql`, `migrations/0005timebookingsdeviceeventid.sql` und `migrations/0006systemeventsapplicationerror.sql` ausdrücklich **nicht** zum originären Phase-1-Lieferumfang. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Mittel; ohne diese Abgrenzung würde der Audit entweder zu streng oder historisch falsch urteilen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | In jedem Review die spätere Herkunft direkt je Datei vermerken. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | `migrations/0003cleanupbookingstatus.sql`, `migrations/0004supplementrejectfieldsandreviewnote.sql`, `migrations/0005timebookingsdeviceeventid.sql`, `migrations/0006systemeventsapplicationerror.sql` |
| Die Dokumentation benennt teils „16 Tabellen“ für `0001schema.sql`, während in den Gesamtunterlagen an anderer Stelle für das festgelegte ER-Modell von „15 Tabellen“ die Rede ist; zugleich wird `schemamigrations` in Phase 1 ausdrücklich als Bestandteil von `0001` genannt. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Mittel; die Zählweise ist ohne Erläuterung mehrdeutig. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Tabellenzählung vereinheitlichen: entweder „15 fachliche Tabellen plus `schemamigrations`“ oder „16 Tabellen inklusive `schemamigrations`“. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | `phase1_planung.md`, `planung_gesamt.md` |
| Der heutige Gesamtstand der Tests wird in `phase1_planung.md` als 12 Tests beschrieben; zugleich nennt `planung_gesamt.md` für den Gesamtstand des Moduls ebenfalls 12 Tests und ordnet die späteren Testfälle den Phasen 4 und 5 zu. Diese Aussagen sind konsistent, müssen aber bei jedem Audit aktiv historisiert werden. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Niedrig; die Faktenlage ist konsistent, aber erklärungsbedürftig. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | Eine feste Abschnittsüberschrift „Historischer Stand vs. heutiger Stand“ in beiden Dokumenten beibehalten oder nachziehen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md) | `phase1_planung.md`, `planung_gesamt.md` |
| Aus `arbeitszeit.md` ist erkennbar, dass das Modulfundament weitergewachsen ist und viele spätere Schichten enthält; das bestätigt die Prüfvorgabe, dass Migrationen und Tests im selben Modul weitergewachsen sind. (Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | Niedrig; das ist keine Codeabweichung, sondern ein erwarteter Evolutionspfad. (Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | Im Audit stets trennen zwischen „Datei existiert noch aus Phase 1“ und „Dateiinhalt ist heute erweitert“. (Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md) | `arbeitszeit.md`, `tests/testmigrations.py` |

## 2. Priorisierte To-do-Liste

1. **P1 – Dokumentationsklarheit herstellen:** In `phase1_planung.md` und `planung_gesamt.md` eine explizite Mapping-Tabelle „historischer Name / reale Codebasis-Schreibweise“ ergänzen, mindestens für `migrations/0001schema.sql`, `migrations/0002seeddefaults.sql`, `scripts/initdb.py` und `tests/testmigrations.py`. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
2. **P1 – Phase-1-Abgrenzung im Testmodul schärfen:** In der Dokumentation die 12 Tests von `tests/testmigrations.py` in 6 originäre Phase-1-Tests und 6 spätere Ergänzungen aufgliedern; die Datei selbst kann unverändert bleiben. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md)
3. **P1 – Tabellenzählung bereinigen:** Die widersprüchliche Zählweise „15 Tabellen“ vs. „16 Tabellen inkl. `schemamigrations`“ vereinheitlichen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
4. **P1 – Ist-Nachweis für `.python-version` und `.gitignore` verbessern:** In `arbeitszeit.md` oder einer separaten Bestandsdatei den tatsächlichen Inhalt oder wenigstens einen Dateibaum dieser beiden Dateien aufnehmen. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md)
5. **P2 – Historische Reichweite von `0001schema.sql` klar markieren:** In der Doku unmittelbar bei `0001schema.sql` vermerken, welche Punkte erst durch `0003`, `0004` und `0005` auf den heutigen Zielzustand gebracht wurden. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
6. **P2 – Seed-Defaults kompakt referenzieren:** Die 5 Seed-Arbeitszeiten, 4 `systemconfig`-Defaults und 9 `auditlog`-Einträge in einer kleinen Referenztabelle dokumentieren. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md)
7. **P3 – Review-Template standardisieren:** Ein dauerhaftes Audit-Template anlegen, das pro Datei die Spalten „originär Phase 1“, „heutiger Stand“, „spätere Ergänzung“, „Abweichung/Ambiguität“ führt. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

## 3. Förmliches Umsetzungsprotokoll

### Arbeitspaket 1 – Pfad- und Namenskonventionen vereinheitlichen

**Reihenfolge/Priorität:** Sofort, höchste Priorität. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

**Umsetzung:**
- In `phase1_planung.md` eine Tabelle mit den Spalten `Historische/normalisierte Bezeichnung` und `Reale Codebasis-Schreibweise` ergänzen. (Quelle: phase1_planung.md)
- In `planung_gesamt.md` dieselbe Schreibweise konsequent übernehmen. (Quelle: planung_gesamt.md)
- Beispiele zwingend aufnehmen: `migrations/0001_schema.sql` → `migrations/0001schema.sql`, `migrations/0002_seed_defaults.sql` → `migrations/0002seeddefaults.sql`, `scripts/init_db.py` → `scripts/initdb.py`, `tests/test_migrations.py` → `tests/testmigrations.py`. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

**Akzeptanzkriterien:**
- Jeder in Phase 1 referenzierte Pfad ist in beiden Planungsdokumenten eindeutig auf die reale Codebasis abgebildet. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
- Es bleibt kein Platzhalter und kein primärer Verweis auf nicht existierende Dateinamen zurück. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

**Erforderliche Testfälle:**
- Dokumentationsreview: Stichprobe aller Phase-1-Dateipfade gegen reale Pfade in `arbeitszeit.md`. (Quelle: arbeitszeit.md)
- Prompt-Regression: Ein Folgeaudit muss ohne manuelle Pfadkorrektur dieselben Dateien finden können. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md)

### Arbeitspaket 2 – Historischen Phase-1-Anteil von `tests/testmigrations.py` sauber abgrenzen

**Reihenfolge/Priorität:** Sofort nach Arbeitspaket 1, höchste Priorität. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

**Umsetzung:**
- In beiden Planungsdokumenten die sechs originären Phase-1-Tests namentlich zusammenfassen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
- Darunter die später hinzugekommenen Tests separat als Phase-4- bzw. Phase-5-Erweiterung listen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
- Klar formulieren, dass das heutige Testmodul den Gesamtstand `0001` bis `0006` prüft, aber historisch nicht vollständig zu Phase 1 gehört. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md)

**Akzeptanzkriterien:**
- Ein Leser kann ohne Rückschlussfehler erkennen, welche Testfälle originär zu Phase 1 gehören. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
- `0003` bis `0006` werden nirgends als originärer Phase-1-Lieferumfang bezeichnet. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

**Erforderliche Testfälle:**
- Dokumentationsreview der Testliste gegen `tests/testmigrations.py`. (Quelle: arbeitszeit.md)
- Konsistenzcheck, dass die Summenbildung 6 + 5 + 1 = 12 in allen Dokumenten gleich dargestellt ist. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

### Arbeitspaket 3 – Schemazählung und historische Schemaentwicklung bereinigen

**Reihenfolge/Priorität:** Hoch, nach den beiden Klarstellungsarbeiten. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

**Umsetzung:**
- Die Tabellenzählung in `phase1_planung.md` und `planung_gesamt.md` auf eine Formulierung festlegen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
- Empfehlung: „15 fachliche Tabellen plus `schemamigrations` = 16 Tabellen in `0001schema.sql`“. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
- Direkt bei `0001schema.sql` einen Kurzblock „später nachgerüstet durch `0003`–`0005`“ ergänzen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

**Akzeptanzkriterien:**
- Es gibt keine widersprüchliche Tabellenanzahl mehr. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
- Der Leser versteht, warum `0001schema.sql` historisch korrekt ist, obwohl spätere Migrationen Teile des Schemas ändern. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

**Erforderliche Testfälle:**
- Dokumentationsabgleich der Tabellenzählung in beiden Dateien. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)
- Fachreview: `schemamigrations` wird entweder überall mitgezählt oder überall separat ausgewiesen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)

### Arbeitspaket 4 – Nachweisqualität des Istbilds in `arbeitszeit.md` erhöhen

**Reihenfolge/Priorität:** Mittel. (Quelle: arbeitszeit.md)

**Umsetzung:**
- In `arbeitszeit.md` einen kompakten Dateibaum des Projektwurzelbestands ergänzen. (Quelle: arbeitszeit.md)
- Für `.python-version` und `.gitignore` mindestens Kurzinhalt oder Volltextauszug aufnehmen. (Quelle: arbeitszeit.md)
- Optional eine Rubrik „Reale Schlüsseldateien Phase 1“ mit den exakten Pfaden anlegen. (Quelle: arbeitszeit.md)

**Akzeptanzkriterien:**
- Der Ist-Nachweis für alle prüfrelevanten Phase-1-Dateien ist in `arbeitszeit.md` direkt sichtbar. (Quelle: arbeitszeit.md)
- Ein externer Auditor muss sich nicht auf indirekte Dokumentenaussagen verlassen, um das Vorhandensein der Basisdateien zu plausibilisieren. (Quelle: phase1_planung.md)(Quelle: arbeitszeit.md)

**Erforderliche Testfälle:**
- Sichtprüfung, dass alle Phase-1-Dateien im Dateibaum oder mit Inhaltsauszug auftauchen. (Quelle: arbeitszeit.md)
- Folgeaudit nur auf Basis von `arbeitszeit.md` muss `.python-version` und `.gitignore` eindeutig referenzieren können. (Quelle: arbeitszeit.md)

## Abschließende Bewertung

**Ist Phase 1 historisch korrekt abgeschlossen?** Ja. Der historische Phase-1-Kern aus Projektgerüst, SQLite-Verbindungsaufbau, Migrationssystem, Seed-Migration, Initialisierungsskript und den originären Migrationstests ist laut `phase1_planung.md`, `planung_gesamt.md` und dem exportierten Istbild in `arbeitszeit.md` vorhanden und als Fundament späterer Ausbaustufen nachvollziehbar. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md)

**Ist die heutige Codebasis mit der Phase-1-Planung konsistent dokumentiert?** Überwiegend ja, aber nicht vollständig trennscharf. Die fachliche Linie stimmt, doch die gemeinsame Fortschreibung derselben Dateien und Testmodule sowie abweichende historische vs. reale Dateinamen erzeugen dokumentarische Unschärfen. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md)

**Wo besteht Dokumentations- oder Bereinigungsbedarf?** Vor allem bei der eindeutigen Pfadbenennung, der expliziten Trennung von originärem Phase-1-Anteil und späteren Erweiterungen im Migrations-Testmodul, der vereinheitlichten Tabellenzählung sowie beim unmittelbaren Ist-Nachweis von `.python-version` und `.gitignore` im Codeexport. (Quelle: phase1_planung.md)(Quelle: planung_gesamt.md)(Quelle: arbeitszeit.md)
