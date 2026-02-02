from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.users.repository import UserRepository
from app.users.service import UserService


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(session)


def get_service(
    repo: UserRepository = Depends(get_repository),
) -> UserService:
    return UserService(repo)


UserServiceDep = Annotated[
    UserService, Depends(get_service)
]