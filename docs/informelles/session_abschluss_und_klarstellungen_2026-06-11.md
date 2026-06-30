# Session-Abschluss und Klarstellungen — 2026-06-11

**Datum:** 2026-06-11  
**Zweck:** Dieses Dokument fasst alle Abschlussnotizen, Abschlussprotokolle,
Klarstellungen und Einordnungsnotizen der Design- und Audit-Session vom 2026-06-11
zusammen. Es ersetzt die folgenden Einzeldokumente, die in `docs/informelles/archiv/`
archiviert sind:

- `abarbeitung_hoch_abschlussnotiz_v1.md`
- `abarbeitung_mittel_abschlussnotiz_v1.md`
- `abarbeitung_niedrig_abschlussnotiz_v1.md`
- `device_event_abschlussprotokoll_v1.md`
- `audit_evidenzgrenzen_v1.md`
- `audit_klarstellungen_niedrig_v1.md`
- `migrationsuebersicht_notiz_v1.md`
- `terminologie_harmonisierung_v1.md`

**Abgrenzung:** Dieses Dokument enthält keine Freigaben, keine DSFA und keine
verbindlichen Betriebsanweisungen. Es dokumentiert den technischen und organisatorischen
Abschlussstand der Session. Verbindliche Referenzdokumente bleiben
`pflichtenheft_arbeitszeit_v5.md`, `regelwerk_arbeitszeit_v5.md` und
`docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`.

---

## 1. Abarbeitung nach Prioritätsstufen

Alle vier Prioritätsstufen aus den Audit-Prompts vom 2026-06-11 sind vollständig
abgearbeitet.

| Priorität | Status | Kern-Deliverables |
|---|---|---|
| kritisch | geschlossen ✓ | `device_events`-Verkettung (Commit `0f20931`) + `testmatrix_revision_v1.md` |
| hoch | geschlossen ✓ | `nachtragsmatrix_phasen_v1.md` + `betriebsdokumentation_arbeitszeit_v1_1.md` |
| mittel | geschlossen ✓ | `terminologie_harmonisierung_v1.md` + `migrationsuebersicht_notiz_v1.md` + Korrekturen in Phasenplänen |
| niedrig | geschlossen ✓ | `audit_klarstellungen_niedrig_v1.md` + `audit_evidenzgrenzen_v1.md` + Ergänzungen in `planung_gesamt.md` |

### 1.1 Priorität hoch — Nachtragsmatrix und Betriebsdokumentation

**Grundlage:** `docs/informelles/planung_hoch_v1_2026-06-11.md`

**Erstellte und geprüfte Deliverables:**

| Deliverable | Soll | Ist | Status |
| --- | --- | --- | --- |
| `nachtragsmatrix_phasen_v1.md` | Phasenübergreifende Nachtragsmatrix, ca. 40+ Zeilen | erstellt (44 Artefakte) | ✓ |
| `betriebsdokumentation_arbeitszeit_v1_1.md` | Formale Betriebsdokumentation, 12 Abschnitte | erstellt | ✓ |
| Verweise in `planung_gesamt.md` | Kurze Verweise auf neue Dokumente | ergänzt | ✓ |
| Verweise in `phase4_planung.md` | Schritt 7 + Schritt 9 | ergänzt | ✓ |
| Verweise in `phase5_planung.md` | Terminal-UI-Abschnitt | ergänzt | ✓ |

**Inhalt Nachtragsmatrix (`nachtragsmatrix_phasen_v1.md`):**

- 44 Artefakte (Migrationen, Scripts, Domain/Application/Infrastructure/Presentation, Testmodule)
- Alle Einträge mit mindestens einer Belegstelle aus Phasenplänen
- Erkannte Phasenverschiebungen:
  - **Vorgezogen (Phase 3 statt 4):** `approve_supplement.py`, `reject_supplement.py`, zugehörige Tests, Ruhezeit- und Rollenprüfung in `book_time.py`
  - **Nachgezogen:** Migrationen 0003–0006, `device_event_id`-Produktionspfad, `restore_exports`, `reactivate`/`change-role`/`bootstrap`, `setup_vollstaendig()`
  - **Spätere Testergänzungen:** `test_migrations.py`, `test_booking_rules.py`, `test_booking_flow.py`, `test_backup.py`
  - **Dokumentationskorrekturen:** v4→v5, `ValidationResult` entfernt
- Eine offene Phasenzuordnung (`test_init_db.py`) explizit als nicht entscheidbar ausgewiesen

**Inhalt Betriebsdokumentation (`betriebsdokumentation_arbeitszeit_v1_1.md`):**

12 Abschnitte: Systemübersicht, Ersteinrichtung, Terminal-UI-Betrieb, Admin-CLI,
Backup-Betrieb, Export-Betrieb, Systemcheck, Rollenkonzept, Hardware-Verkettung
(`device_events`), Migrationsstand, Freigabefähigkeitsstatus (13 Punkte, klar nach
technisch/organisatorisch getrennt), Abgrenzung (kein Freigabedokument, keine DSFA).

**Restpunkte (organisatorisch offen, nicht aus Repo-Artefakten schließbar):**

1. Formale Betriebsfreigabe durch berechtigte Stelle
2. Konkrete Rollenzuweisung (wer ist Admin, Reviewer, Tech)
3. Nachweis Smoke-Tests auf Zielhardware (Protokoll fehlt im Repo)
4. AV-Vertrag falls Cloud-Backup genutzt wird
5. Einbindung in IT-Sicherheitskonzept der Praxis (§ 75b SGB V)
6. OS-seitige Zugriffsrechte auf Exportverzeichnis

### 1.2 Priorität mittel — Terminologie und Migrationsübersicht

**Grundlage:** `docs/informelles/planung_mittel_v1_2026-06-11.md`

**Erstellte und geprüfte Deliverables:**

| Deliverable | Soll | Ist | Status |
| --- | --- | --- | --- |
| `terminologie_harmonisierung_v1.md` | Terminologie-Spannungen dokumentiert | erstellt | ✓ |
| `migrationsuebersicht_notiz_v1.md` | Migrationsübersicht mit Einordnungsnotiz | erstellt | ✓ |
| `phase2_planung.md` Z.327 Überschrift | `V5-Bezüge und organisatorische Auflagen` | korrigiert | ✓ |
| `phase5_planung.md` Z.257 Testzählung | historischer / heutiger Stand getrennt | korrigiert | ✓ |
| `phase5_planung.md` Z.375 Schätzlabel | `~8 Tests` → `8 Tests` | korrigiert | ✓ |
| Migrationstabelle in `phase1_planung.md` | Kompakte Übersichtstabelle | ergänzt | ✓ |

**Offene Punkte:** Keine inhaltlichen Offenheiten aus mittel-Aufgaben.
Terminologische Empfehlungen in `terminologie_harmonisierung_v1.md` sind nicht
bindend; sie erfordern keine Änderung an bestehendem Code oder Dokumentation.

### 1.3 Priorität niedrig — Audit-Klarstellungen und Evidenzgrenzen

**Grundlage:** `docs/claude_coding/claude_code_prompt_niedrig_arbeitszeit_v1_2026-06-11_20-15.md`

**Erstellte und geprüfte Deliverables:**

| Deliverable | Soll | Ist | Status |
| --- | --- | --- | --- |
| `audit_klarstellungen_niedrig_v1.md` | Lesbarkeits-Spannungen dokumentiert | erstellt | ✓ |
| `audit_evidenzgrenzen_v1.md` | Evidenzgrenzen-Dokumentation | erstellt | ✓ |
| Hinweis approve/reject in `planung_gesamt.md` | Phase-3-Abschnitt ergänzt | ergänzt | ✓ |
| Referenz evidenzgrenzen in `planung_gesamt.md` | Link auf neues Dokument | ergänzt | ✓ |

**Offene Punkte:** Keine inhaltlichen Offenheiten aus niedrig-Aufgaben. Die
identifizierten externen Nachweise (Betriebsfreigabe, Rollenzuweisung, AV-Vertrag,
Smoke-Tests, IT-Sicherheitskonzept, Löschkonzept) liegen außerhalb des Repositories.
Sie wurden dokumentiert, nicht geschlossen.

---

## 2. Abschlussprotokoll: device_events / device_event_id

**Grundlage:** `claude_code_anweisung_kritisch_arbeitszeit_v1_2026-06-11_19-42.md` (Schritt A.4)

### 2.1 Getroffene Entscheidung

**Pfad A1 — Produktive Implementierung**

Alle Repository-Artefakte (`planung_gesamt.md`, `phase4_planung.md`,
`phase5_planung.md`, `migrations/0005`) belegen, dass die Verkettung zum
verbindlichen Sollbild gehört. Pfad A2 (formale Sollbildbereinigung) war auf
Artefaktbasis nicht vertretbar. Details: `docs/adr/device_event_architekturentscheidung_v1.md`.

### 2.2 Geänderte Dateien

| Datei | Art der Änderung |
|---|---|
| `src/arbeitszeit/domain/ports/repositories.py` | `DeviceEventRepository`-Protocol ergänzt |
| `src/arbeitszeit/application/unit_of_work.py` | `device_event_repo`-Attribut im Protocol |
| `src/arbeitszeit/infrastructure/db/repositories/device_event.py` (neu) | `SQLiteDeviceEventRepository.add()` |
| `src/arbeitszeit/infrastructure/db/repositories/__init__.py` | Export ergänzt |
| `src/arbeitszeit/infrastructure/db/unit_of_work.py` | `self.device_event_repo` im Konstruktor |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | `RFID_SCAN`-Record erzeugen; ID durchreichen |
| `tests/application/fakes.py` | `FakeDeviceEventRepository`; `FakeUnitOfWork.device_event_repo` |
| `tests/integration/test_device_event_booking.py` (neu) | 3 Integrationstests |
| `docs/informelles/planung_gesamt.md` | 3 Stellen aktualisiert (offener Architekturpunkt → abgeschlossen) |
| `docs/informelles/phase4_planung.md` | Abgrenzungstext aktualisiert |
| `docs/informelles/phase5_planung.md` | Scope-Abgrenzung aktualisiert |

**Git-Commits:**
- `0f20931` — technische Implementierung
- Folge-Commit — Dokumentation

### 2.3 Geprüfte, nicht geänderte Dateien

| Datei | Prüfergebnis |
|---|---|
| `migrations/0001_schema.sql` | `device_events`-Schema korrekt und vollständig; keine Änderung nötig |
| `migrations/0005_time_bookings_device_event_id.sql` | FK-Constraint bereits vorhanden; keine Änderung nötig |
| `src/arbeitszeit/application/commands.py` | `BookCommand.device_event_id: int | None` bereits vorhanden |
| `src/arbeitszeit/application/use_cases/book_time.py` | Übernahme von `cmd.device_event_id` in `TimeBooking` bereits vorhanden |
| `docs/informelles/phase1_planung.md`–`phase3_planung.md` | Kein `device_event_id`-Bezug im Scope dieser Phasen |

### 2.4 Offene Restpunkte (Erweiterungsoptionen, kein Pflichtcharakter)

| Punkt | Beschreibung | Bewertung |
|---|---|---|
| `device_events.related_time_booking_id` | Rückverknüpfung zur Buchung noch nicht befüllt | Kein Sollbild-Auftrag gefunden; Erweiterungsoption |
| `BOOKING_ACCEPTED`/`BOOKING_REJECTED`-`event_types` | Nach Buchungsergebnis nicht rückwirkend gesetzt | Kein Sollbild-Auftrag gefunden; Erweiterungsoption |
| JOIN-Abfragen über `device_events` in `report_queries.py` | Keine Pflichtauswertung über `device_events` | Optional; `time_bookings.device_event_id` reicht |

**Befund:** Der kritische Auditbefund „offener Architekturpunkt device_events /
device_event_id" ist vollständig geschlossen. Operative Kette
`RFID-Scan → device_events-Record → BookCommand.device_event_id → time_bookings.device_event_id`
implementiert, 3 Integrationstests grün, alle 406 Tests der Gesamtsuite grün.

---

## 3. Audit-Evidenzgrenzen

**Zweck:** Systematische Transparenz darüber, was aus den Repository-Artefakten
belegt, nur teilweise belegt oder nicht entscheidbar ist.

**Artefaktbasis:** `planung_gesamt.md` V5-/V2-Abgleich, `phase4_planung.md`,
`phase5_planung.md`, `pflichtenheft_arbeitszeit_v5.md`, `regelwerk_arbeitszeit_v5.md`,
`anlage_einhaltung_pflichtenheft_v2.md`.

### 3.1 Durch Repository-Artefakte vollständig belegt

| Thema | Belegbasis | Aussagegrenze |
| --- | --- | --- |
| Buchungslogik (COME/GO/BREAK) | Domain/Tests: 406 Tests grün | Kein Nachweis realer Gerätenutzung |
| ArbZG-Prüfhilfen (§ 3/4/5) | `compliance_checks.py` + Tests | Ersetzt keine juristische Einzelfallprüfung |
| Backup/Restore-Mechanismus | `backup_service.py` + E2E-Tests | Operativer Einsatz nicht im Repo nachweisbar |
| Systemcheck | `system_check.py` + 17 Tests | Geräte-Check nur mit Simulator-Pfaden |
| Benutzerkontenverwaltung (ADMIN/REVIEWER/TECH) | `user_accounts.py` + 18 Tests | Formale Betriebsfreigabe nicht im Repo |
| `device_events`-Verkettung | Commit `0f20931` + 3 Tests | Nur mit `SimulatedHardwareReader` getestet |
| Revisionsfeste Testmatrix | `docs/betrieb/nachweise/testmatrix_revision_v1.md` | Formale Abnahme nicht im Repo |

### 3.2 Nur teilweise belegt

| Thema | Belegbasis | Aussagegrenze | Offene Folgefrage |
| --- | --- | --- | --- |
| Betriebsdokumentation | `betriebsdokumentation_arbeitszeit_v1_1.md` | Formale Verabschiedung fehlt im Repo | Wer gibt das Dokument frei? |
| NAS-Backup-Funktion | `backup_service.py sync_to_nas()`; E2E-Tests mit Mock-NAS | Echter NAS-Pfad nur als Betriebsentscheidung dokumentiert | Wurde NAS-Sync im Betrieb getestet? |
| Exportverzeichnis-Schutz | `setup.py` setzt `export.export_dir`; Zugriffsrechte OS-Ebene nicht im Repo | Dateisystem-Rechte außerhalb des Codes | Wurden Zugriffsrechte auf dem Zielsystem gesetzt? |
| Restore-Freigabe | `restore_from()` implementiert und getestet | Berechtigung zur Restore-Durchführung ist Betriebsregel | Wer ist im Betrieb berechtigt? |

### 3.3 Nicht entscheidbar auf Basis der vorliegenden Artefakte

| Thema | Aussagegrenze | Offene Folgefrage |
| --- | --- | --- |
| Passwort-Änderung als Bestandteil von „änderbar" (PH v5 §7.9) | Kein CLI-Befehl `users change-password` vorhanden; PH §7.9 nennt „änderbar" ohne Spezifikation | Muss §7.9 „änderbar" explizit Passwort-Änderung einschließen? |
| Organisatorische Rollenzuweisung in der Praxis | Nur als Anforderung in PH §15 / RW §22 | Wer ist konkret Admin, Prüfer, technische Betreuung? |
| Hardware-Smoke-Tests auf Zielhardware | Keine Smoke-Test-Protokolle im Repo | Wurden Smoke-Tests auf dem realen Terminal-Gerät durchgeführt? |
| Formale Betriebsfreigabe als System | Kein Freigabedokument im Repo | Welche Stelle gibt das System für den Produktivbetrieb frei? |
| AV-Vertrag Cloud-Backup | `planung_gesamt.md` nennt AV-Vertrag als erforderlich | Wurde Cloud-Backup entschieden? Falls ja, AV-Vertrag abgeschlossen? |
| IT-Sicherheitskonzept § 75b SGB V | Einbindung in Praxis-IT-Sicherheitskonzept außerhalb des Repos | Ist das System in das Sicherheitskonzept der Praxis eingebunden? |
| Schlüsselverwaltung, TOM, Rotationskonzept | Nur als Anforderung genannt | Wurden diese Unterlagen für die Praxis erstellt? |

### 3.4 Erforderliche externe Nachweise

1. Formale Betriebsfreigabe durch berechtigte Person/Stelle
2. Organisatorische Rollenzuweisung (wer ist Admin, Prüfer, technische Betreuung)
3. AV-Vertrag, falls Cloud-Backup genutzt wird
4. Nachweis Smoke-Tests auf Zielhardware
5. Einbindung in IT-Sicherheitskonzept der Praxis (§ 75b SGB V)
6. Aufbewahrungs- und Löschkonzept (schriftlich verabschiedet)

---

## 4. Lesbarkeits-Spannungen und Korrekturen

Alle fünf im Audit-Selbstcheck identifizierten Lesbarkeits-Spannungen wurden
dokumentiert. Es wurden keine fachlichen Inhalte geändert, keine Sollbilder
überschrieben.

### 4.1 Spannung 1 — fehlender Hinweis auf vorimplementierte Phase-4-Use-Cases

**Betroffene Datei:** `planung_gesamt.md` (Phase-3-Abschnitt)

Die Zielstruktur in `planung_gesamt.md` listete nur die vier originären Phase-3-Use-Cases.
`approve_supplement.py` und `reject_supplement.py` erschienen nicht, obwohl sie in
Phase 3 real vorimplementiert wurden. Belegt in `phase3_planung.md` Z.102–103 und
Z.257–273. **Behebung:** Knapper Hinweis in `planung_gesamt.md` ergänzt (2026-06-11).

### 4.2 Spannung 2 — `phase4_planung.md`: `tests/integration/`-Phasenzuordnung

`phase4_planung.md` nennt in der Zielstruktur 8 Integration-Test-Dateien. Tatsächlich
enthält `tests/integration/` 16 Dateien, darunter `test_user_accounts.py`,
`test_init_db.py` und `test_device_event_booking.py`, die nach dem Phase-4-Abschluss
ergänzt wurden. Phasenzuordnung der drei zusätzlichen Dateien:

- `test_user_accounts.py` — Phase 5 (users-Modul)
- `test_init_db.py` — Phase 4+ (`setup_vollstaendig()`-Erweiterung)
- `test_device_event_booking.py` — Phase 4 nachgezogen (Commit `0f20931`, 2026-06-11)

**Behebung:** Keine Änderung an `phase4_planung.md` — die Zählung 165 ist korrekt.
Detaillierte Phasenzuordnung in `docs/betrieb/nachweise/nachtragsmatrix_phasen_v1.md`.

### 4.3 Spannung 3 — `phase5_planung.md`: historische und heutige Testzählstände

Z.257 mischte historischen Stand (361) und heutigen Stand (395) ohne Labels.
Z.375 enthielt die überholte Schätzung `~8 Tests` für `test_supplement_flow.py`.
**Behebung durch mittel-Aufgabe (2026-06-11):** Labels ergänzt; exakter Wert `8 Tests` gesetzt.

### 4.4 Spannung 4 — `phase2_planung.md`: V4-Bezüge-Überschrift

Z.327: Überschrift `## V4-Bezüge und organisatorische Auflagen` bei Inhalt, der
ausschließlich v5-Dokumente referenzierte.
**Behebung:** → `## V5-Bezüge und organisatorische Auflagen` (2026-06-11).

### 4.5 Spannung 5 — `tests/integration/`: Phasenzuordnung dreier Dateien

Keine Planungsdatei nennte `test_user_accounts.py`, `test_init_db.py` und
`test_device_event_booking.py` explizit. Fachlich ist die Testzählung korrekt;
es handelt sich um eine historische Zuordnungsfrage ohne inhaltliche Auswirkung.
**Behebung:** Keine Änderung. Detaillierte Zuordnung in der Nachtragsmatrix.

---

## 5. Migrationsübersicht und -einordnung

Alle 6 Dateien unter `migrations/` wurden vollständig gelesen und eingeordnet.

### 5.1 Änderungstypen

| Migration | Technisch direkt belegt | Fachlich belegt | Typ |
| --- | --- | --- | --- |
| `0001_schema.sql` | ✓ (DDL lesbar) | ✓ (Tabellenstruktur direkt) | Initialschema |
| `0002_seed_defaults.sql` | ✓ (INSERT lesbar) | ✓ (Werte direkt: Mo–Fr, Zeiten) | fachliche Erweiterung |
| `0003_cleanup_booking_status.sql` | ✓ (ALTER via Rebuild) | ✓ (SQL-Kommentar explizit) | Compliance-/Nachweisfeld |
| `0004_supplement_reject_fields_and_review_note.sql` | ✓ (ALTER via Rebuild) | ✓ (SQL-Kommentar explizit) | fachliche Erweiterung |
| `0005_time_bookings_device_event_id.sql` | ✓ (ALTER via Rebuild) | Teilweise | Vorbereitungspunkt ohne belegte operative Nutzung zum Zeitpunkt der Migration |
| `0006_system_events_application_error.sql` | ✓ (ALTER via Rebuild) | ✓ (SQL-Kommentar explizit) | technische Strukturergänzung |

### 5.2 Historische Befunde (geschlossen)

**Migration 0003 — Befund Audit P1-02:**
`0001_schema.sql` enthielt ursprünglich `POSSIBLE_BREAK_VIOLATION`,
`POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION` und `MANUAL_ENTRY`
als `BookingStatus`-Werte. Diese waren regelwerkswidrig (Regelwerk v5 §11: diese
Zustände gehören zu `ReviewCaseType`, nicht zu `BookingStatus`). `0003` hat diese
Werte aus dem CHECK-Constraint entfernt. Das initiale Schema war transient inkonsistent;
der Fehler gilt als dauerhaft dokumentiert und durch `0003` behoben.

**Migration 0005:**
Die Migration bereitet `device_event_id` im Schema vor. Die operative Nutzung
(Produktionspfad schreibt `device_events`-Records und reicht die ID durch) wurde
nachträglich mit Commit `0f20931` in `booking_loop.py` implementiert.
Einordnung als „Vorbereitungspunkt ohne belegte operative Nutzung zum Zeitpunkt
der Migration" ist korrekt und belastbar.

### 5.3 Nicht entscheidbar auf Basis der vorliegenden Artefakte

- **0001:** Kein SQL-Kommentar vorhanden. Ob einzelne Felder nachträglich anders
  konzipiert wurden als ursprünglich geplant, ist aus der Migrationsdatei allein
  nicht ableitbar.
- **0002:** Kein SQL-Kommentar vorhanden. Ob die Seed-Werte (z. B. Arbeitszeiten)
  formell abgestimmt oder provisorisch sind, ist aus dem SQL nicht entscheidbar.

---

## 6. Terminologie-Harmonisierung

**Betroffene Dateien:** `phase2_planung.md`, `phase5_planung.md`

Drei konkrete Korrekturen wurden vorgenommen (Details in Abschnitt 4). Alle
historischen Testzählstände bleiben erhalten; sie wurden nur mit klaren Labels
versehen. Keine Planungsinhalte wurden inhaltlich uminterpretiert. Historische
Phasenbezüge in `phase5_planung.md` (z. B. „Stand Phase 5/Schritt 2") wurden
nicht gelöscht.

**Empfohlenes Vorzugsvokabular** (nicht bindend, kein Änderungsbedarf am Code):
Die Terminologie-Harmonisierung hat keine weiteren verbindlichen Wortfeld-Empfehlungen
identifiziert, die über die drei oben genannten Korrekturen hinausgehen. Alle
zentralen Fachbegriffe (Zeitbuchung, Buchungsquelle, Nachtrag, Korrektur,
Prüffall) sind in Pflichtenheft v5 und Regelwerk v5 verbindlich definiert.
