# Prüfbericht: phase1_planung.md und phase1_coding_aufgabe.md

**Prüfgrundlage:** `docs/informelles/planung_gesamt.md` (Stand: 2026-06-11)
**Geprüfte Dokumente:**
- `docs/informelles/phase1_planung.md`
- `docs/informelles/phase1_coding_aufgabe.md`

---

## phase1_planung.md

### Fehler 1 — `requires-python` widersprüchlich (Zeile 34 vs. 42)

Zeile 34: `requires-python = ">=3.11,<3.13"`
Zeile 42: `.python-version: Pinnt auf 3.14 für lokale Entwicklung`

Die aktuelle `pyproject.toml` sagt `>=3.14,<3.15`. Zeile 34 war ein nicht aktualisiertes
historisches Artefakt aus der Phase-1-Entstehungszeit.

**Behobene Korrektur:** `">=3.11,<3.13"` als historischen Stand markiert mit Hinweis auf
heute gültiges `">=3.14,<3.15"`.

---

### Fehler 2 — Indizesanzahl und -liste falsch (Zeile 161)

Das Dokument sagte `Indizes (11):` und listete 14 Einträge. Das reale Schema
`0001_schema.sql` hat **17 Indizes**. Fehlend waren:

- `idx_work_schedule_versions_scope_weekday_valid_from`
- `idx_audit_log_object_event_at`
- `idx_audit_log_employee_event_at`

**Behobene Korrektur:** Zähler auf 17 korrigiert, alle drei fehlenden Indizes ergänzt.

---

### Fehler 3 — V4-Bezüge-Abschnitte noch auf v4 (Zeilen 299–329)

Der Abschnitt „V4-Bezüge" (Zeile 299) und der Footer-Block (Zeilen 321–324)
referenzierten noch Pflichtenheft v4 und Regelwerk v4 sowie die alten Dateinamen
`pflichtenheft_arbeitszeit_v4.md` und `regelwerk_arbeitszeit_v4.md`, obwohl alle
anderen Planungsdokumente bereits auf v5 umgestellt waren.

**Behobene Korrektur:** `V4-Bezüge` → `V5-Bezüge`; alle §-Referenzen und Dateinamen
auf v5 aktualisiert; Rollentrennung-Abschnitt um Verweis auf §7.9 und §16a
(Benutzerkontenverwaltung) ergänzt.

---

### Lücke — `scripts/init_db.py`-Beschreibung unvollständig (Zeilen 251–255)

Das Dokument beschrieb `init_db.py` nur mit den ursprünglichen vier Aufgaben. Die
später implementierte `setup_vollstaendig()`-Prüfung (Fälle A/B/C) und das
`--db`-Argparse-Flag wurden nicht erwähnt.

**Behobene Korrektur:** Beschreibung um Fälle A/B/C und `--db`-Flag ergänzt.

---

## phase1_coding_aufgabe.md

**Befund: Inhaltlich korrekt.**

Die beschriebene Aufgabe (`init_db.py` prüft Setup-Vollständigkeit) ist vollständig
implementiert. `scripts/init_db.py` enthält `setup_vollstaendig()`, die drei Fälle A/B/C
sowie die korrekte Abschlussmeldung in `setup.py`.

Das Dokument beschreibt akkurat, was getan werden sollte und getan wurde. Es enthält
keine kritischen Fehler.

---

## Zusammenfassung

| Dokument | Problem | Schwere | Status |
| --- | --- | --- | --- |
| `phase1_planung.md` Zeile 34 | `requires-python` ohne historische Markierung | gering | ✓ behoben |
| `phase1_planung.md` Zeile 161 | Indizes: „11"/14 gelistet, tatsächlich 17 | mittel | ✓ behoben |
| `phase1_planung.md` Zeilen 299–324 | v4-Referenzen statt v5 | mittel | ✓ behoben |
| `phase1_planung.md` Zeilen 251–255 | `init_db.py` Setup-Check fehlte | gering | ✓ behoben |
| `phase1_coding_aufgabe.md` | Korrekt | — | — |
