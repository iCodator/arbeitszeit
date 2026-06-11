# Planung: Abarbeitung kritischer Auditpunkte
## Grundlage: `claude_code_anweisung_kritisch_arbeitszeit_v1_2026-06-11_19-42.md`

**Datum:** 2026-06-11  
**Erstellt von:** Claude Code  

---

## 0. Ist-Stand-Analyse vor Planungsbeginn

### 0.1 Tests

406 Tests grün (verifiziert: `pytest tests/ -q --tb=no`).

### 0.2 Deliverable-Status laut Anweisung

| Deliverable | Vorgeschlagener Dateiname | Status |
|---|---|---|
| Analyse + Entscheidungsvorlage device_events | `device_event_architekturentscheidung_v1.md` | **fehlend** |
| Abschlussprotokoll device_events | `device_event_abschlussprotokoll_v1.md` | **fehlend** |
| Revisionsfeste Testmatrix | `testmatrix_revision_v1.md` | **fehlend** |
| Prüfbericht Testmatrix | `testmatrix_pruefbericht_v1.md` | **fehlend** |
| Abweichungsliste Planung vs. Matrix | `testmatrix_planabweichungen_v1.md` | **fehlend** |

### 0.3 Technischer Stand device_events (Arbeitsauftrag A)

Die Implementierung wurde unmittelbar vor dieser Planung abgeschlossen (Commit `0f20931`).
Betroffene Änderungen:

| Datei | Änderung |
|---|---|
| `src/arbeitszeit/domain/ports/repositories.py` | `DeviceEventRepository`-Protocol neu |
| `src/arbeitszeit/application/unit_of_work.py` | `device_event_repo` im Protocol |
| `src/arbeitszeit/infrastructure/db/repositories/device_event.py` | `SQLiteDeviceEventRepository.add()` |
| `src/arbeitszeit/infrastructure/db/unit_of_work.py` | `self.device_event_repo` im Konstruktor |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | `RFID_SCAN`-Record erzeugen, ID durchreichen |
| `tests/application/fakes.py` | `FakeDeviceEventRepository` |
| `tests/integration/test_device_event_booking.py` | 3 neue Tests |

**Planungsdokumente noch veraltet:** `planung_gesamt.md`, `phase4_planung.md`, `phase5_planung.md`
enthalten noch Aussagen wie „noch nicht vollständig im Produktionspfad aktiv" und
„offener Architekturpunkt" — diese müssen aktualisiert werden.

### 0.4 Referenzdokumente Arbeitsauftrag B

Beide Referenzdokumente sind im Projektwurzel vorhanden (nicht in `docs/`):
- `pflichtenheft_arbeitszeit_v5.md` ✓
- `regelwerk_arbeitszeit_v5.md` ✓

---

## Arbeitsauftrag A — Dokumentation der device_events-Entscheidung

**Status der Implementierung:** Pfad A1 (produktive Umsetzung) wurde gewählt und
vollständig umgesetzt. Zu erbringen sind die drei Dokumentations-Deliverables.

### A.1 Schritt A.1+A.2: Architekturentscheidungs-Dokument erstellen

**Datei:** `docs/informelles/device_event_architekturentscheidung_v1.md`

Inhalt gemäß Anweisung (Schritt A.1 + A.2 kombiniert):

1. **Dokumentiertes Sollbild** — Belege aus:
   - `planung_gesamt.md` Z.61, Z.87, Z.92, Z.170: explizite Aussagen zur Verkettung
   - `phase4_planung.md`: Schritt-2-Abschnitt mit `device_event_id` FK
   - `phase5_planung.md`: Scope-Abgrenzung
   - `migrations/0005_time_bookings_device_event_id.sql`: Schema-Vorbereitung

2. **Tatsächliches Istbild** — Belege aus:
   - `booking_loop.py` (vorher `device_event_id=None`, jetzt `RFID_SCAN`-Record)
   - `src/.../repositories/device_event.py` (neu)
   - `tests/integration/test_device_event_booking.py` (3 Tests)
   - `src/.../domain/ports/repositories.py` (DeviceEventRepository)

3. **Abweichungsanalyse:** Lücke war operativ (kein Produktionspfad), nicht nur dokumentarisch.

4. **Gewählter Pfad:** A1 — Evidenz: Schema, Migration, BookCommand.device_event_id,
   Planungsdokumente fordern Verkettung.

5. **Evidenztabelle** mit Spalten Artefakt / Sollbild / Istbild / Bedeutung

### A.2 Schritt A.3+A.4: Planungsdokumente aktualisieren + Abschlussprotokoll

**Betroffene Dokumente:**

| Dokument | Stelle | Aktualisierung |
|---|---|---|
| `planung_gesamt.md` Z.61 | „noch nicht operativ aktiviert" | → „operativ aktiviert (Commit 0f20931)" |
| `planung_gesamt.md` Z.92 | „nicht vollständig im Produktionspfad aktiv" | → Abschlussformulierung |
| `planung_gesamt.md` Z.170 | „offener Architekturpunkt" | → „abgeschlossen" |
| `phase4_planung.md` | Offener-Punkt-Abschnitt | → Status-Update |
| `phase5_planung.md` | Scope-Abgrenzung Z.9 | → Anpassen |

**Datei:** `docs/informelles/device_event_abschlussprotokoll_v1.md`

Pflichtinhalt laut Anweisung:
- Entscheidung: A1, begründet mit Artefakt-Evidenz
- Geänderte Dateien (8)
- Geprüfte, nicht geänderte Dateien
- Offene Restpunkte (z. B. `related_time_booking_id` wird noch nicht befüllt)
- Einschätzung: kritischer Auditbefund **vollständig geschlossen**

---

## Arbeitsauftrag B — Revisionsfeste Testmatrix

### B.1 Referenzquellen

Zu verwenden: `pflichtenheft_arbeitszeit_v5.md` und `regelwerk_arbeitszeit_v5.md`
(beide im Projektwurzel; werden vollständig gelesen, nicht paraphrasiert).

Zusätzlich: `docs/anlage_einhaltung_pflichtenheft_v2.md` (sofern vorhanden).

### B.2 Muss-Anforderungen extrahieren

Matrix-ID-Schema:
- `PH-01..PH-NN` für Pflichtenheft v5
- `RW-01..RW-NN` für Regelwerk v5

Für jede Anforderung: ID, Kurzname, Quellstelle (Datei + §-Angabe), Beschreibung,
Kategorie (Buchung / Korrektur / Nachtrag / Review / Export / Backup / Restore /
Systemcheck / Zeitmonitor / Benutzerkonten / Rollen / Migrationen).

### B.3 Tests erfassen

Vollständige strukturierte Erfassung aller Tests:
- `tests/test_migrations.py` (12 Tests)
- `tests/domain/` (67 Tests in 4 Dateien)
- `tests/application/` (109 Tests inkl. test_fake_unit_of_work.py)
- `tests/integration/` (165 Tests inkl. test_device_event_booking.py)
- `tests/e2e/` (42 Tests)

Jeder Test: Datei, Testname, Ebene, Was geprüft wird, Zuordnungsstatus.

### B.4 Matrix erstellen

**Datei:** `docs/informelles/testmatrix_revision_v1.md`

Pflichtstruktur:

```
| Matrix-ID | Quelle | Quellstelle | Muss-Anforderung | Zugeordnete Tests | Testebene | Abdeckungsgrad | Kommentar |
```

Abdeckungsgrade: `vollständig belegt` / `teilweise belegt` / `nicht belegt` /
`nicht entscheidbar auf Basis der vorliegenden Artefakte`

### B.5 Prüfbericht

**Datei:** `docs/informelles/testmatrix_pruefbericht_v1.md`

Abschnitte: Referenzdokumente, Extraktionsmethode, Zuordnungsmethode,
Unsicherheiten, Anforderungen ohne Test, Tests ohne Muss-Zuordnung,
phasenübergreifende Vermischungen, offene Punkte.

### B.6 Konsistenzabgleich + Abweichungsliste

**Datei:** `docs/informelles/testmatrix_planabweichungen_v1.md`

Prüfung gegen: alle phase?_planung.md und planung_gesamt.md.
Spalten: betroffene Datei / Aussage Planung / Aussage Matrix / Bewertung /
empfohlene Folgeaktion.

---

## Reihenfolge der Ausführung

```
1. A.1  device_event_architekturentscheidung_v1.md erstellen
2. A.2a planung_gesamt.md, phase4_planung.md, phase5_planung.md aktualisieren
3. A.2b device_event_abschlussprotokoll_v1.md erstellen
4. B.1  Referenzdokumente verifizieren und inventarisieren
5. B.2  Muss-Anforderungen extrahieren (pflichtenheft_v5 + regelwerk_v5, vollständig lesen)
6. B.3  Tests vollständig erfassen
7. B.4  testmatrix_revision_v1.md erstellen
8. B.5  testmatrix_pruefbericht_v1.md erstellen
9. B.6  testmatrix_planabweichungen_v1.md erstellen
10.    Commit + Push aller Dokumente
```

---

## Verbotene Abkürzungen (aus Anweisung übernommen)

- Keine Textkosmetik statt Evidenzanalyse
- Keine Schönfärbung: offene Restpunkte offen benennen
- Keine Kopierpaste aus Planungsdokumentation ohne echten Testbezug
- Keine Testabdeckungsbehauptung ohne Lesen der konkreten Testfunktion
- Keine stillen Glättungen von Widersprüchen

---

## Definition of Done (aus Anweisung)

1. ✓ Architekturpunkt device_events analysiert
2. ✓ Entscheidung A1 dokumentiert und begründet
3. ☐ Technische Umsetzung vollständig dokumentiert (Abschlussprotokoll)
4. ☐ Planungsdoks aktualisiert
5. ☐ Revisionsfeste Testmatrix existiert
6. ☐ Testmatrix ordnet Muss-Anforderungen konkreten Tests zu
7. ☐ Prüfbericht zur Matrix existiert
8. ☐ Abweichungsliste existiert
9. ☐ Unsicherheiten offen benannt
10. ☐ Nichts als erledigt markiert, was nicht belastbar belegt ist
