# Programmieraufgabe Phase 1 – arbeitszeit

## Quellenbasis

Diese Aufgabe basiert auf `planung_gesamt.md` sowie fachlich ergänzend auf `phase1_planung_konkret.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage Einhaltung Pflichtenheft v2`.

## Ziel

Implementiere **ausschließlich Phase 1** des Projekts `arbeitszeit`. Führe **keine** Aufgaben aus späteren Phasen aus. Es geht in dieser Aufgabe nur um das technische Grundgerüst: Projektstruktur, initiales SQLite-Schema, Seed-Daten, Datenbankverbindung, Migrationsrunner, Initialisierungsskript und erste Migrationstests. [planung_gesamt.md; phase1_planung_konkret.md]

Die Aufgabe ist erfolgreich abgeschlossen, wenn eine neue Datenbank ausschließlich aus den Migrationen `0001_schema.sql` und `0002_seed_defaults.sql` reproduzierbar aufgebaut werden kann und die vorgesehenen Phase-1-Tests erfolgreich laufen. [planung_gesamt.md; phase1_planung_konkret.md]

## Strikte Grenzen

Arbeite streng innerhalb dieses Umfangs. **Nicht** Teil dieser Aufgabe sind insbesondere: [planung_gesamt.md; phase1_planung_konkret.md]

- Domänenobjekte, Enums, Entities oder Business-Regeln. [planung_gesamt.md; phase1_planung_konkret.md]
- Use Cases oder Application-Schicht. [planung_gesamt.md; phase1_planung_konkret.md]
- SQLite-Repositories oder Unit of Work. [planung_gesamt.md; phase1_planung_konkret.md]
- Export, PDF, Reports oder Pflichtauswertungen. [planung_gesamt.md; phase1_planung_konkret.md]
- Backup/Restore, NAS-Sync oder Zeitmonitor. [planung_gesamt.md; phase1_planung_konkret.md]
- Terminal-UI oder Admin-CLI. [planung_gesamt.md; phase1_planung_konkret.md]
- spätere Migrationen `0003` bis `0006`. [planung_gesamt.md; phase1_planung_konkret.md]

Wenn du bei der Umsetzung an einen Punkt kommst, an dem eine spätere Architekturentscheidung nötig wäre, stoppe an der sauberen Phase-1-Grenze und implementiere nichts darüber hinaus. [planung_gesamt.md; phase1_planung_konkret.md]

## Verbindlicher Lieferumfang

Erzeuge oder vervollständige exakt die folgenden Bestandteile: [planung_gesamt.md; phase1_planung_konkret.md]

- `pyproject.toml`. [planung_gesamt.md; phase1_planung_konkret.md]
- `src/`-Projektstruktur. [planung_gesamt.md; phase1_planung_konkret.md]
- `tests/`-Verzeichnis. [planung_gesamt.md; phase1_planung_konkret.md]
- `.gitignore`. [planung_gesamt.md; phase1_planung_konkret.md]
- `.python-version`. [planung_gesamt.md; phase1_planung_konkret.md]
- `migrations/0001_schema.sql`. [planung_gesamt.md; phase1_planung_konkret.md]
- `migrations/0002_seed_defaults.sql`. [planung_gesamt.md; phase1_planung_konkret.md]
- `src/arbeitszeit/infrastructure/db/connection.py`. [planung_gesamt.md; phase1_planung_konkret.md]
- `src/arbeitszeit/infrastructure/db/migrations.py`. [planung_gesamt.md; phase1_planung_konkret.md]
- `scripts/init_db.py`. [planung_gesamt.md; phase1_planung_konkret.md]
- `tests/test_migrations.py`. [planung_gesamt.md; phase1_planung_konkret.md]

Hinweis: Falls die genaue Package-Struktur im Repo bereits leicht abweicht, orientiere dich am vorhandenen Projektlayout, solange Inhalt und Verantwortung dieser Dateien unverändert bleiben. [phase1_planung_konkret.md]
