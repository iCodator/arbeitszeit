-- Migration 0003: BookingStatus bereinigen
-- POSSIBLE_BREAK_VIOLATION, POSSIBLE_REST_VIOLATION, POSSIBLE_MAX_HOURS_VIOLATION
-- und MANUAL_ENTRY aus time_bookings.current_status entfernen.
-- Diese Zustaende werden durch ReviewCase + Severity abgebildet;
-- die Herkunft (manuell vs. Terminal) liegt in BookingSource.
--
-- booking_status_history.new_status: POSSIBLE_*-Werte entfernen,
-- MANUAL_ENTRY bleibt als Herkunftskennzeichnung von Statuswechseln.

-- time_bookings mit bereinigtem CHECK neu anlegen
CREATE TABLE time_bookings_new (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    rfid_card_id INTEGER,
    booking_type TEXT NOT NULL CHECK (booking_type IN ('COME', 'GO', 'BREAK_START', 'BREAK_END')),
    booked_at TEXT NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('TERMINAL', 'MANUAL', 'IMPORT')),
    terminal_id INTEGER,
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
    FOREIGN KEY (terminal_id) REFERENCES terminals(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

INSERT INTO time_bookings_new SELECT * FROM time_bookings;
DROP TABLE time_bookings;
ALTER TABLE time_bookings_new RENAME TO time_bookings;

-- booking_status_history mit bereinigtem CHECK neu anlegen
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
            'CLOSED_WITH_NOTE',
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

-- Indizes fuer time_bookings neu anlegen
CREATE INDEX idx_time_bookings_employee_booked_at
    ON time_bookings(employee_id, booked_at);

CREATE INDEX idx_time_bookings_status_booked_at
    ON time_bookings(current_status, booked_at);

-- Index fuer booking_status_history neu anlegen
CREATE INDEX idx_booking_status_history_booking_changed_at
    ON booking_status_history(time_booking_id, changed_at);
