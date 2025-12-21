from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AttendanceRequestCreateSchema(BaseModel):
    request_type: str = Field(
        examples=["FORGOT_CLOCK_IN", "FORGOT_CLOCK_OUT"]
    )
    requested_time: datetime
    reason: str


class AttendanceRequestResponseSchema(BaseModel):
    id: int
    user_id: int
    attendance_id: Optional[int]
    request_type: str
    requested_time: datetime
    reason: str
    status: str
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True