# Betriebsdokumentation – arbeitszeit

**Version:** 1.1  
**Datum:** 2026-06-13  
**Grundlage:** `docs/claude_coding/claude_code_prompt_hoch_arbeitszeit_v1_2026-06-11_20-08.md`

**Methodik:** Alle Aussagen sind ausschließlich aus Repo-Artefakten belegt.
Technische Aussagen: aus Code und Phasenplänen. Betriebsregeln: aus Phasenplänen
explizit als „Betriebsregel/Betriebsentscheidung" ausgewiesen. Organisatorische
Auflagen: aus Pflichtenheft v5 / Regelwerk v5 / planung_gesamt.md — ohne
Freigabe-Behauptung.

**Abkürzungen:** PH = Pflichtenheft v5, RW = Regelwerk v5

---

## 1. Systemübersicht

Das System `arbeitszeit` ist ein lokales Zeiterfassungssystem für eine Zahnarztpraxis.
Es besteht aus fünf Komponenten:

1. **SQLite-Datenbank** — lokale Datenhaltung (WAL-Modus), Migrations-basierte Versionierung
2. **Terminal-UI** — Arbeitnehmer-RFID-Erfassung am Zeiterfassungsterminal
3. **Admin-CLI** — administrative Verwaltung (Mitarbeiter, Zeitkorrekturen, Exporte)
4. **Backup-Service** — lokale Sicherung + optionale NAS-Spiegelung
5. **System-Check** — Selbstprüfung der Konfiguration und Geräte

**Technische Basis:** Python 3.11–3.12, SQLite ≥ 3.35 (WAL + RETURNING-Support),
`evdev` für RFID-Hardware, `fpdf2` für PDF-Export.

---

## 2. Ersteinrichtung

**Beleg:** `scripts/init_db.py`, `scripts/setup.py`, `phase4_planung.md Schritt 9`

### 2.1 Datenbankinitialisierung

```bash
python scripts/init_db.py --db arbeitszeit.db
```

- Führt alle Migrationsdateien unter `migrations/` in numerischer Reihenfolge aus
- Idempotent: bereits angewandte Migrationen werden nicht erneut ausgeführt
- `setup_vollstaendig()` prüft anschließend, ob `backup.backup_dir` und
  `export.export_dir` in `system_config` gesetzt sind

### 2.2 Systemkonfiguration interaktiv

```bash
python scripts/setup.py --db arbeitszeit.db
```

Setzt interaktiv folgende Pflicht-Keys in `system_config`:
- `backup.backup_dir` — Zielverzeichnis für lokale Backups
- `export.export_dir` — Exportverzeichnis für CSV/PDF-Auswertungen

Optionale Keys (NAS, Terminal-ID, Zeitmonitor-Schwellenwert) werden ebenfalls
abgefragt, können aber leer gelassen werden.

### 2.3 Bootstrap: Ersten Admin-Account anlegen

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  users bootstrap \
  --username NAME --password PASSWORT
```

Dieser Pfad erfordert kein `--user-id`, da noch kein Admin existiert. Die Funktion
prüft vor Ausführung, ob bereits ein aktiver Admin existiert; falls ja, wird der
Aufruf abgelehnt.  
**Beleg:** `presentation/admin_cli/user_accounts.py cmd_users_bootstrap()`

### 2.4 Systemcheck nach Einrichtung

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db --user-id <ID> \
  system check
```

`infrastructure/system_check.py` besitzt keinen eigenständigen `__main__`-Einstiegspunkt;
der Aufruf erfolgt ausschließlich über die Admin-CLI (`system check`).  
Prüft: DB-Zugriff, Pflicht-Konfigurationskeys, optionale Gerätepfade, NAS-Erreichbarkeit,
Fremdschlüssel-Konsistenz, NTP-Synchronisation.  
**Beleg:** `infrastructure/system_check.py`, `presentation/admin_cli/system.py`, `phase4_planung.md Schritt 9`

---

## 3. Laufendes Betrieb — Terminal-UI

**Beleg:** `presentation/terminal_ui/main.py`, `phase5_planung.md`

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db arbeitszeit.db \
  --numpad /dev/input/eventX \
  --rfid /dev/input/eventY \
  --terminal-id 1
```

`--numpad` und `--rfid` sind Pflichtargumente (`presentation/terminal_ui/main.py`).

### 3.1 Ablauf pro Zyklus

1. RFID-Karte lesen (Hardware oder Simulator)
2. `device_events`-Record schreiben (Autocommit, vor Transaktion)
3. `BookUseCase` ausführen (COME/GO/BREAK-Logik, Ruhezeitprüfung; keine Rollenprüfung, siehe Designentscheidung unten)
4. Ergebnis ausgeben; Fehler → APPLICATION_ERROR in `system_events` protokollieren

**Designentscheidung — rollenlose Terminal-Buchung (Regelwerk v5 §16):**  
Terminal-Buchungen prüfen keine `UserRole`. Die Authentifikation des Mitarbeiters
erfolgt ausschließlich über die gültige, aktiv-gestellte RFID-Karte. Dies ist die
vom Regelwerk v5 §16 vorgesehene Mitarbeiteraktion; eine zusätzliche Benutzerkonten-
Prüfung ist darin nicht gefordert. Schreibende Administrationsaktionen (Korrekturen,
Nachträge, Regelzeitänderungen) prüfen die `UserRole` gesondert in ihren jeweiligen
Use Cases.

### 3.2 Zeitmonitor

Läuft parallel im Terminal-UI. Prüft Systemzeitsprünge bei jedem Buchungszyklus
(ereignisgetrieben, kein fester 30-Sekunden-Takt im Code nachweisbar).  
Schwellenwert: `time_monitor.jump_threshold_seconds` aus `system_config`
(Standard: 60 Sekunden).

Erkannte Ereignisse werden als `TIME_JUMP_DETECTED` oder
`MANUAL_TIME_CHANGE_DETECTED` in `system_events` geschrieben.  
**Beleg:** `infrastructure/time_monitor.py`, `phase5_planung.md Schritt 5`

**Hinweis: Fehlerbehandlung Zeitmonitor**  
Kann der Zeitmonitor interne Ereignisse (z. B. Schreibfehler in `system_events`)
nicht protokollieren, werden diese Fehler mindestens als Warnung im Log erfasst.
Damit bleibt ein defekter Zeitmonitor nicht unbemerkt; die eigentliche
Arbeitszeiterfassung läuft jedoch weiter.

### 3.3 Gerätesimulator

Für Tests ohne Echthardware: `SimulatedHardwareReader` wird derzeit nur direkt in
Testcode instanziiert (z. B. `tests/presentation/test_booking_loop.py`); ein CLI-Flag
zur Aktivierung im Terminal-UI-Einstiegspunkt (etwa `--simulator`) existiert nicht.  
**Beleg:** `infrastructure/hardware/simulator.py`

---

## 4. Laufendes Betrieb — Admin-CLI

**Beleg:** `presentation/admin_cli/main.py`, `presentation/admin_cli/user_accounts.py`,
`presentation/admin_cli/employees.py`, `phase5_planung.md`

Alle Admin-CLI-Befehle erfordern `--db` und (außer `users bootstrap`) `--user-id`
oder die Umgebungsvariable `ADMIN_USER_ID`.

### 4.1 Benutzerkontenverwaltung

| Befehl | Funktion | Rollenanforderung |
| --- | --- | --- |
| `users add` | Neuen Benutzer anlegen | ADMIN |
| `users list` | Alle Benutzer auflisten | ADMIN |
| `users deactivate` | Konto deaktivieren | ADMIN |
| `users reactivate` | Konto reaktivieren | ADMIN |
| `users change-role` | Rolle ändern | ADMIN |
| `users bootstrap` | Ersten Admin anlegen | kein aktiver Admin vorhanden |

**Beleg:** `presentation/admin_cli/user_accounts.py`

**Hinweis: Passwort-Hashing (DSGVO Art. 32)**  
Passwörter werden nicht im Klartext gespeichert. Die Admin-CLI verwendet
PBKDF2-HMAC-SHA256 mit einem zufälligen Salt und einer erhöhten Iterationszahl,
um die Passwörter vor einfachen Brute-Force-Angriffen zu schützen. Dieses Verfahren
ist als technische Maßnahme im Sinne von DSGVO Art. 32 zu verstehen und für die
lokale Einzelplatzanwendung der Praxis angemessen. Die konkrete Ausgestaltung
(Iterationszahl, Salt-Länge) ist im Quellcode (`user_accounts.py`) dokumentiert.

### 4.2 Mitarbeiterverwaltung

| Befehl | Funktion |
| --- | --- |
| `employees add` | Mitarbeiter anlegen |
| `employees list` | Alle Mitarbeiter auflisten |
| `employees deactivate` | Mitarbeiter deaktivieren |

**Beleg:** `presentation/admin_cli/employees.py`

### 4.3 Zeitbuchungen

| Befehl | Funktion |
| --- | --- |
| `bookings correct` | Buchungskorrektur (CorrectBookingUseCase) |
| `bookings supplement` | Nachtragsantrag einreichen |
| `bookings approve-supplement` | Nachtragsantrag genehmigen (REVIEWER oder ADMIN) |
| `bookings reject-supplement` | Nachtragsantrag ablehnen (REVIEWER oder ADMIN) |

Ein eigenständiges Listing-Kommando `bookings list` existiert nicht; Auflistungen
laufen über `reports open-bookings`, `reports warn-cases`, `reports corrections`
bzw. `reports supplements`.

### 4.4 Exporte

| Befehl | Funktion |
| --- | --- |
| `reports export-csv` | CSV-Auswertung (Detail + verdichtet, filterbar nach `--from`/`--to`/`--employee-id`) |
| `reports export-csv-review-cases` | Offene Prüffälle als CSV exportieren |
| `reports export-pdf-day` / `export-pdf-week` / `export-pdf-month` / `export-pdf-employee` | PDF-Report (Tag/Woche/Monat/Mitarbeiter) |

Ein eigenständiger `export`-Domain-Befehl mit Unterbefehlen `csv`/`pdf` existiert
nicht; die tatsächliche Struktur liegt unter der Domain `reports`.  
**Beleg:** `presentation/admin_cli/reports.py`, `infrastructure/export/report_queries.py`, `phase4_planung.md Schritt 8`

---

## 5. Backup-Betrieb

**Beleg:** `scripts/backup.py`, `infrastructure/backup/backup_service.py`,
`phase4_planung.md Schritt 7`

### 5.1 Lokales Backup erstellen

```bash
python scripts/backup.py \
  --db arbeitszeit.db \
  --backup-dir backups/ \
  [--export-dir exports/]
```

- Erzeugt timestamped SQLite-Copy im `--backup-dir`
- Optional: `--export-dir` kopiert CSV/PDF-Exporte in `backup_dir/exports/`
- Protokolliert `BACKUP_CREATED` im `audit_log` (Event-Katalog `domain/audit_events.py`); die
  separate `system_events`-Tabelle sieht für Backup-Vorgänge die Werte `DB_BACKUP_CREATED`/
  `DB_BACKUP_FAILED` vor, deren produktive Verwendung im Backup-Service nicht nachgewiesen ist

### 5.2 NAS-Spiegelung

NAS-Sync wird ausschließlich über die `system_config`-Schlüssel `backup.nas_enabled`
(boolescher Wert) und `backup.nas_path` (Zielpfad) gesteuert, nicht über ein CLI-Flag:

```bash
python scripts/backup.py \
  --db arbeitszeit.db \
  --backup-dir backups/
```

Sind beide Schlüssel entsprechend gesetzt, synchronisiert der obige Aufruf automatisch
zum NAS. Ein `--nas-path`-Flag existiert in `scripts/backup.py` nicht.

Nutzt `rsync --archive --delete`: striktes Spiegeln ohne eigenständige Archivfunktion.

**Betriebsregel (RW v5 §17/§18):** Der NAS-Pfad ist ausschließlich als
Hot-Backup-Spiegel vorgesehen. Für Langzeitarchivierung ist ein zweiter NAS-Pfad
ohne `--delete` oder lokale Rotation vor der Spiegelung erforderlich.  
**Beleg:** `phase4_planung.md Z.363–371`

### 5.3 Restore

```python
from arbeitszeit.infrastructure.backup.backup_service import SQLiteBackupService
svc = SQLiteBackupService(db_path, backup_dir)
svc.restore_from(backup_path, restore_exports=False)
```

- Überschreibt die aktive Datenbank mit dem Backup
- `restore_exports=True`: stellt auch den Exports-Unterordner wieder her
- Protokolliert `RESTORE_COMPLETED` im `audit_log` der wiederhergestellten Datenbank
  (nicht in `system_events`, wo stattdessen `RESTORE_STARTED`/`RESTORE_FINISHED`/
  `RESTORE_FAILED` vorgesehen sind, deren produktive Verwendung im Backup-Service
  nicht nachgewiesen ist)

**Betriebsregel:** `RESTORE_COMPLETED` erscheint ausschließlich in der
wiederhergestellten Datenbank, nicht im Backup selbst.  
**Beleg:** `phase4_planung.md Z.373–376`

**Organisatorische Auflage (RW v5 §20):** Restore-Durchführung erfordert Freigabe
durch eine berechtigte Person. Wer das im konkreten Betrieb ist, ist **nicht im Repo
festgelegt** — diese Zuordnung ist organisatorisch zu klären.

---

## 6. Export-Betrieb

**Beleg:** `infrastructure/export/report_queries.py`, `phase4_planung.md Schritt 8`,
`RW v5 §17/§18/§20`

Exportverzeichnis (`export.export_dir`) ist in Zugriffsschutz- und
Archivierungskonzept einzubeziehen; Exportdateien sind in Backups eingeschlossen
(s. Abschnitt 5.1).

Gesetzliche Mindestaufbewahrungsfrist: **2 Jahre** gemäß Regelwerk v5 §18 (in Anlehnung
an § 16 Abs. 2 ArbZG für Mehrarbeit). Eine darüber hinausgehende Aufbewahrung von bis
zu 5 Jahren ist gemäß `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md`
eine organisatorische Praxisfestlegung ohne technische Durchsetzung im Code.  
**Beleg:** `regelwerk_arbeitszeit_v5.md` §18, `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md`

Zugriffsrechte auf Exportverzeichnis-Ebene sind auf Betriebssystem-Ebene zu setzen;
dies ist **nicht Teil des Codes**.

---

## 7. Systemcheck im Betrieb

**Beleg:** `infrastructure/system_check.py`, `phase4_planung.md Schritt 9`

Empfohlene Prüfhäufigkeit: täglich oder bei Systemstart.

```bash
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id <ID> system check
```

`infrastructure/system_check.py` besitzt keinen eigenständigen `__main__`-Einstiegspunkt;
der Aufruf erfolgt ausschließlich über die Admin-CLI.

Prüfbereiche:

| Prüfung | Implementiert | Verhalten bei Fehler |
| --- | --- | --- |
| DB-Zugriff (WAL, row_factory) | ✓ | Check-Ergebnis FAIL |
| Pflicht-Config-Keys | ✓ | Check-Ergebnis FAIL |
| NAS-Erreichbarkeit | ✓ | Check-Ergebnis FAIL (deaktiviertes NAS-Backup selbst liefert OK) |
| Fremdschlüssel-Konsistenz | ✓ | Check-Ergebnis FAIL |
| NTP-Synchronisation | ✓ | Check-Ergebnis FAIL |
| Gerätepfade (evdev) | ✓ | übersprungen wenn kein Pfad angegeben |

`CheckResult` kennt nur ein binäres `ok`-Feld; einen separaten „WARNING“-Status je
Einzelprüfung gibt es im Code nicht. Ergebnisse werden in `system_events` mit
`event_type` `SELFTEST_OK` (Gesamtergebnis erfolgreich) bzw. `SELFTEST_FAIL`
(mindestens ein Check fehlgeschlagen) protokolliert — nicht als `SYSTEM_CHECK_*`.

### 7.1 Sichtbare Warnungen beim Systemstart

Wenn der Systemcheck beim Start der Terminal-UI fehlschlägt, erscheint eine
prominente Meldung am Terminal-Bildschirm:

```text
==================================================
SYSTEMWARNUNG — Betrieb eingeschränkt:
  FEHLER: <Prüfname>: <Fehlerbeschreibung>
==================================================
```

Der Buchungsbetrieb läuft weiter — eine Warnung blockiert die Praxis nicht.
Zusätzlich wird eine Desktop-Benachrichtigung (`notify-send`) ausgelöst,
sofern `libnotify-bin` installiert ist (Lubuntu/Linux Mint: standardmäßig vorhanden).

### 7.2 systemd-Journal (wenn als systemd-Unit betrieben)

Wenn `arbeitszeit-terminal` als systemd-Unit läuft, landen Fehlermeldungen
automatisch im systemd-Journal. Für die Betreiberin / den Admin:

```bash
# Warnungen und Fehler von heute
journalctl -u arbeitszeit-terminal -p warning --since today

# Live-Mitschnitt
journalctl -u arbeitszeit-terminal -f
```

---

## 8. Rollenkonzept

**Beleg:** PH v5 §5/§15, RW v5 §16/§22, `domain/enums.py`

| Rolle | Benutzergruppe | Typische Berechtigung |
| --- | --- | --- |
| ADMIN | Praxisleitung / IT-Betreuer | Alle schreibenden CLI-Operationen |
| REVIEWER | Prüfer / Praxisleitung | Nachtrag genehmigen/ablehnen |
| TECH | Technische Betreuung | Konfigurationsänderungen |

Rollenzuordnung pro Person: Betriebliche Festlegung erforderlich.  
**Nicht im Repo festgelegt:** Welche Person konkret Admin, Reviewer oder Tech ist.  
**Beleg:** PH v5 §15, RW v5 §22 (Anforderung, kein Nachweis der Umsetzung)

---

## 9. Hardware-Verkettung (device_events)

**Beleg:** `infrastructure/db/repositories/device_event.py`, `presentation/terminal_ui/booking_loop.py`,
`Commit 0f20931`

Jeder RFID-Scan am Terminal erzeugt vor der Buchung einen `device_events`-Record
(Autocommit-Modus). Die daraus resultierende ID wird über `BookCommand.device_event_id`
mit der Zeitbuchung verknüpft.

**Zweck:** Audit-Trail. Auch abgewiesene Karten (UnknownCard) hinterlassen einen
`device_events`-Record. Schlägt der INSERT fehl, wird keine Buchung versucht.

Aktuell nur mit `SimulatedHardwareReader` getestet; kein Nachweis realer Gerätenutzung
im Repo.

---

## 10. Migrationsstand

**Beleg:** `migrations/`, `phase1_planung.md`, `planung_gesamt.md Z.114–117`

| Migration | Inhalt | Phase |
| --- | --- | --- |
| 0001 | Initialschema (16 Tabellen, 17 Indizes) | 1 |
| 0002 | Seed-Daten (Regelarbeitszeiten, system_config-Defaults) | 1 |
| 0003 | Cleanup booking_status (NOT NULL + CHECK-Constraint) | 4 |
| 0004 | Supplement-Felder: reject_fields + review_note | 4 |
| 0005 | time_bookings.device_event_id (Schemavorbereitung, NULL) | 4 |
| 0006 | system_events.APPLICATION_ERROR (technische Strukturergänzung) | 5 |

Migration wird automatisch durch `scripts/init_db.py` angewandt.
Idempotenz: Glob-Runner führt jede SQL-Datei nur einmalig aus.

---

## 11. Freigabefähigkeitsstatus

| Thema | Status | Beleg | Offen |
| --- | --- | --- | --- |
| Buchungslogik COME/GO/BREAK | technisch vollständig | 406 Tests grün, Stand Commit `0f20931` (aktueller Repository-Stand: 480 Tests gesamt) | — |
| ArbZG-Prüfhilfen §3/§4/§5 | technisch vollständig | compliance_checks.py + Tests | Ersetzt keine Einzelfallprüfung |
| Backup + Restore | technisch vollständig | backup_service.py + e2e-Tests | Restore-Freigabe organisatorisch klären |
| Systemcheck | technisch vollständig | system_check.py + 17 Tests | Reale Gerätepfade im Betrieb eintragen |
| Benutzerkontenverwaltung | technisch vollständig | user_accounts.py + 18 Tests | Rollenzuordnung organisatorisch klären |
| NAS-Spiegelung | technisch vorbereitet | backup_service.py sync_to_nas() | Echter NAS-Pfad als Betriebsentscheidung |
| device_events-Kette | technisch vollständig | Commit `0f20931` + 3 Tests | Nur mit Simulator getestet |
| Exportzugangsschutz | technisch vorbereitet | setup.py setzt export.export_dir | OS-seitige Zugriffsrechte zu setzen |
| Betriebsfreigabe als System | **nicht im Repo** | — | Formale Freigabe durch berechtigte Stelle |
| Smoke-Tests Zielhardware | **nicht nachgewiesen** | phase4_planung.md Hinweis | Protokoll fehlt |
| Organisat. Rollenzuweisung | **nicht im Repo** | — | Wer ist konkret Admin/Reviewer/Tech? |
| AV-Vertrag Cloud-Backup | **nicht im Repo** | planung_gesamt.md Z.258 | Falls Cloud-Backup genutzt wird |
| IT-Sicherheitskonzept §75b SGB V | **nicht im Repo** | planung_gesamt.md Z.258 | Einbindung in Praxis-IT-Konzept |

---

## 12. Abgrenzung

Dieses Dokument beschreibt **technisch implementierte Abläufe** auf Basis von
Repo-Artefakten. Es stellt keine:

- Formale Betriebsfreigabe dar
- Datenschutz-Folgenabschätzung
- Organisationsanweisung
- Abnahme-Protokoll

dar. Diese Dokumente sind außerhalb dieses Repositories zu erstellen und zu verabschieden.