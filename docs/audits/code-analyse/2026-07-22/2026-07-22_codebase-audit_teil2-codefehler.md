# Codebase-Audit Teil 2 — Codefehler

| Feld | Wert |
| --- | --- |
| Erstellt | 2026-07-22 |
| Auditor | Claude Sonnet 4.6 (Code-Review-Agent) |
| Codestand | main, commit a9ccfb2 |
| Scope | Bugs, Off-by-one-Fehler, fehlerhafte Fehlerbehandlung, Null-Handling, tote Codepfade |
| Methode | statische Quellcode-Analyse, vollständiges Line-by-Line-Review aller Kernmodule |

## Zusammenfassung

Acht belegte Befunde wurden identifiziert. Davon zwei Hoch, vier Mittel und
zwei Niedrig. Der schwerwiegendste Befund (falsche chronologische Reihenfolge
in `projected`-Liste bei `ApproveSupplementUseCase`) führt zu silently falschen
Compliance-Berechnungen bei rückwirkenden Nachtragsfreigaben. Der zweite
Hoch-Befund ist eine eigenständige Instanz des in Teil 1 als Kritisch
eingestuften UTC-vs.-Lokal-Fehlers — diesmal im `ApproveSupplementUseCase`.

---

## Befunde (absteigend nach Schweregrad)

---

### [Hoch] `projected`-Liste in `ApproveSupplementUseCase` nicht chronologisch sortiert

**Datei:** `src/arbeitszeit/application/use_cases/approve_supplement.py:78`

**Problem:** `projected = list(day_bookings) + [placeholder]` hängt den
Nachtrag immer ans Ende der Tagesbuchungen an. `day_bookings` kommt aus
`list_for_employee_on_day`, sortiert nach `booked_at`. Der Placeholder hat
`booked_at = supplement.event_at`. Liegt `supplement.event_at` zeitlich
**vor** der letzten bestehenden Tagesbuchung, ist `projected` nicht mehr
chronologisch geordnet.

`evaluate_booking` ruft `_work_stats` auf (`compliance_checks.py:67`), das
ausdrücklich `# day_bookings must be in chronological order` voraussetzt.
Mit Out-of-order-Liste berechnet `_work_stats` negative Arbeitsblock-Deltas
(`block = past_ts - future_ts`) und summiert diese auf. Der resultierende
`status` und die `flags` sind fachlich falsch.

**Auslösefall:**
Tagessequenz: `[COME@08:00, BREAK_START@12:00, BREAK_END@12:30]`.
Admin erfasst Nachtrag `GO@10:00` (`event_at < BREAK_START`).
`validate_booking_sequence(GO, [COME, BREAK_START, BREAK_END])` besteht:
`open_work=True`, `open_break=False` → `_validate_go` wirft nicht.
`projected = [COME@08:00, BREAK_START@12:00, BREAK_END@12:30, GO@10:00]`.
`_work_stats` berechnet:

- COME@08:00 → `work_block_start = 08:00`
- BREAK_START@12:00 → `block = 4 h`, `net_work = 4 h`, `break_start = 12:00`
- BREAK_END@12:30 → `total_break = 30 min`, `work_block_start = 12:30`
- GO@10:00 → `block = 10:00 − 12:30 = −2,5 h`, `net_work = 1,5 h`

Statt ~4 h Nettoarbeitszeit wird 1,5 h ermittelt. Keine Compliance-Flags
werden erzeugt; Buchungsstatus ist `OK` statt ggf. `WARN`.

**Hinweis:** Im normalen RFID-Flow (`book_time.py:177`) tritt das Problem
nicht auf, weil `cmd.booked_at` stets `datetime.now(timezone.utc)` ist und
damit immer nach allen bisherigen Tagesbuchungen liegt.

**Empfohlene Korrektur:** `projected` vor Übergabe an `evaluate_booking`
nach `booked_at` sortieren:
```python
projected = sorted(list(day_bookings) + [placeholder], key=lambda b: b.booked_at)
```

---

### [Hoch] UTC-vs.-Lokal-Fehler in `ApproveSupplementUseCase._build_schedule_flags`

**Datei:** `src/arbeitszeit/application/use_cases/approve_supplement.py:189,194`

**Problem:** `_build_schedule_flags` ruft `get_effective` mit
`supplement.event_at.isoweekday()` und `supplement.event_at.date()` auf und
vergleicht danach `schedule.start_time <= supplement.event_at.time()`. Alle
drei Ausdrücke operieren auf dem UTC-Zeitstempel. Regelarbeitszeiten in
`work_schedule_versions` sind lokal gespeichert (z. B. `07:30`, `18:00`).
Dies ist dieselbe strukturelle Ursache wie der in Teil 1 als **Kritisch**
eingestufte Befund in `book_time.py:145–150`, nur im selteneren
Supplement-Approve-Pfad.

**Auslösefall:** Admin gibt einen Nachtrag mit `event_at = 08:00 Uhr lokal
(CEST, UTC+2)` frei. `supplement.event_at.time()` ergibt `06:00 UTC`. Regelzeitplan:
`start_time=07:30`, `end_time=18:00`. Vergleich: `07:30 <= 06:00` → False →
fälschlich `OUTSIDE_SCHEDULE_WINDOW`-Flag gesetzt → follow-up ReviewCase
erzeugt.

**Empfohlene Korrektur:** `supplement.event_at.astimezone()` für Zeitvergleich
und Wochentag-/Datumslookup verwenden (analog zur Empfehlung in Teil 1).

---

### [Mittel] `CreateEmployeeUseCase` erlaubt unkontrollierte Doppelung mit inaktiven Mitarbeitern

**Datei:** `src/arbeitszeit/application/use_cases/manage_employees.py:31`

**Problem:** Die Konfliktprüfung vor dem Anlegen eines neuen Mitarbeiters
verwendet `get_active_by_personnel_no` (`employee.py:32`), das ausschließlich
`active = 1` prüft. Da `employees.personnel_no` im Schema als `UNIQUE`
definiert ist (`0001_schema.sql:10`), schlägt der darauffolgende INSERT fehl,
wenn ein **inaktiver** Mitarbeiter dieselbe `personnel_no` besitzt. Statt
einer freundlichen `ConflictError`-Meldung propagiert eine
`sqlite3.IntegrityError`, die im Admin-CLI-Handler
(`except DomainError`) nicht gefangen wird und als Python-Traceback
erscheint.

**Auslösefall:**
1. Mitarbeiterin mit `personnel_no = 'MA-007'` wird deaktiviert.
2. Admin legt neuen Mitarbeiter mit `personnel_no = 'MA-007'` an.
3. `get_active_by_personnel_no('MA-007')` → None (inaktiv nicht gefunden).
4. `employee_repo.add(...)` → `sqlite3.IntegrityError: UNIQUE constraint failed`.
5. Transaktion rollt zurück, aber Exception passiert
   `except DomainError` → unkontrollierter Absturz.

**Empfohlene Korrektur:** Statt `get_active_by_personnel_no` eine Methode
`get_by_personnel_no` (ohne Aktivitätsfilter) verwenden. Ist eine Zeile
vorhanden, `ConflictError` mit klarem Hinweis werfen.

---

### [Mittel] Admin kann eigenes Konto deaktivieren — letzter-Admin-Lockout möglich

**Datei:** `src/arbeitszeit/application/use_cases/manage_user_accounts.py:94–124`

**Problem:** `DeactivateUserAccountUseCase.execute` prüft weder, ob
`cmd.acting_user_id == cmd.target_user_id` (Selbstdeaktivierung), noch ob
nach der Operation mindestens ein aktiver Admin verbleibt. Das Repository
besitzt `has_active_admin()` (genutzt in `BootstrapAdminUseCase:220`), wird
aber in `DeactivateUserAccountUseCase` nicht aufgerufen. Ein Admin kann damit
das einzige aktive Administratorkonto deaktivieren; das System hat danach
keinerlei aktive Admin-Nutzer mehr und ist nicht mehr verwaltbar.
`ChangeUserRoleUseCase` weist denselben Mangel auf: Rollenwechsel auf `REVIEWER`
oder `TECH` für das letzte Admin-Konto ist möglich.

**Auslösefall:**
1. System hat genau einen aktiven Admin.
2. Admin ruft `user-accounts deactivate --user-id <eigene-id>` auf.
3. Kein Fehler, Konto deaktiviert.
4. Alle weiteren Admin-Aktionen (Login, Passwortreset, Rollenzuweisung)
   sind dauerhaft gesperrt; kein Self-Service-Recovery möglich.

**Empfohlene Korrektur:** Vor Deaktivierung und Rollenwechsel prüfen, ob
mindestens ein weiterer aktiver Admin erhalten bleibt:
```python
if self._uow.user_account_repo.has_active_admin() == 1 and \
   target.role == UserRole.ADMIN:
    raise ValidationError("Letztes Admin-Konto kann nicht deaktiviert werden.")
```

---

### [Mittel] `_close_correctable_cases` gibt nur erste Prüffall-ID zurück

**Datei:** `src/arbeitszeit/application/use_cases/correct_booking.py:143–153`

**Problem:** Schließt eine Buchung mehrere korrigierbare Review-Cases (z. B.
`POSSIBLE_BREAK_VIOLATION` **und** `POSSIBLE_REST_VIOLATION`), werden alle
geschlossen, aber nur die ID des **ersten** Cases in `review_case_id`
gespeichert (Guard `if review_case_id is None: review_case_id = case.id`).
Das Audit-Log (`details_json.review_case_id`) und `CorrectionResult`
enthalten ausschließlich diese eine ID. Die Schließung der übrigen Cases
ist nicht rückverfolgbar.

**Auslösefall:** Buchung hat Review-Cases für `POSSIBLE_BREAK_VIOLATION`
(ID 42) und `POSSIBLE_REST_VIOLATION` (ID 43). Nach Korrektur sind beide
geschlossen. `CorrectionResult.review_case_id = 42`. Case 43 ist im Audit-Log
nicht erwähnt.

**Empfohlene Korrektur:** Rückgabetyp auf `list[ReviewCaseId]` erweitern;
alle geschlossenen IDs im `CorrectionResult` und Audit-Log aufführen.
Alternativ `review_case_id` als `ReviewCaseId | None` belassen, aber
im `details_json` alle IDs als Array dokumentieren.

---

### [Mittel] `list_between` verwendet inklusives `to_dt` — inkonsistent mit Codebase-Konvention

**Datei:** `src/arbeitszeit/infrastructure/db/repositories/time_booking.py:81`

**Problem:** `list_between` filtert `booked_at >= from_dt AND booked_at <= to_dt`
(inklusiv auf beiden Seiten). Alle anderen Zeitraum-Abfragen im Projekt
(`list_for_employee_on_day`, `report_queries.list_bookings`, alle
`_intervals.py`-Intervalle) verwenden halboffene Intervalle `[from, to)`.
Ruft Code `list_between` und gleichzeitig `list_for_employee_on_day` mit
demselben Tages-Intervall auf, erhält er eine Buchung mit
`booked_at == next_day_start` zweimal oder gar nicht, je nach Verwendung.

**Auslösefall:** Buchung exakt um `00:00:00 UTC` des Folgetages. Ein
Aggregations-Report, der beide Methoden kombiniert, zählt diese Buchung
doppelt oder übersieht sie.

**Empfohlene Korrektur:** Operator auf `booked_at < ?` (exklusiv) umstellen.

---

### [Niedrig] Verbindungs-Leak wenn zweiter `open_connection`-Aufruf fehlschlägt

**Datei:** `src/arbeitszeit/presentation/terminal_ui/booking_loop.py:43–44`

**Problem:**
```python
conn = open_connection(db_path)       # erfolgreich
audit_conn = open_connection(db_path) # wirft OSError/sqlite3.OperationalError
```
Schlägt der zweite Aufruf fehl, bevor `try:` erreicht ist, wird `conn` nie
in `finally: conn.close()` geschlossen. Obwohl `open_connection` für
SQLite-Dateien in der Praxis nie zweimal fehlschlägt, wenn der erste
erfolgreich war, ist das Ressourcen-Handling strukturell falsch.

**Empfohlene Korrektur:** Nested `try/finally`:
```python
conn = open_connection(db_path)
try:
    audit_conn = open_connection(db_path)
    try:
        ...
    finally:
        audit_conn.close()
finally:
    conn.close()
```

---

### [Niedrig] `occurred_at` in `EvdevHardwareReader.read_next` nach UID-Assemblierung gesetzt

**Datei:** `src/arbeitszeit/infrastructure/hardware/evdev_reader.py:208`

**Problem:** `occurred_at = datetime.now(timezone.utc)` wird **nach** dem
Ende der `while`-Schleife gesetzt — also nachdem die vollständige UID
assembliert und die Schleife verlassen wurde. Der Zeitpunkt der Kartenauflage
liegt typischerweise wenige Millisekunden früher. Im pathologischen Fall
(langsam sendender Lesekopf, Betriebssystem-Scheduling-Verzögerung) kann
die Differenz knapp 1 Sekunde betragen (maximale Länge eines
`_read_rfid_uid`-Polls). Für eine Zeiterfassung mit Minutengenauigkeit ist
dies vernachlässigbar; für forensische Genauigkeit bei genauen Tagesgrenzen
(z. B. kurz nach Mitternacht UTC) könnte die Buchung dem falschen UTC-Tag
zugeordnet werden.

**Empfohlene Korrektur:** `occurred_at` am Beginn der
`_read_rfid_uid`-Methode erfassen, wenn das erste Zeichen empfangen wird —
oder sofort nach dem erfolgreichen `break` aus dem Poll-Loop speichern.

---

## Analysierte Dateien (Teil 2 — ergänzend zu Teil 1)

| Datei | Analysiert |
| --- | --- |
| `src/arbeitszeit/application/use_cases/approve_supplement.py` | vollständig |
| `src/arbeitszeit/application/use_cases/reject_supplement.py` | vollständig |
| `src/arbeitszeit/application/use_cases/manage_employees.py` | vollständig |
| `src/arbeitszeit/application/use_cases/manage_rfid_cards.py` | vollständig |
| `src/arbeitszeit/application/use_cases/manage_user_accounts.py` | vollständig |
| `src/arbeitszeit/application/use_cases/manage_work_schedule.py` | vollständig |
| `src/arbeitszeit/application/queries.py` | vollständig |
| `src/arbeitszeit/application/results.py` | vollständig |
| `src/arbeitszeit/domain/entities.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/employee.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/review_case.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/supplement.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/work_schedule.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/migrations.py` | vollständig |
| `src/arbeitszeit/infrastructure/export/report_queries.py` | vollständig |
| `src/arbeitszeit/infrastructure/export/csv_exporter.py` | vollständig |
| `src/arbeitszeit/infrastructure/backup/backup_service.py` | vollständig |
| `src/arbeitszeit/infrastructure/system_check.py` | vollständig |
| `src/arbeitszeit/infrastructure/time_monitor.py` | vollständig |
| `src/arbeitszeit/presentation/admin_cli/bookings.py` | vollständig |
| `src/arbeitszeit/presentation/admin_cli/audit.py` | vollständig |
| `src/arbeitszeit/presentation/admin_cli/reports.py` | vollständig |
| `src/arbeitszeit/presentation/admin_cli/_intervals.py` | vollständig |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | vollständig |
| `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` | vollständig |
