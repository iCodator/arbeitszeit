# Prüfbericht: `docs/03_installation_technik/handbuch_rollen_cli_ergaenzung.md`

**Geprüfte Datei:** `docs/03_installation_technik/handbuch_rollen_cli_ergaenzung.md`  
**Datei-SHA:** `978fd3798f88e8d80e93ab0e32c9ed4de222d52a`  
**Prüfdatum:** 2026-07-04  
**Prüfbericht-Version:** 1.1  
**Geprüft gegen:** Codestand `main` (HEAD-SHA: `adf990a6cb28c2586d4e278ae3697e9defeac12f`)  
**Abgeglichen mit:** `docs/03_installation_technik/installationsanleitung_arbeitszeit.md`

---

## Gesamteinschätzung

Das Dokument ist eine Ergänzungsfassung für das Handbuch der Arbeitszeiterfassung und beschreibt die Admin-CLI-Benutzerverwaltung, den Bootstrap-Prozess, Beispielaufrufe sowie fachliche Klarstellungen zu Rollen und Systemfunktionen.

Die Mehrzahl der Aussagen ist korrekt und durch Quellcode sowie ergänzend durch die Installationsanleitung belegbar. Gegenüber der vorherigen Fassung des Prüfberichts waren zwei Bewertungen zu korrigieren: Die Aussagen zur Datenbankinitialisierung und zur Konfiguration deployment-spezifischer Pfade sind durch die Installationsanleitung belegbar und daher als korrekt einzustufen. Kritisch bleibt, dass ein expliziter Beispielaufruf für `users bootstrap` im Dokument fehlt; sofern ein solcher ergänzt wird, muss er ohne globales `--user-id` formuliert sein.

---

## Kapitel 1 — Ergänzung Admin-CLI-Befehlsübersicht

### Gesamteinschätzung des Kapitels

Die Tabelle der `users`-Befehle spiegelt den tatsächlichen Code korrekt wider. Alle sechs aufgelisteten Unterbefehle und ihre Beschreibungen stimmen mit den registrierten Subcommands in `user_accounts.py` und dem Dispatch-Table in `main.py` überein.

---

- **Aussage:** Befehl `users list` — Benutzerkonten anzeigen  
- **Status:** korrekt  
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Funktion `cmd_users_list`; `src/arbeitszeit/presentation/admin_cli/main.py`, Dispatch-Table `("users", "list")`  
- **Bewertung:** Unterbefehl ist registriert und implementiert.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Befehl `users add` — Neues Benutzerkonto für `ADMIN`, `REVIEWER` oder `TECH` anlegen  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `register_subcommands()` → `add_parser("add")`; Argument `--role` mit `choices=["ADMIN", "REVIEWER", "TECH"]`; `main.py`, Dispatch-Table `("users", "add")`  
- **Bewertung:** Korrekt. Die drei Rollen sind die einzigen zulässigen Werte.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Befehl `users deactivate` — Benutzerkonto deaktivieren  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `add_parser("deactivate")`; `cmd_users_deactivate`; `main.py`, Dispatch-Table `("users", "deactivate")`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Befehl `users reactivate` — Benutzerkonto reaktivieren  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `add_parser("reactivate")`; `cmd_users_reactivate`; `main.py`, Dispatch-Table `("users", "reactivate")`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Befehl `users change-role` — Rolle eines Benutzerkontos ändern  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `add_parser("change-role")`; `cmd_users_change_role`; `main.py`, Dispatch-Table `("users", "change-role")`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Befehl `users bootstrap` — Erstes Administratorkonto anlegen (nur wenn noch kein Admin existiert)  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `add_parser("bootstrap")` mit Hilfetext „nur wenn kein Admin existiert“; `src/arbeitszeit/application/use_cases/manage_user_accounts.py`, `BootstrapAdminUseCase.execute()` prüft via `has_active_admin()` und wirft `ConflictError`, falls bereits ein aktiver Admin existiert  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

## Kapitel 2 — Ergänzung Ersteinrichtung

### Gesamteinschätzung des Kapitels

Die beschriebene Reihenfolge der Ersteinrichtung ist in wesentlichen Punkten belegbar. Durch den Abgleich mit der Installationsanleitung sind die Schritte zur Datenbankinitialisierung und zur Konfiguration deployment-spezifischer Pfade nun als korrekt einzuordnen.

---

- **Aussage:** Schritt 1 — Datenbank initialisieren.  
- **Status:** korrekt  
- **Beleg:** `docs/03_installation_technik/installationsanleitung_arbeitszeit.md`, Schritt 7 nennt ausdrücklich `python scripts/init_db.py`; zusätzlich führt `src/arbeitszeit/presentation/admin_cli/main.py` bei CLI-Aufrufen `run_migrations(conn)` aus  
- **Bewertung:** Die Initialisierung ist durch die Installationsanleitung explizit beschrieben und damit verifizierbar.  
- **Anpassungsvorschlag:** Optional präzisieren, dass zusätzlich Migrationen beim CLI-Aufruf ausgeführt werden.

---

- **Aussage:** Schritt 2 — Deployment-spezifische Pfade konfigurieren.  
- **Status:** korrekt  
- **Beleg:** `docs/03_installation_technik/installationsanleitung_arbeitszeit.md`, Schritt 8 nennt `python scripts/setup.py --db arbeitszeit.db`; `src/arbeitszeit/presentation/admin_cli/system.py` liest Konfigurationswerte wie `backup.backup_dir`, `export.export_dir`, `backup.nas_enabled` und `backup.nas_path` aus `system_config`  
- **Bewertung:** Die Installationsanleitung beschreibt den Setup-Schritt zur Grundkonfiguration; der Code zeigt die Verwendung dieser Pfadkonfigurationen im Systembereich.  
- **Anpassungsvorschlag:** Optional konkretisieren, welche Konfigurationsschlüssel für Backup und Export verwendet werden.

---

- **Aussage:** Schritt 3 — Ersten Administrator über den Bootstrap-Prozess anlegen.  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `cmd_users_bootstrap`; `manage_user_accounts.py`, `BootstrapAdminUseCase`; `main.py` mit Sonderbehandlung des Bootstrap-Befehls ohne `user-id`-Anforderung  
- **Bewertung:** Korrekt und notwendig, da Bootstrap die Voraussetzung für weitere Benutzerverwaltungsoperationen ist.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Schritt 4 — Weitere Benutzerkonten für Prüfer und technische Betreuung über die Admin-CLI anlegen.  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `cmd_users_add`; `manage_user_accounts.py`, `CreateUserAccountUseCase`; Rollen `REVIEWER` und `TECH` sind zulässige Werte für `--role`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Schritt 5 — Erst danach in den regulären Betrieb übergehen.  
- **Status:** nicht verifizierbar  
- **Beleg:** Kein expliziter Code- oder Dokumentationsmechanismus für einen formalen „Betriebsübergang“ im Repository auffindbar  
- **Bewertung:** Prozessuale Aussage ohne direkte technische Entsprechung. Inhaltlich plausibel, aber nicht belegbar.  
- **Anpassungsvorschlag:** Als Empfehlung oder Hinweis formulieren, nicht als verifizierten Pflichtschritt.

---

## Kapitel 3 — Beispielaufrufe

### Gesamteinschätzung des Kapitels

Die vorhandenen Beispielaufrufe für `users add`, `users deactivate`, `users reactivate` und `users change-role` sind syntaktisch korrekt. Eine inhaltliche Lücke besteht darin, dass ein expliziter Beispielaufruf für `users bootstrap` fehlt. Falls dieser ergänzt wird, muss er ohne globales `--user-id` formuliert sein, da der Bootstrap-Pfad in `main.py` ohne `_resolve_user_id()` ausgeführt wird.

---

- **Aussage:** Aufruf `users add` für Rolle ADMIN:  
  `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username admin1 --role ADMIN`  
- **Status:** korrekt  
- **Beleg:** `main.py` → globale Argumente `--db` und `--user-id`; `user_accounts.py` → `add_parser("add")` mit `--username` und `--role`  
- **Bewertung:** Aufruf ist syntaktisch korrekt.  
- **Anpassungsvorschlag:** Hinweis ergänzen, dass das Paket installiert sein muss, z. B. gemäß Installationsanleitung über `pip install -e .[dev]`.

---

- **Aussage:** Aufruf `users add` für Rolle REVIEWER:  
  `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username pruefer1 --role REVIEWER`  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `--role` erlaubt `REVIEWER`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Aufruf `users add` für Rolle TECH:  
  `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username tech1 --role TECH`  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `--role` erlaubt `TECH`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Aufruf `users deactivate`:  
  `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users deactivate --user-id 3`  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py` → lokales Argument `--user-id` mit `dest="deactivate_user_id"`; globales `--user-id` bleibt getrennt  
- **Bewertung:** Korrekt. argparse trennt globales und lokales Zielattribut.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Aufruf `users reactivate`:  
  `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users reactivate --user-id 3`  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py` → `dest="reactivate_user_id"`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Aufruf `users change-role`:  
  `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users change-role --user-id 3 --role REVIEWER`  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py` → `dest="target_user_id"`; `--role` erlaubt `REVIEWER`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Für `users bootstrap` fehlt ein expliziter Beispielaufruf.  
- **Status:** nicht verifizierbar  
- **Beleg:** `docs/03_installation_technik/handbuch_rollen_cli_ergaenzung.md`, Kapitel 3 enthält keinen Beispielaufruf für `users bootstrap`; `main.py` behandelt Bootstrap als Sonderfall ohne `_resolve_user_id(args)`  
- **Bewertung:** Es liegt keine falsche Syntax im Dokument vor, sondern eine dokumentarische Lücke. Ein ergänzter Beispielaufruf darf kein globales `--user-id` verwenden.  
- **Anpassungsvorschlag:** Beispiel ergänzen:  
  ```bash
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db users bootstrap --username admin1
  ```

---

- **Aussage:** Der Modulaufruf via `python -m arbeitszeit.presentation.admin_cli.main` setzt eine installierte oder korrekt eingebundene Paketstruktur voraus.  
- **Status:** korrekt  
- **Beleg:** `pyproject.toml` enthält keinen `[project.scripts]`-Eintrag; `tool.setuptools.packages.find.where = ["src"]`; `docs/03_installation_technik/installationsanleitung_arbeitszeit.md`, Schritt 6 nennt `pip install -e .[dev]`  
- **Bewertung:** Die Installationsanleitung deckt die notwendige Paketinstallation ab. Die Aussage ist damit verifizierbar.  
- **Anpassungsvorschlag:** Im Dokument optional auf die Installationsvoraussetzung verweisen.

---

## Kapitel 4 — Fachliche Klarstellungen für das Handbuch

### Gesamteinschätzung des Kapitels

Die meisten Klarstellungen sind korrekt und durch den Code belegbar. Bei der Aussage zum Restore ist die Kernaussage korrekt; präzisierungsbedürftig bleibt, dass zwar eine programmatische Methode vorhanden ist, aber kein CLI-Befehl und keine eigenständige Restore-Anleitung im geprüften Material vorliegen.

---

- **Aussage:** Benutzerkonten für `ADMIN`, `REVIEWER` und `TECH` werden regulär über die Admin-CLI verwaltet.  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `cmd_users_*`; `main.py`, Dispatch-Table; `manage_user_accounts.py`, Use Cases  
- **Bewertung:** Korrekt. Die CLI ist der dokumentierte Verwaltungsweg.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Direkte SQL-Änderungen an Benutzerkonten sind kein regulärer Betriebsprozess.  
- **Status:** nicht verifizierbar  
- **Beleg:** Keine ausdrückliche technische Sperre oder normative Repository-Regel hierzu auffindbar  
- **Bewertung:** Inhaltlich nachvollziehbar, aber nicht technisch oder dokumentarisch belegt.  
- **Anpassungsvorschlag:** Als Empfehlung formulieren, nicht als belegte Tatsache.

---

- **Aussage:** Der erste Administrator wird über einen gesonderten Bootstrap-Prozess eingerichtet.  
- **Status:** korrekt  
- **Beleg:** `user_accounts.py`, `cmd_users_bootstrap`; `manage_user_accounts.py`, `BootstrapAdminUseCase`; `main.py`, Sonderfall für Bootstrap ohne Benutzer-ID-Auflösung  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Der Bootstrap-Prozess darf nur verwendet werden, solange noch kein aktives Administratorkonto vorhanden ist.  
- **Status:** korrekt  
- **Beleg:** `BootstrapAdminUseCase.execute()` prüft `has_active_admin()` und verhindert weiteren Bootstrap bei vorhandenem aktivem Admin  
- **Bewertung:** Technisch erzwungen.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Benutzerkonten werden im Regelbetrieb deaktiviert statt physisch gelöscht.  
- **Status:** korrekt  
- **Beleg:** `DeactivateUserAccountUseCase` nutzt `user_account_repo.deactivate()`; kein Delete-Use-Case und kein `users delete`-Subcommand im Repository vorhanden  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Rollenwechsel, Aktivierung und Deaktivierung sind Administrationsvorgänge und müssen protokolliert werden.  
- **Status:** korrekt  
- **Beleg:** `manage_user_accounts.py` — Audit-Log-Einträge in `CreateUserAccountUseCase`, `DeactivateUserAccountUseCase`, `ReactivateUserAccountUseCase` und `ChangeUserRoleUseCase`  
- **Bewertung:** Korrekt. Die Protokollierung ist im Use-Case-Code implementiert.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** `REVIEWER` darf keine Benutzerkonten oder Rollen verwalten.  
- **Status:** korrekt  
- **Beleg:** `manage_user_accounts.py` — Schreib-Use-Cases prüfen durchgehend auf `actor.role == UserRole.ADMIN`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** `TECH` darf Backup und Systemcheck über die Admin-CLI-Befehlsgruppe `system` ausführen (`require_admin_or_tech`).  
- **Status:** korrekt  
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py` — `cmd_system_check()` und `cmd_system_backup()` rufen `require_admin_or_tech(conn, user_id)` auf; `src/arbeitszeit/presentation/admin_cli/_auth.py` erlaubt `ADMIN` und `TECH`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** `TECH` darf keine fachlichen Freigaben oder Rollenänderungen vornehmen.  
- **Status:** korrekt  
- **Beleg:** `manage_user_accounts.py` verlangt für Rollenänderungen `ADMIN`; für Benutzerverwaltungs-Use-Cases besteht keine Berechtigung für `TECH`  
- **Bewertung:** Korrekt.  
- **Anpassungsvorschlag:** keiner

---

- **Aussage:** Für einen Restore-Vorgang existiert kein eigener Admin-CLI-Befehl; ein Restore ist nur programmatisch über `SQLiteBackupService.restore_from()` möglich.  
- **Status:** korrekt (mit Präzisierungsbedarf)  
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/system.py` registriert nur `check` und `backup`; `src/arbeitszeit/infrastructure/backup/backup_service.py` enthält `SQLiteBackupService.restore_from()`; in der geprüften Installationsanleitung ist kein Restore-Befehl dokumentiert  
- **Bewertung:** Korrekt, soweit kein CLI-Befehl existiert und die programmatische Methode vorhanden ist. Präzisierungsbedarf besteht hinsichtlich einer separaten Restore-Anleitung.  
- **Anpassungsvorschlag:** Formulierung erweitern: Die Methode ist implementiert, ein dokumentierter Bedienpfad für Restore fehlt jedoch.

---

## Zusammenfassung der Befunde

| Nr. | Kapitel | Status | Schwere |
|---|---|---|---|
| 1.1 | 1 | korrekt | — |
| 1.2 | 1 | korrekt | — |
| 1.3 | 1 | korrekt | — |
| 1.4 | 1 | korrekt | — |
| 1.5 | 1 | korrekt | — |
| 1.6 | 1 | korrekt | — |
| 2.1 | 2 | korrekt | — |
| 2.2 | 2 | korrekt | — |
| 2.3 | 2 | korrekt | — |
| 2.4 | 2 | korrekt | — |
| 2.5 | 2 | nicht verifizierbar | gering |
| 3.1 | 3 | korrekt | — |
| 3.2 | 3 | korrekt | — |
| 3.3 | 3 | korrekt | — |
| 3.4 | 3 | korrekt | — |
| 3.5 | 3 | korrekt | — |
| 3.6 | 3 | korrekt | — |
| 3.7 | 3 | nicht verifizierbar | hoch |
| 3.8 | 3 | korrekt | — |
| 4.1 | 4 | korrekt | — |
| 4.2 | 4 | nicht verifizierbar | gering |
| 4.3 | 4 | korrekt | — |
| 4.4 | 4 | korrekt | — |
| 4.5 | 4 | korrekt | — |
| 4.6 | 4 | korrekt | — |
| 4.7 | 4 | korrekt | — |
| 4.8 | 4 | korrekt | — |
| 4.9 | 4 | korrekt | — |
| 4.10 | 4 | korrekt (mit Präzisierungsbedarf) | gering |

**Korrekt:** 25  
**Nicht verifizierbar:** 3  
**Inkorrekt:** 0

---

## Offene Punkte für manuelle Klärung

1. **Befund 3.7 (hoch):** Ein expliziter Beispielaufruf für `users bootstrap` fehlt weiterhin im Dokument und sollte ergänzt werden. Der Aufruf darf kein globales `--user-id` verwenden.
2. **Befund 2.5 (gering):** Die Formulierung „in den regulären Betrieb übergehen“ bleibt ohne technische oder dokumentarische Entsprechung im Repository.
3. **Befund 4.2 (gering):** Die Aussage zu direkten SQL-Änderungen ist als Betriebsregel plausibel, aber nicht ausdrücklich durch Repository-Material normiert.
4. **Befund 4.10 (gering):** Eine eigenständige Restore-Anleitung fehlt weiterhin.
