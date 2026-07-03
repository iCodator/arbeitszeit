# evdev_reader.py

## Zweck

`evdev_reader.py` liest Buchungsanfragen von zwei physischen evdev-Geräten:

- einem USB-Numpad zur Auswahl des Buchungstyps
- einem RFID-Reader, der sich als HID-Tastatur meldet

Das Modul bildet diese Eingaben auf eine `RawBookingRequest` ab.

## Unterstützte Hardwareannahmen

Der Code setzt Linux-Geräte unter `/dev/input/event*` voraus.

Der RFID-Reader muss seine UID als Tastatureingabe liefern:

- nur Hex-Zeichen `0-9` und `A-F`
- Abschluss der UID mit `Enter`

Nicht-Hex-Zeichen werden ignoriert.

Reader mit Präfixen, Suffixen oder abweichender Kodierung werden durch dieses
Modul nicht allgemein unterstützt. Für solche Geräte ist eine angepasste
Reader-Policy erforderlich.

## Buchungstypen

Das Numpad ordnet die Tasten `1` bis `4` festen Buchungstypen zu:

- `1` oder `KP1` -> `COME`
- `2` oder `KP2` -> `GO`
- `3` oder `KP3` -> `BREAK_START`
- `4` oder `KP4` -> `BREAK_END`

Der Wartezustand auf die Buchungstyp-Auswahl blockiert unbegrenzt. Das ist im
Code ausdrücklich so vorgesehen.

## RFID-Leseverhalten

Nach Auswahl des Buchungstyps startet das Modul einen RFID-Lesevorgang.

Dabei gilt:

- Standard-Timeout: 5,0 Sekunden
- Das Timeout ist im Konstruktor konfigurierbar.
- Gelesen wird bis `Enter` oder bis zum Timeout.
- `Shift` wird berücksichtigt: Ohne Shift werden `a-f` (Kleinbuchstaben)
  erfasst, mit Shift `A-F` (Großbuchstaben).
- Nicht-Hex-Tasten werden in beiden Fällen verworfen.

Die gelesene UID wird vor der Weiterverarbeitung per `.strip()` bereinigt.

## Zeitstempel und Ergebnisobjekt

Der Zeitstempel `occurred_at` wird erst nach vollständigem Abschluss der
UID-Lesung gesetzt.

Damit beschreibt der Zeitstempel den Abschluss der gesamten
Buchungsanforderung und nicht schon den Zwischenstand nach der Auswahl des
Buchungstyps.

Aus erfolgreicher Eingabe entsteht eine `RawBookingRequest` mit:

- `booking_type`
- `uid_hash`
- `occurred_at`

Die UID selbst wird dabei nicht direkt gespeichert, sondern vor Übergabe mit
`hash_uid(...)` gehasht.

## Fehlerverhalten

Im Code sind insbesondere folgende Fehlerfälle vorgesehen:

- `EmptyUidError`, wenn der Reader nach dem Lesen eine leere UID liefert
- `HardwareTimeoutError`, wenn innerhalb des Zeitlimits keine vollständige UID
  gelesen wird
- `OSError`, wenn das Numpad-Gerät unerwartet geschlossen wird

Diese Fehler sind fachlich sinnvoll getrennt und können von der aufrufenden
Schicht unterschiedlich behandelt werden.

## Gerätezugriff und Exklusivität

Beide Geräte werden im Konstruktor als `InputDevice` geöffnet.

Der `grab`-Parameter ist konfigurierbar (Standard: `True`). Bei `grab=True`
werden Numpad und RFID-Reader exklusiv für diesen Prozess reserviert. Für
Diagnosezwecke oder Tests kann `grab=False` übergeben werden.

Das ist für einen Kiosk- oder Terminalbetrieb sinnvoll, weil dieselben
Eingaben nicht gleichzeitig an andere Prozesse weitergereicht werden.

## Lebenszyklus

Die aufrufende Schicht ist für `close()` verantwortlich.

`close()` versucht bei beiden Geräten jeweils:

- `ungrab()`
- `close()`

Fehler beim Freigeben oder Schließen werden dabei bewusst unterdrückt, damit
ein Problem an einem Gerät das Aufräumen des anderen Geräts nicht verhindert.

## Selbstkritische Befunde

Der Quelltext ist insgesamt klar und zielgerichtet, hat aber einige Grenzen und
Prüfpunkte:

- Der Konstruktor räumt nicht sichtbar auf, wenn das erste Gerät erfolgreich
  geöffnet wurde und das zweite Öffnen danach fehlschlägt.
- Die Unterstützung ist bewusst auf HID-Reader mit Hex-UID und `Enter`
  zugeschnitten.
- Konkrete Angaben zu USB-IDs, udev-Regeln, Event-Pfaden oder
  Wiederverbindungslogik stehen nicht in diesem Modul.
- Das Modul beschreibt den tatsächlichen Hardwarezugriff, aber nicht die
  betriebliche Erkennung oder Auswahl der Geräte.

Diese Punkte sollten in ergänzender Betriebs- oder
Installationsdokumentation separat festgehalten werden.

## Nicht aus diesem Modul ableitbar

Folgende Aussagen lassen sich aus `evdev_reader.py` allein nicht belastbar
belegen und sollten daher nicht in diese Dateidokumentation hineinbehauptet
werden:

- konkrete Hersteller- oder Modellbezeichnungen der Geräte
- feste `/dev/input/eventX`-Nummern
- konkrete udev-Regeln
- automatische Reconnect-Strategien
- Rechte- oder Rollenkonzepte außerhalb des Hardwarezugriffs

## Quellen

- `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`
