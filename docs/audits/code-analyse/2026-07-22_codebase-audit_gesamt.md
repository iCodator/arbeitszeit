# Codebase-Audit Gesamtbericht

| Feld | Wert |
| --- | --- |
| Erstellt | 2026-07-22 |
| Auditor | Claude Sonnet 4.6 (Code-Review-Agent) |
| Codestand | main, commit a9ccfb2 |
| Scope | Vollständige Codebase: Domain, Application, Infrastructure, Presentation |
| Methode | statische Quellcode-Analyse, keine Laufzeitprüfung |
| Teilberichte | Teil 1 (Logikbrüche), Teil 2 (Codefehler), Teil 3 (Sicherheitsrisiken) |

## Zusammenfassung

Insgesamt 24 Befunde über drei Kategorien identifiziert:
**1 Kritisch, 6 Hoch, 9 Mittel, 8 Niedrig.**

Der kritischste Befund (UTC-vs.-Lokal-Vergleich in der Regelzeitfensterprüfung) erzeugt im
Produktivbetrieb für *jede* Sommerzeitbuchung einen falschen `OUTSIDE_SCHEDULE_WINDOW`-Prüffall.
Zwei weitere Hoch-Befunde (Severity-Downgrade in `check_break_compliance` und fehlende
chronologische Sortierung in `ApproveSupplementUseCase`) führen zu silently falschen
Compliance-Ergebnissen. Im Sicherheitsbereich ist die unsalted SHA-256-Hashing-Methode
für RFID-UIDs das gravierendste Problem, da sie die DSGVO-Pseudonymisierung de facto
unwirksam macht.

---

## Kategorie 1 — Logikbrüche

*Quelle: 2026-07-22/2026-07-22_codebase-audit_teil1-logikbrueche.md*
*Auditor: Claude Sonnet 4.6 — Codestand: commit 2eead92*

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

## Kategorie 2 — Codefehler

*Quelle: 2026-07-22/2026-07-22_codebase-audit_teil2-codefehler.md*
*Auditor: Claude Sonnet 4.6 — Codestand: commit a9ccfb2*

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

## Kategorie 3 — Sicherheitsrisiken

*Quelle: 2026-07-22/2026-07-22_codebase-audit_teil3-sicherheit.md*
*Auditor: Claude Sonnet 4.6 — Codestand: commit a9ccfb2*

---

### [Hoch] Unsalted SHA-256 für RFID-UIDs — DSGVO-Pseudonymisierung wirkungslos

**Datei:** `src/arbeitszeit/infrastructure/hardware/uid_hash.py:8`

**Problem:** `hash_uid()` berechnet `hashlib.sha256(raw_uid.encode()).hexdigest()`
ohne Pepper, HMAC-Key oder Salt. Standard-RFID-Karten (ISO 14443 Typ A, z. B.
Mifare Classic) verwenden 4-Byte-UIDs (2³² ≈ 4,3 Milliarden Möglichkeiten). Auf
moderner GPU-Hardware lässt sich der gesamte Keyspace in Sekunden bis Minuten
durchsuchen. Ein Angreifer, der Lesezugriff auf die Datenbank erhält, kann alle
gespeicherten `rfid_cards.uid_hash`-Werte auf physische Karten-UIDs
zurückrechnen.

Die DSGVO Art. 32 TOM „Pseudonymisierung", auf die das Datenschutzkonzept des
Projekts Bezug nimmt, ist damit für RFID-Daten nicht wirksam: ein entschlossener
Angreifer kann die Verknüpfung Karten-UID ↔ Mitarbeiter aus der Datenbank
ableiten.

**Auslösefall:** Angreifer erhält Lesezugriff auf `arbeitszeit.db` (z. B. durch
unsicheres Backup oder kompromittierten NAS-Speicher) und erschöpft den
4-Byte-UID-Keyspace mit einem Brute-Force-Tool.

**Empfehlung:** HMAC-SHA256 mit einem installationsspezifischen Pepper aus dem
OS-Keyring oder einer separaten, berechtigungsgeschützten Schlüsseldatei:

```python
import hmac, os
# Schlüssel einmalig erzeugen und sicher speichern (nicht in config.toml)
_PEPPER = os.environb.get(b"RFID_PEPPER")  # oder aus Keyring laden
def hash_uid(raw_uid: str) -> str:
    return hmac.new(_PEPPER, raw_uid.encode(), "sha256").hexdigest()
```

Bestehende Hashes in der Datenbank müssten nach Einführung des Peppers neu
berechnet werden (einmalige Migration).

---

### [Hoch] Passwort-Hash gespeichert, aber nie verifiziert — Admin-CLI ohne Authentifikation

**Dateien:**
`src/arbeitszeit/presentation/admin_cli/user_accounts.py:41–47` (Hashing),
`src/arbeitszeit/presentation/admin_cli/main.py:45–68` (Identitätsauflösung),
`src/arbeitszeit/presentation/admin_cli/_auth.py:14–35` (Rollenprüfung)

**Problem:** Die Admin-CLI identifiziert den Aufrufer ausschließlich anhand
einer numerischen `user_id` (aus CLI-Argument `--user-id`, Umgebungsvariable
`ADMIN_USER_ID` oder `config.toml`). Eine Passwort-Verifikation existiert im
gesamten Codebase nicht: es gibt keine `verify_password()`-Funktion, und
`password_hash` wird nach dem Anlegen eines Kontos nie wieder gelesen.

Der Code in `_auth.py` prüft nur, ob die angegebene `user_id` in der Datenbank
als ADMIN/REVIEWER/TECH mit `active=1` existiert — nicht, ob der Aufrufer das
zugehörige Passwort kennt. Das Bootstrap-Konto bekommt immer `id=1` (SQLite
AUTOINCREMENT), was vorhersagbar ist.

**Auslösefall:** Ein Nutzer mit OS-Zugriff (z. B. als Mitglied der Systemgruppe,
die Lesezugriff auf das CLI-Binary hat) führt `admin --user-id 1 employees list`
aus und erhält vollständige Mitarbeiterdaten — ohne jede Passworteingabe.

**Hinweis:** Das Sicherheitsmodell ist konsistent mit einem lokalen Kiosk-System,
bei dem „OS-Zugriff = Admin-Zugriff" gilt. Das ist architektonisch vertretbar,
aber nur wenn OS-Level-Berechtigungen (Dateisystem-ACLs, systemd-Unit mit
dedizierten Nutzern) tatsächlich durchgesetzt sind. Das gespeicherte Passwort
erweckt einen falschen Eindruck von Zugriffskontrolle.

**Empfehlung:** Zwei Optionen:

1. Passwort-Verifikation nachrüsten: `--password` am CLI-Start abfragen,
   `password_hash` aus der DB laden, mit PBKDF2-HMAC-SHA256 und
   `secrets.compare_digest()` vergleichen.
2. Den `password_hash`-Mechanismus als „für zukünftige Web-UI reserviert"
   explizit dokumentieren und im Sicherheitskonzept festhalten, dass der
   Admin-CLI-Zugriff ausschließlich durch OS-Berechtigungen geschützt ist.

---

### [Mittel] Vollständiger `uid_hash` in Fehlerfall-Audit-Log — Rückverfolgbarkeit

**Datei:** `src/arbeitszeit/application/use_cases/book_time.py:264–279`

**Problem:** Im Fehlerfall „unbekannte Karte" schreibt `_verify_card()` den
vollständigen 64-Zeichen-SHA-256-Hash in `details_json` des Audit-Logs:

```python
details_json=json.dumps({"uid_hash": uid_hash, "terminal_id": terminal_id}, ...)
```

In Kombination mit dem fehlenden Pepper (Befund 1) ermöglicht jeder mit
Lesezugriff auf `audit_log`, den gespeicherten Hash auf die physische Karten-UID
zurückzurechnen und festzustellen, welche Karte wann an welchem Terminal
gescannt wurde — auch ohne Mitarbeiter-Zuordnung. Damit ist selbst der versuchte
Zutritt mit einer fremden/gestohlenen Karte vollständig nachverfolgbar auf die
Karten-UID.

**Auslösefall:** Audit-Log wird an eine dritte Stelle (z. B. SIEM, NAS-Backup)
übermittelt; Empfänger kann alle unbekannten Karten-UIDs brute-forcen.

**Empfehlung:** Nur den Präfix des Hashes im Audit-Log speichern, wie es das
Debounce-Logging in `debounce.py` bereits korrekt macht (`uid_hash[:8]`):

```python
"uid_hash_prefix": uid_hash[:8]
```

---

### [Mittel] Keine Format-Validierung für `--uid-hash`-Parameter

**Dateien:**
`src/arbeitszeit/presentation/admin_cli/employees.py:215` (`cards assign`),
`src/arbeitszeit/presentation/admin_cli/employees.py:229` (`cards replace`)

**Problem:** Der Parameter `--uid-hash` wird ohne Formatprüfung direkt als
`uid_hash`-Wert in der Datenbank gespeichert. Der Hilfetext lautet „Fertig
berechneter SHA-256-Hash der Karten-UID", aber es wird nicht verifiziert, ob
der übergebene String tatsächlich ein 64-Zeichen-Hex-String ist.

Gibt ein Operator versehentlich die rohe UID (z. B. `A1B2C3D4`) statt ihres
Hashes ein, wird die Karte dauerhaft nicht erkannt (der Terminal hasht die UID
beim Scan, die DB enthält die ungehashte Rohform). Die Fehlerursache ist dann
schwer nachzuvollziehen.

**Empfehlung:** Validierung vor Anlage des Commands:

```python
import re
if not re.fullmatch(r"[0-9a-f]{64}", uid_hash):
    print("Fehler: --uid-hash muss ein 64-Zeichen-SHA-256-Hex-String sein.", file=sys.stderr)
    sys.exit(1)
```

---

### [Mittel] Audit-Log-Eintrag nach Buchungs-Commit — Write-Gap

**Datei:** `src/arbeitszeit/application/use_cases/book_time.py:204–246`

**Problem:** Nach dem Commit der Buchungstransaktion (Zeile 204) werden
Audit-Log-Einträge auf der separaten `audit_conn`-Verbindung geschrieben
(Zeilen 206–246). Das ergibt folgenden zeitlichen Ablauf:

1. `self._uow.commit()` — Buchung ist dauerhaft in der DB.
2. `self._uow.audit_log_repo.add(...)` — Audit-Eintrag wird geschrieben.

Ein Prozessabsturz (SIGKILL, OOM) zwischen Schritt 1 und 2 hinterlässt eine
Buchung ohne zugehörigen Audit-Log-Eintrag. Dies verletzt die
ArbZG-Dokumentationspflicht (lückenlose Aufzeichnung) und die DSGVO-Pflicht
zur Nachvollziehbarkeit von Datenverarbeitungen.

Der Kommentar im Code erklärt die bewusste Designentscheidung (Lock-Vermeidung);
das Risiko ist aber nicht explizit dokumentiert.

**Auslösefall:** Rasperry Pi verliert Strom oder wird per SIGKILL beendet exakt
nach dem Buchungs-Commit, bevor der Audit-Log-Eintrag geschrieben wird. Im
Audit-Log fehlt dann ein `TIME_BOOKED`-Ereignis für eine real existierende
Buchung.

**Empfehlung:** Write-Ahead-Ansatz: Audit-Log-Eintrag vor dem Commit schreiben
(mit `status: "pending"`), nach dem Commit auf `status: "committed"` aktualisieren.
Alternativ: regelmäßige Plausibilitätsprüfung „Buchungen ohne Audit-Eintrag"
als Admin-Befehl.

---

### [Niedrig] Rohe RFID-UID im Klartext im Diagnose-Skript

**Datei:** `scripts/verify_hardware.py` (Zeile ~334)

**Problem:** Das Diagnose-Skript gibt die gescannte RFID-Roh-UID unverschleiert
aus:

```python
_info(f"Rohe UID (Hex):  {uid_raw.upper()}")
```

Wird das Skript in einer protokollierten Terminal-Sitzung (SSH-Audit,
tmux-Log, systemd-Journal mit Verbose-Level) ausgeführt, landet die physische
Karten-UID als Klartext in Logdateien — außerhalb des Hash-Speichermodells
der Anwendung.

**Empfehlung:** Roh-UID nach den ersten vier Zeichen maskieren:

```python
_info(f"Rohe UID (Hex):  {uid_raw[:4].upper()}****")
_info(f"Länge:           {len(uid_raw)} Zeichen ({len(uid_raw) * 4} Bit)")
```

---

### [Niedrig] Generiertes Passwort auf stdout ausgegeben

**Datei:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py:77, 162`

**Problem:** Bei automatisch generierten Passwörtern (kein `--password`-Argument)
wird das Klartext-Passwort auf stdout ausgegeben:

```python
print(f"Generiertes Passwort (einmalig sichtbar): {password}")
```

In automatisierten Deployment-Workflows (z. B. Ansible-Playbooks, CI/CD-Skripte)
kann stdout-Output in Protokolldateien, Job-Artifacts oder Audit-Trails landen.

**Empfehlung:** Passwort-Ausgabe auf stderr umleiten (stderr wird in den meisten
Automation-Tools standardmäßig nicht persistiert) oder den Aufrufer explizit
auf das Risiko hinweisen:

```python
print("WARNUNG: Passwort wird einmalig angezeigt. Nicht in Logs umleiten.", file=sys.stderr)
print(f"Passwort: {password}", file=sys.stderr)
```

---

### [Niedrig] Audit-Log ohne Integritätssicherung

**Datei:** `migrations/0001_schema.sql:302–313`

**Problem:** Die `audit_log`-Tabelle hat einen einfachen Autoincrement-Primärschlüssel
ohne Hash-Verkettung (Row-Chaining), HMAC-Signatur oder Append-Only-Constraint.
Ein Datenbankadministrator mit Schreibzugriff kann Einträge lautlos löschen
oder verändern, ohne dass dies detektierbar wäre. Dasselbe gilt für Angreifer,
die Schreibzugriff auf die `.db`-Datei erhalten.

Für ArbZG-Compliance (lückenlose Arbeitszeitaufzeichnung) und DSGVO-Accountability
ist eine manipulationssichere Protokollierung relevant.

**Empfehlung:** Periodischer Export der Audit-Log-Tabelle in eine unveränderliche
Zieldatei (z. B. append-only File auf NAS) oder HMAC-Kette über
`(id, event_type, event_at, employee_id, details_json)` mit Verweis auf den
Hash des Vorgängereintrags.

---

### [Niedrig] Kein Dependency-Lock-File — keine reproduzierbaren Builds

**Datei:** `pyproject.toml`

**Problem:** Alle Abhängigkeiten sind ausschließlich mit Untergrenzen definiert
(z. B. `evdev>=1.7`, `reportlab>=4.0`). Ein Lock-File (z. B. `uv.lock` oder
`pip-compile`-Output) fehlt. Bei einer Neuinstallation auf einem anderen System
können jede neuere Version gezogen werden, was:

- Reproduzierbarkeit von Builds verhindert,
- Sicherheits-Patches im Produktivbetrieb nicht erzwingt (der Operator muss
  aktiv aktualisieren),
- eine genaue CVE-Prüfung für die tatsächlich deployten Versionen erschwert.

**Feststellung zu aktuellen Versionen:** Die im Entwicklungssystem installierten
Versionen (evdev 1.9.3, reportlab 5.0.0, pypdf 6.13.1, pytest 9.0.3, ruff 0.15.16)
entsprechen dem aktuellen Stand; keine bekannten CVEs in diesen Versionen
identifiziert.

**Empfehlung:** `uv lock` oder `pip-compile` in den CI/CD-Prozess einbinden und
das erzeugte Lock-File ins Repository aufnehmen.

---

## Positive Feststellungen (Sicherheitsbereich, keine Befunde)

- **SQL-Injection:** Alle Datenbankzugriffe durchgängig mit parametrisierten
  Abfragen. Die einzige String-Interpolation in `migrations.py` ist durch
  `isdigit() and len() == 4` auf den Wertebereich `"0000"`–`"9999"` beschränkt
  und korrekt mit `# nosec B608` annotiert.
- **Subprozess-Sicherheit:** Alle externen Programmaufrufe (`rsync`, `notify-send`,
  `timedatectl`) verwenden absolute Pfade und `shell=False`. Kein Injektionsvektor
  für Benutzeringaben in Prozessargumenten.
- **Passwort-Hashing:** PBKDF2-HMAC-SHA256 mit 260.000 Iterationen und 16-Byte-
  Zufallssalt — korrekte Implementierung nach aktuellem NIST-Standard.
- **RFID-Exklusivzugriff:** `evdev.grab()` verhindert, dass andere Prozesse
  RFID-Eingaben mitlesen.
- **Keine hartkodierte Credentials:** Weder in Quellcode noch in `config.toml.example`
  wurden Passwörter, Schlüssel oder Tokens gefunden.
- **Konfigurationsgeheimnisse:** `config.toml` enthält ausschließlich Pfade und
  IDs, keine Authentifizierungsinformationen.
- **Deserialisierung:** Keine Nutzung von `pickle` oder `yaml.load()` ohne
  `Loader`; ausschließlich `json.loads()` und `tomllib` (read-only, stdlib).
- **Foreign-Key-Constraints:** `PRAGMA foreign_keys = ON` aktiv; referenzielle
  Integrität auf Datenbankebene gesichert.
- **Keine CORS-/Rate-Limit-Risiken:** Kein Netzwerk-Interface, kein HTTP-Server;
  nicht anwendbar für dieses System.

---

## Zusammenfassungstabelle

| Kategorie | Kritisch | Hoch | Mittel | Niedrig | Gesamt |
| --- | --- | --- | --- | --- | --- |
| Logikbrüche (Teil 1) | 1 | 2 | 2 | 2 | 7 |
| Codefehler (Teil 2) | 0 | 2 | 4 | 2 | 8 |
| Sicherheitsrisiken (Teil 3) | 0 | 2 | 3 | 4 | 9 |
| **Gesamt** | **1** | **6** | **9** | **8** | **24** |
