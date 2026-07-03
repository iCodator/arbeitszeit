# Prüfbericht: Migration verbleibender Pflichtenheft-v5-Referenzen auf v6

## Gesamteinschätzung

Auf Basis eines repository-weiten Scans nach „Pflichtenheft v5" / „Version 5"-Bezügen (siehe `docs/pruefberichte/dokumentations_inventar.md` für die vollständige Fundstellenübersicht) wurden drei aktive Dokumente identifiziert, deren Pflichtenheft-Referenz noch auf die nicht mehr existierende Datei `pflichtenheft_arbeitszeit_v5.md` verwies. Nach Rücksprache wurden diese drei Stellen kontrolliert auf `pflichtenheft_arbeitszeit_v6.md` migriert; historische Artefakte (CHANGELOG, Testmatrix-Nachweise, datierte Abschlussdokumente, Prüfberichte) blieben planmäßig unverändert. Zusätzlich wurde die zuvor ohne Archivierung gelöschte Datei `pflichtenheft_arbeitszeit_v5.md` aus dem Git-Verlauf wiederhergestellt und unter `docs/archive/` abgelegt, um das Versionsarchiv (v3, v4, v5) lückenlos zu machen.

## Durchgeführte Änderungen

### 1. `docs/adr/adr-cqrs-lesezugriff.md`, Zeile 178
- **Vorher:** `Pflichtenheft v5 §7.12 — Pflichtauswertungen`
- **Nachher:** `Pflichtenheft v6 §7.13 — Pflichtauswertungen`
- **Beleg:** In `pflichtenheft_arbeitszeit_v6.md` ist §7.12 „Export" (Zeile 149), der Abschnitt „Pflichtauswertungen" liegt unter §7.13 (Zeile 164). Die reine Versionsangabe war somit nicht ausreichend; die Paragraphennummer musste mitkorrigiert werden.

### 2. `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md`, Zeilen 10 und 13
- **Vorher (Z. 10):** `Auflagen: aus Pflichtenheft v5 / Regelwerk v5 / planung_gesamt.md — ohne Freigabe-Behauptung.`
- **Nachher (Z. 10):** `Auflagen: aus Pflichtenheft v6 / Regelwerk v5 / planung_gesamt.md — ohne Freigabe-Behauptung.`
- **Vorher (Z. 13):** `**Abkürzungen:** PH = Pflichtenheft v5, RW = Regelwerk v5`
- **Nachher (Z. 13):** `**Abkürzungen:** PH = Pflichtenheft v6, RW = Regelwerk v5`
- **Beleg:** Nur der Pflichtenheft-Anteil wurde angehoben; der Regelwerk-Anteil bleibt unverändert bei v5, da `regelwerk_arbeitszeit_v5.md` laut `docs/pruefberichte/pruefbericht_session_abschluss.md` (Zeile 49) unverändert gültig ist und nicht auf v6 angehoben wurde.

### 3. `docs/datenschutz/vvt_arbeitszeit_v1.md`, Zeilen 16 und 242
- **Vorher (Z. 16):** `(Stand: pflichtenheft_arbeitszeit_v5.md, regelwerk_arbeitszeit_v5.md)`
- **Nachher (Z. 16):** `(Stand: pflichtenheft_arbeitszeit_v6.md, regelwerk_arbeitszeit_v5.md)`
- **Vorher (Z. 242):** `*Grundlage: pflichtenheft_arbeitszeit_v5.md §§ 4, 8.4, 11, 12; regelwerk_arbeitszeit_v5.md §§ 17, 18; …*`
- **Nachher (Z. 242):** `*Grundlage: pflichtenheft_arbeitszeit_v6.md §§ 4, 8.4, 11, 12; regelwerk_arbeitszeit_v5.md §§ 17, 18; …*`
- **Beleg:** Die Paragraphen 4 („Rechts- und Regelrahmen"), 8.4 („Datensparsamkeit"), 11 („Datenschutz und Zugriffsschutz") und 12 („Aufbewahrung, Archivierung und Löschung") existieren in `pflichtenheft_arbeitszeit_v6.md` unter identischer Nummerierung und identischem Titel (Zeilen 17, 197, 241, 255) — anders als beim ADR-Fall war hier keine Paragraphenverschiebung festzustellen, sodass eine reine Versionsangaben-Korrektur ausreichend war.
- **Nicht geändert (Z. 238):** Die Versionshistorien-Zeile „Erstversion auf Basis `pflichtenheft_arbeitszeit_v5.md` und `regelwerk_arbeitszeit_v5.md`" wurde bewusst unverändert gelassen, da sie den dokumentierten Stand zum Erstellungszeitpunkt (2026-06-12) beschreibt und keine aktuelle Referenz darstellt.

### 4. Wiederherstellung `docs/archive/pflichtenheft_arbeitszeit_v5.md`
- **Quelle:** Git-Commit `0673d20~1` (identisch mit Commit `7a714ae`, dem letzten Stand vor der Löschung im nachfolgenden Commit `0673d20`).
- **Beleg für Auswahl dieses Standes:** Der frühere Commit `ddbe32e` enthielt die Datei noch mit interner Kopfzeile „Version 4.0" (redaktioneller Zwischenstand); erst `7a714ae` („pflichtenheft und regelwerk auch intern auf v5 gesetzt") korrigierte die interne Versionsangabe auf „Version 5.0". Ein Diff zwischen dem Stand aus `7a714ae` und `0673d20~1` ergab keine Unterschiede, somit ist `0673d20~1` der endgültige, unveränderte letzte v5-Stand.
- **Ergebnis:** Datei ist nun konsistent mit dem bestehenden Archivierungsmuster für `pflichtenheft_arbeitszeit_v3.md` und `pflichtenheft_arbeitszeit_v4.md` unter `docs/archive/` abgelegt.

## Bewusst unverändert belassene Dokumente (Bestätigung des Ausschlusses)

- `CHANGELOG.md` (Zeilen 20, 54, 57, 61) — historisches Änderungsprotokoll, beschreibt Release-Zustände zum jeweiligen Zeitpunkt korrekt.
- `docs/betrieb/nachweise/testmatrix_pruefbericht_v1.md`, `docs/betrieb/nachweise/testmatrix_revision_v1.md` — dokumentieren die Prüfgrundlage einer abgeschlossenen, revisionsfesten Testdurchführung.
- `docs/informelles/session_abschluss_und_klarstellungen_2026-06-11.md` — datiertes Abschluss-Artefakt, beschreibt den Versionsübergang selbst mit explizitem Zeitbezug.
- `docs/pruefberichte/pruefbericht_rechtskonformitaet_pflichtenheft.md`, `docs/pruefberichte/pruefbericht_session_abschluss.md`, `docs/pruefberichte/dokumentations_inventar.md` — Prüfberichte/Inventar zitieren historisch geprüfte Zustände als Beleg, keine lebenden Referenzen.

## Offene Punkte

Keine. Alle vier zur Entscheidung vorgelegten Klärungspunkte wurden geklärt und umgesetzt.

## Quellenbelege

- Löschung von `pflichtenheft_arbeitszeit_v5.md`: Commit `0673d20`.
- Letzter unveränderter v5-Stand: Commit `0673d20~1` = `7a714ae`, verifiziert per Diff gegen den internen Versionsstring „Version 5.0".
- Paragraphenverschiebung §7.12/§7.13: `pflichtenheft_arbeitszeit_v6.md`, Zeilen 149 und 164, abgeglichen mit vorherigem Stand in `docs/adr/adr-cqrs-lesezugriff.md`.
- Fortbestand von `regelwerk_arbeitszeit_v5.md`: `docs/pruefberichte/pruefbericht_session_abschluss.md`, Zeile 49.
- Gliederungsvergleich §4/§8.4/§11/§12: `pflichtenheft_arbeitszeit_v6.md`, Zeilen 17, 197, 241, 255.
