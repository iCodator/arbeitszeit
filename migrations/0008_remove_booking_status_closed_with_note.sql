-- Migration 0008: BookingStatus.CLOSED_WITH_NOTE aus Schema entfernen
-- Dieser Status wurde nie von einem Use Case gesetzt und ist fachlich nicht
-- vorgesehen. Kein existierender Datensatz hat diesen Status.
--
-- time_bookings.current_status: CLOSED_WITH_NOTE aus CHECK entfernen.
-- booking_status_history.new_status: CLOSED_WITH_NOTE aus CHECK entfernen.

-- time_bookings neu anlegen (Struktur aus 0005, ohne CLOSED_WITH_NOTE)
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
            'CORRECTED'
        )
    ),
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (rfid_card_id) REFERENCES rfid_cards(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (terminal_id) REFERENCES terminals(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (device_event_id) REFERENCES device_events(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

INSERT INTO time_bookings_new SELECT * FROM time_bookings;
DROP TABLE time_bookings;
ALTER TABLE time_bookings_new RENAME TO time_bookings;

CREATE INDEX idx_time_bookings_employee_booked_at
    ON time_bookings(employee_id, booked_at);

CREATE INDEX idx_time_bookings_status_booked_at
    ON time_bookings(current_status, booked_at);

-- booking_status_history neu anlegen (CLOSED_WITH_NOTE entfernt, MANUAL_ENTRY bleibt)
CREATE TABLE booking_status_history_new (
    id INTEGER PRIMARY KEY,
    time_booking_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL CHECK (
        new_status IN (
            'OK',
            'OPEN',
            'WARN',
            'NEEDS_REVIEW',
            'CORRECTED',
            'MANUAL_ENTRY'
        )
    ),
    reason TEXT,
    changed_by_user_id INTEGER,
    changed_at TEXT NOT NULL,
    FOREIGN KEY (time_booking_id) REFERENCES time_bookings(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (changed_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

INSERT INTO booking_status_history_new SELECT * FROM booking_status_history;
DROP TABLE booking_status_history;
ALTER TABLE booking_status_history_new RENAME TO booking_status_history;

CREATE INDEX idx_booking_status_history_booking_changed_at
    ON booking_status_history(time_booking_id, changed_at);
