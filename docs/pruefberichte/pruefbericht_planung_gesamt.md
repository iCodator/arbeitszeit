# Prüfbericht: docs/informelles/planung_gesamt.md

## Gesamteinschätzung

`docs/informelles/planung_gesamt.md` beschreibt den Implementierungsplan und -stand des Projekts über fünf Phasen. Die weit überwiegende Mehrheit der geprüften Zahlen und Aussagen (Enum-, Fehler-, Entitäten- und Testzahlen, ER-Modell, Tabellenanzahl, Autorisierungsmatrix) ist exakt mit der Codebase deckungsgleich. Es wurden zwei Zählfehler (Repository-Anzahl), ein direkter inhaltlicher Widerspruch zu einer im selben Dokument getroffenen Aussage sowie ein unbereinigtes Diff-Artefakt gefunden und korrigiert. Der Zielstruktur-Codeblock in Phase 3 war unvollständig gegenüber dem aktuellen Repository-Stand und wurde um einen erläuternden Hinweis ergänzt, ohne den originären Codeblock selbst zu verändern.

## Befunde

- Aussage: „`ports/repositories.py` — 10 Protocol-Interfaces für Repositories der Entitäten und Aggregate.“
- Status: inkorrekt
- Beleg: `src/arbeitszeit/domain/ports/repositories.py` enthält 11 `Protocol`-Klassen: `EmployeeRepository`, `UserAccountRepository`, `RfidCardRepository`, `TimeBookingRepository`, `WorkScheduleRepository`, `ReviewCaseRepository`, `SupplementRepository`, `BookingCorrectionRepository`, `AuditLogRepository`, `DeviceEventRepository`, `SystemConfigRepository`.
- Bewertung: Die Codebase enthält nachweislich 11 statt der genannten 10 Interfaces. Die Zahl war vermutlich veraltet aus einer früheren Projektphase.
- Anpassungsvorschlag: „10“ auf „11“ korrigiert.

---

- Aussage: „10 SQLite-Repositories mit Parameterized Statements, Roundtrips und Scope-/Statuslogik.“ (Phase 4)
- Status: inkorrekt
- Beleg: `src/arbeitszeit/infrastructure/db/repositories/` enthält 11 Repository-Implementierungsdateien (`audit_log.py`, `booking_correction.py`, `device_event.py`, `employee.py`, `review_case.py`, `rfid_card.py`, `supplement.py`, `system_config.py`, `time_booking.py`, `user_account.py`, `work_schedule.py`).
- Bewertung: Analog zur ersten Fundstelle inkorrekt; die Anzahl der SQLite-Implementierungen entspricht der Anzahl der Protocol-Interfaces.
- Anpassungsvorschlag: „10“ auf „11“ korrigiert.

---

- Aussage: „Die vollständige operative Kette [device_event_id] ... ist nach aktuellem Stand noch nicht im Produktionspfad aktiviert.“ (Phase 5, ursprünglich Zeile 246)
- Status: inkorrekt
- Beleg: `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` (Zeilen 39–62) erzeugt vor dem `BookUseCase`-Aufruf einen `RFID_SCAN`-Record in `device_events` und übergibt die neue ID als `BookCommand.device_event_id`; `src/arbeitszeit/application/use_cases/book_time.py` (Zeilen 168, 186) persistiert diese ID in `time_bookings.device_event_id`. Die Kette ist zusätzlich durch drei Integrationstests in `tests/integration/test_device_event_booking.py` abgedeckt (`test_erfolgreiche_buchung_schreibt_device_event_und_verknuepft_id`, `test_unknown_card_schreibt_device_event_aber_keine_buchung`, `test_fehler_im_device_event_insert_verhindert_buchung`).
- Bewertung: Diese Aussage widersprach direkt zwei anderen Stellen im selben Dokument (Zeilen 68 und 179–182), die die Kette bereits als „implementiert“ bzw. „vollständig operativ“ beschreiben, und dem tatsächlichen Codestand. Es handelte sich um einen veralteten, nicht aktualisierten Absatz aus einer früheren Projektphase.
- Anpassungsvorschlag: Absatz umformuliert; die Aussage „noch nicht aktiviert“ wurde durch eine mit Codebeleg und Testverweis gestützte Feststellung ersetzt, dass die Kette implementiert und getestet ist. Die Überschrift „Offener Architekturpunkt“ wurde entsprechend zu „`device_event_id`-Verkettung“ angepasst, da kein offener Punkt mehr vorliegt.

---

- Aussage: Markdown-Diff-Artefakt am Dokumentende (zwei mit „- “ bzw. „+ “ präfixierte Zeilen, die jeweils auf `docs/informelles/testmatrix_revision_v1.md` bzw. `docs/betrieb/nachweise/testmatrix_revision_v1.md` verweisen)
- Status: inkorrekt (Markdown-Formatfehler und falscher Pfad in der ersten Zeile)
- Beleg: `find . -iname "testmatrix_revision_v1.md"` zeigt die Datei ausschließlich unter `docs/betrieb/nachweise/testmatrix_revision_v1.md` (bereits in früheren Prüfberichten dieser Sitzung, u. a. zum Betriebsfreigabe-Protokoll, mit identischem Befund bestätigt).
- Bewertung: Die beiden Zeilen sind ein unbereinigtes Diff-/Merge-Artefakt (Markdown-Sonderzeichen „- “/„+ “ am Zeilenanfang), keine gültige Markdown-Liste im Sinne der Projektregeln. Zusätzlich verwies die als „-“ markierte (ältere) Version auf den falschen Pfad `docs/informelles/`.
- Anpassungsvorschlag: Beide Zeilen zu einer einzigen regulären Fließtextzeile mit dem korrekten Pfad `docs/betrieb/nachweise/testmatrix_revision_v1.md` zusammengeführt.

---

- Aussage: Zielstruktur-Codeblock (Phase 3) listet unter `use_cases/` nur `manage_work_schedule.py`, `register_supplement.py`, `correct_booking.py`, `book_time.py`
- Status: nicht verifizierbar als vollständige Aktualbeschreibung / korrekt als historischer Phase-3-Lieferumfang
- Beleg: `src/arbeitszeit/application/use_cases/` enthält aktuell 9 Dateien: die 4 genannten plus `approve_supplement.py`, `reject_supplement.py`, `manage_employees.py`, `manage_rfid_cards.py`, `manage_user_accounts.py`.
- Bewertung: Der Codeblock ist als Darstellung des *originären* Phase-3-Lieferumfangs plausibel und wird durch den unmittelbar nachfolgenden Hinweistext („`approve_supplement.py` und `reject_supplement.py` wurden in Phase 3 vorimplementiert“) gestützt, der bereits auf Abweichungen vom Codeblock hinweist. Der Codeblock selbst suggerierte jedoch ohne zusätzlichen Kontext einen unvollständigen Ist-Stand.
- Anpassungsvorschlag: Codeblock unverändert belassen (historische Zielstruktur, keine falsche Tatsachenbehauptung), jedoch direkt darunter ein klarstellender Hinweis ergänzt, dass der aktuelle Repository-Stand zusätzlich `approve_supplement.py`, `reject_supplement.py`, `manage_employees.py`, `manage_rfid_cards.py` und `manage_user_accounts.py` enthält.

---

- Aussage: „11 StrEnum-Klassen“ (`enums.py`)
- Status: korrekt
- Beleg: `src/arbeitszeit/domain/enums.py` enthält genau 11 `StrEnum`-Klassen: `BookingType`, `BookingStatus`, `ReviewCaseType`, `ReviewCaseStatus`, `ReviewSeverity`, `CardStatus`, `UserRole`, `BookingSource`, `ChangeOrigin`, `ApprovalStatus`, `ScopeType`.
- Bewertung: Vollständig deckungsgleich mit Code.

---

- Aussage: „DomainError-Basis + 9 Subklassen“ (`errors.py`)
- Status: korrekt
- Beleg: `src/arbeitszeit/domain/errors.py` enthält `DomainError` als Basisklasse und genau 9 Subklassen (`UnknownCardError`, `InactiveCardError`, `InactiveEmployeeError`, `InvalidBookingSequenceError`, `OpenPhaseConflictError`, `PermissionDeniedError`, `ValidationError`, `NotFoundError`, `ConflictError`).
- Bewertung: Vollständig deckungsgleich mit Code.

---

- Aussage: „9 frozen @dataclass-Entitäten“ (`entities.py`)
- Status: korrekt
- Beleg: `src/arbeitszeit/domain/entities.py` enthält genau 9 `@dataclass(frozen=True)`-Klassen (`Employee`, `UserAccount`, `RfidCard`, `TimeBooking`, `WorkScheduleVersion`, `ReviewCase`, `Supplement`, `BookingCorrection`, `AuditLogEntry`).
- Bewertung: Vollständig deckungsgleich mit Code.

---

- Aussage: „15 fachliche Tabellen ... + schema_migrations = 16 Tabellen in 0001_schema.sql“
- Status: korrekt
- Beleg: `migrations/0001_schema.sql` enthält genau 16 `CREATE TABLE`-Anweisungen (`schema_migrations`, `employees`, `user_accounts`, `rfid_cards`, `terminals`, `time_bookings`, `booking_status_history`, `booking_corrections`, `supplements`, `review_cases`, `review_case_actions`, `work_schedule_versions`, `system_config`, `device_events`, `system_events`, `audit_log`).
- Bewertung: Vollständig deckungsgleich mit Code. Auch die ER-Modell-Tabelle (5 Ebenen: Person, Erfassung, Prüfung, Änderung, Nachweis) bildet ausschließlich tatsächlich existierende Tabellen ab.

---

- Aussage: „12 Tests für die Migrationskette 0001–0006“ und „5 Tests für `setup_vollstaendig()`“
- Status: korrekt
- Beleg: `tests/test_migrations.py` enthält genau 12 Testfunktionen (`grep -c "^def test_"`); `tests/integration/test_init_db.py` enthält genau 5 Testfunktionen.
- Bewertung: Vollständig deckungsgleich mit Code.

---

- Aussage: Phase-2-Testzahlen „67 gesamt“ (14 + 9 + 42 + 2)
- Status: korrekt
- Beleg: `tests/domain/test_booking_rules.py` = 14 Testfunktionen, `tests/domain/test_compliance_checks.py` = 9, `tests/domain/test_entities.py` = 42, `tests/domain/test_audit_events.py` = 2. Summe: 67.
- Bewertung: Einzelzahlen und Summe stimmen exakt mit der Codebase überein.

---

- Aussage: „Die definierten Zustände OPEN, OK, WARN, NEEDS_REVIEW, CORRECTED und CLOSED_WITH_NOTE“ (`BookingStatus`)
- Status: korrekt
- Beleg: `src/arbeitszeit/domain/enums.py`, Klasse `BookingStatus`, enthält exakt diese sechs Werte.
- Bewertung: Vollständig deckungsgleich mit Code.

---

- Aussage: Autorisierungstabelle (Erlaubte Rollen je Use Case: `RegisterSupplementUseCase` ADMIN/REVIEWER, `ApproveSupplementUseCase` REVIEWER/ADMIN, `RejectSupplementUseCase` REVIEWER/ADMIN, `CorrectBookingUseCase` ADMIN/REVIEWER, `ManageWorkScheduleUseCase` ADMIN, Backup/Restore TECH/ADMIN)
- Status: korrekt
- Beleg: Rollenprüfungen in `register_supplement.py` (Zeile 38: `{UserRole.ADMIN, UserRole.REVIEWER}`), `approve_supplement.py` (Zeile 213: `{UserRole.REVIEWER, UserRole.ADMIN}`), `reject_supplement.py` (Zeile 36: `{UserRole.REVIEWER, UserRole.ADMIN}`), `correct_booking.py` (Zeile 52: `{UserRole.ADMIN, UserRole.REVIEWER}`), `manage_work_schedule.py` (Zeile 32: `UserRole.ADMIN`); Backup/Restore in `admin_cli/system.py` gegen `require_admin_or_tech()` aus `_auth.py`.
- Bewertung: Vollständig deckungsgleich mit Code.

---

- Aussage: „Phasenübergreifende Nachtragsmatrix ... 44 Einträge“
- Status: nicht verifizierbar
- Beleg: `docs/betrieb/nachweise/nachtragsmatrix_phasen_v1.md` enthält mehrere Tabellen; die Haupttabelle „Matrix“ (Abschnitt ab Zeile 16) umfasst 45 Datenzeilen, weitere Tabellen unter „Explizit erkannte Phasenverschiebungen“, „Nachgezogene Artefakte“ u. a. folgen mit zusätzlichen Einträgen.
- Bewertung: Es ist aus dem Dokumenttext nicht eindeutig ableitbar, ob sich „44 Einträge“ auf die Haupttabelle allein oder eine andere Teilmenge bezieht; die gezählte Haupttabelle weicht mit 45 knapp von der genannten Zahl ab. Eine Korrektur ohne eindeutige Referenzgrundlage würde eine neue ungesicherte Behauptung einführen.
- Anpassungsvorschlag: keiner; Punkt zur manuellen Klärung markiert, Originaltext unverändert belassen.

## Zusammenfassung der vorgenommenen Änderungen

1. „10 Protocol-Interfaces“ auf „11“ korrigiert (`ports/repositories.py`-Beschreibung, Phase 2).
2. „10 SQLite-Repositories“ auf „11“ korrigiert (Phase 4).
3. Widersprüchlichen und veralteten Absatz zur `device_event_id`-Verkettung (Phase 5) korrigiert: Aussage „noch nicht im Produktionspfad aktiviert“ ersetzt durch eine durch Code (`booking_loop.py`, `book_time.py`) und Tests (`test_device_event_booking.py`) belegte Feststellung, dass die Kette implementiert ist; Überschrift von „Offener Architekturpunkt“ zu „`device_event_id`-Verkettung“ angepasst.
4. Unbereinigtes Diff-Artefakt am Dokumentende (zwei „-“/„+“-Zeilen mit unterschiedlichen Pfaden) zu einer korrekten Zeile mit dem tatsächlichen Pfad `docs/betrieb/nachweise/testmatrix_revision_v1.md` zusammengeführt.
5. Klarstellenden Hinweis unterhalb des Phase-3-Zielstruktur-Codeblocks ergänzt, dass der aktuelle Repository-Stand zusätzlich `approve_supplement.py`, `reject_supplement.py`, `manage_employees.py`, `manage_rfid_cards.py` und `manage_user_accounts.py` enthält, ohne den historischen Codeblock selbst zu verändern.

## Offene Punkte (nicht verifizierbar)

- Die genaue Bezugsgröße der Aussage „44 Einträge“ zur Nachtragsmatrix konnte nicht eindeutig auf eine Tabelle in `nachtragsmatrix_phasen_v1.md` zurückgeführt werden (gezählte Haupttabelle: 45 Zeilen). Empfehlung: manuelle Klärung durch den Dokumentenverantwortlichen, welche Teilmenge gezählt wurde.
- Commit-Hash `0f20931` (Referenz für die device_events-Architekturentscheidung) wurde nicht erneut gegen die Git-Historie geprüft; dies wurde bereits in früheren Prüfberichten dieser Sitzung als plausibel übernommen und hier nicht erneut verifiziert.
