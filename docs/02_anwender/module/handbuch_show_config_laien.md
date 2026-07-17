# Aktuelle Konfiguration anzeigen

**Kapitel:** 8-Laien
**Version:** 1.0
**Stand:** Juli 2026
**Zielgruppe:** Praxisleitung, Verwaltung

## Wozu dient dieses Werkzeug?

Mit `scripts/show_config.py` können Sie jederzeit prüfen, welche
Einstellungen das System gerade verwendet — zum Beispiel welcher
Datenbankpfad eingerichtet ist, wo Backups gespeichert werden oder
welche interne Systemkonfiguration aktiv ist.

Das Werkzeug zeigt nur an — es ändert nichts.

## Befehl

```bash
python scripts/show_config.py --db /pfad/zur/arbeitszeit.db
```

Falls Sie eine Konfigurationsdatei an einem anderen Ort haben:

```bash
python scripts/show_config.py --db /pfad/zur/arbeitszeit.db \
  --config /pfad/zur/config.toml
```

## Beispielausgabe

```text
=== config.toml: /home/user/.config/arbeitszeit/config.toml ===
database.path     = /home/user/data/arbeitszeit.db
terminal.id       = 1
backup.backup_dir = /var/backups/arbeitszeit
backup.log_dir    = /var/log/arbeitszeit

=== DB (system_config): /home/user/data/arbeitszeit.db ===
Schlüssel                                 Wert           Ver  Herkunft     Geändert am
app.timezone                              Europe/Berlin    1   SYSTEM_SEED  2026-01-01T00:00
booking.grace_seconds_after_numpad_select 30               1   SYSTEM_SEED  2026-01-01T00:00
backup.nas_enabled                        False            1   SYSTEM_SEED  2026-01-01T00:00
backup.nas_path                           (nicht gesetzt)  1   SYSTEM_SEED  2026-01-01T00:00

4 Einträge
```

## Was bedeuten die Angaben?

**Oberer Abschnitt (`config.toml`):** Die Einstellungen aus der
Konfigurationsdatei, die beim Start geladen werden. Typisch sind hier
Datenbankpfad, Terminal-Nummer und Backup-Verzeichnis.

**Unterer Abschnitt (`DB system_config`):** Systeminterne Einstellungen,
die in der Datenbank gespeichert sind. Diese werden automatisch angelegt
und normalerweise nicht manuell verändert.

| Systemeinstellung | Bedeutung |
| --- | --- |
| `app.timezone` | Zeitzone des Systems (Standard: Europe/Berlin) |
| `booking.grace_seconds_after_numpad_select` | Reaktionszeit am Terminal in Sekunden |
| `backup.nas_enabled` | Ob Backups auf ein Netzlaufwerk synchronisiert werden |
| `backup.nas_path` | Pfad zum Netzlaufwerk für Backups |

## Wenn die Datenbank nicht gefunden wird

Falls die angegebene Datenbankdatei nicht vorhanden ist, gibt das
Werkzeug eine Fehlermeldung aus und beendet sich. Überprüfen Sie in
diesem Fall den Pfad zur Datenbankdatei.
