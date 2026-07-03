# Audit-Klarstellungen (Niedrig-Priorität)

**Datum:** 2026-06-11  
**Grundlage:** `docs/claude_coding/claude_code_prompt_niedrig_arbeitszeit_v1_2026-06-11_20-15.md`

**Zweck:** Dieses Dokument klärt Lesbarkeits-Spannungen und Terminologie-Inkonsistenzen,
die im Audit-Selbstcheck identifiziert wurden. Es verändert kein fachliches Sollbild
und schließt keine Punkte höherer Priorität.

---

## Artefaktbasis

- `docs/informelles/planung_gesamt.md`
- `docs/informelles/phase2_planung.md`
- `docs/informelles/phase3_planung.md`
- `docs/informelles/phase4_planung.md`
- `docs/informelles/phase5_planung.md`
- `tests/integration/` (Datei-Inventar)

---

## Erkannte Spannungen und Klarstellungen

### Spannung 1 — planung_gesamt.md Phase-3-Abschnitt: fehlender Hinweis auf vorimplementierte Phase-4-Use-Cases

**Betroffene Datei:** `planung_gesamt.md` (Phase-3-Abschnitt)

**Missverständliche Stelle:** Die Zielstruktur in planung_gesamt.md listet nur die
vier originären Phase-3-Use-Cases (manage_work_schedule, register_supplement,
correct_booking, book_time). `approve_supplement.py` und `reject_supplement.py`
erscheinen nicht.

**Warum irritierend:** Wer nur planung_gesamt.md liest, sieht diese beiden Use Cases
nicht in Phase 3, obwohl sie dort real vorimplementiert wurden.

**Klarstellung:** `phase3_planung.md` Z.102–103, 257–273 dokumentiert dies explizit.
`planung_gesamt.md` wurde um einen knappen Hinweis ergänzt (2026-06-11).

**Art:** Lesbarkeits-Spannung, kein inhaltlicher Widerspruch.

**Ergebnis:** Minimale Ergänzung in planung_gesamt.md; phase3_planung.md unverändert.

---

### Spannung 2 — phase4_planung.md: tests/integration/-Phasenzuordnung

**Betroffene Datei:** `phase4_planung.md`

**Missverständliche Stelle:** phase4_planung.md nennt in der Zielstruktur 8
Integration-Test-Dateien. Tatsächlich enthält `tests/integration/` 16 Dateien,
darunter `test_user_accounts.py`, `test_init_db.py`, `test_device_event_booking.py`,
die nach dem Phase-4-Abschluss ergänzt wurden.

**Warum irritierend:** Die Aussage „165 Tests (Phase 4)" stimmt als Gesamtzählung,
aber einzelne Testdateien sind nicht explizit Phase 4 zugeordnet.

**Klarstellung:** Die drei nicht gelisteten Dateien gehören zu:
- `test_user_accounts.py` — Phase 5 (users-Modul)
- `test_init_db.py` — Phase 4+ (setup_vollstaendig()-Erweiterung)
- `test_device_event_booking.py` — Phase 4 nachgezogen (Commit `0f20931`, 2026-06-11)

**Art:** Historische Zuordnungsspannung. Keine Änderung an phase4_planung.md
vorgenommen — die Zählung 165 ist korrekt, die Phasenzuordnung der einzelnen
Dateien ist in `nachtragsmatrix_phasen_v1.md` detaillierter dokumentiert.

---

### Spannung 3 — phase5_planung.md: historische und heutige Testzählstände

**Betroffene Datei:** `phase5_planung.md`

**Missverständliche Stellen:**
- Z.257: Mischung historischer Stand (361) und heutiger Stand (395) ohne Labels
- Z.375: überholte Schätzung „~8 Tests" für test_supplement_flow.py

**Klarstellung:** Behoben durch mittel-Aufgabe (2026-06-11):
- Z.257: „historischer Stand Phase 5/Schritt 2" / „heutiger Gesamtstand: 395 Tests"
- Z.375: „8 Tests" (exakter Wert, kein Schätzlabel mehr)

---

### Spannung 4 — phase2_planung.md: V4-Bezüge-Überschrift

**Betroffene Datei:** `phase2_planung.md`

**Missverständliche Stelle:** Z.327 Überschrift `## V4-Bezüge` bei v5-Inhalt.

**Klarstellung:** Behoben durch mittel-Aufgabe (2026-06-11):
→ `## V5-Bezüge und organisatorische Auflagen`

---

### Spannung 5 — tests/integration/ Phasenzuordnung dreier Dateien

**Betroffene Dateien:** `test_user_accounts.py`, `test_init_db.py`,
`test_device_event_booking.py`

**Missverständliche Stelle:** Keine Planungsdatei nennt diese drei Dateien explizit.

**Auswirkung:** Nur Lesbarkeits-Frage; fachlich ist die Testzählung korrekt.

**Ergebnis:** Keine Änderung. Detaillierte Phasenzuordnung in `nachtragsmatrix_phasen_v1.md`.

**Art:** Historische Zuordnung offen für diese drei Dateien.

---

## Nicht entscheidbar auf Basis der vorliegenden Artefakte

- Ob `test_init_db.py` formell Phase 4 oder Phase 4+ zuzuordnen ist — kein expliziter
  Planungseintrag vorhanden.
