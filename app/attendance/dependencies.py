from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session
from app.attendance.repository import AttendanceRepository
from app.attendance.service import AttendanceService


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> AttendanceRepository:
    return AttendanceRepository(session)


def get_service(
    repo: AttendanceRepository = Depends(get_repository),
) -> AttendanceService:
    return AttendanceService(repo)


AttendanceServiceDep = Annotated[
    AttendanceService, Depends(get_service)
]