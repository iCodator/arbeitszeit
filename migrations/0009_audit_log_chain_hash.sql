-- Migration 0009: HMAC-Kette für Audit-Log-Integritätssicherung
-- Fügt chain_hash TEXT zur audit_log-Tabelle hinzu.
-- Bestehende Einträge erhalten chain_hash = NULL (keine Rückverkettung).
-- Neue Einträge erhalten einen HMAC-SHA256-Hash, der die Kette bildet.
-- Referenz: docs/08_planung_intern/decisions/0003-audit-log-integritaet.md

ALTER TABLE audit_log ADD COLUMN chain_hash TEXT;
