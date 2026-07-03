# Prüfbericht: `docs/betrieb/restore_checkliste.md`

**Geprüftes Dokument:** `docs/betrieb/restore_checkliste.md` (Version 1.0, Stand 2026-06-13)
**Geprüft gegen:** `src/arbeitszeit/infrastructure/backup/backup_service.py`, `src/arbeitszeit/presentation/admin_cli/system.py`, `src/arbeitszeit/presentation/admin_cli/main.py`, `src/arbeitszeit/domain/audit_events.py`, `tests/e2e/test_backup.py`

## Gesamteinschätzung

Die Restore-Checkliste ist überwiegend als organisatorisches Formular gestaltet (Freigabe, Ja/Nein-Prüffragen, Unterschriftenfelder) und enthält nur wenige technisch prüfbare Aussagen. Die geprüften technischen Bezüge — Existenz einer Restore-Funktionalität, Audit-Dokumentation des Restore-Ereignisses und Erwähnung der Admin-CLI — sind im Kern korrekt, jedoch mit einer wesentlichen Einschränkung: Das Dokument suggeriert implizit die Nutzung der Admin-CLI für den Restore-Vorgang selbst („Admin-CLI startet fehlerfrei“ als Nachprüfung), obwohl im admin_cli kein eigenständiger `restore`-Befehl existiert. Der Restore ist ausschließlich über die Methode `restore_from` der Klasse `SQLiteBackupService` im Code implementiert, nicht über ein CLI-Kommando.

---

## Kapitel 1: Zweck

**Aussage:** „Die Checkliste soll sicherstellen, dass ein Restore nur geplant, dokumentiert und nachvollziehbar durchgeführt wird.“
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Zweckbeschreibung eines Verfahrens, kein technischer Sachverhalt.

---

## Kapitel 2: Voraussetzungen vor dem Restore

**Aussage:** Sämtliche Prüffragen (Restore-Anlass, Freigabe, Backup-Identifikation, Rollen `ADMIN`/`TECH`).
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Formularfelder für organisatorische Freigabe- und Kontrollprozesse; kein Code-Bezug prüfbar. Die Rollen `ADMIN`/`TECH` werden zwar im Code für Berechtigungsprüfungen verwendet (siehe Kapitel 4 unten), die Checkliste selbst macht hier aber keine technische Aussage über deren Implementierung, sondern fragt nur ab, ob Zuständigkeiten *geklärt* sind.

---

## Kapitel 3: Restore-Freigabe

**Aussage:** Formularfelder zu Anlass, Freigabe, Zeitpunkt, durchführender Person, verwendetem Backup.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Reines Dokumentationsformular ohne technischen Prüfgehalt.

---

## Kapitel 4: Technische Durchführung

### 4.1 Vorbereitung

**Aussage:** „Anwendung / Terminalbetrieb gestoppt“, „Admin-CLI / sonstige Zugriffe beendet“, „Aktuelle Datenbankkopie vor Restore erstellt“.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Ablaufschritte als Checklisten-Items, keine verifizierbare technische Behauptung über Code-Verhalten.

**Implizite technische Voraussetzung — Vorbedingung „keine offenen Verbindungen zur Ziel-DB“:**
**Aussage (sinngemäß hinterlegte technische Notwendigkeit von „Admin-CLI/Zugriffe beendet“ vor Restore):** Der Restore aus einem Backup setzt voraus, dass keine anderen Verbindungen zur Ziel-Datenbank offen sind.
**Status:** korrekt
**Beleg:** `src/arbeitszeit/infrastructure/backup/backup_service.py` Zeilen 98-101, Docstring von `restore_from`: „Vorbedingung: Keine offenen Verbindungen zur Ziel-DB beim Aufruf.“
**Bewertung:** Der Checklistenpunkt „Admin-CLI / sonstige Zugriffe beendet“ deckt sich mit einer im Code explizit dokumentierten Vorbedingung der `restore_from`-Methode.

### 4.2 Wiederherstellung

**Aussage:** „Restore aus identifiziertem Backup durchgeführt.“
**Status:** korrekt
**Beleg:** `backup_service.py` Zeilen 98-145, Methode `restore_from(self, backup_path: Path, *, restore_exports: bool = False) -> None`. Die Methode stellt die Datenbank aus einer Backup-Datei per SQLite-Backup-API wieder her (`src.backup(dst)`, Zeile 116) und führt anschließend `PRAGMA integrity_check` aus (Zeile 117).
**Bewertung:** Eine Restore-Funktionalität mit dem beschriebenen Verhalten existiert im Code und ist durch Tests belegt (`tests/e2e/test_backup.py`, `test_restore_stellt_daten_wieder_her`, Zeilen 115-131; `test_backup_und_restore_roundtrip_mehrere_datensaetze`, Zeilen 134-148).

**Aussage:** „Falls vorgesehen: Exportdateien mit wiederhergestellt.“
**Status:** korrekt
**Beleg:** `backup_service.py` Zeilen 104-108, 127-134: Parameter `restore_exports: bool = False`; bei `True` werden Exportdateien aus `<backup_dir>/exports/` per `shutil.copytree` in `self._export_dir` zurückkopiert. Testbeleg: `tests/e2e/test_backup.py` Zeilen 311-326 (`test_restore_with_exports_kopiert_exportdateien_zurueck`) und Zeilen 329-341 (`test_restore_ohne_flag_stellt_keine_exporte_wieder_her`), die explizit das Verhalten mit und ohne Flag verifizieren.
**Bewertung:** Vollständig durch Code und Tests belegt.

**Aussage:** „Schreib-/Leserechte der wiederhergestellten Dateien geprüft.“
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Manuelle Prüfhandlung nach dem Restore, im Code nicht als automatisierte Funktion vorhanden; keine technische Aussage über Code-Verhalten, sondern eine durchzuführende Kontrolle.

**Aussage:** „Anwendung wieder gestartet.“
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Betrieblicher Ablaufschritt.

---

## Kapitel 5: Funktionsprüfung nach Restore

**Aussage:** „Datenbank lässt sich öffnen.“
**Status:** korrekt (als technisch sinnvolle Prüfung im Sinne der Integritätsprüfung des Codes)
**Beleg:** `backup_service.py` Zeile 117: `result = dst.execute("PRAGMA integrity_check").fetchone()[0]`; bei fehlgeschlagener Prüfung wird ein `RuntimeError` ausgelöst (Zeilen 118-121).
**Bewertung:** Der Code selbst führt bereits während `restore_from` eine Integritätsprüfung der wiederhergestellten Datenbank durch; das manuelle Nachprüfen „Datenbank lässt sich öffnen“ ist als zusätzliche Kontrolle plausibel im Sinne des Codes, jedoch primär eine organisatorische Nachkontrolle, kein separater Test einer Codefunktion. Als technische Randbedingung wird bestätigt, dass eine automatisierte Integritätsprüfung existiert.

**Aussage:** „Admin-CLI startet fehlerfrei.“
**Status:** nicht verifizierbar / irreführend im Kontext des Restore
**Beleg:** `src/arbeitszeit/presentation/admin_cli/main.py` Zeilen 95-102 (Subcommand-Registrierung); `src/arbeitszeit/presentation/admin_cli/system.py` Zeilen 95-101 (`register_subcommands`, registriert nur `check` und `backup` unter `system`). Es existiert kein `restore`-Subbefehl in `main.py` oder `system.py`, weder als eigenständige Domäne noch als `system`-Unterbefehl.
**Bewertung:** Die Admin-CLI ist als generelles Verwaltungswerkzeug funktionsfähig und ihr Start nach einem Restore ist grundsätzlich eine sinnvolle Prüfung, um die DB-Integrität aus Anwendungssicht zu bestätigen. Der Prüfpunkt selbst ist als allgemeine Funktionsprüfung nicht falsch. Da die Restore-Checkliste jedoch keinen konkreten CLI-Befehl für den Restore-Vorgang benennt und der Prüfauftrag ausdrücklich verlangt, ob im Dokument beschriebene CLI-Befehle für Backup/Restore tatsächlich existieren, ist hier hervorzuheben: Es gibt **keinen** `admin restore`- oder `admin system restore`-Befehl im Repository. Der Restore ist ausschließlich als Methode `restore_from` der Klasse `SQLiteBackupService` implementiert und muss derzeit programmatisch (z. B. über ein eigenes Skript oder eine Python-Konsole) aufgerufen werden, nicht über die Admin-CLI.
**Anpassungsvorschlag:** Ergänzung eines expliziten technischen Hinweises in Kapitel 4.2, dass für den Restore-Vorgang selbst kein CLI-Befehl (`admin ...`) zur Verfügung steht, sondern die Methode `SQLiteBackupService.restore_from()` (`src/arbeitszeit/infrastructure/backup/backup_service.py`) direkt angesprochen werden muss. Andernfalls sollte klargestellt werden, wie der Restore in der Praxis technisch ausgelöst wird, um Verwechslungen mit dem vorhandenen `admin system backup`-Befehl zu vermeiden.

**Aussage:** „Stichprobenhafte Buchungen / Mitarbeiterdaten vorhanden.“
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Manuelle Stichprobenkontrolle, keine automatisiert prüfbare Codeaussage.

**Aussage:** „Systemcheck erfolgreich oder plausibel.“
**Status:** korrekt (Systemcheck-Funktionalität existiert)
**Beleg:** `src/arbeitszeit/infrastructure/system_check.py` Zeilen 46-64, Funktion `run_system_check`; CLI-Zugriff über `admin system check` (`src/arbeitszeit/presentation/admin_cli/system.py` Zeilen 14-28, `cmd_system_check`, sowie Subparser-Registrierung Zeile 100: `ssub.add_parser("check", ...)`).
**Bewertung:** Ein Systemcheck-Befehl existiert tatsächlich in der Admin-CLI unter `admin system check` und deckt u. a. DB-Zugriff, Konfigurationsschlüssel, NAS-Erreichbarkeit und Fremdschlüssel-Konsistenz ab. Der Prüfpunkt „Systemcheck erfolgreich“ ist technisch durch einen real existierenden Befehl umsetzbar.

**Aussage:** „Backup-/Exportpfade weiterhin korrekt.“
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Manuelle Prüfung der Konfiguration nach dem Restore; keine automatisierte Codefunktion, die explizit geprüft werden könnte, auch wenn `system_check.py` verwandte Konfigurationsschlüssel prüft (`_check_config_keys`, Zeilen 116-131).

**Aussage:** „Restore-Ereignis dokumentiert.“
**Status:** korrekt
**Beleg:** `backup_service.py` Zeilen 136-145: Nach erfolgreichem Restore wird ein Audit-Eintrag mit `audit_events.RESTORE_COMPLETED` erzeugt (`self._log_audit(audit_events.RESTORE_COMPLETED, {"backup_path": ..., "backup_mtime": ...})`); Ereignistyp definiert in `src/arbeitszeit/domain/audit_events.py` Zeile 38: `RESTORE_COMPLETED = "RESTORE_COMPLETED"`. Testbeleg: `tests/e2e/test_backup.py` Zeilen 214-222 (`test_restore_erstellt_audit_eintrag`).
**Bewertung:** Die automatische Dokumentation des Restore-Ereignisses im Audit-Log ist durch Code und Tests eindeutig belegt. Bemerkenswert (nicht im Dokument erwähnt, aber relevant): Laut Code-Kommentar (Zeilen 136-138) landet dieser Audit-Eintrag in der *wiederhergestellten* Datenbank selbst, da er ein nachgelagertes Ereignis im neuen Ist-Zustand ist, nicht Teil des gesicherten Standes.

---

## Kapitel 6: Bewertung des Restore-Ergebnisses

**Aussage:** Formularfelder „Restore erfolgreich?“, „Einschränkungen/offene Punkte“, „Weitere Maßnahmen erforderlich?“.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Bewertungsformular ohne technischen Prüfgehalt.

---

## Kapitel 7: Nachdokumentation

**Aussage:** Verweis auf zu prüfende/ergänzende Dokumente (`betriebsdokumentation_arbeitszeit_v1_1.md`, `betriebsfreigabe_protokoll.md`, `backup_zeitplan_und_automatisierung.md`).
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Verweis auf andere Betriebsdokumente; die Existenz dieser Dateien wurde im Rahmen dieser Prüfung im Verzeichnis `docs/betrieb/` bestätigt, ist aber eine Dokumentenverwaltungsfrage, keine technische Codeaussage.

---

## Kapitel 8: Abschluss und Unterschriften

**Aussage:** Unterschriftenfelder für Durchführende Person, Verantwortliche Stelle, technische Prüfung.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Formularfelder ohne technischen Prüfgehalt.

---

## Kapitel 9: Änderungshistorie

**Aussage:** Versionstabelle mit Datum und Änderungsvermerk.
**Status:** nicht zutreffend (organisatorisch)
**Beleg:** –
**Bewertung:** Dokumentenverwaltung, kein Code-Bezug.

---

## Zusätzlicher Befund: Fehlerpfade des Restore (nicht explizit im Dokument behandelt)

**Beobachtung:** Die Checkliste behandelt nicht explizit, wie mit einem fehlschlagenden Restore umzugehen ist (z. B. beschädigte Backup-Datei, fehlende Backup-Datei).
**Status:** nicht verifizierbar (Auslassung, keine Falschaussage)
**Beleg:** `backup_service.py` Zeilen 110-111 (`FileNotFoundError` bei fehlender Backup-Datei), Zeilen 117-121 (`RuntimeError` bei fehlgeschlagener Integritätsprüfung); Testbeleg: `tests/e2e/test_backup.py` Zeilen 180-198 (`test_restore_aus_nicht_existierender_datei_wirft_file_not_found`, `test_restore_aus_beschaedigter_datei_schlaegt_fehl`, letzterer erwartet `sqlite3.DatabaseError`).
**Bewertung:** Der Code definiert klare Fehlerpfade für einen missglückten Restore (fehlende Datei, beschädigte Datei, gescheiterte Integritätsprüfung), die in der Checkliste nicht als eigene Prüfpunkte auftauchen. Dies ist keine Falschaussage im Dokument, aber eine sinnvoll schließbare Lücke.
**Anpassungsvorschlag:** Ergänzung eines Punktes in Kapitel 5 („Funktionsprüfung nach Restore“) oder 6, der explizit nach dem Auftreten von Fehlermeldungen wie „Backup-Datei nicht gefunden“ oder einer fehlgeschlagenen Integritätsprüfung („Integritätsprüfung der wiederhergestellten DB fehlgeschlagen“) fragt, da diese Fehlertexte exakt so im Code auftreten (`backup_service.py` Zeile 111 bzw. Zeilen 119-121).
