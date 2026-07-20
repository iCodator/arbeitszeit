__version__ = "1.1"

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from arbeitszeit.domain.enums import AdminAction, BookingType


class EmptyUidError(RuntimeError):
    """RFID-Lesegerät lieferte eine leere oder nicht mappbare UID."""


class HardwareTimeoutError(RuntimeError):
    """RFID-Lesevorgang hat das Zeitlimit überschritten."""


@dataclass(frozen=True)
class RawBookingRequest:
    booking_type: BookingType
    uid_hash: str
    occurred_at: datetime


@dataclass(frozen=True)
class AdminActionRequest:
    action: AdminAction


@runtime_checkable
class HardwareReader(Protocol):
    def read_next(self) -> RawBookingRequest | AdminActionRequest: ...
    def read_rfid_uid_hash(self, timeout: float = 15.0) -> str: ...
    def close(self) -> None: ...
