# Prüfbericht: Kapitel „Infrastrukturschicht" (`docs/module/handbuch_infrastructure.md`)

**Geprüfte Quelle:** `docs/module/handbuch_infrastructure.md`
**Repository:** `iCodator/arbeitszeit`
**Prüfmodus:** Freitext-Report (keine Änderungen am Original-Handbuchtext)

## Gesamteinschätzung

Das Kapitel „Infrastrukturschicht" beschreibt die Datenbank-, Hardware-, Export-,
Backup- und Systemüberwachungskomponenten überwiegend zutreffend; die Mehrzahl der
technischen Detailaussagen zu PRAGMAs, Transaktionssemantik, Hardwarezugriff,
Backup-/NAS-Logik und Benachrichtigungsverhalten ist durch den Quellcode belegt.
Mehrere Einzelaussagen sind jedoch veraltet oder unvollständig: Die Berufung auf ein
architektonisches SQL-Zugriffsverbot außerhalb der Infrastrukturschicht widerspricht
der aktuellen ADR-Lage, die Systemcheck-Tabelle nennt eine Prüfung zu wenig, ein
zitierter Helfername existiert so nicht im Code, und zwei Komponentenbeschreibungen
(CSV-Export, `work_schedule`-Repository) sind unvollständig. Ein Einzelpunkt zu
In-Memory-Datenbanken konnte nicht verifiziert werden.

## Detailbefunde

- Aussage: „Direct-SQL-Abfragen außerhalb von `infrastructure` sind architektonisch
  verboten (Regelwerk §11)."
- Status: inkorrekt
- Beleg: `docs/adr/adr-cqrs-lesezugriff.md` (ADR-002, Status „Akzeptiert", 2026-06-30);
  `regelwerk_arbeitszeit_v5.md` §11
- Bewertung: ADR-002 erlaubt Direct-SQL-Lesezugriffe (und in dokumentierten Fällen auch
  Schreibzugriffe) außerhalb von `infrastructure`, konkret in
  `presentation/admin_cli/employees.py` und `presentation/admin_cli/schedule.py`. Der
  Klammerverweis „§11" trifft zudem nicht mehr zu: §11 des aktuell gültigen Regelwerks
  v5.0 behandelt „Prüfstatus", nicht SQL-Zugriffsregeln. Die Aussage widerspricht damit
  sowohl der referenzierten Architekturentscheidung als auch der zitierten Quelle
  selbst.
- Anpassungsvorschlag: Den Satz an die in ADR-002 dokumentierte Ausnahmeregelung
  anpassen und die Regelwerk-Referenz entfernen oder auf die zutreffende Fundstelle
  korrigieren, sofern eine solche im Regelwerk identifizierbar ist.

- Aussage: Die Systemcheck-Tabelle (Abschnitt zu `system_check.py`) führt fünf
  Prüfbereiche auf.
- Status: inkorrekt
- Beleg: `src/arbeitszeit/infrastructure/system_check.py` (Aufruf `_check_ntp()`);
  `tests/integration/test_system_check.py` (`assert "ntp_sync" in names`)
- Bewertung: Der Code führt sechs Prüfungen aus; die Tabelle im Handbuch nennt nur
  fünf und lässt die NTP-Synchronisationsprüfung (`ntp_sync`) aus. Der Integrationstest
  bestätigt explizit das Vorhandensein dieses Prüfbereichs.
- Anpassungsvorschlag: Zeile für die NTP-Synchronisationsprüfung (`ntp_sync`) in der
  Tabelle ergänzen, unter Beibehaltung des bestehenden Tabellenformats.

- Aussage: „Alle Repositories nutzen zur Zeilenkonvertierung die Hilfsfunktion
  `_row_to_entity`."
- Status: inkorrekt
- Beleg: `src/arbeitszeit/infrastructure/db/repositories/*.py`
- Bewertung: Eine Funktion namens `_row_to_entity` existiert im Code nicht. Jedes
  Repository verwendet eine eigene, spezifisch benannte Konvertierungsfunktion, z. B.
  `_row_to_booking`, `_row_to_employee`, `_row_to_card`, `_row_to_user_account`,
  `_row_to_version`, `_row_to_case`, `_row_to_correction`, `_row_to_supplement`.
- Anpassungsvorschlag: Den generischen Funktionsnamen durch eine Formulierung
  ersetzen, die auf das wiederkehrende Namensmuster verweist, ohne einen konkreten,
  nicht existierenden Funktionsnamen zu benennen (z. B. Hinweis auf repository-eigene
  `_row_to_*`-Funktionen).

- Aussage: „Alle Zeitstempel werden über `_helpers._parse_dt()` UTC-normalisiert."
- Status: inkorrekt
- Beleg: `src/arbeitszeit/infrastructure/db/repositories/audit_log.py`,
  `system_config.py`, `device_event.py`
- Bewertung: Die drei genannten Repositories importieren `_helpers` nicht und
  besitzen keine Lese- bzw. Konvertierungsmethoden, die `_parse_dt()` verwenden. Die
  Verallgemeinerung „alle Repositories" trifft daher nicht für den gesamten
  Repository-Bestand zu.
- Anpassungsvorschlag: Die Aussage auf die tatsächlich betroffenen Repositories
  einschränken oder als „die meisten zeitstempelverarbeitenden Repositories"
  präzisieren.

- Aussage: Der CSV-Export bietet zwei Exportfunktionen.
- Status: inkorrekt
- Beleg: `src/arbeitszeit/infrastructure/export/csv_exporter.py`
  (`export_detail`, `export_condensed`, `export_review_cases`)
- Bewertung: Der Code enthält drei Exportfunktionen, nicht zwei. Die Funktion
  `export_review_cases` fehlt in der Handbuchbeschreibung vollständig.
- Anpassungsvorschlag: Dritte Exportfunktion (`export_review_cases`) in der
  Aufzählung bzw. Tabelle ergänzen.

- Aussage: Die Kernmethoden-Tabelle von `SQLiteWorkScheduleRepository` ist
  vollständig.
- Status: inkorrekt
- Beleg: `src/arbeitszeit/infrastructure/db/repositories/work_schedule.py`
  (Methode `list_versions()`)
- Bewertung: Die Tabelle im Handbuch führt die Methode `list_versions()` nicht auf,
  obwohl sie im Repository implementiert ist.
- Anpassungsvorschlag: Zeile für `list_versions()` in der Kernmethoden-Tabelle
  ergänzen, unter Beibehaltung des bestehenden Tabellenformats.

- Aussage: „Repositories arbeiten auf jeder `sqlite3.Connection`, auch auf
  In-Memory-Datenbanken (`:memory:`)."
- Status: nicht verifizierbar
- Beleg: keine direkte Fundstelle in Code oder Testsuite
- Bewertung: Im Repository konnte keine Verwendung von `:memory:`-Datenbanken
  gefunden werden; die Testsuite nutzt durchgängig dateibasierte Datenbanken über
  `tmp_path`. Die Aussage ist technisch plausibel, da keine repository-spezifische
  Bindung an Dateipfade im Code erkennbar ist, lässt sich aber anhand der
  vorhandenen Repository-Evidenz nicht bestätigen.
- Anpassungsvorschlag: Aussage als nicht durch Tests abgedeckt kennzeichnen oder
  vorsichtiger formulieren, sofern keine weitere Evidenz beigebracht werden kann.

- Aussage: PRAGMA-Einstellungen (`isolation_level=None`, `journal_mode=WAL`,
  `foreign_keys=ON`, `busy_timeout=5000`) werden beim Verbindungsaufbau gesetzt.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/db/connection.py`
- Bewertung: Alle vier PRAGMA-Werte und deren Begründungen stimmen mit der
  Implementierung in `open_connection()` überein.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: Migrationslogik validiert Schemaversionen und ist gegen SQL-Injection
  abgesichert.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/db/migrations.py`
- Bewertung: Versionsprüfung und parametrisierte Ausführung entsprechen der
  Beschreibung im Handbuch.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: Der Unit-of-Work-Controller stellt Rollback- und Commit-Semantik sowie
  einen `audit_conn`-Fallback bereit; er verwaltet elf Repository-Attribute.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/db/unit_of_work.py`
- Bewertung: Anzahl und Verhalten der Repository-Attribute sowie
  Rollback-/Commit-/Fallback-Logik stimmen mit dem Code überein.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: Der Hardware-RFID-Reader (`evdev_reader.py`) implementiert
  Timeout-Verhalten, exklusiven Gerätezugriff (`grab=True`), Hex-UID-Verarbeitung
  und Zeitstempelerfassung (`occurred_at`).
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`;
  `docs/infrastructure/evdev_reader.md`
- Bewertung: Alle genannten Verhaltensweisen sind im Code sowie in der
  begleitenden Moduldokumentation bestätigt.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: Der Simulator (`simulator.py`) bildet Hardwareereignisse über eine
  Warteschlange (deque) nach und wirft bei fehlenden Ereignissen einen
  `RuntimeError`.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/hardware/simulator.py`
- Bewertung: Deque-basierte Pending-Verwaltung und Fehlerverhalten entsprechen
  der Implementierung.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: `report_queries.py` verwendet für Zeiträume ein halboffenes Intervall
  `[from_dt, to_dt)`.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/export/report_queries.py`
- Bewertung: Die Intervallgrenzen in den SQL-Abfragen entsprechen der im Handbuch
  beschriebenen Halboffenheit.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: `backup_service.py` implementiert lokale Sicherung, NAS-Synchronisation
  und Wiederherstellung und protokolliert die Ereignistypen `BACKUP_CREATED`,
  `BACKUP_SYNC_FAILED`, `BACKUP_SYNCED_TO_NAS` und `RESTORE_COMPLETED`.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/backup/backup_service.py`
- Bewertung: Methoden (`create_local_backup`, `sync_to_nas`, `restore_from`) und
  Audit-Ereignistypen stimmen mit dem Code überein.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: Die NAS-Erreichbarkeitsprüfung erfolgt ausschließlich über
  `Path.exists()`/`os.access()`, ohne Ping-Mechanismus.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/backup/backup_service.py`
- Bewertung: Der Code verwendet keine Netzwerk-Ping-Prüfung, sondern
  ausschließlich dateisystembasierte Prüfungen, wie im Handbuch beschrieben.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: `time_monitor.py` erkennt Zeitsprünge anhand eines konfigurierbaren
  Schwellenwerts und erzeugt entsprechende Ereignistypen.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/time_monitor.py`
- Bewertung: Schwellenwertlogik und Konfigurationsschlüssel entsprechen der
  Beschreibung im Handbuch.
- Anpassungsvorschlag: keiner erforderlich.

- Aussage: `notification.py` verhält sich fail-safe und benötigt das Paket
  `libnotify-bin`.
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/notification.py`
- Bewertung: Die Fail-Safe-Logik bei fehlendem `notify-send` sowie die genannte
  Paketabhängigkeit sind im Code nachvollziehbar.
- Anpassungsvorschlag: keiner erforderlich.

## Offene Punkte

- Der Punkt zu In-Memory-Datenbanken (`:memory:`) bleibt mangels Testabdeckung
  ungeklärt und sollte manuell geprüft oder im Handbuch vorsichtiger formuliert
  werden.
- Der Hinweis zur Regelwerk-Referenz („§11") sollte nur nach Klärung der korrekten
  Fundstelle im aktuellen Regelwerk aktualisiert werden; ohne diese Klärung ist nur
  die Streichung des veralteten Verweises belegbar.
