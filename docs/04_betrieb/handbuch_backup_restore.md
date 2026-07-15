# Handbuch: Backup und Restore – System „arbeitszeit"

**System:** arbeitszeit
**Dokumenttyp:** Betriebshandbuch – Backup und Restore
**Version:** 1.1
**Stand:** 2026-07-15
**Zielgruppe:** Rollen ADMIN, TECH

> Dieses Handbuch beschreibt die im Repository nachweisbare Durchführung von
> Backup und Restore für das System `arbeitszeit`. Es ergänzt
> `backup_zeitplan_und_automatisierung.md` für Zeitplanung und Automatisierung
> sowie `restore_checkliste.md` für Freigabe und operative Durchführung.

---

## 1. Zweck und Geltungsbereich

Dieses Handbuch beschreibt die technisch nachweisbaren Abläufe für:

- manuelles Backup über die Admin-CLI,
- manuelles oder automatisiertes Backup über `scripts/backup.py`,
- optionale NAS-Synchronisation,
- Restore über die Methode `restore_from` des `SQLiteBackupService`.

Nicht Bestandteil dieses Handbuchs sind:

- ein eigenständiger CLI-Restore-Befehl,
- ein im Repository enthaltenes dauerhaftes Restore-Skript,
- eine technische Umsetzung automatischer Backup-Rotation,
- organisatorische Freigaberegeln außerhalb der Repository-Belege.

---

## 2. Technische Grundlage

Die technische Implementierung liegt in
`src/arbeitszeit/infrastructure/backup/backup_service.py`.

Das Backup verwendet die SQLite-Backup-API über `src.backup(dst)`.
Dabei wird eine neue Datenbankdatei im Backup-Verzeichnis erzeugt.
Wenn ein Exportverzeichnis gesetzt ist und existiert, wird dessen Inhalt nach
`<backup_dir>/exports/` kopiert.

Der Restore verwendet ebenfalls die SQLite-Backup-API. Nach dem Einspielen des
Backups wird `PRAGMA integrity_check` auf der wiederhergestellten Datenbank
ausgeführt. Nur bei Ergebnis `ok` gilt der Restore technisch als erfolgreich.

---

## 3. Konfigurationsquellen

Für Backup und Restore existieren zwei nachweisbare Konfigurationsquellen:

1. `config.toml`
2. `system_config` in der SQLite-Datenbank

Die Vorrangregeln sind nicht überall identisch und müssen getrennt betrachtet
werden.

### 3.1 `config.toml`

Die Datei `config.toml.example` sowie
`src/arbeitszeit/infrastructure/config_file.py` belegen folgende Einträge im
Abschnitt `[backup]`:

| Schlüssel in `config.toml` | Bedeutung |
|---|---|
| `backup_dir` | Zielverzeichnis für Datenbank-Backups |
| `export_dir` | Verzeichnis für Exportdateien, die in das Backup übernommen werden können |
| `log_dir` | Log-Verzeichnis; für die Backup-Implementierung selbst nicht direkt verwendet |

Die Suchreihenfolge für `config.toml` ist nachweisbar wie folgt:

1. expliziter Pfad über `--config`,
2. Umgebungsvariable `ARBEITSZEIT_CONFIG`,
3. `~/.config/arbeitszeit/config.toml`,
4. `./config.toml`.

### 3.2 `system_config`

Zusätzlich werden in der Datenbank folgende Schlüssel verwendet:

| Schlüssel in `system_config` | Bedeutung |
|---|---|
| `backup.backup_dir` | Fallback-Backup-Verzeichnis für die Admin-CLI, wenn `config.toml` kein `backup_dir` liefert |
| `export.export_dir` | Fallback-Exportverzeichnis für die Admin-CLI, wenn `config.toml` kein `export_dir` liefert |
| `backup.nas_enabled` | Aktiviert oder deaktiviert NAS-Synchronisation |
| `backup.nas_path` | Zielpfad für NAS-Synchronisation |

### 3.3 Vorrangregeln je Ausführungsweg

| Ausführungsweg | `backup_dir` | `export_dir` |
|---|---|---|
| Admin-CLI `system backup` | `config.toml` vor `system_config` | `config.toml` vor `system_config` |
| `scripts/backup.py` | CLI `--backup-dir` vor `config.toml`, sonst Fallback `backups` | CLI `--export-dir` vor `config.toml`, sonst `None` |

Für `scripts/backup.py` ist kein Lesen von `backup.backup_dir` oder
`export.export_dir` aus `system_config` nachweisbar. Die Datenbank wird dort nur
für `backup.nas_enabled` und `backup.nas_path` verwendet.

---

## 4. Backup über die Admin-CLI

Die Admin-CLI registriert den Unterbefehl `system backup` in
`src/arbeitszeit/presentation/admin_cli/system.py`.

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db /pfad/zu/arbeitszeit.db \
  --user-id <ID> \
  system backup
```

### 4.1 Voraussetzungen

Für `system backup` sind folgende Bedingungen nachweisbar:

- Der aufrufende Benutzer muss `ADMIN` oder `TECH` sein.
- Ein Backup-Verzeichnis muss auflösbar sein.
- Die Datenbankdatei muss verfügbar sein.

Die Rollenprüfung erfolgt über `require_admin_or_tech(...)`.

### 4.2 Auflösung des Backup-Verzeichnisses

Die Admin-CLI löst das Backup-Verzeichnis in folgender Reihenfolge auf:

1. `app_config.backup.backup_dir` aus `config.toml`, sofern geladen,
2. `backup.backup_dir` aus `system_config`,
3. sonst Fehler und Abbruch mit Exit-Code 1.

Die Fehlermeldung nennt explizit beide zulässigen Konfigurationswege:
`[backup] backup_dir` in `config.toml` oder den Schlüssel
`backup.backup_dir` in `system_config`.

### 4.3 Auflösung des Export-Verzeichnisses

Das Export-Verzeichnis wird in folgender Reihenfolge aufgelöst:

1. `app_config.backup.export_dir` aus `config.toml`,
2. `export.export_dir` aus `system_config`,
3. sonst `None`.

Wenn kein Export-Verzeichnis aufgelöst werden kann, läuft das Backup dennoch
weiter; es werden dann nur die Datenbankdaten gesichert.

### 4.4 Ablauf

Der Ablauf des CLI-Backups ist nachweisbar wie folgt:

1. Rollenprüfung `ADMIN` oder `TECH`.
2. Auflösung von `backup_dir`.
3. Auflösung von `export_dir`.
4. Erzeugung eines lokalen Backups über `service.create_local_backup()`.
5. Ausgabe `Backup erstellt: <Pfad>`.
6. Optionaler NAS-Sync über `_run_nas_sync(...)`.

Wenn der NAS-Sync erfolgreich ist, gibt die CLI zusätzlich
`NAS-Synchronisation erfolgreich.` aus.
Bei Fehler im NAS-Sync erfolgt Abbruch mit Exit-Code 1.

---

## 5. Backup über `scripts/backup.py`

Das Repository enthält mit `scripts/backup.py` ein eigenständiges Backup-Skript
für manuelle Ausführung oder Automatisierung.

```bash
python scripts/backup.py \
  --db arbeitszeit.db \
  --backup-dir /pfad/zum/backup
```

Optional sind zusätzlich `--config` und `--export-dir` verfügbar.

### 5.1 Parameter

| Parameter | Bedeutung |
|---|---|
| `--db` | Pfad zur Datenbankdatei, Standard `arbeitszeit.db` |
| `--config` | expliziter Pfad zu `config.toml` |
| `--backup-dir` | Zielverzeichnis für Backups |
| `--export-dir` | Exportverzeichnis, das nach `backup_dir/exports/` kopiert werden kann |

### 5.2 Auflösungslogik

Für `scripts/backup.py` ist folgende Priorität nachweisbar:

- `backup_dir`: CLI `--backup-dir` vor `config.toml`, sonst Fallback `backups`
- `export_dir`: CLI `--export-dir` vor `config.toml`, sonst `None`

Wenn die Datenbankdatei nicht existiert, bricht das Skript mit Fehlerausgabe auf
`stderr` und Exit-Code 1 ab.

### 5.3 NAS-Verhalten

NAS-Synchronisation wird in `scripts/backup.py` nicht über CLI-Parameter,
sondern über die Datenbankkonfiguration gesteuert:

- `backup.nas_enabled`
- `backup.nas_path`

Nur wenn `backup.nas_enabled` den JSON-Wert `true` liefert und zusätzlich ein
Pfad aus `backup.nas_path` vorhanden ist, wird `service.run(...)` mit einem
`nas_path` aufgerufen.

### 5.4 Ausgabe

Bei erfolgreicher Ausführung erzeugt das Skript eine Ausgabe im Format:

```text
Backup: <backup_path>  (<size_bytes> Bytes)
```

Danach folgt entweder:

```text
NAS-Sync: <nas_path>
```

oder:

```text
NAS-Sync: deaktiviert
```

---

## 6. Internes Verhalten des Backup-Service

Die Klasse `SQLiteBackupService` implementiert die eigentliche Backup- und
Restore-Logik.

### 6.1 Lokales Backup

Die Methode `create_local_backup(...)` führt nachweisbar folgende Schritte aus:

1. Anlegen des Backup-Verzeichnisses mit `mkdir(parents=True, exist_ok=True)`.
2. Erzeugung eines UTC-Zeitstempels im Format `YYYYMMDDTHHMMSSZ`.
3. Erzeugung des Dateinamens `arbeitszeit_<Zeitstempel>.db`.
4. Kopie der Datenbank über die SQLite-Backup-API.
5. Optionales Kopieren des Exportverzeichnisses nach `backup_dir/exports/`,
   falls `export_dir` gesetzt ist und existiert.
6. Schreiben eines Audit-Log-Eintrags `BACKUP_CREATED`.

### 6.2 NAS-Synchronisation

Die Methode `sync_to_nas(...)` führt `rsync` mit festem absolutem Pfad und
festen Parametern aus:

```text
/usr/bin/rsync --archive --delete <backup_dir>/ <nas_path>/
```

Das Verhalten ist damit ein Spiegeln des Backup-Verzeichnisses zum NAS-Ziel.
Eine eigenständige Archivierungslogik oder Rotation ist im Code nicht enthalten.

Bei Fehler von `rsync` wird ein Audit-Ereignis `BACKUP_SYNC_FAILED` mit
Fehlerdetails geschrieben und die Ausnahme erneut ausgelöst.
Bei Erfolg wird `BACKUP_SYNCED_TO_NAS` protokolliert.

### 6.3 Gesamtaufruf `run(...)`

Die Methode `run(...)` erzeugt zunächst immer ein lokales Backup.
Nur wenn ein `nas_path` übergeben wird, folgt zusätzlich die NAS-
Synchronisation.

Der Rückgabewert ist ein `BackupResult` mit:

- `backup_path`
- `size_bytes`
- `synced_to_nas`

---

## 7. Audit-Log für Backup und Restore

Backup- und Restore-Vorgänge werden über `_log_audit(...)` in die Tabelle
`audit_log` geschrieben.

Die Einträge werden mit folgenden festen Attributen erzeugt:

- `object_type = "backup_service"`
- `object_id = 0`
- `user_id = None`
- `employee_id = None`

### 7.1 Ereignisse

| `event_type` | Auslöser | Nachweisbarer Inhalt von `details_json` |
|---|---|---|
| `BACKUP_CREATED` | nach erfolgreichem lokalem Backup | `backup_path`, `size_bytes`, optional `export_dir` |
| `BACKUP_SYNCED_TO_NAS` | nach erfolgreichem NAS-Sync | `nas_path` |
| `BACKUP_SYNC_FAILED` | nach fehlgeschlagenem NAS-Sync | `nas_path`, `returncode`, `cmd`, `stderr` |
| `RESTORE_COMPLETED` | nach Restore und Integritätsprüfung | `backup_path`, `backup_mtime` |

### 7.2 Beispielabfragen

Letzte Backup- und Restore-Ereignisse:

```sql
SELECT event_type, event_at, details_json
FROM audit_log
WHERE object_type = 'backup_service'
ORDER BY event_at DESC
LIMIT 20;
```

Nur fehlgeschlagene NAS-Synchronisationen:

```sql
SELECT event_at, details_json
FROM audit_log
WHERE event_type = 'BACKUP_SYNC_FAILED'
ORDER BY event_at DESC
LIMIT 5;
```

---

## 8. NAS-Synchronisation

### 8.1 Aktivierung

Die technische Aktivierung erfolgt über `system_config`:

- `backup.nas_enabled`
- `backup.nas_path`

Die Werte werden im Code als JSON gelesen.
Daher ist `backup.nas_enabled` als JSON-Boolean und `backup.nas_path` als
JSON-String zu speichern.

### 8.2 Beispielhafte SQL-Einträge

```sql
INSERT INTO system_config (config_key, config_value_json, changed_by, changed_at)
VALUES ('backup.nas_enabled', 'true', 'admin', datetime('now'));

INSERT INTO system_config (config_key, config_value_json, changed_by, changed_at)
VALUES ('backup.nas_path', '"/mnt/nas/arbeitszeit-backup"', 'admin', datetime('now'));
```

### 8.3 Reichweite der Prüfung

Der Systemcheck testet die NAS-Erreichbarkeit nicht per Ping oder TCP-Verbindung.
Nachweisbar geprüft werden nur:

- ob `backup.nas_enabled` vorhanden ist,
- ob bei aktivem NAS `backup.nas_path` vorhanden ist,
- ob der konfigurierte Pfad existiert,
- ob der Pfad schreibbar ist.

Die Implementierung geht ausdrücklich von einem eingebundenen Dateisystem-Mount
als NAS-Ziel aus.

---

## 9. Systemcheck-Bezug

Der Systemcheck ist in
`src/arbeitszeit/infrastructure/system_check.py` implementiert und über die
Admin-CLI mit `system check` aufrufbar.

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db /pfad/zu/arbeitszeit.db \
  --user-id <ID> \
  system check
```

### 9.1 Backup-relevante Prüfungen

Nachweisbar backup-relevant sind folgende Prüfungen:

| Prüfung | Quelle | Bedeutung |
|---|---|---|
| `config_keys` | `system_config` | prüft, ob `backup.nas_enabled` und `backup.nas_path` vorhanden sind |
| `nas_reachability` | `system_config` und Dateisystem | prüft bei aktiviertem NAS Pfad-Existenz und Schreibbarkeit |
| `config_file_paths` | `config.toml` | prüft, ob `backup_dir` und `export_dir` aus `config.toml` existieren, sofern `AppConfig` übergeben wurde |

### 9.2 Wichtige Abgrenzung

Nicht nachweisbar ist eine Pflichtprüfung von `backup.backup_dir` oder
`export.export_dir` in `system_config` durch `_REQUIRED_CONFIG_KEYS`.
Diese beiden DB-Schlüssel gehören nicht zur dort definierten Pflichtliste.

---

## 10. Restore

Ein Admin-CLI-Unterbefehl `system restore` ist im Repository nicht vorhanden.
Der Restore ist ausschließlich über die Methode `restore_from(...)` des
`SQLiteBackupService` implementiert.

### 10.1 Vorbedingungen

Aus Code und begleitender Dokumentation sind folgende Vorbedingungen belegbar:

| Vorbedingung | Status |
|---|---|
| Ziel-Backup-Datei existiert | technisch zwingend |
| Keine offenen Verbindungen zur Ziel-Datenbank beim Restore | im Code als Vorbedingung dokumentiert |
| Anwendung vor Restore beenden | betrieblich erforderlich, im Code nicht automatisiert |
| Restore-Freigabe gemäß `restore_checkliste.md` | organisatorisch dokumentiert |

### 10.2 Programmatischer Aufruf

Ein minimaler Restore-Aufruf ist nachweisbar in dieser Form möglich:

```python
from pathlib import Path
from arbeitszeit.infrastructure.backup import SQLiteBackupService

service = SQLiteBackupService(
    db_path=Path("/pfad/zu/arbeitszeit.db"),
    backup_dir=Path("/pfad/zum/backup-verzeichnis"),
)

service.restore_from(
    Path("/pfad/zum/backup-verzeichnis/arbeitszeit_YYYYMMDDTHHMMSSZ.db")
)
```

Wenn Exportdateien zusätzlich zurückkopiert werden sollen, ist ein Aufruf mit
`restore_exports=True` und gesetztem `export_dir` möglich.

### 10.3 Ablauf des Restore

Die Methode `restore_from(...)` führt nachweisbar folgende Schritte aus:

1. Prüfung, ob die Backup-Datei existiert; sonst `FileNotFoundError`.
2. Öffnen von Backup-Datei und Ziel-Datenbank.
3. Rückkopie per SQLite-Backup-API von Backup nach Ziel.
4. Ausführung von `PRAGMA integrity_check` auf der wiederhergestellten
   Ziel-Datenbank.
5. Bei Ergebnis ungleich `ok`: `RuntimeError`.
6. Optionales Zurückkopieren von `backup_path.parent / "exports"` nach
   `export_dir`, wenn `restore_exports=True` und `export_dir` gesetzt ist.
7. Schreiben von `RESTORE_COMPLETED` in das Audit-Log.

### 10.4 Besonderheit des Audit-Eintrags

Der Eintrag `RESTORE_COMPLETED` wird bewusst erst nach dem Restore in die
wiederhergestellte Datenbank geschrieben.
Damit dokumentiert der Eintrag den Restore-Vorgang im neuen Ist-Zustand und
nicht im gesicherten Stand der Backup-Datei.

---

## 11. Wiederherstellung von Exportdateien

Die Behandlung von Exportdateien ist im Code klar getrennt von der
Datenbankwiederherstellung.

### 11.1 Beim Backup

Wenn `export_dir` gesetzt ist und das Verzeichnis existiert, wird dessen Inhalt
nach `backup_dir/exports/` kopiert.

### 11.2 Beim Restore

Ein Rückkopieren erfolgt nur, wenn beide Bedingungen erfüllt sind:

- `restore_exports=True`
- `self._export_dir` ist gesetzt

Zusätzlich muss das Verzeichnis `backup_path.parent / "exports"` existieren.
Ohne diese Bedingungen findet keine Wiederherstellung der Exportdateien statt.

---

## 12. Operative Durchführung des Restore

Das Repository enthält kein dauerhaftes Skript `restore_einmalig.py`.
Nachweisbar ist nur die zugrunde liegende Python-API.

Für den operativen Betrieb ist daher belegbar ableitbar:

1. Anwendung und sonstige Zugriffe beenden.
2. Ziel-Backup identifizieren.
3. Restore über einen gezielten Python-Aufruf der API ausführen.
4. Danach Anwendung und Systemcheck erneut starten.
5. Restore anhand Audit-Log und Funktionsprüfung kontrollieren.

### 12.1 Backup-Dateien identifizieren

Beispielhafte Shell-Abfrage:

```bash
ls -lt /pfad/zum/backup-verzeichnis/arbeitszeit_*.db
```

Beispielhafte Audit-Log-Abfrage:

```sql
SELECT event_at, details_json
FROM audit_log
WHERE event_type = 'BACKUP_CREATED'
ORDER BY event_at DESC
LIMIT 10;
```

### 12.2 Funktionsprüfung nach Restore

Nachweisbar sinnvoll und mit Repository-Artefakten abgestützt sind mindestens:

- Systemcheck über `system check`
- Start der Terminal-UI
- Sichtprüfung des Audit-Log-Eintrags `RESTORE_COMPLETED`

Beispiel für den Systemcheck:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db /pfad/zu/arbeitszeit.db \
  --user-id <ID> \
  system check
```

---

## 13. Nicht nachweisbare oder nicht implementierte Punkte

Folgende Aussagen sind im Repository nicht als technische Funktion
nachweisbar und werden deshalb bewusst nicht als implementierte Eigenschaft
beschrieben:

- ein CLI-Befehl `system restore`,
- ein dauerhaft im Repository enthaltenes Restore-Hilfsskript,
- automatische Backup-Rotation oder Aufräumlogik,
- eine Prüfung von `backup.backup_dir` und `export.export_dir` als
  Pflichtschlüssel im Systemcheck,
- eine technische Freigabelogik für Restore-Vorgänge,
- eine im Code definierte Langzeitarchivierung jenseits der NAS-Spiegelung.

---

## 14. Zugehörige Dokumente

| Dokument | Bezug |
|---|---|
| [backup_zeitplan_und_automatisierung.md](backup_zeitplan_und_automatisierung.md) | Zeitplanung und Automatisierung von Backups |
| [restore_checkliste.md](restore_checkliste.md) | operative Freigabe- und Durchführungsschritte für Restore |
| [betriebsdokumentation_arbeitszeit_v1_1.md](betriebsdokumentation_arbeitszeit_v1_1.md) | übergeordnete Betriebsdokumentation |
| `scripts/backup.py` | eigenständiges Backup-Skript |
| `src/arbeitszeit/infrastructure/backup/backup_service.py` | technische Backup- und Restore-Implementierung |
| `src/arbeitszeit/presentation/admin_cli/system.py` | Admin-CLI für `system backup` und `system check` |
| `src/arbeitszeit/infrastructure/system_check.py` | technische Prüfungen mit Backup-Bezug |

---

## 15. Versionsvermerk

**Vorversion:** 1.0

**Neue Version:** 1.1

**Begründung der Versionserhöhung:**
Minor-Erhöhung aufgrund evidenzbasierter Korrekturen und Präzisierungen ohne
grundlegende Änderung der Dokumentlogik. Insbesondere wurden die tatsächlichen
Vorrangregeln von `config.toml` und `system_config`, die reale Reichweite des
Systemchecks sowie die nachweisbaren Restore-Wege an den Repository-Stand
angepasst.
