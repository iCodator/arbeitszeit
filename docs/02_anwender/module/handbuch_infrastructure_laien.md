# Das technische Rückgrat — Konfiguration und Betrieb

**Kapitel:** 6-Laien
**Version:** 1.2
**Stand:** Juli 2026
**Zielgruppe:** Praxisleitung, Verwaltung

## Was ist die Infrastruktur?

Das System besteht aus mehreren Teilen: der Benutzeroberfläche (Terminal und
Admin-Programm), der Datenbank und dem technischen Rückgrat. Das technische
Rückgrat kümmert sich automatisch um Datenbankzugriff, Konfiguration, Backups,
Hardwareanschluss (RFID) und Systemprüfungen.

Als Praxisleitung oder Verwaltung müssen Sie hier in der Regel nichts
konfigurieren — Ihre IT-Betreuung hat das beim Einrichten des Systems erledigt.

## Die Konfigurationsdatei

Das System liest seine Einstellungen aus einer Textdatei namens `config.toml`.
Eine typische Konfiguration sieht so aus:

```toml
[database]
path = "/home/user/data/arbeitszeit.db"

[terminal]
id = 1
rfid = "Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader"

[backup]
backup_dir = "/var/backups/arbeitszeit"
export_dir = "/var/exports/arbeitszeit"
log_dir    = "/var/log/arbeitszeit"
```

**Was bedeuten die Abschnitte?**

| Abschnitt | Bedeutung |
| --- | --- |
| `[database]` | Wo liegt die Datenbankdatei |
| `[terminal]` | Welches Buchungsterminal ist das (Nummer, Gerätename) |
| `[backup]` | Wo werden Sicherungen gespeichert |

Die aktuelle Konfiguration können Sie jederzeit mit dem Befehl
`scripts/show_config.py` einsehen (siehe Kapitel 8).

## Backup

Das System kann Datensicherungen erstellen:

```bash
# Lokale Sicherung erstellen
azadmin --db arbeitszeit.db system backup
```

Das Backup läuft im Hintergrund, ohne den laufenden Betrieb zu unterbrechen —
Buchungen können während der Sicherung weiter erfasst werden. Die Sicherungsdatei
wird im konfigurierten Backup-Verzeichnis abgelegt
(Standard: `backup.backup_dir` in `config.toml`).

Falls ein Netzlaufwerk (NAS) konfiguriert ist, wird die Sicherung anschließend
automatisch dorthin übertragen.

## Systemprüfung

Die Systemprüfung prüft, ob alle technischen Komponenten in Ordnung sind.
Sie wird automatisch bei jedem Start des Buchungsterminals ausgeführt und
kann auch manuell aufgerufen werden:

```bash
azadmin --db arbeitszeit.db system check
```

Was die Systemprüfung prüft und wann Sie sie aufrufen sollten, ist im
Kapitel 9 (Systemprüfung) beschrieben.

## Was Sie nicht selbst anpassen sollten

Die Konfigurationsdatei sollte ausschließlich von Ihrer IT-Betreuung geändert
werden. Falsche Einstellungen können dazu führen, dass das Terminal oder das
Admin-Programm nicht mehr starten.

Bei Problemen mit der Hardware (RFID-Reader) oder der Datenbankverbindung
wenden Sie sich ebenfalls an Ihre IT-Betreuung.

## Doppel-Scan-Schutz

Das System erkennt automatisch, wenn dieselbe RFID-Karte innerhalb von
3 Sekunden ein zweites Mal vorgehalten wird. Der zweite Scan wird dann
stillschweigend ignoriert — es genügt, die Karte einmal kurz an den
Reader zu halten. Dieser Schutz verhindert technisches Rauschen durch
unbeabsichtigtes doppeltes Auflegen.
