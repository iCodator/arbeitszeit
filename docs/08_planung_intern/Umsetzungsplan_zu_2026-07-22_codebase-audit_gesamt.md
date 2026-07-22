Priorisierter Handlungsplan
Die Reihenfolge berücksichtigt Schweregrad, gemeinsame Wurzelursachen (ein Fix behebt mehrere Befunde) und Aufwand.

Phase 1 — Sofort (diese Woche)
Zentrale Zeitzonen-Hilfsfunktion (to_local(dt)) im Domain- oder Utility-Modul schaffen und konsequent anwenden in book_time.py:145–150 (kritisch), book_time.py:138–139 (mittel) und approve_supplement.py:189,194 (hoch) — ein Fix für drei Befunde.

check_break_compliance in compliance_checks.py:33–47 umbauen: Prüfreihenfolge umkehren oder alle Flags sammeln statt beim ersten Treffer zurückzukehren, damit CRITICAL nicht durch WARN verdeckt wird.

projected-Liste in approve_supplement.py:78 chronologisch sortieren, bevor sie an _work_stats übergeben wird.

Vor Rollout aller drei Fixes: Regressionstests mit konkreten DST-Grenzfällen (Buchung 08:00 CEST, Buchung 00:30 lokal Montag) ergänzen, da diese Testlücke die Ursache für gleich drei Befunde ist.

Phase 2 — Kurzfristig (Woche 2–3)
CorrectBookingUseCase (correct_booking.py:65–84) so erweitern, dass booking_type in time_bookings tatsächlich mutiert wird oder list_for_employee_on_day korrigierte Werte berücksichtigt.

HMAC-SHA256 mit installationsspezifischem Pepper für hash_uid() einführen (uid_hash.py:8), inklusive einmaliger Migration bestehender Hashes.

Architekturentscheidung treffen und dokumentieren: Passwort-Verifikation in der Admin-CLI nachrüsten oder das OS-Zugriffsmodell explizit als Sicherheitskonzept festschreiben. Das ist eine Grundsatzfrage, keine reine Code-Korrektur.

Phase 3 — Mittelfristig (Woche 3–4)
Befund	Datei	Kurzmaßnahme
Doppelung inaktiver Mitarbeiter	manage_employees.py:31	get_by_personnel_no ohne Aktivitätsfilter nutzen, ConflictError werfen
Letzter-Admin-Lockout	manage_user_accounts.py:94–124	has_active_admin()-Prüfung vor Deaktivierung/Rollenwechsel
Nachtrag ohne Sequenzprüfung	register_supplement.py:60–76	validate_booking_sequence vor dem Speichern aufrufen
Nur erste Fall-ID gespeichert	correct_booking.py:143–153	Rückgabetyp auf Liste erweitern
Inklusives Intervall	time_booking.py:81	< statt <= bei to_dt
Voller Hash im Audit-Log	book_time.py:264–279	Nur uid_hash[:8] loggen (analog debounce.py)
Fehlende Formatprüfung	employees.py:215,229	Regex-Check auf 64-Zeichen-Hex vor Speichern
Audit-Log-Write-Gap	book_time.py:204–246	Write-Ahead-Status oder Plausibilitätsprüfung „Buchung ohne Audit-Eintrag"
Phase 4 — Backlog (Niedrig, unkritisch)
CLOSED_WITH_NOTE fachlich klären: entfernen oder implementieren.

Kommentar zu OpenPhaseConflictError als bewusstes Sicherheitsnetz ergänzen.

Verschachteltes try/finally in booking_loop.py:43–44 für Connection-Leak.

occurred_at in evdev_reader.py:208 an den Beginn des Polls verschieben.

Rohe UID in verify_hardware.py maskieren (erste vier Zeichen + Sternchen).

Generiertes Passwort auf stderr statt stdout ausgeben.

Audit-Log-Integritätssicherung (HMAC-Kette oder Append-Only-Export) einplanen.

Dependency-Lock-File (uv lock) einführen und ins Repository aufnehmen.