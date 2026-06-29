# Installationsanleitung – arbeitszeit v2.0

**Version:** 2.0  
**Stand:** Juni 2026  
**Betrifft:** Paket `arbeitszeit` · Python `>=3.14,<3.15` · Linux Mint / Lubuntu · SQLite

> ⚠️ **Hinweis:** Diese Anleitung ersetzt vollständig die ältere Installationsanleitung v1.0. Inhalte der v1.0 wurden nicht übernommen. Alle Schritte basieren ausschließlich auf dem tatsächlichen Inhalt des Repositories (Dateien, Skripte, Quellcode).

---

## 1. Ziel und kurzer Überblick

Diese Anleitung beschreibt die vollständige Erstinstallation des lokalen Zeiterfassungssystems `arbeitszeit` auf einem Linux-Mint- oder Lubuntu-Rechner. Das System dient der rechtlich nachvollziehbaren Arbeitszeiterfassung in einer Zahnarztpraxis.

**Kernbestandteile des Systems:**

- **SQLite-Datenbank** – einzige Datenquelle, keine Cloud-Anbindung
- **RFID-Reader** – wird als USB-HID-Gerät (Tastatur-Emulation) betrieben
- **USB-Numpad** – zur Buchungsauswahl (Tasten 1–4)
- **Terminal-UI** – operativer Buchungsbetrieb (Endlosschleife)
- **Admin-CLI** – Verwaltung von Mitarbeitern, Konten, Berichten und System

**Gesamtablauf in Kurzform:**

```
Systempakete → Repository → Venv → pip install → init_db.py → setup.py
→ ADMIN (Bootstrap) → REVIEWER/TECH anlegen → EMPLOYEE anlegen → Funktionstest → Starten
```

---

## 2. Voraussetzungen

### 2.1 Betriebssystem

- Linux Mint oder Lubuntu (aktuelle LTS-Version empfohlen)
- Internetzugang für den Installationsvorgang
- Benutzer mit `sudo`-Berechtigung

### 2.2 Python-Version

Das Repository schreibt in `pyproject.toml` die Version `>=3.14,<3.15` vor. Stellen Sie sicher, dass genau diese Python-Version auf dem System vorhanden ist.

> ⚠️ **Wichtiger Hinweis:** Python 3.14 ist in den Standard-Paketquellen aktueller Linux-Mint- und Lubuntu-LTS-Versionen **nicht enthalten**. Es muss manuell installiert werden – entweder über das `deadsnakes`-PPA oder über `pyenv`.

**Option A – deadsnakes-PPA (einfacher):**

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.14 python3.14-venv python3.14-dev
```

**Option B – pyenv (empfohlen für Entwickler):**

Das Repository enthält eine Datei `.python-version` mit dem Wert `3.14`. Wenn `pyenv` installiert ist, erkennt es diese Datei automatisch und verwendet die passende Version.

```bash
pyenv install 3.14
```

**Prüfschritt – korrekte Version vorhanden?**

```bash
python3.14 --version
```

Wird `Python 3.14.x` ausgegeben, ist die Version korrekt installiert.

> ⚠️ **Hinweis:** Im Projektkontext wird gelegentlich „Python 3.11" genannt. Maßgeblich für die Installation ist ausschließlich die Angabe in `pyproject.toml`. Prüfen Sie die installierte Version vor dem Fortfahren.

### 2.3 Git

Git wird zum Herunterladen des Repositories benötigt:

```bash
git --version
```

Ist Git nicht installiert:

```bash
sudo apt install -y git
```

### 2.4 Hardware

- RFID-Reader als USB-HID-Lesegerät (erscheint unter `/dev/input/event*`)
- USB-Numpad (ebenfalls unter `/dev/input/event*`)
- Schreibrechte auf die entsprechenden Gerätedateien für den ausführenden Benutzer

---

## 3. Zusätzliche Systempakete installieren

Einige Python-Pakete (insbesondere `evdev`) sind native Erweiterungen und werden beim `pip install` aus dem Quellcode kompiliert. Dafür benötigt das System einen C-Compiler und passende Kernel-Header. Ohne diese Pakete bricht der `pip install`-Schritt mit einem Compiler-Fehler ab.

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

**Was wird hier installiert?**

| Paket | Bedeutung |
|---|---|
| `build-essential` | Compiler-Werkzeuge, insbesondere `gcc` und `make` |
| `linux-headers-$(uname -r)` | Kernel-Header passend zum aktuell laufenden Kernel (nötig für evdev) |
| `python3-dev` | Python-Entwicklerdateien (u.a. `Python.h`), nötig zum Kompilieren nativer Erweiterungen |

**Prüfschritt – Compiler vorhanden?**

```bash
gcc --version
```

Wird eine Versionsnummer ausgegeben (z.B. `gcc (Ubuntu 13.x) 13.x.x`), ist der Compiler korrekt installiert. Erscheint stattdessen `command not found`, war die Installation nicht erfolgreich – prüfen Sie die Ausgabe von `apt` auf Fehlermeldungen.

### 3.1 Diagnosewerkzeug für Eingabegeräte installieren (optional, aber empfohlen)

Für die Ermittlung und Prüfung von USB-Numpad und RFID-Reader wird das Werkzeug `evtest` empfohlen. Es zeigt live die Events von Linux-Eingabegeräten unter `/dev/input/event*` an und hilft dabei, die korrekten Gerätedateien für den späteren Start der Terminal-UI zu identifizieren.

Installation:

```bash
sudo apt install -y evtest
```

Beispielaufruf:

```bash
sudo evtest
```

`evtest` listet die verfügbaren Eingabegeräte auf und erlaubt anschließend die Auswahl eines konkreten Geräts. Beim Drücken der Numpad-Tasten bzw. beim Vorhalten einer RFID-Karte kann geprüft werden, ob das jeweilige Gerät korrekt erkannt wird und auf welchem `/dev/input/eventX`-Pfad es verfügbar ist.

Alternativ können die Gerätedateien auch ohne `evtest` über die stabileren Symlinks unter `/dev/input/by-id/` ermittelt werden:

```bash
ls -la /dev/input/by-id/
```

Für den operativen Start der Anwendung sind anschließend die dort ermittelten Gerätepfade an die Parameter `--numpad` und `--rfid` zu übergeben.

---

## 4. Repository herunterladen

Laden Sie den Quellcode des Projekts mit Git auf Ihr System:

```bash
git clone https://github.com/iCodator/arbeitszeit.git
```

Nach dem Klonen liegt ein neues Verzeichnis `arbeitszeit/` im aktuellen Ordner.

**Erfolgskontrolle:**

```bash
ls arbeitszeit/
```

Sie sollten u.a. folgende Einträge sehen: `pyproject.toml`, `scripts/`, `src/`, `tests/`, `README.md`.

---

## 5. In das Projektverzeichnis wechseln

Alle weiteren Befehle müssen **innerhalb** des Projektverzeichnisses ausgeführt werden:

```bash
cd arbeitszeit
```

---

## 6. Virtuelle Python-Umgebung erstellen und aktivieren

Eine virtuelle Umgebung (kurz: „venv") ist ein abgeschlossener Python-Bereich, in dem die Pakete des Projekts installiert werden – unabhängig vom Rest des Systems. Das verhindert Konflikte mit anderen Python-Projekten.

**Umgebung erstellen:**

Wenn Python 3.14 über das deadsnakes-PPA installiert wurde, verwenden Sie explizit den Versionspfad:

```bash
python3.14 -m venv .venv
```

Wenn `pyenv` verwendet wird und die korrekte Version aktiv ist, genügt:

```bash
python3 -m venv .venv
```

Dies erzeugt einen neuen Ordner `.venv/` im Projektverzeichnis.

**Umgebung aktivieren:**

```bash
source .venv/bin/activate
```

Nach der Aktivierung erscheint `(.venv)` am Anfang der Eingabeaufforderung. Das zeigt an, dass die virtuelle Umgebung aktiv ist. Alle folgenden `python`- und `pip`-Befehle laufen jetzt in dieser Umgebung.

> 💡 **Tipp:** Die virtuelle Umgebung muss nach jedem Neustart des Terminals erneut aktiviert werden (`source .venv/bin/activate`). Sie wird **nicht** automatisch aktiv.

---

## 7. Python-Abhängigkeiten installieren

Installieren Sie das Paket `arbeitszeit` samt aller Abhängigkeiten. Der Schalter `-e` steht für „editable" – Änderungen im `src/`-Verzeichnis werden sofort wirksam, ohne neu installieren zu müssen. `[dev]` schließt zusätzliche Entwicklungswerkzeuge (pytest, ruff usw.) ein.

```bash
pip install -e .[dev]
```

**Was wird installiert?**

Laut `pyproject.toml` sind das folgende Kernpakete:

- `evdev>=1.7` – Zugriff auf Linux-Eingabegeräte (RFID, Numpad); erfordert den Compiler aus Schritt 3
- `reportlab>=4.0` – PDF-Berichtserzeugung

Zusätzlich als Entwicklungsabhängigkeiten (`[dev]`):

- `pytest>=8.0`, `pytest-cov>=5.0` – Testausführung
- `pypdf>=4.0` – PDF-Prüfung in Tests
- `ruff>=0.6` – statische Code-Analyse
- `import-linter>=2.0` – Prüfung der Architektur-Schichtgrenzen (Clean Architecture)

**Erfolgskontrolle:**

```bash
pip show arbeitszeit
```

Die Ausgabe sollte den Namen `arbeitszeit`, die Version `0.1.0` und den Speicherort im `src/`-Verzeichnis anzeigen.

> ⚠️ **Hinweis:** Schlägt die Installation mit einer Meldung wie `gcc: command not found` oder `Python.h: No such file or directory` fehl, wurden die Systempakete aus Schritt 3 nicht korrekt installiert. Führen Sie Schritt 3 erneut aus, bevor Sie `pip install` wiederholen.

---

## 8. Datenbank initialisieren

`scripts/init_db.py` legt die SQLite-Datenbankdatei an und führt alle vorbereiteten Migrationen durch. Ohne diesen Schritt existieren weder Tabellen noch Konfigurationseinträge – `setup.py` würde in diesem Fall mit einem Fehler abbrechen, da es eine bereits vorhandene Datenbank erwartet.

```bash
python scripts/init_db.py
```

**Was passiert hier?**

Das Skript öffnet (bzw. erzeugt) die Datei `arbeitszeit.db` im aktuellen Verzeichnis, führt alle vorhandenen SQL-Migrationen aus und prüft anschließend, ob die Ersteinrichtung noch aussteht.

Die Migrationsversionen werden als vierstellige Zahlen ausgegeben, entsprechend den Dateinamen im Verzeichnis `migrations/` (z.B. `0001_schema.sql` → Version `0001`).

**Typische Ausgabe nach erfolgreicher Initialisierung:**

```
Migration 0001 angewendet.
Migration 0002 angewendet.
Migration 0003 angewendet.
Migration 0004 angewendet.
Migration 0005 angewendet.
Migration 0006 angewendet.
⚠  Ersteinrichtung noch erforderlich:
   python scripts/setup.py --db arbeitszeit.db
```

Sind bereits alle Migrationen eingespielt (z.B. bei einer Wiederholung), lautet die Ausgabe:

```
Keine neuen Migrationen.
⚠  Ersteinrichtung noch erforderlich:
   python scripts/setup.py --db arbeitszeit.db
```

**Abweichender Datenbankpfad (optional):**

```bash
python scripts/init_db.py --db /pfad/zur/arbeitszeit.db
```

---

## 9. Ersteinrichtung durchführen

`scripts/setup.py` setzt systemspezifische Konfigurationseinträge in der Datenbank: das Backup-Verzeichnis (`backup.backup_dir`) und das Exportverzeichnis für CSV/PDF (`export.export_dir`). Das Skript ist **idempotent** – bereits konfigurierte Einträge werden übersprungen, nie überschrieben.

> ⚠️ **Hinweis:** `setup.py` prüft beim Start, ob die Datenbankdatei existiert. Ist das nicht der Fall, bricht es mit der Meldung `Fehler: Datenbank nicht gefunden` ab und weist darauf hin, zuerst `init_db.py` auszuführen. Die Reihenfolge **init_db.py → setup.py** ist daher zwingend einzuhalten.

### 9.1 Interaktiver Modus

Ohne zusätzliche Parameter fragt das Skript die Pfade interaktiv ab:

```bash
python scripts/setup.py --db arbeitszeit.db
```

Beispielhafte Eingabeaufforderung:

```
Ersteinrichtung arbeitszeit
========================================
  Backup-Verzeichnis (absoluter Pfad): /var/backups/arbeitszeit
  Exportverzeichnis für CSV/PDF (absoluter Pfad): /var/exports/arbeitszeit
========================================
Ersteinrichtung abgeschlossen. System betriebsbereit.
```

Das Skript legt die angegebenen Verzeichnisse automatisch an, falls sie noch nicht existieren.

### 9.2 Nicht-interaktiver Modus

Für automatisierte Einrichtungen können die Pfade direkt als Parameter übergeben werden:

```bash
python scripts/setup.py --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
    --export-dir /var/exports/arbeitszeit
```

**Erfolgskontrolle:** Das Skript gibt am Ende aus: `Ersteinrichtung abgeschlossen. System betriebsbereit.`

---

## 10. Ersten ADMIN anlegen (Bootstrap)

Nach Datenbankinitialisierung und Ersteinrichtung muss ein erstes Administratorkonto angelegt werden. Dieser Schritt heißt „Bootstrap" und ist nur möglich, solange **kein** aktives ADMIN-Konto in der Datenbank existiert. Der Bootstrap-Befehl benötigt – anders als alle anderen Admin-Befehle – keine vorherige Benutzer-ID, weil es noch keinen Admin gibt, der den Vorgang autorisieren könnte.

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    users bootstrap \
    --username adminname
```

Wird kein `--password` angegeben, generiert das System ein sicheres Zufallspasswort und zeigt es **einmalig** in der Ausgabe an:

```
Erstes Administratorkonto angelegt (ID 1).
Generiertes Passwort (einmalig sichtbar): xY3-mNpQ8rTz
```

> ⚠️ **Hinweis:** Notieren Sie das angezeigte Passwort sofort sicher. Es wird nicht erneut angezeigt und ist nicht in der Datenbank im Klartext gespeichert.

Alternativ mit selbst gewähltem Passwort:

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    users bootstrap \
    --username adminname \
    --password IhrSicheresPasswort
```

**Erfolgskontrolle – ADMIN-Konto prüfen:**

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    users list
```

> 💡 **Hinweis:** Der Parameter `--db` ist bei der Admin-CLI **immer Pflicht** – es gibt keinen Standardwert. Bei `users list` wird keine `--user-id` benötigt, da es sich um eine lesende Operation ohne Rollenprüfung handelt.

Das Konto sollte mit Rolle `ADMIN` und Status `aktiv` erscheinen.

---

## 11. REVIEWER und zusätzliche TECH-Konten anlegen

Weitere Benutzerkonten mit den Rollen `REVIEWER` oder `TECH` können erst nach dem Bootstrap angelegt werden, da jede schreibende Operation die ADMIN-Rolle voraussetzt. Die Benutzer-ID des Admins (aus Schritt 10, z.B. `1`) muss dabei angegeben werden.

**Zulässige Rollen für Benutzerkonten:** `ADMIN`, `REVIEWER`, `TECH`

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users add \
    --username pruefer01 \
    --role REVIEWER
```

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    users add \
    --username technik01 \
    --role TECH
```

Auch hier gilt: Wird kein `--password` angegeben, wird ein Zufallspasswort generiert und einmalig angezeigt.

> 💡 **Tipp:** Die Benutzer-ID des ausführenden Admins kann statt `--user-id` auch über die Umgebungsvariable `ADMIN_USER_ID` gesetzt werden:
> ```bash
> export ADMIN_USER_ID=1
> ```

---

## 12. EMPLOYEE als Mitarbeiter-Datensatz anlegen

> ⚠️ **Wichtiger Unterschied:** `EMPLOYEE` ist **kein** Benutzerkonto wie `ADMIN`, `REVIEWER` oder `TECH`. Ein Mitarbeiter wird als eigenständiger Datensatz in der Tabelle `employees` angelegt und bucht seine Arbeitszeit ausschließlich über den RFID-Reader – nicht über ein Login. Der Anlege-Weg über `users add` gilt für `EMPLOYEE` **nicht** und ist technisch auch nicht möglich (erlaubte Rollen dort sind nur `ADMIN`, `REVIEWER`, `TECH`).

### 12.1 Mitarbeiter-Datensatz anlegen

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    employees add \
    --personnel-no M001 \
    --first-name Maria \
    --last-name Mustermann
```

Die Ausgabe bestätigt die neue interne ID, z.B.: `Mitarbeiter angelegt (ID 1).`

### 12.2 RFID-Karte dem Mitarbeiter zuweisen

Damit ein Mitarbeiter buchen kann, muss seine RFID-Karte in der Datenbank registriert werden. Der `--uid-hash` ist der SHA-256-Hash der Roh-UID der Karte, der vom System beim Einlesen automatisch berechnet wird (implementiert in `arbeitszeit/infrastructure/hardware/evdev_reader.py`).

**Empfohlener Weg zur Ermittlung des UID-Hashs:**

Da der Hash nicht ohne weiteres vorab bekannt ist, empfiehlt sich folgender Ablauf:
1. Terminal-UI starten (Schritt 14.1)
2. RFID-Karte einlesen – die Karte wird als „nicht erkannt" zurückgewiesen, da noch nicht registriert
3. Den dabei erzeugten Eintrag in der Tabelle `rfid_cards` (Spalte `uid_hash`) oder im `audit_log` / `system_events` einsehen, um den Hash zu ermitteln
4. Den ermittelten Hash anschließend mit `cards assign` registrieren

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    cards assign \
    --employee-id 1 \
    --uid-hash <SHA256-HASH-DER-KARTE>
```

### 12.3 Mitarbeiterliste prüfen

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    employees list
```

---

## 13. Funktionstest nach der Installation

Führen Sie nach der Einrichtung die automatisierten Tests durch, um sicherzustellen, dass das System korrekt installiert ist.

### 13.1 Gesamte Testsuite

```bash
pytest
```

### 13.2 Nur Migrationstests

Besonders relevant nach der Initialisierung:

```bash
pytest tests/test_migrations.py
```

### 13.3 Testsuite mit Abdeckungsbericht

```bash
pytest --cov=arbeitszeit
```

**Erfolgskontrolle:** Alle Tests sollten mit `passed` abschließen, keine `FAILED`-Zeilen erscheinen.

### 13.4 Systemcheck über Admin-CLI

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    system check
```

---

## 14. Anwendung starten

### 14.1 Terminal-UI (operativer Buchungsbetrieb)

Die Terminal-UI ist der Dauerbetriebsmodus für die Buchungserfassung. Sie läuft als Endlosschleife und wartet auf RFID- und Numpad-Eingaben. Vor dem Start wird automatisch ein Systemcheck durchgeführt.

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
    --db arbeitszeit.db \
    --numpad /dev/input/eventX \
    --rfid /dev/input/eventY \
    --terminal-id 1
```

**Parameter:**

| Parameter | Bedeutung |
|---|---|
| `--db` | Pfad zur SQLite-Datenbankdatei (Pflicht, kein Standardwert) |
| `--numpad` | Gerätedatei des USB-Numpads (z.B. `/dev/input/event3`) |
| `--rfid` | Gerätedatei des RFID-Readers (z.B. `/dev/input/event4`) |
| `--terminal-id` | Ganzzahlige ID dieses Terminals (z.B. `1`) |

> 💡 **Tipp:** Die korrekten Gerätedateien für Numpad und RFID-Reader ermitteln Sie mit:
> ```bash
> ls /dev/input/by-id/
> ```
> oder durch Beobachtung der Ausgabe von:
> ```bash
> sudo evtest
> ```

Die Anwendung beendet sich sauber bei `Strg+C` oder einem `SIGTERM`-Signal.

### 14.2 Admin-CLI

```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    --user-id 1 \
    <unterbefehl>
```

---

## 15. Backup manuell anstoßen

Das Backup-Skript sichert die SQLite-Datenbankdatei und kann optional Exportdateien (CSV/PDF) miteinbeziehen.

**Minimaler Aufruf** (Backup-Verzeichnis als Parameter, Standard wäre `backups/`):

```bash
python scripts/backup.py --db arbeitszeit.db --backup-dir /var/backups/arbeitszeit
```

**Erweiterter Aufruf** mit Exportverzeichnis (Exportdateien werden in `backup-dir/exports/` kopiert):

```bash
python scripts/backup.py \
    --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
    --export-dir /var/exports/arbeitszeit
```

**Parameter:**

| Parameter | Bedeutung | Standard |
|---|---|---|
| `--db` | Pfad zur Datenbankdatei | `arbeitszeit.db` |
| `--backup-dir` | Zielverzeichnis für Backups | `backups/` |
| `--export-dir` | Exportverzeichnis (CSV/PDF); wird in `backup-dir/exports/` kopiert | keiner |

Ein optionaler NAS-Sync wird über die system_config-Einträge `backup.nas_enabled` und `backup.nas_path` gesteuert (konfigurierbar über Admin-CLI).

---

## 16. Typische Fehler und Lösungen

### Fehler: Python 3.14 nicht gefunden

**Ursache:** Python 3.14 ist in den Standard-Paketquellen der verwendeten Linux-Distribution nicht enthalten.  
**Lösung:** Schritt 2.2 dieser Anleitung befolgen (deadsnakes-PPA oder pyenv).

---

### Fehler: `gcc: command not found` beim `pip install`

**Ursache:** Der C-Compiler ist nicht installiert. Nötig für `evdev`.  
**Lösung:**
```bash
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

---

### Fehler: `fatal error: Python.h: No such file or directory`

**Ursache:** Die Python-Entwicklerdateien fehlen.  
**Lösung:**
```bash
sudo apt install -y python3-dev
```

---

### Fehler: `Fehler: Datenbank nicht gefunden: arbeitszeit.db`

**Ursache:** `setup.py` wurde aufgerufen, bevor `init_db.py` ausgeführt wurde.  
**Lösung:** Führen Sie zuerst `init_db.py` aus:
```bash
python scripts/init_db.py
```

---

### Fehler: `Es existiert bereits ein aktives Administratorkonto. Bootstrap nicht möglich.`

**Ursache:** Der Bootstrap-Befehl wurde ein zweites Mal aufgerufen, obwohl bereits ein Admin existiert.  
**Lösung:** Keinen erneuten Bootstrap ausführen. Verwenden Sie stattdessen `users add --role ADMIN` mit einem bestehenden Admin.

---

### Fehler: `Fehler: Zugriff verweigert. Aktion erfordert ADMIN-Rolle.`

**Ursache:** Die angegebene `--user-id` gehört nicht zu einem aktiven ADMIN-Konto.  
**Lösung:** Prüfen Sie die Benutzer-ID:
```bash
python -m arbeitszeit.presentation.admin_cli.main \
    --db arbeitszeit.db \
    users list
```

---

### Fehler: `Fehler: Benutzername bereits vergeben.`

**Ursache:** Ein Benutzerkonto mit diesem Benutzernamen existiert bereits in der Datenbank.  
**Lösung:** Wählen Sie einen anderen Benutzernamen oder prüfen Sie die Benutzerliste.

---

### Fehler beim Starten der Terminal-UI: Gerätedatei nicht gefunden

**Ursache:** Der angegebene Pfad für `--numpad` oder `--rfid` existiert nicht oder gehört einem anderen Gerät.  
**Lösung:** Ermitteln Sie die aktuellen Gerätedateien:
```bash
ls /dev/input/by-id/
```

---

## 17. Kurzübersicht wichtiger Befehle

| Zweck | Befehl |
|---|---|
| Datenbank initialisieren | `python scripts/init_db.py` |
| Ersteinrichtung (interaktiv) | `python scripts/setup.py --db arbeitszeit.db` |
| Ersteinrichtung (nicht-interaktiv) | `python scripts/setup.py --db arbeitszeit.db --backup-dir /pfad --export-dir /pfad` |
| Ersten ADMIN anlegen | `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db users bootstrap --username adminname` |
| Benutzerkonto anlegen | `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 users add --username name --role REVIEWER` |
| Benutzerliste anzeigen | `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db users list` |
| Mitarbeiter anlegen | `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 employees add --personnel-no M001 --first-name V --last-name N` |
| Mitarbeiterliste anzeigen | `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 employees list` |
| RFID-Karte zuweisen | `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 cards assign --employee-id 1 --uid-hash <HASH>` |
| Systemcheck | `python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 system check` |
| Terminal-UI starten | `python -m arbeitszeit.presentation.terminal_ui.main --db arbeitszeit.db --numpad /dev/input/eventX --rfid /dev/input/eventY --terminal-id 1` |
| Backup manuell (einfach) | `python scripts/backup.py --db arbeitszeit.db --backup-dir /var/backups/arbeitszeit` |
| Backup manuell (mit Exports) | `python scripts/backup.py --db arbeitszeit.db --backup-dir /var/backups/arbeitszeit --export-dir /var/exports/arbeitszeit` |
| Tests ausführen | `pytest` |
| Nur Migrationstests | `pytest tests/test_migrations.py` |
| Tests mit Coverage | `pytest --cov=arbeitszeit` |

---

*Installationsanleitung arbeitszeit v2.0 · Erstellt Juni 2026 · Basis: Repository-Stand `iCodator/arbeitszeit`*
