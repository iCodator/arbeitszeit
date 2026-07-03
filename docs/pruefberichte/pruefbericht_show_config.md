# Prüfbericht: `docs/module/handbuch_show_config.md` (`scripts/show_config.py`)

## Gesamteinschätzung

Dieses Kapitel ist ausgesprochen präzise und deckt sich in jedem geprüften Detail exakt mit dem Quellcode von `scripts/show_config.py`. Der im Dokument angegebene SHA-Hash der Datei stimmt mit dem aktuellen Repository-Zustand überein. Sämtliche Aussagen zu Argumenten, SQL-Abfragen, Ausgabeformaten, Wertdekodierung und Abhängigkeiten sind wortgetreu belegt. Es wurde kein Korrekturbedarf festgestellt.

## Befunde

- Aussage: „Grundlage: Ausschließlich der Quellcode `scripts/show_config.py` (SHA `ea5a4f2f68cdf699be0b469477cf95c52fc6b485`)."
  Status: korrekt
  Beleg: `git hash-object scripts/show_config.py` liefert exakt `ea5a4f2f68cdf699be0b469477cf95c52fc6b485`.
  Bewertung: Der angegebene Hash stimmt mit dem aktuellen Dateiinhalt im Repository überein.

- Aussage: „Liest Einträge aus der Tabelle `system_config` ... gibt sie auf der Konsole aus. Reines Lesewerkzeug — schreibt und verändert keine Datenbankeinträge."
  Status: korrekt
  Beleg: `scripts/show_config.py`, Zeilen 22–70 (`_current_config`, `_all_versions`) enthalten ausschließlich `SELECT`-Anweisungen; keine `INSERT`/`UPDATE`/`DELETE` im gesamten Skript.
  Bewertung: Bestätigt.

- Aussage: Aufruf `python scripts/show_config.py --db <DB_PATH> [--all-versions] [--json]`; `--db` zwingend erforderlich; bei fehlender Datenbankdatei Fehlermeldung auf `stderr` und Exit-Code 1.
  Status: korrekt
  Beleg: Zeilen 135–141 (`"--db", required=True`); Zeilen 156–158 (`if not db.exists(): print(..., file=sys.stderr); sys.exit(1)`)
  Bewertung: Exakt bestätigt.

- Aussage: Optionstabelle `--db DB_PATH` (Pfad, ja), `--all-versions` (Flag, nein, Standard nur neueste), `--json` (Flag, nein, JSON statt Tabelle); `--json` intern auf `dest="as_json"` abgebildet.
  Status: korrekt
  Beleg: Zeilen 135–152
  Bewertung: Alle Optionsnamen, Pflichtstatus und der `dest`-Alias exakt bestätigt.

- Aussage: Abgefragte Spalten `config_key`, `config_value_json`, `version`, `change_origin`, `changed_by_user_id`, `changed_at`, `reason`.
  Status: korrekt
  Beleg: Zeilen 28–35 und 56–63 (beide SQL-Abfragen selektieren exakt diese sieben Spalten)
  Bewertung: Bestätigt.

- Aussage: „Ohne `--all-versions`: pro `config_key` nur der Datensatz mit dem höchsten `version`-Wert (Unterabfrage `MAX(version)`)."
  Status: korrekt
  Beleg: Zeilen 37–41 (korrelierte Unterabfrage `WHERE s.version = (SELECT MAX(s2.version) FROM system_config s2 WHERE s2.config_key = s.config_key)`)
  Bewertung: Bestätigt.

- Aussage: „Mit `--all-versions`: alle Versionen aller Keys, sortiert nach `config_key ASC, version DESC`."
  Status: korrekt
  Beleg: Zeile 65 (`ORDER BY config_key, version DESC`); `config_key` ohne Zusatz entspricht SQL-Standard `ASC`.
  Bewertung: Bestätigt.

- Aussage: Tabellenspalten `Schlüssel`/`Wert`/`Ver`/`Herkunft`/`Geändert am` mit den beschriebenen Formatierungsregeln (linksbündig/rechtsbündig, 40-Zeichen-Begrenzung mit `…`, `changed_at` nur erste 16 Zeichen).
  Status: korrekt
  Beleg: Zeilen 92–125 (`col_key`, `col_val = min(col_val, 40)`, `f"{version:>3}"` rechtsbündig, `val[:col_val - 1] + "…"`, `str(r["changed_at"])[:16]`)
  Bewertung: Alle Formatierungsdetails exakt bestätigt.

- Aussage: Spaltenbreiten für `Schlüssel` und `Herkunft` dynamisch aus Maximum aller Zeilenwerte plus Spaltenüberschrift berechnet; `Wert` auf 40 Zeichen begrenzt.
  Status: korrekt
  Beleg: Zeilen 92, 95 (`max(len("Schlüssel"), *(len(...) for r in rows))` bzw. analog für `Herkunft`); Zeile 94 (`col_val = min(col_val, 40)`)
  Bewertung: Bestätigt.

- Aussage: Mit `--all-versions` erscheint zwischen Einträgen verschiedener Keys eine Leerzeile.
  Status: korrekt
  Beleg: Zeilen 117–120 (`if all_versions and key != prev_key and prev_key: print()`)
  Bewertung: Bestätigt.

- Aussage: Zählerzeile „N Eintrag/Einträge" am Ende der Tabelle; bei keinen Einträgen „Keine Konfigurationseinträge vorhanden."
  Status: korrekt
  Beleg: Zeile 128 (`print(f"{len(rows)} Eintrag/Einträge")`); Zeile 88 (`print("Keine Konfigurationseinträge vorhanden.")`)
  Bewertung: Wortgleich bestätigt.

- Aussage: JSON-Format mit Feldern `key`, `value`, `version`, `change_origin`, `changed_at`, `reason`; `indent=2`, `ensure_ascii=False`; `changed_by_user_id` erscheint in keinem Ausgabepfad.
  Status: korrekt
  Beleg: Zeilen 164–175 (Dict-Keys exakt `key`/`value`/`version`/`change_origin`/`changed_at`/`reason`, `json.dumps(..., ensure_ascii=False, indent=2)`); `changed_by_user_id` wird zwar in Zeile 33/61 aus der DB gelesen, taucht aber weder im JSON-Dict (Zeilen 164–172) noch in der Tabellenausgabe (Zeilen 97–125) auf.
  Bewertung: Alle Feldnamen und Formatierungsparameter exakt bestätigt; die Aussage zum fehlenden `changed_by_user_id` in beiden Ausgabepfaden ist zutreffend.

- Aussage: `_decode_value()` dekodiert mit `json.loads()`: `null` → `(nicht gesetzt)`, `str` → unverändert, andere Typen → `str(val)`, ungültiges JSON/`TypeError` → Rohwert unverändert.
  Status: korrekt
  Beleg: Zeilen 73–83 exakt in dieser Fallreihenfolge implementiert.
  Bewertung: Bestätigt.

- Aussage: Abhängigkeiten ausschließlich Python-Standardbibliothek (`argparse`, `json`, `sys`, `pathlib`) und `arbeitszeit.infrastructure.db.connection.open_connection` (internes Modul); Datenbankverbindung in `_current_config()`/`_all_versions()` je in `try/finally` geöffnet und geschlossen.
  Status: korrekt
  Beleg: Zeilen 12–19 (Importliste); Zeilen 24–47 und 52–70 (`try: ... finally: conn.close()`)
  Bewertung: Bestätigt.

- Aussage: „Diagnosewerkzeug für Betrieb und Entwicklung. Schreibt keine Daten. Für interaktive Erstkonfiguration ist `scripts/setup.py` zuständig."
  Status: korrekt
  Beleg: Kein Schreibzugriff im gesamten Skript (siehe oben); `scripts/setup.py` ist an anderer Stelle als für die interaktive Ersteinrichtung zuständiges Skript bestätigt (siehe Prüfbericht Installationskapitel).
  Bewertung: Bestätigt.

## Anpassungsvorschläge

Keine. Alle prüfbaren Aussagen sind vollständig und exakt durch den Quellcode belegt.
