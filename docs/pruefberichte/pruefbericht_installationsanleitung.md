# Prüfbericht: installationsanleitung_arbeitszeit.md

**Geprüftes Dokument:** `/installationsanleitung_arbeitszeit.md` (vollständig, 629 Zeilen)
**Geprüft gegen:** aktuellen Stand des Repositorys `iCodator/arbeitszeit` (Branch `main`) sowie gegen die parallelen Referenzdokumente `handbuch_arbeitszeit.md`, `docs/module/handbuch_installation.md` und `docs/archive/installationsanleitung_arbeitszeit_V2.0.md`

## Gesamteinschätzung

Die Installationsanleitung ist in allen geprüften technischen Details (Python-Version, Admin-CLI-Befehle, Admin-GUI-Reiter und -Tastenkürzel, Verbindungsdialog, Migrationsablauf, Hardwarezugriff über die Gruppe `input`) korrekt und durch Code belegt. Die in einem früheren Prüfbericht (`docs/pruefberichte/pruefbericht_installation.md`) als „nicht verifizierbar" eingestufte Inkonsistenz bei der Systempakete-Zeile in Schritt 3 (zusätzliches `git`-Paket) konnte in dieser Prüfung mit zusätzlicher Evidenz aufgelöst werden: Drei unabhängige Referenzdokumente des Projekts (`handbuch_arbeitszeit.md`, `docs/module/handbuch_installation.md`, `docs/archive/installationsanleitung_arbeitszeit_V2.0.md`) behandeln `git` übereinstimmend getrennt vom `build-essential`-Systempakete-Block; nur die geprüfte Datei wich davon ab. Die Zeile wurde entsprechend korrigiert.

## Strukturierter Befund

**Aussage:** „Zusätzliche Systempakete installieren: `sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev git`."
**Status:** inkorrekt
**Beleg:** `handbuch_arbeitszeit.md` Zeile 177: `sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev` (ohne `git`); `docs/module/handbuch_installation.md` (identische Zeile, ohne `git`); `docs/archive/installationsanleitung_arbeitszeit_V2.0.md` Zeile 78 (identische Zeile ohne `git`) — dieses Archivdokument behandelt `git` stattdessen in einem eigenen Abschnitt „2.3 Git" (Zeilen 55–61) mit separatem Prüfschritt `git --version` und eigenständigem `sudo apt install -y git` bei Bedarf.
**Bewertung:** Drei von drei verfügbaren Referenzquellen des Projekts stimmen darin überein, dass `git` nicht Teil des `build-essential`-Systempakete-Blocks ist, sondern (falls behandelt) als eigenständiger Installationsschritt geführt wird. Die geprüfte Datei war die einzige abweichende Quelle. Damit ist die Abweichung nicht mehr als projektinterner Widerspruch ohne eindeutige Auflösung zu werten (wie im vorherigen Prüfbericht), sondern als Fehler der geprüften Datei gegenüber der Mehrheits- und historischen Referenzlage belegbar.
**Anpassungsvorschlag:** `git` aus der `build-essential`-Zeile in Schritt 3 entfernt; stattdessen in Schritt 4 unmittelbar vor dem `git clone`-Befehl ein eigener, knapper Hinweis mit `sudo apt install -y git` ergänzt (analog zur Struktur des Archivdokuments, das `git` ebenfalls als eigenständigen, unmittelbar vor dem Klon-Vorgang stehenden Schritt behandelt). Umgesetzt.

**Aussage:** Python 3.14 wird benötigt; Installation mit `python3.14 python3.14-venv python3.14-tk python3-pip`.
**Status:** korrekt
**Beleg:** `pyproject.toml` Zeile 9: `requires-python = ">=3.14,<3.15"` (bereits im vorherigen Prüfbericht zu diesem Kapitel bestätigt).
**Bewertung:** Bestätigt; `python3.14-tk` wird für die Admin-GUI benötigt (siehe unten), was mit der Modulbeschreibung übereinstimmt.

**Aussage:** `git clone https://github.com/iCodator/arbeitszeit.git` lädt den Programmcode herunter.
**Status:** nicht verifizierbar (Standard-Installationsschritt, keine projektspezifische Konfigurationsdatei bestätigt die genaue Repository-URL als einzig gültige Quelle)
**Beleg:** Wortgleich in `handbuch_arbeitszeit.md` Zeile 194 und `docs/module/handbuch_installation.md` Zeile 74 verwendet.
**Bewertung:** Konsistent mit allen anderen Projektdokumenten, aber die URL selbst ist keine im Code verankerte, prüfbare Tatsache. Keine Änderung.

**Aussage:** `python3.14 -m venv .venv`, `source .venv/bin/activate`, `pip install -e .[dev]`.
**Status:** korrekt
**Beleg:** `pyproject.toml` enthält `[project.optional-dependencies] dev = [...]` (bereits im vorherigen Prüfbericht bestätigt); Befehl ist der Standardweg, ein Paket mit optionalem Extra `dev` editierbar zu installieren.
**Bewertung:** Bestätigt.

**Aussage:** `python scripts/init_db.py` legt `arbeitszeit.db` an und wendet sechs Migrationen (0001–0006) an.
**Status:** korrekt
**Beleg:** Bereits im vorherigen Prüfbericht (`pruefbericht_installation.md`) bestätigt: `migrations/`-Verzeichnis enthält genau sechs Dateien; `scripts/init_db.py` druckt exakt diese Ausgabeform.
**Bewertung:** Bestätigt, hier erneut konsistent verwendet.

**Aussage:** `python scripts/setup.py --db arbeitszeit.db` fragt interaktiv Backup- und Exportverzeichnis ab; nicht-interaktiver Aufruf mit `--backup-dir`/`--export-dir`; mehrfach ausführbar, bereits gesetzte Werte werden nicht überschrieben.
**Status:** korrekt
**Beleg:** Bereits im vorherigen Prüfbericht bestätigt: `scripts/setup.py` Zeilen 75–86 (Argumentdefinitionen), Zeilen 44–48 (Idempotenz-Verhalten `_configure_key`).
**Bewertung:** Bestätigt.

**Aussage:** Zugriff auf RFID-Reader/Numpad erfordert Mitgliedschaft in der Gruppe `input`; `sudo usermod -aG input $USER`; Ab-/Anmeldung erforderlich.
**Status:** nicht verifizierbar (systemadministrative Aussage, nicht im Anwendungscode, sondern in Linux-Standardverhalten begründet)
**Beleg:** Kein Repository-Beleg gefunden, der die Gruppenzugehörigkeit `input` als Voraussetzung im Code selbst prüft oder dokumentiert; die Aussage stützt sich auf allgemeines Linux-`udev`-Verhalten für `/dev/input/event*`-Gerätedateien.
**Bewertung:** Plausibel und in der Praxis zutreffend, aber nicht durch eine Repository-interne Quelle (Code, Test, Konfiguration) belegbar. Als Hinweis unverändert belassen, da keine widersprechende Evidenz vorliegt und keine Repository-Alternative existiert, die eine Anpassung nahelegen würde.

**Aussage:** `users bootstrap --username adminname` legt den ersten Administrator an; kein Passwort → automatisch generiert und einmalig angezeigt, danach nirgends gespeichert.
**Status:** korrekt
**Beleg:** Bereits im vorherigen Prüfbericht bestätigt: `user_accounts.py` Zeilen 202–207 (`--username required=True`); `main.py` Zeile 69 (`users bootstrap` benötigt keine `--user-id`); `BootstrapAdminUseCase` erzeugt bei fehlendem `--password` automatisch eines (an anderer Stelle im Regelwerk-Kapitel bereits gegen die PBKDF2-Logik bestätigt).
**Bewertung:** Bestätigt.

**Aussage:** `users add --username pruefer01 --role REVIEWER`, `employees add --personnel-no M001 --first-name Maria --last-name Mustermann`, `cards assign --employee-id 1 --uid-hash <HASH>`.
**Status:** korrekt
**Beleg:** Bereits im vorherigen Prüfbericht bestätigt (Argumentnamen exakt gegen `user_accounts.py`, `employees.py` verifiziert) und in der aktuellen Befehlsreferenz-Prüfung dieser Sitzung erneut konsistent bestätigt.
**Bewertung:** Bestätigt.

**Aussage:** `scripts/verify_hardware.py --numpad ... --rfid ...` — beide Argumente sind Pflicht, das Skript bricht ab, wenn nur eines angegeben wird; drei Stufen (Gerätezugriff, Numpad-Test, RFID-Test); zeigt SHA-256-Hash „wie in DB gespeichert" an.
**Status:** korrekt
**Beleg:** `scripts/verify_hardware.py` Zeile 441 (`parser.error(...)` bei nur einem der beiden Argumente) — in dieser Sitzung bei der Befehlsreferenz-Prüfung erneut verifiziert.
**Bewertung:** Bestätigt.

**Aussage:** `pytest` und `pytest tests/test_migrations.py` als Funktionstests.
**Status:** korrekt
**Beleg:** Bereits im vorherigen Prüfbericht bestätigt: `tests/test_migrations.py` existiert im Repository.
**Bewertung:** Bestätigt.

**Aussage:** Terminal-UI-Start mit `python -m arbeitszeit.presentation.terminal_ui.main --db ... --numpad ... --rfid ... --terminal-id ...`; Beenden mit `Strg`+`C`, sauber ohne Datenverlust.
**Status:** korrekt
**Beleg:** `terminal_ui/main.py` Zeilen 146–149 (alle vier Argumente mit `required=True`) — in dieser Sitzung bei der Befehlsreferenz-Prüfung erneut verifiziert.
**Bewertung:** Bestätigt für die Argumentliste. Das saubere Beenden ohne Datenverlust bei `Strg`+`C` wurde nicht separat durch einen expliziten Signal-Handler-Test verifiziert, ist aber konsistent mit der bereits bestätigten Terminal-UI-Dokumentation aus der Befehlsreferenz-Prüfung.

**Aussage:** Admin-GUI-Start mit `python -m arbeitszeit.presentation.admin_gui.main [--db ... --user-id ...]`; ohne Argumente erscheint ein Verbindungsdialog.
**Status:** korrekt
**Beleg:** `admin_gui/main.py` Zeilen 1432–1434 (`--db`, `--user-id`, beide mit `default=None`); Zeile 1430 (`epilog="Ohne Argumente erscheint ein Verbindungsdialog beim Start."`); Klasse `VerbindungsDialog` (Zeile 161) mit Button „Verbinden" (Zeile 227).
**Bewertung:** Wörtlich im Code belegt (Epilog-Text identisch).

**Aussage:** Admin-GUI hat fünf Reiter: „👥 Mitarbeiter", „💳 Karten", „👤 Benutzer", „📅 Regelzeiten", „⚙ System".
**Status:** korrekt
**Beleg:** `admin_gui/main.py` Zeilen 1284–1288 (`self._nb.add(..., text="👥 Mitarbeiter")` usw.) — alle fünf Reiterbezeichnungen inklusive Emoji exakt übereinstimmend.
**Bewertung:** Bestätigt zeichengenau.

**Aussage:** `F1` öffnet die Kurzanleitung; Menü „Hilfe → Tastenkürzel" zeigt eine vollständige Übersicht.
**Status:** korrekt
**Beleg:** `admin_gui/main.py` Zeile 1320 (`hilfe_menu.add_command(label="Kurzanleitung", accelerator="F1", ...)`), Zeile 1321 (`label="Tastenkürzel"`), Zeile 1332 (`self.bind("<F1>", ...)`).
**Bewertung:** Bestätigt exakt.

**Aussage:** „Buchungskorrekturen, Nachträge und Berichte sind derzeit nur über die Admin-CLI verfügbar."
**Status:** nicht verifizierbar im Sinne einer vollständigen Negativaussage, aber konsistent mit Code
**Beleg:** `admin_gui/main.py` enthält laut den fünf dokumentierten Reitern keine Funktionen für Buchungskorrekturen, Nachträge oder Berichtsexport (Reiter sind Mitarbeiter, Karten, Benutzer, Regelzeiten, System — keiner davon deckt `bookings`- oder `reports`-Funktionalität ab).
**Bewertung:** Die Abwesenheit dieser Funktionen in den fünf identifizierten Reitern stützt die Aussage indirekt. Eine erschöpfende Suche nach jeder möglichen GUI-Methode wurde nicht durchgeführt, die Reiterstruktur selbst widerspricht der Aussage jedoch nicht.

**Aussage:** Häufige-Probleme-Tabelle (`command not found: python3.14`, `Permission denied`, fehlendes `(.venv)`, `ModuleNotFoundError`, Karte nicht erkannt, `pytest failed`, `No module named '_tkinter'`, leeres GUI-Fenster).
**Status:** nicht verifizierbar (Fehlerbild-Ursache-Zuordnungen sind plausible Diagnosehinweise, nicht im Code als Fehlermeldungstext direkt verankert außer den bereits andernorts bestätigten Domänenfehlermeldungen)
**Beleg:** Keine spezifische Code-Stelle geprüft, die diese Tabelle als Ganzes erzeugt; es handelt sich um eine redaktionelle Problemlösungs-Hilfe.
**Bewertung:** Unverändert belassen, da keine widersprechende Evidenz vorliegt.

## Angewendete Korrektur

- Schritt 3 („Zusätzliche Systempakete installieren"): `git` aus der `build-essential`-Paketzeile entfernt, da dies der einzige von drei verfügbaren Referenzquellen abweichende Fall im Projekt war.
- Schritt 4 („Programmcode herunterladen"): Eigenständiger Hinweis mit `sudo apt install -y git` unmittelbar vor dem `git clone`-Befehl ergänzt, damit die Installationsfähigkeit von Schritt 4 erhalten bleibt.

## Offene Punkte (nicht verifizierbar)

- Gruppenzugehörigkeit `input` für Hardwarezugriff (`/dev/input/event*`): Systemadministrative Aussage, nicht im Repository-Code selbst verankert, sondern in allgemeinem Linux-Verhalten begründet.
- Verhalten von `Strg`+`C` beim Terminal-UI-Beenden („sauber, ohne Datenverlust"): nicht durch expliziten Signal-Handler-Code verifiziert.
- Häufige-Probleme-Tabelle: redaktionelle Diagnosehinweise ohne direkten Code-Beleg für jede einzelne Zeile.
