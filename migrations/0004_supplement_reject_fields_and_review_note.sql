-- Migration 0004: Semantische Trennung Genehmigung/Ablehnung bei Nachtraegen
-- und Notizfeld fuer Prueffaelle.
--
-- supplements: rejected_by_user_id / rejected_at als eigene Felder statt
-- Wiederverwendung der approved_by-Felder fuer Ablehnungen.
--
-- review_cases: note TEXT fuer Schliessungsbegruendung bei CLOSED_WITH_NOTE.

-- supplements mit semantisch getrennten Feldern neu anlegen
CREATE TABLE supplements_new (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    related_time_booking_id INTEGER,
    booking_type TEXT NOT NULL CHECK (booking_type IN ('COME', 'GO', 'BREAK_START', 'BREAK_END')),
    event_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    reason TEXT NOT NULL,
    recorded_by_user_id INTEGER NOT NULL,
    approval_status TEXT NOT NULL CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED')),
    approved_by_user_id INTEGER,
    approved_at TEXT,
    rejected_by_user_id INTEGER,
    rejected_at TEXT,
    CHECK (
        (approval_status = 'PENDING'
            AND approved_by_user_id IS NULL AND approved_at IS NULL
            AND rejected_by_user_id IS NULL AND rejected_at IS NULL)
        OR
        (approval_status = 'APPROVED'
            AND approved_by_user_id IS NOT NULL AND approved_at IS NOT NULL
            AND rejected_by_user_id IS NULL AND rejected_at IS NULL)
        OR
        (approval_status = 'REJECTED'
            AND rejected_by_user_id IS NOT NULL AND rejected_at IS NOT NULL
            AND approved_by_user_id IS NULL AND approved_at IS NULL)
    ),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (related_time_booking_id) REFERENCES time_bookings(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (recorded_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (approved_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (rejected_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

INSERT INTO supplements_new (
    id, employee_id, related_time_booking_id, booking_type, event_at,
    recorded_at, reason, recorded_by_user_id, approval_status,
    approved_by_user_id, approved_at, rejected_by_user_id, rejected_at
)
SELECT
    id, employee_id, related_time_booking_id, booking_type, event_at,
    recorded_at, reason, recorded_by_user_id, approval_status,
    CASE WHEN approval_status = 'APPROVED' THEN approved_by_user_id ELSE NULL END,
    CASE WHEN approval_status = 'APPROVED' THEN approved_at ELSE NULL END,
    CASE WHEN approval_status = 'REJECTED' THEN approved_by_user_id ELSE NULL END,
    CASE WHEN approval_status = 'REJECTED' THEN approved_at ELSE NULL END
FROM supplements;

DROP TABLE supplements;
ALTER TABLE supplements_new RENAME TO supplements;

CREATE INDEX idx_supplements_employee_event_at
    ON supplements(employee_id, event_at);
CREATE INDEX idx_supplements_approval_status
    ON supplements(approval_status, recorded_at);

-- review_cases: Notizfeld hinzufuegen
ALTER TABLE review_cases ADD COLUMN note TEXT;
