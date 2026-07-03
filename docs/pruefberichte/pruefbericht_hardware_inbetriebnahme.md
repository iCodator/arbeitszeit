# Prüfbericht: Hardware-Inbetriebnahme- und Smoke-Test-Protokoll

**Geprüftes Dokument:** `docs/betrieb/hardware_inbetriebnahme_protokoll.md` (Version 1.0, Stand 2026-06-12)
**Prüfgrundlage:** `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`, `simulator.py`, `src/arbeitszeit/infrastructure/system_check.py`, `src/arbeitszeit/presentation/admin_cli/` (main.py, system.py, bookings.py, reports.py, employees.py), `src/arbeitszeit/presentation/terminal_ui/main.py`, `scripts/backup.py`, `scripts/verify_hardware.py`, Migrationen (`migrations/0001_schema.sql`, `0002_seed_defaults.sql`)

## Gesamteinschätzung

Das Dokument ist überwiegend ein auszufüllendes Formular; die meisten Einträge sind organisatorische Leerfelder ohne technischen Prüfgehalt. Die enthaltenen technischen Aussagen (Gerätedateipfade, Konfigurationsschlüssel, CLI-Befehle) sind größtenteils durch den Code belegt, jedoch enthalten Abschnitt 5 und 6 mehrere **nicht existierende CLI-Unterbefehle bzw. Kommandozeilenparameter**, die so im Repository nicht implementiert sind. Diese Abweichungen sind sachlich relevant, da sie bei tatsächlicher Nutzung des Protokolls zu Fehlbedienung führen würden.

---

### Abschnitt 2.2 — Gerätedateien (Linux)

- **Aussage:** „Die Zuordnung der Gerätedateien ist durch `evtest` oder vergleichbare Werkzeuge zu prüfen.“
  **Status:** nicht verifizierbar
  **Beleg:** Kein Verweis auf `evtest` im Repository; `scripts/verify_hardware.py` implementiert stattdessen eine eigene interaktive Geräteauflistung (`list_input_devices()`, Zeilen ca. 95–115) und einen eigenen Smoke-Test.
  **Bewertung:** `evtest` ist ein systemweites Standardwerkzeug außerhalb des Repositoriums; seine Eignung kann nicht aus dem Code verifiziert werden, ist aber auch nicht widerlegt. Das im Repository vorhandene, speziell für dieses Projekt gebaute Werkzeug `scripts/verify_hardware.py` wird im Protokoll nicht erwähnt, obwohl es exakt dem hier beschriebenen Zweck dient.
  **Anpassungsvorschlag:** Ergänzend auf `scripts/verify_hardware.py --list` bzw. `scripts/verify_hardware.py --numpad … --rfid …` verweisen, da dieses Skript projektspezifisch für Gerätezuordnung und Lese-Test entwickelt wurde (`scripts/verify_hardware.py`, Docstring Zeilen 1–22).

- **Aussage (Formularfeld):** „Leserechte geprüft“ / Gerätedatei `/dev/input/event____`
  **Status:** nicht zutreffend (organisatorisch)
  **Beleg:** Auszufüllendes Formularfeld ohne feste Werte.
  **Bewertung:** Reine Vorlage, keine prüfbare technische Aussage.

---

### Abschnitt 3 — Systemkonfiguration arbeitszeit

- **Aussage:** Konfigurationspunkt „Pfad zur SQLite-Datenbank (`--db`)“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/main.py`, Parameter `--db` (Zeile ca. 44–50); `src/arbeitszeit/presentation/terminal_ui/main.py`, `parser.add_argument("--db", required=True, type=Path)` (Zeile ca. 133).
  **Bewertung:** Der Parametername stimmt exakt mit beiden CLI-Einstiegspunkten überein.

- **Aussage:** Konfigurationspunkt „Terminal-ID (`--terminal-id`)“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/terminal_ui/main.py`, `parser.add_argument("--terminal-id", required=True, type=int)` (Zeile ca. 136).
  **Bewertung:** Parametername und Pflichtstatus stimmen überein.

- **Aussage:** Konfigurationspunkt „`backup.backup_dir` (system_config)“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py`, Abfrage `config_key = 'backup.backup_dir'` (Funktion `cmd_system_backup`); `scripts/init_db.py`, `_DEPLOYMENT_KEYS = ("backup.backup_dir", "export.export_dir")`.
  **Bewertung:** Schlüssel existiert exakt so in system_config und wird für das Backup-Zielverzeichnis verwendet.

- **Aussage:** Konfigurationspunkt „`export.export_dir` (system_config)“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py`, Abfrage `config_key = 'export.export_dir'`; `scripts/init_db.py`, `_DEPLOYMENT_KEYS`.
  **Bewertung:** Schlüssel ist im Code belegt.

- **Aussage:** Konfigurationspunkt „`time_monitor.jump_threshold_seconds`“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/infrastructure/time_monitor.py`, Abfrage `config_key = 'time_monitor.jump_threshold_seconds'` (Zeile ca. 92), Docstring der Funktion `load_threshold_from_config` (Zeile 86).
  **Bewertung:** Schlüssel und Verwendungszweck (Zeitsprung-Erkennung) stimmen mit dem Code überein.

- **Aussage:** Konfigurationspunkt „NAS-Pfad für Backup (falls genutzt)“
  **Status:** korrekt
  **Beleg:** `migrations/0002_seed_defaults.sql`, Zeilen 31–32, Seed-Werte für `backup.nas_enabled` und `backup.nas_path`; `src/arbeitszeit/presentation/admin_cli/system.py`, Abfragen dieser Schlüssel in `cmd_system_backup`.
  **Bewertung:** Beide Konfigurationsschlüssel existieren und werden für die NAS-Synchronisation ausgewertet.

---

### Abschnitt 4 — Smoke-Test Terminal-UI

- **Aussage:** „Terminal-UI-Startbefehl: `python -m arbeitszeit.presentation.terminal_ui.main --db … --terminal-id …`“
  **Status:** nicht verifizierbar (unvollständig, aber nicht falsch)
  **Beleg:** `src/arbeitszeit/presentation/terminal_ui/main.py`, `if __name__ == "__main__":`-Block (Zeilen 132–142): Pflichtparameter sind `--db`, `--numpad`, `--rfid`, `--terminal-id`.
  **Bewertung:** Die im Protokoll gezeigte Befehlszeile ist mit „…“ verkürzt und lässt offen, ob `--numpad`/`--rfid` gemeint mit „…“ sind. Als Kurzform ist sie nicht falsch, aber unvollständig gegenüber den tatsächlich erforderlichen Parametern.
  **Anpassungsvorschlag:** Vollständige Beispielzeile mit allen vier Pflichtparametern (`--db`, `--numpad`, `--rfid`, `--terminal-id`) ergänzen, analog zu `src/arbeitszeit/presentation/terminal_ui/main.py` Zeilen 133–136.

- **Aussage (Abschnitt 4.3):** „Testbuchungen im Admin-CLI sichtbar (`bookings list`)“
  **Status:** inkorrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/bookings.py`, Funktion `register_subcommands` (Zeilen 159–182): registrierte Unterbefehle sind ausschließlich `correct`, `supplement`, `approve-supplement`, `reject-supplement`. Ein Unterbefehl `list` existiert nicht.
  **Bewertung:** Der im Protokoll genannte Befehl `bookings list` ist im Admin-CLI nicht implementiert und würde bei Ausführung mit einem Argparse-Fehler abgebrochen. Buchungsübersichten werden stattdessen über `reports`-Unterbefehle (z. B. `open-bookings`, `corrections`, `supplements`) bereitgestellt.
  **Anpassungsvorschlag:** Verweis auf tatsächlich vorhandene Befehle korrigieren, z. B. `reports open-bookings` (`src/arbeitszeit/presentation/admin_cli/reports.py`, Zeile 306) statt `bookings list`.

- **Aussage:** „device_events-Einträge vorhanden“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/infrastructure/db/repositories/device_event.py`, Klasse `SQLiteDeviceEventRepository`, Methode `add()`; Tabelle `device_events` in `migrations/0001_schema.sql` und `migrations/0005_time_bookings_device_event_id.sql`.
  **Bewertung:** Die Tabelle und die Schreiblogik existieren tatsächlich im System.

- **Aussage:** „system_events ohne Fehler während des Tests“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/infrastructure/system_check.py`, Funktion `_write_event()` (schreibt `SELFTEST_OK`/`SELFTEST_FAIL` in `system_events`); `src/arbeitszeit/presentation/terminal_ui/main.py`, Funktion `_log_system_event()` (schreibt `APPLICATION_ERROR`-Einträge).
  **Bewertung:** Die Tabelle `system_events` wird tatsächlich sowohl von Systemcheck als auch Terminal-UI für Fehler-/Statusprotokollierung verwendet.

---

### Abschnitt 5 — Smoke-Test Admin-CLI

- **Aussage:** „Systemcheck: `python -m arbeitszeit.infrastructure.system_check --db …`“
  **Status:** inkorrekt
  **Beleg:** `src/arbeitszeit/infrastructure/system_check.py` enthält keinen `if __name__ == "__main__":`-Block und keine eigenständige CLI-Argumentverarbeitung. Der Systemcheck ist ausschließlich über den Admin-CLI-Unterbefehl erreichbar: `src/arbeitszeit/presentation/admin_cli/system.py`, Funktion `register_subcommands()`, `ssub.add_parser("check", …)`, aufgerufen über `src/arbeitszeit/presentation/admin_cli/main.py --db … --user-id … system check`.
  **Bewertung:** Der im Protokoll angegebene Befehl `python -m arbeitszeit.infrastructure.system_check --db …` kann nicht ausgeführt werden, da das Modul nicht als eigenständiges Skript aufrufbar ist (kein `__main__`-Guard). Der korrekte Aufruf lautet `python -m arbeitszeit.presentation.admin_cli.main --db … --user-id … system check`.
  **Anpassungsvorschlag:** Befehl ersetzen durch `python -m arbeitszeit.presentation.admin_cli.main --db <pfad> --user-id <id> system check`, siehe `src/arbeitszeit/presentation/admin_cli/system.py`, Funktion `cmd_system_check`.

- **Aussage:** „Mitarbeiterliste: `python -m arbeitszeit.presentation.admin_cli.main --db … employees list`“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/employees.py`, Zeile 138: `emp_sub.add_parser("list", help="Alle Mitarbeiter auflisten")`.
  **Bewertung:** Unterbefehl existiert exakt wie beschrieben.

- **Aussage:** „Buchungsübersicht Test-Mitarbeiter: `… bookings list --employee …`“
  **Status:** inkorrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/bookings.py`, Zeilen 159–182: kein `list`-Unterbefehl unter `bookings` vorhanden (siehe auch obige Bewertung zu Abschnitt 4.3).
  **Bewertung:** Wie oben – dieser Befehl existiert nicht in der aktuellen CLI-Struktur.
  **Anpassungsvorschlag:** Ersetzen durch einen tatsächlich vorhandenen Reporting-Befehl, z. B. `reports open-bookings` oder `reports corrections --from … --to …` (`src/arbeitszeit/presentation/admin_cli/reports.py`, Zeilen 306–321).

- **Aussage:** „CSV-Export: `… reports export csv …`“
  **Status:** inkorrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/reports.py`, Zeile 279: der registrierte Unterbefehl heißt `export-csv` (mit Bindestrich), nicht `export csv` (zwei getrennte Wörter).
  **Bewertung:** Mit der im Protokoll angegebenen Syntax würde argparse den Unterbefehl nicht erkennen; korrekt ist ein einzelnes Token `export-csv`.
  **Anpassungsvorschlag:** Befehl korrigieren zu `reports export-csv --employee … --from … --to …` gemäß `src/arbeitszeit/presentation/admin_cli/reports.py`, Zeile 279.

- **Aussage:** „PDF-Export: `… reports export pdf …`“
  **Status:** inkorrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/reports.py`, Zeilen 289–300: registrierte Unterbefehle sind `export-pdf-day`, `export-pdf-week`, `export-pdf-month`, `export-pdf-employee`. Ein generischer Befehl `export pdf` existiert nicht.
  **Bewertung:** Wie beim CSV-Export ist die im Protokoll gezeigte Schreibweise nicht lauffähig; zudem muss zwingend einer der vier spezifischen Report-Typen gewählt werden.
  **Anpassungsvorschlag:** Befehl präzisieren, z. B. `reports export-pdf-day --employee … --date …` (`src/arbeitszeit/presentation/admin_cli/reports.py`, Zeile 289).

---

### Abschnitt 6 — Smoke-Test Backup und NAS

- **Aussage:** „Lokales Backup erstellt: `python scripts/backup.py --db … --backup-dir …`“
  **Status:** korrekt
  **Beleg:** `scripts/backup.py`, Docstring Zeilen 5–6 sowie `argparse`-Definition der Parameter `--db` und `--backup-dir` (Zeilen 24–33).
  **Bewertung:** Befehl und Parameter stimmen exakt mit dem Skript überein.

- **Aussage:** „NAS-Spiegelung (falls konfiguriert): `python scripts/backup.py … --nas-path …`“
  **Status:** inkorrekt
  **Beleg:** `scripts/backup.py`, `argparse.ArgumentParser`-Definition (Zeilen 22–41): Es existiert kein Parameter `--nas-path`. Der NAS-Sync wird ausschließlich automatisch über die in der Datenbank hinterlegten `system_config`-Werte `backup.nas_enabled` und `backup.nas_path` gesteuert (Zeilen 52–56, Aufruf `service.run(nas_path=nas_path if nas_enabled and nas_path else None)`, Zeile 60).
  **Bewertung:** Der im Protokoll genannte Kommandozeilenparameter `--nas-path` existiert nicht in `scripts/backup.py`. Die NAS-Synchronisation wird nicht über einen CLI-Parameter, sondern über die Systemkonfiguration gesteuert.
  **Anpassungsvorschlag:** Hinweis korrigieren: NAS-Synchronisation erfolgt automatisch, wenn `backup.nas_enabled=true` und `backup.nas_path` in `system_config` gesetzt sind; kein zusätzlicher CLI-Parameter erforderlich (Beleg: `scripts/backup.py`, Zeilen 52–60).

---

### Abschnitt 7–9 — Abweichungen, Abnahme, Wiederholte Tests

- **Aussagen:** Unterschriftenfelder, Verantwortlichkeiten, Fristen für Maßnahmen, Freitextfelder für Abweichungen.
  **Status:** nicht zutreffend (organisatorisch)
  **Beleg:** Reine Formularfelder ohne technischen Aussagegehalt.
  **Bewertung:** Betrifft ausschließlich betriebliche Verantwortlichkeiten und Vorlagenfelder; keine Prüfung gegen Code möglich oder erforderlich.

---

### Abschnitt 10 — Bezug zu weiteren Dokumenten

- **Aussage:** Verweis auf `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`
  **Status:** korrekt
  **Beleg:** Datei existiert im Repository unter `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`.
  **Bewertung:** Verweis ist zutreffend, Datei ist vorhanden.

- **Aussage:** Verweis auf `docs/datenschutz/vvt_arbeitszeit_v1.md`
  **Status:** korrekt
  **Beleg:** Datei existiert im Repository unter `docs/datenschutz/vvt_arbeitszeit_v1.md`.
  **Bewertung:** Verweis ist zutreffend.

- **Aussage:** Verweis auf `docs/betrieb/rollenzuweisung.md`
  **Status:** korrekt
  **Beleg:** Datei existiert im Repository unter `docs/betrieb/rollenzuweisung.md` (zusätzlich existiert eine ältere Formularvariante `rollenzuweisung_arbeitszeit_v1_0.md`).
  **Bewertung:** Verweis ist zutreffend; die referenzierte Datei ist die aktuelle, vollständige Fassung.

---

## Zusammenfassung der Kernbefunde

1. Der Befehl `python -m arbeitszeit.infrastructure.system_check --db …` (Abschnitt 5) ist **nicht ausführbar** – das Modul besitzt keinen `__main__`-Einstiegspunkt (`src/arbeitszeit/infrastructure/system_check.py`).
2. Die Befehle `bookings list` (Abschnitte 4.3 und 5), `reports export csv` und `reports export pdf` (Abschnitt 5) entsprechen **nicht** der tatsächlichen argparse-Unterbefehlsstruktur (`src/arbeitszeit/presentation/admin_cli/bookings.py`, `reports.py`).
3. Der Parameter `--nas-path` für `scripts/backup.py` (Abschnitt 6) **existiert nicht**; NAS-Sync erfolgt automatisch über `system_config`.
4. Alle geprüften Konfigurationsschlüssel (`backup.backup_dir`, `export.export_dir`, `time_monitor.jump_threshold_seconds`, `backup.nas_enabled`, `backup.nas_path`) sind im Code korrekt belegt.
5. Die referenzierten Begleitdokumente in Abschnitt 10 existieren im Repository.
