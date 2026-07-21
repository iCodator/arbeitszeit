# Faktenprüfung F8: `_RFID_READ_TIMEOUT` — Verwendung, Zweck und Entfernbarkeit

## Geprüfte Dateien

| Datei | Betroffene Stellen |
| --- | --- |
| `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` | Zeile 18–20, 77–78, 215–228, 230–241, 243–253, 274–288 |
| `src/arbeitszeit/presentation/terminal_ui/main.py` | Zeile 143–171, 209–230 |
| `tests/integration/test_hardware_evdev.py` | Zeile 152–208, 334–389 |

Vollständige Suche nach `_RFID_READ_TIMEOUT` und `rfid_timeout` im gesamten Projektverzeichnis
(`src/` und `tests/`) ergab außer den unten aufgeführten Fundstellen keine weiteren Treffer.

---

## 1. Fundstellen von `_RFID_READ_TIMEOUT`

Der Name `_RFID_READ_TIMEOUT` taucht im gesamten Projekt an genau **zwei Stellen** auf:

| Datei | Zeile | Art |
| --- | --- | --- |
| `evdev_reader.py` | 78 | Definition: `_RFID_READ_TIMEOUT: float = 5.0` |
| `evdev_reader.py` | 220 | Verwendung: `self._read_rfid_uid(timeout=_RFID_READ_TIMEOUT).strip()` |

Der Wert `5.0` erscheint darüber hinaus an drei Stellen in den Tests — jedoch **nicht** durch
Referenz auf die Konstante, sondern als eigenständiges Literal:

| Datei | Zeile | Kontext |
| --- | --- | --- |
| `test_hardware_evdev.py` | 166 | Direkt: `reader._read_rfid_uid(5.0)` |
| `test_hardware_evdev.py` | 208 | Direkt: `reader._read_rfid_uid(5.0)` |
| `test_hardware_evdev.py` | 341 | Default-Parameter in Testhelfer: `timeout: float = 5.0` |

Die Tests referenzieren `_RFID_READ_TIMEOUT` **nicht namentlich** — sie testen das
Verhalten von `_read_rfid_uid()` bei einem übergebenen Timeout-Argument, unabhängig
vom Wert der Konstante.

---

## 2. Technischer Zweck des Timeouts in `_read_rfid_uid()`

### Worauf wartet die Methode?

`_read_rfid_uid(timeout: float)` wartet auf die vollständige Hex-UID eines RFID-Lesegeräts,
die als HID-Tastatureingabe angeliefert wird (Zeichen für Zeichen, abgeschlossen durch Enter).
Der Wartemechanismus ist:

```python
deadline = time.monotonic() + timeout          # Zeile 283: absolute Frist
while True:
    self._wait_rfid_ready(deadline, timeout)   # Zeile 285: OS-Ebene
    result, shift_active = self._read_rfid_batch(chars, shift_active)
    if result is not None:
        return result
```

Innerhalb von `_wait_rfid_ready()` (Zeilen 243–253):

```python
remaining = deadline - time.monotonic()
if remaining <= 0:
    raise HardwareTimeoutError(...)            # Absolute Frist überschritten
ready, _, _ = select.select([self._rfid.fd], [], [], remaining)
if not ready:
    raise HardwareTimeoutError(...)            # select() lief ohne Event ab
```

Der `select.select()`-Aufruf übergibt `remaining` als Timeout-Argument. Das ist ein
OS-Systemaufruf, der den Prozess blockiert, bis entweder ein Event auf dem
Gerätedeskriptor eintrifft oder `remaining` Sekunden vergangen sind.

### Was passiert konkret beim Timeout?

`HardwareTimeoutError` wird geworfen und propagiert unbehandelt durch `_read_rfid_uid()`
→ `read_next()` → `process_booking()` bis nach `_run_one_cycle()` (Zeile 159),
wo er durch `except Exception as exc` abgefangen wird. Dort:

- Ausgabe auf `sys.stderr`: `"Interner Fehler — Betrieb wird fortgesetzt."`
- `logging.exception()` mit Traceback in die Log-Datei (falls konfiguriert)
- `_log_system_event()` schreibt `APPLICATION_ERROR`-Eintrag in `system_events`
- `time.sleep(2)` — 2-Sekunden-Pause
- Rückkehr aus `_run_one_cycle()` → nächster Zyklus beginnt

Es findet kein Zustandswechsel statt; `running` bleibt `True`.

---

## 3. Aufrufkette

`_read_rfid_uid()` wird **einmal pro Buchungszyklus** aufgerufen, nicht in einer Schleife:

```
run()                              [main.py, Zeile 174]
  └─ while running:                [main.py, Zeile 227]
       └─ _run_one_cycle()         [main.py, Zeile 228]
            └─ process_booking()   [booking_loop.py, Zeile 42]
                 └─ reader.read_next()          [evdev_reader.py, Zeile 215]
                      ├─ _read_booking_type()   [Zeile 216 — blockiert unbegrenzt]
                      └─ _read_rfid_uid(        [Zeile 220]
                             timeout=_RFID_READ_TIMEOUT)
```

`_read_booking_type()` (Zeilen 230–241) blockiert mithilfe von `evdev.InputDevice.read_loop()`,
das seinerseits `select.select([self.fd], [], [])` **ohne Timeout-Argument** aufruft
(belegt durch Quellcode-Inspektion der evdev-Bibliothek). Das ist laut Modul-Docstring
(Zeile 18–20) bewusstes Design: "Das ist beabsichtigt: Das System wartet im Idle auf
eine Buchungsauswahl. Timeout-Logik für den Wartezustand gehört in die aufrufende
Betriebsschicht."

`_read_rfid_uid()` wird erst aufgerufen, nachdem `_read_booking_type()` eine gültige
Numpad-Taste zurückgegeben hat.

---

## 4. Prüfung der vollständigen Entfernbarkeit

### 4a. Hängt eine Komponente von regelmäßigem Rückkehren aus `_read_rfid_uid()` ab?

**Ja: die Signalbehandlung.**

`run()` installiert für SIGTERM und SIGINT einen Handler `_stop()` (Zeilen 211–216),
der `running = False` setzt. Die Schleife `while running:` prüft diesen Wert jedoch
nur **zwischen Zyklen**, nicht während eines Zyklus. Kommt ein Signal während des
Wartens in `_read_rfid_uid()`, gilt Folgendes:

- Der Signal-Handler `_stop()` wird sofort ausgeführt und setzt `running = False`.
- **PEP 475 (Python ≥ 3.5):** `select.select()` wird nach einem `EINTR`-Signal
  automatisch vom Python-Interpreter neu gestartet. Das Signal-Handling (Ausführen
  von `_stop()`) erfolgt vor dem Neustart, aber `select.select()` setzt anschließend
  den Wartevorgang bis zum nächsten Event oder Timeout fort.
- Mit Timeout: `_read_rfid_uid()` kehrt spätestens nach `_RFID_READ_TIMEOUT` Sekunden
  zurück → `while running:` kann `running = False` erkennen → Graceful Shutdown.
- **Ohne Timeout:** `select.select()` läuft weiter bis ein RFID-Event eintrifft, egal
  ob ein Signal `running = False` gesetzt hat. Das Terminal würde nicht beendet, solange
  keine RFID-Karte gescannt wird.

### 4b. Blockiert die Methode ohne Timeout unbegrenzt?

**Ja.** Wird `select.select([self._rfid.fd], [], [])` ohne Timeout-Argument aufgerufen,
blockiert der Prozess im Kernel bis zu einem Event auf dem RFID-Deskriptor.
Ohne eingehende Events (keine Karte gescannt) bleibt der Prozess dort dauerhaft stehen.

Für den normalen Betrieb (Nutzer scannt sofort nach Numpad-Eingabe) wäre das kein Problem.
Für den Fehlerfall (Numpad-Taste gedrückt, keine Karte gescannt) wäre das Terminal
dauerhaft blockiert und durch keinen Befehl (außer `SIGKILL`) beendbar.

**Einschränkung:** Dasselbe gilt schon jetzt für `_read_booking_type()`. Das Terminal
blockiert im Idle bereits unbegrenzt und reagiert nicht sofort auf SIGTERM. Dieses
Verhalten ist im Modul-Docstring explizit als gewollt beschrieben. Das Entfernen des
RFID-Timeouts würde dieses Muster auf die zweite Warte-Phase ausdehnen.

### 4c. Tests oder Code-Stellen, die sich auf `_RFID_READ_TIMEOUT` verlassen?

Kein Test importiert oder referenziert `_RFID_READ_TIMEOUT` namentlich. Alle Tests
in `TestReadRfidUid` (Zeilen 152–208) rufen `_read_rfid_uid(5.0)` mit einem
Literal-Argument auf; der konkrete Wert spielt in den Tests keine inhaltliche Rolle
(alle `select.select()`-Aufrufe werden gemockt). Ein Entfernen oder Umbenennen der
Konstante hätte **keine Auswirkungen auf die Tests**.

`scan_rfid_uid_hash()` (Zeile 154) ist eine separate Funktion (nicht Teil von
`EvdevHardwareReader`) mit eigenem Timeout-Parameter (Default 15,0 s) und ist
von `_RFID_READ_TIMEOUT` unabhängig.

---

## 5. Fazit zur Entfernbarkeit

**Ergebnis: Nicht ersatzlos entfernbar — entfernbar mit Anpassung, die das Fehlerverhalten
verändert.**

Begründung:

1. **Fehlerfall Numpad-ohne-RFID:** Im aktuellen Code-Stand ruft `read_next()` zuerst
   `_read_booking_type()` (blockiert bis Numpad-Eingabe), dann `_read_rfid_uid()` auf.
   Ohne den Timeout würde ein unbeabsichtigter Numpad-Druck das Terminal dauerhaft
   blockieren, bis eine RFID-Karte gescannt wird — ohne Möglichkeit zum Graceful Shutdown.

2. **Graceful Shutdown:** SIGTERM setzt `running = False`, aber das Terminal kehrt ohne
   Timeout aus `_read_rfid_uid()` nicht zurück, solange keine Karte gescannt wird.
   Ein Prozess-Stop wäre nur per `SIGKILL` möglich — ein Unterschied zu SIGTERM.
   Der Datenverlust-Beitrag ist gering (kein laufender Schreibvorgang), aber der
   Shutdown-Weg entspricht nicht dem in `run()` vorgesehenen Mechanismus.

3. **Tests:** Nicht betroffen. Die Tests referenzieren die Konstante nicht direkt.

**Wichtige Einschränkung:** Das unter Punkt 2 beschriebene SIGTERM-Verhalten besteht
für die `_read_booking_type()`-Phase bereits jetzt — das Terminal reagiert im Idle
(Warten auf Numpad) ebenfalls nicht sofort auf SIGTERM. Das ist explizit so dokumentiert.
Das Entfernen von `_RFID_READ_TIMEOUT` würde dieses Muster auf die RFID-Warte-Phase
ausdehnen, aber kein grundlegend neues Problem einführen.

**Für die laufende RFID-only-Migration gilt ergänzend (nicht eindeutig feststellbar):**
Sobald `_read_booking_type()` und der Numpad-Pfad vollständig entfernt werden, entfällt
der unter Punkt 1 beschriebene Fehlerfall. Ob das Timeout für die dann verbleibende
einzige Warte-Phase (`_read_rfid_uid()` als alleinigen Blockierpunkt) sinnvoll ist,
hängt davon ab, ob eine RFID-Karte im regulären Betrieb immer innerhalb kurzer Zeit
präsentiert wird. Das ist eine betriebliche Frage, die aus dem Code allein nicht
beantwortet werden kann.

---

## Nicht eindeutig feststellbare Punkte

- **Betriebliche Kartenscan-Zeiterwartung:** Ob 5,0 s als Timeout für den RFID-only-Betrieb
  zu kurz ist (kein Numpad-Zwischenschritt mehr, Nutzer scannt sofort), lässt sich aus
  dem Code nicht ableiten. Es hängt von Hardware (Lesereichweite, USB-Latenz) und
  Nutzerverhalten ab.

- **Verhalten von `select.select()` bei SIGTERM unter der konkreten Ziel-Hardware**
  (Raspberry Pi, evtl. anderer Linux-Kernel): PEP 475 gilt ab Python 3.5 plattformübergreifend;
  plattformspezifische Besonderheiten wurden nicht geprüft.
