from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel


class AttendanceResponseSchema(BaseModel):
    id: int
    user_id: int
    clock_in: datetime
    clock_out: Optional[datetime]
    total_minutes: Optional[int]
    overtime_minutes: Optional[int]
    is_manual: bool

    class Config:
        from_attributes = True

class AttendanceSummaryResponse(BaseModel):
    month: str  # YYYY-MM
    totalWorkingMinutes: int
    overtimeMinutes: int
    presentDays: int
    absentDays: int
    paidHolidays: int
    payableDays: int

AttendanceState = Literal[
    "NOT_CLOCKED_IN",
    "CLOCKED_IN",
    "CLOCKED_OUT"
]

AttendanceSource = Literal[
    "ATTENDANCE",
    "REQUEST",
    "NONE"
]


class AttendanceTodayStateResponse(BaseModel):
    state: AttendanceState
    source: AttendanceSource

    effective_clock_in: Optional[datetime] = None
    effective_clock_out: Optional[datetime] = None

    can_clock_in: bool
    can_clock_out: bool

    can_request_clock_in: bool
    can_request_clock_out: bool

    message: Optional[str] = None