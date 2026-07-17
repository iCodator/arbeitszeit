# Die Datenbank — was wird gespeichert?

**Kapitel:** 7-Laien
**Version:** 1.0
**Stand:** Juli 2026
**Zielgruppe:** Praxisleitung, Verwaltung

## Die Datenbank wird automatisch verwaltet

Das System speichert alle Daten in einer einzigen Datenbankdatei
(`arbeitszeit.db`). Diese Datei wird automatisch angelegt und aktualisiert —
Sie müssen nie direkt in die Datenbank eingreifen.

Der Pfad zur Datenbankdatei ist in `config.toml` unter `[database]` eingetragen
und kann mit `scripts/show_config.py` abgerufen werden (Kapitel 8).

## Was wird gespeichert?

Die Datenbank enthält folgende Datenbereiche:

| Datenbereich | Was wird gespeichert |
| --- | --- |
| Mitarbeitende | Name, Personalnummer, aktiv/inaktiv |
| RFID-Karten | Kartenkennung, zugehörige Mitarbeiterin, Status |
| Buchungen | Alle Kommen/Gehen/Pause-Einträge mit Zeitstempel und Status |
| Korrekturen | Jede nachträgliche Buchungsänderung mit Grund und Benutzer |
| Nachträge | Manuell erfasste Buchungsergänzungen mit Genehmigungsstatus |
| Prüffälle | Regelauffälligkeiten, die bearbeitet werden müssen |
| Dienstplan | Soll-Arbeitszeiten nach Wochentag |
| Benutzerkonten | Admin-, Prüfer- und Technikerkonten |
| Systemeinstellungen | Interne Konfigurationswerte (Zeitzone, Toleranzen) |
| Systemereignisse | Protokoll von Backups, Systemprüfungen und Fehlern |

## Backup und Wiederherstellung

Regelmäßige Backups der Datenbankdatei sind wichtig. Das System erstellt
auf Befehl eine Sicherungskopie, ohne den laufenden Betrieb zu unterbrechen:

```bash
azadmin system backup --db arbeitszeit.db
```

Bei Datenverlust kann die Datenbank aus einer Sicherungskopie
wiederhergestellt werden. Wenden Sie sich dafür an Ihre IT-Betreuung.

## Was Sie nie tun sollten

Öffnen oder bearbeiten Sie die Datenbankdatei niemals direkt mit externen
Programmen. Das kann die Datenbank beschädigen und zu Datenverlust führen.
Alle Änderungen an den gespeicherten Daten erfolgen ausschließlich über
das Admin-Programm (`azadmin`) oder das Buchungsterminal.
