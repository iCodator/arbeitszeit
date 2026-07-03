# Prüfbericht: `docs/module/handbuch_audit.md` (Audit und Prüfstatus)

## Gesamteinschätzung

Dieses Kapitel unterscheidet sich strukturell von den übrigen Handbuchkapiteln: Es ist selbst eine Meta-Prüfliste mit den Abschnitten „Sicher belegt", „Nicht überbehaupten" und „Empfohlene nächste Prüfungen", keine klassische Nutzerdokumentation. Alle 18 unter „Sicher belegt" aufgeführten Einzelaussagen wurden gegen den Code verifiziert und sind vollständig korrekt. Der Abschnitt „Nicht überbehaupten" formuliert bewusst Zurückhaltung statt Tatsachenbehauptungen und ist daher nicht im klassischen Sinn prüfbar. Der Abschnitt „Empfohlene nächste Prüfungen" verweist auf konkret existierende Dateien. Substanzielle Fehler wurden nicht gefunden.

## Befunde (Abschnitt „Sicher belegt")

- Aussage: „Python-Anforderung `>=3.14,<3.15`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeile 9 (`requires-python = ">=3.14,<3.15"`)
  Bewertung: Wortgleich bestätigt.

- Aussage: „Paketabhängigkeiten aus `pyproject.toml`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen 10–22
  Bewertung: Abhängigkeiten existieren wie referenziert.

- Aussage: „Trennung in `presentation`, `infrastructure`, `application`, `domain`."
  Status: korrekt
  Beleg: `pyproject.toml`, Zeilen 105–110 (`[tool.importlinter.contracts]`, `layers = ["arbeitszeit.presentation", "arbeitszeit.infrastructure", "arbeitszeit.application", "arbeitszeit.domain"]`)
  Bewertung: Exakte Schichtnamen und Reihenfolge bestätigt.

- Aussage: „Vorhandensein von `scripts/init_db.py`, `scripts/setup.py`, `scripts/backup.py`."
  Status: korrekt
  Beleg: Verzeichnisauflistung `scripts/` bestätigt alle drei Dateien.
  Bewertung: Bestätigt.

- Aussage: „Bootstrap des ersten Administratorkontos."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Zeilen 202–207 (`users_sub.add_parser("bootstrap", ...)`)
  Bewertung: Bestätigt.

- Aussage: „Zulässige Rollen für `users add`: `ADMIN`, `REVIEWER`, `TECH`."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Zeile 174 (`choices=["ADMIN", "REVIEWER", "TECH"]`)
  Bewertung: Exakt bestätigt.

- Aussage: „Mitarbeiterverwaltung über `employees add`."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/employees.py`, Zeile 140
  Bewertung: Bestätigt.

- Aussage: „`employees deactivate` und `cards deactivate` erfordern positionale IDs."
  Status: korrekt
  Beleg: `employees.py`, Zeile 146 (`deact.add_argument("id", type=int)`) und Zeile 161 (`deact_card.add_argument("id", type=int)`)
  Bewertung: Beide verwenden ein positionales Argument `id`, kein Options-Flag.

- Aussage: „`cards replace` erfordert `--old-card-id` und `--uid-hash`."
  Status: korrekt
  Beleg: `employees.py`, Zeilen 156–158
  Bewertung: Exakt bestätigt.

- Aussage: „`users deactivate`, `users reactivate` und `users change-role` erfordern ein eigenes `--user-id` für das Zielkonto."
  Status: korrekt
  Beleg: `user_accounts.py`, Zeilen 189–198: jeweils eigenes `--user-id`-Argument mit unterschiedlichem `dest` (`deactivate_user_id`, `reactivate_user_id`, `target_user_id`)
  Bewertung: Bestätigt, inklusive der Tatsache, dass dies ein separates Argument zum globalen `--user-id` des aufrufenden Admin-Kontos ist.

- Aussage: „Kartenzuweisung über `cards assign --uid-hash`."
  Status: korrekt
  Beleg: `employees.py`, Zeile 154
  Bewertung: Bestätigt.

- Aussage: „Terminal-UI mit Pflichtparametern `--db`, `--numpad`, `--rfid`, `--terminal-id`."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/terminal_ui/main.py`, Zeilen 146–149, alle vier mit `required=True`
  Bewertung: Exakt bestätigt.

- Aussage: „Admin-CLI mit verpflichtendem `--db`; Benutzer-ID alternativ über `ADMIN_USER_ID`."
  Status: korrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/main.py`, Zeilen 39–44 (`--db`, `required=True`) und Zeilen 16–32 (`_resolve_user_id`: Fallback auf `os.environ.get("ADMIN_USER_ID")`)
  Bewertung: Bestätigt.

- Aussage: „`setup.py` unterstützt nicht-interaktiven Aufruf mit `--backup-dir` und `--export-dir`."
  Status: korrekt
  Beleg: `scripts/setup.py`, Zeilen 75–86
  Bewertung: Bestätigt.

- Aussage: „Vierstellige Migrationsversionen `0001` bis `0006`."
  Status: korrekt
  Beleg: Verzeichnis `migrations/` enthält genau `0001_schema.sql` bis `0006_system_events_application_error.sql`
  Bewertung: Bestätigt.

- Aussage: „NAS-bezogene Konfigurationsschlüssel im Backup-Skript."
  Status: korrekt
  Beleg: `scripts/backup.py`, Zeilen 7–8, 53–56 (`backup.nas_enabled`, `backup.nas_path`); `src/arbeitszeit/infrastructure/backup/backup_service.py`, Zeilen 70–96 (`sync_to_nas`)
  Bewertung: Bestätigt.

- Aussage: „`scripts/verify_hardware.py` für Hardware-Smoke-Tests."
  Status: korrekt
  Beleg: Datei existiert im Repository (`scripts/verify_hardware.py`, 16430 Bytes)
  Bewertung: Bestätigt.

- Aussage: „`run_audit.sh` und `scripts/generate_audit_notes.py` für Code-Audits."
  Status: korrekt
  Beleg: Beide Dateien existieren im Repository (`run_audit.sh` ausführbar, `scripts/generate_audit_notes.py`, 20047 Bytes)
  Bewertung: Bestätigt.

## Befunde (Abschnitt „Nicht überbehaupten")

Status: nicht anwendbar / korrekt im Sinne der Selbstbeschreibung
Bewertung: Dieser Abschnitt formuliert bewusst methodische Vorsicht (z. B. „genaue interne RFID-Hash-Bildung ... nur wenn vollständig gelesen") statt inhaltlicher Tatsachenbehauptungen. Er ist daher nicht im Sinne von „korrekt/inkorrekt gegenüber dem Code" prüfbar, sondern beschreibt eine Arbeitsregel für künftige Dokumentationsarbeit. Kein Widerspruch zum Code feststellbar.

## Befunde (Abschnitt „Empfohlene nächste Prüfungen")

- Aussage: Verweis auf `migrations/0001_schema.sql`, `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`, `scripts/show_config.py`, sowie `bookings.py`, `reports.py`, `schedule.py`, `system.py` im Admin-CLI.
  Status: korrekt
  Beleg: Alle genannten Dateien/Pfade existieren im Repository und wurden in früheren bzw. weiteren Prüfzyklen dieser Space-Historie bereits einzeln behandelt (`enums.py` und `evdev_reader.py` liegen bereits als eigene Prüfberichte vor).
  Bewertung: Die Empfehlungsliste ist technisch zutreffend; ein Teil der empfohlenen Prüfungen wurde in dieser Space-Historie bereits durchgeführt.

## Anpassungsvorschläge

Keine. Alle prüfbaren Aussagen des Kapitels sind durch das Repository vollständig belegt. Kein Korrekturbedarf.
