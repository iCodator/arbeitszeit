# Prüfbericht: docs/handbuch_rollen_cli_ergaenzung_v1_0.md

## Gesamteinschätzung

Das Dokument beschreibt die Erweiterung der Admin-CLI-Befehlsübersicht um die Benutzerverwaltung (`users`-Domäne). Die Kernaussagen zu den vorhandenen Subcommands (`add`, `list`, `deactivate`, `reactivate`, `change-role`, `bootstrap`), zur Protokollierungspflicht und zu den Rollenbeschränkungen sind größtenteils durch den Code belegt. Zwei Fehler wurden gefunden: ein nicht existierender Befehl `set-password` in der Befehlstabelle sowie eine falsche Aussage, dass `TECH` einen Restore-Vorgang über die CLI ausführen dürfe (ein solcher CLI-Befehl existiert für keine Rolle). Zusätzlich wurde die Argumentsyntax der Beispielaufrufe für `deactivate`/`reactivate`/`change-role` präzisiert, da diese Positionsargumente verwendeten, wo tatsächlich benannte `--user-id`-Optionen erforderlich sind.

## Befunde

- Aussage: Tabelle nennt `users set-password` – "Passwort initial setzen oder zurücksetzen".
  Status: inkorrekt
  Beleg: `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Funktion `register_subcommands()`, definiert nur die Subparser `add`, `list`, `deactivate`, `reactivate`, `change-role`, `bootstrap`. Ein `set-password`-Subcommand, eine zugehörige Handler-Funktion (`cmd_users_set_password`) oder ein `SetPassword*`-Use-Case existieren nicht im gesamten Repository (`grep -rn "set-password|set_password|SetPassword"` liefert keine Treffer).
  Bewertung: Der Befehl `set-password` existiert nicht in der Codebase.
  Anpassungsvorschlag: In der Tabelle durch den tatsächlich vorhandenen Befehl `bootstrap` ersetzt (Passwortänderung für bestehende Konten ist über die CLI aktuell nicht separat möglich; ein neues Passwort kann nur beim Anlegen via `add` vergeben werden).

- Aussage: `users add` – "Neues Benutzerkonto für ADMIN, REVIEWER oder TECH anlegen".
  Status: korrekt
  Beleg: `user_accounts.py`, `add.add_argument("--role", required=True, choices=["ADMIN", "REVIEWER", "TECH"], ...)`.
  Bewertung: Direkt im Code bestätigt.

- Aussage: `users list`, `users deactivate`, `users reactivate`, `users change-role` existieren als Subcommands.
  Status: korrekt
  Beleg: `register_subcommands()` in `user_accounts.py` sowie Dispatch-Tabelle in `main.py` (Zeilen mit `("users", "list")`, `("users", "deactivate")`, `("users", "reactivate")`, `("users", "change-role")`).

- Aussage: Beispielaufrufe verwenden `python -m arbeitszeit.presentation.admin_cli.main ...` mit `users deactivate 3` bzw. `users change-role --id 3 --role REVIEWER` (Positionsargument bzw. `--id`).
  Status: inkorrekt
  Beleg: `deact.add_argument("--user-id", dest="deactivate_user_id", ...)`, `react.add_argument("--user-id", dest="reactivate_user_id", ...)`, `change.add_argument("--user-id", dest="target_user_id", ...)` — alle drei Subcommands verlangen die benannte Option `--user-id`, nicht `--id` und nicht ein Positionsargument.
  Bewertung: Die Beispielaufrufe hätten mit einem Parametrisierungsfehler abgebrochen.
  Anpassungsvorschlag: Auf `--user-id 3` korrigiert (umgesetzt). Der Aufruf über `python -m arbeitszeit.presentation.admin_cli.main` ist technisch funktionsfähig, da `main.py` einen `if __name__ == "__main__":`-Block besitzt; das an anderer Stelle im Projekt gebräuchliche Kürzel `admin` (siehe `prog="admin"` in `main.py`) wurde nicht verändert, da beide Aufrufformen lauffähig sind und das Dokument den Modulpfad konsistent verwendet.

- Aussage: "Der erste Administrator wird über einen gesonderten Bootstrap-Prozess eingerichtet" / "Der Bootstrap-Prozess darf nur verwendet werden, solange noch kein aktives Administratorkonto vorhanden ist."
  Status: korrekt
  Beleg: `cmd_users_bootstrap()` in `user_accounts.py` ruft `BootstrapAdminUseCase` auf; `main.py` behandelt `("users", "bootstrap")` gesondert vor der regulären `--user-id`-Prüfung ("Bootstrap benötigt keine user-id — es gibt noch keinen Admin"). Die Beschränkung auf den Zustand "noch kein Admin vorhanden" liegt in der Use-Case-Logik der Anwendungsschicht (nicht im Detail nachgeprüft, aber die CLI-seitige Sonderbehandlung stützt die Aussage).

- Aussage: "Rollenwechsel, Aktivierung und Deaktivierung sind Administrationsvorgänge und müssen protokolliert werden."
  Status: korrekt
  Beleg: `src/arbeitszeit/domain/audit_events.py` definiert `USER_ACCOUNT_CREATED`, `USER_ACCOUNT_DEACTIVATED`, `USER_ACCOUNT_REACTIVATED`, `USER_ACCOUNT_ROLE_CHANGED`; alle vier Use Cases in `manage_user_accounts.py` rufen die entsprechende Audit-Protokollierung auf.

- Aussage: "`REVIEWER` darf keine Benutzerkonten oder Rollen verwalten."
  Status: korrekt
  Beleg: Alle vier schreibenden Use Cases in `manage_user_accounts.py` (Create, Deactivate, Reactivate, ChangeRole) prüfen `actor.role != UserRole.ADMIN` und lehnen andernfalls mit `DomainError` ab — REVIEWER hat somit keine Berechtigung.

- Aussage: "`TECH` darf Backup, Restore, Systemcheck und betriebsnahe Systemfunktionen ausführen, aber keine fachlichen Freigaben oder Rollenänderungen vornehmen."
  Status: inkorrekt (Teilaspekt "Restore")
  Beleg: `src/arbeitszeit/presentation/admin_cli/system.py` importiert und verwendet `require_admin_or_tech` für die Subcommands `check` und `backup` — dies bestätigt, dass TECH Backup und Systemcheck ausführen darf. Ein Restore-Subcommand existiert jedoch in `system.py` nicht (bereits in früheren Prüfungen dieser Session belegt, u. a. `pruefbericht_betriebsdokumentation.md`); Restore ist ausschließlich über `SQLiteBackupService.restore_from()` programmatisch erreichbar, ohne CLI-Anbindung für irgendeine Rolle.
  Bewertung: Die Aussage suggeriert einen CLI-Restore-Befehl, der für TECH freigegeben sei — ein solcher Befehl existiert für keine Rolle.
  Anpassungsvorschlag: Formulierung präzisiert: TECH darf Backup und Systemcheck über die CLI ausführen; Restore ist nur programmatisch möglich (umgesetzt).

## Zusammenfassung der Korrekturen

1. Tabelle in Abschnitt 1: nicht existierenden Befehl `set-password` entfernt, durch tatsächlich vorhandenen Befehl `bootstrap` ersetzt.
2. Beispielaufrufe in Abschnitt 3: Argumentsyntax für `deactivate`, `reactivate`, `change-role` von Positionsargument/`--id` auf die tatsächlich erforderliche Option `--user-id` korrigiert.
3. Klarstellung in Abschnitt 4: Aussage zu TECH-Berechtigungen präzisiert — kein CLI-Restore-Befehl vorhanden, Restore nur programmatisch über `SQLiteBackupService.restore_from()`.

## Offene Punkte

- Ob eine Passwortänderung für bestehende (nicht-Bootstrap-)Benutzerkonten im Betrieb überhaupt vorgesehen ist und ggf. auf anderem Weg (z. B. Deaktivieren + Neuanlegen) erfolgen soll, ist aus dem Code nicht ersichtlich und bleibt nicht verifizierbar. Das Dokument wurde an dieser Stelle nicht um eine neue Behauptung ergänzt, sondern der nicht existierende Befehl lediglich entfernt.
- Die genaue interne Prüflogik von `BootstrapAdminUseCase` (ob und wie technisch verhindert wird, dass ein zweiter Bootstrap-Lauf ein weiteres Administratorkonto anlegt) wurde nicht im Detail nachvollzogen; die CLI-seitige Sonderbehandlung stützt die im Dokument getroffene Aussage, eine tiefergehende Verifikation der Use-Case-Interna stand außerhalb des Prüfumfangs dieses Kapitels.
