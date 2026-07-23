# Das Verwaltungsprogramm — Kurzanleitung

**Kapitel:** 4-Laien
**Version:** 1.4
**Stand:** Juli 2026
**Zielgruppe:** Praxisleitung, Verwaltung

## Zwei Zugangswege

Das System hat zwei verschiedene Benutzerschnittstellen:

| Schnittstelle | Wer | Wozu |
| --- | --- | --- |
| Terminal (Buchungsbildschirm) | alle Mitarbeitenden | Kommen, Gehen, Pause |
| Admin-Programm (Kommandozeile) | Praxisleitung, Admin | Verwaltung, Berichte, Korrekturen |

Dieses Kapitel beschreibt das Admin-Programm.

## Das Admin-Programm starten

Das Admin-Programm wird über die Kommandozeile gestartet. Wenn der
Kurzbefehl `azadmin` eingerichtet ist, lautet der Aufruf z. B.:

```bash
azadmin employees list --db arbeitszeit.db
```

Ohne Kurzbefehl:

```bash
python -m arbeitszeit.presentation.admin_cli.main employees list --db arbeitszeit.db
```

Die meisten Befehle benötigen `--db` (Datenbankpfad) und `--user-id`
(Ihre Admin-Benutzer-ID). Ist `config.toml` eingerichtet, werden diese
Werte automatisch aus der Konfigurationsdatei gelesen.

## Mitarbeitende verwalten

```bash
# Alle Mitarbeitenden anzeigen
azadmin employees list

# Neue Mitarbeitende anlegen
azadmin employees add --personnel-no 042 \
  --first-name Anna --last-name Muster

# Mitarbeitende deaktivieren
azadmin employees deactivate 5
```

## RFID-Karten verwalten

```bash
# Karte einer Mitarbeiterin zuweisen
azadmin cards assign --employee-id 3 --uid-hash abc123

# Karte ersetzen (alte wird automatisch deaktiviert)
azadmin cards replace --old-card-id 7 --uid-hash xyz789

# Karte deaktivieren (z. B. bei Verlust)
azadmin cards deactivate 7
```

## Buchungen korrigieren und Nachträge

```bash
# Buchung korrigieren
azadmin bookings correct --booking-id 17 \
  --type GO --at "15.07.2026 17:30" \
  --reason "Falsche Uhrzeit"

# Nachtrag anlegen (vergessene Buchung)
azadmin bookings supplement --employee-id 3 \
  --type COME --at "14.07.2026 08:00" \
  --reason "Stempelgerät war defekt"

# Nachtrag genehmigen
azadmin bookings approve-supplement --supplement-id 12

# Nachtrag ablehnen
azadmin bookings reject-supplement --supplement-id 12 \
  --reason "Buchung bereits vorhanden"
```

## Berichte

```bash
# Offene Buchungsphasen (ohne passendes Ende)
azadmin reports open-bookings

# Warnungen anzeigen (--from und --to sind Pflicht)
azadmin reports warn-cases --from 01.07.2026 --to 31.07.2026

# Offene Prüffälle anzeigen
azadmin reports open-review-cases

# Monatsbericht als PDF erstellen
azadmin reports export-pdf-month --year 2026 --month 7

# Buchungen als CSV exportieren (--from und --to sind Pflicht)
azadmin reports export-csv --from 01.07.2026 --to 31.07.2026
```

## Dienstplan

```bash
# Standardarbeitszeit für Montag einstellen
azadmin schedule set --weekday 1 --start 07:30 --end 18:00 \
  --from 01.08.2026

# Aktuellen Dienstplan anzeigen
azadmin schedule show
```

## Systemfunktionen

```bash
# Systemprüfung ausführen
azadmin system check

# Backup erstellen
azadmin system backup
```

## Benutzerkonten

```bash
# Benutzerkonten anzeigen
azadmin users list

# Neues Benutzerkonto anlegen
azadmin users add --username reviewer1 --role REVIEWER

# Ersten Admin einrichten (nur beim allerersten Start)
azadmin users bootstrap --username admin
```

## Das Buchungsterminal

Das Terminal läuft als eigenes Programm, das dauerhaft im Hintergrund
aktiv ist. Am Beginn jedes Zyklus erscheint die Aufforderung „Karte an
das RFID-Lesegerät halten …" auf dem Bildschirm. Mitarbeitende halten
ihre RFID-Karte kurz an den Reader — das System erkennt automatisch,
welche Buchungsart als nächste fällig ist (Kommen, Pause, Gehen), und
bestätigt die Buchung auf dem Bildschirm.

**Kurztag-Regelung:** Bei Schichten mit einer Solldauer von höchstens
6 Stunden entfällt die Pausenpflicht (§ 4 ArbZG). Das System bucht
beim zweiten Scan direkt „Gehen" statt „Pause beginnen". Ein dritter
Scan wird mit einer Fehlermeldung abgewiesen.

**Doppel-Scan-Schutz:** Wird dieselbe Karte innerhalb von 3 Sekunden
nochmals vorgehalten, ignoriert das Terminal den Scan automatisch.

Das Terminal läuft in einer Endlosschleife und muss nur bei Wartung
oder Konfigurationsänderungen neu gestartet werden. Es überprüft beim
Start automatisch, ob alle Komponenten betriebsbereit sind.

Fehler während einer Buchung führen nicht zum Absturz des Terminals —
das System protokolliert den Fehler und läuft weiter.

## Offene Vortagsschichten prüfen

Wenn ein Mitarbeitender vergessen hat, sich am Vortag auszustempeln,
erkennt das System das beim nächsten Scan und hinterlegt automatisch
einen Audit-Eintrag. Die Praxisleitung kann diese Fälle abfragen:

```bash
azadmin --db arbeitszeit.db audit open-shifts
```
