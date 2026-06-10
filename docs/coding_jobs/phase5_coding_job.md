# Programmieraufgabe Phase 5 – arbeitszeit

## Quellenbasis

Diese Aufgabe basiert auf den Dateien `phase5_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

## Ziel

Implementiere **ausschließlich Phase 5** des Projekts `arbeitszeit`. Phase 5 umfasst die **Präsentations- und Betriebsschicht**: Terminal-UI, Admin-CLI, den Zeitmonitor als Betriebsprozess, die betriebsnahe Integration der Hardware-Leseschicht sowie belastbare E2E-Tests für das Gesamtsystem. Diese Zieldefinition folgt aus `phase5_planung_konkret.md` und `planung_gesamt.md`.

Die Aufgabe ist erfolgreich abgeschlossen, wenn der technisch bereits vorhandene Kern aus Phase 1 bis 4 zu einem bedienbaren und betreibbaren Gesamtsystem zusammengeführt wird, ohne offene organisatorische Nachweise fälschlich als durch Code erledigt darzustellen. Diese Abgrenzung ergibt sich aus `phase5_planung_konkret.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

## Strikte Grenzen

Arbeite streng innerhalb dieses Umfangs. **Nicht** Teil dieser Aufgabe sind insbesondere:

- initiale Migrations- und DB-Grundlagen aus Phase 1,
- reine Domänenmodellierung aus Phase 2,
- isolierte Application-Orchestrierung aus Phase 3,
- grundlegende Infrastrukturimplementierungen aus Phase 4, soweit sie bereits vorhanden sind,
- organisatorische Dokumentation oder externe Nachweise.

Diese Grenzen ergeben sich aus `phase5_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

## Verbindlicher Lieferumfang

Erzeuge oder vervollständige mindestens die folgenden Bestandteile:

- `src/arbeitszeit/presentation/terminal_ui.py`
- `src/arbeitszeit/presentation/admin_cli.py`
- `src/arbeitszeit/presentation/formatters.py`
- `src/arbeitszeit/infrastructure/time_monitor.py`
- E2E-Tests für Zeitmonitor, Backup/Restore, Reports und TUI/CLI-nahe Abläufe unter `tests/e2e/`

Zusätzlich sind die in Phase 4 vorhandenen Hardware-, Export-, Backup- und Systemcheck-Dienste so einzubinden, dass daraus bedienbare Betriebsflüsse entstehen. Quellen: `phase5_planung_konkret.md`, `planung_gesamt.md`.

## Aufgabenbeschreibung

### 1. Terminal-UI implementieren

Implementiere in `presentation/terminal_ui.py` die Textoberfläche für den laufenden Buchungsbetrieb.

Pflichtumfang:
- Eingabe bzw. Empfang von RFID-Scan-Ereignissen,
- Aufruf des `BookUseCase`,
- benutzerfreundliche Anzeige von Erfolg, Warnungen und Fehlern,
- konsistente Rückmeldung zu offenen Phasen, Prüfhinweisen und Review-relevanten Situationen.

Die UI darf Ergebnisse formatieren und Flüsse steuern, aber **keine** fachliche Entscheidungslogik aus Domäne oder Application duplizieren. Quellen: `phase5_planung_konkret.md`, `planung_gesamt.md`.

### 2. Admin-CLI implementieren

Implementiere in `presentation/admin_cli.py` die administrative Kommandozeilenschnittstelle.

Die CLI muss mindestens bedienbar machen:
- Änderungen von Regelarbeitszeiten,
- Anlegen, Freigeben und Ablehnen von Nachträgen,
- Korrigieren von Buchungen,
- Auslösen von Exporten und Berichten,
- Starten von Backup/Restore und Systemcheck-nahen Funktionen.

Die CLI muss ausschließlich auf Use Cases, Exportdienste und Infrastrukturdienste aufsetzen, nicht auf direkte SQL- oder Dateisystemabkürzungen außerhalb der vorgesehenen Schnittstellen. Quellen: `phase5_planung_konkret.md`, `planung_gesamt.md`.

### 3. Formatierungsschicht implementieren

Implementiere in `presentation/formatters.py` die einheitlichen Darstellungsregeln für Terminal- und CLI-Ausgaben.

Diese Schicht muss konsistente Textrepräsentationen für Erfolg, Warnung, Fehler, Review-Hinweise und Berichtsresultate liefern, damit TUI und CLI keine divergierenden ad-hoc-Textlogiken entwickeln. Quellen: `phase5_planung_konkret.md`, `planung_gesamt.md`.

### 4. Zeitmonitor implementieren

Implementiere in `infrastructure/time_monitor.py` den betrieblichen Zeitmonitor.

Pflichtumfang:
- Vergleich von Systemzeit mit vertrauenswürdiger Referenz,
- Schwellwertprüfung für Zeitabweichungen,
- Schreiben von `TIME_DRIFT_DETECTED`-Ereignissen in `system_events`,
- testbare Kapselung des Monitorverhaltens.

Damit wird eine in `Pflichtenheft v4`, `Regelwerk v4`, `phase5_planung_konkret.md` und `planung_gesamt.md` beschriebene Anforderung technisch geschlossen.

### 5. Hardware-Pfad betrieblich anbinden

Binde die in Phase 4 vorbereitete Hardware-Leseschicht in den laufenden TUI-Betrieb ein.

Pflichtumfang:
- Kopplung von RFID-/Input-Ereignissen an die TUI,
- sauberes Fehlerhandling bei Lesefehlern,
- konsistente Weitergabe an `BookUseCase`,
- Protokollierung relevanter Gerätezustände oder Lesefehler über vorhandene Infrastrukturpfade.

Wichtig: Phase 5 darf **keine** weitergehende Vollständigkeit des `device_events`-Pfads behaupten, als `planung_gesamt.md` und `Anlage v2` tatsächlich hergeben.

### 6. Export-, Bericht- und Admin-Flows bedienbar machen

Mache die in Phase 4 implementierten Export- und Berichtsdienste über Admin-Kommandos bedienbar.

Pflichtumfang:
- Aufruf der CSV- und PDF-Erzeugung über definierte Admin-Kommandos,
- Auswahl sinnvoller Parameter für Tages-, Wochen-, Monats- und Mitarbeiterberichte,
- konsistente Rückmeldung über Zielpfade, Erfolg und Fehler.

Die fachliche Konsistenz der Berichte muss weiterhin ausschließlich auf `report_queries.py` beruhen. Die CLI darf keine eigene Ableitungslogik ergänzen. Quellen: `phase5_planung_konkret.md`, `planung_gesamt.md`, `Regelwerk v4`.

### 7. Backup/Restore- und Selbsttest-Flows bedienbar machen

Integriere die in Phase 4 vorhandenen technischen Dienste in bedienbare Admin-Flows.

Pflichtumfang:
- CLI-Kommandos zum Start von Backup, Restore und Integritätsprüfung,
- Rückmeldung über Erfolg, Fehler und relevante Audit-/Systemereignisse,
- Nutzung der vorhandenen Backup-/Systemcheck-Dienste ohne Umgehungsschicht.

Wichtig: Die Bedienbarkeit eines Backups ersetzt **nicht** die betriebliche Dokumentation von Rotation, Zuständigkeit und Datenschutz. Diese Grenzen werden in `phase5_planung_konkret.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2` ausdrücklich festgehalten.

### 8. E2E-Tests für Gesamtsystemflüsse implementieren

Erstelle belastbare E2E-Tests für die wesentlichen Gesamtsystemflüsse.

Mindestens abzudecken sind:
- Zeitmonitor,
- Backup/Restore,
- Reports,
- TUI-/CLI-nahe Abläufe.

Diese Tests müssen die Verkettung von Präsentation, Application und Infrastruktur belegen. Quellen: `phase5_planung_konkret.md`, `planung_gesamt.md`.

## Akzeptanzkriterien

Die Aufgabe ist nur dann erfüllt, wenn alle folgenden Kriterien erfüllt sind:

- Terminal-UI und Admin-CLI sind auf den vorhandenen Use Cases und Diensten aufgebaut.
- `formatters.py` sorgt für konsistente Darstellung zentraler Resultate und Fehlerbilder.
- `time_monitor.py` protokolliert Zeitabweichungen korrekt in `system_events`.
- Hardware-Eingaben sind in einen bedienbaren Betriebsfluss integriert.
- Export-, Backup-, Restore- und Systemcheck-Funktionen sind über Admin-Flows nutzbar.
- E2E-Tests decken die wesentlichen Gesamtsystempfade nachvollziehbar ab.
- Es wird keine weitergehende operative Vollständigkeit des `device_events`-Pfads behauptet, als die Planung tatsächlich belegt.
- Offene organisatorische Nachweise werden nicht als durch Code erledigt dargestellt.

Quellen: `phase5_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4`, `Anlage v2`.

## Arbeitsweise

Arbeite akribisch, konservativ und selbstkritisch.

- Ziehe keine Fachlogik in TUI oder CLI.
- Nutze ausschließlich vorhandene Use Cases und Dienste.
- Behaupte keine vollständige Schließung des `device_events`-Pfads.
- Ersetze keine organisatorischen Nachweise durch Codebehauptungen.

Diese Leitplanken folgen aus `phase5_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4` und `Anlage v2`.

## Explizite Nicht-Ziele

Folgende Dinge dürfen **nicht** umgesetzt werden:

- Umbau der Domäne oder der grundlegenden Use-Case-Architektur,
- direkte SQL- oder Dateisystemabkürzungen in TUI/CLI außerhalb vorhandener Dienste,
- neue Infrastrukturgrundlagen, die bereits in Phase 4 hätten existieren müssen,
- formale Datenschutz-, Sicherheits- oder Betriebsdokumentation,
- Behauptung einer vollständig geschlossenen `device_events`-Produktionskette, wenn diese laut Planung offen bleibt.

Quellen: `phase5_planung_konkret.md`, `planung_gesamt.md`, `Pflichtenheft v4`, `Regelwerk v4`, `Anlage v2`.

## Ergebnisformat

Liefere am Ende ausschließlich den Phase-5-Code für Präsentations-/Betriebsschicht und die zugehörigen E2E-Tests. Führe **keine** Arbeiten aus früheren Phasen neu aus und dokumentiere sauber, wo die Phase-5-Grenze bewusst eingehalten wurde. Grundlage: `phase5_planung_konkret.md`, `planung_gesamt.md`.
