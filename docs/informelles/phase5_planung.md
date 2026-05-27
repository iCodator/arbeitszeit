# Planung Phase 5 – Präsentation

Stand: 2026-05-27. Basiert auf Pflichtenheft v3 und Regelwerk v3.
Phase 5 vollständig abgeschlossen (Schritte 0–5).
Nachgeführte Code-Review-Korrekturen (2026-05-27):

- P1: open-bookings + open-review-cases mit --from/--to Zeitraumfilter
- P1: list_open_bookings_in_period() in report_queries.py ergänzt
- P2: PDF-Intervalle von 23:59:59 auf halb-offene UTC-Intervalle umgestellt
- P2: CSV-Intervallbildung in reports.py vereinheitlicht (alle via day_interval())
- P2: Alle <= to_dt in report_queries.py auf < to_dt korrigiert
- P3: Tippfehler und Fallback-Text in schedule show bereinigt

369 Tests grün (alle Ebenen).

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

- Systemzeitprotokollierung (Pflichtenheft v3 §9.3 / Regelwerk v3 §21)

Betriebsdokumentation (Phase 5, kein Code):

- Exportverzeichnis: Zugriffsrechte, Aufbewahrungsfristen, Löschkonzept
  (Regelwerk v3 §17/§18, Befund 4/8-07)

353 Tests grün (alle Ebenen, Stand Phase 5/Schritt 1; jetzt 369).


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


### Schritt 0 – Voraussetzung: Phase 4/Schritt 9 nachholen  ✓

`infrastructure/system_check.py` implementiert (Phase 4/Schritt 9 abgeschlossen).


### Schritt 1 – presentation/terminal_ui/  ✓

`booking_loop.py` — zentraler Buchungsablauf:

1. `reader.read_next()` — blockiert bis Numpad-Keypress + RFID-Scan
2. `BookCommand` aufbauen, `BookUseCase(uow).execute(cmd)` aufrufen
3. Feedback-Ausgabe (OK / WARN / NEEDS_REVIEW / Fehler)

`main.py` — Endlosschleife mit:
- Startprüfung via `system_check.py`
- Fehlerbehandlung: `DomainError`-Subklassen → spezifische Fehlermeldung;
  unerwartete Exception → in `system_events` protokollieren + weiterarbeiten
- Graceful-Shutdown auf SIGTERM/SIGINT

**Architekturkorrektur in BookUseCase (Nebeneffekt aus e2e-Tests):**
In `BookUseCase.execute()` wurde ein Deadlock-Problem behoben: `uow.commit()`
wird jetzt VOR dem TIME_BOOKED-Audit-Log-Eintrag aufgerufen. Nach commit hält
`conn` keinen RESERVED-Lock mehr, sodass `audit_conn` (autocommit) ohne Blockierung
schreiben kann. Ablehnungspfade sind nicht betroffen (dort hat `conn` nur SELECTs
ausgeführt). Diese Deadlock-Situation war bisher nicht testbar, weil es keinen
e2e-Test mit echter SQLite-DB und zwei Verbindungen gab.

**Korrekturen aus förmlichem Review (Befund 5/1-04, 5/1-06):**

- Befund 5/1-04: `run_system_check()` erhält jetzt `numpad_path` und `rfid_path`
  aus den Gerätepfaden von `run()`, damit die Geräteverfügbarkeitsprüfung beim
  Systemstart nicht übersprungen wird.

- Befund 5/1-06: Unerwartete Laufzeitfehler werden jetzt als `APPLICATION_ERROR`
  (nicht `APPLICATION_STOP`) in `system_events` protokolliert. Dazu wurde
  `0006_system_events_application_error.sql` ergänzt, das `system_events` per
  Table-Rebuild um `APPLICATION_ERROR` erweitert.

10 Tests in `tests/e2e/test_booking_flow.py`:
- Vollständiger Buchungsablauf COME → GO (Simulator + echte SQLite-DB)
- COME → BREAK_START → BREAK_END → GO
- Unbekannte RFID-Karte → Abweisung mit Audit-Log
- Inaktive Karte → Abweisung mit Audit-Log


### Schritt 2 – presentation/admin_cli/  ✓

Vollständig implementiert. Argparse-basiertes CLI mit Subcommands:

```
src/arbeitszeit/presentation/admin_cli/
├── __init__.py
├── _intervals.py    day_interval / week_interval / month_interval
├── main.py          Einstiegspunkt (argparse, --user-id / ADMIN_USER_ID)
├── employees.py     Mitarbeiter + Karten (direktes SQL, ADMIN-Rolle)
├── bookings.py      Korrekturen + Nachträge (Use Cases, ADMIN/REVIEWER)
├── schedule.py      Regelarbeitszeit (ManageWorkScheduleUseCase, ADMIN)
├── reports.py       PDF/CSV-Export + Pflichtauswertungen (ADMIN/REVIEWER)
└── system.py        Systemcheck + Backup (ADMIN/TECH)
```

**Deadlock-Korrektur in allen Use Cases (Nebeneffekt):**
Das commit()-vor-audit-Muster aus Schritt 1 (BookUseCase) wurde auf alle
weiteren schreibenden Use Cases übertragen, die denselben Deadlock hatten:
`RegisterSupplementUseCase`, `ApproveSupplementUseCase`,
`RejectSupplementUseCase`, `CorrectBookingUseCase`, `ManageWorkScheduleUseCase`.
In jedem Fall: `uow.commit()` VOR `audit_log_repo.add()`, damit `conn`
keinen RESERVED-Lock mehr hält, wenn `audit_conn` schreiben will.

8 Tests in `tests/e2e/test_supplement_flow.py`:
- Nachtrag erfassen (REVIEWER) → PENDING
- Nachtrag erfassen (EMPLOYEE) → PermissionDeniedError
- Nachtrag erfassen (unbekannter Mitarbeiter) → NotFoundError
- Nachtrag genehmigen (ADMIN) → TimeBooking angelegt, Status MANUAL
- Nachtrag ablehnen (REVIEWER) → REJECTED
- Nachtrag genehmigen nach Ablehnung → ValidationError
- Nachtrag genehmigen (inaktiver Mitarbeiter) → InactiveEmployeeError
- Nachtrag genehmigen (unbekannter Benutzer) → PermissionDeniedError

361 Tests grün (alle Ebenen, Stand Phase 5/Schritt 2).

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


### Schritt 5 – Systemzeitprotokollierung  ✓

(Pflichtenheft v3 §9.3 / Regelwerk v3 §21)

`infrastructure/time_monitor.py`:

- `SystemTimeMonitor(db_path, threshold_seconds=60.0)` — Sprungdetektion via
  Monotonic-Clock vs. Wall-Clock-Vergleich.
- `check()` — nimmt Zeitsample; schreibt `system_events`-Eintrag bei Sprung.
- `load_threshold_from_config(db_path, default=60.0)` — liest optionalen
  Schwellenwert aus `system_config`-Schlüssel `time_monitor.jump_threshold_seconds`.

Erkennungslogik:
- Vorwärtssprung (`diff > threshold`): `TIME_JUMP_DETECTED` (WARN)
- Rückwärtssprung (`diff < -threshold`): `MANUAL_TIME_CHANGE_DETECTED` (WARN)
- NTP-Drift (< Schwellenwert) wird herausgefiltert; Default 60 Sekunden.

Integration in `terminal_ui/main.py`:
- `monitor.check()` als erster Schritt in jedem Loop-Durchlauf, vor
  blockierendem `read_next()`. Dadurch werden Sprünge zwischen zwei
  Buchungen zuverlässig erkannt (Monotonic-Clock läuft auch während Blockierung).

Kein eigener AuditLogEntry — `system_events` ist die korrekte Ablage für
Betriebsereignisse ohne fachlichen Buchungsbezug.

NTP-Synchronisation ist Betriebsvoraussetzung, nicht Aufgabe dieser Schicht.

8 Tests in `tests/integration/test_time_monitor.py`:
- Erster Aufruf → kein Ereignis (Basiswert setzen)
- Normaler Ablauf → kein Ereignis
- Vorwärtssprung > Threshold → TIME_JUMP_DETECTED
- Rückwärtssprung > Threshold → MANUAL_TIME_CHANGE_DETECTED
- Sprung < Threshold → kein Ereignis
- details_json enthält diff_seconds
- load_threshold_from_config mit Fallback
- load_threshold_from_config liest system_config-Wert

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
ephemere dateibasierte SQLite-Test-DB (tmp_path / "arbeitszeit.db" + run_migrations()).
Dateibasiert ist für Zwei-Verbindungen-Semantik (conn + audit_conn) sachgerechter als
In-Memory.
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
Systemzeitabweichung        → test_time_monitor.py  (grün)
Notfallnachtrag             → test_register_supplement.py  (grün)
Restore-Test                → tests/e2e/test_backup.py  (grün)
Auswertung offener Fälle    → test_export.py  (grün)
```
