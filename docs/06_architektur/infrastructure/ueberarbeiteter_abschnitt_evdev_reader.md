# evdev_reader.py

## Zweck

`evdev_reader.py` liest Buchungsanfragen vom physischen RFID-Reader.

Das Modul bildet RFID-Scans auf eine `RawBookingRequest` ab.

## Unterstützte Hardwareannahmen

Der Code setzt Linux-Geräte unter `/dev/input/event*` voraus.

Der RFID-Reader muss seine UID als Tastatureingabe liefern:

- nur Hex-Zeichen `0-9` und `A-F`
- Abschluss der UID mit `Enter`

Nicht-Hex-Zeichen werden ignoriert.

Reader mit Präfixen, Suffixen oder abweichender Kodierung werden durch dieses
Modul nicht allgemein unterstützt. Für solche Geräte ist eine angepasste
Reader-Policy erforderlich.

## RFID-Leseverhalten

`read_next()` wartet blockierend auf den nächsten RFID-Scan ohne fachliches
Zeitlimit.

Dabei gilt:

- Intern wiederholt `_read_rfid_uid()` kurze 1-Sekunden-Poll-Intervalle
  (`select()`), damit SIGTERM nach spätestens diesem Intervall wirksam werden
  kann.
- `HardwareTimeoutError` wird von `read_next()` abgefangen und intern
  behandelt; er wird **nicht** nach außen weitergegeben.
- `Shift` wird berücksichtigt: Mit Shift werden `A-F` in Großschreibung
  erfasst, ohne Shift `a-f` in Kleinschreibung.
- Nicht-Hex-Tasten werden verworfen.

Die gelesene UID wird vor der Weiterverarbeitung per `.strip()` bereinigt.

## Zeitstempel und Ergebnisobjekt

Der Zeitstempel `occurred_at` wird erst nach vollständigem Abschluss der
UID-Lesung gesetzt.

Aus erfolgreicher Eingabe entsteht eine `RawBookingRequest` mit:

- `uid_hash`
- `occurred_at`

Die UID selbst wird nicht direkt gespeichert, sondern vor Übergabe mit
`hash_uid(...)` gehasht. Der Buchungstyp ist **nicht** Teil von
`RawBookingRequest`; er wird in der Applikationsschicht positionsbasiert
abgeleitet (`derive_booking_type` in `book_time.py`).

## Fehlerverhalten

- `EmptyUidError`: Reader liefert nach dem Lesen eine leere UID.
- `HardwareTimeoutError`: intern nach jedem 1-Sekunden-Poll-Intervall —
  wird von `read_next()` abgefangen und führt zu einem neuen Leseversuch.
  Kein externer Fehler, sondern ein internes Steuerungssignal.

## Gerätezugriff und Exklusivität

Das RFID-Gerät wird im Konstruktor als `InputDevice` geöffnet.

Der `grab`-Parameter ist konfigurierbar (Standard: `True`). Bei `grab=True`
wird der RFID-Reader exklusiv für diesen Prozess reserviert. Für
Diagnosezwecke oder Tests kann `grab=False` übergeben werden.

Das ist für einen Kiosk- oder Terminalbetrieb sinnvoll, weil dieselben
Eingaben nicht gleichzeitig an andere Prozesse weitergereicht werden.

## Doppel-Scan-Schutz

`EvdevHardwareReader` implementiert keinen Doppel-Scan-Schutz. Diese
Verantwortung liegt bei `DebouncedHardwareReader` (`debounce.py`), der
`EvdevHardwareReader` wrapt und Scans derselben UID innerhalb von 3 Sekunden
verwirft.

## Lebenszyklus

Die aufrufende Schicht ist für `close()` verantwortlich.

`close()` versucht:

- `ungrab()`
- `close()`

Fehler beim Freigeben oder Schließen werden als Warnings geloggt, aber nicht
weitergeworfen.

## Selbstkritische Befunde

Der Quelltext ist insgesamt klar und zielgerichtet, hat aber einige Grenzen
und Prüfpunkte:

- Konkrete Angaben zu USB-IDs, udev-Regeln, Event-Pfaden oder
  Wiederverbindungslogik stehen nicht in diesem Modul.
- Das Modul beschreibt den tatsächlichen Hardwarezugriff, aber nicht die
  betriebliche Erkennung oder Auswahl der Geräte.

Diese Punkte sollten in ergänzender Betriebs- oder Installationsdokumentation
separat festgehalten werden.

## Nicht aus diesem Modul ableitbar

Folgende Aussagen lassen sich aus `evdev_reader.py` allein nicht belastbar
belegen:

- konkrete Hersteller- oder Modellbezeichnungen der Geräte
- feste `/dev/input/eventX`-Nummern
- konkrete udev-Regeln
- automatische Reconnect-Strategien
- Rechte- oder Rollenkonzepte außerhalb des Hardwarezugriffs

## Quellen

- `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`
