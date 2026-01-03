from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import DbSession
from app.users.models import User


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with DbSession() as session:
        yield session

# def require_admin(user: User = Depends(get_current_user)):
def require_admin():
    # if user.role != "ADMIN":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin access required"
    #     )
    return "ADMIN"