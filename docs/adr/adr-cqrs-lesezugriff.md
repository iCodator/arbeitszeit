# ADR-002: Direkte Infra-Zugriffe bei Leseopierationen in der Admin-CLI

**Status:** Akzeptiert  
**Datum:** 2026-06-30  
**Betroffene Schichten:** `presentation/admin_cli/` → `infrastructure/`

---

## Kontext

Das Projekt folgt einer 4-Schichten-Architektur:

```
presentation/ → application/ → domain/ ← infrastructure/
```

Schreibende Operationen laufen ausnahmslos über Use Cases in `application/use_cases/`:

| Admin-CLI-Modul | Use Case |
|---|---|
| `bookings.py` | `CorrectBookingUseCase`, `RegisterSupplementUseCase`, `ApproveSupplementUseCase`, `RejectSupplementUseCase` |
| `schedule.py` | `ManageWorkScheduleUseCase` |

Für **lesende Operationen** wurde bei der Implementierung eine Entscheidung getroffen,
die bisher nicht explizit dokumentiert war. Sie betrifft drei Bereiche:

### 1. `reports.py` — Berichte und Exporte

`reports.py` importiert direkt aus `infrastructure/export/`:

```python
from arbeitszeit.infrastructure.export import csv_exporter, pdf_report_service
from arbeitszeit.infrastructure.export.report_queries import (
    list_open_bookings, list_open_bookings_in_period,
    list_corrections, list_supplements, list_warn_bookings,
    list_open_review_cases, list_open_review_cases_in_period,
    BookingRow, CorrectionRow, ReviewCaseRow, SupplementRow,
)
```

`report_queries.py` enthält ca. 10 komplexe SQL-Queries mit JOINs über mehrere Tabellen
(time_bookings, employees, review_cases, supplements, booking_corrections).
Diese Queries sind reine Lesevorgänge ohne Zustandsänderung.

### 2. `employees.py` — Mitarbeiter- und Kartenverwaltung

`employees.py` führt direkte `conn.execute()`-Aufrufe durch — sowohl für
Lesezugriffe (z.B. `SELECT id, active FROM employees`) als auch für die wenigen
Schreiboperationen (Mitarbeiter anlegen, Karte deaktivieren), die mangels
entsprechendem Use Case ebenfalls direkt per SQL implementiert sind.

### 3. `schedule.py` — Arbeitszeitmodell-Anzeige

Liest Arbeitszeitversionen direkt per `conn.execute()` für die Listendarstellung;
die Schreiboperation delegiert an `ManageWorkScheduleUseCase`.

---

## Entscheidung

**Lesende Operationen in der Admin-CLI greifen direkt auf `infrastructure/` zu.**
Eine zwischengeschaltete `application/queries.py`-Schicht wird bewusst nicht eingeführt.

Die Architekturgrenze gilt weiterhin für alle **schreibenden** Operationen:
jede Zustandsänderung läuft über einen Use Case.

---

## Begründung

### Warum kein `application/queries.py`?

**1. Keine Fachlogik in Lesezugriffen**

`report_queries.py` enthält ausschließlich SQL mit Formatierungslogik für die Ausgabe.
Es gibt keine Domänenregeln, Validierungen oder Invarianten, die schützenswert wären.
Ein Query-DTO in `application/queries.py` würde die SQL-Abfrage nur umbenennen,
nicht verbessern.

**2. Lesezugriffe haben keine Seiteneffekte**

Use Cases existieren, um **Invarianten zu schützen** (z.B. keine Doppelbuchung,
Rollenprüfung vor Nachtrag). Bei Lesezugriffen gibt es nichts zu schützen —
ein fehlerhafter Report verändert keine Daten.

**3. Praktische Kohärenz mit CQRS-Prinzip**

Command Query Responsibility Segregation (CQRS) trennt explizit zwischen
Commands (schreiben, Use Cases) und Queries (lesen, direkter Datenzugriff).
Der Ist-Zustand entspricht exakt diesem Muster — nur ohne den Namen.

**4. Aufwand vs. Nutzen**

`report_queries.py` enthält ~10 Funktionen mit jeweils 15–40 Zeilen SQL.
Diese in `application/queries.py` zu wrappen würde ~10 Passthrough-Funktionen
erzeugen, die ausschließlich delegieren. Das ist Boilerplate ohne Mehrwert.

### Bekannte Abweichung: `employees.py` mit direktem SQL für Schreiboperationen

`employees.py` enthält auch schreibende Operationen (Mitarbeiter anlegen,
Karte deaktivieren) direkt per SQL — ohne Use Case. Das ist eine **separate**
Abweichung von der Architektur, nicht Teil dieser ADR.

**Begründung:** Diese Operationen enthalten keine komplexe Fachlogik oder
Domäneninvarianten, die einen Use Case rechtfertigen würden. Sie sind
administrative CRUD-Operationen mit direkter Rollenprüfung.
Sollte in Zukunft Fachlogik (z.B. Kartenhistorie-Validierung) hinzukommen,
ist ein Use Case nachzurüsten.

---

## Konsequenzen

### Für Entwickler

- `application/use_cases/` enthält **ausschließlich** schreibende Use Cases.
  Das ist kein Versehen — Lesezugriffe gehören bewusst nicht dorthin.
- `infrastructure/export/report_queries.py` ist der kanonische Ort für
  Berichtsabfragen. Neue Report-Queries gehören dorthin, nicht in `application/`.
- Direkte `conn.execute()`-Aufrufe in `admin_cli/` sind für Lesezugriffe erlaubt.
  Für schreibende Operationen mit Domänenlogik ist ein Use Case zu verwenden.

### Für Code-Reviews

Import von `arbeitszeit.infrastructure.*` in `presentation/admin_cli/` ist
für Lesezugriffe akzeptiert. Ein Linter-Kommentar `# noqa: Architecture` ist
**nicht** notwendig — der Direktzugriff ist kein Verstoß, sondern Absicht.

### Grenzfall: `employees.py` Schreiboperationen

Die direkten Schreibzugriffe in `employees.py` sind pragmatisch akzeptiert
solange sie:
- keine Domäneninvarianten verletzen können,
- eine explizite Rollenprüfung (`_require_admin`) enthalten,
- einen Audit-Log-Eintrag schreiben.

---

## Verworfene Alternativen

### A: `application/queries.py` mit Query-DTOs

```python
# application/queries.py (verworfen)
@dataclass(frozen=True)
class ListOpenBookingsQuery:
    employee_id: int | None
    from_dt: datetime | None
    to_dt: datetime | None

def list_open_bookings(uow: UnitOfWork, query: ListOpenBookingsQuery) -> list[BookingRow]:
    return report_queries.list_open_bookings(uow._conn, ...)  # Passthrough
```

**Verworfen:** Reine Delegation ohne eigene Logik. Erhöht Komplexität und
Zeilenzahl ohne Mehrwert. Versteckt außerdem, dass `report_queries.py`
direkte SQL-Verbindungen braucht, die das UnitOfWork-Protokoll nicht
bereitstellt.

### B: Repository-Methoden für alle Lesezugriffe

Alle Queries als Methoden in die bestehenden Repository-Protokolle
(`TimeBookingRepository`, `SupplementRepository` etc.) aufnehmen.

**Verworfen:** Report-Queries joinen typischerweise 3–5 Tabellen und
überschreiten die sinnvolle Verantwortung eines einzelnen Repositories.
Ein `TimeBookingRepository.list_open_bookings_with_employee_name()` wäre
eine unnatürliche Erweiterung des Repository-Protokolls.

---

## Referenzen

- `src/arbeitszeit/infrastructure/export/report_queries.py` — alle Lesezugriffe
- `src/arbeitszeit/presentation/admin_cli/reports.py` — Verwendung in Reports
- `src/arbeitszeit/presentation/admin_cli/employees.py` — direkte SQL-Zugriffe
- `src/arbeitszeit/presentation/admin_cli/schedule.py` — gemischtes Muster
- Pflichtenheft v5 §7.12 — Pflichtauswertungen
