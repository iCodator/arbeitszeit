---
lang: de-DE
mainfont: "Clear Sans"
monofont: "DejaVu Sans Mono"
fontsize: 10pt
geometry:
  - margin=2cm
  - bindingoffset=1cm
header-includes:
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyhead{}
  - \fancyfoot[R]{\fontsize{8}{9.5}\selectfont Seite \thepage/\pageref{LastPage}}
  - \renewcommand{\headrulewidth}{0pt}
  - \renewcommand{\footrulewidth}{0.2pt}
  - \usepackage{lastpage}
  - \fancypagestyle{plain}{\fancyhf{}\fancyhead{}\fancyfoot[R]{\fontsize{8}{9.5}\selectfont Seite \thepage/\pageref{LastPage}}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0.2pt}}
---

# Handbuch: Zeiterfassungssystem arbeitszeit

**Version:** 1.9
**Stand:** Juli 2026
**Projekt:** Lokales Zeiterfassungssystem für eine Zahnarztpraxis

## Über dieses Handbuch

Dieses Handbuch richtet sich an **Praxispersonal ohne IT-Kenntnisse** —
zum Beispiel die Praxisleiterin oder eine Verwaltungskraft, die
Mitarbeitende anlegen, Berichte erzeugen und das System im Alltag
betreuen soll.

Technische Hintergründe (Datenbankschema, Architektur, Quellcode) sind
hier bewusst weggelassen. Diese finden sich im technischen Handbuch
`docs/03_installation_technik/befehlsreferenz.md`.

---

## Inhalt

1. [Was ist `arbeitszeit`?](#kapitel-1-was-ist-arbeitszeit)
2. [Erste Schritte](#kapitel-2-erste-schritte)
3. [Mitarbeitende verwalten](#kapitel-3-mitarbeitende-verwalten)
4. [Buchungsbetrieb am Terminal](#kapitel-4-buchungsbetrieb-am-terminal)
5. [Buchungen korrigieren und Nachträge](#kapitel-5-buchungen-korrigieren-und-nachträge)
6. [Berichte erstellen](#kapitel-6-berichte-erstellen)
7. [Arbeitszeitplan setzen](#kapitel-7-arbeitszeitplan-setzen)
8. [Benutzerverwaltung](#kapitel-8-benutzerverwaltung)
9. [System-Wartung](#kapitel-9-system-wartung)
10. [Buchungsterminal als Systemdienst einrichten und verwalten](#kapitel-10-buchungsterminal-als-systemdienst-einrichten-und-verwalten)
11. [Häufige Fragen und Fehlermeldungen](#kapitel-11-häufige-fragen-und-fehlermeldungen)

---

## Kapitel 1: Was ist `arbeitszeit`?

Das System `arbeitszeit` erfasst die Arbeitszeiten von
Praxismitarbeitenden automatisch:

- Mitarbeitende buchen **Kommen, Gehen und Pausen** mit ihrer
  persönlichen RFID-Karte an einem Buchungsterminal.
- Das System prüft automatisch, ob die gesetzlichen
  Arbeitszeitgrenzen (ArbZG) eingehalten werden.
- Administratoren verwalten Stammdaten, erzeugen Berichte und
  greifen bei Korrekturbedarf ein — alles über die Kommandozeile.
- Alle Daten werden lokal auf dem Praxis-PC gespeichert.

Das System besteht aus zwei Teilen:

| Teil | Beschreibung |
| --- | --- |
| **Buchungsterminal** | Läuft dauerhaft im Hintergrund; nimmt Buchungen per Numpad und RFID-Karte entgegen |
| **Admin-Programm** | Wird von der Administratorin bei Bedarf aufgerufen; dient der Verwaltung und Auswertung |

---

## Kapitel 2: Erste Schritte

### 2.1 Das Admin-Programm aufrufen

Das Admin-Programm hat keinen eigenen Befehlsnamen. Es wird immer
vollständig aufgerufen:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db /pfad/zur/datenbank.db \
  --user-id 1 \
  <bereich> <aktion>
```

**Empfehlung:** Einmal einen Kurznamen einrichten und ihn dauerhaft
verfügbar machen:

```bash
alias azadmin="python -m arbeitszeit.presentation.admin_cli.main"
echo 'alias azadmin="python -m arbeitszeit.presentation.admin_cli.main"' >> ~/.bashrc
```

Danach reicht der Kurzaufruf:

```bash
azadmin --db /pfad/zur/datenbank.db --user-id 1 <bereich> <aktion>
```

Alle Beispiele in diesem Handbuch verwenden den Kurzaufruf `azadmin`.

**Was ist `--user-id 1`?**
Das ist die ID des angemeldeten Administrators. Das System prüft damit,
ob die ausführende Person die nötige Berechtigung hat.

**Wo ist die Datenbank?**
Der Pfad steht in der Konfigurationsdatei `config.toml` unter
`[database] path`. Alternativ kann `--db` bei jedem Aufruf angegeben
werden.

### 2.2 Konfigurationsdatei

Das System sucht die Datei `config.toml` in dieser Reihenfolge:

1. `--config <PFAD>` (direkt angegeben)
2. Umgebungsvariable `ARBEITSZEIT_CONFIG`
3. `~/.config/arbeitszeit/config.toml`
4. `./config.toml` (im aktuellen Verzeichnis)

Minimale Konfiguration:

```toml
[database]
path = "/home/praxis/daten/arbeitszeit.db"

[terminal]
id = 1
numpad = "Usb KeyBoard Usb KeyBoard"
rfid = "Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader"

[backup]
backup_dir = "/var/backups/arbeitszeit"
export_dir  = "/var/exports/arbeitszeit"
log_dir     = "/var/log/arbeitszeit"
```

Die genauen Gerätenamen für `numpad` und `rfid` liefert
`scripts/verify_hardware.py --list`.

### 2.3 Ersten Administrator anlegen

Beim allerersten Start — **bevor** ein Administratorkonto existiert —
muss `users bootstrap` ohne `--user-id` aufgerufen werden:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db /pfad/zur/datenbank.db \
  users bootstrap --username admin
```

Das System zeigt das Passwort **einmalig** an. Unbedingt notieren
oder sofort ändern!

### 2.4 Funktionstest

```bash
pytest
pytest tests/test_migrations.py
```

---

## Kapitel 3: Mitarbeitende verwalten

### 3.1 Alle Mitarbeitenden anzeigen

```bash
azadmin --db db.db --user-id 1 employees list
```

Die Ausgabe zeigt IDs, Personalnummern, Namen und ob das Konto aktiv ist.

### 3.2 Mitarbeiter anlegen

```bash
azadmin --db db.db --user-id 1 employees add \
  --personnel-no M001 \
  --first-name Maria \
  --last-name Muster
```

**Pflichtangaben:** `--personnel-no`, `--first-name`, `--last-name`

**Rolle:** ADMIN

### 3.3 Mitarbeiter deaktivieren

```bash
azadmin --db db.db --user-id 1 employees deactivate 5
```

`5` ist die ID des Mitarbeiters (aus `employees list` ablesen).

Deaktivierte Mitarbeitende können sich nicht mehr am Terminal einbuchen.
Ihre bisherigen Daten bleiben erhalten.

**Rolle:** ADMIN

### 3.4 RFID-Karte zuweisen

Jeder Mitarbeiter braucht eine eigene RFID-Karte, um sich am Terminal
zu identifizieren.

**Variante A — mit Scanner (empfohlen):**

```bash
azadmin --db db.db --user-id 1 cards assign \
  --employee-id 3 \
  --scan \
  --rfid "Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader"
```

Das System wartet dann auf den Kartenleser — Karte vorhalten.

**Variante B — mit vorberechnetem Hash:**

```bash
azadmin --db db.db --user-id 1 cards assign \
  --employee-id 3 \
  --uid-hash abc123...
```

Den Hash einer Karte ermittelt `python scripts/verify_hardware.py`
(Karte vorhalten, Hash aus der Ausgabe kopieren).

**Rolle:** ADMIN

### 3.5 Karte ersetzen

Wenn eine Karte verloren oder defekt ist:

```bash
azadmin --db db.db --user-id 1 cards replace \
  --old-card-id 2 \
  --uid-hash <HASH-DER-NEUEN-KARTE>
```

Den Hash der neuen Karte vorher mit `scripts/verify_hardware.py`
ermitteln. Die alte Karte wird automatisch gesperrt.

**Rolle:** ADMIN

### 3.6 Karte deaktivieren

```bash
azadmin --db db.db --user-id 1 cards deactivate 2
```

`2` ist die Karten-ID (aus der Ausgabe von `cards assign` oder
`employees list` ablesen).

**Rolle:** ADMIN

---

## Kapitel 4: Buchungsbetrieb am Terminal

### 4.1 Terminal starten

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db /pfad/zur/datenbank.db \
  --numpad "Usb KeyBoard Usb KeyBoard" \
  --rfid "Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader" \
  --terminal-id 1
```

Wenn `config.toml` vollständig ausgefüllt ist, reicht:

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db /pfad/zur/datenbank.db
```

Das Terminal läuft dann dauerhaft im Hintergrund. Wie es beim
Systemstart automatisch gestartet wird, erklärt Kapitel 10.

### 4.2 Buchung durchführen

Am Beginn jedes Buchungszyklus wird der Bildschirm geleert und das
Buchungsarten-Menü angezeigt. Jede Buchung läuft dann in zwei Schritten ab:

**Schritt 1 — Buchungsart auf dem Numpad wählen:**

| Taste | Buchungsart |
| --- | --- |
| **1** | Kommen (Schichtbeginn) |
| **2** | Gehen (Schichtende) |
| **3** | Pause beginnen |
| **4** | Pause beenden |

Schritt 2: RFID-Karte vorhalten.

Das System hat nach der Numpad-Eingabe 30 Sekunden Zeit für den
Kartenscan (konfigurierbar über `booking.grace_seconds_after_numpad_select`
in der Datenbank).

Nach der Rückmeldung wartet das System 2 Sekunden, dann beginnt der
nächste Zyklus.

### 4.3 Rückmeldungen des Terminals

Nach jeder Buchung erscheint eine Meldung:

| Meldung | Bedeutung |
| --- | --- |
| `Buchung erfasst.` | Alles in Ordnung |
| `Buchung erfasst — Hinweis: Regelzeitabweichung festgestellt.` | Buchung wurde gespeichert, aber die Arbeitszeit weicht vom Arbeitszeitplan ab |
| `Buchung erfasst — Prüfpflicht: Manuelle Überprüfung erforderlich.` | Ein gesetzlicher Arbeitszeitgrenzwert wurde erreicht — REVIEWER muss prüfen |
| `Karte nicht erkannt.` | Diese Karte ist nicht im System registriert |
| `Karte deaktiviert.` | Die Karte wurde gesperrt oder ersetzt |
| `Mitarbeiter inaktiv.` | Das Mitarbeiterkonto wurde deaktiviert |
| `Ungültige Buchungsreihenfolge.` | Z. B. zweimal „Kommen" ohne „Gehen" dazwischen |
| `Offene Phase — bitte zuerst abschließen.` | Es gibt noch eine offene Schicht oder Pause |

### 4.4 Terminal beenden

Wie das Terminal sauber beendet und als Systemdienst verwaltet wird,
erklärt Kapitel 10.

Alternativ im Vordergrund: `STRG+C`.

---

## Kapitel 5: Buchungen korrigieren und Nachträge

**Hinweis:** Alle Befehle in diesem Kapitel erfordern die Rolle
**ADMIN** oder **REVIEWER**.

### 5.1 Buchung korrigieren

Wenn eine Buchung falsch erfasst wurde (falscher Typ oder falsche Uhrzeit),
kann sie korrigiert werden:

```bash
azadmin --db db.db --user-id 1 bookings correct \
  --booking-id 42 \
  --type COME \
  --at "15.07.2026 08:00" \
  --reason "Kartenleser hat nicht reagiert, manuell nachgepflegt"
```

**Mögliche Buchungstypen für `--type`:**

| Wert | Bedeutung |
| --- | --- |
| `COME` | Kommen |
| `GO` | Gehen |
| `BREAK_START` | Pause beginnen |
| `BREAK_END` | Pause beenden |

**Format für `--at`:** `TT.MM.JJJJ HH:MM` (UTC), z. B. `15.07.2026 08:30`

Die Buchungs-ID (`--booking-id`) steht in der Ausgabe von
`reports open-bookings` oder `reports warn-cases`.

### 5.2 Nachtrag erfassen

Ein Nachtrag ist eine **nachträgliche Buchung**, die nicht am Terminal
erfasst wurde (z. B. weil jemand vergessen hat auszustempeln):

```bash
azadmin --db db.db --user-id 1 bookings supplement \
  --employee-id 3 \
  --type GO \
  --at "15.07.2026 17:30" \
  --reason "Vergessen auszustempeln, per Rücksprache bestätigt"
```

Ein Nachtrag ist zunächst **ausstehend** (Prüfstatus: `PENDING`) und
muss separat genehmigt werden.

### 5.3 Nachtrag genehmigen

```bash
azadmin --db db.db --user-id 1 bookings approve-supplement \
  --supplement-id 7
```

Erst nach der Genehmigung wird der Nachtrag als echte Buchung
gespeichert und in Berichten ausgewertet.

### 5.4 Nachtrag ablehnen

```bash
azadmin --db db.db --user-id 1 bookings reject-supplement \
  --supplement-id 7 \
  --reason "Zeitangabe nicht plausibel — laut Dienstplan war die Person nicht anwesend"
```

### 5.5 Nachträge und Korrekturen finden

Alle ausstehenden Nachträge anzeigen:

```bash
azadmin --db db.db --user-id 1 reports supplements \
  --from 01.07.2026 --to 31.07.2026
```

Alle Korrekturen eines Zeitraums anzeigen:

```bash
azadmin --db db.db --user-id 1 reports corrections \
  --from 01.07.2026 --to 31.07.2026
```

---

## Kapitel 6: Berichte erstellen

Alle Berichte erfordern die Rolle **ADMIN** oder **REVIEWER**.
Dateien werden automatisch im Verzeichnis gespeichert, das in
`config.toml` unter `[backup] export_dir` angegeben ist.

### 6.1 CSV-Berichte

**Alle Buchungen eines Zeitraums als CSV:**

```bash
azadmin --db db.db --user-id 1 reports export-csv \
  --from 01.07.2026 --to 31.07.2026
```

Erzeugt zwei Dateien:

- **Detail-CSV** — jede einzelne Buchung mit Zeitstempel und Status
- **Verdichtet-CSV** — eine Zeile pro Mitarbeiter und Tag mit
  Nettoarbeitszeit

**Nur für einen Mitarbeiter:**

```bash
azadmin --db db.db --user-id 1 reports export-csv \
  --from 01.07.2026 --to 31.07.2026 --employee-id 3
```

**Prüffälle (Arbeitszeitverstöße) als CSV:**

```bash
azadmin --db db.db --user-id 1 reports export-csv-review-cases \
  --from 01.07.2026 --to 31.07.2026
```

### 6.2 PDF-Berichte

**Tagesbericht:**

```bash
azadmin --db db.db --user-id 1 reports export-pdf-day \
  --date 15.07.2026
```

**Wochenbericht (ISO-Wochennummer):**

```bash
azadmin --db db.db --user-id 1 reports export-pdf-week \
  --year 2026 --week 29
```

**Monatsbericht:**

```bash
azadmin --db db.db --user-id 1 reports export-pdf-month \
  --year 2026 --month 7
```

**Mitarbeiterbericht:**

```bash
azadmin --db db.db --user-id 1 reports export-pdf-employee \
  --employee-id 3 \
  --from 01.07.2026 \
  --to 31.07.2026
```

### 6.3 Pflichtauswertungen

Diese Auswertungen werden direkt auf dem Bildschirm angezeigt
(keine Datei):

**Offene Buchungen** (Schichten oder Pausen, die noch nicht
abgeschlossen sind):

```bash
# Alle offenen Buchungen
azadmin --db db.db --user-id 1 reports open-bookings

# Eingegrenzt auf einen Zeitraum
azadmin --db db.db --user-id 1 reports open-bookings \
  --from 01.07.2026 --to 31.07.2026
```

**Buchungen mit Hinweis oder Prüfpflicht** (WARN- und
NEEDS\_REVIEW-Status):

```bash
azadmin --db db.db --user-id 1 reports warn-cases \
  --from 01.07.2026 --to 31.07.2026
```

**Offene Prüffälle** (müssen von einem REVIEWER bearbeitet werden):

```bash
azadmin --db db.db --user-id 1 reports open-review-cases
```

---

## Kapitel 7: Arbeitszeitplan setzen

Der Arbeitszeitplan legt fest, wann ein Mitarbeiter laut Plan anfangen
und aufhören soll. Abweichungen davon führen zum Status `WARN`.

### 7.1 Standard-Arbeitszeiten nach Ersteinrichtung

Nach der Installation sind folgende Zeiten voreingestellt:

| Wochentag | Beginn | Ende |
| --- | --- | --- |
| Montag | 07:30 | 18:00 |
| Dienstag | 07:30 | 18:00 |
| Mittwoch | 07:30 | 18:00 |
| Donnerstag | 07:30 | 14:00 |
| Freitag | 07:30 | 16:00 |

Diese gelten für **alle Mitarbeitenden** ab dem 01.01.2026.

### 7.2 Globale Regelarbeitszeit ändern

Beispiel: Freitag soll ab dem 01.08.2026 um 16:00 enden:

```bash
azadmin --db db.db --user-id 1 schedule set \
  --weekday 5 \
  --start 07:30 \
  --end 16:00 \
  --from 01.08.2026
```

**Wochentage:** 1 = Montag, 2 = Dienstag, … 7 = Sonntag

**Zeitformat:** HH:MM (z. B. `07:30`, `17:00`)

**Datumsformat:** TT.MM.JJJJ (z. B. `01.08.2026`)

**Rolle:** ADMIN

### 7.3 Individuelle Regelarbeitszeit für einen Mitarbeiter

Wenn ein Mitarbeiter andere Zeiten hat als der Rest:

```bash
azadmin --db db.db --user-id 1 schedule set \
  --weekday 5 \
  --start 07:30 \
  --end 13:00 \
  --from 01.08.2026 \
  --employee-id 3
```

Die individuelle Zeit hat Vorrang vor der globalen.

### 7.4 Aktuelle Arbeitszeitpläne anzeigen

```bash
azadmin --db db.db --user-id 1 schedule show
```

**Rolle:** ADMIN oder REVIEWER

---

## Kapitel 8: Benutzerverwaltung

**Benutzerkonto** vs. **Mitarbeiterkonto**:

- Ein **Mitarbeiterkonto** (`employees`) gehört zur Person, die am
  Terminal bucht — per RFID-Karte.
- Ein **Benutzerkonto** (`users`) gehört zur Person, die das
  Admin-Programm benutzt — also der Administratorin, dem Prüfer
  oder dem IT-Betreuer.

Beides sind getrennte Datensätze. Eine Person kann beides haben.

### 8.1 Rollen

| Rolle | Berechtigung |
| --- | --- |
| `ADMIN` | Alles — Verwaltung, Berichte, Korrekturen, Backup |
| `REVIEWER` | Berichte anzeigen; Buchungskorrekturen und Nachträge genehmigen |
| `TECH` | Systemcheck und Backup ausführen |
| `EMPLOYEE` | Buchungen am Terminal — kein Zugang zum Admin-Programm |

### 8.2 Benutzerkonten anzeigen

```bash
azadmin --db db.db --user-id 1 users list
```

### 8.3 Benutzerkonto anlegen

```bash
azadmin --db db.db --user-id 1 users add \
  --username petra \
  --role REVIEWER
```

Ohne `--password` erzeugt das System ein zufälliges Passwort und
zeigt es **einmalig** an. Bitte sofort weitergeben oder notieren.

Optional kann das Konto mit einem Mitarbeiterdatensatz verknüpft werden:

```bash
azadmin --db db.db --user-id 1 users add \
  --username petra \
  --role REVIEWER \
  --employee-id 3 \
  --password geheim123
```

**Rolle:** ADMIN

### 8.4 Benutzerkonto deaktivieren und reaktivieren

```bash
# Achtung: das erste --user-id ist das eigene Konto (Administratorin),
#           das zweite --user-id ist das Zielkonto!
azadmin --db db.db --user-id 1 users deactivate --user-id 2
azadmin --db db.db --user-id 1 users reactivate --user-id 2
```

### 8.5 Rolle ändern

```bash
azadmin --db db.db --user-id 1 users change-role \
  --user-id 2 \
  --role ADMIN
```

**Rolle:** ADMIN

---

## Kapitel 9: System-Wartung

### 9.1 Backup

Das Backup erstellt eine Sicherungskopie der Datenbank:

```bash
azadmin --db db.db --user-id 1 system backup
```

Die Kopie wird im Verzeichnis gespeichert, das in `config.toml`
unter `[backup] backup_dir` angegeben ist. Wenn NAS-Synchronisation
aktiviert ist (`backup.nas_enabled = true`), wird zusätzlich auf das
NAS kopiert.

**Wichtig:** Schlägt die NAS-Übertragung fehl, ist das lokale Backup
bereits fertig. Das System meldet dann einen Fehler und beendet sich
mit Exit-Code 1.

**Rolle:** ADMIN oder TECH

### 9.2 Systemcheck

```bash
azadmin --db db.db --user-id 1 system check
```

Das System prüft automatisch:

- Datenbankzugriff
- Pflichteinstellungen in der Datenbank
- NAS-Erreichbarkeit (wenn aktiviert)
- Datenbankintegrität (Fremdschlüssel)
- Dateipfade aus `config.toml`
- Zeitsynchronisation der Systemuhr (NTP)
- RFID-Reader und Numpad erreichbar

**Rolle:** ADMIN oder TECH

### 9.3 Konfiguration einrichten oder prüfen

```bash
# Wichtig: --config muss VOR dem Befehl system stehen!
azadmin --config /pfad/config.toml --user-id 1 system setup
```

Führt einen interaktiven Dialog zur Konfiguration durch.

**Aktuelle Konfiguration anzeigen:**

```bash
python scripts/show_config.py --db datenbank.db
```

Zeigt die Werte aus `config.toml` und aus der Datenbank
nebeneinander an.

### 9.4 Hardware prüfen

```bash
# Alle erkannten Eingabegeräte auflisten
python scripts/verify_hardware.py --list

# Numpad und RFID-Reader interaktiv testen
python scripts/verify_hardware.py
```

Exit-Codes: 0 = alles in Ordnung, 1 = Fehler, 2 = Gerät nicht gefunden.

### 9.5 Regelmäßige Wartungsaufgaben

Das Betriebshandbuch `docs/04_betrieb/handbuch_backup_restore.md`
beschreibt:

- empfohlene Backup-Häufigkeit
- Schritte zur Datenwiederherstellung (Restore)
- Prüfschritte nach einem Restore

---

## Kapitel 10: Buchungsterminal als Systemdienst einrichten und verwalten

Das Buchungsterminal soll dauerhaft laufen — auch nach einem Systemneustart.
Am einfachsten gelingt das mit **systemd**, dem Dienst-Manager von Linux.
Dieser Abschnitt erklärt, wie der Dienst eingerichtet wird und wie man das
Terminal danach startet, stoppt und überwacht.

### 10.1 Warum systemd?

Ohne systemd muss das Terminal nach jedem Neustart manuell gestartet werden.
Mit systemd:

- startet das Terminal **automatisch** nach jedem Systemneustart,
- wird bei einem Absturz **automatisch neu gestartet**,
- sind alle Meldungen des Terminals in der **System-Protokolldatei**
  (`journalctl`) abrufbar,
- lässt sich das Terminal mit einem einzigen Befehl sauber stoppen.

### 10.2 Dienst-Datei erstellen

Als Administrator folgenden Inhalt in die Datei
`/etc/systemd/system/arbeitszeit-terminal.service` schreiben
(Pfade anpassen!):

```ini
[Unit]
Description=arbeitszeit Buchungsterminal
After=network.target

[Service]
Type=simple
WorkingDirectory=/pfad/zu/arbeitszeit
User=<linux-benutzer>
Group=<linux-gruppe>
Environment="VIRTUAL_ENV=/pfad/zu/arbeitszeit/.venv"
Environment="PATH=/pfad/zu/arbeitszeit/.venv/bin:/usr/bin"
ExecStart=/pfad/zu/arbeitszeit/.venv/bin/python \
  -m arbeitszeit.presentation.terminal_ui.main \
  --config /etc/arbeitszeit/config.toml
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Was bedeuten die wichtigsten Zeilen?**

| Zeile | Bedeutung |
| --- | --- |
| `WorkingDirectory` | Verzeichnis, in dem das Programm gestartet wird |
| `User` / `Group` | Linux-Konto, unter dem das Terminal läuft |
| `ExecStart` | Der vollständige Startbefehl |
| `Restart=on-failure` | Neustart bei unerwartetem Absturz |
| `RestartSec=5` | 5 Sekunden warten vor dem Neustart |

### 10.3 Dienst aktivieren und starten

```bash
# systemd über die neue Datei informieren
sudo systemctl daemon-reload

# Dienst beim Systemstart automatisch starten (einmalig einrichten)
sudo systemctl enable arbeitszeit-terminal

# Dienst jetzt sofort starten
sudo systemctl start arbeitszeit-terminal

# Prüfen, ob der Dienst läuft
sudo systemctl status arbeitszeit-terminal
```

Ein grünes `active (running)` in der Statusanzeige bedeutet: das Terminal
läuft.

### 10.4 Auswirkungen auf den täglichen Betrieb

Nach der Einrichtung ändert sich der Alltag so:

| Vorher (ohne systemd) | Nachher (mit systemd) |
| --- | --- |
| Terminal nach Neustart manuell starten | Startet automatisch |
| Bei Absturz: Terminal bleibt aus | Neustart nach 5 Sekunden |
| Keine strukturierten Protokolleinträge | Alle Meldungen in `journalctl` |
| Beenden nur über `kill` per SSH | `sudo systemctl stop …` |

Das Terminal selbst verhält sich für Mitarbeitende genauso wie bisher —
die Buchungsmaske erscheint, Karten werden gescannt, alles läuft wie
gewohnt.

### 10.5 Terminal über systemctl steuern

| Aktion | Befehl |
| --- | --- |
| Status prüfen | `sudo systemctl status arbeitszeit-terminal` |
| Starten | `sudo systemctl start arbeitszeit-terminal` |
| Sauber beenden | `sudo systemctl stop arbeitszeit-terminal` |
| Neu starten | `sudo systemctl restart arbeitszeit-terminal` |
| Autostart aktivieren | `sudo systemctl enable arbeitszeit-terminal` |
| Autostart deaktivieren | `sudo systemctl disable arbeitszeit-terminal` |

`systemctl stop` sendet ein Stoppsignal an das Terminal. Das Terminal
beendet den laufenden Buchungsschritt, gibt Numpad und RFID-Reader frei
und schaltet sich dann ab. Das dauert wenige Sekunden.

### 10.6 Meldungen des Terminals einsehen

```bash
# Meldungen live verfolgen (mit STRG+C beenden)
journalctl -u arbeitszeit-terminal -f

# Meldungen von heute
journalctl -u arbeitszeit-terminal --since today

# Nur Warnungen und Fehler
journalctl -u arbeitszeit-terminal -p warning --since today
```

### 10.7 Terminal beenden — per SSH (ohne systemd)

Falls das Terminal nicht als systemd-Dienst läuft, kann es über SSH
sauber beendet werden.

**Schritt 1:** Per SSH auf den Praxis-PC verbinden:

```bash
ssh benutzername@praxis-pc
```

**Schritt 2:** Prozess-ID des Buchungsterminals herausfinden:

```bash
pgrep -f "terminal_ui"
```

Die Ausgabe ist eine Zahl, z. B. `4287`. Keine Ausgabe bedeutet:
Terminal läuft gerade nicht.

**Schritt 3:** Terminal sauber beenden:

```bash
kill 4287
```

Die Zahl durch die eigene Prozess-ID aus Schritt 2 ersetzen.
Das Terminal beendet den aktuellen Buchungsschritt, gibt die Hardware frei
und schaltet sich dann ab.

**Schritt 4 (Kontrolle):**

```bash
pgrep -f "terminal_ui"
```

Keine Ausgabe: Terminal ist gestoppt.

### 10.8 Was man nicht tun sollte

| Aktion | Warum vermeiden |
| --- | --- |
| `kill -9 <pid>` | Erzwingt sofortigen Abbruch — Hardware wird nicht freigegeben |
| Computer ausschalten ohne vorheriges Stoppen | Gleiche Wirkung wie `kill -9` |
| SSH-Verbindung ohne `kill` trennen | Der Prozess läuft weiter — nichts passiert |

---

## Kapitel 11: Häufige Fragen und Fehlermeldungen

### 11.1 Fehlermeldungen am Terminal

| Meldung | Ursache | Was tun? |
| --- | --- | --- |
| `Karte nicht erkannt.` | Karte nicht zugewiesen | `cards assign` ausführen |
| `Karte deaktiviert.` | Karte gesperrt oder ersetzt | Neue Karte zuweisen (`cards assign`) |
| `Mitarbeiter inaktiv.` | Mitarbeiterkonto deaktiviert | Mit ADMIN klären |
| `Ungültige Buchungsreihenfolge.` | Z. B. zweimal Kommen ohne Gehen | Korrektur via `bookings correct` |
| `Offene Phase — bitte zuerst abschließen.` | Noch eine offene Schicht oder Pause | Offene Buchung via `bookings correct` schließen |

### 11.2 Buchungsstatus verstehen

| Status | Bedeutung |
| --- | --- |
| `OPEN` | Schicht oder Pause läuft noch — noch nicht abgeschlossen |
| `OK` | Abgeschlossen, alles im Rahmen der gesetzlichen Limits |
| `WARN` | Abgeschlossen, aber Abweichung vom Arbeitszeitplan oder Grenzwert-Hinweis |
| `NEEDS_REVIEW` | Muss von einer Person mit Rolle REVIEWER geprüft werden |
| `CORRECTED` | Wurde nachträglich korrigiert |
| `CLOSED_WITH_NOTE` | Manuell mit Begründung abgeschlossen |

### 11.3 Berichte: Dateien nicht gefunden

**Problem:** Die Berichtsdatei erscheint nicht.

**Ursache:** Das Exportverzeichnis ist nicht korrekt konfiguriert.

**Lösung:** In `config.toml` den Abschnitt `[backup]` prüfen:

```toml
[backup]
export_dir = "/var/exports/arbeitszeit"
```

Das Verzeichnis muss existieren und beschreibbar sein.

### 11.4 Terminal startet nicht

**Problem:** `python -m arbeitszeit.presentation.terminal_ui.main`
schlägt fehl.

**Mögliche Ursachen und Lösung:**

```bash
# Gerätenamen aller Eingabegeräte anzeigen
python scripts/verify_hardware.py --list
```

Den angezeigten genauen Namen in `config.toml` unter `[terminal]`
eintragen.

### 11.5 Prüffälle bearbeiten

Wenn eine Buchung den Status `NEEDS_REVIEW` hat, muss eine Person mit
Rolle REVIEWER aktiv werden:

```bash
# Offene Prüffälle anzeigen
azadmin --db db.db --user-id 1 reports open-review-cases

# Details zur betroffenen Buchung
azadmin --db db.db --user-id 1 reports warn-cases \
  --from 01.07.2026 --to 31.07.2026

# Korrektur oder Nachtrag anlegen
azadmin --db db.db --user-id 1 bookings correct \
  --booking-id <ID> --type <TYP> --at <ZEITPUNKT> --reason "<BEGRÜNDUNG>"
```

### 11.6 Admin-Programm antwortet mit Fehler

**Problem:** Fehlermeldung nach dem Aufruf.

| Fehlermeldung | Bedeutung |
| --- | --- |
| `command not found: admin` | Alias nicht eingerichtet; vollständigen Befehl verwenden oder Alias in ~/.bashrc eintragen |
| `Fehler: Datenbankdatei nicht gefunden` | Pfad in `--db` ist falsch |
| `Fehler: Benutzer-ID nicht gefunden` | `--user-id` zeigt auf ein nicht existentes Konto |
| `PermissionDeniedError` | Das Konto hat nicht die nötige Rolle für diesen Befehl |
| `NotFoundError` | Die angegebene ID (Buchung, Mitarbeiter, Karte) existiert nicht |

---

## Versionsvermerk

| Version | Datum | Änderungen |
| --- | --- | --- |
| v1.9 | 2026-07-20 | Neues Kapitel 10: Terminal als systemd-Dienst einrichten und verwalten (inkl. SSH-Fallback); Kapitel 10 (FAQ) → 11 |
| v1.8 | 2026-07-20 | Datumsformat auf TT.MM.JJJJ umgestellt; --at-Format auf TT.MM.JJJJ HH:MM; Terminal-UI: Hinweis auf Menüanzeige und 2-Sekunden-Pause ergänzt |
| v1.7 | 2026-07-17 | Vollständige Neustrukturierung als Laien-Handbuch: aufgabenorientiert, ohne Architekturdetails, mit konkreten Beispielen für alle Befehle |
| v1.6 | 2026-05-22 | Technisch-architektonische Dokumentation |
