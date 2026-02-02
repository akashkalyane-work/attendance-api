from typing import Optional, Tuple
from datetime import datetime, timezone

from fastapi import HTTPException

from app.auth.repository import Repository
from app.auth.tokens import TokenManager
from app.core.config import settings
from app.core.password import verify_password
from app.users.repository import UserRepository


class Service:
    def __init__(self, repo: Repository, user_repo: UserRepository):
        self.repo = repo
        self.user_repo = user_repo
        self.tokens = TokenManager(
            settings.JWT_SECRET_KEY, 
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            settings.ALGORITHM
        )

    async def authenticate(self, email: str, password: str) -> Optional[Tuple[int, str]]:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user.id, user.role

    async def issue_tokens(self, user_id: int, role: str):
        access = self.tokens.create_access_token(user_id, role)
        refresh = self.tokens.create_refresh_token(user_id)

        payload = self.tokens.verify(refresh, "refresh")
        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc
        )

        await self.repo.upsert(user_id, refresh, expires_at)

        return access, refresh

    async def refresh(self, refresh_token: str):
        payload = self.tokens.verify(refresh_token, "refresh")
        user_id = int(payload["sub"])

        stored = await self.repo.validate(refresh_token)
        print("stored ", stored.expires_at, "now", datetime.now(timezone.utc))
        if not stored or stored.expires_at < datetime.now(timezone.utc):
            raise HTTPException(401, "Refresh token expired")
        
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(401, "User not found")

        return await self.issue_tokens(user_id, user.role)

    async def logout(self, user_id: int):
        await self.repo.revoke(user_id)