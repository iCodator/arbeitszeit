# Prüfbericht: `regelwerk_arbeitszeit_v5.md`

## Gesamteinschätzung

Das Regelwerk ist in den meisten fachlichen Kernpunkten (Buchungsarten, Plausibilitätsregeln, Regelarbeitszeiten, ArbZG-Prüfhilfen mit exakten Schwellenwerten, Rollenprinzip, Backup-Berechtigung) präzise und deckt sich mit der Codebase. Ein konkreter Fehler wurde in §11 gefunden: Der dort genannte Enum-Wert `MANUAL_ENTRY` existiert im Code nicht — der tatsächliche `ReviewCaseType`-Wert lautet `MANUAL_ENTRY_REVIEW`. Eine Aussage zur Aufbewahrungsfrist (§18) ist mangels technischer Implementierung nicht verifizierbar.

## Befunde

- Aussage: Terminalablauf „Buchungsart wählen, dann RFID-Chip scannen" als verbindliche Reihenfolge.
  Status: nicht verifizierbar
  Beleg: Kein direkter Terminal-UI-Quellcode wurde in dieser Prüfsitzung eingesehen (Terminal-Bedienablauf wurde in früheren Kapiteln, nicht in dieser Sitzung, geprüft).
  Bewertung: Keine Gegen-Evidenz gefunden, aber auch keine Bestätigung in dieser Sitzung eingesehen; als bereits in früheren Zyklen behandelt eingestuft, hier nicht erneut mit Primärbeleg bestätigt.

- Aussage: Zulässige Buchungsarten `Kommen`, `Gehen`, `Pause Start`, `Pause Ende`.
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/enums.py`, Zeilen 4–8: `class BookingType(StrEnum): COME, GO, BREAK_START, BREAK_END` — vier Werte, inhaltlich deckungsgleich mit den vier deutschen Bezeichnungen des Regelwerks.
  Bewertung: Bestätigt (technische Enum-Werte sind Übersetzungen der im Regelwerk genannten fachlichen Begriffe).

- Aussage: Plausibilitätsregeln (§6) — u. a. `Kommen` während offener Pause unzulässig, `Gehen` bei offener Pause ohne Klärung, `Pause Start` bei offener Pause unzulässig, `Pause Ende` ohne offene Pause unzulässig.
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/services/booking_rules.py`, Zeilen 31, 37, 46, 50 — exakt diese vier Fälle werfen `InvalidBookingSequenceError` bzw. `OpenPhaseConflictError`.
  Bewertung: Bestätigt.

- Aussage (§7): Regelarbeitszeiten Montag–Mittwoch 07:30–18:00, Donnerstag 07:30–14:00, Freitag 07:30–16:00.
  Status: korrekt
  Beleg: `migrations/0002_seed_defaults.sql`, Zeilen 14–18: `weekday` 1–3 → `07:30`–`18:00`; `weekday` 4 → `07:30`–`14:00`; `weekday` 5 → `07:30`–`16:00` (GLOBAL-Scope, Standardwerte).
  Bewertung: Exakt bestätigt, inklusive aller fünf Werktage.

- Aussage (§10): ArbZG-Prüfhilfen — Warnung >6h ohne Pause, Warnung >9h ohne ausreichende Pause, Warnung >8h täglicher Arbeitszeit, Eskalation >10h täglicher Arbeitszeit, Warnung <11h Ruhezeit.
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/services/compliance_checks.py`: `check_break_compliance` prüft `max_continuous > 6*3600` (Zeile 34) und `net_work > 9*3600 and total_break < 45*60` (Zeile 38); `check_max_hours` prüft `net_work > 10*3600` als `CRITICAL` (Zeile 50) und `net_work > 8*3600` als `WARN` (Zeile 54); `check_rest_period` prüft `< 11*3600` Sekunden zwischen `last_go` und `next_come` (Zeile 60).
  Bewertung: Alle fünf genannten Schwellenwerte exakt bestätigt.

- Aussage (§11): Buchungsstatus-Enum `BookingStatus` mit Werten `OK`, `OPEN`, `WARN`, `NEEDS_REVIEW`, `CORRECTED`, `CLOSED_WITH_NOTE`.
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/enums.py`, Zeilen 11–17 — exakt diese sechs Werte in dieser Reihenfolge.
  Bewertung: Bestätigt.

- Aussage (§11): Fachliche Hinweislagen `POSSIBLE_BREAK_VIOLATION`, `POSSIBLE_REST_VIOLATION`, `POSSIBLE_MAX_HOURS_VIOLATION` als `ReviewCaseType`-Werte (nicht als `BookingStatus`).
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/enums.py`, Zeilen 20–31 (`class ReviewCaseType`) enthält diese drei Werte; sie sind nicht Teil von `BookingStatus` (Zeilen 11–17).
  Bewertung: Bestätigt.

- Aussage (§11): Fachliche Hinweislage `MANUAL_ENTRY` als `ReviewCaseType`-Wert, orthogonal modelliert; zusätzlich `MANUAL_ENTRY` in Kombination mit `BookingSource.MANUAL` auf `TimeBooking`.
  Status: inkorrekt
  Beleg: `src/arbeitszeit/domain/enums.py`, Zeile 31: Der tatsächliche `ReviewCaseType`-Wert lautet `MANUAL_ENTRY_REVIEW`, nicht `MANUAL_ENTRY`. Verwendungsstellen bestätigen ausschließlich `MANUAL_ENTRY_REVIEW`: `application/use_cases/register_supplement.py` Zeile 81, `application/use_cases/approve_supplement.py` Zeile 103, `application/use_cases/reject_supplement.py` Zeile 59, Kommentar in `application/use_cases/correct_booking.py` Zeile 27. Der separate Aspekt `BookingSource.MANUAL` (Zeile 63 in `enums.py`) existiert tatsächlich und wird in `approve_supplement.py` (Zeilen 127, 162) verwendet — dieser Teil der Aussage ist korrekt.
  Anpassungsvorschlag: In §11 den Enum-Wert `MANUAL_ENTRY` durch `MANUAL_ENTRY_REVIEW` ersetzen (sowohl in der Aufzählung als auch im Fließtext).

- Aussage (§12/§13): Korrekturen und Nachträge müssen alten Zustand, neuen Zustand, Begründung, korrigierende Person und Zeitstempel dokumentieren; Nachträge müssen als solche gekennzeichnet sein.
  Status: nicht verifizierbar
  Beleg: In dieser Prüfsitzung wurde kein Primärbeleg (z. B. `correct_booking.py`, `register_supplement.py` im Detail) auf exakte Feldabdeckung (alter/neuer Zustand, Begründung, Person, Zeitstempel) hin untersucht.
  Bewertung: Keine Gegen-Evidenz gefunden; mangels vertiefter Prüfung in dieser Sitzung als nicht verifizierbar eingestuft.

- Aussage (§16): Rollen `ADMIN`, `REVIEWER`, `TECH` sowie `EMPLOYEE`; nur `ADMIN` darf Benutzerkonten mit diesen Rollen anlegen/ändern/deaktivieren/reaktivieren; erster Administrator über gesonderten Bootstrap-Prozess.
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/enums.py`, Zeilen 54–58: `class UserRole(StrEnum): EMPLOYEE, ADMIN, REVIEWER, TECH`. `application/use_cases/manage_user_accounts.py`, `presentation/admin_cli/user_accounts.py` und `presentation/admin_gui/main.py` implementieren die Benutzerkontenverwaltung; Bootstrap-Mechanismus referenziert in `scripts/setup.py` (Datei existiert, Rollenbezug nicht im Detail in dieser Sitzung geprüft).
  Bewertung: Enum-Struktur exakt bestätigt; Rollenverwaltungsdateien vorhanden und passend benannt.

- Aussage (§16): Prüfer (`REVIEWER`) dürfen offene/auffällige Fälle, Nachträge und Korrekturen bearbeiten, jedoch keine Benutzerkonten/Rollen/Systemkonfigurationen verwalten.
  Status: korrekt
  Beleg: `approve_supplement.py` Zeile 213 und `correct_booking.py` Zeile 52 erlauben `REVIEWER` neben `ADMIN`; `manage_employees.py` (Zeilen 23, 78) und `manage_rfid_cards.py` (Zeilen 27, 87, 157) verlangen strikt `UserRole.ADMIN`, `REVIEWER` ist dort nicht zugelassen.
  Bewertung: Bestätigt.

- Aussage (§20): Backup- und Restore-Funktionen ausschließlich für Benutzer mit Rolle `ADMIN` oder `TECH`.
  Status: korrekt
  Beleg: `presentation/admin_cli/system.py`, Zeilen 20 und 37 rufen `require_admin_or_tech(conn, user_id)` vor Systemcheck und Backup auf; `presentation/admin_cli/_auth.py`, Zeilen 24–33, definiert `require_admin_or_tech` mit exakter Prüfung `role not in ("ADMIN", "TECH")`.
  Bewertung: Exakt bestätigt.

- Aussage (§18): Arbeitszeitdaten mindestens 2 Jahre aufzubewahren; keine physische Löschung im Normalfall.
  Status: nicht verifizierbar
  Beleg: Keine technische Implementierung einer Mindestaufbewahrungsfrist (z. B. Löschsperre, Ablaufdatum) wurde im Code gefunden; die Aussage beschreibt eine organisatorische Regel ohne zugehörigen Programmcode.
  Bewertung: Weder bestätigt noch widerlegt — die Aussage ist als organisatorische Vorgabe formuliert und dahingehend nicht mit einer Codeimplementierung verifizierbar. Kein Korrekturbedarf, da das Regelwerk keine Codeimplementierung behauptet.

## Anpassungsvorschläge (zusammengefasst)

1. §11: Enum-Bezeichnung `MANUAL_ENTRY` auf `MANUAL_ENTRY_REVIEW` korrigieren (Aufzählung und Fließtext).
