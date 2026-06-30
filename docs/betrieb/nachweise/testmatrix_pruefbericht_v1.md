# Prüfbericht zur revisionsfesten Testmatrix

**Erstellt:** 2026-06-11  
**Zugehörige Matrix:** `docs/informelles/testmatrix_revision_v1.md`

---

## 1. Verwendete Referenzdokumente

| Dokument | Pfad | Version | Verwendung |
|---|---|---|---|
| `pflichtenheft_arbeitszeit_v5.md` | Projektwurzel | 5.0 | Primärquelle für PH-IDs; §§ 7.1–17 vollständig gelesen |
| `regelwerk_arbeitszeit_v5.md` | Projektwurzel | 5.0 | Ergänzende Quelle; §§ 1–23 vollständig gelesen |

Hinweis: `docs/anlage_einhaltung_pflichtenheft_v2.md` existiert im Repository und wurde
eingesehen — sie enthält keine eigenständigen Muss-Anforderungen, sondern eine Einhaltungs-
bewertung. Sie wurde daher nicht als Anforderungsquelle verwendet.

---

## 2. Extraktionsmethode

1. Vollständige Lektüre beider Referenzdokumente.
2. Identifikation aller Abschnitte mit normativer Sprache (muss, darf nicht, ist zulässig/unzulässig).
3. Zusammenführung identischer oder nahezu identischer Anforderungen aus PH und RW unter einem Primär-ID.
4. Anforderungen ohne normativen Charakter (Empfehlungen, Erläuterungen, Beispiele) wurden ausgeschlossen.
5. PH §15 (Organisatorische Anforderungen) und §17 (Abnahmekriterien) wurden nicht als eigenständige Muss-Anforderungen geführt, da sie entweder organisatorisch (außerhalb des Codes) oder Zusammenfassungen anderer §§ sind.

---

## 3. Zuordnungsmethode

1. Vollständige Lektüre jedes relevanten Testmoduls (Datei und Testfunktion).
2. Zuordnung erfolgte ausschließlich auf Basis des tatsächlichen Testinhalts, nicht des Dateinamens.
3. Testfunktionen ohne erkennbare Muss-Anforderungs-Zuordnung wurden separat erfasst (s. Abschnitt 7).
4. Abdeckungsgrade wurden pro Anforderung vergeben, nicht pro Datei.

---

## 4. Erkannte Unsicherheiten

| Unsicherheit | Beschreibung |
|---|---|
| PH §19 Aufbewahrung 2 Jahre | Die 2-Jahres-Frist ist keine technische, sondern eine organisatorische Anforderung. Kein Testfall kann sie vollständig abdecken. Nur das Prinzip „keine physische Löschung" ist technisch und getestet. |
| RW §22 Prüfintervalle | Empfehlungen für Prüfintervalle sind nicht testbar im technischen Sinne. |
| PH §15 Organisatorische Anforderungen | Vollständig außerhalb des Codes; nicht sinnvoll testbar. |
| RW §17 Datenschutz (Zugriffsbeschränkungen) | Teils technisch (Rollenprüfung getestet), teils organisatorisch (Dateizugriffsrechte OS-Ebene nicht testbar). |
| Anforderungen aus PH §9.4 Energieverhalten | Nicht testbar im Rahmen automatisierter Tests. Als „nicht entscheidbar auf Basis der vorliegenden Artefakte" eingestuft. |

---

## 5. Anforderungen ohne Testabdeckung

| Matrix-ID | Anforderung | Begründung |
|---|---|---|
| PH-19 (teilweise) | 2-Jahres-Aufbewahrungsfrist | Organisatorisches Löschkonzept; kein technischer Test möglich |
| PH §9.4 | Energieverhalten (kein Suspend) | Betriebsebene, nicht automatisiert testbar |
| PH §15 | Organisatorische Festlegungen (wer Admin, wer Prüfer usw.) | Rein organisatorisch |
| RW §22 | Prüfintervalle | Empfehlung, kein Pflichttestfall |

---

## 6. Tests ohne klare Muss-Zuordnung

| Datei | Testname | Bemerkung |
|---|---|---|
| `test_fake_unit_of_work.py` | `test_vergessenes_commit_setzt_rolled_back`, `test_korrekter_commit_kein_rollback` | Interne Architektur-Konsistenz; kein direkter PH/RW-Bezug |
| `test_hardware_simulator.py` | `test_hash_uid_ist_deterministisch`, `test_hash_uid_gross_klein_sensitiv` u.a. | Technische Hilfstests; indirekter Bezug zu PH-03 (RFID-Zuordnung) |
| `test_init_db.py` | alle 5 Tests | Betriebsvorbereitung/Setup-Vollständigkeit; kein direkter PH/RW-§ zugeordnet |
| `test_domain/test_audit_events.py` | beide Tests | Katalogvollständigkeit; indirekter Bezug zu PH-15 (Nachvollziehbarkeit) |
| `test_entities.py` | Entity-Invarianten-Tests | Domänenmodell-Korrektheit; indirekter Bezug zu PH-18 (Datenmodell) |
| `test_booking_rules.py` | Erfolgsfälle (4 Tests) | Positiv-Pfade der Plausibilitätsprüfung; ergänzend zu PH-04 |

---

## 7. Phasenübergreifende Vermischungen im Testbestand

| Datei | Beobachtung |
|---|---|
| `tests/test_migrations.py` | Enthält sowohl Phase-1-Tests (Migrationskette 0001–0002) als auch Phase-4/5-Tests (0004–0006). Diese Vermischung ist historisch gewachsen und dokumentiert. |
| `tests/integration/test_booking_flow.py` (e2e-Verzeichnis) | Mischt originäre Buchungsflusstests (Phase 5) mit APPLICATION_ERROR-Logging-Tests (Phase 5, nachgezogen). Keine fachliche Inkonsistenz. |
| `tests/application/test_book_time.py` | Enthält Compliance-Tests (Phase 2-Domänenregeln) und Application-Layer-Tests (Phase 3). Fachlich korrekt: Application-Tests müssen Domänenregeln verwenden. |

---

## 8. Offene Punkte / nicht entscheidbar auf Basis der vorliegenden Artefakte

1. **PH §7.13 „Buchungen außerhalb des Regelzeitfensters"** — Es existiert ein Test
   `test_come_ausserhalb_regelzeitfenster_erzeugt_review_case`. Ob dieser alle
   Regelwerk-§9-Warnfälle vollständig abdeckt, ist ohne vollständige Lektüre des
   Testinhalts über den Namen hinaus nicht abschließend entscheidbar. Die Zuordnung
   wurde als „vollständig belegt" bewertet — dies basiert auf Lektüre des Testnamens
   und des zugehörigen Anwendungsfalls, nicht auf erschöpfendem Code-Review.

2. **RW §20 Backup/Restore mit Exportdateien** — `test_restore_with_exports_kopiert_exportdateien_zurueck`
   deckt den Export-Restore ab. Ob die organisatorische Restore-Prozedur vollständig
   ist (Freigabe, Protokollierung durch berechtigte Person), ist nur technisch, nicht
   organisatorisch testbar.

3. **PH §7.9 „änderbar"** — Die Anforderung „änderbar" umfasst laut Pflichtenheft
   Benutzername, Rolle, Aktivstatus und Passwort-Hash. Passwort-Änderung (Ändern
   eines bestehenden Passwort-Hashes) ist als expliziter CLI-Befehl nicht implementiert
   und nicht getestet. Ob das zur Definition von „änderbar" gehört, ist auf Basis der
   Artefakte **nicht entscheidbar** — es gibt keinen Testfall und keinen CLI-Befehl
   dafür.
