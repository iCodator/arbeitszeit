# Programmieraufgabe: `APPLICATION_ERROR`-Logging in Terminal-UI absichern

## Herleitung aus `phase5_planung.md`

Das Dokument beschreibt in Befund 5/1-06 explizit:

> „Unerwartete Laufzeitfehler werden jetzt als `APPLICATION_ERROR`
> (nicht `APPLICATION_STOP`) in `system_events` protokolliert. Dazu wurde
> `0006_system_events_application_error.sql` ergänzt."

Die Testverteilungs-Sektion nennt 10 Tests in `tests/e2e/test_booking_flow.py`.
Alle 10 rufen `process_booking()` direkt auf — keiner testet den Ausnahme-Handler
in `run()`, der `APPLICATION_ERROR` auslöst.

---

## Befund

`terminal_ui/main.py` enthält in `run()` eine Endlosschleife:

```python
while running:
    try:
        monitor.check()
        booking_result = process_booking(reader, db_path, terminal_id)
        print(format_feedback(booking_result))
    except DomainError as exc:
        msg = _DOMAIN_MESSAGES.get(type(exc), f"Fehler: {exc.message}")
        print(msg)
    except Exception as exc:                       # ← dieser Pfad ist ungetestet
        print("Interner Fehler — Betrieb wird fortgesetzt.", file=sys.stderr)
        _log_system_event(
            db_path, "APPLICATION_ERROR",
            {"error": str(exc), "type": type(exc).__name__},
        )
```

Das `except Exception`-Zweig ist der einzige Pfad, der `APPLICATION_ERROR` in
`system_events` schreibt. Er ist nicht testbar, solange die Logik direkt in der
Endlosschleife steckt — ein Test müsste `run()` in einem Thread starten und per
Signal stoppen, was die Tests fragil und plattformabhängig macht.

---

## Aufgabe

**Loop-Body extrahieren und `APPLICATION_ERROR`-Logging mit zwei E2E-Tests absichern.**

### 1. `terminal_ui/main.py`: `_run_one_cycle()` extrahieren

Den Try/Except-Block aus der `while running:`-Schleife in eine eigene Funktion
auslagern:

```python
def _run_one_cycle(
    reader: HardwareReader,
    db_path: Path,
    terminal_id: int,
    monitor: SystemTimeMonitor,
) -> None:
    """Ein Buchungszyklus: Zeitcheck → Buchung → Feedback oder Fehlerbehandlung."""
    monitor.check()
    try:
        booking_result = process_booking(reader, db_path, terminal_id)
        print(format_feedback(booking_result))
    except DomainError as exc:
        msg = _DOMAIN_MESSAGES.get(type(exc), f"Fehler: {exc.message}")
        print(msg)
    except Exception as exc:
        print("Interner Fehler — Betrieb wird fortgesetzt.", file=sys.stderr)
        _log_system_event(
            db_path,
            "APPLICATION_ERROR",
            {"error": str(exc), "type": type(exc).__name__},
        )
```

`run()` wird damit:

```python
try:
    while running:
        _run_one_cycle(reader, db_path, terminal_id, monitor)
finally:
    reader.close()
```

**Kein Verhaltensunterschied** — reine Extraktion.

### 2. `tests/e2e/test_booking_flow.py`: Zwei neue Tests

Die Tests rufen `_run_one_cycle()` direkt auf, ohne Threading.

```python
from arbeitszeit.presentation.terminal_ui.main import _run_one_cycle


def test_unerwartete_exception_schreibt_application_error_in_system_events(
    db, terminal_id, card_id
):
    """Unerwarteter Fehler im Reader → APPLICATION_ERROR in system_events."""

    class BrokenReader:
        def read_next(self):
            raise RuntimeError("Gerätepanne simuliert")
        def close(self):
            pass

    monitor = _make_monitor(db)  # Hilfsfunktion analog zu bestehenden Tests
    _run_one_cycle(BrokenReader(), db, terminal_id, monitor)

    conn = open_connection(db)
    events = conn.execute(
        "SELECT event_type, details_json FROM system_events "
        "WHERE event_type = 'APPLICATION_ERROR'"
    ).fetchall()
    conn.close()

    assert len(events) == 1
    details = json.loads(events[0]["details_json"])
    assert details["type"] == "RuntimeError"
    assert "Gerätepanne" in details["error"]


def test_domain_error_schreibt_kein_application_error(db, terminal_id):
    """DomainError (bekannter Fehlertyp) darf keinen APPLICATION_ERROR auslösen."""

    class UnknownCardReader:
        def read_next(self):
            # Simuliert unbekannte Karte ohne Datenbankzugriff über den Fehler-Pfad
            from arbeitszeit.infrastructure.hardware.simulator import (
                RawBookingRequest,
            )
            return RawBookingRequest(
                booking_type=BookingType.COME,
                uid_hash="unbekannte_uid",
                occurred_at=datetime.now(timezone.utc),
            )
        def close(self):
            pass

    monitor = _make_monitor(db)
    _run_one_cycle(UnknownCardReader(), db, terminal_id, monitor)

    conn = open_connection(db)
    count = conn.execute(
        "SELECT COUNT(*) FROM system_events WHERE event_type = 'APPLICATION_ERROR'"
    ).fetchone()[0]
    conn.close()
    assert count == 0
```

---

## Betroffene Dateien

| Datei | Änderung |
|---|---|
| `src/arbeitszeit/presentation/terminal_ui/main.py` | Loop-Body → `_run_one_cycle()` extrahieren |
| `tests/e2e/test_booking_flow.py` | 2 neue Tests + `_make_monitor()`-Hilfsfunktion |

---

## Akzeptanzkriterium

- `_run_one_cycle()` ist direkt importierbar und aufrufbar ohne `run()` oder Threads
- Unerwartete Exception → `APPLICATION_ERROR` in `system_events` mit
  `{"type": ..., "error": ...}` in `details_json`
- Bekannte `DomainError`-Subklassen → kein `APPLICATION_ERROR`-Eintrag
- `python -m pytest tests/e2e/test_booking_flow.py` → 12 Tests grün
- `python -m pytest` → alle Tests grün (keine Regression)
