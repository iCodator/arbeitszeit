# Architekturentscheidung: device_events / device_event_id

**Datum:** 2026-06-11  
**Grundlage:** `claude_code_anweisung_kritisch_arbeitszeit_v1_2026-06-11_19-42.md`  
**Schritte A.1 + A.2 kombiniert gemäß erlaubtem Vorgehen**

---

## 1. Kurzfassung

Der offene Architekturpunkt `device_events` / `device_event_id` wurde auf Basis
der Repository-Artefakte analysiert. Die Evidenz spricht eindeutig für **Pfad A1
(produktive Implementierung)**. Die Implementierung wurde am 2026-06-11 vollständig
abgeschlossen (Git-Commit `0f20931`). Dieses Dokument belegt die Entscheidung.

---

## 2. Dokumentiertes Sollbild (aus Artefakten)

| Artefakt | Stelle | Aussage |
|---|---|---|
| `planung_gesamt.md` | Z.61 | „Der vollständige produktive Verkettungspfad über `device_events` ist architektonisch vorgesehen, aber noch nicht operativ aktiviert." |
| `planung_gesamt.md` | Z.87 | Kern-Use-Case `buchen()` umfasst `device_events` in der Transaktionsbeschreibung |
| `planung_gesamt.md` | Z.92 | „Die Transaktionskette für `device_events` ist im Zielschnitt beschrieben, aber laut aktuellem Umsetzungsstand noch nicht vollständig im Produktionspfad aktiv." |
| `planung_gesamt.md` | Z.170 | „Die betriebliche End-to-End-Verkettung ist vorbereitet, aber laut aktuellem Stand noch nicht produktiv geschlossen. Dieser Punkt bleibt als offener Architekturpunkt markiert." |
| `phase4_planung.md` | Z.184–185 | „Abgrenzung Schritt 2: Stellt ausschließlich die **Schemafähigkeit** her. Die vollständige operative Nutzung (Hardware-Schicht erzeugt `device_events`, ID wird via `BookCommand.device_event_id` durchgereicht) ist Teil der größeren Infrastrukturkette." |
| `phase5_planung.md` | Z.5–11 | „Scope-Abgrenzung: Die operative Aktivierung der device_event_id-Verkettung ... ist bisher nicht operativ aktiviert — Infrastruktur ist vorbereitet, aber kein Produktionspfad schreibt derzeit device_events in die DB. Das ist ein dokumentierter offener Architekturpunkt, kein Planverstoß." |
| `migrations/0005_time_bookings_device_event_id.sql` | Vollständig | Table-Rebuild ergänzt `device_event_id INTEGER REFERENCES device_events(id)`, bestehende Zeilen mit `NULL` vorbelegt |

**Fazit Sollbild:** Die Verkettung ist im Sollbild ausdrücklich verlangt
(Transaktionsbeschreibung, Architekturüberblick, Device-Event-Verantwortungsteilung).
Sie wurde nur deshalb noch nicht umgesetzt, weil sie bewusst auf einen späteren
Implementierungsschritt verschoben worden war — nicht weil sie optional ist.

---

## 3. Tatsächliches Istbild vor Implementierung

Folgende Teilstücke waren vor dem 2026-06-11 vorhanden:

| Artefakt | Zustand |
|---|---|
| `migrations/0001_schema.sql` | `device_events`-Tabelle mit Spalten `id, event_type, terminal_id, rfid_uid_hash, payload_json, occurred_at, related_time_booking_id` |
| `migrations/0005_time_bookings_device_event_id.sql` | `time_bookings.device_event_id INTEGER REFERENCES device_events(id)` |
| `src/arbeitszeit/application/commands.py` | `BookCommand.device_event_id: int \| None` |
| `src/arbeitszeit/application/use_cases/book_time.py` | Übernahme von `cmd.device_event_id` in `TimeBooking` |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | `device_event_id=None` hard gesetzt — **kein device_events-Record erzeugt** |

**Operative Kette fehlend:** Es gab keinen produktiven Codepfad, der bei einem
echten Geräteereignis einen `device_events`-Datensatz anlegt und dessen ID an
`BookCommand.device_event_id` weiterreicht. Die Lücke war **technisch-operativ**,
nicht nur dokumentarisch.

---

## 4. Abweichungsanalyse (vor Implementierung)

| Dimension | Soll | Ist | Lückentyp |
|---|---|---|---|
| `device_events`-Record bei Buchung | wird erzeugt | nie erzeugt | operativ |
| `device_event_id` in BookCommand | echte ID | immer `None` | operativ |
| `time_bookings.device_event_id` | verweist auf Record | immer `NULL` | operativ |
| Repository für device_events | `DeviceEventRepository`-Port + Impl. | nicht vorhanden | technisch |
| Test der Kette | Kette nachweisbar getestet | kein Test vorhanden | dokumentarisch |

---

## 5. Evidenztabelle für Entscheidung

| Artefakt | Aussage zum Sollbild | Aussage zum Istbild | Bedeutung für Entscheidung |
|---|---|---|---|
| `planung_gesamt.md` Z.87 | `device_events` ist Teil der `buchen()`-Transaktion | Transaktion ohne device_events-Record | Implementierung erforderlich (Pfad A1) |
| `planung_gesamt.md` Z.170 | „End-to-End-Verkettung vorbereitet" | „noch nicht produktiv geschlossen" | Explizite Vorabentscheidung für A1 |
| `migrations/0005` | Schemaerweiterung als Vorbereitung | NULL-Werte in allen Zeilen | Vorbereitung war für A1 gedacht |
| `BookCommand.device_event_id` | Feld vorhanden, um ID durchzureichen | Immer `None` | Implementierungslücke, kein Sollbild-Widerspruch |
| `phase5_planung.md` Z.9 | „kein Planverstoß" | Architekturpunkt noch offen | Keine fachliche Ablehnung der Verkettung |

---

## 6. Empfohlene Entscheidung: **Pfad A1 — Produktive Implementierung**

Die Artefakte belegen eindeutig, dass die Verkettung zum Sollbild gehört
(Kern-Use-Case-Beschreibung, Architekturüberblick, Schema-Vorbereitung). Eine
formale Sollbildbereinigung (Pfad A2) wäre nicht durch Artefakte gedeckt.

---

## 7. Warum nicht Pfad A2?

Pfad A2 (formale Sollbildbereinigung) wäre nur vertretbar, wenn die Artefakte
belegen würden, dass die Verkettung **nicht** zum Sollbild gehört. Das ist nicht
der Fall:

- `planung_gesamt.md` Z.87 listet `device_events` als Pflichtinhalt der
  `buchen()`-Transaktion.
- Die Schema-Vorbereitung über Migration 0005 wäre ohne A1-Vorhaben unnötig gewesen.
- `phase5_planung.md` markiert den Punkt als „kein Planverstoß" — nicht als
  „nicht geplant".

---

## 8. Umgesetzte Implementierung (Pfad A1)

Commit `0f20931` vom 2026-06-11:

| Datei | Änderung |
|---|---|
| `src/arbeitszeit/domain/ports/repositories.py` | `DeviceEventRepository`-Protocol: `add(...) -> int` |
| `src/arbeitszeit/application/unit_of_work.py` | `device_event_repo: DeviceEventRepository` im Protocol |
| `src/arbeitszeit/infrastructure/db/repositories/device_event.py` (neu) | `SQLiteDeviceEventRepository.add()` mit `INSERT ... RETURNING id` |
| `src/arbeitszeit/infrastructure/db/repositories/__init__.py` | Export ergänzt |
| `src/arbeitszeit/infrastructure/db/unit_of_work.py` | `self.device_event_repo = SQLiteDeviceEventRepository(conn)` |
| `src/arbeitszeit/presentation/terminal_ui/booking_loop.py` | `RFID_SCAN`-Record erzeugen; ID an `BookCommand.device_event_id` |
| `tests/application/fakes.py` | `FakeDeviceEventRepository`; `FakeUnitOfWork.device_event_repo` |
| `tests/integration/test_device_event_booking.py` (neu) | 3 Tests: Erfolgsfall, UnknownCard, INSERT-Fehler |

**Transaktionsentscheidung (im Code dokumentiert):** Der `device_events`-INSERT
läuft im Autocommit-Modus vor dem `BEGIN` des `BookUseCase`. Der Record bleibt auch
bei fachlicher Buchungsabweisung (z. B. `UnknownCard`) erhalten — gewolltes
Audit-Trail-Verhalten. Schlägt der INSERT fehl, wird keine Buchung versucht.

---

## 9. Offene Restpunkte nach Implementierung

| Punkt | Beschreibung | Bewertung |
|---|---|---|
| `related_time_booking_id` | Spalte in `device_events` wird noch nicht befüllt (Rückverknüpfung) | Erweiterungsoption, nicht im ursprünglichen Sollbild als Pflicht beschrieben |
| Auswertung in `report_queries.py` | Keine JOIN-Abfragen über `device_events` | Optional; `time_bookings.device_event_id` reicht für Nachverfolgung |
| `BOOKING_ACCEPTED` / `BOOKING_REJECTED` event_types | Nach Buchungsergebnis nicht rückwirkend gesetzt | Kein Sollbild-Auftrag gefunden; als mögliche Erweiterung markieren |

---

## 10. Nicht entscheidbar auf Basis der vorliegenden Artefakte

- Ob `device_events` künftig auch für abgelehnte Buchungen mit `UNKNOWN_CARD`-/
  `INACTIVE_CARD`-event_type differenziert werden soll — kein belastbarer Auftrag
  im Repo gefunden. Aktuell werden alle Buchungsversuche als `RFID_SCAN` erfasst.
- Ob `related_time_booking_id` als Pflichtfeld nachgepflegt werden muss — keine
  explizite Anforderung in Pflichtenheft oder Regelwerk gefunden (nicht geprüft im
  Rahmen dieser Analyse).
