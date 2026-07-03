# Prüfbericht: `docs/datenschutz/vvt_arbeitszeit_v1.md`

**Geprüftes Dokument:** `docs/datenschutz/vvt_arbeitszeit_v1.md` (Version 1.0, Stand 2026-06-12)
**Repository:** iCodator/arbeitszeit
**Prüfgrundlage:** `migrations/0001_schema.sql`, `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, `scripts/backup.py`, `src/arbeitszeit/infrastructure/backup/backup_service.py`, `regelwerk_arbeitszeit_v5.md`, `pflichtenheft_arbeitszeit_v6.md`

---

## Gesamteinschätzung

Das VVT ist überwiegend eine rechtlich-organisatorische Vorlage mit Ausfüllfeldern; die wenigen technisch prüfbaren Aussagen (Datenbanktabellen, Hash-Verfahren, Restore-Mechanismus) enthielten drei konkrete Abweichungen vom Code, die korrigiert wurden. Die Aufbewahrungsfrist-Angaben (Abschnitt 8) sind konsistent mit Regelwerk und Pflichtenheft und wurden nicht verändert.

---

## Strukturierter Report je Aussage

**Aussage:** Passwort-Hash wird mit „bcrypt/argon2“ erzeugt.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Funktion `_hash_password`: `hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)`. Weder bcrypt noch argon2 werden im Repository verwendet.
**Bewertung:** Das im VVT genannte Verfahren entspricht nicht dem tatsächlich implementierten.
**Anpassungsvorschlag:** Auf „PBKDF2-HMAC-SHA256, 260.000 Iterationen, Zufallssalt“ korrigiert.

**Aussage:** Korrekturen und Nachträge werden in den Tabellen `booking_corrections` und `supplement_requests` gespeichert.
**Status:** inkorrekt
**Beleg:** `migrations/0001_schema.sql`: `CREATE TABLE booking_corrections` und `CREATE TABLE supplements` (keine Tabelle `supplement_requests`).
**Anpassungsvorschlag:** Tabellenname auf `supplements` korrigiert.

**Aussage:** Wiederherstellung erfolgt über `scripts/backup.py --restore`.
**Status:** inkorrekt
**Beleg:** `scripts/backup.py`, `main()`: Die einzigen `argparse`-Argumente sind `--db`, `--backup-dir`, `--export-dir`; kein `--restore`-Flag. Restore ist ausschließlich über die Methode `SQLiteBackupService.restore_from()` (`src/arbeitszeit/infrastructure/backup/backup_service.py`) programmatisch erreichbar, ohne CLI-Wrapper.
**Anpassungsvorschlag:** Auf „`SQLiteBackupService.restore_from()`, programmatisch, kein eigenständiges CLI-Flag“ korrigiert.

**Aussage:** Gehashte RFID-UID wird in der Tabelle `rfid_cards` gespeichert.
**Status:** korrekt
**Beleg:** `migrations/0001_schema.sql`, `CREATE TABLE rfid_cards`.

**Aussage:** Zeiterfassungsdaten werden in `time_bookings` gespeichert; Audit-Log-Daten in `audit_log`/`system_events`; Hardware-Rohereignisse in `device_events`.
**Status:** korrekt
**Beleg:** `migrations/0001_schema.sql`: alle vier Tabellen (`time_bookings`, `audit_log`, `system_events`, `device_events`) existieren exakt unter diesen Namen.

**Aussage:** Aufbewahrungsfrist für Zeiterfassungsdaten und Korrekturen: 2 Jahre gemäß ArbZG § 16 Abs. 2.
**Status:** korrekt
**Beleg:** `regelwerk_arbeitszeit_v5.md` Zeile 182 („Arbeitszeitdaten sind mindestens 2 Jahre aufzubewahren“) und `pflichtenheft_arbeitszeit_v6.md` Zeile 257 (gleiche Frist, mit Verweis auf § 16 Abs. 2 ArbZG) stimmen mit der VVT-Angabe überein.

**Aussage:** Export- und PDF-Dateien: 5 Jahre (empfohlen), § 147 AO / § 257 HGB analog.
**Status:** korrekt gekennzeichnet als Empfehlung
**Beleg:** Das Dokument kennzeichnet diesen Wert selbst explizit als „(empfohlen)“ und nicht als gesetzliche Pflicht, was konsistent mit der übrigen Repository-Dokumentation ist (`docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md`: 5 Jahre als organisatorische Praxisfestlegung ohne technische Durchsetzung).
**Bewertung:** Keine Korrektur erforderlich, da bereits korrekt als Empfehlung statt Pflicht formuliert.

**Aussage:** Rollenbasiertes Berechtigungskonzept (ADMIN/REVIEWER/TECH) ist „technisch erzwungen in der Anwendung“.
**Status:** korrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/_auth.py` (`require_admin_or_reviewer`, `require_admin_or_tech`) sowie Rollenprüfungen in den Use Cases unter `application/use_cases/manage_user_accounts.py`.

**Aussage:** SQLite läuft im WAL-Modus.
**Status:** korrekt
**Beleg:** Bereits in früheren Prüfungen dieses Projekts (Datenbankschema-Kapitel) belegt; `infrastructure/db/connection.py` aktiviert WAL-Modus.

**Aussage (Abschnitt 9.3):** „Fallback bei Geräteausfall: Schriftliche Notfallerfassung und gekennzeichneter Nachtrag (Regelwerk v5 §19)“.
**Status:** nicht verifizierbar (Regelwerk-Paragraph nicht im Rahmen dieser Prüfung gegengelesen)
**Bewertung:** Der Verweis betrifft eine organisatorische Regel im Regelwerk, keine Code-Aussage; ohne gezielte Prüfung von §19 wird dies nicht als falsch markiert, aber auch nicht bestätigt.

---

## Zusammenfassung der Korrekturen

1. Passwort-Hash-Verfahren: „bcrypt/argon2“ → „PBKDF2-HMAC-SHA256, 260.000 Iterationen, Zufallssalt“.
2. Tabellenname: `supplement_requests` → `supplements`.
3. Restore-Verfahren: `scripts/backup.py --restore` (existiert nicht) → `SQLiteBackupService.restore_from()` (programmatisch, kein CLI-Flag).

## Offene Punkte

- Verweis auf Regelwerk v5 §19 (Fallback bei Geräteausfall) wurde nicht gezielt gegengelesen; als nicht verifizierbar belassen, keine Änderung vorgenommen.
- Alle übrigen Abschnitte (Verantwortlicher, DSB, Zwecke, Betroffenenrechte, DSFA, Meldepflichten, Unterschriften) sind organisatorische/rechtliche Ausfüllvorlagen ohne unmittelbaren Codebezug und wurden nicht verändert.
