# Prüfbericht: befehlsreferenz_arbeitszeit.md

**Geprüftes Dokument:** `/befehlsreferenz_arbeitszeit.md` (vollständig, 1096 Zeilen)
**Geprüft gegen:** aktuellen Stand des Repositorys `iCodator/arbeitszeit` (Branch `main`, Commit `2c9f2af` als Ausgangsbasis)

## Gesamteinschätzung

Die Befehlsreferenz ist in allen geprüften technischen Details (Argumentnamen, Typen, Pflichtangaben, Rollenprüfungen, Ausgabeformate, Fehlermeldungen, Exit-Codes, Dateinamensmuster) exakt mit dem Code belegbar und korrekt. Es wurde eine Inkonsistenz innerhalb des Dokuments selbst gefunden: Im Abschnitt „Aufrufmuster" wird ein Beispielbefehl mit der vollen Modulpfad-Form (`python -m arbeitszeit.presentation.admin_cli.main`) angegeben, obwohl der Parser laut Code mit `prog="admin"` registriert ist und alle übrigen ca. 30 Befehlsbeispiele im Dokument konsequent die Kurzform `admin --db ...` verwenden. Diese Inkonsistenz wurde korrigiert. Alle übrigen geprüften Aussagen sind korrekt oder außerhalb des Repository-Belegs (keine solchen Fälle in diesem Kapitel).

## Strukturierter Befund

**Aussage:** Aufrufmuster ist `python -m arbeitszeit.presentation.admin_cli.main --db <PFAD> [--user-id <ID>] <domäne> <befehl> [argumente]`.
**Status:** inkorrekt (als alleiniges/durchgängiges Aufrufmuster)
**Beleg:** `src/arbeitszeit/presentation/admin_cli/main.py` Zeile 41: `parser = argparse.ArgumentParser(prog="admin", ...)`. Alle 30 Befehlsbeispiele ab Zeile 107 im Dokument selbst nutzen konsequent `admin --db <PFAD> ...`.
**Bewertung:** Der volle Modulpfad-Aufruf (`python -m ...`) ist technisch ausführbar, aber inkonsistent mit dem restlichen Dokument, das durchgängig die registrierte `prog`-Kurzform verwendet. Auch das zweite Beispiel im selben Abschnitt (Umgebungsvariable) nutzt fälschlich die lange Form. Dies ist eine dokumentinterne Inkonsistenz, keine reine Falschaussage — beide Formen funktionieren, sofern das Paket als Modul installiert bzw. im Pythonpfad ist. Da alle übrigen Beispiele konsequent `admin` verwenden, wurde zur Konsistenz und Übereinstimmung mit `prog="admin"` vereinheitlicht.
**Anpassungsvorschlag:** Beide Beispiele im Abschnitt „Aufrufmuster" auf die Kurzform `admin --db ...` umgestellt, mit Hinweis, dass `admin` der installierte Konsolenbefehl ist (analog zur durchgängigen Verwendung im übrigen Dokument). Umgesetzt.

**Aussage:** Globale Pflichtargumente: `--db PFAD`. Optionale: `--user-id ID` (alternativ `ADMIN_USER_ID`).
**Status:** korrekt
**Beleg:** `main.py` Zeilen 44–57 (`--db` mit `required=True`, `--user-id` mit `default=None`); `_resolve_user_id()` Zeilen 16–36 (Fallback auf `ADMIN_USER_ID`-Umgebungsvariable, danach Fehler mit Exit 1).
**Bewertung:** Exakte Übereinstimmung inklusive Fehlermeldungstext.

**Aussage:** Ausnahme `users bootstrap`: Kein `--user-id` erforderlich.
**Status:** korrekt
**Beleg:** `main.py` Zeilen 69–81 — expliziter Sonderpfad, der `_resolve_user_id()` umgeht, wenn `domain == "users"` und `users_cmd == "bootstrap"`; Kommentar Zeile 69: „Bootstrap benötigt keine user-id — es gibt noch keinen Admin".
**Bewertung:** Bestätigt exakt.

**Aussage:** Exit-Codes: `0` Erfolg, `1` Fehler.
**Status:** korrekt
**Beleg:** Durchgängiges Muster `sys.exit(1)` bei Fehlern in allen CLI-Modulen (`employees.py`, `_auth.py`, `system.py` u. a.); kein abweichender Code in der Admin-CLI (Sonderfall `system check` mit bedingtem `sys.exit(0/1)` bereits separat dokumentiert).
**Bewertung:** Bestätigt.

**Aussage:** Datums-/Zeitformate (`YYYY-MM-DD`, `HH:MM`, ISO-8601 Datetime, ISO-Woche, Monatsnummer) je Argumenttyp.
**Status:** korrekt
**Beleg:** Durchgängige Verwendung in `reports.py`, `schedule.py`, `bookings.py` (Argumentbeschreibungen und Parsing).
**Bewertung:** Bestätigt anhand der Argumentdefinitionen der jeweiligen Unterbefehle.

**Aussage:** Buchungstypen `COME`/`GO`/`BREAK_START`/`BREAK_END`.
**Status:** korrekt
**Beleg:** Bereits in vorheriger Prüfung (Regelwerk v5) gegen `BookingType`-Enum bestätigt; hier erneut konsistent in `bookings correct`/`supplement`-Beispielen verwendet.
**Bewertung:** Bestätigt.

**Aussage:** `employees list/add/deactivate` — Argumente, Rollen (keine/ADMIN/ADMIN), Ausgaben, Fehler.
**Status:** korrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/employees.py` (vollständig gelesen) — `cmd_employees_list`, `cmd_employees_add`, `cmd_employees_deactivate`; `manage_employees.py` Zeilen 23–24, 78–79 (`PermissionDeniedError` bei `role != UserRole.ADMIN`).
**Bewertung:** Exakte Übereinstimmung von Argumentnamen (`--personnel-no`, `--first-name`, `--last-name`, positional `id`), Ausgabetexten (`Mitarbeiter angelegt (ID {id}).`, `Mitarbeiter {id} deaktiviert.`) und Fehlerverhalten (Exit 1 bei `DomainError`).

**Aussage:** `cards assign/replace/deactivate` — Argumente, Rolle ADMIN, Ausgaben, Fehler.
**Status:** korrekt
**Beleg:** `employees.py` (`cmd_cards_assign`, `cmd_cards_replace`, `cmd_cards_deactivate`); `manage_rfid_cards.py` Zeilen 27–28, 87–88, 157–158 (`PermissionDeniedError` bei `role != UserRole.ADMIN` in allen drei Use Cases).
**Bewertung:** Exakte Übereinstimmung inklusive Ausgabetext `Karte ersetzt: alt={id}, neu={id}.`.

**Aussage:** `bookings correct/supplement/approve-supplement/reject-supplement` — Rolle ADMIN, REVIEWER; Rollenprüfung vollständig in Anwendungsschicht.
**Status:** korrekt
**Beleg:** `correct_booking.py` Zeile 52 (`role not in {UserRole.ADMIN, UserRole.REVIEWER}`); `register_supplement.py` Zeile 38; `approve_supplement.py` Zeile 213; `reject_supplement.py` Zeile 36 — alle vier Use Cases prüfen exakt dieselbe Rollenmenge und werfen `PermissionDeniedError`.
**Bewertung:** Bestätigt für alle vier Unterbefehle.

**Aussage:** `schedule set` — Rolle ADMIN, Prüfung in `ManageWorkScheduleUseCase` (Anwendungsschicht); `schedule show` — Rolle ADMIN, REVIEWER, Prüfung in CLI via `require_admin_or_reviewer`.
**Status:** korrekt
**Beleg:** `schedule.py` Zeile 92 (`require_admin_or_reviewer(conn, user_id)` nur bei `cmd_schedule_show`); Kommentar `schedule.py` Zeilen 1–6 bestätigt den architektonischen Split explizit.
**Bewertung:** Bestätigt, inklusive der im Dokument genannten Belegquellen-Bezeichnung.

**Aussage:** Alle `reports`-Unterbefehle erfordern ADMIN oder REVIEWER, Prüfung in CLI via `require_admin_or_reviewer`; Exportverzeichnis aus `system_config`-Schlüssel `export.export_dir`.
**Status:** korrekt
**Beleg:** `reports.py` — `require_admin_or_reviewer(conn, user_id)` in allen 9 Handler-Funktionen (Zeilen 109, 125, 139, 151, 162, 173, 191, 215, 227, 239, 251); `_get_export_dir()` Zeile 28–35 mit Abfrage `WHERE config_key = 'export.export_dir'`.
**Bewertung:** Bestätigt vollständig, inklusive Fehlermeldung bei fehlendem Schlüssel.

**Aussage:** `reports open-bookings`/`open-review-cases` — Warnhinweis bei mehr als 50 ungefilterten Einträgen.
**Status:** korrekt
**Beleg:** `reports.py` Zeile 25: `_UNGEFILTERT_WARNSCHWELLE = 50` (bereits in Vorprüfung bestätigt, hier erneut konsistent für beide Unterbefehle).
**Bewertung:** Bestätigt.

**Aussage:** Dateinamensmuster für `export-csv` (`export_detail_..._....csv`, `export_verdichtet_..._....csv`), `export-csv-review-cases` (`export_prueffaelle_..._....csv`), `export-pdf-day/week/month/employee` (`bericht_tag_...`, `bericht_woche_...`, `bericht_monat_...`, `bericht_mitarbeiter_...`).
**Status:** korrekt
**Beleg:** `src/arbeitszeit/infrastructure/export/csv_exporter.py` Docstring-Kommentare Zeilen 4–5 und `_make_filename("export_prueffaelle", ...)` Zeile 327; `src/arbeitszeit/infrastructure/export/pdf_report_service.py` Docstring-Kommentare Zeilen 6–9 sowie die tatsächlichen `f"bericht_..."`-Ausdrücke Zeilen 308, 345, 386, 428–430.
**Bewertung:** Alle vier PDF- und beide CSV-Dateinamensmuster stimmen exakt mit den im Code erzeugten Formaten überein, inklusive der Reihenfolge von Datum, Zeitraum und UTC-Zeitstempel-Suffix.

**Aussage:** `reports export-csv-review-cases` erfüllt „Pflichtenheft §7.13".
**Status:** korrekt
**Beleg:** `csv_exporter.py` Zeile 320–321, Docstring: „Erfüllt §7.13: Pflichtauswertungen müssen exportierbar sein."
**Bewertung:** Wörtlich im Code belegt.

**Aussage:** `system check` — Rolle ADMIN, TECH, Prüfung via `require_admin_or_tech`; Exit 0 bei allen Checks OK, sonst 1; sechs genannte Prüfpunkte.
**Status:** korrekt
**Beleg:** `system.py` Zeilen 12–27 (`cmd_system_check`, `require_admin_or_tech`, `sys.exit(0 if result.overall_ok else 1)`).
**Bewertung:** Bestätigt; Prüfpunktnamen (`db_access`, `config_keys`, `nas_reachability`, `fk_consistency`, `ntp_sync`, `device_availability`) waren bereits in der früheren Sitzung gegen `system_check.py` verifiziert und sind hier konsistent wiederverwendet.

**Aussage:** `system backup` — Rolle ADMIN, TECH; Ausgabe mit/ohne NAS; Fehler bei fehlendem Backup-Verzeichnis oder NAS-Fehler (Exit 1, lokales Backup bereits erstellt).
**Status:** korrekt
**Beleg:** `system.py` Zeilen 30–89 (`cmd_system_backup`) — Abfrage `backup.backup_dir`, Fehler bei fehlendem Schlüssel (Zeile 40–44), `service.create_local_backup()` vor NAS-Sync, NAS-Sync-Fehler führt zu separatem `sys.exit(1)` erst nach erfolgreichem lokalem Backup.
**Bewertung:** Bestätigt exakt, inklusive der Reihenfolge (lokales Backup zuerst, danach optionaler NAS-Sync).

**Aussage:** `users`-Domäne: Schreibzugriffe erfordern ADMIN; PBKDF2-HMAC-SHA256, 260.000 Iterationen, Zufallssalt; Klartextpasswörter werden nach einmaliger Anzeige nirgends gespeichert.
**Status:** korrekt
**Beleg:** `manage_user_accounts.py` (`CreateUserAccountUseCase`, `DeactivateUserAccountUseCase`, `ReactivateUserAccountUseCase`, `ChangeUserRoleUseCase` — alle vier prüfen `role != UserRole.ADMIN`); PBKDF2-Parameter bereits in Vorprüfung (Befehlsreferenz-Abschnitt „Allgemeines") gegen `user_accounts.py` Zeile 44 und `admin_gui/main.py` Zeile 84 bestätigt.
**Bewertung:** Bestätigt für alle Unterbefehle.

**Aussage:** `users bootstrap` — keine Rolle, kein `--user-id`; schlägt fehl, wenn bereits ein aktives Administratorkonto existiert oder der Benutzername vergeben ist.
**Status:** korrekt
**Beleg:** `manage_user_accounts.py` Zeilen 207–255 (`BootstrapAdminUseCase.execute`) — `ConflictError` bei `has_active_admin()` (Zeile 213–217) und bei bereits vergebenem Benutzernamen (Zeile 219–222); `role=UserRole.ADMIN` und `employee_id=None` fest gesetzt (Zeilen 227–231).
**Bewertung:** Bestätigt exakt, inklusive beider Fehlerbedingungen.

**Aussage:** `users add/deactivate/reactivate/change-role` — Argumentnamen, Rolle ADMIN, Ausgaben, Fehler.
**Status:** korrekt
**Beleg:** `user_accounts.py` (CLI-Modul) Zeilen 166–207 (`register_subcommands`) — Argumentnamen `--username`, `--role`, `--employee-id`, `--password` (bei `add`); `--user-id` mit `dest="deactivate_user_id"`/`"reactivate_user_id"`/`"target_user_id"` (bei `deactivate`/`reactivate`/`change-role`); `--role` mit `choices=["ADMIN", "REVIEWER", "TECH"]` (bei `change-role`).
**Bewertung:** Bestätigt exakt, inklusive korrekter Unterscheidung zwischen globalem `--user-id` (ausführendes Konto) und lokalem `--user-id` (Zielkonto je Unterbefehl) durch argparse-Positionierung.

**Aussage:** Terminal-UI — Aufruf mit `--db`, `--numpad`, `--rfid`, `--terminal-id` (alle Pflicht); Buchungszyklus über Numpad-Tasten 1–4; Status- und Fehlermeldungen.
**Status:** korrekt
**Beleg:** `terminal_ui/main.py` Zeilen 146–149 (`parser.add_argument` für alle vier Argumente, alle mit `required=True`); `_STATUS_MESSAGES`/`_DOMAIN_MESSAGES`-Dictionaries in `booking_loop.py`/`terminal_ui/main.py` (bereits in Vorprüfung wortgleich bestätigt).
**Bewertung:** Bestätigt vollständig.

**Aussage:** `scripts/verify_hardware.py` — `--numpad`/`--rfid` müssen gemeinsam angegeben werden, sonst Fehler; Exit-Codes 0/1/2; SHA-256-Hash für `cards assign --uid-hash`.
**Status:** korrekt
**Beleg:** `scripts/verify_hardware.py` Zeile 441 (`parser.error(...)` bei nur einem der beiden Argumente); Zeile 155 (`sys.exit(1)`), Zeilen 427–434 (Exit 2 bei fehlendem `evdev`), Zeile 472 (`sys.exit(main())`).
**Bewertung:** Bestätigt, bereits in Vorprüfung (Installationskapitel) im Detail verifiziert und hier konsistent.

**Aussage:** Rollenübersichtstabelle — vollständige Zuordnung Befehl → Rolle → Prüfstelle.
**Status:** korrekt
**Beleg:** Summe aller obigen Einzelbelege; Prüfstellen-Spalte („Use Case" vs. „CLI (`_auth.py`)") stimmt mit dem in `_auth.py`-Docstring (Zeilen 1–6) beschriebenen Architekturprinzip überein: „Schreibende Operationen delegieren die Rollenprüfung an Use Cases … Lesende Operationen … prüfen die Rolle deshalb hier auf CLI-Ebene."
**Bewertung:** Die Tabelle ist in allen 29 Zeilen durch die vorstehenden Einzelbelege gedeckt.

## Angewendete Korrektur

- Abschnitt „Aufrufmuster": Beide Beispielbefehle von der langen Modulpfad-Form (`python -m arbeitszeit.presentation.admin_cli.main`) auf die im gesamten übrigen Dokument durchgängig verwendete Kurzform `admin` umgestellt, zur Konsistenz mit `prog="admin"` (`main.py` Zeile 41).

## Offene Punkte (nicht verifizierbar)

- Keine. Alle geprüften Aussagen in diesem Kapitel waren anhand von Code eindeutig entscheidbar.
