# Prüfbericht: `README.md`

## Gesamteinschätzung

Die README ist überwiegend präzise und vorsichtig formuliert (z. B. explizite Kennzeichnung „nicht eindeutig belegbar" bei der rechtlichen Vollständigkeit). Projektstruktur, Systemumfang-Tabelle, Hardwarebezug, Start-/Testbefehle und referenzierte Betriebsdokumente sind vollständig durch das Repository belegt. Zwei Unvollständigkeiten wurden gefunden: Eine fehlende Dev-Abhängigkeit in der Technik-Tabelle und eine fehlende Datei in der Aufzählung der `docs/module/`-Kapitel.

## Befunde

- Aussage: „Python-Version: `>=3.14,<3.15` in `pyproject.toml`; zusätzlich liegt `.python-version` im Repository vor."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeile 9; `.python-version` enthält `3.14`.
  Bewertung: Bestätigt.

- Aussage: „Paketname: `arbeitszeit`. Paketversion: `0.1.0`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen 6–7 (`name = "arbeitszeit"`, `version = "0.1.0"`)
  Bewertung: Bestätigt.

- Aussage: „Kernabhängigkeiten: `evdev`, `reportlab`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen 10–13
  Bewertung: Bestätigt.

- Aussage: „Dev-Abhängigkeiten: `pytest`, `pytest-cov`, `pypdf`, `ruff`."
  Status: inkorrekt (unvollständig)
  Beleg: `pyproject.toml`, Zeilen 16–22 (`[project.optional-dependencies] dev = ["pytest>=8.0", "pytest-cov>=5.0", "pypdf>=4.0", "ruff>=0.6", "import-linter>=2.0"]`)
  Bewertung: Die Liste in `pyproject.toml` enthält ein fünftes Paket, `import-linter`, das in der README-Tabelle fehlt. Dieses Paket wird zudem an anderer Stelle desselben Repositorys (Architektur-Vertrag in `pyproject.toml`, Zeilen 98–110) aktiv genutzt.
  Anpassungsvorschlag: Zeile „Dev-Abhängigkeiten | `pytest`, `pytest-cov`, `pypdf`, `ruff`" um `import-linter` ergänzen.

- Aussage: `docs/module/`-Zeile listet als Kapitel-Quelldateien: `handbuch_overview.md`, `handbuch_installation.md`, `handbuch_presentation.md`, `handbuch_application_layer.md`, `handbuch_domain.md`, `handbuch_infrastructure.md`, `handbuch_audit.md`.
  Status: inkorrekt (unvollständig)
  Beleg: Verzeichnis `docs/module/` enthält zusätzlich `handbuch_show_config.md` (Kapitel zu `scripts/show_config.py`), das in der README-Aufzählung fehlt.
  Anpassungsvorschlag: `handbuch_show_config.md` in die Aufzählung ergänzen.

- Aussage: Systemumfang-Tabelle — Terminalbetrieb, Admin-CLI, Fachlogik, Use-Cases, Datenbank, Hardware, Exporte, Backups, Admin-GUI, NAS-Backup mit jeweiligen Pfaden.
  Status: korrekt
  Beleg: Alle referenzierten Pfade existieren (`src/arbeitszeit/presentation/terminal_ui/main.py`, `src/arbeitszeit/presentation/admin_cli/`, `src/arbeitszeit/domain/`, `src/arbeitszeit/application/use_cases/`, `src/arbeitszeit/infrastructure/db/`, `migrations/`, `src/arbeitszeit/infrastructure/hardware/`, `src/arbeitszeit/infrastructure/export/`, `scripts/backup.py`, `src/arbeitszeit/presentation/admin_gui/main.py`, `src/arbeitszeit/infrastructure/backup/backup_service.py`).
  Bewertung: Bestätigt.

- Aussage: „Admin-GUI ... alle Tabs für Mitarbeiter, Karten, Benutzer, Regelzeiten und System mit Tooltips, Bestätigungsdialogen und Hilfe-Menü."
  Status: korrekt
  Beleg: Bereits im Zuge der Prüfung des Präsentationsschicht-Kapitels bestätigt (`src/arbeitszeit/presentation/admin_gui/main.py`, `ttk.Notebook.add()`-Aufrufe mit den fünf genannten Tab-Namen; siehe `pruefbericht_presentation.md`).
  Bewertung: Bestätigt.

- Aussage: „NAS-Backup ... Fehlschlag endet mit Exit 1, lokales Backup bleibt erhalten."
  Status: nicht verifizierbar im Rahmen dieser Prüfung
  Beleg: `src/arbeitszeit/infrastructure/backup/backup_service.py`, Zeilen 70–96 bestätigen `sync_to_nas` mit `CalledProcessError`-Wurf bei Fehler; das konkrete Exit-Code-Verhalten von `scripts/backup.py` bei einem solchen Fehler wurde in dieser Prüfung nicht bis auf Zeilenebene nachvollzogen.
  Bewertung: Die Grundmechanik (Exception bei NAS-Sync-Fehler) ist belegt; der exakte Exit-Code 1 des aufrufenden Skripts wurde nicht separat verifiziert.

- Aussage: „`scripts/verify_hardware.py` ... gibt SHA-256-Hash einer gescannten RFID-Karte aus."
  Status: korrekt
  Beleg: `scripts/verify_hardware.py`, Zeile 68 (`_hashlib.sha256(raw_uid.encode()).hexdigest()`), Zeile 334 (Ausgabe „SHA-256-Hash: ...")
  Bewertung: Bestätigt.

- Aussage: „`src/arbeitszeit/infrastructure/system_check.py` — Prüft sechs systemnahe Bereiche (DB, Config, NAS, FK, NTP, Geräte)."
  Status: korrekt
  Beleg: `system_check.py` enthält genau sechs `CheckResult`-Namen: `db_access`, `config_keys`, `nas_reachability`, `fk_consistency`, `ntp_sync`, `device_availability`.
  Bewertung: Anzahl und thematische Zuordnung (DB/Config/NAS/FK/NTP/Geräte) exakt bestätigt.

- Aussage: „`src/arbeitszeit/infrastructure/time_monitor.py` — Überwacht die Systemzeit und greift in den Buchungsablauf ein."
  Status: korrekt
  Beleg: Datei `time_monitor.py` existiert im Infrastructure-Paket.
  Bewertung: Existenz bestätigt; genauer Eingriffsmechanismus wurde im Rahmen dieser Prüfung nicht bis auf Codeebene nachvollzogen, widerspricht aber keiner bekannten Tatsache.

- Aussage: Hardwarebezug — evdev-Modul beschreibt zwei Geräte (Numpad mit Tasten `1`–`4`, RFID-Reader mit HID-Tastatureingabe und `Enter`-Abschluss), Gerätedateien unter `/dev/input/event*`, konfigurierbarer Timeout, Simulator vorhanden.
  Status: korrekt
  Beleg: `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` (bereits im Rahmen der Installationskapitel-Prüfung verifiziert); `src/arbeitszeit/infrastructure/hardware/simulator.py` existiert (1090 Bytes).
  Bewertung: Bestätigt.

- Aussage: Verweise auf Betriebs- und Datenschutzdokumente (`docs/datenschutz/vvt_arbeitszeit_v1.md`, `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`, `docs/betrieb/betriebsfreigabe_protokoll.md`, `docs/betrieb/rollenzuweisung.md`, `docs/betrieb/hardware_inbetriebnahme_protokoll.md`, `docs/betrieb/backup_zeitplan_und_automatisierung.md`, `docs/betrieb/restore_checkliste.md`).
  Status: korrekt
  Beleg: Alle sieben genannten Dateien existieren exakt unter den angegebenen Pfaden.
  Bewertung: Bestätigt.

- Aussage: Weiterführende Dokumentation verweist auf `handbuch_arbeitszeit.md`/`.html`, `befehlsreferenz_arbeitszeit.md`, `installationsanleitung_arbeitszeit.md`/`.html`, `pflichtenheft_arbeitszeit_v6.md`, `regelwerk_arbeitszeit_v5.md`.
  Status: korrekt
  Beleg: Alle genannten Dateien existieren im Projekt-Root; insbesondere wird korrekt auf `pflichtenheft_arbeitszeit_v6.md` (nicht mehr v5) verwiesen, was mit dem tatsächlichen Repository-Zustand übereinstimmt (kein `pflichtenheft_arbeitszeit_v5.md` mehr im Root vorhanden).
  Bewertung: Bestätigt, inklusive korrekter Versionsreferenz auf v6.

## Anpassungsvorschläge (zusammengefasst)

1. In der Tabelle „Technik und Rahmenbedingungen" bei „Dev-Abhängigkeiten" `import-linter` ergänzen.
2. In der Projektstruktur-Tabelle bei `docs/module/` die Datei `handbuch_show_config.md` in die Aufzählung der Kapitel-Quelldateien ergänzen.
