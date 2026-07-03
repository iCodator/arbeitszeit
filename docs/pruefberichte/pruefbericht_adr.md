# Prüfbericht: docs/adr/adr-cqrs-lesezugriff.md und docs/adr/adr_presentation_infrastructure_v1.md

## Gesamteinschätzung

Beide Architekturentscheidungsdokumente (ADRs) sind inhaltlich sehr präzise und nahezu vollständig durch Code belegt: Alle in der Import-Tabelle von `adr_presentation_infrastructure_v1.md` genannten Presentation-Dateien importieren tatsächlich exakt die dort aufgeführten Infrastructure-Symbole, der beschriebene Layer-Contract entspricht wortgleich der `import-linter`-Konfiguration in `pyproject.toml`, und die referenzierten Commit-Hashes sowie die daraus resultierenden Dateien (`application/queries.py`, `domain/value_objects.py`) existieren. Ein Fehler wurde gefunden: `adr-cqrs-lesezugriff.md` verweist auf eine nicht existierende Datei `docs/adr/ADR-001-migrations-struktur.md`.

## Befunde

- Aussage: „`docs/adr/ADR-001-migrations-struktur.md` — verwandte ADR (Zwei-Schichten-Muster)“ (Referenzliste, `adr-cqrs-lesezugriff.md`)
- Status: inkorrekt
- Beleg: `docs/adr/` enthält ausschließlich `adr-cqrs-lesezugriff.md`, `adr_presentation_infrastructure_v1.md` und `device_event_architekturentscheidung_v1.md`; eine Datei mit dem Namen `ADR-001-migrations-struktur.md` existiert nicht im Repository, auch nicht unter anderem Pfad.
- Bewertung: Toter Verweis auf ein nicht vorhandenes Dokument.
- Anpassungsvorschlag: Zeile aus der Referenzliste entfernt.

---

- Aussage: Import-Tabelle in `adr_presentation_infrastructure_v1.md` (14 Zeilen, u. a. `admin_cli/main.py` → `open_connection`/`run_migrations`, `admin_cli/bookings.py`/`schedule.py` → `SQLiteUnitOfWork`, `admin_cli/reports.py` → `csv_exporter`/`pdf_report_service`/Query-Funktionen, `admin_cli/system.py` → `SQLiteBackupService`/`run_system_check`, `terminal_ui/booking_loop.py` → `open_connection`/`SQLiteUnitOfWork`/`HardwareReader`, `terminal_ui/main.py` → `open_connection`/`EvdevHardwareReader`/`HardwareReader`/`SQLiteSystemConfigRepository`/`run_system_check`/`time_monitor`)
- Status: korrekt
- Beleg: Grep der `from arbeitszeit.infrastructure`-Importzeilen in allen sieben genannten Presentation-Dateien bestätigt jede einzelne Tabellenzeile wortgleich (u. a. `admin_cli/main.py` Zeilen 10–11, `admin_cli/bookings.py` Zeile 35, `admin_cli/schedule.py` Zeile 21, `admin_cli/reports.py` Zeilen 10–11, `admin_cli/system.py` Zeilen 9–10, `terminal_ui/booking_loop.py` Zeilen 11–13, `terminal_ui/main.py` Zeilen 18–24).
- Bewertung: Vollständig deckungsgleich mit Code.

---

- Aussage: „`presentation → infrastructure → application → domain`“ als verbindliche Import-Richtung / Layer-Contract
- Status: korrekt
- Beleg: `pyproject.toml`, Abschnitt `[[tool.importlinter.contracts]]`, `layers = ["arbeitszeit.presentation", "arbeitszeit.infrastructure", "arbeitszeit.application", "arbeitszeit.domain"]`.
- Bewertung: Die im Dokument beschriebene Schichtreihenfolge entspricht exakt der `import-linter`-Konfiguration.

---

- Aussage: „Die zugehörigen Row-Typen (`BookingRow`, `CorrectionRow`, `SupplementRow`, `ReviewCaseRow`) wurden bereits nach `application/queries.py` verschoben (Commit `6510bfb`)“
- Status: korrekt
- Beleg: `src/arbeitszeit/application/queries.py` enthält die Klassen `BookingRow`, `CorrectionRow`, `SupplementRow`, `ReviewCaseRow` (Zeilen 28, 43, 61, 79). Der referenzierte Commit `6510bfb` existiert in der Git-Historie mit der Nachricht „Feat: application/queries.py – Query-DTOs in Application-Layer (CQRS-Symmetrie)“.
- Bewertung: Vollständig deckungsgleich mit Code und Commit-Historie.

---

- Aussage: „`domain/value_objects.py` (Commit `63f75b1`) — starke ID-Typen eingeführt“
- Status: korrekt
- Beleg: `src/arbeitszeit/domain/value_objects.py` existiert; Commit `63f75b1` existiert in der Git-Historie mit der Nachricht „Feat: domain/value_objects.py – starke NewType-IDs eingeführt“.
- Bewertung: Vollständig deckungsgleich mit Code und Commit-Historie.

---

- Aussage: „`SQLiteSystemConfigRepository` direkt in `terminal_ui/main.py`“ importiert, um den `rfid_timeout`-Wert aus `system_config` zu lesen (als offenes Backlog-Item markiert)
- Status: korrekt
- Beleg: `src/arbeitszeit/presentation/terminal_ui/main.py`, Zeile 19: `from arbeitszeit.infrastructure.db.repositories import SQLiteSystemConfigRepository`; Zeilen 123–128 verwenden dies zum Lesen von `rfid_timeout` aus der `system_config`-Tabelle.
- Bewertung: Vollständig deckungsgleich mit Code.

---

- Aussage (ADR-002, Kontext): Tabelle „Schreibende Operationen laufen ausnahmslos über Use Cases“ mit `bookings.py` → `CorrectBookingUseCase`, `RegisterSupplementUseCase`, `ApproveSupplementUseCase`, `RejectSupplementUseCase`; `schedule.py` → `ManageWorkScheduleUseCase`
- Status: korrekt
- Beleg: Rollenprüfungen und Aufrufstruktur dieser vier Use Cases wurden bereits im Rahmen dieser Prüfsitzung (Prüfbericht zu `planung_gesamt.md`) gegen den Code verifiziert; die entsprechenden Klassen existieren in `src/arbeitszeit/application/use_cases/`.
- Bewertung: Deckungsgleich mit Code.

## Zusammenfassung der vorgenommenen Änderungen

1. In `docs/adr/adr-cqrs-lesezugriff.md` den toten Verweis auf die nicht existierende Datei `docs/adr/ADR-001-migrations-struktur.md` aus der Referenzliste entfernt.
2. Keine Änderungen an `docs/adr/adr_presentation_infrastructure_v1.md` erforderlich; alle geprüften Aussagen sind korrekt.

## Offene Punkte (nicht verifizierbar)

- Die Bezeichnung „ADR-002“ im Titel von `adr-cqrs-lesezugriff.md` setzt implizit eine Nummerierungsreihenfolge voraus (ADR-001 wäre dann die entfernte Referenzdatei). Da diese Datei nicht existiert, ist nicht abschließend feststellbar, ob die Nummerierung „ADR-002“ nach wie vor sinnvoll ist oder ob sie ebenfalls angepasst werden sollte; dies wird als redaktionelle Entscheidung markiert und nicht eigenmächtig geändert, da der Titel selbst keine falsche Tatsachenbehauptung über den Code enthält.
