# Prüfbericht: `docs/betrieb/rollenzuweisung.md`

**Geprüftes Dokument:** [`docs/betrieb/rollenzuweisung.md`](../../04_betrieb/rollenzuweisung.md) – "Rollenzuweisung und Zugriffsregelung" (Version 1.0, Stand 2026-06-12)
**Geprüft gegen:** `src/arbeitszeit/domain/enums.py`, `src/arbeitszeit/application/use_cases/*.py`, `src/arbeitszeit/presentation/admin_cli/*.py`, `src/arbeitszeit/presentation/admin_gui/main.py`, `src/arbeitszeit/infrastructure/db/repositories/user_account.py`, `src/arbeitszeit/infrastructure/backup/backup_service.py`, `docs/betrieb/restore_checkliste.md`

## Gesamteinschätzung

Das Rollenmodell (ADMIN/REVIEWER/TECH) und die meisten in der Zugriffstabelle (Abschnitt 6) beschriebenen Berechtigungen sind im Code exakt so implementiert und durch explizite Rollenprüfungen in der Anwendungsschicht bzw. auf CLI-Ebene belegt. Eine wesentliche Abweichung wurde gefunden: Der Code kennt zusätzlich die Rolle `EMPLOYEE` im `UserRole`-Enum, die im Dokument nicht erwähnt wird, auch wenn sie für Benutzerkonten aktuell nicht vergebbar ist. Zudem existiert für "Restore auslösen" kein rollengeprüfter Admin-CLI-Befehl, sodass die Zeile "Restore auslösen – ADMIN Ja / TECH Ja" nicht durch eine tatsächliche Rechteprüfung im Code gedeckt ist. Der übrige Großteil des Dokuments besteht aus organisatorischen Formularfeldern, die korrekt als nicht prüfbar zu behandeln sind.

---

## Abschnitt 3: Rollenmodell

**Aussage:** "Es gelten ausschließlich die folgenden Rollen im Administrations- und Prüfbetrieb: ADMIN, REVIEWER, TECH."
**Status:** inkorrekt
**Beleg:** [`src/arbeitszeit/domain/enums.py`, Zeilen 54–58](../arbeitszeit/src/arbeitszeit/domain/enums.py): `class UserRole(StrEnum): EMPLOYEE = "EMPLOYEE"; ADMIN = "ADMIN"; REVIEWER = "REVIEWER"; TECH = "TECH"`.
**Bewertung:** Der Code definiert zusätzlich die Rolle `EMPLOYEE` im `UserRole`-Enum. Für die Vergabe an Benutzerkonten (`user_accounts`) ist `EMPLOYEE` jedoch explizit ausgeschlossen: In [`manage_user_accounts.py`, Zeile 21](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_user_accounts.py) ist `_ALLOWED_ROLES = {UserRole.ADMIN, UserRole.REVIEWER, UserRole.TECH}` definiert, und `CreateUserAccountUseCase.execute()` (Zeilen 37–41) sowie `ChangeUserRoleUseCase.execute()` (Zeilen 171–174) lehnen jede nicht in dieser Menge enthaltene Rolle mit `ValidationError` ab. Die CLI-Argumente für `users add`/`users change-role` beschränken die Auswahl ebenfalls auf `["ADMIN", "REVIEWER", "TECH"]` ([`user_accounts.py`, Zeilen 173–177 und 199](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/user_accounts.py)). Für den "Administrations- und Prüfbetrieb" (also Benutzerkonten mit Rollen) ist die Aussage im Kern also praktisch zutreffend, aber die Formulierung "es gelten ausschließlich" ist technisch nicht exakt, da `EMPLOYEE` als vierter Enum-Wert im Code existiert und in Abfragen wie `WHERE role != 'EMPLOYEE'` ([`user_accounts.py`, Zeile 81](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/user_accounts.py); [`admin_gui/main.py`, Zeile 826](../arbeitszeit/src/arbeitszeit/presentation/admin_gui/main.py)) aktiv referenziert wird.
**Anpassungsvorschlag:** Ergänzen: "Im System ist zusätzlich die technische Rolle `EMPLOYEE` vorgesehen (z. B. für Mitarbeitende ohne administratives Benutzerkonto); diese kann jedoch keinem administrativen Benutzerkonto zugewiesen werden und ist für den Administrations- und Prüfbetrieb ohne Bedeutung."

---

## Abschnitt 5.1–5.3: Zuständigkeiten

**Aussage:** "ADMIN ist zuständig für: Anlegen, Aktivieren, Deaktivieren und Ändern von Benutzerkonten."
**Status:** korrekt
**Beleg:** [`manage_user_accounts.py`](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_user_accounts.py), Klassen `CreateUserAccountUseCase` (Zeile 31), `DeactivateUserAccountUseCase` (Zeile 89), `ReactivateUserAccountUseCase` (Zeile 127) – jeweils `actor.role != UserRole.ADMIN` löst `PermissionDeniedError` aus.
**Bewertung:** Alle vier Operationen (anlegen, deaktivieren, reaktivieren, Rolle ändern) sind ausschließlich für aktive Benutzer mit Rolle `ADMIN` freigegeben.

**Aussage:** "ADMIN ist zuständig für: Zuweisung und Änderung von Rollen."
**Status:** korrekt
**Beleg:** [`manage_user_accounts.py`, `ChangeUserRoleUseCase.execute()`, Zeile 165](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_user_accounts.py).
**Bewertung:** Rollenänderung ist ausschließlich ADMIN vorbehalten, deckungsgleich mit dem Dokument.

**Aussage:** "ADMIN ist zuständig für: Verwaltung von Mitarbeitenden, RFID-Zuordnungen und Regelarbeitszeiten, soweit technisch vorgesehen."
**Status:** korrekt
**Beleg:** [`manage_employees.py`, Zeilen 23 und 78](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_employees.py) (`CreateEmployeeUseCase`, `DeactivateEmployeeUseCase`); [`manage_rfid_cards.py`, Zeilen 27, 87, 157](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_rfid_cards.py) (`AssignRfidCardUseCase`, `ReplaceRfidCardUseCase`, `DeactivateRfidCardUseCase`); [`manage_work_schedule.py`, Zeile 32](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_work_schedule.py) (`ManageWorkScheduleUseCase`) – jeweils `actor.role != UserRole.ADMIN`.
**Bewertung:** Alle drei Bereiche (Mitarbeiterverwaltung, RFID-Kartenverwaltung, Regelarbeitszeitänderung) sind im Code ausschließlich ADMIN vorbehalten, exakt wie im Dokument beschrieben.

**Aussage:** "REVIEWER ist zuständig für: Prüfung offener und auffälliger Fälle" sowie "Bearbeitung und Freigabe von Nachträgen".
**Status:** korrekt
**Beleg:** [`approve_supplement.py`, `_check_permission()`, Zeilen 208–217](../arbeitszeit/src/arbeitszeit/application/use_cases/approve_supplement.py): `approver.role not in {UserRole.REVIEWER, UserRole.ADMIN}`; [`reject_supplement.py`, Zeile 36](../arbeitszeit/src/arbeitszeit/application/use_cases/reject_supplement.py); [`register_supplement.py`, Zeile 38](../arbeitszeit/src/arbeitszeit/application/use_cases/register_supplement.py); [`correct_booking.py`, Zeile 52](../arbeitszeit/src/arbeitszeit/application/use_cases/correct_booking.py); für lesende Abfragen: [`admin_cli/_auth.py`, `require_admin_or_reviewer()`, Zeilen 12–21](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/_auth.py), verwendet in `reports.py` und `schedule.py` (`cmd_schedule_show`).
**Bewertung:** Freigabe/Ablehnung von Nachträgen, Buchungskorrekturen und das Einsehen offener Fälle/Berichte sind konsistent für REVIEWER und ADMIN freigegeben, TECH ist überall ausgeschlossen.

**Aussage:** "REVIEWER: Ablehnung oder Rückgabe unvollständiger Sachverhalte mit Begründung."
**Status:** korrekt
**Beleg:** [`reject_supplement.py`, `RejectSupplementCommand` mit Feld `reason`, Zeile 39 f. und `cmd.reason` in `AuditLogEntry`, Zeile 87](../arbeitszeit/src/arbeitszeit/application/use_cases/reject_supplement.py); CLI erfordert `--reason` als Pflichtparameter ([`bookings.py`, Zeile 183](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/bookings.py)).
**Bewertung:** Eine Begründung (`reason`) ist bei Ablehnung technisch verpflichtend und wird im Audit-Log gespeichert.

**Aussage:** "TECH ist zuständig für: Systemcheck. Backup und Restore im Rahmen der technischen Betreuung."
**Status:** teilweise inkorrekt (Systemcheck/Backup korrekt, Restore nicht durch Rechteprüfung im Code abgedeckt)
**Beleg:** Für Systemcheck und Backup: [`admin_cli/system.py`, `cmd_system_check()` Zeile 20 und `cmd_system_backup()` Zeile 37](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/system.py), beide rufen `require_admin_or_tech()` auf ([`_auth.py`, Zeilen 24–33](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/_auth.py)). Für Restore: Es existiert lediglich eine Methode `restore_from()` in [`backup_service.py`, Zeile 98](../arbeitszeit/src/arbeitszeit/infrastructure/backup/backup_service.py), jedoch **kein** zugehöriger Subcommand in der Admin-CLI (`system.py` registriert nur `check` und `backup`, siehe [Zeilen 98–101](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/system.py)). `restore_from()` wird im Produktivcode nirgends aufgerufen (nur in `tests/e2e/test_backup.py`), es gibt somit keine rollengeprüfte, produktiv nutzbare Restore-Funktion.
**Bewertung:** Systemcheck und Backup sind korrekt durch `require_admin_or_tech` abgesichert und stimmen mit der Zuständigkeitsbeschreibung überein. Die Aussage zu "Restore" ist nicht durch eine im Code vorhandene, rollengeprüfte Funktion belegt; Restore ist laut [`restore_checkliste.md`](../../04_betrieb/restore_checkliste.md) ein rein manueller, organisatorisch abzuwickelnder Vorgang außerhalb der Admin-CLI.
**Anpassungsvorschlag:** Klarstellen, dass Restore aktuell kein durch Rollenprüfung abgesicherter CLI-Befehl ist, sondern ein manueller technischer Vorgang gemäß Restore-Checkliste, der organisatorisch auf ADMIN/TECH beschränkt werden soll, ohne dass dies technisch im System erzwungen wird.

**Aussage:** "TECH darf keine fachlichen Freigaben, keine Rollenänderungen und keine inhaltlichen Korrekturen von Zeitdaten vornehmen, sofern dies nicht ausdrücklich zusätzlich als ADMIN-Berechtigung vergeben wurde."
**Status:** korrekt
**Beleg:** `TECH` ist in keiner der Rollenmengen für Nachtragsfreigabe/-ablehnung, Buchungskorrektur oder Rollenänderung enthalten: [`approve_supplement.py` Zeile 213](../arbeitszeit/src/arbeitszeit/application/use_cases/approve_supplement.py), [`reject_supplement.py` Zeile 36](../arbeitszeit/src/arbeitszeit/application/use_cases/reject_supplement.py), [`correct_booking.py` Zeile 52](../arbeitszeit/src/arbeitszeit/application/use_cases/correct_booking.py), [`manage_user_accounts.py` `ChangeUserRoleUseCase`, Zeile 165](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_user_accounts.py) (nur ADMIN).
**Bewertung:** Die Aussage ist durch die jeweiligen Rollenprüfungen im Code vollständig gedeckt; TECH kann diese Aktionen technisch nicht ausführen.

---

## Abschnitt 6: Zugriffsregelung (Tabelle)

**Aussage:** "Benutzerkonten anlegen/ändern/deaktivieren – ADMIN: Ja, REVIEWER: Nein, TECH: Nein – Nur via Admin-CLI."
**Status:** korrekt
**Beleg:** [`manage_user_accounts.py`, Zeilen 31, 89, 127, 165](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_user_accounts.py); CLI-Einstiegspunkt ausschließlich über [`admin_cli/main.py`](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/main.py), keine äquivalente Funktion in `admin_gui` außerhalb desselben Use-Case-Aufrufs.
**Bewertung:** Zutreffend; nur ADMIN kann diese Operationen ausführen, unabhängig vom Frontend (CLI/GUI), da die Prüfung im Use Case (Anwendungsschicht) liegt und nicht nur auf CLI-Ebene.
**Anpassungsvorschlag:** "Nur via Admin-CLI" ist ungenau, da laut Code auch `admin_gui/main.py` (Tab "Benutzerkontenverwaltung", Zeile 750) dieselben Use Cases zur Benutzerkontenverwaltung aufruft. Empfehlung: "Nur via Admin-CLI oder Admin-GUI" bzw. "nur über administrative Oberflächen, nicht über das Terminal".

**Aussage:** "Rollen ändern – ADMIN: Ja, REVIEWER: Nein, TECH: Nein – Nur via Admin-CLI."
**Status:** korrekt (Rollenlogik), Bemerkung "Nur via Admin-CLI" nicht vollständig
**Beleg:** [`manage_user_accounts.py`, `ChangeUserRoleUseCase.execute()`, Zeile 165](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_user_accounts.py); auch aufrufbar über `admin_gui/main.py`, Zeilen 1015–1031 (Rollen-Änderungsdialog).
**Bewertung:** Die Rollenbeschränkung (nur ADMIN) ist korrekt. Die Formulierung "Nur via Admin-CLI" trifft nicht exakt zu, da die Rollenänderung auch über die Admin-GUI möglich ist.
**Anpassungsvorschlag:** Wie oben – Formulierung auf "Admin-CLI oder Admin-GUI" anpassen.

**Aussage:** "Mitarbeitende anlegen/ändern – ADMIN: Ja, REVIEWER: Nein, TECH: Nein."
**Status:** korrekt
**Beleg:** [`manage_employees.py`, Zeilen 23 und 78](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_employees.py).
**Bewertung:** Deckt sich mit dem Code; nur ADMIN darf Mitarbeitende anlegen/deaktivieren.

**Aussage:** "Offene Fälle prüfen – ADMIN: Ja, REVIEWER: Ja, TECH: Nein."
**Status:** korrekt
**Beleg:** [`admin_cli/_auth.py`, `require_admin_or_reviewer()`, Zeilen 12–21](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/_auth.py), verwendet u. a. in [`reports.py`, `cmd_reports_open_review_cases()`, Zeile 251](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/reports.py).
**Bewertung:** Zutreffend; nur ADMIN/REVIEWER können offene Prüffälle einsehen, TECH ist ausgeschlossen.

**Aussage:** "Nachträge freigeben/ablehnen – ADMIN: Ja, REVIEWER: Ja, TECH: Nein – Mit Begründung."
**Status:** korrekt
**Beleg:** [`approve_supplement.py`, Zeile 213](../arbeitszeit/src/arbeitszeit/application/use_cases/approve_supplement.py); [`reject_supplement.py`, Zeile 36](../arbeitszeit/src/arbeitszeit/application/use_cases/reject_supplement.py) mit Pflichtfeld `reason`.
**Bewertung:** Die Rollenbeschränkung und das Begründungserfordernis (zumindest bei Ablehnung, technisch als Pflichtparameter) sind im Code nachgewiesen. Für die Freigabe (`approve-supplement`) ist im Code kein Pflichtfeld `reason` vorgesehen (`ApproveSupplementCommand` enthält laut [`approve_supplement.py`](../arbeitszeit/src/arbeitszeit/application/use_cases/approve_supplement.py) nur `supplement_id` und `approving_user_id`); die Bemerkungsspalte "Mit Begründung" trifft daher nur auf die Ablehnung zu, nicht auf die Freigabe.
**Anpassungsvorschlag:** Bemerkung präzisieren: "Ablehnung erfordert Begründung; Freigabe technisch ohne Begründungspflicht."

**Aussage:** "Backup auslösen – ADMIN: Ja, REVIEWER: Nein, TECH: Ja – Technische Funktion."
**Status:** korrekt
**Beleg:** [`admin_cli/system.py`, `cmd_system_backup()`, Zeile 37](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/system.py) ruft `require_admin_or_tech()` auf.
**Bewertung:** Vollständig durch Code belegt.

**Aussage:** "Restore auslösen – ADMIN: Ja, REVIEWER: Nein, TECH: Ja – Nur nach Freigabe."
**Status:** nicht verifizierbar
**Beleg:** Kein Restore-Subcommand in [`admin_cli/system.py`](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/system.py) (nur `check` und `backup`, Zeilen 98–101); `restore_from()` existiert nur als interne Methode in [`backup_service.py`, Zeile 98](../arbeitszeit/src/arbeitszeit/infrastructure/backup/backup_service.py) und wird laut Repository-Suche nur in `tests/e2e/test_backup.py` aufgerufen, nicht in einem produktiven Aufrufpfad mit Rollenprüfung.
**Bewertung:** Da es keinen mit einer Rollenprüfung versehenen Restore-Befehl im Code gibt, kann die konkrete rollenbasierte Berechtigungsverteilung ("ADMIN Ja / TECH Ja") technisch nicht verifiziert werden. Die Aussage mag organisatorisch beabsichtigt sein (vgl. [`restore_checkliste.md`, Zeile 29](../../04_betrieb/restore_checkliste.md): "Die Rollen/Zuständigkeiten für den Restore sind geklärt (ADMIN/TECH)"), ist aber nicht technisch erzwungen.
**Anpassungsvorschlag:** Bemerkungsspalte ergänzen: "Technisch nicht durch Rollenprüfung im System erzwungen; rein organisatorische Festlegung gemäß Restore-Checkliste."

**Aussage:** "Systemcheck – ADMIN: Ja, REVIEWER: Nein, TECH: Ja – Technische Funktion."
**Status:** korrekt
**Beleg:** [`admin_cli/system.py`, `cmd_system_check()`, Zeile 20](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/system.py) ruft `require_admin_or_tech()` auf.
**Bewertung:** Vollständig durch Code belegt.

**Aussage:** "Export erzeugen – ADMIN: Ja, REVIEWER: Ja, TECH: Nein – Nur berechtigt."
**Status:** korrekt
**Beleg:** [`admin_cli/reports.py`](../arbeitszeit/src/arbeitszeit/presentation/admin_cli/reports.py), alle Export-Funktionen (`cmd_reports_export_csv`, Zeile 109; `cmd_reports_export_csv_review_cases`, Zeile 125; `cmd_reports_export_pdf_day`, Zeile 139; `cmd_reports_export_pdf_week`, Zeile 151; `cmd_reports_export_pdf_month`, Zeile 162; `cmd_reports_export_pdf_employee`, Zeile 173) rufen `require_admin_or_reviewer()` auf.
**Bewertung:** Durchgängig belegt für alle Exportvarianten (CSV, PDF).

**Aussage:** "Regelarbeitszeiten ändern – ADMIN: Ja, REVIEWER: Nein, TECH: Nein – Soweit organisatorisch festgelegt."
**Status:** korrekt
**Beleg:** [`manage_work_schedule.py`, `ManageWorkScheduleUseCase.execute()`, Zeile 32](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_work_schedule.py): `actor.role != UserRole.ADMIN` löst `PermissionDeniedError` aus.
**Bewertung:** Zutreffend; ausschließlich ADMIN darf Regelarbeitszeiten ändern.

---

## Abschnitt 1, 2, 4, 7, 8, 9, 10, 11, 12, 13, 14 – organisatorische Inhalte

**Aussage:** Abschnitt 2 (Verantwortliche Stelle), Abschnitt 4 (Rolleninhaber-Tabelle mit Namen/Kontaktdaten), Abschnitt 7 (Einweisungsnachweise mit Unterschriftsfeldern), Abschnitt 8 (Stellvertretungstabelle), Abschnitt 10 (Widerruf/Änderung-Formular), Abschnitt 11 (Nachweis der Einweisung).
**Status:** nicht zutreffend (organisatorisches Formularfeld)
**Beleg:** Entsprechende Tabellen enthalten ausschließlich Freitext-Platzhalter (`__________________________________________`) für Namen, Daten, Unterschriften.
**Bewertung:** Diese Abschnitte sind ausfüllbare Formularfelder ohne technischen Aussagegehalt und daher nicht gegen die Codebase prüfbar.

**Aussage:** Abschnitt 1 (Zweck), Abschnitt 9 (Datenschutz und Vertraulichkeit – organisatorische Verpflichtungserklärungen), Abschnitt 13 (Änderungshistorie), Abschnitt 14 (Anleitung zur Pflege des Dokuments).
**Status:** nicht zutreffend (organisatorisches Formularfeld)
**Bewertung:** Es handelt sich um rein organisatorische bzw. prozessuale Festlegungen (Zuständigkeit für Dokumentenpflege, Aktualisierungsanlässe, Aufbewahrung), die keine technisch nachprüfbaren Tatsachenbehauptungen über die Codebase enthalten.

**Aussage (Abschnitt 12):** Bezug zu Projektunterlagen, u. a. `docs/datenschutz/vvt_arbeitszeit_v1.md`.
**Status:** nicht verifizierbar
**Beleg:** Die Datei `docs/datenschutz/vvt_arbeitszeit_v1.md` wurde im ausgecheckten Repository nicht gefunden (Verzeichnis `docs/datenschutz/` existiert im geprüften Checkout nicht).
**Bewertung:** Der Verweis auf dieses Dokument kann anhand des vorliegenden Repository-Stands nicht verifiziert werden, da die referenzierte Datei nicht auffindbar ist.
**Anpassungsvorschlag:** Prüfen, ob die Datei unter einem anderen Pfad existiert oder der Verweis anzupassen bzw. als offen zu kennzeichnen ist.

---

## Zusammenfassung der Kernbefunde

1. **Rollenmodell:** ADMIN/REVIEWER/TECH sind exakt so im Code implementiert (`UserRole`-Enum, `_ALLOWED_ROLES`, `require_admin_or_reviewer`, `require_admin_or_tech`). Zusätzlich existiert `UserRole.EMPLOYEE`, das im Dokument nicht erwähnt wird, aber für administrative Benutzerkonten nicht vergebbar ist ([`src/arbeitszeit/domain/enums.py`](../arbeitszeit/src/arbeitszeit/domain/enums.py), [`manage_user_accounts.py`](../arbeitszeit/src/arbeitszeit/application/use_cases/manage_user_accounts.py)).
2. **Zugriffsregelung (Abschnitt 6):** Alle Zeilen außer "Restore auslösen" sind durch konkrete Rechteprüfungen im Code belegt.
3. **Restore:** Es existiert keine rollengeprüfte, produktiv nutzbare Restore-Funktion im Admin-CLI; die Zeile "Restore auslösen" im Dokument ist technisch nicht verifizierbar.
4. **"Nur via Admin-CLI":** Diese Bemerkung trifft für Benutzerkonten-/Rollenverwaltung nicht exakt zu, da dieselben Use Cases auch über `admin_gui/main.py` erreichbar sind.
5. Die überwiegende Mehrheit des Dokuments (Abschnitte 1, 2, 4, 7–14) besteht aus organisatorischen Formularfeldern ohne technischen Prüfgehalt.
