# Prüfbericht: `docs/betrieb/backup_zeitplan_und_automatisierung.md`

**Geprüftes Dokument:** `docs/betrieb/backup_zeitplan_und_automatisierung.md` (Version 1.0, Stand 2026-06-12)
**Geprüft gegen:** `src/arbeitszeit/infrastructure/backup/backup_service.py`, `scripts/backup.py`, `src/arbeitszeit/presentation/admin_cli/system.py`, `src/arbeitszeit/presentation/admin_cli/main.py`, `src/arbeitszeit/infrastructure/system_check.py`, `src/arbeitszeit/domain/audit_events.py`, `tests/e2e/test_backup.py`

## Gesamteinschätzung

Das Dokument beschreibt die Backup-Automatisierung ausschließlich auf Basis des Skripts `scripts/backup.py` und erwähnt den eigentlichen Backup-Dienst `src/arbeitszeit/infrastructure/backup/backup_service.py` nicht. Die zentralen technischen Kernaussagen zu Backup-Arten, Methodennamen und Audit-Ereignissen sind mit dem Code konsistent, jedoch enthält Kapitel 4.3 eine faktisch falsche CLI-Option (`--nas-path`), die im tatsächlichen Skript nicht existiert. Organisatorische Inhalte (Zeitpläne als Empfehlung, Verantwortlichkeitstabellen, auszufüllende Formularfelder) sind erwartungsgemäß nicht gegen Code prüfbar und wurden entsprechend gekennzeichnet.

---

## Kapitel 1: Ziel des Backup-Konzepts

**Aussage:** „Ziel ist es, die Arbeitszeitdaten so zu sichern, dass … die Wiederherstellung aus einem Backup mit vertretbarem Aufwand möglich ist.“
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Zielformulierung ohne prüfbaren technischen Gehalt; betrifft betriebliche Zielsetzung, nicht Code-Verhalten.

**Aussage:** Bezugnahme auf § 16 Abs. 2 ArbZG (mindestens zwei Jahre Aufbewahrung).
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Rechtliche/regulatorische Aussage, nicht durch Repository-Code verifizierbar.

---

## Kapitel 2: Backup-Arten im System „arbeitszeit“

**Aussage:** „`scripts/backup.py` unterstützt zwei grundlegende Backup-Arten: 1. Lokales Backup (Kopie der SQLite-Datenbank, optional Exportverzeichnisse), 2. NAS-Spiegelung (optional) per `rsync`.“
**Status:** korrekt
**Beleg:** `scripts/backup.py` Zeilen 17, 59-60 (Aufruf von `SQLiteBackupService(...).run(nas_path=...)`); `src/arbeitszeit/infrastructure/backup/backup_service.py` Zeilen 35-68 (`create_local_backup`, inkl. optionalem Kopieren von `export_dir` nach `backup_dir/exports/`) und Zeilen 70-96 (`sync_to_nas`, Aufruf von `rsync --archive --delete`).
**Bewertung:** Die Beschreibung der zwei Backup-Arten und deren technische Umsetzung (SQLite-Kopie via `create_local_backup`, NAS-Spiegelung via `rsync` in `sync_to_nas`) ist mit dem Code der `SQLiteBackupService`-Klasse konsistent, auf die `scripts/backup.py` intern zurückgreift.

**Aussage:** „Kopie der SQLite-Datenbank (und optional der Exportverzeichnisse) in ein lokales Backup-Verzeichnis.“
**Status:** korrekt
**Beleg:** `backup_service.py` Zeilen 35-60, Methode `create_local_backup`: nutzt die SQLite-Backup-API (`src.backup(dst)`) und kopiert bei gesetztem und existierendem `export_dir` per `shutil.copytree` nach `backup_dir/exports/`.
**Bewertung:** Vollständig durch Code belegt.

**Aussage:** „NAS-Spiegelung (optional): Spiegelung des Backup-Verzeichnisses auf ein Netzlaufwerk (NAS) per `rsync`.“
**Status:** korrekt
**Beleg:** `backup_service.py` Zeilen 70-96, Methode `sync_to_nas`: `subprocess.run(["rsync", "--archive", "--delete", f"{self._backup_dir}/", f"{nas_path}/"], ...)`.
**Bewertung:** Exakt durch Code belegt, inklusive der verwendeten rsync-Optionen.

---

## Kapitel 3: Empfohlener Zeitplan

**Aussage:** Tägliches Backup Mo–Fr gegen 20:30 Uhr, Zeitfenster 20:00–06:00 Uhr, wöchentliches Voll-Check-Backup optional.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Explizit als betriebliche Empfehlung gekennzeichnet („Empfohlener Zeitplan“, „Empfehlung“); kein im Code hinterlegter Zeitplan, der geprüft werden könnte. Der Code selbst enthält keine feste Ausführungszeit — diese wird ausschließlich extern (cron/systemd) konfiguriert.

---

## Kapitel 4: Beispiel — Automatisierung mit `cron`

**Aussage:** „Sicherstellen, dass `scripts/backup.py` lauffähig ist“, Aufruf `python scripts/backup.py --help`.
**Status:** korrekt
**Beleg:** `scripts/backup.py` Zeilen 1-70, insbesondere `argparse.ArgumentParser` ab Zeile 23; Skript ist direkt ausführbar (`if __name__ == "__main__": main()`, Zeilen 69-70).
**Bewertung:** Das Skript existiert im angegebenen Pfad und ist als CLI mit `argparse` (inkl. automatischer `--help`-Ausgabe) ausgestattet.

**Aussage:** CLI-Aufruf mit Parametern `--db` und `--backup-dir`:
```
python scripts/backup.py --db /pfad/zu/arbeitszeit.db --backup-dir /var/backups/arbeitszeit
```
**Status:** korrekt
**Beleg:** `scripts/backup.py` Zeilen 24-35: `parser.add_argument("--db", ...)`, `parser.add_argument("--backup-dir", ...)`.
**Bewertung:** Beide Parameternamen sind exakt im Skript als Argparse-Optionen definiert.

**Aussage:** „`30 20 * * 1-5`: Mo–Fr um 20:30 Uhr.“ (Cron-Zeitplan)
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Als betriebliche Musterkonfiguration gekennzeichnet („Hinweis: Die folgenden Beispiele sind als Muster gedacht“); nicht im Code oder in einer Konfigurationsdatei des Repositorys hinterlegt.

**Aussage:** „Ausgabe wird in `backup.log` protokolliert, um Erfolge/Fehler nachprüfen zu können.“
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Betrifft die Ausgabeumleitung im Cron-Beispiel (Shell-Redirection `>>`), keine Funktion des Backup-Codes selbst; das Skript schreibt selbst keine Logdatei, sondern gibt Ergebnisse auf `stdout`/`stderr` aus (`scripts/backup.py` Zeilen 48, 62-66).

### Kapitel 4.3: Cronjob mit NAS-Spiegelung

**Aussage:** CLI-Aufruf mit Parameter `--nas-path`:
```
python scripts/backup.py --db /pfad/zu/arbeitszeit.db --backup-dir /var/backups/arbeitszeit --nas-path /mnt/nas/arbeitszeit-backup
```
**Status:** inkorrekt
**Beleg:** `scripts/backup.py` Zeilen 23-42 (vollständige `argparse`-Definition): Es existieren ausschließlich die Argumente `--db`, `--backup-dir` und `--export-dir`. Ein Argument `--nas-path` ist nicht definiert.
**Bewertung:** Das Skript liest die NAS-Konfiguration stattdessen aus der Datenbank über `SQLiteSystemConfigRepository` unter den Schlüsseln `backup.nas_enabled` und `backup.nas_path` (`scripts/backup.py` Zeilen 52-56: `config.get_current("backup.nas_enabled")`, `config.get_current("backup.nas_path")`). Ein CLI-Flag `--nas-path` würde beim Aufruf zu einem `argparse`-Fehler („unrecognized arguments“) führen. Diese Aussage widerspricht damit direkt dem Code.
**Anpassungsvorschlag:** Abschnitt 4.3 korrigieren: NAS-Sync wird nicht über ein CLI-Flag gesteuert, sondern über die in der Datenbank hinterlegten `system_config`-Einträge `backup.nas_enabled` (Boolean) und `backup.nas_path` (Pfad-String), wie im Docstring von `scripts/backup.py` (Zeilen 1-9) beschrieben. Der Cronjob-Befehl sollte entsprechend ohne `--nas-path` dargestellt werden, mit dem Hinweis, dass die NAS-Aktivierung vorab per Konfiguration (nicht per CLI-Parameter) erfolgen muss.

**Aussage:** „Voraussetzung: NAS-Einbindung wurde vorher eingerichtet und getestet.“
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Organisatorischer Hinweis ohne prüfbaren Code-Bezug.

---

## Kapitel 5: Automatisierung mit `systemd`-Timer

**Aussage:** Service-Unit ruft `python scripts/backup.py --db ... --backup-dir ...` auf (ohne `--nas-path`).
**Status:** korrekt
**Beleg:** `scripts/backup.py` Zeilen 24-35 (Argumente `--db`, `--backup-dir` existieren); im Gegensatz zu Kapitel 4.3 wird hier korrekt kein `--nas-path`-Flag verwendet.
**Bewertung:** Konsistent mit der tatsächlichen Argumentliste des Skripts.

**Aussage:** Inhalte der Service-Unit- und Timer-Unit-Dateien (`/etc/systemd/system/arbeitszeit-backup.service`, `.timer`), `OnCalendar=Mon..Fri 20:30`.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Reine Infrastruktur-/Betriebskonfiguration außerhalb des Repository-Codes, als Beispiel gekennzeichnet.

---

## Kapitel 6: Verantwortlichkeiten und Kontrolle

**Aussage:** Tabelle mit Aufgaben, Verantwortlichkeiten (TECH/Admin, Praxisleitung) und Frequenzen.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Rollen- und Prozessorganisation, nicht im Code abgebildet.

---

## Kapitel 7: Aufbewahrung und Löschkonzept für Backups

**Aussage:** „Empfehlung: mind. 30 tägliche Backups aufbewahren“, „6 Monats-Backups“, Löschplan.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Es existiert im Code keine automatische Rotations- oder Löschlogik für Backups; weder `backup_service.py` noch `scripts/backup.py` enthalten Funktionen zum Entfernen alter Backup-Dateien. Die Aussage ist ausdrücklich als betriebliche Empfehlung/Beispielstrategie formuliert und daher als organisatorisch einzustufen, nicht als technische (widerlegbare) Behauptung über vorhandene Code-Funktionalität.

---

## Kapitel 8: Dokumentation der eingerichteten Backup-Automatisierung

**Aussage:** Auszufüllende Formularfelder (Methode, verantwortliche Person, Datum, Pfad, Protokolldatei).
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Formularvorlage ohne technischen Prüfgehalt.

---

## Kapitel 9: Änderungen und Historie

**Aussage:** Versionstabelle mit Datum und Änderungsvermerk.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Dokumentenverwaltung, kein Code-Bezug.

---

## Zusätzlicher Befund: Fehlende Erwähnung des eigentlichen Backup-Dienstes

**Beobachtung:** Das Dokument beschreibt ausschließlich `scripts/backup.py` als Automatisierungsgrundlage und erwähnt weder die Klasse `SQLiteBackupService` in `src/arbeitszeit/infrastructure/backup/backup_service.py` noch den administrativen CLI-Befehl `admin system backup` in `src/arbeitszeit/presentation/admin_cli/system.py` (Zeilen 31-92, registriert als Subparser `("system", "backup")` in `src/arbeitszeit/presentation/admin_cli/system.py` Zeile 101).
**Status:** nicht verifizierbar (als Auslassung, nicht als Falschaussage)
**Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py` Zeilen 31-101; `src/arbeitszeit/infrastructure/backup/backup_service.py` Zeilen 23-178.
**Bewertung:** Das Dokument macht keine falsche Aussage über den `admin_cli`-Befehl, da es ihn schlicht nicht erwähnt. Da im Repository zwei parallele Wege zum Auslösen eines Backups existieren (`scripts/backup.py` und `admin system backup`), die sich in der Bedienung unterscheiden (CLI-Flags vs. `system_config`-gesteuert ohne Flags), könnte die Beschränkung auf `scripts/backup.py` in der Praxis zu Verwirrung führen. Dies ist kein inhaltlicher Fehler, sondern eine Vollständigkeitslücke.
**Anpassungsvorschlag:** Ergänzung eines Hinweises, dass alternativ der administrative Befehl `admin system backup` zur Verfügung steht (siehe `src/arbeitszeit/presentation/admin_cli/system.py`, Funktion `cmd_system_backup`), der Backup-Verzeichnis, Export-Verzeichnis und NAS-Konfiguration ausschließlich aus der `system_config`-Tabelle liest und keine CLI-Parameter für Pfade entgegennimmt.

---

## Zusätzlicher Befund: Audit-Ereignistypen (nicht im Dokument erwähnt, aber Teil des Prüfauftrags)

**Aussage (Prüfauftrag):** Prüfung der Audit-Ereignistypen `BACKUP_CREATED`, `BACKUP_SYNC_FAILED`, `BACKUP_SYNCED_TO_NAS`.
**Status:** korrekt (Existenz im Code bestätigt; im Dokument selbst nicht erwähnt)
**Beleg:** `src/arbeitszeit/domain/audit_events.py` Zeilen 35-37: `BACKUP_CREATED = "BACKUP_CREATED"`, `BACKUP_SYNCED_TO_NAS = "BACKUP_SYNCED_TO_NAS"`, `BACKUP_SYNC_FAILED = "BACKUP_SYNC_FAILED"`; Verwendung in `backup_service.py` Zeile 67 (`self._log_audit(audit_events.BACKUP_CREATED, details)`), Zeile 87 (`BACKUP_SYNC_FAILED`), Zeile 96 (`BACKUP_SYNCED_TO_NAS`); Testabdeckung in `tests/e2e/test_backup.py` Zeilen 204-266 (`test_backup_erstellt_audit_eintrag`, `test_nas_sync_erfolg_erstellt_audit_eintrag`, `test_nas_sync_fehler_erstellt_audit_eintrag_mit_cmd_und_stderr`).
**Bewertung:** Alle drei geforderten Ereignistypen existieren exakt mit den genannten Namen im Code und sind durch Tests abgesichert. Das Dokument selbst erwähnt diese Ereignistypen nicht, was keine Falschaussage, aber eine Lücke darstellt, da Kapitel 6 („Kontrolle der Backup-Logs“) von auditierbaren Vorgängen spricht, ohne auf die konkreten Audit-Ereignisse im System zu verweisen.
**Anpassungsvorschlag:** Ergänzender Hinweis, dass Backup-Vorgänge zusätzlich im Audit-Log der Anwendung (Tabelle `audit_log`) mit den Ereignistypen `BACKUP_CREATED`, `BACKUP_SYNCED_TO_NAS` bzw. bei Fehlern `BACKUP_SYNC_FAILED` protokolliert werden.
