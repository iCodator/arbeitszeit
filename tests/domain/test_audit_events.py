import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.domain import audit_events

_EXPECTED = {
    audit_events.TIME_BOOKED,
    audit_events.BOOKING_REJECTED_UNKNOWN_CARD,
    audit_events.BOOKING_REJECTED_INACTIVE_CARD,
    audit_events.BOOKING_CORRECTED,
    audit_events.SUPPLEMENT_CREATED,
    audit_events.SUPPLEMENT_APPROVED,
    audit_events.SUPPLEMENT_REJECTED,
    audit_events.WORK_SCHEDULE_CHANGED,
    audit_events.BACKUP_CREATED,
    audit_events.BACKUP_SYNCED_TO_NAS,
    audit_events.BACKUP_SYNC_FAILED,
    audit_events.RESTORE_COMPLETED,
    audit_events.USER_ACCOUNT_CREATED,
    audit_events.USER_ACCOUNT_DEACTIVATED,
}


def test_alle_event_type_werte_sind_eindeutig():
    all_values = [
        v for k, v in vars(audit_events).items()
        if not k.startswith("_") and isinstance(v, str)
    ]
    assert len(all_values) == len(set(all_values)), (
        "Doppelte event_type-Werte im Katalog: " +
        str([v for v in all_values if all_values.count(v) > 1])
    )


def test_katalog_enthaelt_genau_die_erwarteten_namen():
    actual = {
        v for k, v in vars(audit_events).items()
        if not k.startswith("_") and isinstance(v, str)
    }
    assert actual == _EXPECTED, (
        f"Unbekannte: {actual - _EXPECTED}, Fehlende: {_EXPECTED - actual}"
    )
