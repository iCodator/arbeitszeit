Programmieraufgabe: init_db.py prüft Setup-Vollständigkeit
Herleitung aus phase1_planung.md
Das Dokument beschreibt scripts/init_db.py als Initialisierungsskript mit der Anforderung: „Gibt Rückmeldung an stdout." Aktuell beschränkt sich die Rückmeldung auf „Migration X angewendet." — ohne Hinweis, ob das System danach betriebsbereit ist.

Der heutige Stand hat zwei Skripte mit einer impliziten Reihenfolge:

1. init_db.py — legt Schema + Seeds an
2. setup.py — setzt deployment-spezifische Keys (backup.backup_dir, export.export_dir)

Ohne Schritt 2 schlägt admin system check mit Fehler fehl (config_keys: FAIL), obwohl die Migrationen erfolgreich waren. Es gibt keinen Hinweis auf diese Lücke — außerdem endet setup.py aktuell mit der falschen Reihenfolge:

„Weiter mit: python scripts/init_db.py --db … (falls noch nicht erledigt)"

Aufgabe
scripts/init_db.py nach erfolgter Migration prüfen, ob die Deployment-Keys gesetzt sind, und den Nutzer klar führen.

Konkret

1. init_db.py: Setup-Check nach Migrationen

Nach run_migrations() prüfen, ob backup.backup_dir und export.export_dir in system_config vorhanden sind. Abhängig vom Ergebnis:


# Fall A: Neue Migrationen wurden angewendet, Setup fehlt noch
Migration 0001 angewendet.
...
Migration 0006 angewendet.
⚠  Ersteinrichtung noch erforderlich:
   python scripts/setup.py --db /pfad/zur/db

# Fall B: DB war bereits aktuell, Setup bereits erfolgt
Keine neuen Migrationen. System betriebsbereit.

# Fall C: DB war bereits aktuell, Setup fehlt noch
Keine neuen Migrationen.
⚠  Ersteinrichtung noch erforderlich:
   python scripts/setup.py --db /pfad/zur/db
Optional: --with-setup-Flag, das setup.py-Logik direkt aufruft (interaktiv oder mit --backup-dir/--export-dir-Durchreichung).

2. setup.py: Abschlussmeldung korrigieren

Die falsche Zeile


print("Weiter mit: python scripts/init_db.py --db ... (falls noch nicht erledigt)")
durch eine korrekte Betriebsanweisung ersetzen:


print("System bereit. Terminal-UI: python -m arbeitszeit.presentation.terminal_ui.main")
print("Admin-CLI:  python -m arbeitszeit.presentation.admin_cli.main --user-id <ID>")
Betroffene Dateien
Datei	Änderung
scripts/init_db.py	Setup-Check + Ausgabe nach Migration
scripts/setup.py	Abschlussmeldung korrigieren
tests/	ggf. einen Test für den Check-Pfad
Akzeptanzkriterium
python scripts/init_db.py --db frisch.db auf einer frischen DB endet mit einem klaren Hinweis auf setup.py. Nach Ausführen von setup.py zeigt admin system check Gesamt: OK.