from datetime import datetime
from typing import Optional
from pydantic import BaseModel, computed_field, Field

from app.core.enums import AttendanceRequestType, AttendanceRequestStatus
from app.users.schemas import UserResponse


class AttendanceRequestCreateSchema(BaseModel):
    request_type: AttendanceRequestType
    requested_time: datetime
    reason: str


class AttendanceRequestResponseSchema(BaseModel):
    id: int
    user_id: int
    attendance_id: Optional[int]
    request_type: AttendanceRequestType
    requested_time: datetime
    reason: str
    status: AttendanceRequestStatus
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True

class AttendanceRequestAdminResponse(BaseModel):
    id: int
    user: UserResponse
    attendance_id: Optional[int]
    request_type: AttendanceRequestType
    requested_time: datetime
    reason: str
    status: AttendanceRequestStatus
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True