from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session
from app.admin.repository import AdminRepository


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> AdminRepository:
    return AdminRepository(session)