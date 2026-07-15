# Handbuch – `scripts/show_config.py`

**Kapitel:** 8
**Version:** 1.1
**Stand:** Juli 2026
**Quelldatei:** `docs/02_anwender/module/handbuch_show_config.md`
**Grundlage:** Ausschließlich der Quellcode `scripts/show_config.py` sowie die
verwendeten Infrastrukturmodule für Konfigurations- und
Datenbankzugriff.

## Zweck

`scripts/show_config.py` dient zur Anzeige der Laufzeitkonfiguration des
Systems. Das Skript kann sowohl Werte aus einer `config.toml` als auch Einträge
aus der Datenbanktabelle `system_config` lesen und auf der Konsole oder als
JSON ausgeben.

Das Skript ist ein reines Lesewerkzeug. Im vorliegenden Quellcode sind keine
schreibenden Datenbankoperationen und keine Änderungen an der
`config.toml` implementiert.

## Aufruf

```bash
python scripts/show_config.py --db <DB_PATH> [--config <CONFIG_PATH>] [--all-versions] [--json]
```

Das Argument `--db` ist zwingend erforderlich. Fehlt die Datenbankdatei am
angegebenen Pfad, bricht das Skript mit einer Fehlermeldung auf `stderr` und
Exit-Code 1 ab.

## Optionen

| Option | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--db DB_PATH` | Pfad | ja | Pfad zur SQLite-Datenbankdatei |
| `--config CONFIG_PATH` | Pfad | nein | Pfad zu `config.toml`; ohne Angabe erfolgt automatische Suche |
| `--all-versions` | Flag | nein | Alle Versionen pro Schlüssel anzeigen; Standard ist nur der jeweils aktuelle Stand |
| `--json` | Flag | nein | Ausgabe als JSON statt als Textdarstellung |

Die Langform `--json` wird intern auf das Attribut `as_json` abgebildet. Die
Option `--config` überschreibt die automatische Suche nach der
Konfigurationsdatei.

## Datenquellen

Das Skript verwendet zwei voneinander getrennte Datenquellen:

1. `config.toml`, sofern ein Pfad übergeben oder eine Datei automatisch
   gefunden wurde.
2. die Tabelle `system_config` der angegebenen SQLite-Datenbank.

Die automatische Suche nach `config.toml` erfolgt über `find_config()` aus
`arbeitszeit.infrastructure.config_file`. Dabei werden der in diesem Modul
implementierte Suchpfad über Umgebungsvariable, XDG-Pfad und lokales
Arbeitsverzeichnis genutzt.

## Abfrage der Datenbank

Für die Datenbankausgabe sind zwei Abfragepfade implementiert:

- `_current_config(db)` liefert pro `config_key` nur den Datensatz mit der
  höchsten `version`.
- `_all_versions(db)` liefert alle Versionen aller Schlüssel, sortiert nach
  `config_key` aufsteigend und `version` absteigend.

Das Skript liest aus `system_config` folgende Spalten:

- `config_key`
- `config_value_json`
- `version`
- `change_origin`
- `changed_by_user_id`
- `changed_at`
- `reason`

Die gelesenen Zeilen werden jeweils mit `dict(r)` in Wörterbücher überführt.
Die Datenbankverbindung wird in beiden Abfragefunktionen explizit wieder
geschlossen.

## Anzeige von `config.toml`

Für die Anzeige der TOML-Konfiguration wird `_print_config_toml()` verwendet.
Dabei werden nur Felder ausgegeben, deren Werte nicht `None` sind.

Im Quellcode sind folgende ausgabefähige Felder belegt:

- `database.path`
- `terminal.id`
- `terminal.numpad`
- `terminal.rfid`
- `backup.backup_dir`
- `backup.export_dir`
- `backup.log_dir`
- `admin.user_id`

Sind keine Werte gesetzt, gibt das Skript den Text `(keine Werte gesetzt)` aus.
Schlägt das Laden der Datei fehl, wird eine Fehlermeldung in der Form
`Fehler beim Lesen: ...` ausgegeben.

## Textausgabe

Ohne `--json` erzeugt das Skript eine zweigeteilte Textausgabe.

Zuerst wird ein Abschnitt für `config.toml` ausgegeben:

```text
=== config.toml: <pfad> ===
```

Dabei sind drei Fälle implementiert:

- Es wurde eine Datei gefunden und sie existiert: Die Werte werden formatiert
  ausgegeben.
- Es wurde ein Pfad bestimmt, aber die Datei existiert nicht: Ausgabe
  `(Datei nicht vorhanden)`.
- Es wurde keine Datei gefunden: Ausgabe
  `(keine config.toml gefunden — nutze --config um Pfad anzugeben)`.

Danach folgt immer der Datenbankabschnitt:

```text
=== DB (system_config): <db-pfad> ===
```

Für die Tabellenansicht der Datenbankwerte wird `_print_table()` verwendet.
Die Ausgabe enthält folgende Spalten:

| Spalte | Quelle | Hinweise |
| --- | --- | --- |
| `Schlüssel` | `config_key` | linke Ausrichtung, dynamische Breite |
| `Wert` | `config_value_json` | dekodiert über `_decode_value()`, Breite maximal 40 Zeichen |
| `Ver` | `version` | rechtsbündige Ganzzahl |
| `Herkunft` | `change_origin` | linke Ausrichtung, dynamische Breite |
| `Geändert am` | `changed_at` | auf die ersten 16 Zeichen gekürzt |

Überlange Werte werden vor der Ausgabe mit einem abschließenden Ellipsenzeichen
`…` gekürzt. Bei `--all-versions` wird zwischen Einträgen verschiedener
`config_key` jeweils eine Leerzeile eingefügt.

Am Ende der Tabelle steht eine Zählerzeile in der Form:

```text
N Eintrag/Einträge
```

Sind keine Datenbankeinträge vorhanden, gibt das Skript aus:

```text
Keine Konfigurationseinträge vorhanden.
```

## JSON-Ausgabe

Mit `--json` gibt das Skript ein JSON-Objekt auf `stdout` aus. Die Ausgabe ist
nicht auf die Datenbank beschränkt.

Das oberste Objekt enthält mindestens den Schlüssel `db`. Dessen Wert ist eine
Liste von Objekten mit folgenden Feldern:

```json
{
  "key": "<config_key>",
  "value": <dekodierter JSON-Wert>,
  "version": <integer>,
  "change_origin": "<string>",
  "changed_at": "<string>",
  "reason": "<string|null>"
}
```

Wenn eine `config.toml` gefunden wird und erfolgreich geladen werden kann,
fügt das Skript zusätzlich ein Objekt `config_toml` hinzu. Dieses enthält:

- `path`
- `database_path`
- `terminal_id`
- `terminal_numpad`
- `terminal_rfid`
- `backup_dir`
- `export_dir`
- `log_dir`
- `admin_user_id`

Schlägt das Laden der TOML-Datei im JSON-Pfad fehl, wird statt `config_toml`
das Feld `config_toml_error` gesetzt. Die JSON-Ausgabe erfolgt mit
`ensure_ascii=False` und `indent=2`.

## Wertdekodierung

Für die Tabellenansicht dekodiert `_decode_value()` jeden Wert aus
`config_value_json` mittels `json.loads()`.

Die implementierten Regeln lauten:

- JSON-`null` wird als `(nicht gesetzt)` ausgegeben.
- Ein JSON-String wird unverändert zurückgegeben.
- Andere erfolgreich dekodierte Typen werden mit `str(...)` in Text
  umgewandelt.
- Bei `json.JSONDecodeError` oder `TypeError` wird der Rohwert unverändert
  zurückgegeben.

Diese Dekodierungslogik gilt nur für die Textdarstellung. Im JSON-Ausgabepfad
wird `config_value_json` direkt mit `json.loads(...)` in einen JSON-Wert
überführt.

## Abhängigkeiten

Das Skript verwendet folgende Module:

- Python-Standardbibliothek: `argparse`, `json`, `sys`, `pathlib`
- `arbeitszeit.infrastructure.config_file.find_config`
- `arbeitszeit.infrastructure.config_file.load_config`
- `arbeitszeit.infrastructure.db.connection.open_connection`

Zusätzlich wird zu Beginn des Skripts das Projektverzeichnis `src` über
`sys.path.insert(...)` in den Importpfad aufgenommen.

## Abgrenzung

`scripts/show_config.py` ist ein Diagnose- und Prüfwerkzeug. Der Quellcode
belegt keine Funktion zum Ändern von Datenbankwerten und keine Funktion zum
Schreiben einer `config.toml`.

Für die Einrichtung und Pflege der Konfigurationsdatei ist stattdessen im
Repository das Skript `scripts/setup.py` vorhanden. Für den eigentlichen
Buchungsbetrieb und die Administration existieren getrennte Einstiegspunkte
unter `src/arbeitszeit/presentation/terminal_ui/` und
`src/arbeitszeit/presentation/admin_cli/`.
