# Kapitel 4: Die Anwendungsschicht (`application`)

> **Quelle:** `src/arbeitszeit/application/` im Repository `iCodator/arbeitszeit`

Die Anwendungsschicht ist das Herzstück der fachlichen Steuerung. Sie vermittelt
zwischen der Präsentationsschicht (UI, Terminal-Handler) und der Domänenschicht
(Geschäftsregeln, Entitäten). Sie enthält **keine** SQL-Logik, **keine**
Hardware-Zugriffe und **keine** UI-Elemente — ausschließlich Ablaufsteuerung,
Validierung und Koordination.

---

## 4.1 Überblick und Einordnung

Das Paket folgt dem **CQRS-Prinzip** (Command Query Responsibility Segregation):
Schreibende Operationen werden über *Commands* und *Use Cases* gesteuert,
lesende Operationen über *Query-DTOs*. Beide Seiten sind strikt getrennt,
sodass sie unabhängig voneinander weiterentwickelt und getestet werden können.

```
src/arbeitszeit/application/
├── __init__.py            # leer — kein impliziter Re-Export
├── commands.py            # Eingabe-DTOs für alle schreibenden Operationen
├── queries.py             # Ausgabe-DTOs für lesende Abfragen (CQRS-Read)
├── results.py             # Ausgabe-DTOs für schreibende Operationen
├── unit_of_work.py        # Transaktion-Protokoll (Protocol-Klasse)
└── use_cases/
    ├── __init__.py
    ├── book_time.py           # Buchung via RFID-Terminal
    ├── correct_booking.py     # Manuelle Korrektur durch Admin/Reviewer
    ├── register_supplement.py # Nachtrag erfassen (Status: PENDING)
    ├── approve_supplement.py  # Nachtrag freigeben → erzeugt Buchung
    ├── reject_supplement.py   # Nachtrag ablehnen
    └── manage_work_schedule.py # Regelarbeitszeit ändern
```

---

## 4.2 Commands — Eingabe-DTOs (`commands.py`)

Commands sind **unveränderliche Datenbehälter** (`frozen=True, slots=True`),
die alle für eine Operation notwendigen Parameter bündeln. Sie enthalten keine
Logik. Die Use Cases konsumieren Commands als einzigen Eingabeparameter.

| Command-Klasse | Zweck |
|---|---|
| `BookCommand` | RFID-Buchung vom Terminal (Kommen/Gehen/Pause) |
| `CreateSupplementCommand` | Nachtrag durch Admin/Reviewer erfassen |
| `CreateCorrectionCommand` | Bestehende Buchung korrigieren |
| `ApproveSupplementCommand` | Nachtrag genehmigen |
| `RejectSupplementCommand` | Nachtrag ablehnen (mit Begründung) |
| `ChangeWorkScheduleCommand` | Regelarbeitszeit für Wochentag/Scope setzen |

Alle Commands importieren ihre Value-Object-Typen (z. B. `EmployeeId`,
`TerminalId`) aus `arbeitszeit.domain.value_objects`, um Typsicherheit
ohne Primitive Obsession zu gewährleisten.

---

## 4.3 Results — Ausgabe-DTOs schreibender Operationen (`results.py`)

Jeder Use Case gibt ein typisiertes Result-Objekt zurück. Results sind ebenfalls
`frozen` und `slots`-optimiert. Sie enthalten nur die IDs und Status-Werte, die
die Präsentationsschicht für Rückmeldungen oder Folgeverarbeitungen benötigt.

| Result-Klasse | Enthaltene Felder |
|---|---|
| `BookResult` | `booking_id`, `status`, `follow_up_case_ids` |
| `SupplementResult` | `supplement_id`, `review_case_id` |
| `CorrectionResult` | `correction_id`, `updated_booking_id`, `review_case_id` |
| `WorkScheduleChangeResult` | `new_version_id`, `superseded_version_id` |
| `ApproveSupplementResult` | `supplement_id`, `booking_id`, `booking_status`, `follow_up_case_ids` |
| `RejectSupplementResult` | `supplement_id`, `review_case_id` |

---

## 4.4 Queries — Lesende Abfrage-DTOs (`queries.py`)

Die Query-DTOs bilden die CQRS-Leseseite ab. Sie definieren die Zeilenstruktur
für Berichte und Listen, ohne selbst SQL auszuführen. Die eigentlichen
Datenbankabfragen liegen in der Infrastrukturschicht
(`infrastructure/export/report_queries.py`).

| Row-Klasse | Verwendungszweck |
|---|---|
| `BookingRow` | Buchungsliste mit Mitarbeiterzuordnung für Berichte |
| `CorrectionRow` | Korrekturprotokoll mit altem und neuem Zustand (Regelwerk v3 §12) |
| `SupplementRow` | Nachtragsliste mit Freigabestatus (Regelwerk v3 §13/§19) |
| `ReviewCaseRow` | Offene Prüffälle (Pflichtenheft v3 §7.6/§7.12) |

Die Trennung von Command- und Query-Typen stellt sicher, dass
Präsentationsmodule **keine** Infrastruktur-Klassen importieren müssen.

---

## 4.5 Unit of Work — Transaktionsprotokoll (`unit_of_work.py`)

`UnitOfWork` ist ein **Protocol** (strukturelles Typing, kein Erben nötig).
Es fasst alle Repository-Referenzen unter einem gemeinsamen Transaktionskontext
zusammen und garantiert atomare Schreiboperationen.

```python
with self._uow:
    # Alle Lese- und Schreiboperationen hier
    self._uow.commit()
```

Die in `UnitOfWork` definierten Repositories:

- `employee_repo` — Mitarbeiterstammdaten
- `user_account_repo` — Benutzerkonten (mit Rollen)
- `rfid_card_repo` — RFID-Karten und deren Status
- `time_booking_repo` — Zeitbuchungen (Kommen/Gehen/Pause)
- `work_schedule_repo` — Regelarbeitszeitversionen
- `review_case_repo` — Prüffälle
- `supplement_repo` — Nachträge
- `booking_correction_repo` — Buchungskorrekturen
- `audit_log_repo` — Unveränderliches Audit-Protokoll
- `system_config_repo` — Systemeinstellungen
- `device_event_repo` — Geräteereignisse (Terminal, Numpad)

> **Wichtig:** Das Audit-Log wird nach `commit()` geschrieben (nicht davor).
> Begründung: Nach dem Commit hält die Hauptverbindung keinen `RESERVED`-Lock
> mehr, sodass die Audit-Verbindung (SQLite WAL-Modus, Autocommit) ohne
> Blockierung schreiben kann.

---

## 4.6 Use Cases im Detail

### 4.6.1 `BookUseCase` — Terminalbuchung (`book_time.py`)

Dieser Use Case verarbeitet jede RFID-Buchung vom Terminal. Er ist der am
häufigsten ausgeführte Use Case im Tagesbetrieb.

**Ablauf:**

1. RFID-Karte per `uid_hash` nachschlagen
2. Bei unbekannter Karte → Audit-Eintrag `BOOKING_REJECTED_UNKNOWN_CARD` + `UnknownCardError`
3. Bei inaktiver Karte → Audit-Eintrag `BOOKING_REJECTED_INACTIVE_CARD` + `InactiveCardError`
4. Mitarbeiter laden und Aktivstatus prüfen
5. Tagesbuchungen laden, Buchungsreihenfolge validieren (`validate_booking_sequence`)
6. Regelarbeitszeit prüfen → ggf. `ComplianceFlag(OUTSIDE_SCHEDULE_WINDOW, WARN)` setzen
7. Compliance-Checks durchführen: Pausenpflicht, Höchstarbeitszeit, Ruhezeit
8. Buchung speichern mit berechnetem Status (`OK` / `WARN` / `NEEDS_REVIEW`)
9. Prüffälle für jeden `ComplianceFlag` anlegen
10. `commit()` → Audit-Log `TIME_BOOKED` schreiben
11. `BookResult` zurückgeben

**Statuslogik der Buchung:**

| Status | Bedingung |
|---|---|
| `OPEN` | Buchungstyp ist `COME` oder `BREAK_START` (Tag noch offen) |
| `OK` | Keine Compliance-Verstöße |
| `WARN` | Mindestens ein Flag ohne `CRITICAL`-Schwere |
| `NEEDS_REVIEW` | Mindestens ein Flag mit `CRITICAL`-Schwere |

**Ablehnungspfade und SQLite-Locks:**

In den Ablehnungspfaden (unbekannte/inaktive Karte) darf vor dem
Audit-Log-Schreibvorgang **keine** andere Schreiboperation auf der
Hauptverbindung stattgefunden haben. Nur SELECTs sind vor dem ersten
Audit-Write erlaubt. Diese Invariante muss bei Erweiterungen gewahrt bleiben.

---

### 4.6.2 `CorrectBookingUseCase` — Buchungskorrektur (`correct_booking.py`)

Ermöglicht berechtigten Benutzern (Rolle `ADMIN` oder `REVIEWER`), eine
bestehende Buchung nachträglich zu ändern.

**Ablauf:**

1. Berechtigungsprüfung des handelnden Benutzers
2. Originalbuchung und zugehörigen Mitarbeiter laden
3. `BookingCorrection`-Datensatz anlegen (Vorher/Nachher-Snapshot)
4. Status der Originalbuchung auf `CORRECTED` setzen
5. Offene Prüffälle des Mitarbeiters durchsuchen:
   - Prüffälle mit `booking_id == original` und korrigierbarem Typ → Status `RESOLVED`
6. `commit()` → Audit-Log `BOOKING_CORRECTED` schreiben
7. `CorrectionResult` zurückgeben

**Korrigierbare Prüffalltypen** (`_CORRECTABLE_CASE_TYPES`):
`OPEN_WORK_PHASE`, `OPEN_BREAK_PHASE`, `IMPLAUSIBLE_SEQUENCE`,
`POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`,
`POSSIBLE_MAX_HOURS_VIOLATION`, `OUTSIDE_SCHEDULE_WINDOW`.

Nicht durch Buchungskorrektur schließbar: `MANUAL_ENTRY_REVIEW`,
`UNKNOWN_CARD_ATTEMPT`, `INACTIVE_CARD_ATTEMPT`, `TIME_ANOMALY`.

---

### 4.6.3 `RegisterSupplementUseCase` — Nachtrag erfassen (`register_supplement.py`)

Erfasst eine nachträglich einzutragende Buchung (z. B. vergessenes Einstempeln).
Der Nachtrag wird zunächst im Status `PENDING` angelegt — er erzeugt noch
**keine** Buchung in `time_bookings`.

**Ablauf:**

1. Berechtigungsprüfung (`ADMIN` oder `REVIEWER`)
2. Mitarbeiter laden und Aktivstatus prüfen
3. Falls `related_booking_id` angegeben: Existenz der Originalbuchung sicherstellen
4. `Supplement`-Datensatz mit Status `PENDING` anlegen
5. Prüffall `MANUAL_ENTRY_REVIEW` (Schwere `INFO`) anlegen
6. `commit()` → Audit-Log `SUPPLEMENT_CREATED` schreiben
7. `SupplementResult` zurückgeben

---

### 4.6.4 `ApproveSupplementUseCase` — Nachtrag freigeben (`approve_supplement.py`)

Genehmigt einen ausstehenden Nachtrag und überführt ihn in eine echte
Buchung mit vollständiger Compliance-Prüfung.

**Ablauf:**

1. Berechtigungsprüfung (`ADMIN` oder `REVIEWER`)
2. Nachtrag laden, Status muss `PENDING` sein (sonst `ValidationError`)
3. Mitarbeiter laden und prüfen
4. Nachtrag in `approved` überführen (`supplement_repo.approve`)
5. Zugehörigen Prüffall `MANUAL_ENTRY_REVIEW` auf `RESOLVED` schließen
6. Buchungsreihenfolge validieren (wie bei Terminal-Buchung)
7. Regelarbeitszeit und Compliance-Checks durchführen
8. Neue `TimeBooking` mit Source `MANUAL` anlegen
9. Folge-Prüffälle aus Compliance-Flags anlegen
10. `commit()` → Audit-Log `SUPPLEMENT_APPROVED` schreiben
11. `ApproveSupplementResult` zurückgeben

---

### 4.6.5 `RejectSupplementUseCase` — Nachtrag ablehnen (`reject_supplement.py`)

Lehnt einen ausstehenden Nachtrag ab, ohne eine Buchung zu erzeugen.

**Ablauf:**

1. Berechtigungsprüfung (`ADMIN` oder `REVIEWER`)
2. Nachtrag laden, Status muss `PENDING` sein
3. Nachtrag auf `rejected` setzen (`supplement_repo.reject`)
4. Ggf. zugehörigen Prüffall `MANUAL_ENTRY_REVIEW` mit Status
   `CLOSED_WITH_NOTE` und der Ablehnungsbegründung schließen
5. `commit()` → Audit-Log `SUPPLEMENT_REJECTED` schreiben
6. `RejectSupplementResult` zurückgeben

---

### 4.6.6 `ManageWorkScheduleUseCase` — Regelarbeitszeit (`manage_work_schedule.py`)

Ändert die Regelarbeitszeit für einen Wochentag, entweder global (alle
Mitarbeiter) oder mitarbeiterspezifisch. Nur Benutzer mit Rolle `ADMIN`
dürfen diesen Use Case ausführen.

**Ablauf:**

1. Berechtigungsprüfung (`ADMIN` — strikt, kein `REVIEWER`)
2. Aktuell gültige Version für Wochentag/Scope laden
3. Konfliktprüfung: existiert bereits eine Version mit gleichem `valid_from`
   → `ConflictError`
4. Rückwärtseinfüge-Schutz: existiert eine spätere Version → `ValidationError`
5. Aktuelle Version schließen (`valid_until = valid_from - 1 Tag`)
6. Neue `WorkScheduleVersion` anlegen
7. `commit()` → Audit-Log `WORK_SCHEDULE_CHANGED` schreiben
   (enthält Vorher/Nachher-Snapshot)
8. `WorkScheduleChangeResult` zurückgeben

---

## 4.7 Querschnittliche Entwurfsprinzipien

### Berechtigungsprüfung

Alle manuellen Use Cases (Korrektur, Nachtrag, Regelzeitänderung) prüfen
zu Beginn die Benutzerrolle und werfen `PermissionDeniedError`, bevor sie
irgendwelche Datenbankzugriffe ausführen. Terminal-Buchungen (`BookUseCase`)
benötigen keine Rollenprüfung — die RFID-Karte ist das Authentifikationsmittel
des Mitarbeiters (Regelwerk v5 §16).

### Audit-Log-Konsistenz

Das Audit-Log wird in **allen** Use Cases nach dem `commit()` geschrieben.
Diese Reihenfolge ist eine bewusste Architekturentscheidung für SQLite im
WAL-Modus: Erst nach dem Commit gibt die Hauptverbindung ihren `RESERVED`-Lock
frei, sodass die Audit-Verbindung (separater Autocommit-Cursor) blockierungsfrei
schreiben kann.

### Unveränderlichkeit der DTOs

Alle Commands und Results sind `@dataclass(frozen=True, slots=True)`.
`frozen=True` verhindert versehentliche Mutation nach der Erzeugung.
`slots=True` reduziert Speicherbedarf und beschleunigt Attributzugriffe.

### Fehlertypen

| Fehlerklasse | Bedeutung |
|---|---|
| `PermissionDeniedError` | Fehlende Berechtigung der handelnden Person |
| `NotFoundError` | Entität (Mitarbeiter, Buchung, Nachtrag) nicht gefunden |
| `InactiveCardError` | RFID-Karte ist gesperrt oder deaktiviert |
| `InactiveEmployeeError` | Mitarbeiter ist nicht mehr aktiv |
| `UnknownCardError` | RFID-UID ist im System nicht registriert |
| `ValidationError` | Fachliche Verletzung (z. B. falscher Status) |
| `ConflictError` | Doppelter Eintrag (z. B. doppelte Regelzeitversion) |

---

## 4.8 Erweiterungshinweise

- **Neuer Use Case:** Neue Datei in `use_cases/`, entsprechendes Command in
  `commands.py` und Result in `results.py` ergänzen. `UnitOfWork` in
  `unit_of_work.py` nur erweitern, wenn ein neues Repository benötigt wird.
- **Neue Abfragesicht:** Neue `*Row`-Klasse in `queries.py` definieren;
  die SQL-Implementierung gehört in `infrastructure/export/report_queries.py`.
- **Compliance-Regel hinzufügen:** Neue Prüffunktion in
  `domain/services/compliance_checks.py`, dann in `_evaluate_booking()` der
  betroffenen Use Cases aufrufen.
- **Reihenfolge beim Audit-Log nie ändern:** Der Commit muss vor dem
  Audit-Log-Schreibvorgang erfolgen (SQLite-WAL-Lock-Invariante, s. o.).
