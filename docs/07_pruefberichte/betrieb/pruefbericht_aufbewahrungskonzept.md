# Prüfbericht: Aufbewahrungs- und Löschkonzept – arbeitszeit

**Geprüftes Dokument:** `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` (Version 1.0)
**Prüfgrundlage:** `regelwerk_arbeitszeit_v5.md` (§18, §19, §20), `pflichtenheft_arbeitszeit_v6.md` (Kap. 12), Quellcode-Suche nach Lösch-/Retention-Logik in `src/arbeitszeit/` (u. a. `src/arbeitszeit/infrastructure/db/repositories/`, `src/arbeitszeit/presentation/admin_cli/employees.py`, `user_accounts.py`), `src/arbeitszeit/infrastructure/backup/backup_service.py`, `src/arbeitszeit/domain/enums.py`

## Gesamteinschätzung

Das Konzept beschreibt die grundsätzliche Löschstrategie (Deaktivierung statt physischer Löschung) zutreffend und deckt sich mit dem Fehlen jeglicher `DELETE`-Anweisungen im Code sowie mit den in Regelwerk v5 (§18) und Pflichtenheft v6 (Kap. 12) verankerten Prinzipien. Der gravierendste Befund betrifft jedoch die genannten Aufbewahrungsfristen: Das Dokument nennt an mehreren Stellen eine **5-Jahres-Frist**, die in keinem der beiden aktuell gültigen Referenzdokumente (Regelwerk v5, Pflichtenheft v6) enthalten ist – beide nennen ausschließlich „mindestens 2 Jahre“. Dies ist ein klarer Versionskonflikt, der im Dokument korrigiert werden sollte. Ein im Dokument beschriebenes Backup-Rotationskonzept mit konkreten Zahlenwerten ist zudem im Code nicht implementiert und daher nicht verifizierbar.

---

### Abschnitt 1 — Zweck und Geltungsbereich

- **Aussage:** Das Konzept gilt „für alle mit dem System ‚arbeitszeit‘ erfassten Arbeitszeitdaten“ sowie „alle zugehörigen Protokoll- und Systemdaten (z. B. Audit-Log, system_events)“.
  **Status:** korrekt
  **Beleg:** `migrations/0001_schema.sql` enthält Tabellen für Arbeitszeitbuchungen sowie `system_events`; Audit-Log-Funktionalität ist in `src/arbeitszeit/infrastructure/backup/backup_service.py` über `SQLiteAuditLogRepository` und `audit_events` referenziert.
  **Bewertung:** Die genannten Datenkategorien existieren tatsächlich im Datenmodell.

---

### Abschnitt 2 — Rechtsgrundlagen und Rahmen

- **Aussage:** „Die Pflicht zur Aufbewahrung dienstlicher Arbeitszeitnachweise steht einer vollständigen physischen Löschung aller Datensätze regelmäßig entgegen. Stattdessen wird mit Status, Einschränkung der Verarbeitung und technischen Schutzmaßnahmen gearbeitet.“
  **Status:** korrekt
  **Beleg:** Keine `DELETE FROM`-Anweisung in `src/arbeitszeit/` auffindbar (Volltextsuche über das gesamte Quellverzeichnis); stattdessen existieren ausschließlich `deactivate()`-Methoden, z. B. `src/arbeitszeit/infrastructure/db/repositories/employee.py`, Zeile 38, und `src/arbeitszeit/infrastructure/db/repositories/user_account.py`, Zeile 39.
  **Bewertung:** Das beschriebene Prinzip „Deaktivierung statt Löschung“ ist durch die Implementierung durchgängig belegt und deckt sich mit Regelwerk v5, §18: „Fachlich relevante Buchungen werden im Normalfall nicht physisch gelöscht, sondern durch Status, Korrektur oder Archivierung behandelt.“

- **Aussage (Rechtsgrundlagen):** Verweis auf ArbZG § 16, DSGVO Art. 5/17/32, BDSG.
  **Status:** nicht zutreffend (organisatorisch)
  **Beleg:** Rein juristische Aufzählung ohne technischen Bezug zum Repository.
  **Bewertung:** Rechtsgrundlagenbenennung ist keine gegen Code prüfbare technische Aussage; inhaltlich deckungsgleich mit den in `pflichtenheft_arbeitszeit_v6.md`, Kap. 12 und Fußnote 8 zitierten Rechtsquellen.

---

### Abschnitt 3 — Datenkategorien im System „arbeitszeit“

- **Aussage:** „Benutzerkonten-Daten: Benutzername, gehashte Passwörter, Rolle (ADMIN/REVIEWER/TECH)“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/domain/enums.py`, Zeilen 56–58: `ADMIN = "ADMIN"`, `REVIEWER = "REVIEWER"`, `TECH = "TECH"`.
  **Bewertung:** Die drei genannten Rollen entsprechen exakt der im Code definierten Rollen-Enumeration.

- **Aussage:** „Technische Protokolle: Audit-Log, system_events, device_events“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/infrastructure/db/repositories/device_event.py` (Tabelle `device_events`); `system_check.py`, Funktion `_write_event()` (Tabelle `system_events`); `backup_service.py`, `SQLiteAuditLogRepository` (Audit-Log).
  **Bewertung:** Alle drei genannten Protokolltypen sind im Code als eigenständige Mechanismen vorhanden.

- **Aussage:** „Exportdaten: CSV/PDF-Auswertungen, die außerhalb der Datenbank erzeugt werden“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/reports.py`, Unterbefehle `export-csv`, `export-pdf-day`, `export-pdf-week`, `export-pdf-month`, `export-pdf-employee` (Zeilen 279–300).
  **Bewertung:** Export-Funktionalität für CSV und PDF ist im Code vorhanden und erzeugt Dateien außerhalb der SQLite-Datenbank.

---

### Abschnitt 4.1 — Aufbewahrungsfristen: Arbeitszeitdaten

- **Aussage:** „Reguläre Aufbewahrungsfrist: mindestens 2 Jahre nach dem jeweiligen Kalenderjahr der Entstehung, in Anlehnung an § 16 Abs. 2 ArbZG.“
  **Status:** korrekt
  **Beleg:** `regelwerk_arbeitszeit_v5.md`, §18: „Arbeitszeitdaten sind mindestens 2 Jahre aufzubewahren.“; `pflichtenheft_arbeitszeit_v6.md`, Kap. 12: „Arbeitszeitdaten müssen mindestens 2 Jahre aufbewahrt werden.“
  **Bewertung:** Die 2-Jahres-Frist stimmt mit beiden aktuell gültigen Referenzdokumenten überein.

- **Aussage:** „Praktische Umsetzung: Daten in der Datenbank werden nicht physisch gelöscht, sondern verbleiben dauerhaft, werden aber nach Ablauf von 5 Jahren nur noch bei berechtigtem Bedarf ausgewertet.“
  **Status:** inkorrekt
  **Beleg:** Weder `regelwerk_arbeitszeit_v5.md` noch `pflichtenheft_arbeitszeit_v6.md` enthalten eine 5-Jahres-Frist. `regelwerk_arbeitszeit_v5.md`, §18 nennt ausschließlich „mindestens 2 Jahre“; `pflichtenheft_arbeitszeit_v6.md`, Kap. 12 ebenso nur „mindestens 2 Jahre“. Eine Suche nach „5 Jahr“ in beiden Dokumenten ergibt keinen Treffer. Zudem existiert im Code keine zeitgesteuerte Auswertungsbeschränkung nach Fristablauf (keine entsprechende Logik in `src/arbeitszeit/`).
  **Bewertung:** Die genannte 5-Jahres-Frist ist ein Versionskonflikt gegenüber den beiden aktuell gültigen Regeldokumenten und zugleich technisch nicht im Code abgebildet (keine Umsetzung einer „eingeschränkten Auswertung nach 5 Jahren“ auffindbar).
  **Anpassungsvorschlag:** Frist auf die in Regelwerk v5 §18 und Pflichtenheft v6 Kap. 12 einheitlich genannten „mindestens 2 Jahre“ abstimmen oder, falls eine längere praktische Aufbewahrung fachlich gewünscht ist, dies als eigenständige, von den Regeldokumenten unabhängige betriebliche Entscheidung kennzeichnen und mit den Regeldokumenten abgleichen/dort ergänzen.

---

### Abschnitt 4.2 — Mitarbeiter-Stammdaten

- **Aussage:** „Nach Beendigung des Beschäftigungsverhältnisses: Deaktivierung der Zuordnung im System (z. B. Deaktivierung RFID-Karte, Kennzeichnung als ‚inaktiv‘).“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/employees.py`, Funktionen `cmd_employees_deactivate` (Zeile 69) und `cmd_cards_deactivate` (Zeile 116); zugehörige Use Cases `DeactivateEmployeeUseCase`, `DeactivateRfidCardUseCase`.
  **Bewertung:** Sowohl Mitarbeiter- als auch Karten-Deaktivierung sind als konkrete, separate Funktionen im Code vorhanden und entsprechen exakt der Beschreibung.

- **Aussage:** „Mindestaufbewahrung der arbeitszeitrelevanten Daten: 2 Jahre, praktische Aufbewahrung von bis zu 5 Jahren, wenn arbeitsrechtliche Auseinandersetzungen nicht ausgeschlossen sind.“
  **Status:** inkorrekt
  **Beleg:** Wie unter 4.1 dargelegt, nennen weder `regelwerk_arbeitszeit_v5.md` noch `pflichtenheft_arbeitszeit_v6.md` eine 5-Jahres-Frist.
  **Bewertung:** Gleicher Versionskonflikt wie in Abschnitt 4.1; die 2-Jahres-Frist ist belegt, die zusätzliche 5-Jahres-Angabe nicht.
  **Anpassungsvorschlag:** Analog zu 4.1 anpassen oder als eigenständige, nicht aus den Regeldokumenten abgeleitete Praxisentscheidung kennzeichnen.

---

### Abschnitt 4.3 — Benutzerkonten-Daten

- **Aussage:** „Nach Ausscheiden oder Rollenwechsel: Deaktivierung des Benutzerkontos (kein Login mehr möglich).“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Funktion `cmd_users_deactivate` (Zeile 93); `src/arbeitszeit/infrastructure/db/repositories/user_account.py`, Methode `deactivate()` (Zeile 39).
  **Bewertung:** Funktion existiert exakt wie beschrieben.

- **Aussage:** „Keine physische Löschung von Audit-Log-Einträgen, um Nachvollziehbarkeit zu gewährleisten.“
  **Status:** korrekt
  **Beleg:** Keine `DELETE FROM`-Anweisung für Audit-Log-Tabellen im gesamten Quellverzeichnis auffindbar; `src/arbeitszeit/infrastructure/backup/backup_service.py` verwendet `SQLiteAuditLogRepository` ausschließlich für Einfüge-Operationen (`_log_audit`).
  **Bewertung:** Aussage ist durch das Fehlen jeglicher Löschfunktion für Audit-Log-Daten belegt.

---

### Abschnitt 4.4 — Technische Protokolle (Audit-Log, system_events, device_events)

- **Aussage:** „Mindestens 2 Jahre, faktisch solange das System produktiv im Einsatz ist.“
  **Status:** korrekt
  **Beleg:** Deckt sich mit der 2-Jahres-Frist aus `regelwerk_arbeitszeit_v5.md` §18 und `pflichtenheft_arbeitszeit_v6.md` Kap. 12; keine automatische Löschroutine für `system_events` oder `device_events` im Code vorhanden, sodass „faktisch dauerhaft“ zutreffend beschrieben ist.
  **Bewertung:** Sowohl die Fristangabe als auch das Fehlen einer technischen Löschautomatik sind belegt.

---

### Abschnitt 4.5 — Exporte (CSV/PDF)

- **Aussage:** „Standardaufbewahrungsfrist der Praxis für solche Dokumente: 5 Jahre, sofern nicht kürzere Fristen vereinbart oder längere Aufbewahrung aus Gründen der Beweisführung erforderlich ist.“
  **Status:** inkorrekt
  **Beleg:** Weder `regelwerk_arbeitszeit_v5.md` noch `pflichtenheft_arbeitszeit_v6.md` nennen eine 5-Jahres-Frist für Exporte; beide Dokumente verweisen für Exporte/Berichte nur allgemein auf ein „Archivierungs- und Löschkonzept“ (Regelwerk v5 §18: „Berichte, Pflichtauswertungen und Exportdateien sind nach dem festgelegten Archivierungs- und Löschkonzept zu behandeln.“; Pflichtenheft v6 Kap. 12: „Technische Protokolle, Backups und Exportdateien sind nach einem definierten Archivierungs- und Löschkonzept zu behandeln.“), ohne eine konkrete Jahreszahl festzulegen.
  **Bewertung:** Die konkrete 5-Jahres-Zahl für Exporte ist in den aktuell gültigen Regeldokumenten nicht enthalten und daher nicht durch sie gedeckt; zugleich ist im Code keine automatisierte fristbasierte Löschung von Exportdateien implementiert (keine entsprechende Funktion in `src/arbeitszeit/infrastructure/backup/backup_service.py` oder anderswo), sodass die Angabe auch technisch nicht überprüfbar umgesetzt ist.
  **Anpassungsvorschlag:** Konkrete Fristangabe entweder entfernen bzw. als eigenständige, nicht aus Regelwerk v5/Pflichtenheft v6 abgeleitete organisatorische Festlegung kennzeichnen, oder mit den Regeldokumenten harmonisieren.

---

### Abschnitt 5 — Löschung, Deaktivierung und Anonymisierung

- **Aussage:** „Primär werden Konten und Mitarbeiter-Datensätze deaktiviert, nicht physisch gelöscht.“
  **Status:** korrekt
  **Beleg:** Siehe Belege zu Abschnitt 4.2/4.3 (`employees.py`, `user_accounts.py`, jeweilige Repository-`deactivate()`-Methoden); keine `DELETE FROM`-Anweisung für diese Entitäten im Code.
  **Bewertung:** Durchgängig belegt.

- **Aussage:** „Produktiv-Datenbank: keine routinemäßige physische Löschung einzelner Arbeitszeitdatensätze; stattdessen Kennzeichnung von Korrekturen über Korrektur-Mechanismen, deaktivierte Mitarbeiter-/Benutzerkonten.“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/presentation/admin_cli/bookings.py`, Unterbefehle `correct` und `supplement` (Zeilen 165–178) als Korrekturmechanismen statt Löschung; keine `DELETE`-Logik für Buchungsdaten im Code.
  **Bewertung:** Korrektur-Mechanismen sind im Code als eigenständige, dokumentierte Funktionen vorhanden.

- **Aussage:** „Exporte: nach Ablauf der internen Aufbewahrungsfrist werden Exportdateien in definierten Zyklen gelöscht (siehe Abschnitt 7).“
  **Status:** nicht verifizierbar
  **Beleg:** Keine automatisierte Löschroutine für Exportdateien in `src/arbeitszeit/` oder `scripts/` auffindbar.
  **Bewertung:** Die beschriebene zyklische Löschung ist im Code nicht implementiert; ob dies rein organisatorisch (manuell) erfolgen soll, lässt sich aus dem Dokument selbst vermuten (Verweis auf Abschnitt 7, Verantwortlichkeiten), ist aber nicht technisch verifizierbar, da kein automatisierter Mechanismus existiert.

---

### Abschnitt 6 — Backups und Wiederherstellung

- **Aussage:** „Backups enthalten regelmäßig vollständige Kopien der Datenbank und ggf. Exporte.“
  **Status:** korrekt
  **Beleg:** `src/arbeitszeit/infrastructure/backup/backup_service.py`, Methode `create_local_backup()`: erstellt vollständige SQLite-Kopie via `src.backup(dst)` und kopiert bei gesetztem `export_dir` zusätzlich Exportdateien nach `backup_dir/exports/` (`shutil.copytree`).
  **Bewertung:** Beschreibung stimmt exakt mit der Implementierung überein.

- **Aussage:** „Rotationskonzept (z. B. tägliche Backups der letzten X Tage, wöchentliche Backups der letzten Y Wochen).“ sowie das nachfolgende Formularfeld „Konkretes Rotationschema: Tägliche/Wöchentliche/Monatliche Sicherungen: ___“
  **Status:** nicht verifizierbar
  **Beleg:** `src/arbeitszeit/infrastructure/backup/backup_service.py` enthält keine Rotations- oder Aufräumlogik (keine Funktion zum Löschen älterer Backup-Dateien); `scripts/backup.py` erstellt bei jedem Aufruf lediglich eine neue, zeitgestempelte Backup-Datei, ohne alte Stände zu entfernen.
  **Bewertung:** Ein automatisiertes Rotationskonzept mit Lösch- oder Aufräumfunktion ist im Repository nicht implementiert. Die Aussage beschreibt eine wünschenswerte organisatorische Praxis, die technisch nicht abgebildet ist; die konkreten Zahlenwerte sind zudem als Formularfelder ohnehin auszufüllen.
  **Anpassungsvorschlag:** Klarstellen, dass die Backup-Rotation derzeit nicht durch das System automatisiert wird, sondern manuell bzw. durch externe Mechanismen (z. B. Cron/systemd-Timer-Konfiguration außerhalb des Repositories) umzusetzen ist, sofern keine entsprechende Codefunktion existiert.

---

### Abschnitt 7 — Verantwortlichkeiten

- **Aussagen:** Benennung von „Datenschutz-Verantwortliche/r der Praxis“ und „Technische Verantwortung (IT/Betrieb)“ als ausfüllbare Felder.
  **Status:** nicht zutreffend (organisatorisch)
  **Beleg:** Formularfelder ohne technischen Bezug.
  **Bewertung:** Betriebliche Zuständigkeitsregelung, nicht gegen Code prüfbar.

---

### Abschnitt 8 — Dokumentation von Löschvorgängen

- **Aussage:** Vorgaben zur Protokollierung außergewöhnlicher Löschvorgänge (Datum, Person, Kategorie, Begründung, Methode, Bestätigung).
  **Status:** nicht zutreffend (organisatorisch)
  **Beleg:** Beschreibt einen manuellen, papier-/formularbasierten Dokumentationsprozess außerhalb der Software.
  **Bewertung:** Kein technisch prüfbarer Bezug zum Code; das Fehlen einer entsprechenden automatisierten Lösch-Protokollfunktion im Code (siehe oben) steht im Einklang damit, dass dies laut Dokument manuell zu führen ist.

---

### Abschnitt 9 — Inkrafttreten und Überprüfung

- **Aussage:** „Es wird mindestens alle 2 Jahre oder bei wesentlichen Änderungen der Rechtslage bzw. der Systemarchitektur überprüft.“
  **Status:** nicht zutreffend (organisatorisch)
  **Beleg:** Organisatorische Überprüfungsregel ohne technischen Prüfgegenstand.
  **Bewertung:** Kein Codebezug möglich; rein prozessuale Festlegung.

---

## Zusammenfassung der Kernbefunde

1. **Versionskonflikt bei Aufbewahrungsfristen:** Die im Dokument mehrfach genannte 5-Jahres-Frist (Abschnitte 4.1, 4.2, 4.5) ist in keinem der beiden aktuell gültigen Regeldokumente enthalten. `regelwerk_arbeitszeit_v5.md` (§18) und `pflichtenheft_arbeitszeit_v6.md` (Kap. 12) nennen ausschließlich „mindestens 2 Jahre“. Dies ist der schwerwiegendste Befund und sollte vorrangig korrigiert oder mit den Regeldokumenten abgeglichen werden.
2. Das Grundprinzip „Deaktivierung statt physischer Löschung“ ist durchgängig durch den Code belegt (keine `DELETE FROM`-Anweisungen für Mitarbeiter-, Benutzerkonten- oder Buchungsdaten; ausschließlich `deactivate()`-Methoden).
3. Die genannten Datenkategorien (Arbeitszeitdaten, Stammdaten, Benutzerkonten mit Rollen ADMIN/REVIEWER/TECH, technische Protokolle, Exporte) sind vollständig im Datenmodell und Code wiederzufinden.
4. Ein konkretes, automatisiertes Backup-Rotationskonzept sowie eine automatisierte zyklische Löschung von Exportdateien sind im Code **nicht implementiert** und daher nicht verifizierbar; die entsprechenden Aussagen in Abschnitt 5 und 6 sollten als organisatorisch/manuell umzusetzend gekennzeichnet werden, sofern keine Automatisierung vorgesehen ist.
