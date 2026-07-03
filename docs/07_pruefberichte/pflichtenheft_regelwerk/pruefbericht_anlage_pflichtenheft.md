# Prüfbericht: `anlage_einhaltung_pflichtenheft.md`

## Gesamteinschätzung

Die Anlage ordnet Pflichtenheft-Anforderungen Rechtsgrundlagen und Kammerkommunikation zu. Der überwiegende Teil der Zuordnungstabelle betrifft externe Rechtsquellen (EuGH, BAG, ArbZG, ArbSchG, DSGVO, BDSG, Kammertexte), die nicht aus dem Repository verifizierbar sind und außerhalb des Prüfauftrags "Codebase-Abgleich" liegen. Die technischen und quantitativen Angaben (Prüflogik-Schwellenwerte, genannte Technikkomponenten) sind mit der Codebase deckungsgleich. Keine Korrektur erforderlich.

## Befunde

- Aussage: Rechtsgrundlagen EuGH C-55/18, BAG 1 ABR 22/21, ArbSchG § 3 Abs. 2 Nr. 1, ArbZG §§ 3–5 und § 16, DSGVO Art. 5/32, BDSG § 26.
  Status: nicht verifizierbar
  Beleg: Externe Rechtsquellen sind nicht Bestandteil des Repositorys und daher im Rahmen dieses Prüfauftrags (Abgleich Handbuch/Anlage gegen Codebase) nicht verifizierbar.
  Bewertung: Außerhalb der Prüfbarkeit durch Repository-Evidenz; keine Aussage zur juristischen Korrektheit möglich oder beabsichtigt.

- Aussage: Prüflogik — Hinweis bei mehr als 6 Stunden ohne Pause, mehr als 9 Stunden ohne ausreichende Gesamtpause, mehr als 8 oder 10 Stunden täglicher Arbeitszeit, Unterschreitung der 11-stündigen Ruhezeit.
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/services/compliance_checks.py`, Zeilen 34, 38, 50, 54, 60 (bereits im Rahmen der Prüfung von `regelwerk_arbeitszeit_v5.md` in dieser Sitzung mit exakten Schwellenwerten bestätigt).
  Bewertung: Bestätigt, deckungsgleich mit den bereits verifizierten Schwellenwerten aus dem Regelwerk.

- Aussage: Aufbewahrung von Arbeitszeitnachweisen mindestens 2 Jahre.
  Status: nicht verifizierbar
  Beleg: Keine technische Implementierung einer Mindestaufbewahrungsfrist im Code gefunden (siehe bereits dokumentierter Befund zu `regelwerk_arbeitszeit_v5.md` §18).
  Bewertung: Organisatorische Vorgabe ohne zugehörige Codeimplementierung; weder bestätigt noch widerlegt.

- Aussage: Rollen- und Rechtekonzept als projektinterne Muss-Anforderung.
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/enums.py`, Zeilen 54–58 (`UserRole`: `EMPLOYEE`, `ADMIN`, `REVIEWER`, `TECH`); Rollenprüfungen in `application/use_cases/manage_employees.py`, `manage_rfid_cards.py`, `approve_supplement.py`, `correct_booking.py`, `presentation/admin_cli/_auth.py`.
  Bewertung: Bestätigt, ein Rollen- und Rechtekonzept ist im Code tatsächlich umgesetzt.

- Aussage: Nachvollziehbarkeit über Audit-Log, Korrektur- und Nachtragslogik als projektinterne Muss-Anforderung.
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/audit_events.py` (Audit-Event-Typen wie `TIME_BOOKED`, `BOOKING_CORRECTED`, `BOOKING_REJECTED_UNKNOWN_CARD`); `application/use_cases/correct_booking.py`, `register_supplement.py`, `approve_supplement.py`, `reject_supplement.py` implementieren Korrektur- bzw. Nachtragsprozesse.
  Bewertung: Bestätigt, entsprechende Module existieren.

- Aussage: Technikkomponenten RFID-Reader, USB-Numpad, SQLite, NAS, PDF/CSV als reine technische Projektentscheidung.
  Status: korrekt
  Beleg: `src/arbeitszeit/infrastructure/hardware/evdev_reader.py` (RFID/HID-Eingabe über evdev), SQLite-Migrationen unter `migrations/`, NAS-Synchronisation in `infrastructure/backup/backup_service.py` (`sync_to_nas`), PDF-Export in `infrastructure/export/pdf_report_service.py`, CSV-Export in `infrastructure/export/csv_exporter.py`.
  Bewertung: Alle genannten Technikkomponenten sind im Code tatsächlich vorhanden und belegbar.

## Anpassungsvorschläge (zusammengefasst)

Keine. Alle repository-prüfbaren Aussagen sind bestätigt; die rechtlichen Zuordnungen liegen außerhalb der Prüfbarkeit durch Repository-Evidenz und werden entsprechend als nicht verifizierbar eingestuft, ohne dass daraus ein Korrekturbedarf am Dokument abgeleitet wird.
