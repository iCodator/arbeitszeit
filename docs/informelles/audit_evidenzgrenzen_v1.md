# Audit-Evidenzgrenzen

**Datum:** 2026-06-11  
**Grundlage:** `docs/claude_coding/claude_code_prompt_niedrig_arbeitszeit_v1_2026-06-11_20-15.md`

**Zweck:** Dieses Dokument dokumentiert systematisch, was aus den Repository-Artefakten
belegt, nur teilweise belegt oder nicht entscheidbar ist. Es ersetzt keine offenen
Punkte aus kritisch-, hoch- oder mittel-Priorität und behauptet keine Freigaben.

**Abgrenzung:** Punkte, die durch kritisch/hoch/mittel-Aufgaben geschlossen wurden
oder werden, sind als solche markiert.

---

## Artefaktbasis

- `planung_gesamt.md` V5-/V2-Abgleich (Z.249–260)
- `phase4_planung.md`, `phase5_planung.md`
- `pflichtenheft_arbeitszeit_v5.md`, `regelwerk_arbeitszeit_v5.md`
- `docs/anlage_einhaltung_pflichtenheft_v2.md`

---

## Durch Repository-Artefakte belegt

| Thema | Kategorie | Belegbasis | Aussagegrenze |
| --- | --- | --- | --- |
| Buchungslogik (COME/GO/BREAK) | vollständig belegt | domain/tests: 406 Tests grün | Kein Nachweis realer Gerätenutzung |
| ArbZG-Prüfhilfen (§3/4/5) | vollständig belegt | compliance_checks.py + Tests | Ersetzt keine juristische Einzelfallprüfung |
| Backup/Restore-Mechanismus | vollständig belegt | backup_service.py + e2e-Tests | Operativer Einsatz nicht im Repo nachweisbar |
| Systemcheck | vollständig belegt | system_check.py + 17 Tests | Geräte-Check nur mit Simulator-Pfaden |
| Benutzerkontenverwaltung (ADMIN/REVIEWER/TECH) | vollständig belegt | user_accounts.py + 18 Tests | Formale Betriebsfreigabe nicht im Repo |
| device_events-Verkettung | vollständig belegt | Commit `0f20931` + 3 Tests | Nur mit SimulatedHardwareReader getestet |
| Revisionsfeste Testmatrix | erstellt (2026-06-11) | `testmatrix_revision_v1.md` | Formale Abnahme nicht im Repo |

---

## Nur teilweise belegt

| Thema | Kategorie | Belegbasis | Aussagegrenze | Folgefrage |
| --- | --- | --- | --- | --- |
| Betriebsdokumentation | technisch vorbereitet, organisatorisch nicht belegt | `betriebsdokumentation_arbeitszeit_v1_1.md` (geplant durch hoch-Aufgabe) | Formale Verabschiedung fehlt im Repo | Wer gibt das Dokument frei? |
| NAS-Backup-Funktion | technisch vorbereitet, organisatorisch nicht belegt | backup_service.py sync_to_nas(); E2E-Tests mit Mock-NAS | Echter NAS-Pfad nur als Betriebsentscheidung dokumentiert | Wurde NAS-Sync im Betrieb getestet? |
| Exportverzeichnis-Schutz | technisch vorbereitet, organisatorisch nicht belegt | setup.py setzt export.export_dir; Zugriffsrechte OS-Ebene nicht im Repo | Dateisystem-Rechte außerhalb des Codes | Wurden Zugriffsrechte auf dem Zielsystem gesetzt? |
| Restore-Freigabe | technisch vorbereitet, organisatorisch nicht belegt | restore_from() implementiert und getestet | Berechtigung zur Restore-Durchführung ist Betriebsregel | Wer ist im Betrieb berechtigt? |

---

## Nicht entscheidbar auf Basis der vorliegenden Artefakte

| Thema | Kategorie | Belegbasis | Aussagegrenze | Folgefrage |
| --- | --- | --- | --- | --- |
| Passwort-Änderung als Bestandteil von „änderbar" (PH v5 §7.9) | nicht entscheidbar | Kein CLI-Befehl `users change-password` vorhanden; PH §7.9 nennt „änderbar" ohne Spezifikation | Ob Passwort-Änderung zum Scope gehört, ist aus Artefakten nicht eindeutig entscheidbar | Muss §7.9 „änderbar" explizit Passwort-Änderung einschließen? |
| Organisatorische Rollenzuweisung in der Praxis | außerhalb des Repositorys organisatorisch zu klären | Nur als Anforderung in PH §15 / RW §22 | Kein Nachweis der Festlegung im Repo | Wer ist konkret Admin, Prüfer, technische Betreuung? |
| Hardware-Smoke-Tests auf Zielhardware | im Audit nicht vollständig verifiziert | phase4_planung.md: „bis Phase 5 durch Smoke-Tests auf Zielhardware zu verifizieren" | Keine Smoke-Test-Protokolle im Repo | Wurden Smoke-Tests auf dem realen Terminal-Gerät durchgeführt? |
| Formale Betriebsfreigabe als System | externer Freigabenachweis fehlt | Kein Freigabedokument im Repo | Technisches System vorhanden; formale Freigabe fehlt | Welche Stelle gibt das System für den Produktivbetrieb frei? |
| AV-Vertrag Cloud-Backup | außerhalb des Repositorys organisatorisch zu klären | planung_gesamt.md Z.258 nennt AV-Vertrag als erforderlich | Kein AV-Vertrag im Repo | Wurde Cloud-Backup entschieden? Falls ja, AV-Vertrag abgeschlossen? |
| IT-Sicherheitskonzept §75b SGB V | außerhalb des Repositorys organisatorisch zu klären | planung_gesamt.md Z.258 | Einbindung in Praxis-IT-Sicherheitskonzept außerhalb des Repos | Ist das System in das Sicherheitskonzept der Praxis eingebunden? |
| Schlüsselverwaltung, TOM, Rotationskonzept | außerhalb des Repositorys organisatorisch zu klären | planung_gesamt.md Z.257 | Nur als Anforderung genannt | Wurden diese Unterlagen für die Praxis erstellt? |

---

## Erforderliche externe Nachweise für weitergehende Entscheidungen

1. Formale Betriebsfreigabe durch berechtigte Person/Stelle
2. Organisatorische Rollenzuweisung (wer ist Admin, Prüfer, technische Betreuung)
3. AV-Vertrag, falls Cloud-Backup genutzt wird
4. Nachweis Smoke-Tests auf Zielhardware
5. Einbindung in IT-Sicherheitskonzept der Praxis (§75b SGB V)
6. Aufbewahrungs- und Löschkonzept (schriftlich verabschiedet)

---

## Abgrenzung zu offenen Punkten höherer Priorität

- **kritisch:** device_events und Testmatrix — beide 2026-06-11 geschlossen ✓
- **hoch:** Nachtragsmatrix und Betriebsdokumentation — in Bearbeitung (geplant)
- **mittel:** Terminologie und Migrationsübersicht — 2026-06-11 abgeschlossen ✓
- **niedrig (dieses Dokument):** Transparenz-Dokumentation — keine Inhaltsentscheidungen
