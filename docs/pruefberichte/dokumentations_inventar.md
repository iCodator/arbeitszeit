# Dokumentations-Inventar – Projekt `arbeitszeit`

**Stand:** 03.07.2026, 13:36 Uhr (Update) · **Repository:** [iCodator/arbeitszeit](https://github.com/iCodator/arbeitszeit) · **Basis-Commit:** `c1bdc9d` (Integrationsstand der drei Handbuchkapitel gegen Commits `2f3ce0e`, `217ff42`, `341a33f` verifiziert)

## Zweck dieses Dokuments

Dieses Inventar erfasst **alle** Markdown-/HTML-Dokumentationsdateien im Repository (aktueller Baum und `docs/archive/`, `docs/audits/`) mit Zweck, Status und letztem Bearbeitungsdatum. Es ist die Entscheidungsgrundlage für eine mögliche Restrukturierung der Dokumentation und ersetzt keine inhaltliche Prüfung einzelner Kapitel gegen den Code – diese erfolgt weiterhin kapitelweise im Prüfmodus.

**Legende Status:**

| Kürzel | Bedeutung |
|---|---|
| **AR** | Aktiv-Referenz — verbindliches, aktuell gültiges Dokument, wird von anderen Dateien referenziert |
| **AB** | Aktiv-Betrieb — aktuell gültige Betriebs-/Nachweisdokumentation |
| **HA** | Historisch-Archiv — abgelöste Versionsstände, bereits in `docs/archive/` |
| **HS** | Historisch-Snapshot — datierter Prüf-/Audit-Zeitpunkt, nicht fortzuschreiben |
| **TK** | Tooling-Konfiguration — Werkzeug-/Prozessregeln, kein fachlicher Inhalt |
| **DUP** | Duplikat — inhaltlich oder funktional doppelt vorhanden |

**Legende Prüfstand (diese Space-Historie):**

| Kürzel | Bedeutung |
|---|---|
| ✅ geprüft | In dieser oder einer früheren Sitzung im Prüfmodus gegen den Code verifiziert |
| ⏳ offen | Noch nicht kapitelweise gegen den Code geprüft |
| — | Prüfung nicht vorgesehen (Archiv/Snapshot/Tooling) |

---

## 1. Aktive Referenz- und Kerndokumente (Repository-Wurzel)

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`README.md`](../README.md) | Projekteinstieg, Verweisliste auf alle Kerndokumente | AR | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (import-linter-Dev-Abhängigkeit und `handbuch_show_config.md` ergänzt) – siehe `pruefbericht_readme.md` |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Beitragsrichtlinien, Code-Stil, Prüfpflichten bei Änderungen | AR | 2026-07-03 | ✅ geprüft (03.07.), 3 Korrekturen umgesetzt (tests/presentation/ ergänzt, `handbuch_show_config.md` nachgetragen, Testmatrix-Pfad korrigiert) – siehe `pruefbericht_contributing.md` |
| [`CHANGELOG.md`](../CHANGELOG.md) | Chronologische Versionsänderungen | AB | 2026-06-13 | — (historisch fortlaufend, nicht rückwirkend zu prüfen) |
| [`pflichtenheft_arbeitszeit_v6.md`](../pflichtenheft_arbeitszeit_v6.md) | Funktionale/nicht-funktionale Anforderungen, rechtlicher Rahmen | AR | 2026-07-03 | ✅ geprüft (Rechtskonformität, heute) |
| [`regelwerk_arbeitszeit_v5.md`](../regelwerk_arbeitszeit_v5.md) | Fachliche Regelsammlung (Buchung, Pausen, Gesetzeskonformität) | AR | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (§11 Enum-Bezeichnung `MANUAL_ENTRY` → `MANUAL_ENTRY_REVIEW`) – siehe `pruefbericht_regelwerk.md` |
| [`anlage_einhaltung_pflichtenheft.md`](../anlage_einhaltung_pflichtenheft.md) | Nachweis der Pflichtenheft-Erfüllung (v1, Wurzelverzeichnis) | AR | 2026-07-03 | ✅ geprüft (03.07.), keine belegte Korrektur erforderlich (Rechtsverweise als nicht verifizierbar markiert) – siehe `pruefbericht_anlage_pflichtenheft.md` |
| [`handbuch_arbeitszeit.md`](../handbuch_arbeitszeit.md) | Konsolidiertes Gesamthandbuch (aus `docs/module/` zusammengeführt) | AR | 2026-07-03 | ✅ geprüft (03.07.), alle 6 Kapitel mit den bereits geprüften `docs/module/`-Korrekturen synchronisiert (Kapitel 1 Overview, Kapitel 3 Presentation inkl. Warnschwellen-Fußnote, Kapitel 4 Application Layer, Kapitel 5 Domain, Kapitel 6 Infrastructure) |
| `handbuch_arbeitszeit.html` | HTML-Export des Gesamthandbuchs | AR | 2026-07-01 | — (Ableitung, kein Primärdokument) |
| [`befehlsreferenz_arbeitszeit.md`](../befehlsreferenz_arbeitszeit.md) | Schnellreferenz aller CLI-/Terminal-Befehle | AR | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (Aufrufmuster-Beispiele auf Kurzform `admin` vereinheitlicht) – siehe `pruefbericht_befehlsreferenz.md` |
| [`installationsanleitung_arbeitszeit.md`](../installationsanleitung_arbeitszeit.md) | Installationsanleitung für Laien | AR | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (`git`-Paket aus build-essential-Zeile entfernt, als eigenständiger Schritt vor `git clone` ergänzt) – siehe `pruefbericht_installationsanleitung.md` |
| `installationsanleitung_arbeitszeit.html` | HTML-Export der Installationsanleitung | AR | 2026-07-01 | — (Ableitung) |

**Hinweis Duplikat-Risiko:** `handbuch_arbeitszeit.md` (konsolidiert) und die 8 Einzelkapitel unter `docs/module/handbuch_*.md` decken denselben Inhalt in zwei Formen ab. Falls beide dauerhaft gepflegt werden sollen, muss klar sein, welches die Quelle der Wahrheit ist (lt. README: `docs/module/` ist Quelle, `handbuch_arbeitszeit.md` das daraus zusammengeführte Ergebnis).

---

## 2. Handbuch-Kapitel (`docs/module/`)

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`handbuch_overview.md`](../docs/module/handbuch_overview.md) | Handbuch-Übersicht/Einstieg | AR | 2026-07-03 | ✅ geprüft (03.07.), 2 Korrekturen umgesetzt (admin_gui in Zweck-Satz und Projektstruktur-Baum ergänzt) – siehe `pruefbericht_overview.md` |
| [`handbuch_domain.md`](../docs/module/handbuch_domain.md) | Domain-Modell-Kapitel | AR | 2026-07-01 | ✅ geprüft, 4 Korrekturen integriert (Commit `2f3ce0e`; Abgleich Datei ↔ `ueberarbeiteter_abschnitt_handbuch_domain.md` per Diff bestätigt: keine Abweichung) |
| [`handbuch_application_layer.md`](../docs/module/handbuch_application_layer.md) | Anwendungsschicht-Kapitel | AR | 2026-07-01 | ✅ geprüft, Korrekturen integriert (Commit `217ff42`; Abgleich Datei ↔ `ueberarbeiteter_abschnitt_handbuch_application_layer.md` per Diff bestätigt: keine Abweichung) |
| [`handbuch_infrastructure.md`](../docs/module/handbuch_infrastructure.md) | Infrastrukturschicht-Kapitel | AR | 2026-07-03 | ✅ geprüft (heute, siehe `pruefbericht_infrastructure.md`) |
| [`handbuch_presentation.md`](../docs/module/handbuch_presentation.md) | Präsentationsschicht-Kapitel | AR | 2026-07-03 | ✅ geprüft (03.07.), 3 Korrekturen umgesetzt (admin_gui/-Abschnitt ergänzt, `reports export-csv-review-cases` nachgetragen, 50-Einträge-Warnschwellen-Fußnote wiederhergestellt) – siehe `pruefbericht_presentation.md` und `pruefbericht_presentation_nachtrag_warnschwelle.md` |
| [`handbuch_installation.md`](../docs/module/handbuch_installation.md) | Installations-Kapitel (Modulform) | AR | 2026-07-01 | ✅ geprüft (keine Korrektur erforderlich) |
| [`handbuch_audit.md`](../docs/module/handbuch_audit.md) | Audit- und Prüfstatus-Kapitel | AR | 2026-07-01 | ✅ geprüft (alle 18 Aussagen bestätigt, keine Korrektur erforderlich) |
| [`handbuch_show_config.md`](../docs/module/handbuch_show_config.md) | Dokumentation `scripts/show_config.py` | AR | 2026-07-01 | ✅ geprüft (SHA-Hash und alle Detailaussagen bestätigt, keine Korrektur erforderlich) |
| [`datenbankschema_arbeitszeit.md`](../docs/module/datenbankschema_arbeitszeit.md) | Datenbankschema-Referenz | AR | 2026-07-01 | ✅ geprüft, 3 Korrekturen integriert (Commit `341a33f`; Abgleich Datei ↔ `ueberarbeiteter_abschnitt_handbuch_datenbankschema_arbeitszeit.md` per Diff bestätigt: keine Abweichung) |
| [`ueberarbeiteter_abschnitt_handbuch_domain.md`](../docs/module/ueberarbeiteter_abschnitt_handbuch_domain.md) | Vorbereitete korrigierte Fassung von `handbuch_domain.md` | HS (überholt) | 2026-07-03 | Bereits vollständig in `handbuch_domain.md` integriert (Commit `2f3ce0e`) und inhaltsgleich (Diff bestätigt) — Datei ist damit überholt/redundant |
| [`ueberarbeiteter_abschnitt_handbuch_application_layer.md`](../docs/module/ueberarbeiteter_abschnitt_handbuch_application_layer.md) | Vorbereitete korrigierte Fassung von `handbuch_application_layer.md` | HS (überholt) | 2026-07-03 | Bereits vollständig in `handbuch_application_layer.md` integriert (Commit `217ff42`) und inhaltsgleich (Diff bestätigt) — Datei ist damit überholt/redundant |
| [`ueberarbeiteter_abschnitt_handbuch_datenbankschema_arbeitszeit.md`](../docs/module/ueberarbeiteter_abschnitt_handbuch_datenbankschema_arbeitszeit.md) | Vorbereitete korrigierte Fassung von `datenbankschema_arbeitszeit.md` | HS (überholt) | 2026-07-03 | Bereits vollständig in `datenbankschema_arbeitszeit.md` integriert (Commit `341a33f`) und inhaltsgleich (Diff bestätigt) — Datei ist damit überholt/redundant |

---

## 3. Betriebsdokumentation (`docs/betrieb/`)

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`betriebsdokumentation_arbeitszeit_v1_1.md`](../docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md) | Aktueller Stand der Betriebsdokumentation (Export, Rechte, Aufbewahrung, Backup) | AB | 2026-07-03 | ✅ geprüft (03.07.), mehrere Korrekturen umgesetzt (nicht existierende CLI-Befehle/Flags, Systemcheck-Aufruf, Protokollierungsziel, Klassenname, Fristen-/Paragraphenverweis) – siehe `pruefbericht_betriebsdokumentation.md` |
| [`betriebsfreigabe_protokoll.md`](../docs/betrieb/betriebsfreigabe_protokoll.md) | Formular zur Betriebsfreigabe der Praxis | AB | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (Pfadangaben zu Testmatrix-Nachweisen korrigiert) – siehe `pruefbericht_betriebsfreigabe_protokoll.md` |
| [`rollenzuweisung.md`](../docs/betrieb/rollenzuweisung.md) | Aktuelle Rollenzuweisung und Zugriffsregelung | AB | 2026-07-03 | ✅ geprüft (03.07.), 4 Korrekturen umgesetzt (EMPLOYEE-Rolle ergänzt, Admin-CLI/Admin-GUI präzisiert, Begründungspflicht bei Nachträgen, Restore-Zeile als organisatorisch gekennzeichnet) – siehe `pruefbericht_rollenzuweisung.md` |
| [`aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md`](../docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md) | Aufbewahrungs-/Löschkonzept | AB | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (5-Jahres-Praxisfristen als Praxisfestlegung über gesetzliche Mindestfrist hinaus präzisiert) – siehe `pruefbericht_aufbewahrungskonzept.md` |
| [`backup_zeitplan_und_automatisierung.md`](../docs/betrieb/backup_zeitplan_und_automatisierung.md) | Backup-Zeitplan, Cron/systemd-Automatisierung | AB | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (`--nas-path`-CLI-Parameter existiert nicht, NAS-Sync läuft über `system_config`) – siehe `pruefbericht_backup_zeitplan.md` |
| [`datenschutz_und_tom_arbeitszeit_v1_0.md`](../docs/betrieb/datenschutz_und_tom_arbeitszeit_v1_0.md) | Technische/organisatorische Maßnahmen (TOM) | AB | 2026-06-13 | ✅ geprüft (03.07.), keine belegte Korrektur erforderlich (Passwort-Hashing, Rollenmodell, NAS-Sync, Audit-Log bestätigt) – siehe `pruefbericht_datenschutz_und_tom.md` |
| [`hardware_inbetriebnahme_protokoll.md`](../docs/betrieb/hardware_inbetriebnahme_protokoll.md) | Hardware-Inbetriebnahme-/Smoke-Test-Protokoll | AB | 2026-07-03 | ✅ geprüft (03.07.), mehrere Korrekturen umgesetzt (nicht existierende CLI-Befehle ersetzt, `--nas-path` entfernt) – siehe `pruefbericht_hardware_inbetriebnahme.md` |
| [`restore_checkliste.md`](../docs/betrieb/restore_checkliste.md) | Restore-Checkliste | AB | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (Hinweis: kein Admin-CLI-Restore-Befehl, nur `SQLiteBackupService.restore_from()`) – siehe `pruefbericht_restore_checkliste.md` |
| `rollenzuweisung_arbeitszeit_v1_0.md` | Frühere Fassung der Rollenzuweisung (v1_0) | **DUP** von `rollenzuweisung.md` | 2026-06-13 | — (Ablöse-Kandidat, siehe Empfehlung) |

**Nachweise (`docs/betrieb/nachweise/`):**

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`testmatrix_revision_v1.md`](../docs/betrieb/nachweise/testmatrix_revision_v1.md) | Revisionsfeste Testmatrix (Anforderung↔Test) | HS | 2026-06-30 | — (bewusst nicht auf v6 umgestellt, historischer Stand) |
| [`testmatrix_pruefbericht_v1.md`](../docs/betrieb/nachweise/testmatrix_pruefbericht_v1.md) | Prüfbericht zur Testmatrix | HS | 2026-06-30 | — |
| [`testmatrix_planabweichungen_v1.md`](../docs/betrieb/nachweise/testmatrix_planabweichungen_v1.md) | Abweichungsliste Planung vs. Testmatrix | HS | 2026-06-30 | — |
| [`nachtragsmatrix_phasen_v1.md`](../docs/betrieb/nachweise/nachtragsmatrix_phasen_v1.md) | Phasenübergreifende Nachtragsmatrix (44 Einträge) | HS | 2026-06-30 | — |

---

## 4. Datenschutz und Sicherheit

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`docs/datenschutz/vvt_arbeitszeit_v1.md`](../docs/datenschutz/vvt_arbeitszeit_v1.md) | Verzeichnis von Verarbeitungstätigkeiten (Art. 30 DSGVO) | AB | 2026-07-03 | ✅ geprüft (03.07.), 3 Korrekturen umgesetzt (Passwort-Hash-Verfahren, Tabellenname, Restore-Verfahren korrigiert) – siehe `pruefbericht_vvt.md` |
| [`docs/SECURITY.md`](../docs/SECURITY.md) | Sicherheitsmodell des Systems | AR | 2026-07-03 | ✅ geprüft (03.07.), 4 Korrekturen umgesetzt (Audit-Ereignisnamen, CLI-prog-Name, Passwort-Hash-Verortung, Spaltenname) – siehe `pruefbericht_security.md` |

---

## 5. Architekturentscheidungen (`docs/adr/`)

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`adr-cqrs-lesezugriff.md`](../docs/adr/adr-cqrs-lesezugriff.md) | ADR-002: Direkte Infra-Lesezugriffe in Admin-CLI | AR (fixierter Beschluss) | 2026-07-03 | ✅ geprüft (03.07.), 1 Korrektur umgesetzt (toter Verweis auf nicht existierende `ADR-001-migrations-struktur.md` entfernt) – siehe `pruefbericht_adr.md` |
| [`adr_presentation_infrastructure_v1.md`](../docs/adr/adr_presentation_infrastructure_v1.md) | ADR-ARCH-001: Composition Root, Infra-Importe in Presentation | AR (fixierter Beschluss) | 2026-06-30 | ✅ geprüft (03.07.), keine Korrektur erforderlich (Import-Tabelle, Layer-Contract, Commit-Referenzen vollständig verifiziert) – siehe `pruefbericht_adr.md` |
| [`device_event_architekturentscheidung_v1.md`](../docs/adr/device_event_architekturentscheidung_v1.md) | Architekturentscheidung `device_events`/`device_event_id` | AR (fixierter Beschluss) | 2026-06-30 | — |

---

## 6. Domain- und Infrastruktur-Detaildokumentation

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`docs/domain/enums.md`](../docs/domain/enums.md) | Dokumentation aller Domain-Enums | AR | 2026-07-01 | ✅ geprüft (03.07., kein Änderungsbedarf, siehe `pruefbericht_enums.md`) |
| [`docs/infrastructure/evdev_reader.md`](../docs/infrastructure/evdev_reader.md) | Hardwarebeschreibung `evdev_reader.py` | AR | 2026-07-03 | ✅ geprüft, 2 Korrekturen direkt im Dokument umgesetzt (Shift-Logik a-f/A-F, `grab`-Parameter als konfigurierbar präzisiert) – siehe `pruefbericht_evdev_reader.md` und `pruefbericht_evdev_reader_integration.md` |
| [`docs/verzeichnisstruktur_arbeitszeit.md`](../docs/verzeichnisstruktur_arbeitszeit.md) | Vollständige Verzeichnis-/Dateiübersicht des Repos | AR | 2026-07-03 | ✅ geprüft (03.07.), mehrere Korrekturen umgesetzt (fehlende Dateien/Verzeichnisse ergänzt, hardware-Modul und admin_cli-Unterbefehle korrigiert) – siehe `pruefbericht_verzeichnisstruktur.md` |
| [`docs/handbuch_rollen_cli_ergaenzung_v1_0.md`](../docs/handbuch_rollen_cli_ergaenzung_v1_0.md) | Ergänzung Rollen-CLI (v1.1-Inhalt trotz v1_0-Dateiname) | AR | 2026-07-03 | ✅ geprüft (03.07.), 3 Korrekturen umgesetzt (`set-password`->`bootstrap`, Argumentsyntax `--user-id`, TECH-Restore-Aussage präzisiert) – siehe `pruefbericht_handbuch_rollen_cli_ergaenzung.md` |
| [`docs/infrastructure/ueberarbeiteter_abschnitt_evdev_reader.md`](../docs/infrastructure/ueberarbeiteter_abschnitt_evdev_reader.md) | Als „überarbeitet“ angelegte Fassung von `evdev_reader.md` | HS (veraltetes Zwischendokument) | 2026-07-03 | **Auffälligkeit:** Die eigentliche Korrektur wurde direkt in `evdev_reader.md` umgesetzt (Commit `055de57`); diese separate Datei weicht davon inzwischen inhaltlich leicht ab und wurde nicht nachgezogen – als überholt zu betrachten |

---

## 7. Informelle Planungsdokumente (`docs/informelles/`)

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`planung_gesamt.md`](../docs/informelles/planung_gesamt.md) | Gesamter Implementierungsplan, Design-Session-Zusammenfassung, offene Punkte | AR (bewusst als Gruppe-A-Referenz behandelt) | 2026-07-03 | ✅ geprüft (03.07.), 5 Korrekturen umgesetzt (Repository-Anzahl 10->11 an zwei Stellen, Widerspruch zur device_event_id-Verkettung aufgelöst, Diff-Artefakt bereinigt, Hinweis zu use_cases-Dateien ergänzt) – siehe `pruefbericht_planung_gesamt.md` |
| [`session_abschluss_und_klarstellungen_2026-06-11.md`](../docs/informelles/session_abschluss_und_klarstellungen_2026-06-11.md) | Evidenzgrenzen-Protokoll vom 2026-06-11 | HS | 2026-07-03 | ✅ geprüft (03.07.), 2 Korrekturen umgesetzt (Archivpfad, veraltete Pflichtenheft-Referenz mit Zeitbezug präzisiert) – siehe `pruefbericht_session_abschluss.md` |

---

## 8. Prüfberichte (`docs/pruefberichte/`)

| Datei | Zweck | Status | Letzte Änderung | Prüfstand |
|---|---|---|---|---|
| [`pruefbericht_infrastructure.md`](../docs/pruefberichte/pruefbericht_infrastructure.md) | Prüfbericht Kapitel Infrastrukturschicht | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_rechtskonformitaet_pflichtenheft.md`](../docs/pruefberichte/pruefbericht_rechtskonformitaet_pflichtenheft.md) | Prüfbericht Rechtskonformität Pflichtenheft | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_enums.md`](../docs/pruefberichte/pruefbericht_enums.md) | Prüfbericht `docs/domain/enums.md` – kein Änderungsbedarf | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_evdev_reader.md`](../docs/pruefberichte/pruefbericht_evdev_reader.md) | Prüfbericht `docs/infrastructure/evdev_reader.md` – 2 Korrekturen offen | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_handbuch_domain.md`](../docs/pruefberichte/pruefbericht_handbuch_domain.md) | Prüfbericht `docs/module/handbuch_domain.md` – 4 Korrekturen, integriert in Commit `2f3ce0e` | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_handbuch_application_layer.md`](../docs/pruefberichte/pruefbericht_handbuch_application_layer.md) | Prüfbericht `docs/module/handbuch_application_layer.md` – mehrere Korrekturen (davon 1 Schwere „hoch“), integriert in Commit `217ff42` | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_datenbankschema_arbeitszeit.md`](../docs/pruefberichte/pruefbericht_datenbankschema_arbeitszeit.md) | Prüfbericht `docs/module/datenbankschema_arbeitszeit.md` – 3 Korrekturen, integriert in Commit `341a33f` | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_presentation.md`](../docs/pruefberichte/pruefbericht_presentation.md) | Prüfbericht `docs/module/handbuch_presentation.md` – 2 Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_overview.md`](../docs/pruefberichte/pruefbericht_overview.md) | Prüfbericht `docs/module/handbuch_overview.md` – 2 Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_installation.md`](../docs/pruefberichte/pruefbericht_installation.md) | Prüfbericht `docs/module/handbuch_installation.md` – keine belegte Korrektur, 1 Inkonsistenz zwischen aktiven Dokumenten notiert | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_audit.md`](../docs/pruefberichte/pruefbericht_audit.md) | Prüfbericht `docs/module/handbuch_audit.md` – alle 18 Aussagen bestätigt, keine Korrektur erforderlich | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_show_config.md`](../docs/pruefberichte/pruefbericht_show_config.md) | Prüfbericht `docs/module/handbuch_show_config.md` – SHA-Hash und alle Detailaussagen bestätigt, keine Korrektur erforderlich | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_readme.md`](../docs/pruefberichte/pruefbericht_readme.md) | Prüfbericht `README.md` – 1 Korrektur umgesetzt (import-linter, handbuch_show_config.md) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_contributing.md`](../docs/pruefberichte/pruefbericht_contributing.md) | Prüfbericht `CONTRIBUTING.md` – 3 Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_regelwerk.md`](../docs/pruefberichte/pruefbericht_regelwerk.md) | Prüfbericht `regelwerk_arbeitszeit_v5.md` – 1 Korrektur umgesetzt (§11 Enum-Bezeichnung) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_anlage_pflichtenheft.md`](../docs/pruefberichte/pruefbericht_anlage_pflichtenheft.md) | Prüfbericht `anlage_einhaltung_pflichtenheft.md` – keine belegte Korrektur erforderlich | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_befehlsreferenz.md`](../docs/pruefberichte/pruefbericht_befehlsreferenz.md) | Prüfbericht `befehlsreferenz_arbeitszeit.md` – 1 Korrektur umgesetzt (Aufrufmuster-Kurzform) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_installationsanleitung.md`](../docs/pruefberichte/pruefbericht_installationsanleitung.md) | Prüfbericht `installationsanleitung_arbeitszeit.md` – 1 Korrektur umgesetzt (git-Paket-Inkonsistenz aufgelöst) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_aufbewahrungskonzept.md`](../docs/pruefberichte/pruefbericht_aufbewahrungskonzept.md) | Prüfbericht `aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` – 1 Korrektur umgesetzt (5-Jahres-Fristen präzisiert) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_hardware_inbetriebnahme.md`](../docs/pruefberichte/pruefbericht_hardware_inbetriebnahme.md) | Prüfbericht `hardware_inbetriebnahme_protokoll.md` – mehrere Korrekturen umgesetzt (falsche CLI-Befehle) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_backup_zeitplan.md`](../docs/pruefberichte/pruefbericht_backup_zeitplan.md) | Prüfbericht `backup_zeitplan_und_automatisierung.md` – 1 Korrektur umgesetzt (`--nas-path` entfernt) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_rollenzuweisung.md`](../docs/pruefberichte/pruefbericht_rollenzuweisung.md) | Prüfbericht `rollenzuweisung.md` – 4 Korrekturen umgesetzt (EMPLOYEE, Admin-GUI, Begründung, Restore) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_restore_checkliste.md`](../docs/pruefberichte/pruefbericht_restore_checkliste.md) | Prüfbericht `restore_checkliste.md` – 1 Korrektur umgesetzt (Restore-CLI-Hinweis) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_betriebsdokumentation.md`](../docs/pruefberichte/pruefbericht_betriebsdokumentation.md) | Prüfbericht `betriebsdokumentation_arbeitszeit_v1_1.md` – mehrere Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_betriebsfreigabe_protokoll.md`](../docs/pruefberichte/pruefbericht_betriebsfreigabe_protokoll.md) | Prüfbericht `betriebsfreigabe_protokoll.md` – 1 Korrektur umgesetzt (Pfadangaben) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_vvt.md`](../docs/pruefberichte/pruefbericht_vvt.md) | Prüfbericht `docs/datenschutz/vvt_arbeitszeit_v1.md` – 3 Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_security.md`](../docs/pruefberichte/pruefbericht_security.md) | Prüfbericht `docs/SECURITY.md` – 4 Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_verzeichnisstruktur.md`](../docs/pruefberichte/pruefbericht_verzeichnisstruktur.md) | Prüfbericht `docs/verzeichnisstruktur_arbeitszeit.md` – mehrere Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_handbuch_rollen_cli_ergaenzung.md`](../docs/pruefberichte/pruefbericht_handbuch_rollen_cli_ergaenzung.md) | Prüfbericht `docs/handbuch_rollen_cli_ergaenzung_v1_0.md` – 3 Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_planung_gesamt.md`](../docs/pruefberichte/pruefbericht_planung_gesamt.md) | Prüfbericht `docs/informelles/planung_gesamt.md` – 5 Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_datenschutz_und_tom.md`](../docs/pruefberichte/pruefbericht_datenschutz_und_tom.md) | Prüfbericht `docs/betrieb/datenschutz_und_tom_arbeitszeit_v1_0.md` – keine Korrektur erforderlich | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_adr.md`](../docs/pruefberichte/pruefbericht_adr.md) | Prüfbericht beider ADR-Dateien – 1 Korrektur umgesetzt (toter Verweis entfernt) | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_session_abschluss.md`](../docs/pruefberichte/pruefbericht_session_abschluss.md) | Prüfbericht `docs/informelles/session_abschluss_und_klarstellungen_2026-06-11.md` – 2 Korrekturen umgesetzt | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_evdev_reader_integration.md`](../docs/pruefberichte/pruefbericht_evdev_reader_integration.md) | Nachtrags-Prüfbericht zur Integration der `evdev_reader.md`-Korrekturen | HS (Nachweisdokument) | 2026-07-03 | — |
| [`pruefbericht_presentation_nachtrag_warnschwelle.md`](../docs/pruefberichte/pruefbericht_presentation_nachtrag_warnschwelle.md) | Nachtrags-Prüfbericht zur Warnschwellen-Fußnote in `handbuch_presentation.md` | HS (Nachweisdokument) | 2026-07-03 | — |

---

## 9. Werkzeug-/Prozesskonfiguration (kein fachlicher Inhalt)

| Datei | Zweck | Status | Letzte Änderung |
|---|---|---|---|
| [`.claude/claude.md`](../.claude/claude.md) | Entwicklungsmodus-Regeln für KI-Agenten | TK | 2026-07-03 |
| [`.claude/audit/CLAUDE_audit.md`](../.claude/audit/CLAUDE_audit.md) | Auditmodus-Regeln für KI-Agenten | TK | 2026-07-03 |
| [`.claude/rules/CLAUDE_strict.md`](../.claude/rules/CLAUDE_strict.md) | Strenger Modus für sensible Bereiche | TK | 2026-06-30 |
| `.claude/markdown-Rules.md` | Markdownlint-Regelreferenz | TK / **DUP** | 2026-07-03 |
| `.claude/rules/markdown-Rules.md` | Identische Kopie der Markdownlint-Regelreferenz | TK / **DUP** | 2026-07-03 |

**Duplikat bestätigt:** `.claude/markdown-Rules.md` und `.claude/rules/markdown-Rules.md` sind byteidentisch (2.814 Zeilen); ebenso liegt `Markdown Syntax Documentation.pdf` doppelt unter `.claude/` und `.claude/rules/` vor. Hier ist zu klären, welcher Pfad der verbindliche ist.

---

## 10. Archiv — abgelöste Versionsstände (`docs/archive/`, heute bereitgestellt)

Alle Dateien in diesem Abschnitt sind laut deiner Entscheidung **Gruppe B** (historisch, nicht fortzuschreiben). Aufgeführt zur Vollständigkeit und zur Nachvollziehbarkeit der Versionslinie.

### Pflichtenheft-/Regelwerk-Historie

| Datei | Abgelöst durch | Letzte Änderung |
|---|---|---|
| [`pflichtenheft_arbeitszeit_v3.md`](../docs/archive/pflichtenheft_arbeitszeit_v3.md) | v4 → v5 → **v6** (aktuell) | 2026-07-03 (Verschiebung) |
| [`pflichtenheft_arbeitszeit_v4.md`](../docs/archive/pflichtenheft_arbeitszeit_v4.md) | v5 → **v6** (aktuell) | 2026-07-03 (Verschiebung) |
| [`regelwerk_arbeitszeit_v3.md`](../docs/archive/regelwerk_arbeitszeit_v3.md) | v4 → **v5** (aktuell) | 2026-07-03 (Verschiebung) |
| [`regelwerk_arbeitszeit_v4.md`](../docs/archive/regelwerk_arbeitszeit_v4.md) | **v5** (aktuell) | 2026-07-03 (Verschiebung) |
| [`anlage_einhaltung_pflichtenheft_v2.md`](../docs/archive/anlage_einhaltung_pflichtenheft_v2.md) | `anlage_einhaltung_pflichtenheft.md` (Wurzel, v1 — Achtung: niedrigere Versionsnummer ist aktuell!) | 2026-07-03 (Verschiebung) |

### Handbuch-/Installationshistorie

| Datei | Abgelöst durch | Letzte Änderung |
|---|---|---|
| [`handbuch_arbeitszeit_V1.0.md`](../docs/archive/handbuch_arbeitszeit_V1.0.md) | V1.1 → V1.2 → v1.1 (Kleinschreibung!) → **`handbuch_arbeitszeit.md`** (aktuell) | 2026-07-03 (Verschiebung) |
| [`handbuch_arbeitszeit_V1.1.md`](../docs/archive/handbuch_arbeitszeit_V1.1.md) | s. o. | 2026-07-03 (Verschiebung) |
| [`handbuch_arbeitszeit_V1.2.md`](../docs/archive/handbuch_arbeitszeit_V1.2.md) | s. o. | 2026-07-03 (Verschiebung) |
| [`handbuch_arbeitszeit_v1.1.md`](../docs/archive/handbuch_arbeitszeit_v1.1.md) | s. o. (Namenskollision mit `V1.1.md` — nur Groß-/Kleinschreibung unterscheidet) | 2026-07-03 (Verschiebung) |
| `handbuch_arbeitszeit.html`, `handbuch_arbeitszeit_v1.0.html` | Aktueller HTML-Export in Repo-Wurzel | 2026-07-03 (Verschiebung) |
| [`installationsanleitung_arbeitszeit_V1.0.md`](../docs/archive/installationsanleitung_arbeitszeit_V1.0.md) | V2.0 → **aktuelle Fassung** (Wurzel) | 2026-07-03 (Verschiebung) |
| [`installationsanleitung_arbeitszeit_V2.0.md`](../docs/archive/installationsanleitung_arbeitszeit_V2.0.md) | **aktuelle Fassung** (Wurzel) | 2026-07-03 (Verschiebung) |

### Betriebsdokumentation-Historie

| Datei | Abgelöst durch | Letzte Änderung |
|---|---|---|
| [`betriebsdokumentation_arbeitszeit_v1.md`](../docs/archive/betriebsdokumentation_arbeitszeit_v1.md) | **v1_1** (aktuell, `docs/betrieb/`) | 2026-07-03 (Verschiebung) |
| [`addendum_datenschutz_it_sicherheit_arbeitszeit_v1.md`](../docs/archive/addendum_datenschutz_it_sicherheit_arbeitszeit_v1.md) | Inhalt vermutlich in `datenschutz_und_tom_arbeitszeit_v1_0.md` aufgegangen — **nicht verifiziert** | 2026-07-03 (Verschiebung) |

### Design-Session- und Planungsprotokolle (Phasenplanung)

| Datei | Zweck | Letzte Änderung |
|---|---|---|
| [`phase1_planung.md`](../docs/archive/phase1_planung.md) … [`phase5_planung.md`](../docs/archive/phase5_planung.md) | Phasenweise Design-/Umsetzungsplanung (Grundgerüst, Domäne, Application, Infrastruktur, Präsentation) | 2026-07-03 (Verschiebung) |
| [`migrationsuebersicht_notiz_v1.md`](../docs/archive/migrationsuebersicht_notiz_v1.md) | Einordnungsnotiz zu DB-Migrationen | 2026-07-03 (Verschiebung) |
| [`terminologie_harmonisierung_v1.md`](../docs/archive/terminologie_harmonisierung_v1.md) | Vereinheitlichung von Fachbegriffen | 2026-07-03 (Verschiebung) |
| [`device_event_abschlussprotokoll_v1.md`](../docs/archive/device_event_abschlussprotokoll_v1.md) | Abschlussprotokoll zur `device_events`-Entscheidung | 2026-07-03 (Verschiebung) |
| [`abarbeitung_hoch_abschlussnotiz_v1.md`](../docs/archive/abarbeitung_hoch_abschlussnotiz_v1.md), [`_mittel_`](../docs/archive/abarbeitung_mittel_abschlussnotiz_v1.md), [`_niedrig_`](../docs/archive/abarbeitung_niedrig_abschlussnotiz_v1.md) | Abschlussnotizen zur Abarbeitung nach Prioritätsstufe | 2026-07-03 (Verschiebung) |
| [`audit_evidenzgrenzen_v1.md`](../docs/archive/audit_evidenzgrenzen_v1.md) | Frühere Fassung der Evidenzgrenzen (vgl. `session_abschluss_und_klarstellungen_2026-06-11.md`) | 2026-07-03 (Verschiebung) |
| [`audit_klarstellungen_niedrig_v1.md`](../docs/archive/audit_klarstellungen_niedrig_v1.md) | Audit-Klarstellungen (niedrige Priorität) | 2026-07-03 (Verschiebung) |

---

## 11. Audit-Snapshots (`docs/audits/`, heute bereitgestellt)

Zeitpunktbezogene, maschinell und manuell erstellte Prüfläufe. Nicht fortzuschreiben, aber wertvoll als historischer Nachweis für Testabdeckung/Codequalität zu einem bestimmten Datum.

| Datei | Zweck | Datum |
|---|---|---|
| [`audit_arbeitszeit_v1_2026-06-11_19-28.md`](../docs/audits/audit_arbeitszeit_v1_2026-06-11_19-28.md) | Audit-Bericht Gesamtrepository | 2026-06-11 |
| [`audit_arbeitszeit_v1_2026-06-12_13-58.md`](../docs/audits/audit_arbeitszeit_v1_2026-06-12_13-58.md) | Audit-Bericht Gesamtrepository | 2026-06-12 |
| [`audit_arbeitszeit_v1_2026-06-13_09-04.md`](../docs/audits/audit_arbeitszeit_v1_2026-06-13_09-04.md) | Audit-Bericht Gesamtrepository | 2026-06-13 |
| [`audit_arbeitszeit_nachaudit_v1_2026-06-13.md`](../docs/audits/audit_arbeitszeit_nachaudit_v1_2026-06-13.md) | Nachaudit nach Behebung technischer Befunde | 2026-06-13 |
| [`reports/audit-notes-2026-06-16.md`](../docs/audits/reports/audit-notes-2026-06-16.md) | Auswertung des Tooling-Laufs vom 16.06. | 2026-06-16 |
| `reports/2026-06-16/coverage.xml`, `pytest.txt`, `mypy-report.txt`, `ruff-report.txt`, `bandit-report.json`, `radon-cc.txt`, `radon-raw.txt`, `import-linter.txt` | Rohdaten der Tooling-Läufe (Testabdeckung, Typprüfung, Linting, Security-Scan, Komplexität, Architektur-Import-Regeln) | 2026-06-16 |

---

## Zusammenfassung: Zahlen

| Kategorie | Anzahl Dateien |
|---|---|
| Aktive Referenz-/Kerndokumente (Abschnitt 1–2) | 20 |
| Überholte Zwischenstand-Dateien, bereits integriert (Abschnitt 2, 6) | 4 |
| Aktive Betriebs-/Datenschutz-/ADR-/Detaildokumente (Abschnitt 3–7) | 24 |
| Prüfberichte (Abschnitt 8) | 33 |
| Tooling-Konfiguration inkl. Duplikate (Abschnitt 9) | 5 |
| Archiv — abgelöste Versionsstände (Abschnitt 10) | 28 |
| Audit-Snapshots inkl. Rohdaten (Abschnitt 11) | 13 |
| **Gesamt** | **127** |

Von den 44 aktiven Dokumenten (Abschnitt 1–8, ohne die 4 Zwischenstand-Dateien, die alle als überholt/bereits integriert gelten) wurden inzwischen **34 Kapitel** vollständig im Prüfmodus gegen den Code verifiziert:

| Kapitel | Ergebnis |
|---|---|
| Pflichtenheft (Rechtskonformität) | geprüft, korrekt |
| Infrastruktur-Handbuchkapitel | geprüft, korrekt |
| `docs/domain/enums.md` | geprüft, **kein Änderungsbedarf** |
| `docs/infrastructure/evdev_reader.md` | geprüft, **2 Korrekturen offen**, Überarbeitung noch nicht eingearbeitet |
| `docs/module/handbuch_domain.md` | geprüft, **4 Korrekturen integriert** (Commit `2f3ce0e`) |
| `docs/module/handbuch_application_layer.md` | geprüft, **Korrekturen integriert** (1× Schwere hoch; Commit `217ff42`) |
| `docs/module/datenbankschema_arbeitszeit.md` | geprüft, **3 Korrekturen integriert** (Commit `341a33f`) |
| `docs/module/handbuch_presentation.md` | geprüft, **2 Korrekturen direkt umgesetzt** (admin_gui/-Abschnitt ergänzt, `reports export-csv-review-cases` nachgetragen) |
| `docs/module/handbuch_overview.md` | geprüft, **2 Korrekturen direkt umgesetzt** (admin_gui in Zweck-Satz und Projektstruktur-Baum ergänzt) |
| `docs/module/handbuch_installation.md` | geprüft, **keine belegte Korrektur** – 1 Inkonsistenz zwischen aktiven Dokumenten notiert (Systempakete-Zeile, `git` im apt-Befehl uneinheitlich) |
| `docs/module/handbuch_audit.md` | geprüft, **alle 18 Aussagen bestätigt**, keine Korrektur erforderlich |
| `docs/module/handbuch_show_config.md` | geprüft, **SHA-Hash und alle Detailaussagen bestätigt**, keine Korrektur erforderlich |
| `README.md` | geprüft, **1 Korrektur direkt umgesetzt** (import-linter-Dev-Abhängigkeit und `handbuch_show_config.md`-Verweis ergänzt) |
| `CONTRIBUTING.md` | geprüft, **3 Korrekturen direkt umgesetzt** (tests/presentation/ ergänzt, `handbuch_show_config.md` nachgetragen, Testmatrix-Pfad korrigiert) |
| `regelwerk_arbeitszeit_v5.md` | geprüft, **1 Korrektur direkt umgesetzt** (§11 Enum-Bezeichnung `MANUAL_ENTRY` → `MANUAL_ENTRY_REVIEW`) |
| `anlage_einhaltung_pflichtenheft.md` | geprüft, **keine belegte Korrektur erforderlich** (Rechtsverweise außerhalb Repository-Evidenz als nicht verifizierbar markiert) |
| `befehlsreferenz_arbeitszeit.md` | geprüft, **1 Korrektur direkt umgesetzt** (Aufrufmuster-Beispiele auf Kurzform `admin` vereinheitlicht) |
| `installationsanleitung_arbeitszeit.md` | geprüft, **1 Korrektur direkt umgesetzt** (`git`-Paket-Inkonsistenz zwischen Referenzdokumenten aufgelöst) |
| `docs/verzeichnisstruktur_arbeitszeit.md` | geprüft, **mehrere Korrekturen direkt umgesetzt** (fehlende Dateien/Verzeichnisse ergänzt, hardware-Modul und admin_cli korrigiert) |
| `docs/handbuch_rollen_cli_ergaenzung_v1_0.md` | geprüft, **3 Korrekturen direkt umgesetzt** (`bootstrap`, `--user-id`, TECH-Restore-Aussage) |
| `docs/betrieb/aufbewahrungs_und_loeschkonzept_arbeitszeit_v1_0.md` | geprüft, **1 Korrektur direkt umgesetzt** (5-Jahres-Praxisfristen präzisiert) |
| `docs/betrieb/hardware_inbetriebnahme_protokoll.md` | geprüft, **mehrere Korrekturen direkt umgesetzt** (falsche CLI-Befehle/Flags) |
| `docs/betrieb/backup_zeitplan_und_automatisierung.md` | geprüft, **1 Korrektur direkt umgesetzt** (`--nas-path` entfernt) |
| `docs/betrieb/rollenzuweisung.md` | geprüft, **4 Korrekturen direkt umgesetzt** (EMPLOYEE, Admin-GUI, Begründungspflicht, Restore-Kennzeichnung) |
| `docs/betrieb/restore_checkliste.md` | geprüft, **1 Korrektur direkt umgesetzt** (Restore-CLI-Hinweis) |
| `docs/betrieb/betriebsdokumentation_arbeitszeit_v1_1.md` | geprüft, **mehrere Korrekturen direkt umgesetzt** (CLI-Befehle/Flags, Protokollierungsziel, Klassenname, Fristen) |
| `docs/betrieb/betriebsfreigabe_protokoll.md` | geprüft, **1 Korrektur direkt umgesetzt** (Pfadangaben zu Testmatrix-Nachweisen) |
| `docs/betrieb/datenschutz_und_tom_arbeitszeit_v1_0.md` | geprüft, **keine belegte Korrektur erforderlich** |
| `docs/datenschutz/vvt_arbeitszeit_v1.md` | geprüft, **3 Korrekturen direkt umgesetzt** (Passwort-Hash-Verfahren, Tabellenname, Restore-Verfahren) |
| `docs/SECURITY.md` | geprüft, **4 Korrekturen direkt umgesetzt** (Audit-Ereignisnamen, CLI-prog-Name, Passwort-Hash-Verortung, Spaltenname) |
| `docs/adr/adr-cqrs-lesezugriff.md` | geprüft, **1 Korrektur direkt umgesetzt** (toter Verweis entfernt) |
| `docs/adr/adr_presentation_infrastructure_v1.md` | geprüft, **keine Korrektur erforderlich** |
| `docs/informelles/planung_gesamt.md` | geprüft, **5 Korrekturen direkt umgesetzt** (Repository-Anzahl, Widerspruch device_event_id, Diff-Artefakt, Hinweis use_cases) |
| `docs/informelles/session_abschluss_und_klarstellungen_2026-06-11.md` | geprüft, **2 Korrekturen direkt umgesetzt** (Archivpfad, Pflichtenheft-Referenz mit Zeitbezug) |
| `docs/infrastructure/evdev_reader.md` | geprüft, **2 Korrekturen direkt umgesetzt** (Shift-Logik a-f/A-F, `grab`-Parameter konfigurierbar) |

Damit sind es **34 geprüfte Kapitel**, und für alle 34 ist der belegte Korrekturbedarf vollständig integriert. Für die drei zuvor als offen geführten Kapitel (`docs/module/handbuch_domain.md`, `docs/module/handbuch_application_layer.md`, `docs/module/datenbankschema_arbeitszeit.md`) wurde am 03.07.2026 verifiziert, dass die vorbereiteten Überarbeitungen (`ueberarbeiteter_abschnitt_handbuch_domain.md`, `ueberarbeiteter_abschnitt_handbuch_application_layer.md`, `ueberarbeiteter_abschnitt_handbuch_datenbankschema_arbeitszeit.md`) bereits in früheren Commits (`2f3ce0e`, `217ff42`, `341a33f`) inhaltsgleich in die primären Handbuchdateien übernommen wurden (Diff-Vergleich ohne Abweichung); zusätzlich wurden die betroffenen Domain-Feldergänzungen (ReviewCase, AuditLogEntry) und die use_cases-Liste auch im konsolidierten Gesamthandbuch (`handbuch_arbeitszeit.md`, Kapitel 4 und 5) als bereits synchronisiert bestätigt. Die drei `ueberarbeiteter_abschnitt_*.md`-Dateien gelten damit als überholt/redundant. Alle 34 geprüften Kapitel sind somit vollständig korrigiert bzw. benötigten keine Korrektur. Von den 44 aktiven Dokumenten sind damit **7 noch ungeprüft**: `handbuch_arbeitszeit.html` und `installationsanleitung_arbeitszeit.html` (reine HTML-Ableitungen, nicht separat zu prüfen), `CHANGELOG.md` (historisch fortlaufend) und `device_event_architekturentscheidung_v1.md` (ADR, als fixierter Beschluss nicht im Fokus).

**Geltender Arbeitszyklus je Kapitel:** Prüfung → Anpassung (nur belegte Korrekturen) → Commit (Prüfbericht + geänderte Handbuchdatei gemeinsam, aussagekräftige Commit-Message) → Push. Wurde für alle in dieser Tabelle aufgeführten Kapitel eingehalten.

---

## Beobachtete Auffälligkeiten (nur Feststellung, keine Änderung)

1. **Bestätigtes Duplikat:** `.claude/markdown-Rules.md` und `.claude/rules/markdown-Rules.md` sind identisch (ebenso die zugehörige PDF). Unklar, welcher Pfad verbindlich ist.
2. **Mögliches Duplikat:** `docs/betrieb/rollenzuweisung_arbeitszeit_v1_0.md` neben dem aktuelleren `docs/betrieb/rollenzuweisung.md` — Inhalt nicht Wort-für-Wort verglichen, nur anhand von Namen/Datum als Ablöse-Kandidat markiert.
3. **Uneinheitliche Versionsnotation:** Groß-/Kleinschreibung wechselt zwischen `V1.0`/`v1.0`, `_v1_0`/`_v1.0`, was in `docs/archive/` zu Namenskollisionen wie `handbuch_arbeitszeit_V1.1.md` vs. `handbuch_arbeitszeit_v1.1.md` führt (zwei verschiedene Dateien, nur Groß-/Kleinschreibung trennt sie).
4. **Umgekehrte Versionslogik bei der Anlage:** `anlage_einhaltung_pflichtenheft.md` (Wurzel) trägt keine Versionsnummer und wird als „v1“ bezeichnet, während die höhere `anlage_einhaltung_pflichtenheft_v2.md` bereits im Archiv liegt — die Versionsreihenfolge ist ohne Blick in den Dateiinhalt nicht eindeutig erkennbar.
5. **`addendum_datenschutz_it_sicherheit_arbeitszeit_v1.md`**: Zusammenhang zu `datenschutz_und_tom_arbeitszeit_v1_0.md` nicht geprüft — könnte inhaltlich bereits aufgegangen oder weiterhin eigenständig relevant sein.
6. **`ueberarbeiteter_abschnitt_evdev_reader.md` ist inzwischen überholt:** Die beiden im Prüfbericht (`pruefbericht_evdev_reader.md`) belegten Korrekturen (Shift-Logik a-f/A-F, `grab`-Parameter als konfigurierbar) wurden direkt in `docs/infrastructure/evdev_reader.md` umgesetzt (Commit `055de57`, siehe `pruefbericht_evdev_reader_integration.md`). Die separate „überarbeitete“ Datei wurde dabei nicht nachgezogen und weicht nun in der Formulierung leicht vom aktuellen Original ab — sie sollte entfernt oder als überholt gekennzeichnet werden.
7. **Drei weitere vorbereitete Überarbeitungen sind ebenfalls bereits integriert und damit überholt:** `ueberarbeiteter_abschnitt_handbuch_domain.md` (→ Commit `2f3ce0e`), `ueberarbeiteter_abschnitt_handbuch_application_layer.md` (→ Commit `217ff42`) und `ueberarbeiteter_abschnitt_handbuch_datenbankschema_arbeitszeit.md` (→ Commit `341a33f`) wurden am 03.07.2026 per Diff gegen die jeweils aktuelle Datei in `docs/module/` verglichen — in allen drei Fällen ohne inhaltliche Abweichung. Anders als zuvor im Inventar vermerkt, besteht hier **kein** offener Integrationsbedarf mehr; die drei separaten Dateien sind reine, nun überholte Zwischenstände und können entfernt werden.
8. **Toter Querverweis in ADR-002 gefunden und entfernt:** `docs/adr/adr-cqrs-lesezugriff.md` verwies auf eine nicht existierende Datei `ADR-001-migrations-struktur.md`; im Repository existieren nur 3 ADR-Dateien, keine davon mit diesem Namen (siehe `pruefbericht_adr.md`).
9. **Falscher Archivpfad in historischem Session-Protokoll korrigiert:** `docs/informelles/session_abschluss_und_klarstellungen_2026-06-11.md` referenzierte einen nicht existierenden Pfad `docs/informelles/archiv/` statt des tatsächlichen `docs/archive/` (siehe `pruefbericht_session_abschluss.md`).

Diese Punkte sind Beobachtungen aus Dateinamen/Metadaten bzw. direktem Dateivergleich, keine inhaltlich vollständig verifizierten Befunde zu allen ungeprüften Kapiteln. Sie müssten im Prüfmodus einzeln bestätigt werden, bevor daraus eine Löschung, Integration oder Zusammenführung folgt.
