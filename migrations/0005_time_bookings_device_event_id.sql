-- Migration 0005: device_event_id in time_bookings ergaenzen
-- FK-Constraint auf device_events erfordert Table-Rebuild (SQLite-Einschraenkung).
-- Alle bestehenden Zeilen erhalten device_event_id = NULL.

CREATE TABLE time_bookings_new (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    rfid_card_id INTEGER,
    booking_type TEXT NOT NULL CHECK (booking_type IN ('COME', 'GO', 'BREAK_START', 'BREAK_END')),
    booked_at TEXT NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('TERMINAL', 'MANUAL', 'IMPORT')),
    terminal_id INTEGER,
    device_event_id INTEGER,
    current_status TEXT NOT NULL CHECK (
        current_status IN (
            'OK',
            'OPEN',
            'WARN',
            'NEEDS_REVIEW',
            'CORRECTED',
            'CLOSED_WITH_NOTE'
        )
    ),
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (rfid_card_id) REFERENCES rfid_cards(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (terminal_id) REFERENCES terminals(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (device_event_id) REFERENCES device_events(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

INSERT INTO time_bookings_new (
    id, employee_id, rfid_card_id, booking_type, booked_at,
    source, terminal_id, device_event_id, current_status, note, created_at
)
SELECT
    id, employee_id, rfid_card_id, booking_type, booked_at,
    source, terminal_id, NULL, current_status, note, created_at
FROM time_bookings;

DROP TABLE time_bookings;
ALTER TABLE time_bookings_new RENAME TO time_bookings;

CREATE INDEX idx_time_bookings_employee_booked_at
    ON time_bookings(employee_id, booked_at);

CREATE INDEX idx_time_bookings_status_booked_at
    ON time_bookings(current_status, booked_at);
