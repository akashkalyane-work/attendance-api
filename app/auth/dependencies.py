from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import OAuth2PasswordBearerWithCookie
from app.auth.service import Service
from app.auth.repository import Repository
from app.users.repository import UserRepository
from app.auth.tokens import TokenManager
from app.core.config import settings
from app.core.database import get_session


def get_repo(session: AsyncSession = Depends(get_session)):
    return Repository(session)


def get_user_repo(session: AsyncSession = Depends(get_session)):
    return UserRepository(session)


def get_service(
    repo=Depends(get_repo),
    user_repo=Depends(get_user_repo),
):
    return Service(repo, user_repo)


AuthServiceDep = Annotated[Service, Depends(get_service)]


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
):
    token_manager = TokenManager(
                        settings.JWT_SECRET_KEY, 
                        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
                        settings.ALGORITHM
                    )

    payload = token_manager.verify(token, expected="access")
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    repo = UserRepository(session)
    user = await repo.get_by_id(int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user