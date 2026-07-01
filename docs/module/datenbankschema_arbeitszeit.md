# Datenbankschema `arbeitszeit`

**Kapitel:** 6.1 (Ergänzung zu Infrastructure Layer)
**Version:** 1.0
**Stand:** Juli 2026
**Quelldateien:** `migrations/0001_schema.sql` bis `migrations/0006_system_events_application_error.sql`

## Zweck dieses Dokuments

Dieses Dokument beschreibt das SQLite-Schema von `arbeitszeit` exakt auf
Basis der gelesenen Migrationsdateien. Alle Tabellen, Spalten,
Constraints und Indizes sind direkt aus dem SQL-Quelltext übernommen,
nicht aus abgeleiteten oder vermuteten Zusammenhängen.

## Migrationsübersicht

| Version | Datei | Zweck |
| --- | --- | --- |
| 0001 | `0001_schema.sql` | Ursprüngliches Gesamtschema (17 Tabellen, 17 Indizes) |
| 0002 | `0002_seed_defaults.sql` | Standard-Wochenarbeitszeiten und System-Konfigurationswerte |
| 0003 | `0003_cleanup_booking_status.sql` | Bereinigung der Status-Werte in `time_bookings` und `booking_status_history` |
| 0004 | `0004_supplement_reject_fields_and_review_note.sql` | Trennung von Genehmigung und Ablehnung bei Nachträgen; Notizfeld für Prüffälle |
| 0005 | `0005_time_bookings_device_event_id.sql` | Verknüpfung von Buchungen mit Geräte-Ereignissen |
| 0006 | `0006_system_events_application_error.sql` | Neuer Ereignistyp `APPLICATION_ERROR` in `system_events` |

Jede Migration ist in `schema_migrations` mit ihrer vierstelligen
Versionsnummer und dem Anwendungszeitpunkt (`applied_at`) verzeichnet.

## Tabellen im finalen Zustand (nach Migration 0006)

### employees

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `personnel_no` | TEXT | NOT NULL, UNIQUE |
| `first_name` | TEXT | NOT NULL |
| `last_name` | TEXT | NOT NULL |
| `active` | INTEGER | NOT NULL, DEFAULT 1, CHECK IN (0, 1) |
| `employment_start` | TEXT | — |
| `employment_end` | TEXT | — |
| `created_at` | TEXT | NOT NULL |
| `updated_at` | TEXT | NOT NULL |

Zusätzlicher Tabellen-Constraint: `employment_end` muss NULL sein oder
größer/gleich `employment_start`.

### user_accounts

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `username` | TEXT | NOT NULL, UNIQUE |
| `password_hash` | TEXT | NOT NULL |
| `role` | TEXT | NOT NULL, CHECK IN ('EMPLOYEE', 'ADMIN', 'REVIEWER', 'TECH') |
| `employee_id` | INTEGER | FOREIGN KEY → `employees(id)` |
| `active` | INTEGER | NOT NULL, DEFAULT 1, CHECK IN (0, 1) |
| `created_at` | TEXT | NOT NULL |
| `updated_at` | TEXT | NOT NULL |

Fremdschlüssel `employee_id` mit `ON UPDATE RESTRICT ON DELETE RESTRICT`.

### rfid_cards

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `uid_hash` | TEXT | NOT NULL, UNIQUE |
| `employee_id` | INTEGER | NOT NULL, FOREIGN KEY → `employees(id)` |
| `status` | TEXT | NOT NULL, CHECK IN ('ACTIVE', 'INACTIVE', 'REPLACED', 'LOST') |
| `valid_from` | TEXT | NOT NULL |
| `valid_until` | TEXT | — |
| `replaced_by_card_id` | INTEGER | FOREIGN KEY → `rfid_cards(id)` (Selbstreferenz) |
| `created_at` | TEXT | NOT NULL |

Zusätzlicher Constraint: `valid_until` muss NULL sein oder
größer/gleich `valid_from`.

### terminals

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `terminal_code` | TEXT | NOT NULL, UNIQUE |
| `hostname` | TEXT | — |
| `location_text` | TEXT | — |
| `active` | INTEGER | NOT NULL, DEFAULT 1, CHECK IN (0, 1) |
| `created_at` | TEXT | NOT NULL |

### time_bookings

Diese Tabelle wurde durch Migration 0003 (Status-Bereinigung) und
Migration 0005 (`device_event_id`) jeweils vollständig neu angelegt,
da SQLite `CHECK`-Constraints nicht nachträglich per `ALTER TABLE`
ändern kann.

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `employee_id` | INTEGER | NOT NULL, FOREIGN KEY → `employees(id)` |
| `rfid_card_id` | INTEGER | FOREIGN KEY → `rfid_cards(id)` |
| `booking_type` | TEXT | NOT NULL, CHECK IN ('COME', 'GO', 'BREAK_START', 'BREAK_END') |
| `booked_at` | TEXT | NOT NULL |
| `source` | TEXT | NOT NULL, CHECK IN ('TERMINAL', 'MANUAL', 'IMPORT') |
| `terminal_id` | INTEGER | FOREIGN KEY → `terminals(id)` |
| `device_event_id` | INTEGER | FOREIGN KEY → `device_events(id)` (seit 0005) |
| `current_status` | TEXT | NOT NULL, CHECK IN ('OK', 'OPEN', 'WARN', 'NEEDS_REVIEW', 'CORRECTED', 'CLOSED_WITH_NOTE') |
| `note` | TEXT | — |
| `created_at` | TEXT | NOT NULL |

**Historischer Hinweis:** In Migration 0001 enthielt `current_status`
zusätzlich die Werte `POSSIBLE_BREAK_VIOLATION`,
`POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION` und
`MANUAL_ENTRY`. Migration 0003 hat diese entfernt, da vergleichbare
Sachverhalte seither ausschließlich über `review_cases` mit einer
`severity`-Einstufung abgebildet werden; die Herkunft einer Buchung
(manuell oder Terminal) wird über `source` abgebildet.

### booking_status_history

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `time_booking_id` | INTEGER | NOT NULL, FOREIGN KEY → `time_bookings(id)` |
| `old_status` | TEXT | — |
| `new_status` | TEXT | NOT NULL, CHECK IN ('OK', 'OPEN', 'WARN', 'NEEDS_REVIEW', 'CORRECTED', 'CLOSED_WITH_NOTE', 'MANUAL_ENTRY') |
| `reason` | TEXT | — |
| `changed_by_user_id` | INTEGER | FOREIGN KEY → `user_accounts(id)` |
| `changed_at` | TEXT | NOT NULL |

Anders als bei `time_bookings.current_status` bleibt `MANUAL_ENTRY`
hier seit Migration 0003 als zulässiger Wert erhalten, da es in dieser
Tabelle die Herkunft eines Statuswechsels kennzeichnet, nicht den
Buchungsstatus selbst.

### booking_corrections

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `time_booking_id` | INTEGER | NOT NULL, FOREIGN KEY → `time_bookings(id)` |
| `old_values_json` | TEXT | NOT NULL |
| `new_values_json` | TEXT | NOT NULL |
| `reason` | TEXT | NOT NULL |
| `corrected_by_user_id` | INTEGER | NOT NULL, FOREIGN KEY → `user_accounts(id)` |
| `corrected_at` | TEXT | NOT NULL |

### supplements

Durch Migration 0004 vollständig neu angelegt, um Genehmigung und
Ablehnung eines Nachtrags über getrennte Spaltenpaare abzubilden.

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `employee_id` | INTEGER | NOT NULL, FOREIGN KEY → `employees(id)` |
| `related_time_booking_id` | INTEGER | FOREIGN KEY → `time_bookings(id)` |
| `booking_type` | TEXT | NOT NULL, CHECK IN ('COME', 'GO', 'BREAK_START', 'BREAK_END') |
| `event_at` | TEXT | NOT NULL |
| `recorded_at` | TEXT | NOT NULL |
| `reason` | TEXT | NOT NULL |
| `recorded_by_user_id` | INTEGER | NOT NULL, FOREIGN KEY → `user_accounts(id)` |
| `approval_status` | TEXT | NOT NULL, CHECK IN ('PENDING', 'APPROVED', 'REJECTED') |
| `approved_by_user_id` | INTEGER | FOREIGN KEY → `user_accounts(id)` |
| `approved_at` | TEXT | — |
| `rejected_by_user_id` | INTEGER | FOREIGN KEY → `user_accounts(id)` (seit 0004) |
| `rejected_at` | TEXT | seit 0004 |

Tabellen-Constraint (seit 0004): Je nach `approval_status` müssen
genau die dazu passenden Genehmigungs- oder Ablehnungsfelder gesetzt
sein, alle anderen müssen NULL sein. Bei `PENDING` müssen alle vier
Felder NULL sein.

**Vor Migration 0004** existierte nur ein gemeinsames Feldpaar
(`approved_by_user_id`, `approved_at`), das sowohl für Genehmigungen
als auch für Ablehnungen verwendet wurde. Die Migration überträgt
bestehende Daten anhand von `approval_status` in die jeweils passenden
neuen Felder.

### review_cases

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `employee_id` | INTEGER | NOT NULL, FOREIGN KEY → `employees(id)` |
| `time_booking_id` | INTEGER | FOREIGN KEY → `time_bookings(id)` |
| `case_type` | TEXT | NOT NULL, CHECK IN (siehe unten) |
| `status` | TEXT | NOT NULL, CHECK IN ('OPEN', 'IN_REVIEW', 'RESOLVED', 'CLOSED_WITH_NOTE') |
| `severity` | TEXT | NOT NULL, CHECK IN ('INFO', 'WARN', 'CRITICAL') |
| `detected_at` | TEXT | NOT NULL |
| `description` | TEXT | NOT NULL |
| `closed_at` | TEXT | — |
| `closed_by_user_id` | INTEGER | FOREIGN KEY → `user_accounts(id)` |
| `note` | TEXT | seit Migration 0004 |

Zulässige Werte für `case_type`: `OPEN_WORK_PHASE`, `OPEN_BREAK_PHASE`,
`OUTSIDE_SCHEDULE_WINDOW`, `POSSIBLE_BREAK_VIOLATION`,
`POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION`,
`IMPLAUSIBLE_SEQUENCE`, `UNKNOWN_CARD_ATTEMPT`, `INACTIVE_CARD_ATTEMPT`,
`TIME_ANOMALY`, `MANUAL_ENTRY_REVIEW`.

Tabellen-Constraint: Bei Status `OPEN` oder `IN_REVIEW` müssen
`closed_at` und `closed_by_user_id` NULL sein; bei `RESOLVED` oder
`CLOSED_WITH_NOTE` müssen beide gesetzt sein.

### review_case_actions

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `review_case_id` | INTEGER | NOT NULL, FOREIGN KEY → `review_cases(id)` |
| `action_type` | TEXT | NOT NULL, CHECK IN ('CREATED', 'COMMENT_ADDED', 'STATUS_CHANGED', 'CORRECTION_LINKED', 'SUPPLEMENT_LINKED', 'CLOSED', 'REOPENED') |
| `note` | TEXT | — |
| `performed_by_user_id` | INTEGER | NOT NULL, FOREIGN KEY → `user_accounts(id)` |
| `created_at` | TEXT | NOT NULL |

### work_schedule_versions

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `scope_type` | TEXT | NOT NULL, CHECK IN ('GLOBAL', 'EMPLOYEE') |
| `scope_employee_id` | INTEGER | FOREIGN KEY → `employees(id)` |
| `weekday` | INTEGER | NOT NULL, CHECK BETWEEN 1 AND 7 |
| `start_time` | TEXT | NOT NULL |
| `end_time` | TEXT | NOT NULL |
| `valid_from` | TEXT | NOT NULL |
| `valid_until` | TEXT | — |
| `change_origin` | TEXT | NOT NULL, CHECK IN ('SYSTEM_SEED', 'ADMIN_UI', 'MIGRATION') |
| `changed_by_user_id` | INTEGER | FOREIGN KEY → `user_accounts(id)` |
| `changed_at` | TEXT | NOT NULL |
| `reason` | TEXT | — |

Drei Tabellen-Constraints: `scope_employee_id` ist NULL bei `GLOBAL`
und NOT NULL bei `EMPLOYEE`; `valid_until` ist NULL oder größer/gleich
`valid_from`; bei `change_origin = 'SYSTEM_SEED'` muss
`changed_by_user_id` NULL sein, bei `'ADMIN_UI'` muss es gesetzt sein,
bei `'MIGRATION'` ist beides zulässig.

Migration 0002 befüllt diese Tabelle mit den Standard-Arbeitszeiten:
Montag bis Mittwoch 07:30–18:00 Uhr, Donnerstag 07:30–14:00 Uhr,
Freitag 07:30–16:00 Uhr, jeweils gültig ab dem 2026-01-01 mit
`change_origin = 'SYSTEM_SEED'`.

### system_config

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `config_key` | TEXT | NOT NULL |
| `config_value_json` | TEXT | NOT NULL |
| `version` | INTEGER | NOT NULL |
| `change_origin` | TEXT | NOT NULL, CHECK IN ('SYSTEM_SEED', 'ADMIN_UI', 'MIGRATION') |
| `changed_by_user_id` | INTEGER | FOREIGN KEY → `user_accounts(id)` |
| `changed_at` | TEXT | NOT NULL |
| `reason` | TEXT | — |

`UNIQUE (config_key, version)` stellt die in
`handbuch_infrastructure.md` beschriebene Versionierungslogik sicher:
Der aktuell gültige Wert ist stets der Datensatz mit dem höchsten
`version`-Wert je Schlüssel.

Migration 0002 seedet vier Startwerte: `app.timezone`
(`"Europe/Berlin"`), `booking.grace_seconds_after_numpad_select`
(`30`), `backup.nas_enabled` (`false`) und `backup.nas_path` (`null`),
jeweils mit `version = 1` und `change_origin = 'SYSTEM_SEED'`.

### device_events

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `event_type` | TEXT | NOT NULL, CHECK IN ('NUMPAD_INPUT', 'RFID_SCAN', 'UNKNOWN_CARD', 'INACTIVE_CARD', 'CARD_ASSIGNMENT_FAILURE', 'BOOKING_ACCEPTED', 'BOOKING_REJECTED') |
| `terminal_id` | INTEGER | FOREIGN KEY → `terminals(id)` |
| `rfid_uid_hash` | TEXT | — |
| `payload_json` | TEXT | — |
| `occurred_at` | TEXT | NOT NULL |
| `related_time_booking_id` | INTEGER | FOREIGN KEY → `time_bookings(id)` |

Diese Tabelle wird seit Migration 0005 zusätzlich über
`time_bookings.device_event_id` referenziert und dokumentiert damit,
welches konkrete Hardware-Ereignis zu einer Buchung geführt hat.

### system_events

Diese Tabelle wurde durch Migration 0006 vollständig neu angelegt, um
den zusätzlichen Ereignistyp `APPLICATION_ERROR` aufzunehmen.

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `event_type` | TEXT | NOT NULL, CHECK IN (siehe unten) |
| `source` | TEXT | NOT NULL |
| `severity` | TEXT | NOT NULL, CHECK IN ('INFO', 'WARN', 'ERROR') |
| `event_at` | TEXT | NOT NULL |
| `details_json` | TEXT | — |
| `related_object_type` | TEXT | — |
| `related_object_id` | INTEGER | — |

Zulässige Werte für `event_type`: `SELFTEST_OK`, `SELFTEST_FAIL`,
`DB_BACKUP_CREATED`, `DB_BACKUP_FAILED`, `RESTORE_STARTED`,
`RESTORE_FINISHED`, `RESTORE_FAILED`, `NAS_REACHABLE`,
`NAS_UNREACHABLE`, `TIME_JUMP_DETECTED`,
`MANUAL_TIME_CHANGE_DETECTED`, `DEVICE_UNAVAILABLE`,
`DEVICE_RECOVERED`, `APPLICATION_START`, `APPLICATION_STOP` und (seit
Migration 0006) `APPLICATION_ERROR`.

Laut Kommentar in `0006_system_events_application_error.sql` gilt
folgende fachliche Abgrenzung: `APPLICATION_STOP` bezeichnet einen
regulären oder fehlerinduzierten Prozessabbruch, während
`APPLICATION_ERROR` einen abgefangenen Fehler bei fortgesetztem
Betrieb protokolliert (zum Beispiel eine unerwartete Ausnahme in der
Terminal-UI-Schleife, ohne dass der Prozess beendet wird).

### audit_log

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY |
| `event_type` | TEXT | NOT NULL |
| `object_type` | TEXT | NOT NULL |
| `object_id` | INTEGER | NOT NULL |
| `user_id` | INTEGER | FOREIGN KEY → `user_accounts(id)` |
| `employee_id` | INTEGER | FOREIGN KEY → `employees(id)` |
| `event_at` | TEXT | NOT NULL |
| `details_json` | TEXT | NOT NULL |

Anders als bei `system_events` ist `event_type` hier nicht über einen
`CHECK`-Constraint eingeschränkt, sondern ein freier Text. Migration
0002 schreibt bereits beim Seeding zwei Beispieleinträge mit
`event_type = 'SEEDED'` für die initialen Datensätze in
`work_schedule_versions` und `system_config`.

### schema_migrations

| Spalte | Typ | Constraint |
| --- | --- | --- |
| `version` | TEXT | NOT NULL, PRIMARY KEY |
| `applied_at` | TEXT | NOT NULL |

## Indizes im finalen Zustand

| Index | Tabelle | Spalten |
| --- | --- | --- |
| `idx_user_accounts_employee_id` | `user_accounts` | `employee_id` |
| `idx_rfid_cards_employee_status` | `rfid_cards` | `employee_id`, `status` |
| `idx_time_bookings_employee_booked_at` | `time_bookings` | `employee_id`, `booked_at` |
| `idx_time_bookings_status_booked_at` | `time_bookings` | `current_status`, `booked_at` |
| `idx_booking_status_history_booking_changed_at` | `booking_status_history` | `time_booking_id`, `changed_at` |
| `idx_booking_corrections_booking_corrected_at` | `booking_corrections` | `time_booking_id`, `corrected_at` |
| `idx_supplements_employee_event_at` | `supplements` | `employee_id`, `event_at` |
| `idx_supplements_approval_status` | `supplements` | `approval_status`, `recorded_at` |
| `idx_review_cases_status_detected_at` | `review_cases` | `status`, `detected_at` |
| `idx_review_cases_employee_detected_at` | `review_cases` | `employee_id`, `detected_at` |
| `idx_review_case_actions_case_created_at` | `review_case_actions` | `review_case_id`, `created_at` |
| `idx_work_schedule_versions_scope_weekday_valid_from` | `work_schedule_versions` | `scope_type`, `scope_employee_id`, `weekday`, `valid_from` |
| `idx_system_config_key_version` | `system_config` | `config_key`, `version` |
| `idx_device_events_occurred_at` | `device_events` | `occurred_at` |
| `idx_system_events_event_at` | `system_events` | `event_at` |
| `idx_audit_log_object_event_at` | `audit_log` | `object_type`, `object_id`, `event_at` |
| `idx_audit_log_employee_event_at` | `audit_log` | `employee_id`, `event_at` |

## Technisches Muster: Table-Rebuild bei CHECK-Änderungen

Migrationen 0003, 0004, 0005 und 0006 folgen alle demselben Muster,
weil SQLite bestehende `CHECK`-Constraints nicht per `ALTER TABLE`
ändern kann:

1. Neue Tabelle mit Suffix `_new` und geändertem Schema anlegen.
2. Daten aus der alten Tabelle per `INSERT INTO ... SELECT` übertragen
   (bei 0004 mit `CASE`-Logik zur Datenumverteilung).
3. Alte Tabelle löschen (`DROP TABLE`).
4. Neue Tabelle auf den ursprünglichen Namen umbenennen
   (`ALTER TABLE ... RENAME TO`).
5. Zugehörige Indizes neu anlegen, da sie beim `DROP TABLE` mit
   gelöscht wurden.

Migration 0004 nutzt dieses Muster nur für `supplements`; die
Ergänzung von `note` in `review_cases` erfolgt dort direkt per
`ALTER TABLE review_cases ADD COLUMN note TEXT`, da das Hinzufügen
einer nullable Spalte ohne `CHECK`-Constraint in SQLite ohne
Table-Rebuild möglich ist.

## Globale Einstellung

`PRAGMA foreign_keys = ON;` wird in `0001_schema.sql` einmalig gesetzt
und gilt für die referenzielle Integrität aller Fremdschlüssel im
Schema. Alle Fremdschlüssel im gesamten Schema verwenden durchgängig
`ON UPDATE RESTRICT ON DELETE RESTRICT` — ein Löschen oder Ändern
referenzierter Datensätze wird von der Datenbank grundsätzlich
verweigert, solange abhängige Datensätze existieren.
