# Prüfbericht: `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`

**Geprüftes Dokument:** `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` (Version 1.1, Datum 2026-06-13)
**Repository:** iCodator/arbeitszeit
**Prüfgrundlage:** `src/arbeitszeit/`, `scripts/`, `migrations/`, `tests/`

---

## Gesamteinschätzung

Das Dokument ist strukturell sorgfältig aus dem Code abgeleitet, enthielt jedoch mehrere konkrete technische Fehler bei CLI-Befehlen/-Flags, Event-Protokollierungszielen und einer veralteten Testkennzahl. Alle unten aufgeführten, belegten Abweichungen wurden korrigiert. Organisatorische Aussagen (Rollenverantwortung, Freigabeprozesse) sind unverändert geblieben, da sie außerhalb des Codebezugs liegen.

---

## Strukturierter Report je Aussage

**Aussage:** Bootstrap-Befehl enthält `--full-name "Vollständiger Name"`.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, `register_subcommands()`: der `bootstrap`-Subcommand kennt nur `--username` und `--password`; kein `--full-name`.
**Anpassungsvorschlag:** Argument aus dem Beispielbefehl entfernt.

**Aussage:** Systemcheck wird via `python -m arbeitszeit.infrastructure.system_check --db arbeitszeit.db` aufgerufen.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/infrastructure/system_check.py` besitzt keinen `__main__`-Block. Erreichbar nur über `admin_cli system check` (`src/arbeitszeit/presentation/admin_cli/system.py`).
**Anpassungsvorschlag:** Aufruf auf `admin --db <PFAD> --user-id <ID> system check` korrigiert (an beiden Fundstellen: Abschnitt 2.4 und Abschnitt 7).

**Aussage:** Terminal-UI-Aufruf mit nur `--db` und `--terminal-id`.
**Status:** inkorrekt (unvollständig)
**Beleg:** `src/arbeitszeit/presentation/terminal_ui/main.py`: `--numpad` und `--rfid` sind `required=True`.
**Anpassungsvorschlag:** Beispielaufruf um `--numpad`/`--rfid` ergänzt.

**Aussage:** `BookUseCase` prüft „Ruhezeit- und Rollenprüfung“.
**Status:** inkorrekt (Teilaussage)
**Beleg:** `src/arbeitszeit/application/use_cases/book_time.py`: Terminal-Buchungen führen explizit keine `UserRole`-Prüfung durch (bestätigt durch die unmittelbar folgende Designentscheidung im selben Dokument).
**Anpassungsvorschlag:** Auf „Ruhezeitprüfung; keine Rollenprüfung, siehe Designentscheidung unten“ präzisiert.

**Aussage:** Zeitmonitor prüft Systemzeitsprünge „alle 30 Sekunden“.
**Status:** nicht verifizierbar als festes Intervall
**Beleg:** `src/arbeitszeit/infrastructure/time_monitor.py` enthält keinen Scheduler; `terminal_ui/main.py` ruft `monitor.check()` einmal pro Buchungszyklus auf, nicht zeitgesteuert.
**Anpassungsvorschlag:** Auf „bei jedem Buchungszyklus (ereignisgetrieben, kein fester 30-Sekunden-Takt im Code nachweisbar)“ korrigiert.

**Aussage:** Gerätesimulator wird über `--simulator`-Flag aktiviert.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/presentation/terminal_ui/main.py` kennt kein `--simulator`-Argument; repositoryweite Suche ergab keinen Treffer. `SimulatedHardwareReader` wird nur in Testcode direkt instanziiert.
**Anpassungsvorschlag:** Abschnitt umformuliert; CLI-Beispiel mit nicht existierendem Flag entfernt.

**Aussage:** `bookings`-Domain kennt `list`, `correct`, `supplement register/approve/reject`.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/bookings.py`: tatsächliche Subcommands sind `correct`, `supplement`, `approve-supplement`, `reject-supplement`; kein `list`.
**Anpassungsvorschlag:** Tabelle auf die vier tatsächlichen Subcommands korrigiert; Hinweis auf `reports open-bookings`/`warn-cases`/`corrections`/`supplements` als Listing-Ersatz ergänzt.

**Aussage:** Es existiert ein Top-Level-Befehl `export csv`/`export pdf`.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/main.py` registriert keinen eigenen `export`-Domain-Parser; tatsächliche Befehle sind `reports export-csv`, `export-csv-review-cases`, `export-pdf-day/-week/-month/-employee` (`reports.py`).
**Anpassungsvorschlag:** Tabelle entsprechend ersetzt.

**Aussage:** Backup protokolliert `BACKUP_CREATED` in `system_events`.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/infrastructure/backup/backup_service.py`, `_log_audit()`: schreibt in `audit_log`, nicht `system_events`. `system_events`-CHECK-Constraint (`migrations/0006_system_events_application_error.sql`) kennt für Backups nur `DB_BACKUP_CREATED`/`DB_BACKUP_FAILED`.
**Anpassungsvorschlag:** Zieltabelle korrigiert, Hinweis auf abweichende `system_events`-Werte ergänzt.

**Aussage:** NAS-Sync wird über `--nas-path`-CLI-Flag konfiguriert.
**Status:** inkorrekt
**Beleg:** `scripts/backup.py` kennt nur `--db`, `--backup-dir`, `--export-dir`. NAS-Sync wird über `system_config`-Schlüssel `backup.nas_enabled`/`backup.nas_path` gesteuert.
**Anpassungsvorschlag:** Abschnitt 5.2 entsprechend korrigiert.

**Aussage:** Restore-Codebeispiel importiert Klasse `BackupService`.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/infrastructure/backup/backup_service.py` definiert `SQLiteBackupService`, keine Klasse `BackupService`.
**Anpassungsvorschlag:** Klassenname im Codebeispiel korrigiert.

**Aussage:** Restore protokolliert `RESTORE_COMPLETED` „in der wiederhergestellten Datenbank“ (implizit `system_events`).
**Status:** inkorrekt (Zieltabelle)
**Beleg:** `backup_service.py` schreibt `RESTORE_COMPLETED` via `_log_audit()` in `audit_log`; `system_events` kennt stattdessen `RESTORE_STARTED`/`RESTORE_FINISHED`/`RESTORE_FAILED`.
**Anpassungsvorschlag:** Zieltabelle präzisiert.

**Aussage:** Organisatorische Restore-Freigabe wird mit „RW v5 §18“ referenziert.
**Status:** inkorrekt (Paragraphenverweis)
**Beleg:** `regelwerk_arbeitszeit_v5.md` §18 behandelt Aufbewahrung/Löschung, nicht Restore-Freigabe; §20 regelt Backup/Restore.
**Anpassungsvorschlag:** Verweis auf §20 korrigiert.

**Aussage:** Aufbewahrungsfrist „5 Jahre gemäß ArbZG / RW v5 §20“.
**Status:** inkorrekt
**Beleg:** `regelwerk_arbeitszeit_v5.md` §18 nennt eine gesetzliche Mindestfrist von 2 Jahren; §20 behandelt Backup/Restore, keine Aufbewahrungsfristen. `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` stuft 5 Jahre als organisatorische Praxisfestlegung ohne technische Durchsetzung ein.
**Anpassungsvorschlag:** Auf gesetzliche 2-Jahres-Mindestfrist (§18) mit Hinweis auf die 5-Jahres-Praxisfestlegung als organisatorische Ergänzung umformuliert.

**Aussage (Systemcheck-Tabelle):** NAS-Erreichbarkeit liefert bei Fehler „WARNING“; fünf Prüfbereiche insgesamt; Ergebnisse als `SYSTEM_CHECK_*` protokolliert.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/infrastructure/system_check.py`: `CheckResult` hat nur binäres `ok`-Feld (kein WARNING-Zustand); es gibt sechs Prüfungen (NTP-Synchronisation fehlte in der Tabelle); Event-Typen sind `SELFTEST_OK`/`SELFTEST_FAIL`, nicht `SYSTEM_CHECK_*` (`migrations/0006_system_events_application_error.sql`).
**Anpassungsvorschlag:** Tabelle um NTP-Zeile ergänzt, NAS-Zeile auf FAIL korrigiert, Ereignisnamen korrigiert.

**Aussage:** „406 Tests grün“ (Freigabefähigkeitsstatus-Tabelle).
**Status:** inkorrekt (veraltet)
**Beleg:** `python3 -m pytest --collect-only -q` ergibt aktuell 480 Tests im Repository-Stand. Die Zahl 406 stammt aus einem früheren Entwicklungsstand (siehe CHANGELOG.md, ältere Archivdokumente).
**Anpassungsvorschlag:** Ursprungswert als historische Momentaufnahme mit Commit-Bezug (`0f20931`) gekennzeichnet und aktueller Stand (480 Tests) ergänzt, ohne den historischen Wert zu entfernen.

---

## Zusammenfassung der Korrekturen

1. `--full-name` aus Bootstrap-Beispiel entfernt.
2. Systemcheck-Aufrufe (Abschnitt 2.4 und 7) auf `admin --db <PFAD> --user-id <ID> system check` korrigiert.
3. Terminal-UI-Beispielaufruf um Pflichtparameter `--numpad`/`--rfid` ergänzt.
4. „Rollenprüfung“ in Ablaufbeschreibung als nicht zutreffend präzisiert.
5. Zeitmonitor-Intervall „alle 30 Sekunden“ auf ereignisgetriebenes Verhalten korrigiert.
6. Nicht existierendes `--simulator`-Flag aus Gerätesimulator-Abschnitt entfernt.
7. `bookings`-Tabelle auf tatsächliche Subcommands (`correct`, `supplement`, `approve-supplement`, `reject-supplement`) korrigiert.
8. `export csv`/`export pdf` durch tatsächliche `reports export-*`-Subcommands ersetzt.
9. Backup-/Restore-Protokollierungsziel von `system_events` auf `audit_log` korrigiert.
10. `--nas-path`-CLI-Flag durch `system_config`-Schlüssel-Steuerung ersetzt.
11. Klassenname `BackupService` auf `SQLiteBackupService` korrigiert.
12. Paragraphenverweis der Restore-Freigabe von §18 auf §20 korrigiert.
13. Aufbewahrungsfrist von „5 Jahre gemäß ArbZG/§20“ auf gesetzliche 2-Jahres-Mindestfrist (§18) mit Praxisfestlegungs-Hinweis korrigiert.
14. Systemcheck-Tabelle: NTP-Prüfung ergänzt, NAS-Verhalten auf FAIL korrigiert, Ereignisnamen `SELFTEST_OK`/`SELFTEST_FAIL` statt `SYSTEM_CHECK_*`.
15. Testkennzahl „406 Tests“ mit Commit-Bezug versehen und aktueller Stand (480 Tests) ergänzt.

## Offene Punkte

- Python-Versionsangabe „3.11–3.12“ (Abschnitt 1) konnte nicht abschließend gegen `pyproject.toml` verifiziert werden; ein möglicher Widerspruch zum CHANGELOG-Eintrag „Python-Zielversion auf 3.14 angehoben“ besteht, wurde aber mangels eindeutigem Beleg nicht geändert.
- `journalctl -u arbeitszeit-terminal`-Hinweis (Abschnitt 7.2) ist mangels vorhandener systemd-Unit-Datei im Repository nicht verifizierbar; unverändert belassen, da nicht widerlegt.
- Aussage zu Rollenanforderung bei `bookings approve-supplement`/`reject-supplement` (REVIEWER/ADMIN) konnte nicht direkt im CLI-Modul verifiziert werden (Rollenprüfung vermutlich in den zugehörigen Use Cases); unverändert belassen, da nicht widerlegt.
