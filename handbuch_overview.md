# Handbuch `arbeitszeit` – Übersicht

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

## Zweck

`arbeitszeit` ist ein lokal betriebenes Zeiterfassungssystem für eine
Zahnarztpraxis. Die Anwendung verwendet SQLite als einzige Datenbank und trennt
Fachlogik, Infrastruktur und Benutzeroberflächen klar voneinander.

Aus dem Repository eindeutig belegt sind ein Terminalmodus für den operativen
Buchungsbetrieb sowie eine Admin-CLI für Verwaltungsaufgaben.

## Projektstruktur

Aus dem Repository klar belegt ist folgende Hauptstruktur:

```text
arbeitszeit/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── run_audit.sh
├── test_booking_loop.py
├── installationsanleitung_arbeitszeit.md
├── handbuch_arbeitszeit.md
├── migrations/
├── scripts/
├── docs/
├── src/
│   └── arbeitszeit/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── presentation/
│           ├── admin_cli/
│           └── terminal_ui/
└── tests/
```

## Schichten

In `pyproject.toml` ist eine Architekturprüfung mit `import-linter`
hinterlegt. Daraus geht hervor, dass das Projekt diese Schichten trennt:

- `arbeitszeit.presentation`
- `arbeitszeit.infrastructure`
- `arbeitszeit.application`
- `arbeitszeit.domain`

Diese Struktur entspricht einer Clean-Architecture-orientierten Trennung.
