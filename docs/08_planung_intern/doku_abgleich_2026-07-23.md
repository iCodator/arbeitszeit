# Dokumentationsabgleich: Quellcode vs. Anwenderdokumentation

**Stand:** 2026-07-23
**Grundlage:** Quellcode in `src/arbeitszeit/presentation/admin_cli/` und
`src/arbeitszeit/presentation/terminal_ui/` — vollständig gelesen.
Verglichene Dokumente: `befehlsreferenz.md`, `installationsanleitung.md`, `handbuch.md`.

---

## 1. Befehlsreferenz (`docs/03_installation_technik/befehlsreferenz.md`)

### 1.1 Fehlende Domain `audit` — kritisch

Die Domain `audit` ist in `admin_cli/main.py` vollständig registriert und
wird in `admin_cli/audit.py` implementiert. Sie fehlt **vollständig** in der
Befehlsreferenz.

**Tatsächlich vorhandene Befehle:**

| Befehl | Argumente | Rolle |
| --- | --- | --- |
| `audit open-shifts` | `--days N` (optional, Standard: 30) | ADMIN, REVIEWER |
| `audit verify-chain` | keine CLI-Argumente; benötigt `AUDIT_HMAC_KEY` (Umgebungsvariable) | ADMIN, REVIEWER |

`audit open-shifts` listet aus dem Audit-Log erkannte offene Vortagsschichten.
`audit verify-chain` prüft die HMAC-SHA256-Kettenhashes aller Audit-Einträge;
bricht mit Exit-Code 1 ab, wenn Einträge korrumpiert sind; bricht mit Exit-Code 1
ab, wenn `AUDIT_HMAC_KEY` nicht gesetzt ist.

**Folge:** Die Rollenübersicht am Ende der Befehlsreferenz enthält ebenfalls
keine Zeilen für diese beiden Befehle.

### 1.2 Fehlende globale Option `--admin-password` — mittel

`admin_cli/main.py` registriert:

```python
parser.add_argument(
    "--admin-password",
    default=None,
    metavar="PASSWORT",
    help="Admin-Passwort (Standard: interaktive Eingabe via getpass)",
)
```

Die Tabelle „Globale optionale Argumente" in der Befehlsreferenz führt
`--config`, `--db` und `--user-id`, aber nicht `--admin-password`. Die Option
ist für skriptgesteuerten (nicht-interaktiven) Betrieb relevant.

### 1.3 Versionswiderspruch im Dokument — mittel

Der Dokumentkopf enthält `**Version:** 1.7`, der Versionsvermerk am Ende des
Dokuments enthält:

> **Vorversion:** 1.5
> **Neue Version:** 1.6

Die Versionsvermerk-Sektion wurde nicht auf 1.7 aktualisiert, obwohl der
Kopf bereits 1.7 trägt. Änderungen, die den Sprung auf 1.7 begründen,
sind nicht festgehalten.

### 1.4 Passwortausgabe auf stderr undokumentiert — gering

`users add` und `users bootstrap` schreiben das generierte Passwort
(falls kein `--password` angegeben wurde) auf `sys.stderr`, nicht auf stdout:

```python
# user_accounts.py, Zeile 77
print(f"Generiertes Passwort (einmalig sichtbar): {password}", file=sys.stderr)
```

Die Befehlsreferenz zeigt die Passwortausgabe als normale Ausgabe ohne
Hinweis auf stderr. Das ist bei Skripten relevant, die stdout und stderr
getrennt auswerten.

### 1.5 Rollenübersicht unvollständig — gering

Die Rollenübersicht endet nach `users change-role`. Die Befehle
`audit open-shifts` und `audit verify-chain` fehlen (Konsequenz aus 1.1).

---

## 2. Installationsanleitung (`docs/03_installation_technik/installationsanleitung.md`)

### 2.1 `--numpad` existiert nicht in `terminal_ui` — kritisch

Schritt 15 der Installationsanleitung zeigt:

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db arbeitszeit.db \
  --numpad "USB Numpad" \
  --rfid "HID 1234:5678" \
  --terminal-id 1
```

`terminal_ui/main.py` registriert folgende CLI-Argumente:

```python
parser.add_argument("--config", ...)
parser.add_argument("--db", ...)
parser.add_argument("--rfid", ...)
parser.add_argument("--terminal-id", ...)
```

**`--numpad` ist nicht registriert.** Der Aufruf würde mit einem Fehler
von `argparse` scheitern.

Ebenfalls falsch ist die Aussage in Schritt 15:

> „Die Terminal-UI liest dann `database.path`, `terminal.numpad`,
> `terminal.rfid` und `terminal.id` aus der Konfiguration."

`terminal_ui/main.py` liest aus der Konfiguration:
`app_config.database.path`, `app_config.terminal.rfid`,
`app_config.terminal.id`. Der Schlüssel `terminal.numpad` wird nie
gelesen. Das Numpad-Konzept (Tasteneingaben 1–4) ist in der terminal_ui
nicht vorhanden — die Terminal-UI arbeitet ausschließlich per RFID;
der Buchungstyp wird positionsbasiert durch die Domänenlogik abgeleitet.

### 2.2 Fehlender Abgleich `verify_hardware.py --numpad` mit Befehlsreferenz — gering

Schritt 10 der Installationsanleitung zeigt:

```bash
python scripts/verify_hardware.py \
  --numpad /dev/input/event3 \
  --rfid /dev/input/event4
```

Die Befehlsreferenz führt `--numpad` für `scripts/verify_hardware.py`
nur als Prosahinweis auf:
„Das Skript enthält zusätzlich eine Numpad-Testfunktion (`--numpad`)
für Diagnosezwecke", listet es aber nicht in der Argumente-Tabelle
des Skripts. Die Quellen von `scripts/verify_hardware.py` wurden in
dieser Analyse nicht gelesen; die Inkonsistenz zwischen den beiden
Dokumenten bleibt aber bestehen.

---

## 3. Handbuch (`docs/02_anwender/handbuch.md`)

### 3.1 Domain `audit` fehlt — mittel

Die Befehle `audit open-shifts` und `audit verify-chain` sind im Handbuch
nicht erwähnt. Das Handbuch richtet sich bewusst an Praxispersonal ohne
IT-Hintergrund, dennoch wäre zumindest ein kurzer Verweis sinnvoll:
`audit verify-chain` ist eine Integritätsprüfung, die Administratoren
bei Verdacht auf Datenmanipulation ausführen würden.

### 3.2 Exit-Code von `scripts/verify_hardware.py` weicht von Befehlsreferenz ab — mittel

Handbuch Kapitel 9.4:

> Exit-Codes: 0 = alles in Ordnung, 1 = Fehler, **2 = Gerät nicht gefunden.**

Befehlsreferenz, Abschnitt `scripts/verify_hardware.py`:

> Exit-Codes: `0` = alle Tests bestanden, `1` = mindestens ein Test
> fehlgeschlagen, **`2` = `evdev` nicht installiert**

Die Bedeutung von Exit-Code 2 ist in beiden Dokumenten verschieden.
Da die Befehlsreferenz das dedizierte technische Referenzdokument ist,
ist dort die korrekte Angabe zu erwarten. Das Handbuch enthält
wahrscheinlich eine veraltete oder fehlerhafte Beschreibung.

### 3.3 `--admin-password` fehlt — gering

Das globale Argument `--admin-password` ist nicht dokumentiert.
Für einen Administrator, der Admin-CLI-Aufrufe per Skript automatisiert,
ist diese Option relevant.

### 3.4 Terminal-Aufruf mit teilweise redundantem `--db` — gering

Kapitel 4.1 zeigt unter „config.toml vollständig ausgefüllt":

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
  --db /pfad/zur/datenbank.db
```

Wenn `config.toml` wirklich vollständig ist, enthält sie auch
`[database] path`, womit `--db` am CLI ebenfalls entbehrlich wäre.
Der Beispielaufruf ist nicht falsch, kann aber verwirren.

---

## 4. Handlungsvorschläge

### Priorität 1 — Sofort beheben

**A) `audit`-Domain in Befehlsreferenz ergänzen.**
Einen neuen Abschnitt `### audit` anlegen mit:

- `audit open-shifts`: Syntax, `--days N` (Standard 30), Ausgabeformat, Rolle.
- `audit verify-chain`: Syntax, Umgebungsvariable `AUDIT_HMAC_KEY` (Pflicht),
  Exit-Codes (0 = OK, 1 = Kettenfehler oder Key fehlt), Rolle.

Die Rollenübersicht um beide Befehle ergänzen.

**B) `--numpad` aus terminal_ui-Aufruf in Installationsanleitung entfernen.**
Schritt 15 korrigieren: `--numpad "USB Numpad"` entfernen,
`terminal.numpad` aus der config.toml-Beschreibung streichen.
Der Buchungsbetrieb läuft ausschließlich per RFID; die Tasteneingabe
(Numpad) ist kein Bestandteil der terminal_ui.

### Priorität 2 — Zeitnah beheben

**C) `--admin-password` in Befehlsreferenz aufnehmen.**
In der Tabelle „Globale optionale Argumente" einen Eintrag hinzufügen:

| `--admin-password PASSWORT` | Admin-Passwort; Standard: interaktive Eingabe via `getpass` |

**D) Versionsvermerk in Befehlsreferenz aktualisieren.**
Den Versionsvermerk auf Version 1.7 setzen und die Änderungen seit 1.6
beschreiben (mindestens: `audit`-Domain hinzugefügt, `--admin-password`
dokumentiert).

**E) Exit-Code 2 für `scripts/verify_hardware.py` vereinheitlichen.**
Entweder Handbuch oder Befehlsreferenz korrigieren, sodass beide denselben
Wert für Exit-Code 2 nennen. Dazu `scripts/verify_hardware.py` lesen und
den tatsächlichen Wert feststellen.

### Priorität 3 — Bei nächster Revision einarbeiten

**F) Passwortausgabe auf stderr in Befehlsreferenz kennzeichnen.**
Bei `users add` und `users bootstrap` ergänzen, dass das generierte
Passwort auf stderr ausgegeben wird, z. B.:

> `Generiertes Passwort (einmalig sichtbar): <passwort>` (stderr)

**G) `audit`-Domain im Handbuch erwähnen.**
In Kapitel 9 (System-Wartung) einen kurzen Abschnitt 9.X hinzufügen,
der `audit open-shifts` und `audit verify-chain` als
Werkzeuge für Integritätsprüfung und offene Schichten benennt.

**H) `--numpad` für `verify_hardware.py` in Befehlsreferenz vollständig dokumentieren.**
Entweder in die Argumente-Tabelle aufnehmen (falls vorhanden) oder den
Prosahinweis entfernen.
