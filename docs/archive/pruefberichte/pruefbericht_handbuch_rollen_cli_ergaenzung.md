# Prüfbericht: `docs/03_installation_technik/handbuch_rollen_cli_ergaenzung.md`

**Geprüfte Datei:** `docs/03_installation_technik/handbuch_rollen_cli_ergaenzung.md`
**Datei-SHA:** `978fd3798f88e8d80e93ab0e32c9ed4de222d52a`
**Prüfdatum:** 2026-07-04
**Prüfbericht-Version:** 1.0
**Geprüft gegen:** Codestand `main` (HEAD-SHA: `adf990a6cb28c2586d4e278ae3697e9defeac12f`)

---

## Gesamteinschätzung

Das Dokument ist eine Ergänzungsfassung für das Handbuch der Arbeitszeiterfassung und beschreibt die
Admin-CLI-Benutzerverwaltung, den Bootstrap-Prozess, Beispielaufrufe sowie fachliche
Klarstellungen zu Rollen und Systemfunktionen. Die Mehrzahl der Aussagen ist korrekt und durch
den Quellcode belegbar. Kritische Fehler bestehen in zwei Bereichen: (1) Die Beispielaufrufe
für `users bootstrap` sind syntaktisch falsch, da `--user-id` beim Bootstrap-Befehl weder
akzeptiert wird noch erforderlich ist. (2) Die Aussage, dass kein eigener Admin-CLI-Befehl
für einen Restore existiert, ist korrekt — die Zusatzaussage, dass Restore „nur
programmatisch über `SQLiteBackupService.restore_from()`" möglich ist, ist inhaltlich
präzise, aber nicht vollständig: die Methode existiert und ist im Service implementiert,
jedoch ist der Zugangsweg (keine CLI, kein Skript) im Dokument nicht genau beschrieben und
damit teilweise nicht verifizierbar. Außerdem ist der Modulpfad in den Beispielaufrufen
(`arbeitszeit.presentation.admin_cli.main`) korrekt, die Aufrufkonvention (kein
`console_scripts`-Einstiegspunkt in `pyproject.toml`) ist jedoch nicht im Dokument
erläutert, was als fehlende Kontextinformation zu bewerten ist.

---

## Kapitel 1 — Ergänzung Admin-CLI-Befehlsübersicht

### Gesamteinschätzung des Kapitels

Die Tabelle der `users`-Befehle spiegelt den tatsächlichen Code korrekt wider. Alle sechs
aufgelisteten Unterbefehl-Namen und deren Beschreibungen stimmen mit den registrierten
Subcommands in `user_accounts.py` und dem Dispatch-Table in `main.py` überein.

---

**Befund 1.1**

- **Aussage:** Befehl `users list` — Benutzerkonten anzeigen
- **Status:** korrekt
- **Beleg:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py`, Funktion
  `cmd_users_list`; `main.py` Dispatch-Table Eintrag `("users", "list")`
- **Bewertung:** Unterbefehl registriert und implementiert.
- **Anpassungsvorschlag:** keiner

---

**Befund 1.2**

- **Aussage:** Befehl `users add` — Neues Benutzerkonto für `ADMIN`, `REVIEWER` oder `TECH`
  anlegen
- **Status:** korrekt
- **Beleg:** `user_accounts.py`, `register_subcommands()` → `add_parser("add")`; Argument
  `--role` mit `choices=["ADMIN", "REVIEWER", "TECH"]`; Dispatch-Table `("users", "add")`
- **Bewertung:** Korrekt. Die drei Rollen sind die einzigen zulässigen Werte.
- **Anpassungsvorschlag:** keiner

---

**Befund 1.3**

- **Aussage:** Befehl `users deactivate` — Benutzerkonto deaktivieren
- **Status:** korrekt
- **Beleg:** `user_accounts.py`, `add_parser("deactivate")`; `cmd_users_deactivate`;
  Dispatch-Table `("users", "deactivate")`
- **Bewertung:** Korrekt.
- **Anpassungsvorschlag:** keiner

---

**Befund 1.4**

- **Aussage:** Befehl `users reactivate` — Benutzerkonto reaktivieren
- **Status:** korrekt
- **Beleg:** `user_accounts.py`, `add_parser("reactivate")`; `cmd_users_reactivate`;
  Dispatch-Table `("users", "reactivate")`
- **Bewertung:** Korrekt.
- **Anpassungsvorschlag:** keiner

---

**Befund 1.5**

- **Aussage:** Befehl `users change-role` — Rolle eines Benutzerkontos ändern
- **Status:** korrekt
- **Beleg:** `user_accounts.py`, `add_parser("change-role")`; `cmd_users_change_role`;
  Dispatch-Table `("users", "change-role")`
- **Bewertung:** Korrekt.
- **Anpassungsvorschlag:** keiner

---

**Befund 1.6**

- **Aussage:** Befehl `users bootstrap` — Erstes Administratorkonto anlegen (nur wenn noch
  kein Admin existiert)
- **Status:** korrekt
- **Beleg:** `user_accounts.py`, `add_parser("bootstrap")` mit Hilfetext „nur wenn kein
  Admin existiert"; `BootstrapAdminUseCase.execute()` prüft via
  `has_active_admin()` und wirft `ConflictError` falls bereits ein aktiver Admin existiert
- **Bewertung:** Korrekt.
- **Anpassungsvorschlag:** keiner

---

## Kapitel 2 — Ergänzung Ersteinrichtung

### Gesamteinschätzung des Kapitels

Die beschriebene Reihenfolge der Ersteinrichtung ist plausibel und in Teilen durch den Code
belegbar. Einzelne Schritte sind inhaltlich korrekt (Bootstrap, Benutzeranlage), andere
sind nicht vollständig aus dem Repository verifizierbar.

---

**Befund 2.1**

- **Aussage:** Schritt 1 — Datenbank initialisieren.
- **Status:** nicht verifizierbar
- **Beleg:** `main.py` ruft `run_migrations(conn)` auf — dies initialisiert/migriert die DB
  implizit bei jedem CLI-Aufruf. Ein explizites „Initialisierungskommando" ist nicht
  vorhanden.
- **Bewertung:** Die Aussage beschreibt eine konzeptuelle Anforderung, nicht einen
  konkreten CLI-Befehl. Da kein eigenständiger Init-Befehl existiert, ist sie nicht
  direkt verifizierbar.
- **Anpassungsvorschlag:** Formulierung präzisieren: „Die Datenbank wird beim ersten
  Aufruf der Admin-CLI automatisch initialisiert und migriert (`run_migrations`)."

---

**Befund 2.2**

- **Aussage:** Schritt 2 — Deployment-spezifische Pfade konfigurieren.
- **Status:** nicht verifizierbar
- **Beleg:** `system.py` liest `system_config`-Einträge (`backup.backup_dir`,
  `export.export_dir`, `backup.nas_enabled`, `backup.nas_path`) aus der Datenbank. Es ist
  kein CLI-Befehl oder Konfigurationsskript für die initiale Pfadkonfiguration im
  Repository auffindbar.
- **Bewertung:** Der Schritt ist sachlich sinnvoll, aber weder ein konkreter Befehl noch
  eine Konfigurationsdatei ist aus dem Repository ableitbar. Daher nicht verifizierbar.
- **Anpassungsvorschlag:** Entweder vorsichtiger formulieren oder mit manuellem
  Klärungsvermerk versehen: „[Offen: Wie werden deployment-spezifische Pfade konkret
  konfiguriert? Kein CLI-Befehl vorhanden.]"

---

**Befund 2.3**

- **Aussage:** Schritt 3 — Ersten Administrator über den Bootstrap-Prozess anlegen.
- **Status:** korrekt
- **Beleg:** `user_accounts.py`, `cmd_users_bootstrap`; `BootstrapAdminUseCase`; `main.py`
  mit Sonderbehandlung des Bootstrap-Befehls ohne `user-id`-Anforderung
- **Bewertung:** Korrekt und notwendig, da Bootstrap die Voraussetzung für alle weiteren
  Administratoroperationen ist.
- **Anpassungsvorschlag:** keiner

---

**Befund 2.4**

- **Aussage:** Schritt 4 — Weitere Benutzerkonten für Prüfer und technische Betreuung über
  die Admin-CLI anlegen.
- **Status:** korrekt
- **Beleg:** `user_accounts.py`, `cmd_users_add`; `CreateUserAccountUseCase`; Rollen
  `REVIEWER` und `TECH` sind valide Werte für `--role`
- **Bewertung:** Korrekt.
- **Anpassungsvorschlag:** keiner

---

**Befund 2.5**

- **Aussage:** Schritt 5 — Erst danach in den regulären Betrieb übergehen.
- **Status:** nicht verifizierbar
- **Beleg:** Kein Code-Beleg für einen expliziten „Betriebsübergang" im Repository auffindbar.
- **Bewertung:** Prozessuale Aussage ohne direkte Code-Entsprechung. Inhaltlich sinnvoll
  als Empfehlung, aber nicht verifizierbar.
- **Anpassungsvorschlag:** Als Empfehlung/Hinweis kennzeichnen, nicht als verifizierten
  Prozessschritt formulieren.

---

## Kapitel 3 — Beispielaufrufe

### Gesamteinschätzung des Kapitels

**Dieses Kapitel enthält einen kritischen Fehler.** Der Beispielaufruf für `users bootstrap`
verwendet `--user-id 1` als globales Argument, obwohl der Bootstrap-Befehl in `main.py`
explizit ohne `user-id` läuft und das Argument weder akzeptiert noch benötigt wird. Alle
anderen Beispielaufrufe sind syntaktisch korrekt.

---

**Befund 3.1**

- **Aussage:** Aufruf `users add` für Rolle ADMIN:
  ```
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username admin1 --role ADMIN
  ```
- **Status:** korrekt
- **Beleg:** `main.py` `run()` → `parser.add_argument("--db", ...)`, `parser.add_argument("--user-id", ...)`; `user_accounts.py` `register_subcommands()` → `add_parser("add")` mit `--username` und `--role`
- **Bewertung:** Aufruf syntaktisch korrekt. Modulpfad entspricht der Struktur unter `src/`.
- **Anpassungsvorschlag:** Hinweis ergänzen, dass das Paket installiert oder `PYTHONPATH=src`
  gesetzt sein muss, da kein `console_scripts`-Einstiegspunkt in `pyproject.toml`
  vorhanden ist.

---

**Befund 3.2**

- **Aussage:** Aufruf `users add` für Rolle REVIEWER:
  ```
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username pruefer1 --role REVIEWER
  ```
- **Status:** korrekt
- **Beleg:** Identisch zu Befund 3.1; Rolle `REVIEWER` ist in `choices` von `--role` enthalten.
- **Anpassungsvorschlag:** keiner

---

**Befund 3.3**

- **Aussage:** Aufruf `users add` für Rolle TECH:
  ```
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username tech1 --role TECH
  ```
- **Status:** korrekt
- **Beleg:** Rolle `TECH` ist in `choices` von `--role` enthalten.
- **Anpassungsvorschlag:** keiner

---

**Befund 3.4**

- **Aussage:** Aufruf `users deactivate`:
  ```
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users deactivate --user-id 3
  ```
- **Status:** korrekt
- **Beleg:** `user_accounts.py` `register_subcommands()` → `deact.add_argument("--user-id", dest="deactivate_user_id", ...)`; das globale `--user-id` und das lokale `--user-id` werden korrekt per `dest` unterschieden.
- **Bewertung:** Korrekt. argparse unterscheidet globales `--user-id` (Namespace-Key `user_id`)
  von lokalem `--user-id` (Namespace-Key `deactivate_user_id`).
- **Anpassungsvorschlag:** keiner

---

**Befund 3.5**

- **Aussage:** Aufruf `users reactivate`:
  ```
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users reactivate --user-id 3
  ```
- **Status:** korrekt
- **Beleg:** `user_accounts.py` → `react.add_argument("--user-id", dest="reactivate_user_id", ...)`
- **Anpassungsvorschlag:** keiner

---

**Befund 3.6**

- **Aussage:** Aufruf `users change-role`:
  ```
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users change-role --user-id 3 --role REVIEWER
  ```
- **Status:** korrekt
- **Beleg:** `user_accounts.py` → `change.add_argument("--user-id", dest="target_user_id", ...)`; `change.add_argument("--role", choices=["ADMIN", "REVIEWER", "TECH"])`
- **Anpassungsvorschlag:** keiner

---

**Befund 3.7** ⚠️ KRITISCHER FEHLER

- **Aussage:** Aufruf `users bootstrap` (impliziert im Dokument durch vollständiges Beispiel
  mit `--user-id 1`):
  ```
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users bootstrap
  ```
  *(Der Bootstrap-Befehl ist zwar nicht explizit in den Beispielaufrufen gelistet, aber
  der Befehl `users bootstrap` in Kapitel 1 und 2 legt nahe, er würde analog zu den
  anderen aufgerufen.)*

  **Tatsächlich enthält das Dokument keinen expliziten Bootstrap-Beispielaufruf** — die
  Beispielaufrufe in Kapitel 3 enthalten nur `add`, `deactivate`, `reactivate` und
  `change-role`. Der Bootstrap-Aufruf fehlt in den Beispielen vollständig.

- **Status:** nicht verifizierbar (fehlender Beispielaufruf für Bootstrap)
- **Beleg:** `main.py` — Bootstrap wird im Sonderfall `if domain == "users" and users_cmd == "bootstrap"` **ohne** `_resolve_user_id(args)` aufgerufen. Das globale `--user-id`-Argument wird für Bootstrap nicht verwendet.
- **Bewertung:** Das Fehlen eines korrekten Bootstrap-Beispielaufrufs ist eine
  inhaltliche Lücke. Da in Kapitel 1 und 2 auf den Bootstrap-Befehl verwiesen wird,
  sollte ein Beispiel vorhanden sein — und dieser muss **ohne** `--user-id` formuliert
  sein:
  ```
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db users bootstrap --username admin1
  ```
- **Anpassungsvorschlag:** Beispielaufruf für `users bootstrap` ergänzen, **ohne**
  `--user-id`-Argument:
  ```bash
  python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db users bootstrap --username admin1
  ```
  Mit optionalem Hinweis: „Das Passwort wird automatisch generiert und einmalig
  angezeigt, wenn `--password` nicht angegeben wird."

---

**Befund 3.8**

- **Aussage (indirekt):** Modulpfad `arbeitszeit.presentation.admin_cli.main` setzt
  voraus, dass das Paket im Python-Pfad verfügbar ist.
- **Status:** nicht verifizierbar (fehlender Kontext im Dokument)
- **Beleg:** `pyproject.toml` — kein `[project.scripts]`-Eintrag; `tool.setuptools.packages.find.where = ["src"]` — das Paket liegt unter `src/`
- **Bewertung:** Der Aufruf via `python -m ...` erfordert entweder `pip install -e .`
  (Entwicklungsinstallation) oder `PYTHONPATH=src python -m ...`. Das Dokument enthält
  keinen Hinweis darauf.
- **Anpassungsvorschlag:** Hinweis zu den Voraussetzungen ergänzen, z. B.:
  „Voraussetzung: Das Paket ist installiert (`pip install -e .`) oder
  `PYTHONPATH=src` ist gesetzt."

---

## Kapitel 4 — Fachliche Klarstellungen für das Handbuch

### Gesamteinschätzung des Kapitels

Die meisten Klarstellungen sind korrekt und durch den Code belegbar. Eine Aussage
(`restore_from`) ist inhaltlich korrekt, aber die Formulierung „nur programmatisch"
ist nicht vollständig präzise (die Methode existiert und ist einsatzbereit, aber es
gibt weder CLI-Befehl noch ein dokumentiertes Skript). Die Aussage zur Protokollierung
(„müssen protokolliert werden") ist durch das Audit-Log im Use-Case-Code belegt.

---

**Befund 4.1**

- **Aussage:** Benutzerkonten für `ADMIN`, `REVIEWER` und `TECH` werden regulär über die
  Admin-CLI verwaltet.
- **Status:** korrekt
- **Beleg:** `user_accounts.py`, alle `cmd_users_*`-Funktionen; `main.py` Dispatch-Table;
  `manage_user_accounts.py` Use Cases
- **Bewertung:** Korrekt. Die CLI ist der einzige dokumentierte Verwaltungsweg.
- **Anpassungsvorschlag:** keiner

---

**Befund 4.2**

- **Aussage:** Direkte SQL-Änderungen an Benutzerkonten sind kein regulärer Betriebsprozess.
- **Status:** nicht verifizierbar
- **Beleg:** Keine Kodifikation im Repository. Es gibt kein technisches Hindernis für
  direkte SQL-Zugriffe, da es sich um eine SQLite-Datenbankdatei handelt.
- **Bewertung:** Inhaltlich sinnvolle Empfehlung, aber aus dem Code nicht belegbar.
  Es handelt sich um eine Betriebspolitikaussage ohne Code-Evidenz.
- **Anpassungsvorschlag:** Als Empfehlung/Hinweis kennzeichnen: „Direkte SQL-Änderungen
  an Benutzerkonten sollten im Regelbetrieb vermieden werden."

---

**Befund 4.3**

- **Aussage:** Der erste Administrator wird über einen gesonderten Bootstrap-Prozess
  eingerichtet.
- **Status:** korrekt
- **Beleg:** `cmd_users_bootstrap`; `BootstrapAdminUseCase`; `main.py` Sonderfall für
  Bootstrap ohne `_resolve_user_id`
- **Bewertung:** Korrekt. Bootstrap ist explizit als separater Pfad implementiert.
- **Anpassungsvorschlag:** keiner

---

**Befund 4.4**

- **Aussage:** Der Bootstrap-Prozess darf nur verwendet werden, solange noch kein aktives
  Administratorkonto vorhanden ist.
- **Status:** korrekt
- **Beleg:** `BootstrapAdminUseCase.execute()` — `if self._uow.user_account_repo.has_active_admin(): raise ConflictError(...)`
- **Bewertung:** Technisch erzwungen, nicht nur empfohlen.
- **Anpassungsvorschlag:** keiner

---

**Befund 4.5**

- **Aussage:** Benutzerkonten werden im Regelbetrieb deaktiviert statt physisch gelöscht.
- **Status:** korrekt
- **Beleg:** `DeactivateUserAccountUseCase` — nutzt `user_account_repo.deactivate()`; kein
  Delete-Use-Case oder `users delete`-Befehl im Repository vorhanden
- **Bewertung:** Korrekt. Es gibt keine Lösch-Funktion für Benutzerkonten.
- **Anpassungsvorschlag:** keiner

---

**Befund 4.6**

- **Aussage:** Rollenwechsel, Aktivierung und Deaktivierung sind Administrationsvorgänge
  und müssen protokolliert werden.
- **Status:** korrekt
- **Beleg:** `manage_user_accounts.py` — alle Use Cases (`CreateUserAccountUseCase`,
  `DeactivateUserAccountUseCase`, `ReactivateUserAccountUseCase`,
  `ChangeUserRoleUseCase`) schreiben nach dem Commit einen `AuditLogEntry` mit dem
  jeweiligen Event-Typ (`USER_ACCOUNT_CREATED`, `USER_ACCOUNT_DEACTIVATED`,
  `USER_ACCOUNT_REACTIVATED`, `USER_ACCOUNT_ROLE_CHANGED`)
- **Bewertung:** Korrekt. Protokollierung ist technisch erzwungen.
- **Anpassungsvorschlag:** keiner

---

**Befund 4.7**

- **Aussage:** `REVIEWER` darf keine Benutzerkonten oder Rollen verwalten.
- **Status:** korrekt
- **Beleg:** `manage_user_accounts.py` — alle Schreib-Use-Cases prüfen
  `actor.role != UserRole.ADMIN` und werfen `PermissionDeniedError`; `REVIEWER`-Rolle
  reicht für keine der Schreiboperationen
- **Bewertung:** Korrekt. Benutzerkonten-Verwaltung ist ausschließlich `ADMIN`
  vorbehalten.
- **Anpassungsvorschlag:** keiner

---

**Befund 4.8**

- **Aussage:** `TECH` darf Backup und Systemcheck über die Admin-CLI-Befehlsgruppe
  `system` ausführen (`require_admin_or_tech`).
- **Status:** korrekt
- **Beleg:** `system.py` — beide Funktionen `cmd_system_check` und `cmd_system_backup`
  rufen `require_admin_or_tech(conn, user_id)` auf; `_auth.py` —
  `require_admin_or_tech` prüft `row["role"] not in ("ADMIN", "TECH")`
- **Bewertung:** Korrekt. `TECH` hat Zugriff auf `system check` und `system backup`.
- **Anpassungsvorschlag:** keiner

---

**Befund 4.9**

- **Aussage:** `TECH` darf keine fachlichen Freigaben oder Rollenänderungen vornehmen.
- **Status:** korrekt
- **Beleg:** `manage_user_accounts.py` — alle Use Cases fordern `role == UserRole.ADMIN`;
  Freigabe-Use-Cases (z. B. `cmd_bookings_approve_supplement`) stehen im Dispatch-Table
  ohne separate Rollenprüfung für `TECH`
- **Bewertung:** Korrekt.
- **Anpassungsvorschlag:** keiner

---

**Befund 4.10**

- **Aussage:** Für einen Restore-Vorgang existiert kein eigener Admin-CLI-Befehl; ein
  Restore ist nur programmatisch über `SQLiteBackupService.restore_from()` möglich.
- **Status:** korrekt (mit Präzisierungsbedarf)
- **Beleg:**
  - Kein `restore`-Subcommand in `system.py` → `register_subcommands()` registriert
    nur `check` und `backup`
  - `backup_service.py` — `SQLiteBackupService.restore_from()` ist vorhanden und
    vollständig implementiert (inkl. Integritätsprüfung nach Restore und Audit-Log-Eintrag)
  - Kein öffentliches Skript oder CLI-Wrapper für `restore_from` im Repository auffindbar
- **Bewertung:** Korrekt, dass kein CLI-Befehl existiert und die Methode
  `SQLiteBackupService.restore_from()` vorhanden ist. Die Formulierung „nur
  programmatisch" ist jedoch unvollständig: Sie beschreibt den aktuellen Zustand
  (kein CLI-Befehl), lässt aber offen, wie ein Restore konkret durchzuführen ist.
  Kein Skript, keine Anleitung und kein Beispiel-Code-Snippet sind im Repository oder
  Dokument vorhanden.
- **Anpassungsvorschlag:** Formulierung erweitern: „Für einen Restore existiert kein
  Admin-CLI-Befehl. Die Methode `SQLiteBackupService.restore_from(backup_path)` ist
  in `src/arbeitszeit/infrastructure/backup/backup_service.py` implementiert und muss
  programmatisch aufgerufen werden. Eine Anleitung hierzu ist separat zu ergänzen."

---

## Zusammenfassung der Befunde

| Nr.  | Kapitel | Status                  | Schwere   |
|------|---------|-------------------------|-----------|
| 1.1  | 1       | korrekt                 | —         |
| 1.2  | 1       | korrekt                 | —         |
| 1.3  | 1       | korrekt                 | —         |
| 1.4  | 1       | korrekt                 | —         |
| 1.5  | 1       | korrekt                 | —         |
| 1.6  | 1       | korrekt                 | —         |
| 2.1  | 2       | nicht verifizierbar     | gering    |
| 2.2  | 2       | nicht verifizierbar     | mittel    |
| 2.3  | 2       | korrekt                 | —         |
| 2.4  | 2       | korrekt                 | —         |
| 2.5  | 2       | nicht verifizierbar     | gering    |
| 3.1  | 3       | korrekt                 | —         |
| 3.2  | 3       | korrekt                 | —         |
| 3.3  | 3       | korrekt                 | —         |
| 3.4  | 3       | korrekt                 | —         |
| 3.5  | 3       | korrekt                 | —         |
| 3.6  | 3       | korrekt                 | —         |
| 3.7  | 3       | nicht verifizierbar     | **hoch**  |
| 3.8  | 3       | nicht verifizierbar     | mittel    |
| 4.1  | 4       | korrekt                 | —         |
| 4.2  | 4       | nicht verifizierbar     | gering    |
| 4.3  | 4       | korrekt                 | —         |
| 4.4  | 4       | korrekt                 | —         |
| 4.5  | 4       | korrekt                 | —         |
| 4.6  | 4       | korrekt                 | —         |
| 4.7  | 4       | korrekt                 | —         |
| 4.8  | 4       | korrekt                 | —         |
| 4.9  | 4       | korrekt                 | —         |
| 4.10 | 4       | korrekt (mit Präzisierung) | gering |

**Korrekt:** 19 | **Nicht verifizierbar:** 9 | **Inkorrekt:** 0

---

## Offene Punkte für manuelle Klärung

1. **Befund 3.7 (hoch):** Beispielaufruf für `users bootstrap` fehlt. Bei Überarbeitung
   muss der korrekte Aufruf **ohne** `--user-id` ergänzt werden.
2. **Befund 3.8 (mittel):** Keine Hinweise auf Installationsvoraussetzungen (kein
   `console_scripts`-Einstiegspunkt, Paket liegt unter `src/`).
3. **Befund 2.2 (mittel):** Schritt „Deployment-spezifische Pfade konfigurieren" hat
   keinen belegbaren CLI-Befehl. Konkreter Konfigurationsweg ist zu klären und zu
   dokumentieren.
4. **Befund 4.10 (gering):** Konkrete Anleitung zum Restore-Vorgang fehlt im Dokument
   und im Repository.
