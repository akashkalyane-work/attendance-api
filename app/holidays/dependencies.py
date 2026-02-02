from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from .repository import PaidHolidayRepository
from .service import PaidHolidayService


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> PaidHolidayRepository:
    return PaidHolidayRepository(session)


def get_service(
    repo: PaidHolidayRepository = Depends(get_repository),
) -> PaidHolidayService:
    return PaidHolidayService(repo)


PaidHolidayServiceDep = Annotated[
    PaidHolidayService, Depends(get_service)
]