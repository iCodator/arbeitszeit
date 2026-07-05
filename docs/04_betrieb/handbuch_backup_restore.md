# Handbuch: Backup und Restore – System „arbeitszeit"

**System:** arbeitszeit
**Dokumenttyp:** Betriebshandbuch – Backup und Restore
**Version:** 1.0
**Stand:** 2026-07-05
**Zielgruppe:** Rollen ADMIN, TECH

> Dieses Handbuch beschreibt, wie Backups der Datenbank ausgelöst und wie die
> Datenbank aus einem Backup wiederhergestellt wird. Es ergänzt
> `backup_zeitplan_und_automatisierung.md` (cron/systemd-Zeitplan) und
> `restore_checkliste.md` (Freigabe-Checkliste), ohne diese zu duplizieren.

---

## 1. Überblick

Das System kennt zwei Wege, ein Backup auszulösen:

1. **Admin-CLI** (`admin system backup`) — erfordert Anmeldung als ADMIN oder TECH
2. **Standalone-Script** (`scripts/backup.py`) — keine Rollenprüfung, geeignet für Cron/systemd

Für den Restore gibt es **keinen CLI-Befehl**. Der Restore wird als einmaliges
Python-Script ausgeführt (siehe Abschnitt 6).

**Technische Grundlage:** Beide Wege nutzen die SQLite Online Backup API. Die
Datenbank bleibt während des gesamten Backup-Vorgangs vollständig les- und schreibbar —
kein Schreibstopp, keine Sperre.

---

## 2. Konfigurationsschlüssel (`system_config`)

Alle Backup-Pfade werden in der `system_config`-Tabelle der Datenbank gespeichert.

| Schlüssel | Typ | Standard | Pflicht für |
|---|---|---|---|
| `backup.backup_dir` | JSON-String | nicht gesetzt | `admin system backup` |
| `backup.nas_enabled` | JSON-Boolean | `false` | NAS-Sync (optional) |
| `backup.nas_path` | JSON-String oder null | `null` | NAS-Sync (optional) |
| `export.export_dir` | JSON-String | nicht gesetzt | Export-Mitnahme (optional) |

### Konfiguration setzen (SQL)

```sql
-- Lokales Backup-Verzeichnis (Pflicht für admin system backup)
INSERT INTO system_config (config_key, config_value_json, changed_by, changed_at)
VALUES ('backup.backup_dir', '"/var/backups/arbeitszeit"', 'admin', datetime('now'));

-- Export-Verzeichnis (optional — CSV/PDF werden ins Backup kopiert)
INSERT INTO system_config (config_key, config_value_json, changed_by, changed_at)
VALUES ('export.export_dir', '"/opt/arbeitszeit/exports"', 'admin', datetime('now'));
```

Werte werden als JSON gespeichert: Strings in Anführungszeichen, Booleans ohne.
Bei mehrfach gesetztem Schlüssel gilt immer der Eintrag mit der höchsten `version`.

### Konfiguration lesen (SQL)

```sql
SELECT config_key, config_value_json
FROM system_config
ORDER BY config_key, version DESC;
```

---

## 3. Backup manuell auslösen

### 3.1 Admin-CLI (Rolle ADMIN oder TECH)

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db /pfad/zu/arbeitszeit.db \
  --user-id <ID> \
  system backup
```

**Ablauf:**

1. Rollenprüfung: nur ADMIN oder TECH darf diesen Befehl ausführen
2. Liest `backup.backup_dir` aus `system_config` — fehlt der Schlüssel, Abbruch mit Exit 1
3. Liest optional `export.export_dir` aus `system_config`
4. Erstellt lokales Backup
5. Prüft `backup.nas_enabled`; wenn aktiv, liest `backup.nas_path` und löst NAS-Sync aus

**Beispielausgabe (ohne NAS):**

```
Backup erstellt: /var/backups/arbeitszeit/arbeitszeit_20260705T200000Z.db
```

**Beispielausgabe (mit NAS):**

```
Backup erstellt: /var/backups/arbeitszeit/arbeitszeit_20260705T200000Z.db
NAS-Synchronisation erfolgreich.
```

### 3.2 Standalone-Script (kein Login erforderlich)

```bash
cd /pfad/zu/arbeitszeit
source .venv/bin/activate

python scripts/backup.py \
  --db arbeitszeit.db \
  --backup-dir /var/backups/arbeitszeit \
  [--export-dir /pfad/zu/exports]
```

**Unterschied zur Admin-CLI:** Das Backup-Verzeichnis wird hier als CLI-Argument
übergeben (`--backup-dir`), nicht aus `system_config` gelesen. Der NAS-Sync liest
weiterhin `backup.nas_enabled` und `backup.nas_path` aus der Datenbank.

**Beispielausgabe:**

```
Backup: /var/backups/arbeitszeit/arbeitszeit_20260705T200000Z.db  (2.048.576 Bytes)
NAS-Sync: deaktiviert
```

**Hilfe anzeigen:**

```bash
python scripts/backup.py --help
```

---

## 4. Was das Backup intern tut

Der Reihe nach:

1. Erstellt `backup_dir` mit `mkdir -p`, falls nicht vorhanden
2. Generiert Zeitstempel im Format `YYYYMMDDTHHMMSSZ` (UTC)
3. Öffnet die laufende Datenbank und eine neue Datei `backup_dir/arbeitszeit_<Zeitstempel>.db`
4. Kopiert den Datenbankinhalt via **SQLite Online Backup API** (`src.backup(dst)`) —
   die Quelldatenbank bleibt dabei vollständig nutzbar
5. Falls `export_dir` gesetzt und vorhanden: kopiert den gesamten Inhalt des
   Export-Verzeichnisses via `shutil.copytree` nach `backup_dir/exports/`
   (vorhandene Dateien werden überschrieben)
6. Schreibt einen `BACKUP_CREATED`-Eintrag ins `audit_log`
7. Wenn NAS-Sync aktiv: führt
   `/usr/bin/rsync --archive --delete {backup_dir}/ {nas_path}/` aus
8. Bei rsync-Erfolg: schreibt `BACKUP_SYNCED_TO_NAS` ins `audit_log`
9. Bei rsync-Fehler: schreibt `BACKUP_SYNC_FAILED` ins `audit_log` und gibt die
   Ausnahme weiter (Abbruch mit Exit 1)

> **Hinweis:** Es gibt keine automatische Rotation. Backup-Dateien akkumulieren
> im `backup_dir`. Das Aufräumen alter Backups ist Betriebsaufgabe. Richtwert:
> mindestens 30 tägliche Backups aufbewahren (§ 16 Abs. 2 ArbZG: 2 Jahre).
> Siehe `backup_zeitplan_und_automatisierung.md` Abschnitt 7.

---

## 5. NAS-Synchronisation einrichten

Das NAS muss als Dateisystem-Mount eingebunden sein (z.B. `/mnt/nas/...`). Es wird
kein Netzwerk-Ping durchgeführt — die Erreichbarkeit wird über die Existenz und
Schreibbarkeit des Mount-Pfads geprüft.

### Konfiguration aktivieren

```sql
-- NAS aktivieren
INSERT INTO system_config (config_key, config_value_json, changed_by, changed_at)
VALUES ('backup.nas_enabled', 'true', 'admin', datetime('now'));

-- NAS-Zielpfad setzen (Mount-Punkt)
INSERT INTO system_config (config_key, config_value_json, changed_by, changed_at)
VALUES ('backup.nas_path', '"/mnt/nas/arbeitszeit-backup"', 'admin', datetime('now'));
```

### Konfiguration deaktivieren

```sql
INSERT INTO system_config (config_key, config_value_json, changed_by, changed_at)
VALUES ('backup.nas_enabled', 'false', 'admin', datetime('now'));
```

### Systemcheck

`admin system check` (Rolle ADMIN oder TECH) prüft automatisch:

- Ist `backup.nas_enabled` in `system_config` vorhanden?
- Wenn aktiv: Ist `backup.nas_path` gesetzt?
- Ist der NAS-Pfad im Dateisystem erreichbar (`Path.exists()`)?
- Ist der NAS-Pfad schreibbar (`os.access(..., W_OK)`)?

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db /pfad/zu/arbeitszeit.db --user-id <ID> \
  system check
```

---

## 6. Datenbank wiederherstellen (Restore)

> **Wichtig:** Es gibt keinen `admin system restore`-Befehl. Der Restore wird als
> einmaliges Python-Script ausgeführt. Vor dem Restore muss die Anwendung gestoppt
> werden. Die Freigabe ist gemäß `restore_checkliste.md` einzuholen.

### 6.1 Vorbedingungen

| Schritt | Pflicht |
|---|---|
| Terminal-UI gestoppt | ja |
| Admin-CLI-Verbindungen beendet | ja |
| Aktuellen Ist-Zustand als Backup gesichert | empfohlen |
| Backup-Datei identifiziert und Pfad notiert | ja |
| Freigabe laut `restore_checkliste.md` eingeholt | ja |

### 6.2 Backup-Datei identifizieren

Verfügbare Backups auflisten (neueste zuerst):

```bash
ls -lt /var/backups/arbeitszeit/arbeitszeit_*.db
```

Alternativ über das Audit-Log (letzte Backups):

```sql
SELECT event_at, details_json
FROM audit_log
WHERE event_type = 'BACKUP_CREATED'
ORDER BY event_at DESC LIMIT 10;
```

### 6.3 Restore durchführen

Einmaliges Restore-Script erstellen (z.B. `scripts/restore_einmalig.py`):

```python
from arbeitszeit.infrastructure.backup import SQLiteBackupService
from pathlib import Path

service = SQLiteBackupService(
    db_path=Path("/pfad/zu/arbeitszeit.db"),
    backup_dir=Path("/var/backups/arbeitszeit"),
    # export_dir=Path("/pfad/zu/exports"),  # nur wenn Exportdateien mitwiederhergestellt werden sollen
)

service.restore_from(
    Path("/var/backups/arbeitszeit/arbeitszeit_20260705T200000Z.db"),
    # restore_exports=True,  # optional: Exportdateien aus backup_dir/exports/ zurückkopieren
)

print("Restore abgeschlossen.")
```

Script ausführen:

```bash
cd /pfad/zu/arbeitszeit
source .venv/bin/activate
python scripts/restore_einmalig.py
```

Nach dem Restore Script löschen:

```bash
rm scripts/restore_einmalig.py
```

### 6.4 Was der Restore intern tut

1. Prüft ob `backup_path` existiert — `FileNotFoundError` wenn nicht
2. Überschreibt `db_path` via **SQLite Online Backup API**
3. Führt `PRAGMA integrity_check` aus — `RuntimeError` wenn Ergebnis ≠ `"ok"`
4. Optional (`restore_exports=True`): kopiert `backup_dir/exports/` zurück in `export_dir`
5. Schreibt `RESTORE_COMPLETED` in die **neu wiederhergestellte** Datenbank

> **Hinweis:** Der `RESTORE_COMPLETED`-Eintrag landet in der wiederhergestellten DB,
> nicht in der Vor-Restore-Datenbank. Das ist beabsichtigt: Der Eintrag dokumentiert
> den Restore-Vorgang im neuen Ist-Zustand.

### 6.5 Funktionsprüfung nach Restore

```bash
# Systemcheck ausführen
python -m arbeitszeit.presentation.admin_cli.main \
  --db /pfad/zu/arbeitszeit.db --user-id <ID> \
  system check

# Terminal-UI starten
python -m arbeitszeit.presentation.terminal_ui.main \
  --db /pfad/zu/arbeitszeit.db --numpad /dev/... --rfid /dev/... --terminal-id 1
```

---

## 7. Audit-Log: Was wird protokolliert?

Alle Backup- und Restore-Ereignisse werden in die `audit_log`-Tabelle geschrieben
(`object_type = 'backup_service'`, `user_id = NULL`, `employee_id = NULL`).

| `event_type` | Wann | Felder in `details_json` |
|---|---|---|
| `BACKUP_CREATED` | nach erfolgreichem lokalem Backup | `backup_path`, `size_bytes`[, `export_dir`] |
| `BACKUP_SYNCED_TO_NAS` | nach erfolgreichem NAS-Sync | `nas_path` |
| `BACKUP_SYNC_FAILED` | nach fehlgeschlagenem NAS-Sync | `nas_path`, `returncode`, `cmd`, `stderr` |
| `RESTORE_COMPLETED` | nach Restore + Integritätsprüfung | `backup_path`, `backup_mtime` |

### Letzte Backup-Ereignisse abfragen

```sql
SELECT event_type, event_at, details_json
FROM audit_log
WHERE object_type = 'backup_service'
ORDER BY event_at DESC
LIMIT 20;
```

### NAS-Sync-Fehler prüfen

```sql
SELECT event_at, details_json
FROM audit_log
WHERE event_type = 'BACKUP_SYNC_FAILED'
ORDER BY event_at DESC
LIMIT 5;
```

---

## 8. Systemcheck-Integration

`admin system check` prüft folgende Backup-relevante Punkte:

| Prüfpunkt | Bedingung für Bestehen |
|---|---|
| `backup.nas_enabled` in `system_config` | Schlüssel vorhanden |
| `backup.nas_path` in `system_config` | Schlüssel vorhanden |
| `backup.backup_dir` in `system_config` | Schlüssel vorhanden |
| `export.export_dir` in `system_config` | Schlüssel vorhanden |
| NAS-Pfad erreichbar | `Path.exists()` = True (nur wenn `nas_enabled = true`) |
| NAS-Pfad schreibbar | `os.access(..., W_OK)` = True (nur wenn `nas_enabled = true`) |

> **Hinweis:** Die Schlüssel `backup.backup_dir` und `export.export_dir` werden vom
> Systemcheck auf Vorhandensein geprüft, aber nicht automatisch durch Migrationen
> gesetzt. Sie müssen nach der Erstinstallation manuell konfiguriert werden
> (siehe Abschnitt 2).

---

## 9. Zugehörige Dokumente

| Dokument | Inhalt |
|---|---|
| [backup_zeitplan_und_automatisierung.md](backup_zeitplan_und_automatisierung.md) | cron/systemd-Automatisierung, Aufbewahrungsfristen, Zeitplan |
| [restore_checkliste.md](restore_checkliste.md) | Freigabe-Checkliste und Nachweisprotokoll für Restore-Vorgänge |
| [betriebsdokumentation_arbeitszeit_v1_1.md](betriebsdokumentation_arbeitszeit_v1_1.md) | Gesamtbetriebsdokumentation |
| `scripts/backup.py` | Standalone-Script (`--help` für Optionen) |
| `src/arbeitszeit/infrastructure/backup/backup_service.py` | Technische Implementierung |

---

## 10. Änderungshistorie

| Version | Datum | Änderung | Verantwortlich |
|---|---|---|---|
| 1.0 | 2026-07-05 | Erstfassung | __________________ |
