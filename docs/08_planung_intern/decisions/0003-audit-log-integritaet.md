# 0003 — Audit-Log-Integrität: HMAC-Kette oder Append-Only-Export

## Status

Vorgeschlagen

## Kontext

Der Codebase-Audit vom 2026-07-22 (Teil 3, Sicherheit) hat folgenden Befund
(Priorität: Niedrig) erhoben:

> Die `audit_log`-Tabelle hat einen einfachen Autoincrement-Primärschlüssel
> ohne Hash-Verkettung, HMAC-Signatur oder Append-Only-Constraint. Ein
> Datenbankadministrator mit Schreibzugriff kann Einträge lautlos löschen
> oder verändern, ohne dass dies detektierbar wäre.

Das System protokolliert gemäß ArbZG alle buchungsrelevanten Ereignisse
(Kommen, Gehen, Pausen) sowie administrative Aktionen (Kontenverwaltung,
Nachträge, Korrekturen). Für ArbZG-Compliance und DSGVO-Accountability ist
eine manipulationssichere Protokollierung relevant.

Aktuelles Schema (`audit_log`-Tabelle, Migration 0001):

```sql
CREATE TABLE audit_log (
    id            INTEGER PRIMARY KEY,
    event_type    TEXT NOT NULL,
    object_type   TEXT,
    object_id     INTEGER,
    user_id       INTEGER,
    employee_id   INTEGER,
    event_at      TEXT NOT NULL,
    details_json  TEXT
);
```

Es gibt keinen Mechanismus, der eine nachträgliche Veränderung eines Eintrags
erkennbar machen würde.

## Entscheidungsoptionen

### Option A: HMAC-Kette (Row-Chaining)

Jeder neue Eintrag enthält einen `chain_hash`-Wert, der als HMAC-SHA256 über
die Felder des aktuellen Eintrags **und** den `chain_hash` des Vorgängers
berechnet wird.

Felder für die Hash-Eingabe (Vorschlag):

```
HMAC-SHA256(key=AUDIT_HMAC_KEY,
            data=f"{id}|{event_type}|{event_at}|{employee_id}|{details_json}|{prev_chain_hash}")
```

Vorteile:

- Vollständig in SQLite umsetzbar — kein externes System erforderlich
- Nachträgliche Veränderungen oder Löschungen brechen die Kette
- Prüfung jederzeit mit einem Admin-CLI-Befehl (`verify-audit-chain`) möglich

Nachteile:

- Jeder `audit_log`-INSERT muss den Vorgänger-Hash lesen (zusätzlicher DB-Read)
- Der HMAC-Key muss sicher aufbewahrt werden (z. B. `AUDIT_HMAC_KEY`-Umgebungsvariable)
- Spalte `chain_hash TEXT` muss via Migration ergänzt werden
- Der Genesis-Eintrag (id=1) hat einen definierten Startwert (`"0" * 64`)

Umsetzungsschritte:

1. Migration: `chain_hash TEXT` zur `audit_log`-Tabelle hinzufügen (nullable für
   Altdaten; neue Einträge NOT NULL)
2. `AuditLogRepository.add()` und `add_transactional()`: HMAC berechnen und
   schreiben
3. Admin-CLI-Befehl `audit verify-chain` implementieren
4. `AUDIT_HMAC_KEY` in Konfiguration und `system_check.py` aufnehmen

### Option B: Periodischer Append-Only-Export

Das Audit-Log wird in regelmäßigen Abständen (täglich / nach jeder Schicht)
in eine unveränderliche Datei auf einem externen Medium (NAS) exportiert.

Format: JSONL (eine JSON-Zeile pro Eintrag) oder CSV.

Vorteile:

- Einfache Implementierung (reiner Lese- und Schreibvorgang)
- Export-Datei ist unabhängig von der SQLite-Datei
- NAS kann mit Append-Only-Dateisystemrechten konfiguriert werden

Nachteile:

- Erfordert externer Speicher (NAS) mit korrekter Konfiguration
- Zwischen dem letzten Export und einem Angriff liegende Einträge wären
  nicht in der Export-Datei sichergestellt
- Kein Mechanismus, der Veränderungen *innerhalb* der DB vor dem Export erkennt

## Empfehlung

**Option A (HMAC-Kette)** wird empfohlen, da sie:

- keine externe Infrastruktur erfordert (kein NAS zwingend nötig)
- lückenlos schützt (jede Veränderung, auch zwischen Exporten, ist erkennbar)
- mit dem bestehenden Backup-Konzept (NAS-Export) kombinierbar ist

Option B kann als ergänzende Maßnahme (Export auf NAS) parallel umgesetzt
werden, ersetzt Option A jedoch nicht vollständig.

## Nächste Schritte

Vor der Implementierung sind folgende Fragen zu klären:

1. Welche Umgebungsvariable / Konfigurationsdatei soll `AUDIT_HMAC_KEY`
   bereitstellen?
2. Soll der Key beim ersten Start automatisch generiert und in der DB gespeichert
   werden (einfacher Betrieb) oder extern verwaltet (höhere Sicherheit)?
3. Wie soll mit Altdaten (Einträgen ohne `chain_hash`) umgegangen werden —
   Migration mit `chain_hash = NULL` oder nachträgliche Verkettung?

Erst nach Klärung dieser Fragen soll die Implementierung beginnen.

## Betroffene Komponenten

- `migrations/` — neue Migration für `chain_hash`-Spalte
- `src/arbeitszeit/infrastructure/db/repositories/audit_log.py` — Hash-Berechnung
- `src/arbeitszeit/domain/ports/repositories.py` — ggf. Signatur-Erweiterung
- `src/arbeitszeit/presentation/admin_cli/` — neuer Befehl `audit verify-chain`
- `src/arbeitszeit/infrastructure/system_check.py` — Key-Verfügbarkeit prüfen
