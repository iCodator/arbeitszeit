# Faktenprüfung: `_RFID_READ_TIMEOUT` — Auslösemechanismus und Systemverhalten

## Geprüfte Dateien

| Datei | Betroffene Stellen |
| --- | --- |
| `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` | Zeile 78, 217–253, 274–288 |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | Zeile 42–77 |
| `src/arbeitszeit/presentation/terminal_ui/main.py` | Zeile 143–171, 227–230 |

---

## 1. Der Konstantenwert und sein Verwendungspunkt

```python
_RFID_READ_TIMEOUT: float = 5.0  # evdev_reader.py, Zeile 78
```

Der Wert wird an **einer einzigen Stelle** verwendet:

```python
def read_next(self) -> RawBookingRequest:  # Zeile 217
    booking_type = self._read_booking_type()
    raw_uid = self._read_rfid_uid(timeout=_RFID_READ_TIMEOUT).strip()  # Zeile 220
    ...
```

`_read_rfid_uid()` wartet auf die RFID-Karte, nachdem der Buchungstyp über das Numpad
ausgewählt wurde. Läuft der Timeout ab, bevor die vollständige Karten-UID eingelesen ist,
wird `HardwareTimeoutError` geworfen.

---

## 2. Technischer Auslösemechanismus

`_read_rfid_uid(timeout: float)` arbeitet nach folgendem Schema:

```
deadline = time.monotonic() + 5.0          # absolute Frist
while True:
    _wait_rfid_ready(deadline, timeout)    # blockiert bis zum nächsten Event
    result = _read_rfid_batch(...)         # liest gepufferte Events
    if result is not None:
        return result
```

### Innere Funktion `_wait_rfid_ready(deadline, timeout)`

```python
remaining = deadline - time.monotonic()    # Zeile 248: verbleibende Zeit
if remaining <= 0:
    raise HardwareTimeoutError(...)        # Zeile 250: Frist bereits überschritten
ready, _, _ = select.select(
    [self._rfid.fd], [], [], remaining     # Zeile 251: OS-Warteaufruf
)
if not ready:
    raise HardwareTimeoutError(...)        # Zeile 253: select lief leer aus
```

Es gibt **zwei unterschiedliche Auslösequellen für `HardwareTimeoutError`:**

1. **Absolute Frist überschritten** (`remaining <= 0`): tritt auf, wenn mehrere
   aufeinanderfolgende Lesevorgänge zusammen länger als 5 Sekunden dauern, ohne
   eine vollständige UID zu liefern.

2. **`select.select()` läuft leer** (`not ready`): tritt auf, wenn innerhalb der
   verbleibenden Zeit kein einziges Kernel-Event auf dem RFID-Gerätedeskriptor
   eintrifft. Das ist der häufigste Fall — keine Karte präsentiert.

`select.select()` ist ein systemnaher Aufruf (POSIX `select(2)`). Der Prozess blockiert
im Kernel, bis entweder ein Event eintrifft oder `remaining` Sekunden vergangen sind.
Es wird kein CPU-Polling betrieben.

---

## 3. Verhalten von `read_next()` bei Timeout

`HardwareTimeoutError` wird in `_read_rfid_uid()` geworfen und propagiert **unbehandelt**
aus `read_next()` heraus. In `read_next()` gibt es keinen `try/except`-Block.
Es gibt **keine interne Wiederholung** (`read_next()` versucht nicht, nach einem Timeout
erneut zu warten).

---

## 4. Äußere Aufrufkette

### `process_booking()` — `booking_loop.py`, Zeile 42

```python
def process_booking(reader, db_path, terminal_id) -> BookResult:
    request = reader.read_next()   # Zeile 42 — HardwareTimeoutError propagiert unbehandelt
    ...
```

Kein `try/except` in `process_booking()` für `HardwareTimeoutError`.
Die Exception steigt weiter auf.

### `_run_one_cycle()` — `main.py`, Zeile 143–171

```python
try:
    monitor.check()
    booking_result = process_booking(reader, db_path, terminal_id)  # Zeile 154
    print(format_feedback(booking_result))
except DomainError as exc:
    msg = _DOMAIN_MESSAGES.get(type(exc), f"Fehler: {exc.message}")
    print(msg)
except Exception as exc:                                   # Zeile 159 — greift hier
    print("Interner Fehler — Betrieb wird fortgesetzt.", file=sys.stderr)
    logging.exception("Buchungszyklus: unbehandelter Fehler")
    _log_system_event(
        db_path,
        "APPLICATION_ERROR",
        {"error": str(exc), "type": type(exc).__name__, "traceback": traceback.format_exc()},
    )
time.sleep(2)
```

`HardwareTimeoutError` ist eine Subklasse von `RuntimeError`, **nicht** von `DomainError`.
Der erste `except DomainError`-Zweig greift daher nicht. Der zweite Zweig
`except Exception` fängt die Exception auf.

Konkrete Wirkung eines Timeouts in `_run_one_cycle()`:

| Schritt | Aktion |
| --- | --- |
| Ausgabe auf `stderr` | `"Interner Fehler — Betrieb wird fortgesetzt."` |
| `logging.exception()` | Eintrag mit vollständigem Traceback in Log-Datei (wenn `logging.log_dir` konfiguriert) |
| `_log_system_event()` | INSERT in `system_events`-Tabelle, `event_type='APPLICATION_ERROR'`, `severity='ERROR'`, `source='terminal_ui'`, `details_json` mit Fehlertext, Typname und Traceback |
| `time.sleep(2)` | 2-Sekunden-Pause |
| Rückgabe | `_run_one_cycle()` gibt normal zurück |

### Äußere Schleife — `main.py`, Zeile 227–230

```python
while running:
    _run_one_cycle(reader, db_path, terminal_id, monitor)
```

`running` wird ausschließlich durch `SIGTERM` oder `SIGINT` auf `False` gesetzt.
`HardwareTimeoutError` hat **keinen Einfluss auf `running`**.

Nach Rückkehr von `_run_one_cycle()` — unabhängig davon, ob ein Timeout aufgetreten ist
oder nicht — beginnt sofort der nächste Buchungszyklus: `_clear_screen()`, Menüausgabe,
Warten auf Numpad-Eingabe.

---

## 5. Tatsachenbasierte Antworten auf die gestellten Fragen

**Frage a — Wie löst `select.select()` den Timeout aus?**

`select.select([rfid_fd], [], [], remaining)` blockiert den Prozess im Kernel.
Trifft in `remaining` Sekunden kein Event auf dem Gerätedeskriptor ein,
gibt `select.select()` ein leeres Ergebnis-Tuple zurück. `_wait_rfid_ready()` prüft
`if not ready` und wirft daraufhin `HardwareTimeoutError`. Das ist ein einziger,
blockierender Systemaufruf ohne Polling-Schleife.

**Frage b — Was bedeutet `HardwareTimeoutError` für `read_next()`?**

`read_next()` beendet sich sofort mit der Exception. Kein Retry, kein Logging innerhalb
von `read_next()`. Die Exception propagiert direkt an den Aufrufer (`process_booking()`).

**Frage c — Wie behandelt die äußere Aufrufkette die Exception?**

`_run_one_cycle()` fängt sie über `except Exception` auf, gibt eine Fehlermeldung auf
`stderr` aus, schreibt einen `APPLICATION_ERROR`-Eintrag in `system_events` und
`logging.exception()` in die Log-Datei. Danach wartet sie 2 Sekunden und kehrt zurück.

**Frage d — Wartet das Terminal weiter oder stoppt es?**

Das Terminal **wartet weiter und stoppt nicht**. Die äußere `while running`-Schleife
setzt den Betrieb nach jedem `_run_one_cycle()`-Aufruf fort, unabhängig davon, ob
ein Timeout aufgetreten ist.

**Frage e — Wird der Timeout geloggt oder angezeigt?**

Ja, dreifach:

1. `sys.stderr`-Ausgabe: `"Interner Fehler — Betrieb wird fortgesetzt."` (nicht benutzerfreundlich)
2. `logging.exception()`: Eintrag mit Traceback in `terminal_ui.log` (wenn konfiguriert)
3. `_log_system_event()`: INSERT in `system_events` mit vollständigem Fehlerkontext

Dem Mitarbeiter am Terminal wird **kein** fachlicher Hinweis angezeigt (kein
„Karte nicht gelesen" o. ä.). Die Fehlermeldung auf `stderr` ist technisch und
richtet sich implizit an Systemadministratoren.

---

## 6. Nicht eindeutig aus dem Code feststellbare Punkte

- **Sichtbarkeit der `stderr`-Ausgabe am physischen Terminal:** Hängt von der
  Darstellung des Terminal-Emulators und dem Display-Setup in der Praxis ab.
  Im Code ist `sys.stderr` die Ausgabe, ob dies auf dem physischen Bildschirm
  sichtbar ist, ist betriebsumgebungsabhängig.

- **Angemessenheit von 5,0 Sekunden:** Ob dieser Wert für den reinen RFID-Betrieb
  ausreicht, hängt von der Hardware (Lesegerät, USB-Latenz) und dem typischen
  Nutzerverhalten ab. Der bisher konfigurierte Produktivwert betrug 30 Sekunden
  (via `booking.grace_seconds_after_numpad_select`). Der neue Wert ist nicht
  konfigurierbar; eine Anpassung erfordert eine Code-Änderung.
