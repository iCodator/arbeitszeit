# Faktenanalyse: Offene Fragen F4, F1, F2, F6, F7

## F4 — Verhalten bei 5. Buchung (alle vier Buchungstypen)

**Belegte Fakten:**

Nach einem vollständigen Tagesablauf (COME → BREAK\_START → BREAK\_END → GO)
liefert `_has_open_work()` den Wert `False` und `_has_open_break()` den Wert
`False`.
Grundlage:
[domain/services/booking_rules.py:68–82](../../src/arbeitszeit/domain/services/booking_rules.py)

Die Funktion `validate_booking_sequence()` ruft anhand des gewünschten Typs
den zuständigen `_validate_*()`-Validator auf
([booking_rules.py:20–23](../../src/arbeitszeit/domain/services/booking_rules.py)).

Verhalten je Buchungstyp bei Zustand `open_work=False, open_break=False`:

**COME** → `_validate_come(False, False)` ([booking_rules.py:31–34](../../src/arbeitszeit/domain/services/booking_rules.py)):
Prüft `if open_work` (False → kein Fehler) und `if open_break` (False → kein Fehler).
**Kein Fehler wird geworfen.** Die Buchung wird ohne Exception durchgeführt.

**GO** → `_validate_go(False, False)` ([booking_rules.py:37–40](../../src/arbeitszeit/domain/services/booking_rules.py)):
Prüft `if not open_work` → True → wirft
`InvalidBookingSequenceError("GO ohne offene Arbeitsphase nicht zulässig.")`.
**Exception wird geworfen.**

**BREAK\_START** → `_validate_break_start(False, False)` ([booking_rules.py:43–49](../../src/arbeitszeit/domain/services/booking_rules.py)):
Prüft `if not open_work` → True → wirft
`InvalidBookingSequenceError("BREAK_START ohne offene Arbeitsphase.")`.
**Exception wird geworfen.**

**BREAK\_END** → `_validate_break_end(False, False)` ([booking_rules.py:52–53](../../src/arbeitszeit/domain/services/booking_rules.py)):
Prüft `if not open_break` → True → wirft
`InvalidBookingSequenceError("BREAK_END ohne offene Pause nicht zulässig.")`.
**Exception wird geworfen.**

**Tatsachenantwort:**

Es gibt aktuell keine generelle Obergrenze von vier Buchungen pro Tag im Code.
Die Buchungstypen GO, BREAK\_START und BREAK\_END werden nach einem vollständigen
Tagesablauf durch die jeweiligen `_validate_*()`-Funktionen mit einer
`InvalidBookingSequenceError`-Exception abgewiesen. Der Buchungstyp COME hingegen
wird nach einem vollständigen Tagesablauf (Zustand `open_work=False,
open_break=False`) von `_validate_come()` **nicht** abgewiesen und kann ohne
Exception verarbeitet werden. Eine fünfte Buchung vom Typ COME ist im aktuellen
Code technisch möglich.

---

## F1 — Rolle von `validate_booking_sequence()`

**Belegte Fakten:**

Produktive Aufrufstellen vollständig (ergänzend zur F3-Klärung eigenständig
geprüft):

- [application/use_cases/book_time.py:25](../../src/arbeitszeit/application/use_cases/book_time.py)
  — Import in `book_time.py`
- [application/use_cases/book_time.py:104–107](../../src/arbeitszeit/application/use_cases/book_time.py)
  — Aktiver Aufruf in `BookUseCase.execute()`:

  ```python
  validate_booking_sequence(
      cmd.booking_type,
      [b.booking_type for b in day_bookings],
  )
  ```

  `cmd.booking_type` stammt aus `BookCommand`, das in
  [booking_loop.py:70](../../src/arbeitszeit/presentation/terminal_ui/booking_loop.py)
  aus `request.booking_type` befüllt wird — dem Wert aus der
  NumPad-Hardware-Eingabe.

- [application/use_cases/approve_supplement.py:27](../../src/arbeitszeit/application/use_cases/approve_supplement.py)
  — Import in `approve_supplement.py`
- [application/use_cases/approve_supplement.py:56–59](../../src/arbeitszeit/application/use_cases/approve_supplement.py)
  — Aktiver Aufruf in `ApproveSupplementUseCase.execute()`:

  ```python
  validate_booking_sequence(
      supplement.booking_type,
      [b.booking_type for b in day_bookings],
  )
  ```

  `supplement.booking_type` stammt aus dem `supplements`-Datenbankdatensatz,
  der beim `RegisterSupplementUseCase`-Aufruf gespeichert wurde und ebenfalls
  einen explizit angegebenen Typ enthält.

Es gibt keine weiteren produktiven Aufrufstellen außerhalb dieser beiden
Use Cases.

Die Signatur der Funktion lautet:

```python
def validate_booking_sequence(
    booking_type: BookingType,
    day_bookings: Sequence[BookingType],
) -> None:
```

([booking_rules.py:12–14](../../src/arbeitszeit/domain/services/booking_rules.py))

Die Funktion nimmt `booking_type` als ersten Parameter entgegen und prüft,
ob dieser Typ im gegebenen Tageskontext zulässig ist. Sie leitet den Typ
nicht ab — sie setzt ihn als Eingabe voraus. An keiner ihrer zwei produktiven
Aufrufstellen wird ein berechneter oder abgeleiteter Typ übergeben; in beiden
Fällen stammt der Typ aus einer vorangegangenen expliziten Eingabe (Hardware
oder gespeicherter Supplement-Datensatz).

**Tatsachenantwort:**

`validate_booking_sequence()` prüft ausschließlich einen vom Aufrufer
vorgegebenen `booking_type`. Die Funktion berechnet oder leitet den Typ nicht
ab. Ihre Signatur setzt einen vorab bekannten Typ als Pflichtparameter voraus.
Die Funktion ist strukturell in der Lage, mit einem beliebig erzeugten
`BookingType`-Wert aufgerufen zu werden — auch einem abgeleiteten — sofern
der Aufrufer diesen Wert vor dem Aufruf berechnet und als Argument übergibt.
Die Funktion selbst enthält keine Logik, die die Herkunft des Typs
(Eingabe vs. Ableitung) unterscheidet oder voraussetzt.

---

## F2 — Ergänzende Detailprüfung zu F4

Status: Vollständig durch F4-Prüfung (Schritt 1) abgedeckt, keine zusätzliche
Prüfung erforderlich.

Alle vier Buchungstypen wurden in Schritt 1 mit konkreten Codezeilen aus
[booking_rules.py](../../src/arbeitszeit/domain/services/booking_rules.py)
belegt. Die genaue Fehlerklasse (`InvalidBookingSequenceError` vs. kein Fehler)
und der Fehlertext wurden je Typ angegeben.

---

## F6 — `booking.grace_seconds_after_numpad_select`

**Belegte Fakten:**

Der Config-Key tritt an folgenden Stellen auf:

- [migrations/0002_seed_defaults.sql:30](../../migrations/0002_seed_defaults.sql)
  — `INSERT`-Eintrag mit Defaultwert `30` (Typ: Integer):

  ```sql
  ('booking.grace_seconds_after_numpad_select', 30, 1, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup'),
  ```

- [infrastructure/system_check.py:25](../../src/arbeitszeit/infrastructure/system_check.py)
  — Eintrag in `_REQUIRED_CONFIG_KEYS`:

  ```python
  "booking.grace_seconds_after_numpad_select",
  ```

  Der System-Check prüft damit, ob dieser Key in der Datenbank vorhanden ist.

- [presentation/terminal_ui/main.py:226–230](../../src/arbeitszeit/presentation/terminal_ui/main.py)
  — Lesezugriff und Verwendung in `run()`:

  ```python
  grace_json = SQLiteSystemConfigRepository(grace_conn).get_current(
      "booking.grace_seconds_after_numpad_select"
  )
  rfid_timeout = float(json.loads(grace_json)) if grace_json is not None else 5.0
  ```

  Der gelesene Wert wird als `rfid_timeout` an `EvdevHardwareReader.__init__()`
  übergeben ([main.py:235](../../src/arbeitszeit/presentation/terminal_ui/main.py)).

- [infrastructure/hardware/evdev_reader.py:208–222](../../src/arbeitszeit/infrastructure/hardware/evdev_reader.py)
  — `rfid_timeout` wird in `read_next()` als Timeout für `_read_rfid_uid()`
  verwendet:

  ```python
  raw_uid = self._read_rfid_uid(timeout=self._rfid_timeout).strip()
  ```

  `_read_rfid_uid()` ist die Funktion, die nach einer NumPad-Auswahl auf
  den RFID-Scan wartet
  ([evdev_reader.py:276–285](../../src/arbeitszeit/infrastructure/hardware/evdev_reader.py)).
  Der Ablauf in `read_next()` ist: zuerst `_read_booking_type()` (NumPad-Eingabe),
  danach `_read_rfid_uid(timeout=self._rfid_timeout)` (RFID-Scan mit Timeout).

Der Config-Key tritt außerhalb von `main.py` (Präsentationsschicht) und
`system_check.py` (Infrastruktur) nicht auf. Es gibt keinen Zugriff auf diesen
Key in der Domänen- oder Anwendungsschicht.

**Tatsachenantwort:**

Der Wert von `booking.grace_seconds_after_numpad_select` wird ausschließlich
als Timeout für den RFID-Leseschritt verwendet, der auf eine NumPad-Auswahl
folgt (`EvdevHardwareReader.read_next()`: erst NumPad, dann RFID innerhalb des
Timeouts). Der Key hat keinen Verwendungsort außerhalb dieses NumPad-bezogenen
Ablaufs. Ein Zugriff aus einem rein RFID-bezogenen Codepfad (ohne NumPad)
existiert nicht.

---

## F7 — Persistenz vs. Live-Ableitung des Tageszustands

**Belegte Fakten:**

Das vollständige Datenbankschema ist in
[migrations/0001_schema.sql](../../migrations/0001_schema.sql) definiert.
Es enthält folgende Tabellen: `schema_migrations`, `employees`, `user_accounts`,
`rfid_cards`, `terminals`, `time_bookings`, `booking_status_history`,
`booking_corrections`, `supplements`, `review_cases`, `review_case_actions`,
`work_schedule_versions`, `system_config`, `device_events`, `system_events`,
`audit_log`.

Keine dieser Tabellen enthält eine Spalte oder eine Tabellenstruktur, die
einen Tageszustand (z. B. `day_state`, `current_state`, `booking_count_today`
o. ä.) pro Mitarbeitendem explizit persistiert. Die weiteren Migrationen
(`0003` bis `0006`) fügen keine solche Struktur hinzu (bestätigt durch
vollständige Dateiauflistung der Migrationsdateien).

Die `list_for_employee_on_day()`-Implementierung in
[infrastructure/db/repositories/time_booking.py:58–68](../../src/arbeitszeit/infrastructure/db/repositories/time_booking.py)
führt bei jedem Aufruf eine direkte SQL-Abfrage aus:

```python
rows = self._conn.execute(
    f"{_SELECT} WHERE employee_id = ? AND booked_at >= ? AND booked_at < ? "
    "ORDER BY booked_at",
    (employee_id, day_start.isoformat(), next_day.isoformat()),
).fetchall()
```

Es gibt keinen Caching-Mechanismus, keine In-Memory-Zustandsspeicherung und
kein Repository-internes State-Objekt, das Ergebnisse vorhält. Jeder Aufruf
liest live aus der Datenbank.

**Tatsachenantwort:**

Es existiert im aktuellen Datenbankschema keine Tabelle und keine Spalte, die
einen Tageszustand pro Mitarbeitendem explizit persistiert. Der Tageszustand
wird bei jedem Zugriff ausschließlich live aus den gespeicherten
`time_bookings`-Datensätzen abgeleitet. Es gibt keinen zwischengespeicherten
Zustand.

---

## Nicht eindeutig feststellbare Punkte

Keine. Alle fünf Fragen sind aus dem Code vollständig und eindeutig
beantwortbar.
