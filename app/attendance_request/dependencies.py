from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.attendance.repository import AttendanceRepository
from app.attendance_request.repository import AttendanceRequestRepository
from app.attendance_request.service import AttendanceRequestService


def get_service(
    session: AsyncSession = Depends(get_session),
):
    return AttendanceRequestService(
        AttendanceRequestRepository(session),
        AttendanceRepository(session),
    )


AttendanceRequestServiceDep = Annotated[
    AttendanceRequestService, Depends(get_service)
]