# Prüfbericht: docs/betrieb/datenschutz_und_tom_arbeitszeit_v1_0.md

## Gesamteinschätzung

Das Dokument ist überwiegend ein auszufüllendes organisatorisches TOM-Formular (Verantwortlichkeiten, Schulung, AV-Verträge, Unterschriften) ohne prüfbaren Tatsachengehalt. Die wenigen technisch konkreten Aussagen (Passwort-Hashing-Verfahren, Rollenmodell, NAS-Sync-Funktion, referenzierte Dokumente) sind vollständig durch den Code belegt. Es wurde keine inkorrekte Aussage gefunden; eine bereits aus einem früheren Prüfbericht bekannte Auslassung (Rolle `EMPLOYEE`) wird als Anmerkung aufgeführt, ohne dass eine Korrektur am Dokument erforderlich ist, da das Dokument keinen Vollständigkeitsanspruch formuliert.

## Befunde

- Aussage: „Die Anwendung verwendet PBKDF2-HMAC-SHA256 mit zufälligem Salt und erhöhter Iterationszahl (siehe Quellcode `presentation/admin_cli/user_accounts.py`).“
- Status: korrekt
- Beleg: `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Zeilen 40–45: `hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)` mit `salt = os.urandom(16)`.
- Bewertung: Verfahren, Zufallssalt und erhöhte Iterationszahl (260.000) sind exakt so implementiert.

---

- Aussage: „Rollenmodelle in der Anwendung: ADMIN, REVIEWER, TECH“ (Abschnitt 5.1)
- Status: korrekt (mit Anmerkung)
- Beleg: `src/arbeitszeit/domain/enums.py`, Zeilen 54–58: `class UserRole(StrEnum): EMPLOYEE = "EMPLOYEE"; ADMIN = "ADMIN"; REVIEWER = "REVIEWER"; TECH = "TECH"`.
- Bewertung: Das Dokument benennt die drei für administrative Benutzerkonten tatsächlich vergebbaren Rollen korrekt (`_ALLOWED_ROLES = {ADMIN, REVIEWER, TECH}` in `manage_user_accounts.py`, Zeile 21) und erhebt keinen expliziten Vollständigkeitsanspruch ("die Rollenmodelle sind..." statt "es gelten ausschließlich..."). Der Code kennt zusätzlich `UserRole.EMPLOYEE`, das jedoch für Benutzerkonten nicht zuweisbar ist. Diese Abweichung wurde bereits im Prüfbericht zu `docs/betrieb/rollenzuweisung.md` dokumentiert.
- Anpassungsvorschlag: keiner, da keine falsche oder als vollständig ausgegebene Behauptung vorliegt.

---

- Aussage: „Optionale NAS-Spiegelung, soweit betrieblich vorgesehen.“
- Status: korrekt
- Beleg: `src/arbeitszeit/infrastructure/backup/backup_service.py`, Zeile 70: `def sync_to_nas(self, nas_path: Path) -> None`.
- Bewertung: Die Funktionalität existiert im Backup-Service und ist als optional (separater Methodenaufruf) implementiert.

---

- Aussage: „Wichtige Änderungen ... werden im Audit-Log bzw. in `system_events` protokolliert.“
- Status: korrekt
- Beleg: `migrations/0001_schema.sql` enthält die Tabellen `audit_log` und `system_events` (bereits in dieser Sitzung mehrfach gegen Code verifiziert, u. a. im Prüfbericht zur Betriebsdokumentation v1.1).
- Bewertung: Beide Tabellen existieren im Schema.

---

- Aussage: Verweis auf ein separates Dokument „Rollenzuweisung – arbeitszeit“ (Abschnitt 5.1) und ein „Aufbewahrungs- und Löschkonzept“ (Abschnitt 5.3)
- Status: korrekt
- Beleg: `docs/betrieb/rollenzuweisung.md` (bzw. `rollenzuweisung_arbeitszeit_v1_0.md`) und `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` existieren im Repository.
- Bewertung: Referenzierte Dokumente sind vorhanden.

## Zusammenfassung der vorgenommenen Änderungen

Keine Änderungen am Dokument erforderlich; alle prüfbaren technischen Aussagen sind korrekt belegt.

## Offene Punkte (nicht verifizierbar)

- Die übrigen Abschnitte des Dokuments (Verantwortlichkeiten, Schulungspflichten, AV-Vertrags-Prozesse, Unterschriftenfelder, Inkrafttretensdatum) sind organisatorische Ausfüllfelder ohne Codebezug und daher nicht gegen das Repository verifizierbar.
