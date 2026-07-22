# Codebase-Audit Teil 1 — Logikbrüche

| Feld | Wert |
| --- | --- |
| Erstellt | 2026-07-22 |
| Auditor | Claude Sonnet 4.6 (Code-Review-Agent) |
| Codestand | main, commit 2eead92 |
| Scope | Domain, Application, Infrastructure (DB + Hardware) |
| Methode | statische Quellcode-Analyse, keine Laufzeitprüfung |

## Zusammenfassung

Sieben belegte Befunde wurden identifiziert. Davon einer Kritisch, zwei Hoch,
zwei Mittel und zwei Niedrig. Der kritischste Befund (Zeitzonen-Vergleich im
Regelzeitfenster) würde im Produktivbetrieb für jede Buchung einen falschen
`OUTSIDE_SCHEDULE_WINDOW`-Prüffall erzeugen.

---

## Befunde (absteigend nach Schweregrad)

---

### [Kritisch] Zeitzonen-Vergleich bei der Regelzeitfensterprüfung

**Datei:** `src/arbeitszeit/application/use_cases/book_time.py:145–150`

**Problem:** Der Vergleich `schedule.start_time <= cmd.booked_at.time() <= schedule.end_time`
vergleicht UTC-Zeit gegen lokale Regelzeiten. `cmd.booked_at` ist stets
UTC (erzeugt via `datetime.now(timezone.utc)` in `evdev_reader.py:208`).
Die Regelarbeitszeiten in `work_schedule_versions` sind lokal (z. B. `07:30`,
`18:00`). In Deutschland (CET = UTC+1, CEST = UTC+2) ergibt sich eine
systematische Verschiebung von 1–2 Stunden.

**Auslösefall:** Mitarbeiterin bucht um 08:00 Uhr Lokalzeit (CEST, UTC+2).
`cmd.booked_at.time()` ergibt `06:00 UTC`. Der Regelzeitplan enthält
`start_time=07:30`, `end_time=18:00`. Vergleich: `07:30 <= 06:00` → False →
`OUTSIDE_SCHEDULE_WINDOW` wird gesetzt, obwohl die Buchung pünktlich ist.
Da alle Buchungen der Praxis in der Sommerzeit bis zu 2 Stunden vor dem
Regelstart (UTC) liegen, erzeugt *jede* Buchung einen falschen Prüffall.

**Empfohlene Korrektur:** `cmd.booked_at.time()` durch
`cmd.booked_at.astimezone().time()` ersetzen, sodass die lokale Systemzeit
mit den lokalen Regelzeiten verglichen wird. Alternativ könnten Regelzeiten
in UTC normiert gespeichert werden, was aber alle bestehenden Einträge
migrieren würde.

---

### [Hoch] Schweregrad-Downgrade in `check_break_compliance`

**Datei:** `src/arbeitszeit/domain/services/compliance_checks.py:33–47`

**Problem:** Die Funktion gibt bei `max_continuous > 6 h` sofort ein `WARN`
zurück (Frühausstieg), ohne danach die schwerwiegendere CRITICAL-Bedingung
`net_work > 9 h AND total_break < 45 min` zu prüfen. Ist beides gleichzeitig
erfüllt, wird eine CRITICAL-Verletzung fälschlich als WARN eingestuft.

**Auslösefall:**
Mitarbeiterin: COME 07:00, BREAK_START 14:30, BREAK_END 14:40, GO 17:00.

- `max_continuous = 7,5 h > 6 h` → erste Prüfung: return WARN.
- `net_work = 9,83 h > 9 h` und `total_break = 10 min < 45 min` → würde
  CRITICAL ergeben, wird aber nie erreicht.
- `check_max_hours`: `9,83 h < 10 h` → kein CRITICAL von dort.
- Ergebnis: Buchungsstatus `WARN` statt `NEEDS_REVIEW`; ReviewCase mit
  Severity `WARN` statt `CRITICAL`. Der Fall entgeht der Eskalation.

Im Bereich 9–10 h Nettoarbeitszeit mit unzureichender Pause und einem
kontinuierlichen Block > 6 h fehlt die gesetzlich gebotene CRITICAL-Einstufung
vollständig.

**Empfohlene Korrektur:** Die Prüffolge umkehren: zuerst CRITICAL-Bedingungen
(`net_work > 9 h`) prüfen, dann WARN-Bedingungen (`max_continuous > 6 h`);
oder `return` durch `append` ersetzen, um alle zutreffenden Flags unabhängig
voneinander zu sammeln und die schwerste Severity zu ermitteln.

---

### [Hoch] Korrektur ändert `booking_type` in `time_bookings` nicht

**Datei:** `src/arbeitszeit/application/use_cases/correct_booking.py:65–84`

**Problem:** `CorrectBookingUseCase` schreibt den korrigierten Buchungstyp und
-zeitstempel ausschließlich in `booking_corrections.new_values_json` (JSON).
Der `booking_type`-Wert in `time_bookings` bleibt unverändert; nur der
`current_status` wechselt auf `CORRECTED`. Weil `list_for_employee_on_day`
keine Filterung auf `current_status` vornimmt, enthält `day_booking_types` bei
der nächsten Buchung weiterhin den alten (falschen) Typ.

**Auslösefall:** Admin korrigiert eine fehlerhafte COME-Buchung auf GO (z. B.
falsche Karte am Ausgang gescannt). In `time_bookings` steht weiterhin
`booking_type = 'COME'`, Status = `CORRECTED`. Beim nächsten RFID-Scan:
`day_booking_types = [COME]` → `derive_booking_type([COME]) = BREAK_START`
statt des erwarteten COME (neue Schicht). Der gesamte weitere Tagesablauf
wird auf Basis des alten, falschen Typs abgeleitet.

**Empfohlene Korrektur:** Entweder `time_bookings.booking_type` und
`time_bookings.booked_at` bei der Korrektur aktualisieren (direkte Mutation
mit Korrekturhistorie in `booking_corrections`), oder `list_for_employee_on_day`
so erweitern, dass CORRECTED-Buchungen durch ihre korrigierten Werte ersetzt
werden.

---

### [Mittel] Fehlzeitplan-Lookup mit UTC-Wochentag und UTC-Datum

**Datei:** `src/arbeitszeit/application/use_cases/book_time.py:138–139`

**Problem:** `cmd.booked_at.isoweekday()` und `cmd.booked_at.date()` liefern
den ISO-Wochentag und das Datum des UTC-Zeitstempels. Liegt die Buchung lokal
am Montag um 00:30 Uhr (22:30 UTC Sonntag), wird der Regelzeitplan für Sonntag
abgerufen — nicht für Montag. Damit kann die Kurztag-Regelung (`_is_short_day`)
für den falschen Wochentag eingreifen oder der falsche Regelzeitrahmen für
OUTSIDE_SCHEDULE_WINDOW herangezogen werden.

**Auslösefall:** Mitarbeiterin bucht um 00:30 Uhr Montagmorgen lokal
(22:30 UTC Sonntag). `isoweekday()` = 7 (Sonntag), obwohl es lokal Montag ist.
Für Sonntag existiert kein Regelzeitplan → `schedule = None` → keine
Kurztag-Prüfung und keine OUTSIDE_SCHEDULE_WINDOW-Warnung.

**Hinweis:** Für eine Zahnarztpraxis mit Buchungszeiten 07:30–18:00 Uhr ist
dieser Grenzfall praktisch irrelevant (keine Buchungen nahe UTC-Mitternacht).
Der Befund ist korrekt für eine vollständige formale Analyse.

**Empfohlene Korrektur:** `cmd.booked_at.astimezone()` für Wochentag- und
Datumsberechnung verwenden.

---

### [Mittel] Nachtrag-UseCase ohne Buchungssequenz-Validierung

**Datei:** `src/arbeitszeit/application/use_cases/register_supplement.py:60–76`

**Problem:** `RegisterSupplementUseCase` erzeugt einen `Supplement`-Datensatz
mit beliebigem `booking_type` (COME, GO, BREAK_START, BREAK_END), ohne
`validate_booking_sequence` oder `derive_booking_type` aufzurufen. Ein Prüfer
kann einen Nachtrag mit fachlich unzulässigem Typ eintragen.

**Auslösefall:** Die Tagessequenz ist `[COME, BREAK_START]` (Pause offen).
Prüfer erfasst einen Nachtrag `GO` auf den Mitarbeiter für denselben Tag.
Der GO wird ohne Sequenzprüfung als `Supplement` gespeichert. Da Nachträge
nicht direkt in `time_bookings` einfließen, beeinflusst dies die nächste
RFID-Buchung nicht, erzeugt aber einen fachlich inkonsistenten Datensatz
(GO ohne abgeschlossene Pause) in `supplements`.

**Empfohlene Korrektur:** Vor dem Speichern des Nachtrags die Sequenz des
betroffenen Tages laden und `validate_booking_sequence` aufrufen. Bei Verstoß
`InvalidBookingSequenceError` oder ein Application-seitiger Fehler.

---

### [Niedrig] `BookingStatus.CLOSED_WITH_NOTE` definiert aber nie gesetzt

**Datei:** `src/arbeitszeit/domain/enums.py:19`

**Problem:** `BookingStatus.CLOSED_WITH_NOTE` ist im Enum, im DB-Schema
(Migration 0003) und in `booking_status_history.new_status` als erlaubter
Wert definiert. Kein UseCase setzt diesen Status je auf eine Buchung.
`set_status` in `time_booking.py` könnte ihn technisch setzen, wird aber
nirgends mit diesem Wert aufgerufen.

**Auslösefall:** Ein Reviewer oder Entwickler könnte annehmen, dieser Status
existiere operativ; ein manueller DB-Eingriff oder eine Admin-CLI-Funktion
könnte ihn irrtümlich setzen. Die Auswertungslogik berücksichtigt ihn nicht.

**Empfohlene Korrektur:** Klären, ob `CLOSED_WITH_NOTE` für Buchungen (nicht
ReviewCases) fachlich vorgesehen ist. Falls nein: aus Enum und DB-CHECK
entfernen. Falls ja: Use Case implementieren.

---

### [Niedrig] `OpenPhaseConflictError` im normalen RFID-Buchungsflow unerreichbar

**Datei:** `src/arbeitszeit/domain/services/booking_rules.py:48`

**Problem:** `_validate_go` wirft `OpenPhaseConflictError`, wenn bei einem
GO eine Pause noch offen ist. Im normalen RFID-Flow gibt `derive_booking_type`
bei offener Pause stets `BREAK_END` zurück — nicht GO. Der Error-Handler in
`_DOMAIN_MESSAGES` der Terminal-UI (`"Offene Phase — bitte zuerst abschließen."`)
ist daher toter Code für den operativen Terminalbetrieb.

**Auslösefall:** `OpenPhaseConflictError` ist nur erreichbar, wenn
`validate_booking_sequence` direkt mit `GO` und einer offenen Pause aufgerufen
wird — z. B. aus Tests oder künftigen Code-Pfaden, die den RFID-Flow umgehen.

**Empfohlene Korrektur:** Kein unmittelbarer Handlungsbedarf; der Schutz
`validate_booking_sequence` ist korrekt und sinnvoll als Sicherheitsnetz.
Für Klarheit im Code könnte ein Kommentar ergänzt werden, der erklärt, warum
der Handler in `_DOMAIN_MESSAGES` defensiv vorgehalten wird.

---

## Analysierte Dateien

| Datei | Analysiert |
| --- | --- |
| `src/arbeitszeit/domain/entities.py` | vollständig |
| `src/arbeitszeit/domain/enums.py` | vollständig |
| `src/arbeitszeit/domain/errors.py` | vollständig |
| `src/arbeitszeit/domain/value_objects.py` | vollständig |
| `src/arbeitszeit/domain/services/booking_rules.py` | vollständig |
| `src/arbeitszeit/domain/services/compliance_checks.py` | vollständig |
| `src/arbeitszeit/application/use_cases/book_time.py` | vollständig |
| `src/arbeitszeit/application/use_cases/_booking_evaluation.py` | vollständig |
| `src/arbeitszeit/application/use_cases/correct_booking.py` | vollständig |
| `src/arbeitszeit/application/use_cases/register_supplement.py` | vollständig |
| `src/arbeitszeit/application/commands.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/migrations.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/time_booking.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/review_case.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/work_schedule.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/supplement.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/booking_correction.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/audit_log.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/repositories/_helpers.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/unit_of_work.py` | vollständig |
| `src/arbeitszeit/infrastructure/db/connection.py` | vollständig |
| `src/arbeitszeit/infrastructure/hardware/debounce.py` | vollständig |
| `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` | vollständig |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | vollständig |
| `src/arbeitszeit/presentation/terminal_ui/main.py` | vollständig |
| `migrations/0001_schema.sql` | vollständig |
| `migrations/0003_cleanup_booking_status.sql` | vollständig |
| `migrations/0004_supplement_reject_fields_and_review_note.sql` | vollständig |
| `migrations/0005_time_bookings_device_event_id.sql` | vollständig |
| `docs/01_normativ/regelwerk_arbeitszeit.md` | vollständig |
| `tests/application/test_book_time.py` | vollständig |
| `tests/domain/test_booking_rules.py` | vollständig |
| `tests/domain/test_compliance_checks.py` | vollständig |
