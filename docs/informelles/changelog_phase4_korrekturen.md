# Changelog – nachgezogene Korrekturen in Phase 4 (Schritte 4/1 bis 4/6)

Stand: 2026-05-26

Dieses Changelog dokumentiert die in Planung und Implementierungsplanung nachgezogenen Präzisierungen und Korrekturen, die aus den Review-Runden zu Phase 4 entstanden sind. Es beschreibt nicht neue Fachfunktionen, sondern die bereinigte, jetzt konsistente Lesart von Codebasis und Planungsunterlagen.

## 4/1 – Use Cases und Migrationen

- `ApproveSupplementUseCase` ist in Planung und Implementierungsplanung jetzt eindeutig als **Pflichtbestandteil** beschrieben; bloßes `supplement_repo.approve()` ohne Erzeugung einer echten `TimeBooking` gilt ausdrücklich als fachlich unvollständig.
- Die Pflicht zur vollständigen Compliance-Bewertung eines genehmigten Nachtrags wurde explizit festgeschrieben: `source = MANUAL`, ReviewCases pro ComplianceFlag und eigener Audit-Log-Eintrag `SUPPLEMENT_APPROVED`.
- Die Rollenprüfung in allen schreibenden Use Cases ist nun als eigener Nachrüstpunkt 1c sauber benannt und für `RegisterSupplementUseCase`, `CorrectBookingUseCase`, `ManageWorkScheduleUseCase`, `ApproveSupplementUseCase` und `RejectSupplementUseCase` präzisiert.
- Die Ruhezeitprüfung nach ArbZG §5 wurde in den Phase-4-Unterlagen ausdrücklich von einem „späteren Thema“ zu einer **verbindlichen Pflichtanforderung** hochgezogen und sowohl für `BookUseCase` als auch `ApproveSupplementUseCase` konkretisiert.
- Die Abgrenzung von Migration `0005_time_bookings_device_event_id.sql` wurde geschärft: Die Migration stellt nur die **Schemafähigkeit** für `device_event_id` her, nicht bereits die vollständige operative Geräteverkettung.

## 4/2 – Migrationen / Schemafähigkeit

- Die Planunterlagen benennen jetzt klar, dass `0003`, `0004` und `0005` Korrektur- bzw. Nachrüstmigrationen auf den finalen Phase-4-Schemastand sind und frühe Abweichungen aus `0001_schema.sql` bereinigen.
- Für `device_event_id` wurde die Erwartung korrigiert: kein Index ist vorhanden, dies wird aber ausdrücklich als **bewusst offen gelassene Optimierung** und nicht als Lücke beschrieben.
- Die Lesart „Schritt 2 = vollständige Device-Event-Ende-zu-Ende-Verkettung“ wurde explizit ausgeschlossen; zulässig ist nur die Lesart „Schritt 2 = DB-seitige Vorbereitbarkeit“.

## 4/3 – Unit of Work

- Die Exit-Semantik der `SQLiteUnitOfWork` wurde in den Unterlagen auf den tatsächlichen Codezustand nachgezogen: nicht mehr „Rollback nur bei Exception“, sondern **commit-or-rollback** für jede noch offene Transaktion.
- Das `audit_conn`-Muster ist jetzt ausdrücklich dokumentiert: Audit-Einträge laufen über eine getrennte Autocommit-Verbindung und überleben dadurch den Rollback der Haupttransaktion.
- Die Rolle von `open_connection()` als einzige erlaubte Erzeugungsstelle für `audit_conn` ist nun klar formuliert, inklusive PRAGMA-/WAL-/busy_timeout-Begründung.
- Die `rowcount`-Prüfung in `approve()`, `reject()` und `resolve()` ist jetzt ausdrücklich als Schutz gegen stille No-Ops dokumentiert.

## 4/4 – Repositories

- Die Work-Schedule-Logik wurde präzisiert: `get_effective()` ist als zweistufige Prioritätslogik `EMPLOYEE vor GLOBAL` beschrieben, inklusive bewusstem Fallback auf globale Regeln, wenn keine mitarbeiterspezifische Version greift.
- `list_versions(weekday=None, scope_employee_id=None)` ist jetzt korrekt als **GLOBAL-only bei `None`** dokumentiert und gerade nicht als „alle Scopes“; für eine Gesamtsicht sind zwei Aufrufe nötig.
- Die Invariante gegen überlappende Regelzeitversionen wurde eindeutig der Domänenlogik (`ManageWorkScheduleUseCase`) zugeordnet und nicht mehr implizit dem Repository oder SQLite-Constraint zugeschrieben.
- Die UTC-Tagesgrenze für `list_for_employee_on_day()` ist jetzt ausdrücklich als Systemannahme festgehalten, samt Hinweis, dass Buchungsnormalisierung und Auswertungen bei späterer Zeitzonenänderung gemeinsam angepasst werden müssten.
- Das Intervallverhalten von `list_between()` wurde präzisiert: halb-offenes Intervall `[from_dt, to_dt)`, also exklusives Ende; daraus wurde eine Planungsnotiz für spätere Hilfsfunktionen in Phase 5 abgeleitet.
- Die Formulierung zu `SystemConfigRepository.set_current()` wurde geschärft: „immer zusammen mit AuditLogEntry“ ist **keine Repository-Innenpflicht**, sondern eine Verwendungsregel für den aufrufenden Use Case in derselben Transaktion.
- Zusätzlich ist jetzt explizit dokumentiert, dass Schritt 4 zwar das Repository fachlich fertigstellt, die operative Nutzung von `system_config` aber erst in Phase 5 durch die Admin-CLI erfolgt.

## 4/5 – Integrations-Testbasis

- Die frühere missverständliche Formulierung „In-Memory-SQLite“ wurde bereinigt; korrekt ist nun „ephemere dateibasierte SQLite-Testdatenbank mit Migrationen“.
- Der Scope von Schritt 5 wurde geschärft: Er umfasst ausschließlich die Repository-/UoW-Integrationsbasis; Hardware-, Export- und Backup-Tests gehören zu späteren Schritten.
- Die Fixture-Struktur ist jetzt nachvollziehbar erläutert: `conftest.py` als gemeinsame Basis, lokale Sonderfixtures in `test_unit_of_work.py` aus technischen Gründen wegen `audit_conn`.
- Der Pflicht-Testfall zu zwei gleichzeitig gültigen `EMPLOYEE`-Versionen mit deterministischer Auswahl der neueren Version ist jetzt ausdrücklich hervorgehoben.

## 4/6 – Hardware-Schicht

- Die frühere Unschärfe zu `map_rfid_key()` wurde behoben: Die Funktion mappt **RFID-HID-Keycodes auf Hex-Zeichen**, nicht Numpad-Keys auf Buchungsarten.
- Das Numpad-Mapping ist nun getrennt und explizit als `_NUMPAD_TO_BOOKING_TYPE` dokumentiert.
- Schritt 6 ist jetzt klar als **Leseschicht** beschrieben; die Persistenz von `device_events` und die vollständige Betriebsverkettung werden ausdrücklich späteren Schritten zugeordnet.
- Das blockierende Verhalten von `read_booking_type()` / `read_uid()` ist jetzt als bewusste Schichtgrenze dokumentiert; Idle-Timeout, Reconnect und Geräteausfallbehandlung wurden als Aufgabe der späteren Betriebsschicht festgehalten.
- Die Testbeschreibung wurde präzisiert: Es handelt sich um Adapter-Schnittstellen- und Logiktests ohne physische EVDEV-Geräte; reale Gerätebesonderheiten sollen später per manuellen Smoke-Tests auf Zielhardware geprüft werden.

## 4/7 – Backup-Schicht

- Die Schritt-7-Dokumentation wurde um konkrete Implementierungsdetails ergänzt:
  `_log_audit()` öffnet eine eigene `open_connection()`-Verbindung (kein Fremdkontext);
  alle vier Audit-Events sind mit ihren Feldinhalten beschrieben.
- `sync_to_nas()` mit `rsync --archive --delete` ist jetzt als **Spiegelung** klassifiziert,
  mit explizitem Hinweis auf das Archivierungsrisiko: `--delete` entfernt am NAS-Ziel,
  was lokal fehlt; Archiv- und Mirror-Pfad müssen betrieblich getrennt werden, wenn
  der NAS Langzeitablage sein soll (Regelwerk v3 §17/§18).
- Die Platzierung von `RESTORE_COMPLETED` ist jetzt ausdrücklich dokumentiert: Das Event
  wird in die **wiederhergestellte Datenbank** geschrieben und beschreibt den Ist-Zustand
  nach dem Restore, nicht den gesicherten Altstand.
- Der Deployment-Trigger (systemd-Timer/cron) wurde als **Betriebsintegration** abgegrenzt;
  `scripts/backup.py` deckt die manuelle Auslösbarkeit ab, die Timer-Konfiguration ist
  kein Python-Artefakt von Schritt 7.
- **Exportdatei-Lücke implementiert (Schritt 7 Nachtrag):** `SQLiteBackupService` um
  `export_dir: Path | None`-Parameter erweitert; `create_local_backup()` kopiert
  Exportdateien via `shutil.copytree` in `backup_dir/exports/` (fehlende Export-Dir
  wird ignoriert); `scripts/backup.py` erhält `--export-dir`; 3 neue E2E-Tests
  (19 gesamt, 325 Tests grün). Pflichtenheft v3 §12/§14 + Regelwerk v3 §17/§18/§20
  damit erfüllt.

## Bewertung

Die nachgezogenen Korrekturen betreffen vor allem **Dokumentationsschärfe, Grenzziehung zwischen Schritten und präzisere Architekturlesart**. Die aktuelle Planung ist damit deutlich konsistenter zur Codebasis als in den früheren Zwischenständen.
