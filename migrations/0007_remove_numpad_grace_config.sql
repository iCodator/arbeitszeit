-- Entfernt den durch die RFID-only-Umstellung obsolet gewordenen Config-Key.
-- Der Key booking.grace_seconds_after_numpad_select steuerte den Timeout zwischen
-- NumPad-Auswahl und nachfolgendem RFID-Scan. Da NumPad-Eingaben vollständig entfallen,
-- ist dieser Schlüssel ohne fachliche Funktion.
DELETE FROM system_config WHERE config_key = 'booking.grace_seconds_after_numpad_select';
