# Prüfbericht – `docs/module/handbuch_application_layer.md`

## Gesamteinschätzung

Das Handbuch ist insgesamt von hoher Qualität und deckt die Struktur der Anwendungsschicht weitgehend korrekt ab. Die kritischsten Abweichungen betreffen das **Verzeichnis-Listing** in Abschnitt 4.1 (fehlende Dateien, falsche Dateinamen), die **`BootstrapAdminUseCase`-Beschreibung** (falsche Audit-Event-Typen- und Duplikat-Prüflogik-Darstellung) sowie die **`ChangeUserRoleUseCase`-Beschreibung** (falsche Fehlerlogik). Einige Aussagen zu Referenznormen (Regelwerk v3, Pflichtenheft v3) sowie zur `_evaluate_booking()`-Methode sind nicht verifizierbar.

---

## Abschnitt 4.1 – Überblick und Einordnung

---

**Befund 1**

Aussage:
Das Verzeichnis-Listing zeigt `use_cases/` mit den Dateien: `book_time.py`, `correct_booking.py`, `register_supplement.py`, `approve_supplement.py`, `reject_supplement.py`, `manage_work_schedule.py`.

Status:
**inkorrekt** (unvollständig)

Beleg:
[`src/arbeitszeit/application/use_cases/`-Verzeichnis-Listing](https://github.com/iCodator/arbeitszeit/tree/2e8781e9681b16c373c337b2ea1d901a9f4db264/src/arbeitszeit/application/use_cases) [cite:5]

Bewertung:
Das tatsächliche Verzeichnis enthält zusätzlich `manage_employees.py`, `manage_rfid_cards.py` und `manage_user_accounts.py`. Diese drei Dateien fehlen im Handbuch-Listing vollständig. [cite:5]

Änderungsvorschlag:
Das Listing ergänzen:
```text
use_cases/
    ├── __init__.py
    ├── book_time.py
    ├── correct_booking.py
    ├── register_supplement.py
    ├── approve_supplement.py
    ├── reject_supplement.py
    ├── manage_work_schedule.py
    ├── manage_employees.py
    ├── manage_rfid_cards.py
    └── manage_user_accounts.py
```

---

## Abschnitt 4.2 – Commands

---

**Befund 2**

Aussage:
Commands importieren Value-Object-Typen aus `arbeitszeit.domain.value_objects`, um Typsicherheit ohne Primitive Obsession zu gewährleisten.

Status:
**korrekt**

Beleg:
`commands.py`, Importblock: `from arbeitszeit.domain.value_objects import (DeviceEventId, EmployeeId, RfidCardId, SupplementId, TerminalId, TimeBookingId, UserAccountId,)` [cite:6]

Bewertung:
Die Aussage ist vollständig durch den Code belegbar.

Änderungsvorschlag:
Keiner.

---

**Befund 3**

Aussage:
Alle Commands sind `@dataclass(frozen=True, slots=True)`.

Status:
**korrekt**

Beleg:
`commands.py`, alle Klassen tragen `@dataclass(frozen=True, slots=True)` [cite:6]

Bewertung:
Alle 16 Command-Klassen in `commands.py` verwenden `@dataclass(frozen=True, slots=True)`.

Änderungsvorschlag:
Keiner.

---

**Befund 4**

Aussage:
Die Command-Tabelle listet 16 Commands, darunter `BookCommand`, `CreateSupplementCommand`, `CreateCorrectionCommand`, `ApproveSupplementCommand`, `RejectSupplementCommand`, `ChangeWorkScheduleCommand`, `CreateEmployeeCommand`, `DeactivateEmployeeCommand`, `AssignRfidCardCommand`, `ReplaceRfidCardCommand`, `DeactivateRfidCardCommand`, `CreateUserAccountCommand`, `DeactivateUserAccountCommand`, `ReactivateUserAccountCommand`, `ChangeUserRoleCommand`, `BootstrapAdminCommand`.

Status:
**korrekt**

Beleg:
`commands.py`, vollständige Liste aller Klassen [cite:6]

Bewertung:
Alle 16 im Handbuch genannten Command-Klassen sind identisch im Code vorhanden.

Änderungsvorschlag:
Keiner.

---

## Abschnitt 4.3 – Results

---

**Befund 5**

Aussage:
`BookResult` enthält die Felder `booking_id`, `status`, `follow_up_case_ids`.

Status:
**korrekt**

Beleg:
`results.py`: `class BookResult: booking_id: TimeBookingId; status: BookingStatus; follow_up_case_ids: tuple[ReviewCaseId, ...]` [cite:7]

Bewertung:
Felder stimmen exakt überein.

Änderungsvorschlag:
Keiner.

---

**Befund 6**

Aussage:
`SupplementResult` enthält die Felder `supplement_id`, `review_case_id`.

Status:
**korrekt**

Beleg:
`results.py`: `class SupplementResult: supplement_id: SupplementId; review_case_id: ReviewCaseId | None` [cite:7]

Bewertung:
Felder stimmen überein. Der `None`-Fall bei `review_case_id` wird im Handbuch nicht explizit erwähnt, widerspricht aber auch nicht der Aussage.

Änderungsvorschlag:
Optional kann ergänzt werden: `review_case_id` ist `ReviewCaseId | None`.

---

**Befund 7**

Aussage:
`CorrectionResult` enthält die Felder `correction_id`, `updated_booking_id`, `review_case_id`.

Status:
**korrekt**

Beleg:
`results.py`: `class CorrectionResult: correction_id: BookingCorrectionId; updated_booking_id: TimeBookingId; review_case_id: ReviewCaseId | None` [cite:7]

Bewertung:
Felder stimmen überein.

Änderungsvorschlag:
Keiner.

---

**Befund 8**

Aussage:
`WorkScheduleChangeResult` enthält die Felder `new_version_id`, `superseded_version_id`.

Status:
**korrekt**

Beleg:
`results.py`: `class WorkScheduleChangeResult: new_version_id: WorkScheduleVersionId; superseded_version_id: WorkScheduleVersionId | None` [cite:7]

Bewertung:
Felder stimmen überein. `superseded_version_id` ist `Optional`, was das Handbuch nicht angibt – aber nicht widerlegt.

Änderungsvorschlag:
Keiner (optional: `| None` vermerken).

---

**Befund 9**

Aussage:
`RejectSupplementResult` enthält die Felder `supplement_id`, `review_case_id`.

Status:
**korrekt**

Beleg:
`results.py`: `class RejectSupplementResult: supplement_id: SupplementId; review_case_id: ReviewCaseId | None` [cite:7]

Bewertung:
Felder stimmen überein.

Änderungsvorschlag:
Keiner.

---

**Befund 10**

Aussage:
Void-Use-Cases (Deactivate/Reactivate/ChangeRole) geben `None` zurück — kein eigenes Result-Objekt.

Status:
**korrekt**

Beleg:
`manage_user_accounts.py`: `DeactivateUserAccountUseCase.execute()` → `None`, `ReactivateUserAccountUseCase.execute()` → `None`, `ChangeUserRoleUseCase.execute()` → `None`; in `results.py` existieren keine Result-Klassen für diese Use Cases [cite:7][cite:12]

Bewertung:
Die Aussage ist korrekt. Gilt analog auch für `DeactivateEmployeeUseCase` und die RFID-`DeactivateRfidCardUseCase`. [cite:13]

Änderungsvorschlag:
Keiner.

---

## Abschnitt 4.4 – Queries

---

**Befund 11**

Aussage:
Die eigentlichen Datenbankabfragen liegen in `infrastructure/export/report_queries.py`.

Status:
**korrekt**

Beleg:
`queries.py`, Docstring: `„Die Ausführung der Abfragen liegt in infrastructure/export/report_queries.py."` [cite:9]

Bewertung:
Die Quelldatei selbst belegt diese Behauptung im Docstring.

Änderungsvorschlag:
Keiner.

---

**Befund 12**

Aussage:
`CorrectionRow` ist dokumentiert mit Verweis auf „Regelwerk v3 §12".

Status:
**nicht verifizierbar**

Beleg:
`queries.py`: Docstring `CorrectionRow`: `„Regelwerk v3 §12"` — das referenzierte Regelwerk-Dokument ist im Repository nicht als auswertbare Datei vorhanden [cite:9]

Bewertung:
Die Normenreferenz findet sich im Code-Docstring, das referenzierte Regelwerk ist jedoch nicht direkt im Repository zugänglich, sodass Inhalt und Versionsnummer nicht verifiziert werden können.

Änderungsvorschlag:
Ohne zugängliches Regelwerk nicht änderbar. Kennzeichnung als „interne Referenz, nicht öffentlich verifizierbar" erwägen oder unverändert belassen.

---

**Befund 13**

Aussage:
`ReviewCaseRow` enthält das Feld „Offene Prüffälle" (mit Verweis auf Pflichtenheft v3 §7.6/§7.12).

Status:
**nicht verifizierbar** (Teilaussage)

Beleg:
`queries.py`: `ReviewCaseRow`-Docstring: `„Offener oder aktiver Prüffall (Pflichtenheft v3 §7.6/§7.12)"` — der Klassen-Docstring weicht vom Handbuch-Wortlaut ab: im Handbuch steht „Offene Prüffälle", im Code „Offener oder aktiver Prüffall" [cite:9]

Bewertung:
Der Code beschreibt die Row als für offene **oder aktive** Prüffälle, das Handbuch nennt nur „Offene Prüffälle". Der Begriff „aktiv" fällt unter die nicht verifizierbare Normenreferenz.

Änderungsvorschlag:
Handbuchtext angleichen: `ReviewCaseRow` → „Offene oder aktive Prüffälle (Pflichtenheft v3 §7.6/§7.12)".

---

## Abschnitt 4.5 – Unit of Work

---

**Befund 14**

Aussage:
`UnitOfWork` ist ein `Protocol` (strukturelles Typing, kein Erben nötig).

Status:
**korrekt**

Beleg:
`unit_of_work.py`: `class UnitOfWork(Protocol):` [cite:8]

Bewertung:
Vollständig korrekt.

Änderungsvorschlag:
Keiner.

---

**Befund 15**

Aussage:
Das Handbuch listet 11 Repositories im `UnitOfWork`: `employee_repo`, `user_account_repo`, `rfid_card_repo`, `time_booking_repo`, `work_schedule_repo`, `review_case_repo`, `supplement_repo`, `booking_correction_repo`, `audit_log_repo`, `system_config_repo`, `device_event_repo`.

Status:
**korrekt**

Beleg:
`unit_of_work.py`: alle 11 genannten Repository-Attribute sind identisch deklariert [cite:8]

Bewertung:
Vollständige Übereinstimmung.

Änderungsvorschlag:
Keiner.

---

**Befund 16**

Aussage:
Das Audit-Log wird nach `commit()` geschrieben (nicht davor).

Status:
**korrekt**

Beleg:
`book_time.py`, Kommentar: `„Erst commit, dann Audit-Log schreiben: nach commit hält conn keinen RESERVED-Lock mehr, sodass audit_conn (autocommit) schreiben kann ohne zu blockieren."` Gleiches gilt in `correct_booking.py` und allen anderen Use Cases [cite:10][cite:11]

Bewertung:
Die Aussage ist durchgehend im gesamten Codebase belegt.

Änderungsvorschlag:
Keiner.

---

## Abschnitt 4.6.1 – `BookUseCase`

---

**Befund 17**

Aussage:
Schritt 6 der Ablaufbeschreibung: „Regelarbeitszeit prüfen → ggf. `ComplianceFlag(OUTSIDE_SCHEDULE_WINDOW, WARN)` setzen".

Status:
**korrekt**

Beleg:
`book_time.py`: `schedule_flags = [ComplianceFlag(ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW, ReviewSeverity.WARN)]` [cite:10]

Bewertung:
Exakt so implementiert.

Änderungsvorschlag:
Keiner.

---

**Befund 18**

Aussage:
Statuslogik: `OPEN` → Buchungstyp ist `COME` oder `BREAK_START` (Tag noch offen).

Status:
**korrekt**

Beleg:
`book_time.py`, `_evaluate_booking()`: `if booking_type in (BookingType.COME, BookingType.BREAK_START): return BookingStatus.OPEN, list(extra_flags or [])` [cite:10]

Bewertung:
Exakt so implementiert.

Änderungsvorschlag:
Keiner.

---

**Befund 19**

Aussage:
Ablehnungspfade: In den Ablehnungspfaden (unbekannte/inaktive Karte) darf vor dem Audit-Log-Schreibvorgang **keine** andere Schreiboperation auf der Hauptverbindung stattgefunden haben.

Status:
**korrekt**

Beleg:
`book_time.py`, Kommentar: `„INVARIANTE Ablehnungspfade: Vor jedem audit_log_repo.add() in einem Ablehnungspfad (UnknownCard/InactiveCard) darf conn keine Schreiboperation (INSERT/UPDATE/DELETE) ausgeführt haben."` [cite:10]

Bewertung:
Die Invariante ist explizit im Kommentar dokumentiert und durch den Code (nur SELECTs vor dem ersten Audit-Write) belegt.

Änderungsvorschlag:
Keiner.

---

**Befund 20**

Aussage:
Abschnitt 4.7: Ablehnungspfade nutzen eine „Autocommit-Audit-Verbindung".

Status:
**nicht verifizierbar**

Beleg:
`book_time.py`: Die Use-Case-Schicht ruft nur `self._uow.audit_log_repo.add()` auf. Die Implementierung des Audit-Log-Repositories (autocommit vs. normale Verbindung) liegt in der Infrastrukturschicht, die nicht Teil dieser Prüfung ist [cite:10]

Bewertung:
Aus der Anwendungsschicht allein ist der „Autocommit"-Charakter der Audit-Verbindung nicht ableitbar; dieser ist ein Infrastrukturdetail.

Änderungsvorschlag:
Die Formulierung könnte präzisiert werden: „Die Audit-Verbindung persistiert unabhängig vom UoW-Commit (Implementierungsdetail der Infrastrukturschicht)." – oder als Hinweis kennzeichnen, dass dieses Detail in der Infrastrukturschicht implementiert ist.

---

## Abschnitt 4.6.2 – `CorrectBookingUseCase`

---

**Befund 21**

Aussage:
Schritt 1: Berechtigungsprüfung des handelnden Benutzers (ADMIN oder REVIEWER).

Status:
**korrekt**

Beleg:
`correct_booking.py`: `actor.role not in {UserRole.ADMIN, UserRole.REVIEWER}` → `PermissionDeniedError` [cite:11]

Bewertung:
Vollständig korrekt.

Änderungsvorschlag:
Keiner.

---

**Befund 22**

Aussage:
Korrigierbare Prüffalltypen (`_CORRECTABLE_CASE_TYPES`): `OPEN_WORK_PHASE`, `OPEN_BREAK_PHASE`, `IMPLAUSIBLE_SEQUENCE`, `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION`, `OUTSIDE_SCHEDULE_WINDOW`.

Status:
**korrekt**

Beleg:
`correct_booking.py`, `_CORRECTABLE_CASE_TYPES = frozenset({...})` — alle 7 genannten Typen sind identisch aufgeführt [cite:11]

Bewertung:
Vollständige und exakte Übereinstimmung.

Änderungsvorschlag:
Keiner.

---

**Befund 23**

Aussage:
Nicht durch Buchungskorrektur schließbar: `MANUAL_ENTRY_REVIEW`, `UNKNOWN_CARD_ATTEMPT`, `INACTIVE_CARD_ATTEMPT`, `TIME_ANOMALY`.

Status:
**korrekt**

Beleg:
`correct_booking.py`, Kommentar: `„MANUAL_ENTRY_REVIEW (Nachtragsprozess), UNKNOWN_CARD_ATTEMPT, INACTIVE_CARD_ATTEMPT und TIME_ANOMALY werden nicht durch eine Buchungskorrektur geschlossen."` [cite:11]

Bewertung:
Vollständig durch Code-Kommentar belegt.

Änderungsvorschlag:
Keiner.

---

## Abschnitt 4.6.7 – Mitarbeiterverwaltung

---

**Befund 24**

Aussage:
Schritt 2 bei `CreateEmployeeUseCase`: „Duplikat-Personalnummer prüfen → `ConflictError`".

Status:
**korrekt** (mit Präzisierungsbedarf)

Beleg:
`manage_employees.py`: `self._uow.employee_repo.get_active_by_personnel_no(cmd.personnel_no)` — es wird nur auf **aktive** Personalnummern geprüft [cite:13]

Bewertung:
Die Prüfung betrifft ausschließlich **aktive** Mitarbeiter-Personalnummern (`get_active_by_personnel_no`). Das Handbuch schreibt schlicht „Duplikat-Personalnummer", was den aktiven Scope nicht erwähnt.

Änderungsvorschlag:
Schritt 2 präzisieren: „Duplikat-Personalnummer unter aktiven Mitarbeitern prüfen → `ConflictError`".

---

**Befund 25**

Aussage:
Schritt 3 bei `CreateEmployeeUseCase`: „`Employee`-Entität anlegen via `EmployeeRepository.add()`".

Status:
**korrekt**

Beleg:
`manage_employees.py`: `saved = self._uow.employee_repo.add(Employee(...))` [cite:13]

Bewertung:
Exakt so implementiert.

Änderungsvorschlag:
Keiner.

---

## Abschnitt 4.6.9 – Benutzerkontenverwaltung

---

**Befund 26**

Aussage:
`CreateUserAccountUseCase` Schritt 2: „Rolle prüfen: nur `ADMIN`, `REVIEWER`, `TECH` erlaubt → `ValidationError`".

Status:
**korrekt**

Beleg:
`manage_user_accounts.py`: `_ALLOWED_ROLES = {UserRole.ADMIN, UserRole.REVIEWER, UserRole.TECH}`, `if cmd.role not in _ALLOWED_ROLES: raise ValidationError(...)` [cite:12]

Bewertung:
Vollständig korrekt.

Änderungsvorschlag:
Keiner.

---

**Befund 27**

Aussage:
`ChangeUserRoleUseCase`: „Prüft zusätzlich, dass die neue Rolle nicht `EMPLOYEE` ist (`ValidationError`)."

Status:
**inkorrekt** (irreführende Vereinfachung)

Beleg:
`manage_user_accounts.py`: Die Prüfung lautet `if cmd.new_role not in _ALLOWED_ROLES: raise ValidationError(...)`. `_ALLOWED_ROLES = {ADMIN, REVIEWER, TECH}` — verbotene Rollen sind **alle**, die nicht in `_ALLOWED_ROLES` sind (also nicht nur `EMPLOYEE`). [cite:12]

Bewertung:
Das Handbuch stellt es so dar, als würde nur `EMPLOYEE` als neue Rolle abgelehnt. Tatsächlich prüft der Code gegen eine positive Allowlist (`ADMIN`, `REVIEWER`, `TECH`). Falls das Enum weitere Rollen enthält (z. B. `GUEST`), wären diese ebenfalls verboten. Die Formulierung ist daher irreführend vereinfacht.

Änderungsvorschlag:
Formulierung ändern zu: „Prüft zusätzlich, dass die neue Rolle in der erlaubten Menge `{ADMIN, REVIEWER, TECH}` liegt, andernfalls `ValidationError`."

---

**Befund 28**

Aussage:
`BootstrapAdminUseCase` Beschreibung: „Prüft via `has_active_admin()`, ob bereits ein aktiver Admin existiert → `ConflictError`."

Status:
**korrekt**

Beleg:
`manage_user_accounts.py`: `if self._uow.user_account_repo.has_active_admin(): raise ConflictError(...)` [cite:12]

Bewertung:
Vollständig korrekt.

Änderungsvorschlag:
Keiner.

---

**Befund 29**

Aussage:
`BootstrapAdminUseCase`: „Im Audit-Log wird `user_id = saved.id` (Self-Reference) verwendet."

Status:
**korrekt**

Beleg:
`manage_user_accounts.py`: `user_id=saved.id` im `AuditLogEntry`-Aufruf des `BootstrapAdminUseCase` [cite:12]

Bewertung:
Vollständig korrekt.

Änderungsvorschlag:
Keiner.

---

**Befund 30**

Aussage:
`BootstrapAdminUseCase` verwendet als Audit-Event den Typ implizit (Handbuch nennt keinen expliziten Typ).

Status:
**nicht verifizierbar** (nicht im Handbuch behauptet, aber Klärungsbedarf)

Beleg:
`manage_user_accounts.py`: Das Audit-Log verwendet `audit_events.USER_ACCOUNT_CREATED` (nicht einen eigenen `BOOTSTRAP_ADMIN`-Typ), mit dem Zusatzfeld `"bootstrap": True` im `details_json` [cite:12]

Bewertung:
Das Handbuch macht keine Aussage über den konkreten Audit-Event-Typ des Bootstrap-Vorgangs. Im Code wird `USER_ACCOUNT_CREATED` mit Bootstrap-Flag verwendet, was ein Leser des Handbuchs nicht erwarten würde.

Änderungsvorschlag:
Ergänzung empfohlen: „Das Audit-Log schreibt `USER_ACCOUNT_CREATED` mit dem Zusatzfeld `bootstrap: true` im `details_json` (kein eigener Event-Typ)."

---

**Befund 31**

Aussage:
`BootstrapAdminUseCase` prüft ausschließlich via `has_active_admin()` (kein Username-Duplikat-Check laut Handbuch).

Status:
**inkorrekt** (unvollständig)

Beleg:
`manage_user_accounts.py`: Nach dem `has_active_admin()`-Check folgt ein zweiter Check: `if self._uow.user_account_repo.get_by_username(cmd.username) is not None: raise ConflictError(...)` [cite:12]

Bewertung:
Das Handbuch beschreibt nur den `has_active_admin()`-Check als Konfliktprüfung. Der Code enthält zusätzlich einen Username-Duplikat-Check, der ebenfalls `ConflictError` wirft. Dieser zweite Prüfschritt fehlt im Handbuch.

Änderungsvorschlag:
Ablauf ergänzen: „1. Prüft via `has_active_admin()`, ob bereits ein aktiver Admin existiert → `ConflictError`. **2. Prüft, ob der gewünschte Username bereits vergeben ist → `ConflictError`.**"

---

## Abschnitt 4.7 – Querschnittliche Entwurfsprinzipien

---

**Befund 32**

Aussage:
`frozen=True` verhindert versehentliche Mutation nach der Erzeugung. `slots=True` reduziert Speicherbedarf und beschleunigt Attributzugriffe.

Status:
**korrekt** (Code-Beleg; Python-Semantik nicht im Repo verifizierbar, aber Decorator-Nutzung ist belegbar)

Beleg:
`commands.py`, `results.py`: alle Klassen mit `@dataclass(frozen=True, slots=True)` [cite:6][cite:7]

Bewertung:
Die Verwendung des Decorators ist vollständig belegbar. Die beschriebenen Effekte von `frozen` und `slots` entsprechen der Python-Sprachspezifikation.

Änderungsvorschlag:
Keiner.

---

**Befund 33**

Aussage:
Alle manuellen Use Cases prüfen zu Beginn die Benutzerrolle und werfen `PermissionDeniedError`, bevor sie irgendwelche Datenbankzugriffe ausführen.

Status:
**korrekt** (mit einer Nuance)

Beleg:
`correct_booking.py`, `manage_employees.py`, `manage_user_accounts.py`, `manage_rfid_cards.py`: alle beginnen mit `actor = self._uow.user_account_repo.get_by_id(...)` gefolgt von `raise PermissionDeniedError` [cite:11][cite:12][cite:13]

Bewertung:
Der Berechtigungscheck selbst erfordert technisch einen Datenbankzugriff (`get_by_id` des Actors). Die Formulierung „bevor sie irgendwelche Datenbankzugriffe ausführen" ist daher semantisch ungenau — gemeint ist offenbar: bevor sie *fachliche* Datenbankzugriffe (auf das Zielobjekt) ausführen.

Änderungsvorschlag:
Formulierung präzisieren: „Alle manuellen Use Cases prüfen zu Beginn die Benutzerrolle (via `get_by_id` des handelnden Accounts) und werfen `PermissionDeniedError`, bevor sie auf das Zielobjekt zugreifen."

---

**Befund 34**

Aussage:
Fehler-Tabelle in 4.7 nennt `InactiveEmployeeError` als eigenständige Fehlerklasse.

Status:
**korrekt**

Beleg:
`book_time.py` und `correct_booking.py`: `from arbeitszeit.domain.errors import InactiveEmployeeError` — wird geworfen bei inaktivem Mitarbeiter [cite:10][cite:11]

Bewertung:
Die Fehlerklasse existiert und wird in Use Cases verwendet.

Änderungsvorschlag:
Keiner.

---

## Abschnitt 4.8 – Erweiterungshinweise

---

**Befund 35**

Aussage:
„Compliance-Regel hinzufügen: Neue Prüffunktion in `domain/services/compliance_checks.py`, dann in `_evaluate_booking()` der betroffenen Use Cases aufrufen."

Status:
**korrekt**

Beleg:
`book_time.py`: `from arbeitszeit.domain.services.compliance_checks import (ComplianceFlag, check_break_compliance, check_max_hours, check_rest_period,)` und `_evaluate_booking()`-Funktion [cite:10]

Bewertung:
Das Muster ist genau so im Code sichtbar: Compliance-Funktionen aus `compliance_checks.py` werden in `_evaluate_booking()` aufgerufen.

Änderungsvorschlag:
Keiner.

---

## Zusammenfassung der Befunde nach Priorität

| # | Abschnitt | Status | Schwere |
|---|---|---|---|
| 1 | 4.1 Verzeichnis-Listing | **inkorrekt** | hoch – 3 Dateien fehlen |
| 31 | 4.6.9 Bootstrap-Duplikat-Check | **inkorrekt** | mittel – fehlender Prüfschritt |
| 27 | 4.6.9 ChangeUserRole-Logik | **inkorrekt** | mittel – irreführende Vereinfachung |
| 24 | 4.6.7 Duplikat-Personalnummer | korrekt (Präzisierung) | niedrig – `get_active_by_personnel_no` |
| 13 | 4.4 ReviewCaseRow-Beschreibung | nicht verifizierbar | niedrig – Wortlaut-Abweichung |
| 20 | 4.7 Autocommit-Audit-Verbindung | nicht verifizierbar | niedrig – Infrastrukturdetail |
| 30 | 4.6.9 Bootstrap-Audit-Event-Typ | nicht verifizierbar | niedrig – Ergänzung empfohlen |
| 33 | 4.7 PermissionDenied-Timing | korrekt (Präzisierung) | niedrig – semantische Unschärfe |
