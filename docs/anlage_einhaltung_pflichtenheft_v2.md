# Anlage Einhaltung Pflichtenheft – Projekt arbeitszeit (Version 2)

Diese Anlage dokumentiert den fachlichen und technischen Einhaltungsstand zum Pflichtenheft des Projekts **arbeitszeit**. Sie dient als nachvollziehbare Zuordnungs- und Prüfunterlage zwischen Anforderungsdokument, aktuellem Umsetzungsstand, offenen Punkten und ergänzender Betriebsverantwortung.[cite:5]

Version 2 bezieht sich auf das fortgeschriebene Pflichtenheft Version 4. Gegenüber der bisherigen Fassung wurden insbesondere die ausdrückliche arbeitschutzrechtliche Herleitung, die Klarstellung zur lokalen Verarbeitung mit verschlüsselten Backups, die Einbindung in die IT-Sicherheitsanforderungen von Zahnarztpraxen sowie die Dokumentation künftiger Erweiterbarkeit bei möglichen Wochenprüfungen ergänzt.[cite:5]

## 1. Zweck und Geltungsbereich

Diese Anlage beschreibt nicht das Soll neu, sondern ordnet die Anforderungen des Pflichtenhefts den heute bekannten technischen, dokumentarischen und organisatorischen Umsetzungsständen zu.[cite:5]

Sie umfasst:

- die fachlichen Kernanforderungen des Systems,
- den bekannten Repo- und Dokumentationsstand,
- die Abgrenzung zwischen bereits im System angelegter Umsetzung und noch organisatorisch zu regelnden Punkten,
- die Kennzeichnung offener oder nur unter Vorbehalt nachgewiesener Punkte.

Nicht Zweck dieser Anlage ist die Ersetzung von Betriebsdokumentation, Datenschutzdokumentation, Restore-Runbooks oder der organisatorischen Verantwortungszuweisung innerhalb der Praxis. Diese Unterlagen bleiben eigenständige Nachweisdokumente.

## 2. Referenzdokumente und Versionsbezug

Diese Anlage bezieht sich auf folgende fachlich maßgebliche Unterlagen:

- Pflichtenheft Projekt arbeitszeit – Version 3 als vorliegende Basisfassung im Repo-Stand.[cite:5]
- Die fortgeschriebene inhaltliche Fassung Version 4 mit Ergänzungen zu ArbSchG, IT-Sicherheitsrichtlinie, lokaler Verarbeitung, verschlüsselten Backups und möglicher Erweiterbarkeit auf Wochenprüfungen.
- Regelwerk arbeitszeit – Version 3 als Konkretisierung fachlicher Prüf- und Betriebsregeln.
- Planungs- und Auditunterlagen zum bekannten Umsetzungsstand, insbesondere Gesamtplanung und Audit Phase 5.

Soweit Anforderungen aus Version 3 unverändert fortgelten, werden sie in dieser Anlage ohne inhaltliche Neubewertung übernommen. Soweit Version 4 Anforderungen präzisiert oder erweitert, weist diese Anlage dies ausdrücklich aus.[cite:5]

## 3. Bewertungslogik

Für jede relevante Anforderung wird einer der folgenden Einhaltungsstände verwendet:

- **Erfüllt**: Anforderung ist durch Systemdesign, Codebasis oder belastbare Dokumentation nachvollziehbar abgedeckt.
- **Erfüllt mit Betriebsabhängigkeit**: Systemseitige Grundlage ist vorhanden, die rechtssichere oder vollständige Einhaltung hängt aber zusätzlich von organisatorischer Praxisfestlegung, Konfiguration oder Betriebsdokumentation ab.
- **Teilweise erfüllt**: Kernelemente sind vorhanden, aber Nachweis, Tiefe oder Randfälle sind noch nicht vollständig geschlossen.
- **Offen**: Die Anforderung ist bisher nicht belastbar erfüllt oder nur konzeptionell vorbereitet.

Diese Anlage trennt bewusst zwischen Software-Umsetzung und Praxisbetrieb. Ein im Code vorbereiteter Mechanismus ersetzt nicht automatisch eine erforderliche organisatorische Regel oder ein verabschiedetes Betriebskonzept.

## 4. Gesamtbewertung

Das Projekt **arbeitszeit** erfüllt den fachlichen Kern des Pflichtenhefts in weiten Teilen konzeptionell und technisch. Besonders stark nachgewiesen sind Datenmodell, Kernbuchungslogik, Rollenansatz, Prüfstatus, Auswertungsbasis, Exportpfade, Backup-/Restore-Technik, Systemcheck und Protokollierungsansätze.

Nicht vollständig geschlossen sind nach dem vorliegenden Auditstand vor allem betriebliche Nachweise und einzelne formale Freigabepunkte. Dazu zählen insbesondere eine vollständig verabschiedete Betriebsdokumentation zu Export, Backup, Restore und Aufbewahrung, die revisionsfeste Testzuordnung aller Muss-Szenarien sowie der ausdrücklich noch offene produktive `deviceevents`-Pfad.

Die neuen Präzisierungen aus Pflichtenheft Version 4 ändern daran nichts im negativen Sinn. Sie machen vor allem Rechtsgrundlage, Datenschutzarchitektur und Praxis-IT-Einbindung expliziter und dadurch auditfester.

## 5. Einhaltung nach Anforderungsbereichen

### 5.1 Dokumentzweck und Systemziel

Die Zielbeschreibung eines lokalen elektronischen Zeiterfassungssystems für eine Zahnarztpraxis ist durch Architektur, Dokumentation und Planungsunterlagen gedeckt. Der lokale Fokus, die Nachvollziehbarkeit, die Kennzeichnung von Auffälligkeiten und die Möglichkeit berechtigter Korrekturen sind konsistent in Pflichtenheft, Regelwerk und Umsetzungsplanung angelegt.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

### 5.2 Geltungsbereich

Der dokumentierte Zuschnitt auf Zeiterfassung, nicht aber auf Lohnabrechnung, Urlaubsplanung oder vollständige Personalverwaltung, ist klar und wird im bekannten Projektstand nicht verlassen. Die vorhandenen Komponenten betreffen Erfassung, Prüfung, Korrektur, Nachtrag, Export, Reporting und Systembetrieb, nicht jedoch Lohn- oder Urlaubslogik.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

### 5.3 Rechts- und Regelrahmen

Die Bezugnahme auf BAG-/EuGH-Rechtsprechung sowie auf das ArbZG ist sachlich tragfähig und weiterhin aktuell. Die Ergänzung um das Arbeitsschutzgesetz, insbesondere § 3 ArbSchG, ist fachlich sinnvoll, weil die Pflicht zur Arbeitszeiterfassung heute wesentlich auch arbeitsschutzrechtlich hergeleitet wird.[cite:5]

Die zusätzliche Einbindung der IT-Sicherheitsrichtlinie für Zahnarztpraxen ist ebenfalls sachgerecht. Für Zahnarztpraxen gelten seit 2026 verschärfte bzw. aktualisierte IT-Sicherheitsanforderungen, sodass die ausdrückliche Verankerung des Systems in diesem Rahmen richtig und aktuell ist.

**Bewertung:** Erfüllt mit Betriebsabhängigkeit, weil die rechtliche Einordnung dokumentiert ist, die praktische Einbindung in das Praxis-IT-Sicherheitskonzept aber organisatorisch umgesetzt und dokumentiert werden muss.

### 5.4 Nutzerrollen und Rechte

Pflichtenheft und Regelwerk verlangen eine klare Rollentrennung. Der dokumentierte Systementwurf und die Planungsunterlagen nennen die Rollen EMPLOYEE, ADMIN, REVIEWER und TECH; die Trennung wird sowohl im Datenmodell als auch in Use Cases und Admin-CLI ausdrücklich berücksichtigt.[cite:5]

Im Audit wird die Rollenlogik grundsätzlich als vorhanden bewertet, zugleich aber darauf hingewiesen, dass Unterbefehlstiefe, Testtiefe und betriebliche Rechtezuweisung sauber dokumentiert bleiben müssen. Damit ist die technische Grundstruktur vorhanden, die organisatorische Zuordnung bleibt jedoch Praxisaufgabe.

**Bewertung:** Erfüllt mit Betriebsabhängigkeit.

### 5.5 Normalablauf der Zeiterfassung

Der vorgesehene Standardablauf aus Buchungsart, RFID-Einlesen, Karten-/Benutzerprüfung, Buchungsfolgenprüfung, Speicherung und Statussetzung ist im Projektansatz konsistent beschrieben. Die Präsentationsschicht mit Terminal-UI und Buchungsschleife wurde laut Planung und Audit als vorhandener Kernpfad nachgewiesen.[cite:5]

Eine vollständige Herkunftsnachvollziehbarkeit jedes Hardware-Ereignisses bis in `timebookings.deviceeventid` ist jedoch nach Auditstand noch nicht operativ aktiviert. Deshalb ist der Kernablauf funktional vorhanden, aber die durchgehende Ereignisverkettung bleibt ein offener Architektur- und Nachweispunkt.

**Bewertung:** Teilweise erfüllt.

### 5.6 Funktionale Kernanforderungen

#### 5.6.1 Buchungsarten

Die geforderten Buchungsarten `Kommen`, `Gehen`, `Pause Start` und `Pause Ende` sind im fachlichen Modell verankert und in Datenmodell, Logik und Gerätefluss vorgesehen.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

#### 5.6.2 Erfassung von Beginn, Ende und Dauer

Das Pflichtenheft verlangt Erfassung von Arbeitsbeginn, Arbeitsende und Unterbrechungen sowie ableitbare Dauer. Diese Grundlage ist über `timebookings`, Statuslogik und die beschriebenen Export-/Auswertungswege nachvollziehbar angelegt.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

#### 5.6.3 RFID-Zuordnung

Das Datenmodell enthält RFID-Karten mit Status- und Mitarbeiterbezug. Regelwerk, Hardware-/Anwendungslogik und Review-Case-Typen für unbekannte oder inaktive Karten bilden den geforderten Umgang mit nicht gültigen Karten sachgerecht ab.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

#### 5.6.4 Plausibilitätsprüfung

Die Erkennung unplausibler Buchungsfolgen ist fachlich vorgesehen und wird im Review-Case-Modell sowie in den Domänen- und Use-Case-Beschreibungen verankert. Das Audit beschreibt die Kernlogik als fachlich stimmig, auch wenn nicht jede Randfalltiefe allein aus dem Export revisionsfest ableitbar ist.[cite:5]

**Bewertung:** Erfüllt mit Nachweisvorbehalt.

#### 5.6.5 Offene Buchungen

Offene Buchungen und offene Pausen sind als Status- und Auswertungskategorie vorgesehen. Das Pflichtenheft verlangt ausdrücklich, dass keine künstliche automatische Abschlussbuchung erzeugt wird; diese fachliche Richtung wird auch in Regelwerk und Auswertungslogik gestützt.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

#### 5.6.6 Prüfstatus und Kennzeichnungen

Die Statuswerte `OK`, `OPEN`, `WARN`, `NEEDS_REVIEW`, `CORRECTED` und `CLOSED_WITH_NOTE` sind im Dokumentenstand klar vorgesehen. Im Datenmodell und in der Planungsbeschreibung finden sich korrespondierende Status- und Review-Case-Strukturen für mögliche Pausen-, Ruhezeit- und Höchstarbeitszeitverstöße.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

#### 5.6.7 Korrekturen und Nachträge

Korrekturen und Nachträge sind fachlich getrennt modelliert und mit Begründung, Bearbeiterbezug und Protokollierung angelegt. Das Audit zur Application-Schicht bewertet diese Trennung ausdrücklich als sachgerecht umgesetzt; insbesondere bleibt eine Korrektur nachvollziehbar, statt die Ursprungsbuchung still zu überschreiben.[cite:5]

**Bewertung:** Erfüllt.

#### 5.6.8 Regelarbeitszeiten

Die Verwaltung von Regelarbeitszeiten ist im Datenmodell (`workscheduleversions`) und in den zugehörigen Use Cases und Repositories angelegt. Seed-Daten für die initialen Zeiten sind dokumentiert; Änderungen werden versioniert statt still überschrieben.[cite:5]

**Bewertung:** Erfüllt.

#### 5.6.9 Prüflogik Arbeitszeitgesetz

Die Tagesprüfungen zu Pausen, täglicher Arbeitszeit und Ruhezeit sind im Sollbild ausdrücklich vorhanden und werden in Planung und Testzuordnung den entsprechenden Modulen zugeordnet. Die Testabdeckung der Muss-Szenarien aus dem Pflichtenheft ist in der Gesamtplanung konkret benannt.[cite:5]

Die Ergänzung in Version 4, dass mögliche spätere Wochenprüfungen bei Gesetzesänderung ergänzt werden können, ist fachlich klug, aber derzeit noch bewusst eine Erweiterungsoption und keine Ist-Umsetzung. Solange die aktuelle ArbZG-Logik maßgeblich ist, ist diese Abgrenzung korrekt.

**Bewertung:** Erfüllt für aktuelle Tageslogik; Erweiterbarkeit auf Wochenprüfungen konzeptionell vorgesehen.

#### 5.6.10 Selbsttest

Der Selbsttest/Systemcheck ist als eigener Infrastrukturbaustein dokumentiert und deckt Konfiguration, Geräteverfügbarkeit, NAS-Erreichbarkeit, Datenbankzugriff und Grundkonsistenz ab. Planung und Audit sehen diesen Teil als im Wesentlichen umgesetzt an.[cite:5]

**Bewertung:** Erfüllt mit betrieblichem Nachweisvorbehalt für reales Warn-/Fehlerverhalten auf Zielhardware.

#### 5.6.11 Export

CSV- und PDF-Auswertungen, Zeiträume, Zuordnung, Kennzeichnung von Korrekturen/Nachträgen und Einbeziehung in das Schutz- und Backup-Konzept sind konzeptionell detailliert beschrieben. Die Exportarchitektur über zentrale Report-Queries wird in der Planung strukturiert und im Audit grundsätzlich bestätigt.[cite:5]

Offen bleibt jedoch laut Audit die vollständig verabschiedete betriebliche Dokumentation zu Exportverzeichnis, Rechten, Aufbewahrung und Löschung. Dadurch ist die technische Basis vorhanden, die formale Betriebsfreigabe aber noch nicht vollständig nachgewiesen.

**Bewertung:** Erfüllt mit Betriebsabhängigkeit.

#### 5.6.12 Pflichtauswertungen

Das Pflichtenheft fordert gezielte Pflichtauswertungen für offene Buchungen/Pausen, Korrekturen, Nachträge, Pausen-, Ruhezeit- und Höchstarbeitszeitverstöße, Regelzeitfenster-Verstöße sowie Warn-/Prüfstatus-Fälle. Die Planung ordnet diese Kategorien konkreten Query-, CSV- und App-Report-Pfaden zu.[cite:5]

Das Audit bestätigt, dass Pflichtauswertungen in der Anwendung grundsätzlich vorgesehen und weitgehend umgesetzt sind, weist aber darauf hin, dass die revisionsfeste Nachweisführung der ausschließlichen Nutzung zentraler Report-Queries und die vollständige Testtiefe noch besser belegt werden sollten.

**Bewertung:** Teilweise erfüllt mit guter technischer Grundlage.

### 5.7 Nichtfunktionale Anforderungen

#### 5.7.1 Robustheit, Nachvollziehbarkeit, Resilienz

Transaktionssicherheit, Rollback-Semantik, Audit-Log, Systemereignisse, Backup/Restore und Wiederanlauf sind in Planung und Audit mehrfach als zentrale Architekturprinzipien beschrieben. Besonders die spätere Korrektur des Musters „commit vor Audit-Write“ wird offen dokumentiert und erhöht die reale Robustheit der SQLite-basierten Architektur.

**Bewertung:** Erfüllt mit dokumentierten Restpunkten zur formalen Nachweisführung.

#### 5.7.2 Datensparsamkeit

Die Dokumente verfolgen eine datensparsame Lösung mit arbeitszeitbezogenen Beschäftigtendaten, ohne biometrische Verfahren oder unnötige Zusatzdomänen. Diese Ausrichtung ist mit DSGVO/BDSG vereinbar und durch den lokalen Systemansatz zusätzlich plausibel gestützt.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

### 5.8 Technische Anforderungen

#### 5.8.1 Plattform und Komponenten

Python, SQLite, RFID-Reader, USB-Numpad, `evdev`, Linux-Terminal und optionale NAS-Anbindung entsprechen dem dokumentierten Soll und der bekannten Architektur. Diese technische Grundausrichtung ist konsistent.[cite:5]

**Bewertung:** Erfüllt.[cite:5]

#### 5.8.2 Systemzeit

Die Anforderung zur protokollierten Erkennung von Zeitsprüngen wurde im späteren Projektstand ausdrücklich aufgegriffen. Planung und Audit nennen `timemonitor.py`, Eventtypen für Zeitabweichungen und zugehörige Tests; die grundsätzliche Abdeckung des Themas ist damit dokumentiert.[cite:5]

**Bewertung:** Erfüllt mit Nachweisvorbehalt für vollständige Grenzfalltiefe.

#### 5.8.3 Energieverhalten

Das Energieverhalten ist im Pflichtenheft beschrieben, in den vorliegenden Code- und Auditunterlagen aber nicht als gesondert tief verifizierter Punkt dokumentiert. Es handelt sich stark um einen Betriebs- und Systemkonfigurationspunkt des Terminalgeräts.[cite:5]

**Bewertung:** Erfüllt mit Betriebsabhängigkeit.[cite:5]

### 5.9 Datenmodell

Das geforderte Datenmodell ist sehr weitgehend nachweisbar. Tabellen für Benutzer, RFID-Karten, Buchungen, Korrekturen, Nachträge, Prüffälle, Regelarbeitszeiten, Systemkonfiguration und Audit-Log sind im dokumentierten Schema vorhanden; zusätzlich existieren systemevents und weitere Hilfsstrukturen.[cite:5]

**Bewertung:** Erfüllt.

### 5.10 Datenschutz und Zugriffsschutz

Die Fortentwicklung auf Version 4 mit ausdrücklicher Festlegung „produktive Verarbeitung ausschließlich lokal“ ist datenschutzrechtlich sinnvoll. Sie passt zum bisherigen Architekturansatz und reduziert die Komplexität gegenüber einem produktiven Cloud-Betrieb.

Die ergänzte Beschreibung verschlüsselter Backups lokal und optional in der Cloud ist ebenfalls tragfähig, wenn die Cloud nur als Backup-Medium dient, clientseitig verschlüsselt wird und der Anbieter bei externer Speicherung als Auftragsverarbeiter eingebunden ist. Diese Klarstellung ist richtig, ersetzt aber nicht die separate Datenschutz- und Betriebsdokumentation der Praxis.

Der aktuelle Auditstand zeigt zugleich, dass Export-, Backup-, Aufbewahrungs- und Restore-Prozesse betrieblich noch schriftlich fertiggestellt werden müssen. Daher ist dieser Bereich fachlich gut vorbereitet, aber nicht allein durch Code erledigt.

**Bewertung:** Erfüllt mit deutlicher Betriebsabhängigkeit.

### 5.11 Aufbewahrung, Archivierung und Löschung

Die Mindestaufbewahrung von 2 Jahren ist im Pflichtenheft benannt. Das Prinzip, fachlich relevante Buchungen nicht physisch zu löschen, sondern über Status- und Korrekturmechanismen nachvollziehbar zu behandeln, ist fachlich sauber und mit dem restlichen Systemansatz konsistent.[cite:5]

Die neue Präzisierung eines Rotationskonzepts für Backups ist sachgerecht, weil auch Backup-Bestände datenschutzrechtlich in Lösch- und Speicherbegrenzungsüberlegungen einbezogen werden müssen. Hier besteht aber ausdrücklich noch Bedarf an betrieblicher Konkretisierung in Form eines verabschiedeten Konzepts.

**Bewertung:** Erfüllt mit Betriebsabhängigkeit.

### 5.12 Fallback, Notfallbetrieb, Backup und Restore

Notfallnachtrag, Backup, Restore und Restore-Test sind in Planung und Testarchitektur angelegt. Das Audit hebt aber hervor, dass die operative Betriebsdokumentation zu Restore-Verfahren und Freigabe noch als eigenständiger Nachweis geschlossen werden muss.[cite:5]

**Bewertung:** Teilweise erfüllt.

### 5.13 Organisatorische Anforderungen

Das Pflichtenheft verlangt zu Recht verbindliche Festlegungen zu Rollen, Freigaben, Prüffrequenzen, Backup-Tests und inzwischen auch zur Einbindung in das Praxis-IT-Sicherheitskonzept. Genau diese Punkte sind typischerweise nicht im Code, sondern in Praxisorganisation und Betriebsunterlagen zu regeln.[cite:5]

**Bewertung:** Offen auf organisatorischer Ebene, obwohl das System hierfür geeignete technische Anknüpfungspunkte bereitstellt.

### 5.14 Testanforderungen und Abnahmekriterien

Die Gesamtplanung enthält eine explizite Zuordnung der Muss-Szenarien aus dem Pflichtenheft zu Testmodulen. Das ist ein starker Nachweis für die fachliche Testausrichtung.

Gleichzeitig fordert das Audit eine revisionsfeste Testmatrix, weil Dateipräsenz und Plantext allein für eine harte formale Abnahme noch nicht in jedem Punkt ausreichen. Diese Einschätzung ist plausibel und sollte übernommen werden.

**Bewertung:** Teilweise erfüllt.

## 6. Spezifische Ergänzungen aus Pflichtenheft Version 4

### 6.1 ArbSchG als ausdrückliche Grundlage

Die ergänzte ausdrückliche Bezugnahme auf § 3 ArbSchG verbessert die rechtliche Begründung des Systems. Sie führt nicht zu neuen technischen Muss-Funktionen, stärkt aber die juristische Herleitung der bereits vorgesehenen objektiven Zeiterfassung.

**Einhaltungsstand:** Dokumentarisch erfüllt.

### 6.2 Lokale Verarbeitung und verschlüsselte Backups

Die Klarstellung, dass die produktive Verarbeitung ausschließlich lokal erfolgt und die Cloud nur optional als verschlüsseltes Backup-Medium genutzt wird, ist mit der dokumentierten Architektur vereinbar. Für die vollständige Einhaltung sind jedoch AV-Vertrag, Schlüsselverwaltung, Serverstandortprüfung und Backup-Rotationskonzept außerhalb des Codes zu dokumentieren.

**Einhaltungsstand:** Erfüllt mit Betriebsabhängigkeit.

### 6.3 Einbindung in IT-Sicherheitskonzept der Zahnarztpraxis

Die ausdrückliche Verknüpfung mit der IT-Sicherheitsrichtlinie für Zahnarztpraxen ist fachlich richtig. Der bekannte Repo-Stand liefert Bausteine wie Rollen, Backup, Systemcheck und Protokollierung, die Einbindung in das formale Praxis-IT-Sicherheitskonzept bleibt aber organisatorische Aufgabe.

**Einhaltungsstand:** Erfüllt mit Betriebsabhängigkeit.

### 6.4 Künftige Wochenprüfungen

Die in Version 4 beschriebene mögliche Erweiterbarkeit um Wochenprüfungen ist derzeit bewusst eine Zukunftsoption. Die aktuelle Einhaltung bezieht sich auf die heute maßgeblichen Tagesgrenzen und Ruhezeiten nach ArbZG.

**Einhaltungsstand:** Für die aktuelle Rechtslage erfüllt; Erweiterungsoption offen, aber nicht defizitär.

## 7. Offene Punkte und Auflagen

Auf Basis der vorliegenden Audit- und Planungsunterlagen bestehen insbesondere folgende noch zu schließende Punkte:

- Schriftlich verabschiedete Betriebsdokumentation zu Exportverzeichnis, Dateirechten, Aufbewahrung, Löschregeln, Backup und Restore.
- Revisionsfeste Testmatrix, die Muss-Anforderungen und Abnahmekriterien direkt einzelnen Tests zuordnet.
- Entscheidung oder vollständige Umsetzung des produktiven `deviceevents`-/`deviceeventid`-Pfads für lückenlose Ereignisherkunft.
- Organisatorische Zuordnung von Rollen, Freigabeverantwortungen, Prüfintervallen und IT-Sicherheitsverantwortlichkeiten in der Praxis.[cite:5]
- Datenschutz- und Backup-Unterlagen der Praxis für AV-Vertrag, Schlüsselverwaltung, Speicherort, Rotationskonzept und Restore-Freigabe.

Diese Punkte relativieren nicht den vorhandenen Projektfortschritt, sind aber für formale Freigabe und spätere Revisionssicherheit wesentlich.

## 8. Schlussbewertung

Das Projekt **arbeitszeit** ist in Bezug auf das Pflichtenheft fachlich deutlich fortgeschritten und in vielen Kernpunkten bereits belastbar angelegt oder umgesetzt. Die größten verbleibenden Risiken liegen weniger in der Grundarchitektur als in der sauberen Schließung von Betriebs-, Test- und Freigabenachweisen.

Die Fortschreibung des Pflichtenhefts auf Version 4 macht die Dokumentation rechtlich und organisatorisch präziser. Deshalb ist es sachgerecht, auch diese Anlage auf Version 2 fortzuschreiben und die neuen Punkte ausdrücklich als dokumentierte Erweiterungen zu kennzeichnen.

## 9. Versionshistorie

- **Version 2 (2026-06-10):** Vollständige Fortschreibung auf Basis des fortentwickelten Pflichtenhefts Version 4; Ergänzungen zu ArbSchG, lokaler Verarbeitung, verschlüsselten Backups lokal/Cloud, IT-Sicherheitsrichtlinie für Zahnarztpraxen und konzeptioneller Erweiterbarkeit auf Wochenprüfungen.
- **Version 1:** Frühere Zuordnungsfassung zur Pflichtenheft-Version 3.[cite:4][cite:5]
