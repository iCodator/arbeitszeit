# Terminologie-Harmonisierung

**Datum:** 2026-06-11  
**Grundlage:** `docs/claude_coding/claude_code_prompt_mittel_arbeitszeit_v1_2026-06-11_20-12.md`

---

## Betroffene Dateien

- `docs/informelles/phase2_planung.md`
- `docs/informelles/phase5_planung.md`

---

## Änderungen

### Änderung 1 — phase2_planung.md Z.327

**Irritation:** Abschnittsüberschrift `## V4-Bezüge und organisatorische Auflagen`
bei Inhalt, der ausschließlich v5-Dokumente referenziert.

**Evidenzgrundlage:** Zeilen 329–331 benennen explizit `pflichtenheft_arbeitszeit_v5.md`
und `regelwerk_arbeitszeit_v5.md`. Die Überschrift widerspricht ihrem eigenen Inhalt.

**Präzisierung:** `## V4-Bezüge und organisatorische Auflagen`
→ `## V5-Bezüge und organisatorische Auflagen`

**Art:** Terminologische Unstimmigkeit (nicht inhaltlicher Widerspruch). Keine
historische Aussage wurde überschrieben — der Inhalt war bereits korrekt.

---

### Änderung 2 — phase5_planung.md Z.257

**Irritation:** `361 Tests grün (alle Ebenen, Stand Phase 5/Schritt 2; heute 395).`
vermischt ohne eindeutige Labels einen historischen Zwischenstand (361) mit dem
aktuellen Gesamtstand (395). Lesende können nicht direkt erkennen, welche Zahl
wann galt.

**Evidenzgrundlage:** Beide Zahlen sind in der Datei selbst belegt. „Stand Phase
5/Schritt 2" ist die historische Markierung; „heute 395" ist der Gesamtstand nach
allen Coding-Aufgaben.

**Präzisierung:**
`361 Tests grün (alle Ebenen, Stand Phase 5/Schritt 2; heute 395).`
→ `361 Tests grün (historischer Stand Phase 5/Schritt 2); heutiger Gesamtstand: 395 Tests.`

**Art:** Lesbarkeits-Spannung. Historische Zahl 361 bleibt erhalten.

---

### Änderung 3 — phase5_planung.md Z.375

**Irritation:** `(Schätzung: ~8 Tests)` für `test_supplement_flow.py` ist überholt.
Der exakte Wert ist aus dem Repo direkt ermittelbar: `pytest tests/e2e/test_supplement_flow.py --collect-only` liefert 8 Tests.

**Evidenzgrundlage:** Tatsächliche Testanzahl per pytest-Inventar verifizierbar.

**Präzisierung:** `(Schätzung: ~8 Tests)` → `(8 Tests)`

**Art:** Überholte Schätzung. Kein inhaltlicher Widerspruch, nur veraltetes Label.

---

## Bewusst beibehaltene historische Formulierungen

- Alle historischen Testzählstände (z. B. „361 Tests grün") bleiben erhalten;
  sie wurden nur mit klaren Labels versehen.
- Keine Planungsinhalte wurden inhaltlich uminterpretiert.
- Historische Phasenbezüge in phase5_planung.md (z. B. „Stand Phase 5/Schritt 2")
  wurden nicht gelöscht.

---

## Nicht entscheidbar auf Basis der vorliegenden Artefakte

Keine Punkte in diesem Dokument. Alle drei Korrekturen sind durch die Dateien
selbst belegt.
