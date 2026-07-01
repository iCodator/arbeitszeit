# Handbuch `arbeitszeit` – Installation

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

## Systemvoraussetzungen

### Betriebssystem

Die Projektunterlagen und die Installationsdokumentation beziehen sich auf
Linux Mint und Lubuntu.

### Python-Version

Die verbindliche Python-Anforderung steht in `pyproject.toml`:

```toml
requires-python = ">=3.14,<3.15"
```

Damit ist für die Installation Python 3.14 erforderlich.

Prüfung der installierten Version:

```bash
python3.14 --version
```

`python3 --version` allein ist nicht ausreichend, wenn auf dem System eine
andere Python-Hauptversion als 3.14 als Standard eingerichtet ist.

### Python-Abhängigkeiten

Laufzeitabhängigkeiten:

| Paket | Mindestversion | Zweck |
| --- | --- | --- |
| `evdev` | `>=1.7` | Zugriff auf Linux-Eingabegeräte |
| `reportlab` | `>=4.0` | PDF-Erzeugung |

Entwicklungsabhängigkeiten:

| Paket | Mindestversion | Zweck |
| --- | --- | --- |
| `pytest` | `>=8.0` | Testausführung |
| `pytest-cov` | `>=5.0` | Coverage |
| `pypdf` | `>=4.0` | PDF-Prüfung in Tests |
| `ruff` | `>=0.6` | Linting |
| `import-linter` | `>=2.0` | Architekturprüfung |

### Zusätzliche Systempakete

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) python3-dev
```

### Hardware

Sicher belegt sind folgende Hardware-Komponenten im Projektkontext:

- RFID-Reader als USB-HID-Gerät
- USB-Numpad als Eingabegerät

Die Gerätedateien werden unter Linux über `/dev/input/event*` angesprochen.

## Installation

Repository klonen:

```bash
git clone https://github.com/iCodator/arbeitszeit.git
cd arbeitszeit
```

Virtuelle Umgebung erstellen:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

Abhängigkeiten installieren:

```bash
pip install -e .[dev]
```

Datenbank initialisieren:

```bash
python scripts/init_db.py
```

Der Datenbankpfad kann optional mit `--db` angegeben werden. Standard ist
`arbeitszeit.db`.

Typische Ausgabe:

```text
Migration 0001 angewendet.
Migration 0002 angewendet.
Migration 0003 angewendet.
Migration 0004 angewendet.
Migration 0005 angewendet.
Migration 0006 angewendet.
⚠  Ersteinrichtung noch erforderlich:
   python scripts/setup.py --db arbeitszeit.db
```

## Ersteinrichtung

Die Reihenfolge ist zwingend:

1. `scripts/init_db.py`
2. `scripts/setup.py`

Interaktiver Aufruf:

```bash
python scripts/setup.py --db arbeitszeit.db
```

Nicht-interaktiver Aufruf:

```bash
python scripts/setup.py   --db arbeitszeit.db   --backup-dir /var/backups/arbeitszeit   --export-dir /var/exports/arbeitszeit
```

Bereits konfigurierte Schlüssel werden beim erneuten Aufruf übersprungen.

## Erste Konten und Stammdaten

Ersten ADMIN anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   users bootstrap   --username adminname
```

Weiteres Benutzerkonto anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   users add   --username pruefer01   --role REVIEWER
```

Mitarbeiter anlegen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   employees add   --personnel-no M001   --first-name Maria   --last-name Mustermann
```

RFID-Karte zuweisen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   cards assign   --employee-id 1   --uid-hash <HASH>
```

## Funktionstest

```bash
pytest
pytest tests/test_migrations.py
pytest --cov=arbeitszeit
```
