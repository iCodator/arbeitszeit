# Rollenzuweisung – arbeitszeit

**Version:** 1.0  
**Praxis:** ____________________________________________  
**Standort:** __________________________________________  
**Datum:** ____ / ____ / 20____  

---

## 1. Zweck

Dieses Dokument legt fest, welche Personen in der Zahnarztpraxis welche Rollen im
System **„arbeitszeit“** innehaben. Es ergänzt das technische Rollenkonzept im
Pflichtenheft/Regelwerk und in der Betriebsdokumentation.

---

## 2. Rollen im System

Die Anwendung „arbeitszeit“ kennt u. a. folgende Rollen:

- **ADMIN** – vollumfängliche technische und fachliche Administration,
- **REVIEWER** – fachliche Prüfung und Freigabe/Ablehnung von Nachträgen,
- **TECH** – technische Betreuung (z. B. Backup, Konfiguration),
- **EMPLOYEE** – normale Mitarbeiter:innen, die am Terminal buchen.

Dieses Dokument bezieht sich auf die administrativen Rollen ADMIN, REVIEWER, TECH.

---

## 3. Konkrete Rollenzuweisung

### 3.1 ADMIN-Rollen

| Name | Funktion in der Praxis | Rolle im System | Gültig ab | Gültig bis (falls befristet) |
| --- | --- | --- | --- | --- |
| ______________________ | ______________________ | ADMIN | __.__.20__ | __.__.20__ |
| ______________________ | ______________________ | ADMIN | __.__.20__ | __.__.20__ |

Regel: Es soll stets mindestens **eine** verantwortliche Person mit ADMIN-Rolle
geben. Änderungen werden zeitnah in diesem Dokument nachgeführt.

### 3.2 REVIEWER-Rollen

| Name | Funktion in der Praxis | Rolle im System | Gültig ab | Gültig bis |
| --- | --- | --- | --- | --- |
| ______________________ | ______________________ | REVIEWER | __.__.20__ | __.__.20__ |
| ______________________ | ______________________ | REVIEWER | __.__.20__ | __.__.20__ |

REVIEWER dürfen Nachträge genehmigen oder ablehnen. Die Zuordnung soll sich an
der fachlichen Verantwortung (Praxisleitung, vertretungsberechtigte Personen)
orientieren.

### 3.3 TECH-Rollen

| Name | Funktion in der Praxis | Rolle im System | Gültig ab | Gültig bis |
| --- | --- | --- | --- | --- |
| ______________________ | ______________________ | TECH | __.__.20__ | __.__.20__ |
| ______________________ | ______________________ | TECH | __.__.20__ | __.__.20__ |

TECH-Rollen haben technische Verantwortung (z. B. Backup, Systemcheck, Updates),
aber keine oder nur eingeschränkte fachliche Rechte.

---

## 4. Änderungen der Rollenzuweisung

Jede Änderung (Zuweisung, Entzug, Wechsel einer Rolle) wird in einem Änderungsprotokoll
festgehalten:

| Datum | Person | Änderung | Verantwortliche/r |
| --- | --- | --- | --- |
| __.__.20__ | ____________________ | z. B. „Rolle ADMIN → REVIEWER“ | ____________________ |
| __.__.20__ | ____________________ | z. B. „neuer ADMIN“ | ____________________ |

Die technische Umsetzung (Aktivieren/Deaktivieren von Benutzerkonten, Rollenwechsel
im System) erfolgt ausschließlich durch Personen mit bestehender ADMIN-Rolle und
wird über das Audit-Log des Systems protokolliert.

---

## 5. Inkrafttreten

Dieses Dokument tritt am **____ / ____ / 20____** in Kraft und wird bei jeder
Änderung einer administrativen Rolle aktualisiert.

---

**Unterschrift Praxisleitung:** _______________________________ Datum: ______________  

**Unterschrift (falls vorhanden) IT-Verantwortliche/r:** ______ Datum: ______________