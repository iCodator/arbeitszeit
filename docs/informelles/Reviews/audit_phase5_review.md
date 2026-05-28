# Audit Phase 5 – Master-Audit „Präsentation und Betrieb“

## 1. Auditauftrag

### Gegenstand
Geprüft wurde der historische Sollstand von **Phase 5 – Präsentation vollständig abgeschlossen** gegen den heutigen, in `arbeitszeit.md` exportierten Repo-Stand. Grundlage sind ausschließlich die vorliegenden Repo-Artefakte und Planungsdokumente. [file:3][file:6][file:8]

### Ziel
Ziel des Audits ist ein strenger Soll-/Ist-Abgleich für Terminal-UI, Admin-CLI, Systemzeitprotokollierung, Migrationsnachtrag `0006_system_events_application_error.sql`, E2E-Abdeckung und die phasenübergreifende Freigabefähigkeit. Dabei werden historische Planerfüllung, heutige Tragfähigkeit und formale Abnahmefähigkeit getrennt bewertet. [file:3][file:6][file:8][file:9][file:7]

### Prüfmaßstab
Der historische Phase-5-Sollstand wird primär aus `planung_gesamt.md` im Abschnitt „Phase 5 – Präsentation vollständig abgeschlossen“ und aus `phase5_planung.md` hergeleitet. Fachliche Mindestanforderungen ergeben sich ergänzend aus `pflichtenheft_arbeitszeit_v3.md` und `regelwerk_arbeitszeit_v3.md`. [file:3][file:6][file:7][file:9]

### Freigabekontext
Phase 5 ist laut Planung der Schritt, in dem Präsentationsschicht und betriebsnahe Abläufe vollständig nachgewiesen sein müssen. Eine Freigabe ist deshalb nur vertretbar, wenn zentrale Bedienpfade, Reporting, Systemcheck, Zeitüberwachung und Fehlerprotokollierung nachvollziehbar zusammenpassen. [file:3][file:6][file:9]

### Grenzen der Prüfung
Das Audit basiert ausschließlich auf den vorliegenden Dateien. Aussagen zu realem Betriebsverhalten, Geräteverdrahtung, Produktivkonfiguration, organisatorischer Rollenzuweisung und tatsächlichem Restore-/NAS-Betrieb sind **nicht entscheidbar auf Basis der vorliegenden Artefakte**, soweit dafür kein belastbarer Repo-Nachweis vorliegt. [file:3][file:8][file:9]

### Muss-/Darf-nicht-Regeln
Es wurden keine stillschweigenden Harmonisierungshypothesen verwendet. Wo Planstand, Pfadbezeichnung oder Codeexport voneinander abweichen, ist der Befund explizit als Dokumentationsbruch, Ambiguität oder Abgrenzung offener Betriebspunkte ausgewiesen. [file:3][file:6][file:8]

## 2. Artefaktbasis

### Primärquellen
- `arbeitszeit.md` – aktueller Codeexport mit Verzeichnisbaum und Quellständen. [file:8]
- `planung_gesamt.md` – phasenübergreifender Implementierungsplan inkl. Phase-5-Stand. [file:6]
- `phase5_planung.md` – detaillierter Phase-5-Plan inkl. Nachträgen und Review-Korrekturen. [file:3]
- `pflichtenheft_arbeitszeit_v3.md` – fachliche und betriebliche Mindestanforderungen. [file:9]
- `regelwerk_arbeitszeit_v3.md` – verbindliche Bedien-, Prüf- und Betriebsregeln. [file:7]

### Sekundärquellen
- `phase4_planung.md` – relevante Vorbedingungen aus Phase 4, insbesondere Infrastruktur und offene Restabgrenzungen. [file:2]

### Konkret geprüfte Dateien
- `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` [file:8]
- `src/arbeitszeit/presentation/terminal_ui/main.py` [file:8]
- `src/arbeitszeit/presentation/admin_cli/_intervals.py` [file:8]
- `src/arbeitszeit/presentation/admin_cli/bookings.py` [file:8]
- `src/arbeitszeit/presentation/admin_cli/employees.py` [file:8]
- `src/arbeitszeit/presentation/admin_cli/reports.py` [file:8]
- `src/arbeitszeit/presentation/admin_cli/schedule.py` [file:8]
- `src/arbeitszeit/presentation/admin_cli/system.py` [file:8]
- `src/arbeitszeit/presentation/admin_cli/main.py` [file:8]
- `src/arbeitszeit/infrastructure/time_monitor.py` [file:8]
- `src/arbeitszeit/infrastructure/system_check.py` [file:8]
- `migrations/0006_system_events_application_error.sql` [file:8]
- `tests/e2e/test_booking_flow.py` [file:8]
- `tests/e2e/test_supplement_flow.py` [file:8]
- `tests/e2e/test_backup.py` [file:8]
- `tests/integration/test_time_monitor.py` [file:8]
- `tests/test_migrations.py` [file:8]

### Nicht prüfbare oder fehlende Artefakte
- Eine eigenständige Betriebsdokumentation zu Exportverzeichnis, Rechtekonzept für Dateisystem/NAS und Aufbewahrungs-/Löschkonzept ist in den geprüften Artefakten nicht als operative Ausführung dokumentiert. Das wird in `phase5_planung.md` selbst als nicht-code-seitiger offener Punkt benannt. [file:3][file:9][file:7]
- Ein operativer Produktionspfad, der `device_events` erzeugt und `device_event_id` durchgehend aus der Hardware-Schicht in die Buchungskette einspeist, ist laut Planung explizit noch nicht aktiviert. [file:2][file:3][file:6]

## 3. Auditmethodik

### Vorgehensweise
1. Historischen Sollstand aus `planung_gesamt.md` und `phase5_planung.md` extrahiert. [file:3][file:6]
2. Heutigen Repo-Iststand aus `arbeitszeit.md` abgeleitet. [file:8]
3. Dateiweise sowie querschnittlich gegen Pflichtenheft und Regelwerk abgeglichen. [file:7][file:8][file:9]
4. Jeden Befund einer Hauptkategorie und – falls sinnvoll – einer Nebenkategorie zugeordnet. [file:3][file:8]

### Trennung der Bewertungen
Für jedes Prüffeld wurden drei Ebenen getrennt betrachtet:
- historischer Phase-5-Planstand: erfüllt / teilweise / nicht erfüllt,
- heutiger Repo-Iststand: tragfähig / riskant / unklar,
- Freigabefähigkeit: GO / GO mit Auflagen / NO-GO. [file:3][file:6][file:8]

### Bewertungs- und Eskalationslogik
- **Abnahmesperre** bei fehlendem oder nicht belastbar belegtem Kernpfad.
- **Freigabehemmnis** bei relevanter Inkonsistenz ohne unmittelbare Kernlücke.
- **Dokumentationsbruch** bei Pfad-, Namens- oder Planbezeichnungsfehlern.
- **Nicht entscheidbar auf Basis der vorliegenden Artefakte** bei fehlendem Repo-Nachweis für Betriebs- oder Architekturfragen. [file:3][file:6][file:8]

## 4. Executive Audit Verdict

- **Historischer Phase-5-Stand:** GO unter Vorbehalt. Die geplanten Präsentationsbausteine und Nachträge sind im Repo grundsätzlich nachweisbar, aber der Sollstand ist nicht völlig planidentisch dokumentiert, weil einzelne Betriebs- und Architekturreste explizit offen bleiben. [file:3][file:6][file:8]
- **Heutiger Repo-Stand:** GO unter Vorbehalt. Fachlich und technisch wirkt der Stand tragfähig, jedoch nicht vollständig freigabesauber dokumentiert. [file:3][file:8][file:9]
- **Formale Abnahmefähigkeit:** nicht gegeben. Offene Abgrenzungen und fehlende belastbare Repo-Nachweise für bestimmte Betriebs- und E2E-Aussagen verhindern eine harte Abnahmefreigabe. [file:3][file:8][file:9]
- **Abnahmesperren vorhanden:** ja. Mindestens die nicht abschließend belegte E2E-Betriebsnähe, die offene `device_event_id`-/`device_events`-Produktivkette und die unvollständig operative Betriebsdokumentation sind freigabehemmend. [file:3][file:6][file:8][file:9]

## 5. Abnahmesperren

### SP-01
- **Befund:** Der Produktionspfad `HardwareReader -> device_events -> BookCommand.device_event_id -> time_bookings.device_event_id` ist ausdrücklich vorbereitet, aber weiterhin nicht operativ aktiviert. [file:2][file:3][file:6]
- **Warum freigabehemmend:** Phase 5 darf diesen Punkt nicht stillschweigend als abgeschlossen behandeln. Die Kette ist architektonisch relevant für vollständige Nachvollziehbarkeit von Terminalereignissen. [file:2][file:3][file:6]
- **Betroffene Artefakte:** `phase4_planung.md`, `phase5_planung.md`, `planung_gesamt.md`, mittelbar `src/arbeitszeit/infrastructure/hardware/*`, `src/arbeitszeit/presentation/terminal_ui/booking_loop.py`. [file:2][file:3][file:6][file:8]
- **Zwingende Auflösung vor Freigabe:** Entweder vollständige operative Implementierung inkl. Tests und Dokumentation oder explizite Freigabeentscheidung, dass dieser Pfad nicht zum Abnahmesoll von Phase 5 gehört. [file:2][file:3][file:6]

### SP-02
- **Befund:** Die behauptete betriebliche Reife der Präsentationsschicht stützt sich stark auf Testzählungen in der Planung, während der Codeexport selbst nur Dateipräsenz und einzelne beschriebene Testinhalte nachweist. Eine belastbare Prüfung der realen Testtiefe über alle Fehler- und Rechtepfade ist mit dem vorliegenden Export nicht vollständig möglich. [file:3][file:6][file:8]
- **Warum freigabehemmend:** Phase 5 lebt laut Planung von betriebsnahen E2E-Ketten. Wo die Artefaktlage nur teilweise Inhaltsnachweise liefert, ist eine harte Abnahme ohne ergänzenden Testbeleg nicht revisionsfest. [file:3][file:8][file:9]
- **Betroffene Artefakte:** `tests/e2e/test_booking_flow.py`, `tests/e2e/test_supplement_flow.py`, `tests/e2e/test_backup.py`, `phase5_planung.md`. [file:3][file:8]
- **Zwingende Auflösung vor Freigabe:** Vollständige testfallweise Nachweisführung oder separate Testmatrix mit Zuordnung der Muss-Szenarien zu konkreten Tests. [file:3][file:9]

### SP-03
- **Befund:** Betriebsdokumentation zu Exportverzeichnis, Rechten, Aufbewahrung und Löschkonzept bleibt laut Phase-5-Plan offen und ist in den geprüften Repo-Artefakten nicht als abgeschlossener Bestandteil nachweisbar. [file:3][file:7][file:9]
- **Warum freigabehemmend:** Pflichtenheft und Regelwerk verlangen Schutz, Archivierung und geregelten Betrieb von Exporten und Backups. Ohne dokumentierten Zielzustand ist die Phase nicht formal abnahmebereit. [file:7][file:9]
- **Betroffene Artefakte:** `phase5_planung.md`, `pflichtenheft_arbeitszeit_v3.md`, `regelwerk_arbeitszeit_v3.md`. [file:3][file:7][file:9]
- **Zwingende Auflösung vor Freigabe:** Schriftlich verabschiedete Betriebsdokumentation mit Verantwortlichkeiten, Fristen, Dateischutz und Restore-/Backup-Verfahren. [file:7][file:9]

## 6. Negativbefund-Verzeichnis

| ID | Priorität | Kategorie | Nebenkategorie | Datei / Artefakt | Soll | Ist | Abweichung | Risiko | Freigabefolge | Maßnahme |
|---|---|---|---|---|---|---|---|---|---|---|
| N-01 | A | Abnahmesperre | architekturentscheid erforderlich | `phase4_planung.md`, `phase5_planung.md`, `planung_gesamt.md` | `device_event_id`-Verkettung fachlich sauber einordnen. [file:2][file:3][file:6] | Operativer Produktionspfad ausdrücklich offen. [file:2][file:3][file:6] | Phase-5-Abschluss ist hier nicht voll operativ. | Nachvollziehbarkeit der Terminalereignisse bleibt unvollständig. | NO-GO bis zur expliziten Entscheidung. | Architekturentscheid dokumentieren oder Pfad implementieren. |
| N-02 | A | Abnahmesperre | test-seitig zu korrigieren | `tests/e2e/test_booking_flow.py`, `tests/e2e/test_supplement_flow.py`, `tests/e2e/test_backup.py` | Betriebsnahe E2E-Reife belastbar nachweisen. [file:3][file:9] | Testdateien sind vorhanden; vollständige Tiefenbewertung ist auf Basis des Exports nicht durchgängig möglich. [file:8] | Testpräsenz ist nicht gleich vollständiger Reifenachweis. | Überbewertung der Freigabereife. | NO-GO ohne belastbaren Testbeleg. | Testmatrix und Laufnachweise ergänzen. |
| N-03 | A | Abnahmesperre | betrieblich zu klären | `phase5_planung.md`, `pflichtenheft_arbeitszeit_v3.md`, `regelwerk_arbeitszeit_v3.md` | Betriebs- und Aufbewahrungskonzept abgeschlossen. [file:3][file:7][file:9] | Laut Planung noch offener Nicht-Code-Punkt. [file:3] | Formale Betriebsfreigabe unvollständig. | Compliance- und Betriebsrisiko. | NO-GO für formale Abnahme. | Betriebsdokumentation verbindlich abschließen. |
| N-04 | B | Dokumentationsbruch | plan-seitig zu korrigieren | `planung_gesamt.md` | Verbindliche Referenzdateien korrekt benennen. [file:6] | `planung_gesamt.md` verweist noch auf `docs/pflichtenheft_arbeitszeit_v3.md` und `docs/regelwerk_arbeitszeit_v3.md`, während die verbindlichen realen Dateien im Auditkontext `pflichtenheft_arbeitszeit_v3.md` und `regelwerk_arbeitszeit_v3.md` heißen. [file:6][file:7][file:9] | Pfadbenennung nicht konsistent mit realer Arbeitsgrundlage. | Fehlsteuerung bei Audits und Nacharbeit. | GO nur mit Auflage. | Planreferenzen bereinigen. |
| N-05 | B | Dokumentationsbruch | plan-seitig zu korrigieren | Prompt-/Planreferenzen zu Präsentationspfaden | Korrekte reale Pfade nennen. [file:3][file:8] | Reale Codebasis nutzt `terminal_ui`, `admin_cli`, `_intervals.py`, `time_monitor.py`, `system_check.py`, `0006_system_events_application_error.sql`. [file:8] | Frühere Schreibweisen ohne Unterstriche oder mit abweichenden Namen sind falsch. | Verwechslung von Artefakten. | GO nur mit Auflage. | Einheitliche Pfadliste etablieren. |
| N-06 | B | Schwerwiegende Ambiguität | historisch planwidrig | `phase5_planung.md`, `planung_gesamt.md`, `arbeitszeit.md` | „Phase 5 vollständig abgeschlossen“ müsste ohne relevante offene Restpunkte belegbar sein. [file:3][file:6] | Gleichzeitig bleiben `device_event_id`-Produktivpfad und Betriebsdokumentation offen. [file:3][file:6] | Abschlussformel ist stärker als die Artefaktlage. | Historische Freigabebewertung wird unscharf. | GO historisch nur unter Vorbehalt. | Abschlussformulierung präzisieren. |
| N-07 | B | Testmangel | heute fachlich riskant | `tests/integration/test_time_monitor.py`, `phase5_planung.md` | Systemzeitüberwachung belastbar gegen V3 §16 nachweisen. [file:3][file:9] | Planung nennt 8 Tests; im Export ist die Datei vorhanden, aber die vollständige Differenzierung aller Vorwärts-/Rückwärtssprünge ist nicht vollständig sichtbar. [file:3][file:8] | Vollständiger Testinhalt nicht revisionsfest aus dem Export belegbar. | Restunsicherheit bei Grenzfällen. | GO nur mit Auflage. | Testfälle explizit dokumentieren. |
| N-08 | C | Dokumentationsbruch | heute fachlich unkritisch | `phase5_planung.md`, `planung_gesamt.md` | Einheitliche Benennung der Eventtypen und Config-Keys. [file:3][file:6] | Die Plandokumente verwenden sprechende Namen wie `APPLICATION_ERROR`, `TIME_JUMP_DETECTED`, `MANUAL_TIME_CHANGE_DETECTED`, `time_monitor.jump_threshold_seconds`; reale Codepfade und Dateinamen sind zwar konsistent, aber die exakte Übereinstimmung der Literale ist im Export nur teilweise belegbar. [file:3][file:8] | Literale und Bezeichner sind nicht überall im Audit direkt nachprüfbar. | Geringes Dokumentationsrisiko. | Keine harte Sperre, aber Bereinigungsbedarf. | Konstanten-/Key-Liste dokumentieren. |
| N-09 | C | Freigabehemmnis | betrieblich zu klären | `tests/e2e/test_backup.py`, `phase5_planung.md`, `pflichtenheft_arbeitszeit_v3.md` | Restore praktisch getestet und betrieblich beschrieben. [file:3][file:9] | Testdatei ist vorhanden; operative Restore-Prozedur im Betrieb bleibt als Artefakt nicht vollständig beschrieben. [file:3][file:8] | Technischer Test und Betriebsfreigabe fallen nicht automatisch zusammen. | Fehlannahme über Betriebsreife. | GO nur mit Auflage. | Restore-Runbook ergänzen. |
| N-10 | D | Vorgezogene Erweiterung | heute fachlich unkritisch | `migrations/0006_system_events_application_error.sql`, `tests/test_migrations.py` | Phase-5-Nachtrag sauber als spätere Erweiterung auf Phase-1-Fundament führen. [file:6] | `0006` und der zusätzliche Migrationstest sind vorhanden und konsistent, aber nicht Teil früherer Phasen. [file:6][file:8] | Kein Mangel, aber klare Historisierung nötig. | Gering. | Keine Sperre. | Historische Abgrenzung in Doku beibehalten. |

## 7. Dateiweise Auditprüfung

### `src/arbeitszeit/presentation/terminal_ui/booking_loop.py`
- **Sollanforderung:** Zentraler Buchungsablauf mit `reader.read_next()`, Aufbau des `BookCommand`, Aufruf von `BookUseCase` und Rückmeldung für COME/GO/PAUSE-Fälle. [file:3][file:9][file:7]
- **Tatsächlicher Inhalt:** Die Datei ist im Export vorhanden und wird in `phase5_planung.md` ausdrücklich als Kapselung von `reader.read_next() -> BookCommand -> BookUseCase.execute()` beschrieben. [file:3][file:8]
- **Abweichungsanalyse:** Der Sollkern ist nachweisbar. Nicht nachweisbar ist allein aus dem Export, ob alle Rand- und Gerätefehlerpfade in derselben Tiefe implementiert sind, wie der Plan es suggeriert. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Vollständige Test-/Fehlerpfadbelege ergänzen. [file:3][file:8]
- **Notwendige Tests / Belege:** E2E-Matrix für COME, GO, BREAK_START, BREAK_END, unbekannte Karte, inaktive Karte, Sequenzfehler, Leserfehler. [file:3][file:7][file:9]

### `src/arbeitszeit/presentation/terminal_ui/main.py`
- **Sollanforderung:** Endlosschleife mit Start-Systemcheck, Behandlung von `DomainError`, Logging unerwarteter Exceptions in `system_events`, Graceful-Shutdown bei `SIGTERM`/`SIGINT`. [file:3][file:6][file:9]
- **Tatsächlicher Inhalt:** Die Datei ist vorhanden; `phase5_planung.md` beschreibt genau diese Integration und nennt zusätzlich den Nachtrag, dass unerwartete Laufzeitfehler als `APPLICATION_ERROR` geloggt werden. [file:3][file:8]
- **Abweichungsanalyse:** Der Planstand ist konsistent beschrieben. Die exakte Robustheit des Signalhandlings und das konkrete Weiterlaufverhalten bei unerwarteten Exceptions sind im Export nicht vollständig tiefenprüfbar. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig mit Restunsicherheit. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Explizite Testbelege für Signalpfade und Fehlerwiederanlauf bereitstellen. [file:3][file:8]
- **Notwendige Tests / Belege:** Simulation `DomainError`, unerwartete Exception, Startfehler, `SIGTERM`, `SIGINT`, Logging in `system_events`. [file:3][file:9]

### `src/arbeitszeit/presentation/admin_cli/_intervals.py`
- **Sollanforderung:** `day_interval`, `week_interval`, `month_interval` als UTC-normalisierte halb-offene Intervalle; keine ad-hoc-Grenzen in Aufrufern. [file:3][file:2]
- **Tatsächlicher Inhalt:** Reale Codebasis enthält `_intervals.py`; das entspricht der Zielstruktur von Phase 5. [file:3][file:8]
- **Abweichungsanalyse:** Inhaltlich planidentisch benannt. Frühere oder fremde Referenzen ohne Unterstrich wären falsch. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:8]
- **Freigabebewertung:** GO. [file:3][file:8]
- **Notwendige Korrektur:** Keine Codekorrektur erkennbar; nur Pfadkonsistenz in Doku sicherstellen. [file:3][file:8]
- **Notwendige Tests / Belege:** Grenzfälle für Tages-, Wochen- und Monatswechsel dokumentieren. [file:3][file:8]

### `src/arbeitszeit/presentation/admin_cli/employees.py`
- **Sollanforderung:** Mitarbeiter- und Kartenverwaltung, direkte SQL-Schreibpfade bewusst nur dort, wo kein Use Case existiert, ausschließlich für ADMIN. [file:3][file:7][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; Phase-5-Plan beschreibt direktes SQL als bewusste Entscheidung. [file:3][file:8]
- **Abweichungsanalyse:** Das ist kein Mangel, sondern dokumentierte Architekturentscheidung. Ohne Vollcodeeinsicht bleibt offen, wie strikt Rollenprüfung und Auditierung je Unterbefehl umgesetzt sind. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig, aber prüfbelegabhängig. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Unterbefehlweise Rechte-/Audit-Matrix dokumentieren. [file:3][file:9]
- **Notwendige Tests / Belege:** ADMIN erfolgreich, REVIEWER/EMPLOYEE verweigert, Kartenersatz, Deaktivierung, Reaktivierung falls vorhanden. [file:3][file:7][file:9]

### `src/arbeitszeit/presentation/admin_cli/bookings.py`
- **Sollanforderung:** Korrekturen und Nachträge ausschließlich über vorhandene Use Cases; Rollen ADMIN/REVIEWER. [file:3][file:6][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; `phase5_planung.md` beschreibt sie so. Ergänzend sind E2E-Tests für Supplement-Flow vorhanden. [file:3][file:8]
- **Abweichungsanalyse:** Kernsoll erfüllt. Die belastbare Durchgängigkeit des commit-vor-audit-Musters über alle schreibenden Use Cases wird durch Planung behauptet, aber im Export nicht in voller Codebreite verifiziert. [file:3][file:8]
- **Historische Bewertung:** erfüllt mit Vorbehalt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Nachweis je Use Case ergänzen, dass `uow.commit()` vor Auditwrite liegt oder Ablehnungspfad bewusst ausgenommen ist. [file:3][file:8]
- **Notwendige Tests / Belege:** genehmigen, ablehnen, Doppelgenehmigung, Rollenfehler, inaktiver Mitarbeiter, Audit-Überleben bei Rollback. [file:2][file:3][file:8]

### `src/arbeitszeit/presentation/admin_cli/schedule.py`
- **Sollanforderung:** Regelarbeitszeiten über `ManageWorkScheduleUseCase`, korrekte Fallback-Kommunikation GLOBAL/EMPLOYEE, Anzeige konsolidierter Scopes. [file:3][file:2][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; Planung dokumentiert Korrekturen an Tippfehlern und Fallback-Texten. [file:3][file:8]
- **Abweichungsanalyse:** Inhaltlich wirkt der Sollstand erfüllt. Ohne vollständigen Quelltext bleibt offen, ob die Anzeige wirklich alle Scope-Kombinationen robust zusammenführt. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Anzeigeverhalten bei geschlossenem EMPLOYEE-Scope und GLOBAL-Fallback explizit testbar dokumentieren. [file:2][file:3]
- **Notwendige Tests / Belege:** GLOBAL-only, EMPLOYEE überschreibt GLOBAL, EMPLOYEE geschlossen -> GLOBAL greift wieder. [file:2][file:3]

### `src/arbeitszeit/presentation/admin_cli/reports.py`
- **Sollanforderung:** Export- und In-App-Pflichtauswertungen, Filter nach Zeitraum und Mitarbeiter, ausschließlich `report_queries.py` als Wahrheitsquelle. [file:3][file:7][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; Plan nennt die fünf Auswertungskategorien, Zeitraumfilter-Nachträge und Korrekturen der Intervallbildung. [file:3][file:8]
- **Abweichungsanalyse:** Das spricht klar für Erfüllung des Plansolls. Nicht vollständig beweisbar ist anhand des Exports, ob jede Unterfunktion tatsächlich ausschließlich über `report_queries.py` arbeitet und keine Altlogikreste existieren. [file:3][file:8]
- **Historische Bewertung:** erfüllt mit Vorbehalt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig, aber dokumentarisch nachweispflichtig. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Datenquellenmatrix je Reportbefehl dokumentieren; direkte SQL-Ad-hoc-Queries ausdrücklich ausschließen oder belegen. [file:3][file:8]
- **Notwendige Tests / Belege:** `open-bookings`, `warn-cases`, `corrections`, `supplements`, `open-review-cases`; jeweils mit/ohne Zeitraumfilter und mit/ohne Mitarbeiterfilter. [file:3][file:9]

### `src/arbeitszeit/presentation/admin_cli/system.py`
- **Sollanforderung:** `admin system check` und manuelles Backup; Rollen ADMIN/TECH; konsistente Integration mit `run_system_check()` und Backup-Service. [file:3][file:7][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; Planung dokumentiert zusätzlich den Bugfix `config_value` -> `config_value_json` samt `json.loads()` und NAS-Nullwertbehandlung. [file:3][file:8]
- **Abweichungsanalyse:** Sollstand weitgehend erfüllt. Nicht vollständig entscheidbar bleibt, ob die Benutzer-Ausgabe und Fehlerklassifikation im Betrieb ausreichend robust sind. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Ergebnisdarstellung, Warn-/Fehlerklassifikation und Protokollwirkung explizit belegen. [file:3][file:9]
- **Notwendige Tests / Belege:** Systemcheck erfolgreich, Geräte fehlen, NAS fehlt, Datenbankfehler, TECH erlaubt, REVIEWER/EMPLOYEE verboten. [file:3][file:9]

### `src/arbeitszeit/presentation/admin_cli/main.py`
- **Sollanforderung:** argparse-basierter Einstiegspunkt mit `--user-id` oder `ADMIN_USER_ID`, konsistenter Befehlsstruktur. [file:3]
- **Tatsächlicher Inhalt:** Datei vorhanden und im Plan so beschrieben. [file:3][file:8]
- **Abweichungsanalyse:** Keine konkrete fachliche Abweichung erkennbar; nur Pfadkonsistenz ist relevant. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:8]
- **Freigabebewertung:** GO. [file:3][file:8]
- **Notwendige Korrektur:** Keine. [file:3][file:8]
- **Notwendige Tests / Belege:** CLI-Parsing, fehlende User-ID, Umgebungsvariablen-Fallback. [file:3]

### `src/arbeitszeit/infrastructure/time_monitor.py`
- **Sollanforderung:** Vergleich von Wall-Clock und Monotonic-Clock, Config-Key `time_monitor.jump_threshold_seconds`, Fallback 60 Sekunden, Ereignisse bei Vorwärts-/Rückwärtssprüngen, testbare injizierbare Clock-Funktionen. [file:3][file:7][file:9]
- **Tatsächlicher Inhalt:** Datei ist vorhanden; `phase5_planung.md` beschreibt genau diese Architektur. [file:3][file:8]
- **Abweichungsanalyse:** Der geplante Mechanismus ist belegbar beschrieben. Nicht abschließend belegbar ist auf Basis des Exports, ob alle Eventnamen im Schema und im Code exakt deckungsgleich sind und ob alle Grenzfälle getestet werden. [file:3][file:8]
- **Historische Bewertung:** erfüllt mit Vorbehalt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig, aber punktuell unklar. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Exakte Literale, Config-Key und Testfallabdeckung dokumentieren. [file:3][file:8]
- **Notwendige Tests / Belege:** kleiner Sprung unter Schwelle, Vorwärtssprung über Schwelle, Rückwärtssprung über Schwelle, fehlerhafte Config, Fallback 60 Sekunden, Loop-Integration vor `read_next()`. [file:3][file:9]

### `src/arbeitszeit/infrastructure/system_check.py`
- **Sollanforderung:** Selbsttest für Konfiguration, Geräte, NAS, Datenbank und Grundkonsistenz; Integration in Terminal-UI und Admin-CLI. [file:3][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; Planstand nennt sie als nachgeholte Voraussetzung aus Phase 4 und als integrierten Bestandteil von Phase 5. [file:2][file:3][file:8]
- **Abweichungsanalyse:** Der funktionale Sollstand ist beschrieben. Die genaue inhaltliche Tiefe einzelner Prüfungen ist im Export nicht vollständig rekonstruierbar. [file:3][file:8][file:9]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Prüfraster des Systemchecks ausdokumentieren. [file:3][file:9]
- **Notwendige Tests / Belege:** jede Prüfkategorie einzeln fehlgeschlagen/erfolgreich. [file:9]

### `migrations/0006_system_events_application_error.sql`
- **Sollanforderung:** Erweiterung von `system_events.eventtype` um `APPLICATION_ERROR`, damit unerwartete Terminal-UI-Fehler schema-konform geloggt werden können. [file:3][file:6]
- **Tatsächlicher Inhalt:** Migration ist in der realen Codebasis vorhanden. [file:8]
- **Abweichungsanalyse:** Dateiname und Phasenzuordnung sind konsistent. Frühere oder alternative Schreibweisen ohne Unterstriche sind falsch. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3][file:6]
- **Heutige fachliche Bewertung:** tragfähig. [file:8]
- **Freigabebewertung:** GO. [file:3][file:8]
- **Notwendige Korrektur:** Keine Implementierungskorrektur erkennbar; nur konsistente Benennung in allen Dokumenten. [file:3][file:6][file:8]
- **Notwendige Tests / Belege:** Migrationstest auf zulässigen Eventtype und Laufzeitpfadtest für unerwartete Exceptions. [file:3][file:6][file:8]

### `tests/test_migrations.py`
- **Sollanforderung:** Phase-5-Erweiterung für Migration `0006`; frühere Phase-1/4-Anteile historisch sauber getrennt. [file:6]
- **Tatsächlicher Inhalt:** Datei ist vorhanden; `planung_gesamt.md` ordnet den zusätzlichen Phase-5-Test ausdrücklich der `0006`-Erweiterung zu. [file:6][file:8]
- **Abweichungsanalyse:** Kein fachlicher Mangel. Historische Zuordnung muss explizit bleiben. [file:6][file:8]
- **Historische Bewertung:** erfüllt. [file:6]
- **Heutige fachliche Bewertung:** tragfähig. [file:8]
- **Freigabebewertung:** GO. [file:6][file:8]
- **Notwendige Korrektur:** Historische Kommentierung im Audit-/Review-Kontext fortführen. [file:6]
- **Notwendige Tests / Belege:** Nachweis, dass `APPLICATION_ERROR` vor/nach Migration unterschiedlich behandelt wird. [file:6][file:8]

### `tests/e2e/test_booking_flow.py`
- **Sollanforderung:** Vollständiger Buchungsablauf mit Simulator und echter SQLite-DB, einschließlich Ablehnung unbekannter/inaktiver Karten und Sequenzpfaden. [file:3][file:9][file:7]
- **Tatsächlicher Inhalt:** Datei ist vorhanden; Planung nennt 10 Tests mit COME→GO, COME→BREAK_START→BREAK_END→GO sowie Abweisungspfaden. [file:3][file:8]
- **Abweichungsanalyse:** Positiver Nachweis für die Kernpfade. Nicht vollständig entscheidbar ist die Abdeckung von Signal-, Geräte- und Wiederanlaufpfaden. [file:3][file:8]
- **Historische Bewertung:** erfüllt mit Vorbehalt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Explizite Auflistung aller negativen Betriebsfälle ergänzen. [file:3][file:8]
- **Notwendige Tests / Belege:** DomainError, RuntimeError, Shutdown, Zeitsprung während blockierendem Lesen. [file:3][file:9]

### `tests/e2e/test_supplement_flow.py`
- **Sollanforderung:** Nachtrag von Erfassung bis Genehmigung/Ablehnung, inklusive Rollen-, Fehler- und Statuspfade. [file:3][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; Planung nennt 8 Tests mit PENDING→APPROVED, PENDING→REJECTED, Rollenfehlern und Folgezuständen. [file:3][file:8]
- **Abweichungsanalyse:** Gute Abdeckung des Plansolls. Die Breite weiterer CLI-bezogener Befehle außerhalb des Supplementpfads bleibt dadurch nicht automatisch nachgewiesen. [file:3][file:8]
- **Historische Bewertung:** erfüllt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig. [file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Ergänzende CLI-E2E-Belege für andere Befehlsklassen dokumentieren. [file:3][file:8]
- **Notwendige Tests / Belege:** Mitarbeiterverwaltung, Reports, Systembefehle, Schedule-Befehle als durchgehende CLI-Pfade. [file:3][file:9]

### `tests/e2e/test_backup.py`
- **Sollanforderung:** Restore-Test mit echtem Backup; Phase-5-nah als betrieblicher End-to-End-Nachweis relevant. [file:3][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; bereits Phase 4 zugeordnet, aber für Phase 5 als betrieblicher Freigabenachweis weiter relevant. [file:2][file:3][file:8]
- **Abweichungsanalyse:** Kein Implementierungsmangel. Der Schritt ist jedoch nicht gleichbedeutend mit vollständiger betrieblicher Restore-Dokumentation. [file:3][file:8][file:9]
- **Historische Bewertung:** teilweise erfüllt. [file:3][file:9]
- **Heutige fachliche Bewertung:** tragfähig, aber betrieblich unvollständig dokumentiert. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Restore-Runbook und Freigabeprozess ergänzen. [file:7][file:9]
- **Notwendige Tests / Belege:** Restore unter Rollenprüfung, Restore nach Fehler, Restore inkl. Export-/Archivdateien soweit im Sicherungskonzept enthalten. [file:7][file:9]

### `tests/integration/test_time_monitor.py`
- **Sollanforderung:** Nachweis der Systemzeitprotokollierung gemäß V3 §16. [file:3][file:9]
- **Tatsächlicher Inhalt:** Datei vorhanden; Planung nennt 8 Tests. [file:3][file:8]
- **Abweichungsanalyse:** Formal vorhanden und planseitig positiv beschrieben. Vollständige Einzelfalltiefe ist im Export nicht abschließend nachvollziehbar. [file:3][file:8]
- **Historische Bewertung:** erfüllt mit Vorbehalt. [file:3]
- **Heutige fachliche Bewertung:** tragfähig mit Restunsicherheit. [file:3][file:8]
- **Freigabebewertung:** GO mit Auflagen. [file:3][file:8]
- **Notwendige Korrektur:** Testfälle und erwartete Eventtypen explizit dokumentieren. [file:3][file:8]
- **Notwendige Tests / Belege:** Vorwärtssprung, Rückwärtssprung, unter Schwellwert, fehlerhafte Konfiguration, Fallback. [file:3][file:9]

## 8. Querschnittsaudit

### Terminal-UI und Buchungsfluss
Der historische Sollstand fordert eine belastbare Terminal-UI für den realen Buchungsablauf mit Numpad-Auswahl vor RFID-Scan, fachlicher Sequenzprüfung und Fehlerbehandlung. Die Artefakte weisen `terminal_ui/booking_loop.py`, `terminal_ui/main.py` und die zugehörigen E2E-Tests nach; damit ist der Kernpfad erfüllt. [file:3][file:7][file:8][file:9]

Freigabekritisch bleibt, dass die gesamte betriebliche Robustheit der Endlosschleife, des Signalhandlings und der Fehlerwiederaufnahme nicht vollständig aus dem Export heraus nachprüfbar ist. Deshalb ist der Pfad fachlich tragfähig, aber nicht ohne Auflagen hart abnahmefähig. [file:3][file:8]

### commit-vor-audit-Korrektur
Die Planung beschreibt die Architekturkorrektur eindeutig: `uow.commit()` muss vor dem Auditwrite erfolgen, damit `audit_conn` nicht am RESERVED-Lock der Hauptverbindung blockiert. Diese Korrektur wurde laut `phase5_planung.md` auf alle schreibenden Use Cases ausgeweitet; Ablehnungspfade sind bewusst ausgenommen, weil dort keine schreibende Haupttransaktion blockiert. [file:2][file:3][file:6]

Das ist fachlich plausibel und passt zur in Phase 4 beschriebenen `audit_conn`-Architektur. Vollständig revisionsfest ist die Durchgängigkeit aber erst, wenn je Use Case ein expliziter Code- oder Testnachweis vorliegt. [file:2][file:3][file:8]

### Admin-CLI und Rollen-/Intervalllogik
Die Planungsartefakte verlangen eine argparse-basierte Admin-CLI mit klarer Rollenprüfung als erstem Schritt jeder Operation und mit `_intervals.py` als zentraler UTC-/Halboffen-Quelle. Die reale Codebasis enthält genau diese Struktur mit `admin_cli/main.py`, `_intervals.py`, `employees.py`, `bookings.py`, `schedule.py`, `reports.py` und `system.py`. [file:3][file:8][file:9]

Dokumentarisch kritisch sind nur falsche Fremdreferenzen wie `admincli` oder `intervals.py` ohne Unterstrich. Fachlich ist die Struktur stimmig; die vollständige Rechte- und Unterbefehlstiefe bleibt jedoch teilweise nur planbasiert beschrieben. [file:3][file:8]

### Pflichtauswertungen in der App
Pflichtenheft und Phase-5-Plan verlangen, dass Pflichtauswertungen nicht nur exportiert, sondern auch in der Anwendung einsehbar sind. Der Plan benennt `open-bookings`, `warn-cases`, `corrections`, `supplements` und `open-review-cases` ausdrücklich als Admin-Reports und fordert `report_queries.py` als einzige Wahrheitsquelle. [file:3][file:7][file:9]

Die reale Codebasis enthält `reports.py` und `report_queries.py`, dazu die dokumentierten Nachträge für Zeitraumfilter und halboffene Intervalle. Ein freigabefester Nachweis, dass keinerlei Ad-hoc-SQL-Reste mehr existieren, ist auf Basis des Exports aber nur eingeschränkt möglich. [file:3][file:8]

### Systemcheck im UI
Der Systemcheck ist sowohl für `admin system check` als auch für den Start der Terminal-UI vorgesehen. Diese Integration ist in Phase-5-Plan und Codeexport konsistent angelegt. [file:3][file:8][file:9]

Offen bleibt die Tiefe des betrieblichen Verhaltennachweises bei Warn- und Fehlerfällen. Das ist kein klarer Implementierungsmangel, aber ein Freigaberisiko ohne ergänzende Nachweisführung. [file:3][file:8]

### Systemzeitprotokollierung
Phase 5 schließt laut Planung die bis dahin offene Systemzeitprotokollierung ab. `time_monitor.py` und `tests/integration/test_time_monitor.py` sind vorhanden; geplant sind Vorwärts-/Rückwärtssprünge, Config-Threshold und injizierbare Clocks. [file:3][file:8][file:9]

Das erfüllt den Sollkern aus Pflichtenheft §9.3 und Regelwerk §21. Nicht abschließend entscheidbar bleibt aus dem Export heraus die Vollständigkeit der Grenzfalltests und die exakte Literaldeckung von Eventtypen und Config-Key. [file:3][file:7][file:8][file:9]

### Migrationsnachtrag 0006 / APPLICATION_ERROR
Die Migration `0006_system_events_application_error.sql` ist real vorhanden und wird in `planung_gesamt.md` ausdrücklich Phase 5 zugeordnet. Sie schließt die Schema-Lücke für unerwartete Exception-Logs der Terminal-UI. [file:6][file:8]

Hier liegt kein sichtbarer Implementierungsmangel vor. Kritisch ist nur, dass alle Dokumente denselben realen Dateinamen und denselben Eventtyp konsistent verwenden müssen. [file:3][file:6][file:8]

### Bugfix-/Code-Review-Nachträge
`phase5_planung.md` dokumentiert mehrere Nachträge: `config_value_json`, `json.loads()`, halboffene Intervalle in `report_queries.py`, normierte `day_interval()`-Nutzung in `reports.py` sowie Text-/Tippfehlerkorrekturen in `schedule.py`. Diese Nachträge passen inhaltlich zur späteren Reifephase und sind mit der realen Dateistruktur kompatibel. [file:3][file:8]

Sie sind damit eher **nachgeführte Plananpassungen** als Mängel. Revisionsfest wird der Stand erst, wenn für jede Nachkorrektur ein präziser Testbeleg oder Codeauszug referenziert wird. [file:3][file:8]

### E2E-Betriebsnähe
Der Plan behauptet für Phase 5 eine vollständige Präsentationsreife mit 369 grünen Tests und konkreten E2E-Dateien. Die Dateien `tests/e2e/test_booking_flow.py`, `tests/e2e/test_supplement_flow.py` und `tests/e2e/test_backup.py` sind real vorhanden. [file:3][file:8]

Trotzdem ist die Betriebsnähe nicht vollständig allein aus Dateipräsenz und Plantext beweisbar. Für eine harte Abnahme fehlt in den Artefakten eine testfallgenaue Freigabematrix, die alle Muss-Szenarien und Abnahmekriterien direkt auf konkrete Tests abbildet. [file:3][file:9]

### Offener `deviceeventid`-/`deviceevents`-Produktionspfad
Dieser Punkt ist explizit offen dokumentiert und darf daher nicht stillschweigend als erledigt gelten. Die Schema-/API-Vorbereitung aus Phase 4 ist vorhanden, aber die operative Verkettung durch die Hardware-Schicht ist laut Plan nicht aktiv. [file:2][file:3][file:6]

Das ist entweder ein bewusst außerhalb des Abnahmesolls liegender Restpunkt oder ein offener Architektur-/Betriebspunkt. Ohne expliziten Freigabeentscheid bleibt daraus eine Abnahmesperre. [file:2][file:3][file:6]

## 9. Nicht entscheidbare Punkte

- **Reale Robustheit des Signalhandlings in `terminal_ui/main.py`** – Grund: Der Export belegt Dateipräsenz und Planbeschreibung, aber nicht alle Laufzeitszenarien oder Testdetails. Fehlender Nachweis: vollständige Testfallinhalte. Risiko: unentdeckte Wiederanlauf- oder Shutdown-Lücken. Empfohlene Klärung: Testmatrix plus ggf. Codeauszüge. [file:3][file:8]
- **Vollständige Unterbefehlstiefe der Admin-CLI** – Grund: Die Struktur ist belegt, nicht jede Unterfunktion inhaltlich. Fehlender Nachweis: vollständige CLI-Testabdeckung je Unterbefehl. Risiko: Rechte- oder Pfadinkonsistenzen in Randfällen. Empfohlene Klärung: befehlsbezogene Testübersicht. [file:3][file:8]
- **Vollständige Literaldeckung von `TIME_JUMP_DETECTED`, `MANUAL_TIME_CHANGE_DETECTED`, `APPLICATION_ERROR` und `time_monitor.jump_threshold_seconds` im Code** – Grund: Plan nennt die Literale, Export liefert nicht überall den exakten Volltext. Fehlender Nachweis: konkrete Codezeilen/Tests. Risiko: Schema-/Runtime-Mismatch. Empfohlene Klärung: Konstantenliste mit Codebelegen. [file:3][file:8]
- **Operative NAS-/Export-Rechte, Aufbewahrungsfristen und Löschkonzept** – Grund: nicht code-seitige Betriebsdokumentation fehlt in den Artefakten. Fehlender Nachweis: verabschiedetes Betriebskonzept. Risiko: Compliance- und Betriebsrisiken. Empfohlene Klärung: schriftliche Betriebsfreigabeunterlagen. [file:3][file:7][file:9]
- **Vollständiger Produktionsbetrieb der `device_events`-Kette** – Grund: laut Planung explizit offen. Fehlender Nachweis: operativer Implementierungs- und Testbeleg. Risiko: Lücke in der Herkunftsnachvollziehbarkeit. Empfohlene Klärung: Architekturentscheid oder Umsetzung. [file:2][file:3][file:6]

## 10. Maßnahmenkatalog

1. **Freigabeentscheidung zum offenen `device_events`-Produktionspfad treffen**
   - Verantwortungsbereich: Architektur
   - betroffene Dateien: `phase4_planung.md`, `phase5_planung.md`, `planung_gesamt.md`, ggf. `src/arbeitszeit/infrastructure/hardware/evdev_reader.py`, `src/arbeitszeit/presentation/terminal_ui/booking_loop.py`
   - Zielzustand: Entweder ausdrücklich außerhalb des Phase-5-Abnahmesolls dokumentiert oder operativ vollständig umgesetzt.
   - Akzeptanzkriterien: eindeutige Entscheidung ohne Widerspruch; bei Umsetzung durchgehende ID-Kette inkl. Tests.
   - Pflichttests: Hardware→`device_events`→`BookCommand.device_event_id`→`time_bookings.device_event_id`.
   - Freigabewirkung: hebt SP-01 auf. [file:2][file:3][file:6][file:8]

2. **Revisionsfeste Testmatrix für Phase 5 erstellen**
   - Verantwortungsbereich: Tests
   - betroffene Dateien: `tests/e2e/test_booking_flow.py`, `tests/e2e/test_supplement_flow.py`, `tests/e2e/test_backup.py`, `tests/integration/test_time_monitor.py`, `tests/test_migrations.py`
   - Zielzustand: Jeder Muss-Punkt aus Phase 5, Pflichtenheft §16 und den Freigabekriterien ist einem konkreten Test zugeordnet.
   - Akzeptanzkriterien: keine unbelegte Testzählung mehr; alle Kernpfade inkl. Rechte- und Fehlerfälle direkt referenziert.
   - Pflichttests: vorhandene Tests referenzieren, fehlende Tests ergänzen.
   - Freigabewirkung: reduziert SP-02 und N-07. [file:3][file:8][file:9]

3. **Betriebsdokumentation für Export, Backup, Restore und Aufbewahrung verbindlich abschließen**
   - Verantwortungsbereich: Betrieb
   - betroffene Dateien: außerhalb des Codes; Referenz in `phase5_planung.md`, `pflichtenheft_arbeitszeit_v3.md`, `regelwerk_arbeitszeit_v3.md`
   - Zielzustand: freigegebenes Betriebskonzept mit Rechten, NAS, Exportverzeichnis, Fristen, Löschregeln und Restore-Prozess.
   - Akzeptanzkriterien: schriftlich verabschiedet, konsistent mit Pflichtenheft/Regelwerk.
   - Pflichttests: Restore-Probelauf und Backup-/Export-Schutzprüfung gegen das Runbook.
   - Freigabewirkung: hebt SP-03 auf. [file:3][file:7][file:9]

4. **Pfad- und Namenskonsistenz in allen Plan- und Reviewdokumenten bereinigen**
   - Verantwortungsbereich: Planung
   - betroffene Dateien: `planung_gesamt.md`, `phase5_planung.md`, weitere Audit-/Reviewdokumente
   - Zielzustand: nur reale Pfade und Dateinamen verwenden, z. B. `admin_cli`, `terminal_ui`, `_intervals.py`, `time_monitor.py`, `system_check.py`, `0006_system_events_application_error.sql`.
   - Akzeptanzkriterien: keine veralteten oder normalisierten Falschpfade mehr.
   - Pflichttests: Dokumentenreview gegen realen Verzeichnisbaum.
   - Freigabewirkung: beseitigt N-04 und N-05. [file:3][file:6][file:8]

5. **commit-vor-audit-Nachweis je schreibendem Use Case explizit dokumentieren**
   - Verantwortungsbereich: Code
   - betroffene Dateien: `src/arbeitszeit/application/use_cases/book_time.py`, `register_supplement.py`, `approve_supplement.py`, `reject_supplement.py`, `correct_booking.py`, `manage_work_schedule.py`
   - Zielzustand: pro Use Case nachvollziehbar dokumentiert oder getestet, wann `commit()` vor Audit erfolgt und welche Ablehnungspfade ausgenommen sind.
   - Akzeptanzkriterien: keine impliziten Annahmen mehr über Locking-Verhalten.
   - Pflichttests: SQLite-E2E/Integration mit Hauptverbindung und Auditverbindung.
   - Freigabewirkung: entschärft commit-/Locking-Ambiguität. [file:2][file:3][file:8]

6. **Reportdatenquellen und Intervallsemantik befehlsweise belegen**
   - Verantwortungsbereich: Code
   - betroffene Dateien: `src/arbeitszeit/presentation/admin_cli/reports.py`, `src/arbeitszeit/infrastructure/export/report_queries.py`, `src/arbeitszeit/infrastructure/export/pdf_report_service.py`
   - Zielzustand: für jeden Reportbefehl klare Zuordnung auf `report_queries.py` und halb-offene Intervalle.
   - Akzeptanzkriterien: keine Ad-hoc-Query-Reste; Zeitraumgrenzen konsistent.
   - Pflichttests: Filter- und Mitternachtsgrenzfälle, PDF-/CSV-Gleichlauf.
   - Freigabewirkung: reduziert Berichts-/Semantikrisiko. [file:3][file:8][file:9]

7. **Systemzeitmonitor und APPLICATION_ERROR-Logging mit Konstanten-/Schema-Matrix absichern**
   - Verantwortungsbereich: Code
   - betroffene Dateien: `src/arbeitszeit/infrastructure/time_monitor.py`, `src/arbeitszeit/presentation/terminal_ui/main.py`, `migrations/0006_system_events_application_error.sql`, `tests/integration/test_time_monitor.py`, `tests/test_migrations.py`
   - Zielzustand: exakte Deckung von Eventtypen, Config-Key und Migration dokumentiert.
   - Akzeptanzkriterien: kein möglicher Literal-Drift zwischen Planung, Schema und Laufzeitcode.
   - Pflichttests: Vorwärts-/Rückwärtssprung, Fallback-Threshold, RuntimeException→`APPLICATION_ERROR`.
   - Freigabewirkung: reduziert N-07 und N-08. [file:3][file:6][file:8]

## 11. Freigabereihenfolge

- **zuerst zwingend zu klären:** offener `device_events`-/`device_event_id`-Produktionspfad; betriebliche Dokumentationspflichten für Export/Backup/Restore/Aufbewahrung; belastbare E2E-Testmatrix. [file:2][file:3][file:6][file:7][file:9]
- **danach zwingend zu korrigieren:** Pfad- und Namenskonsistenz in den Planunterlagen; explizite Nachweise für commit-vor-audit, Reportdatenquellen und Zeitmonitor-Literale. [file:3][file:6][file:8]
- **danach dokumentarisch zu bereinigen:** Abschlussformulierungen in Phase 5 präzisieren, damit „vollständig abgeschlossen“ nicht über offene Restpunkte hinweg täuscht. [file:3][file:6]
- **danach optional zu härten:** zusätzliche E2E-Fehlerpfade für Signalhandling, Wiederanlauf, Gerätefehler und Admin-CLI-Randfälle. [file:3][file:8][file:9]

## 12. Go/No-Go-Matrix

| Prüffeld | historisch GO? | heute GO? | Freigabestatus | Restbedingung |
|---|---|---|---|---|
| Terminal-UI und Buchungsfluss | Ja, mit Vorbehalt [file:3][file:8] | Ja, mit Auflagen [file:3][file:8] | GO mit Auflagen | stärkere E2E-/Fehlerpfadbelege |
| commit-vor-audit-Korrektur | Ja, mit Vorbehalt [file:2][file:3] | Ja, mit Auflagen [file:2][file:3][file:8] | GO mit Auflagen | Use-Case-weiser Nachweis |
| Admin-CLI und Rollenlogik | Ja [file:3][file:8] | Ja, mit Auflagen [file:3][file:8] | GO mit Auflagen | Unterbefehlweise Rechte-/Auditmatrix |
| Pflichtauswertungen in der App | Ja, mit Vorbehalt [file:3][file:9] | Ja, mit Auflagen [file:3][file:8] | GO mit Auflagen | exklusive Nutzung von `report_queries.py` belegen |
| Systemcheck im UI | Ja [file:3][file:8] | Ja, mit Auflagen [file:3][file:8] | GO mit Auflagen | Fehler-/Warnverhalten explizit testen |
| Systemzeitprotokollierung | Ja, mit Vorbehalt [file:3][file:9] | Ja, mit Auflagen [file:3][file:8] | GO mit Auflagen | Literale und Grenzfälle belegen |
| Migrationsnachtrag 0006 / APPLICATION_ERROR | Ja [file:6][file:8] | Ja [file:8] | GO | konsistente Namensführung |
| E2E-Betriebsnähe gesamt | Nein, nicht voll belastbar [file:3][file:8][file:9] | Nein, nicht voll belastbar [file:3][file:8][file:9] | NO-GO | Testmatrix und Nachweisführung |
| Offener `device_event_id`-/`device_events`-Pfad | Nein [file:2][file:3][file:6] | Nein [file:2][file:3][file:6] | NO-GO | Architekturentscheid oder Umsetzung |
| Betriebsdokumentation | Nein [file:3][file:7][file:9] | Nein [file:3][file:7][file:9] | NO-GO | schriftlich abschließen |

## 13. Schlussentscheidung

- **Phase 5 historisch freigabefähig:** nein, nicht ohne Vorbehalt. Der Planstand ist weitgehend umgesetzt, aber nicht widerspruchsfrei „vollständig abgeschlossen“, solange offene Betriebspunkte und der nicht aktivierte `device_events`-Pfad parallel dokumentiert bleiben. [file:2][file:3][file:6]
- **Phase 5 im heutigen Repo-Zustand freigabefähig:** nein. Der Stand wirkt fachlich tragfähig, ist aber nicht formal freigabesauber, weil Abnahmesperren verbleiben. [file:3][file:8][file:9]
- **Freigabe nur nach Auflagen:** ja. Erforderlich sind Architekturentscheid bzw. Umsetzung zum `device_events`-Pfad, revisionsfeste Testnachweise und abgeschlossene Betriebsdokumentation. [file:2][file:3][file:7][file:9]
- **empfohlene nächste Aktion:** Rückgabe zur Nacharbeit mit Architekturentscheid und Dokumentations-/Testschließung vor formaler Abnahme. [file:2][file:3][file:8][file:9]
