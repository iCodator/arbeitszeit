# Prüfbericht: Entfernung `src/arbeitszeit/presentation/admin_gui/` aus `main`

**Geprüft am:** 04.07.2026  
**Basis-Branch:** `main`  
**Geprüfter Bereich:**

- Code: `src/arbeitszeit/presentation/` [cite:31]
- Handbuch-Module:
  - `docs/02_anwender/module/handbuch_presentation.md` [cite:39]
  - `docs/02_anwender/module/handbuch_overview.md` [cite:40]
- Verzeichnisstruktur: `docs/verzeichnisstruktur_arbeitszeit.md` [cite:36]
- README: `README.md` [cite:41]
- Prüfbericht Präsentationsschicht: `docs/07_pruefberichte/handbuch/pruefbericht_presentation.md` [cite:30]
- Installations- und Referenzdokumente (nur Existenz geprüft, Inhalt hier nicht vollständig ausgewertet):
  - `docs/03_installation_technik/befehlsreferenz_arbeitszeit.md` [cite:42]
  - `docs/03_installation_technik/installationsanleitung_arbeitszeit.md` [cite:42]
- Gesamt-Handbuch (nur Existenz geprüft, Inhalt hier nicht vollständig ausgewertet):
  - `docs/02_anwender/handbuch_arbeitszeit.md` [cite:37]

## 1 Ausgangslage und Codebefund

### 1.1 Präsentationsschicht im Branch `main`

- Das Verzeichnis `src/arbeitszeit/presentation/` enthält im aktuellen `main`-Branch nur noch: [cite:31]
  - `__init__.py`
  - `admin_cli/`
  - `terminal_ui/`

- Ein Verzeichnis `src/arbeitszeit/presentation/admin_gui/` existiert im aktuellen `main`-Branch nicht mehr. [cite:31]

- Eine Code-Suche im Repository nach `admin_gui` liefert auf `main` keine Treffer. [cite:33]

- Eine weitere Code-Suche nach `tkinter` liefert auf `main` ebenfalls keine Treffer. [cite:35]

**Bewertung:**  
Es ist eindeutig belegt, dass die Admin-GUI (`admin_gui/`) im aktuellen `main`-Branch entfernt wurde und keine Referenzen auf `admin_gui` oder `tkinter` mehr im `main`-Branch vorhanden sind. [cite:31][cite:33][cite:35]

## 2 Handbuch Präsentationsschicht und Überblick

### 2.1 `docs/02_anwender/module/handbuch_presentation.md`

**Relevante Aussagen:**

1. Die Präsentationsschicht gliedert sich in zwei eigenständige Untermodule: [cite:39]
   - `presentation/terminal_ui/` – operativer Buchungsbetrieb
   - `presentation/admin_cli/` – administrative Verwaltung

2. `admin_gui/` wird im Dokument nicht erwähnt. [cite:39]

**Bewertung je Aussage:**

- Aussage 1 (zwei Untermodule `terminal_ui/`, `admin_cli/`):
  - **Status:** korrekt
  - **Beleg:** `src/arbeitszeit/presentation/` enthält auf `main` nur `admin_cli/` und `terminal_ui/`. [cite:31]
  - **Bewertung:** Die Strukturangabe stimmt exakt mit der aktuellen Präsentationsschicht im Branch `main` überein. [cite:31][cite:39]

- Aussage 2 (keine Erwähnung von `admin_gui/`):
  - **Status:** korrekt
  - **Beleg:** Vollständige Quelldatei `handbuch_presentation.md` enthält keinen Hinweis auf `admin_gui`. [cite:39]
  - **Bewertung:** Das Präsentationskapitel ist konsistent mit der aktuellen Codebasis im Branch `main`. [cite:31][cite:39]

**Anpassungsvorschlag:**  
Keine; das Kapitel ist für den aktuellen `main`-Stand korrekt. [cite:31][cite:39]

### 2.2 `docs/02_anwender/module/handbuch_overview.md`

**Relevante Aussagen:**

1. Der Projektstruktur-Ausschnitt zeigt unter `src/arbeitszeit/presentation/` die Verzeichnisse `admin_cli/` und `terminal_ui/`. [cite:40]

2. Es wird festgehalten, dass aus dem Repository eindeutig ein Terminalmodus und eine Admin-CLI belegt sind. [cite:40]

**Bewertung je Aussage:**

- Aussage 1 (Struktur mit `admin_cli/` und `terminal_ui/`):
  - **Status:** korrekt
  - **Beleg:** Verzeichnislisting `src/arbeitszeit/presentation/` auf `main` ohne `admin_gui/`. [cite:31]
  - **Bewertung:** Die angegebene Struktur stimmt mit der tatsächlichen Verzeichnisstruktur überein. [cite:31][cite:40]

- Aussage 2 (belegte Oberflächen: Terminalmodus und Admin-CLI):
  - **Status:** korrekt
  - **Beleg:** Es existieren die Verzeichnisse `terminal_ui/` und `admin_cli/`, weitere Präsentationsschichten sind nicht vorhanden. [cite:31][cite:39][cite:40]
  - **Bewertung:** Die Aussage ist durch den Code eindeutig gedeckt. [cite:31][cite:39][cite:40]

**Anpassungsvorschlag:**  
Keine. [cite:31][cite:40]

### 2.3 `docs/verzeichnisstruktur_arbeitszeit.md`

**Relevante Aussagen zur Präsentationsschicht:**

- Das Dokument beschreibt unter `src/arbeitszeit/presentation/` zwei Untermodule: `terminal_ui/` und `admin_cli/`. [cite:36]

- `admin_gui/` wird nicht erwähnt. [cite:36]

**Bewertung:**

- **Status:** korrekt  
- **Beleg:** Verzeichnislisting `src/arbeitszeit/presentation/` auf `main` enthält kein `admin_gui/`. [cite:31]  
- **Bewertung:** Die Verzeichnisbeschreibung der Präsentationsschicht ist konsistent mit dem aktuellen `main`. [cite:31][cite:36]

**Anpassungsvorschlag:**  
Keine. [cite:31][cite:36]

### 2.4 `README.md`

**Relevante Aussagen zur Präsentationsschicht:**

- Systemumfang-Tabelle:
  - Terminalbetrieb mit Einstiegspunkt `src/arbeitszeit/presentation/terminal_ui/main.py`. [cite:41]
  - Admin-CLI mit Modulen unter `src/arbeitszeit/presentation/admin_cli/`. [cite:41]

- Projektstruktur-Tabelle:
  - Listet `src/arbeitszeit/presentation/terminal_ui/` und `src/arbeitszeit/presentation/admin_cli/` als Präsentationskomponenten. [cite:41]

- Es findet sich keine Erwähnung von `admin_gui/`. [cite:41]

**Bewertung:**

- **Status:** korrekt  
- **Beleg:** Verzeichnisstruktur der Präsentationsschicht auf `main` (nur `terminal_ui/` und `admin_cli/`). [cite:31][cite:41]  
- **Bewertung:** Der README-Stand ist konsistent mit der aktuellen Codebasis im Branch `main`. [cite:31][cite:41]

**Anpassungsvorschlag:**  
Keine. [cite:31][cite:41]

### 2.5 `docs/02_anwender/handbuch_arbeitszeit.md`

**Geprüft:**

- Die Datei wurde in diesem Durchgang nicht vollständig inhaltlich analysiert. Es ist lediglich belegt, dass sie existiert und das konsolidierte Handbuch darstellt. [cite:37]

**Bewertung bzgl. `admin_gui`:**

- **Status:** nicht verifizierbar
- **Beleg:** Kein Volltext-Abgleich im Rahmen dieses Prüfberichts. [cite:37]
- **Bewertung:** Ob in dieser konsolidierten Handbuchdatei noch historische Hinweise auf `admin_gui` enthalten sind, ist mit den hier durchgeführten Schritten nicht eindeutig feststellbar. [cite:37]

**Anpassungsvorschlag:**

- Volltextsuche (außerhalb dieses Prüfberichts) in `docs/02_anwender/handbuch_arbeitszeit.md` nach:
  - `admin_gui`
  - `GUI`
  - `tkinter`
  - eindeutigen Startbefehlen wie `python -m arbeitszeit.presentation.admin_gui.main`

Solange diese Suche nicht erfolgt ist, bleibt der Status bzgl. `admin_gui` „nicht verifizierbar“. [cite:37]

## 3 Bestands-Prüfbericht Präsentationsschicht

### 3.1 `docs/07_pruefberichte/handbuch/pruefbericht_presentation.md`

**Metadaten und Kontext:**

- Geprüft am: 03.07.2026
- Basis-Commit: `e3fbb0d0985d7f98ba0dac5cec86a28f7d6ad302`
- Geprüfte Quelle: `src/arbeitszeit/presentation/` (terminal_ui/, admin_cli/, admin_gui/) [cite:30]

**Relevante Aussagen mit Bezug zu `admin_gui`:**

1. Im Header wird `admin_gui/` als Teil der geprüften Quelle aufgeführt. [cite:30]

2. In der Gesamteinschätzung wird kritisiert, dass das Präsentationshandbuch nur zwei Untermodule nennt, obwohl ein drittes Untermodul `admin_gui/` existiert. [cite:30]

3. Im Befund zur Aussage „zwei eigenständige Untermodule" werden als Beleg genannt:
   - Datei `src/arbeitszeit/presentation/admin_gui/main.py` mit Docstring zur Admin-GUI und Einstieg `python -m arbeitszeit.presentation.admin_gui.main`.
   - Commit `f4cef2c` mit der Beschreibung einer neuen Admin-GUI. [cite:30]

4. Im Abschnitt „Offene Punkte" wird festgehalten, dass der Funktionsumfang der Admin-GUI nur oberflächlich gesichtet wurde und eine vollständige Feature-Prüfung noch fehlt. [cite:30]

5. Ebenfalls im Abschnitt „Offene Punkte" wird erwähnt, dass es für `admin_cli/` und `admin_gui/` keine spezifischen Testdateien gibt. [cite:30]

**Bewertung je Aussage gegen den aktuellen `main`:**

- Aussage 1 (Header nennt `admin_gui/` als geprüfte Quelle):
  - **Status:** inkorrekt für den aktuellen `main`
  - **Beleg:** `admin_gui/` existiert im aktuellen `main` nicht. [cite:31]
  - **Bewertung:** Der Prüfbericht dokumentiert hier explizit einen Zustand, der im aktuellen `main` nicht mehr vorliegt. Als laufender Prüfstatus für `main` ist diese Angabe falsch. [cite:30][cite:31]

- Aussage 2 (Handbuch nennt nur zwei Untermodule, obwohl `admin_gui/` existiert):
  - **Status:** inkorrekt für den aktuellen `main`
  - **Beleg:** `handbuch_presentation.md` nennt zwei Untermodule (`terminal_ui/` und `admin_cli/`), und im Code existieren auf `main` genau diese beiden Unterverzeichnisse; `admin_gui/` ist entfernt. [cite:31][cite:39]
  - **Bewertung:** Die damalige Kritik war bezogen auf den damaligen Stand korrekt, ist nach Entfernung von `admin_gui/` aus `main` aber nicht mehr zutreffend. [cite:30][cite:31][cite:39]

- Aussage 3 (Beleg mit `admin_gui/main.py` und Commit `f4cef2c`):
  - **Status:** nicht verifizierbar auf aktuellem `main`
  - **Beleg:** Die Datei `admin_gui/main.py` ist auf `main` nicht mehr vorhanden; der genannte Commit ist auf `main` nicht aus der aktuellen Struktur ersichtlich. [cite:31][cite:30]
  - **Bewertung:** Der Beleg beschreibt eine historische Codebasis bzw. einen anderen Branch. Für den aktuellen `main` ist er nicht anwendbar. [cite:30][cite:31]

- Aussage 4 (Offener Punkt „Funktionsumfang der Admin-GUI nur oberflächlich gesichtet"):
  - **Status:** gegenstandslos im Kontext `main`
  - **Beleg:** `admin_gui/` ist auf `main` nicht vorhanden. [cite:31]
  - **Bewertung:** Die offene Aufgabe betrifft nur noch den Branch, in dem `admin_gui/` weiterentwickelt wird, nicht den Branch `main`. [cite:30][cite:31]

- Aussage 5 (Offener Punkt „keine spezifischen Testdateien für `admin_cli/` und `admin_gui/`"):
  - **Status:** teilweise korrekt, teilweise gegenstandslos
  - **Beleg:**
    - Keine spezifischen Tests für `admin_cli/` sind im `tests/`-Verzeichnis belegt. [cite:36]
    - `admin_gui/` existiert auf `main` nicht. [cite:31]
  - **Bewertung:** Der Teil zur Admin-GUI ist gegenstandslos geworden; der Hinweis auf fehlende spezifische Tests für `admin_cli/` ist weiterhin zutreffend. [cite:30][cite:31][cite:36]

**Anpassungsvorschlag (nur Befund, nicht umgesetzt):**

- Header und Gesamteinschätzung so anpassen, dass klar ist:
  - `admin_gui/` war zum Zeitpunkt dieser Prüfung Bestandteil eines anderen Branches bzw. eines früheren Stands, ist aber im aktuellen `main` nicht mehr vorhanden. [cite:30][cite:31]
  - Die Kritik an der Zahl der Untermodule im Handbuch bezieht sich nur auf den damaligen Zustand.

- `admin_gui`-bezogene offene Punkte als historische Notizen kennzeichnen oder in einen eigenständigen Prüfbericht für den Branch `admin_gui` auslagern. [cite:30][cite:31]

## 4 Installations- und Befehlsdokumentation

### 4.1 `docs/03_installation_technik/befehlsreferenz_arbeitszeit.md`

**Geprüft:**

- Die Datei wurde in diesem Durchgang nicht im Volltext ausgewertet; nur Existenz und Pfad sind belegt. [cite:42]

**Bewertung bzgl. möglicher `admin_gui`-Erwähnungen:**

- **Status:** nicht verifizierbar
- **Beleg:** Kein inhaltlicher Vollabgleich im Rahmen dieses Prüfberichts. [cite:42]

**Anpassungsvorschlag:**

- Volltextsuche in dieser Datei nach:
  - `admin_gui`
  - `GUI`
  - `tkinter`
  - `python -m arbeitszeit.presentation.admin_gui.main`

Ohne diese Prüfung kann nicht ausgeschlossen werden, dass ältere Hinweise auf eine GUI in der Befehlsreferenz verblieben sind. [cite:42]

### 4.2 `docs/03_installation_technik/installationsanleitung_arbeitszeit.md`

**Geprüft:**

- Die Datei wurde in diesem Durchgang nicht im Volltext ausgewertet; nur Existenz und Pfad sind belegt. [cite:42]

**Bewertung bzgl. möglicher `admin_gui`-Erwähnungen:**

- **Status:** nicht verifizierbar
- **Beleg:** Kein inhaltlicher Vollabgleich im Rahmen dieses Prüfberichts. [cite:42]

**Anpassungsvorschlag:**

- Volltextsuche in dieser Datei nach:
  - `admin_gui`
  - `GUI`
  - `tkinter`

Bis dahin bleibt die Frage, ob GUI-spezifische Installationshinweise enthalten sind, offen. [cite:42]

## 5 Weitere Dokumentbereiche

### 5.1 `docs/04_betrieb/` und `docs/05_datenschutz_recht/`

**Geprüft:**

- Diese Verzeichnisse wurden in diesem Durchgang nicht gezielt auf `admin_gui`-Erwähnungen untersucht; es ist lediglich belegt, dass sie existieren und betriebliche bzw. datenschutzrechtliche Dokumente enthalten. [cite:36][cite:41]

**Bewertung bzgl. `admin_gui`:**

- **Status:** nicht verifizierbar
- **Beleg:** Keine Volltextanalyse im Rahmen dieses Berichts. [cite:36][cite:41]

**Anpassungsvorschlag:**

- Stichprobenartige bzw. vollständige Volltextsuche nach `admin_gui`, `GUI` und `tkinter` in allen Dateien der Verzeichnisse `docs/04_betrieb/` und `docs/05_datenschutz_recht/`.

### 5.2 `docs/06_architektur/*`

**Geprüft (aus diesem und früheren Durchgängen):**

- `docs/06_architektur/domain/enums.md` [cite:26]
- `docs/06_architektur/infrastructure/evdev_reader.md` und zugehöriger überarbeiteter Abschnitt [cite:27]

In den geprüften Teilen gibt es keinen direkten Bezug zu `admin_gui`. [cite:26][cite:27]

**Bewertung bzgl. `admin_gui`:**

- **Status:** teilweise verifiziert (für die konkret gelesenen Dateien), ansonsten nicht verifizierbar
- **Beleg:** Keine GUI-Erwähnungen in den geprüften Architekturdateien, keine Vollsicht über alle weiteren Dateien in `docs/06_architektur/`. [cite:26][cite:27]

**Anpassungsvorschlag:**

- Ergänzende Volltextsuche in allen Dateien unter `docs/06_architektur/` nach `admin_gui`, `GUI` und `tkinter`.

## 6 Gesamte Bewertung

1. **Codebasis `main`:**
   - `admin_gui/` ist im Branch `main` entfernt. [cite:31]
   - Es existieren keine Referenzen zu `admin_gui` oder `tkinter` im aktuellen `main`. [cite:33][cite:35]

2. **Handbuchmodul Präsentationsschicht, Überblick, README, Verzeichnisstruktur:**
   - Alle überprüften Dokumente beschreiben die Präsentationsschicht ausschließlich mit `terminal_ui/` und `admin_cli/`. [cite:36][cite:39][cite:40][cite:41]
   - Diese Aussagen sind mit der aktuellen Struktur des Branches `main` vollständig konsistent. [cite:31][cite:36][cite:39][cite:40][cite:41]

3. **Bestands-Prüfbericht zur Präsentationsschicht:**
   - `pruefbericht_presentation.md` enthält mehrere Aussagen, die auf einen Zustand mit vorhandener `admin_gui/` verweisen. [cite:30]
   - Diese Aussagen sind für den aktuellen Branch `main` ganz oder teilweise nicht mehr gültig oder nur noch als historisch zu betrachten. [cite:30][cite:31]
   - Eine Aktualisierung oder klare Kennzeichnung als historischer Stand wäre notwendig, um Fehlinterpretationen zu vermeiden. [cite:30][cite:31]

4. **Installations- und Befehlsdokumentation sowie Gesamt-Handbuch:**
   - Für `befehlsreferenz_arbeitszeit.md`, `installationsanleitung_arbeitszeit.md` und `handbuch_arbeitszeit.md` liegt in diesem Prüfbericht keine vollständige inhaltliche Analyse bzgl. möglicher `admin_gui`-Erwähnungen vor. [cite:37][cite:42]
   - Diese Dokumente sind in Bezug auf `admin_gui` aktuell als „nicht verifizierbar" zu führen, bis eine gezielte Volltextsuche durchgeführt wurde. [cite:37][cite:42]

## 7 Offene Punkte für Folgeschritte

1. Volltextanalyse von:
   - `docs/02_anwender/handbuch_arbeitszeit.md` [cite:37]
   - `docs/03_installation_technik/befehlsreferenz_arbeitszeit.md` [cite:42]
   - `docs/03_installation_technik/installationsanleitung_arbeitszeit.md` [cite:42]

   hinsichtlich möglicher Erwähnungen von `admin_gui`, `GUI`, `tkinter` oder GUI-bezogenen Startbefehlen.

2. Volltextsuche in:
   - `docs/04_betrieb/`
   - `docs/05_datenschutz_recht/`
   - `docs/06_architektur/`

   nach `admin_gui`, `GUI`, `tkinter`.

3. Aktualisierung von `docs/07_pruefberichte/handbuch/pruefbericht_presentation.md`, um:
   - `admin_gui`-bezogene Befunde klar als historisch zu kennzeichnen oder aus dem Geltungsbereich des Branches `main` herauszunehmen. [cite:30][cite:31]
   - den Header so anzupassen, dass `admin_gui/` nicht mehr als aktuell geprüfte Quelle im Branch `main` aufgeführt wird. [cite:30][cite:31]
