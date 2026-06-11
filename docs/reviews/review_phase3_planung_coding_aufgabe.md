# Prüfbericht: phase3_planung.md und phase3_coding_aufgabe.md

**Prüfgrundlage:** `docs/informelles/planung_gesamt.md` (Stand: 2026-06-11)
**Geprüfte Dokumente:**
- `docs/informelles/phase3_planung.md`
- `docs/informelles/phase3_coding_aufgabe.md`

---

## phase3_planung.md

### Fehler 1 — `FakeUnitOfWork.__exit__` beschreibt veraltete Semantik (Zeilen 48–49)

Zeilen 48–49 beschrieben:
> „Ruft `rollback()` bei Exception, damit Tests das reale Transaktionsverhalten
> widerspiegeln."

Die `phase3_coding_aufgabe` wurde implementiert. `FakeUnitOfWork.__exit__` nutzt
heute `if not self.committed: self.rollback()` — rollback bei **jeder** unkonfirmierten
Transaktion, nicht nur bei Exceptions. Zwei Gegentests in
`tests/application/test_fake_unit_of_work.py` sichern das ab.

**Behobene Korrektur:** Abschnitt mit korrekter Implementierung, Semantik-Tabelle
und Hinweis auf Gegentests aktualisiert.

---

### Fehler 2 — v4-Referenzen (Zeilen 278, 320, 328, 339–340)

| Zeile | Vorher | Nachher |
| --- | --- | --- |
| 278 | `Pflichtenheft v4 §5 / Regelwerk v4 §16` | v5 |
| 320 | `Pflichtenheft v4 §16 Testpflicht-Abdeckung` | v5 |
| 328 | `Regelwerk v4 §21` | v5 |
| 339–340 | `pflichtenheft_v4.md`, `regelwerk_v4.md` | v5 |

**Behobene Korrektur:** Alle vier Stellen auf v5 aktualisiert.

---

### Fehler 3 — Testanzahlen veraltet (Zeilen 303, 312, 313)

| Zeile | Vorher | Nachher |
| --- | --- | --- |
| 303 | `Gesamt tests/application/ – 107 Tests` | **109 Tests** |
| 312 | `pytest tests/domain/ # 63 Tests` | **67 Tests** |
| 313 | `pytest tests/application/ # 107 Tests` | **109 Tests** |

Ursachen:
- Domain: +4 Tests aus `phase2_coding_aufgabe` (Erfolgsfall-Tests in `test_booking_rules.py`)
- Application: +2 Tests aus `phase3_coding_aufgabe` (`test_fake_unit_of_work.py`)

Verifiziert: `pytest tests/application/ --collect-only` → 109 Tests.

**Behobene Korrektur:** Alle drei Zähler aktualisiert; `test_fake_unit_of_work.py`
in der Testverteilungstabelle ergänzt.

---

## phase3_coding_aufgabe.md

**Befund: Inhaltlich korrekt und vollständig implementiert.**

- `FakeUnitOfWork.__exit__` nutzt `not self.committed` ✓ (Zeile 398 in `fakes.py` bestätigt)
- `tests/application/test_fake_unit_of_work.py` mit 2 Gegentests vorhanden ✓
- Alle Akzeptanzkriterien erfüllt ✓

---

## Zusammenfassung

| Dokument | Problem | Status |
| --- | --- | --- |
| `phase3_planung.md` Z. 48–49 | `FakeUnitOfWork.__exit__` veraltete Semantik | ✓ behoben |
| `phase3_planung.md` Z. 278, 320, 328, 339–340 | v4-Referenzen → v5 | ✓ behoben |
| `phase3_planung.md` Z. 303, 312, 313 | Testanzahlen 107/63 → 109/67 | ✓ behoben |
| `phase3_coding_aufgabe.md` | Korrekt, vollständig implementiert | ✓ |
