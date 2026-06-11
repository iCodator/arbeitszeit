# Handbuch-Ergänzung Rollen-CLI für arbeitszeit – Version 1.1

Für das eigentliche Handbuch `handbuch_arbeitszeit_print.html` lag in den verfügbaren Dateien in diesem Arbeitsstand kein lesbarer Volltext vor. Deshalb wird hier eine direkt einarbeitbare Ergänzungsfassung für die betroffenen Handbuchteile bereitgestellt.

## 1. Ergänzung Admin-CLI-Befehlsübersicht

Die vorhandene Befehlsübersicht ist um die Benutzerverwaltung zu erweitern.

| Gruppe | Befehl | Beschreibung |
|---|---|---|
| users | list | Benutzerkonten anzeigen |
| users | add | Neues Benutzerkonto für `ADMIN`, `REVIEWER` oder `TECH` anlegen |
| users | deactivate | Benutzerkonto deaktivieren |
| users | reactivate | Benutzerkonto reaktivieren |
| users | change-role | Rolle eines Benutzerkontos ändern |
| users | set-password | Passwort initial setzen oder zurücksetzen |

## 2. Ergänzung Ersteinrichtung

Die Ersteinrichtung ist in dieser Reihenfolge zu beschreiben:

1. Datenbank initialisieren.
2. Deployment-spezifische Pfade konfigurieren.
3. Ersten Administrator über den Bootstrap-Prozess anlegen.
4. Weitere Benutzerkonten für Prüfer und technische Betreuung über die Admin-CLI anlegen.
5. Erst danach in den regulären Betrieb übergehen.

## 3. Beispielaufrufe

```bash
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username admin1 --role ADMIN
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username pruefer1 --role REVIEWER
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username tech1 --role TECH
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users deactivate 3
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users reactivate 3
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users change-role --id 3 --role REVIEWER
```

## 4. Fachliche Klarstellungen für das Handbuch

Diese Punkte sollten im Handbuchtext ausdrücklich genannt werden:

- Benutzerkonten für `ADMIN`, `REVIEWER` und `TECH` werden regulär über die Admin-CLI verwaltet.
- Direkte SQL-Änderungen an Benutzerkonten sind kein regulärer Betriebsprozess.
- Der erste Administrator wird über einen gesonderten Bootstrap-Prozess eingerichtet.
- Der Bootstrap-Prozess darf nur verwendet werden, solange noch kein aktives Administratorkonto vorhanden ist.
- Benutzerkonten werden im Regelbetrieb deaktiviert statt physisch gelöscht.
- Rollenwechsel, Aktivierung und Deaktivierung sind Administrationsvorgänge und müssen protokolliert werden.
- `REVIEWER` darf keine Benutzerkonten oder Rollen verwalten.
- `TECH` darf Backup, Restore, Systemcheck und betriebsnahe Systemfunktionen ausführen, aber keine fachlichen Freigaben oder Rollenänderungen vornehmen.
