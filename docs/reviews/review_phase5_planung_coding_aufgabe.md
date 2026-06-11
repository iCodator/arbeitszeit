# Prüfbericht: phase5_planung.md und phase5_coding_aufgabe.md

**Prüfgrundlage:** `docs/informelles/planung_gesamt.md` (Stand: 2026-06-11)
**Geprüfte Dokumente:**
- `docs/informelles/phase5_planung.md`
- `docs/informelles/phase5_coding_aufgabe.md`

---

## phase5_planung.md

### Fehler 1 — v4-Referenzen (15+ Stellen)

**§-Nummern mit Verschiebung** (v5 fügte §7.9 Benutzerverwaltung ein):

| Vorher | Nachher |
| --- | --- |
| `Pflichtenheft v4 §7.12` (Zeilen 110, 295) | `Pflichtenheft v5 §7.13` |
| `Pflichtenheft v4 §7.10` (Zeile 313) | `Pflichtenheft v5 §7.11` |

**Globale Ersetzungen** (§-Nummern bleiben gleich):
- `Basiert auf Pflichtenheft v4 und Regelwerk v4` (Zeile 3) → v5
- Alle `Pflichtenheft v4` → `Pflichtenheft v5`
- Alle `Regelwerk v4` → `Regelwerk v5`
- Alle `V4 §` → `V5 §` (Testpflicht-Abschnitt-Überschrift, Zeile 362, 389)
- `V4-Bezüge` → `V5-Bezüge`; Footer-Dateinamen auf v5

**Behobene Korrektur:** Alle Stellen aktualisiert; Datum auf 2026-06-11 aktualisiert.

---

### Fehler 2 — Testanzahlen veraltet (mehrere Stellen)

| Stelle | Vorher | Nachher |
| --- | --- | --- |
| Zeile 21, 56 | `369 Tests grün (alle Ebenen)` | `395 Tests grün` |
| Zeile 32 | `(6 Use Cases, 107 Tests)` | `109 Tests` |
| Zeile 217 | `10 Tests in test_booking_flow.py` | `12 Tests` |
| Zeile 258 | `361 Tests grün (Stand Schritt 2)` | `…; heute 395` |
| Zeile 373 | `(Schätzung: ~10 Tests)` | `(12 Tests, inkl. 2 APPLICATION_ERROR-Tests)` |

Verifiziert: `pytest tests/e2e/test_booking_flow.py --collect-only` → 12 Tests.

**Behobene Korrektur:** Alle Zähler aktualisiert.

---

### Fehler 3 — `_run_one_cycle()` nicht dokumentiert (um Zeile 192)

Die `phase5_coding_aufgabe` extrahierte den Loop-Body in `_run_one_cycle()`.
Das wurde in der `main.py`-Beschreibung nicht erwähnt.

**Behobene Korrektur:** Hinweis auf `_run_one_cycle()`-Extraktion und Testbarkeit
im `main.py`-Abschnitt ergänzt.

---

## phase5_coding_aufgabe.md

**Befund: Inhaltlich korrekt und vollständig implementiert.**

- `_run_one_cycle()` in `main.py` vorhanden und direkt importierbar ✓
- 12 Tests in `test_booking_flow.py` (10 + 2 neue) ✓
- `APPLICATION_ERROR` → `system_events` bei RuntimeError ✓
- `DomainError` → kein `APPLICATION_ERROR` ✓
- Alle Akzeptanzkriterien erfüllt ✓

---

## Zusammenfassung

| Dokument | Problem | Status |
| --- | --- | --- |
| `phase5_planung.md` 15+ Stellen | v4-Referenzen → v5 (inkl. §7.10→§7.11, §7.12→§7.13) | ✓ behoben |
| `phase5_planung.md` 5 Stellen | Testanzahlen veraltet (369/10/107 → 395/12/109) | ✓ behoben |
| `phase5_planung.md` Zeile 192 | `_run_one_cycle()` nicht dokumentiert | ✓ behoben |
| `phase5_coding_aufgabe.md` | Korrekt, vollständig implementiert | ✓ |
