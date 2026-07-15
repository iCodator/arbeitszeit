# Handbuch `arbeitszeit` – Application

**Kapitel:** 5
**Version:** 1.1
**Stand:** Juli 2026
**Quelldatei:** `docs/02_anwender/module/handbuch_application.md`

## Zweck

Die Anwendungsschicht bündelt die fachnahen Anwendungsdienste des Systems.
Im Repository ist sie unter `src/arbeitszeit/application/` angeordnet und
liegt im konfigurierten Schichtenmodell zwischen Infrastruktur und Domäne.

Aus `pyproject.toml` ist die Anwendungsschicht als eigenständiger Layer
belegt. Die Schicht dient damit als Vermittlungsebene zwischen
Benutzerschnittstellen, technischer Infrastruktur und den fachlichen
Domänenregeln.

## Einordnung im Schichtenmodell

Die in `pyproject.toml` konfigurierte Layer-Reihenfolge nennt folgende Ebenen:

- `arbeitszeit.presentation`
- `arbeitszeit.infrastructure`
- `arbeitszeit.application`
- `arbeitszeit.domain`

Daraus folgt, dass `application` als eigene strukturelle Schicht vorgesehen
ist. Sie ist im Repository nicht nur konzeptionell erwähnt, sondern als
reales Paket unter `src/arbeitszeit/application/` vorhanden.

## Paketstruktur

Aus der Repository-Struktur ist das Paket
`src/arbeitszeit/application/` eindeutig belegt. Dieses Kapitel beschreibt
es als Anwendungsbereich des Systems, ohne einzelne Unterdateien zu
behaupten, die aus dem hier gesicherten Repository-Befund nicht im Detail
verifiziert wurden.

Belegt ist jedoch seine tatsächliche Verwendung durch andere Schichten.
Sowohl die Präsentationsschicht als auch Infrastrukturbausteine greifen im
laufenden Betrieb auf fachliche Abläufe zu, die im Schichtenmodell unterhalb
von Presentation und Infrastructure, aber oberhalb der Domäne verortet sind.

## Rolle gegenüber Presentation

Die Präsentationsschicht stellt Eingaben, Befehlsparameter und den
Betriebsablauf bereit. Aus `admin_cli/main.py` und `terminal_ui/main.py` ist
ersichtlich, dass diese Einstiegspunkte fachliche Operationen nicht allein auf
Basis von Ein- und Ausgabe organisieren, sondern fachbezogene Abläufe mit
mehreren Systemschritten anstoßen.

Dazu gehören insbesondere Buchungsvorgänge, Korrektur- und
Ergänzungsprozesse, Dienstplanvorgänge, Berichte sowie Benutzer- und
Systemoperationen. Die Anwendungsschicht ist im Schichtenmodell der
naheliegende Ort für die Koordination solcher Abläufe zwischen Bedienung,
Datenzugriff und Fachlogik.

## Rolle gegenüber Domain

Die Domänenschicht enthält die fachlichen Begriffe und Regeln des Systems.
Die Anwendungsschicht steht darüber und orchestriert diese Regeln für
konkrete Anwendungsfälle.

Diese Einordnung ergibt sich aus der in `pyproject.toml` festgelegten
Abfolge der Layer. `application` ist damit keine reine Datenhaltung und auch
keine Benutzerschnittstelle, sondern die Ausführungsschicht für fachliche
Anwendungsfälle.

## Fachliche Anwendungsfälle

Aus den belegten Einstiegspunkten und Befehlsgruppen des Repositorys sind
folgende fachliche Anwendungsfelder erkennbar:

| Bereich | Belegbarer Anwendungsfall |
| --- | --- |
| Terminalbetrieb | Verarbeitung laufender Buchungen |
| Administration Mitarbeitende | Anlegen, Auflisten und Deaktivieren |
| Kartenverwaltung | Zuordnen, Ersetzen und Deaktivieren |
| Buchungsbearbeitung | Korrigieren, Ergänzen, Prüfen |
| Dienstplanung | Setzen und Anzeigen von Planwerten |
| Berichtswesen | CSV- und PDF-Exporte sowie Prüffälle |
| Benutzerverwaltung | Benutzer anlegen, Rollen ändern, aktivieren, deaktivieren |
| Systembetrieb | Setup, Backup, Systemcheck |

Diese Tabelle beschreibt bewusst nur die fachlichen Arbeitsbereiche, die aus
Befehlsnamen und Einstiegspunkten sicher ableitbar sind. Sie trifft keine
weiteren Aussagen über interne Klassennamen oder Detailimplementierungen, die
hier nicht unmittelbar belegt wurden.

## Orchestrierungsfunktion

Die Anwendungsschicht ist aus der Architektur des Repositorys als
Orchestrierungsschicht zu verstehen. Sie verbindet mehrere technische und
fachliche Schritte zu einem ausführbaren Arbeitsablauf.

Ein Beispiel dafür ist der Terminalbetrieb: Dort werden Konfiguration,
Datenbankzugriff, Hardwareanbindung, Systemprüfung, Zeitüberwachung und
Buchungsverarbeitung zusammengeführt. Die fachliche Verarbeitung des
Buchungsvorgangs selbst gehört weder zur reinen Gerätelogik noch zur bloßen
Konsolenausgabe und ist daher der Anwendungsebene fachlich zugeordnet.

## Beziehung zu Infrastruktur

Die Anwendungsschicht nutzt technische Dienste der Infrastruktur, ohne mit ihr
identisch zu sein. Dies ergibt sich bereits aus den belegten Infrastrukturteilen
für Datenbank, Konfiguration, Hardware, Export, Backup, Benachrichtigung,
Systemprüfung und Zeitüberwachung.

Die technische Durchführung dieser Funktionen liegt in `infrastructure`. Die
Anwendungsschicht verwendet solche Dienste, um daraus nutzbare
Anwendungsabläufe zu bilden.

## Beziehung zu den Repositories

Im Repository ist mit `SQLiteSystemConfigRepository` mindestens ein konkretes
Repository aus dem Datenbankbereich belegt. Dessen Verwendung in
`terminal_ui/main.py` zeigt, dass fachrelevante Konfigurationswerte nicht nur
technisch gelesen, sondern in betriebliche Anwendungsabläufe eingebunden
werden.

Dies stützt die Annahme einer vermittelnden Anwendungsschicht, ohne dass dieses
Kapitel unbelegte Aussagen über jeden einzelnen Service oder jedes Modul unter
`application/` machen muss.

## Abgrenzung

Dieses Kapitel beschreibt die Anwendungsschicht nur in dem Umfang, der aus der
Schichtenkonfiguration, der Paketstruktur und den belegten Laufzeitpfaden
sicher ableitbar ist. Es behauptet keine einzelnen Klassen, Dienste oder
Methoden im Paket `application`, solange diese aus dem hier abgesicherten
Repository-Befund nicht direkt benannt werden können.

Nicht belegt ist in diesem Kapitel eine eigenständige Benutzeroberfläche,
eine reine Persistenzschicht oder eine rein domänische Regeldefinition. Die
Anwendungsschicht ist vielmehr als fachliche Ausführungsebene zwischen diesen
Bereichen dokumentiert.
