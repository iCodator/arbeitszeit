# Plan: Admin-TUI auf Textual-Basis

**Stand:** 2026-07-20
**Branch:** `feature/admin_gui`

## Kontext

Die bestehende `admin_cli` ist funktional vollständig, aber nur über die
Kommandozeile bedienbar. Eine Textual-TUI soll dieselben Operationen interaktiv
zugänglich machen — navigierbar mit Pfeiltasten, tabellarische Übersichten,
Formulare für Schreiboperationen — ohne dabei die bestehende Architektur
zu verändern.

Die TUI ruft Use Cases **direkt** auf (wie die CLI), kein Subprocess-Wrapping.
Die Architektur (kein DI-Framework, reines Constructor Injection) erlaubt das
ohne Anpassungen an der Domänenschicht.

Geschätzter Aufwand: **4–5 Wochen.**

---

## Nicht im Scope (CLI bleibt zuständig)

- `cards assign --scan` (Hardware-Zugriff)
- `system setup` (interaktiver Einrichtungsassistent)
- `users bootstrap` (einmaliger Erststart)

---

## Architektur-Grundlagen

**DB-Verbindung öffnen** (einmalig beim App-Start):

```python
from arbeitszeit.infrastructure.config_file import find_config, load_config
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork

cfg = load_config(find_config())
conn = open_connection(cfg.database.path)        # Haupt-Transaktion
audit_conn = open_connection(cfg.database.path)  # Autocommit für AuditLog
run_migrations(conn)
```

**Use Case aufrufen** (pro Action):

```python
uow = SQLiteUnitOfWork(conn, audit_conn)   # leichtgewichtig, kein Singleton
result = SomeUseCase(uow).execute(SomeCommand(...))
```

**Fehlerbehandlung:** alle fachlichen Fehler erben von `DomainError`
(`src/arbeitszeit/domain/errors.py`): `PermissionDeniedError`, `NotFoundError`,
`ConflictError`, `ValidationError` u. a. → in der TUI als Notification anzeigen.

---

## Neue Dateistruktur

```text
src/arbeitszeit/presentation/admin_tui/
├── __init__.py
├── app.py              # TuiApp-Klasse, main()-Einstiegspunkt
├── _connection.py      # DB-Verbindungslebenszyklus + Config (sys.exit-frei)
└── screens/
    ├── login.py        # LoginScreen: DB-Pfad + User-ID eingeben
    ├── main.py         # MainScreen: Sidebar + ContentArea
    ├── employees.py    # Mitarbeiterliste + Add/Deactivate-Modals
    ├── cards.py        # Assign/Replace/Deactivate-Modals
    ├── bookings.py     # Correct/Supplement/Approve/Reject-Tabs
    ├── schedule.py     # Dienstplan-Übersicht + Set-Modal
    ├── reports.py      # Alle 10 Report-Typen mit Datumsfeldern
    ├── system.py       # SystemCheck + Backup
    └── users.py        # Benutzerliste + Add/Deactivate/Reactivate/ChangeRole
```

Kein `widgets/`-Verzeichnis in Phase 1 — gemeinsame Widgets als interne
Hilfsfunktionen beginnen; bei Bedarf später auslagern.

---

## Screens im Detail

### `_connection.py` — Verbindungshelfer

Adaptiert `_resolve_db_path()` / `_resolve_user_id()` aus `admin_cli/main.py`,
ersetzt `sys.exit()` durch `ValueError`. Stellt `AppState`-Dataclass bereit:
`conn`, `audit_conn`, `db_path`, `user_id`, `cfg`.

```python
def resolve_db_path(db_arg: Path | None, cfg: AppConfig | None) -> Path:
    if db_arg:
        return db_arg
    if cfg and cfg.database.path:
        return cfg.database.path
    raise ValueError("Kein Datenbankpfad angegeben und keiner in config.toml.")

def resolve_user_id(user_id_arg: int | None, cfg: AppConfig | None) -> int:
    if user_id_arg is not None:
        return user_id_arg
    env_val = os.environ.get("ADMIN_USER_ID")
    if env_val:
        return int(env_val)
    if cfg and cfg.admin and cfg.admin.user_id:
        return cfg.admin.user_id
    raise ValueError("Keine Benutzer-ID angegeben.")
```

### `LoginScreen`

- Zwei `Input`-Widgets: DB-Pfad (vorbelegt aus `config.toml`), User-ID
- Schaltfläche „Verbinden" → `open_connection` + `run_migrations` → `MainScreen`
- Fehlermeldung bei falschem Pfad oder nicht existentem Konto

### `MainScreen`

- Links: `ListView` mit 7 Einträgen (Employees, Cards, Bookings, Schedule,
  Reports, System, Users)
- Rechts: `ContentSwitcher` — tauscht die aktive Komponente aus
- Tastaturkürzel: `q` zum Beenden, Zifferntasten 1–7 für direkten Sprung

### `EmployeesScreen`

- `DataTable`: ID | Nr | Name | Status — via direktem SQL (wie CLI)
- Schaltflächen: „Hinzufügen" (Modal), „Deaktivieren" (Modal mit ID-Bestätigung)
- Modal „Hinzufügen": Personalnr., Vorname, Nachname → `CreateEmployeeUseCase`
- Modal „Deaktivieren": ID-Eingabe → `DeactivateEmployeeUseCase`

### `CardsScreen`

- Kein Listing (kein allgemeiner List-Befehl ohne Employee-Kontext)
- Drei Schaltflächen: „Zuweisen", „Ersetzen", „Deaktivieren" — je ein Modal
- „Zuweisen": Employee-ID + UID-Hash → `AssignRfidCardUseCase`
- „Ersetzen": alte Card-ID + neuer UID-Hash → `ReplaceRfidCardUseCase`
- „Deaktivieren": Card-ID → `DeactivateRfidCardUseCase`

### `BookingsScreen`

- `TabbedContent` mit 4 Tabs: Korrektur / Nachtrag / Genehmigen / Ablehnen
- Korrektur: Booking-ID, Typ (Select), Datum+Uhrzeit (TT.MM.JJJJ HH:MM),
  Begründung → `CorrectBookingUseCase`
- Nachtrag anlegen: Employee-ID, Typ, Datum+Uhrzeit, Begründung
  → `RegisterSupplementUseCase` (`recorded_at = datetime.now(utc)` intern)
- Nachtrag genehmigen: Supplement-ID → `ApproveSupplementUseCase`
- Nachtrag ablehnen: Supplement-ID + Begründung → `RejectSupplementUseCase`

### `ScheduleScreen`

- `DataTable`: Wochentag | Von | Bis | Gültig ab | Bereich — via direktem SQL
- Schaltfläche „Eintrag setzen" → Modal: Wochentag (Select 1–7), Start (HH:MM),
  Ende (HH:MM), Datum (TT.MM.JJJJ), Employee-ID (optional)
  → `ManageWorkScheduleUseCase`

### `ReportsScreen`

- `TabbedContent`: Export-Tab / Auswertungen-Tab
- Export-Tab: CSV, PDF-Tag, PDF-Woche, PDF-Monat, PDF-Mitarbeiter,
  CSV-Prüffälle — je mit Datums-/Jahres+Monats-Inputs; Ergebnis: Ausgabepfad
- Auswertungen-Tab: offene Buchungen, Warnfälle, Korrekturen, Nachträge,
  offene Prüffälle — je mit optionalem Datumsbereich als `DataTable`

### `SystemScreen`

- „Systemcheck" → `run_system_check()` → Ergebnis als `DataTable`
- „Backup erstellen" → `SQLiteBackupService.create_local_backup()`
  → Ausgabepfad als Notification

### `UsersScreen`

- `DataTable`: ID | Benutzername | Rolle | Status — via direktem SQL
- Schaltflächen: Hinzufügen / Deaktivieren / Reaktivieren / Rolle ändern
  → je ein Modal

---

## Einstiegspunkt

`pyproject.toml` unter `[project.scripts]`:

```toml
aztui = "arbeitszeit.presentation.admin_tui.app:main"
```

Aufruf: `aztui` oder `python -m arbeitszeit.presentation.admin_tui.app`

---

## Abhängigkeit

`textual` unter `[project.dependencies]` in `pyproject.toml` ergänzen
(aktuelle Stable-Version prüfen und pinnen).

---

## Phasen und Reihenfolge

| Phase | Inhalt | Aufwand |
| --- | --- | --- |
| 1 | `_connection.py`, `app.py`, `LoginScreen`, `MainScreen`-Skeleton | 2–3 Tage |
| 2 | `EmployeesScreen` + Modals (einfachste Gruppe, Referenzimplementierung) | 2–3 Tage |
| 3 | `UsersScreen`, `CardsScreen`, `ScheduleScreen` | 4–5 Tage |
| 4 | `BookingsScreen` (Datumseingabe, 4 Tabs) | 3–4 Tage |
| 5 | `ReportsScreen` (10 Untertypen, CSV/PDF-Pfadausgabe) | 5–6 Tage |
| 6 | `SystemScreen`, Keyboard-Shortcuts, Fehlerbehandlung, Tests | 3–4 Tage |

**Gesamt: ca. 4–5 Wochen**

---

## Betroffene Dateien

| Datei | Art |
| --- | --- |
| `src/arbeitszeit/presentation/admin_tui/` | neues Paket (alle Dateien neu) |
| `pyproject.toml` | `[project.scripts]` + `[project.dependencies]` ergänzen |
| `CHANGELOG.md` | Eintrag |

Keine Änderungen an Domäne, Infrastruktur oder bestehender `admin_cli`.

---

## Verifikation

```bash
aztui
# → LoginScreen erscheint, DB-Pfad vorbelegt
# → Employees → Hinzufügen → Formular → "Mitarbeiter angelegt"
# → Reports → CSV-Export → Ausgabepfad erscheint
pytest tests/integration/test_admin_tui.py -q
```
