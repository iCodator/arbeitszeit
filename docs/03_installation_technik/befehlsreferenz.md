---
lang: de-DE
mainfont: "Myriad Pro"
monofont: "DejaVu Sans Mono"
fontsize: 11pt
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

# Befehlsreferenz `arbeitszeit`

**Version:** 1.5
**Stand:** Juli 2026
**Projekt:** Lokales Zeiterfassungssystem für eine Zahnarztpraxis

Dieses Dokument listet die im Repository belegbaren Befehle mit Syntax,
Argumenten, Rollenanforderungen und Ausgaben. Grundlage sind ausschließlich
Quellcode und Changelog des Repositorys.

---

## Inhaltsverzeichnis

- [Allgemeines](#allgemeines)
- [Admin-CLI](#admin-cli)
  - [employees](#employees)
  - [cards](#cards)
  - [bookings](#bookings)
  - [schedule](#schedule)
  - [reports](#reports)
  - [system](#system)
  - [users](#users)
- [Terminal-UI](#terminal-ui)
- [Hilfsskripte](#hilfsskripte)
- [Rollenübersicht](#rollenübersicht)
- [Versionsvermerk](#versionsvermerk)

---

## Allgemeines

### Aufrufmuster

Die Admin-CLI ist im Repository als Python-Modul belegt:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  [--config <CONFIG_PATH>] \
  [--db <DATENBANKPFAD>] \
  [--user-id <BENUTZER-ID>] \
  <domäne> <befehl> [argumente]
```

Da der Modulpfad lang ist, verwenden alle Beispiele in diesem Dokument den
Alias `azadmin`. Einmalig in der aktuellen Shell-Sitzung einrichten:

```bash
alias azadmin="python -m arbeitszeit.presentation.admin_cli.main"
```

Für dauerhafte Verfügbarkeit in `~/.bashrc` eintragen:

```bash
echo 'alias azadmin="python -m arbeitszeit.presentation.admin_cli.main"' >> ~/.bashrc
source ~/.bashrc
```

**Hinweis:** Falls der Alias nicht aktiv ist, ersetze `azadmin` in allen
Beispielen durch `python -m arbeitszeit.presentation.admin_cli.main`.

Alternativ kann die Benutzer-ID über die Umgebungsvariable gesetzt werden:

```bash
export ADMIN_USER_ID=1
azadmin --db arbeitszeit.db employees list
```

### Globale Pflichtargumente

| Argument | Beschreibung |
| --- | --- |
| `--db PFAD` | Pfad zur SQLite-Datenbankdatei, sofern kein Wert über `config.toml` aufgelöst wird |

### Globale optionale Argumente

| Argument | Beschreibung |
| --- | --- |
| `--config CONFIG_PATH` | Pfad zu `config.toml` (Standard: automatische Suche) |
| `--user-id ID` | Benutzer-ID des ausführenden Kontos |

### Auflösung der Benutzer-ID

Die Benutzer-ID wird in folgender Reihenfolge aufgelöst:

1. CLI-Argument `--user-id`
2. Umgebungsvariable `ADMIN_USER_ID`
3. `admin.user_id` aus `config.toml`
4. Fehlerabbruch

**Ausnahme `users bootstrap`:** Kein `--user-id` erforderlich. Dieser Befehl
wird vor der Anlage des ersten Administrators ausgeführt.

### Auflösung der Konfigurationsdatei

`config.toml` wird in folgender Reihenfolge gesucht:

1. `--config <PFAD>` (explizit angegeben)
2. Umgebungsvariable `ARBEITSZEIT_CONFIG`
3. `~/.config/arbeitszeit/config.toml`
4. `./config.toml` (aktuelles Verzeichnis)

Ist keine Konfigurationsdatei auffindbar und kein `--db` angegeben, bricht
das Programm mit Exit-Code `1` ab.

### Exit-Codes

| Code | Bedeutung |
| --- | --- |
| `0` | Erfolg |
| `1` | Fehler (fehlende Berechtigung, ungültige Eingabe, Datenbankfehler, NAS-Fehler) |

### Datum- und Uhrzeitformate

| Format | Beispiel | Verwendung |
| --- | --- | --- |
| `YYYY-MM-DD` | `2026-07-01` | Datumsargumente (`--from`, `--to`, `--date`) |
| `HH:MM` | `08:30` | Uhrzeitargumente (`--start`, `--end`) |
| ISO-8601 Datetime | `2026-07-01T08:30:00` oder `2026-07-01T08:30:00Z` | `--at`-Argumente; fehlende Zeitzone wird als UTC behandelt |
| ISO-Wochennummer | `1` bis `53` | `--week`-Argument |
| Monatsnummer | `1` bis `12` | `--month`-Argument |

### Buchungstypen (`--type`)

Die CLI validiert `--type` gegen `BookingType(value.upper())`. Die konkret
zulässigen Enum-Werte werden in dieser Datei nur in den belegten Beispielen
geführt:

| Wert | Bedeutung |
| --- | --- |
| `COME` | Kommen |
| `GO` | Gehen |
| `BREAK_START` | Pause Beginn |
| `BREAK_END` | Pause Ende |

---

## Admin-CLI

---

### employees

Mitarbeiterverwaltung. Schreibzugriffe laufen über Use Cases der
Application-Schicht.

---

#### `employees list`

Listet alle Mitarbeiter auf.

```bash
azadmin --db <PFAD> employees list
```

**Rolle:** keine
**Ausgabe:**

```text
  ID  Nr            Name                            Status
------------------------------------------------------------
   1  M001          Maria Mustermann                aktiv
   2  M002          Klaus Beispiel                  inaktiv
```

oder `Keine Mitarbeiter vorhanden.`

---

#### `employees add`

Legt einen neuen Mitarbeiter an.

```bash
azadmin --db <PFAD> --user-id <ID> employees add \
  --personnel-no <PERSONALNUMMER> \
  --first-name <VORNAME> \
  --last-name <NACHNAME>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--personnel-no` | string | ja | Eindeutige Personalnummer |
| `--first-name` | string | ja | Vorname |
| `--last-name` | string | ja | Nachname |

**Rolle:** ADMIN
**Ausgabe:** `Mitarbeiter angelegt (ID 3).`
**Fehler:** Domänenfehler, z. B. doppelte Personalnummer → Exit 1

---

#### `employees deactivate`

Deaktiviert einen Mitarbeiter.

```bash
azadmin --db <PFAD> --user-id <ID> employees deactivate <MITARBEITER-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `id` | int | ja | Mitarbeiter-ID (positional) |

**Rolle:** ADMIN
**Ausgabe:** `Mitarbeiter 3 deaktiviert.`

---

### cards

RFID-Kartenverwaltung. Alle Schreibzugriffe erfordern `ADMIN`.

---

#### `cards assign`

Weist einem Mitarbeiter eine neue RFID-Karte zu. Die UID kann direkt vom
RFID-Reader eingelesen (`--scan --rfid`) oder als vorab berechneter Hash
übergeben werden (`--uid-hash`). Beide Varianten schließen sich gegenseitig aus.

**Methode 1 – Direkt scannen:**

```bash
azadmin --db <PFAD> --user-id <ID> cards assign \
  --employee-id <MITARBEITER-ID> \
  --scan \
  --rfid "HID 1234:5678"
```

**Methode 2 – Hash manuell angeben:**

```bash
azadmin --db <PFAD> --user-id <ID> cards assign \
  --employee-id <MITARBEITER-ID> \
  --uid-hash <HASH>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--employee-id` | int | ja | ID des zugehörigen Mitarbeiters |
| `--scan` | flag | nein¹ | UID direkt vom RFID-Reader einlesen |
| `--rfid` | string | nein¹ | Gerätename oder -pfad des RFID-Readers für `--scan` |
| `--uid-hash` | string | nein¹ | SHA-256-Hash der Karten-UID |

¹ Entweder `--uid-hash` oder `--scan` zusammen mit `--rfid` muss angegeben
werden.

**Rolle:** ADMIN
**Ausgabe:** `Karte zugewiesen (ID 5).`
**Fehler:** UID-Hash bereits vergeben, Mitarbeiter nicht gefunden,
RFID-Scan-Timeout, Gerät nicht gefunden → Exit 1

---

#### `cards replace`

Ersetzt eine verlorene oder defekte Karte durch eine neue.

```bash
azadmin --db <PFAD> --user-id <ID> cards replace \
  --old-card-id <ALTE-KARTEN-ID> \
  --uid-hash <NEUER-HASH>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--old-card-id` | int | ja | ID der zu ersetzenden Karte |
| `--uid-hash` | string | ja | SHA-256-Hash der neuen Karte |

**Hinweis:** `cards replace` akzeptiert keinen `--scan`-Modus. Den UID-Hash der
neuen Karte vorab mit `scripts/verify_hardware.py` ermitteln (beim Scan wird
der Hash ausgegeben).

**Rolle:** ADMIN
**Ausgabe:** `Karte ersetzt: alt=5, neu=6.`

---

#### `cards deactivate`

Deaktiviert eine RFID-Karte.

```bash
azadmin --db <PFAD> --user-id <ID> cards deactivate <KARTEN-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `id` | int | ja | Karten-ID (positional) |

**Rolle:** ADMIN
**Ausgabe:** `Karte 5 deaktiviert.`

---

### bookings

Buchungskorrekturen und Nachträge. Die CLI validiert Eingabeformate und
übergibt an Use Cases der Application-Schicht.

---

#### `bookings correct`

Korrigiert eine bestehende Buchung.

```bash
azadmin --db <PFAD> --user-id <ID> bookings correct \
  --booking-id <BUCHUNGS-ID> \
  --type <BUCHUNGSTYP> \
  --at <ISO-DATETIME> \
  --reason <BEGRÜNDUNG>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--booking-id` | int | ja | ID der zu korrigierenden Buchung |
| `--type` | string | ja | Neuer Buchungstyp |
| `--at` | ISO-8601 | ja | Neuer Buchungszeitpunkt |
| `--reason` | string | ja | Begründung der Korrektur |

**Rolle:** ADMIN, REVIEWER
**Ausgabe:** `Korrektur angelegt (ID 12), Buchung 47 auf CORRECTED gesetzt.`
**Fehler:** Ungültiger Buchungstyp, ungültiges Datum, Domänenfehler → Exit 1

---

#### `bookings supplement`

Erfasst eine nachträgliche Buchung und erzeugt einen Prüffall.

```bash
azadmin --db <PFAD> --user-id <ID> bookings supplement \
  --employee-id <MITARBEITER-ID> \
  --type <BUCHUNGSTYP> \
  --at <ISO-DATETIME> \
  --reason <BEGRÜNDUNG> \
  [--related-booking-id <BUCHUNGS-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--employee-id` | int | ja | Mitarbeiter-ID |
| `--type` | string | ja | Buchungstyp |
| `--at` | ISO-8601 | ja | Ereigniszeitpunkt |
| `--reason` | string | ja | Begründung |
| `--related-booking-id` | int | nein | Verknüpfte Buchung |

**Rolle:** ADMIN, REVIEWER
**Ausgabe:** `Nachtrag angelegt (ID 8), Prüffall 3 erzeugt.`

---

#### `bookings approve-supplement`

Genehmigt einen Nachtrag.

```bash
azadmin --db <PFAD> --user-id <ID> bookings approve-supplement \
  --supplement-id <NACHTRAGS-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--supplement-id` | int | ja | ID des zu genehmigenden Nachtrags |

**Rolle:** ADMIN, REVIEWER
**Ausgabe:** `Nachtrag 8 genehmigt, Buchung 52 angelegt (Status: OK).`

---

#### `bookings reject-supplement`

Lehnt einen Nachtrag ab.

```bash
azadmin --db <PFAD> --user-id <ID> bookings reject-supplement \
  --supplement-id <NACHTRAGS-ID> \
  --reason <BEGRÜNDUNG>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--supplement-id` | int | ja | ID des abzulehnenden Nachtrags |
| `--reason` | string | ja | Ablehnungsgrund |

**Rolle:** ADMIN, REVIEWER
**Ausgabe:** `Nachtrag 8 abgelehnt.`

---

### schedule

Regelarbeitszeit verwalten.

---

#### `schedule set`

Setzt die Regelarbeitszeit für einen Wochentag global oder
mitarbeiterspezifisch.

```bash
azadmin --db <PFAD> --user-id <ID> schedule set \
  --weekday <1-7> \
  --start <HH:MM> \
  --end <HH:MM> \
  --from <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--weekday` | int (1–7) | ja | Wochentag: 1=Mo, 2=Di, …, 7=So |
| `--start` | HH:MM | ja | Beginn der Regelarbeitszeit |
| `--end` | HH:MM | ja | Ende der Regelarbeitszeit |
| `--from` | YYYY-MM-DD | ja | Gültig ab diesem Datum |
| `--employee-id` | int | nein | Mitarbeiterspezifische Ausnahme |

**Rolle:** ADMIN
**Ausgabe (global):**

```text
Globale Regelarbeitszeit gesetzt (Version 3): Mo 08:00–17:00 ab 2026-08-01.
Vorgängerversion 1 geschlossen.
```

**Ausgabe (mitarbeiterspezifisch):**

```text
Mitarbeiterspezifische Regelarbeitszeit gesetzt (Version 4): Mitarbeiter 2, Mo 09:00–16:00 ab 2026-08-01.
```

---

#### `schedule show`

Zeigt alle aktiven Regelarbeitszeitversionen.

```bash
azadmin --db <PFAD> --user-id <ID> schedule show
```

**Rolle:** ADMIN, REVIEWER
**Ausgabe:**

```text
Globale Regelarbeitszeit (gültige Versionen):
    ID  Tag  Von    Bis    Gültig ab
     3  Mo   08:00  17:00  2026-08-01

Mitarbeiterspezifische Regelarbeitszeit:
    ID  MitarID  Tag  Von    Bis    Gültig ab
     4        2  Mo   09:00  16:00  2026-08-01
```

oder `Keine aktiven Regelarbeitszeitversionen vorhanden.`

---

### reports

Berichte und Pflichtauswertungen. Alle Report-Befehle erfordern `ADMIN` oder
`REVIEWER`. Das Exportverzeichnis wird aus `config.toml` `[backup] export_dir`
gelesen — gesetzt via `scripts/setup.py` oder `system setup`.

---

#### `reports export-csv`

Exportiert Detailbuchungen und verdichtete Übersicht als CSV.

```bash
azadmin --db <PFAD> --user-id <ID> reports export-csv \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--from` | YYYY-MM-DD | ja | Beginn des Zeitraums |
| `--to` | YYYY-MM-DD | ja | Ende des Zeitraums |
| `--employee-id` | int | nein | Nur für diesen Mitarbeiter |

**Ausgabe:**

```text
Detail-CSV: /var/exports/arbeitszeit/export_detail_20260701_20260731_20260701T120000Z.csv
Verdichtet-CSV: /var/exports/arbeitszeit/export_verdichtet_20260701_20260731_20260701T120000Z.csv
```

---

#### `reports export-csv-review-cases`

Exportiert Prüffälle im Zeitraum als CSV.

```bash
azadmin --db <PFAD> --user-id <ID> reports export-csv-review-cases \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--from` | YYYY-MM-DD | ja | Beginn des Zeitraums |
| `--to` | YYYY-MM-DD | ja | Ende des Zeitraums |
| `--employee-id` | int | nein | Nur für diesen Mitarbeiter |

**Ausgabe:**

```text
Prüffälle-CSV: /var/exports/arbeitszeit/export_prueffaelle_20260701_20260731_20260701T120000Z.csv
```

---

#### `reports export-pdf-day`

Erstellt einen Tagesbericht als PDF.

```bash
azadmin --db <PFAD> --user-id <ID> reports export-pdf-day \
  --date <YYYY-MM-DD>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--date` | YYYY-MM-DD | ja | Kalendertag des Berichts |

**Ausgabe:** `PDF: /var/exports/arbeitszeit/bericht_tag_2026-07-01_….pdf`

---

#### `reports export-pdf-week`

Erstellt einen Wochenbericht als PDF.

```bash
azadmin --db <PFAD> --user-id <ID> reports export-pdf-week \
  --year <YYYY> \
  --week <1-53>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--year` | int | ja | Jahr |
| `--week` | int | ja | ISO-Wochennummer |

**Ausgabe:** `PDF: /var/exports/arbeitszeit/bericht_woche_2026-W27_….pdf`

---

#### `reports export-pdf-month`

Erstellt einen Monatsbericht als PDF.

```bash
azadmin --db <PFAD> --user-id <ID> reports export-pdf-month \
  --year <YYYY> \
  --month <1-12>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--year` | int | ja | Jahr |
| `--month` | int | ja | Monatsnummer |

**Ausgabe:** `PDF: /var/exports/arbeitszeit/bericht_monat_2026-07_….pdf`

---

#### `reports export-pdf-employee`

Erstellt einen Mitarbeiterbericht für einen Zeitraum als PDF.

```bash
azadmin --db <PFAD> --user-id <ID> reports export-pdf-employee \
  --employee-id <MITARBEITER-ID> \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--employee-id` | int | ja | Mitarbeiter-ID |
| `--from` | YYYY-MM-DD | ja | Beginn des Zeitraums |
| `--to` | YYYY-MM-DD | ja | Ende des Zeitraums |

**Ausgabe:** `PDF: /var/exports/arbeitszeit/bericht_mitarbeiter_0001_….pdf`

---

#### `reports open-bookings`

Listet Buchungen mit Status `OPEN`, optional im Zeitraum gefiltert.

```bash
azadmin --db <PFAD> --user-id <ID> reports open-bookings \
  [--from <YYYY-MM-DD> --to <YYYY-MM-DD>] \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--from` | YYYY-MM-DD | nein | Beginn des Zeitraums |
| `--to` | YYYY-MM-DD | nein | Ende des Zeitraums |
| `--employee-id` | int | nein | Nur für diesen Mitarbeiter |

**Hinweis:** Werden mehr als 50 Einträge ohne Zeitraumfilter gefunden,
erscheint ein Hinweis auf stderr, `--from` und `--to` zu verwenden.

---

#### `reports warn-cases`

Listet Buchungen mit Status `WARN` oder `NEEDS_REVIEW` im Zeitraum.

```bash
azadmin --db <PFAD> --user-id <ID> reports warn-cases \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--from` | YYYY-MM-DD | ja | Beginn |
| `--to` | YYYY-MM-DD | ja | Ende |
| `--employee-id` | int | nein | Filter |

---

#### `reports corrections`

Listet Buchungskorrekturen im Zeitraum.

```bash
azadmin --db <PFAD> --user-id <ID> reports corrections \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

---

#### `reports supplements`

Listet Nachträge im Zeitraum.

```bash
azadmin --db <PFAD> --user-id <ID> reports supplements \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

---

#### `reports open-review-cases`

Listet offene Prüffälle, optional im Zeitraum gefiltert.

```bash
azadmin --db <PFAD> --user-id <ID> reports open-review-cases \
  [--from <YYYY-MM-DD> --to <YYYY-MM-DD>] \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--from` | YYYY-MM-DD | nein | Beginn |
| `--to` | YYYY-MM-DD | nein | Ende |
| `--employee-id` | int | nein | Filter |

**Hinweis:** Wie `open-bookings` erfolgt bei mehr als 50 ungefilterten
Einträgen ein Hinweis auf stderr.

---

### system

Systemcheck, Backup und Konfiguration.

---

#### `system check`

Führt einen Systemcheck durch und gibt den Status aller Prüfpunkte aus.

```bash
azadmin --db <PFAD> --user-id <ID> system check
```

**Rolle:** ADMIN, TECH
**Exit-Code:** `0` = alles OK, `1` = mindestens ein Check fehlgeschlagen

---

#### `system backup`

Erstellt manuell ein Datenbank-Backup und synchronisiert optional auf den NAS.

```bash
azadmin --db <PFAD> --user-id <ID> system backup
```

**Rolle:** ADMIN, TECH
**Ausgabe (Erfolg, NAS aktiv):**

```text
Backup erstellt: /var/backups/arbeitszeit/arbeitszeit_20260701T120000Z.db
NAS-Synchronisation erfolgreich.
```

**Ausgabe (Erfolg, kein NAS):**

```text
Backup erstellt: /var/backups/arbeitszeit/arbeitszeit_20260701T120000Z.db
```

**Fehler:** `backup_dir` nicht konfiguriert → Exit 1;
NAS-Synchronisation fehlgeschlagen → Exit 1

---

#### `system setup`

Bearbeitet die `config.toml` interaktiv.

```bash
azadmin [--config <CONFIG_PATH>] --db <PFAD> --user-id <ID> system setup
```

**Wichtig:** `--config` ist ein **globales Argument** und muss **vor** dem
Domainnamen `system` angegeben werden. Die folgende Syntax ist falsch:

```bash
azadmin system setup --config /pfad/config.toml  # FALSCH – --config gehört vor "system"
```

**Rolle:** ADMIN, TECH
**Verhalten:** Der Schreibpfad wird über `resolve_config_write_path()` bestimmt;
anschließend wird `setup_config()` aufgerufen.

---

### users

Benutzerkontenverwaltung. Passwörter werden mit PBKDF2-HMAC-SHA256,
260.000 Iterationen und Zufallssalt gehasht.

---

#### `users bootstrap`

Legt das erste Administratorkonto an.

```bash
azadmin --db <PFAD> users bootstrap \
  --username <BENUTZERNAME> \
  [--password <PASSWORT>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--username` | string | ja | Benutzername des ersten Administrators |
| `--password` | string | nein | Passwort; wird bei Weglassen generiert |

**Rolle:** keine
**Ausgabe:**

```text
Erstes Administratorkonto angelegt (ID 1).
Generiertes Passwort (einmalig sichtbar): xKj8!mP2nqR5
```

---

#### `users add`

Legt ein neues Benutzerkonto an.

```bash
azadmin --db <PFAD> --user-id <ID> users add \
  --username <BENUTZERNAME> \
  --role <ROLLE> \
  [--employee-id <MITARBEITER-ID>] \
  [--password <PASSWORT>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--username` | string | ja | Eindeutiger Benutzername |
| `--role` | ADMIN\|REVIEWER\|TECH | ja | Rolle |
| `--employee-id` | int | nein | Verknüpfter Mitarbeiter |
| `--password` | string | nein | Passwort; wird bei Weglassen generiert |

**Rolle:** ADMIN
**Ausgabe:**

```text
Benutzerkonto angelegt (ID 2).
Generiertes Passwort (einmalig sichtbar): mN7$qZ3vLp9w
```

---

#### `users list`

Listet alle Benutzerkonten außer `EMPLOYEE` auf.

```bash
azadmin --db <PFAD> users list
```

**Rolle:** keine

---

#### `users deactivate`

Deaktiviert ein Benutzerkonto.

**Achtung — zwei `--user-id`-Argumente:** Das erste (globale) `--user-id` ist
die ID des ausführenden Admins. Das zweite `--user-id` (nach dem Subcommand)
ist das Zielkonto. Beispiel: Admin mit ID 1 deaktiviert Konto mit ID 3:

```bash
azadmin --db <PFAD> --user-id 1 users deactivate --user-id 3
```

Vollständige Syntax:

```bash
azadmin --db <PFAD> --user-id <ID> users deactivate \
  --user-id <ZIEL-BENUTZER-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--user-id` | int | ja | ID des zu deaktivierenden Kontos |

**Rolle:** ADMIN
**Ausgabe:** `Benutzerkonto 3 deaktiviert.`

---

#### `users reactivate`

Reaktiviert ein deaktiviertes Benutzerkonto.

**Achtung — zwei `--user-id`-Argumente:** Wie bei `users deactivate` gilt das
erste `--user-id` dem ausführenden Admin, das zweite dem Zielkonto.

```bash
azadmin --db <PFAD> --user-id <ID> users reactivate \
  --user-id <ZIEL-BENUTZER-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--user-id` | int | ja | ID des zu reaktivierenden Kontos |

**Rolle:** ADMIN
**Ausgabe:** `Benutzerkonto 3 reaktiviert.`

---

#### `users change-role`

Ändert die Rolle eines Benutzerkontos.

**Achtung — zwei `--user-id`-Argumente:** Wie bei `users deactivate` gilt das
erste `--user-id` dem ausführenden Admin, das zweite dem Zielkonto.

```bash
azadmin --db <PFAD> --user-id <ID> users change-role \
  --user-id <ZIEL-BENUTZER-ID> \
  --role <NEUE-ROLLE>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--user-id` | int | ja | ID des Benutzerkontos |
| `--role` | ADMIN\|REVIEWER\|TECH | ja | Neue Rolle |

**Rolle:** ADMIN
**Ausgabe:** `Rolle von Benutzerkonto 2 geändert.`

---

## Terminal-UI

Die Terminal-UI läuft dauerhaft am Buchungsgerät und verarbeitet RFID-Scans
und Numpad-Eingaben.

### Aufruf

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  [--config <CONFIG_PATH>] \
  [--db <DATENBANKPFAD>] \
  [--numpad <GERÄTENAME_ODER_PFAD>] \
  [--rfid <GERÄTENAME_ODER_PFAD>] \
  [--terminal-id <ID>]
```

| Argument | Typ | Beschreibung |
| --- | --- | --- |
| `--config` | Pfad | Pfad zu `config.toml` |
| `--db` | Pfad | SQLite-Datenbankdatei; alternativ aus `config.toml` |
| `--numpad` | Gerätename oder -pfad | z. B. `USB Numpad` oder `/dev/input/event3` |
| `--rfid` | Gerätename oder -pfad | z. B. `RFID Reader` oder `/dev/input/event4` |
| `--terminal-id` | int | Eindeutige Terminal-ID; alternativ aus `config.toml` |

**Hinweis:** Die Werte werden in der Priorität CLI → `config.toml` → Fehler
aufgelöst. Die Argumente sind daher nicht in jedem Fall als CLI-Pflicht zu
verstehen, müssen aber insgesamt auflösbar sein.

### Buchungszyklus

1. Mitarbeiter drückt auf dem Numpad eine Taste (`1` bis `4`).
2. Mitarbeiter hält RFID-Karte an den Leser.
3. System verarbeitet die Buchung und gibt Feedback aus.

### Rückmeldungen

| Situation | Ausgabe |
| --- | --- |
| Buchung erfasst (Status `OK` oder `OPEN`) | `Buchung erfasst.` |
| Buchung erfasst (Status `WARN`) | `Buchung erfasst — Hinweis: Regelzeitabweichung festgestellt.` |
| Buchung erfasst (Status `NEEDS_REVIEW`) | `Buchung erfasst — Prüfpflicht: Manuelle Überprüfung erforderlich.` |
| Karte unbekannt | `Karte nicht erkannt.` |
| Karte deaktiviert | `Karte deaktiviert.` |
| Mitarbeiter inaktiv | `Mitarbeiter inaktiv.` |
| Falsche Buchungsreihenfolge | `Ungültige Buchungsreihenfolge.` |
| Offene Phase | `Offene Phase — bitte zuerst abschließen.` |
| Interner Fehler | `Interner Fehler — Betrieb wird fortgesetzt.` |

### Beenden

`Ctrl+C` oder `SIGTERM` — sauberes Beenden der Schleife.

---

## Hilfsskripte

---

### `scripts/init_db.py`

Führt alle ausstehenden Datenbankmigrationen aus.

```bash
python scripts/init_db.py [--db <PFAD>]
```

| Argument | Standard | Beschreibung |
| --- | --- | --- |
| `--db` | `arbeitszeit.db` | Datenbankdatei |

**Ausgabe:** Eine Zeile pro angewendeter Migration; Hinweis auf
Ersteinrichtung, wenn `scripts/setup.py` noch erforderlich ist.

---

### `scripts/setup.py`

Ersteinrichtung und Pflege der `config.toml`.

```bash
python scripts/setup.py \
  [--config <CONFIG_PATH>] \
  [--db <DB_PATH>] \
  [--terminal-id <ID>] \
  [--numpad <NAME>] \
  [--rfid <NAME>] \
  [--admin-user-id <ID>] \
  [--backup-dir <PFAD>] \
  [--export-dir <PFAD>] \
  [--log-dir <PFAD>]
```

| Argument | Beschreibung |
| --- | --- |
| `--config` | Zielpfad für `config.toml` |
| `--db` | Datenbankpfad; wird auch als Hinweisquelle für Migrationswerte genutzt |
| `--terminal-id` | Terminal-ID |
| `--numpad` | Numpad-Gerätename |
| `--rfid` | RFID-Gerätename |
| `--admin-user-id` | Admin-Benutzer-ID |
| `--backup-dir` | Backup-Verzeichnis |
| `--export-dir` | Exportverzeichnis |
| `--log-dir` | Log-Verzeichnis |

**Hinweis:** Das Skript schreibt `config.toml` und nicht primär
`system_config`-Einträge.

---

### `scripts/backup.py`

Erstellt ein lokales Backup und synchronisiert optional auf den NAS.

```bash
python scripts/backup.py \
  [--db <PFAD>] \
  [--config <CONFIG_PATH>] \
  [--backup-dir <PFAD>] \
  [--export-dir <PFAD>]
```

| Argument | Standard | Beschreibung |
| --- | --- | --- |
| `--db` | `arbeitszeit.db` | Quelldatenbank |
| `--config` | automatische Suche | Pfad zu `config.toml` |
| `--backup-dir` | `backups/` | Backup-Zielverzeichnis, falls nicht in `config.toml` gesetzt |
| `--export-dir` | — | Exportverzeichnis |

---

### `scripts/verify_hardware.py`

Interaktiver Hardware-Smoke-Test für Numpad und RFID-Leser.

```bash
python scripts/verify_hardware.py \
  [--numpad <GERÄTEPFAD> --rfid <GERÄTEPFAD>] \
  [--list] \
  [--skip-interactive]
```

| Argument | Beschreibung |
| --- | --- |
| `--numpad` | Numpad-Gerätepfad |
| `--rfid` | RFID-Lesegerätepfad |
| `--list` | Nur Gerätedateien auflisten |
| `--skip-interactive` | Nur Gerätezugriff prüfen |

**Wichtig:** `--numpad` und `--rfid` müssen gemeinsam angegeben werden. Werden
beide weggelassen, startet eine interaktive Geräteauswahl.

**Exit-Codes:** `0` = alle Tests bestanden, `1` = mindestens ein Test
fehlgeschlagen, `2` = `evdev` nicht installiert

---

### `scripts/show_config.py`

Zeigt die aktuelle Konfiguration aus `config.toml` und `system_config` an.

```bash
python scripts/show_config.py \
  --db <PFAD> \
  [--config <CONFIG_PATH>] \
  [--all-versions] \
  [--json]
```

| Argument | Beschreibung |
| --- | --- |
| `--db` | Datenbankdatei (Pflicht) |
| `--config` | Pfad zu `config.toml` |
| `--all-versions` | Alle Versionen statt nur aktueller Werte anzeigen |
| `--json` | JSON-Ausgabe statt Tabelle |

---

## Rollenübersicht

| Befehl | Rolle | Prüfung |
| --- | --- | --- |
| `employees list` | keine | — |
| `employees add` | ADMIN | Use Case |
| `employees deactivate` | ADMIN | Use Case |
| `cards assign` | ADMIN | Use Case |
| `cards replace` | ADMIN | Use Case |
| `cards deactivate` | ADMIN | Use Case |
| `bookings correct` | ADMIN, REVIEWER | Use Case |
| `bookings supplement` | ADMIN, REVIEWER | Use Case |
| `bookings approve-supplement` | ADMIN, REVIEWER | Use Case |
| `bookings reject-supplement` | ADMIN, REVIEWER | Use Case |
| `schedule set` | ADMIN | Use Case |
| `schedule show` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports export-csv` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports export-csv-review-cases` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports export-pdf-day` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports export-pdf-week` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports export-pdf-month` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports export-pdf-employee` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports open-bookings` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports warn-cases` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports corrections` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports supplements` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `reports open-review-cases` | ADMIN, REVIEWER | CLI (`_auth.py`) |
| `system check` | ADMIN, TECH | CLI (`_auth.py`) |
| `system backup` | ADMIN, TECH | CLI (`_auth.py`) |
| `system setup` | ADMIN, TECH | CLI (`_auth.py`) |
| `users bootstrap` | keine | Use Case |
| `users add` | ADMIN | Use Case |
| `users list` | keine | — |
| `users deactivate` | ADMIN | Use Case |
| `users reactivate` | ADMIN | Use Case |
| `users change-role` | ADMIN | Use Case |
| Terminal-UI | keine CLI-Rolle | Use Case |

---

## Versionsvermerk

- **Vorversion:** 1.4
- **Neue Version:** 1.5
- **Begründung:** Minor-Erhöhung wegen grundlegender Korrektur der Befehlsbeispiele
  (alle `admin ...`-Kurzformen durch belegbaren `azadmin`-Alias ersetzt), Behebung
  veralteter Dokumentation (`export_dir`-Quelle), Belegung der bookings-Rollen aus
  Use Cases (ADMIN, REVIEWER) sowie Laien-gerechten Hinweisen zum `--user-id`-Konflikt,
  zur `--config`-Platzierung bei `system setup`, zur Alias-Einrichtung und zu
  `cards replace`.
