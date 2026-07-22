# Umsetzungsplan — Codebase-Audit 2026-07-22

| Feld | Wert |
| --- | --- |
| Erstellt | 2026-07-22 |
| Grundlage | 2026-07-22_codebase-audit_gesamt.md |
| Befunde gesamt | 24 (1 Kritisch, 6 Hoch, 9 Mittel, 8 Niedrig) |
| Phasen | 4 |

## Leitprinzip

Jede Phase ist ein in sich geschlossener Arbeitsschritt, der unabhängig
commitet, getestet und deployed werden kann. Innerhalb einer Phase werden
Aufgaben mit gemeinsamer Wurzelursache gebündelt — das senkt Komplexität
und Fehlerrisiko. Aufgaben verschiedener Phasen werden **nicht** parallel
begonnen.

---

## Phase 1 — Sofort

**Ziel:** Die drei schwerwiegendsten Laufzeitfehler beheben, die im
Produktivbetrieb täglich falsche Daten erzeugen. Alle drei teilen dieselbe
Wurzelursache (fehlendes UTC→Lokal-Mapping), deshalb wird zuerst die
gemeinsame Hilfsfunktion geschaffen.

**Befunde:** [Kritisch] UTC-Vergleich `book_time.py:145–150` ·
[Mittel] UTC-Wochentag `book_time.py:138–139` ·
[Hoch] UTC-Vergleich `approve_supplement.py:189,194` ·
[Hoch] Fehlende Sortierung `approve_supplement.py:78` ·
[Hoch] Severity-Downgrade `compliance_checks.py:33–47`

### Schritt 1.1 — Regressionstests (vor jedem Code-Fix)

Neue Testfälle in `tests/application/test_book_time.py` und
`tests/application/test_approve_supplement.py` schreiben, die **vor** dem
Fix rot sind:

- Buchung `08:00 CEST` (= `06:00 UTC`) → muss `OK` sein, nicht
  `OUTSIDE_SCHEDULE_WINDOW`
- Buchung `00:30 Uhr Montag lokal` (= `22:30 UTC Sonntag`) → Wochentag-Lookup
  muss Montag liefern
- Nachtrag mit `event_at = 08:00 CEST` → kein `OUTSIDE_SCHEDULE_WINDOW`

Kein Produktionscode ändern, bis alle drei Tests nachweislich rot sind.

### Schritt 1.2 — Hilfsfunktion `to_local(dt)` einführen

Neue Funktion in einem geeigneten Modul (z. B.
`src/arbeitszeit/domain/utils.py` oder `src/arbeitszeit/utils.py`):

```python
def to_local(dt: datetime) -> datetime:
    return dt.astimezone()
```

Einheit-Test: `to_local(utc_ts).time()` liefert lokale Uhrzeit.

### Schritt 1.3 — Hilfsfunktion in `book_time.py` einsetzen

Zwei unabhängige Stellen in derselben Datei korrigieren:

- `book_time.py:138–139`: `cmd.booked_at.isoweekday()` und
  `cmd.booked_at.date()` → `to_local(cmd.booked_at).isoweekday()` /
  `.date()`
- `book_time.py:145–150`: `cmd.booked_at.time()` →
  `to_local(cmd.booked_at).time()`

Regressionstests aus Schritt 1.1 müssen anschließend grün sein.
Commit: `fix(book_time): UTC→Lokal-Konvertierung für Zeitplan-Vergleich`

### Schritt 1.4 — Hilfsfunktion in `approve_supplement.py` einsetzen

- `approve_supplement.py:189,194`: `supplement.event_at.isoweekday()`,
  `.date()`, `.time()` → `to_local(supplement.event_at).*`

Separater Commit: `fix(approve_supplement): UTC→Lokal für Schedule-Flags`

### Schritt 1.5 — Chronologische Sortierung in `approve_supplement.py`

- `approve_supplement.py:78`: Zeile ändern auf

```python
projected = sorted(
    list(day_bookings) + [placeholder],
    key=lambda b: b.booked_at,
)
```

Testfall: Nachtrag mit `event_at` zwischen zwei bestehenden Buchungen →
`net_work` muss korrekt summiert werden.
Commit: `fix(approve_supplement): projected-Liste chronologisch sortieren`

### Schritt 1.6 — Prüffolge in `compliance_checks.py` korrigieren

`check_break_compliance` umbauen: alle Flags unabhängig prüfen, schwerste
Severity zurückgeben (kein Frühausstieg nach erstem Treffer).

Testfall: `COME 07:00 · BREAK_START 14:30 · BREAK_END 14:40 · GO 17:00`
→ muss `CRITICAL` liefern, nicht `WARN`.
Commit: `fix(compliance_checks): CRITICAL nicht durch WARN verdecken`

**Abnahme Phase 1:** Alle neuen Tests grün, bestehende Test-Suite grün,
kein neuer Ruff-/mypy-Befund.

---

## Phase 2 — Kurzfristig (Woche 2–3)

**Ziel:** Datenkonsistenz bei Buchungskorrekturen sichern und die beiden
sicherheitskritischen Befunde (RFID-Hashing, Admin-Authentifizierung) klären.
Jede Aufgabe ist unabhängig; keine muss auf eine andere warten.

**Befunde:** [Hoch] `correct_booking.py:65–84` · [Hoch] `uid_hash.py:8` ·
[Hoch] Admin-CLI ohne Passwort-Verifikation

### Schritt 2.1 — `CorrectBookingUseCase`: `booking_type` tatsächlich mutieren

Zwei alternative Ansätze — einen wählen und umsetzen:

**Option A (empfohlen):** `time_bookings.booking_type` und `booked_at` direkt
per UPDATE aktualisieren; `booking_corrections` bleibt als Revisionshistorie.

**Option B:** `list_for_employee_on_day` CORRECTED-Buchungen durch ihre
korrigierten Werte ersetzen lassen (Join auf `booking_corrections`).

Testfall: COME-Buchung auf GO korrigieren → nächster RFID-Scan muss
`derive_booking_type` mit dem korrigierten Typ aufrufen.
Commit: `fix(correct_booking): booking_type in time_bookings mutieren`

### Schritt 2.2 — HMAC-SHA256-Pepper für `hash_uid()`

Voraussetzung: Architekturentscheidung zur Schlüsselverwaltung treffen
(Umgebungsvariable `RFID_PEPPER` vs. geschützte Schlüsseldatei).

Danach:

1. `uid_hash.py` auf HMAC-SHA256 mit Pepper umstellen
2. Einmalige Migrationsfunktion (CLI-Befehl oder Skript) schreiben, die alle
   bestehenden Hashes in `rfid_cards` neu berechnet
3. Dokumentieren, wie der Pepper bei einer Neuinstallation gesetzt wird

**Achtung:** Pepper muss **vor** der Migration gesetzt und gesichert sein.
Nach der Migration sind Karten ohne Pepper dauerhaft nicht mehr erkennbar.

Testfall: `hash_uid('A1B2C3D4')` ohne Pepper → `ValueError` oder
explizite Fehlermeldung.
Commit: `security(uid_hash): HMAC-SHA256 mit Pepper statt unsalted SHA-256`

### Schritt 2.3 — Architekturentscheidung Admin-CLI-Authentifizierung

Dies ist keine Codeaufgabe, sondern eine Grundsatzentscheidung. Zwei Optionen:

**Option A — Passwort-Verifikation nachrüsten:** `--password`-Argument am
CLI-Start, PBKDF2-Vergleich mit `secrets.compare_digest()`.

**Option B — OS-Modell dokumentieren:** `password_hash`-Feld als
„für Web-UI reserviert" im Code und Sicherheitskonzept kennzeichnen;
festschreiben, dass Admin-CLI-Zugriff ausschließlich durch OS-ACLs
(systemd-Unit, Dateisystem-Berechtigungen) geschützt ist.

Ergebnis dieser Phase ist ein Commit mit entweder der Code-Implementierung
(Option A) oder einer Kommentar-/Dokumentationsänderung (Option B).

**Abnahme Phase 2:** Buchungskorrektur-Tests grün; RFID-Migration auf
Testdatenbank erfolgreich durchgeführt; Admin-CLI-Authentifizierungsmodell
dokumentiert.

---

## Phase 3 — Mittelfristig (Woche 3–4)

**Ziel:** Acht kleinere, voneinander unabhängige Einzelfixes umsetzen. Jeder
Fix ist ein eigener Commit; kein Fix hängt vom Ergebnis eines anderen ab.
Reihenfolge nach absteigendem Auswirkungsrisiko.

**Grundregel:** Pro Arbeitseinheit: eine Aufgabe, ein Testfall, ein Commit.
Nicht mehrere Aufgaben gleichzeitig offen halten.

| # | Befund | Datei | Maßnahme |
| --- | --- | --- | --- |
| 3.1 | Doppelung inaktiver Mitarbeiter | `manage_employees.py:31` | `get_active_by_personnel_no` → `get_by_personnel_no`; bei Treffer `ConflictError` werfen |
| 3.2 | Letzter-Admin-Lockout | `manage_user_accounts.py:94–124` | `has_active_admin()`-Prüfung vor Deaktivierung und Rollenwechsel |
| 3.3 | Nachtrag ohne Sequenzprüfung | `register_supplement.py:60–76` | `validate_booking_sequence` vor `repo.add()` aufrufen |
| 3.4 | Nur erste Fall-ID gespeichert | `correct_booking.py:143–153` | Rückgabetyp auf `list[ReviewCaseId]`; alle IDs in Audit-Log |
| 3.5 | Inklusives Intervall | `time_booking.py:81` | `booked_at <= to_dt` → `booked_at < to_dt` |
| 3.6 | Voller Hash im Audit-Log | `book_time.py:264–279` | `uid_hash` → `uid_hash_prefix: uid_hash[:8]` |
| 3.7 | Fehlende Formatprüfung `--uid-hash` | `employees.py:215,229` | `re.fullmatch(r"[0-9a-f]{64}", uid_hash)` vor Speichern |
| 3.8 | Audit-Log-Write-Gap | `book_time.py:204–246` | Write-Ahead mit `status: pending/committed` oder Admin-Plausibilitätsprüfung |

Zu 3.1 und 3.2 jeweils einen Testfall ergänzen, der den Fehlerfall provoziert
(inaktive `personnel_no` wiederverwenden; letztes Admin-Konto deaktivieren).

**Abnahme Phase 3:** Jeder Schritt einzeln: Testfall rot → Fix → Testfall
grün → Commit. Gesamte Test-Suite nach Phase 3 grün.

---

## Phase 4 — Backlog (Niedrig, ohne Zeitdruck)

**Ziel:** Technische Schulden und Klarheitslücken beseitigen. Kein Fix hier
hat produktiven Auswirkungen auf Korrektheit oder Sicherheit im laufenden
Betrieb. Umsetzung opportunistisch, z. B. im Rahmen ohnehin notwendiger
Änderungen an den betroffenen Dateien.

| Befund | Maßnahme |
| --- | --- |
| `CLOSED_WITH_NOTE` nie gesetzt | Fachlich klären: aus Enum und Migration entfernen oder Use Case implementieren |
| `OpenPhaseConflictError` unerreichbar | Kommentar ergänzen, der den defensiven Charakter des Handlers erklärt |
| Connection-Leak `booking_loop.py:43–44` | Verschachteltes `try/finally` für beide Verbindungen |
| `occurred_at` zu spät gesetzt `evdev_reader.py:208` | Zeitstempel ans Beginn des Polls verschieben |
| Rohe UID in `verify_hardware.py` | Ausgabe auf erste vier Zeichen + `****` beschränken |
| Passwort auf `stdout` `user_accounts.py:77,162` | Ausgabe auf `stderr` umleiten |
| Audit-Log-Integrität | HMAC-Kette oder periodischer Append-Only-Export einplanen |
| Fehlendes Lock-File | `uv lock` ausführen, `uv.lock` ins Repository aufnehmen |

---

## Überblick

| Phase | Befunde | Zeitrahmen | Abhängigkeiten |
| --- | --- | --- | --- |
| 1 — Sofort | 5 | Woche 1 | keine |
| 2 — Kurzfristig | 3 | Woche 2–3 | Phase 1 abgeschlossen |
| 3 — Mittelfristig | 8 | Woche 3–4 | Phase 2 abgeschlossen |
| 4 — Backlog | 8 | ohne Frist | unabhängig |
| **Gesamt** | **24** | | |
