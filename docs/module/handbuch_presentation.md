# Handbuch `arbeitszeit` – Präsentationsschicht (`src/arbeitszeit/presentation`)

**Kapitel:** 3
**Version:** 1.0
**Stand:** Juli 2026
**Quelldatei:** `docs/module/handbuch_presentation.md`

## Überblick und Aufbau

Die Präsentationsschicht ist die äußerste Schale des Systems und bildet
die einzige Schnittstelle zwischen Benutzer (oder Administrator) und der
darunterliegenden Fach- und Anwendungslogik. Sie enthält keine
Geschäftslogik, sondern übersetzt ausschließlich Benutzereingaben in
Kommandos der Anwendungsschicht und gibt Ergebnisse als lesbare Texte
aus. Das Paket gliedert sich in zwei eigenständige Untermodule:

- `presentation/terminal_ui/` – operativer Buchungsbetrieb (Endlosschleife, RFID + Numpad)
- `presentation/admin_cli/` – administrative Verwaltung (Kommandozeile, rollenbasiert)

---

## Terminal-UI (`terminal_ui/`)

### Zweck und Betriebsmodus

Die Terminal-UI ist der im laufenden Praxisbetrieb aktive Prozess. Sie
startet beim Systemstart als Endlosschleife und wartet kontinuierlich auf
Hardware-Eingaben: zuerst Auswahl der Buchungsart über das Numpad, dann
RFID-Kartenscan. Der Prozess reagiert auf `SIGTERM` und `SIGINT`
(Strg+C) mit einem sauberen Graceful Shutdown.

### Startparameter

Die Terminal-UI wird mit vier Pflichtargumenten gestartet:

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db /pfad/zur/datenbank.db \
  --numpad /dev/input/eventX \
  --rfid /dev/input/eventY \
  --terminal-id 1
```

### Startverhalten und Systemcheck

Vor dem Eintritt in die Buchungsschleife führt `run()` automatisch einen
Systemcheck durch. Schlägt der Check fehl, wird eine
Desktop-Benachrichtigung ausgelöst (`notify(…, urgency="critical")`),
aber der Buchungsbetrieb wird **nicht** abgebrochen — die Praxis soll
arbeitsfähig bleiben. Fehlerdetails werden in der Tabelle
`system_events` gespeichert.

### Buchungszyklus (`booking_loop.py`)

Jeder Buchungszyklus läuft in drei Schritten ab:

1. **Numpad-Eingabe:** Der Mitarbeiter wählt die Buchungsart (Kommen,
   Gehen, Pause-Start, Pause-Ende) über das USB-Numpad.
2. **RFID-Scan:** Das System wartet auf den Kartenscan. Das Timeout ist
   konfigurierbar über `booking.grace_seconds_after_numpad_select` in
   `system_config` (Standardwert: 5 Sekunden).
3. **Buchungsverarbeitung:** Das Geräteereignis (`RFID_SCAN`) wird
   **vor** dem eigentlichen `BookUseCase`-Aufruf in `device_events`
   gespeichert — absichtlich, damit auch fachlich gescheiterte Buchungen
   (z. B. unbekannte Karte) lückenlos protokolliert bleiben.

### Feedback-Ausgabe

Nach jeder Buchung gibt das Terminal eine einzeilige Rückmeldung aus.

| Status | Ausgabe |
| --- | --- |
| `OPEN` / `OK` | `Buchung erfasst.` |
| `WARN` | `Buchung erfasst — Hinweis: Regelzeitabweichung festgestellt.` |
| `NEEDS_REVIEW` | `Buchung erfasst — Prüfpflicht: Manuelle Überprüfung erforderlich.` |

### Domänenfehler-Behandlung

Bekannte Domänenfehler werden in menschenlesbare Meldungen übersetzt und
ausgegeben, ohne den Prozess zu beenden:

| Fehlerklasse | Anzeige |
| --- | --- |
| `UnknownCardError` | `Karte nicht erkannt.` |
| `InactiveCardError` | `Karte deaktiviert.` |
| `InactiveEmployeeError` | `Mitarbeiter inaktiv.` |
| `InvalidBookingSequenceError` | `Ungültige Buchungsreihenfolge.` |
| `OpenPhaseConflictError` | `Offene Phase — bitte zuerst abschließen.` |

Unerwartete Ausnahmen werden in `system_events` protokolliert; der
Betrieb läuft weiter.

---

## Admin-CLI (`admin_cli/`)

### Zweck

Die Admin-CLI ist das Verwaltungswerkzeug für Administratoren und
technisches Personal. Sie wird als `admin`-Programm gestartet, erfordert
immer die Datenbankdatei (`--db`) und eine Benutzer-ID (`--user-id`
oder Umgebungsvariable `ADMIN_USER_ID`), und verteilt alle Aufrufe über
eine zentrale Dispatch-Tabelle an spezialisierte Handler-Module.

### Grundaufruf

```bash
admin --db /pfad/zur/datenbank.db --user-id 1 <domain> <subcommand> [optionen]
```

Alternativ zur `--user-id`-Option kann die Umgebungsvariable
`ADMIN_USER_ID` gesetzt werden. Die einzige Ausnahme ist
`users bootstrap` — dieser Befehl benötigt keine Benutzer-ID, da noch
kein Admin existiert.

### Rollenmodell

Alle schreibenden Operationen prüfen die Rolle des aufrufenden Benutzers
direkt gegen die Tabelle `user_accounts`. Es gibt drei Rollen:

| Rolle | Erlaubte Bereiche |
| --- | --- |
| `ADMIN` | Alle Operationen (Lesen + Schreiben) |
| `REVIEWER` | Berichte, Buchungsüberprüfung, Nachträge genehmigen/ablehnen |
| `TECH` | Systemcheck, Backup |

Lesende Operationen (z. B. `employees list`, `users list`) sind ohne
Rolleneinschränkung nutzbar.

---

## Domain: `employees` und `cards`

### Mitarbeiterverwaltung (`employees.py`)

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `employees list` | Alle Mitarbeiter tabellarisch auflisten | keine |
| `employees add --personnel-no … --first-name … --last-name …` | Mitarbeiter anlegen | `ADMIN` |
| `employees deactivate <id>` | Mitarbeiter deaktivieren | `ADMIN` |

### Kartenverwaltung

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `cards assign --employee-id … --uid-hash …` | Neue RFID-Karte einem Mitarbeiter zuweisen | `ADMIN` |
| `cards replace --old-card-id … --uid-hash …` | Verlorene/defekte Karte ersetzen (alte Karte erhält Status `REPLACED`) | `ADMIN` |
| `cards deactivate <id>` | Karte auf Status `INACTIVE` setzen | `ADMIN` |

Jede schreibende Operation wird mit einem `_audit(…)`-Eintrag in
`audit_log` protokolliert. Verwendete Ereignistypen:
`EMPLOYEE_CREATED`, `EMPLOYEE_DEACTIVATED`, `CARD_ASSIGNED`,
`CARD_REPLACED`, `CARD_DEACTIVATED`.

---

## Domain: `bookings`

Buchungskorrekturen und Nachträge laufen vollständig über Use Cases der
Anwendungsschicht — die Rollenprüfung erfolgt dort, die CLI übernimmt
nur Fehlerformatierung und Ausgabe.

| Befehl | Beschreibung |
| --- | --- |
| `bookings correct --booking-id … --type … --at … --reason …` | Bestehende Buchung korrigieren; erzeugt einen neuen Korrektur-Datensatz und setzt die alte Buchung auf `CORRECTED` |
| `bookings supplement --employee-id … --type … --at … --reason …` | Nachträgliche Buchung erfassen; erzeugt automatisch einen Prüffall (`review_case`) |
| `bookings approve-supplement --supplement-id …` | Nachtrag freigeben → Buchung wird wirksam |
| `bookings reject-supplement --supplement-id … --reason …` | Nachtrag ablehnen |

Das `--at`-Argument erwartet ISO-8601-Format (z. B.
`2026-07-01T08:00:00`). Fehlt die Zeitzone, wird UTC angenommen.

---

## Domain: `schedule`

Die Regelarbeitszeit wird versioniert gespeichert; jede Änderung erzeugt
eine neue Version und schließt die Vorgängerversion.

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `schedule set --weekday 1-7 --start HH:MM --end HH:MM --from YYYY-MM-DD` | Globale Regelarbeitszeit setzen | `ADMIN` |
| `schedule show` | Alle aktiven Versionen anzeigen (global + mitarbeiterspezifisch) | `ADMIN`, `REVIEWER` |

---

## Domain: `reports`

Alle Report-Befehle erfordern `ADMIN`- oder `REVIEWER`-Rolle. Das
Export-Verzeichnis wird aus `system_config` (Schlüssel
`export.export_dir`) gelesen.

### Export-Befehle

| Befehl | Beschreibung |
| --- | --- |
| `reports export-csv --from … --to … [--employee-id …]` | Zwei CSV-Dateien: Detailbuchungen + verdichtete Übersicht |
| `reports export-pdf-day YYYY-MM-DD` | Tagesbericht als PDF |
| `reports export-pdf-week <Jahr> <KW>` | Wochenbericht (ISO-Woche) als PDF |
| `reports export-pdf-month <Jahr> <Monat>` | Monatsbericht als PDF |
| `reports export-pdf-employee --employee-id … --from … --to …` | Mitarbeiterbericht als PDF |

### Pflichtauswertungen

| Befehl | Beschreibung |
| --- | --- |
| `reports open-bookings [--from … --to …] [--employee-id …]` | Buchungen mit Status `OPEN` |
| `reports warn-cases --from … --to … [--employee-id …]` | Buchungen mit Status `WARN` oder `NEEDS_REVIEW` |
| `reports corrections --from … --to … [--employee-id …]` | Alle Korrekturen im Zeitraum |
| `reports supplements --from … --to … [--employee-id …]` | Alle Nachträge im Zeitraum |
| `reports open-review-cases [--from … --to …] [--employee-id …]` | Offene Prüffälle |

---

## Domain: `system`

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `system check` | Systemcheck auslösen; gibt Detailstatus aller Prüfpunkte aus; Exitcode 0 = OK, 1 = Fehler | `ADMIN`, `TECH` |
| `system backup` | Manuelles Backup der SQLite-Datenbank auslösen; bei aktivierter NAS-Synchronisation (`backup.nas_enabled`) wird das Backup auch auf den NAS-Pfad kopiert | `ADMIN`, `TECH` |

Der Backup-Dienst liest Zielverzeichnis und NAS-Pfad aus `system_config`.
Schlägt die NAS-Synchronisation fehl, wird nur eine Warnung ausgegeben —
der Prozess endet nicht mit Fehler.

---

## Domain: `users`

Passwörter werden mit PBKDF2-HMAC-SHA256 und 260.000 Iterationen gehasht
(DSGVO Art. 32). Das Klartextpasswort wird nach der Ausgabe nirgends
gespeichert.

| Befehl | Beschreibung | Rolle |
| --- | --- | --- |
| `users bootstrap --username … [--password …]` | Erstes Administratorkonto anlegen (nur wenn noch kein aktiver Admin existiert) | — |
| `users add --username … --role … [--employee-id …] [--password …]` | Neues Benutzerkonto anlegen | `ADMIN` |
| `users list` | Alle Konten tabellarisch auflisten | keine |
| `users deactivate --user-id …` | Benutzerkonto deaktivieren | `ADMIN` |
| `users reactivate --user-id …` | Benutzerkonto reaktivieren | `ADMIN` |
| `users change-role --user-id … --role …` | Rolle eines Kontos ändern | `ADMIN` |

Wird `--password` weggelassen, generiert das System ein sicheres
zufälliges Passwort und zeigt es **einmalig** auf der Konsole an.

---

## Zeitraum-Hilfsfunktionen (`_intervals.py`)

Alle Datums-/Zeitraumberechnungen in der Admin-CLI verwenden ausschließlich
die drei Funktionen aus
`src/arbeitszeit/presentation/admin_cli/_intervals.py`. Eigene
Ad-hoc-Konstruktionen aus Benutzereingaben sind verboten, um
UTC-Normalisierung und halboffene Intervalle `[from_dt, to_dt)`
sicherzustellen.

| Funktion | Beschreibung |
| --- | --- |
| `day_interval(day)` | `[day 00:00 UTC, next_day 00:00 UTC)` |
| `week_interval(year, week)` | ISO-Woche: Montag 00:00 UTC bis Montag+7 00:00 UTC |
| `month_interval(year, month)` | Erster bis (exklusiv) erster des Folgemonats, UTC |
