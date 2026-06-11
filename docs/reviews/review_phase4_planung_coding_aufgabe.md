# Prüfbericht: phase4_planung.md und phase4_coding_aufgabe.md

**Prüfgrundlage:** `docs/informelles/planung_gesamt.md` (Stand: 2026-06-11)
**Geprüfte Dokumente:**
- `docs/informelles/phase4_planung.md`
- `docs/informelles/phase4_coding_aufgabe.md`

---

## phase4_planung.md

### Fehler 1 — v4-Referenzen durchgehend (25+ Stellen)

Phase 4 enthielt die meisten v4-Referenzen aller Phasenpläne. Betroffen waren:

**§-Nummern mit Verschiebung** (v5 führte §7.9 Benutzerverwaltung ein):

| Vorher | Nachher |
| --- | --- |
| `V4 §7.9 Pflichtanforderung` (Zeile 418) | `V5 §7.10 Pflichtanforderung` |
| `Pflichtenheft v4 §7.11` (Zeile 541) | `Pflichtenheft v5 §7.12` |
| `Pflichtenheft v4 §7.12` (Zeilen 560, 565) | `Pflichtenheft v5 §7.13` |

**Globale Ersetzungen** (§-Nummern bleiben gleich):
- Alle `Pflichtenheft v4` → `Pflichtenheft v5`
- Alle `Regelwerk v4` → `Regelwerk v5`
- Alle `V4 §` → `V5 §`
- Abschnittsüberschrift `V4-Bezüge` → `V5-Bezüge`
- Footer-Dateinamen `pflichtenheft_v4.md`, `regelwerk_v4.md` → v5

**Behobene Korrektur:** Alle Stellen aktualisiert.

---

### Fehler 2 — Testanzahlen durchgehend veraltet (Zeilen 3, 156, 385, 630–635)

| Stelle | Vorher | Nachher |
| --- | --- | --- |
| Zeile 3 (Kopfzeile) | `369 Tests grün` | `395 Tests grün` |
| Zeile 156 (Dateibaum) | `test_backup.py 19 Tests` | `22 Tests` |
| Zeile 385 | `19 e2e-Tests` | `22 e2e-Tests` |
| Zeile 630 | `tests/test_migrations.py – 11 Tests` | `12 Tests` |
| Zeile 631 | `tests/domain/ – 63 Tests` | `67 Tests` |
| Zeile 632 | `tests/application/ – 107 Tests` | `109 Tests` |
| Zeile 633 | `tests/integration/ – 142 Tests` | `165 Tests` |
| Zeile 634 | `tests/e2e/ – 19 Tests` | `22 Tests` |
| Zeile 635 | `369 Tests grün gesamt` | `395 Tests grün gesamt` |

Ursachen der Differenzen:
- +1 Migrations-Test (phase2/phase3 Wachstum)
- +4 Domain-Tests (phase2_coding_aufgabe: Erfolgsfall-Tests)
- +2 Application-Tests (phase3_coding_aufgabe: FakeUnitOfWork-Tests)
- +23 Integration-Tests (user_accounts, init_db, und weitere)
- +3 E2E-Tests (phase4_coding_aufgabe: restore_exports)

**Behobene Korrektur:** Alle Zähler auf aktuelle Werte aktualisiert; Hinweise auf
jeweilige Quelle ergänzt.

---

### Fehler 3 — `restore_from()` ohne restore_exports-Dokumentation (um Zeile 385)

Die `phase4_coding_aufgabe` wurde implementiert: `restore_from()` hat nun einen
optionalen Parameter `restore_exports: bool = False`. Das war in phase4_planung.md
nicht dokumentiert.

**Behobene Korrektur:** Hinweis auf `restore_exports`-Parameter und 3 neue Tests
bei den E2E-Test-Zählern ergänzt.

---

## phase4_coding_aufgabe.md

**Befund: Inhaltlich korrekt und vollständig implementiert.**

- `restore_from(backup_path, *, restore_exports=False)` implementiert ✓
- `shutil.copytree`-Block für Export-Restore vorhanden ✓
- 3 neue E2E-Tests in `tests/e2e/test_backup.py` (19 → 22) ✓
- Alle Akzeptanzkriterien erfüllt ✓

---

## Zusammenfassung

| Dokument | Problem | Status |
| --- | --- | --- |
| `phase4_planung.md` 25+ Stellen | v4-Referenzen → v5 (inkl. §7.x-Verschiebungen) | ✓ behoben |
| `phase4_planung.md` 9 Stellen | Testanzahlen veraltet (369→395, etc.) | ✓ behoben |
| `phase4_planung.md` Zeile 385 | restore_exports-Parameter nicht dokumentiert | ✓ behoben |
| `phase4_coding_aufgabe.md` | Korrekt, vollständig implementiert | ✓ |
