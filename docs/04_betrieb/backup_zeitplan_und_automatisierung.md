# Backup-Zeitplan und Automatisierung – System „arbeitszeit“

**System:** arbeitszeit  
**Dokumenttyp:** Betriebsdokument – Backup-Zeitplan und Automatisierung  
**Version:** 1.0  
**Stand:** 2026-06-12  
**Ablageort:** `docs/betrieb/backup_zeitplan_und_automatisierung.md`

> Dieses Dokument beschreibt, **wann** und **wie** Backups für `arbeitszeit`
> automatisch ausgeführt werden sollen. Es richtet sich ausdrücklich auch an
> Betreiber ohne tiefe Linux-/Admin-Kenntnisse und ergänzt die technische
> Beschreibung in `scripts/backup.py` und der Betriebsdokumentation.
> Die Pflicht zur Aufbewahrung von Arbeitszeitnachweisen ergibt sich u. a. aus
> § 16 Abs. 2 ArbZG (mindestens zwei Jahre).[web:133][web:136][web:139]

---

## 1. Ziel des Backup-Konzepts

Ziel ist es, die Arbeitszeitdaten so zu sichern, dass:

- die gesetzlichen Aufbewahrungspflichten erfüllt werden,[web:133][web:136][web:139]
- ein Verlust der lokalen Daten (Hardwaredefekt, Bedienfehler) nicht zum Verlust
  der Arbeitszeitnachweise führt,
- die Wiederherstellung aus einem Backup mit vertretbarem Aufwand möglich ist.[web:131][web:137][web:140]

---

## 2. Backup-Arten im System „arbeitszeit“

`scripts/backup.py` unterstützt zwei grundlegende Backup-Arten:

1. **Lokales Backup**  
   - Kopie der SQLite-Datenbank (und optional der Exportverzeichnisse) in ein
     lokales Backup-Verzeichnis.
2. **NAS-Spiegelung (optional)**  
   - Spiegelung des Backup-Verzeichnisses auf ein Netzlaufwerk (NAS) per `rsync`.

Die Kombination aus lokalem Backup plus NAS-Spiegelung ist empfohlen, wenn ein
NAS zuverlässig zur Verfügung steht.

---

## 3. Empfohlener Zeitplan

### 3.1 Tägliches Backup (Minimum)

Für eine kleine Praxis ist ein **tägliches Backup** außerhalb der Praxiszeiten
empfohlen, z. B.:

- Zeitfenster: zwischen 20:00 und 06:00 Uhr,
- Frequenz: mindestens einmal täglich an jedem Arbeitstag.

**Empfehlung:**  
Tägliches Backup **Mo–Fr** gegen 20:30 Uhr.

### 3.2 Wöchentliches Voll-Check-Backup (optional)

Zusätzlich kann einmal pro Woche (z.B. Freitagabend) ein Backup mit ausdrücklicher
Dokumentation und ggf. manuellem Restore-Test eingeplant werden.

---

## 4. Beispiel: Automatisierung mit `cron` (Linux Mint/Lubuntu)

> Hinweis: Die folgenden Beispiele sind als **Muster** gedacht. Anpassungen an
> Pfade und Benutzernamen sind jeweils erforderlich.[web:131][web:134][web:137][web:140]

### 4.1 Vorbereitung

1. Sicherstellen, dass `scripts/backup.py` lauffähig ist:

   ```bash
   cd /pfad/zu/arbeitszeit
   source .venv/bin/activate
   python scripts/backup.py --help
   ```

2. Pfade festlegen:

   - Datenbank: `/pfad/zu/arbeitszeit.db`
   - Backup-Verzeichnis: `/var/backups/arbeitszeit/`
   - (optional) NAS-Pfad: `/mnt/nas/arbeitszeit-backup/`

3. Backup-Verzeichnis anlegen (einmalig):

   ```bash
   sudo mkdir -p /var/backups/arbeitszeit
   sudo chown <benutzer>:<gruppe> /var/backups/arbeitszeit
   ```

### 4.2 Einfache Cronjob-Variante (tägliches Backup)

Ausführung als Benutzer, unter dem auch das System betrieben wird:

```bash
crontab -e
```

Dann z. B. hinzufügen:

```bash
# Tägliches arbeitszeit-Backup um 20:30 Uhr
30 20 * * 1-5 cd /pfad/zu/arbeitszeit && \
  . .venv/bin/activate && \
  python scripts/backup.py \
    --db /pfad/zu/arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
  >> /var/backups/arbeitszeit/backup.log 2>&1
```

Erläuterung:

- `30 20 * * 1-5`: Mo–Fr um 20:30 Uhr.[web:131][web:137]
- Ausgabe wird in `backup.log` protokolliert, um Erfolge/Fehler nachprüfen zu können.[web:137][web:140]

### 4.3 Cronjob mit NAS-Spiegelung (optional)

`scripts/backup.py` kennt kein eigenes CLI-Flag für den NAS-Pfad. Die NAS-Spiegelung
wird stattdessen automatisch ausgeführt, wenn in der `system_config`-Tabelle die
Schlüssel `backup.nas_enabled` (aktiviert) und `backup.nas_path` (Zielpfad, z. B.
`/mnt/nas/arbeitszeit-backup`) gesetzt sind; das Skript liest beide Werte selbst aus
der Datenbank aus. Der Cronjob-Aufruf unterscheidet sich in diesem Fall nicht vom
Aufruf ohne NAS-Sync:

```bash
# Tägliches arbeitszeit-Backup um 21:00 Uhr (NAS-Sync erfolgt automatisch,
# sofern backup.nas_enabled/backup.nas_path in system_config gesetzt sind)
0 21 * * 1-5 cd /pfad/zu/arbeitszeit && \
  . .venv/bin/activate && \
  python scripts/backup.py \
    --db /pfad/zu/arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
  >> /var/backups/arbeitszeit/backup_nas.log 2>&1
```

Voraussetzung: NAS-Einbindung wurde vorher eingerichtet, getestet und über
`system_config` (`backup.nas_enabled`, `backup.nas_path`) konfiguriert.

---

## 5. Beispiel: Automatisierung mit `systemd`-Timer (Alternative)

Bei Lubuntu mit `systemd` kann statt `cron` ein Timer verwendet werden.
Dies erfordert Admin-Rechte und ist eher für technisch versiertere Personen gedacht.[web:132][web:135][web:138]

### 5.1 Service-Unit (z.B. `/etc/systemd/system/arbeitszeit-backup.service`)

```ini
[Unit]
Description=Tägliches Backup für arbeitszeit

[Service]
Type=oneshot
WorkingDirectory=/pfad/zu/arbeitszeit
User=<benutzer>
Group=<gruppe>
Environment="VIRTUAL_ENV=/pfad/zu/arbeitszeit/.venv"
Environment="PATH=/pfad/zu/arbeitszeit/.venv/bin:/usr/bin"
ExecStart=/usr/bin/env python scripts/backup.py \
  --db /pfad/zu/arbeitszeit.db \
  --backup-dir /var/backups/arbeitszeit
StandardOutput=append:/var/backups/arbeitszeit/backup_systemd.log
StandardError=append:/var/backups/arbeitszeit/backup_systemd.log
```

### 5.2 Timer-Unit (z.B. `/etc/systemd/system/arbeitszeit-backup.timer`)

```ini
[Unit]
Description=Täglicher Backup-Timer für arbeitszeit

[Timer]
OnCalendar=Mon..Fri 20:30
Persistent=true

[Install]
WantedBy=timers.target
```

Aktivierung:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now arbeitszeit-backup.timer
sudo systemctl status arbeitszeit-backup.timer
```

---

## 6. Verantwortlichkeiten und Kontrolle

| Aufgabe | Verantwortlich | Frequenz |
|---|---|---|
| Kontrolle der Cron-/Timer-Konfiguration | TECH / Admin | bei Einrichtung + jährlich |
| Stichprobenprüfung der Backup-Logs | TECH / Admin | monatlich |
| Durchführung eines Test-Restores (auf Testsystem) | TECH in Abstimmung mit Praxisleitung | mindestens jährlich |
| Aktualisierung dieses Dokuments | Praxisleitung / TECH | bei Änderungen am Backup-Konzept |

---

## 7. Aufbewahrung und Löschkonzept für Backups

- Backups enthalten Arbeitszeitdaten, die mindestens **zwei Jahre** aufzubewahren sind.[web:133][web:136][web:139]
- Gleichzeitig muss die Speichernutzung beherrschbar bleiben:
  - Empfehlung: mind. 30 tägliche Backups aufbewahren.
  - Zusätzlich wöchentliche und monatliche Stände möglich (Rotation).
- Konkrete Strategie (Beispiel):

  - Letzte 30 Tage: tägliche Backups,
  - Zusätzlich: 6 Monats-Backups (jeweils erster Arbeitstag im Monat),
  - Ältere Backups nach dokumentiertem Löschplan entfernen.

Löschvorgänge von Backups sind – soweit möglich – zu dokumentieren (Datum, Umfang, verantwortliche Person).

---

## 8. Dokumentation der eingerichteten Backup-Automatisierung

| Feld | Eintrag |
|---|---|
| Eingesetzte Methode | ☐ cron ☐ systemd-timer ☐ manuell ☐ Sonstiges: __________ |
| Verantwortliche Person für Einrichtung | __________________________________________ |
| Datum der Einrichtung / letzten Anpassung | __________________________________________ |
| Pfad zur Crontab / Timer-Units | __________________________________________ |
| Protokolldatei(en) | __________________________________________ |

---

## 9. Änderungen und Historie

| Version | Datum | Änderung | Verantwortlich |
|---|---|---|---|
| 1.0 | 2026-06-12 | Erstfassung Backup-Zeitplan und Automatisierung | __________________ |