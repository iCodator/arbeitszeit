# Betriebsdokumentation – arbeitszeit

**Version:** 1.0  
**Datum:** 2026-06-11  
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

```
python scripts/init_db.py --db arbeitszeit.db
```

- Führt alle Migrationsdateien unter `migrations/` in numerischer Reihenfolge aus
- Idempotent: bereits angewandte Migrationen werden nicht erneut ausgeführt
- `setup_vollstaendig()` prüft anschließend, ob `backup.backup_dir` und
  `export.export_dir` in `system_config` gesetzt sind

### 2.2 Systemkonfiguration interaktiv

```
python scripts/setup.py --db arbeitszeit.db
```

Setzt interaktiv folgende Pflicht-Keys in `system_config`:
- `backup.backup_dir` — Zielverzeichnis für lokale Backups
- `export.export_dir` — Exportverzeichnis für CSV/PDF-Auswertungen

Optionale Keys (NAS, Terminal-ID, Zeitmonitor-Schwellenwert) werden ebenfalls
abgefragt, können aber leer gelassen werden.

### 2.3 Bootstrap: Ersten Admin-Account anlegen

```
python -m arbeitszeit.presentation.admin_cli.main \
  --db arbeitszeit.db \
  users bootstrap \
  --username NAME --password PASSWORT --full-name "Vollständiger Name"
```

Dieser Pfad erfordert kein `--user-id`, da noch kein Admin existiert. Die Funktion
prüft vor Ausführung, ob bereits ein aktiver Admin existiert; falls ja, wird der
Aufruf abgelehnt.  
**Beleg:** `presentation/admin_cli/user_accounts.py cmd_users_bootstrap()`

### 2.4 Systemcheck nach Einrichtung

```
python -m arbeitszeit.infrastructure.system_check \
  --db arbeitszeit.db
```

Prüft: DB-Zugriff, Pflicht-Konfigurationskeys, optionale Gerätepfade, NAS-Erreichbarkeit,
Fremdschlüssel-Konsistenz.  
**Beleg:** `infrastructure/system_check.py`, `phase4_planung.md Schritt 9`

---

## 3. Laufendes Betrieb — Terminal-UI

**Beleg:** `presentation/terminal_ui/main.py`, `phase5_planung.md`

```
python -m arbeitszeit.presentation.terminal_ui.main \
  --db arbeitszeit.db \
  --terminal-id 1
```

### 3.1 Ablauf pro Zyklus

1. RFID-Karte lesen (Hardware oder Simulator)
2. `device_events`-Record schreiben (Autocommit, vor Transaktion)
3. `BookUseCase` ausführen (COME/GO/BREAK-Logik, Ruhezeit- und Rollenprüfung)
4. Ergebnis ausgeben; Fehler → APPLICATION_ERROR in `system_events` protokollieren

### 3.2 Zeitmonitor

Läuft parallel im Terminal-UI. Prüft Systemzeitsprünge alle 30 Sekunden.  
Schwellenwert: `time_monitor.jump_threshold_seconds` aus `system_config`
(Standard: 60 Sekunden).

Erkannte Ereignisse werden als `TIME_JUMP_DETECTED` oder
`MANUAL_TIME_CHANGE_DETECTED` in `system_events` geschrieben.  
**Beleg:** `infrastructure/time_monitor.py`, `phase5_planung.md Schritt 5`

### 3.3 Gerätesimulator

Für Tests ohne Echthardware:

```
python -m arbeitszeit.presentation.terminal_ui.main \
  --db arbeitszeit.db --terminal-id 1 --simulator
```

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
| `bookings list` | Buchungen (gefiltert nach Mitarbeiter/Zeitraum) |
| `bookings correct` | Buchungskorrektur (CorrectBookingUseCase) |
| `bookings supplement register` | Nachtragsantrag einreichen |
| `bookings supplement approve` | Nachtragsantrag genehmigen (REVIEWER oder ADMIN) |
| `bookings supplement reject` | Nachtragsantrag ablehnen (REVIEWER oder ADMIN) |

### 4.4 Exporte

| Befehl | Funktion |
| --- | --- |
| `export csv` | CSV-Auswertung (filterbar nach Mitarbeiter/Zeitraum) |
| `export pdf` | PDF-Report (filterbar nach Mitarbeiter/Zeitraum) |

**Beleg:** `infrastructure/export/report_queries.py`, `phase4_planung.md Schritt 8`

---

## 5. Backup-Betrieb

**Beleg:** `scripts/backup.py`, `infrastructure/backup/backup_service.py`,
`phase4_planung.md Schritt 7`

### 5.1 Lokales Backup erstellen

```
python scripts/backup.py \
  --db arbeitszeit.db \
  --backup-dir backups/ \
  [--export-dir exports/]
```

- Erzeugt timestamped SQLite-Copy im `--backup-dir`
- Optional: `--export-dir` kopiert CSV/PDF-Exporte in `backup-dir/exports/`
- Protokolliert `BACKUP_CREATED` in `system_events`

### 5.2 NAS-Spiegelung

```
python scripts/backup.py \
  --db arbeitszeit.db \
  --backup-dir backups/ \
  --nas-path /mnt/nas/arbeitszeit-backup/
```

Nutzt `rsync --archive --delete`: striktes Spiegeln ohne eigenständige Archivfunktion.

**Betriebsregel (RW v5 §17/§18):** Der NAS-Pfad ist ausschließlich als
Hot-Backup-Spiegel vorgesehen. Für Langzeitarchivierung ist ein zweiter NAS-Pfad
ohne `--delete` oder lokale Rotation vor der Spiegelung erforderlich.  
**Beleg:** `phase4_planung.md Z.363–371`

Erfolg: `BACKUP_SYNCED_TO_NAS`; Fehler: `BACKUP_SYNC_FAILED` in `system_events`.

### 5.3 Restore

```python
from arbeitszeit.infrastructure.backup.backup_service import BackupService
svc = BackupService(db_path, backup_dir)
svc.restore_from(backup_path, restore_exports=False)
```

- Überschreibt die aktive Datenbank mit dem Backup
- `restore_exports=True`: stellt auch den Exports-Unterordner wieder her
- Protokolliert `RESTORE_COMPLETED` in der **wiederhergestellten** Datenbank

**Betriebsregel:** `RESTORE_COMPLETED` erscheint ausschließlich in der
wiederhergestellten Datenbank, nicht im Backup selbst.  
**Beleg:** `phase4_planung.md Z.373–376`

**Organisatorische Auflage (RW v5 §18):** Restore-Durchführung erfordert Freigabe
durch eine berechtigte Person. Wer das im konkreten Betrieb ist, ist **nicht im Repo
festgelegt** — diese Zuordnung ist organisatorisch zu klären.

---

## 6. Export-Betrieb

**Beleg:** `infrastructure/export/report_queries.py`, `phase4_planung.md Schritt 8`,
`RW v5 §17/§18/§20`

Exportverzeichnis (`export.export_dir`) ist in Zugriffsschutz- und
Archivierungskonzept einzubeziehen; Exportdateien sind in Backups eingeschlossen
(s. Abschnitt 5.1).

Aufbewahrungsfrist: **5 Jahre** gemäß ArbZG / RW v5 §20.  
**Beleg:** `planung_gesamt.md` (V5-/V2-Abgleich, Aufbewahrungsfristen)

Zugriffsrechte auf Exportverzeichnis-Ebene sind auf Betriebssystem-Ebene zu setzen;
dies ist **nicht Teil des Codes**.

---

## 7. Systemcheck im Betrieb

**Beleg:** `infrastructure/system_check.py`, `phase4_planung.md Schritt 9`

Empfohlene Prüfhäufigkeit: täglich oder bei Systemstart.

```
python -m arbeitszeit.infrastructure.system_check --db arbeitszeit.db
```

Prüfbereiche:

| Prüfung | Implementiert | Verhalten bei Fehler |
| --- | --- | --- |
| DB-Zugriff (WAL, row_factory) | ✓ | Check-Ergebnis FAIL |
| Pflicht-Config-Keys | ✓ | Check-Ergebnis FAIL |
| NAS-Erreichbarkeit | ✓ | Check-Ergebnis WARNING (optional) |
| Fremdschlüssel-Konsistenz | ✓ | Check-Ergebnis FAIL |
| Gerätepfade (evdev) | ✓ | übersprungen wenn kein Pfad angegeben |

Ergebnisse werden in `system_events` (event_type: SYSTEM_CHECK_*) protokolliert.

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
| Buchungslogik COME/GO/BREAK | technisch vollständig | 406 Tests grün | — |
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
