from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from arbeitszeit.domain.enums import BookingType


class EmptyUidError(RuntimeError):
    """RFID-Lesegerät lieferte eine leere oder nicht mappbare UID."""


@dataclass(frozen=True)
class RawBookingRequest:
    booking_type: BookingType
    uid_hash: str
    occurred_at: datetime


class HardwareReader(Protocol):
    def read_next(self) -> RawBookingRequest: ...
    def close(self) -> None: ...
