# Die Spielregeln des Systems

**Kapitel:** 2.1-Laien
**Version:** 1.0
**Stand:** Juli 2026
**Zielgruppe:** Praxisleitung, Verwaltung

## Was sind die Spielregeln?

Das Zeiterfassungssystem kennt feste Regeln, wann welche Buchung erlaubt
ist und wann eine Arbeitszeit als problematisch gilt. Diese Regeln sind
fest im System verankert und können nicht umgangen werden.

## Welche Buchungsarten gibt es?

Jede Buchung hat genau einen von vier Typen:

| Buchungstyp | Bedeutung |
| --- | --- |
| Kommen | Arbeitsbeginn |
| Gehen | Arbeitsende |
| Pause beginnt | Beginn einer Pause |
| Pause endet | Ende einer Pause |

## In welcher Reihenfolge müssen Buchungen erfolgen?

Das System prüft, ob jede neue Buchung zur bisherigen Tageshistorie passt.
Folgende Regeln gelten:

| Neue Buchung | Erlaubt wenn... |
| --- | --- |
| Kommen | noch kein Arbeitsbeginn heute |
| Gehen | Arbeitsbeginn vorhanden, keine offene Pause |
| Pause beginnt | Arbeitsbeginn vorhanden, keine offene Pause |
| Pause endet | offene Pause vorhanden |

**Beispiel:** Wenn eine Mitarbeiterin auf Pause gegangen ist und dann
versucht, auf Gehen zu buchen, zeigt das Terminal eine Fehlermeldung —
die Pause muss zuerst beendet werden.

Das erste Buchungsereignis des Tages muss immer eine Kommen-Buchung sein.

## Arbeitszeitgrenzen nach dem Arbeitszeitgesetz

Das System prüft automatisch, ob die erfassten Zeiten die gesetzlichen
Grenzen einhalten. Bei Verstößen oder Warnungen wird ein Prüffall angelegt,
der von Ihnen oder einem Prüfer bearbeitet werden muss.

### Höchstarbeitszeit (§3 ArbZG)

| Situation | Bewertung |
| --- | --- |
| Netto-Arbeitszeit über 10 Stunden | Kritisch — Prüffall |
| Netto-Arbeitszeit über 8 Stunden | Warnung |

### Pausenvorschriften (§4 ArbZG)

| Situation | Bewertung |
| --- | --- |
| Arbeitsabschnitt ohne Unterbrechung länger als 6 Stunden | Warnung |
| Netto über 9 Stunden, aber weniger als 45 Minuten Pause insgesamt | Kritisch — Prüffall |
| Netto über 6 Stunden, aber weniger als 30 Minuten Pause insgesamt | Warnung |

### Ruhezeit (§5 ArbZG)

| Situation | Bewertung |
| --- | --- |
| Weniger als 11 Stunden zwischen Arbeitsende und nächstem Arbeitsbeginn | Kritisch — Prüffall |

## Was ist ein Prüffall?

Wenn das System eine Regelauffälligkeit erkennt — entweder eine
ArbZG-Verletzung oder eine unplausible Buchungssequenz — legt es
automatisch einen Prüffall an. Prüffälle erscheinen im Bericht
„Offene Prüffälle" (`reports open-review-cases`) und müssen von
Ihnen oder einem Prüfer bearbeitet werden.

## Was ist ein Nachtrag?

Wenn eine Buchung vergessen oder falsch erfasst wurde, kann ein
Nachtrag angelegt werden. Ein Nachtrag ist eine manuelle Buchungsergänzung,
die genehmigt werden muss, bevor sie wirksam wird. Nachträge und
Genehmigungen werden im Haupthandbuch unter Kapitel 5 beschrieben.

## Was ist eine Korrektur?

Eine Korrektur ändert eine bereits vorhandene Buchung (z. B. falsche
Uhrzeit). Sie wird ebenfalls in Kapitel 5 des Haupthandbuchs beschrieben.
Korrekturen werden im System dauerhaft protokolliert und sind nicht
rückgängig zu machen.
