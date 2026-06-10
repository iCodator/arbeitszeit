# Konkrete Planung Phase 5 – arbeitszeit

## Zweck

Dieses Dokument leitet aus der aktuellen Gesamtplanung die **konkrete Phase 5** für das Projekt `arbeitszeit` ab. Phase 5 umfasst die **Präsentations- und Betriebsschicht**: Terminal-UI, Admin-CLI, den Zeitmonitor als Betriebsprozess, betriebsnahe Integration der Hardware-Leseschicht sowie den finalen End-to-End-Nachweis des Systems. [planung_gesamt.md]

Phase 5 setzt auf den abgeschlossenen Phasen 1 bis 4 auf. Ziel ist nicht mehr das Modellieren oder grundlegende Integrieren einzelner Bausteine, sondern das kontrollierte Zusammenführen des technisch bereits vorhandenen Kerns zu einem tatsächlich bedienbaren und betreibbaren Gesamtsystem. [planung_gesamt.md]

Die Phase-5-Planung steht im Kontext der aktuellen Referenzdokumente `docs/pflichtenheft_arbeitszeit_v4.md`, `docs/regelwerk_arbeitszeit_v4.md` und `docs/anlage_einhaltung_pflichtenheft_v2.md`. Dieses Dokument beschreibt den heute gültigen fachlichen Zuschnitt von Phase 5 und grenzt ihn ausdrücklich gegen frühere Phasen sowie gegen weiterhin offene organisatorische Nachweise ab. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Zielbild Phase 5

Phase 5 liefert die **bedienbare Systemoberfläche und die betriebliche Laufzeitverkettung**. Dazu gehören die TUI für Anwender, die Admin-CLI für Administration und Reports, der kontinuierliche Systemzeitmonitor und die Orchestrierung der RFID-Eingaben bis in die Anwendungsfälle. [planung_gesamt.md]

Gleichzeitig ist Phase 5 nicht mit „alles ist endgültig vollständig“ gleichzusetzen. Die Gesamtplanung dokumentiert ausdrücklich, dass auch nach Phase 5 einzelne betriebliche und formale Nachweise offen bleiben können, etwa revisionsfeste Testmatrix, AV-Vertrag, Schlüssel-/Rotationskonzept oder formale Einbindung ins IT-Sicherheitskonzept der Praxis. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

## Verbindlicher Lieferumfang

Laut aktueller Gesamtplanung umfasst Phase 5 mindestens die folgenden Bestandteile: [planung_gesamt.md]

- `presentation/terminal_ui.py`. [planung_gesamt.md]
- `presentation/admin_cli.py`. [planung_gesamt.md]
- `presentation/formatters.py`. [planung_gesamt.md]
- `infrastructure/time_monitor.py`. [planung_gesamt.md]
- E2E-Tests für Zeitmonitor, Backup/Restore, Reports und TUI/CLI-nahe Abläufe. [planung_gesamt.md]

Die Gesamtplanung dokumentiert außerdem, dass in Phase 5 die bis dahin vorbereiteten Hardware- und Exportpfade in einen benutzbaren Betriebsfluss eingebunden werden. Das ist für die konkrete Planung zentral. [planung_gesamt.md]

## Nicht Teil von Phase 5

Die folgenden Themen gehören **nicht** zur konkreten Phase-5-Umsetzung: [planung_gesamt.md]

- initiale Migrations- und DB-Grundlagen aus Phase 1, [planung_gesamt.md]
- reine Domänenmodellierung aus Phase 2, [planung_gesamt.md]
- isolierte Application-Orchestrierung aus Phase 3, [planung_gesamt.md]
- grundlegende Infrastrukturimplementierungen aus Phase 4, soweit sie bereits vorhanden sind. [planung_gesamt.md]

Selbstkritische Abgrenzung: Phase 5 darf diese früheren Schichten nutzen und integrieren, soll sie aber nicht fachlich neu erfinden. Sobald in Phase 5 grundlegende Domänen- oder Repository-Verträge umgebaut werden müssten, wäre das ein Signal, dass frühere Phasen nicht sauber abgeschlossen waren. [planung_gesamt.md]

## Fachliche Leitplanken

Phase 5 muss die in Pflichtenheft und Regelwerk geforderte Bedien- und Kontrollierbarkeit des Systems praktisch erfahrbar machen. Dazu gehören insbesondere: [Pflichtenheft v4] [Regelwerk v4]

- klare Benutzerführung für Buchungen und Administratorfunktionen, [Pflichtenheft v4] [Regelwerk v4]
- nachvollziehbare Darstellung von Warnungen, Prüf- und Review-Fällen, [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- sichere Ausführung administrativer Operationen nur für berechtigte Benutzer, [Pflichtenheft v4] [Regelwerk v4]
- betriebliche Überwachung von Zeitabweichungen und Selbsttest-/Backup-bezogenen Systemereignissen. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]

Dabei muss die Präsentationsschicht strikt auf den bereits vorhandenen Use Cases und Exportdiensten aufsetzen. Fachlogik darf nicht in Terminal-UI oder CLI „hineindiffundieren“. [planung_gesamt.md]

## Konkrete Arbeitspakete

### 1. Terminal-UI implementieren

In `presentation/terminal_ui.py` wird die Textoberfläche für den laufenden Buchungsbetrieb umgesetzt. [planung_gesamt.md]

Die Gesamtplanung weist dieser Komponente mindestens folgende Verantwortung zu: [planung_gesamt.md]
- Eingabe bzw. Empfang von RFID-Scan-Ereignissen, [planung_gesamt.md]
- Aufruf des `BookUseCase`, [planung_gesamt.md]
- benutzerfreundliche Anzeige von Erfolg, Warnungen und Fehlern, [planung_gesamt.md]
- konsistente Rückmeldung zu offenen Phasen, Prüfhinweisen und Review-relevanten Situationen. [planung_gesamt.md]

Selbstkritische Präzisierung: Die UI darf Ergebnisse formatieren und Flüsse steuern, aber keine fachliche Entscheidungslogik duplizieren, die bereits in Domain oder Application existiert. [planung_gesamt.md]

### 2. Admin-CLI implementieren

In `presentation/admin_cli.py` wird die administrative Kommandozeilenschnittstelle umgesetzt. [planung_gesamt.md]

Laut Gesamtplanung umfasst sie insbesondere: [planung_gesamt.md]
- Änderungen von Regelarbeitszeiten, [planung_gesamt.md]
- Anlegen, Freigeben und Ablehnen von Nachträgen, [planung_gesamt.md]
- Korrigieren von Buchungen, [planung_gesamt.md]
- Auslösen von Exporten und Berichten, [planung_gesamt.md]
- Starten von Backup/Restore und Systemcheck-nahen Funktionen. [planung_gesamt.md]

Die CLI muss dabei ausschließlich auf Use Cases, Exportdienste und Infrastrukturdienste aufsetzen, nicht auf direkte SQL- oder Dateisystemabkürzungen außerhalb der vorgesehenen Schnittstellen. [planung_gesamt.md]

### 3. Formatierungsschicht implementieren

In `presentation/formatters.py` werden die einheitlichen Darstellungsregeln für Terminal- und CLI-Ausgaben umgesetzt. [planung_gesamt.md]

Diese Schicht ist wichtig, damit dieselben fachlichen Resultate konsistent und verständlich angezeigt werden, ohne dass jede Oberfläche eigene ad-hoc-Textlogik erfindet. Gerade für Warnungen, Review-Fälle, Fehlerfälle und Berichtsresultate ist diese Trennung ein Qualitätsmerkmal. [planung_gesamt.md]

### 4. Zeitmonitor implementieren

In `infrastructure/time_monitor.py` wird der betriebliche Zeitmonitor umgesetzt. [planung_gesamt.md]

Die Gesamtplanung beschreibt diesen Monitor als Phase-5-Abschluss der Zeitprotokollierung. Er prüft die Abweichung zwischen Systemzeit und einer vertrauenswürdigen Referenz und schreibt bei Schwellwertüberschreitung `TIME_DRIFT_DETECTED`-Ereignisse in `system_events`. [planung_gesamt.md]

Damit wird ein in Pflichtenheft und Regelwerk geforderter Nachweis technisch geschlossen, der in den früheren Phasen nur vorbereitet war. [Pflichtenheft v4] [Regelwerk v4]

### 5. Hardware-Pfad betrieblich anbinden

Phase 4 liefert die Hardware-Leseschicht, Phase 5 verbindet sie in einen laufenden Betriebsfluss. [planung_gesamt.md]

Die konkrete Phase-5-Planung umfasst deshalb: [planung_gesamt.md]
- Kopplung von RFID-/Input-Ereignissen an die TUI, [planung_gesamt.md]
- sauberes Fehlerhandling bei Lesefehlern, [planung_gesamt.md]
- konsistente Weitergabe an `BookUseCase`, [planung_gesamt.md]
- Protokollierung relevanter Gerätezustände oder Lesefehler über vorhandene Infrastrukturpfade. [planung_gesamt.md]

Selbstkritische Präzisierung: Die Gesamtplanung benennt weiterhin offene Punkte rund um den vollständigen produktiven `device_events`-Pfad. Phase 5 darf daher keine weitergehende Vollständigkeit behaupten, als die Gesamtplanung hergibt. [planung_gesamt.md] [Anlage v2]

### 6. Export-, Bericht- und Admin-Flows bedienbar machen

Phase 4 implementiert die Export- und Berichtsschicht technisch; Phase 5 macht sie bedienbar über CLI und administrative Abläufe. [planung_gesamt.md]

Dazu gehören insbesondere: [planung_gesamt.md]
- Aufruf der CSV- und PDF-Erzeugung über definierte Admin-Kommandos, [planung_gesamt.md]
- Auswahl sinnvoller Parameter für Tages-, Wochen-, Monats- und Mitarbeiterberichte, [planung_gesamt.md]
- konsistente Rückmeldung über Zielpfade, Erfolg und Fehler. [planung_gesamt.md]

Die fachliche Konsistenz der Berichte muss dabei weiterhin ausschließlich auf `report_queries.py` beruhen. Die CLI darf keine eigene Ableitungslogik ergänzen. [planung_gesamt.md] [Regelwerk v4]

### 7. Backup/Restore- und Selbsttest-Flows bedienbar machen

Phase 5 integriert die in Phase 4 vorhandenen technischen Dienste in bedienbare Admin-Flows. [planung_gesamt.md]

Die konkrete Planung umfasst daher: [planung_gesamt.md]
- CLI-Kommandos zum Start von Backup, Restore und Integritätsprüfung, [planung_gesamt.md]
- Rückmeldung über Erfolg, Fehler und relevante Audit-/Systemereignisse, [planung_gesamt.md]
- Nutzung der vorhandenen Backup-/Systemcheck-Dienste ohne Umgehungsschicht. [planung_gesamt.md]

Wichtig ist auch hier die Selbstkritik: Die Bedienbarkeit eines Backups ersetzt **nicht** die betriebliche Dokumentation von Rotation, Zuständigkeit und Datenschutz. Diese Punkte bleiben laut Anlage v2 offen, wenn sie außerhalb des Codes nicht nachgewiesen sind. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

### 8. E2E-Tests für Gesamtsystemflüsse implementieren

In Phase 5 werden die betriebsnahen End-to-End-Tests vervollständigt. [planung_gesamt.md]

Die Gesamtplanung nennt hier insbesondere E2E-Abdeckung für: [planung_gesamt.md]
- Zeitmonitor, [planung_gesamt.md]
- Backup/Restore, [planung_gesamt.md]
- Reports, [planung_gesamt.md]
- TUI-/CLI-nahe Abläufe. [planung_gesamt.md]

Diese Tests sind entscheidend, weil sie nicht mehr nur isolierte Komponenten, sondern die Verkettung von Präsentation, Application und Infrastruktur belegen. [planung_gesamt.md]

## Qualitätskriterien für den Phase-5-Abschluss

Phase 5 gilt erst dann als sauber abgeschlossen, wenn alle folgenden Punkte erfüllt sind: [planung_gesamt.md]

- Terminal-UI und Admin-CLI sind auf den vorhandenen Use Cases und Diensten aufgebaut. [planung_gesamt.md]
- `formatters.py` sorgt für konsistente Darstellung zentraler Resultate und Fehlerbilder. [planung_gesamt.md]
- `time_monitor.py` protokolliert Zeitabweichungen korrekt in `system_events`. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4]
- Hardware-Eingaben sind in einen bedienbaren Betriebsfluss integriert. [planung_gesamt.md]
- Export-, Backup-, Restore- und Systemcheck-Funktionen sind über Admin-Flows nutzbar. [planung_gesamt.md]
- E2E-Tests decken die wesentlichen Gesamtsystempfade nachvollziehbar ab. [planung_gesamt.md]
- Es wird keine weitergehende operative Vollständigkeit des `device_events`-Pfads behauptet, als die Gesamtplanung tatsächlich belegt. [planung_gesamt.md] [Anlage v2]

## Bekannte Risiken und Selbstkritik

Ein zentrales Risiko ist das Einziehen von Fachlogik in die Präsentationsschicht. Phase 5 darf Resultate darstellen und Flüsse auslösen, aber keine Statusregeln, Review-Logik oder Berechnungen neu definieren, die bereits in Domäne, Application oder Exportschicht festgelegt sind. [planung_gesamt.md]

Ein weiteres Risiko ist die Überschätzung des Betriebsreifegrads. Die Gesamtplanung zeigt klar, dass technische Bedienbarkeit nicht automatisch alle organisatorischen Nachweispunkte schließt. Auch nach Phase 5 können AV-Vertrag, Testmatrix, Rotationskonzept, Schlüsselverwaltung und Einbindung ins Praxis-IT-Sicherheitskonzept offen bleiben, wenn sie außerhalb des Codes nicht dokumentiert sind. [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

Ein drittes Risiko ist die falsche Darstellung des Hardwarepfads. Die Gesamtplanung beschreibt für Phase 5 die betriebliche Verkettung, hält aber zugleich offene Punkte rund um den vollständigen `device_events`-Pfad fest. Diese Spannung muss in der Planung ausdrücklich sichtbar bleiben. [planung_gesamt.md] [Anlage v2]

## Offene Punkte nach Phase 5

Auch nach Abschluss der konkreten Phase 5 können laut aktueller Gesamtplanung und Anlage v2 noch folgende Punkte offen sein: [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]

- revisionsfeste Testmatrix und vollständige Nachweisführung, [Anlage v2]
- AV-Vertrag und formale Datenschutzunterlagen, [Anlage v2]
- dokumentiertes Schlüssel-, Backup- und Rotationskonzept, [Anlage v2]
- formale Einbindung in das IT-Sicherheitskonzept der Praxis, [Anlage v2]
- vollständige betriebliche Schließung des `device_events`-Pfads, soweit dies nicht bereits außerhalb des hier beschriebenen Codeumfangs gelöst wird. [planung_gesamt.md] [Anlage v2]

## Ergebnis

Die konkrete Phase 5 ist damit klar begrenzt: **Terminal-UI, Admin-CLI, Formatierungsschicht, Zeitmonitor, betriebliche Verkettung der Hardware-Leseschicht, bedienbare Export-/Backup-/Systemcheck-Flows und belastbare E2E-Tests für das Gesamtsystem**. Genau dieses Paket macht laut aktueller Gesamtplanung aus dem technisch integrierten Kern der Phase 4 ein bedienbares und betreibbares System, ohne offene organisatorische Restpunkte zu verschweigen. [planung_gesamt.md] [Pflichtenheft v4] [Regelwerk v4] [Anlage v2]
