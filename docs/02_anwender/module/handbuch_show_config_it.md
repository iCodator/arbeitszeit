# Handbuch – `scripts/show_config.py` — technisches Referenzhandbuch

**Kapitel:** 8-IT
**Version:** 1.1
**Stand:** Juli 2026
**Zielgruppe:** Entwickler, Systemverantwortliche
**Quelldatei:** `scripts/show_config.py`

## Zweck

`scripts/show_config.py` dient zur Anzeige der Laufzeitkonfiguration des
Systems. Das Skript kann sowohl Werte aus einer `config.toml` als auch Einträge
aus der Datenbanktabelle `system_config` lesen und auf der Konsole oder als
JSON ausgeben.

Das Skript ist ein reines Lesewerkzeug. Im vorliegenden Quellcode sind keine
schreibenden Datenbankoperationen und keine Änderungen an der
`config.toml` implementiert.

## Aufruf

Das Skript muss aus dem Projektroot aufgerufen werden, da es via
`sys.path.insert(...)` das Verzeichnis `src` in den Importpfad aufnimmt:

```bash
cd /pfad/zu/arbeitszeit
python scripts/show_config.py --db <DB_PATH> [--config <CONFIG_PATH>] [--all-versions] [--json]
```

Das Argument `--db` ist zwingend erforderlich. Fehlt die Datenbankdatei am
angegebenen Pfad, bricht das Skript mit einer Fehlermeldung auf `stderr` und
Exit-Code 1 ab — auch im JSON-Modus (`--json`).

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

## Exit-Codes

| Code | Bedeutung |
| --- | --- |
| 0 | Erfolg |
| 1 | DB-Datei nicht gefunden oder nicht lesbar (auch im JSON-Modus) |

## Datenquellen

Das Skript verwendet zwei voneinander getrennte Datenquellen:

1. `config.toml`, sofern ein Pfad übergeben oder eine Datei automatisch
   gefunden wurde.
2. die Tabelle `system_config` der angegebenen SQLite-Datenbank.

Die automatische Suche nach `config.toml` erfolgt über `find_config()` aus
`arbeitszeit.infrastructure.config_file`. Dabei werden Umgebungsvariable
`ARBEITSZEIT_CONFIG`, XDG-Pfad `~/.config/arbeitszeit/config.toml` und
lokales Arbeitsverzeichnis `./config.toml` geprüft.

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
- `terminal.rfid`
- `backup.backup_dir`
- `backup.export_dir`
- `backup.log_dir`
- `admin.user_id`

Sind keine Werte gesetzt, gibt das Skript den Text `(keine Werte gesetzt)` aus.
Schlägt das Laden der Datei fehl, wird eine Fehlermeldung in der Form
`Fehler beim Lesen: ...` ausgegeben.

## Textausgabe (Beispiel)

Ohne `--json` erzeugt das Skript eine zweigeteilte Textausgabe:

```text
=== config.toml: /home/user/.config/arbeitszeit/config.toml ===
database.path      = /home/user/data/arbeitszeit.db
terminal.id        = 1
backup.backup_dir  = /var/backups/arbeitszeit

=== DB (system_config): /home/user/data/arbeitszeit.db ===
Schlüssel                                   Wert              Ver  Herkunft     Geändert am
app.timezone                                Europe/Berlin       1   SYSTEM_SEED  2026-01-01T00:00
backup.nas_enabled                          False               1   SYSTEM_SEED  2026-01-01T00:00
backup.nas_path                             (nicht gesetzt)     1   SYSTEM_SEED  2026-01-01T00:00

3 Einträge
```

Die drei Fälle für `config.toml`:

- Datei gefunden und lesbar: Werte werden formatiert ausgegeben.
- Pfad bestimmt, Datei existiert nicht: `(Datei nicht vorhanden)`.
- Keine Datei gefunden: `(keine config.toml gefunden — nutze --config um Pfad anzugeben)`.

Die Tabellenansicht der Datenbankwerte (`_print_table()`) enthält folgende
Spalten:

| Spalte | Quelle | Hinweise |
| --- | --- | --- |
| `Schlüssel` | `config_key` | linke Ausrichtung, dynamische Breite |
| `Wert` | `config_value_json` | dekodiert über `_decode_value()`, maximal 40 Zeichen |
| `Ver` | `version` | rechtsbündige Ganzzahl |
| `Herkunft` | `change_origin` | linke Ausrichtung, dynamische Breite |
| `Geändert am` | `changed_at` | auf die ersten 16 Zeichen gekürzt |

Überlange Werte werden mit `…` gekürzt. Bei `--all-versions` wird zwischen
Einträgen verschiedener `config_key` jeweils eine Leerzeile eingefügt.

## JSON-Ausgabe

Mit `--json` gibt das Skript ein JSON-Objekt auf `stdout` aus:

```json
{
  "db": [
    {
      "key": "app.timezone",
      "value": "Europe/Berlin",
      "version": 1,
      "change_origin": "SYSTEM_SEED",
      "changed_at": "2026-01-01T00:00:00",
      "reason": null
    }
  ],
  "config_toml": {
    "path": "/home/user/.config/arbeitszeit/config.toml",
    "database_path": "/home/user/data/arbeitszeit.db",
    "terminal_id": 1,
    "terminal_rfid": "Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader",
    "backup_dir": "/var/backups/arbeitszeit",
    "export_dir": null,
    "log_dir": "/var/log/arbeitszeit",
    "admin_user_id": null
  }
}
```

Schlägt das Laden der TOML-Datei im JSON-Pfad fehl, wird statt `config_toml`
das Feld `config_toml_error` gesetzt. Die JSON-Ausgabe erfolgt mit
`ensure_ascii=False` und `indent=2`.

## Wertdekodierung

Für die Tabellenansicht dekodiert `_decode_value()` jeden Wert aus
`config_value_json` mittels `json.loads()`:

- JSON-`null` → `(nicht gesetzt)`
- JSON-String → unveränderter String
- Andere Typen → `str(...)`
- `json.JSONDecodeError` oder `TypeError` → Rohwert unverändert

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
`sys.path.insert(...)` in den Importpfad aufgenommen. Das Skript muss daher
aus dem Projektroot aufgerufen werden.

## Abgrenzung

`scripts/show_config.py` ist ein Diagnose- und Prüfwerkzeug. Der Quellcode
belegt keine Funktion zum Ändern von Datenbankwerten und keine Funktion zum
Schreiben einer `config.toml`.

Für die Einrichtung und Pflege der Konfigurationsdatei ist stattdessen im
Repository das Skript `scripts/setup.py` vorhanden. Für den eigentlichen
Buchungsbetrieb und die Administration existieren getrennte Einstiegspunkte
unter `src/arbeitszeit/presentation/terminal_ui/` und
`src/arbeitszeit/presentation/admin_cli/`.
