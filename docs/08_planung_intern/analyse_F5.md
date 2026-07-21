# Faktenanalyse F5: Verhalten bei Buchung kurz nach Mitternacht

## Grundlage der Kalendertag-Bestimmung

Die einzige Implementierung von `list_for_employee_on_day()` befindet sich in
[infrastructure/db/repositories/time_booking.py:58–68](../../src/arbeitszeit/infrastructure/db/repositories/time_booking.py).

Die Funktion bestimmt den Kalendertag ausschließlich durch Extraktion des
UTC-Datums aus dem übergebenen `day`-Parameter und baut daraus ein Zeitfenster:

```python
day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
next_day = day_start + timedelta(days=1)
```

Gesucht werden alle Buchungen mit `booked_at >= day_start AND booked_at < next_day`.
Ein Kommentar in derselben Funktion (Zeile 59–60) lautet:

> `day` muss ein UTC-Kalendertag sein, konsistent mit UTC-normalisierten
> booked_at-Werten. Die Application-Schicht ist verantwortlich für die
> Normalisierung vor dem Aufruf.

Der `day`-Parameter wird in `BookUseCase.execute()` durch `cmd.booked_at.date()`
erzeugt ([book_time.py:101](../../src/arbeitszeit/application/use_cases/book_time.py)).
`cmd.booked_at` entspricht `request.occurred_at`, das in
[evdev_reader.py:223](../../src/arbeitszeit/infrastructure/hardware/evdev_reader.py)
als `datetime.now(timezone.utc)` gesetzt wird — also dem UTC-Zeitstempel des
Scan-Abschlusses.

Es existiert keine andere Logik (kein schichtbezogener Cutoff, kein
Zeitfenstermechanismus, keine lokale Zeitzonenkorrektur) zur Bestimmung des
Kalendertags.

## Verhalten bei Buchung kurz nach Mitternacht

**Belegte Fakten:**

Im Beispielfall COME am Vortag (UTC) um 22:00 Uhr, nächster Scan um 00:30 Uhr
(UTC am Folgetag):

1. `datetime.now(timezone.utc)` liefert für den Scan um 00:30 Uhr einen
   Zeitstempel mit dem UTC-Datum des Folgetags
   ([evdev_reader.py:223](../../src/arbeitszeit/infrastructure/hardware/evdev_reader.py)).

2. `BookUseCase.execute()` ruft `.date()` auf diesem Zeitstempel auf und erhält
   das Folgetag-Datum ([book_time.py:101](../../src/arbeitszeit/application/use_cases/book_time.py)).

3. `list_for_employee_on_day()` baut daraus das Fenster
   `[00:00:00 UTC Folgetag, 00:00:00 UTC übernächster Tag)`
   ([time_booking.py:61–62](../../src/arbeitszeit/infrastructure/db/repositories/time_booking.py)).

4. Die COME-Buchung vom Vortag (22:00 UTC) liegt außerhalb dieses Fensters und
   wird nicht zurückgegeben.

5. `day_bookings` ist leer; `validate_booking_sequence()` sieht keine
   Tagesbuchungen für das Folgetag-Datum.

6. `_validate_first_booking()` in
   [booking_rules.py:27–29](../../src/arbeitszeit/domain/services/booking_rules.py)
   prüft, ob der Buchungstyp für eine erste Tagesbuchung zulässig ist.
   Bei einem COME-Scan würde kein Fehler geworfen.

**Tatsachenantwort:** Die Buchung um 00:30 Uhr (UTC) wird als erste Buchung
eines neuen Kalendertags behandelt (Zustand 0 — keine Buchung vorhanden). Es
gibt keinen Mechanismus, der sie dem Vortag oder einer vorangegangenen Schicht
zuordnet.

**Nebeneffekt (belegt):** Der Ruhezeitcheck `_check_rest_period_flags()` in
[_booking_evaluation.py:31–44](../../src/arbeitszeit/application/use_cases/_booking_evaluation.py)
nutzt `prev_bookings`, die über
`list_for_employee_on_day(employee.id, cmd.booked_at.date() - timedelta(days=1))`
ermittelt werden ([book_time.py:120–121](../../src/arbeitszeit/application/use_cases/book_time.py)).
Im Beispielfall würde die COME-Buchung um 22:00 UTC als letzte Buchung des
Vortags gefunden und damit die Ruhezeit zwischen dem GO des Vortags (falls
vorhanden) und dem COME des Folgetags geprüft. Diese Prüfung läuft über ein
separates Datumsfenster und ist von der Tagessequenz-Logik unabhängig.

## Vorhandene Tests zu diesem Verhalten

Keine vorhanden. Die Testdateien enthalten keine Tests, die Zeitstempel über
Mitternacht (UTC) hinweg modellieren oder das Verhalten von
`list_for_employee_on_day()` bei einem Tageswechsel während eines offenen
Tagesablaufs prüfen. Dies wurde durch vollständige Suche nach den Mustern
`00:30`, `T23:`, `T00:`, `midnight`, `tageswechsel` in allen Testdateien
bestätigt — kein Treffer mit Bezug zu diesem Szenario.

## Explizite Hinweise auf bewusste Nicht-Behandlung

Keine vorhanden. Es gibt im gesamten Produktivcode keinen Kommentar, kein TODO,
kein FIXME und keine dokumentierte Einschränkung, die den Mitternachtsübergang
oder Schichtmodelle über Tagesgrenzen hinweg thematisiert.

Der einzige Hinweis auf die UTC-Grundlage ist der Kommentar in
[time_booking.py:59–60](../../src/arbeitszeit/infrastructure/db/repositories/time_booking.py),
der jedoch ausschließlich die Konsistenz der UTC-Normalisierung beschreibt,
nicht die Frage der Schichtzuordnung.

## Nicht eindeutig feststellbare Punkte

Keine. Das Verhalten ist aus dem Code vollständig und eindeutig bestimmbar:
Der Kalendertag wird ausschließlich durch das UTC-Datum des `booked_at`-Zeitstempels
bestimmt; eine Zuordnung zu einem vorangegangenen Arbeitstag existiert nicht.
