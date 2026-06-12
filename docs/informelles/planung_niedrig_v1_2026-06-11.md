# Planung: Abarbeitung „niedrig"-Priorität
## Grundlage: `docs/claude_coding/claude_code_prompt_niedrig_arbeitszeit_v1_2026-06-11_20-15.md`

**Datum:** 2026-06-11

**Wichtiger Vorbehalt aus Prompt:** Der „niedrig"-Block im Audit-Bericht war nicht direkt
sichtbar. Nur Punkte, die sich belastbar aus Selbstcheck-Hinweisen und Evidenzgrenzen
ableiten lassen, werden bearbeitet. Kein fiktiver Scope wird erfunden.

---

## 0. Ist-Stand-Analyse

### 0.1 Identifizierte Spannungen in den Planungsdokumenten

**Spannung 1 — phase3_planung.md vs. planung_gesamt.md:**
- phase3_planung.md Z.102–103, 112–113, 257, 273: `approve_supplement.py` und
  `reject_supplement.py` explizit als „Phase 4, in Phase 3 vorimplementiert" gekennzeichnet
- planung_gesamt.md Phase-3-Abschnitt: kein expliziter Hinweis auf diese vorgezogene
  Einführung — für Lesende ohne phase3_planung.md-Kenntnisse potenziell irritierend
- Art: Lesbarkeits-Spannung, kein inhaltlicher Widerspruch

**Spannung 2 — phase4_planung.md: Integration-Testzählung „165 Tests":**
- phase4_planung.md nennt 165 Integrationstests (Z.644)
- tests/integration/ enthält 16 Dateien, darunter nachträglich hinzugefügte:
  `test_user_accounts.py`, `test_init_db.py`, `test_device_event_booking.py`,
  `test_time_monitor.py` — diese laufen heute unter „Phase 4"-Integration,
  gehören aber teils zu Phase 5+ oder wurden nach Phase-4-Abschluss ergänzt
- Art: Historische Zuordnungsspannung; phase4_planung.md-Zahl ist korrekt
  (sie wurde aktualisiert), aber die Phasenzuordnung einzelner Test-Dateien ist offen

**Spannung 3 — phase5_planung.md: historische und heutige Testzählstände gemischt:**
- Z.257: `361 Tests grün (historischer Stand Phase 5/Schritt 2; heutiger Gesamtstand: 395 Tests)`
  — aktuell noch ohne klares Label (wird durch mittel-Aufgabe präzisiert)
- Z.375: `(Schätzung: ~8 Tests)` — wird durch mittel-Aufgabe präzisiert
- Art: Lesbarkeits-Spannung

**Spannung 4 — phase2_planung.md: V4-Bezüge-Überschrift:**
- Z.327: `## V4-Bezüge und organisatorische Auflagen` — Inhalt referenziert v5
- Art: Terminologische Unstimmigkeit, wird durch mittel-Aufgabe behoben

**Spannung 5 — tests/integration/ Phasenzuordnung:**
- phase4_planung.md listet nur 8 der 16 Integration-Test-Dateien im Zielstruktur-Abschnitt
- Nicht explizit gelistete Dateien: test_user_accounts.py, test_init_db.py,
  test_device_event_booking.py
- Historische Zuordnung dieser drei Dateien zu einer Phase: nicht direkt aus
  phase4_planung.md ableitbar

### 0.2 Identifizierte Evidenzgrenzen im Repository

Aus `planung_gesamt.md` V5-/V2-Abgleich (Z.249–260) bereits explizit gelistet:

1. **Betriebsdokumentation** — „schriftlich verabschiedet" nicht belegbar aus Repo
   (teilweise adressiert durch betriebsdokumentation-Aufgabe aus hoch-Priorität)
2. **Revisionsfeste Testmatrix** — erstellt (2026-06-11), DoD erfüllt
3. **device_events/device_event_id** — implementiert (2026-06-11), DoD erfüllt
4. **Organisatorische Rollenzuweisung** — außerhalb des Repos, kein Nachweis möglich
5. **AV-Vertrag, Schlüsselverwaltung, TOM, Rotationskonzept** — außerhalb des Repos
6. **IT-Sicherheitskonzept §75b SGB V** — außerhalb des Repos
7. **Cloud-Backup mit Verschlüsselung** — technische Grundlage vorhanden,
   Entscheidung und Organisation außerhalb des Repos

Zusätzliche, nicht in planung_gesamt.md gelistete Evidenzgrenzen:
8. **Reale Hardware-Smoke-Tests** — phase4_planung.md erwähnt „Reale Gerätebesonderheiten
   bis Phase 5 durch Smoke-Tests auf Zielhardware zu verifizieren"; kein Nachweis im Repo
9. **Passwort-Änderung für Benutzerkonten** — kein CLI-Befehl und kein Test im Repo;
   Pflichtenheft v5 §7.9 sagt „änderbar", ob Passwort dazu gehört: nicht entscheidbar
10. **Formale Freigabe als Betriebssystem** — kein Freigabedokument im Repo

---

## Teil A — Klarstellungsnotiz planen

### A.1 Zu erstellende Datei

**`docs/informelles/audit_klarstellungen_niedrig_v1.md`**

Inhalt:
- Für jede der 5 Spannungen (0.1): betroffene Datei(en), missverständliche Stelle,
  warum irritierend, Lesbarkeits- vs. inhaltliche Spannung, ob Änderung nötig
- Spannungen 1–4 werden durch mittel/niedrig-Aufgaben adressiert → als solche markieren
- Spannung 5 (tests/integration/-Zuordnung): offen markieren

### A.2 Minimale Ergänzungen in Planungsdokumenten (A3)

**planung_gesamt.md:**
- Im Phase-3-Abschnitt: knappen Hinweis auf vorimplementierte Phase-4-Use-Cases ergänzen
  (analog zu phase3_planung.md, dort bereits klar benannt)

**phase4_planung.md und phase5_planung.md:**
- Prüfen ob kurze Verweise auf audit_klarstellungen_niedrig_v1.md sinnvoll sind
- Entscheidung erst nach Erstellung der Klarstellungsnotiz

---

## Teil B — Evidenzgrenzen-Notiz planen

### B.1 Zu erstellende Datei

**`docs/informelles/audit_evidenzgrenzen_v1.md`**

Struktur:
1. Titel, Datum
2. Zweck und Abgrenzung (explizit: ersetzt keine höheren Prioritäten)
3. Artefaktbasis
4. Belegt (technisch im Code nachweisbar)
5. Nur teilweise belegt (technische Grundlage vorhanden, organisatorische Seite offen)
6. Nicht entscheidbar (Punkte 4, 5, 6, 8, 9, 10 aus 0.2)
7. Erforderliche externe Nachweise
8. Abgrenzung zu offenen Punkten aus kritisch/hoch/mittel

### B.2 Kategorisierung der Evidenzgrenzen

| # | Punkt | Kategorie |
|---|---|---|
| 1 | Betriebsdokumentation formal verabschiedet | technisch vorbereitet, organisatorisch nicht belegt |
| 2 | Revisionsfeste Testmatrix | erledigt (2026-06-11) |
| 3 | device_events | erledigt (2026-06-11) |
| 4 | Organisatorische Rollenzuweisung | außerhalb des Repositorys organisatorisch zu klären |
| 5 | AV-Vertrag, TOM, Schlüsselverwaltung | außerhalb des Repositorys organisatorisch zu klären |
| 6 | IT-Sicherheitskonzept §75b SGB V | außerhalb des Repositorys organisatorisch zu klären |
| 7 | Cloud-Backup mit Verschlüsselung | technisch vorbereitet, organisatorisch nicht belegt |
| 8 | Hardware-Smoke-Tests auf Zielhardware | im Audit nicht vollständig verifiziert |
| 9 | Passwort-Änderung für Benutzerkonten | nicht entscheidbar auf Basis der vorliegenden Artefakte |
| 10 | Formale Betriebsfreigabe | externer Freigabenachweis fehlt |

### B.3 planung_gesamt.md-Verweis (B5)

planung_gesamt.md hat bereits Z.249–260 eine strukturierte Liste offener Punkte.
Prüfung: Verweis auf `audit_evidenzgrenzen_v1.md` sinnvoll? → ja, als knappe
Referenz am Ende des V5-/V2-Abgleich-Abschnitts.

---

## Ausführungsreihenfolge

```
1. audit_klarstellungen_niedrig_v1.md erstellen (A1)
2. planung_gesamt.md: knapper Hinweis vorimplementierte Phase-4-Use-Cases (A3)
3. audit_evidenzgrenzen_v1.md erstellen (B1)
4. planung_gesamt.md: Verweis auf audit_evidenzgrenzen_v1.md (B5)
5. abarbeitung_niedrig_abschlussnotiz_v1.md erstellen
6. Tests laufen (keine Codeänderungen)
7. Commit + Push
```

---

## Definition of Done (6 Kriterien aus Prompt)

1. ☐ Selbstcheck-Spannungen in audit_klarstellungen_niedrig_v1.md aufbereitet
2. ☐ Evidenzgrenzen in audit_evidenzgrenzen_v1.md dokumentiert
3. ☐ Dokumentergänzungen minimal-invasiv
4. ☐ Unentscheidbarkeit explizit benannt
5. ☐ Kein Eindruck, höhere Prioritäten seien damit geschlossen
6. ☐ Abschlussnotiz dokumentiert Änderungen, Prüfungen, Restoffenheiten
