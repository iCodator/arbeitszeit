# Handbuch `arbeitszeit` – Infrastrukturschicht (`src/arbeitszeit/infrastructure`)

**Kapitel:** 6
**Version:** 1.0
**Stand:** Juli 2026
**Quelldatei:** `docs/module/handbuch_infrastructure.md`

## Überblick und Zweck

Die Infrastrukturschicht ist die unterste technische Ebene des Systems `arbeitszeit`.
Sie übersetzt die fachlichen Anforderungen der Domain- und Anwendungsschicht in
konkrete Betriebsmittel: SQLite-Datenbankzugriffe, Hardware-Kommunikation, Dateiexporte,
Backups und Systemüberwachung.

**Grundregel:** Alle anderen Schichten (Domain, Application) dürfen die Infrastruktur
nutzen, aber niemals von ihr abhängen. Die Infrastruktur kennt die Domain, nicht umgekehrt.
Direct-SQL-Abfragen außerhalb von `infrastructure` sind architektonisch verboten
(Regelwerk §11).

### Verzeichnisstruktur

```text
src/arbeitszeit/infrastructure/
├── __init__.py
├── notification.py          # Desktop-Benachrichtigung
├── system_check.py          # Selbsttest beim Start
├── time_monitor.py          # Zeitsprung-Erkennung
├── backup/
│   └── backup_service.py    # Lokales Backup + NAS-Sync
├── db/
│   ├── connection.py        # SQLite-Verbindung mit PRAGMAs
│   ├── migrations.py        # Schema-Migration aus SQL-Dateien
│   ├── unit_of_work.py      # Transaktionscontroller + Repositories
│   └── repositories/        # Ein Repository pro Entität (11 Klassen)
├── export/
│   ├── csv_exporter.py      # Detail- und Verdichtungsexport (CSV)
│   ├── pdf_report_service.py# Tages-/Wochen-/Monats-/Mitarbeiterberichte (PDF)
│   └── report_queries.py    # Gemeinsame Abfrageschicht für alle Exportkanäle
└── hardware/
    ├── ports.py             # Protokoll-Definitionen (Protocol-Klassen)
    ├── uid_hash.py          # SHA-256-Hash der RFID-UID
    ├── evdev_reader.py      # Physischer RFID-Reader + Numpad (evdev)
    └── simulator.py         # In-Memory-Simulator für Tests
```

---

## Datenbankzugriff (`db/`)

### Verbindungsaufbau — `db/connection.py`

Alle Datenbankverbindungen werden ausschließlich über `open_connection(db_path)` geöffnet.
Die Funktion setzt vier SQLite-PRAGMAs, die für den Betrieb zwingend erforderlich sind:

| PRAGMA | Wert | Begründung |
|---|---|---|
| `isolation_level` | `None` | Manuelle Transaktionskontrolle (kein Autocommit-Fallback) |
| `journal_mode` | `WAL` | Gleichzeitige Lese-/Schreibzugriffe (audit_conn + Haupt-Transaktion) |
| `foreign_keys` | `ON` | Referenzielle Integrität auf Datenbankebene |
| `busy_timeout` | `5000 ms` | 5 Sekunden Wartezeit bei Lock-Konflikt statt sofortigem Fehler |

Die Verbindung liefert immer `sqlite3.Row`-Objekte zurück, sodass Spalten
per Namen abrufbar sind (`row["employee_id"]` statt `row[0]`).

### Migrationen — `db/migrations.py`

Das Schema wird ausschließlich durch nummerierte SQL-Dateien im Verzeichnis
`migrations/` gesteuert (Format: `NNNN_beschreibung.sql`).

`run_migrations(conn)` arbeitet folgendes Schema ab:

1. Bereits angewandte Versionen aus `schema_migrations` laden.
2. SQL-Dateien aufsteigend durchlaufen; bekannte Versionen überspringen.
3. Jede Migration und ihre Registrierung in `schema_migrations` in **einer einzigen
   Transaktion** ausführen — entweder beides oder keines wird geschrieben.
4. Bei Fehler: `conn.rollback()`, dann Ausnahme weiterwerfen.

Der Versionsstring wird durch `version.isdigit() and len(version) == 4` validiert,
bevor er in den SQL-String eingebettet wird (kein SQL-Injection-Risiko).

### Unit of Work — `db/unit_of_work.py`

`SQLiteUnitOfWork` ist der einzige Einstiegspunkt für Use-Cases, die Datenbankänderungen
vornehmen. Er bündelt alle elf Repositories unter einem gemeinsamen Transaktions-Context-Manager:

```python
with SQLiteUnitOfWork(conn, audit_conn=audit_conn) as uow:
    uow.time_booking_repo.add(booking)
    uow.audit_log_repo.add(entry)
    uow.commit()   # explizit notwendig — __exit__ rollt sonst zurück
```

**Transaktionssemantik:** `__exit__` rollt **immer** zurück, sofern kein explizites
`commit()` aufgerufen wurde — auch ohne Exception. Eine vergessene Bestätigung
persistiert damit nie stillschweigend.

**Audit-Connection:** Die optionale `audit_conn` wird ausschließlich für Audit-Log-Einträge
verwendet und muss mit `isolation_level=None` (Autocommit) geöffnet sein.
Dadurch bleiben Audit-Einträge auch nach einem Rollback der Haupt-Transaktion erhalten.
Ohne `audit_conn` fällt das Audit-Log auf die Haupt-Verbindung zurück —
Einträge, die vor einem Rollback erzeugt wurden, gehen dann verloren.

### Repositories — `db/repositories/`

Jede Domänen-Entität besitzt genau ein Repository. Alle Repositories folgen demselben
Muster: Konstruktor nimmt `conn: sqlite3.Connection`; interne Hilfsfunktion `_row_to_entity`
wandelt `sqlite3.Row` in das Domänenobjekt um; alle Zeitstempel werden über
`_helpers._parse_dt()` UTC-normalisiert.

| Repository-Klasse | Tabelle | Kernmethoden |
|---|---|---|
| `SQLiteTimeBookingRepository` | `time_bookings` | `add`, `get_by_id`, `list_for_employee_on_day`, `list_open_for_employee`, `list_between`, `set_status` |
| `SQLiteEmployeeRepository` | `employees` | `get_by_id`, `get_active_by_personnel_no` |
| `SQLiteRfidCardRepository` | `rfid_cards` | `get_by_uid_hash`, `get_active_by_uid_hash`, `get_by_id` |
| `SQLiteUserAccountRepository` | `user_accounts` | `get_by_id`, `get_by_username`, `add` |
| `SQLiteWorkScheduleRepository` | `work_schedule_versions` | `add`, `close_version`, `get_effective` |
| `SQLiteReviewCaseRepository` | `review_cases` | `add`, `list_open_for_employee`, `resolve` |
| `SQLiteBookingCorrectionRepository` | `booking_corrections` | `add`, `list_for_booking` |
| `SQLiteSupplementRepository` | `supplements` | `add`, `get_by_id`, `list_pending`, `approve`, `reject` |
| `SQLiteAuditLogRepository` | `audit_log` | `add` (immer via `audit_conn` mit Autocommit) |
| `SQLiteSystemConfigRepository` | `system_config` | `get_current`, `set_current` |
| `SQLiteDeviceEventRepository` | `device_events` | `add` |

**Statushistorie:** `set_status` im `SQLiteTimeBookingRepository` schreibt jeden
Statuswechsel zusätzlich in `booking_status_history` — der vollständige Verlauf
jeder Buchung ist damit lückenlos rekonstruierbar.

**Konfigurationsversionierung:** `SQLiteSystemConfigRepository.set_current` erstellt
bei jeder Änderung einen neuen Datensatz mit inkrementierter `version`-Nummer.
Der aktuelle Wert ist stets der Datensatz mit dem höchsten `version`-Wert.

**Zeitzonenregel:** `list_for_employee_on_day` erwartet einen UTC-Kalendertag.
Die Anwendungsschicht ist verantwortlich, den lokalen Arbeitstag vor dem Aufruf
in UTC zu normalisieren.

---

## Hardware-Abstraktion (`hardware/`)

### Protokolldefinition — `hardware/ports.py`

Alle Hardware-Komponenten kommunizieren ausschließlich über das `HardwareReader`-Protocol
(PEP 544). Der Rückgabetyp jeder Buchungsanforderung ist `RawBookingRequest`:

```python
@dataclass(frozen=True)
class RawBookingRequest:
    booking_type: BookingType  # COME | GO | BREAK_START | BREAK_END
    uid_hash: str              # SHA-256-Hash der Karten-UID
    occurred_at: datetime      # UTC-Zeitstempel nach vollständiger UID-Lesung
```

Zusätzlich definiert `ports.py` zwei Fehlerfälle:
- `EmptyUidError`: RFID-Reader lieferte leere oder nicht mappbare UID.
- `HardwareTimeoutError`: UID-Lesung überschritt das Zeitlimit (Standard: 5 Sekunden).

### UID-Hashing — `hardware/uid_hash.py`

Die Roh-UID des RFID-Lesers (Hex-String oder Dezimalfolge) wird **nie direkt gespeichert**.
`hash_uid(raw_uid)` berechnet den SHA-256-Hash als Hex-String:

```python
hashlib.sha256(raw_uid.encode()).hexdigest()
```

Dieser Hash ist der einzige Bezeichner, der in die Datenbank gelangt (`rfid_cards.uid_hash`).
Damit ist die physische Karten-UID aus dem Datenbankinhalt nicht rückrechenbar.

### Physischer Reader — `hardware/evdev_reader.py`

`EvdevHardwareReader` liest Buchungsanfragen von zwei unabhängigen USB-HID-Geräten:

1. **USB-Numpad** (`/dev/input/event*`): Tasten 1–4 (KP-Variante und normale Ziffern)
   wählen den Buchungstyp (COME/GO/BREAK_START/BREAK_END).
2. **RFID-Reader** (`/dev/input/event*`): Liefert die Karten-UID als Hex-Zeichenfolge,
   abgeschlossen durch Enter. Nicht-Hex-Zeichen werden ignoriert.

**Ablauf eines `read_next()`-Aufrufs:**
1. `_read_booking_type()` blockiert unbegrenzt bis zu einer gültigen Numpad-Taste
   (Idle-Wartezustand, kein Timeout — Timeout-Logik gehört in die aufrufende Schicht).
2. `_read_rfid_uid()` liest die UID mit einem konfigurierbaren Timeout (Standard: 5 s).
3. `occurred_at` wird erst nach vollständiger UID-Lesung gesetzt.
4. `hash_uid()` berechnet den Hash; das `RawBookingRequest`-Objekt wird zurückgegeben.

Geräte werden mit `grab=True` exklusiv belegt, damit keine anderen Prozesse
(z. B. der Desktop) dieselben Tastenanschläge empfangen.

**Voraussetzung:** Der Systemprozess benötigt Lesezugriff auf `/dev/input/event*`
(Gruppe `input` oder udev-Regel).

Die Funktion `map_rfid_key(keycode, shift_active)` ist eigenständig testbar
ohne physische Hardware (enthält die gesamte Filterlogik).

### Simulator — `hardware/simulator.py`

`SimulatedHardwareReader` implementiert dasselbe `HardwareReader`-Protocol wie der
physische Reader und ermöglicht Tests ohne Hardware:

```python
reader = SimulatedHardwareReader()
reader.inject(BookingType.COME, uid_hash="abc123...")
request = reader.read_next()  # liefert das injizierte Ereignis
```

Die interne Queue ist eine `deque`; `pending` gibt die Anzahl noch nicht abgerufener
Ereignisse zurück. `read_next()` auf leerer Queue wirft `RuntimeError`.

---

## Export (`export/`)

### Gemeinsame Abfrageschicht — `export/report_queries.py`

**Alle** Exportkanäle (CSV, PDF, UI-Pflichtauswertungen) nutzen ausschließlich die
Funktionen in `report_queries.py`. Direkte Ad-hoc-Queries außerhalb dieses Moduls
sind architektonisch verboten (Regelwerk §11).

Öffentliche Abfragefunktionen:

| Funktion | Ergebnis |
|---|---|
| `list_bookings(conn, from_dt, to_dt, employee_id?)` | Alle Buchungen im Zeitraum, aufsteigend nach `booked_at` |
| `list_open_bookings(conn, employee_id?)` | Buchungen mit Status OPEN (kein Zeitraum) |
| `list_warn_bookings(conn, from_dt, to_dt, employee_id?)` | Buchungen mit Status WARN oder NEEDS_REVIEW |
| `list_open_bookings_in_period(conn, from_dt, to_dt, employee_id?)` | Offene Buchungen im Zeitraum (§7.12) |
| `list_corrections(conn, from_dt, to_dt, employee_id?)` | Korrekturen nach `corrected_at` |
| `list_supplements(conn, from_dt, to_dt, employee_id?)` | Nachträge nach `event_at` |
| `list_open_review_cases(conn, employee_id?)` | Offene Prüffälle (OPEN + IN_REVIEW, kein Zeitraum) |
| `list_open_review_cases_in_period(conn, from_dt, to_dt, employee_id?)` | Offene Prüffälle im Zeitraum (§7.12) |
| `list_review_cases_for_booking(conn, booking_id)` | Alle Prüffälle zu einer bestimmten Buchung |
| `get_employee_identity(conn, employee_id)` | `(personnel_no, employee_name)` — Fallback bei fehlendem Datensatz |

Alle Zeitraumbeschränkungen verwenden das halboffene Intervall `[from_dt, to_dt)`.

### CSV-Export — `export/csv_exporter.py`

Zwei Exportfunktionen erzeugen CSV-Dateien nach Pflichtenheft §7.11:

**Detailexport** (`export_detail`): Eine Zeile pro Buchung.

Felder: `buchungs_id`, `mitarbeiter_nr`, `mitarbeiter_name`, `datum`, `uhrzeit`,
`buchungsart`, `status`, `quelle`, `ist_nachtrag`, `ist_korrigiert`, `dauer_minuten`

- `dauer_minuten` wird aus dem Tagesverlauf abgeleitet: GO = Minuten seit letztem COME;
  BREAK_END = Minuten seit letztem BREAK_START; COME/BREAK_START = leer.
- Nachträge (`source=MANUAL`) werden mit `ist_nachtrag=ja` gekennzeichnet.

**Verdichtungsexport** (`export_condensed`): Eine Zeile pro Mitarbeiter und Kalendertag.

Felder: `mitarbeiter_nr`, `mitarbeiter_name`, `datum`, `nettoarbeitszeit_minuten`,
`nettopausenzeit_minuten`, `pausenanzahl`, `anzahl_buchungen`, `offene_buchungen`,
`warn_buchungen`, `pruefpflicht_buchungen`, `korrekturen`, `nachtraege`

Die Tagesstatistik `_day_stats()` arbeitet als Zustandsmaschine:
- Nettoarbeitszeit = Summe aller Arbeitsphasen (COME→BREAK_START und BREAK_END→GO).
- Pausen werden nicht zur Arbeitszeit gezählt.
- Korrekturen werden am `corrected_at`-Tag, Nachträge am `event_at`-Tag gezählt.

**Dateinamenschema:**

```text
export_detail_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
export_verdichtet_YYYYMMDD_YYYYMMDD_YYYYMMDDTHHMMSSZ.csv
```

Der `export_dir`-Pfad wird von der aufrufenden Schicht aus `system_config`
gelesen und direkt übergeben.

### PDF-Berichte — `export/pdf_report_service.py`

Vier Berichtsfunktionen erzeugen A4-PDFs via `reportlab` (Pflichtenheft §7.11):

| Funktion | Dateiname | Zeitraum |
|---|---|---|
| `create_daily_report(conn, day, export_dir)` | `bericht_tag_YYYY-MM-DD_…Z.pdf` | Ein Kalendertag (alle Mitarbeiter) |
| `create_weekly_report(conn, year, week, export_dir)` | `bericht_woche_YYYY-WNN_…Z.pdf` | ISO-Woche (alle Mitarbeiter) |
| `create_monthly_report(conn, year, month, export_dir)` | `bericht_monat_YYYY-MM_…Z.pdf` | Kalendermonat (alle Mitarbeiter) |
| `create_employee_report(conn, employee_id, from_dt, to_dt, export_dir)` | `bericht_mitarbeiter_NNNN_…_…Z.pdf` | Freier Zeitraum (ein Mitarbeiter) |

Jeder Bericht enthält fünf inhaltliche Abschnitte:
1. **Buchungen** — Tabelle aller Buchungen im Zeitraum
2. **Korrekturen** — Alter Zustand, neuer Zustand, Begründung, Zeitstempel
3. **Nachträge** — Buchungsart, Ereigniszeitpunkt, Begründung, Freigabestatus
4. **Offene Prüffälle** — Typ, Schwere, Beschreibung, Erkennungszeitpunkt
5. **Erläuterungen** — Bedeutung der Status-Codes (OPEN, WARN, NEEDS_REVIEW,
   Nachträge, Korrekturen)

---

## Backup (`backup/backup_service.py`)

`SQLiteBackupService` verwaltet lokale Sicherungskopien und optionale NAS-Synchronisation.

### Methoden

**`create_local_backup()`**: Erstellt ein Online-Backup via SQLite-Backup-API
(`sqlite3.Connection.backup()`). Die Quelldatenbank bleibt während des Backups
vollständig lesbar und schreibbar — kein Sperren, kein Downtime.

- Dateiname: `arbeitszeit_YYYYMMDDTHHMMSSZ.db`
- Falls `export_dir` gesetzt: Exportdateien werden nach `backup_dir/exports/` kopiert
  und vom nachfolgenden NAS-Sync mitgenommen.
- Ergebnis wird in `audit_log` mit Ereignistyp `BACKUP_CREATED` protokolliert.

**`sync_to_nas(nas_path)`**: Synchronisiert `backup_dir/` → NAS via `rsync --archive --delete`.

- Schlägt die Synchronisation fehl, wird `BACKUP_SYNC_FAILED` mit Returncode,
  Befehlszeile und stderr ins Audit-Log geschrieben; die Ausnahme wird weitergereicht.
- Erfolg wird mit `BACKUP_SYNCED_TO_NAS` protokolliert.

**`restore_from(backup_path, restore_exports?)`**: Stellt die Datenbank aus einer
Backup-Datei wieder her.

- Vorbedingung: Keine offenen Verbindungen zur Zieldatenbank beim Aufruf.
- Führt nach dem Restore `PRAGMA integrity_check` aus; schlägt dieser fehl,
  wird `RuntimeError` geworfen.
- Mit `restore_exports=True` und gesetztem `export_dir`: Exportdateien werden
  aus `backup_dir/exports/` zurück in `export_dir` kopiert.
- Ergebnis wird als `RESTORE_COMPLETED` ins Audit-Log der **wiederhergestellten**
  Datenbank geschrieben.

**`run(nas_path?)`**: Kombinierte Hilfsmethode — erstellt lokales Backup und
synchronisiert optional zum NAS; gibt `BackupResult` zurück.

**NAS-Erreichbarkeitsprüfung (Designentscheidung):** Das System prüft den
NAS-Mount-Punkt ausschließlich per `Path.exists()` und `os.access(..., os.W_OK)`.
Kein Netzwerk-Ping oder TCP-Verbindungstest — ein vorübergehend nicht erreichbares
NAS (Neustart, Wartung) soll keinen `SELFTEST_FAIL` auslösen.

---

## Systemüberwachung

### Selbsttest — `system_check.py`

`run_system_check(db_path, numpad_path?, rfid_path?)` prüft beim Systemstart
fünf Bereiche und schreibt das Gesamtergebnis als `SELFTEST_OK` oder `SELFTEST_FAIL`
in `system_events`:

| Prüfbereich | Was wird geprüft |
|---|---|
| `db_access` | Datenbankverbindung öffenbar; alle erwarteten Migrationsversionen angewendet |
| `config_keys` | Sechs Pflicht-Konfigurationsschlüssel in `system_config` vorhanden |
| `nas_reachability` | NAS-Pfad existiert und ist schreibbar (nur wenn `backup.nas_enabled=true`) |
| `fk_consistency` | `PRAGMA foreign_key_check` meldet keine verwaisten Fremdschlüsselreferenzen |
| `device_availability` | Numpad und RFID-Gerätepfade existieren und sind lesbar |

Jeder Bereich liefert ein `CheckResult(name, ok, detail)`. Das `SystemCheckResult`
aggregiert alle Checks; `overall_ok` ist `True` genau dann, wenn alle Checks bestanden sind.

### Zeitsprung-Erkennung — `time_monitor.py`

`SystemTimeMonitor` erkennt Uhrzeitänderungen durch Gegenüberstellung von
Wall-Clock (`datetime.now(timezone.utc)`) und monotoner Uhr (`time.monotonic()`):

```text
diff = actual_wall_ts - (last_wall_ts + mono_elapsed)
```

- `|diff| > threshold` (Standard: 60 Sekunden): Zeitsprung erkannt.
- `diff > 0`: Vorwärtssprung → Ereignistyp `TIME_JUMP_DETECTED`
  (NTP-Korrektur oder manuelle Vorstellung).
- `diff < 0`: Rückwärtssprung → Ereignistyp `MANUAL_TIME_CHANGE_DETECTED`
  (fast immer manuell).

Der Schwellenwert filtert NTP-Drift (typisch < 1 s/Stunde) heraus.
`load_threshold_from_config(db_path)` liest den Wert aus `system_config`
(Schlüssel `time_monitor.jump_threshold_seconds`); Fallback: 60 Sekunden.

Beide Clock-Funktionen sind per Dependency-Injection ersetzbar (`_wall_clock`,
`_mono_clock`), was Unit-Tests ohne Systemzeit-Manipulation ermöglicht.

### Desktop-Benachrichtigung — `notification.py`

`notify(title, body, urgency?)` sendet eine Desktop-Benachrichtigung via `notify-send`
(Pflichtenheft §7.10: Systemzustand muss dem Betreiber sichtbar sein).

- Dringlichkeitsstufen: `"low"` | `"normal"` | `"critical"`
- **Fail-Safe:** `FileNotFoundError` (notify-send nicht installiert) und
  `TimeoutExpired` werden still ignoriert; ein `logging.debug`-Eintrag wird erzeugt.
- Sonstige Ausnahmen erzeugen einen `logging.warning`-Eintrag.
- Voraussetzung: Paket `libnotify-bin` (auf Lubuntu/Linux Mint standardmäßig vorhanden).

---

## Querverbindungen und Architekturprinzipien

### Abhängigkeitsrichtung

```text
Application/Domain
       ↓
  infrastructure/
  ├── db/           ← nutzt domain.entities, domain.enums, domain.ports
  ├── export/       ← nutzt application.queries, domain.enums
  ├── hardware/     ← nutzt domain.enums
  ├── backup/       ← nutzt domain.audit_events, domain.entities
  └── system_check/ ← nutzt infrastructure.db.connection
```

Alle Repositories implementieren die in `domain/ports/repositories.py` definierten
Abstract-Base-Interfaces — die Fachlogik kennt daher nur das Interface, nie die
SQLite-Implementierung.

### Nicht delegierte Verantwortlichkeiten

Die Infrastrukturschicht übernimmt bewusst **keine** Zuständigkeit für:
- Fachliche Validierung (gehört in die Domain- oder Anwendungsschicht).
- Timeout-Logik für den Numpad-Idle-Wartezustand (gehört in die Betriebsschicht).
- NTP-Synchronisation (Aufgabe des Betriebssystems / systemd).
- Authentifizierung und Autorisierung (Anwendungsschicht).

### Testbarkeit

Alle sicherheitskritischen und zustandsbehafteten Teile sind ohne physische Hardware testbar:
- `SimulatedHardwareReader` implementiert dasselbe Protocol wie `EvdevHardwareReader`.
- `map_rfid_key()` ist eine pure Funktion ohne Gerätezugriff.
- `SystemTimeMonitor` akzeptiert injizierbare Clock-Callbacks.
- Repositories arbeiten auf jeder `sqlite3.Connection`, auch auf In-Memory-Datenbanken (`:memory:`).
