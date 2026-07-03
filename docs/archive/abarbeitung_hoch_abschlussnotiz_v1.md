# Abschlussnotiz: Abarbeitung „hoch"-Priorität

**Datum:** 2026-06-11  
**Grundlage:** `docs/informelles/planung_hoch_v1_2026-06-11.md`

---

## Deliverables: Soll vs. Ist

| Deliverable | Soll | Ist | Status |
| --- | --- | --- | --- |
| `nachtragsmatrix_phasen_v1.md` | Phasenübergreifende Nachtragsmatrix, ca. 40+ Zeilen | erstellt (44 Artefakte) | ✓ |
| `betriebsdokumentation_arbeitszeit_v1_1.md` | Formale Betriebsdokumentation, 12 Abschnitte | erstellt | ✓ |
| Verweise in `planung_gesamt.md` | Kurze Verweise auf neue Dokumente | ergänzt | ✓ |
| Verweise in `phase4_planung.md` | Schritt 7 + Schritt 9 | ergänzt | ✓ |
| Verweise in `phase5_planung.md` | Terminal-UI-Abschnitt | ergänzt | ✓ |
| `abarbeitung_hoch_abschlussnotiz_v1.md` | Diese Datei | erstellt | ✓ |

---

## Inhalt Nachtragsmatrix (`nachtragsmatrix_phasen_v1.md`)

- 44 Artefakte (Migrationen, Scripts, Domain/Application/Infrastructure/Presentation,
  Testmodule)
- Alle Einträge mit mindestens einer Belegstelle aus Phasenplänen
- Erkannte Phasenverschiebungen:
  - **Vorgezogen (Phase 3 statt 4):** approve_supplement.py, reject_supplement.py,
    zugehörige Tests, Ruhezeit- und Rollenprüfung in book_time.py
  - **Nachgezogen:** Migrations 0003–0006, device_event_id-Produktionspfad,
    restore_exports, reactivate/change-role/bootstrap, setup_vollstaendig()
  - **Spätere Testergänzungen:** test_migrations.py, test_booking_rules.py,
    test_booking_flow.py, test_backup.py
  - **Dokumentationskorrekturen:** v4→v5, ValidationResult entfernt
- Eine offene Phasenzuordnung (test_init_db.py) explizit als nicht entscheidbar
  ausgewiesen

---

## Inhalt Betriebsdokumentation (`betriebsdokumentation_arbeitszeit_v1_1.md`)

12 Abschnitte:
1. Systemübersicht
2. Ersteinrichtung (init_db, setup, bootstrap, systemcheck)
3. Terminal-UI-Betrieb (Ablauf, Zeitmonitor, Simulator)
4. Admin-CLI (Benutzer, Mitarbeiter, Buchungen, Exporte)
5. Backup-Betrieb (lokal, NAS-Spiegelung, Restore)
6. Export-Betrieb (Aufbewahrungsfristen, Zugriffsschutz)
7. Systemcheck
8. Rollenkonzept
9. Hardware-Verkettung (device_events)
10. Migrationsstand
11. Freigabefähigkeitsstatus (13 Punkte, klar nach technisch/organisatorisch getrennt)
12. Abgrenzung (kein Freigabedokument, keine DSFA)

---

## Definition of Done — Selbstcheck

| Kriterium | Erfüllt |
| --- | --- |
| Belegorientierte Nachtragsmatrix existiert | ✓ |
| Historische Zielphase, tatsächliche Einführungsphase, spätere Änderungen pro Artefakt | ✓ |
| Vorgezogen/nachgezogen/Doku-Korrekturen erkennbar | ✓ |
| Eigenständige Betriebsdokumentation existiert | ✓ |
| Klare Trennung Technik / Regel / Auflage / Unentscheidbarkeit | ✓ |
| Planungsdokumente um kurze Verweise ergänzt | ✓ |
| Abschlussnotiz mit Restpunkten und Evidenzgrenzen (diese Datei) | ✓ |
| Nichts als „geregelt" / „freigegeben" dargestellt ohne Repo-Beleg | ✓ |

---

## Restpunkte und Evidenzgrenzen

Folgende Punkte wurden in der Betriebsdokumentation als **organisatorisch offen**
ausgewiesen und sind nicht aus Repo-Artefakten schließbar:

1. Formale Betriebsfreigabe durch berechtigte Stelle
2. Konkrete Rollenzuweisung (wer ist Admin, Reviewer, Tech)
3. Nachweis Smoke-Tests auf Zielhardware (Protokoll fehlt im Repo)
4. AV-Vertrag falls Cloud-Backup genutzt wird
5. Einbindung in IT-Sicherheitskonzept der Praxis (§75b SGB V)
6. OS-seitige Zugriffsrechte auf Exportverzeichnis

---

## Abgrenzung zu anderen Prioritäten

- **kritisch:** geschlossen ✓ (device_events + Testmatrix)
- **hoch (dieses Dokument):** geschlossen ✓
- **mittel:** geschlossen ✓
- **niedrig:** geschlossen ✓

Alle vier Prioritätsstufen aus den Audit-Prompts (2026-06-11) sind abgearbeitet.
