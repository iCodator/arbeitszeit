# Implementierungsplan: arbeitszeit

## Kontext

Die Dokumente unter `docs/informelles/` dokumentieren eine vollständige Design-Session für das Zeiterfassungssystem. Sie enthalten die wesentlichen Entscheidungen zu Domänenmodell, Datenbankschema, Projektstruktur, Use-Cases, Prüfregeln, Export, Betrieb und Testabdeckung.[cite:7]

**Verbindliche Referenzdokumente:** `docs/pflichtenheft_arbeitszeit_v5.md`, `docs/regelwerk_arbeitszeit_v5.md`, `docs/anlage_einhaltung_pflichtenheft_v2.md`.[cite:8][cite:9][cite:10]

Dieses Dokument beschreibt den bekannten technischen Umsetzungs- und Planungsstand des Projekts. Organisatorische, datenschutzrechtliche und betriebliche Pflichten der Praxis werden ausdrücklich benannt, soweit sie laut Pflichtenheft v5, Regelwerk v5 und Anlage v2 nicht allein durch Code erfüllt werden können.[cite:8][cite:9][cite:10]

---

## Ergänzende Leitplanken aus den Referenzdokumenten v5/v2

### Rechts- und Regelrahmen

Die Systemauslegung stützt sich auf die Pflicht zu einem objektiven, verlässlichen und zugänglichen Zeiterfassungssystem sowie auf die arbeitszeitrechtlichen Anforderungen zu Höchstarbeitszeit, Ruhepausen und Ruhezeit. Pflichtenheft v5 ergänzt dies ausdrücklich um das Arbeitsschutzgesetz als organisatorische Grundlage des Arbeitgebers für geeignete Schutz- und Erfassungsmaßnahmen.[cite:8]

Für den Betrieb in der Zahnarztpraxis ist zusätzlich die IT-Sicherheitsrichtlinie nach § 75b SGB V zu beachten. Rollen, Rechte, Backup, Protokollierung, Schutz der Praxis-IT und die Einbindung in das Praxis-IT-Sicherheitskonzept sind daher nicht nur technische, sondern auch organisatorische Anforderungen.[cite:8][cite:9][cite:10]

### Datenschutz, lokale Verarbeitung und Backup-Architektur

Die produktive Verarbeitung von Arbeitszeitdaten erfolgt ausschließlich lokal in der Praxis-IT-Infrastruktur. Externe Cloud-Dienste sind nicht für produktive Verarbeitung oder Auswertung vorgesehen.[cite:8][cite:9]

Verschlüsselte Backups dürfen optional zusätzlich in einem externen Cloud-Speicher abgelegt werden, wenn die Verschlüsselung clientseitig vor Verlassen der Praxisumgebung erfolgt und der Cloud-Anbieter nur als technisches Backup-Medium dient. Dafür sind außerhalb dieses Dokuments insbesondere AV-Vertrag, Schlüsselverwaltung, Speicherortprüfung, TOM-Dokumentation und Rotationskonzept zu regeln.[cite:8][cite:9][cite:10]

### Offene Praxis- und Nachweispflichten

Die Anlage Einhaltung Pflichtenheft v2 bewertet das Projekt fachlich als weit fortgeschritten, benennt aber weiterhin offene organisatorische und formale Nachweise. Dazu gehören insbesondere eine schriftlich verabschiedete Betriebsdokumentation zu Export, Rechten, Aufbewahrung, Löschregeln, Backup und Restore, eine revisionsfeste Testmatrix, die Entscheidung zum produktiven `device_events`-/`device_event_id`-Pfad sowie die organisatorische Zuordnung von Rollen, Freigabeverantwortungen, Prüfintervallen und IT-Sicherheitsverantwortlichkeiten.[cite:10]

Diese Punkte werden in den fachlichen Phasen unten dort aufgegriffen, wo sie technischen Bezug haben. Soweit sie rein organisatorisch sind, werden sie als externe Auflagen gekennzeichnet und nicht fälschlich als bereits durch Code erfüllt dargestellt.[cite:10]

### Benutzer- und Rollenverwaltung (Pflichtenheft v5 §7.9 / Regelwerk v5 §16, §16a)

Pflichtenheft v5 §7.9 (neu gegenüber v4) macht die Admin-CLI-basierte Benutzerkontenverwaltung zur verbindlichen Anforderung. Direktes SQL darf kein regulärer Betriebsprozess sein.

Regelwerk v5 §16a (neu) definiert Benutzerkonten als eigenständige Zugangsobjekte, die optional einem Mitarbeiterdatensatz zugeordnet sein können. Doppelte Benutzernamen sind unzulässig; inaktive Konten dürfen keine administrativen oder prüfenden Aktionen ausführen.

Implementiert (`admin_cli users`-Modul, Phase 5+):

- `users add --username <u> --role <ADMIN|REVIEWER|TECH> [--employee-id <id>] [--password <pw>]`
- `users list`
- `users deactivate --user-id <id>`
- Passwort-Hashing via `hashlib.pbkdf2_hmac` (stdlib, salt:hash-Format)
- Audit-Events `USER_ACCOUNT_CREATED`, `USER_ACCOUNT_DEACTIVATED`

Noch nicht implementiert — offene Punkte gemäß Pflichtenheft v5 §7.9 und §16 Testanforderungen:

- `users reactivate --user-id <id>` (Reaktivierung deaktivierter Konten)
- `users change-role --user-id <id> --role <NEUE_ROLLE>` (Rollenwechsel)
- Bootstrap-Prozess: Ersteinrichtung des ersten Administratorkontos über die CLI, solange noch kein aktives Administratorkonto vorhanden ist. (Pflichtenheft v5 §7.9: „dieser Bootstrap-Prozess darf nur nutzbar sein, solange noch kein aktives Administratorkonto vorhanden ist")

---

## Was die Dokumente festgelegt haben

### 01 – Fachlicher Kern
- Zentrum ist die **unveränderliche Buchung** (`Zeitbuchung`), nicht die „Tagesarbeitszeit“.[cite:7]
- Offene Fälle werden **nicht automatisch geschlossen** – immer explizite Klärung.[cite:7][cite:9]
- Trennung: TerminalEreignis → Zeitbuchung (erst nach Prüfung). Der vollständige produktive Verkettungspfad über `device_events` ist architektonisch vorgesehen, aber noch nicht operativ aktiviert.[cite:7][cite:10]

### 02 – ER-Modell (5 Ebenen)

| Ebene | Entitäten |
| --- | --- |
| Person | `employees`, `user_accounts`, `rfid_cards` |
| Erfassung | `terminals`, `time_bookings`, `device_events` |
| Prüfung | `review_cases`, `review_case_actions`, `booking_status_history` |
| Änderung | `booking_corrections`, `supplements`, `work_schedule_versions` |
| Nachweis | `audit_log`, `system_events`, `system_config` |

Die Tabellenstruktur deckt die im Pflichtenheft geforderten fachlichen Kernstrukturen ab und erweitert sie um Betriebs- und Nachweisobjekte. Die Anlage v2 bewertet das Datenmodell als weitgehend vollständig nachgewiesen.[cite:7][cite:8][cite:10]

### 03–09 – SQLite DDL

- **15 fachliche Tabellen** mit FK-Constraints, CHECK-Constraints, Indizes (+ `schema_migrations` = 16 Tabellen in `0001_schema.sql`).[cite:7]
- `work_schedule_versions` + `system_config`: Herkunftsfeld `change_origin` (`SYSTEM_SEED` / `ADMIN_UI` / `MIGRATION`) – kein künstlicher Bootstrap-User.[cite:7]
- Komplexe Prüfregeln liegen bewusst in Python-Domänenlogik und nicht in SQLite.[cite:7]
- `system_events` dient als Nachweis für Betriebsereignisse einschließlich Selbsttest, Backup/Restore und Systemzeitprotokollierung.[cite:7][cite:8]
- **Aufbewahrungsprinzip:** Fachlich relevante Buchungen werden nicht physisch gelöscht; Klärung erfolgt über Status, Korrekturen oder Archivierung. Die Mindestaufbewahrung beträgt 2 Jahre; Backups, Exportdateien und Berichte unterliegen zusätzlich einem gesondert festzulegenden Archivierungs- und Löschkonzept einschließlich Rotation.[cite:7][cite:8][cite:9][cite:10]

### 11 – 4 Kern-Use-Cases

| Use-Case | Transaktion umfasst |
| --- | --- |
| `buchen()` | `device_events`, `time_bookings`, `booking_status_history`, `review_cases`, `audit_log` |
| `nachtrag_anlegen()` | `supplements`, `review_cases`, `audit_log` |
| `korrektur_anlegen()` | `booking_corrections`, `time_bookings`, `booking_status_history`, `review_cases`, `audit_log` |
| `regelarbeitszeit_ändern()` | `work_schedule_versions` (alt schließen + neu), `audit_log` |

Hinweis: Die Transaktionskette für `device_events` ist im Zielschnitt beschrieben, aber laut aktuellem Umsetzungsstand noch nicht vollständig im Produktionspfad aktiv. Dieser Punkt bleibt als offene Architektur- und Nachweisfrage bestehen.[cite:7][cite:10]

---

## Implementierungsreihenfolge

### Phase 1 – Grundgerüst ✓ abgeschlossen

Originärer Phase-1-Lieferumfang (Migrationen 0001/0002, 6 Tests):
- `pyproject.toml`, `src/`-Layout, `tests/`, `.gitignore`, `.python-version`.[cite:7]
- `migrations/0001_schema.sql` – finale DDL, enthält `schema_migrations`.[cite:7]
- `migrations/0002_seed_defaults.sql` – Regelzeiten + System-Config-Defaults.[cite:7]
- `infrastructure/db/connection.py` – `isolation_level=None`, `PRAGMA foreign_keys = ON`, `row_factory`.[cite:7]
- `infrastructure/db/migrations.py` – `executescript()` mit `BEGIN/COMMIT`, Versionsvalidierung vor f-String.[cite:7]
- `scripts/init_db.py`.[cite:7]
- `tests/test_migrations.py` – ursprünglich 6 Testfälle für 0001/0002.[cite:7]

Spätere Nachträge auf demselben Fundament (nicht Teil des Phase-1-Abschlusses):
- `migrations/0003_cleanup_booking_status.sql` – Status-CHECK bereinigt (Phase 4). [cite:7]
- `migrations/0004_supplement_reject_fields_and_review_note.sql` – `rejected_by_user_id`/`rejected_at` + `note`-Feld (Phase 4). [cite:7]
- `migrations/0005_time_bookings_device_event_id.sql` – `device_event_id` FK (Phase 4). [cite:7]
- `migrations/0006_system_events_application_error.sql` – `APPLICATION_ERROR` als `event_type` (Phase 5). [cite:7]
- `tests/test_migrations.py` – zusätzliche Tests für 0003–0006.[cite:7]

Heutiger Gesamtstand des Testmoduls: 12 Tests für die Migrationskette 0001–0006.[cite:7]

---

### Phase 2 – Domäne ✓ abgeschlossen

Umgesetzt unter `src/arbeitszeit/domain/`.[cite:7]

**`enums.py`** — 11 `StrEnum`-Klassen: `BookingType`, `BookingStatus`, `ReviewCaseType`, `ReviewCaseStatus`, `ReviewSeverity`, `CardStatus`, `UserRole`, `BookingSource`, `ChangeOrigin`, `ApprovalStatus`, `ScopeType`.[cite:7]

**`errors.py`** — `DomainError`-Basis + 9 Subklassen: `UnknownCardError`, `InactiveCardError`, `InactiveEmployeeError`, `InvalidBookingSequenceError`, `OpenPhaseConflictError`, `PermissionDeniedError`, `ValidationError`, `NotFoundError`, `ConflictError`.[cite:7]

**`entities.py`** — 9 frozen `@dataclass`-Entitäten mit fachlichen Invarianten, darunter `TimeBooking`, `WorkScheduleVersion`, `ReviewCase`, `Supplement`, `BookingCorrection` und `AuditLogEntry`.[cite:7]

**`services/booking_rules.py`** — `validate_booking_sequence()`, `ValidationResult`.[cite:7]

**`services/compliance_checks.py`** — `check_break_compliance()`, `check_max_hours()`, `check_rest_period()`, `ComplianceFlag`.[cite:7]

V4-relevant bleibt: Die arbeitszeitrechtlichen Prüfungen orientieren sich an den im Pflichtenheft genannten Tagesanforderungen. Eine mögliche spätere Erweiterung um Wochenprüfungen ist dokumentarisch vorgesehen, aber kein aktueller Implementierungsbestandteil.[cite:8][cite:9]

V4- und Regelwerk-konforme Statusmodellierung:
- `POSSIBLE_*`-Prüflagen werden als `ReviewCaseType` modelliert.[cite:7][cite:9]
- `MANUAL_ENTRY` wird als `BookingSource.MANUAL` modelliert.[cite:7][cite:9]
- `report_queries.py` ist die zentrale Wahrheitsquelle für Berichte, Pflichtauswertungen, Filterlogik und Projektionen; direkte abweichende Ad-hoc-Queries sind architektonisch unzulässig.[cite:7][cite:9]

**`ports/repositories.py`** — 10 `Protocol`-Interfaces für Repositories der Entitäten und Aggregate.[cite:7]

**Tests** (63 gesamt, alle grün):
- `tests/domain/test_booking_rules.py` – 10 Tests.[cite:7]
- `tests/domain/test_compliance_checks.py` – 9 Tests.[cite:7]
- `tests/domain/test_entities.py` – 42 Invariantentests.[cite:7]
- `tests/domain/test_audit_events.py` – 2 Tests.[cite:7]

---

### Phase 3 – Application ✓ abgeschlossen

#### Architekturentscheidungen

**BookingStatus-Semantik** — Status beschreibt die einzelne Buchung, nicht den Tagesstatus. Die definierten Zustände `OPEN`, `OK`, `WARN`, `NEEDS_REVIEW`, `CORRECTED` und `CLOSED_WITH_NOTE` entsprechen den verbindlichen Statusvorgaben aus Pflichtenheft und Regelwerk.[cite:7][cite:8][cite:9]

**`booking_status_history`** — Infrastruktur-Seiteneffekt über `time_booking_repo.set_status()`; kein eigenes History-Repository in der Application-Schicht.[cite:7]

**`device_event_id`** — Verantwortungsteilung:
- Hardware-/Infrastruktur-Schicht erzeugt `device_events` vor Use-Case-Aufruf.[cite:7]
- `BookCommand.device_event_id: int | None` wird an `TimeBooking.device_event_id` durchgereicht.[cite:7]
- Die betriebliche End-to-End-Verkettung ist vorbereitet, aber laut aktuellem Stand noch nicht produktiv geschlossen. Dieser Punkt bleibt als offener Architekturpunkt markiert und entspricht der Bewertung in Anlage v2.[cite:7][cite:10]

**Autorisierungsmuster** — Rollenprüfung in schreibenden Use Cases gemäß Pflichtenheft v5 §5 und Regelwerk v5 §16.[cite:7][cite:8][cite:9]

| Use Case | Erlaubte Rollen | Prüf-ID |
| --- | --- | --- |
| `RegisterSupplementUseCase` | ADMIN, REVIEWER | `recorded_by_user_id` |
| `ApproveSupplementUseCase` | REVIEWER, ADMIN | `approving_user_id` |
| `RejectSupplementUseCase` | REVIEWER, ADMIN | `rejected_by_user_id` |
| `CorrectBookingUseCase` | ADMIN, REVIEWER | `corrected_by_user_id` |
| `ManageWorkScheduleUseCase` | ADMIN | `changed_by_user_id` |
| Backup/Restore | TECH, ADMIN | Betriebsebene |

#### Zielstruktur

```text
src/arbeitszeit/application/
├── __init__.py
├── unit_of_work.py
├── commands.py
├── results.py
└── use_cases/
    ├── __init__.py
    ├── manage_work_schedule.py
    ├── register_supplement.py
    ├── correct_booking.py
    └── book_time.py
```

Die in Phase 3 festgelegten Commands, Results, Fakes und Use Cases entsprechen dem dokumentierten Fachmodell und den Prüfregeln. Die in Pflichtenheft v5 geforderten Kernabläufe, Korrektur-/Nachtragsmechanismen und Prüfpfade sind damit in der Anwendungslogik abgebildet.[cite:7][cite:8]

---

### Phase 4 – Infrastruktur ✓ vollständig abgeschlossen

Phase 4 schließt Datenbank-Integration, echte Repositorys, Unit of Work, Backup, Export, Pflichtauswertungen und Selbsttest. Die technische Umsetzung deckt damit große Teile von Pflichtenheft v5 §7.11–§7.13, §9.3, §12 und §14 ab.[cite:7][cite:8]

Wesentliche Punkte:
- `SQLiteUnitOfWork` mit konsequenter commit-or-rollback-Semantik.[cite:7]
- 10 SQLite-Repositories mit Parameterized Statements, Roundtrips und Scope-/Statuslogik.[cite:7]
- `system_events` für Backup, Restore, Selbsttest und später Systemzeitabweichungen.[cite:7]
- `report_queries.py` als zentrale Ableitungsschicht für CSV, PDF und Pflichtauswertungen.[cite:7][cite:9]
- `SQLiteBackupService` mit NAS-Sync, Restore-Test, Integritätsprüfung und optionalem Mitsichern von Exportdateien.[cite:7]

**V4-/Anlage-v2-relevante Klarstellung:** Die technische Backup-Architektur ist stark, bildet aber nicht automatisch alle organisatorischen und datenschutzrechtlichen Zusatzpflichten ab. Für lokale und optionale verschlüsselte Cloud-Backups sind zusätzlich schriftliche Regelungen zu Schlüsseln, Speicherorten, AV-Vertrag, Restore-Freigabe und Rotation erforderlich; diese liegen außerhalb des Codes und bleiben laut Anlage v2 offene Nachweispunkte.[cite:8][cite:9][cite:10]

**Systemzeitprotokollierung:** Die ursprünglich offene V3-/V4-Anforderung aus Pflichtenheft §9.3 und Regelwerk §21 wurde später geschlossen. Zeitsprünge und manuelle Uhrzeitänderungen werden über `time_monitor.py` und `system_events` protokolliert.[cite:7][cite:8][cite:9]

---

### Phase 5 – Präsentation ✓ vollständig abgeschlossen

Die Präsentationsschicht umfasst `presentation/terminal_ui/` und `presentation/admin_cli/`. Damit sind Betriebsfunktionen, Buchungsfluss, Berichte, Pflichtauswertungen und Systemcheck in benutzbarer Form zugänglich.[cite:7]

Wesentliche Punkte:
- Terminal-UI mit `process_booking()`, `format_feedback()`, Systemcheck beim Start und Fehlerprotokollierung.[cite:7]
- Admin-CLI mit Befehlen für Mitarbeiter, Karten, Buchungen, Regelzeiten, Reports und Systemfunktionen.[cite:7]
- Admin-CLI `users`-Gruppe (Pflichtenheft v5 §7.9): `users add`, `users list`, `users deactivate`. Passwort-Hashing via `hashlib.pbkdf2_hmac`. Audit-Events `USER_ACCOUNT_CREATED`, `USER_ACCOUNT_DEACTIVATED` im Audit-Log. Implementiert nach Phase-5-Abschluss als direktes Folge-Increment zu §7.9.[cite:8]
- Pflichtauswertungen sind in der Anwendung einsehbar und exportierbar, wie es Pflichtenheft v5 §7.13 verlangt.[cite:7][cite:8]
- Systemzeitprotokollierung ist in den Loop integriert und damit auch betrieblich angebunden.[cite:7]

**Offener Architekturpunkt – `device_event_id`-Verkettung:**
Die Spalte `time_bookings.device_event_id` ist im Schema vorhanden. Die vollständige operative Kette, bei der die Hardware-Schicht vor `process_booking()` einen `device_events`-Datensatz anlegt und dessen ID bis zur Buchung persistiert, ist nach aktuellem Stand noch nicht im Produktionspfad aktiviert. Dieser Punkt ist unverändert offen und bleibt für eine lückenlose Ereignisherkunft relevant.[cite:7][cite:10]

---

## Testaufteilung

| Verzeichnis | Inhalt |
| --- | --- |
| `tests/domain/` | Domänenregeln, Invarianten (Phase 2) |
| `tests/application/` | Use-Case-Tests mit Fake-Repositories (Phase 3) |
| `tests/integration/` | Repositorys, Export, Systemcheck, Zeitmonitor gegen echte SQLite-DB (Phase 4/5) |
| `tests/e2e/` | Vollständige Abläufe: Buchen, Nachtrag, Backup/Restore (Phase 4/5) |
| `tests/test_migrations.py` | Migrationsrunner |

Die vorhandene Testdokumentation weist die Pflichtszenarien fachlich gut zu. Anlage v2 fordert darüber hinaus eine **revisionsfeste Testmatrix**, die Muss-Anforderungen und Abnahmekriterien direkt einzelnen Tests zuordnet. Diese Matrix ist nicht Teil des vorliegenden Dokuments und bleibt als gesonderter Nachweispunkt offen.[cite:7][cite:10]

## V5-/V2-Abgleich: offene Punkte und externe Auflagen

Die folgenden Punkte sind nach dem aktuellen Stand **nicht zu überspringen** und bewusst als offen oder extern gekennzeichnet, weil sie laut Referenzdokumenten nicht allein durch den implementierten Code als erledigt gelten dürfen:[cite:8][cite:9][cite:10]

- Schriftlich verabschiedete Betriebsdokumentation zu Exportverzeichnis, Dateirechten, Aufbewahrung, Löschregeln, Backup und Restore.[cite:10]
- Revisionsfeste Testmatrix mit direkter Zuordnung von Muss-Anforderungen und Abnahmekriterien zu konkreten Tests.[cite:10]
- Entscheidung und vollständige produktive Umsetzung des `device_events`-/`device_event_id`-Pfads.[cite:7][cite:10]
- Organisatorische Zuordnung von Rollen, Freigabeverantwortungen, Prüfintervallen und IT-Sicherheitsverantwortlichkeiten in der Praxis.[cite:8][cite:9][cite:10]
- Datenschutz- und Backup-Unterlagen der Praxis für AV-Vertrag, Schlüsselverwaltung, Speicherorte, TOM, Rotationskonzept und Restore-Freigabe.[cite:8][cite:9][cite:10]
- Formale Einbindung des Systems in das Praxis-IT-Sicherheitskonzept nach § 75b SGB V.[cite:8][cite:9][cite:10]
- Optionale Cloud-Backup-Nutzung nur mit vorgelagerter clientseitiger Verschlüsselung und sauber dokumentierter datenschutzrechtlicher Grundlage; eine operative Cloud-Backup-Implementierung ist in diesem Plan nicht beschrieben.[cite:8][cite:9]
- `users reactivate`: Reaktivierung deaktivierter Benutzerkonten (Pflichtenheft v5 §7.9, Regelwerk v5 §16). Noch nicht implementiert.[cite:8][cite:9]
- `users change-role`: Rollenwechsel eines bestehenden Benutzerkontos (Pflichtenheft v5 §7.9, Regelwerk v5 §16). Audit-Event `USER_ACCOUNT_ROLE_CHANGED` erforderlich. Noch nicht implementiert.[cite:8][cite:9]
- Bootstrap-Prozess: Ersteinrichtung des ersten Administratorkontos über die CLI, solange noch kein aktives Administratorkonto vorhanden ist (Pflichtenheft v5 §7.9). Aktuell nur per direktem SQL möglich; kein betriebsprozess-tauglicher Weg vorhanden. Noch nicht implementiert.[cite:8][cite:9]

## Pflichtenheft v5 §16 Testpflicht-Abdeckung

| Pflichtszenario | Abdeckung | Status |
| --- | --- | --- |
| mehr als 6h ohne Pause | `tests/domain/test_compliance_checks.py` | ✓ |
| mehr als 9h ohne ausreichende Gesamtpause | `tests/domain/test_compliance_checks.py` | ✓ |
| Arbeitszeit über 8h | `tests/domain/test_compliance_checks.py` + `tests/application/test_book_time.py` | ✓ |
| Arbeitszeit über 10h | `tests/domain/test_compliance_checks.py` + `tests/application/test_book_time.py` | ✓ |
| Unterschreitung Ruhezeit (<11h) | `tests/application/test_book_time.py` | ✓ |
| Systemzeitabweichung | `tests/integration/test_time_monitor.py` | ✓ |
| Notfallnachtrag | `tests/application/test_register_supplement.py` | ✓ |
| Restore-Test mit echtem Backup | `tests/e2e/test_backup.py` | ✓ |
| Auswertung offener und auffälliger Fälle | `tests/integration/test_export.py` | ✓ |
| Bootstrap-Prozess: erster Admin über CLI, solange kein aktives Admin-Konto existiert | — | ✗ offen |
| Anlegen Benutzerkonto mit Rolle `REVIEWER` | `tests/integration/test_user_accounts.py` | ✓ |
| Anlegen Benutzerkonto mit Rolle `TECH` | `tests/integration/test_user_accounts.py` | ✓ |
| Zurückweisung ungültiger Rollenwerte | `tests/integration/test_user_accounts.py` | ✓ |
| Zurückweisung doppelter Benutzernamen | `tests/integration/test_user_accounts.py` | ✓ |
| Deaktivierung eines Benutzerkontos | `tests/integration/test_user_accounts.py` | ✓ |
| Reaktivierung eines Benutzerkontos | — | ✗ offen |
| Rollenwechsel eines bestehenden Benutzerkontos | — | ✗ offen |
| Zugriffsschutz: Nicht-Admin darf keine Benutzer-/Rollenänderung ausführen | `tests/integration/test_user_accounts.py` | ✓ |
| Audit-Log-Nachweis für Anlage und Deaktivierung | `tests/integration/test_user_accounts.py` | ✓ |
| Audit-Log-Nachweis für Reaktivierung und Rollenwechsel | — | ✗ offen |

Diese Tabelle dokumentiert die fachliche Testabdeckung im Projektstand. Sie ersetzt nicht die zusätzlich geforderte formale Testmatrix für Abnahme- und Revisionszwecke.[cite:7][cite:8][cite:10]
