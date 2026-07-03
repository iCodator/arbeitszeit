# Prüfbericht: `docs/SECURITY.md`

**Geprüftes Dokument:** `docs/SECURITY.md`
**Repository:** iCodator/arbeitszeit
**Prüfgrundlage:** `src/arbeitszeit/domain/audit_events.py`, `src/arbeitszeit/presentation/admin_cli/main.py`, `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, `migrations/0001_schema.sql`

---

## Gesamteinschätzung

Das Sicherheitsmodell-Dokument ist inhaltlich weitgehend zutreffend, enthielt jedoch mehrere Detailfehler bei Audit-Ereignisnamen, CLI-Aufrufbeispielen und einer Datenbankspaltenbezeichnung, die gegen den Code nicht standhielten. Alle Abweichungen wurden korrigiert; die organisatorischen und rechtlichen Aussagen (Abschnitt 6 und 7) sind Ankreuz-/Empfehlungscharakter ohne unmittelbaren Codebezug und bleiben unverändert.

---

## Strukturierter Report je Aussage

**Aussage:** Audit-Ereignis für NAS-Sync lautet `BACKUP_NAS_SYNCED`.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/domain/audit_events.py` definiert die Konstante `BACKUP_SYNCED_TO_NAS`; `BACKUP_NAS_SYNCED` existiert nicht.
**Bewertung:** Der Ereignisname wich vom tatsächlichen Konstantennamen im Code ab.
**Anpassungsvorschlag:** Zeile korrigiert zu `BACKUP_SYNCED_TO_NAS`.

**Aussage:** Audit-Ereignis für erfasste Buchung lautet `BOOKING_CREATED`.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/domain/audit_events.py`, Abschnitt „Buchungsereignisse“: definiert `TIME_BOOKED`; keine Konstante `BOOKING_CREATED` im gesamten Modul.
**Bewertung:** Der genannte Ereignisname existiert im Code nicht.
**Anpassungsvorschlag:** Zeile korrigiert zu `TIME_BOOKED`.

**Aussage:** Systemcheck und Backup werden über `arbeitszeit system check` bzw. `arbeitszeit system backup` aufgerufen.
**Status:** inkorrekt
**Beleg:** `src/arbeitszeit/presentation/admin_cli/main.py`: `argparse.ArgumentParser(prog="admin", ...)`. Der tatsächliche Aufruf lautet `admin --db <PFAD> --user-id <ID> system check` bzw. `system backup`.
**Bewertung:** Das im Dokument genannte Kommando `arbeitszeit` existiert als CLI-Einstiegspunkt-Name nicht; der tatsächliche `prog`-Name ist `admin`.
**Anpassungsvorschlag:** Beide Aufrufbeispiele auf `admin --db <PFAD> --user-id <ID> system check`/`system backup` korrigiert.

**Aussage:** „Das verwendete Hash-Verfahren ist in `infrastructure/db/` dokumentiert.“
**Status:** inkorrekt
**Beleg:** Die Passwort-Hashing-Funktion `_hash_password` (PBKDF2-HMAC-SHA256, 260.000 Iterationen, 16-Byte-Zufallssalt) ist in `src/arbeitszeit/presentation/admin_cli/user_accounts.py` definiert, nicht unter `infrastructure/db/`.
**Bewertung:** Der referenzierte Ort war falsch; das Verfahren selbst (PBKDF2-HMAC-SHA256) ist zutreffend, aber am falschen Modulpfad verortet.
**Anpassungsvorschlag:** Abschnitt 5 korrigiert: Verfahren und konkrete Parameter (PBKDF2-HMAC-SHA256, 260.000 Iterationen, 16-Byte-Salt) direkt benannt, mit korrektem Verweis auf `presentation/admin_cli/user_accounts.py`, Funktion `_hash_password`.

**Aussage:** Deaktivierte Benutzerkonten werden über die Spalte `is_active = false` erkannt.
**Status:** inkorrekt
**Beleg:** `migrations/0001_schema.sql`, Tabelle `user_accounts`: Spalte `active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))`. Eine Spalte `is_active` existiert im Schema nicht.
**Bewertung:** Der Spaltenname im Dokument entsprach nicht dem tatsächlichen Schema.
**Anpassungsvorschlag:** Korrigiert zu `active = 0`.

**Aussage (Abschnitt 2):** RFID-UIDs werden mit SHA-256 gehasht (`infrastructure/hardware/uid_hash.py`).
**Status:** korrekt
**Beleg:** `src/arbeitszeit/infrastructure/hardware/uid_hash.py`, Funktion `hash_uid`, verwendet `hashlib.sha256`.
**Bewertung:** Datei- und Verfahrensangabe stimmen mit dem Code überein.

**Aussage (Abschnitt 4):** Systemcheck prüft NAS-Erreichbarkeit ausschließlich über Dateisystem-Mount (`Path.exists()`, `os.access(..., os.W_OK)`), kein aktiver Netzwerk-Ping.
**Status:** korrekt
**Beleg:** `src/arbeitszeit/infrastructure/system_check.py`, Funktion `_check_nas` verwendet exakt diese Prüfmechanik ohne Netzwerkprotokoll-Test.
**Bewertung:** Aussage ist durch den Code direkt belegt.

**Aussage (Abschnitt 6):** „§ 147 AO: 10 Jahre für lohnsteuerrelevante Aufzeichnungen“ als Empfehlung zur Aufbewahrungsfrist.
**Status:** nicht verifizierbar (kein Codebezug)
**Beleg:** Es handelt sich um eine rechtliche Referenz (Abgabenordnung), nicht um eine aus dem Repository ableitbare technische Aussage. Das System selbst erzwingt keine Aufbewahrungsfrist.
**Bewertung:** Die Aussage betrifft eine gesetzliche Fundstelle außerhalb des Repositorys und wird als Empfehlung an den Betreiber formuliert; sie steht nicht im Widerspruch zum Code (das Dokument erwähnt korrekt, dass das System keine automatische Löschfunktion enthält). Keine Änderung erforderlich.

**Aussage (Abschnitt 7):** „Bekannte Einschränkungen“ (kein Netzwerk-Ping, keine automatische Sitzungsablauf, keine Verschlüsselung der SQLite-Datei, keine automatische Backup-Integritätsprüfung).
**Status:** korrekt, soweit code-bezogen; übrige Punkte organisatorisch
**Beleg:** Fehlender Netzwerk-Ping bereits in Abschnitt 4 belegt (`_check_nas`). Für CLI-Sitzungsablauf und SQLite-Verschlüsselung existiert im Code keine gegenteilige Implementierung (keine Session-Timeout-Logik, keine Verschlüsselungsroutine in `infrastructure/db/`), was die Aussage stützt.
**Bewertung:** Keine Abweichung zum Code feststellbar.

---

## Zusammenfassung der Korrekturen

1. Audit-Ereignis „NAS-Sync“: `BACKUP_NAS_SYNCED` → `BACKUP_SYNCED_TO_NAS`.
2. Audit-Ereignis „Buchung erfasst“: `BOOKING_CREATED` → `TIME_BOOKED`.
3. CLI-Aufrufbeispiele: `arbeitszeit system check`/`system backup` → `admin --db <PFAD> --user-id <ID> system check`/`system backup`.
4. Passwort-Hash-Dokumentationsort: `infrastructure/db/` → `presentation/admin_cli/user_accounts.py`, Funktion `_hash_password`, mit konkreten Parametern (PBKDF2-HMAC-SHA256, 260.000 Iterationen, 16-Byte-Salt).
5. Spaltenname deaktivierter Konten: `is_active = false` → `active = 0`.

## Offene Punkte

Keine offenen, nicht verifizierbaren Punkte mit Änderungsbedarf. Die rechtliche AO-Referenz (Abschnitt 6) und die organisatorischen Einschränkungen (Abschnitt 7) sind außerhalb des Codebezugs und bleiben unverändert.
