# Planung Phase 5 – Präsentation

Stand: 2026-05-24. Basiert auf Pflichtenheft v3 und Regelwerk v3.
Phase 5 noch nicht begonnen.

Voraussetzung: Phase 4/Schritt 9 (system_check.py) muss vor Schritt 4
dieser Phase abgeschlossen sein.

---

## Ausgangslage nach Phase 4

Vollständig implementiert:

```
src/arbeitszeit/
├── domain/            Phase 2 ✓
├── application/       Phase 3 ✓  (6 Use Cases, 107 Tests)
└── infrastructure/
    ├── db/            Phase 4 ✓  (10 Repos, UoW, Migrationen)
    ├── hardware/      Phase 4 ✓  (EvdevHardwareReader, Simulator)
    ├── backup/        Phase 4 ✓  (SQLiteBackupService, 19 e2e-Tests)
    └── export/        Phase 4 ✓  (report_queries, CSV, PDF)
```

Offen aus Phase 4:

- `infrastructure/system_check.py` (Pflichtenheft v3 §7.10) — muss vor
  Phase-5-Schritt 4 fertiggestellt sein
- Systemzeitprotokollierung (Pflichtenheft v3 §9.3 / Regelwerk v3 §21)

325 Tests grün (alle Ebenen).


---

## Architekturentscheidungen für Phase 5


### Trennung Terminal-UI und Admin-CLI

Zwei getrennte Einstiegspunkte:

- `presentation/terminal_ui/` — operativer Buchungsbetrieb, läuft dauerhaft
  auf dem Terminal-Rechner, kein Benutzerwechsel während Betrieb
- `presentation/admin_cli/` — administrative Verwaltung, separater Aufruf
  mit Rollenprüfung per Kommandozeile

Keine gemeinsame UI-Abstraktion vorab. Erst wenn echter Querschnittscode
entsteht, gemeinsamen Code in ein Modul extrahieren.


### Buchungsart kommt ausschließlich vom USB-Numpad

(Pflichtenheft v3 §6 / Regelwerk v3 §3)

Die Buchungsart (COME, GO, BREAK_START, BREAK_END) wird durch Tastendruck
am USB-Numpad ausgewählt, bevor die RFID-Karte gelesen wird.
Kein System-Input, keine Tastatureingabe, keine programmatische Vorgabe.

Konsequenz für Terminal-UI: erst Numpad-Auswahl abwarten, dann RFID-Scan
auslösen. Beides über `HardwareReader`-Protocol aus infrastructure/hardware/.


### Admin-CLI: Rollenprüfung über UserAccount

Alle schreibenden Admin-Operationen prüfen die Rolle des ausführenden Users
(Pflichtenheft v3 §5 / Regelwerk v3 §16). Kein Bypass über CLI-Flags.

Rollentrennung:

| Operation                     | Erlaubte Rollen    |
|-------------------------------|--------------------|
| Buchung via Terminal          | — (via RFID-Karte) |
| Mitarbeiter/Karte verwalten   | ADMIN              |
| Korrektur anlegen             | ADMIN, REVIEWER    |
| Nachtrag anlegen              | ADMIN, REVIEWER    |
| Nachtrag freigeben/ablehnen   | ADMIN, REVIEWER    |
| Regelarbeitszeit ändern       | ADMIN              |
| Export/Bericht erzeugen       | ADMIN, REVIEWER    |
| Systemcheck auslösen          | ADMIN, TECH        |


### Pflichtauswertungen: Anzeige über report_queries.py

Alle Pflichtauswertungen (Pflichtenheft v3 §7.12) nutzen ausschließlich
die Funktionen aus `report_queries.py` — keine neuen Ad-hoc-Queries in der
Präsentationsschicht.


### Regelarbeitszeit-Anzeige in Admin-CLI

`WorkScheduleRepository.list_versions(scope_employee_id=None)` liefert nur GLOBAL-Scope-Versionen,
nicht alle Versionen aller Mitarbeiter. Für eine vollständige Übersicht im Admin-CLI sind zwei
Aufrufe nötig: einmal ohne `scope_employee_id` (GLOBAL) und einmal pro Mitarbeiter mit dessen ID.
`schedule.py` muss das in der Anzeige kombinieren.

EMPLOYEE→GLOBAL-Fallback: Werden alle mitarbeiterspezifischen Versionen geschlossen ohne eine
neue anzulegen, greift automatisch die globale Praxisregel. Die Admin-CLI soll das dem Benutzer
klar kommunizieren (z. B. „Mitarbeiterspezifische Regelzeit entfernt — globale Praxisregel gilt
wieder").


### Zeitraum-Hilfsfunktionen (Pflicht vor erster Intervallübergabe)

`TimeBookingRepository.list_between()` und alle Exportfunktionen erwarten halb-offene
Intervalle `[from_dt, to_dt)` mit UTC-normalisierten Datetimes. Das gesamte System definiert
Tagesgrenzen als UTC-Tage (Systemannahme aus Phase 4).

Die Admin-CLI und die Terminal-UI dürfen `from_dt`/`to_dt` nie ad hoc aus Benutzereingaben
konstruieren. Stattdessen müssen Hilfsfunktionen bereitgestellt werden, die Standardzeiträume
erzeugen und die UTC-Annahme kapseln:

- `day_interval(day: date) → tuple[datetime, datetime]` — gibt `(day_start_utc, next_day_utc)` zurück
- `week_interval(year: int, week: int) → tuple[datetime, datetime]` — ISO-Woche, Montag 00:00 bis Sonntag+1 00:00
- `month_interval(year: int, month: int) → tuple[datetime, datetime]` — erster bis letzter Tag + 1 Tag

Diese Funktionen sichern, dass alle Aufrufer konsistente Intervallgrenzen verwenden.
Fehlerhafte inklusive `to_dt`-Grenzen (z. B. `23:59:59`) würden Buchungen kurz vor Mitternacht
systematisch ausschließen.


---

## Zielstruktur

```
src/arbeitszeit/presentation/
├── __init__.py
├── terminal_ui/
│   ├── __init__.py
│   ├── main.py          Einstiegspunkt (Endlosschleife)
│   └── booking_loop.py  Buchungsablauf: Numpad → RFID → BookUseCase
└── admin_cli/
    ├── __init__.py
    ├── main.py          Einstiegspunkt (argparse/click)
    ├── employees.py     Mitarbeiter + Karten verwalten
    ├── bookings.py      Korrekturen + Nachträge
    ├── schedule.py      Regelarbeitszeit ändern
    ├── reports.py       PDF/CSV-Export + Pflichtauswertungen anzeigen
    └── system.py        Systemcheck + Backup manuell auslösen

tests/e2e/
├── test_backup.py        16 Tests ✓  (Phase 4)
├── test_booking_flow.py  vollständiger Buchungsablauf (Phase 5)
└── test_supplement_flow.py  Nachtrag von Erfassung bis Genehmigung (Phase 5)
```


---

## Implementierungsreihenfolge


### Schritt 0 – Voraussetzung: Phase 4/Schritt 9 nachholen

`infrastructure/system_check.py` implementieren (Pflichtenheft v3 §7.10):

- Konfigurationsprüfung: alle `system_config`-Keys vorhanden
- Geräteverfügbarkeit: evdev-Gerät erreichbar
- NAS-Erreichbarkeit: Backup-Zielpfad mountbar/schreibbar
- Datenbankzugriff: Datei öffenbar, Migrationsstand aktuell
- Grundkonsistenz: keine verwaisten Fremdschlüssel

Ergebnis in `system_events` (`event_type='SYSTEM_CHECK'`) protokolliert.
Aufrufbar manuell und als Startprüfung beim Systemstart.

Vor Schritt 4 dieser Phase muss das Modul vorhanden sein.


### Schritt 1 – presentation/terminal_ui/

`booking_loop.py` — zentraler Buchungsablauf:

1. Auf Numpad-Keypress warten (HardwareReader, BookingType aus Tastenzuordnung)
2. RFID-Scan abwarten (mit Timeout; Abbruch wenn kein Scan)
3. `BookCommand` aufbauen, `BookUseCase(uow).execute(cmd)` aufrufen
4. Feedback-Ausgabe (OK / WARN / NEEDS_REVIEW / Fehler)

`main.py` — Endlosschleife mit:
- Startprüfung via `system_check.py`
- Fehlerbehandlung: `DomainError`-Subklassen → spezifische Fehlermeldung;
  unerwartete Exception → in `system_events` protokollieren + weiterarbeiten
- Graceful-Shutdown auf SIGTERM/SIGINT

Testfälle in `tests/e2e/test_booking_flow.py`:
- Vollständiger Buchungsablauf COME → GO (Simulator + echte SQLite-DB)
- COME → BREAK_START → BREAK_END → GO
- Unbekannte RFID-Karte → Abweisung mit Audit-Log
- Inaktive Karte → Abweisung mit Audit-Log


### Schritt 2 – presentation/admin_cli/

Strukturiertes CLI (argparse oder click), untergeordnete Befehle:

```
admin employees list
admin employees add --personnel-no E001 --first-name ... --last-name ...
admin employees deactivate <id>
admin cards assign --employee-id <id> --uid-hash <hash>
admin cards replace --old-card-id <id> --uid-hash <hash>
admin cards deactivate <id>

admin bookings correct --booking-id <id> --type <type> --at <datetime> --reason "..."
admin bookings supplement --employee-id <id> --type <type> --at <datetime> --reason "..."
admin bookings approve-supplement --supplement-id <id>
admin bookings reject-supplement --supplement-id <id> --reason "..."

admin schedule set --weekday <1-7> --start <HH:MM> --end <HH:MM> --from <YYYY-MM-DD>
admin schedule show

admin reports export-csv --from <date> --to <date> [--employee-id <id>]
admin reports export-pdf-day <date>
admin reports export-pdf-week <year> <week>
admin reports export-pdf-month <year> <month>
admin reports export-pdf-employee --employee-id <id> --from <date> --to <date>

admin system check
admin system backup
```

Rollenprüfung: erster Schritt in jedem Befehl, vor jeder Datenoperation.
Keine interaktive Passworteingabe im initialen Scope — Benutzer-ID per
`--user-id`-Flag oder Umgebungsvariable `ADMIN_USER_ID`.


### Schritt 3 – Pflichtauswertungen in App einsehbar

(Pflichtenheft v3 §7.12)

```
admin reports open-bookings [--employee-id <id>]
admin reports warn-cases --from <date> --to <date> [--employee-id <id>]
admin reports corrections --from <date> --to <date> [--employee-id <id>]
admin reports supplements --from <date> --to <date> [--employee-id <id>]
admin reports open-review-cases [--employee-id <id>]
```

Alle acht Pflichtauswertungskategorien tabellarisch dargestellt.
Alle nutzen ausschließlich `report_queries.py` als Datenquelle.
Alle sind auch als CSV exportierbar (Schritt 2 `reports export-csv`
gibt dasselbe Datenset aus).


### Schritt 4 – Selbsttest im UI integrieren

(Pflichtenheft v3 §7.10)

Voraussetzung: `infrastructure/system_check.py` (Schritt 0) fertig.

`admin system check` ruft `system_check.py` auf und zeigt das Ergebnis
tabellarisch in der Konsole an. Ergebnis wird zusätzlich in `system_events`
protokolliert (bereits in `system_check.py` implementiert).

Terminal-UI ruft Systemcheck beim Start automatisch auf.
Bei kritischem Befund: Warnung ausgeben, aber weiterlaufen (kein Hard-Stop).


### Schritt 5 – Systemzeitprotokollierung

(Pflichtenheft v3 §9.3 / Regelwerk v3 §21)

Erkennung von Zeitsprüngen und manuellen Uhrzeitänderungen:
- Periodisch Systemzeit mit letztem bekannten Wert vergleichen
- Sprung > Schwellenwert (konfigurierbar via `system_config`) →
  INSERT in `system_events` (event_type `TIME_JUMP_DETECTED` oder
  `MANUAL_TIME_CHANGE_DETECTED`, details_json mit Differenz)
- Schwellenwert-Default: 60 Sekunden (nur echte Sprünge, nicht NTP-Drift)

Optional: AuditLogEntry für prüfpflichtige Fälle.
NTP-Synchronisation ist Betriebsvoraussetzung, nicht Aufgabe dieser Schicht.

Deckt V3 §16-Testpflicht „Systemzeitabweichung" ab.


---

## Testverteilung Phase 5

```
tests/e2e/test_booking_flow.py    — vollständiger Buchungsablauf
                                     COME/GO, COME/BREAK/BREAK_END/GO,
                                     Abweisung unbekannte/inaktive Karte
                                     (Schätzung: ~10 Tests)
tests/e2e/test_supplement_flow.py — Nachtrag von Erfassung bis Genehmigung
                                     inkl. Ablehnung, Rollenprüfung
                                     (Schätzung: ~8 Tests)
```

tests/e2e/ verwendet Simulator (SimulatedHardwareReader) und
echte SQLite-In-Memory-DB (run_migrations()).
Keine Unit-Tests für Präsentationsschicht — die Logik liegt vollständig
in Application- und Infrastructure-Schicht.


---

## V3 §16 Testpflicht-Abdeckung nach Phase 5

```
>6h ohne Pause              → test_compliance_checks.py  (grün)
>9h ohne ausreichende Pause → test_compliance_checks.py  (grün)
>8h Arbeitszeit             → test_compliance_checks.py + test_book_time.py  (grün)
>10h Arbeitszeit            → test_compliance_checks.py + test_book_time.py  (grün)
Ruhezeitverletzung <11h     → test_book_time.py  (grün)
Systemzeitabweichung        → test_e2e? / system_events-Prüfung  (Phase 5/Schritt 5)
Notfallnachtrag             → test_register_supplement.py  (grün)
Restore-Test                → tests/e2e/test_backup.py  (grün)
Auswertung offener Fälle    → test_export.py  (grün)
```
