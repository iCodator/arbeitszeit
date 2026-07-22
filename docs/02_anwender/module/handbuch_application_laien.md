# Was passiert im Hintergrund?

**Kapitel:** 3-Laien
**Version:** 1.1
**Stand:** Juli 2026
**Zielgruppe:** Praxisleitung, Verwaltung

## Übersicht

Dieses Kapitel erklärt in einfacher Sprache, was das System im Hintergrund
macht — wenn eine Mitarbeiterin bucht, wenn Sie eine Korrektur vornehmen
oder einen Nachtrag anlegen.

## Was passiert bei einer Buchung am Terminal?

Wenn eine Mitarbeiterin ihre RFID-Karte ans Terminal hält, läuft im
Hintergrund folgendes ab:

1. Das System prüft, ob die Karte bekannt und aktiv ist.
2. Es prüft, ob die Mitarbeiterin aktiv ist.
3. Es ermittelt automatisch die nächste Buchungsart anhand der bisherigen
   Tageshistorie (Kommen → Pause beginnt → Pause endet → Gehen).
   Bei einem Kurztag (Solldauer ≤ 6 h) entfällt der Pausenschritt —
   der 2. Scan bucht direkt Gehen.
4. Es prüft, ob die ermittelte Buchungsart zur Tageshistorie passt.
5. Es speichert die Buchung.
6. Es prüft automatisch, ob Arbeitszeitgrenzen erreicht oder überschritten sind.
7. Das Terminal zeigt eine Bestätigung an.

Wenn eine dieser Prüfungen fehlschlägt, erscheint eine klare Fehlermeldung
auf dem Terminal (z. B. „Unbekannte Karte" oder „Pause zuerst beenden").

### Buchungsstatus

Nach der Buchung erhält jede Buchung automatisch einen Status:

| Status | Bedeutung |
| --- | --- |
| Offen | Kommen oder Pause-Start ohne passendes Ende |
| In Ordnung | Regelkonforme, abgeschlossene Buchung |
| Warnung | ArbZG-Warnschwelle erreicht |
| Prüffall | Kritische ArbZG-Verletzung oder Anomalie — muss bearbeitet werden |
| Korrigiert | Nachträglich korrigiert |

## Was passiert bei einer Korrektur?

Wenn Sie eine Buchung korrigieren (z. B. falsche Uhrzeit), legt das System
einen dauerhaften Korrektureintrag an. Die ursprüngliche Buchung wird nicht
gelöscht, sondern als „korrigiert" markiert. Der Korrekturgrund und der
durchführende Benutzer werden protokolliert.

Korrekturen sind nur für bestimmte Arten von Prüffällen möglich. Einige
Situationen (z. B. unbekannte Kartenzugriffe) können nicht per Korrektur
bereinigt werden, sondern müssen anders behandelt werden.

## Was passiert bei einem Nachtrag?

Ein Nachtrag ist eine manuelle Buchungsergänzung — zum Beispiel wenn eine
Mitarbeiterin vergessen hat zu stempeln. Der Ablauf ist zweistufig:

1. **Anlegen:** Sie oder ein Prüfer legen den Nachtrag mit Grund an.
   Der Nachtrag erhält zunächst den Status „Ausstehend".
2. **Genehmigen oder Ablehnen:** Ein Prüfer oder Admin genehmigt oder
   lehnt den Nachtrag ab.
   - Bei Genehmigung wird die Buchung automatisch angelegt und erneut
     auf Arbeitszeitgrenzen geprüft.
   - Bei Ablehnung bleibt die Buchung unverändert.

## Wer darf was tun?

Das System kennt drei Benutzerrollen für die Verwaltung:

| Rolle | Kann... |
| --- | --- |
| Admin | Alles: Mitarbeitende, Karten, Buchungen, Berichte, Benutzer |
| Prüfer | Prüffälle bearbeiten, Nachträge anlegen und genehmigen/ablehnen, Buchungen korrigieren |
| Techniker | Technische Betriebsaufgaben |

Die Rolle „Mitarbeitender" kann keinen Admin-CLI-Zugang erhalten.

## Rollen einrichten

Benutzerkonten und Rollen werden über den Befehl `users add` angelegt.
Beim ersten Start des Systems muss ein erster Admin-Account über
`users bootstrap` eingerichtet werden. Das ist nur möglich, wenn noch
kein aktiver Admin vorhanden ist.
