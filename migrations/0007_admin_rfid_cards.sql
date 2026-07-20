-- Migration 0007: Admin-RFID-Karten und zugehörige Systemereignisse
--
-- admin_rfid_cards: Speichert RFID-Karten, die am Terminal
-- administrative Aktionen (Stop, Neustart) auslösen dürfen.
-- Bewusst unabhängig von rfid_cards und employees, da Admin-Karten
-- keine Mitarbeiterbindung benötigen.
--
-- system_events: Um ADMIN_ACCESS_GRANTED und ADMIN_ACCESS_DENIED erweitert.
-- Admin-RFID-Ereignisse werden als Systemereignisse protokolliert,
-- da sie Prozesszustand des Terminals betreffen (kein device_events,
-- um den FK-Rebuild zu vermeiden).

CREATE TABLE admin_rfid_cards (
    id         INTEGER PRIMARY KEY,
    uid_hash   TEXT    NOT NULL UNIQUE,
    label      TEXT,
    active     INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT    NOT NULL
);

CREATE INDEX idx_admin_rfid_cards_uid_hash
    ON admin_rfid_cards(uid_hash);

-- system_events um ADMIN_ACCESS_GRANTED und ADMIN_ACCESS_DENIED erweitern.
-- Rebuild nötig, da SQLite CHECK-Constraints nicht per ALTER TABLE änderbar sind.
CREATE TABLE system_events_new (
    id INTEGER PRIMARY KEY,
    event_type TEXT NOT NULL CHECK (
        event_type IN (
            'SELFTEST_OK',
            'SELFTEST_FAIL',
            'DB_BACKUP_CREATED',
            'DB_BACKUP_FAILED',
            'RESTORE_STARTED',
            'RESTORE_FINISHED',
            'RESTORE_FAILED',
            'NAS_REACHABLE',
            'NAS_UNREACHABLE',
            'TIME_JUMP_DETECTED',
            'MANUAL_TIME_CHANGE_DETECTED',
            'DEVICE_UNAVAILABLE',
            'DEVICE_RECOVERED',
            'APPLICATION_START',
            'APPLICATION_STOP',
            'APPLICATION_ERROR',
            'ADMIN_ACCESS_GRANTED',
            'ADMIN_ACCESS_DENIED'
        )
    ),
    source TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('INFO', 'WARN', 'ERROR')),
    event_at TEXT NOT NULL,
    details_json TEXT,
    related_object_type TEXT,
    related_object_id INTEGER
);

INSERT INTO system_events_new SELECT * FROM system_events;
DROP TABLE system_events;
ALTER TABLE system_events_new RENAME TO system_events;

CREATE INDEX idx_system_events_event_at
    ON system_events(event_at);
