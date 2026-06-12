# Planung: Abarbeitung „mittel"-Priorität
## Grundlage: `docs/claude_coding/claude_code_prompt_mittel_arbeitszeit_v1_2026-06-11_20-12.md`

**Datum:** 2026-06-11

---

## 0. Ist-Stand-Analyse (Bestandsaufnahme vor Änderung)

### 0.1 phase2_planung.md — Terminologie-Befunde

| Zeile | Befund | Art |
|---|---|---|
| 327 | Abschnittsüberschrift `## V4-Bezüge und organisatorische Auflagen` | Missverständlich: Inhalt referenziert v5-Dokumente, Überschrift sagt V4 |
| 174 | `Regelwerk v5 §11-konform` | Korrekt, kein Handlungsbedarf |
| 200, 222, 225 | Pflichtenheft/Regelwerk v5 §-Referenzen | Korrekt |
| 329–331 | v5-Referenzdokumentpfade | Korrekt |

**Fazit:** Einziger echter Terminologie-Fehler in phase2_planung.md: Abschnittsüberschrift `V4-Bezüge` bei v5-Inhalten.

### 0.2 phase5_planung.md — Terminologie-Befunde

| Zeile | Befund | Art |
|---|---|---|
| 257 | `361 Tests grün (alle Ebenen, Stand Phase 5/Schritt 2; heute 395).` | Mischung historischer Stand (361) und heutiger Stand (395) ohne klares Label |
| 375 | `(Schätzung: ~8 Tests)` für test_supplement_flow.py | Überholte Schätzung — tatsächlich 8 Tests (nicht Schätzung) |
| 18, 53 | `395 Tests grün (alle Ebenen)` | Korrekt |
| 29 | `(6 Use Cases, 109 Tests)` für Application | Korrekt |
| 372 | `(12 Tests, inkl. 2 APPLICATION_ERROR-Tests)` | Korrekt |

**Fazit:** Zwei Textstellen in phase5_planung.md mit unklarer historisch/aktuell-Trennung.

### 0.3 Migrationen — Inventur

Alle 6 Migrationen gelesen; Zweck aus Kommentaren im SQL-Code belegbar:

| Migration | Kommentar-Quelle |
|---|---|
| 0001_schema.sql | Kein Kommentar, aber DDL vollständig lesbar |
| 0002_seed_defaults.sql | Kein Kommentar, INSERT-Inhalt direkt lesbar |
| 0003_cleanup_booking_status.sql | Kommentar: „BookingStatus bereinigen, POSSIBLE_*und MANUAL_ENTRY entfernen" |
| 0004_supplement_reject_fields_and_review_note.sql | Kommentar: „Semantische Trennung Genehmigung/Ablehnung, Notizfeld für Prüffälle" |
| 0005_time_bookings_device_event_id.sql | Kommentar: „device_event_id ergänzen, Table-Rebuild" |
| 0006_system_events_application_error.sql | Kommentar: „APPLICATION_ERROR hinzufügen, Abgrenzung zu APPLICATION_STOP" |

---

## Teil A — Terminologie harmonisieren

### A.1 Konkrete Änderungen in phase2_planung.md

**Änderung 1 (Zeile 327):**
- Befund: `## V4-Bezüge und organisatorische Auflagen` — Inhalt referenziert v5, Überschrift sagt V4
- Evidenz: Zeilen 329–331 benennen explizit `pflichtenheft_arbeitszeit_v5.md` und `regelwerk_arbeitszeit_v5.md`
- Aktion: Umbenennung auf `## V5-Bezüge und organisatorische Auflagen`
- Historische Entwicklung bleibt erhalten (keine inhaltliche Änderung)

### A.2 Konkrete Änderungen in phase5_planung.md

**Änderung 1 (Zeile 257):**
- Befund: `361 Tests grün (alle Ebenen, Stand Phase 5/Schritt 2; heute 395).`
- Evidenz: Phase-5-Plan enthält diesen Zwischenstand ohne Trennkennzeichnung
- Aktion: Formulierung klarer trennen:
  `361 Tests grün (historischer Stand Phase 5/Schritt 2); heutiger Gesamtstand: 395 Tests.`
- Historische Zahl 361 bleibt erhalten

**Änderung 2 (Zeile 375):**
- Befund: `(Schätzung: ~8 Tests)` für test_supplement_flow.py
- Evidenz: pytest collect-only liefert exakt 8 Tests in test_supplement_flow.py
- Aktion: `(Schätzung: ~8 Tests)` → `(8 Tests)`
- Label „Schätzung" entfällt, da exakter Wert belastbar ermittelbar ist

### A.3 Deliverable: terminologie_harmonisierung_v1.md

**Datei:** `docs/informelles/terminologie_harmonisierung_v1.md`

Pflichtabschnitte:
1. Titel, Datum
2. Betroffene Dateien
3. Änderungen (je: Irritation / Evidenz / Präzisierung)
4. Bewusst beibehaltene historische Formulierungen
5. Nicht entscheidbar auf Basis der vorliegenden Artefakte

---

## Teil B — Migrationsübersicht in phase1_planung.md

### B.1 Tabelle-Schema

Spalten gemäß Prompt:

| Migration | Technische Änderung | Fachliche Änderung | Änderungstyp | Belegbasis / Kommentar |

**Belegregeln (strikt):**
- Technische Änderung: direkt aus DDL/INSERT lesbar
- Fachliche Änderung: nur wenn Kommentar oder Kontext sie klar benennt
- Änderungstyp: ausschließlich Vokabular aus Prompt B2

### B.2 Vorschau Tabelleninhalt (zur Planung)

| Migration | Techn. Änderung | Fachliche Änderung | Typ | Beleg |
|---|---|---|---|---|
| 0001_schema.sql | 16-Tabellen-DDL, 17 Indizes, schema_migrations | Vollständiges Fachschema inkl. device_events, time_bookings, user_accounts u.a. | Initialschema | DDL vollständig lesbar |
| 0002_seed_defaults.sql | INSERT work_schedule_versions (5 Zeilen), system_config (4 Zeilen), audit_log (9 Einträge) | Mo–Fr Regelarbeitszeiten; Standardkonfig backup.nas_enabled=false | fachliche Erweiterung | INSERT-Inhalt lesbar |
| 0003_cleanup_booking_status.sql | CHECK-Constraint auf time_bookings.current_status und booking_status_history.new_status entfernt; Table-Rebuild | Entfernung von POSSIBLE_* und MANUAL_ENTRY aus BookingStatus — orthogonale Modellierung via ReviewCaseType | Compliance-/Nachweisfeld | SQL-Kommentar Z.1–5 |
| 0004_supplement_reject_fields_and_review_note.sql | supplements: rejected_by_user_id, rejected_at; review_cases: note TEXT | Ablehnung formal von Genehmigung getrennt; Prüffall-Notiz | fachliche Erweiterung | SQL-Kommentar Z.1–6 |
| 0005_time_bookings_device_event_id.sql | device_event_id INTEGER FK, Table-Rebuild; Indizes wiederhergestellt | Schemaverknüpfung time_bookings → device_events (null bei bestehenden Zeilen) | Vorbereitungspunkt ohne belegte operative Nutzung (zum Zeitpunkt der Migration) | SQL-Kommentar Z.1–3; operative Nutzung kam mit Commit 0f20931 |
| 0006_system_events_application_error.sql | CHECK-Constraint system_events.event_type um APPLICATION_ERROR erweitert; Table-Rebuild | Neuer Systemereignistyp für abgefangene Laufzeitfehler | technische Strukturergänzung | SQL-Kommentar Z.1–5 |

### B.3 Deliverable: Ergänzung in phase1_planung.md

Die Tabelle wird als neuer Abschnitt **am Ende** von `docs/informelles/phase1_planung.md` eingefügt
(nach dem V5-Bezüge-Abschnitt), damit historische Inhalte unberührt bleiben.

### B.4 Deliverable: migrationsuebersicht_notiz_v1.md

**Datei:** `docs/informelles/migrationsuebersicht_notiz_v1.md`

Pflichtabschnitte:
1. Titel, Datum
2. Ausgewertete Migrationsdateien
3. Methodik der Einordnung
4. Trennung technischer vs. fachlicher Aussage
5. Offene Einordnungsfragen
6. Fälle mit „nicht entscheidbar auf Basis der vorliegenden Artefakte"

---

## Ausführungsreihenfolge

```
1. phase2_planung.md: V4-Bezüge → V5-Bezüge (eine Zeile)
2. phase5_planung.md: zwei Textstellen präzisieren
3. terminologie_harmonisierung_v1.md erstellen
4. phase1_planung.md: Migrationsübersicht-Tabelle anhängen
5. migrationsuebersicht_notiz_v1.md erstellen
6. abarbeitung_mittel_abschlussnotiz_v1.md erstellen
7. Tests laufen (keine Codeänderungen erwartet)
8. Commit + Push
```

---

## Definition of Done (7 Kriterien aus Prompt)

1. ☐ phase2_planung.md terminologisch präziser, ohne Historie zu verlieren
2. ☐ phase5_planung.md trennt historische und heutige Testzählstände klar
3. ☐ Harmonisierung separat dokumentiert (terminologie_harmonisierung_v1.md)
4. ☐ phase1_planung.md enthält kompakte, belegorientierte Migrationsübersicht
5. ☐ Einordnungsnotiz zur Migrationsübersicht existiert
6. ☐ Alle unsicheren Punkte offen markiert
7. ☐ Keine historische Entwicklung unzulässig überschrieben
