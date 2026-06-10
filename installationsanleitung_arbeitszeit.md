# Installationsanleitung – Arbeitszeit

**Zeiterfassungssystem für die Zahnarztpraxis**

---

## Was ist „Arbeitszeit"?

„Arbeitszeit" ist ein lokales Computerprogramm zur Erfassung der Arbeitszeiten der Mitarbeiter in einer Zahnarztpraxis. Jeder Mitarbeiter hat eine RFID-Karte (ähnlich wie eine Schlüsselkarte) und kann damit am Terminal per Tastendruck ein- und ausbuchen. Das Programm läuft vollständig auf dem lokalen Rechner in der Praxis – keine Internetverbindung, kein Cloud-Dienst, keine externen Server. Alle Daten bleiben im Haus.

---

## Was wird benötigt?

Bevor die Installation beginnt, müssen folgende Voraussetzungen erfüllt sein:

**Hardware:**
- Ein Linux-Computer (z. B. ein kleiner PC oder ein Raspberry Pi)
- Ein USB-Numpad (die Zehnertastatur, die man extern einsteckt)
- Ein USB-RFID-Leser (liest die Mitarbeiterkarten)
- Optional: ein NAS-Laufwerk (Netzwerkspeicher) für automatische Datensicherungen

**Software:**
- Das Betriebssystem **Linux** muss bereits installiert sein
- **Python 3.14** muss installiert sein (genau diese Version – nicht neuer, nicht älter; siehe nächster Abschnitt)
- **Git** muss installiert sein (dient zum Herunterladen des Programms)
- Eine Internetverbindung ist nur für die einmalige Installation nötig

> **Hinweis:** Für erste Tests kann auch ohne die echte Hardware gearbeitet werden – das Programm enthält einen Simulator.

---

## Schritt 0 – Python 3.14 prüfen und installieren

Das Programm benötigt **exakt Python 3.14** – keine ältere und keine neuere Version. Da auf den meisten Linux-Systemen bereits eine andere Python-Version vorinstalliert ist, muss zuerst geprüft werden, was vorhanden ist.

### Python-Version prüfen

Öffne ein Terminal-Fenster und gib ein:

```bash
python3 --version
```

Die Ausgabe zeigt die installierte Version, z. B.:

```
Python 3.12.3
```

**Was bedeutet das?**

| Ausgabe | Bedeutung | Aktion nötig? |
|---|---|---|
| `Python 3.14.x` | Richtige Version vorhanden | ✅ Nein – weiter mit Schritt 1 |
| `Python 3.12.x` oder ähnlich | Falsche Version | ⚠️ Ja – Python 3.14 zusätzlich installieren |
| Fehlermeldung / nicht gefunden | Python fehlt komplett | ⚠️ Ja – Python 3.14 installieren |

> **Wichtig:** Die vorhandene Python-Version wird **nicht gelöscht** – sie bleibt erhalten und wird vom System weiterhin genutzt. Python 3.14 wird **zusätzlich** installiert.

---

### Python 3.14 installieren mit pyenv

Der einfachste Weg, eine zusätzliche Python-Version zu installieren, ist das Werkzeug **pyenv**. Es verwaltet mehrere Python-Versionen nebeneinander, ohne das System zu beeinflussen.

#### 0a – Abhängigkeiten installieren

Zuerst werden einige Hilfspakete benötigt, die Linux zum Bauen von Python braucht:

```bash
sudo apt update && sudo apt install -y \
    build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev \
    curl git libncursesw5-dev xz-utils tk-dev \
    libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

> Das Passwort für `sudo` wird abgefragt – das ist das normale Systempasswort.

**Was passiert hier?** Linux braucht diese Bausteine, um Python aus dem Quellcode zu kompilieren (also selbst zu „übersetzen"). Das ist einmalig nötig.

#### 0b – pyenv installieren

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```

Dann pyenv zum System bekannt machen. Folgende drei Zeilen in die Konfigurationsdatei der Shell eintragen:

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```

Anschließend die Konfiguration neu einlesen:

```bash
source ~/.bashrc
```

> **Was ist `.bashrc`?** Das ist eine versteckte Konfigurationsdatei, die beim Öffnen jedes Terminal-Fensters automatisch gelesen wird. Die drei `echo`-Befehle hängen einfach drei neue Zeilen ans Ende dieser Datei an.

#### 0c – Python 3.14 installieren

```bash
pyenv install 3.14.0
```

> Dieser Vorgang **dauert einige Minuten** (5–15 Minuten je nach Rechner), weil Python aus dem Quellcode gebaut wird. Das ist normal – einfach abwarten bis die Eingabeaufforderung wieder erscheint.

Prüfen, ob die Installation geklappt hat:

```bash
pyenv versions
```

Beispielausgabe:

```
* system (set by /home/benutzer/.pyenv/version)
  3.14.0
```

Das `*` zeigt die aktuell aktive Version. `system` ist die alte vorinstallierte Version, `3.14.0` ist die neu installierte.

#### 0d – Python 3.14 für das arbeitszeit-Projekt festlegen

Python 3.14 wird **nur im Projektordner** aktiviert – nicht systemweit. Das schützt andere Programme vor unerwünschten Änderungen.

Zuerst in den Projektordner wechseln (oder erst nach Schritt 1 zurückkommen):

```bash
cd arbeitszeit
pyenv local 3.14.0
```

Dieser Befehl legt eine kleine Datei (`.python-version`) im Projektordner an. Damit weiß pyenv: „In diesem Ordner immer Python 3.14 benutzen."

Zur Kontrolle:

```bash
python3 --version
```

Erwartete Ausgabe:

```
Python 3.14.0
```

✅ Wenn das steht, ist Python 3.14 korrekt eingerichtet.

---

## Schritt 1 – Programm herunterladen

Öffne ein Terminal-Fenster (die schwarze Eingabeaufforderung in Linux) und gib folgende Befehle ein. Nach jeder Zeile die Eingabe-Taste drücken.

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
```

**Was passiert hier?**
- `git clone` lädt das gesamte Programm aus dem Internet herunter und speichert es in einem Ordner namens `arbeitszeit`.
- `cd arbeitszeit` wechselt in diesen Ordner.

---

## Schritt 2 – Virtuelle Umgebung erstellen

Eine „virtuelle Umgebung" ist ein abgeschlossener Bereich auf dem Computer, in dem das Programm mit all seinen Hilfsbibliotheken installiert wird – ohne das restliche System zu beeinflussen.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Nach dem zweiten Befehl erscheint in der Eingabezeile der Zusatz `(.venv)` – das zeigt an, dass die virtuelle Umgebung aktiv ist.

> **Wichtig:** Immer wenn das Programm später gestartet oder verwaltet werden soll, muss zuerst dieser Befehl ausgeführt werden: `source .venv/bin/activate`

---

## Schritt 3 – Programm installieren

```bash
pip install -e ".[dev]"
```

Dieser Befehl installiert das Programm selbst sowie alle benötigten Hilfsprogramme automatisch. Je nach Internetgeschwindigkeit kann das 1–3 Minuten dauern. Am Ende erscheint eine Erfolgsmeldung.

---

## Schritt 4 – Datenbank einrichten

Das Programm speichert alle Zeitbuchungen in einer Datei (der „Datenbank"). Diese muss zuerst angelegt werden:

```bash
python scripts/init_db.py --db arbeitszeit.db
```

**Was passiert hier?** Es wird die Datei `arbeitszeit.db` erstellt. Diese Datei ist die zentrale Datenspeicher-Datei – sie sollte regelmäßig gesichert werden.

---

## Schritt 5 – Verzeichnisse konfigurieren

Einmalig müssen zwei Ordner festgelegt werden:
- Ein **Backup-Ordner**: Wohin werden die Datensicherungen gespeichert?
- Ein **Export-Ordner**: Wohin werden PDF- und CSV-Berichte gespeichert?

### Option A – Interaktiv (empfohlen für Einsteiger)

```bash
python scripts/setup.py --db arbeitszeit.db
```

Das Programm fragt dann der Reihe nach nach den Pfaden. Einfach eingeben, was man möchte, z. B.:
- Backup-Verzeichnis: `/var/backups/arbeitszeit`
- Export-Verzeichnis: `/var/exports/arbeitszeit`

### Option B – Alles auf einmal

```bash
python scripts/setup.py --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit \
    --export-dir /var/exports/arbeitszeit
```

---

## Schritt 6 – Terminal-Anzeige starten

Sobald das USB-Numpad und der RFID-Leser angeschlossen sind, kann das Terminal gestartet werden. Dazu müssen die Gerätepfade der Hardware bekannt sein (meist unter `/dev/input/by-id/` zu finden):

```bash
python -m arbeitszeit.presentation.terminal_ui.main \
    --db arbeitszeit.db \
    --numpad /dev/input/by-id/usb-numpad \
    --rfid   /dev/input/by-id/usb-rfid \
    --terminal-id 1
```

**Was passiert?** Das Terminal läuft als Dauerprogramm und wartet auf Kartenbuchungen. Es lässt sich sauber mit `Strg + C` beenden.

> **Tipp:** Den genauen Gerätepfad herausfinden mit: `ls /dev/input/by-id/`

---

## Schritt 7 – Verwaltung über die Admin-Oberfläche

Die Administration (Mitarbeiter anlegen, Berichte erstellen, Backups machen usw.) läuft über eine Text-Befehlsoberfläche. Grundstruktur:

```bash
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 <Befehl>
```

Die `1` steht für die ID des Admin-Benutzers. Wichtige Beispiele:

| Was soll gemacht werden? | Befehl |
|---|---|
| Alle Mitarbeiter anzeigen | `employees list` |
| Neuen Mitarbeiter anlegen | `employees add` |
| RFID-Karte zuweisen | `cards assign` |
| Systemcheck ausführen | `system check` |
| Manuelles Backup starten | `system backup` |
| Monatsbericht als PDF | `reports export-pdf-month` |

**Vollständiges Beispiel – Systemcheck:**

```bash
python -m arbeitszeit.presentation.admin_cli.main --db arbeitszeit.db --user-id 1 system check
```

---

## Datensicherung (Backup)

Die Datenbank sollte regelmäßig gesichert werden. Das geht manuell mit:

```bash
python scripts/backup.py \
    --db arbeitszeit.db \
    --backup-dir /var/backups/arbeitszeit
```

Für automatische tägliche Backups kann dieser Befehl als **cron-Job** oder **systemd-Timer** eingerichtet werden. Falls ein NAS vorhanden ist, kann der Backup-Pfad auf einen Netzwerkordner gesetzt werden – das System spiegelt die Daten dort automatisch hin.

---

## Häufige Fragen

**Muss immer das Terminal offen bleiben?**
Im produktiven Betrieb läuft das Terminalprogramm als Dauerprozess. Es empfiehlt sich, es als systemd-Dienst einzurichten, damit es nach einem Neustart automatisch startet.

**Was ist, wenn ich die Hardware noch nicht habe?**
Das Programm enthält einen Hardware-Simulator für Tests. Die Installation funktioniert genauso – einfach ohne die `--numpad` und `--rfid` Parameter starten oder den Simulator verwenden.

**Wo sind die Mitarbeiterdaten gespeichert?**
Ausschließlich in der Datei `arbeitszeit.db` auf dem lokalen Rechner. Es werden keine Daten ins Internet übertragen.

**Kann ich die Datenbank auf mehrere Computer verteilen?**
Nein – das System ist für einen einzelnen lokalen Rechner ausgelegt. Der NAS-Sync dient nur als Backup, nicht als gleichzeitiger Zugriff von mehreren Rechnern.

**Wird meine bisherige Python-Version gelöscht?**
Nein. pyenv installiert Python 3.14 zusätzlich. Die Systemversion bleibt unverändert erhalten. Nur im `arbeitszeit`-Ordner wird automatisch Python 3.14 verwendet.

---

## Zusammenfassung – Reihenfolge der Schritte

| Schritt | Befehl / Aktion |
|---|---|
| 0. Python 3.14 prüfen & installieren | `python3 --version` → ggf. pyenv + `pyenv install 3.14.0` |
| 1. Herunterladen | `git clone …` + `cd arbeitszeit` |
| 2. Virtuelle Umgebung | `python3 -m venv .venv` + `source .venv/bin/activate` |
| 3. Installieren | `pip install -e ".[dev]"` |
| 4. Datenbank anlegen | `python scripts/init_db.py --db arbeitszeit.db` |
| 5. Verzeichnisse einrichten | `python scripts/setup.py --db arbeitszeit.db` |
| 6. Terminal starten | `python -m arbeitszeit.presentation.terminal_ui.main …` |
| 7. Admin-CLI nutzen | `python -m arbeitszeit.presentation.admin_cli.main …` |

---

*Dieses Dokument basiert auf dem [README.md](https://github.com/iCodator/arbeitszeit/blob/main/README.md) und der Projektstruktur des arbeitszeit-Repositories.*
