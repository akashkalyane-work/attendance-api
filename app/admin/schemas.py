from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TodayAttendanceDashboardItem(BaseModel):
    attendance_id: Optional[int]
    user_id: int
    user_name: str
    clock_in: Optional[datetime]
    status: str   # Present | Late | Not In Yet


class PendingRequestDashboardItem(BaseModel):
    id: int
    user_id: int
    user_name: str
    request_type: str
    requested_time: datetime
    status: str


class AdminDashboardResponse(BaseModel):
    today_attendance: List[TodayAttendanceDashboardItem]
    pending_requests: List[PendingRequestDashboardItem]

class AdminTimeEditSchema(BaseModel):
    clock_in: datetime | None = None
    clock_out: datetime | None = None