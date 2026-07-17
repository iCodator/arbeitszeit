# Systemübersicht — technisches Referenzhandbuch

**Kapitel:** 1-IT
**Version:** 1.0
**Stand:** Juli 2026
**Zielgruppe:** Entwickler, Systemverantwortliche
**Quelldateien:** `pyproject.toml`, `README.md`, `config.toml.example`

## Systemcharakteristik

`arbeitszeit` ist ein lokal betriebenes Zeiterfassungssystem für eine
Zahnarztpraxis, implementiert als Python-Paket im `src`-Layout.

| Eigenschaft | Wert |
| --- | --- |
| Python-Version | `>=3.14,<3.15` (strikt) |
| Datenbank | SQLite |
| Paketmanager | uv (`uv.lock`) |
| Laufzeit-Abhängigkeiten | `evdev>=1.7`, `reportlab>=4.0` |
| Architekturprüfung | import-linter |

## Schichtenmodell

Das Schichtenmodell ist in `pyproject.toml` via import-linter erzwungen:

```
presentation > infrastructure > application > domain
```

Jede Schicht darf nur auf darunter liegende Schichten zugreifen.
Seitliche Abhängigkeiten zwischen Peers sind verboten.

| Schicht | Paket | Aufgabe |
| --- | --- | --- |
| Presentation | `arbeitszeit.presentation` | Admin-CLI und Terminal-UI |
| Infrastructure | `arbeitszeit.infrastructure` | DB, Hardware, Backup, Systemprüfung |
| Application | `arbeitszeit.application` | Use Cases, Commands, Results, UoW |
| Domain | `arbeitszeit.domain` | Entitäten, Enumerationen, Regeln |

## Projektstruktur

```text
arbeitszeit/
├── config.toml.example
├── docs/
│   ├── 01_normativ/
│   ├── 02_anwender/
│   │   └── module/          # Kapitel-Handbücher
│   ├── 03_installation_technik/
│   ├── 04_betrieb/
│   ├── 05_datenschutz_recht/
│   ├── 06_architektur/
│   ├── 07_pruefberichte/
│   └── audits/reports/      # Audit-Ausgaben (run_audit.sh)
├── migrations/              # 0001–0006 SQL-Migrationsdateien
├── pyproject.toml
├── run_audit.sh
├── scripts/                 # Hilfs- und Betriebsskripte
│   ├── backup.py
│   ├── generate_audit_notes.py
│   ├── init_db.py
│   ├── setup.py
│   ├── show_config.py
│   └── verify_hardware.py
├── src/
│   └── arbeitszeit/
│       ├── application/
│       │   ├── commands.py
│       │   ├── queries.py
│       │   ├── results.py
│       │   ├── unit_of_work.py
│       │   └── use_cases/
│       ├── domain/
│       │   ├── entities.py
│       │   ├── enums.py
│       │   ├── errors.py
│       │   ├── ports/
│       │   ├── services/
│       │   └── value_objects.py
│       ├── infrastructure/
│       │   ├── backup/
│       │   ├── db/
│       │   ├── export/
│       │   ├── hardware/
│       │   ├── config_file.py
│       │   ├── system_check.py
│       │   └── time_monitor.py
│       └── presentation/
│           ├── admin_cli/
│           └── terminal_ui/
└── tests/
```

## Einstiegspunkte

Das Paket enthält keinen `[project.scripts]`-Eintrag. Alle Einstiegspunkte
werden über `python -m` aufgerufen.

| Einstiegspunkt | Befehl |
| --- | --- |
| Admin-CLI | `python -m arbeitszeit.presentation.admin_cli.main` |
| Terminal-UI | `python -m arbeitszeit.presentation.terminal_ui.main` |
| DB-Initialisierung | `python scripts/init_db.py` |
| Konfigurationseinrichtung | `python scripts/setup.py` |
| Konfigurationsanzeige | `python scripts/show_config.py --db ...` |
| Backup | `python scripts/backup.py --db ...` |
| Hardware-Prüfung | `python scripts/verify_hardware.py` |
| Statischer Audit | `bash run_audit.sh` |

Empfohlener Alias für die Admin-CLI:

```bash
alias azadmin='python -m arbeitszeit.presentation.admin_cli.main'
```

## Konfiguration

Die TOML-Konfigurationsdatei wird über `find_config()` gesucht:

1. Umgebungsvariable `ARBEITSZEIT_CONFIG`
2. `~/.config/arbeitszeit/config.toml`
3. `./config.toml` (Working-Directory)

Datenbank- und Benutzerpfad können alternativ per CLI-Argument oder
Umgebungsvariable (`ADMIN_USER_ID`) übergeben werden.

Die Struktur der Konfigurationsdatei ist in `handbuch_infrastructure_it.md`
vollständig dokumentiert. Eine Beispielkonfiguration liegt als
`config.toml.example` vor.

## Datenbankmigrationen

Migrationen werden über `migrations.run_migrations(conn)` ausgeführt.
Die Admin-CLI führt Migrationen bei jedem Start aus. Das Datenbankschema
(16 Tabellen, 17 Indizes, 6 Migrationen) ist in
`handbuch_datenbankschema_it.md` vollständig dokumentiert.
