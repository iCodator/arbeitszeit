__version__ = "1.0"

class DomainError(Exception):
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", **context: object) -> None:
        super().__init__(message or self.code)
        self.message = message or self.code
        self.context = context


class UnknownCardError(DomainError):
    code = "UNKNOWN_CARD"


class InactiveCardError(DomainError):
    code = "INACTIVE_CARD"


class InactiveEmployeeError(DomainError):
    code = "INACTIVE_EMPLOYEE"


class InvalidBookingSequenceError(DomainError):
    code = "INVALID_BOOKING_SEQUENCE"


class OpenPhaseConflictError(DomainError):
    code = "OPEN_PHASE_CONFLICT"


class PermissionDeniedError(DomainError):
    code = "PERMISSION_DENIED"


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class ConflictError(DomainError):
    code = "CONFLICT"
