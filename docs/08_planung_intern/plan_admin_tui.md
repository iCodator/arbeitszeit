# Plan: Admin-TUI auf Textual-Basis

**Stand:** 2026-07-20
**Branch:** `feature/admin_gui`
**Gesamt:** 16 Schritte, ca. 4–5 Wochen

## Prinzipien

- Jeder Schritt endet mit einem **lauffähigen, prüfbaren Zustand**.
- Kein Schritt startet, bevor der vorherige verifiziert ist.
- Lesezugriff (Liste anzeigen) immer **vor** Schreibzugriff (Modal) implementieren.
- Fehlerbehandlung in jedem Schritt mitliefern — nicht am Ende nachrüsten.

---

## Kontext

Die bestehende `admin_cli` ist funktional vollständig. Eine Textual-TUI soll
dieselben Operationen interaktiv zugänglich machen — ohne die bestehende
Architektur zu verändern. Die TUI ruft Use Cases **direkt** auf (kein
Subprocess-Wrapping). Kein DI-Framework — reines Constructor Injection.

**Nicht im Scope** (CLI bleibt zuständig):

- `cards assign --scan` (Hardware-Zugriff)
- `system setup` (interaktiver Assistent)
- `users bootstrap` (einmaliger Erststart)

---

## Dateistruktur (Zielzustand)

```text
src/arbeitszeit/presentation/admin_tui/
├── __init__.py
├── app.py
├── _connection.py
└── screens/
    ├── login.py
    ├── main.py
    ├── employees.py
    ├── cards.py
    ├── bookings.py
    ├── schedule.py
    ├── reports.py
    ├── system.py
    └── users.py
```

---

## Schritt 1 — Paketgerüst + Abhängigkeit

**Dateien:** `pyproject.toml`, `src/arbeitszeit/presentation/admin_tui/__init__.py`,
`src/arbeitszeit/presentation/admin_tui/app.py`

- `textual` unter `[project.dependencies]` in `pyproject.toml` eintragen
  (aktuelle Stable-Version pinnen)
- Einstiegspunkt `aztui = "arbeitszeit.presentation.admin_tui.app:main"`
  unter `[project.scripts]` ergänzen
- `app.py`: minimale `class AdminTuiApp(App)` mit leerem `compose()`,
  `main()`-Funktion die `AdminTuiApp().run()` aufruft

**Verifikation:**

```bash
pip install -e .
aztui          # startet, zeigt leeres Terminal-Fenster, q beendet
```

---

## Schritt 2 — `_connection.py`: Config + DB-Verbindung

**Datei:** `src/arbeitszeit/presentation/admin_tui/_connection.py`

`sys.exit()`-freie Varianten der CLI-Hilfsfunktionen:

```python
@dataclass
class AppState:
    conn: sqlite3.Connection
    audit_conn: sqlite3.Connection
    db_path: Path
    user_id: int
    cfg: AppConfig | None

def resolve_db_path(db_arg: Path | None, cfg: AppConfig | None) -> Path:
    # --db > config.toml > ValueError

def resolve_user_id(user_id_arg: int | None, cfg: AppConfig | None) -> int:
    # arg > ENV ADMIN_USER_ID > config.toml > ValueError

def open_app_state(db_path: Path, user_id: int) -> AppState:
    # open_connection × 2, run_migrations, return AppState
```

Importiert aus:
`arbeitszeit.infrastructure.config_file` (`find_config`, `load_config`),
`arbeitszeit.infrastructure.db.connection` (`open_connection`),
`arbeitszeit.infrastructure.db.migrations` (`run_migrations`)

**Verifikation:**

```bash
python -c "
from pathlib import Path
from arbeitszeit.presentation.admin_tui._connection import open_app_state
state = open_app_state(Path('arbeitszeit.db'), 1)
print(state.user_id)
"
```

---

## Schritt 3 — `LoginScreen`

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/login.py`

- `Input` DB-Pfad — vorbelegt aus `find_config()` → `load_config()` →
  `cfg.database.path`
- `Input` User-ID — vorbelegt aus `cfg.admin.user_id` oder leer
- Button „Verbinden" → ruft `open_app_state()` auf, bei Erfolg `push_screen(MainScreen(state))`
- Fehlermeldung (Label, rot) bei `ValueError` oder `sqlite3.OperationalError`
- `app.py` zeigt `LoginScreen` als initiale App-Klasse

**Verifikation:**

```text
aztui
→ LoginScreen erscheint, DB-Pfad vorbelegt
→ falsche DB → Fehlermeldung erscheint, kein Absturz
→ korrekte DB + User-ID → wechselt zu MainScreen (noch leer)
```

---

## Schritt 4 — `MainScreen`-Skeleton

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/main.py`

- Horizontales Layout: `ListView` (links, fixe Breite) + `ContentSwitcher` (rechts)
- `ListView`-Einträge: `1 Mitarbeitende`, `2 RFID-Karten`, `3 Buchungen`,
  `4 Dienstplan`, `5 Berichte`, `6 System`, `7 Benutzer`
- `ContentSwitcher` zeigt je einen Platzhalter-`Static` pro Eintrag
- Tastaturkürzel: `q` → beendet, `1`–`7` → direkter Sprung
- `on_list_view_selected` → schaltet `ContentSwitcher` um

**Verifikation:**

```text
→ Sidebar sichtbar, Navigation mit Pfeiltasten und Zifferntasten funktioniert
→ q beendet sauber
→ Platzhaltertexte erscheinen rechts
```

---

## Schritt 5 — `EmployeesScreen`: Mitarbeiterliste (Lesezugriff)

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/employees.py`

- `DataTable` mit Spalten: ID | Nr | Name | Status
- Beim Mounten: direktes SQL `SELECT id, personnel_no, first_name, last_name, active FROM employees ORDER BY personnel_no`
- `AppState.conn` wird aus dem Screen-Konstruktor übernommen
- `MainScreen` instanziiert `EmployeesScreen(state)` im ContentSwitcher

**Verifikation:**

```text
→ Mitarbeitende | Liste wird geladen und angezeigt
→ leere DB → Tabelle leer, kein Fehler
```

---

## Schritt 6 — `EmployeesScreen`: Hinzufügen + Deaktivieren (Schreibzugriff)

**Datei:** `screens/employees.py` (Ergänzung)

- Button-Leiste unter Tabelle: „+ Hinzufügen" | „Deaktivieren"
- Modal „Hinzufügen": drei `Input`-Felder (Personalnr., Vorname, Nachname)
  → `CreateEmployeeUseCase(SQLiteUnitOfWork(state.conn, state.audit_conn))`
  → bei Erfolg: Notification + Tabelle neu laden
  → bei `DomainError`: Notification mit Fehlermeldung
- Modal „Deaktivieren": `Input` für ID
  → `DeactivateEmployeeUseCase`
  → analog

**Verifikation:**

```text
→ Hinzufügen → neuer Mitarbeiter erscheint in Liste
→ Deaktivieren → Status wechselt auf inaktiv
→ ungültige Personalnummer → DomainError erscheint als Notification
```

---

## Schritt 7 — `UsersScreen`: Benutzerliste + Schreibzugriff

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/users.py`

- `DataTable`: ID | Benutzername | Rolle | Status
- SQL: `SELECT id, username, role, active FROM user_accounts WHERE role != 'EMPLOYEE' ORDER BY role, username`
- Vier Buttons: „+ Hinzufügen" | „Deaktivieren" | „Reaktivieren" | „Rolle ändern"
- Modal „Hinzufügen": Username, Rolle (Select: ADMIN/REVIEWER/TECH),
  optionales Passwort (leer → zufällig generiert, einmalig angezeigt)
  → `CreateUserAccountUseCase` (Passwort-Hashing: PBKDF2-HMAC-SHA256)
- Modals Deaktivieren/Reaktivieren: User-ID-Input
  → `DeactivateUserAccountUseCase` / `ReactivateUserAccountUseCase`
- Modal Rolle ändern: User-ID + Rolle-Select → `ChangeUserRoleUseCase`

**Verifikation:**

```text
→ Benutzerliste wird geladen
→ Hinzufügen mit Zufallspasswort → Passwort wird einmalig als Notification angezeigt
→ Rolle ändern → Status aktualisiert sich in Tabelle
```

---

## Schritt 8 — `CardsScreen`: RFID-Karten-Modals

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/cards.py`

Kein Listing (kein allgemeiner List-Befehl ohne Employee-Kontext).
Drei Buttons → je ein Modal:

- „Zuweisen": Employee-ID + UID-Hash → `AssignRfidCardUseCase`
- „Ersetzen": alte Card-ID + neuer UID-Hash → `ReplaceRfidCardUseCase`
- „Deaktivieren": Card-ID → `DeactivateRfidCardUseCase`

Hinweis-Label: `cards assign --scan` (Hardware-Scan) ist nur per CLI verfügbar.

**Verifikation:**

```text
→ Zuweisen → "Karte zugewiesen (ID X)" Notification
→ ungültige Employee-ID → Fehlermeldung
```

---

## Schritt 9 — `ScheduleScreen`: Dienstplan anzeigen (Lesezugriff)

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/schedule.py`

- Zwei `DataTable`s (oder Tabs): global / mitarbeiterspezifisch
- SQL analog zu `schedule show` in `admin_cli/schedule.py`:
  `SELECT ... FROM work_schedule_versions WHERE valid_until IS NULL ORDER BY scope_type, scope_employee_id, weekday`
- Rollenpüfung: `require_admin_or_reviewer(state.conn, state.user_id)`
  → bei Fehler: Notification, Screen bleibt leer

**Verifikation:**

```text
→ Dienstplan wird angezeigt
→ kein Eintrag → Tabelle leer, kein Fehler
```

---

## Schritt 10 — `ScheduleScreen`: Dienstplan setzen (Schreibzugriff)

**Datei:** `screens/schedule.py` (Ergänzung)

- Button „Eintrag setzen" → Modal:
  - Wochentag (Select 1–7, Beschriftung Mo–So)
  - Start-Zeit (`Input`, Format HH:MM)
  - End-Zeit (`Input`, Format HH:MM)
  - Gültig ab (`Input`, Format TT.MM.JJJJ)
  - Employee-ID (`Input`, optional — leer = globale Regel)
- → `ManageWorkScheduleUseCase`
- Nach Erfolg: Tabelle neu laden

**Verifikation:**

```text
→ neuer Eintrag erscheint in Tabelle
→ ungültiges Datumsformat → Validierungsmeldung vor Use-Case-Aufruf
```

---

## Schritt 11 — `BookingsScreen`: Tab-Gerüst + Buchung korrigieren

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/bookings.py`

- `TabbedContent` mit 4 Tabs: Korrektur | Nachtrag | Genehmigen | Ablehnen
- Tab 1 „Korrektur": Booking-ID, Typ (Select: COME/GO/BREAK_START/BREAK_END),
  Datum+Uhrzeit (`Input`, Format TT.MM.JJJJ HH:MM), Begründung
  → `CorrectBookingUseCase`
- Lokale Validierung vor Use-Case-Aufruf: Datumsformat, Typ-Enum

**Verifikation:**

```text
→ Tab-Struktur erscheint
→ gültige Korrektur → Notification "Korrektur angelegt (ID X)"
→ ungültiges Datum → Fehlermeldung vor Aufruf
```

---

## Schritt 12 — `BookingsScreen`: Nachtrag + Genehmigung + Ablehnung

**Datei:** `screens/bookings.py` (Ergänzung)

- Tab 2 „Nachtrag": Employee-ID, Typ, Datum+Uhrzeit, Begründung,
  optionale Related-Booking-ID
  → `RegisterSupplementUseCase` (`recorded_at = datetime.now(utc)` intern)
- Tab 3 „Genehmigen": Supplement-ID → `ApproveSupplementUseCase`
- Tab 4 „Ablehnen": Supplement-ID + Begründung → `RejectSupplementUseCase`

**Verifikation:**

```text
→ alle 4 Tabs bedienbar
→ Nachtrag genehmigen → "Buchung X angelegt (Status: OK)"
```

---

## Schritt 13 — `ReportsScreen`: Auswertungen (Lesezugriff)

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/reports.py`

- `TabbedContent`: Auswertungen | Export
- Auswertungen-Tab: Sub-Navigation für 5 Berichte:
  offene Buchungen, Warnfälle, Korrekturen, Nachträge, offene Prüffälle
- Je zwei optionale Datumsfelder (`--from` / `--to`, TT.MM.JJJJ) + optionale Employee-ID
- Ergebnis als `DataTable` (Spalten je nach Bericht)
- Rollenprüfung via `require_admin_or_reviewer`

**Verifikation:**

```text
→ Warnfälle: Tabelle zeigt Buchungen mit WARN-Status
→ leerer Zeitraum → Tabelle leer, kein Fehler
→ fehlende Rolle → Fehlermeldung
```

---

## Schritt 14 — `ReportsScreen`: Exporte (CSV + PDF)

**Datei:** `screens/reports.py` (Ergänzung)

- Export-Tab: Sub-Navigation für 6 Export-Typen:
  CSV-Buchungen, CSV-Prüffälle, PDF-Tag, PDF-Woche, PDF-Monat, PDF-Mitarbeiter
- Je nach Typ: Datums-Inputs (TT.MM.JJJJ), Jahr+Woche, Jahr+Monat,
  Employee-ID — alles via `Input`-Widgets
- Nach Aufruf: Ausgabepfad als Notification anzeigen
- Verwendet `_intervals.py`-Hilfsfunktionen (`day_interval`, `week_interval`,
  `month_interval`) und `_get_export_dir()` aus `admin_cli/reports.py`

**Verifikation:**

```text
→ CSV-Export → Datei existiert, Pfad erscheint als Notification
→ PDF-Monat → PDF-Datei wird erzeugt
```

---

## Schritt 15 — `SystemScreen`

**Datei:** `src/arbeitszeit/presentation/admin_tui/screens/system.py`

- Button „Systemcheck" → `run_system_check(state.db_path, state.cfg)`
  → Ergebnis als `DataTable`: Check | Status | Detail
- Button „Backup erstellen" → `SQLiteBackupService(...).create_local_backup()`
  → Ausgabepfad als Notification
  → NAS-Sync falls konfiguriert
- Rollenprüfung: `require_admin_or_tech`

**Verifikation:**

```text
→ Systemcheck → alle 7 Checks erscheinen in Tabelle
→ Backup → Dateipfad in Notification
```

---

## Schritt 16 — Finalisierung

- Einheitliche Fehlerbehandlung: alle `DomainError`-Subklassen werden
  als Textual-`Notification` (Typ `error`) angezeigt — keine rohen Exceptions
- Keyboard-Shortcuts: `1`–`7` in `MainScreen` vollständig verdrahten
- `CHANGELOG.md`: Eintrag für das neue Feature
- Integrationstests: `tests/integration/test_admin_tui.py`
  (LoginScreen mit Test-DB, EmployeesScreen Add/Deactivate)
- Statische Prüfung: `ruff check src/arbeitszeit/presentation/admin_tui/`
  und `mypy src/arbeitszeit/presentation/admin_tui/ --ignore-missing-imports`

**Verifikation:**

```bash
ruff check src/arbeitszeit/presentation/admin_tui/
mypy src/arbeitszeit/presentation/admin_tui/ --ignore-missing-imports
pytest tests/integration/test_admin_tui.py -q
aztui   # vollständiger manueller Durchlauf aller Screens
```

---

## Abhängigkeiten zwischen Schritten

```text
1 → 2 → 3 → 4 → 5 → 6
                4 → 7
                4 → 8
                4 → 9 → 10
                4 → 11 → 12
                4 → 13 → 14
                4 → 15
          6,7,8,10,12,14,15 → 16
```

Schritte 5–15 bauen alle auf Schritt 4 (`MainScreen`) auf und sind
**untereinander unabhängig** — können in beliebiger Reihenfolge umgesetzt werden.

---

## Betroffene Dateien (Zielzustand)

| Datei | Art |
| --- | --- |
| `src/arbeitszeit/presentation/admin_tui/` | neues Paket |
| `pyproject.toml` | `textual`-Abhängigkeit + `aztui`-Einstiegspunkt |
| `CHANGELOG.md` | Eintrag |

Keine Änderungen an Domäne, Infrastruktur oder bestehender `admin_cli`.
