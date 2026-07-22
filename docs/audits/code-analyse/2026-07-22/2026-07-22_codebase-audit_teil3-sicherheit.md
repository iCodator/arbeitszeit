# Codebase-Audit Teil 3 — Sicherheitsrisiken

| Feld | Wert |
| --- | --- |
| Erstellt | 2026-07-22 |
| Auditor | Claude Sonnet 4.6 (Security-Audit-Agent) |
| Codestand | main, commit a9ccfb2 |
| Scope | Alle Python-Quellen, Migrationsskripte, Dependency-Manifest |
| Methode | statische Quellcode-Analyse, keine Laufzeitprüfung |

## Zusammenfassung

Neun Befunde wurden identifiziert. Davon zwei Hoch, drei Mittel und vier Niedrig.
Kein Befund mit Kritisch-Einstufung. Die ernsthaftesten Risiken betreffen die
RFID-Pseudonymisierung (unsalted SHA-256) und eine fehlende Passwort-Verifikation
in der Admin-CLI. Der Gesamtcode zeigt solide Grundsicherheit: alle SQL-Abfragen
sind parameterisiert, alle Subprozesse nutzen absolute Pfade ohne Shell,
und keine hartkodierte Credentials wurden gefunden.

---

## Befunde (absteigend nach Schweregrad)

---

### [Hoch] Unsalted SHA-256 für RFID-UIDs — DSGVO-Pseudonymisierung wirkungslos

**Datei:** `src/arbeitszeit/infrastructure/hardware/uid_hash.py:8`

**Problem:** `hash_uid()` berechnet `hashlib.sha256(raw_uid.encode()).hexdigest()`
ohne Pepper, HMAC-Key oder Salt. Standard-RFID-Karten (ISO 14443 Typ A, z. B.
Mifare Classic) verwenden 4-Byte-UIDs (2³² ≈ 4,3 Milliarden Möglichkeiten). Auf
moderner GPU-Hardware lässt sich der gesamte Keyspace in Sekunden bis Minuten
durchsuchen. Ein Angreifer, der Lesezugriff auf die Datenbank erhält, kann alle
gespeicherten `rfid_cards.uid_hash`-Werte auf physische Karten-UIDs
zurückrechnen.

Die DSGVO Art. 32 TOM „Pseudonymisierung", auf die das Datenschutzkonzept des
Projekts Bezug nimmt, ist damit für RFID-Daten nicht wirksam: ein entschlossener
Angreifer kann die Verknüpfung Karten-UID ↔ Mitarbeiter aus der Datenbank
ableiten.

**Auslösefall:** Angreifer erhält Lesezugriff auf `arbeitszeit.db` (z. B. durch
unsicheres Backup oder kompromittierten NAS-Speicher) und erschöpft den
4-Byte-UID-Keyspace mit einem Brute-Force-Tool.

**Empfehlung:** HMAC-SHA256 mit einem installationsspezifischen Pepper aus dem
OS-Keyring oder einer separaten, berechtigungsgeschützten Schlüsseldatei:

```python
import hmac, os
# Schlüssel einmalig erzeugen und sicher speichern (nicht in config.toml)
_PEPPER = os.environb.get(b"RFID_PEPPER")  # oder aus Keyring laden
def hash_uid(raw_uid: str) -> str:
    return hmac.new(_PEPPER, raw_uid.encode(), "sha256").hexdigest()
```

Bestehende Hashes in der Datenbank müssten nach Einführung des Peppers neu
berechnet werden (einmalige Migration).

---

### [Hoch] Passwort-Hash gespeichert, aber nie verifiziert — Admin-CLI ohne Authentifikation

**Dateien:**
`src/arbeitszeit/presentation/admin_cli/user_accounts.py:41–47` (Hashing),
`src/arbeitszeit/presentation/admin_cli/main.py:45–68` (Identitätsauflösung),
`src/arbeitszeit/presentation/admin_cli/_auth.py:14–35` (Rollenprüfung)

**Problem:** Die Admin-CLI identifiziert den Aufrufer ausschließlich anhand
einer numerischen `user_id` (aus CLI-Argument `--user-id`, Umgebungsvariable
`ADMIN_USER_ID` oder `config.toml`). Eine Passwort-Verifikation existiert im
gesamten Codebase nicht: es gibt keine `verify_password()`-Funktion, und
`password_hash` wird nach dem Anlegen eines Kontos nie wieder gelesen.

Der Code in `_auth.py` prüft nur, ob die angegebene `user_id` in der Datenbank
als ADMIN/REVIEWER/TECH mit `active=1` existiert — nicht, ob der Aufrufer das
zugehörige Passwort kennt. Das Bootstrap-Konto bekommt immer `id=1` (SQLite
AUTOINCREMENT), was vorhersagbar ist.

**Auslösefall:** Ein Nutzer mit OS-Zugriff (z. B. als Mitglied der Systemgruppe,
die Lesezugriff auf das CLI-Binary hat) führt `admin --user-id 1 employees list`
aus und erhält vollständige Mitarbeiterdaten — ohne jede Passworteingabe.

**Hinweis:** Das Sicherheitsmodell ist konsistent mit einem lokalen Kiosk-System,
bei dem „OS-Zugriff = Admin-Zugriff" gilt. Das ist architektonisch vertretbar,
aber nur wenn OS-Level-Berechtigungen (Dateisystem-ACLs, systemd-Unit mit
dedizierten Nutzern) tatsächlich durchgesetzt sind. Das gespeicherte Passwort
erweckt einen falschen Eindruck von Zugriffskontrolle.

**Empfehlung:** Zwei Optionen:

1. Passwort-Verifikation nachrüsten: `--password` am CLI-Start abfragen,
   `password_hash` aus der DB laden, mit PBKDF2-HMAC-SHA256 und
   `secrets.compare_digest()` vergleichen.
2. Den `password_hash`-Mechanismus als „für zukünftige Web-UI reserviert"
   explizit dokumentieren und im Sicherheitskonzept festhalten, dass der
   Admin-CLI-Zugriff ausschließlich durch OS-Berechtigungen geschützt ist.

---

### [Mittel] Vollständiger `uid_hash` in Fehlerfall-Audit-Log — Rückverfolgbarkeit

**Datei:** `src/arbeitszeit/application/use_cases/book_time.py:264–279`

**Problem:** Im Fehlerfall „unbekannte Karte" schreibt `_verify_card()` den
vollständigen 64-Zeichen-SHA-256-Hash in `details_json` des Audit-Logs:

```python
details_json=json.dumps({"uid_hash": uid_hash, "terminal_id": terminal_id}, ...)
```

In Kombination mit dem fehlenden Pepper (Befund 1) ermöglicht jeder mit
Lesezugriff auf `audit_log`, den gespeicherten Hash auf die physische Karten-UID
zurückzurechnen und festzustellen, welche Karte wann an welchem Terminal
gescannt wurde — auch ohne Mitarbeiter-Zuordnung. Damit ist selbst der versuchte
Zutritt mit einer fremden/gestohlenen Karte vollständig nachverfolgbar auf die
Karten-UID.

**Auslösefall:** Audit-Log wird an eine dritte Stelle (z. B. SIEM, NAS-Backup)
übermittelt; Empfänger kann alle unbekannten Karten-UIDs brute-forcen.

**Empfehlung:** Nur den Präfix des Hashes im Audit-Log speichern, wie es das
Debounce-Logging in `debounce.py` bereits korrekt macht (`uid_hash[:8]`):

```python
"uid_hash_prefix": uid_hash[:8]
```

---

### [Mittel] Keine Format-Validierung für `--uid-hash`-Parameter

**Dateien:**
`src/arbeitszeit/presentation/admin_cli/employees.py:215` (`cards assign`),
`src/arbeitszeit/presentation/admin_cli/employees.py:229` (`cards replace`)

**Problem:** Der Parameter `--uid-hash` wird ohne Formatprüfung direkt als
`uid_hash`-Wert in der Datenbank gespeichert. Der Hilfetext lautet „Fertig
berechneter SHA-256-Hash der Karten-UID", aber es wird nicht verifiziert, ob
der übergebene String tatsächlich ein 64-Zeichen-Hex-String ist.

Gibt ein Operator versehentlich die rohe UID (z. B. `A1B2C3D4`) statt ihres
Hashes ein, wird die Karte dauerhaft nicht erkannt (der Terminal hasht die UID
beim Scan, die DB enthält die ungehashte Rohform). Die Fehlerursache ist dann
schwer nachzuvollziehen.

**Empfehlung:** Validierung vor Anlage des Commands:

```python
import re
if not re.fullmatch(r"[0-9a-f]{64}", uid_hash):
    print("Fehler: --uid-hash muss ein 64-Zeichen-SHA-256-Hex-String sein.", file=sys.stderr)
    sys.exit(1)
```

---

### [Mittel] Audit-Log-Eintrag nach Buchungs-Commit — Write-Gap

**Datei:** `src/arbeitszeit/application/use_cases/book_time.py:204–246`

**Problem:** Nach dem Commit der Buchungstransaktion (Zeile 204) werden
Audit-Log-Einträge auf der separaten `audit_conn`-Verbindung geschrieben
(Zeilen 206–246). Das ergibt folgenden zeitlichen Ablauf:

1. `self._uow.commit()` — Buchung ist dauerhaft in der DB.
2. `self._uow.audit_log_repo.add(...)` — Audit-Eintrag wird geschrieben.

Ein Prozessabsturz (SIGKILL, OOM) zwischen Schritt 1 und 2 hinterlässt eine
Buchung ohne zugehörigen Audit-Log-Eintrag. Dies verletzt die
ArbZG-Dokumentationspflicht (lückenlose Aufzeichnung) und die DSGVO-Pflicht
zur Nachvollziehbarkeit von Datenverarbeitungen.

Der Kommentar im Code erklärt die bewusste Designentscheidung (Lock-Vermeidung);
das Risiko ist aber nicht explizit dokumentiert.

**Auslösefall:** Rasperry Pi verliert Strom oder wird per SIGKILL beendet exakt
nach dem Buchungs-Commit, bevor der Audit-Log-Eintrag geschrieben wird. Im
Audit-Log fehlt dann ein `TIME_BOOKED`-Ereignis für eine real existierende
Buchung.

**Empfehlung:** Write-Ahead-Ansatz: Audit-Log-Eintrag vor dem Commit schreiben
(mit `status: "pending"`), nach dem Commit auf `status: "committed"` aktualisieren.
Alternativ: regelmäßige Plausibilitätsprüfung „Buchungen ohne Audit-Eintrag"
als Admin-Befehl.

---

### [Niedrig] Rohe RFID-UID im Klartext im Diagnose-Skript

**Datei:** `scripts/verify_hardware.py` (Zeile ~334)

**Problem:** Das Diagnose-Skript gibt die gescannte RFID-Roh-UID unverschleiert
aus:

```python
_info(f"Rohe UID (Hex):  {uid_raw.upper()}")
```

Wird das Skript in einer protokollierten Terminal-Sitzung (SSH-Audit,
tmux-Log, systemd-Journal mit Verbose-Level) ausgeführt, landet die physische
Karten-UID als Klartext in Logdateien — außerhalb des Hash-Speichermodells
der Anwendung.

**Empfehlung:** Roh-UID nach den ersten vier Zeichen maskieren:

```python
_info(f"Rohe UID (Hex):  {uid_raw[:4].upper()}****")
_info(f"Länge:           {len(uid_raw)} Zeichen ({len(uid_raw) * 4} Bit)")
```

---

### [Niedrig] Generiertes Passwort auf stdout ausgegeben

**Datei:** `src/arbeitszeit/presentation/admin_cli/user_accounts.py:77, 162`

**Problem:** Bei automatisch generierten Passwörtern (kein `--password`-Argument)
wird das Klartext-Passwort auf stdout ausgegeben:

```python
print(f"Generiertes Passwort (einmalig sichtbar): {password}")
```

In automatisierten Deployment-Workflows (z. B. Ansible-Playbooks, CI/CD-Skripte)
kann stdout-Output in Protokolldateien, Job-Artifacts oder Audit-Trails landen.

**Empfehlung:** Passwort-Ausgabe auf stderr umleiten (stderr wird in den meisten
Automation-Tools standardmäßig nicht persistiert) oder den Aufrufer explizit
auf das Risiko hinweisen:

```python
print("WARNUNG: Passwort wird einmalig angezeigt. Nicht in Logs umleiten.", file=sys.stderr)
print(f"Passwort: {password}", file=sys.stderr)
```

---

### [Niedrig] Audit-Log ohne Integritätssicherung

**Datei:** `migrations/0001_schema.sql:302–313`

**Problem:** Die `audit_log`-Tabelle hat einen einfachen Autoincrement-Primärschlüssel
ohne Hash-Verkettung (Row-Chaining), HMAC-Signatur oder Append-Only-Constraint.
Ein Datenbankadministrator mit Schreibzugriff kann Einträge lautlos löschen
oder verändern, ohne dass dies detektierbar wäre. Dasselbe gilt für Angreifer,
die Schreibzugriff auf die `.db`-Datei erhalten.

Für ArbZG-Compliance (lückenlose Arbeitszeitaufzeichnung) und DSGVO-Accountability
ist eine manipulationssichere Protokollierung relevant.

**Empfehlung:** Periodischer Export der Audit-Log-Tabelle in eine unveränderliche
Zieldatei (z. B. append-only File auf NAS) oder HMAC-Kette über
`(id, event_type, event_at, employee_id, details_json)` mit Verweis auf den
Hash des Vorgängereintrags.

---

### [Niedrig] Kein Dependency-Lock-File — keine reproduzierbaren Builds

**Datei:** `pyproject.toml`

**Problem:** Alle Abhängigkeiten sind ausschließlich mit Untergrenzen definiert
(z. B. `evdev>=1.7`, `reportlab>=4.0`). Ein Lock-File (z. B. `uv.lock` oder
`pip-compile`-Output) fehlt. Bei einer Neuinstallation auf einem anderen System
können jede neuere Version gezogen werden, was:

- Reproduzierbarkeit von Builds verhindert,
- Sicherheits-Patches im Produktivbetrieb nicht erzwingt (der Operator muss
  aktiv aktualisieren),
- eine genaue CVE-Prüfung für die tatsächlich deployten Versionen erschwert.

**Feststellung zu aktuellen Versionen:** Die im Entwicklungssystem installierten
Versionen (evdev 1.9.3, reportlab 5.0.0, pypdf 6.13.1, pytest 9.0.3, ruff 0.15.16)
entsprechen dem aktuellen Stand; keine bekannten CVEs in diesen Versionen
identifiziert.

**Empfehlung:** `uv lock` oder `pip-compile` in den CI/CD-Prozess einbinden und
das erzeugte Lock-File ins Repository aufnehmen.

---

## Positive Feststellungen (keine Befunde)

- **SQL-Injection:** Alle Datenbankzugriffe durchgängig mit parametrisierten
  Abfragen. Die einzige String-Interpolation in `migrations.py` ist durch
  `isdigit() and len() == 4` auf den Wertebereich `"0000"`–`"9999"` beschränkt
  und korrekt mit `# nosec B608` annotiert.
- **Subprozess-Sicherheit:** Alle externen Programmaufrufe (`rsync`, `notify-send`,
  `timedatectl`) verwenden absolute Pfade und `shell=False`. Kein Injektionsvektor
  für Benutzeringaben in Prozessargumenten.
- **Passwort-Hashing:** PBKDF2-HMAC-SHA256 mit 260.000 Iterationen und 16-Byte-
  Zufallssalt — korrekte Implementierung nach aktuellem NIST-Standard.
- **RFID-Exklusivzugriff:** `evdev.grab()` verhindert, dass andere Prozesse
  RFID-Eingaben mitlesen.
- **Keine hartkodierte Credentials:** Weder in Quellcode noch in `config.toml.example`
  wurden Passwörter, Schlüssel oder Tokens gefunden.
- **Konfigurationsgeheimnisse:** `config.toml` enthält ausschließlich Pfade und
  IDs, keine Authentifizierungsinformationen.
- **Deserialisierung:** Keine Nutzung von `pickle` oder `yaml.load()` ohne
  `Loader`; ausschließlich `json.loads()` und `tomllib` (read-only, stdlib).
- **Foreign-Key-Constraints:** `PRAGMA foreign_keys = ON` aktiv; referenzielle
  Integrität auf Datenbankebene gesichert.
- **Keine CORS-/Rate-Limit-Risiken:** Kein Netzwerk-Interface, kein HTTP-Server;
  nicht anwendbar für dieses System.
