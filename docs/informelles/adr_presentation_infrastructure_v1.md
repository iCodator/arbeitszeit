# ADR-ARCH-001 – Composition Root und direkte Infrastructure-Importe in der Presentation-Schicht

**Datum:** 2026-06-30  
**Status:** Entschieden (dokumentiert)  
**Typ:** Architekturentscheidung  

---

## Kontext

Das Projekt folgt einer 4-Schicht-Architektur mit verbindlicher Import-Richtung:

```
presentation → infrastructure → application → domain
```

`presentation → infrastructure` ist damit **ausdrücklich erlaubt**. Die Frage ist
nicht, ob diese Richtung erlaubt ist, sondern welche konkreten Importe intentional
sind und welche auf verbesserungswürdige Muster hinweisen.

Auslöser für diese ADR: In `admin_cli/` und `terminal_ui/` gibt es direkte Importe
aus `infrastructure/db/`, `infrastructure/export/` und `infrastructure/hardware/`.
Ohne Dokumentation ist unklar, ob das bewusste Architektur (Composition Root) oder
schleichende Kopplung ist.

---

## Beobachteter Ist-Stand

Vollständige Liste aller Infrastructure-Importe in Presentation (Stand 2026-06-30):

| Presentation-Datei | Import | Kategorie |
| --- | --- | --- |
| `admin_cli/main.py` | `open_connection` | Composition Root ✓ |
| `admin_cli/main.py` | `run_migrations` | Infrastructure-Bootstrap ✓ |
| `admin_cli/bookings.py` | `SQLiteUnitOfWork` | Composition Root ✓ |
| `admin_cli/schedule.py` | `SQLiteUnitOfWork` | Composition Root ✓ |
| `admin_cli/reports.py` | `csv_exporter`, `pdf_report_service` | Dienst-Delegierung ✓ |
| `admin_cli/reports.py` | Query-Funktionen aus `report_queries` | SQL-Ausführung ✓ |
| `admin_cli/system.py` | `SQLiteBackupService` | Betriebsdienst ✓ |
| `admin_cli/system.py` | `run_system_check` | Betriebsdienst ✓ |
| `terminal_ui/booking_loop.py` | `open_connection`, `SQLiteUnitOfWork` | Composition Root ✓ |
| `terminal_ui/booking_loop.py` | `HardwareReader` (Port-Interface) | Hardware-Abstraktion ✓ |
| `terminal_ui/main.py` | `open_connection` | Composition Root ✓ |
| `terminal_ui/main.py` | `EvdevHardwareReader`, `HardwareReader` | Gerätetreiber-Wiring ✓ |
| `terminal_ui/main.py` | `run_system_check`, `time_monitor` | Betriebsdienste ✓ |
| `terminal_ui/main.py` | `SQLiteSystemConfigRepository` | Direktes Repository ⚠ |

---

## Entscheidung

### Intentionale Muster (werden nicht geändert)

**Composition Root**  
`presentation/admin_cli/main.py` und `terminal_ui/booking_loop.py` sind die
Einstiegspunkte des Systems. Sie öffnen DB-Verbindungen (`open_connection`),
führen Migrationen aus (`run_migrations`) und verdrahten konkrete Repository-
Implementierungen mit Use Cases (`SQLiteUnitOfWork`). Das ist der klassische
Composition-Root-Punkt — die einzige Stelle, an der Infrastructure-Abhängigkeiten
bewusst zusammengebunden werden.

**Betriebsdienste ohne Application-Wrapper**  
`SQLiteBackupService`, `run_system_check`, `SystemTimeMonitor` haben keinen
sinnvollen Use-Case-Wrapper in der Application-Schicht — sie sind Betriebsabläufe
(Backup, Systemcheck, Zeitprotokollierung), die direkt aus der CLI orchestriert
werden. Ein Application-Layer-Wrapper würde hier nur Boilerplate erzeugen.

**Query-Funktionen in Infrastructure**  
`list_bookings`, `list_corrections` usw. führen SQL aus und gehören in Infrastructure.
Die zugehörigen **Row-Typen** (`BookingRow`, `CorrectionRow`, `SupplementRow`,
`ReviewCaseRow`) wurden bereits nach `application/queries.py` verschoben
(Commit `6510bfb`), damit Presentation-Code keine Infrastructure-Klassen als
Typ-Annotationen benötigt.

### Nicht-intentionales Muster (Backlog)

**`SQLiteSystemConfigRepository` direkt in `terminal_ui/main.py`**  
`terminal_ui/main.py` importiert `SQLiteSystemConfigRepository` direkt, um den
`rfid_timeout`-Wert aus `system_config` zu lesen. Das ist ein einzelner
Config-Wert-Zugriff, kein Betriebsdienst. Hier wäre ein dünner Application-
Wrapper (z. B. `get_config_value(conn, key)` oder ein `SystemConfigService`)
angemessener — bleibt aber als Backlog-Item, da die Verbesserung keine
funktionale Auswirkung hat.

---

## Akzeptable Importe (Allowlist)

| Kategorie | Beispiele | Begründung |
| --- | --- | --- |
| DB-Wiring | `open_connection`, `SQLiteUnitOfWork` | Composition Root — Verdrahtung von Use Cases mit Repos |
| Infrastructure-Bootstrap | `run_migrations` | Einmaliger Bootstrap beim Start |
| Betriebsdienste | `SQLiteBackupService`, `run_system_check` | Kein sinnvoller Use-Case-Wrapper |
| Hardware-Wiring | `EvdevHardwareReader`, `SimulatedHardwareReader` | Gerätetreiber-Auswahl im Einstiegspunkt |
| Hardware-Ports | `HardwareReader` (Interface) | Abstraktion — korrekt |
| Export-Ausführung | `csv_exporter`, `pdf_report_service`, Query-Funktionen | SQL-Ausführung = Infrastructure |

## Unerwünschte Importe (Backlog)

| Kategorie | Beispiel | Status | Verbesserungsvorschlag |
| --- | --- | --- | --- |
| Direktes Repository | `SQLiteSystemConfigRepository` in `terminal_ui/main.py` | offen | Application-seitiger Config-Wrapper |
| Row-Typen direkt | `BookingRow` etc. aus `infrastructure/export/report_queries` | **behoben** ✓ | Erledigt durch `application/queries.py` |

---

## Abgrenzung zur import-linter-Regel

Der import-linter prüft aktuell nur den Contract `presentation → infrastructure → application → domain`.
Dieser Contract wird nicht verletzt — alle genannten Importe folgen der erlaubten
Richtung. Die ADR dokumentiert die **feinere Unterscheidung** innerhalb des erlaubten
Bereichs: welche Importe Composition-Root-Muster sind und welche Verbesserungspotenzial haben.

---

## Referenzen

- `application/queries.py` (Commit `6510bfb`) — Row-Typen in Application-Layer verschoben
- `domain/value_objects.py` (Commit `63f75b1`) — starke ID-Typen eingeführt
- `docs/SECURITY.md` — Sicherheitsrelevante Architekturentscheidungen
