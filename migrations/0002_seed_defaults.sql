BEGIN;

INSERT INTO work_schedule_versions (
    scope_type,
    scope_employee_id,
    weekday,
    start_time,
    end_time,
    valid_from,
    valid_until,
    change_origin,
    changed_by_user_id,
    changed_at,
    reason
) VALUES
    ('GLOBAL', NULL, 1, '07:30', '18:00', '2026-01-01', NULL, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup'),
    ('GLOBAL', NULL, 2, '07:30', '18:00', '2026-01-01', NULL, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup'),
    ('GLOBAL', NULL, 3, '07:30', '18:00', '2026-01-01', NULL, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup'),
    ('GLOBAL', NULL, 4, '07:30', '14:00', '2026-01-01', NULL, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup'),
    ('GLOBAL', NULL, 5, '07:30', '16:00', '2026-01-01', NULL, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup');

INSERT INTO system_config (
    config_key,
    config_value_json,
    version,
    change_origin,
    changed_by_user_id,
    changed_at,
    reason
) VALUES
    ('app.timezone',                              '"Europe/Berlin"', 1, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup'),
    ('booking.grace_seconds_after_numpad_select', 30,              1, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup'),
    ('backup.nas_enabled',                        'false',         1, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup'),
    ('backup.nas_path',                           'null',          1, 'SYSTEM_SEED', NULL, '2026-01-01T00:00:00', 'initial default setup');

INSERT INTO audit_log (
    event_type, object_type, object_id,
    user_id, employee_id, event_at, details_json
)
SELECT
    'SEEDED',
    'WORK_SCHEDULE_VERSION',
    id,
    NULL, NULL,
    changed_at,
    json_object(
        'change_origin', change_origin,
        'scope_type',    scope_type,
        'weekday',       weekday,
        'start_time',    start_time,
        'end_time',      end_time,
        'valid_from',    valid_from,
        'reason',        reason
    )
FROM work_schedule_versions
WHERE change_origin = 'SYSTEM_SEED';

INSERT INTO audit_log (
    event_type, object_type, object_id,
    user_id, employee_id, event_at, details_json
)
SELECT
    'SEEDED',
    'SYSTEM_CONFIG',
    id,
    NULL, NULL,
    changed_at,
    json_object(
        'change_origin',      change_origin,
        'config_key',         config_key,
        'config_value_json',  config_value_json,
        'version',            version,
        'reason',             reason
    )
FROM system_config
WHERE change_origin = 'SYSTEM_SEED';

COMMIT;
