# Implementierungsplan: arbeitszeit

## Kontext

Die Dokumente unter `docs/informelles/` dokumentieren eine vollständige Design-Session für das Zeiterfassungssystem. Sie enthalten die wesentlichen Entscheidungen zu Domänenmodell, Datenbankschema, Projektstruktur, Use-Cases, Prüfregeln, Export, Betrieb und Testabdeckung.

**Verbindliche Referenzdokumente:** `docs/pflichtenheft_arbeitszeit_v6.md`, `docs/regelwerk_arbeitszeit_v5.md`.  
Anlage-Dokumente im Repo: `anlage_einhaltung_pflichtenheft.md` (Wurzelverzeichnis, v1) und `docs/archive/anlage_einhaltung_pflichtenheft_v2.md` (Version 2, referenziert Pflichtenheft v4, archiviert). Aktueller Stand der Betriebsdokumentation: `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`.

Dieses Dokument beschreibt den bekannten technischen Umsetzungs- und Planungsstand des Projekts. Organisatorische, datenschutzrechtliche und betriebliche Pflichten der Praxis werden ausdrücklich benannt, soweit sie laut Pflichtenheft v6, Regelwerk v5 und Anlage v2 nicht allein durch Code erfüllt werden können.

---

## Ergänzende Leitplanken aus den Referenzdokumenten v5/v2

### Rechts- und Regelrahmen

Die Systemauslegung stützt sich auf die Pflicht zu einem objektiven, verlässlichen und zugänglichen Zeiterfassungssystem sowie auf die arbeitszeitrechtlichen Anforderungen zu Höchstarbeitszeit, Ruhepausen und Ruhezeit. Pflichtenheft v6 ergänzt dies ausdrücklich um das Arbeitsschutzgesetz als organisatorische Grundlage des Arbeitgebers für geeignete Schutz- und Erfassungsmaßnahmen.

Für den Betrieb in der Zahnarztpraxis ist zusätzlich die IT-Sicherheitsrichtlinie nach § 75b SGB V zu beachten. Rollen, Rechte, Backup, Protokollierung, Schutz der Praxis-IT und die Einbindung in das Praxis-IT-Sicherheitskonzept sind daher nicht nur technische, sondern auch organisatorische Anforderungen.

### Datenschutz, lokale Verarbeitung und Backup-Architektur

Die produktive Verarbeitung von Arbeitszeitdaten erfolgt ausschließlich lokal in der Praxis-IT-Infrastruktur. Externe Cloud-Dienste sind nicht für produktive Verarbeitung oder Auswertung vorgesehen.

Verschlüsselte Backups dürfen optional zusätzlich in einem externen Cloud-Speicher abgelegt werden, wenn die Verschlüsselung clientseitig vor Verlassen der Praxisumgebung erfolgt und der Cloud-Anbieter nur als technisches Backup-Medium dient. Dafür sind außerhalb dieses Dokuments insbesondere AV-Vertrag, Schlüsselverwaltung, Speicherortprüfung, TOM-Dokumentation und Rotationskonzept zu regeln.

### Offene Praxis- und Nachweispflichten

Die Anlage Einhaltung Pflichtenheft v2 bewertet das Projekt fachlich als weit fortgeschritten, benennt aber weiterhin offene organisatorische und formale Nachweise. Dazu gehören insbesondere eine schriftlich verabschiedete Betriebsdokumentation zu Export, Rechten, Aufbewahrung, Löschregeln, Backup und Restore, eine revisionsfeste Testmatrix, die Entscheidung zum produktiven `device_events`-/`device_event_id`-Pfad sowie die organisatorische Zuordnung von Rollen, Freigabeverantwortungen, Prüfintervallen und IT-Sicherheitsverantwortlichkeiten.

Diese Punkte werden in den fachlichen Phasen unten dort aufgegriffen, wo sie technischen Bezug haben. Soweit sie rein organisatorisch sind, werden sie als externe Auflagen gekennzeichnet und nicht fälschlich als bereits durch Code erfüllt dargestellt.

### Benutzer- und Rollenverwaltung (Pflichtenheft v6 §7.9 / Regelwerk v5 §16, §16a)

Pflichtenheft v6 §7.9 (neu gegenüber v4) macht die Admin-CLI-basierte Benutzerkontenverwaltung zur verbindlichen Anforderung. Direktes SQL darf kein regulärer Betriebsprozess sein.

Regelwerk v5 §16a (neu) definiert Benutzerkonten als eigenständige Zugangsobjekte, die optional einem Mitarbeiterdatensatz zugeordnet sein können. Doppelte Benutzernamen sind unzulässig; inaktive Konten dürfen keine administrativen oder prüfenden Aktionen ausführen.

Implementiert (`admin_cli users`-Modul, Phase 5+):

- `users add --username <u> --role <ADMIN|REVIEWER|TECH> [--employee-id <id>] [--password <pw>]`
- `users list`
- `users deactivate --user-id <id>`
- Passwort-Hashing via `hashlib.pbkdf2_hmac` (stdlib, salt:hash-Format)
- Audit-Events `USER_ACCOUNT_CREATED`, `USER_ACCOUNT_DEACTIVATED`

Vollständig implementiert (`admin_cli users`-Modul, alle 6 Befehle):

- `users add`, `users list`, `users deactivate` ✓
- `users reactivate --user-id <id>` ✓ (Audit-Event `USER_ACCOUNT_REACTIVATED`)
- `users change-role --user-id <id> --role <NEUE_ROLLE>` ✓ (Audit-Event `USER_ACCOUNT_ROLE_CHANGED`)
- `users bootstrap --username <u> [--password <pw>]` ✓ (nur wenn kein aktiver Admin existiert)

---

## Was die Dokumente festgelegt haben

### 01 – Fachlicher Kern
- Zentrum ist die **unveränderliche Buchung** (`Zeitbuchung`), nicht die „Tagesarbeitszeit“.
- Offene Fälle werden **nicht automatisch geschlossen** – immer explizite Klärung.
- Trennung: TerminalEreignis → Zeitbuchung (erst nach Prüfung). Der vollständige produktive Verkettungspfad über `device_events` ist implementiert (Commit `0f20931`, 2026-06-11).

### 02 – ER-Modell (5 Ebenen)

| Ebene | Entitäten |
| --- | --- |
| Person | `employees`, `user_accounts`, `rfid_cards` |
| Erfassung | `terminals`, `time_bookings`, `device_events` |
| Prüfung | `review_cases`, `review_case_actions`, `booking_status_history` |
| Änderung | `booking_corrections`, `supplements`, `work_schedule_versions` |
| Nachweis | `audit_log`, `system_events`, `system_config` |

Die Tabellenstruktur deckt die im Pflichtenheft geforderten fachlichen Kernstrukturen ab und erweitert sie um Betriebs- und Nachweisobjekte. Die Anlage v2 bewertet das Datenmodell als weitgehend vollständig nachgewiesen.

### 03–09 – SQLite DDL

- **15 fachliche Tabellen** mit FK-Constraints, CHECK-Constraints, Indizes (+ `schema_migrations` = 16 Tabellen in `0001_schema.sql`).
- `work_schedule_versions` + `system_config`: Herkunftsfeld `change_origin` (`SYSTEM_SEED` / `ADMIN_UI` / `MIGRATION`) – kein künstlicher Bootstrap-User.
- Komplexe Prüfregeln liegen bewusst in Python-Domänenlogik und nicht in SQLite.
- `system_events` dient als Nachweis für Betriebsereignisse einschließlich Selbsttest, Backup/Restore und Systemzeitprotokollierung.
- **Aufbewahrungsprinzip:** Fachlich relevante Buchungen werden nicht physisch gelöscht; Klärung erfolgt über Status, Korrekturen oder Archivierung. Die Mindestaufbewahrung beträgt 2 Jahre; Backups, Exportdateien und Berichte unterliegen zusätzlich einem gesondert festzulegenden Archivierungs- und Löschkonzept einschließlich Rotation.

### 11 – 4 Kern-Use-Cases

- Architekturentscheidung dokumentiert in `docs/adr/device_event_architekturentscheidung_v1.md`.

| Use-Case | Transaktion umfasst |
| --- | --- |
| `buchen()` | `device_events`, `time_bookings`, `booking_status_history`, `review_cases`, `audit_log` |
| `nachtrag_anlegen()` | `supplements`, `review_cases`, `audit_log` |
| `korrektur_anlegen()` | `booking_corrections`, `time_bookings`, `booking_status_history`, `review_cases`, `audit_log` |
| `regelarbeitszeit_ändern()` | `work_schedule_versions` (alt schließen + neu), `audit_log` |

Die Transaktionskette für `device_events` ist vollständig operativ: `booking_loop.py` erzeugt per `RFID_SCAN`-Record in `device_events` und reicht die ID via `BookCommand.device_event_id` in `time_bookings.device_event_id` durch. Architekturentscheidung dokumentiert in `docs/adr/device_event_architekturentscheidung_v1.md`.

---

## Implementierungsreihenfolge

### Phase 1 – Grundgerüst ✓ abgeschlossen

Originärer Phase-1-Kern vollständig implementiert. Nachträgliche Ergänzungen
(`scripts/setup.py`, `setup_vollstaendig()` in `init_db.py`) wurden Phase 4
zugeordnet, da sie `SQLiteSystemConfigRepository` (Phase 4) importieren.

Originärer Phase-1-Lieferumfang (Migrationen 0001/0002, 6 Tests):
- `pyproject.toml`, `src/`-Layout, `tests/`, `.gitignore`, `.python-version`.
- `migrations/0001_schema.sql` – finale DDL, enthält `schema_migrations`.
- `migrations/0002_seed_defaults.sql` – Regelzeiten + System-Config-Defaults.
- `infrastructure/db/connection.py` – `isolation_level=None`, `PRAGMA foreign_keys = ON`, `row_factory`.
- `infrastructure/db/migrations.py` – `executescript()` mit `BEGIN/COMMIT`, Versionsvalidierung vor f-String.
- `scripts/init_db.py`.
- `tests/test_migrations.py` – ursprünglich 6 Testfälle für 0001/0002.

Spätere Nachträge auf demselben Fundament (nicht Teil des Phase-1-Abschlusses):
- `migrations/0003_cleanup_booking_status.sql` – Status-CHECK bereinigt (Phase 4). 
- `migrations/0004_supplement_reject_fields_and_review_note.sql` – `rejected_by_user_id`/`rejected_at` + `note`-Feld (Phase 4). 
- `migrations/0005_time_bookings_device_event_id.sql` – `device_event_id` FK (Phase 4). 
- `migrations/0006_system_events_application_error.sql` – `APPLICATION_ERROR` als `event_type` (Phase 5). 
- `tests/test_migrations.py` – zusätzliche Tests für 0003–0006.

Heutiger Gesamtstand des Testmoduls: 12 Tests für die Migrationskette 0001–0006.

Hinweis: `tests/integration/test_init_db.py` (5 Tests für `setup_vollstaendig()`)
sind Integrationstests (Phase 4+, abhängig von `SQLiteSystemConfigRepository`),
keine originären Phase-1-Tests.

---

### Phase 2 – Domäne ✓ abgeschlossen

Umgesetzt unter `src/arbeitszeit/domain/`.

**`enums.py`** — 11 `StrEnum`-Klassen: `BookingType`, `BookingStatus`, `ReviewCaseType`, `ReviewCaseStatus`, `ReviewSeverity`, `CardStatus`, `UserRole`, `BookingSource`, `ChangeOrigin`, `ApprovalStatus`, `ScopeType`.

**`errors.py`** — `DomainError`-Basis + 9 Subklassen: `UnknownCardError`, `InactiveCardError`, `InactiveEmployeeError`, `InvalidBookingSequenceError`, `OpenPhaseConflictError`, `PermissionDeniedError`, `ValidationError`, `NotFoundError`, `ConflictError`.

**`entities.py`** — 9 frozen `@dataclass`-Entitäten mit fachlichen Invarianten, darunter `TimeBooking`, `WorkScheduleVersion`, `ReviewCase`, `Supplement`, `BookingCorrection` und `AuditLogEntry`.

**`services/booking_rules.py`** — `validate_booking_sequence()` (Rückgabetyp `None`; `ValidationResult` entfernt).

**`services/compliance_checks.py`** — `check_break_compliance()`, `check_max_hours()`, `check_rest_period()`, `ComplianceFlag`.

V4-relevant bleibt: Die arbeitszeitrechtlichen Prüfungen orientieren sich an den im Pflichtenheft genannten Tagesanforderungen. Eine mögliche spätere Erweiterung um Wochenprüfungen ist dokumentarisch vorgesehen, aber kein aktueller Implementierungsbestandteil.

**Bekannte Nichtabdeckung — Backlog-Item N-02 (Audit P2-04):** Kumulative
Wochenarbeitszeit nach ArbZG §3 (Höchstarbeitszeit über 5 Werktage) ist derzeit
nicht implementiert. Die tagbezogenen Prüfungen in `compliance_checks.py` decken
§3 nur indirekt ab. Wochenprüfungen werden als späteres Backlog-Thema geführt;
kein Handlungsbedarf für den aktuellen Pflichtenheft-v6-Scope.

V4- und Regelwerk-konforme Statusmodellierung:
- `POSSIBLE_*`-Prüflagen werden als `ReviewCaseType` modelliert.
- `MANUAL_ENTRY` wird als `BookingSource.MANUAL` modelliert.
- `report_queries.py` ist die zentrale Wahrheitsquelle für Berichte, Pflichtauswertungen, Filterlogik und Projektionen; direkte abweichende Ad-hoc-Queries sind architektonisch unzulässig.

**`ports/repositories.py`** — 10 `Protocol`-Interfaces für Repositories der Entitäten und Aggregate.

**Tests** (67 gesamt, alle grün):
- `tests/domain/test_booking_rules.py` – 14 Tests (10 Fehlerfälle + 4 Erfolgsfälle).
- `tests/domain/test_compliance_checks.py` – 9 Tests.
- `tests/domain/test_entities.py` – 42 Invariantentests.
- `tests/domain/test_audit_events.py` – 2 Tests.

---

### Phase 3 – Application ✓ abgeschlossen

#### Architekturentscheidungen

- Architekturentscheidung (Pfad A1): `docs/adr/device_event_architekturentscheidung_v1.md`.

**BookingStatus-Semantik** — Status beschreibt die einzelne Buchung, nicht den Tagesstatus. Die definierten Zustände `OPEN`, `OK`, `WARN`, `NEEDS_REVIEW`, `CORRECTED` und `CLOSED_WITH_NOTE` entsprechen den verbindlichen Statusvorgaben aus Pflichtenheft und Regelwerk.

**`booking_status_history`** — Infrastruktur-Seiteneffekt über `time_booking_repo.set_status()`; kein eigenes History-Repository in der Application-Schicht.

**`device_event_id`** — Verantwortungsteilung (vollständig implementiert):
- `booking_loop.py` erzeugt vor `BookUseCase`-Aufruf einen `RFID_SCAN`-Record in `device_events` (Autocommit).
- Die neue `device_events.id` wird als `BookCommand.device_event_id` übergeben.
- `BookUseCase` persistiert die ID in `time_bookings.device_event_id`.
- Architekturentscheidung (Pfad A1): `docs/adr/device_event_architekturentscheidung_v1.md`.

**Autorisierungsmuster** — Rollenprüfung in schreibenden Use Cases gemäß Pflichtenheft v6 §5 und Regelwerk v5 §16.

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

Die in Phase 3 festgelegten Commands, Results, Fakes und Use Cases entsprechen dem dokumentierten Fachmodell und den Prüfregeln. Die in Pflichtenheft v6 geforderten Kernabläufe, Korrektur-/Nachtragsmechanismen und Prüfpfade sind damit in der Anwendungslogik abgebildet.

Hinweis: `approve_supplement.py` und `reject_supplement.py` wurden in Phase 3 vorimplementiert (Phase-4-Inhalt). Detailliert dokumentiert in `phase3_planung.md`.

---

### Phase 4 – Infrastruktur ✓ vollständig abgeschlossen

Phase 4 schließt Datenbank-Integration, echte Repositorys, Unit of Work, Backup, Export, Pflichtauswertungen und Selbsttest. Die technische Umsetzung deckt damit große Teile von Pflichtenheft v6 §7.11–§7.13, §9.3, §12 und §14 ab.

Wesentliche Punkte:
- `SQLiteUnitOfWork` mit konsequenter commit-or-rollback-Semantik.
- 10 SQLite-Repositories mit Parameterized Statements, Roundtrips und Scope-/Statuslogik.
- `system_events` für Backup, Restore, Selbsttest und später Systemzeitabweichungen.
- `report_queries.py` als zentrale Ableitungsschicht für CSV, PDF und Pflichtauswertungen.
- `SQLiteBackupService` mit NAS-Sync, Restore-Test, Integritätsprüfung und optionalem Mitsichern von Exportdateien.

**V4-/Anlage-v2-relevante Klarstellung:** Die technische Backup-Architektur ist stark, bildet aber nicht automatisch alle organisatorischen und datenschutzrechtlichen Zusatzpflichten ab. Für lokale und optionale verschlüsselte Cloud-Backups sind zusätzlich schriftliche Regelungen zu Schlüsseln, Speicherorten, AV-Vertrag, Restore-Freigabe und Rotation erforderlich; diese liegen außerhalb des Codes und bleiben laut Anlage v2 offene Nachweispunkte.

**Systemzeitprotokollierung:** Die ursprünglich offene V3-/V4-Anforderung aus Pflichtenheft §9.3 und Regelwerk §21 wurde später geschlossen. Zeitsprünge und manuelle Uhrzeitänderungen werden über `time_monitor.py` und `system_events` protokolliert.

---

### Phase 5 – Präsentation ✓ vollständig abgeschlossen

Die Präsentationsschicht umfasst `presentation/terminal_ui/` und `presentation/admin_cli/`. Damit sind Betriebsfunktionen, Buchungsfluss, Berichte, Pflichtauswertungen und Systemcheck in benutzbarer Form zugänglich.

Wesentliche Punkte:
- Terminal-UI mit `process_booking()`, `format_feedback()`, Systemcheck beim Start und Fehlerprotokollierung.
- Admin-CLI mit Befehlen für Mitarbeiter, Karten, Buchungen, Regelzeiten, Reports und Systemfunktionen.
- Admin-CLI `users`-Gruppe (Pflichtenheft v6 §7.9): `users add`, `users list`, `users deactivate`. Passwort-Hashing via `hashlib.pbkdf2_hmac`. Audit-Events `USER_ACCOUNT_CREATED`, `USER_ACCOUNT_DEACTIVATED` im Audit-Log. Implementiert nach Phase-5-Abschluss als direktes Folge-Increment zu §7.9.
- Pflichtauswertungen sind in der Anwendung einsehbar und exportierbar, wie es Pflichtenheft v6 §7.13 verlangt.
- Systemzeitprotokollierung ist in den Loop integriert und damit auch betrieblich angebunden.

**Offener Architekturpunkt – `device_event_id`-Verkettung:**
Die Spalte `time_bookings.device_event_id` ist im Schema vorhanden. Die vollständige operative Kette, bei der die Hardware-Schicht vor `process_booking()` einen `device_events`-Datensatz anlegt und dessen ID bis zur Buchung persistiert, ist nach aktuellem Stand noch nicht im Produktionspfad aktiviert. Dieser Punkt ist unverändert offen und bleibt für eine lückenlose Ereignisherkunft relevant.

---

## Testaufteilung

| Verzeichnis | Inhalt |
| --- | --- |
| `tests/domain/` | Domänenregeln, Invarianten (Phase 2) |
| `tests/application/` | Use-Case-Tests mit Fake-Repositories (Phase 3) |
| `tests/integration/` | Repositorys, Export, Systemcheck, Zeitmonitor gegen echte SQLite-DB (Phase 4/5) |
| `tests/e2e/` | Vollständige Abläufe: Buchen, Nachtrag, Backup/Restore (Phase 4/5) |
| `tests/test_migrations.py` | Migrationsrunner |

Die vorhandene Testdokumentation weist die Pflichtszenarien fachlich gut zu. Anlage v2 fordert darüber hinaus eine **revisionsfeste Testmatrix**, die Muss-Anforderungen und Abnahmekriterien direkt einzelnen Tests zuordnet. Diese Matrix ist nicht Teil des vorliegenden Dokuments und bleibt als gesonderter Nachweispunkt offen.

## V5-/V2-Abgleich: offene Punkte und externe Auflagen

Die folgenden Punkte sind nach dem aktuellen Stand **nicht zu überspringen** und bewusst als offen oder extern gekennzeichnet, weil sie laut Referenzdokumenten nicht allein durch den implementierten Code als erledigt gelten dürfen:

- Schriftlich verabschiedete Betriebsdokumentation zu Exportverzeichnis, Dateirechten, Aufbewahrung, Löschregeln, Backup und Restore. Technische Betriebsdokumentation erstellt: `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` (2026-06-11); formale Verabschiedung außerhalb des Repos.
- ~~Revisionsfeste Testmatrix~~ — erstellt: `docs/betrieb/nachweise/testmatrix_revision_v1.md` (2026-06-11).
- ~~Entscheidung und vollständige produktive Umsetzung des `device_events`-/`device_event_id`-Pfads~~ — implementiert (Commit `0f20931`) und dokumentiert (`device_event_architekturentscheidung_v1.md`).
- Organisatorische Zuordnung von Rollen, Freigabeverantwortungen, Prüfintervallen und IT-Sicherheitsverantwortlichkeiten in der Praxis.
- Datenschutz- und Backup-Unterlagen der Praxis für AV-Vertrag, Schlüsselverwaltung, Speicherorte, TOM, Rotationskonzept und Restore-Freigabe.
- Formale Einbindung des Systems in das Praxis-IT-Sicherheitskonzept nach § 75b SGB V.
- Optionale Cloud-Backup-Nutzung nur mit vorgelagerter clientseitiger Verschlüsselung und sauber dokumentierter datenschutzrechtlicher Grundlage; eine operative Cloud-Backup-Implementierung ist in diesem Plan nicht beschrieben.
- ~~`users reactivate`, `users change-role`, Bootstrap-Prozess~~ — implementiert (Phase 5 abgeschlossen).

Evidenzgrenzen (was aus dem Repo belegbar ist und was nicht): `docs/informelles/session_abschluss_und_klarstellungen_2026-06-11.md`.

Phasenübergreifende Nachtragsmatrix (vorgezogene/nachgezogene Artefakte, 44 Einträge): `docs/betrieb/nachweise/nachtragsmatrix_phasen_v1.md` (2026-06-11).

## Pflichtenheft v6 §16 Testpflicht-Abdeckung

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
| Bootstrap-Prozess: erster Admin über CLI, solange kein aktives Admin-Konto existiert | `tests/integration/test_user_accounts.py` | ✓ |
| Anlegen Benutzerkonto mit Rolle `REVIEWER` | `tests/integration/test_user_accounts.py` | ✓ |
| Anlegen Benutzerkonto mit Rolle `TECH` | `tests/integration/test_user_accounts.py` | ✓ |
| Zurückweisung ungültiger Rollenwerte | `tests/integration/test_user_accounts.py` | ✓ |
| Zurückweisung doppelter Benutzernamen | `tests/integration/test_user_accounts.py` | ✓ |
| Deaktivierung eines Benutzerkontos | `tests/integration/test_user_accounts.py` | ✓ |
| Reaktivierung eines Benutzerkontos | `tests/integration/test_user_accounts.py` | ✓ |
| Rollenwechsel eines bestehenden Benutzerkontos | `tests/integration/test_user_accounts.py` | ✓ |
| Zugriffsschutz: Nicht-Admin darf keine Benutzer-/Rollenänderung ausführen | `tests/integration/test_user_accounts.py` | ✓ |
| Audit-Log-Nachweis für Anlage und Deaktivierung | `tests/integration/test_user_accounts.py` | ✓ |
| Audit-Log-Nachweis für Reaktivierung und Rollenwechsel | `tests/integration/test_user_accounts.py` | ✓ |
| device_events-Record bei erfolgreicher Buchung + Verknüpfung device_event_id | `tests/integration/test_device_event_booking.py::test_erfolgreiche_buchung_schreibt_device_event_und_verknuepft_id` | ✓ |
| device_events-Record bei abgewiesener Buchung (UnknownCard) | `tests/integration/test_device_event_booking.py::test_unknown_card_schreibt_device_event_aber_keine_buchung` | ✓ |
| INSERT-Fehler device_events verhindert Buchung | `tests/integration/test_device_event_booking.py::test_fehler_im_device_event_insert_verhindert_buchung` | ✓ |

Diese Tabelle dokumentiert die fachliche Testabdeckung im Projektstand. 
- Die zugehörige revisionsfeste Testmatrix mit vollständiger Anforderungs-zu-Test-Zuordnung befindet sich in `docs/informelles/testmatrix_revision_v1.md`.
+ Die zugehörige revisionsfeste Testmatrix mit vollständiger Anforderungs-zu-Test-Zuordnung befindet sich in `docs/betrieb/nachweise/testmatrix_revision_v1.md`.
