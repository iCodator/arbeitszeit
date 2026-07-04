# Prüfbericht: Handbuch Präsentationsschicht (`docs/module/handbuch_presentation.md`)

**Geprüft am:** 03.07.2026  
**Basis-Commit:** `e3fbb0d0985d7f98ba0dac5cec86a28f7d6ad302`  
**Geprüfte Quelle:** `src/arbeitszeit/presentation/` (`terminal_ui/`, `admin_cli/`)

## Gesamteinschätzung

Der überwiegende Teil des Kapitels ist gegen den Code korrekt und präzise belegt: Terminal-UI-Ablauf, Domänenfehler-Tabelle, Rollenmodell, `_intervals.py` sowie die Domains `employees`/`cards`, `bookings`, `schedule`, `system` und `users` stimmen mit den jeweiligen Quelldateien überein. [cite:6]

Die frühere Kritik an einer unvollständigen Modulzählung im Präsentationskapitel beruhte auf einem historischen Stand, in dem zusätzlich ein Untermodul `admin_gui/` betrachtet wurde. Für den aktuellen Branch `main` ist diese Kritik nicht mehr als laufender Befund heranzuziehen, da `src/arbeitszeit/presentation/` dort nur `terminal_ui/` und `admin_cli/` enthält und keine Referenzen auf `admin_gui` oder `tkinter` mehr vorhanden sind. [cite:4][cite:7][cite:8]

Der Befund zum fehlenden Befehl `reports export-csv-review-cases` bleibt davon unberührt und ist weiterhin als inhaltliche Unvollständigkeit des Handbuchkapitels zu werten. [cite:6]

## Befunde

### Aussage: „Das Paket gliedert sich in zwei eigenständige Untermodule“ (`terminal_ui/`, `admin_cli/`)
- **Status:** korrekt für den aktuellen `main`, historischer Gegenbefund nicht mehr anwendbar
- **Beleg:** Der ältere Prüfbericht wertete diese Aussage als unvollständig, weil damals zusätzlich `admin_gui/` als drittes Untermodul betrachtet wurde. [cite:6] Der neuere Prüfbericht zur Entfernung von `admin_gui/` belegt jedoch, dass `src/arbeitszeit/presentation/` im aktuellen `main` nur noch `admin_cli/` und `terminal_ui/` enthält; `admin_gui/` existiert dort nicht mehr. [cite:4] Eine repositoryweite Codesuche liefert auf `main` zudem keine Treffer für `admin_gui` oder `tkinter`. [cite:7][cite:8]
- **Bewertung:** Die frühere Beanstandung ist als historischer Befund zu kennzeichnen. Für den aktuellen Branch `main` ist die Aussage im Handbuch nicht mehr unvollständig, sondern deckungsgleich mit der vorhandenen Präsentationsschicht. [cite:4][cite:6][cite:7][cite:8]
- **Anpassungsvorschlag:** Den früheren Widerspruch nicht mehr als aktuellen Dokumentationsfehler führen, sondern ausdrücklich als historischen Stand kennzeichnen. [cite:4][cite:6]

### Aussage: Tabelle „Export-Befehle“ unter „Domain: `reports`“ listet `export-csv`, `export-pdf-day`, `export-pdf-week`, `export-pdf-month`, `export-pdf-employee`
- **Status:** inkorrekt (unvollständig)
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/reports.py`, Funktion `cmd_reports_export_csv_review_cases` sowie `register_subcommands`: `rc_csv = rsub.add_parser("export-csv-review-cases", help="Offene Prüffälle als CSV exportieren")`. [cite:6]
- **Bewertung:** Der Befehl `reports export-csv-review-cases` ist implementiert und fehlt im Handbuch weiterhin in der Export-Befehle-Tabelle. Dieser Befund ist unabhängig von der Entfernung von `admin_gui/` und bleibt gültig. [cite:6]
- **Anpassungsvorschlag:** In der Tabelle „Export-Befehle“ eine Zeile ergänzen: `reports export-csv-review-cases --from … --to … [--employee-id …]` | Offene Prüffälle als CSV exportieren. [cite:6]

### Aussage: Terminal-UI-Startparameter, Systemcheck-Verhalten, Buchungszyklus (drei Schritte), Feedback-Tabelle, Domänenfehler-Tabelle
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/terminal_ui/main.py` (`run()`, `_DOMAIN_MESSAGES`, `argparse`-Definition mit `--db`, `--numpad`, `--rfid`, `--terminal-id`), `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` (`_STATUS_MESSAGES`, Reihenfolge `device_event`-Insert vor `BookUseCase`). [cite:6]
- **Bewertung:** Alle geprüften Detailaussagen sind im Code wiederzufinden. [cite:6]

### Aussage: Rollenmodell-Tabelle (`ADMIN`/`REVIEWER`/`TECH`) und „Lesende Operationen … ohne Rolleneinschränkung“
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/_auth.py` (`require_admin_or_reviewer`, `require_admin_or_tech`), `employees.py`/`user_accounts.py` (`cmd_employees_list`, `cmd_users_list` ohne Rollenprüfung). [cite:6]
- **Bewertung:** Die Rollenaufteilung entspricht den tatsächlichen Prüffunktionen. [cite:6]

### Aussage: Domain `employees`/`cards` — Befehlstabelle und Audit-Ereignistypen
- **Status:** nicht verifizierbar (Ereignistypen), im Übrigen korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/employees.py` enthält keine `_audit(...)`-Aufrufe oder String-Literale wie `EMPLOYEE_CREATED`; die Audit-Protokollierung erfolgt laut älterem Bericht vermutlich in der Anwendungsschicht, die dort nicht erneut eingesehen wurde. [cite:6]
- **Bewertung:** Die Befehle selbst und deren Rollen sind bestätigt; die genauen Namen der Audit-Ereignistypen sind innerhalb dieses Prüfgegenstands nicht direkt aus der Präsentationsschicht verifiziert. [cite:6]

### Aussage: Domain `bookings` — Befehlstabelle, ISO-8601/UTC-Fallback für `--at`
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/bookings.py`, Funktion `_parse_dt`: `datetime.fromisoformat(value)`, bei fehlender Zeitzone `dt.replace(tzinfo=timezone.utc)`. [cite:6]
- **Bewertung:** Alle vier Befehle und die Datumslogik sind im Code bestätigt. [cite:6]

### Aussage: Domain `schedule` — Versionierung, Rollenprüfung teils CLI-, teils Use-Case-Ebene
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/schedule.py`: `cmd_schedule_show` ruft `require_admin_or_reviewer(conn, user_id)` direkt auf; `cmd_schedule_set` prüft keine Rolle in der CLI und delegiert an den Use Case. [cite:6]
- **Bewertung:** Die Dokumentation entspricht dem Code. [cite:6]

### Aussage: Domain `system` — Befehle `check`/`backup`, Exitcodes, NAS-Synchronisation
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py`: `sys.exit(0 if result.overall_ok else 1)`; bei NAS-Sync-Fehler `sys.exit(1)` nach bereits erfolgreichem lokalem Backup. [cite:6]
- **Bewertung:** Rollenanforderung, Exitcodes und Fehlerverhalten stimmen mit dem Code überein. [cite:6]

### Aussage: Domain `users` — Passwort-Hashing PBKDF2-HMAC-SHA256, 260.000 Iterationen, Bootstrap ohne Benutzer-ID
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Funktion `_hash_password`: `hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)`; `main.py`: Sonderbehandlung für `("users", "bootstrap")` vor `_resolve_user_id(args)`. [cite:6]
- **Bewertung:** Alle sechs Befehle sowie die Aussage zum automatisch generierten Einmalpasswort sind im Code bestätigt. [cite:6]

### Aussage: `_intervals.py` — drei Funktionen, UTC-Normalisierung, halboffene Intervalle
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/_intervals.py`: `day_interval`, `week_interval`, `month_interval`, jeweils mit `timezone.utc` und halboffenem Rückgabewert `(from_dt, to_dt)`. [cite:6]
- **Bewertung:** Exakte Übereinstimmung mit den beschriebenen Signaturen und Verhalten. [cite:6]

## Offene Punkte

- Die genaue Bezeichnung der Audit-Ereignistypen (`EMPLOYEE_CREATED`, `CARD_ASSIGNED` usw.) konnte innerhalb der Präsentationsschicht nicht verifiziert werden; hierfür wäre eine gesonderte Prüfung der zugehörigen Use Cases in der Anwendungsschicht erforderlich. [cite:6]
- Frühere offene Punkte zur vollständigen Feature-Prüfung der `admin_gui/` sind für den aktuellen Branch `main` gegenstandslos, da `admin_gui/` dort entfernt wurde und keine Referenzen auf `admin_gui` oder `tkinter` mehr vorhanden sind. [cite:4][cite:7][cite:8]
- Die frühere Beobachtung zu fehlenden spezifischen Tests für `admin_gui/` ist für `main` ebenfalls gegenstandslos; der Teilbefund zu fehlenden spezifischen Tests für `admin_cli/` bleibt davon unberührt, wurde in diesem Bericht jedoch nicht erneut vertieft. [cite:4][cite:6]
