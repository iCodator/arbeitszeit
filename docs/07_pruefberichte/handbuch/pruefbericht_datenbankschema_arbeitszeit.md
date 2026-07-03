# Prüfbericht – `docs/module/datenbankschema_arbeitszeit.md`

## Gesamteinschätzung

Das Dokument ist insgesamt von hoher Qualität und deckt das Schema präzise ab. Die große Mehrheit der Aussagen ist durch den SQL-Quelltext direkt belegbar und korrekt. Es wurden jedoch **drei inhaltliche Abweichungen** gefunden: eine inkorrekte Aussage zur Tabellenanzahl in Migration 0001, eine strukturell unvollständige Darstellung des `supplements`-Constraints sowie eine fehlende Angabe zur Neuerstellungsursache in Migration 0005. Außerdem gibt es eine nicht verifizierbare Formulierung beim `PRAGMA`-Geltungsbereich.

## Einzelbefunde

**Aussage:**
Migration 0001 erstellt „17 Tabellen, 17 Indizes".

**Status:**
inkorrekt

**Beleg:**
`migrations/0001_schema.sql` [cite:5]

**Bewertung:**
`0001_schema.sql` enthält folgende `CREATE TABLE`-Statements: `schema_migrations`, `employees`, `user_accounts`, `rfid_cards`, `terminals`, `time_bookings`, `booking_status_history`, `booking_corrections`, `supplements`, `review_cases`, `review_case_actions`, `work_schedule_versions`, `system_config`, `device_events`, `system_events`, `audit_log` – das sind **16 Tabellen**, nicht 17. Die Indizes wurden ebenfalls gezählt: `idx_user_accounts_employee_id`, `idx_rfid_cards_employee_status`, `idx_time_bookings_employee_booked_at`, `idx_time_bookings_status_booked_at`, `idx_booking_status_history_booking_changed_at`, `idx_booking_corrections_booking_corrected_at`, `idx_supplements_employee_event_at`, `idx_supplements_approval_status`, `idx_review_cases_status_detected_at`, `idx_review_cases_employee_detected_at`, `idx_review_case_actions_case_created_at`, `idx_work_schedule_versions_scope_weekday_valid_from`, `idx_system_config_key_version`, `idx_device_events_occurred_at`, `idx_system_events_event_at`, `idx_audit_log_object_event_at`, `idx_audit_log_employee_event_at` – das sind **17 Indizes** (korrekt). Die Tabellenanzahl ist falsch.

**Änderungsvorschlag:**
`| 0001 | 0001_schema.sql | Ursprüngliches Gesamtschema (16 Tabellen, 17 Indizes) |`

**Aussage:**
Migration 0003 bereinigt Status-Werte in `time_bookings` **und** `booking_status_history`.

**Status:**
korrekt

**Beleg:**
`migrations/0003_cleanup_booking_status.sql` [cite:7]

**Bewertung:**
Die Migration legt sowohl `time_bookings_new` als auch `booking_status_history_new` an, überträgt Daten, löscht die alten Tabellen und benennt die neuen um. Beide Tabellen sind betroffen.

**Änderungsvorschlag:**
Kein Änderungsbedarf.

**Aussage:**
Migration 0003 entfernt aus `time_bookings.current_status` die Werte `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION` und `MANUAL_ENTRY`.

**Status:**
korrekt

**Beleg:**
`migrations/0001_schema.sql` (ursprünglicher CHECK), `migrations/0003_cleanup_booking_status.sql` (neuer CHECK ohne diese Werte) [cite:5] [cite:7]

**Bewertung:**
In 0001 enthält `current_status` alle vier genannten Zusatzwerte. In 0003 fehlen sie im neuen CHECK-Constraint.

**Änderungsvorschlag:**
Kein Änderungsbedarf.

**Aussage:**
In `booking_status_history` bleibt `MANUAL_ENTRY` seit Migration 0003 als zulässiger Wert erhalten, da es dort die Herkunft eines Statuswechsels kennzeichnet.

**Status:**
korrekt

**Beleg:**
`migrations/0003_cleanup_booking_status.sql`, Kommentar: „MANUAL_ENTRY bleibt als Herkunftskennzeichnung von Statuswechseln" [cite:7]

**Bewertung:**
Der Kommentar im SQL und der neue CHECK-Constraint in `booking_status_history_new` bestätigen beide die Aussage.

**Änderungsvorschlag:**
Kein Änderungsbedarf.

**Aussage:**
Migration 0005 legt `time_bookings` vollständig neu an, weil SQLite `CHECK`-Constraints nicht nachträglich per `ALTER TABLE` ändern kann.

**Status:**
inkorrekt (Begründung unvollständig / teilweise falsch)

**Beleg:**
`migrations/0005_time_bookings_device_event_id.sql`, Kommentar: „FK-Constraint auf device_events erfordert Table-Rebuild (SQLite-Einschränkung)." [cite:9]

**Bewertung:**
Das Handbuch nennt als Ursache ausschließlich die Unfähigkeit, `CHECK`-Constraints per `ALTER TABLE` zu ändern. Die Migration selbst dokumentiert jedoch explizit, dass der Table-Rebuild wegen des **neuen Foreign-Key-Constraints** auf `device_events` notwendig war – nicht wegen eines CHECK-Constraints. In SQLite können Foreign-Key-Constraints nicht nachträglich per `ALTER TABLE ADD COLUMN` mit einer `REFERENCES`-Klausel ergänzt werden, wenn `PRAGMA foreign_keys = ON` aktiv ist. Der `CHECK`-Constraint für `current_status` ändert sich in 0005 gegenüber 0003 nicht.

**Änderungsvorschlag:**
Den historischen Hinweis im Abschnitt `time_bookings` präzisieren:

> **Historischer Hinweis:** In Migration 0001 enthielt `current_status` zusätzlich die Werte `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION` und `MANUAL_ENTRY`. Migration 0003 hat diese entfernt. Migration 0005 legte die Tabelle erneut vollständig neu an, da das Hinzufügen eines Foreign-Key-Constraints auf `device_events` in SQLite keinen `ALTER TABLE`-Weg erlaubt (nicht wegen eines CHECK-Constraints).

Entsprechend auch im Abschnitt „Technisches Muster: Table-Rebuild bei CHECK-Änderungen" ergänzen, dass Migration 0005 aus einem FK-Constraint-Grund rebuildet, nicht aus einem CHECK-Constraint-Grund.

**Aussage:**
Im Abschnitt „Technisches Muster" heißt es: „Migrationen 0003, 0004, 0005 und 0006 folgen alle demselben Muster, **weil SQLite bestehende `CHECK`-Constraints nicht per `ALTER TABLE` ändern kann**."

**Status:**
inkorrekt (für Migration 0005)

**Beleg:**
`migrations/0005_time_bookings_device_event_id.sql`, Kommentar [cite:9]

**Bewertung:**
Wie beim vorherigen Befund belegt, baut Migration 0005 die Tabelle wegen eines neuen FK-Constraints um, nicht wegen eines CHECK-Constraints. Die pauschale Begründung für alle vier Migrationen ist daher für 0005 falsch.

**Änderungsvorschlag:**
Den einleitenden Satz des Abschnitts differenzieren:

> Migrationen 0003, 0004 und 0006 folgen diesem Muster, weil SQLite bestehende `CHECK`-Constraints nicht per `ALTER TABLE` ändern kann. Migration 0005 folgt demselben Muster, weil SQLite das nachträgliche Hinzufügen eines Foreign-Key-Constraints per `ALTER TABLE ADD COLUMN` nicht unterstützt.

**Aussage:**
Der Tabellen-Constraint in `supplements` (seit 0004): Bei `PENDING` müssen alle vier Felder (`approved_by_user_id`, `approved_at`, `rejected_by_user_id`, `rejected_at`) NULL sein; bei `APPROVED` müssen genau die Genehmigungs-Felder gesetzt, die Ablehnungs-Felder NULL sein; bei `REJECTED` umgekehrt.

**Status:**
korrekt

**Beleg:**
`migrations/0004_supplement_reject_fields_and_review_note.sql`, CHECK-Constraint von `supplements_new` [cite:8]

**Bewertung:**
Der SQL-CHECK-Constraint kodiert exakt diese drei Bedingungen. Das Handbuch beschreibt die Logik inhaltlich richtig.

**Änderungsvorschlag:**
Kein Änderungsbedarf.

**Aussage:**
Vor Migration 0004 existierte in `supplements` nur ein gemeinsames Feldpaar (`approved_by_user_id`, `approved_at`), das für Genehmigungen und Ablehnungen verwendet wurde.

**Status:**
korrekt

**Beleg:**
`migrations/0001_schema.sql` (supplements-Definition ohne rejected_*-Felder) [cite:5]; `migrations/0004_supplement_reject_fields_and_review_note.sql` (SELECT-CASE-Logik zum Datentransfer) [cite:8]

**Bewertung:**
In 0001 gibt es in `supplements` nur `approved_by_user_id` und `approved_at`, kein `rejected_*`. Die CASE-Logik beim Datentransfer in 0004 bestätigt, dass dieselben Felder für beide Fälle genutzt wurden.

**Änderungsvorschlag:**
Kein Änderungsbedarf.

**Aussage:**
`PRAGMA foreign_keys = ON;` wird in `0001_schema.sql` einmalig gesetzt und gilt für die referenzielle Integrität aller Fremdschlüssel im Schema.

**Status:**
nicht verifizierbar (teilweise)

**Beleg:**
`migrations/0001_schema.sql` (PRAGMA vorhanden) [cite:5]; Anwendungscode nicht eingesehen.

**Bewertung:**
Das `PRAGMA`-Statement ist in `0001_schema.sql` belegbar vorhanden. Die Aussage, dass es „für die referenzielle Integrität **aller** Fremdschlüssel" gilt, ist jedoch nur dann vollständig korrekt, wenn der Anwendungscode das PRAGMA bei jeder neuen Datenbankverbindung erneut setzt – da `PRAGMA foreign_keys` in SQLite eine **verbindungsweite** Einstellung ist, die nicht persistent gespeichert wird. Ob der Anwendungscode dies tut, ist aus den Migrationsdateien allein nicht belegbar.

**Änderungsvorschlag:**
Formulierung präzisieren oder mit Vorbehalt kennzeichnen:

> `PRAGMA foreign_keys = ON;` ist in `0001_schema.sql` gesetzt. Da dieses PRAGMA in SQLite verbindungsweit und nicht persistent gilt, muss der Anwendungscode es bei jeder Datenbankverbindung erneut aktivieren, damit die referenzielle Integrität aller Fremdschlüssel durchgesetzt wird. Ob dies im Anwendungscode erfolgt, ist aus den Migrationsdateien allein nicht verifizierbar.

**Aussage:**
`system_config.UNIQUE (config_key, version)` stellt die Versionierungslogik sicher: Der aktuell gültige Wert ist stets der Datensatz mit dem höchsten `version`-Wert je Schlüssel.

**Status:**
korrekt (UNIQUE-Constraint), nicht verifizierbar (Auslesestrategie)

**Beleg:**
`migrations/0001_schema.sql`, `UNIQUE (config_key, version)` in `system_config` [cite:5]

**Bewertung:**
Der UNIQUE-Constraint ist belegbar. Die daraus abgeleitete Auslesestrategie („höchster version-Wert = aktuell gültig") ist eine semantische Konvention, die nicht durch eine VIEW, einen Trigger oder Anwendungslogik im Repository belegt werden kann. Die Aussage verweist auf `handbuch_infrastructure.md` als Quelle – das liegt außerhalb der geprüften Datei.

**Änderungsvorschlag:**
Den zweiten Satz als Verweis auf eine andere Dokumentation kennzeichnen, nicht als direkt aus dem Schema ableitbare Tatsache:

> `UNIQUE (config_key, version)` verhindert doppelte Versionen je Schlüssel. Die Auslesestrategie (aktuell gültiger Wert = höchste `version`-Zahl je Schlüssel) ist in `handbuch_infrastructure.md` beschrieben und nicht allein aus dem Schemacode ableitbar.

**Aussage:**
Migration 0002 schreibt beim Seeding zwei Beispieleinträge in `audit_log` mit `event_type = 'SEEDED'`.

**Status:**
korrekt

**Beleg:**
`migrations/0002_seed_defaults.sql` (zwei `INSERT INTO audit_log`-Blöcke mit `'SEEDED'`) [cite:6]

**Bewertung:**
Die beiden INSERT-Statements sind vorhanden: einer für `WORK_SCHEDULE_VERSION`-Einträge, einer für `SYSTEM_CONFIG`-Einträge, beide mit `event_type = 'SEEDED'`. Da 0002 fünf Wochenzeiteinträge und vier Konfigurationseinträge seedet, werden tatsächlich **neun** `audit_log`-Zeilen erzeugt (nicht „zwei"). Das Handbuch sagt jedoch nur „zwei Beispieleinträge" – das könnte sich auf die zwei INSERT-Statements (als Blöcke) beziehen, was der Formulierung nach mehrdeutig ist.

**Änderungsvorschlag:**
Zur Vermeidung von Missverständnissen präzisieren:

> Migration 0002 schreibt beim Seeding Einträge in `audit_log` mit `event_type = 'SEEDED'`: je einen Eintrag pro geseedeter Zeile in `work_schedule_versions` (5 Einträge) und `system_config` (4 Einträge), insgesamt 9 Zeilen.

**Aussage:**
Migration 0002 seedet Standard-Arbeitszeiten: Montag bis Mittwoch 07:30–18:00 Uhr, Donnerstag 07:30–14:00 Uhr, Freitag 07:30–16:00 Uhr, jeweils gültig ab 2026-01-01.

**Status:**
korrekt

**Beleg:**
`migrations/0002_seed_defaults.sql` [cite:6]

**Bewertung:**
Die fünf INSERT-Zeilen in `work_schedule_versions` entsprechen exakt diesen Werten (weekday 1–3: 18:00, weekday 4: 14:00, weekday 5: 16:00, alle mit `valid_from = '2026-01-01'`).

**Änderungsvorschlag:**
Kein Änderungsbedarf.

**Aussage:**
Migration 0002 seedet vier Startwerte in `system_config`: `app.timezone` (`"Europe/Berlin"`), `booking.grace_seconds_after_numpad_select` (`30`), `backup.nas_enabled` (`false`), `backup.nas_path` (`null`), jeweils mit `version = 1`.

**Status:**
korrekt

**Beleg:**
`migrations/0002_seed_defaults.sql` [cite:6]

**Bewertung:**
Alle vier Schlüssel-Wert-Paare und `version = 1` sind im SQL belegbar.

**Änderungsvorschlag:**
Kein Änderungsbedarf.

**Aussage:**
`system_events` wurde durch Migration 0006 vollständig neu angelegt, um `APPLICATION_ERROR` aufzunehmen.

**Status:**
korrekt

**Beleg:**
`migrations/0006_system_events_application_error.sql` (CREATE TABLE system_events_new, DROP TABLE system_events, RENAME) [cite:10]

**Bewertung:**
Der Table-Rebuild ist vollständig im SQL dokumentiert.

**Änderungsvorschlag:**
Kein Änderungsbedarf.

**Aussage:**
`APPLICATION_STOP` bezeichnet einen regulären oder fehlerinduzierten Prozessabbruch; `APPLICATION_ERROR` bezeichnet einen abgefangenen Fehler bei fortgesetztem Betrieb (z. B. unerwartete Ausnahme in der Terminal-UI-Schleife).

**Status:**
korrekt

**Beleg:**
`migrations/0006_system_events_application_error.sql`, Kommentarzeilen [cite:10]

**Bewertung:**
Der Kommentar im SQL lautet wortgleich: „APPLICATION_STOP = regulärer oder fehlerinduzierter Prozessabbruch; APPLICATION_ERROR = Fehler abgefangen, Prozess läuft weiter." Das Handbuch gibt diesen Inhalt korrekt wieder.

**Änderungsvorschlag:**
Kein Änderungsbedarf.

## Zusammenfassung der Befunde

| # | Aussage (Kurzform) | Status |
|---|---|---|
| 1 | 0001: 17 Tabellen | **inkorrekt** (16 Tabellen) |
| 2 | 0003 bereinigt beide Tabellen | korrekt |
| 3 | 0003 entfernt 4 Statuswerte aus `current_status` | korrekt |
| 4 | `MANUAL_ENTRY` bleibt in `booking_status_history` | korrekt |
| 5 | 0005 rebuildet wegen CHECK-Constraints | **inkorrekt** (wegen FK-Constraint) |
| 6 | Pauschalaussage: alle 4 Migrationen wegen CHECK | **inkorrekt** (0005: FK) |
| 7 | `supplements`-Constraint seit 0004 korrekt | korrekt |
| 8 | Vor 0004: gemeinsame `approved_*`-Felder | korrekt |
| 9 | `PRAGMA foreign_keys = ON` gilt für alle FK | **nicht verifizierbar** (verbindungsweit) |
| 10 | UNIQUE-Constraint + Auslesestrategie | korrekt / **nicht verifizierbar** (Strategie) |
| 11 | 0002 seedet zwei `audit_log`-Einträge | korrekt (mehrdeutig – tatsächlich 9 Zeilen) |
| 12 | 0002 seedet Standardarbeitszeiten korrekt | korrekt |
| 13 | 0002 seedet vier `system_config`-Werte korrekt | korrekt |
| 14 | 0006 rebuildet `system_events` für `APPLICATION_ERROR` | korrekt |
| 15 | Abgrenzung `APPLICATION_STOP` vs. `APPLICATION_ERROR` | korrekt |
