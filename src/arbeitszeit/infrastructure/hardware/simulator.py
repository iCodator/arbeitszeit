__version__ = "1.1"

from collections import deque
from datetime import datetime, timezone

from arbeitszeit.domain.enums import AdminAction, BookingType

from .ports import AdminActionRequest, HardwareReader, RawBookingRequest


class SimulatedHardwareReader(HardwareReader):
    """In-Memory-Simulator für Tests und Entwicklung ohne physische Hardware."""

    def __init__(self) -> None:
        self._queue: deque[RawBookingRequest | AdminActionRequest] = deque()
        self._rfid_queue: deque[str] = deque()

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

    def inject_admin_action(self, action: AdminAction) -> None:
        self._queue.append(AdminActionRequest(action=action))

    def inject_rfid_uid_hash(self, uid_hash: str) -> None:
        self._rfid_queue.append(uid_hash)

    def read_next(self) -> RawBookingRequest | AdminActionRequest:
        if not self._queue:
            raise RuntimeError("Keine Ereignisse in der Simulator-Warteschlange.")
        return self._queue.popleft()

    def read_rfid_uid_hash(self, timeout: float = 15.0) -> str:
        if not self._rfid_queue:
            raise RuntimeError("Keine RFID-UID in der Simulator-Warteschlange.")
        return self._rfid_queue.popleft()

    def close(self) -> None:
        pass

    @property
    def pending(self) -> int:
        return len(self._queue)
