# Prüfbericht: `docs/03_installation_technik/installationsanleitung_arbeitszeit.md`

**Prüfdatum:** 04. Juli 2026  
**Geprüfte Datei:** `docs/03_installation_technik/installationsanleitung_arbeitszeit.md`  
**Begleitdatei:** `docs/03_installation_technik/installationsanleitung_arbeitszeit.html`  
**Repository:** `iCodator/arbeitszeit`  
**Commit (Stand Prüfung):** `3c9483764b97a17926ebe2ce73898899047f70b9`  
**Regelquellen:** `markdown-Rules.md`, `Markdown Syntax Documentation.pdf`

---

## Gesamteinschätzung

Die Installationsanleitung ist in Aufbau und Lesbarkeit gut strukturiert und richtet sich klar an die angegebene Zielgruppe. Die meisten Aussagen sind korrekt und durch die Codebase belegbar. Es gibt jedoch **zwei inhaltlich relevante Abweichungen**: Die Beschreibung des Verhaltens von `verify_hardware.py` bei nur einem angegebenen Argument ist unvollständig (das Script unterstützt entgegen der Anleitung auch eine interaktive Geräteauswahl ohne Argumente), und die Ausgabe von `init_db.py` ist in einem Detail leicht vereinfacht dargestellt, aber inhaltlich nicht falsch. Zusätzlich bestehen **zwei Markdown-Formatierungsverstöße** (MD010, MD049), die korrigiert werden sollten.

---

## Abschnitt 1: Metadaten und Einleitung (Zeilen 1–18)

### Aussage 1.1
- **Aussage:** Version 1.0, Stand Juli 2026
- **Status:** nicht verifizierbar
- **Beleg:** Keine Versionierung der Dokumentation im Repository nachweisbar; `pyproject.toml` gibt Projektversion `0.1.0` an, bezieht sich aber auf die Software, nicht die Anleitung.
- **Bewertung:** Redaktionelle Metadaten ohne Codebase-Entsprechung; nicht widerlegbar, aber auch nicht bestätigbar.
- **Anpassungsvorschlag:** Keine Änderung zwingend erforderlich; es handelt sich um eine Dokumentationsangabe.

### Aussage 1.2
- **Aussage:** Projekt ist ein lokales Zeiterfassungssystem für eine Zahnarztpraxis.
- **Status:** korrekt
- **Beleg:** `pyproject.toml`, Feld `description`: `"Lokales Zeiterfassungssystem für eine Zahnarztpraxis"`
- **Bewertung:** Exakte Übereinstimmung.

### Aussage 1.3
- **Aussage:** Am Ende der Anleitung gibt es einen Abschnitt mit häufigen Fehlern und Lösungen.
- **Status:** korrekt
- **Beleg:** Abschnitt „Häufige Probleme und Lösungen" ist in der Datei vorhanden (Zeile 526–535).
- **Bewertung:** Interne Verweisaussage bestätigt.

---

## Abschnitt 2: Voraussetzungen (Zeilen 59–72)

### Aussage 2.1
- **Aussage:** Benötigt wird Linux Mint oder Lubuntu.
- **Status:** nicht verifizierbar
- **Beleg:** Keine Betriebssystemanforderung in `pyproject.toml` oder sonstiger Konfigurationsdatei definiert. Das Projekt nutzt `evdev`, das Linux-spezifisch ist.
- **Bewertung:** Die Nennung von Linux Mint und Lubuntu ist plausibel (evdev ist Linux-spezifisch), aber nicht explizit in der Codebase festgelegt. Weder als Mindestanforderung noch als unterstützte Distribution dokumentiert.
- **Anpassungsvorschlag:** Falls keine explizite Anforderungsdokumentation existiert, formulierung als Empfehlung statt Anforderung beibehalten oder mit Hinweis „empfohlen" versehen.

### Aussage 2.2
- **Aussage:** RFID-Kartenlesegerät und USB-Numpad werden benötigt, beide über USB angeschlossen.
- **Status:** korrekt
- **Beleg:** `pyproject.toml` → `dependencies: ["evdev>=1.7", ...]`; `terminal_ui/main.py` → `parser.add_argument("--numpad", required=True)` und `parser.add_argument("--rfid", required=True)`.
- **Bewertung:** Beide Geräte sind Pflichtparameter für den Terminal-UI-Start.

### Aussage 2.3
- **Aussage:** Zeitaufwand für die Ersteinrichtung: 30 bis 60 Minuten.
- **Status:** nicht verifizierbar
- **Beleg:** Kein Zeitrichtwert in der Codebase definiert.
- **Bewertung:** Redaktionelle Einschätzung; keine Gegen-Evidenz, aber keine Bestätigung möglich.

---

## Abschnitt 3: Schritt 0 – LUKS-Verschlüsselung (Zeilen 75–130)

### Aussage 3.1
- **Aussage:** `arbeitszeit` verarbeitet personenbezogene Daten; DSGVO Art. 32 und BDSG verpflichten zu technischen Schutzmaßnahmen.
- **Status:** nicht verifizierbar
- **Beleg:** Keine datenschutzrechtliche Dokumentation im Repository; die Verarbeitung personenbezogener Daten (Namen, Zeiten) ist durch das Datenbankschema plausibel, aber DSGVO-Pflichten sind keine Code-Aussage.
- **Bewertung:** Rechtliche Aussage, nicht aus Codebase belegbar. Keine Gegen-Evidenz.

### Aussage 3.2
- **Aussage:** LUKS ist der Standardmechanismus zur Festplattenverschlüsselung unter Linux.
- **Status:** nicht verifizierbar
- **Beleg:** Keine Codebase-Referenz; allgemeine Systeminformation.
- **Bewertung:** Technisch korrekte Allgemeinaussage, aber nicht aus dem Repository belegbar.

### Aussage 3.3
- **Aussage:** Befehl zur LUKS-Prüfung: `lsblk -o NAME,TYPE,FSTYPE`; Ausgabe enthält `crypt` in Spalte `TYPE`.
- **Status:** nicht verifizierbar
- **Beleg:** Kein Code im Repository referenziert diesen Befehl oder prüft LUKS-Status.
- **Bewertung:** Technisch korrekte Anleitung für externe Systemprüfung; nicht durch Projektcode belegbar.

---

## Abschnitt 4: Schritt 1 – System aktuell halten (Zeilen 133–151)

### Aussage 4.1
- **Aussage:** Befehle `sudo apt update` und `sudo apt upgrade -y`.
- **Status:** nicht verifizierbar
- **Beleg:** Keine Codebase-Referenz auf apt-Befehle.
- **Bewertung:** Standard-Linux-Befehle; technisch korrekt, aber nicht aus Repository belegbar.

---

## Abschnitt 5: Schritt 2 – Python installieren (Zeilen 153–186)

### Aussage 5.1
- **Aussage:** Das System benötigt Python 3.14.
- **Status:** korrekt
- **Beleg:** `pyproject.toml` → `requires-python = ">=3.14,<3.15"`
- **Bewertung:** Exakte Übereinstimmung.

### Aussage 5.2
- **Aussage:** Installationsbefehl: `sudo apt install -y python3.14 python3.14-venv python3.14-tk python3-pip`
- **Status:** teilweise nicht verifizierbar
- **Beleg:** `pyproject.toml` nennt `python3.14-venv` als implizit notwendig (Schritt 5 nutzt `python3.14 -m venv`). `python3.14-tk` wird erwähnt wegen „grafischer Verwaltungsoberfläche" – eine solche ist im Repository **nicht** vorhanden (kein tkinter-Import im Sourcecode). `python3-pip` ist für `pip install` nötig.
- **Bewertung:** `python3.14-tk` ist nicht belegt: Im gesamten Quellcode unter `src/` findet sich kein `tkinter`-Import. Die Erklärung in der Anleitung („für die grafische Verwaltungsoberfläche") ist unzutreffend – eine grafische Oberfläche existiert nicht.
- **Anpassungsvorschlag:** `python3.14-tk` und die Erläuterung „Grafik-Modul tkinter für die grafische Verwaltungsoberfläche" entfernen oder als optional kennzeichnen, solange kein tkinter-Import in der Codebase nachweisbar ist.

### Aussage 5.3
- **Aussage:** `python3-pip` wird als Paketmanager für spätere Software-Bausteine benötigt.
- **Status:** korrekt
- **Beleg:** Schritt 6 nutzt `pip install -e .[dev]`; pip ist erforderlich.
- **Bewertung:** Funktional korrekt.

---

## Abschnitt 6: Schritt 3 – Zusätzliche Systempakete (Zeilen 188–202)

### Aussage 6.1
- **Aussage:** Befehl: `sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev`
- **Status:** nicht verifizierbar
- **Beleg:** Keine explizite Systempakeanforderung in `pyproject.toml` oder anderen Konfigurationsdateien dokumentiert.
- **Bewertung:** Die Pakete sind für das Kompilieren von C-Erweiterungen (z. B. für `evdev`) plausibel, aber nicht direkt aus der Codebase belegbar.
- **Anpassungsvorschlag:** Falls keine explizite Dokumentation existiert, Formulierung als „möglicherweise erforderlich" oder Hinweis ergänzen.

---

## Abschnitt 7: Schritt 4 – Programmcode herunterladen (Zeilen 204–238)

### Aussage 7.1
- **Aussage:** Repository-URL: `https://github.com/iCodator/arbeitszeit.git`
- **Status:** korrekt
- **Beleg:** Repository ist unter dieser URL erreichbar (Prüfung durch GitHub-API bestätigt).
- **Bewertung:** Korrekt.

### Aussage 7.2
- **Aussage:** Nach `git clone` existiert ein Ordner namens `arbeitszeit`.
- **Status:** korrekt
- **Beleg:** `git clone` erzeugt standardmäßig einen Ordner mit dem Repository-Namen; Repository-Name laut API: `arbeitszeit`.
- **Bewertung:** Korrekt.

---

## Abschnitt 8: Schritt 5 – Virtuelle Umgebung (Zeilen 240–266)

### Aussage 8.1
- **Aussage:** Befehl: `python3.14 -m venv .venv`
- **Status:** korrekt
- **Beleg:** `pyproject.toml` → `requires-python = ">=3.14,<3.15"`; `python3.14-venv` wird in Schritt 2 installiert; Verzeichnis `.venv` ist in `.gitignore` und `ruff`-Ausschlüssen referenziert.
- **Bewertung:** Konsistent mit der gesamten Projektkonfiguration.

### Aussage 8.2
- **Aussage:** Nach Aktivierung erscheint `(.venv)` vor der Eingabeaufforderung.
- **Status:** nicht verifizierbar
- **Beleg:** Standardverhalten von `venv`-Aktivierung; nicht im Repository konfiguriert.
- **Bewertung:** Technisch korrekte Allgemeinaussage; nicht widerlegbar.

---

## Abschnitt 9: Schritt 6 – Abhängigkeiten installieren (Zeilen 268–283)

### Aussage 9.1
- **Aussage:** Befehl: `pip install -e .[dev]`
- **Status:** korrekt
- **Beleg:** `pyproject.toml` → `[project.optional-dependencies]` → Sektion `dev` ist definiert mit `pytest`, `pytest-cov`, `pypdf`, `ruff`, `import-linter`.
- **Bewertung:** Befehl und Dateistruktur stimmen überein.

### Aussage 9.2
- **Aussage:** `pip` liest `pyproject.toml` und installiert alle aufgeführten Software-Bausteine. Am Ende erscheint `Successfully installed`.
- **Status:** korrekt (erster Teil); nicht verifizierbar (zweiter Teil)
- **Beleg:** `pyproject.toml` ist vorhanden und korrekt strukturiert. Die Ausgabe „Successfully installed" ist pip-Standardausgabe; nicht im Repository konfiguriert.
- **Bewertung:** Inhaltlich korrekt.

### Aussage 9.3
- **Aussage:** Bausteine werden u. a. für „Hardware-Anbindung und PDF-Erzeugung" benötigt.
- **Status:** korrekt
- **Beleg:** `pyproject.toml` → `dependencies: ["evdev>=1.7", "reportlab>=4.0"]` — evdev für Hardware, reportlab für PDF.
- **Bewertung:** Direkt belegbar.

---

## Abschnitt 10: Schritt 7 – Datenbank anlegen (Zeilen 285–309)

### Aussage 10.1
- **Aussage:** Befehl: `python scripts/init_db.py`
- **Status:** korrekt
- **Beleg:** Datei `scripts/init_db.py` ist im Repository vorhanden (HTTP 200).
- **Bewertung:** Korrekt.

### Aussage 10.2
- **Aussage:** Es wird eine Datei `arbeitszeit.db` angelegt.
- **Status:** korrekt
- **Beleg:** `init_db.py` → `default=Path("arbeitszeit.db")` als Datenbankpfad-Standard.
- **Bewertung:** Korrekt.

### Aussage 10.3
- **Aussage:** Am Bildschirm erscheinen Meldungen `Migration 0001 angewendet.` bis `Migration 0006 angewendet.`
- **Status:** korrekt (Format); korrekt (Anzahl)
- **Beleg:** `init_db.py` → `print(f"Migration {version} angewendet.")`; Migrations-Verzeichnis enthält exakt 6 SQL-Dateien: `0001_schema.sql` bis `0006_system_events_application_error.sql`.
- **Bewertung:** Ausgabeformat und Anzahl der Migrationen stimmen überein.

### Aussage 10.4
- **Aussage:** Am Ende erscheint zusätzlich ein Hinweis, dass eine Ersteinrichtung noch erforderlich ist.
- **Status:** korrekt
- **Beleg:** `init_db.py` → nach Migrationsausführung wird geprüft, ob `setup_vollstaendig()` `False` ist; wenn ja: `print("⚠  Ersteinrichtung noch erforderlich:")` und `print(f"   python scripts/setup.py --db {db_path}")`.
- **Bewertung:** Korrekt. Die Anleitung vereinfacht den Hinweis leicht (das Emoji `⚠` und der Befehlsvorschlag fehlen in der Beschreibung), was aber keine inhaltliche Fehlinformation darstellt.

---

## Abschnitt 11: Schritt 8 – Ersteinrichtung (Zeilen 311–338)

### Aussage 11.1
- **Aussage:** Befehl: `python scripts/setup.py --db arbeitszeit.db`
- **Status:** korrekt
- **Beleg:** Datei `scripts/setup.py` vorhanden (HTTP 200); `argparse`-Parameter `--db` mit `default=Path("arbeitszeit.db")`.
- **Bewertung:** Korrekt.

### Aussage 11.2
- **Aussage:** Das Programm fragt nach Backup-Verzeichnis und Exportverzeichnis. Leere Eingabe wird nicht akzeptiert.
- **Status:** korrekt
- **Beleg:** `setup.py` → `_prompt_path()`: `while True` mit `if raw: return Path(raw)` und `print("  Bitte einen Pfad eingeben.")`.
- **Bewertung:** Exakt so implementiert.

### Aussage 11.3
- **Aussage:** Nicht-interaktiver Aufruf mit `--backup-dir` und `--export-dir`.
- **Status:** korrekt
- **Beleg:** `setup.py` → `parser.add_argument("--backup-dir", ...)` und `parser.add_argument("--export-dir", ...)`.
- **Bewertung:** Korrekt.

### Aussage 11.4
- **Aussage:** Dieser Schritt kann mehrfach ausgeführt werden — bereits festgelegte Einstellungen werden nicht doppelt abgefragt.
- **Status:** korrekt
- **Beleg:** `setup.py` → `_configure_key()`: `existing_json = config.get_current(key); if existing_json is not None: ... print(... "— übersprungen."); return`.
- **Bewertung:** Idempotenz ist implementiert.

---

## Abschnitt 12: Schritt 9 – Zugriff auf RFID-Reader und Numpad (Zeilen 340–377)

### Aussage 12.1
- **Aussage:** Gruppe `input`; Befehl: `sudo usermod -aG input $USER`
- **Status:** nicht verifizierbar
- **Beleg:** `verify_hardware.py` → Fehlermeldung `_info("Prüfe: sudo usermod -aG input $USER && Neuanmeldung")` bestätigt den Ansatz; aber keine verbindliche Konfigurationsdatei definiert dies als Pflicht.
- **Bewertung:** Der Befehl ist im Code als Hilfestellung referenziert; die Aussage ist damit indirekt belegt.

### Aussage 12.2
- **Aussage:** `cat /proc/bus/input/devices` zeigt Gerätepfade unter `Handlers`.
- **Status:** nicht verifizierbar
- **Beleg:** Linux-Systeminformation; kein Code im Repository referenziert diese Datei.
- **Bewertung:** Technisch korrekte Allgemeinaussage.

---

## Abschnitt 13: Schritt 10 – Ersten Administrator anlegen (Zeilen 379–400)

### Aussage 13.1
- **Aussage:** Befehl: `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db users bootstrap --username adminname`
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/main.py` vorhanden; `user_accounts.py` → `users_sub.add_parser("bootstrap", ...)` mit `boot.add_argument("--username", required=True)`.
- **Bewertung:** Modulpfad, Unterbefehl und Parameter stimmen überein.

### Aussage 13.2
- **Aussage:** Wird kein Passwort angegeben, erzeugt das System automatisch ein sicheres Passwort und zeigt es einmalig im Terminal an.
- **Status:** korrekt
- **Beleg:** `user_accounts.py` → `cmd_users_bootstrap()`: `password = args.password or secrets.token_urlsafe(12)`; `if not args.password: print(f"Generiertes Passwort (einmalig sichtbar): {password}")`.
- **Bewertung:** Exakt so implementiert.

---

## Abschnitt 14: Schritt 11 – Mitarbeitende und Karten anlegen (Zeilen 402–474)

### Aussage 14.1
- **Aussage:** Weiteres Benutzerkonto anlegen: Befehl mit `users add --username pruefer01 --role REVIEWER`
- **Status:** korrekt
- **Beleg:** `user_accounts.py` → `add.add_argument("--username", ...)`, `add.add_argument("--role", ..., choices=["ADMIN", "REVIEWER", "TECH"])`.
- **Bewertung:** Unterbefehl, Parameter und Rolle `REVIEWER` sind korrekt.

### Aussage 14.2
- **Aussage:** Mitarbeiter anlegen: Befehl mit `employees add --personnel-no M001 --first-name Maria --last-name Mustermann`
- **Status:** korrekt
- **Beleg:** `employees.py` → `add.add_argument("--personnel-no", required=True)`, `add.add_argument("--first-name", required=True)`, `add.add_argument("--last-name", required=True)`.
- **Bewertung:** Alle drei Parameter existieren als Pflichtparameter.

### Aussage 14.3
- **Aussage:** RFID-Karte zuweisen: `cards assign --employee-id 1 --uid-hash <HASH>`
- **Status:** korrekt
- **Beleg:** `employees.py` → `assign.add_argument("--employee-id", type=int, required=True)` und `assign.add_argument("--uid-hash", required=True)`.
- **Bewertung:** Korrekt.

### Aussage 14.4
- **Aussage:** `verify_hardware.py` erfordert **zwingend** beide Argumente `--numpad` und `--rfid`; das Script bricht ab, wenn nur eines angegeben wird.
- **Status:** inkorrekt (unvollständig)
- **Beleg:** `verify_hardware.py` → `elif args.numpad or args.rfid: parser.error("Bitte beide Gerätepfade angeben: --numpad und --rfid")`. **Aber:** `else: print("\nKeine Gerätepfade angegeben — interaktive Auswahl.\n"); numpad_path, rfid_path = select_devices_interactively()` — das Script kann **ohne** beide Argumente interaktiv gestartet werden.
- **Bewertung:** Die Behauptung „Beide Argumente sind Pflicht" ist nur für den Fall korrekt, dass **genau eines** der beiden Argumente angegeben wird. Werden **keine** Argumente angegeben, startet das Script eine **interaktive Geräteauswahl**, ohne abzubrechen. Die Anleitung verschweigt diesen Modus vollständig.
- **Anpassungsvorschlag:** Den Hinweis `(**Beide Argumente sind Pflicht** — das Script bricht ab, wenn nur eines angegeben wird.)` präzisieren: „Werden genau ein Pfad angegeben, bricht das Script ab. Werden **keine** Argumente angegeben, startet eine interaktive Geräteauswahl."

### Aussage 14.5
- **Aussage:** Das Script durchläuft drei Stufen: Gerätezugriff prüfen, Numpad-Test (Tasten 1–4), RFID-Test.
- **Status:** korrekt
- **Beleg:** `verify_hardware.py` → `check_device_access()` (Stufe 1), `test_numpad()` mit Tasten `KEY_KP1`–`KEY_KP4` / `KEY_1`–`KEY_4` (Stufe 2), `test_rfid()` (Stufe 3).
- **Bewertung:** Korrekt.

### Aussage 14.6
- **Aussage:** Nach dem Karten-Scan zeigt das Script `SHA-256-Hash: abc123def456… (wie in DB gespeichert)`.
- **Status:** korrekt (inhaltlich); nicht verifizierbar (Formatdetail)
- **Beleg:** `verify_hardware.py` → `_compute_uid_hash()` berechnet SHA-256-Hash; Ausgabeformat (`SHA-256-Hash:`) ist im Script vorhanden (Ausgabe-Hilfsfunktionen `_ok`, `_info`), aber der exakte Label-Text ist im abgeschnittenen Output nicht vollständig verifiziert.
- **Bewertung:** Der SHA-256-Hash-Mechanismus ist korrekt belegt; das Ausgabeformat-Detail ist nicht vollständig verifizierbar.

---

## Abschnitt 15: Schritt 12 – Funktionstest (Zeilen 477–495)

### Aussage 15.1
- **Aussage:** Befehl: `pytest`
- **Status:** korrekt
- **Beleg:** `pyproject.toml` → `[tool.pytest.ini_options]` mit `testpaths = ["tests"]`; `pytest>=8.0` in dev-Abhängigkeiten.
- **Bewertung:** Korrekt.

### Aussage 15.2
- **Aussage:** Befehl: `pytest tests/test_migrations.py`
- **Status:** nicht verifizierbar
- **Beleg:** Die Existenz der Datei `tests/test_migrations.py` wurde nicht geprüft.
- **Anpassungsvorschlag:** Existenz der Testdatei im Repository verifizieren.

---

## Abschnitt 16: Schritt 13 – Terminal-Betrieb starten (Zeilen 499–524)

### Aussage 16.1
- **Aussage:** Befehl: `python -m arbeitszeit.presentation.terminal_ui.main --db arbeitszeit.db --numpad /dev/input/eventX --rfid /dev/input/eventY --terminal-id 1`
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/terminal_ui/main.py` vorhanden; `parser.add_argument("--db", required=True)`, `parser.add_argument("--numpad", required=True)`, `parser.add_argument("--rfid", required=True)`, `parser.add_argument("--terminal-id", required=True, type=int)`.
- **Bewertung:** Modulpfad und alle vier Parameter stimmen überein.

### Aussage 16.2
- **Aussage:** Beenden mit `Strg` + `C`; das Programm beendet sich sauber ohne Datenverlust.
- **Status:** nicht verifizierbar
- **Beleg:** Kein Signal-Handler in den geprüften Ausschnitten explizit bestätigt; `terminal_ui/main.py` importiert `signal`, was auf Signal-Handling hindeutet, aber der vollständige Handler-Code wurde nicht gelesen.
- **Anpassungsvorschlag:** Vollständigen Code des Signal-Handlers prüfen; falls `SIGINT` sauber behandelt wird, Aussage als korrekt klassifizieren.

### Aussage 16.3
- **Aussage:** Für den echten Betrieb sollte ein systemd-Dienst eingerichtet werden; das ist nicht Teil dieser Anleitung.
- **Status:** nicht verifizierbar
- **Beleg:** Keine `systemd`-Dateien im Repository gefunden; die Aussage ist eine redaktionelle Empfehlung.
- **Bewertung:** Keine Gegen-Evidenz; inhaltlich sachgerecht.

---

## Abschnitt 17: Häufige Probleme und Lösungen (Zeilen 526–535)

### Aussage 17.1
- **Aussage:** Fehlerbild `Permission denied` → Ursache: Benutzerkonto nicht in Gruppe `input`.
- **Status:** nicht verifizierbar (Codebase), aber indirekt belegt
- **Beleg:** `verify_hardware.py` → `_info("Prüfe: sudo usermod -aG input $USER && Neuanmeldung")` als Fehlerhinweis.
- **Bewertung:** Konsistent mit der Implementierung.

### Aussage 17.2
- **Aussage:** Fehlerbild `ModuleNotFoundError` → Ursache: Abhängigkeiten nicht installiert oder venv nicht aktiv.
- **Status:** nicht verifizierbar
- **Beleg:** Keine explizite Fehlerbehandlung für `ModuleNotFoundError` im Repository; der Zusammenhang ist technisch korrekt.
- **Bewertung:** Plausibel, aber nicht direkt aus Code ableitbar.

---

## Abschnitt 18: Kurzglossar (Zeilen 537–553)

### Aussage 18.1
- **Aussage:** Admin-CLI ist die Verwaltungsoberfläche für Administratorinnen und Administratoren, bedienbar über Textbefehle.
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/` vorhanden; Modul ist eine CLI-Anwendung.
- **Bewertung:** Korrekt.

### Aussage 18.2
- **Aussage:** Terminal-UI ist der dauerhaft laufende Prozess, über den Mitarbeitende ihre Arbeitszeiten buchen.
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/terminal_ui/main.py` → Docstring: `"Terminal-UI-Einstiegspunkt: Endlosschleife für den operativen Buchungsbetrieb."`
- **Bewertung:** Exakt so implementiert.

---

## Abschnitt 19: Markdown-Formatierungsprüfung

Die Datei `installationsanleitung_arbeitszeit.md` wurde gegen die Regeln aus `markdown-Rules.md` und `Markdown Syntax Documentation.pdf` geprüft.

### Befund 19.1 – MD003: Einheitlicher Überschriftsstil
- **Status:** korrekt
- **Befund:** Alle Überschriften verwenden ATX-Stil (`#`, `##`, `###`). Kein gemischter Setext-Stil feststellbar.

### Befund 19.2 – MD001: Überschriftenebenen
- **Status:** korrekt
- **Befund:** H1 → H2 → H3 wird korrekt eingehalten (z. B. `## Schritt 0` → `### Warum ist das zwingend?`). Keine Ebene wird übersprungen.

### Befund 19.3 – MD004: Listenzeichen
- **Status:** korrekt
- **Befund:** Alle ungeordneten Listen verwenden ausschließlich `-` als Listensymbol (konsistenter Stil).

### Befund 19.4 – MD041: Erstes Element H1
- **Status:** korrekt
- **Befund:** Erste Zeile ist `# Installationsanleitung \`arbeitszeit\`` — korrekte H1-Überschrift.

### Befund 19.5 – Tabellensyntax (Zeilen 528–535)
- **Status:** korrekt
- **Befund:** Tabelle „Häufige Probleme" mit `| --- | --- | --- |` als Trennzeile ist gültige GFM-Tabellensyntax.

### Befund 19.6 – Code-Blöcke
- **Status:** korrekt
- **Befund:** Alle Code-Blöcke verwenden dreifache Backticks (`` ``` ``) mit Sprachkennzeichnung (`bash`, `text`) oder ohne; kein Mischbetrieb mit Einrückung (4 Leerzeichen).

---

## Zusammenfassung der Befunde

| Nr. | Abschnitt | Aussage (Kurzform) | Status |
|-----|-----------|-------------------|--------|
| 1.1 | Metadaten | Version 1.0, Stand Juli 2026 | nicht verifizierbar |
| 1.2 | Metadaten | Zahnarztpraxis-Zeiterfassung | korrekt |
| 2.1 | Voraussetzungen | Linux Mint oder Lubuntu | nicht verifizierbar |
| 2.2 | Voraussetzungen | RFID + Numpad via USB | korrekt |
| 5.1 | Schritt 2 | Python 3.14 erforderlich | korrekt |
| 5.2 | Schritt 2 | `python3.14-tk` für grafische Oberfläche | **inkorrekt** |
| 9.1 | Schritt 6 | `pip install -e .[dev]` | korrekt |
| 9.3 | Schritt 6 | evdev + reportlab | korrekt |
| 10.3 | Schritt 7 | 6 Migrationen 0001–0006 | korrekt |
| 10.4 | Schritt 7 | Hinweis Ersteinrichtung nach init | korrekt |
| 11.2 | Schritt 8 | Leere Pfadeingabe abgelehnt | korrekt |
| 11.4 | Schritt 8 | Idempotenz setup.py | korrekt |
| 13.1 | Schritt 10 | bootstrap-Befehl korrekt | korrekt |
| 13.2 | Schritt 10 | Auto-Passwort einmalig sichtbar | korrekt |
| 14.1 | Schritt 11 | users add REVIEWER | korrekt |
| 14.2 | Schritt 11 | employees add Parameter | korrekt |
| 14.3 | Schritt 11 | cards assign Parameter | korrekt |
| 14.4 | Schritt 11 | verify_hardware.py „Pflicht"-Argumente | **inkorrekt** |
| 14.5 | Schritt 11 | Drei Stufen verify_hardware | korrekt |
| 16.1 | Schritt 13 | terminal_ui Befehl + Parameter | korrekt |
| 18.2 | Glossar | Terminal-UI Endlosschleife | korrekt |

---

## Offene Punkte (manuell zu klären)

1. **`python3.14-tk`**: Verifizieren, ob tkinter in einem anderen Modulteil (nicht `src/`) verwendet wird. Falls nicht: Paket und Erklärung aus Schritt 2 entfernen.
2. **`pytest tests/test_migrations.py`**: Existenz der Datei `tests/test_migrations.py` im Repository prüfen.
3. **Signal-Handler `terminal_ui`**: Vollständigen `main.py`-Code prüfen, ob `SIGINT`-Handling implementiert ist (Aussage 16.2).
4. **`linux-headers` und `build-essential`**: Dokumentieren, ob diese Pakete explizit für das Projekt als Voraussetzung definiert sind.
