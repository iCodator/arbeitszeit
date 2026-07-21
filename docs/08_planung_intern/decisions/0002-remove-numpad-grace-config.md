# 0002 — Entfernung von `booking.grace_seconds_after_numpad_select`

## Status

Angenommen

## Kontext

Der Konfigurationsschlüssel `booking.grace_seconds_after_numpad_select` wurde
in Migration `0002_seed_defaults.sql` mit dem Defaultwert `30` (Sekunden)
eingetragen. Er steuerte ausschließlich den Timeout zwischen einer NumPad-Auswahl
(Buchungstyp-Eingabe) und dem anschließenden RFID-Scan im bisherigen
Buchungsmodell: Nach der NumPad-Auswahl wartete `EvdevHardwareReader._read_rfid_uid()`
maximal `grace_seconds` Sekunden auf die Karten-UID, bevor sie mit einem
`HardwareTimeoutError` abbrach.

Der Schlüssel wurde an drei Stellen im produktiven Code verwendet:

- `infrastructure/system_check.py` — Pflichtprüfung beim Systemcheck
- `presentation/terminal_ui/main.py` — Lesezugriff aus `system_config`,
  Übergabe als `rfid_timeout`-Parameter an `EvdevHardwareReader`
- `infrastructure/hardware/evdev_reader.py` — Verwendung als Timeout in
  `read_next()` → `_read_rfid_uid()`

Diese Feststellung basiert auf der Faktenprüfung F6 in
`docs/08_planung_intern/analyse_F4_F1_F2_F6_F7.md`.

Im Zuge der RFID-only-Umstellung entfällt die NumPad-Eingabe vollständig.
Damit entfällt auch der fachliche Anlass für diesen Konfigurationsschlüssel.

## Entscheidung

Der Konfigurationsschlüssel `booking.grace_seconds_after_numpad_select` wird
ersatzlos entfernt. Es erfolgt keine Umbenennung, keine Umwidmung und keine
Weiterverwendung unter einem anderen Namen.

Die Entfernung geschieht durch:

- Migration `0007_remove_numpad_grace_config.sql`: löscht den Datensatz aus der
  `system_config`-Tabelle aller bestehenden Datenbanken
- Entfernung aus `_REQUIRED_CONFIG_KEYS` in `system_check.py`
- Entfernung des Lesezugriffs und der `rfid_timeout`-Übergabe in `main.py`
- Entfernung des `rfid_timeout`-Konstruktorparameters in `evdev_reader.py`

## Erwogene Alternativen

**Umbenennung und Weiterverwendung mit neuer Bedeutung** — verworfen, weil
der einzige Zweck des Schlüssels (Timeout zwischen NumPad-Auswahl und RFID-Scan)
im RFID-only-Modell vollständig entfällt. Eine Umbenennung ohne neuen fachlichen
Zweck erzeugt technische Schulden: der Schlüsselname hätte keine Entsprechung
mehr im tatsächlichen Systemverhalten.

**Beibehaltung als ungenutzter Konfigurationswert** — verworfen, weil ein
Konfigurationsschlüssel, der im Code nicht mehr gelesen und nicht mehr angewendet
wird, keine Funktion mehr hat. Seine Präsenz im Schema und im Systemcheck würde
fälschlicherweise suggerieren, er beeinflusse das Systemverhalten.

## Begründung

1. **Zweck entfällt vollständig:** Der Schlüssel steuerte ausschließlich das
   Timing zwischen NumPad-Auswahl und RFID-Scan. Da NumPad-Eingaben im RFID-only-
   Modell nicht mehr existieren, gibt es keine Situation, in der dieser Timeout
   noch fachlich relevant wäre.

2. **Umbenennung ohne neuen Zweck erzeugt technische Schulden:** Ein unter
   anderem Namen fortgeführter Schlüssel hätte keinen definierten Verwendungsfall.
   Solche Scheinwerte erschweren spätere Audits und Systemchecks.

3. **Kein erkennbarer Ersatzbedarf:** Falls künftig ein Scan-Timeout für den
   reinen RFID-Betrieb benötigt wird (z. B. gegen Device-Hänger), ist das ein
   eigenständig zu begründender und zu benennender Konfigurationsschlüssel — keine
   Fortführung dieses Schlüssels.

## Konsequenzen

Betroffene Dateien:

| Datei | Art der Änderung |
| --- | --- |
| `migrations/0007_remove_numpad_grace_config.sql` | Neue Migration: DELETE aus `system_config` |
| `src/arbeitszeit/infrastructure/system_check.py` | Entfernung aus `_REQUIRED_CONFIG_KEYS` |
| `src/arbeitszeit/presentation/terminal_ui/main.py` | Entfernung grace\_conn-Block und `rfid_timeout`-Übergabe |
| `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` | Entfernung `rfid_timeout`-Parameter aus `__init__` |
| `tests/test_migrations.py` | Anpassung der erwarteten Versionsliste und Seed-Anzahl |
| `tests/integration/test_hardware_evdev.py` | Entfernung von `reader._rfid_timeout = 5.0` |
| `tests/integration/test_terminal_ui_main.py` | Entfernung `rfid_timeout`-Assertion |

Falls künftig ein neuer, andersartiger Scan-Timeout benötigt wird, ist dieser
als eigenständiger, fachlich klar benannter Konfigurationsschlüssel zu definieren
und nicht als Fortführung von `booking.grace_seconds_after_numpad_select`.

**Offene Folgefrage:** `EvdevHardwareReader._read_rfid_uid()` verwendet intern
weiterhin den hardcodierten Konstantenwert `_RFID_READ_TIMEOUT = 5.0` (Sekunden).
Der bisher konfigurierte Produktivwert betrug 30 Sekunden. Ob 5,0 Sekunden für
den RFID-only-Betrieb angemessen sind oder ob dieser Wert angepasst werden soll,
ist eine eigenständige fachliche Entscheidung und nicht Gegenstand dieser
Änderung.
