# Prüfbericht: Handbuch Präsentationsschicht (`docs/module/handbuch_presentation.md`)

**Geprüft am:** 03.07.2026
**Basis-Commit:** `e3fbb0d0985d7f98ba0dac5cec86a28f7d6ad302`
**Geprüfte Quelle:** `src/arbeitszeit/presentation/` (terminal_ui/, admin_cli/, admin_gui/)

## Gesamteinschätzung

Der überwiegende Teil des Kapitels ist gegen den Code korrekt und präzise belegt: Terminal-UI-Ablauf, Domänenfehler-Tabelle, Rollenmodell, `_intervals.py`, sowie die Domains `employees`/`cards`, `bookings`, `schedule`, `system` und `users` stimmen mit den jeweiligen Quelldateien überein. Zwei Befunde widersprechen jedoch dem Code: Die Einleitung nennt nur zwei Untermodule, obwohl ein drittes, vollständig ausgebautes Untermodul (`admin_gui/`) existiert; zudem fehlt in der Befehlstabelle zu `reports` ein tatsächlich implementierter Befehl (`export-csv-review-cases`). Beide Punkte betreffen die Vollständigkeit der Dokumentation, nicht die Richtigkeit der bereits enthaltenen Aussagen.

## Befunde

### Aussage: „Das Paket gliedert sich in zwei eigenständige Untermodule“ (terminal_ui/, admin_cli/)
- **Status:** inkorrekt (unvollständig)
- **Beleg:** `src/arbeitszeit/presentation/admin_gui/main.py` (1455 Zeilen), Docstring: „Admin-GUI für arbeitszeit — tkinter/ttk-basierte Verwaltungsoberfläche … Einstieg: `python -m arbeitszeit.presentation.admin_gui.main`“. Commit `f4cef2c` „Neu: Admin-GUI (tkinter/ttk) für Verwaltung ohne Kommandozeile“.
- **Bewertung:** Der Code enthält ein drittes, eigenständiges Präsentations-Untermodul `presentation/admin_gui/`, das eine tkinter/ttk-Anwendung (`ArbeitszeitApp`) mit Tabs für Mitarbeiter-, Karten-, Benutzer-, Regelzeit- und Systemverwaltung bereitstellt und dieselben Use Cases der Anwendungsschicht anspricht wie die Admin-CLI (u. a. `CreateEmployeeUseCase`, `AssignRfidCardUseCase`, `ManageWorkScheduleUseCase`, `BootstrapAdminUseCase`). Dieses Modul ist im Kapitel nicht erwähnt; die Aussage „zwei eigenständige Untermodule“ ist damit unvollständig und widerspricht dem tatsächlichen Codebestand.
- **Anpassungsvorschlag:** Einleitungssatz von „Das Paket gliedert sich in zwei eigenständige Untermodule“ auf „drei eigenständige Untermodule“ ändern und einen dritten Aufzählungspunkt ergänzen: `presentation/admin_gui/` – tkinter/ttk-basierte grafische Verwaltungsoberfläche als Alternative zur Admin-CLI. Ein eigener Abschnitt zum Funktionsumfang der Admin-GUI wäre sinnvoll, kann aber mangels Vorgabe im bestehenden Kapitel nicht ohne weitere Abstimmung ergänzt werden (Umfang/Gliederung wäre zu klären).

### Aussage: Tabelle „Export-Befehle“ unter „Domain: `reports`“ listet `export-csv`, `export-pdf-day`, `export-pdf-week`, `export-pdf-month`, `export-pdf-employee`
- **Status:** inkorrekt (unvollständig)
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/reports.py`, Funktion `cmd_reports_export_csv_review_cases` sowie `register_subcommands`: `rc_csv = rsub.add_parser("export-csv-review-cases", help="Offene Prüffälle als CSV exportieren")`.
- **Bewertung:** Der Befehl `reports export-csv-review-cases` ist implementiert (exportiert offene Prüffälle als CSV über `csv_exporter.export_review_cases`), erfordert wie die übrigen Export-Befehle `ADMIN`/`REVIEWER`-Rolle (`require_admin_or_reviewer`), fehlt aber vollständig in der Export-Befehle-Tabelle des Handbuchs.
- **Anpassungsvorschlag:** In der Tabelle „Export-Befehle“ eine Zeile ergänzen: `reports export-csv-review-cases --from … --to … [--employee-id …]` | Offene Prüffälle als CSV exportieren.

### Aussage: Terminal-UI-Startparameter, Systemcheck-Verhalten, Buchungszyklus (drei Schritte), Feedback-Tabelle, Domänenfehler-Tabelle
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/terminal_ui/main.py` (`run()`, `_DOMAIN_MESSAGES`, `argparse`-Definition mit `--db`, `--numpad`, `--rfid`, `--terminal-id`), `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` (`_STATUS_MESSAGES`, Reihenfolge device_event-Insert vor `BookUseCase`).
- **Bewertung:** Alle geprüften Detailaussagen (Reihenfolge Numpad→RFID→Verarbeitung, `notify(..., urgency="critical")` bei fehlgeschlagenem Systemcheck ohne Prozessabbruch, exakte Statustexte, exakte Fehlerklassen-Zuordnung) sind wortgetreu im Code wiederzufinden.

### Aussage: Rollenmodell-Tabelle (ADMIN/REVIEWER/TECH) und „Lesende Operationen … ohne Rolleneinschränkung“
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/_auth.py` (`require_admin_or_reviewer`, `require_admin_or_tech`), `employees.py`/`user_accounts.py` (`cmd_employees_list`, `cmd_users_list` ohne Rollenprüfung).
- **Bewertung:** Die beschriebene Rollenaufteilung entspricht den tatsächlichen Prüffunktionen; `employees list` und `users list` sind im Code tatsächlich ohne Rollenprüfung implementiert.

### Aussage: Domain `employees`/`cards` — Befehlstabelle und Audit-Ereignistypen
- **Status:** nicht verifizierbar (Ereignistypen), im Übrigen korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/employees.py` enthält keine `_audit(...)`-Aufrufe oder String-Literale wie `EMPLOYEE_CREATED`; die Audit-Protokollierung erfolgt vermutlich in der Anwendungsschicht (Use Cases `CreateEmployeeUseCase` etc.), die in dieser Prüfung nicht erneut eingesehen wurde.
- **Bewertung:** Die Befehle selbst (`employees list/add/deactivate`, `cards assign/replace/deactivate`) und deren Rollen (`ADMIN` für Schreiboperationen, keine Rolle für `list`) sind in `employees.py` und `register_subcommands` exakt bestätigt. Die genauen Namen der Audit-Ereignistypen (`EMPLOYEE_CREATED`, `CARD_ASSIGNED` usw.) konnten in der Präsentationsschicht nicht verifiziert werden, da dort keine entsprechenden Aufrufe sichtbar sind; eine Prüfung der Anwendungsschicht-Use-Cases wäre nötig, war aber nicht Gegenstand dieses Kapitels.

### Aussage: Domain `bookings` — Befehlstabelle, ISO-8601/UTC-Fallback für `--at`
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/bookings.py`, Funktion `_parse_dt`: `datetime.fromisoformat(value)`, bei fehlender Zeitzone `dt.replace(tzinfo=timezone.utc)`.
- **Bewertung:** Alle vier Befehle (`correct`, `supplement`, `approve-supplement`, `reject-supplement`) und ihre Beschreibungen sind im Code exakt wiederzufinden, inklusive der Aussage, dass die Rollenprüfung in der Anwendungsschicht erfolgt (keine `_require_*`-Aufrufe in `bookings.py`).

### Aussage: Domain `schedule` — Versionierung, Rollenprüfung teils CLI/teils Use-Case-Ebene
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/schedule.py`: `cmd_schedule_show` ruft `require_admin_or_reviewer(conn, user_id)` direkt auf; `cmd_schedule_set` prüft keine Rolle in der CLI (delegiert an `ManageWorkScheduleUseCase`).
- **Bewertung:** Die Fußnote im Handbuch, wonach `schedule show` die Rolle direkt in der CLI prüft und `schedule set` dies der Anwendungsschicht überlässt, ist exakt zutreffend, ebenso die Unterscheidung `ScopeType.GLOBAL`/`ScopeType.EMPLOYEE` je nach `--employee-id`.

### Aussage: Domain `system` — Befehle `check`/`backup`, Exitcodes, NAS-Synchronisation
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py`: `sys.exit(0 if result.overall_ok else 1)`; bei NAS-Sync-Fehler `sys.exit(1)` nach bereits erfolgreichem lokalen Backup.
- **Bewertung:** Beschreibung von Rollenanforderung (`ADMIN`, `TECH` via `require_admin_or_tech`), Exitcodes und dem Verhalten bei fehlgeschlagener NAS-Synchronisation stimmt exakt mit dem Code überein.

### Aussage: Domain `users` — Passwort-Hashing PBKDF2-HMAC-SHA256, 260.000 Iterationen, Bootstrap ohne Benutzer-ID
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Funktion `_hash_password`: `hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)`; `main.py`: Sonderbehandlung für `("users", "bootstrap")` vor `_resolve_user_id(args)`.
- **Bewertung:** Alle sechs Befehle der Tabelle (`bootstrap`, `add`, `list`, `deactivate`, `reactivate`, `change-role`) sowie die Aussage zum automatisch generierten Einmalpasswort (`secrets.token_urlsafe(12)`, Ausgabe „einmalig“) sind im Code bestätigt.

### Aussage: `_intervals.py` — drei Funktionen, UTC-Normalisierung, halboffene Intervalle
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/_intervals.py`: `day_interval`, `week_interval`, `month_interval`, jeweils mit `timezone.utc` und halboffenem Rückgabewert `(from_dt, to_dt)`.
- **Bewertung:** Exakte Übereinstimmung mit den beschriebenen Signaturen und Verhalten.

## Offene Punkte (nicht Gegenstand dieser Detailprüfung)

- Die genaue Bezeichnung der Audit-Ereignistypen (`EMPLOYEE_CREATED`, `CARD_ASSIGNED` usw.) konnte innerhalb der Präsentationsschicht nicht verifiziert werden; eine Prüfung der zugehörigen Use-Cases in der Anwendungsschicht wäre hierfür erforderlich.
- Der Funktionsumfang der neu entdeckten Admin-GUI (`admin_gui/main.py`) wurde nur oberflächlich gesichtet (Imports, Docstring); eine vollständige Feature-Prüfung analog zur Admin-CLI-Tabelle wurde in diesem Durchgang nicht vorgenommen.
- Für `admin_cli/` und `admin_gui/` existieren im Testverzeichnis (`tests/presentation/`) keine spezifischen Testdateien — lediglich `test_booking_loop.py` für die Terminal-UI. Dies wurde nur als Beobachtung festgehalten, nicht als Handbuch-Aussage geprüft.
