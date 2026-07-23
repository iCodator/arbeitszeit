# Wie überprüfe ich ob alles läuft?

**Kapitel:** 9-Laien
**Version:** 1.3
**Stand:** Juli 2026
**Zielgruppe:** Praxisleitung, Verwaltung

## Zwei Arten von Systemprüfungen

Das System bietet zwei verschiedene Arten von Prüfungen:

1. **Systemprüfung** — prüft, ob alle technischen Komponenten des
   laufenden Betriebs in Ordnung sind (Datenbank, Konfiguration, Geräte,
   Zeitserver).
2. **Codeprüfung** — ein technisches Werkzeug für Entwickler, das die
   Softwarequalität prüft. Sie müssen sich darum nicht kümmern.

## Die Systemprüfung

Die Systemprüfung prüft automatisch 8 Punkte und zeigt an, ob alles
in Ordnung ist.

### Wann wird die Systemprüfung ausgeführt?

- **Automatisch** bei jedem Start des Buchungsterminals. Wenn ein
  Problem erkannt wird, erscheint eine Warnung — der Buchungsbetrieb
  wird aber trotzdem fortgesetzt.
- **Manuell auf Abruf** über den folgenden Befehl:

```bash
azadmin --db arbeitszeit.db system check
```

### Was wird geprüft?

| Nr. | Was wird geprüft | Wann ist es ein Problem? |
| --- | --- | --- |
| 1 | Datenbankstand | Migrationen wurden nicht vollständig ausgeführt |
| 2 | Pflicht-Einstellungen | Systemkonfiguration fehlt oder ist unvollständig |
| 3 | Backup-Speicherort | Der Sicherungsordner ist nicht erreichbar |
| 4 | Datenbankintegrität | Interne Datenbankverknüpfungen sind beschädigt |
| 5 | Verzeichnisse | Backup- oder Exportordner existiert nicht |
| 6 | Zeitserver | Systemzeit ist nicht synchronisiert |
| 7 | Eingabegeräte | RFID-Reader nicht erreichbar |
| 8 | Sicherheitsschlüssel | Audit-Log-Schlüssel `AUDIT_HMAC_KEY` fehlt oder ist leer |

### Was tun wenn die Prüfung Fehler zeigt?

Bei Fehlern in der Systemprüfung wenden Sie sich an Ihre IT-Betreuung.
Das System notiert alle Prüfergebnisse automatisch in der Datenbank
(`SELFTEST_OK` oder `SELFTEST_FAIL`), damit der Verlauf nachvollziehbar bleibt.

## Vergessene Abmeldungen abfragen

Wenn eine Mitarbeiterin am Vortag vergessen hat, sich auszustempeln,
speichert das System das beim nächsten Scan automatisch. Diese Fälle
können Sie jederzeit abfragen:

```bash
azadmin --db arbeitszeit.db audit open-shifts
```

Das Programm zeigt eine Liste aller erkannten vergessenen Abmeldungen der
letzten 30 Tage — mit Name, Datum und letzter bekannter Buchung. Falls
Sie einen längeren Zeitraum prüfen möchten:

```bash
azadmin --db arbeitszeit.db audit open-shifts --days 90
```

## Wann sollte ich die Systemprüfung manuell ausführen?

- Nach einem Stromausfall
- Nach einer Änderung der Konfiguration
- Wenn das Terminal ungewöhnlich reagiert oder Buchungen fehlschlagen
- Als regelmäßige Routinekontrolle (z. B. einmal pro Woche)
