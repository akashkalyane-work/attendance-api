from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.core.enums import UserRole


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users_with_attendance(self):
        stmt = select(
            User.id,
            User.name,
            User.perday_rate,
        ).where(User.role == UserRole.USER)

        res = await self.session.execute(stmt)
        return res.all()