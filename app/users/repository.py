from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.users.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User):
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int):
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def list(self):
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def update(self, user: User):
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User):
        await self.session.delete(user)
        await self.session.commit()