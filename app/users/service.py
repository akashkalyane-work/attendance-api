from fastapi import HTTPException

from app.users.repository import UserRepository
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.core.password import hash_password


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_users(self):
        return await self.repo.list()

    async def create_user(self, data: UserCreate):
        if await self.repo.get_by_email(data.email):
            raise HTTPException(400, "Email already registered")

        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            perday_rate=data.perday_rate,
            role="user"
        )

        return await self.repo.create(user)

    async def update_user(self, user_id: int, data: UserUpdate):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        update_data = data.dict(exclude_unset=True)

        # Handle password separately — hash it and map to correct field
        if "password" in update_data:
            user.password_hash = hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        return await self.repo.update(user)

    async def delete_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        await self.repo.delete(user)