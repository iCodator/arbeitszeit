# Handbuch `arbeitszeit` – Audit und Prüfstatus

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

## Sicher belegt

Die folgenden Aussagen sind durch die tatsächlich gelesenen Dateien abgesichert:

- Python-Anforderung `>=3.14,<3.15`
- Paketabhängigkeiten aus `pyproject.toml`
- Trennung in `presentation`, `infrastructure`, `application`, `domain`
- Vorhandensein von `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py`
- Bootstrap des ersten Administratorkontos
- Zulässige Rollen für `users add`: `ADMIN`, `REVIEWER`, `TECH`
- Mitarbeiterverwaltung über `employees add`
- `employees deactivate` und `cards deactivate` erfordern positionale IDs
- `cards replace` erfordert `--old-card-id` und `--uid-hash`
- `users deactivate`, `users reactivate` und `users change-role` erfordern
  ein eigenes `--user-id` für das Zielkonto
- Kartenzuweisung über `cards assign --uid-hash`
- Terminal-UI mit Pflichtparametern `--db`, `--numpad`, `--rfid`,
  `--terminal-id`
- Admin-CLI mit verpflichtendem `--db`; Benutzer-ID alternativ über
  `ADMIN_USER_ID`
- `setup.py` unterstützt nicht-interaktiven Aufruf mit `--backup-dir` und
  `--export-dir`
- Vierstellige Migrationsversionen `0001` bis `0006`
- NAS-bezogene Konfigurationsschlüssel im Backup-Skript
- `scripts/verify_hardware.py` für Hardware-Smoke-Tests
- `run_audit.sh` und `scripts/generate_audit_notes.py` für Code-Audits

## Nicht überbehaupten

Die folgenden Punkte sollten in einer technischen Dokumentation nur dann
detailliert dargestellt werden, wenn ihre Implementierung vollständig gelesen
und verifiziert wurde:

- genaue interne RFID-Hash-Bildung und zugehörige Dateipfade
- konkrete Restore-Abläufe und Restore-Befehle
- konkrete `system_events`-Ereignistypen außerhalb nachweislich gelesener
  Stellen
- exakte Inhalte nicht gelesener Module oder Verzeichnisse
- Hardware-Aussagen zu Plattformen, die im gelesenen Code nicht ausdrücklich
  genannt sind

## Empfohlene nächste Prüfungen

Für eine vollständige, dauerhaft belastbare Dokumentation sollten als nächstes
gezielt separat geprüft werden:

1. `migrations/0001_schema.sql` im Volltext für die exakte Datenbankdokumentation
2. `src/arbeitszeit/domain/enums.py` für belastbare Dokumentation der Enums
3. `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` für belastbare
   Hardwarebeschreibung
4. `scripts/show_config.py` nur dann dokumentieren, wenn seine Optionen und
   Ausgabeformate tatsächlich gelesen wurden
5. Admin-CLI-Unterdateien `bookings.py`, `reports.py`, `schedule.py` und
   `system.py` für vollständige Befehls- und Rollenbeschreibung
