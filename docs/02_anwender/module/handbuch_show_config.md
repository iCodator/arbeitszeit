# Handbuch – `scripts/show_config.py`

**Grundlage:** Ausschließlich der Quellcode `scripts/show_config.py`
(SHA `ea5a4f2f68cdf699be0b469477cf95c52fc6b485`).

---

## 1. Zweck

`show_config.py` liest Einträge aus der Tabelle `system_config` der
`arbeitszeit`-SQLite-Datenbank und gibt sie auf der Konsole aus.
Es handelt sich um ein reines Lesewerkzeug — es schreibt und verändert
keine Datenbankeinträge.

---

## 2. Aufruf

```bash
python scripts/show_config.py --db <DB_PATH> [--all-versions] [--json]
```

Das Argument `--db` ist **zwingend erforderlich**. Fehlt die Datenbankdatei
am angegebenen Pfad, bricht das Skript mit einer Fehlermeldung auf `stderr`
und Exit-Code 1 ab.

---

## 3. Optionen

| Option | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--db DB_PATH` | Pfad | ja | Pfad zur SQLite-Datenbankdatei |
| `--all-versions` | Flag | nein | Alle Versionen pro Key anzeigen (Standard: nur neueste) |
| `--json` | Flag | nein | Ausgabe als JSON statt als Tabelle |

Die Langform `--json` wird intern auf das Attribut `as_json` abgebildet
(argparse-Alias `dest="as_json"`).

---

## 4. Abgefragte Datenbankfelder

Das Skript liest aus der Tabelle `system_config` folgende Spalten:

- `config_key`
- `config_value_json`
- `version`
- `change_origin`
- `changed_by_user_id`
- `changed_at`
- `reason`

**Ohne `--all-versions`:** Pro `config_key` wird nur der Datensatz mit
dem höchsten `version`-Wert zurückgegeben (Unterabfrage `MAX(version)`).

**Mit `--all-versions`:** Alle Versionen aller Keys werden zurückgegeben,
sortiert nach `config_key ASC, version DESC`.

---

## 5. Ausgabeformate

### 5.1 Tabellenformat (Standard)

Spalten der Ausgabe:

| Spalte | Quelle | Hinweise |
| --- | --- | --- |
| `Schlüssel` | `config_key` | linksbündig, variable Breite |
| `Wert` | `config_value_json` | JSON-dekodiert, max. 40 Zeichen, überlange Werte werden mit `…` abgeschnitten |
| `Ver` | `version` | rechtsbündig, ganzzahlig |
| `Herkunft` | `change_origin` | linksbündig, variable Breite |
| `Geändert am` | `changed_at` | nur die ersten 16 Zeichen (`YYYY-MM-DDTHH:MM`) |

Die Spaltenbreiten für `Schlüssel` und `Herkunft` werden dynamisch aus dem
Maximum aller Zeilenwerte plus Spaltenüberschrift berechnet. `Wert` ist
auf 40 Zeichen begrenzt.

Mit `--all-versions` erscheint zwischen Einträgen verschiedener Keys
eine Leerzeile.

Am Ende der Tabelle steht eine Zählerzeile:

```text
N Eintrag/Einträge
```

Sind keine Einträge vorhanden, gibt das Skript aus:

```text
Keine Konfigurationseinträge vorhanden.
```

### 5.2 JSON-Format (`--json`)

Gibt ein JSON-Array auf `stdout` aus. Jedes Element enthält folgende Felder:

```json
[
  {
    "key": "<config_key>",
    "value": <dekodierter JSON-Wert>,
    "version": <integer>,
    "change_origin": "<string>",
    "changed_at": "<string>",
    "reason": "<string|null>"
  }
]
```

Die Ausgabe erfolgt mit `indent=2` und `ensure_ascii=False` (Unicode-Zeichen
werden nicht escaped). Das Feld `changed_by_user_id` erscheint in der
JSON-Ausgabe **nicht** (es wird in der Tabellenausgabe ebenfalls nicht
angezeigt — das Feld wird zwar aus der Datenbank gelesen, aber in keinem
Ausgabepfad ausgegeben).

---

## 6. Wertdekodierung

Intern dekodiert `_decode_value()` jeden `config_value_json`-String mit
`json.loads()`:

- `null` → `(nicht gesetzt)`
- `str` → unveränderter String
- alle anderen Typen → `str(val)`
- ungültiges JSON oder `TypeError` → Rohwert wird unverändert ausgegeben

---

## 7. Abhängigkeiten

Das Skript nutzt ausschließlich:

- Python-Standardbibliothek (`argparse`, `json`, `sys`, `pathlib`)
- `arbeitszeit.infrastructure.db.connection.open_connection`
  (internes Modul, kein Drittpaket)

Die Datenbankverbindung wird in `_current_config()` und `_all_versions()`
jeweils in einem `try/finally`-Block geöffnet und explizit geschlossen.

---

## 8. Abgrenzung

`show_config.py` ist ein **Diagnosewerkzeug für den Betrieb und die
Entwicklung**. Es schreibt keine Daten und nimmt keine Konfigurationsänderungen
vor. Für interaktive Erstkonfiguration ist `scripts/setup.py` zuständig.
