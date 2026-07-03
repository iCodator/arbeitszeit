# Sicherheitsmodell — arbeitszeit

Dieses Dokument beschreibt Sicherheits- und Datenschutzentscheidungen des Systems
für Betreiber, Administratoren und Prüfer (Datenschutzbeauftragter, Steuerberater).

---

## 1. Lokale Datenhaltung

Das System speichert **ausschließlich lokal** — keine Cloud-Anbindung, kein
Netzwerkzugriff durch das System selbst. Alle Daten liegen in einer einzigen
SQLite-Datenbankdatei (`arbeitszeit.db`) auf dem lokalen Rechner.

Der Betreiber trägt die Verantwortung für:

- physischen Zugangsschutz zum Gerät
- Zugriffsrechte auf Betriebssystemebene (Linux-Benutzer/-Gruppen)
- regelmäßige Backups (lokal und/oder NAS, siehe Abschnitt 4)

---

## 2. RFID-Kartendaten — Hashing

RFID-Karten-UIDs werden **niemals im Klartext gespeichert**. Beim ersten Einlesen
wird die UID mit SHA-256 gehasht (`infrastructure/hardware/uid_hash.py`). Gespeichert
wird ausschließlich der Hash.

Das bedeutet:

- Aus der Datenbank kann die originale UID einer Karte nicht rekonstruiert werden.
- Ein Verlust der Datenbank gibt keinem Angreifer die physischen Kartendaten.
- Der Hash dient ausschließlich der Zuordnung Karte ↔ Mitarbeiter innerhalb des Systems.

**Kollisionsrisiko:** SHA-256 gilt nach aktuellem Stand (2026) als kollisionssicher
für diesen Anwendungsfall. Eine Migration auf stärkere Verfahren ist über die
Migrationsmechanismen des Systems möglich.

---

## 3. Audit-Log

Alle sicherheitsrelevanten Aktionen werden unveränderlich im `audit_log`
protokolliert, darunter:

| Ereignis | Audit-Typ |
|---|---|
| Buchung erfasst | `TIME_BOOKED` |
| Unbekannte Karte abgewiesen | `BOOKING_REJECTED_UNKNOWN_CARD` |
| Inaktive Karte abgewiesen | `BOOKING_REJECTED_INACTIVE_CARD` |
| Buchung korrigiert (Admin) | `BOOKING_CORRECTED` |
| Nachtrag erfasst | `SUPPLEMENT_CREATED` |
| Nachtrag genehmigt/abgelehnt | `SUPPLEMENT_APPROVED` / `SUPPLEMENT_REJECTED` |
| Regelarbeitszeit geändert | `WORK_SCHEDULE_CHANGED` |
| Backup erstellt | `BACKUP_CREATED` |
| NAS-Sync | `BACKUP_SYNCED_TO_NAS` |

Einträge im `audit_log` werden vom System **nicht gelöscht oder überschrieben**.
Eine Benutzeroberfläche zum nachträglichen Ändern von Audit-Einträgen existiert nicht.

---

## 4. NAS-Backup — Systemverhalten und Grenzen

### Was das System prüft

Der Systemcheck (`admin --db <PFAD> --user-id <ID> system check`, Logik in
`infrastructure/system_check.py`) prüft beim Check-Lauf:

- Ist `backup.nas_enabled` in der Datenbank auf `true` gesetzt?
- Ist `backup.nas_path` gesetzt und nicht leer?
- Ist der konfigurierte Pfad **im Dateisystem erreichbar** (`Path.exists()`)?
- Ist der Pfad **schreibbar** (`os.access(..., os.W_OK)`)?

### Was das System bewusst NICHT prüft

> **Der Systemcheck führt keinen aktiven Netzwerk-Ping oder TCP-Verbindungstest
> zum NAS durch.**

Diese Entscheidung ist bewusst und begründet:

1. **Offline-first-Design:** Das System ist für den Betrieb ohne permanente
   Netzwerkverbindung ausgelegt. Ein Ping-Test im Systemcheck würde bei
   vorübergehend nicht erreichbarem NAS (Neustart, Wartung) einen `SELFTEST_FAIL`
   erzeugen, obwohl das System selbst voll funktionsfähig ist.

2. **NAS als gemounteter Pfad:** Das NAS wird als Netzwerkfreigabe ins
   Dateisystem eingehängt (z. B. `/mnt/nas/arbeitszeit`). Die Prüfung
   `Path.exists()` + `os.access()` ist für diesen Mount-Punkt ausreichend
   und korrekt: Ist der Mount aktiv und schreibbar, ist das NAS erreichbar.
   Ist er es nicht, schlägt die Prüfung fehl.

3. **Netzwerkprüfung gehört in die Infrastruktur:** NAS-Erreichbarkeit (DNS,
   SMB/NFS-Port) ist Aufgabe des Betriebssystems und der systemd-Unit, nicht
   des Anwendungs-Systemchecks.

### Was der Betreiber sicherstellen muss

- Das NAS muss **vor Systemstart** als Dateisystemfreigabe gemountet sein
  (z. B. via `/etc/fstab` oder systemd `.mount`-Unit mit `_netdev`-Option).
- Der Systemcheck meldet `nas_reachability: OK` nur dann, wenn der Mount-Pfad
  tatsächlich existiert und schreibbar ist — **nicht** allein auf Basis der
  DB-Konfiguration.
- Schlägt der NAS-Sync beim Backup (`admin --db <PFAD> --user-id <ID> system backup`) fehl, wird
  eine **Warnung** ausgegeben, aber das lokale Backup bleibt erhalten und der
  Prozess endet mit Exit-Code 0. Das lokale Backup ist das primäre Sicherungsmittel.

### Empfehlung für den Betrieb

```bash
# /etc/fstab-Eintrag (Beispiel für CIFS/SMB):
//nas-hostname/backups/arbeitszeit  /mnt/nas/arbeitszeit  cifs  credentials=/etc/arbeitszeit-nas.cred,_netdev,noauto,x-systemd.automount  0  0
```

Mit `x-systemd.automount` wird der Mount erst beim ersten Zugriff aktiviert —
der Systemcheck erkennt damit korrekt, ob das NAS tatsächlich erreichbar ist.

---

## 5. Benutzerverwaltung

- Passwörter werden **nicht im Klartext** gespeichert. Das verwendete Verfahren
  ist PBKDF2-HMAC-SHA256 mit 260.000 Iterationen und 16-Byte-Zufallssalt
  (`presentation/admin_cli/user_accounts.py`, Funktion `_hash_password`).
- Rollen (`ADMIN`, `REVIEWER`, `TECH`, `EMPLOYEE`) schränken den Zugriff auf
  schreibende Operationen ein. Terminal-Buchungen erfordern keine Anmeldung —
  die Authentifizierung erfolgt ausschließlich über die RFID-Karte.
- Deaktivierte Benutzerkonten (`active = 0`) können sich nicht anmelden
  und deren Aktionen werden vom System abgewiesen.

---

## 6. DSGVO-Hinweise

Das System verarbeitet personenbezogene Daten (Name, Arbeitszeiten) von
Arbeitnehmern. Der Betreiber ist datenschutzrechtlich Verantwortlicher im Sinne
von Art. 4 Nr. 7 DSGVO.

Empfohlene Maßnahmen für den Betreiber:

- Aufnahme des Systems in das **Verzeichnis der Verarbeitungstätigkeiten** (Art. 30 DSGVO)
- Technische Zugangsbeschränkung auf autorisierte Personen (Admin-Terminal)
- Festlegen einer **Aufbewahrungsfrist** für Zeitbuchungsdaten (§ 147 AO: 10 Jahre
  für lohnsteuerrelevante Aufzeichnungen)
- Hinweis an Mitarbeiter gemäß Art. 13 DSGVO (Datenschutzinformation)

Das System selbst enthält keine automatische Datenlöschfunktion. Die Umsetzung
von Löschfristen obliegt dem Betreiber (manuell oder via geplanter DB-Bereinigung).

---

## 7. Bekannte Einschränkungen

| Einschränkung | Begründung / Empfehlung |
|---|---|
| Kein Netzwerk-Ping auf NAS im Systemcheck | Bewusst (siehe Abschnitt 4) — Mount-Prüfung ist ausreichend |
| Kein automatisches Ablaufen von Sitzungen | CLI-Sitzungen laufen bis zum manuellen Beenden; Terminal physisch sichern |
| Keine Verschlüsselung der SQLite-Datei | Betriebssystem-seitige Verschlüsselung (LUKS) empfohlen, wenn Gerät in halböffentlichem Bereich steht |
| Backup-Integrität nicht automatisch geprüft | Manuelle Stichproben-Wiederherstellung empfohlen (halbjährlich) |
