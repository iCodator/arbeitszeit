# Migrationsübersicht — Einordnungsnotiz

**Datum:** 2026-06-11  
**Grundlage:** `docs/claude_coding/claude_code_prompt_mittel_arbeitszeit_v1_2026-06-11_20-12.md`

---

## Ausgewertete Migrationsdateien

Alle 6 Dateien unter `migrations/` wurden vollständig gelesen:

- `0001_schema.sql`
- `0002_seed_defaults.sql`
- `0003_cleanup_booking_status.sql`
- `0004_supplement_reject_fields_and_review_note.sql`
- `0005_time_bookings_device_event_id.sql`
- `0006_system_events_application_error.sql`

---

## Methodik der Einordnung

**Technische Änderung:** Direkt aus DDL oder INSERT-Inhalt der SQL-Datei gelesen.
Keine Interpretation aus Dateinamen; Dateiname dient nur als Orientierung.

**Fachliche Änderung:** Nur formuliert, wenn SQL-Kommentare die fachliche Wirkung
explizit benennen oder wenn der INSERT-Inhalt selbst fachlich direkt lesbar ist
(z. B. Regelarbeitszeiten-Werte). Bei 0001 und 0002 ohne SQL-Kommentare: fachliche
Aussage aus DDL-Tabellenstruktur bzw. INSERT-Werten direkt abgeleitet.

**Änderungstyp-Vokabular (aus Prompt B2):**
- `Initialschema` — 0001
- `fachliche Erweiterung` — 0002, 0004
- `Compliance-/Nachweisfeld` — 0003
- `Vorbereitungspunkt ohne belegte operative Nutzung` — 0005
- `technische Strukturergänzung` — 0006

---

## Trennung technischer vs. fachlicher Aussage

| Migration | Technisch direkt belegt | Fachlich belegt | Fachlich interpretiert |
| --- | --- | --- | --- |
| 0001 | ✓ (DDL lesbar) | ✓ (Tabellenstruktur direkt) | Nein |
| 0002 | ✓ (INSERT lesbar) | ✓ (Werte direkt: Mo–Fr, Zeiten) | Nein |
| 0003 | ✓ (ALTER via Rebuild) | ✓ (SQL-Kommentar explizit) | Nein |
| 0004 | ✓ (ALTER via Rebuild) | ✓ (SQL-Kommentar explizit) | Nein |
| 0005 | ✓ (ALTER via Rebuild) | Teilweise (Kommentar beschreibt Schema, nicht Betrieb) | Operative Nutzung außerhalb Migration (Commit `0f20931`) |
| 0006 | ✓ (ALTER via Rebuild) | ✓ (SQL-Kommentar explizit) | Nein |

---

## Offene Einordnungsfragen

**Migration 0005:**
- Die Migration bereitet `device_event_id` im Schema vor und setzt alle bestehenden
  Zeilen auf NULL. Der SQL-Kommentar beschreibt explizit nur die Schemavorbereitung.
- Die operative Nutzung (Produktionspfad schreibt device_events-Records und reicht
  die ID durch) ist **nicht Teil der Migration selbst**, sondern wurde nachträglich
  mit Commit `0f20931` (2026-06-11) in `booking_loop.py` implementiert.
- Einordnung als „Vorbereitungspunkt ohne belegte operative Nutzung zum Zeitpunkt
  der Migration" ist korrekt und belastbar.

---

## Nicht entscheidbar auf Basis der vorliegenden Artefakte

- **0001:** Kein SQL-Kommentar vorhanden. Die fachliche Beschreibung der Tabellen
  basiert auf DDL-Lektüre. Ob einzelne Felder nachträglich anders konzipiert wurden
  als ursprünglich geplant, ist aus der Migrationsdatei allein nicht ableitbar.
- **0002:** Kein SQL-Kommentar vorhanden. Ob die Seed-Werte (z. B. Arbeitszeiten)
  formell abgestimmt oder provisorisch sind, ist aus dem SQL nicht entscheidbar.
