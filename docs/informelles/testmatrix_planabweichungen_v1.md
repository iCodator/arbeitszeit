# Abweichungsliste: Planung vs. Testmatrix

**Erstellt:** 2026-06-11  
**Testmatrix:** `docs/informelles/testmatrix_revision_v1.md`  
**Geprüfte Planungsdokumente:** `planung_gesamt.md`, `phase1_planung.md`–`phase5_planung.md`

---

## Methodik

Für jeden relevanten Aspekt der Testmatrix wurde geprüft, ob die Planungsdokumente
konsistente, widersprüchliche oder präzisierende Aussagen enthalten. Widersprüche
wurden nicht geglättet, sondern explizit benannt.

---

## Abweichungsliste

| # | Betroffene Datei | Aussage in der Planung | Aussage der Testmatrix | Bewertung | Empfohlene Folgeaktion |
|---|---|---|---|---|---|
| 1 | `planung_gesamt.md` (vor diesem Commit) | „Die Transaktionskette für `device_events` ist noch nicht vollständig im Produktionspfad aktiv" | PH-04, PH-03: Kette ist implementiert und durch 3 Integrationstests belegt | Echter Widerspruch — inzwischen behoben durch Commit `b7b5ea7` | Erledigt: Planungsdokument aktualisiert |
| 2 | `phase5_planung.md` (vor diesem Commit) | „kein Produktionspfad schreibt derzeit device_events in die DB" | Testmatrix: vollständig implementiert | Echter Widerspruch — behoben | Erledigt: phase5_planung.md aktualisiert |
| 3 | `planung_gesamt.md` Testpflicht-Tabelle | Testpflicht-Tabelle nennt als ✗ offen: Bootstrap, Reaktivierung, Rollenwechsel, Audit-Log für diese | Testmatrix: alle vier vollständig belegt durch `test_user_accounts.py` | Nur Präzisierung — Planungsdok war veraltet | Planung bereits aktualisiert (frühere Session) |
| 4 | `phase2_planung.md` | Testverteilung nennt `test_booking_rules.py – 14 Tests` | Testmatrix ordnet 14 Tests zu: 10 Fehlerfälle (PH-04) + 4 Erfolgsfälle | Nur Präzisierung — Zahlen stimmen überein | Kein Handlungsbedarf |
| 5 | `planung_gesamt.md` | Testpflicht-Tabelle enthält kein Szenario für device_events-Verkettung | Testmatrix enthält 3 device_events-Tests (PH-03, PH-04) | Echter Widerspruch (Lücke in der Planung) | `planung_gesamt.md` Testpflicht-Tabelle um device_events-Szenarien ergänzen |
| 6 | `phase1_planung.md` | Gibt `scripts/init_db.py` als Phase-1-Artefakt aus; beschreibt `setup_vollstaendig()` als Erweiterung Phase 4+ | `test_init_db.py` (5 Tests) deckt `setup_vollstaendig()` ab; keine Muss-Anforderung aus PH/RW direkt zugeordnet | Nur Präzisierung — Tests testen interne Initialisierungslogik, keine PH-Anforderung | Kein Handlungsbedarf; Tests als technische Absicherung kategorisieren |
| 7 | `phase3_planung.md` | Testverteilung Phase 3: 109 Tests gesamt | `test_fake_unit_of_work.py` (2 Tests) ohne klare PH/RW-Zuordnung | Nur Präzisierung — Tests prüfen Architektur-Invariante | Als Architektur-Test kennzeichnen; kein Planungswiderspruch |
| 8 | Alle Phasenpläne | Keine Phasendokumentation adressiert PH §9.4 (Energieverhalten) | Testmatrix: kein Test dafür; markiert als nicht testbar | Nicht entscheidbar — organisatorisches/Betriebsthema | Ggf. in Betriebsdokumentation aufnehmen; kein Testbedarf |
| 9 | `planung_gesamt.md` | Offene Punkte: „revisionsfeste Testmatrix" als noch zu erstellen | Testmatrix: jetzt vorhanden | Echter Widerspruch — war offener Punkt, jetzt geschlossen | `planung_gesamt.md` offene Punkte aktualisieren |

---

## Zusammenfassung

| Typ | Anzahl |
|---|---|
| Echter Widerspruch (bereits behoben) | 3 (# 1, 2, 3) |
| Echter Widerspruch (noch offen) | 2 (# 5, 9) |
| Nur Präzisierung | 3 (# 4, 6, 7) |
| Nicht entscheidbar | 1 (# 8) |

---

## Empfohlene Folgeaktionen (noch offen)

**#5:** `planung_gesamt.md` Testpflicht-Tabelle um device_events-Testszenarien ergänzen:
- `test_erfolgreiche_buchung_schreibt_device_event_und_verknuepft_id` → neues Szenario
- `test_unknown_card_schreibt_device_event_aber_keine_buchung` → neues Szenario
- `test_fehler_im_device_event_insert_verhindert_buchung` → neues Szenario

**#9:** `planung_gesamt.md` offene Punkte aktualisieren:
- „revisionsfeste Testmatrix" aus der Liste offener Punkte als erledigt markieren.
