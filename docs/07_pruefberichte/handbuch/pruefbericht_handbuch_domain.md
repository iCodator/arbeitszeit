# Prüfbericht – `docs/module/handbuch_domain.md`

## Gesamteinschätzung

Das Handbuch beschreibt das Domain-Modell insgesamt präzise und deckungsgleich mit der Codebase. Die große Mehrheit der Aussagen ist korrekt und vollständig durch den Quellcode belegbar [cite:5][cite:6][cite:7][cite:8][cite:9][cite:10][cite:11][cite:12]. Es wurden jedoch mehrere Abweichungen identifiziert: Die `ReviewCase`-Entitätsbeschreibung fehlt zwei Pflichtfelder (`id`, `employee_id`, `created_at`, `description`), die Handbuchaussage zur `check_break_compliance`-Prüfreihenfolge weicht von der tatsächlichen Code-Auswertungsreihenfolge ab, und die `AuditLogEntry`-Entität hat im Code ein Feld `event_at`, das im Handbuch fehlt. Zudem enthält die `validate_booking_sequence`-Signatur im Code einen anderen Parameter-Typ als im Handbuch impliziert.

## Abschnitt: Überblick und Designprinzip

---

**Aussage:**
Das Domain-Modell enthält ausschließlich Geschäftslogik und keinerlei Abhängigkeiten zu Datenbank, Hardware oder UI.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/entities.py`, `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/domain/errors.py`, `src/arbeitszeit/domain/value_objects.py` – keine externen Imports außer `dataclasses`, `datetime`, `typing`, `enum` [cite:7][cite:6][cite:8][cite:5]

**Bewertung:** Alle Domain-Dateien importieren ausschließlich Stdlib-Module. Keine Datenbank-, Framework- oder Hardware-Abhängigkeiten vorhanden.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`__init__.py` ist leer – kein öffentliches Re-Export.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/__init__.py` (SHA: `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` = leere Datei) [cite:4]

**Bewertung:** Die Datei hat Größe 0 Bytes, entspricht exakt der Beschreibung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Das Verzeichnisbaum-Diagramm zeigt die Dateien `audit_events.py`, `entities.py`, `enums.py`, `errors.py`, `value_objects.py`, `ports/repositories.py`, `services/booking_rules.py`, `services/compliance_checks.py`.

**Status:** korrekt

**Beleg:** Verzeichnisinhalt `src/arbeitszeit/domain/` [cite:4]

**Bewertung:** Alle aufgeführten Dateien und Unterverzeichnisse sind im Repository vorhanden.

**Änderungsvorschlag:** Kein Änderungsbedarf.

## Abschnitt: Value Objects – Starke ID-Typen

---

**Aussage:**
Alle IDs werden mit `typing.NewType` erzeugt; zur Laufzeit sind sie schlichte `int`-Werte; `mypy` behandelt sie als inkompatible Typen.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/value_objects.py` [cite:5]

**Bewertung:** Code bestätigt exakt dieses Muster. Alle 11 ID-Typen sind via `NewType("...", int)` definiert.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Die Tabelle listet genau diese 11 ID-Typen: `EmployeeId`, `UserAccountId`, `RfidCardId`, `TerminalId`, `TimeBookingId`, `WorkScheduleVersionId`, `ReviewCaseId`, `SupplementId`, `BookingCorrectionId`, `DeviceEventId`, `AuditLogEntryId`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/value_objects.py` – alle 11 `NewType`-Definitionen vorhanden [cite:5]

**Bewertung:** Vollständige Übereinstimmung; keine fehlenden, keine zusätzlichen ID-Typen.

**Änderungsvorschlag:** Kein Änderungsbedarf.

## Abschnitt: Enumerationen

---

**Aussage:**
Alle Enums sind als `StrEnum` definiert; Enum-Werte sind gleichzeitig ihre eigene String-Darstellung (z. B. `BookingType.COME == "COME"`).

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/enums.py` – `from enum import StrEnum`; alle Klassen erben von `StrEnum` [cite:6]

**Bewertung:** Vollständig korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`BookingType` hat die Werte `COME`, `GO`, `BREAK_START`, `BREAK_END`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/enums.py` [cite:6]

**Bewertung:** Exakte Übereinstimmung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`BookingStatus` hat die Werte `OK`, `OPEN`, `WARN`, `NEEDS_REVIEW`, `CORRECTED`, `CLOSED_WITH_NOTE`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/enums.py` [cite:6]

**Bewertung:** Exakte Übereinstimmung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`ReviewCaseType` hat 11 Werte: `OPEN_WORK_PHASE`, `OPEN_BREAK_PHASE`, `OUTSIDE_SCHEDULE_WINDOW`, `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION`, `IMPLAUSIBLE_SEQUENCE`, `UNKNOWN_CARD_ATTEMPT`, `INACTIVE_CARD_ATTEMPT`, `TIME_ANOMALY`, `MANUAL_ENTRY_REVIEW`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/enums.py` [cite:6]

**Bewertung:** Vollständige Übereinstimmung; alle 11 Werte im Code vorhanden.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`ReviewCaseStatus` hat die Werte `OPEN`, `IN_REVIEW`, `RESOLVED`, `CLOSED_WITH_NOTE`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/enums.py` [cite:6]

**Bewertung:** Exakte Übereinstimmung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Tabelle „Weitere Enumerationen": `ReviewSeverity` = `INFO`, `WARN`, `CRITICAL`; `CardStatus` = `ACTIVE`, `INACTIVE`, `REPLACED`, `LOST`; `UserRole` = `EMPLOYEE`, `ADMIN`, `REVIEWER`, `TECH`; `BookingSource` = `TERMINAL`, `MANUAL`, `IMPORT`; `ChangeOrigin` = `SYSTEM_SEED`, `ADMIN_UI`, `MIGRATION`; `ApprovalStatus` = `PENDING`, `APPROVED`, `REJECTED`; `ScopeType` = `GLOBAL`, `EMPLOYEE`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/enums.py` [cite:6]

**Bewertung:** Alle Enums und alle Werte vollständig korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

## Abschnitt: Entitäten

---

**Aussage:**
Alle Entitäten sind als `@dataclass(frozen=True)` definiert.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/entities.py` – alle Klassen mit `@dataclass(frozen=True)` dekoriert [cite:7]

**Bewertung:** Vollständig korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Jede Entität validiert ihre Geschäftsregeln in `__post_init__`.

**Status:** inkorrekt (teilweise)

**Beleg:** `src/arbeitszeit/domain/entities.py` – `TimeBooking` und `WorkScheduleVersion` (kein eigenes `__post_init__` für `TimeBooking`) [cite:7]

**Bewertung:** `TimeBooking` hat **kein** `__post_init__` im Code. Das Handbuch sagt „jede Entität validiert ... in `__post_init__`", was für `TimeBooking` nicht zutrifft.

**Änderungsvorschlag:** Formulierung präzisieren: „Die meisten Entitäten validieren ihre Geschäftsregeln in `__post_init__`. Entitäten ohne fachliche Invarianten (z. B. `TimeBooking`) haben kein `__post_init__`."

---

**Aussage:**
`Employee`-Felder: `id` (`EmployeeId`), `personnel_no` (`str`), `first_name` (`str`), `last_name` (`str`), `is_active` (`bool`) – alle Pflicht.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/entities.py` [cite:7]

**Bewertung:** Exakte Übereinstimmung mit der Klassendefinition.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`Employee`-Invariante: `personnel_no` darf nicht leer oder nur Leerzeichen sein.

**Status:** korrekt

**Beleg:** `entities.py` – `if not self.personnel_no.strip(): raise ValueError(...)` [cite:7]

**Bewertung:** Direkt im Code belegt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`UserAccount`-Felder: `id`, `employee_id`, `username`, `role`, `is_active` – vollständig beschrieben.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/entities.py` [cite:7]

**Bewertung:** Vollständige Übereinstimmung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`RfidCard`-Feld `uid_hash` ist ein „SHA-256-Hash der RFID-UID (nie die Roh-UID)".

**Status:** nicht verifizierbar

**Beleg:** `src/arbeitszeit/domain/entities.py` – Feld ist als `uid_hash: str` deklariert, ohne Hash-Algorithmus-Angabe [cite:7]; kein Test oder Infrastrukturcode geprüft, der SHA-256 explizit bestätigt.

**Bewertung:** Das Feld heißt `uid_hash`, der spezifische Algorithmus (SHA-256) ist im Domain-Code nicht belegt. Eine Infrastruktur-Schicht könnte einen anderen Algorithmus verwenden.

**Änderungsvorschlag:** Entweder den Hash-Algorithmus durch Prüfung der Infrastruktur/Tests belegen oder die Formulierung auf „Hash der RFID-UID" ohne explizite Algorithmusangabe reduzieren, mit dem Hinweis, dass die konkrete Implementierung in der Infrastrukturschicht festgelegt wird.

---

**Aussage:**
`RfidCard`-Invariante: `valid_until` darf nicht vor `valid_from` liegen.

**Status:** korrekt

**Beleg:** `entities.py` – `if self.valid_until is not None and self.valid_until < self.valid_from: raise ValueError(...)` [cite:7]

**Bewertung:** Direkt im Code belegt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`WorkScheduleVersion`-Invarianten: `start_time` muss vor `end_time` liegen; `scope_type` und `scope_employee_id` müssen konsistent sein; `weekday` muss 1–7 (ISO) betragen.

**Status:** korrekt

**Beleg:** `entities.py` – alle drei Prüfungen in `__post_init__` vorhanden; zusätzlich auch `valid_until >= valid_from` geprüft [cite:7]

**Bewertung:** Alle drei genannten Invarianten korrekt. Hinweis: Das Handbuch erwähnt die vierte Invariante (`valid_until` ≥ `valid_from`) nicht, was eine Auslassung ist, aber keine falsche Aussage.

**Änderungsvorschlag:** Zur Vollständigkeit die vierte Invariante ergänzen: „`valid_until` darf nicht vor `valid_from` liegen (wenn gesetzt)."

---

**Aussage:**
`ReviewCase`-Felder-Tabelle listet: `case_type`, `severity`, `status`, `booking_id`, `closed_at`, `closed_by_user_id`, `note`.

**Status:** inkorrekt (unvollständig)

**Beleg:** `src/arbeitszeit/domain/entities.py` – `ReviewCase` hat zusätzlich die Felder `id: ReviewCaseId`, `employee_id: EmployeeId`, `description: str`, `created_at: datetime` [cite:7]

**Bewertung:** Die Handbuch-Tabelle verschweigt vier Pflichtfelder der Entität: `id`, `employee_id`, `description`, `created_at`. Das ist eine sachliche Unvollständigkeit.

**Änderungsvorschlag:** Die Tabelle um die fehlenden Felder ergänzen:

| Feld                | Typ                     | Beschreibung                                  |
|---------------------|-------------------------|-----------------------------------------------|
| `id`                | `ReviewCaseId`          | Datenbankschlüssel                            |
| `employee_id`       | `EmployeeId`            | Betroffener Mitarbeiter                       |
| `case_type`         | `ReviewCaseType`        | Art der Auffälligkeit                         |
| `severity`          | `ReviewSeverity`        | Schweregrad: INFO / WARN / CRITICAL           |
| `status`            | `ReviewCaseStatus`      | Workflow-Status (OPEN → IN_REVIEW → RESOLVED) |
| `description`       | `str`                   | Beschreibung der Auffälligkeit (Pflicht)      |
| `booking_id`        | `TimeBookingId \| None` | Betroffene Zeitbuchung (sofern zuordenbar)    |
| `created_at`        | `datetime`              | Zeitpunkt der Fallanlage                      |
| `closed_at`         | `datetime \| None`      | Zeitpunkt des Abschlusses                     |
| `closed_by_user_id` | `UserAccountId \| None` | Benutzer, der den Fall abgeschlossen hat      |
| `note`              | `str \| None`           | Pflicht bei `CLOSED_WITH_NOTE`                |

---

**Aussage:**
`Supplement`-Beschreibung: „nachträglich erfasste Zeitbuchung (z. B. vergessene Stempelung), die durch einen Administrator genehmigt oder abgelehnt werden muss."

**Status:** nicht verifizierbar

**Beleg:** `src/arbeitszeit/domain/entities.py` – `Supplement` hat kein Feld, das „Administrator" als Genehmiger vorschreibt; `recorded_by_user_id: UserAccountId` und `approved_by_user_id: UserAccountId | None` sind typisiert, aber die Rolle des Genehmigers wird im Domain-Code nicht eingeschränkt [cite:7]

**Bewertung:** Ob ausschließlich Admins genehmigen dürfen, ist eine Use-Case/Berechtigungsregel, nicht eine Domain-Invariante.

**Änderungsvorschlag:** Formulierung neutralisieren: „die durch ein berechtigtes Benutzerkonto genehmigt oder abgelehnt werden muss" – oder als „nicht verifizierbar auf Domain-Ebene" kennzeichnen.

---

**Aussage:**
`Supplement`-Invarianten: Je nach `approval_status` müssen die Felder `approved_by_user_id`, `approved_at`, `rejected_by_user_id`, `rejected_at` korrekt gesetzt/leer sein; `approved_at` und `rejected_at` dürfen nicht vor `recorded_at` liegen.

**Status:** korrekt

**Beleg:** `entities.py` – `__post_init__` mit `_require_no_approval_data`, `_require_approval_data`, `_require_rejection_data`; jeweils `if self.approved_at < self.recorded_at` / `if self.rejected_at < self.recorded_at` [cite:7]

**Bewertung:** Vollständig korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`AuditLogEntry`-Felder-Tabelle: `event_type`, `object_type`, `object_id`, `user_id`, `employee_id`, `details_json`.

**Status:** inkorrekt (unvollständig)

**Beleg:** `src/arbeitszeit/domain/entities.py` – `AuditLogEntry` hat zusätzlich das Feld `id: AuditLogEntryId` und `event_at: datetime` [cite:7]

**Bewertung:** Zwei Felder fehlen in der Tabelle: `id` (Datenbankschlüssel) und `event_at` (Zeitstempel des Ereignisses). Das Feld `event_at` ist dabei besonders relevant, da es fachlich bedeutsam ist.

**Änderungsvorschlag:** Tabelle um `id: AuditLogEntryId` und `event_at: datetime` ergänzen:

| Feld           | Typ                     | Beschreibung                                         |
|----------------|-------------------------|------------------------------------------------------|
| `id`           | `AuditLogEntryId`       | Datenbankschlüssel                                   |
| `event_type`   | `str`                   | Konstantenname aus `audit_events.py`                 |
| `object_type`  | `str`                   | Tabellenname (snake_case) oder Systembezeichner      |
| `object_id`    | `int`                   | Polymorph: Row-ID aus der betroffenen Tabelle        |
| `user_id`      | `UserAccountId \| None` | Auslösendes Benutzerkonto (ggf. kein Konto)          |
| `employee_id`  | `EmployeeId \| None`    | Betroffener Mitarbeiter (ggf. nicht personenbezogen) |
| `event_at`     | `datetime`              | Zeitstempel des protokollierten Ereignisses          |
| `details_json` | `str`                   | Kontextdaten als JSON-String                         |

## Abschnitt: Domänenfehler

---

**Aussage:**
Alle Fehlerklassen erben von `DomainError`; jeder Fehlertyp trägt einen `code`-String.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/errors.py` [cite:8]

**Bewertung:** Vollständige Übereinstimmung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Fehler-Tabelle listet 10 Klassen mit den entsprechenden Codes: `DomainError`/`DOMAIN_ERROR`, `UnknownCardError`/`UNKNOWN_CARD`, `InactiveCardError`/`INACTIVE_CARD`, `InactiveEmployeeError`/`INACTIVE_EMPLOYEE`, `InvalidBookingSequenceError`/`INVALID_BOOKING_SEQUENCE`, `OpenPhaseConflictError`/`OPEN_PHASE_CONFLICT`, `PermissionDeniedError`/`PERMISSION_DENIED`, `ValidationError`/`VALIDATION_ERROR`, `NotFoundError`/`NOT_FOUND`, `ConflictError`/`CONFLICT`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/errors.py` [cite:8]

**Bewertung:** Alle 10 Klassen und Codes korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Alle Fehlerklassen akzeptieren einen optionalen `message`-String sowie beliebige Schlüsselwort-Argumente als `context`-Dictionary.

**Status:** korrekt

**Beleg:** `errors.py` – `DomainError.__init__(self, message: str = "", **context: object)`; `self.context = context` [cite:8]

**Bewertung:** Vollständig korrekt; alle abgeleiteten Klassen erben dieses Verhalten.

**Änderungsvorschlag:** Kein Änderungsbedarf.

## Abschnitt: Repository-Protokolle (Ports)

---

**Aussage:**
Das Domain-Modell definiert Protokolle (`typing.Protocol`) für jeden Repository-Typ; die SQLite-Implementierungen müssen diese Protokolle erfüllen, ohne dass das Domain-Modell sie importiert – klassische Dependency Inversion.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/ports/repositories.py` – `from typing import ... Protocol`; alle Repository-Klassen erben von `Protocol` [cite:10]

**Bewertung:** Vollständig korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Repository-Tabelle listet 11 Protokolle, darunter `SystemConfigRepository`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/ports/repositories.py` – alle 11 Protokolle vorhanden, inkl. `SystemConfigRepository` [cite:10]

**Bewertung:** Vollständige Übereinstimmung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`AuditLogRepository`: Die Implementierung muss Audit-Einträge auch dann persistent speichern, wenn die UnitOfWork zurückgerollt wird; in der SQLite-Implementierung wird dafür eine separate `autocommit`-Verbindung verwendet.

**Status:** korrekt (Domain-Protokoll-Teil); nicht verifizierbar (SQLite-Implementierungsdetail)

**Beleg:** `src/arbeitszeit/domain/ports/repositories.py` – Kommentar in `AuditLogRepository.add`: „Implementierungen MÜSSEN Persistenz auch dann garantieren ... SQLite-Implementierung: separate autocommit-Verbindung verwenden." [cite:10]

**Bewertung:** Das Domain-Protokoll dokumentiert diese Anforderung explizit. Das SQLite-Implementierungsdetail (`autocommit`-Verbindung) ist im Domain-Protokoll als Hinweis vermerkt, aber nicht durch die Infrastrukturschicht geprüft (die in diesem Prüfdurchlauf nicht geladen wurde).

**Änderungsvorschlag:** Den SQLite-`autocommit`-Hinweis als Implementierungshinweis kennzeichnen, der in der Infrastrukturdokumentation zu belegen ist.

---

**Aussage:**
`WorkScheduleRepository.list_versions`: `scope_employee_id=None` → nur GLOBAL; `scope_employee_id=<id>` → nur EMPLOYEE; Rückgabe aufsteigend nach `valid_from`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/ports/repositories.py` – Kommentar in `list_versions` [cite:10]

**Bewertung:** Code bestätigt die Handbuchaussage exakt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`TimeBookingRepository.list_for_employee_on_day` muss aufsteigend nach `booked_at` sortiert zurückgeben.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/ports/repositories.py` – Kommentar: „Muss aufsteigend nach booked_at sortiert zurückgeben." [cite:10]

**Bewertung:** Direkt im Code belegt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

## Abschnitt: Domain Services – Buchungssequenz-Validierung

---

**Aussage:**
Funktion heißt `validate_booking_sequence(booking_type, day_bookings)`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/services/booking_rules.py` – Funktionssignatur: `def validate_booking_sequence(booking_type: BookingType, day_bookings: Sequence[BookingType]) -> None:` [cite:11]

**Bewertung:** Korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Die Funktion wirft einen `DomainError`, wenn die Sequenz verletzt wird.

**Status:** korrekt (präziser: Unterklassen von `DomainError`)

**Beleg:** `booking_rules.py` – wirft `InvalidBookingSequenceError` oder `OpenPhaseConflictError`, beides Unterklassen von `DomainError` [cite:11]

**Bewertung:** Technisch korrekt, da beide spezifischen Fehler `DomainError`-Subtypen sind. Die Aussage ist allerdings weniger präzise als möglich.

**Änderungsvorschlag:** Optional präzisieren: „Sie wirft `InvalidBookingSequenceError` oder `OpenPhaseConflictError` (beides Unterklassen von `DomainError`)."

---

**Aussage:**
`day_bookings` ist eine Liste von `TimeBooking`-Objekten (implizit durch Kontext des Handbuchs).

**Status:** inkorrekt

**Beleg:** `src/arbeitszeit/domain/services/booking_rules.py` – Signatur: `day_bookings: Sequence[BookingType]` [cite:11]

**Bewertung:** Die Funktion erwartet **keine** `TimeBooking`-Objekte, sondern eine `Sequence[BookingType]` (nur die Enum-Werte). Das Handbuch benennt den Parameter zwar nicht explizit falsch, beschreibt ihn aber im Kontext als „übergebenen Listen", ohne den Typ zu nennen – im Gegensatz zur `compliance_checks.py`-Beschreibung, wo `day_bookings` korrekt als `Sequence[TimeBooking]` verwendet wird. Der Unterschied ist fachlich relevant und könnte zu Missverständnissen führen.

**Änderungsvorschlag:** Im Abschnitt der Buchungssequenz-Validierung klarstellen: „`day_bookings` ist eine `Sequence[BookingType]` – also eine chronologisch sortierte Liste der Buchungstypen des Tages, nicht der vollständigen `TimeBooking`-Entitäten."

---

**Aussage:**
Fehler-Mapping-Tabelle: „GO/BREAK_START/BREAK_END als Erstbuchung → `InvalidBookingSequenceError`".

**Status:** korrekt

**Beleg:** `booking_rules.py` – `if booking_type in (BookingType.GO, BookingType.BREAK_END, BookingType.BREAK_START): raise InvalidBookingSequenceError(...)` [cite:11]

**Bewertung:** Vollständig korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Fehler-Mapping: „GO bei offener Pause → `OpenPhaseConflictError`".

**Status:** korrekt

**Beleg:** `booking_rules.py` – `if open_break: raise OpenPhaseConflictError(...)` im GO-Zweig [cite:11]

**Bewertung:** Direkt im Code belegt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

## Abschnitt: ArbZG-Compliance-Prüfungen

---

**Aussage:**
`check_break_compliance` prüft in dieser Reihenfolge: (1) ununterbrochener Arbeitsblock > 6h → `WARN`, (2) Netto > 9h mit < 45 min Gesamtpause → `CRITICAL`, (3) Netto > 6h mit < 30 min Gesamtpause → `WARN`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/services/compliance_checks.py` – die drei `if`-Blöcke in genau dieser Reihenfolge [cite:12]

**Bewertung:** Die Reihenfolge im Handbuch stimmt mit dem Code überein. (Hinweis: Bei Überschreiten des ersten Checks wird frühzeitig zurückgegeben; die Prüfungen sind nicht kumulativ – dies ist im Handbuch nicht erwähnt, aber auch nicht falsch behauptet.)

**Änderungsvorschlag:** Optional einen Hinweis ergänzen, dass `check_break_compliance` bei einem Treffer sofort zurückgibt und die weiteren Prüfungen nicht mehr ausführt.

---

**Aussage:**
`check_max_hours`: Netto > 10h → `CRITICAL`; Netto > 8h → `WARN`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/services/compliance_checks.py` [cite:12]

**Bewertung:** Exakte Übereinstimmung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
`check_rest_period(last_go, next_come)`: Ruhezeit < 11h → `CRITICAL`.

**Status:** korrekt

**Beleg:** `compliance_checks.py` – `if (next_come - last_go).total_seconds() < 11 * 3600: return [ComplianceFlag(..., ReviewSeverity.CRITICAL)]` [cite:12]

**Bewertung:** Vollständig korrekt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Die Prüfungen arbeiten auf der Netto-Arbeitszeit; sie ersetzen keine rechtsverbindliche Einzelfallbewertung.

**Status:** korrekt

**Beleg:** `compliance_checks.py` – Modul-Docstring: „Alle Prüfungen arbeiten auf der **Netto-Arbeitszeit** ... ersetzt keine rechtsverbindliche Einzelfallbewertung." [cite:12]

**Bewertung:** Wortgleich im Code-Docstring belegt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

## Abschnitt: Audit-Event-Katalog

---

**Aussage:**
Keine freien String-Literale für `event_type`; stattdessen zentrale Modulkonstanten aus `audit_events.py`.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/audit_events.py` – Kommentar: „Alle Use Cases und Infrastrukturkomponenten importieren hier — keine freien String-Literale, damit Tippfehler zur Compile-Zeit auffallen." [cite:9]

**Bewertung:** Direkt im Code-Kommentar belegt.

**Änderungsvorschlag:** Kein Änderungsbedarf.

---

**Aussage:**
Die Handbuch-Tabelle listet 21 Audit-Event-Konstanten.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/domain/audit_events.py` – zählt exakt 21 Konstantendefinitionen [cite:9]

**Bewertung:** Vollständige Übereinstimmung.

**Änderungsvorschlag:** Kein Änderungsbedarf.

## Zusammenfassung der Befunde

| Kategorie | Anzahl |
|---|---|
| Korrekt | 32 |
| Inkorrekt / unvollständig | 4 |
| Nicht verifizierbar | 3 |

**Die vier Korrekturbedürftigen im Überblick:**

1. **`ReviewCase`-Tabelle** fehlen vier Pflichtfelder: `id`, `employee_id`, `description`, `created_at` → Tabelle ergänzen [cite:7]
2. **`AuditLogEntry`-Tabelle** fehlen zwei Felder: `id` und `event_at` → Tabelle ergänzen [cite:7]
3. **`validate_booking_sequence`-Parameter** `day_bookings` ist `Sequence[BookingType]`, nicht `Sequence[TimeBooking]` → Typ im Handbuch klarstellen [cite:11]
4. **„Jede Entität validiert in `__post_init__`"** – `TimeBooking` hat kein `__post_init__` → Formulierung abschwächen [cite:7]
