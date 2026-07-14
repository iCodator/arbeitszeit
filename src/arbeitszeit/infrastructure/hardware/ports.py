__version__ = "1.0"

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from arbeitszeit.domain.enums import BookingType


class EmptyUidError(RuntimeError):
    """RFID-Lesegerät lieferte eine leere oder nicht mappbare UID."""


class HardwareTimeoutError(RuntimeError):
    """RFID-Lesevorgang hat das Zeitlimit überschritten."""


@dataclass(frozen=True)
class RawBookingRequest:
    booking_type: BookingType
    uid_hash: str
    occurred_at: datetime


@runtime_checkable
class HardwareReader(Protocol):
    def read_next(self) -> RawBookingRequest: ...
    def close(self) -> None: ...
