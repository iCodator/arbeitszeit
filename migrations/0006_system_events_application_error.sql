-- Migration 0006: system_events um APPLICATION_ERROR erweitern
-- APPLICATION_ERROR protokolliert einen Laufzeitfehler bei weitergeführtem Betrieb
-- (z. B. unerwartete Exception in der Terminal-UI-Schleife ohne Prozessabbruch).
-- Abgrenzung: APPLICATION_STOP = regulärer oder fehlerinduzierter Prozessabbruch;
--             APPLICATION_ERROR = Fehler abgefangen, Prozess läuft weiter.

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
            'APPLICATION_ERROR'
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
