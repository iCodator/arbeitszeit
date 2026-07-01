# Befehlsreferenz `arbeitszeit`

**Version:** 1.0  
**Stand:** Juli 2026  
**Projekt:** Lokales Zeiterfassungssystem für eine Zahnarztpraxis

Dieses Dokument listet alle verfügbaren Befehle mit vollständiger Syntax,
Argumenten, Rollenanforderungen und Ausgaben. Architekturhintergründe finden
sich im `handbuch_arbeitszeit.md`.

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

---

## Allgemeines

### Aufrufmuster

```bash
python -m arbeitszeit.presentation.admin_cli.main \
  --db <DATENBANKPFAD> \
  [--user-id <BENUTZER-ID>] \
  <domäne> <befehl> [argumente]
```

Alternativ kann die Benutzer-ID über die Umgebungsvariable gesetzt werden:

```bash
export ADMIN_USER_ID=1
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db employees list
```

### Globale Pflichtargumente

| Argument | Beschreibung |
| --- | --- |
| `--db PFAD` | Pfad zur SQLite-Datenbankdatei |

### Globale optionale Argumente

| Argument | Beschreibung |
| --- | --- |
| `--user-id ID` | Benutzer-ID des ausführenden Kontos (alternativ: `ADMIN_USER_ID`) |

**Ausnahme `users bootstrap`:** Kein `--user-id` erforderlich — dieser Befehl
wird vor der Anlage des ersten Administrators ausgeführt.

### Exit-Codes

| Code | Bedeutung |
| --- | --- |
| `0` | Erfolg |
| `1` | Fehler (fehlende Berechtigung, ungültige Eingabe, Datenbankfehler, NAS-Fehler) |

### Datum- und Uhrzeitformate

| Format | Beispiel | Verwendung |
| --- | --- | --- |
| `YYYY-MM-DD` | `2026-07-01` | Datumsargumente (`--from`, `--to`, `--date`, `--from_date`) |
| `HH:MM` | `08:30` | Uhrzeitargumente (`--start`, `--end`) |
| ISO-8601 Datetime | `2026-07-01T08:30:00` oder `2026-07-01T08:30:00Z` | `--at`-Argumente; fehlende Zeitzone → UTC |
| ISO-Wochennummer | `1`–`53` | `--week`-Argument |
| Monatsnummer | `1`–`12` | `--month`-Argument |

### Buchungstypen (`--type`)

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

Mitarbeiterverwaltung. Schreibzugriffe erfordern `ADMIN`-Rolle; die
Rollenprüfung erfolgt in der Anwendungsschicht.

---

#### `employees list`

Listet alle Mitarbeiter auf.

```bash
admin --db <PFAD> employees list
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
admin --db <PFAD> --user-id <ID> employees add \
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
**Fehler:** Doppelte Personalnummer → Exit 1

---

#### `employees deactivate`

Deaktiviert einen Mitarbeiter.

```bash
admin --db <PFAD> --user-id <ID> employees deactivate <MITARBEITER-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `id` | int | ja | Mitarbeiter-ID (positional) |

**Rolle:** ADMIN  
**Ausgabe:** `Mitarbeiter 3 deaktiviert.`  
**Fehler:** ID nicht gefunden → Exit 1

---

### cards

RFID-Kartenverwaltung. Alle Schreibzugriffe erfordern `ADMIN`-Rolle.

---

#### `cards assign`

Weist einem Mitarbeiter eine neue RFID-Karte zu.

```bash
admin --db <PFAD> --user-id <ID> cards assign \
  --employee-id <MITARBEITER-ID> \
  --uid-hash <HASH>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--employee-id` | int | ja | ID des zugehörigen Mitarbeiters |
| `--uid-hash` | string | ja | SHA-256-Hash der Karten-UID (siehe `scripts/verify_hardware.py`) |

**Rolle:** ADMIN  
**Ausgabe:** `Karte zugewiesen (ID 5).`  
**Fehler:** UID-Hash bereits vergeben, Mitarbeiter nicht gefunden → Exit 1

---

#### `cards replace`

Ersetzt eine verlorene oder defekte Karte durch eine neue. Die alte Karte
erhält den Status `REPLACED`.

```bash
admin --db <PFAD> --user-id <ID> cards replace \
  --old-card-id <ALTE-KARTEN-ID> \
  --uid-hash <NEUER-HASH>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--old-card-id` | int | ja | ID der zu ersetzenden Karte |
| `--uid-hash` | string | ja | SHA-256-Hash der neuen Karte |

**Rolle:** ADMIN  
**Ausgabe:** `Karte ersetzt: alt=5, neu=6.`  
**Fehler:** Alte Karte nicht gefunden, neuer UID-Hash bereits vergeben → Exit 1

---

#### `cards deactivate`

Deaktiviert eine RFID-Karte (Status → `INACTIVE`).

```bash
admin --db <PFAD> --user-id <ID> cards deactivate <KARTEN-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `id` | int | ja | Karten-ID (positional) |

**Rolle:** ADMIN  
**Ausgabe:** `Karte 5 deaktiviert.`  
**Fehler:** ID nicht gefunden → Exit 1

---

### bookings

Buchungskorrekturen und Nachträge. Rollenprüfung erfolgt vollständig in
der Anwendungsschicht.

---

#### `bookings correct`

Korrigiert eine bestehende Buchung (ändert Typ oder Zeitstempel).

```bash
admin --db <PFAD> --user-id <ID> bookings correct \
  --booking-id <BUCHUNGS-ID> \
  --type <BUCHUNGSTYP> \
  --at <ISO-DATETIME> \
  --reason <BEGRÜNDUNG>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--booking-id` | int | ja | ID der zu korrigierenden Buchung |
| `--type` | string | ja | Neuer Buchungstyp (`COME`, `GO`, `BREAK_START`, `BREAK_END`) |
| `--at` | ISO-8601 | ja | Neuer Buchungszeitpunkt |
| `--reason` | string | ja | Begründung der Korrektur |

**Rolle:** ADMIN, REVIEWER  
**Ausgabe:** `Korrektur angelegt (ID 12), Buchung 47 auf CORRECTED gesetzt.`  
**Fehler:** Ungültiger Buchungstyp, ungültiges Datum, Buchung nicht gefunden → Exit 1

---

#### `bookings supplement`

Erfasst eine nachträgliche Buchung (Nachtrag). Erzeugt automatisch einen
Prüffall.

```bash
admin --db <PFAD> --user-id <ID> bookings supplement \
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
| `--related-booking-id` | int | nein | Verknüpfte Buchung (optional) |

**Rolle:** ADMIN, REVIEWER  
**Ausgabe:** `Nachtrag angelegt (ID 8), Prüffall 3 erzeugt.`  
**Fehler:** Ungültiger Buchungstyp, Mitarbeiter nicht gefunden → Exit 1

---

#### `bookings approve-supplement`

Genehmigt einen Nachtrag. Erstellt eine wirksame Buchung.

```bash
admin --db <PFAD> --user-id <ID> bookings approve-supplement \
  --supplement-id <NACHTRAGS-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--supplement-id` | int | ja | ID des zu genehmigenden Nachtrags |

**Rolle:** ADMIN, REVIEWER  
**Ausgabe:** `Nachtrag 8 genehmigt, Buchung 52 angelegt (Status: OK).`  
**Fehler:** Nachtrag nicht gefunden, bereits bearbeitet → Exit 1

---

#### `bookings reject-supplement`

Lehnt einen Nachtrag ab.

```bash
admin --db <PFAD> --user-id <ID> bookings reject-supplement \
  --supplement-id <NACHTRAGS-ID> \
  --reason <BEGRÜNDUNG>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--supplement-id` | int | ja | ID des abzulehnenden Nachtrags |
| `--reason` | string | ja | Ablehnungsgrund |

**Rolle:** ADMIN, REVIEWER  
**Ausgabe:** `Nachtrag 8 abgelehnt.`  
**Fehler:** Nachtrag nicht gefunden, bereits bearbeitet → Exit 1

---

### schedule

Regelarbeitszeit verwalten.

---

#### `schedule set`

Setzt die Regelarbeitszeit für einen Wochentag — global (alle Mitarbeiter)
oder mitarbeiterspezifisch. Jede Änderung erzeugt eine neue Version und
schließt die Vorgängerversion.

```bash
admin --db <PFAD> --user-id <ID> schedule set \
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
| `--employee-id` | int | nein | Wenn angegeben: mitarbeiterspezifische Ausnahme |

**Rolle:** ADMIN (Prüfung in `ManageWorkScheduleUseCase`)  
**Ausgabe (global):**

```text
Globale Regelarbeitszeit gesetzt (Version 3): Mo 08:00–17:00 ab 2026-08-01.
Vorgängerversion 1 geschlossen.
```

**Ausgabe (mitarbeiterspezifisch):**

```text
Mitarbeiterspezifische Regelarbeitszeit gesetzt (Version 4): Mitarbeiter 2, Mo 09:00–16:00 ab 2026-08-01.
```

**Fehler:** Ungültiges Datum/Uhrzeit, Versionskonflikt → Exit 1

---

#### `schedule show`

Zeigt alle aktiven Regelarbeitszeitversionen.

```bash
admin --db <PFAD> --user-id <ID> schedule show
```

**Rolle:** ADMIN, REVIEWER (Prüfung in CLI via `require_admin_or_reviewer`)  
**Ausgabe:**

```text
Globale Regelarbeitszeit (gültige Versionen):
    ID  Tag  Von    Bis    Gültig ab
   -----------------------------------
     3  Mo   08:00  17:00  2026-08-01

Mitarbeiterspezifische Regelarbeitszeit:
    ID  MitarID  Tag  Von    Bis    Gültig ab
   -------------------------------------------
     4        2  Mo   09:00  16:00  2026-08-01

Hinweis: Globale Praxisregel gilt für alle Mitarbeiter (keine Ausnahmen).
```

oder `Keine aktiven Regelarbeitszeitversionen vorhanden.`

---

### reports

Berichte und Pflichtauswertungen. Alle Report-Befehle erfordern `ADMIN`-
oder `REVIEWER`-Rolle; die Prüfung erfolgt in der CLI via `require_admin_or_reviewer`.
Das Exportverzeichnis wird aus `system_config` (Schlüssel `export.export_dir`) gelesen.

---

#### `reports export-csv`

Exportiert Detailbuchungen und verdichtete Übersicht als CSV.

```bash
admin --db <PFAD> --user-id <ID> reports export-csv \
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

Exportiert offene Prüffälle im Zeitraum als CSV (Pflichtenheft §7.13).

```bash
admin --db <PFAD> --user-id <ID> reports export-csv-review-cases \
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
admin --db <PFAD> --user-id <ID> reports export-pdf-day \
  --date <YYYY-MM-DD>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--date` | YYYY-MM-DD | ja | Kalendertag des Berichts |

**Ausgabe:** `PDF: /var/exports/arbeitszeit/bericht_tag_2026-07-01_….pdf`

---

#### `reports export-pdf-week`

Erstellt einen Wochenbericht (ISO-Woche) als PDF.

```bash
admin --db <PFAD> --user-id <ID> reports export-pdf-week \
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
admin --db <PFAD> --user-id <ID> reports export-pdf-month \
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

Erstellt einen Mitarbeiterbericht für einen freien Zeitraum als PDF.

```bash
admin --db <PFAD> --user-id <ID> reports export-pdf-employee \
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

Listet alle Buchungen mit Status `OPEN`, optional im Zeitraum gefiltert.

```bash
admin --db <PFAD> --user-id <ID> reports open-bookings \
  [--from <YYYY-MM-DD> --to <YYYY-MM-DD>] \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--from` | YYYY-MM-DD | nein | Beginn des Zeitraums |
| `--to` | YYYY-MM-DD | nein | Ende des Zeitraums |
| `--employee-id` | int | nein | Nur für diesen Mitarbeiter |

**Hinweis:** Werden mehr als 50 Einträge ohne Zeitraumfilter gefunden, erscheint
ein Hinweis auf stderr, `--from`/`--to` zu verwenden.

**Ausgabe:**

```text
Offene Buchungen (Status OPEN) — alle:
    ID  Mitarbeiter               Art           Zeitpunkt                Status
---------------------------------------------------------------------------------
    47  Maria Mustermann          COME          2026-07-01T08:05:00Z     OPEN

1 Buchung(en).
```

---

#### `reports warn-cases`

Listet Buchungen mit Status `WARN` oder `NEEDS_REVIEW` im Zeitraum.

```bash
admin --db <PFAD> --user-id <ID> reports warn-cases \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--from` | YYYY-MM-DD | ja | Beginn |
| `--to` | YYYY-MM-DD | ja | Ende |
| `--employee-id` | int | nein | Filter |

**Ausgabe:** Tabelle wie `open-bookings`, gefiltert nach Warenstatus.

---

#### `reports corrections`

Listet Buchungskorrekturen im Zeitraum.

```bash
admin --db <PFAD> --user-id <ID> reports corrections \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

**Ausgabe:**

```text
Buchungskorrekturen:
[12] Maria Mustermann (M001): COME @ 2026-07-01T08:00:00Z → COME @ 2026-07-01T08:05:00Z (Grund: Zeitstempel korrigiert)

1 Korrektur(en).
```

---

#### `reports supplements`

Listet Nachträge (Nachtragsbuchungen) im Zeitraum.

```bash
admin --db <PFAD> --user-id <ID> reports supplements \
  --from <YYYY-MM-DD> \
  --to <YYYY-MM-DD> \
  [--employee-id <MITARBEITER-ID>]
```

**Ausgabe:**

```text
Nachträge:
[8] Maria Mustermann (M001): GO @ 2026-07-01T17:00:00Z (APPROVED) — Vergessen zu stempeln

1 Nachtrag/Nachträge.
```

---

#### `reports open-review-cases`

Listet offene Prüffälle, optional im Zeitraum gefiltert.

```bash
admin --db <PFAD> --user-id <ID> reports open-review-cases \
  [--from <YYYY-MM-DD> --to <YYYY-MM-DD>] \
  [--employee-id <MITARBEITER-ID>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--from` | YYYY-MM-DD | nein | Beginn |
| `--to` | YYYY-MM-DD | nein | Ende |
| `--employee-id` | int | nein | Filter |

**Hinweis:** Wie `open-bookings` — Warnung bei >50 ungefilterten Einträgen.

**Ausgabe:**

```text
Offene Prüffälle — alle:
[3] Maria Mustermann (M001): POSSIBLE_BREAK_VIOLATION (WARN) — Mögliche Pausenverletzung §4 ArbZG

1 Prüffall/-fälle.
```

---

### system

Systemcheck und Backup.

---

#### `system check`

Führt einen Systemcheck durch und gibt den Status aller Prüfpunkte aus.

```bash
admin --db <PFAD> --user-id <ID> system check
```

**Rolle:** ADMIN, TECH (Prüfung in CLI via `require_admin_or_tech`)  
**Exit-Code:** `0` = alles OK, `1` = mindestens ein Check fehlgeschlagen  
**Ausgabe:**

```text
Systemcheck-Ergebnis:
  Gesamt: OK

  [OK  ] db_access: Datenbankzugriff OK
  [OK  ] config_keys: Alle Pflichtschlüssel vorhanden
  [OK  ] nas_reachability: NAS erreichbar
  [OK  ] fk_consistency: Fremdschlüsselkonsistenz OK
  [OK  ] ntp_sync: NTP aktiv und synchronisiert
  [OK  ] device_availability: Geräte verfügbar
```

---

#### `system backup`

Erstellt manuell ein Datenbank-Backup und synchronisiert optional auf den NAS.

```bash
admin --db <PFAD> --user-id <ID> system backup
```

**Rolle:** ADMIN, TECH (Prüfung in CLI via `require_admin_or_tech`)  
**Ausgabe (Erfolg, NAS aktiv):**

```text
Backup erstellt: /var/backups/arbeitszeit/arbeitszeit_20260701T120000Z.db
NAS-Synchronisation erfolgreich.
```

**Ausgabe (Erfolg, kein NAS):**

```text
Backup erstellt: /var/backups/arbeitszeit/arbeitszeit_20260701T120000Z.db
```

**Fehler:** Backup-Verzeichnis nicht konfiguriert → Exit 1;
NAS-Synchronisation fehlgeschlagen → Exit 1 (lokales Backup bereits erstellt)

---

### users

Benutzerkontenverwaltung. Schreibzugriffe erfordern `ADMIN`-Rolle;
Passwörter werden mit PBKDF2-HMAC-SHA256 (260.000 Iterationen, Zufallssalt)
gehasht. Klartextpasswörter werden nach der einmaligen Anzeige nirgends
gespeichert.

---

#### `users bootstrap`

Legt das erste Administratorkonto an. Schlägt fehl, wenn bereits ein
aktives Administratorkonto existiert.

```bash
admin --db <PFAD> users bootstrap \
  --username <BENUTZERNAME> \
  [--password <PASSWORT>]
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--username` | string | ja | Benutzername des ersten Administrators |
| `--password` | string | nein | Passwort (wird automatisch generiert wenn leer) |

**Rolle:** keine (`--user-id` nicht erforderlich)  
**Ausgabe:**

```text
Erstes Administratorkonto angelegt (ID 1).
Generiertes Passwort (einmalig sichtbar): xKj8!mP2nqR5
```

**Fehler:** Admin bereits vorhanden, Benutzername bereits vergeben → Exit 1

---

#### `users add`

Legt ein neues Benutzerkonto an.

```bash
admin --db <PFAD> --user-id <ID> users add \
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
| `--password` | string | nein | Passwort (automatisch generiert wenn leer) |

**Rolle:** ADMIN  
**Ausgabe:**

```text
Benutzerkonto angelegt (ID 2).
Generiertes Passwort (einmalig sichtbar): mN7$qZ3vLp9w
```

**Fehler:** Benutzername bereits vergeben → Exit 1

---

#### `users list`

Listet alle Benutzerkonten (ADMIN, REVIEWER, TECH) auf.

```bash
admin --db <PFAD> users list
```

**Rolle:** keine  
**Ausgabe:**

```text
  ID  Benutzername          Rolle       Status
----------------------------------------------------
   1  admin                 ADMIN       aktiv
   2  pruefer01             REVIEWER    aktiv
   3  technik               TECH        inaktiv
```

oder `Keine Benutzerkonten vorhanden.`

---

#### `users deactivate`

Deaktiviert ein Benutzerkonto.

```bash
admin --db <PFAD> --user-id <ID> users deactivate \
  --user-id <ZIEL-BENUTZER-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--user-id` | int | ja | ID des zu deaktivierenden Kontos |

**Rolle:** ADMIN  
**Ausgabe:** `Benutzerkonto 3 deaktiviert.`  
**Fehler:** ID nicht gefunden → Exit 1

---

#### `users reactivate`

Reaktiviert ein deaktiviertes Benutzerkonto.

```bash
admin --db <PFAD> --user-id <ID> users reactivate \
  --user-id <ZIEL-BENUTZER-ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--user-id` | int | ja | ID des zu reaktivierenden Kontos |

**Rolle:** ADMIN  
**Ausgabe:** `Benutzerkonto 3 reaktiviert.`  
**Fehler:** ID nicht gefunden → Exit 1

---

#### `users change-role`

Ändert die Rolle eines Benutzerkontos.

```bash
admin --db <PFAD> --user-id <ID> users change-role \
  --user-id <ZIEL-BENUTZER-ID> \
  --role <NEUE-ROLLE>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--user-id` | int | ja | ID des Benutzerkontos |
| `--role` | ADMIN\|REVIEWER\|TECH | ja | Neue Rolle |

**Rolle:** ADMIN  
**Ausgabe:** `Rolle von Benutzerkonto 2 geändert.`  
**Fehler:** ID nicht gefunden, ungültige Rolle → Exit 1

---

## Terminal-UI

Die Terminal-UI läuft dauerhaft am Buchungsgerät und verarbeitet RFID-Scans
und Numpad-Eingaben.

### Aufruf

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db <DATENBANKPFAD> \
  --numpad <GERÄTEPFAD> \
  --rfid <GERÄTEPFAD> \
  --terminal-id <ID>
```

| Argument | Typ | Pflicht | Beschreibung |
| --- | --- | --- | --- |
| `--db` | Pfad | ja | SQLite-Datenbankdatei |
| `--numpad` | Gerätepfad | ja | z.B. `/dev/input/event3` |
| `--rfid` | Gerätepfad | ja | z.B. `/dev/input/event4` |
| `--terminal-id` | int | ja | Eindeutige Terminal-ID |

### Buchungszyklus

1. Mitarbeiter drückt auf dem Numpad eine Taste (1–4):

   | Taste | Buchungstyp |
   |---|---|
   | `1` | Kommen |
   | `2` | Gehen |
   | `3` | Pause Beginn |
   | `4` | Pause Ende |

2. Mitarbeiter hält RFID-Karte an den Leser.
3. System verarbeitet die Buchung und gibt Feedback aus.

### Rückmeldungen

| Situation | Ausgabe |
| --- | --- |
| Buchung erfasst (Status OK oder OPEN) | `Buchung erfasst.` |
| Buchung erfasst (Status WARN) | `Buchung erfasst — Hinweis: Regelzeitabweichung festgestellt.` |
| Buchung erfasst (Status NEEDS_REVIEW) | `Buchung erfasst — Prüfpflicht: Manuelle Überprüfung erforderlich.` |
| Karte unbekannt | `Karte nicht erkannt.` |
| Karte deaktiviert | `Karte deaktiviert.` |
| Mitarbeiter inaktiv | `Mitarbeiter inaktiv.` |
| Falsche Buchungsreihenfolge | `Ungültige Buchungsreihenfolge.` |
| Offene Phase | `Offene Phase — bitte zuerst abschließen.` |
| Interner Fehler | `Interner Fehler — Betrieb wird fortgesetzt.` (stderr) |

### Beenden

`Ctrl+C` — sicheres Beenden ohne Datenverlust.

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

**Ausgabe:** Eine Zeile pro angewendeter Migration; Hinweis auf Ersteinrichtung
wenn `scripts/setup.py` noch nicht ausgeführt wurde.

---

### `scripts/setup.py`

Konfiguriert Backup- und Exportverzeichnis (idempotent — bereits gesetzte
Werte werden nicht überschrieben).

```bash
python scripts/setup.py \
  [--db <PFAD>] \
  [--backup-dir <PFAD>] \
  [--export-dir <PFAD>]
```

| Argument | Standard | Beschreibung |
| --- | --- | --- |
| `--db` | `arbeitszeit.db` | Datenbankdatei |
| `--backup-dir` | interaktiv | Verzeichnis für lokale Backups |
| `--export-dir` | interaktiv | Verzeichnis für Exporte und PDFs |

---

### `scripts/backup.py`

Erstellt ein lokales Backup und synchronisiert optional auf den NAS.

```bash
python scripts/backup.py \
  [--db <PFAD>] \
  [--backup-dir <PFAD>] \
  [--export-dir <PFAD>]
```

| Argument | Standard | Beschreibung |
| --- | --- | --- |
| `--db` | `arbeitszeit.db` | Quelldatenbank |
| `--backup-dir` | `backups/` | Backup-Zielverzeichnis |
| `--export-dir` | — | Exportverzeichnis (wird mitgesichert) |

**Ausgabe:**

```text
Backup: /var/backups/arbeitszeit/arbeitszeit_20260701T120000Z.db  (2097152 Bytes)
NAS-Sync: /mnt/nas/backups/arbeitszeit | deaktiviert
```

---

### `scripts/verify_hardware.py`

Interaktiver Hardware-Smoke-Test für Numpad und RFID-Leser. Gibt den
SHA-256-Hash einer gescannten Karte aus — dieser Hash wird für
`cards assign --uid-hash` benötigt.

```bash
python scripts/verify_hardware.py \
  [--numpad <GERÄTEPFAD> --rfid <GERÄTEPFAD>] \
  [--list] \
  [--skip-interactive]
```

| Argument | Beschreibung |
| --- | --- |
| `--numpad` | Numpad-Gerätepfad (z.B. `/dev/input/event3`) |
| `--rfid` | RFID-Lesegerätepfad (z.B. `/dev/input/event4`) |
| `--list` | Nur Gerätedateien auflisten, dann beenden |
| `--skip-interactive` | Hardwaretests überspringen |

**Wichtig:** `--numpad` und `--rfid` müssen immer **gemeinsam** angegeben werden — eines ohne das andere erzeugt einen Fehler. Werden beide weggelassen, startet eine interaktive Geräteauswahl.

**Exit-Codes:** `0` = alle Tests bestanden, `1` = mindestens ein Test fehlgeschlagen,
`2` = evdev nicht installiert

**Wichtig:** Der angezeigte SHA-256-Hash (`wie in DB gespeichert`) ist der Wert,
der bei `cards assign --uid-hash` angegeben werden muss.

---

### `scripts/show_config.py`

Zeigt die aktuellen Systemkonfigurationswerte an.

```bash
python scripts/show_config.py \
  --db <PFAD> \
  [--all-versions] \
  [--json]
```

| Argument | Beschreibung |
| --- | --- |
| `--db` | Datenbankdatei (Pflicht) |
| `--all-versions` | Alle Versionen anzeigen (nicht nur aktuelle) |
| `--json` | JSON-Ausgabe statt Tabelle |

**Ausgabe (Tabelle):**

```text
Schlüssel                Wert                             Ver  Herkunft    Geändert am
────────────────────────────────────────────────────────────────────────────────────────
backup.backup_dir        /var/backups/arbeitszeit         1    MIGRATION   2026-07-01T12:00
export.export_dir        /var/exports/arbeitszeit         1    MIGRATION   2026-07-01T12:00
4 Eintrag/Einträge
```

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
| `users bootstrap` | keine (Sonderfall) | Use Case (kein Admin vorhanden?) |
| `users add` | ADMIN | Use Case |
| `users list` | keine | — |
| `users deactivate` | ADMIN | Use Case |
| `users reactivate` | ADMIN | Use Case |
| `users change-role` | ADMIN | Use Case |
| Terminal-UI | keine (RFID-Karte) | Use Case |
