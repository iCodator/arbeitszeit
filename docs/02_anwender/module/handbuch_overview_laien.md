# Systemübersicht — Was ist das und wer benutzt was?

**Kapitel:** 1-Laien
**Version:** 1.1
**Stand:** Juli 2026
**Zielgruppe:** Praxisleitung, Verwaltung

## Was ist das Zeiterfassungssystem?

Das Zeiterfassungssystem `arbeitszeit` ist eine lokale Software zur
Arbeitszeiterfassung für Zahnarztpraxen. Es läuft auf einem eigenen Rechner
in der Praxis — keine Cloud, keine externe Anmeldung, keine Internetabhängigkeit.

Die erfassten Zeiten werden in einer lokalen Datenbank gespeichert und können
als PDF-Bericht oder CSV-Tabelle exportiert werden.

## Was kann das System?

- Arbeitszeiten per RFID-Karte erfassen (Kommen, Gehen, Pause)
- Buchungssequenzen automatisch prüfen (z. B. Pause muss vor Gehen kommen)
- Arbeitszeitgrenzen nach dem Arbeitszeitgesetz automatisch überwachen
- Nachträge anlegen und genehmigen (für vergessene Buchungen)
- Buchungen nachträglich korrigieren (mit Protokoll)
- Monatsberichte als PDF erstellen
- Buchungen als CSV exportieren
- Datensicherungen erstellen (lokal und optional auf Netzlaufwerk)

## Wer benutzt was?

| Personengruppe | Wie | Womit |
| --- | --- | --- |
| Alle Mitarbeitenden | Buchungsterminal | RFID-Karte |
| Praxisleitung, Verwaltung | Admin-Programm (`azadmin`) | Kommandozeile |
| IT-Betreuung | Admin-Programm + Systemdateien | Kommandozeile, Konfiguration |

Mitarbeitende brauchen kein eigenes Konto — ihre Identität wird über die
RFID-Karte erkannt. Nur Verwaltungspersonen (Admin, Prüfer, Techniker)
erhalten Benutzerkonten im System.

## Wo liegen die Daten?

Alle Daten liegen in einer einzigen Datei: `arbeitszeit.db`. Der Speicherort
ist in der Konfigurationsdatei `config.toml` hinterlegt. Regelmäßige Backups
dieser Datei sind wichtig — das System kann sie auf Befehl erstellen.

## Womit werden Berichte erstellt?

```bash
# Monatsbericht Juli 2026 als PDF
azadmin reports export-pdf-month --year 2026 --month 7 \
  --output /tmp/bericht_juli.pdf

# Alle Buchungen als CSV
azadmin reports export-csv --output /tmp/buchungen.csv
```

## Was brauche ich um loszulegen?

1. Das System muss von Ihrer IT-Betreuung eingerichtet worden sein
   (Datenbank angelegt, Konfiguration gesetzt, erster Admin-Account erstellt).
2. Mitarbeitende brauchen RFID-Karten, die im System eingetragen sind.
3. Sie benötigen Ihre Admin-Benutzer-ID (`--user-id`) für Verwaltungsaufgaben.

Alles Weitere — Mitarbeitende anlegen, Karten zuweisen, Berichte erstellen —
ist im vollständigen Anwenderhandbuch (`docs/02_anwender/handbuch.md`)
und in den Detailkapiteln dieses Verzeichnisses beschrieben.
