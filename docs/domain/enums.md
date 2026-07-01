# Enums – src/arbeitszeit/domain/enums.py

## Geltungsbereich dieser Dokumentation

Diese Dokumentation bezieht sich ausschließlich auf den tatsächlichen
Quelltext von `src/arbeitszeit/domain/enums.py` (Commit-SHA
`27545ddc1167578020cde8ab3dce75f1803cac21`). Alle Aussagen zu Klassennamen,
Basisklassen und Wertelisten sind direkt aus dem Quelltext belegt. Aussagen
zur fachlichen Bedeutung einzelner Werte sind, sofern nicht anders
gekennzeichnet, **nicht** durch Docstrings oder Kommentare im Quelltext
belegt, da die Datei keinerlei Docstrings oder Kommentare enthält.

## Technische Basis

Alle Enums in dieser Datei erben von `StrEnum` aus dem Standardmodul `enum`
(Python 3.11+). Dadurch ist jeder Enum-Wert zugleich ein gültiger `str` und
kann direkt in SQLite-Spalten, JSON-Strukturen oder String-Vergleichen
verwendet werden, ohne explizite Konvertierung. Bei allen elf Enums ist der
String-Wert identisch zum Bezeichnernamen (z. B. `COME = "COME"`); dies ist
im Quelltext durchgehend so belegt und wird nicht als Zufall, sondern als
konsistentes Namensmuster der gesamten Datei dokumentiert.

## BookingType

Definiert die Art einer Zeitbuchung.

- `COME = "COME"`
- `GO = "GO"`
- `BREAK_START = "BREAK_START"`
- `BREAK_END = "BREAK_END"`

Hinweis: Die Datei enthält keinen Docstring und keinen Kommentar zu diesem
Enum. Die vier Werte sind vollständig und ausschließlich aus dem Quelltext
übernommen; eine weitergehende fachliche Definition (z. B. ob Pausen mehrfach
pro Tag zulässig sind) ist im Quelltext nicht enthalten und wird hier nicht
unterstellt.

## BookingStatus

Definiert den Status einer einzelnen Buchung.

- `OK = "OK"`
- `OPEN = "OPEN"`
- `WARN = "WARN"`
- `NEEDS_REVIEW = "NEEDS_REVIEW"`
- `CORRECTED = "CORRECTED"`
- `CLOSED_WITH_NOTE = "CLOSED_WITH_NOTE"`

Hinweis: Sechs Werte, vollständig im Quelltext belegt. Keine Aussage im
Quelltext dazu, welche Übergänge zwischen diesen Status zulässig sind; ein
Zustandsautomat ist an dieser Stelle nicht dokumentiert und müsste separat in
der zugehörigen Fachlogik geprüft werden.

## ReviewCaseType

Definiert den Typ eines Prüffalls (Review-Case).

- `OPEN_WORK_PHASE = "OPEN_WORK_PHASE"`
- `OPEN_BREAK_PHASE = "OPEN_BREAK_PHASE"`
- `OUTSIDE_SCHEDULE_WINDOW = "OUTSIDE_SCHEDULE_WINDOW"`
- `POSSIBLE_BREAK_VIOLATION = "POSSIBLE_BREAK_VIOLATION"`
- `POSSIBLE_REST_VIOLATION = "POSSIBLE_REST_VIOLATION"`
- `POSSIBLE_MAX_HOURS_VIOLATION = "POSSIBLE_MAX_HOURS_VIOLATION"`
- `IMPLAUSIBLE_SEQUENCE = "IMPLAUSIBLE_SEQUENCE"`
- `UNKNOWN_CARD_ATTEMPT = "UNKNOWN_CARD_ATTEMPT"`
- `INACTIVE_CARD_ATTEMPT = "INACTIVE_CARD_ATTEMPT"`
- `TIME_ANOMALY = "TIME_ANOMALY"`
- `MANUAL_ENTRY_REVIEW = "MANUAL_ENTRY_REVIEW"`

Hinweis: Elf Werte, vollständig im Quelltext belegt; dies ist das
umfangreichste Enum der Datei. Die Bezeichner legen thematische Gruppen nahe
(Arbeitszeitgesetz-Verstöße, Kartenprobleme, Zeitanomalien, manuelle
Prüfung), diese Gruppierung ist jedoch eine strukturelle Beobachtung des
Dokumentierenden und keine im Quelltext explizit vorgenommene Kategorisierung.

## ReviewCaseStatus

Definiert den Bearbeitungsstatus eines Prüffalls.

- `OPEN = "OPEN"`
- `IN_REVIEW = "IN_REVIEW"`
- `RESOLVED = "RESOLVED"`
- `CLOSED_WITH_NOTE = "CLOSED_WITH_NOTE"`

Hinweis: Vier Werte, vollständig im Quelltext belegt. Der Wert
`CLOSED_WITH_NOTE` existiert identisch auch in `BookingStatus`; beide Enums
sind im Quelltext als eigenständige, nicht miteinander verknüpfte Klassen
definiert.

## ReviewSeverity

Definiert den Schweregrad eines Prüffalls.

- `INFO = "INFO"`
- `WARN = "WARN"`
- `CRITICAL = "CRITICAL"`

Hinweis: Drei Werte, vollständig im Quelltext belegt. Der Wert `WARN`
existiert identisch auch in `BookingStatus`; eine gemeinsame Basis oder
Ableitung zwischen beiden Enums ist im Quelltext nicht vorhanden, beide
Klassen sind unabhängig definiert.

## CardStatus

Definiert den Status einer RFID-Karte.

- `ACTIVE = "ACTIVE"`
- `INACTIVE = "INACTIVE"`
- `REPLACED = "REPLACED"`
- `LOST = "LOST"`

Hinweis: Vier Werte, vollständig im Quelltext belegt. Keine Aussage im
Quelltext dazu, ob eine als `LOST` markierte Karte reaktivierbar ist oder ob
`REPLACED` automatisch mit der Anlage einer neuen Karte verknüpft wird.

## UserRole

Definiert die Rolle eines Systembenutzers.

- `EMPLOYEE = "EMPLOYEE"`
- `ADMIN = "ADMIN"`
- `REVIEWER = "REVIEWER"`
- `TECH = "TECH"`

Hinweis: Vier Werte, vollständig im Quelltext belegt. Keine Aussage im
Quelltext zu Rechten oder Rollenhierarchien; dies wäre in einer separaten
Autorisierungslogik zu prüfen, die in dieser Datei nicht enthalten ist.

## BookingSource

Definiert die Herkunft einer Buchung.

- `TERMINAL = "TERMINAL"`
- `MANUAL = "MANUAL"`
- `IMPORT = "IMPORT"`

Hinweis: Drei Werte, vollständig im Quelltext belegt. Keine Aussage im
Quelltext dazu, ob `IMPORT`-Buchungen automatisch einen Prüffall auslösen.

## ChangeOrigin

Definiert die Herkunft einer nachträglichen Änderung.

- `SYSTEM_SEED = "SYSTEM_SEED"`
- `ADMIN_UI = "ADMIN_UI"`
- `MIGRATION = "MIGRATION"`

Hinweis: Drei Werte, vollständig im Quelltext belegt. Der Name legt nahe,
dass dieses Enum für das Audit-Log verwendet wird; diese Verwendung ist
jedoch nicht Teil der Datei `enums.py` selbst und daher hier nicht belegt.

## ApprovalStatus

Definiert den Freigabestatus eines Vorgangs.

- `PENDING = "PENDING"`
- `APPROVED = "APPROVED"`
- `REJECTED = "REJECTED"`

Hinweis: Drei Werte, vollständig im Quelltext belegt. Keine Aussage im
Quelltext dazu, welche Entität (z. B. Korrekturantrag) diesen Status trägt.

## ScopeType

Definiert die Gültigkeitsebene einer Einstellung oder Regel.

- `GLOBAL = "GLOBAL"`
- `EMPLOYEE = "EMPLOYEE"`

Hinweis: Zwei Werte, vollständig im Quelltext belegt. Dies ist das kleinste
Enum der Datei; keine weitere Untergliederung (z. B. Praxis-Ebene) ist im
Quelltext vorhanden.

## Was diese Datei nicht enthält

- Keine Docstrings oder Kommentare zu Zweck oder Semantik der Enums.
- Keine Validierungslogik, keine Methoden, keine Property-Definitionen.
- Keine Verknüpfung der Enums zu Datenbanktabellen, Spalten oder anderen
  Modulen; solche Verknüpfungen wären ausschließlich in anderen Dateien zu
  prüfen und sind hier nicht Gegenstand.
- Keine Import-Abhängigkeiten außer `from enum import StrEnum`.

## Offene Punkte für Rückfrage

- Sollen zulässige Statusübergänge (z. B. für `BookingStatus` oder
  `ReviewCaseStatus`) in einer separaten State-Machine-Dokumentation
  festgehalten werden, da sie im Quelltext dieser Datei nicht abgebildet
  sind?
- Ist die Dopplung der Werte `WARN` und `CLOSED_WITH_NOTE` über mehrere Enums
  hinweg beabsichtigt oder sollte sie langfristig vereinheitlicht werden?
