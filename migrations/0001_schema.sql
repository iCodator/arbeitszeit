PRAGMA foreign_keys = ON;

BEGIN;

CREATE TABLE schema_migrations (
    version TEXT NOT NULL PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    personnel_no TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    employment_start TEXT,
    employment_end TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (employment_end IS NULL OR employment_start IS NULL OR employment_end >= employment_start)
);

CREATE TABLE user_accounts (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('EMPLOYEE', 'ADMIN', 'REVIEWER', 'TECH')),
    employee_id INTEGER,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE rfid_cards (
    id INTEGER PRIMARY KEY,
    uid_hash TEXT NOT NULL UNIQUE,
    employee_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'INACTIVE', 'REPLACED', 'LOST')),
    valid_from TEXT NOT NULL,
    valid_until TEXT,
    replaced_by_card_id INTEGER,
    created_at TEXT NOT NULL,
    CHECK (valid_until IS NULL OR valid_until >= valid_from),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (replaced_by_card_id) REFERENCES rfid_cards(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE terminals (
    id INTEGER PRIMARY KEY,
    terminal_code TEXT NOT NULL UNIQUE,
    hostname TEXT,
    location_text TEXT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE time_bookings (
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
            'CLOSED_WITH_NOTE',
            'POSSIBLE_BREAK_VIOLATION',
            'POSSIBLE_REST_VIOLATION',
            'POSSIBLE_MAX_HOURS_VIOLATION',
            'MANUAL_ENTRY'
        )
    ),
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (rfid_card_id) REFERENCES rfid_cards(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (terminal_id) REFERENCES terminals(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE booking_status_history (
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
            'POSSIBLE_BREAK_VIOLATION',
            'POSSIBLE_REST_VIOLATION',
            'POSSIBLE_MAX_HOURS_VIOLATION',
            'MANUAL_ENTRY'
        )
    ),
    reason TEXT,
    changed_by_user_id INTEGER,
    changed_at TEXT NOT NULL,
    FOREIGN KEY (time_booking_id) REFERENCES time_bookings(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (changed_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE booking_corrections (
    id INTEGER PRIMARY KEY,
    time_booking_id INTEGER NOT NULL,
    old_values_json TEXT NOT NULL,
    new_values_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    corrected_by_user_id INTEGER NOT NULL,
    corrected_at TEXT NOT NULL,
    FOREIGN KEY (time_booking_id) REFERENCES time_bookings(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (corrected_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE supplements (
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
    CHECK (
        (approval_status = 'PENDING' AND approved_by_user_id IS NULL AND approved_at IS NULL)
        OR
        (approval_status IN ('APPROVED', 'REJECTED') AND approved_by_user_id IS NOT NULL AND approved_at IS NOT NULL)
    ),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (related_time_booking_id) REFERENCES time_bookings(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (recorded_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (approved_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE review_cases (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    time_booking_id INTEGER,
    case_type TEXT NOT NULL CHECK (
        case_type IN (
            'OPEN_WORK_PHASE',
            'OPEN_BREAK_PHASE',
            'OUTSIDE_SCHEDULE_WINDOW',
            'POSSIBLE_BREAK_VIOLATION',
            'POSSIBLE_REST_VIOLATION',
            'POSSIBLE_MAX_HOURS_VIOLATION',
            'IMPLAUSIBLE_SEQUENCE',
            'UNKNOWN_CARD_ATTEMPT',
            'INACTIVE_CARD_ATTEMPT',
            'TIME_ANOMALY',
            'MANUAL_ENTRY_REVIEW'
        )
    ),
    status TEXT NOT NULL CHECK (status IN ('OPEN', 'IN_REVIEW', 'RESOLVED', 'CLOSED_WITH_NOTE')),
    severity TEXT NOT NULL CHECK (severity IN ('INFO', 'WARN', 'CRITICAL')),
    detected_at TEXT NOT NULL,
    description TEXT NOT NULL,
    closed_at TEXT,
    closed_by_user_id INTEGER,
    CHECK (
        (status IN ('OPEN', 'IN_REVIEW') AND closed_at IS NULL AND closed_by_user_id IS NULL)
        OR
        (status IN ('RESOLVED', 'CLOSED_WITH_NOTE') AND closed_at IS NOT NULL AND closed_by_user_id IS NOT NULL)
    ),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (time_booking_id) REFERENCES time_bookings(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (closed_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE review_case_actions (
    id INTEGER PRIMARY KEY,
    review_case_id INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK (
        action_type IN (
            'CREATED',
            'COMMENT_ADDED',
            'STATUS_CHANGED',
            'CORRECTION_LINKED',
            'SUPPLEMENT_LINKED',
            'CLOSED',
            'REOPENED'
        )
    ),
    note TEXT,
    performed_by_user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (review_case_id) REFERENCES review_cases(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (performed_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE work_schedule_versions (
    id INTEGER PRIMARY KEY,
    scope_type TEXT NOT NULL CHECK (scope_type IN ('GLOBAL', 'EMPLOYEE')),
    scope_employee_id INTEGER,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 1 AND 7),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    valid_until TEXT,
    change_origin TEXT NOT NULL CHECK (change_origin IN ('SYSTEM_SEED', 'ADMIN_UI', 'MIGRATION')),
    changed_by_user_id INTEGER,
    changed_at TEXT NOT NULL,
    reason TEXT,
    CHECK (
        (scope_type = 'GLOBAL' AND scope_employee_id IS NULL)
        OR
        (scope_type = 'EMPLOYEE' AND scope_employee_id IS NOT NULL)
    ),
    CHECK (valid_until IS NULL OR valid_until >= valid_from),
    CHECK (
        (change_origin = 'SYSTEM_SEED' AND changed_by_user_id IS NULL)
        OR
        (change_origin = 'ADMIN_UI' AND changed_by_user_id IS NOT NULL)
        OR
        (change_origin = 'MIGRATION')
    ),
    FOREIGN KEY (scope_employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (changed_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE system_config (
    id INTEGER PRIMARY KEY,
    config_key TEXT NOT NULL,
    config_value_json TEXT NOT NULL,
    version INTEGER NOT NULL,
    change_origin TEXT NOT NULL CHECK (change_origin IN ('SYSTEM_SEED', 'ADMIN_UI', 'MIGRATION')),
    changed_by_user_id INTEGER,
    changed_at TEXT NOT NULL,
    reason TEXT,
    UNIQUE (config_key, version),
    CHECK (
        (change_origin = 'SYSTEM_SEED' AND changed_by_user_id IS NULL)
        OR
        (change_origin = 'ADMIN_UI' AND changed_by_user_id IS NOT NULL)
        OR
        (change_origin = 'MIGRATION')
    ),
    FOREIGN KEY (changed_by_user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE device_events (
    id INTEGER PRIMARY KEY,
    event_type TEXT NOT NULL CHECK (
        event_type IN (
            'NUMPAD_INPUT',
            'RFID_SCAN',
            'UNKNOWN_CARD',
            'INACTIVE_CARD',
            'CARD_ASSIGNMENT_FAILURE',
            'BOOKING_ACCEPTED',
            'BOOKING_REJECTED'
        )
    ),
    terminal_id INTEGER,
    rfid_uid_hash TEXT,
    payload_json TEXT,
    occurred_at TEXT NOT NULL,
    related_time_booking_id INTEGER,
    FOREIGN KEY (terminal_id) REFERENCES terminals(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (related_time_booking_id) REFERENCES time_bookings(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE system_events (
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
            'APPLICATION_STOP'
        )
    ),
    source TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('INFO', 'WARN', 'ERROR')),
    event_at TEXT NOT NULL,
    details_json TEXT,
    related_object_type TEXT,
    related_object_id INTEGER
);

CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    event_type TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id INTEGER NOT NULL,
    user_id INTEGER,
    employee_id INTEGER,
    event_at TEXT NOT NULL,
    details_json TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_accounts(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE INDEX idx_user_accounts_employee_id
    ON user_accounts(employee_id);

CREATE INDEX idx_rfid_cards_employee_status
    ON rfid_cards(employee_id, status);

CREATE INDEX idx_time_bookings_employee_booked_at
    ON time_bookings(employee_id, booked_at);

CREATE INDEX idx_time_bookings_status_booked_at
    ON time_bookings(current_status, booked_at);

CREATE INDEX idx_booking_status_history_booking_changed_at
    ON booking_status_history(time_booking_id, changed_at);

CREATE INDEX idx_booking_corrections_booking_corrected_at
    ON booking_corrections(time_booking_id, corrected_at);

CREATE INDEX idx_supplements_employee_event_at
    ON supplements(employee_id, event_at);

CREATE INDEX idx_supplements_approval_status
    ON supplements(approval_status, recorded_at);

CREATE INDEX idx_review_cases_status_detected_at
    ON review_cases(status, detected_at);

CREATE INDEX idx_review_cases_employee_detected_at
    ON review_cases(employee_id, detected_at);

CREATE INDEX idx_review_case_actions_case_created_at
    ON review_case_actions(review_case_id, created_at);

CREATE INDEX idx_work_schedule_versions_scope_weekday_valid_from
    ON work_schedule_versions(scope_type, scope_employee_id, weekday, valid_from);

CREATE INDEX idx_system_config_key_version
    ON system_config(config_key, version);

CREATE INDEX idx_device_events_occurred_at
    ON device_events(occurred_at);

CREATE INDEX idx_system_events_event_at
    ON system_events(event_at);

CREATE INDEX idx_audit_log_object_event_at
    ON audit_log(object_type, object_id, event_at);

CREATE INDEX idx_audit_log_employee_event_at
    ON audit_log(employee_id, event_at);

COMMIT;
