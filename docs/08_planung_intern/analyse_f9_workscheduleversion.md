# Faktenprüfung F9: `WorkScheduleVersion` — Datenmodell und Sollzeit-Abbildung

Fragestellung: Kann die Sollarbeitszeit pro Wochentag unterschiedlich hinterlegt werden,
und wie wird die für einen gegebenen Kalendertag gültige Version ermittelt?

## Geprüfte Dateien

| Datei | Betroffene Stellen |
| --- | --- |
| `src/arbeitszeit/domain/entities.py` | Zeilen 90–121 |
| `src/arbeitszeit/domain/value_objects.py` | Zeile 25 |
| `src/arbeitszeit/application/commands.py` | Zeilen 61–70 |
| `src/arbeitszeit/application/use_cases/manage_work_schedule.py` | Zeilen 27–66 |
| `src/arbeitszeit/infrastructure/db/repositories/work_schedule.py` | Zeilen 33–34, 70–94 |
| `src/arbeitszeit/application/use_cases/book_time.py` | Zeilen 101–108 |
| `src/arbeitszeit/application/use_cases/approve_supplement.py` | Zeilen 188–196 |
| `src/arbeitszeit/domain/services/compliance_checks.py` | Zeilen 1–104 |
| `src/arbeitszeit/domain/services/booking_rules.py` | Zeilen 1–91 |

---

## 1. Definition und vollständige Feldliste

**Datei:** `src/arbeitszeit/domain/entities.py`, Zeilen 90–121

```python
@dataclass(frozen=True)
class WorkScheduleVersion:
    id: WorkScheduleVersionId          # NewType("WorkScheduleVersionId", int)
    scope_type: ScopeType              # StrEnum: "GLOBAL" | "EMPLOYEE"
    scope_employee_id: EmployeeId | None
    weekday: int                       # ISO-Wochentag 1=Mo … 7=So
    start_time: time                   # datetime.time
    end_time: time                     # datetime.time
    valid_from: date                   # datetime.date
    valid_until: date | None           # datetime.date | None; None = offenes Ende
    change_origin: ChangeOrigin        # StrEnum: "SYSTEM_SEED" | "ADMIN_UI" | "MIGRATION"
    changed_by_user_id: UserAccountId | None
```

`WorkScheduleVersionId` ist `NewType("WorkScheduleVersionId", int)`
(`value_objects.py`, Zeile 25).

---

## 2. Tagesgranularität der Sollarbeitszeit

**Eine Instanz repräsentiert genau einen Wochentag.**

Das Feld `weekday: int` trägt den ISO-Wochentag (1 = Montag, 7 = Sonntag) der Entität.
Es gibt kein Dict, kein Array und keine sieben Einzelfelder innerhalb einer Instanz.

Um alle 7 Wochentage abzudecken, müssen 7 separate `WorkScheduleVersion`-Zeilen in der
Datenbank existieren — eine pro Wochentag.

Es gibt keinen aggregierten Sollstunden-Wert pro Version. Die Sollzeit des Wochentages
ergibt sich ausschließlich aus der Differenz `end_time − start_time`.

---

## 3. Einheit und Format der Sollzeit

Die Sollzeit ist **nicht als eigenes Feld** vorhanden. Sie ergibt sich als implizite
Differenz aus zwei Feldern vom Typ `datetime.time`:

| Feld | Typ | Fundstelle |
| --- | --- | --- |
| `start_time` | `datetime.time` | `entities.py:95` |
| `end_time` | `datetime.time` | `entities.py:96` |

In der Datenbank werden beide als `"HH:MM"`-String gespeichert und beim Lesen
per `_parse_time()` zurück in `datetime.time` umgewandelt
(`repositories/work_schedule.py`, Zeilen 33–34).

Es existieren keine Felder vom Typ `float` (Stunden), `int` (Minuten) oder `timedelta`.

---

## 4. Gültigkeitszeitraum und Versionsermittlung

### Modellierung

- `valid_from: date` — Beginn der Gültigkeit (inklusiv)
- `valid_until: date | None` — Ende der Gültigkeit (inklusiv); `None` = unbefristet

### Repository-Methode `get_effective`

`src/arbeitszeit/infrastructure/db/repositories/work_schedule.py`, Zeilen 70–94:

```python
def get_effective(
    self,
    weekday: int,
    on_date: date,
    employee_id: int | None = None,
) -> WorkScheduleVersion | None:
    on_date_s = on_date.isoformat()
    if employee_id is not None:
        row = self._conn.execute(
            f"{_SELECT} WHERE scope_type = 'EMPLOYEE' AND scope_employee_id = ? "
            "AND weekday = ? AND valid_from <= ? "
            "AND (valid_until IS NULL OR valid_until >= ?) "
            "ORDER BY valid_from DESC LIMIT 1",
            (employee_id, weekday, on_date_s, on_date_s),
        ).fetchone()
        if row:
            return _row_to_version(row)

    row = self._conn.execute(
        f"{_SELECT} WHERE scope_type = 'GLOBAL' AND weekday = ? "
        "AND valid_from <= ? AND (valid_until IS NULL OR valid_until >= ?) "
        "ORDER BY valid_from DESC LIMIT 1",
        (weekday, on_date_s, on_date_s),
    ).fetchone()
    return _row_to_version(row) if row else None
```

**Vorranglogik:**

1. Employee-Scope wird zuerst geprüft; bei Treffer wird Global-Scope ignoriert.
2. Innerhalb eines Scopes gewinnt die Version mit dem größten `valid_from`
   (jüngste passende Version).
3. Datumsbedingung: `valid_from <= on_date AND (valid_until IS NULL OR valid_until >= on_date)`.

---

## 5. `ChangeWorkScheduleCommand` und `ManageWorkScheduleUseCase`

### Command-Dataclass

`src/arbeitszeit/application/commands.py`, Zeilen 61–70:

```python
@dataclass(frozen=True, slots=True)
class ChangeWorkScheduleCommand:
    scope_type: ScopeType
    scope_employee_id: EmployeeId | None
    weekday: int          # ein einzelner Wochentag pro Aufruf
    start_time: time
    end_time: time
    valid_from: date
    change_origin: ChangeOrigin
    changed_by_user_id: UserAccountId | None
    reason: str | None
```

Das Command enthält kein Feld für mehrere Wochentage, keine Liste und kein Dict.

### Use-Case-Rumpf

`src/arbeitszeit/application/use_cases/manage_work_schedule.py`, Zeilen 27–66:

```python
def execute(self, cmd: ChangeWorkScheduleCommand) -> WorkScheduleChangeResult:
    with self._uow:
        self._check_permission(cmd)
        repo = self._uow.work_schedule_repo

        current = repo.get_effective(
            weekday=cmd.weekday,
            on_date=cmd.valid_from,
            employee_id=cmd.scope_employee_id,
        )
        self._validate_no_conflict(cmd, current)

        superseded_id: WorkScheduleVersionId | None = None
        if current is not None:
            repo.close_version(current.id, cmd.valid_from - timedelta(days=1))
            superseded_id = current.id

        new_version = WorkScheduleVersion(
            id=WorkScheduleVersionId(0),
            scope_type=cmd.scope_type,
            scope_employee_id=cmd.scope_employee_id,
            weekday=cmd.weekday,
            start_time=cmd.start_time,
            end_time=cmd.end_time,
            valid_from=cmd.valid_from,
            valid_until=None,
            change_origin=cmd.change_origin,
            changed_by_user_id=cmd.changed_by_user_id,
        )
        saved = repo.add(new_version)
        self._uow.commit()
        ...
```

**Befund:** Die API unterstützt ausschließlich einen Wochentag pro `execute()`-Aufruf.
Um 7 Wochentage zu konfigurieren, sind 7 separate Aufrufe erforderlich. Eine Tages-
granularität im Sinne mehrerer Wochentage in einem einzigen Aufruf existiert nicht.

Beim Anlegen einer neuen Version schließt der Use Case die bisher gültige Version
automatisch mit `valid_until = valid_from_neu − 1 Tag`.

---

## 6. Soll-Ist-Abweichungsberechnung

### `compliance_checks.py` und `booking_rules.py`

Kein Zugriff auf `WorkScheduleVersion`. Beide Dateien operieren ausschließlich auf
`TimeBooking`-Sequenzen:

- `compliance_checks.py` prüft ArbZG-Compliance (Pausen §4, Höchstarbeitszeit §3,
  Ruhezeiten §5).
- `booking_rules.py` validiert die Buchungsreihenfolge (COME/BREAK/GO-Abfolge).

Eine numerische Soll-Ist-Stunden-Berechnung existiert in keiner der beiden Dateien.

### Tatsächliche Verwendungsstellen von `WorkScheduleVersion`

**`book_time.py`, Zeilen 101–108:**

```python
schedule = self._uow.work_schedule_repo.get_effective(
    cmd.booked_at.isoweekday(), cmd.booked_at.date(), employee.id
)
if schedule is not None and not (
    schedule.start_time <= cmd.booked_at.time() <= schedule.end_time
):
    schedule_flags = [
        ComplianceFlag(ReviewCaseType.OUTSIDE_SCHEDULE_WINDOW, ReviewSeverity.WARN)
    ]
```

**`approve_supplement.py`, Zeilen 188–196:** identisches Muster für Nachträge.

**Befund:** An beiden Stellen wird keine numerische Soll-Ist-Abweichung berechnet.
Es wird ausschließlich geprüft, ob ein Buchungszeitstempel innerhalb des Sollzeitfensters
liegt (`start_time <= booked_at.time() <= end_time`). Das ist eine binäre Fensterprüfung.

Eine Funktion, die pro Kalendertag eine numerische Soll-Ist-Abweichung
(z. B. `geleistete_stunden − soll_stunden`) unter Zugriff auf `WorkScheduleVersion`
berechnet, existiert im Codebase nicht.

---

## Zusammenfassung der Kernbefunde

| Frage | Befund |
| --- | --- |
| Tagesgranularität | Eine Instanz = ein Wochentag; 7 Zeilen für alle Tage nötig |
| Sollzeit-Feld | Keines — ergibt sich als `end_time − start_time` (beide `datetime.time`) |
| Einheit | `datetime.time`, kein Float/Int/timedelta |
| Gültigkeitsmodell | `valid_from` (inkl.) / `valid_until` (inkl., `None` = offen) |
| Versionsermittlung | `get_effective(weekday, on_date, employee_id)` — Employee vor Global, jüngste zuerst |
| API-Granularität | 1 Wochentag pro `ChangeWorkScheduleCommand`-Aufruf |
| Soll-Ist-Berechnung | Nicht vorhanden; nur binäre Fensterprüfung in `book_time.py` |
