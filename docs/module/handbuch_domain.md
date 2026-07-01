# Handbuch `arbeitszeit` – Das Domain-Modell

**Kapitel:** 5
**Version:** 1.0
**Stand:** Juli 2026
**Quelldatei:** `docs/module/handbuch_domain.md`

## Überblick und Designprinzip

Das Domain-Modell ist der fachliche Kern des Systems `arbeitszeit`. Es enthält ausschließlich
Geschäftslogik und keinerlei Abhängigkeiten zu Datenbank, Hardware oder UI. Die Schicht ist
nach dem Prinzip **Domain-Driven Design (DDD)** aufgebaut: Entitäten, Value Objects,
Enumerationen, Fehlertypen und Domain Services sind klar voneinander getrennt.
Alle Dateien liegen unter `src/arbeitszeit/domain/`.

```text
src/arbeitszeit/domain/
├── __init__.py          # leer – kein öffentliches Re-Export
├── audit_events.py      # Katalog aller Audit-Log-Eventnamen
├── entities.py          # Entitäten (frozen dataclasses)
├── enums.py             # Alle StrEnum-Typen des Systems
├── errors.py            # Domänenfehler-Hierarchie
├── value_objects.py     # Starke ID-Typen via NewType
├── ports/
│   └── repositories.py  # Repository-Protokolle (Interfaces)
└── services/
    ├── booking_rules.py      # Buchungssequenz-Validierung
    └── compliance_checks.py  # ArbZG-Prüfhilfen
```

---

## Value Objects – Starke ID-Typen

**Datei:** `src/arbeitszeit/domain/value_objects.py`

Alle Primärschlüssel im System sind keine bloßen `int`-Werte, sondern eigene Typen,
die mit `typing.NewType` erzeugt werden:

| ID-Typ                  | Bedeutung                              |
|-------------------------|----------------------------------------|
| `EmployeeId`            | Mitarbeiter-Datensatz                  |
| `UserAccountId`         | Benutzerkonto (Login)                  |
| `RfidCardId`            | RFID-Karte                             |
| `TerminalId`            | Buchungsterminal (Hardware)            |
| `TimeBookingId`         | Zeitbuchung (COME/GO/Pause)            |
| `WorkScheduleVersionId` | Version einer Regelarbeitszeit         |
| `ReviewCaseId`          | Prüffall                               |
| `SupplementId`          | Nachtrag                               |
| `BookingCorrectionId`   | Korrektur einer Buchung                |
| `DeviceEventId`         | Geräteereignis (RFID-Scan, Numpad)     |
| `AuditLogEntryId`       | Eintrag im Audit-Log                   |

**Warum NewType?** Obwohl zur Laufzeit alle IDs schlichte `int`-Werte sind, behandelt
`mypy` sie als inkompatible Typen. Ein versehentlicher Aufruf wie
`booking_repo.get_by_id(employee.id)` wird damit bereits statisch als Typfehler
erkannt – ohne jeglichen Laufzeit-Overhead. Da alle ID-Typen Subtypen von `int` sind,
können sie ohne Konvertierung als SQL-Parameter übergeben werden.

---

## Enumerationen

**Datei:** `src/arbeitszeit/domain/enums.py`

Alle Zustands- und Klassenangaben des Systems sind als `StrEnum` definiert.
Das bedeutet: Die Enum-Werte sind gleichzeitig ihre eigene String-Darstellung
(z. B. `BookingType.COME == "COME"`), was die direkte Speicherung in SQLite
ohne separate Konvertierung ermöglicht.

### Buchungstypen (`BookingType`)

| Wert          | Bedeutung              |
|---------------|------------------------|
| `COME`        | Arbeitsbeginn          |
| `GO`          | Arbeitsende            |
| `BREAK_START` | Pausenbeginn           |
| `BREAK_END`   | Pausenende             |

### Buchungsstatus (`BookingStatus`)

| Wert               | Bedeutung                                        |
|--------------------|--------------------------------------------------|
| `OK`               | Buchung geprüft und regelkonform                 |
| `OPEN`             | Automatisch erzeugt, noch nicht abgeschlossen    |
| `WARN`             | Auffälligkeit, Prüfung empfohlen                 |
| `NEEDS_REVIEW`     | Prüffall wurde angelegt                          |
| `CORRECTED`        | Buchung wurde nachträglich korrigiert            |
| `CLOSED_WITH_NOTE` | Abgeschlossen mit Begründungsnotiz               |

### Prüffall-Typen (`ReviewCaseType`)

| Wert                          | Bedeutung                                        |
|-------------------------------|--------------------------------------------------|
| `OPEN_WORK_PHASE`             | Keine abschließende GO-Buchung vorhanden         |
| `OPEN_BREAK_PHASE`            | Keine BREAK_END-Buchung vorhanden                |
| `OUTSIDE_SCHEDULE_WINDOW`     | Buchung außerhalb der Regelarbeitszeit           |
| `POSSIBLE_BREAK_VIOLATION`    | Möglicher Verstoß gegen §4 ArbZG (Pausen)       |
| `POSSIBLE_REST_VIOLATION`     | Möglicher Verstoß gegen §5 ArbZG (Ruhezeit)     |
| `POSSIBLE_MAX_HOURS_VIOLATION`| Möglicher Verstoß gegen §3 ArbZG (10h-Grenze)   |
| `IMPLAUSIBLE_SEQUENCE`        | Buchungsreihenfolge ist fachlich unplausibel     |
| `UNKNOWN_CARD_ATTEMPT`        | Unbekannte RFID-Karte wurde gescannt             |
| `INACTIVE_CARD_ATTEMPT`       | Deaktivierte RFID-Karte wurde gescannt           |
| `TIME_ANOMALY`                | Zeitstempel weicht stark von Normalwerten ab     |
| `MANUAL_ENTRY_REVIEW`         | Manuell erfasster Eintrag muss geprüft werden    |

### Weitere Enumerationen

| Enum              | Werte                                        | Verwendung                        |
|-------------------|----------------------------------------------|-----------------------------------|
| `ReviewCaseStatus`| `OPEN`, `IN_REVIEW`, `RESOLVED`, `CLOSED_WITH_NOTE` | Workflow eines Prüffalls   |
| `ReviewSeverity`  | `INFO`, `WARN`, `CRITICAL`                   | Schweregrad eines Prüffalls       |
| `CardStatus`      | `ACTIVE`, `INACTIVE`, `REPLACED`, `LOST`     | Status einer RFID-Karte           |
| `UserRole`        | `EMPLOYEE`, `ADMIN`, `REVIEWER`, `TECH`      | Berechtigungsstufe                |
| `BookingSource`   | `TERMINAL`, `MANUAL`, `IMPORT`               | Herkunft einer Zeitbuchung        |
| `ChangeOrigin`    | `SYSTEM_SEED`, `ADMIN_UI`, `MIGRATION`       | Herkunft einer Systemänderung     |
| `ApprovalStatus`  | `PENDING`, `APPROVED`, `REJECTED`            | Genehmigungsstatus eines Nachtrags|
| `ScopeType`       | `GLOBAL`, `EMPLOYEE`                         | Geltungsbereich einer Regelarbeitszeit |

---

## Entitäten

**Datei:** `src/arbeitszeit/domain/entities.py`

Alle Entitäten sind als `@dataclass(frozen=True)` definiert. Das bedeutet: Einmal
erzeugte Entitätsobjekte sind unveränderlich (immutable). Zustandsänderungen werden
nicht durch Mutation, sondern durch neue Datenbankoperationen über die Repositories
ausgedrückt. Jede Entität validiert ihre Geschäftsregeln in `__post_init__`.

### `Employee` – Mitarbeiter

Repräsentiert einen Mitarbeiter der Praxis.

| Feld            | Typ          | Pflicht | Beschreibung                        |
|-----------------|--------------|---------|-------------------------------------|
| `id`            | `EmployeeId` | ja      | Datenbankschlüssel                  |
| `personnel_no`  | `str`        | ja      | Personalnummer (darf nicht leer sein) |
| `first_name`    | `str`        | ja      | Vorname                             |
| `last_name`     | `str`        | ja      | Nachname                            |
| `is_active`     | `bool`       | ja      | Aktiv-Status; inaktive Mitarbeiter dürfen nicht buchen |

**Invariante:** `personnel_no` darf nicht leer oder nur Leerzeichen sein.

---

### `UserAccount` – Benutzerkonto

Repräsentiert ein Anmeldekonto (z. B. für Admins oder Reviewer). Ein Benutzerkonto
kann optional mit einem Mitarbeiter verknüpft sein.

| Feld          | Typ                   | Beschreibung                              |
|---------------|-----------------------|-------------------------------------------|
| `id`          | `UserAccountId`       | Datenbankschlüssel                        |
| `employee_id` | `EmployeeId \| None`  | Optionaler Mitarbeiterbezug               |
| `username`    | `str`                 | Anmeldename (darf nicht leer sein)        |
| `role`        | `UserRole`            | Berechtigungsstufe                        |
| `is_active`   | `bool`                | Ob das Konto aktiv ist                    |

---

### `RfidCard` – RFID-Karte

Repräsentiert eine physische RFID-Karte, die einem Mitarbeiter zugeordnet ist.

| Feld                  | Typ                  | Beschreibung                                        |
|-----------------------|----------------------|-----------------------------------------------------|
| `id`                  | `RfidCardId`         | Datenbankschlüssel                                  |
| `employee_id`         | `EmployeeId`         | Zugehöriger Mitarbeiter                             |
| `uid_hash`            | `str`                | SHA-256-Hash der RFID-UID (nie die Roh-UID)         |
| `status`              | `CardStatus`         | Aktueller Kartenstatus                              |
| `valid_from`          | `date`               | Gültigkeitsbeginn                                   |
| `valid_until`         | `date \| None`       | Gültigkeitsende (None = unbefristet)                |
| `replaced_by_card_id` | `RfidCardId \| None` | Nachfolgekarte bei Ersatz                           |

**Invariante:** `valid_until` darf nicht vor `valid_from` liegen.

---

### `TimeBooking` – Zeitbuchung

Das zentrale Kernobjekt des Systems. Jede Stempelung (Kommen, Gehen, Pause) erzeugt
eine `TimeBooking`-Instanz.

| Feld              | Typ                     | Beschreibung                                  |
|-------------------|-------------------------|-----------------------------------------------|
| `id`              | `TimeBookingId`         | Datenbankschlüssel                            |
| `employee_id`     | `EmployeeId`            | Buchender Mitarbeiter                         |
| `booking_type`    | `BookingType`           | Art der Buchung (COME/GO/BREAK_START/BREAK_END)|
| `booked_at`       | `datetime`              | Zeitstempel der Buchung                       |
| `source`          | `BookingSource`         | Herkunft (Terminal, Manuell, Import)          |
| `status`          | `BookingStatus`         | Aktueller Prüfstatus                          |
| `terminal_id`     | `TerminalId \| None`    | Terminal, das die Buchung erzeugt hat         |
| `rfid_card_id`    | `RfidCardId \| None`    | Verwendete RFID-Karte                         |
| `device_event_id` | `DeviceEventId \| None` | Zugehöriges Geräteereignis                    |
| `note`            | `str \| None`           | Optionale Freitextnotiz                       |

---

### `WorkScheduleVersion` – Regelarbeitszeit

Speichert die Soll-Arbeitszeiten, die entweder global für alle Mitarbeiter oder
individuell pro Mitarbeiter für einen bestimmten Wochentag und Zeitraum gelten.

| Feld                  | Typ                        | Beschreibung                                    |
|-----------------------|----------------------------|-------------------------------------------------|
| `scope_type`          | `ScopeType`                | `GLOBAL` oder `EMPLOYEE`                        |
| `scope_employee_id`   | `EmployeeId \| None`       | Nur bei `EMPLOYEE`-Scope gesetzt                |
| `weekday`             | `int`                      | ISO-Wochentag: 1=Montag … 7=Sonntag             |
| `start_time`          | `time`                     | Beginn der Regelarbeitszeit                     |
| `end_time`            | `time`                     | Ende der Regelarbeitszeit                       |
| `valid_from`          | `date`                     | Gültigkeitsbeginn dieser Version                |
| `valid_until`         | `date \| None`             | Gültigkeitsende (None = aktuell gültig)         |
| `change_origin`       | `ChangeOrigin`             | Wer/was die Änderung ausgelöst hat              |
| `changed_by_user_id`  | `UserAccountId \| None`    | Ausführendes Benutzerkonto                      |

**Invarianten:** `start_time` muss vor `end_time` liegen; `scope_type` und
`scope_employee_id` müssen konsistent sein; `weekday` muss 1–7 (ISO) betragen.

---

### `ReviewCase` – Prüffall

Repräsentiert einen fachlichen Auffälligkeitsbefund, der durch automatische
Compliance-Checks oder manuelle Auslösung entsteht und einen Bearbeitungsworkflow
durchläuft.

| Feld                 | Typ                      | Beschreibung                                  |
|----------------------|--------------------------|-----------------------------------------------|
| `case_type`          | `ReviewCaseType`         | Art der Auffälligkeit                         |
| `severity`           | `ReviewSeverity`         | Schweregrad: INFO / WARN / CRITICAL           |
| `status`             | `ReviewCaseStatus`       | Workflow-Status (OPEN → IN_REVIEW → RESOLVED) |
| `booking_id`         | `TimeBookingId \| None`  | Betroffene Zeitbuchung (sofern zuordenbar)    |
| `closed_at`          | `datetime \| None`       | Zeitpunkt des Abschlusses                     |
| `closed_by_user_id`  | `UserAccountId \| None`  | Benutzer, der den Fall abgeschlossen hat      |
| `note`               | `str \| None`            | Pflicht bei `CLOSED_WITH_NOTE`                |

**Invariante:** Offene Fälle (`OPEN`, `IN_REVIEW`) dürfen keine Schließungsdaten
haben; abgeschlossene Fälle (`RESOLVED`, `CLOSED_WITH_NOTE`) müssen sie haben.
`CLOSED_WITH_NOTE` erfordert zusätzlich eine nicht-leere Begründung.

---

### `Supplement` – Nachtrag

Repräsentiert eine nachträglich erfasste Zeitbuchung (z. B. vergessene Stempelung),
die durch einen Administrator genehmigt oder abgelehnt werden muss.

Der Workflow verläuft immer in einer Richtung:

```text
PENDING  →  APPROVED
         →  REJECTED
```

**Invarianten:** Je nach `approval_status` müssen die entsprechenden Felder
(`approved_by_user_id`, `approved_at`, `rejected_by_user_id`, `rejected_at`)
gesetzt bzw. leer sein. `approved_at` und `rejected_at` dürfen nicht vor
`recorded_at` liegen.

---

### `BookingCorrection` – Buchungskorrektur

Speichert den vollständigen Vorher-/Nachher-Vergleich einer Buchungskorrektur
als unveränderlichen Audit-Trail.

| Feld                   | Typ              | Beschreibung                                    |
|------------------------|------------------|-------------------------------------------------|
| `original_booking_id`  | `TimeBookingId`  | Die korrigierte Originalbuchung                 |
| `corrected_by_user_id` | `UserAccountId`  | Ausführendes Benutzerkonto                      |
| `reason`               | `str`            | Begründung der Korrektur (Pflicht)              |
| `old_booking_type`     | `BookingType`    | Ursprünglicher Buchungstyp                      |
| `old_booked_at`        | `datetime`       | Ursprünglicher Zeitstempel                      |
| `new_booking_type`     | `BookingType`    | Neuer Buchungstyp                               |
| `new_booked_at`        | `datetime`       | Neuer Zeitstempel                               |

**Invariante:** `created_at` darf nicht vor `old_booked_at` liegen.

---

### `AuditLogEntry` – Audit-Log-Eintrag

Repräsentiert einen unveränderlichen Protokolleintrag für revisionssichere
Nachvollziehbarkeit aller systemrelevanten Ereignisse.

| Feld           | Typ                   | Beschreibung                                         |
|----------------|-----------------------|------------------------------------------------------|
| `event_type`   | `str`                 | Konstantenname aus `audit_events.py`                 |
| `object_type`  | `str`                 | Tabellenname (snake_case) oder Systembezeichner      |
| `object_id`    | `int`                 | Polymorph: Row-ID aus der betroffenen Tabelle        |
| `user_id`      | `UserAccountId \| None` | Auslösendes Benutzerkonto (ggf. kein Konto)        |
| `employee_id`  | `EmployeeId \| None`  | Betroffener Mitarbeiter (ggf. nicht personenbezogen) |
| `details_json` | `str`                 | Kontextdaten als JSON-String                         |

---

## Domänenfehler

**Datei:** `src/arbeitszeit/domain/errors.py`

Alle Fehler, die bei Verletzung fachlicher Regeln ausgelöst werden, erben von
`DomainError`. Jeder Fehlertyp trägt einen maschinenlesbaren `code`-String,
der in Logs und der Benutzeroberfläche ausgewertet werden kann.

| Fehlerklasse                  | Code                      | Auslöser                                              |
|-------------------------------|---------------------------|-------------------------------------------------------|
| `DomainError`                 | `DOMAIN_ERROR`            | Basisklasse; direkt oder abgeleitet                   |
| `UnknownCardError`            | `UNKNOWN_CARD`            | Gescannte RFID-Karte ist im System unbekannt          |
| `InactiveCardError`           | `INACTIVE_CARD`           | Gescannte RFID-Karte ist deaktiviert                  |
| `InactiveEmployeeError`       | `INACTIVE_EMPLOYEE`       | Mitarbeiter ist deaktiviert                           |
| `InvalidBookingSequenceError` | `INVALID_BOOKING_SEQUENCE`| Buchungsfolge verletzt Sequenzregeln                  |
| `OpenPhaseConflictError`      | `OPEN_PHASE_CONFLICT`     | Konflikt mit einer offenen Arbeits- oder Pausenphase  |
| `PermissionDeniedError`       | `PERMISSION_DENIED`       | Fehlende Berechtigung für die Aktion                  |
| `ValidationError`             | `VALIDATION_ERROR`        | Fachliche Validierung schlug fehl                     |
| `NotFoundError`               | `NOT_FOUND`               | Gesuchtes Objekt existiert nicht                      |
| `ConflictError`               | `CONFLICT`                | Datenbankkonflikt (z. B. doppelte Buchung)            |

Alle Fehlerklassen akzeptieren einen optionalen `message`-String sowie beliebige
Schlüsselwort-Argumente als `context`-Dictionary für strukturierte Fehlerdiagnose.

---

## Repository-Protokolle (Ports)

**Datei:** `src/arbeitszeit/domain/ports/repositories.py`

Das Domain-Modell kennt keine konkrete Datenbank. Stattdessen definiert es
**Protokolle** (Python `typing.Protocol`) für jeden Repository-Typ. Die SQLite-
Implementierungen in der Infrastrukturschicht müssen diese Protokolle erfüllen,
ohne dass das Domain-Modell sie importiert – klassische Dependency Inversion.

| Protokoll                   | Zuständigkeit                                         |
|-----------------------------|-------------------------------------------------------|
| `EmployeeRepository`        | Mitarbeiter lesen                                     |
| `UserAccountRepository`     | Benutzerkonten lesen                                  |
| `RfidCardRepository`        | RFID-Karten lesen (inkl. UID-Hash-Lookup)             |
| `TimeBookingRepository`     | Buchungen schreiben, lesen, Status setzen             |
| `WorkScheduleRepository`    | Regelarbeitszeiten verwalten (Versionen, Gültigkeit)  |
| `ReviewCaseRepository`      | Prüffälle anlegen und abschließen                     |
| `SupplementRepository`      | Nachträge verwalten (PENDING → APPROVED/REJECTED)     |
| `BookingCorrectionRepository`| Korrekturen anlegen und lesen                        |
| `AuditLogRepository`        | Audit-Einträge persistent schreiben                   |
| `DeviceEventRepository`     | Geräteereignisse (RFID-Scans) protokollieren          |
| `SystemConfigRepository`    | Systemkonfiguration lesen und schreiben               |

> **Wichtiger Sonderfall – `AuditLogRepository`:** Die Implementierung muss
> Audit-Einträge **auch dann persistent speichern**, wenn die übergeordnete
> Transaktion (UnitOfWork) zurückgerollt wird. Grund: Abweisungen von
> unbekannten oder inaktiven Karten sind auditpflichtig und dürfen nicht
> zusammen mit dem fehlgeschlagenen Buchungsvorgang verloren gehen. In der
> SQLite-Implementierung wird dafür eine separate `autocommit`-Verbindung
> verwendet.

### Besonderheit `WorkScheduleRepository.list_versions`

```text
scope_employee_id=None  → ausschließlich GLOBAL-Versionen
scope_employee_id=<id>  → ausschließlich EMPLOYEE-Versionen für diesen MA
Niemals beide Scopes gemischt.
Rückgabe aufsteigend nach valid_from sortiert.
```

### Besonderheit `TimeBookingRepository.list_for_employee_on_day`

Die Rückgabe muss **aufsteigend nach `booked_at`** sortiert sein, da alle
nachgelagerten Compliance-Prüfungen eine chronologische Reihenfolge voraussetzen.

---

## Domain Services

### Buchungssequenz-Validierung

**Datei:** `src/arbeitszeit/domain/services/booking_rules.py`

Die Funktion `validate_booking_sequence(booking_type, day_bookings)` stellt sicher,
dass eine neue Buchung zur bisherigen Tagesfolge passt. Sie wirft einen `DomainError`,
wenn die Sequenz verletzt wird. Die Funktion arbeitet zustandslos auf den übergebenen
Listen – kein Datenbankzugriff.

**Erlaubte Übergänge:**

| Neuer Typ      | Bedingung für Zulässigkeit                                         |
|----------------|--------------------------------------------------------------------|
| `COME`         | Keine offene Arbeitsphase, keine offene Pause                      |
| `GO`           | Offene Arbeitsphase vorhanden; keine offene Pause                  |
| `BREAK_START`  | Offene Arbeitsphase vorhanden; keine offene Pause                  |
| `BREAK_END`    | Offene Pause vorhanden                                             |

**Erster Eintrag des Tages** darf ausschließlich `COME` sein; `GO`, `BREAK_START`
und `BREAK_END` als erste Buchung des Tages sind immer ungültig.

**Fehler-Mapping:**

| Situation                            | Geworfener Fehler              |
|--------------------------------------|-------------------------------|
| GO/BREAK_START/BREAK_END als Erstbuchung | `InvalidBookingSequenceError` |
| COME bei offener Arbeitsphase        | `InvalidBookingSequenceError` |
| COME bei offener Pause               | `InvalidBookingSequenceError` |
| GO ohne offene Arbeitsphase          | `InvalidBookingSequenceError` |
| GO bei offener Pause                 | `OpenPhaseConflictError`      |
| BREAK_START ohne offene Arbeitsphase | `InvalidBookingSequenceError` |
| BREAK_START bei offener Pause        | `InvalidBookingSequenceError` |
| BREAK_END ohne offene Pause          | `InvalidBookingSequenceError` |

---

### ArbZG-Compliance-Prüfungen

**Datei:** `src/arbeitszeit/domain/services/compliance_checks.py`

Drei zustandslose Prüffunktionen erzeugen `ComplianceFlag`-Objekte, wenn
arbeitszeitrechtliche Schwellwerte überschritten werden. Jedes Flag enthält
einen `ReviewCaseType` und einen `ReviewSeverity`-Wert.

> **Hinweis:** Die Prüfungen arbeiten auf der **Netto-Arbeitszeit** (Gesamtdauer
> der Arbeitsphasen abzüglich aller erfassten Pausen). Sie ersetzen keine
> rechtsverbindliche Einzelfallbewertung, sondern dienen als fachliche Prüfhilfe.

#### `check_break_compliance(day_bookings)` – §4 ArbZG

| Bedingung                                              | Schweregrad  |
|--------------------------------------------------------|-------------|
| Ununterbrochener Arbeitsblock > 6 Stunden              | `WARN`      |
| Netto > 9h mit weniger als 45 min Gesamtpause          | `CRITICAL`  |
| Netto > 6h mit weniger als 30 min Gesamtpause          | `WARN`      |

#### `check_max_hours(day_bookings)` – §3 ArbZG

| Bedingung                          | Schweregrad  |
|------------------------------------|-------------|
| Netto-Arbeitszeit > 10 Stunden     | `CRITICAL`  |
| Netto-Arbeitszeit > 8 Stunden      | `WARN`      |

#### `check_rest_period(last_go, next_come)` – §5 ArbZG

| Bedingung                                  | Schweregrad  |
|--------------------------------------------|-------------|
| Ruhezeit zwischen GO und nächstem COME < 11h | `CRITICAL` |

---

## Audit-Event-Katalog

**Datei:** `src/arbeitszeit/domain/audit_events.py`

Um Tippfehler in Audit-Log-Einträgen zu verhindern, sind alle `event_type`-Strings
zentral als Modulkonstanten definiert. Kein Use Case oder Infrastrukturkomponente darf
freie String-Literale für `event_type` verwenden.

| Konstante                        | Ereignis                                      |
|----------------------------------|-----------------------------------------------|
| `TIME_BOOKED`                    | Zeitbuchung erfolgreich gespeichert           |
| `BOOKING_REJECTED_UNKNOWN_CARD`  | Buchung abgewiesen – Karte unbekannt          |
| `BOOKING_REJECTED_INACTIVE_CARD` | Buchung abgewiesen – Karte inaktiv            |
| `BOOKING_CORRECTED`              | Buchung nachträglich korrigiert               |
| `SUPPLEMENT_CREATED`             | Nachtrag erfasst                              |
| `SUPPLEMENT_APPROVED`            | Nachtrag genehmigt                            |
| `SUPPLEMENT_REJECTED`            | Nachtrag abgelehnt                            |
| `WORK_SCHEDULE_CHANGED`          | Regelarbeitszeit geändert                     |
| `EMPLOYEE_CREATED`               | Mitarbeiter angelegt                          |
| `EMPLOYEE_DEACTIVATED`           | Mitarbeiter deaktiviert                       |
| `CARD_ASSIGNED`                  | RFID-Karte einem Mitarbeiter zugewiesen       |
| `CARD_REPLACED`                  | RFID-Karte ersetzt (alte Karte auf REPLACED)  |
| `CARD_DEACTIVATED`               | RFID-Karte deaktiviert                        |
| `USER_ACCOUNT_CREATED`           | Benutzerkonto angelegt                        |
| `USER_ACCOUNT_DEACTIVATED`       | Benutzerkonto deaktiviert                     |
| `USER_ACCOUNT_REACTIVATED`       | Benutzerkonto reaktiviert                     |
| `USER_ACCOUNT_ROLE_CHANGED`      | Rolle eines Benutzerkontos geändert           |
| `BACKUP_CREATED`                 | Datenbank-Backup erstellt                     |
| `BACKUP_SYNCED_TO_NAS`           | Backup erfolgreich auf NAS übertragen         |
| `BACKUP_SYNC_FAILED`             | Backup-Übertragung auf NAS fehlgeschlagen     |
| `RESTORE_COMPLETED`              | Datenbank-Wiederherstellung abgeschlossen     |

---

## Zusammenspiel der Domain-Schicht

Das folgende Ablaufdiagramm zeigt, wie ein typischer RFID-Buchungsvorgang die
Domain-Schicht durchläuft:

```text
[RFID-Scan am Terminal]
        │
        ▼
  RfidCardRepository.get_active_by_uid_hash()
        │
   ┌────┴────┐
   │ Karte   │ nein → UnknownCardError / InactiveCardError
   │ bekannt?│        → AuditLogRepository.add() (autocommit!)
   │ aktiv?  │
   └────┬────┘
        │ ja
        ▼
  EmployeeRepository.get_by_id()
        │
  InactiveEmployeeError? → Fehler
        │
        ▼
  TimeBookingRepository.list_for_employee_on_day()
        │
        ▼
  validate_booking_sequence()   ← booking_rules.py
        │
  Fehler? → InvalidBookingSequenceError / OpenPhaseConflictError
        │
        ▼
  TimeBookingRepository.add()
        │
        ▼
  check_break_compliance()      ← compliance_checks.py
  check_max_hours()
        │
  Flags? → ReviewCaseRepository.add()
        │
        ▼
  AuditLogRepository.add(TIME_BOOKED)
```

Jede Schicht kommuniziert ausschließlich über die in `ports/repositories.py`
definierten Protokolle. Die Domain kennt weder SQLite noch RFID-Hardware.
