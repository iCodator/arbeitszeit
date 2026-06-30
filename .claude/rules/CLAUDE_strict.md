---
description: Strenger Modus für fachlich und technisch besonders sensible Bereiche.
paths:
  - src/arbeitszeit/domain/**
  - src/arbeitszeit/application/**
  - migrations/**
  - tests/domain/**
  - tests/application/**
  - tests/test_migrations.py
---

# CLAUDE_strict.md – Strenger Modus für sensible Bereiche

Diese Regeldatei verschärft die Anforderungen für Änderungen in fachlich, rechtlich und technisch sensiblen Bereichen.
Sie ergänzt `../CLAUDE.md`.

## 1. Vorrang der Vorsicht

In allen von `paths` erfassten Bereichen gilt:

- erst analysieren
- dann gezielt nachfragen
- erst danach minimalinvasiv ändern

Wenn Unsicherheit besteht, ist konservatives Verhalten Pflicht.

## 2. Zusätzliche Analysepflicht

Vor jeder Änderung muss Claude ausdrücklich benennen:

- welche fachliche Regel betroffen ist
- welche bestehenden Module betroffen sind
- warum die Änderung im gewählten Layer stattfindet
- welche Risiken für Nachvollziehbarkeit, Historie oder Regelkonformität bestehen

## 3. Zusätzliche Nachfragepflicht

Claude darf in diesen Bereichen keine Annahmen stillschweigend einbauen.
Wenn mehrere fachlich plausible Interpretationen existieren, muss zuerst eine Rückfrage gestellt werden.

## 4. Minimalinvasive Änderungspflicht

Änderungen in diesen Bereichen müssen:

- so klein wie möglich sein
- bestehende Schnittstellen nur ändern, wenn fachlich zwingend nötig
- keine versteckten Seiteneffekte erzeugen
- durch passende Tests abgesichert werden

## 5. Besondere Regeln für Domain und Application

- Fachregeln nie in Infrastruktur verlagern
- implizite Regeln explizit modellieren
- Korrekturen, Nachträge und Prüffälle nicht vereinfachend zusammenziehen
- fachliche Sonderfälle nicht durch technische Abkürzungen kaschieren

## 6. Besondere Regeln für Migrationen

- jede Schemaänderung muss fachlich begründet sein
- bestehende Daten müssen erhalten bleiben
- Migrationsschritte müssen reproduzierbar und überprüfbar sein
- Änderungen an Migrationslogik erfordern passende Tests
- keine verdeckten Datenbereinigungen

## 7. Qualitätsmaßstab

In diesen Bereichen reicht „funktioniert“ nicht aus.
Erforderlich sind zusätzlich:

- fachliche Plausibilität
- rechtliche Vorsicht
- testbare Nachvollziehbarkeit
- architektonische Sauberkeit

## 8. Verbotene Muster

- schnelle Workarounds in sensibler Fachlogik
- unklare Sammeländerungen ohne klare Begründung
- Vermischung von Regelprüfung und technischer Hilfslogik
- Veränderungen an Historie oder Korrekturpfaden ohne explizite fachliche Absicherung

## 9. Merksatz

In sensiblen Bereichen gilt: lieber eine kleine, präzise und sauber abgesicherte Änderung als eine große, schnelle und fachlich riskante Lösung.
