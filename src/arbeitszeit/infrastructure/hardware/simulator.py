from collections import deque
from datetime import datetime, timezone

from arbeitszeit.domain.enums import BookingType

from .ports import HardwareReader, RawBookingRequest


class SimulatedHardwareReader(HardwareReader):
    """In-Memory-Simulator für Tests und Entwicklung ohne physische Hardware."""

    def __init__(self) -> None:
        self._queue: deque[RawBookingRequest] = deque()

    def inject(
        self,
        booking_type: BookingType,
        uid_hash: str,
        occurred_at: datetime | None = None,
    ) -> None:
        self._queue.append(
            RawBookingRequest(
                booking_type=booking_type,
                uid_hash=uid_hash,
                occurred_at=occurred_at or datetime.now(timezone.utc),
            )
        )

    def read_next(self) -> RawBookingRequest:
        if not self._queue:
            raise RuntimeError("Keine Ereignisse in der Simulator-Warteschlange.")
        return self._queue.popleft()

    def close(self) -> None:
        pass

    @property
    def pending(self) -> int:
        return len(self._queue)
