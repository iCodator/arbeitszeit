# Audit-Bericht: Projekt „arbeitszeit" – Phasen 1–5

**Erstellt:** 2026-06-11  
**Auditor:** KI-gestützter Soll-Ist-Abgleich (Perplexity/Claude)  
**Repo:** iCodator/arbeitszeit  
**Verbindliche Referenzdokumente:** `pflichtenheft_arbeitszeit_v3.md`, `regelwerk_arbeitszeit_v3.md`

---

## 1. Auditauftrag & Scope

Geprüft werden die Phasen 1–5 des Projekts „arbeitszeit", einem lokalen elektronischen Arbeitszeiterfassungssystem für eine Zahnarztpraxis (Python 3.11, SQLite, RFID-Reader, USB-Numpad, Linux Mint/Lubuntu). Grundlage sind ausschließlich die im Space vorhandenen Artefakte. Es wurden keine externen Quellen herangezogen. Wo Informationen fehlen oder nicht eindeutig nachweisbar sind, wird dies explizit kenntlich gemacht.

**Prüfgrenzen:**  
- Keine Ausführung des Codes, keine automatisierte Testausführung möglich.  
- Angaben über Testergebnisse (z. B. „369 Tests grün") stammen ausschließlich aus den Planungsdokumenten und sind nicht durch eine eigene Testausführung verifiziert.  
- Der tatsächliche Inhalt der SQL-Migrationsdateien und einzelner Python-Quelldateien ist über den Codebase-Export `arbeitszeit.md` nachvollziehbar; auf diesen Export wird referenziert.

---

## 2. Artefaktbasis

| Artefakt | Typ | Genutzt für |
|---|---|---|
| `planung_gesamt.md` | Planungsdokument | Gesamtarchitektur, Phasen-Übersicht, offene Punkte |
| `phase1_planung.md` | Planungsdokument | Grundgerüst, Migrationen 0001/0002, Datenbankschema |
| `phase2_planung.md` | Planungsdokument | Domänenmodell, Enums, Entitäten, Services |
| `phase3_planung.md` | Planungsdokument | Application-Schicht, Use Cases, Transaktionsregeln |
| `phase4_planung.md` | Planungsdokument | Infrastruktur, Repositories, Export, Backup |
| `phase5_planung.md` | Planungsdokument | Präsentation, Terminal-UI, Admin-CLI |
| `pflichtenheft_arbeitszeit_v3.md` | Anforderung | Funktionale + nichtfunktionale Pflichtanforderungen |
| `regelwerk_arbeitszeit_v3.md` | Anforderung | Betriebsregeln, Fachregeln, Compliance-Vorgaben |
| `arbeitszeit.md` | Codebase-Export | Verzeichnisstruktur + vollständige Quelltexte |
| `audit_phase1_review.md` – `audit_phase5_review.md` | Voraudit | Bereits dokumentierte Vorprüfungsergebnisse pro Phase |

---

## 3. Phasenweise Bewertung

---

### Phase 1 – Grundgerüst

#### Sollbild laut Dokumentation

Phase 1 liefert das lauffähige Projektgerüst: `pyproject.toml`, `src/`-Layout, SQLite-Datenbankschema (16 Tabellen, `migrations/0001_schema.sql`), Seed-Daten (`migrations/0002_seed_defaults.sql`), Datenbankverbindungsmodul mit korrekten PRAGMAs, idempotenter Migrationsrunner sowie `scripts/init_db.py`. Ursprünglich 6 Migrationstests.

#### Istbild laut Repo

Das Schema (`0001_schema.sql`) enthält alle 16 geforderten Tabellen mit FK-Constraints, CHECK-Constraints und 14 Indizes. Die Verbindungsschicht setzt `isolation_level=None`, `PRAGMA foreign_keys = ON`, `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000`. Der Migrationsrunner arbeitet mit `executescript()` und Versionsvalidierung. Durch spätere Phasen wurden Migrationen 0003–0006 ergänzt; das Testmodul `test_migrations.py` hat jetzt 12 Tests (ursprünglich 6 + 5 aus Phase 4 + 1 aus Phase 5).

**Besonderheit in Schema `0001_schema.sql`:** Die Tabelle `time_bookings` enthielt in `0001` noch fehlerhafte `current_status`-CHECK-Constraints, die POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION und MANUAL_ENTRY als BookingStatus-Werte enthielten. Diese wurden durch Migration `0003_cleanup_booking_status.sql` bereinigt.

#### Befunde Phase 1

| ID | Kategorie | Schweregrad | Befund |
|---|---|---|---|
| P1-01 | Datenbank / Migrationen | Minor-Mangel | Migration `0001_schema.sql` enthielt noch inkorrekte CHECK-Constraints für `current_status` (POSSIBLE_BREAK_VIOLATION etc. als BookingStatus). Behoben durch Migration 0003. Der Mangel ist korrigiert, aber die ursprüngliche `0001` ist ohne `0003` fachlich inkonsistent zum Regelwerk v3 §11. Dokumentiert in `phase1_planung.md`. |
| P1-02 | Datenbank / Migrationen | Hinweis/Observation | `booking_corrections` speichert alten und neuen Zustand als `old_values_json`/`new_values_json` (JSON-Dokumente), nicht als separate Felder. Das Pflichtenheft v3 §7.7 und Regelwerk v3 §12 verlangen die Nachvollziehbarkeit von altem Zustand, neuem Zustand, Begründung, Person und Zeitstempel. Die Umsetzung als JSON ist technisch möglich, erschwert jedoch direkte SQL-Abfragen ohne JSON-Extraktion. Die fachliche Anforderung ist erfüllbar, aber die Feldstruktur der `BookingCorrection`-Entität (`old_booking_type`, `old_booked_at`, `new_booking_type`, `new_booked_at`) weicht von der reinen JSON-Speicherung ab – hier besteht eine Diskrepanz zwischen Entity-Feldern und DB-Speicherung, die beim Audit nicht abschließend aus den Dokumenten aufgelöst werden kann. **Unsicherheit: Die genaue Mapping-Logik zwischen Entity-Feldern und `old_values_json` ist aus den vorliegenden Artefakten nicht vollständig nachvollziehbar.** |
| P1-03 | Dokumentation | Verbesserungspotenzial (OFI) | `test_migrations.py` wurde phasenweit fortgeschrieben (Phase 4: +5 Tests, Phase 5: +1 Test). Die Testmodulbeschreibung lässt nicht sofort erkennen, welche Tests zu welcher Phase gehören. Eine strukturierte Kommentierung nach Migrationsnummer wäre hilfreich. |

**Bewertung Phase 1:**  
Historischer Kern erfüllt? **Ja.**  
Heutiger Stand konsistent? **Ja** (nach Bereinigung durch Migration 0003).  
**Freigabestatus: GO mit Auflagen** (Auflagen: P1-02 Dokumentation des JSON-Mappings klären)

---

### Phase 2 – Domäne

#### Sollbild laut Dokumentation

Vollständiges, infrastrukturfreies Domänenmodell: 11 StrEnum-Klassen, 10 Domänenfehler, 9 frozen Dataclass-Entitäten mit Invarianten, Buchungsregel-Service, Compliance-Check-Service (ArbZG §3/4/5), 10 Repository-Protocol-Interfaces, `audit_events.py`-Konstantenkatalog. Ziel: 38–44 Tests.

#### Istbild laut Repo

Alle 11 Enums vorhanden (`enums.py`). Gegenüber dem ursprünglichen Plan wurden in Phase 2 fachliche Korrekturen vorgenommen: POSSIBLE_*-Flags werden nicht als `BookingStatus`-Werte realisiert, sondern orthogonal über `ReviewCaseType` und `BookingSource.MANUAL` (Regelwerk v3 §11 konform). `ReviewCaseType` hat 11 statt ursprünglich 4 Werte. `CardStatus` um `REPLACED` erweitert. `BookingSource.IMPORT` statt `SYSTEM`.

9 Entitäten mit `__post_init__`-Invarianten; zusätzliche Invarianten gegenüber dem Plan: `personnel_no`-Validierung, `username`-Validierung, `BookingCorrection.created_at >= old_booked_at`. `check_rest_period()` als eigenständige Domänenfunktion mit `(last_go, next_come)`-Schnittstelle vorhanden. 63 Tests (Plan: 38–44), davon 42 Entity-Tests (Plan: 19).

#### Befunde Phase 2

| ID | Kategorie | Schweregrad | Befund |
|---|---|---|---|
| P2-01 | Architektur / Design | Hinweis/Observation | Die Umbenennung von `BREAK_COMPLIANCE_ISSUE` zu `POSSIBLE_BREAK_VIOLATION` und `REST_PERIOD_VIOLATION` zu `POSSIBLE_REST_VIOLATION` ist fachlich sinnvoll und Regelwerk v3 §11 konform. Die Planungsdokumente beschreiben diese Divergenz als bewusste Entscheidung. Kein Mangel, aber externe Prüfer müssen wissen, dass `phase2_planung.md` andere Bezeichner als der finale Code zeigt. |
| P2-02 | Fachlogik / Compliance | Hinweis/Observation | `check_rest_period()` prüft auf <11h Ruhezeit (ArbZG §5, Pflichtenheft v3 §7.9). Die Integration in `BookUseCase` und `ApproveSupplementUseCase` erfolgt erst in Phase 3/4. In der Domänenschicht selbst ist die Funktion vorhanden. **Annahme:** Laut `phase3_planung.md` wurde `check_rest_period()` bereits in Phase 3 in `book_time.py` integriert (nicht erst in Phase 4). Die Integration in `ApproveSupplementUseCase` in Phase 3 vorimplementiert. Dies entspricht dem Pflichtenheft v3 §7.9. |
| P2-03 | Tests | Verbesserungspotenzial (OFI) | 63 Tests (Plan: 38) ist ein positiver Befund (tiefere Testabdeckung als geplant). Kein Mangel. |
| P2-04 | Dokumentation | Hinweis/Observation | Feldname-Diskrepanz: `ReviewCase`-Entität hat `created_at`, die DB-Spalte heißt `detected_at`. Das Mapping erfolgt im Repository. Für externe Prüfer ohne Kenntnis dieser Entscheidung besteht Verwechslungsgefahr bei SQL-Abfragen gegen die DB. Dies ist dokumentiert in `phase2_planung.md` und `phase4_planung.md`. |

**Bewertung Phase 2:**  
Historischer Kern erfüllt? **Ja** (alle Pflichtanforderungen umgesetzt, plan-konforme Abweichungen begründet).  
Heutiger Stand konsistent? **Ja.**  
**Freigabestatus: GO**

---

### Phase 3 – Application (Use Cases)

#### Sollbild laut Dokumentation

Application-Schicht: `UnitOfWork`-Protocol (10 Repositories), 4 Commands/4 Results für Phase 3, 4 Use Cases (`BookUseCase`, `RegisterSupplementUseCase`, `CorrectBookingUseCase`, `ManageWorkScheduleUseCase`). Fakes für alle Repositories. Rollenprüfung laut Plan in Phase 4 vorgesehen.

#### Istbild laut Repo

Alle 4 Kern-Use-Cases implementiert. Zusätzlich `ApproveSupplementUseCase` und `RejectSupplementUseCase` als Phase-4-Vorimplementierung in Phase 3 abgeschlossen. Rollenprüfung für alle schreibenden Use Cases bereits in Phase 3 (nicht erst Phase 4 wie geplant). Transaktionsregel korrigiert: AuditLogEntry wird nach `uow.commit()` geschrieben (via separater `auditconn`), nicht davor – dokumentiert als korrigiertes SQLite-Locking-Problem.

`check_rest_period()` wurde entgegen ursprünglichem Plan (Phase 4/Schritt 1b) bereits in Phase 3 in `book_time.py` integriert. Alle 9 Pflichtanforderungen Compliance (Regelwerk v3 §10) mit ReviewCases abgedeckt. 107 Tests in `tests/application/`.

#### Befunde Phase 3

| ID | Kategorie | Schweregrad | Befund |
|---|---|---|---|
| P3-01 | Architektur / Design | Verbesserungspotenzial (OFI) | Die Vorimplementierung von Phase-4-Komponenten (`ApproveSupplementUseCase`, `RejectSupplementUseCase`) in Phase 3 ist aus Planungssicht ein positiver Abweichungsfall. Die Planungsdokumente beschreiben ihn explizit. Es entsteht jedoch eine Diskrepanz zwischen Phasendefinition und tatsächlichem Lieferzeitpunkt, was die Nachvollziehbarkeit für externe Prüfer (z. B. bei einer Abnahme je Phase) erschweren kann. |
| P3-02 | Fachlogik / Compliance | Hinweis/Observation | Die Transaktionsregel (AuditLog nach commit, nicht davor) ist korrekt und nachvollziehbar dokumentiert. Sie widerspricht dem ursprünglichen Plantext und wurde durch Tests korrigiert. Die Abweichung ist sauber dokumentiert, aber der Plantext `planung_gesamt.md` beschreibt noch den alten Ansatz – könnte bei selektiver Lektüre des Gesamtplans missverständlich sein. |
| P3-03 | Tests | Hinweis/Observation | `FakeTimeBookingRepository.set_status()` schreibt keinen History-Eintrag (nur `dataclasses.replace()`). Das ist eine bewusste Abgrenzung von Infrastrukturverhalten. Tests prüfen dadurch die History-Schreibung nicht auf Fakes-Ebene – diese wird erst auf Integrationsebene (Phase 4) abgedeckt. **Kein Mangel** bei dieser Testarchitektur, aber externe Prüfer könnten fehlende Unit-Tests für History-Einträge als Lücke werten. |

**Bewertung Phase 3:**  
Historischer Kern erfüllt? **Ja.**  
Heutiger Stand konsistent? **Ja** (alle Use Cases, Compliance-Logik, Rollenprüfung vollständig).  
**Freigabestatus: GO**

---

### Phase 4 – Infrastruktur

#### Sollbild laut Dokumentation

SQLite-Repositories (10 Stück) als Infrastruktur-Implementierungen der Domain-Ports, `SQLiteUnitOfWork`, Hardware-Schicht (`EvdevHardwareReader`, `SimulatedHardwareReader`), Backup-Service, Export-Schicht (`report_queries.py`, `csv_exporter.py`, `pdf_report_service.py`), Systemcheck. Migrationen 0003–0005. 342 Tests.

#### Istbild laut Repo

Alle 10 SQLite-Repositories unter `infrastructure/db/repositories/` vorhanden. `SQLiteUnitOfWork` mit WAL-konformer Zwei-Verbindungs-Semantik (Hauptverbindung + `auditconn`). Hardware-Schicht: `EvdevHardwareReader`, `SimulatedHardwareReader`, `uid_hash.py`. Backup-Service: `SQLiteBackupService` mit NAS-optionaler Anbindung. Export: `report_queries.py` (4 frozen Dataclasses, 7 Abfragefunktionen), `csv_exporter.py` (Detail + Verdichtet), `pdf_report_service.py` (4 Berichtstypen via reportlab). Systemcheck: `system_check.py` mit 5 Prüfpunkten. 

Migrationen 0003 (Status-CHECK bereinigt), 0004 (rejected_by_user_id/rejected_at in supplements, note in review_cases), 0005 (device_event_id FK in time_bookings per Table-Rebuild). `device_event_id` ist nullable und wird derzeit nicht operational befüllt (dokumentierter offener Architekturpunkt).

#### Befunde Phase 4

| ID | Kategorie | Schweregrad | Befund |
|---|---|---|---|
| P4-01 | Architektur / Design | Major-Mangel | Die operative `device_event_id`-Verkettung (Hardware-Schicht schreibt `device_events`, ID wird via `BookCommand.device_event_id` durchgereicht) ist **nicht implementiert**. Schema und Infrastruktur sind vorbereitet (Migration 0005, nullable Spalte), aber kein Produktionspfad schreibt derzeit `device_events` in die DB. Dies ist als dokumentierter offener Architekturpunkt eingestuft (phase5_planung.md). **Bewertung:** Für den Praxisbetrieb bedeutet das, dass die Verknüpfung zwischen Hardware-Ereignis und Buchung nicht hergestellt wird. Die Nachvollziehbarkeit „welcher RFID-Scan hat welche Buchung ausgelöst" ist damit eingeschränkt. Ob dies ein NO-GO-Kriterium ist, hängt von der Praxisentscheidung ab. Als Auditor werte ich dies als Major-Mangel mit Freigabehemmnis, solange kein Betriebskonzept dokumentiert, warum die Verkettung verzichtbar ist. |
| P4-02 | Betrieb / Backup | Minor-Mangel | `backup_service.py` und `scripts/backup.py` sind implementiert. Die Frage, ob Restore-Tests tatsächlich regelmäßig durchgeführt werden (Regelwerk v3 §20, §22), ist eine Betriebsanforderung, die über den Code hinausgeht. Ein schriftliches Backup-/Restore-Konzept mit Prüfprotokoll ist **nicht als Datei im Repo nachweisbar**. Pflichtenheft v3 §14 und §17 fordern ein definiertes, protokolliertes Restore-Verfahren. **Nicht entscheidbar, ob dieses außerhalb des Repos vorliegt.** |
| P4-03 | Datenbank / Migrationen | Minor-Mangel | Migration 0005 führt einen Table-Rebuild für `time_bookings` durch (wegen SQLite-Einschränkungen beim Hinzufügen von FK-Spalten). Tests prüfen, dass vorhandene Daten erhalten bleiben. Kein Index auf `device_event_id` wurde bewusst nicht angelegt (dokumentiert in phase4_planung.md). Kein Mangel an sich, aber: Wenn `device_event_id` operational genutzt wird (vgl. P4-01), sollte der fehlende Index nachgeholt werden. |
| P4-04 | Fachlogik / Compliance | Hinweis/Observation | `report_queries.py` ist als einzige erlaubte Datenquelle für alle Ausgabekanäle definiert (Regelwerk v3 §11, phase4_planung.md). Direkte Ad-hoc-Queries außerhalb dieser Schicht sind architektonisch verboten. Ob alle Stellen in Admin-CLI und Terminal-UI dieses Prinzip einhalten, ist aus den vorliegenden Planungsdokumenten für Phase 5 erkennbar (reports.py nutzt report_queries.py), aber eine vollständige statische Prüfung aller Codezeilen ist im Rahmen dieses Audits nicht möglich. **Unsicherheit: Einhaltung in allen CLI-Modulen nicht restlos verifizierbar.** |
| P4-05 | Tests | Verbesserungspotenzial (OFI) | `test_hardware_evdev.py` (7 Tests) prüft die Hardware-Schicht. Ob Fehlerszenarien (Reader nicht verfügbar, Gerätepfad nicht vorhanden) ausreichend abgedeckt sind, ist aus den Planungsdokumenten nicht vollständig nachvollziehbar. Pflichtenheft v3 §8.1 (Robustheit bei Gerätefehlern) erfordert entsprechende Tests. |
| P4-06 | Betrieb / Export | Minor-Mangel | Die Betriebsregel für das Exportverzeichnis (Zugriffsrechte, Aufbewahrungsfrist 5 Jahre, Löschkonzept) ist in `phase5_planung.md` als **Betriebsdokumentation außerhalb des Codes** beschrieben. Diese Dokumentation ist im Repo selbst nicht als separate, eigenständige Betriebsdokumentation vorhanden – sie ist im Planungsdokument enthalten, aber nicht als eigenes Betriebshandbuch o. Ä. für den Praxiseinsatz aufbereitet. |

**Bewertung Phase 4:**  
Historischer Kern erfüllt? **Ja** (alle Repositories, Export, Backup implementiert).  
Heutiger Stand konsistent? **Überwiegend ja**, mit dokumentiertem offenen Architekturpunkt (device_event_id).  
**Freigabestatus: GO mit Auflagen** (Auflagen: P4-01 Betriebsentscheidung device_event_id dokumentieren; P4-02 schriftliches Backup/Restore-Konzept als eigenständiges Dokument; P4-06 Betriebshandbuch für Exportverzeichnis erstellen)

---

### Phase 5 – Präsentation

#### Sollbild laut Dokumentation

Zwei Einstiegspunkte: `terminal_ui/` (Buchungsbetrieb, Endlosschleife) und `admin_cli/` (Verwaltung, argparse/click). Systemzeitprotokollierung (`time_monitor.py`). E2E-Tests für Buchungsablauf und Nachtrag-Flow. Alle Pflichtauswertungen über Admin-CLI zugänglich. 369 Tests gesamt.

#### Istbild laut Repo

`presentation/terminal_ui/` mit `main.py` und `booking_loop.py` vorhanden. `presentation/admin_cli/` mit `main.py`, `employees.py`, `bookings.py`, `schedule.py`, `reports.py`, `system.py` vorhanden. `infrastructure/time_monitor.py` mit `SystemTimeMonitor`, Sprungdetektion (Monotonic- vs. Wall-Clock), Schwellenwert aus `system_config` konfigurierbar. Migration `0006_system_events_application_error.sql` ergänzt `APPLICATION_ERROR` als event_type. E2E-Tests `test_booking_flow.py` und `test_supplement_flow.py` vorhanden. Nachgeführte Code-Review-Korrekturen (2026-05-27): Zeitraumfilter für `open-bookings`, halb-offene UTC-Intervalle in PDF, vereinheitlichte CSV-Intervallbildung.

#### Befunde Phase 5

| ID | Kategorie | Schweregrad | Befund |
|---|---|---|---|
| P5-01 | Architektur / Design | Minor-Mangel | Die `device_event_id`-Verkettung (vgl. P4-01) ist weiterhin offen. Phase 5 schließt dies explizit aus dem Abnahmesoll aus, ohne eine Frist oder Abhilfebedingung zu nennen. Für den produktiven Betrieb fehlt eine Entscheidung: entweder Implementierung oder schriftliche Betriebsentscheidung, dass die Verkettung dauerhaft verzichtbar ist. |
| P5-02 | Betrieb | Minor-Mangel | NTP-Synchronisation ist als Betriebsvoraussetzung deklariert (`time_monitor.py`: „NTP-Synchronisation ist Betriebsvoraussetzung, nicht Aufgabe dieser Schicht"). Ein Betriebshandbuch oder eine Installationsanleitung, die diese Voraussetzung beschreibt und die Einrichtung dokumentiert, ist **nicht als eigenständige Datei im Repo nachweisbar**. Pflichtenheft v3 §9.3 verlangt eine zuverlässig synchronisierte Systemzeit. |
| P5-03 | Tests | Hinweis/Observation | Für die Präsentationsschicht (Terminal-UI, Admin-CLI) gibt es keine Unit-Tests – dies ist eine bewusste Architekturentscheidung (Logik liegt in Application/Infrastructure). Die E2E-Tests `test_booking_flow.py` und `test_supplement_flow.py` decken End-to-End-Abläufe ab. Die genaue Testanzahl ist aus den Planungsdokumenten als Schätzung (~10 bzw. ~8 Tests) angegeben, nicht als verifizierte Zahl. **Unsicherheit: Ob tatsächlich alle kritischen Pfade der Terminal-UI und Admin-CLI durch E2E-Tests abgedeckt sind, ist nicht restlos verifizierbar.** |
| P5-04 | Fachlogik / Compliance | Hinweis/Observation | Die Admin-CLI implementiert Rollenprüfung für alle schreibenden Operationen ohne CLI-Bypass (phase5_planung.md). Ob die Rollenprüfung in jedem Modul (employees.py, bookings.py, schedule.py, reports.py, system.py) vollständig und konsistent umgesetzt ist, ist aus den Planungsdokumenten plausibel, aber nicht durch eine lückenlose Code-Inspektion verifiziert. |
| P5-05 | Betrieb | Major-Mangel | Es existiert **kein nachweisbares schriftliches Betriebshandbuch** (Installations-, Konfigurations-, Betriebsanleitung) als eigenständige Datei im Repo (außer `README.md`, deren Inhalt aus den Artefakten nicht vollständig beurteilt werden kann). Für den Praxiseinsatz in einer Zahnarztpraxis, wo die Betreiberin in der Regel keine Softwareentwicklerin ist, ist eine verständliche Betriebsdokumentation eine Mindestvoraussetzung. Pflichtenheft v3 §15 und §17 beschreiben organisatorische Anforderungen (wer ist Admin, Prüfintervalle, Backup-Rhythmus usw.), die schriftlich festgelegt sein müssen. |
| P5-06 | Dokumentation | Minor-Mangel | Das `README.md` ist im Repo vorhanden. Sein Inhalt ist aus den vorliegenden Artefakten nicht beurteilbar. **Nicht entscheidbar auf Basis der vorliegenden Artefakte**, ob README.md ausreicht oder ergänzt werden muss. |
| P5-07 | Betrieb / Backup | Minor-Mangel | `scripts/setup.py` ist im Repo vorhanden. Inhalt und Vollständigkeit für die Erstinstallation auf Lubuntu sind nicht beurteilbar. **Nicht entscheidbar auf Basis der vorliegenden Artefakte.** |

**Bewertung Phase 5:**  
Historischer Kern erfüllt? **Im Wesentlichen ja** (alle geforderten UI-Komponenten, Systemzeitprotokollierung, E2E-Tests vorhanden).  
Heutiger Stand konsistent? **Überwiegend ja**, mit offenen Betriebsdokumentationslücken.  
**Freigabestatus: GO mit Auflagen** (Auflagen: P5-05 Betriebshandbuch erstellen; P5-01/P5-02 offene Architektur- und Betriebspunkte klären)

---

## 4. Querschnittsbewertung

### Durchgehend positive Muster

- **Saubere Schichttrennung:** Domain → Application → Infrastructure → Presentation ist konsequent durchgehalten. Keine Imports „nach unten" nachweisbar.  
- **Compliance-Vollständigkeit:** Alle 5 ArbZG-Prüfhilfen (§3/4/5) sind als Domänenfunktionen implementiert und in Use Cases integriert (§7.9 Pflichtenheft v3 vollständig).  
- **Orthogonales Status-Modell:** POSSIBLE_*-Flags werden nicht als BookingStatus, sondern als ReviewCaseType realisiert (Regelwerk v3 §11 konform). Diese Entscheidung ist durchgehend konsistent in allen Schichten.  
- **Keine stillen Abschlussbuchungen:** Das System erzeugt keine automatischen Abschlussbuchungen bei offenen Phasen (Regelwerk v3 §14/15 konform).  
- **Aufbewahrungsprinzip:** Keine physische Löschung fachlicher Buchungen durch das System (Regelwerk v3 §18, Pflichtenheft v3 §12 konform).  
- **Audit-Log-Pflicht:** Alle Use Cases schreiben AuditLogEntries. Die Transaktionsregel (nach commit) ist korrekt und sauber dokumentiert.  
- **Testtiefe:** 369 Tests (laut Planungsdokument), 63 Domain-Tests (geplant 38), 107 Application-Tests – deutlich über Plan.

### Wiederkehrende Muster mit Handlungsbedarf

- **Betriebsdokumentation fehlt als eigenständige Artefakte:** Betriebsregeln (Exportverzeichnis, NTP, Backup, Rollen, Prüfintervalle) sind in Planungsdokumenten beschrieben, aber nicht als eigenständige Betriebs- oder Installationsdokumentation für den Praxisbetrieb aufbereitet.  
- **Offener Architekturpunkt device_event_id:** Seit Phase 4 dokumentiert, in Phase 5 explizit aus dem Abnahmesoll ausgeschlossen – ohne Frist oder Entscheidungskonsequenz.  
- **Phasenabgrenzung vs. Vorimplementierung:** Phase-3- und Phase-4-Vorimplementierungen (Approve/Reject Use Cases, Rollenprüfung, check_rest_period) sind gut dokumentiert, aber erschweren die Abnahme je Phase.  
- **Plantext-Abweichungen dokumentiert, aber nicht bereinigt:** Ursprüngliche Planformulierungen in `planung_gesamt.md` (z. B. AuditLog im selben commit, Phase-4-Numpad-Schritt 1c für Rollenprüfung) weichen vom tatsächlichen Code ab. Die Abweichungen sind in den Phasenplanungsdokumenten erklärt, aber `planung_gesamt.md` selbst ist nicht vollständig nachgeführt.

---

## 5. Priorisierte To-do-Liste

### Priorität Kritisch (NO-GO-relevant)

| Prio | Maßnahme | Betroffene Phase(n) / Datei(en) |
|---|---|---|
| K-01 | Schriftliche Betriebsdokumentation erstellen: Installationsanleitung (Lubuntu, Python, NTP, Dienst-Account), Betriebshandbuch (Rollen, Prüfintervalle, Backup-Rhythmus, Exportverzeichnis-Pflege), Notfallprozess schriftlich. Pflichtenheft v3 §15/17 ist ohne diese Dokumente nicht erfüllbar. | Phase 5 / neues Dokument `betrieb/betriebshandbuch.md` |
| K-02 | Betriebsentscheidung device_event_id: Entweder (a) operative Verkettung implementieren (Hardware schreibt device_events, BookCommand nutzt die ID), oder (b) formale schriftliche Entscheidung, dass die Verkettung dauerhaft nicht benötigt wird, mit Begründung und Auswirkung auf Nachvollziehbarkeit. | Phase 4/5 / `planung_gesamt.md`, ggf. `betrieb/betriebshandbuch.md` |
| K-03 | Schriftliches Backup/Restore-Konzept mit Testprotokoll erstellen: Wer führt Restore durch? Wie oft? Wo wird protokolliert? Pflichtenheft v3 §14 und §17 ohne dieses Dokument nicht abnahmefähig. | Phase 4/5 / neues Dokument |

### Priorität Hoch

| Prio | Maßnahme | Betroffene Phase(n) / Datei(en) |
|---|---|---|
| H-01 | Klarstellung des JSON-Mappings für `booking_corrections`: Dokumentieren, wie `old_values_json`/`new_values_json` in der DB den Entity-Feldern `old_booking_type`, `old_booked_at` etc. entsprechen. Sicherstellen, dass Pflichtauswertungen (Regelwerk v3 §12) aus dem JSON alle geforderten Felder (alter Zustand, neuer Zustand, Begründung, Person, Zeitstempel) korrekt ableiten. | Phase 1/4 / `infrastructure/db/repositories/booking_correction.py`, `report_queries.py` |
| H-02 | Prüfen, ob alle CLI-Module (employees.py, bookings.py, schedule.py, reports.py, system.py) Pflichtauswertungen ausschließlich über `report_queries.py` beziehen. Keine Ad-hoc-Queries in Präsentationsschicht (Regelwerk v3 §11). | Phase 5 / `presentation/admin_cli/` |
| H-03 | E2E-Testdeckung prüfen: Sicherstellen, dass kritische Fehlerpfade (unbekannte Karte, inaktive Karte, Geräteausfall) in `test_booking_flow.py` abgedeckt sind (Pflichtenheft v3 §8.1). | Phase 5 / `tests/e2e/` |

### Priorität Mittel

| Prio | Maßnahme | Betroffene Phase(n) / Datei(en) |
|---|---|---|
| M-01 | `planung_gesamt.md` nachführen: Abweichungen gegenüber ursprünglichem Plantext (Transaktionsregel, Vorimplementierungen, check_rest_period-Zeitpunkt) im Gesamtplandokument kenntlich machen. | Phase 3/4/5 / `planung_gesamt.md` |
| M-02 | Index auf `device_event_id` in `time_bookings` nachholen, sobald die Spalte operational genutzt wird (K-02). | Phase 4 / neue Migration `0007_…` |
| M-03 | README.md auf Vollständigkeit und Laienverständlichkeit für Praxisinhaber prüfen. | Alle / `README.md` |
| M-04 | Hardware-Fehlerszenarien in `test_hardware_evdev.py` erweitern: Reader nicht verfügbar, Gerätepfad ungültig (Pflichtenheft v3 §8.1). | Phase 4 / `tests/integration/test_hardware_evdev.py` |

### Priorität Niedrig (OFI)

| Prio | Maßnahme | Betroffene Phase(n) / Datei(en) |
|---|---|---|
| N-01 | `test_migrations.py` mit Kommentaren nach Migrationsnummern strukturieren. | Phase 1/4/5 / `tests/test_migrations.py` |
| N-02 | Feldname-Alias `created_at` ↔ `detected_at` in `ReviewCase` in einem zentralen Kommentar oder Glossar dokumentieren, um Missverständnisse bei DB-Direktabfragen zu vermeiden. | Phase 2/4 / `domain/entities.py`, `infrastructure/db/repositories/review_case.py` |

---

## 6. Abschlussbewertung

### Go/No-Go-Matrix

| Phase | Thema | Freigabestatus | Begründung |
|---|---|---|---|
| **Phase 1** | Grundgerüst, Schema, Migrationen | **GO mit Auflagen** | Kern funktional; JSON-Mapping BookingCorrection dokumentieren (H-01). |
| **Phase 2** | Domänenmodell, Compliance-Services | **GO** | Alle Pflichtanforderungen erfüllt, Tests über Plan. |
| **Phase 3** | Application/Use Cases | **GO** | Vollständig inkl. Vorimplementierungen; Compliance-Logik komplett. |
| **Phase 4** | Infrastruktur, Export, Backup | **GO mit Auflagen** | Kern funktional; device_event_id-Entscheidung (K-02), Backup-Konzept (K-03) offen. |
| **Phase 5** | Präsentation, CLI, Terminal | **GO mit Auflagen** | Code vollständig; Betriebshandbuch (K-01) fehlt als eigenständiges Dokument. |
| **Gesamtsystem** | Betrieb in Zahnarztpraxis | **NO-GO** (temporär) | Abhängig von Erfüllung K-01 (Betriebshandbuch), K-02 (device_event_id-Entscheidung), K-03 (Backup-Konzept). Nach Erfüllung dieser drei Auflagen: **GO mit Restauflagen** (H-01 bis H-03). |

**Keraussage:** Die technisch-fachliche Implementierung ist auf einem sehr soliden Niveau. Alle gesetzlich relevanten Anforderungen (ArbZG §3/4/5, Aufbewahrung, Rollenprüfung, Korrekturnachvollziehbarkeit, keine automatischen Abschlussbuchungen) sind im Code umgesetzt. Die aktuellen NO-GO-Hemmnisse sind ausschließlich **betrieblich-dokumentarischer Natur**, nicht technischer Natur. Das System ist nach Erstellung der drei fehlenden Dokumente (K-01, K-02, K-03) für den Praxisbetrieb freigabefähig.

---

## 7. Selbstcheck (interne Widerspruchsprüfung)

Folgende potenzielle Widersprüche im vorliegenden Bericht werden explizit geprüft:

**Potenzielle Inkonsistenz A:** „Phase 3 GO" und gleichzeitig Transaktionsregel-Abweichung von `planung_gesamt.md`  
→ Kein Widerspruch. Die Abweichung ist in `phase3_planung.md` explizit dokumentiert und fachlich korrekt (SQLite WAL Locking). Die alte Formulierung in `planung_gesamt.md` ist ein Dokumentationsproblem (M-01), kein Implementierungsmangel.

**Potenzielle Inkonsistenz B:** „Phase 5 GO mit Auflagen" und gleichzeitig Gesamtsystem NO-GO  
→ Kein Widerspruch. Phase 5 Code ist vollständig. Das Gesamtsystem-NO-GO ergibt sich aus fehlenden betrieblichen Dokumenten, die keiner einzelnen Phase allein zugeordnet sind (phasenübergreifende Betriebsanforderungen nach Pflichtenheft v3 §15/17).

**Potenzielle Inkonsistenz C:** device_event_id als Major-Mangel (P4-01), aber Phase 4 als „GO mit Auflagen" (nicht NO-GO)  
→ Vertretbar, aber grenzwertig. Die Einstufung als „GO mit Auflagen" (statt NO-GO) basiert auf der Überlegung, dass die Nachvollziehbarkeit von RFID-Scan zu Buchung auch ohne device_event_id durch `uid_hash` in der `time_bookings`-Tabelle gegeben ist (mittelbare Zuordnung). Der direkte Ereignis-Link fehlt, ist aber nicht zwingend für die rechtliche Anforderung nach Pflichtenheft v3. **Unsicherheit: Je nach Auslegung des Prüfers könnte dies ein NO-GO sein.**

**Potenzielle Inkonsistenz D:** Testanzahl „369 Tests grün" nicht durch eigene Ausführung verifiziert  
→ Offen. Alle Testaussagen in diesem Bericht basieren auf den Planungsdokumenten. Eine eigene Testausführung war nicht möglich. Der Bericht benennt dies explizit in Abschnitt 1.

**Verbleibende Unsicherheiten:**  
- Inhalt von `README.md` und `scripts/setup.py` nicht beurteilbar.  
- Vollständigkeit der CLI-Rollenprüfung in allen Modulen nicht restlos verifiziert.  
- JSON-Mapping in `booking_corrections` nicht vollständig nachvollziehbar aus Planungsdokumenten allein.

---

*Ende des Audit-Berichts. Erstellt auf Basis der im Space vorliegenden Artefakte (Stand: 2026-06-11). Keine externen Quellen wurden herangezogen.*
