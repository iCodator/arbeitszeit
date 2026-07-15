# Handbuch `arbeitszeit` – Domain

**Kapitel:** 7
**Version:** 1.1
**Stand:** Juli 2026
**Quelldatei:** `docs/02_anwender/module/handbuch_domain.md`

## Zweck

Die Domänenschicht enthält die fachliche Kernlogik des Systems. Im Repository
ist sie als eigenes Paket unter `src/arbeitszeit/domain/` vorhanden und bildet
im konfigurierten Schichtenmodell die unterste der vier Hauptschichten.

Aus der Layer-Konfiguration in `pyproject.toml` ergibt sich, dass alle höheren
Schichten letztlich auf diese fachliche Basis aufbauen. Die Domäne ist damit
kein Bedienungs- oder Infrastrukturteil, sondern der fachliche Kern des
Zeiterfassungssystems.

## Einordnung im Schichtenmodell

Die Architekturdefinition in `pyproject.toml` nennt `arbeitszeit.domain` als
letzte Ebene der vorgesehenen Layer-Reihenfolge. Oberhalb davon liegen
`application`, `infrastructure` und `presentation`.

Diese Anordnung zeigt, dass die Domäne als fachliche Grundlage dient. Andere
Schichten dürfen nach dieser Struktur auf sie aufbauen, während sie selbst
nicht als Benutzerschnittstelle oder technische Adapterebene gedacht ist.

## Paketstruktur

Das Paket `src/arbeitszeit/domain/` ist in der Repository-Struktur eindeutig
vorhanden. Seine Existenz ist daher belegt, auch wenn aus dem hier gesicherten
Befund nicht jede einzelne enthaltene Datei im Detail benannt wird.

Die Dokumentation bleibt deshalb bewusst auf gesicherte Aussagen beschränkt:
Es existiert eine eigene Domänenschicht, und sie ist architektonisch von
Presentation, Infrastructure und Application getrennt.

## Fachlicher Gegenstand

Aus dem Projektnamen, den Einstiegspunkten und den belegten Befehlsbereichen
ist ableitbar, dass sich die Domäne auf fachliche Gegenstände der
Arbeitszeiterfassung bezieht. Dazu gehören insbesondere Mitarbeitende,
Karten, Buchungen, Dienstpläne, Berichte, Benutzerrollen und
Konfigurationsbezüge mit fachlicher Relevanz.

Diese Begriffe treten im Repository in den Befehlsgruppen der Admin-CLI,
im Terminalbetrieb und in den Datenbank- und Konfigurationspfaden wiederholt
auf. Sie markieren den fachlichen Problemraum, den die Domänenschicht
abbildet.

## Rolle bei Buchungen

Der Terminalbetrieb verarbeitet fortlaufende Buchungsvorgänge. Dabei werden in
`booking_loop.py` und `terminal_ui/main.py` mehrere fachbezogene Fehlersituationen
behandelt, etwa unbekannte Karten, deaktivierte Karten, inaktive
Mitarbeitende, ungültige Buchungsfolgen und offene Phasenkonflikte.

Solche fachlichen Zustände sind inhaltlich der Domäne zuzuordnen. Die
Präsentationsschicht gibt sie nur aus; die zugrunde liegenden Fachregeln gehören
zum fachlichen Kern des Systems.

## Rolle bei Verwaltungsprozessen

Auch die administrativen Befehle weisen auf fachliche Regeln hin, die nicht in
reiner Ein-/Ausgabe aufgehen. Das betrifft etwa das Anlegen und Deaktivieren von
Mitarbeitenden, das Ersetzen oder Deaktivieren von Karten, Korrektur- und
Ergänzungsvorgänge bei Buchungen sowie Rollenänderungen bei Benutzerkonten.

Diese Vorgänge haben jeweils fachliche Bedeutung und setzen konsistente Regeln
voraus. Die Domänenschicht ist im Schichtenmodell derjenige Bereich, in dem
solche Regeln fachlich verortet sind.

## Verhältnis zur Anwendungsschicht

Die Anwendungsschicht orchestriert Anwendungsfälle; die Domäne liefert die
fachlichen Regeln und Begriffe, auf denen diese Anwendungsfälle beruhen. Diese
Arbeitsteilung ergibt sich unmittelbar aus der Layer-Reihenfolge in
`pyproject.toml`.

Die Domäne ist damit nicht für Startparameter, Geräteauflösung, Migrationen oder
Dateisystempfade zuständig. Solche Aspekte gehören zu höheren oder technischen
Schichten.

## Verhältnis zur Infrastruktur

Die Infrastrukturschicht stellt konkrete technische Mittel bereit, etwa
Datenbankzugriff, Konfigurationsdateien, Hardwarezugriff, Backups und
Benachrichtigungen. Die Domänenschicht ist davon fachlich getrennt.

Diese Trennung ist im Repository architektonisch angelegt. Sie verhindert,
dass fachliche Regeln unmittelbar an technische Details der Laufzeitumgebung
gebunden werden.

## Belegbare fachliche Themenfelder

Aus den vorhandenen Befehlen und Laufzeitpfaden lassen sich folgende
fachliche Themenfelder der Domäne sicher ableiten:

| Themenfeld | Belegbasis |
| --- | --- |
| Mitarbeitende | Befehlsgruppe `employees` |
| Karten | Kartenbefehle `assign`, `replace`, `deactivate` |
| Buchungen | Terminalbetrieb sowie Befehlsgruppe `bookings` |
| Dienstpläne | Befehlsgruppe `schedule` |
| Berichtsrelevante Zeitdaten | Befehlsgruppe `reports` |
| Benutzerkonten und Rollen | Befehlsgruppe `users` |
| Fachlich relevante Systemkonfiguration | `system_config` und betriebliche Konfigurationswerte |

Die Tabelle benennt nur Themenfelder, die aus dem Repository-Stand klar
abgeleitet werden können. Sie ersetzt keine Detailanalyse einzelner
Domänenmodule und macht keine unbelegten Aussagen über deren interne Struktur.

## Abgrenzung

Dieses Kapitel verzichtet bewusst auf die Benennung einzelner Domänenklassen,
Aggregatstrukturen oder Wertobjekte, solange sie aus dem hier gesicherten
Repository-Befund nicht direkt nachgewiesen wurden. Die Beschreibung bleibt auf
die architektonisch und fachlich belastbar ableitbaren Aussagen beschränkt.

Nicht dokumentiert werden daher unbelegte Implementierungsdetails. Dokumentiert
wird nur, dass eine echte Domänenschicht vorhanden ist und welche fachlichen
Themenfelder sich aus den belegten Betriebs- und Verwaltungsabläufen sicher
erschließen lassen.
