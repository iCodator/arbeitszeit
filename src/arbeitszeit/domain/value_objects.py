"""Starke ID-Typen für das Domain-Modell.

Alle IDs basieren auf `int`, sind aber für mypy distinkte Typen —
`EmployeeId` und `TimeBookingId` sind zwar beide `int`, aber nicht
wechselseitig assignierbar. So erkennt mypy z. B. versehentlich
vertauschte Parameter bereits statisch, ohne Laufzeit-Overhead.

Verwendung (Konstruktion):
    emp = Employee(id=EmployeeId(row["id"]), ...)
    booking = TimeBooking(employee_id=emp.id, ...)  # emp.id ist EmployeeId ✓

Wichtig: Alle IDs sind Subtypen von `int` — NewType-Werte sind überall
dort verwendbar, wo `int` erwartet wird (z. B. SQL-Parameter).
"""

__version__ = "1.0"

from typing import NewType

EmployeeId = NewType("EmployeeId", int)
UserAccountId = NewType("UserAccountId", int)
RfidCardId = NewType("RfidCardId", int)
TerminalId = NewType("TerminalId", int)
TimeBookingId = NewType("TimeBookingId", int)
WorkScheduleVersionId = NewType("WorkScheduleVersionId", int)
ReviewCaseId = NewType("ReviewCaseId", int)
SupplementId = NewType("SupplementId", int)
BookingCorrectionId = NewType("BookingCorrectionId", int)
DeviceEventId = NewType("DeviceEventId", int)
AuditLogEntryId = NewType("AuditLogEntryId", int)
