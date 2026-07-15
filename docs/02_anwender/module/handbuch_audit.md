# Handbuch `arbeitszeit` – Audit

**Kapitel:** 9
**Version:** 1.1
**Stand:** Juli 2026
**Quelldatei:** `docs/02_anwender/module/handbuch_audit.md`

## Zweck

Dieses Kapitel beschreibt den im Repository belegten Audit-Bezug des Projekts
`arbeitszeit`. Die Darstellung bleibt bewusst auf den Umfang beschränkt, der
sich aus dem nachweislich eingelesenen Repository-Material sicher ableiten
lässt.

Berücksichtigt wurden dabei insbesondere die belegte Projektstruktur, die
vorhandenen Präsentations- und Infrastrukturpfade, die Paketdefinition in
`pyproject.toml`, die Repository-Datei `run_audit.sh` sowie die erkennbaren
Dokumentationsbereiche unter `docs/`.

## Audit-Bezug im Repository

Ein direkter Audit-Bezug ist bereits auf oberster Repository-Ebene erkennbar.
Dort ist die Datei `run_audit.sh` vorhanden.

Zusätzlich existiert unter `docs/` ein eigener Bereich `07_pruefberichte/`.
Bereits die Struktur des Repositorys zeigt damit, dass Prüf- oder Auditbezüge
nicht nur randständig vorkommen, sondern als eigener Dokumentationsbereich
organisiert sind.

## Belegte Quellenbasis

Für dieses Kapitel sind folgende Quellen oder Quellbereiche als relevant
belegt:

| Quelle | Belegbarer Bezug |
| --- | --- |
| `run_audit.sh` | eigener Audit-bezogener Einstiegspunkt auf Repository-Ebene |
| `docs/07_pruefberichte/` | gesonderter Dokumentationsbereich für Prüfberichte |
| `pyproject.toml` | zentrale Projekt- und Architekturdefinition |
| `src/arbeitszeit/presentation/` | Einstiegspunkte für betriebliche und administrative Abläufe |
| `src/arbeitszeit/infrastructure/` | technische Prüf-, Konfigurations- und Laufzeitbausteine |
| `README.md` | übergeordnete Projektdokumentation |

Die Tabelle benennt nur Quellen, deren Existenz oder Rolle aus den eingelesenen
Repository-Befunden sicher ableitbar ist. Sie erhebt keinen Anspruch auf eine
vollständige inhaltliche Tiefenanalyse von `run_audit.sh`, weil diese aus dem
hier gesicherten Material nicht im Detail wiedergegeben werden kann.

## Einordnung von `run_audit.sh`

Die Datei `run_audit.sh` ist als eigenständiges Shell-Skript im Wurzelverzeichnis
vorhanden. Damit ist belegt, dass das Repository einen separaten Einstiegspunkt
für Audit- oder Prüfabläufe vorsieht.

Aus dem alleinigen Dateinamen lässt sich jedoch ohne zusätzliche, hier nicht
explizit gesicherte Skriptinhalte keine vollständige Detailbeschreibung des
konkreten Prüfablaufs ableiten. Dieses Kapitel dokumentiert daher nur sicher,
dass ein solcher Einstiegspunkt vorhanden ist.

## Zusammenhang mit der Architektur

Die belegte Schichtenarchitektur aus `pyproject.toml` trennt Präsentation,
Infrastruktur, Anwendung und Domäne. Diese Trennung ist für Audit- und
Prüfzwecke relevant, weil sie eine klar strukturierte technische und fachliche
Abgrenzung im Projekt vorgibt.

Zusätzlich ist in `pyproject.toml` eine Architekturprüfung mit
`import-linter` hinterlegt. Bereits dieser Befund zeigt, dass die Einhaltung
von Schichtgrenzen im Projekt nicht nur dokumentiert, sondern technisch
berücksichtigt wird.

## Prüfnahe Infrastruktur

Im Infrastrukturpaket sind mit `system_check.py`, `notification.py`,
`time_monitor.py`, dem Datenbankbereich und der Konfigurationsunterstützung
mehrere technische Bausteine vorhanden, die für Prüf-, Diagnose- oder
Überwachungszwecke relevant sind.

Insbesondere `run_system_check(...)` wird im Terminalbetrieb vor dem laufenden
Buchungsbetrieb ausgeführt. Das zeigt, dass zumindest ein Teil der prüfenden
Logik direkt in den Betriebsablauf eingebunden ist.

## Administrativer Prüfbezug

Auch die administrative Oberfläche weist einen nachvollziehbaren Prüfbezug auf.
In `admin_cli/main.py` sind unter anderem Berichtsbefehle, Systembefehle und
Befehle für offene oder warnrelevante Fälle registriert.

Belegt sind insbesondere Befehlsnamen wie `open-bookings`, `warn-cases`,
`corrections`, `supplements` und `open-review-cases`. Diese Benennungen
zeigen, dass das System administrative Sichtweisen auf prüfungsrelevante oder
nachbearbeitungsbedürftige Sachverhalte unterstützt.

## Dokumentationsbezug

Die Verzeichnisstruktur unter `docs/` enthält mit `07_pruefberichte/` einen
explizit benannten Bereich für Prüfberichte. Zusätzlich ist die gesamte
Projektdokumentation in mehrere fachliche Teilbereiche gegliedert.

Daraus lässt sich sicher ableiten, dass Audit- oder Prüfresultate im Projekt
nicht nur technisch, sondern auch dokumentarisch vorgesehen sind. Nicht sicher
ableitbar ist aus dem hier abgesicherten Material jedoch der konkrete Inhalt
aller dort enthaltenen Berichte.

## Grenzen der Aussagekraft

Dieses Kapitel verzichtet bewusst auf eine detaillierte Funktionsbeschreibung
von `run_audit.sh`, solange der vollständige Skriptinhalt nicht als direkt
abgesicherte Quelle vorliegt. Ebenso werden keine konkreten Auditmetriken,
Prüfkriterien, Exit-Codes oder Toolketten behauptet, die aus dem hier
nachweislich eingelesenen Material nicht eindeutig belegt sind.

Die Beschreibung bleibt daher bei folgenden sicheren Aussagen:

- `run_audit.sh` existiert als separater Audit-Einstiegspunkt.
- `docs/07_pruefberichte/` existiert als eigener Prüfberichtsbereich.
- Die Architektur enthält eine technisch hinterlegte Schichtenprüfung.
- Es existieren prüfnahe System- und Berichtsfunktionen in den laufenden
  Projektmodulen.

## Einordnung für Anwender

Für Anwender bedeutet der belegte Repository-Stand vor allem, dass das Projekt
neben dem Buchungs- und Verwaltungsbetrieb auch Prüf- und Kontrollbezüge
berücksichtigt. Diese Bezüge zeigen sich in separaten Audit- oder
Prüfartefakten, in administrativen Auswertungsbefehlen und in technischen
Prüfkomponenten.

Welche einzelnen Prüfabläufe vollständig automatisiert durch `run_audit.sh`
ausgeführt werden, bleibt in dieser Fassung absichtlich offen, solange diese
Details nicht unmittelbar und belastbar aus dem eingelesenen Material zitiert
werden können.
