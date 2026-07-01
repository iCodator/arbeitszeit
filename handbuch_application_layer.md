# Handbuch `arbeitszeit` – Application Layer

**Version:** 1.0
**Stand:** Juli 2026
**Basis:** `handbuch_arbeitszeit.md`

## Abgrenzung

Dieses Dokument beschreibt die belegten fachlichen Anwendungsfälle, soweit sie
über die Admin-CLI aufgerufen werden. Die Projektstruktur und Schichtentrennung
gehören nicht hierher, sondern in `handbuch_overview.md`.

## Befehlsgruppen

Aus `src/arbeitszeit/presentation/admin_cli/main.py` sind folgende
Befehlsgruppen eindeutig belegt:

- `employees`
- `cards`
- `bookings`
- `schedule`
- `reports`
- `system`
- `users`

## Belegte Anwendungsfälle

Aus dem Dispatch in `main.py` sind unter anderem diese konkreten Befehle
belegt:

- `employees list`
- `employees add`
- `employees deactivate`
- `cards assign`
- `cards replace`
- `cards deactivate`
- `bookings correct`
- `bookings supplement`
- `bookings approve-supplement`
- `bookings reject-supplement`
- `schedule set`
- `schedule show`
- `reports export-csv`
- `reports export-pdf-day`
- `reports export-pdf-week`
- `reports export-pdf-month`
- `reports export-pdf-employee`
- `reports open-bookings`
- `reports warn-cases`
- `reports corrections`
- `reports supplements`
- `reports open-review-cases`
- `system check`
- `system backup`
- `users add`
- `users list`
- `users deactivate`
- `users reactivate`
- `users change-role`
- `users bootstrap`

## Beispiele

Mitarbeiter deaktivieren:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   employees deactivate 3
```

RFID-Karte ersetzen:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   cards replace   --old-card-id 2   --uid-hash <NEUER_HASH>
```

Benutzerkonto deaktivieren:

```bash
python -m arbeitszeit.presentation.admin_cli.main   --db arbeitszeit.db   --user-id 1   users deactivate   --user-id 3
```

Hier erscheint `--user-id` zweimal: das erste Mal für den aufrufenden Admin,
das zweite Mal für das Zielkonto.
