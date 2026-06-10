# Konkrete Planung Phase 1 – arbeitszeit

## Zweck

Dieses Dokument leitet aus der aktuellen Gesamtplanung die **konkrete Phase 1** für das Projekt `arbeitszeit` ab. Es beschränkt sich bewusst auf den verifizierten Phase-1-Umfang und trennt strikt zwischen Phase-1-Lieferumfang, späteren Nachträgen und offenen Punkten. [planung_gesamt.md]

Die Phase-1-Planung steht im Kontext der aktuellen Referenzdokumente `docs/pflichtenheft_arbeitszeit_v4.md`, `docs/regelwerk_arbeitszeit_v4.md` und `docs/anlage_einhaltung_pflichtenheft_v2.md`. Gleichzeitig bleibt festgehalten, dass der originäre Phase-1-Umfang historisch auf dem früheren v3-Arbeitsstand aufsetzte; dieses Dokument beschreibt deshalb die **heute gültige fachliche Einordnung** des damaligen Phase-1-Lieferumfangs, ohne spätere Umsetzungen rückwirkend als Teil von Phase 1 auszugeben. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Zielbild Phase 1

Phase 1 liefert das **technische Grundgerüst** des Systems. Ziel ist noch nicht die vollständige Buchungslogik oder UI, sondern eine belastbare Grundlage aus Repository-Struktur, initialem SQLite-Schema, Migrationsmechanismus, Datenbankverbindung, Seed-Daten und ersten Migrationstests. [planung_gesamt.md]

Phase 1 muss so sauber angelegt sein, dass die späteren Phasen Domäne, Application, Infrastruktur und Präsentation darauf stabil aufbauen können. Das betrifft insbesondere die Migrationsfähigkeit des Schemas, referenzielle Integrität, nachvollziehbare Initialisierung und einen reproduzierbaren Datenbank-Setup-Prozess. [planung_gesamt.md]

## Verbindlicher Lieferumfang

Laut aktueller Gesamtplanung umfasst der originäre Phase-1-Abschluss genau die folgenden Bestandteile: [planung_gesamt.md]

- `pyproject.toml` als Projektdefinition. [planung_gesamt.md]
- `src/`-Layout als Python-Projektstruktur. [planung_gesamt.md]
- `tests/` als Grundlage für automatisierte Tests. [planung_gesamt.md]
- `.gitignore` und `.python-version` für Entwicklungsumgebung und Repo-Hygiene. [planung_gesamt.md]
- `migrations/0001_schema.sql` als initiales, vollständiges Datenbankschema einschließlich `schema_migrations`. [planung_gesamt.md]
- `migrations/0002_seed_defaults.sql` für Regelzeiten und Default-Konfiguration. [planung_gesamt.md]
- `infrastructure/db/connection.py` mit `isolation_level=None`, `PRAGMA foreign_keys = ON` und `row_factory`. [planung_gesamt.md]
- `infrastructure/db/migrations.py` mit Migrationsrunner auf Basis von `executescript()` innerhalb von `BEGIN/COMMIT`. [planung_gesamt.md]
- `scripts/init_db.py` zur initialen Datenbankanlage. [planung_gesamt.md]
- `tests/test_migrations.py` mit den ursprünglichen Phase-1-Tests für `0001` und `0002`. [planung_gesamt.md]

Alles darüber hinaus gehört **nicht** zum originären Phase-1-Lieferumfang, auch wenn es später auf diesem Fundament ergänzt wurde. [planung_gesamt.md]

## Nicht Teil von Phase 1

Die Gesamtplanung dokumentiert mehrere spätere Nachträge, die ausdrücklich **nicht** als Phase-1-Abschluss zu werten sind. Dazu gehören insbesondere `0003_cleanup_booking_status.sql`, `0004_supplement_reject_fields_and_review_note.sql`, `0005_time_bookings_device_event_id.sql`, `0006_system_events_application_error.sql` sowie die spätere Erweiterung von `tests/test_migrations.py` auf die gesamte Kette 0001–0006. [planung_gesamt.md]

Ebenfalls nicht Teil von Phase 1 sind Domänenobjekte, Use Cases, SQLite-Repositories, Backup/Restore, Export, Pflichtauswertungen, Systemcheck, Terminal-UI, Admin-CLI und die produktive Systemzeitprotokollierung. Diese Themen werden in der Gesamtplanung erst in Phase 2 bis Phase 5 eingeordnet. [planung_gesamt.md]

## Fachliche Anforderungen, die Phase 1 vorbereiten muss

Auch wenn Phase 1 viele Fachfunktionen noch nicht implementiert, muss das initiale Schema die späteren Anforderungen aus Pflichtenheft und Regelwerk tragfähig vorbereiten. Dazu zählen insbesondere Buchungen, RFID-Karten, Benutzerkonten, Korrekturen, Nachträge, Prüffälle, Regelarbeitszeiten, Systemkonfiguration, Audit-Log und Systemereignisse. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

Phase 1 muss außerdem das Grundprinzip unterstützen, dass fachlich relevante Buchungen nicht physisch gelöscht, sondern später über Status, Korrektur oder Archivierung behandelt werden. Dieses Aufbewahrungsprinzip ist in der Gesamtplanung ausdrücklich als Schema- und Architekturentscheidung verankert und steht im Einklang mit Pflichtenheft v4 §12 sowie Regelwerk v4 §18. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

## Konkrete Arbeitspakete

### 1. Projektgrundlage anlegen

Es wird ein lauffähiges Python-Projektgerüst mit `pyproject.toml`, `src/`, `tests/`, `.gitignore` und `.python-version` angelegt. Ziel ist nicht Vollständigkeit der Fachlogik, sondern ein sauberer und konsistenter Entwicklungsrahmen für spätere Phasen. [planung_gesamt.md]

### 2. Initiales SQLite-Schema definieren

`migrations/0001_schema.sql` muss das initiale Schema vollständig definieren und dabei auch `schema_migrations` enthalten. Die Struktur muss die späteren fachlichen Kernobjekte des Systems bereits tragfähig anlegen. [planung_gesamt.md]

Dabei ist besonders wichtig:
- referenzielle Integrität über Foreign Keys, [planung_gesamt.md]
- CHECK-Constraints für grundlegende Wertebereiche, [planung_gesamt.md]
- Indizes für erwartbare Zugriffe, [planung_gesamt.md]
- Aufnahme von `system_events`, damit spätere Betriebs- und Zeitereignisse überhaupt persistierbar sind. [planung_gesamt.md] [Pflichtenheft v4]

### 3. Seed-Daten festlegen

`migrations/0002_seed_defaults.sql` muss die initialen Regelarbeitszeiten und Standard-Konfigurationswerte einspielen. Die Gesamtplanung benennt diese Migration ausdrücklich als Bestandteil von Phase 1. [planung_gesamt.md]

Die Regelzeiten müssen den fachlichen Vorgaben entsprechen, die im Pflichtenheft und Regelwerk als Standard-Regelarbeitszeiten dokumentiert sind: Montag bis Mittwoch 07:30–18:00, Donnerstag 07:30–14:00, Freitag 07:30–16:00. [Pflichtenheft v4] [Regelwerk v4]

### 4. Datenbankverbindung kapseln

`infrastructure/db/connection.py` muss die SQLite-Verbindung so öffnen, dass Transaktionen kontrollierbar sind und referenzielle Integrität tatsächlich aktiv ist. Dafür nennt die Gesamtplanung drei verbindliche Eckpunkte: `isolation_level=None`, `PRAGMA foreign_keys = ON` und eine gesetzte `row_factory`. [planung_gesamt.md]

Diese Kapselung ist entscheidend, weil spätere Phasen auf konsistentes Verbindungs- und Cursor-Verhalten angewiesen sind. Fehler in diesem Fundament würden sich in alle Folgephasen fortpflanzen. [planung_gesamt.md]

### 5. Migrationsrunner implementieren

`infrastructure/db/migrations.py` muss SQL-Migrationsdateien reproduzierbar anwenden. Laut Gesamtplanung erfolgt dies mit `executescript()` innerhalb eines expliziten `BEGIN/COMMIT`-Rahmens; zusätzlich muss die Versionsvalidierung vor dem f-String erfolgen. [planung_gesamt.md]

Ziel ist ein deterministischer und robuster Mechanismus, der sowohl Erstinitialisierung als auch spätere inkrementelle Schemaentwicklung ermöglicht. Phase 1 schafft damit die technische Voraussetzung für alle nachfolgenden Migrationen. [planung_gesamt.md]

### 6. Initialisierungsskript bereitstellen

`scripts/init_db.py` muss die Datenbank initial anlegen und die verfügbaren Migrationen anwenden. Das Skript ist Teil des originären Phase-1-Lieferumfangs und bildet den wiederholbaren Einstiegspunkt für lokale Entwicklung und Tests. [planung_gesamt.md]

### 7. Migrations-Tests schreiben

`tests/test_migrations.py` muss in Phase 1 die Migrationskette `0001` und `0002` prüfen. Die Gesamtplanung nennt für den originären Phase-1-Stand 6 Tests. [planung_gesamt.md]

Minimal abgesichert werden müssen dabei:
- Schema erfolgreich anlegbar, [planung_gesamt.md]
- Seed-Migration erfolgreich anwendbar, [planung_gesamt.md]
- `schema_migrations` wird korrekt geführt, [planung_gesamt.md]
- Grundtabellen existieren nach Migration, [planung_gesamt.md]
- die Migrationsreihenfolge ist reproduzierbar, [planung_gesamt.md]
- die Datenbankinitialisierung läuft ohne inkonsistenten Zwischenzustand. [planung_gesamt.md]

## Abgrenzung zu späteren Korrekturen

Die aktuelle Gesamtplanung hält ausdrücklich fest, dass das frühe Schema in späteren Phasen an einzelnen Stellen nachgeschärft wurde. Dazu gehören bereinigte BookingStatus-CHECKs, zusätzliche Felder für Nachtragsablehnung, das `note`-Feld auf `review_cases` und die Ergänzung von `device_event_id` in `time_bookings`. [planung_gesamt.md]

Für die konkrete Phase-1-Planung bedeutet das: Das Ziel ist **nicht**, rückwirkend bereits den finalen Stand von 0003–0006 zu liefern. Das Ziel ist ein belastbares erstes Schema, von dem aus diese späteren Korrekturen migrationsbasiert nachvollziehbar ergänzt werden können. [planung_gesamt.md]

## Qualitätskriterien für den Phase-1-Abschluss

Phase 1 gilt erst dann als sauber abgeschlossen, wenn alle folgenden Punkte erfüllt sind: [planung_gesamt.md]

- Projektstruktur ist konsistent und versionierbar angelegt. [planung_gesamt.md]
- `0001_schema.sql` erzeugt das initiale Schema vollständig einschließlich `schema_migrations`. [planung_gesamt.md]
- `0002_seed_defaults.sql` spielt Standard-Regelzeiten und Default-Konfiguration erfolgreich ein. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- Datenbankverbindungen aktivieren Foreign Keys zuverlässig und erlauben kontrollierte Transaktionsführung. [planung_gesamt.md]
- Der Migrationsrunner arbeitet reproduzierbar und bricht bei Fehlern konsistent ab. [planung_gesamt.md]
- `init_db.py` kann eine neue Datenbank aus dem Migrationsbestand erzeugen. [planung_gesamt.md]
- Die ursprünglichen 6 Migrations-Tests für 0001/0002 laufen erfolgreich. [planung_gesamt.md]

## Bekannte Risiken und Selbstkritik

Phase 1 darf nicht den Fehler machen, frühe Schemaentscheidungen als endgültig unveränderlich zu behandeln. Die Gesamtplanung zeigt gerade an den späteren Migrationen 0003–0006, dass ein gutes Fundament nicht bedeutet, von Anfang an bereits den perfekten Endzustand zu kennen. [planung_gesamt.md]

Ein zweites Risiko ist die unklare Vermischung von Phase-1-Umfang und späterem Ist-Zustand. Dieses Dokument trennt deshalb ausdrücklich zwischen dem damaligen Lieferumfang von Phase 1 und dem heutigen Gesamtstand des Projekts. Spätere Korrekturen oder Ergänzungen werden nicht rückwirkend als Phase-1-Ergebnis ausgegeben. [planung_gesamt.md]

Ein drittes Risiko liegt in der Überschätzung dessen, was Phase 1 bereits „fachlich erfüllt“. Phase 1 schafft die technische Voraussetzung für spätere Fachfunktionen, erfüllt aber noch nicht die vollständigen Anforderungen zu Buchungslogik, Export, Pflichtauswertungen, Backup/Restore, Rollenprüfung oder Betrieb. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Offene Punkte, die bewusst nicht in Phase 1 gezogen werden

Die folgenden Punkte sind wichtig, aber **nicht** Bestandteil der konkreten Phase-1-Umsetzung: [planung_gesamt.md] [Anlage v2]

- Domänenregeln und Compliance-Prüfungen, [planung_gesamt.md]
- Application-Use-Cases und Rollenprüfung, [planung_gesamt.md]
- echte SQLite-Repositories und Unit of Work, [planung_gesamt.md]
- Export, PDF, Pflichtauswertungen und Report-Queries, [planung_gesamt.md]
- Backup/Restore, NAS-Sync und Rotationskonzept, [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]
- Terminal-UI, Admin-CLI und betriebliche Orchestrierung, [planung_gesamt.md]
- vollständige operative Verkettung des `device_events`-/`device_event_id`-Pfads, [planung_gesamt.md] [Anlage v2]
- organisatorische Nachweise wie AV-Vertrag, Rollenfestlegung, IT-Sicherheitskonzept, Testmatrix und Betriebsdokumentation. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Ergebnis

Die konkrete Phase 1 ist damit klar begrenzt: **Projektgerüst, initiales SQLite-Schema, Seed-Daten, Verbindungsaufbau, Migrationsrunner, Initialisierungsskript und erste Migrations-Tests**. Genau dieses Fundament ist laut aktueller Gesamtplanung der belastbare Startpunkt des Projekts `arbeitszeit`. [planung_gesamt.md]
