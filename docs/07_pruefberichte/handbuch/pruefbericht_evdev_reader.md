# Prüfbericht – docs/infrastructure/evdev_reader.md

## Gesamteinschätzung

Das Handbuchdokument beschreibt das Modul `evdev_reader.py` insgesamt zutreffend und zeigt eine hohe Übereinstimmung mit dem tatsächlichen Quellcode. Die zentralen Aussagen zu Buchungstypen, RFID-Leseverhalten, Zeitstempellogik, Fehlerbehandlung und Lebenszyklus sind korrekt belegt. Es gibt jedoch zwei präzisierungsbedürftige Punkte: die Beschreibung der Shift-Logik (Groß-/Kleinschreibung der UID) und die Darstellung des `grab`-Parameters im Konstruktor, die beide feiner differenziert werden können. Insgesamt ist die Dokumentation verlässlich und nur in wenigen Detailaussagen unvollständig oder unscharf.

## Abschnitt: Zweck

**Aussage 1:**
`evdev_reader.py` liest Buchungsanfragen von zwei physischen evdev-Geräten: einem USB-Numpad und einem RFID-Reader.

**Status:** korrekt

**Beleg:** `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`, Klasse `EvdevHardwareReader`, Docstring + `__init__` mit `numpad_path` und `rfid_path`

**Bewertung:** Der Konstruktor nimmt genau zwei Gerätepfade entgegen. Der Modulkommentar nennt explizit „Numpad (USB-Numpad)" und „RFID-Reader (HID-Keyboard)".

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 2:**
Das Modul bildet Eingaben auf eine `RawBookingRequest` ab.

**Status:** korrekt

**Beleg:** `evdev_reader.py`, Methode `read_next()`, Rückgabetyp `RawBookingRequest`

**Bewertung:** `read_next()` gibt explizit ein `RawBookingRequest`-Objekt zurück.

**Änderungsvorschlag:** Keiner erforderlich.

## Abschnitt: Unterstützte Hardwareannahmen

**Aussage 3:**
Der Code setzt Linux-Geräte unter `/dev/input/event*` voraus.

**Status:** korrekt

**Beleg:** Modulkommentar: „Linux, physische Geräte unter /dev/input/event*"

**Bewertung:** Direkt im Docstring des Moduls dokumentiert.

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 4:**
Der RFID-Reader muss seine UID als Tastatureingabe liefern: nur Hex-Zeichen `0-9` und `A-F`, Abschluss mit `Enter`.

**Status:** korrekt

**Beleg:** `_HEX_KEY_CHAR`, `_HEX_KEY_CHAR_SHIFT`, `_read_rfid_uid()`, Abbruch bei `KEY_ENTER`/`KEY_KPENTER`

**Bewertung:** Die Mapping-Dictionaries decken exakt `0–9` und `A–F` ab. Enter beendet den Lesevorgang.

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 5:**
Nicht-Hex-Zeichen werden ignoriert.

**Status:** korrekt

**Beleg:** `map_rfid_key()`: gibt `None` zurück für Nicht-Hex-Keycodes; in `_read_rfid_uid()` werden nur Werte `!= None` in `chars` aufgenommen

**Bewertung:** Vollständig durch Code belegt.

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 6:**
Reader mit Präfixen, Suffixen oder abweichender Kodierung werden nicht allgemein unterstützt. Für solche Geräte ist eine angepasste Reader-Policy erforderlich.

**Status:** korrekt

**Beleg:** Modulkommentar: „Präfixe, Suffixe oder abweichende Kodierungen erfordern eine angepasste Reader-Policy."

**Bewertung:** Wortgleich im Modulkommentar belegt.

**Änderungsvorschlag:** Keiner erforderlich.

## Abschnitt: Buchungstypen

**Aussage 7:**
Das Numpad ordnet Tasten `1`–`4` festen Buchungstypen zu: `1`/`KP1` → `COME`, `2`/`KP2` → `GO`, `3`/`KP3` → `BREAK_START`, `4`/`KP4` → `BREAK_END`.

**Status:** korrekt

**Beleg:** `_NUMPAD_TO_BOOKING_TYPE` in `evdev_reader.py`

**Bewertung:** Das Dictionary bildet `KEY_1`, `KEY_KP1` → `COME`; `KEY_2`, `KEY_KP2` → `GO`; `KEY_3`, `KEY_KP3` → `BREAK_START`; `KEY_4`, `KEY_KP4` → `BREAK_END` ab.

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 8:**
Der Wartezustand auf die Buchungstyp-Auswahl blockiert unbegrenzt. Das ist im Code ausdrücklich so vorgesehen.

**Status:** korrekt

**Beleg:** Modulkommentar: „`_read_booking_type()` blockiert unbegrenzt, bis eine gültige Taste gedrückt wird. Das ist beabsichtigt."

**Bewertung:** Direkt im Docstring des Moduls als Designentscheidung ausgewiesen.

**Änderungsvorschlag:** Keiner erforderlich.

## Abschnitt: RFID-Leseverhalten

**Aussage 9:**
Standard-Timeout: 5,0 Sekunden; das Timeout ist im Konstruktor konfigurierbar.

**Status:** korrekt

**Beleg:** `_RFID_READ_TIMEOUT: float = 5.0`; Konstruktorparameter `rfid_timeout: float = _RFID_READ_TIMEOUT`

**Bewertung:** Beide Teile der Aussage sind direkt im Code belegt.

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 10:**
Gelesen wird bis `Enter` oder bis zum Timeout.

**Status:** korrekt

**Beleg:** `_read_rfid_uid()`: Rückgabe bei `KEY_ENTER`/`KEY_KPENTER`; `HardwareTimeoutError` bei Überschreitung des Deadlines

**Bewertung:** Beide Abbruchbedingungen sind im Code implementiert.

**Änderungsvorschlag:** Keiner erforderlich. Ergänzend wäre `KEY_KPENTER` (Numpad-Enter) erwähnenswert, da der Code beide Varianten berücksichtigt.

---

**Aussage 11:**
`Shift` wird berücksichtigt, damit `A-F` auch in Großschreibung erfasst werden können.

**Status:** inkorrekt (unvollständig/irreführend)

**Beleg:** `_HEX_KEY_CHAR` und `_HEX_KEY_CHAR_SHIFT`; `map_rfid_key()`; `_read_rfid_uid()`: `shift_active`-Flag; `_HEX_KEY_CHAR` liefert Kleinbuchstaben (`c.lower()`), `_HEX_KEY_CHAR_SHIFT` liefert Großbuchstaben

**Bewertung:** Die Aussage ist in ihrer Kernaussage richtig (Shift wird ausgewertet), aber sie beschreibt den Effekt ungenau: Ohne Shift werden `A–F` als **Kleinbuchstaben** (`a–f`) gespeichert; mit Shift als **Großbuchstaben** (`A–F`). Das Handbuch impliziert, Shift sei nötig, um Großbuchstaben zu erfassen, verschweigt aber, dass ohne Shift ebenfalls Hex-Zeichen (dann klein) erfasst werden. Tatsächlich wird mit und ohne Shift gelesen – die Shift-Logik beeinflusst nur die Schreibweise.

**Änderungsvorschlag:** Präzisierung: „`Shift` wird berücksichtigt: Ohne Shift werden `a–f` (Kleinbuchstaben) erfasst, mit Shift `A–F` (Großbuchstaben). Nicht-Hex-Tasten werden in beiden Fällen verworfen."

---

**Aussage 12:**
Die gelesene UID wird vor der Weiterverarbeitung per `.strip()` bereinigt.

**Status:** korrekt

**Beleg:** `read_next()`: `raw_uid = self._read_rfid_uid(timeout=self._rfid_timeout).strip()`

**Bewertung:** `.strip()` wird explizit auf das Ergebnis von `_read_rfid_uid()` angewendet.

**Änderungsvorschlag:** Keiner erforderlich.

## Abschnitt: Zeitstempel und Ergebnisobjekt

**Aussage 13:**
Der Zeitstempel `occurred_at` wird erst nach vollständigem Abschluss der UID-Lesung gesetzt.

**Status:** korrekt

**Beleg:** `read_next()`: `occurred_at = datetime.now(timezone.utc)` steht nach `.strip()`, also nach `_read_rfid_uid()`

**Bewertung:** Der Codekommentar bestätigt dies ausdrücklich: „occurred_at erst nach vollständiger UID-Lesung".

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 14:**
`RawBookingRequest` enthält `booking_type`, `uid_hash` und `occurred_at`. Die UID wird nicht direkt gespeichert, sondern mit `hash_uid(...)` gehasht.

**Status:** korrekt

**Beleg:** `read_next()`: `RawBookingRequest(booking_type=booking_type, uid_hash=hash_uid(raw_uid), occurred_at=occurred_at)`

**Bewertung:** Alle drei Felder und der Hash-Aufruf sind direkt im Code belegt.

**Änderungsvorschlag:** Keiner erforderlich.

## Abschnitt: Fehlerverhalten

**Aussage 15:**
`EmptyUidError`, wenn der Reader eine leere UID liefert.

**Status:** korrekt

**Beleg:** `read_next()`: `if not raw_uid: raise EmptyUidError(...)`

**Bewertung:** Der Fehlerfall ist direkt implementiert.

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 16:**
`HardwareTimeoutError`, wenn innerhalb des Zeitlimits keine vollständige UID gelesen wird.

**Status:** korrekt

**Beleg:** `_read_rfid_uid()`: `raise HardwareTimeoutError(...)` bei `remaining <= 0` und bei leerem `select`-Ergebnis

**Bewertung:** Beide Timeout-Pfade im Code werfen `HardwareTimeoutError`.

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 17:**
`OSError`, wenn das Numpad-Gerät unerwartet geschlossen wird.

**Status:** korrekt

**Beleg:** `_read_booking_type()`: `raise OSError("Numpad-Gerät unerwartet geschlossen.")` – wird ausgelöst, wenn `read_loop()` endet, ohne dass eine gültige Taste erkannt wurde

**Bewertung:** Der Fehlerfall ist explizit im Code vorhanden.

**Änderungsvorschlag:** Keiner erforderlich.

## Abschnitt: Gerätezugriff und Exklusivität

**Aussage 18:**
Beide Geräte werden im Konstruktor als `InputDevice` geöffnet.

**Status:** korrekt

**Beleg:** `__init__`: `self._numpad = InputDevice(numpad_path)`, `self._rfid = InputDevice(rfid_path)`

**Bewertung:** Direkt im Konstruktor belegt.

**Änderungsvorschlag:** Keiner erforderlich.

---

**Aussage 19:**
Standardmäßig wird `grab=True` verwendet. Dadurch werden Numpad und RFID-Reader exklusiv für diesen Prozess reserviert.

**Status:** inkorrekt (präzisierungsbedürftig)

**Beleg:** `__init__`: Parameter `grab: bool = True`; `if grab: self._numpad.grab(); self._rfid.grab()`

**Bewertung:** Der Standardwert `grab=True` ist korrekt. Die Aussage, dass `grab=True` die Geräte „standardmäßig" exklusiv reserviert, ist inhaltlich richtig. Jedoch verschweigt das Handbuch, dass `grab` ein explizit konfigurierbarer Parameter ist (`grab=False` ist für „Diagnose/Test" laut Docstring vorgesehen). Das Handbuch stellt `grab=True` als nicht änderbares Verhalten dar, während der Code es als Parameter anbietet.

**Änderungsvorschlag:** Ergänzung: „Der `grab`-Parameter ist konfigurierbar (Standard: `True`). Für Diagnosezwecke oder Tests kann `grab=False` übergeben werden."

## Abschnitt: Lebenszyklus

**Aussage 20:**
Die aufrufende Schicht ist für `close()` verantwortlich.

**Status:** korrekt

**Beleg:** Modulkommentar: „Lebenszyklus: Die aufrufende Schicht ist für close() verantwortlich."

**Bewertung:** Wortgleich im Docstring des Moduls festgehalten.

**Änderungsvorschlag:** Keiner erforderlich. Ergänzend empfiehlt der Modulkommentar „try/finally oder einen Context Manager" – dies könnte im Handbuch erwähnt werden, ist aber keine zwingende Korrektur.

---

**Aussage 21:**
`close()` versucht bei beiden Geräten `ungrab()` und `close()`; Fehler werden dabei bewusst unterdrückt.

**Status:** korrekt

**Beleg:** `close()`: `for dev in (self._numpad, self._rfid): try: dev.ungrab() except Exception: pass; try: dev.close() except Exception: pass`

**Bewertung:** Struktur und Fehlerunterdrückung sind exakt so implementiert.

**Änderungsvorschlag:** Keiner erforderlich.

## Abschnitt: Selbstkritische Befunde

**Aussage 22:**
Der Konstruktor räumt nicht sichtbar auf, wenn das erste Gerät erfolgreich geöffnet wurde und das zweite Öffnen danach fehlschlägt.

**Status:** korrekt

**Beleg:** `__init__`: `self._numpad = InputDevice(numpad_path)` – kein `try/except` um `InputDevice(rfid_path)`

**Bewertung:** Im Konstruktor gibt es keinen Cleanup-Pfad, wenn `InputDevice(rfid_path)` nach erfolgreichem `InputDevice(numpad_path)` eine Exception wirft.

**Änderungsvorschlag:** Keiner erforderlich (Befund korrekt festgehalten).

---

**Aussage 23:**
Das Modul beschreibt den tatsächlichen Hardwarezugriff, aber nicht die betriebliche Erkennung oder Auswahl der Geräte.

**Status:** korrekt

**Beleg:** Modulkommentar: „Gerätepfade werden übergeben (z. B. aus config oder Autodetect)" – die Auswahl selbst liegt außerhalb dieses Moduls

**Bewertung:** Der Konstruktor nimmt Pfade als Parameter entgegen; Erkennung/Auswahl ist nicht Teil von `evdev_reader.py`.

**Änderungsvorschlag:** Keiner erforderlich.

## Abschnitt: Nicht aus diesem Modul ableitbar

**Aussage 24:**
Konkrete Hersteller-/Modellbezeichnungen, feste Event-Nummern, udev-Regeln, Reconnect-Strategien und Rechtekonzepte lassen sich aus `evdev_reader.py` nicht belastbar belegen.

**Status:** korrekt

**Beleg:** Modulkommentar: erwähnt keine konkreten Gerätepfade, USB-IDs oder udev-Regeln; `__init__` erwartet Pfade als Parameter

**Bewertung:** Alle genannten Punkte fehlen im Quelltext, was die Aussage des Handbuchs bestätigt.

**Änderungsvorschlag:** Keiner erforderlich.

## Zusammenfassung der Änderungsbedarfe

| Nr. | Aussage | Status | Priorität |
|-----|---------|--------|-----------|
| 11 | Shift-Beschreibung (Groß-/Kleinschreibung) | inkorrekt (unvollständig) | mittel |
| 19 | `grab=True` als konfigurierbarer Parameter | inkorrekt (unvollständig) | niedrig |
| 10 | `KEY_KPENTER` nicht erwähnt | korrekt (Ergänzungshinweis) | niedrig |
| 20 | `try/finally`-Empfehlung nicht erwähnt | korrekt (Ergänzungshinweis) | niedrig |