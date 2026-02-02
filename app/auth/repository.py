import hashlib
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _hash(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def get_by_user(self, user_id: int) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def upsert(
        self,
        user_id: int,
        refresh_token: str,
        expires_at: datetime,
    ):
        token_hash = self._hash(refresh_token)
        existing = await self.get_by_user(user_id)

        if existing:
            existing.token_hash = token_hash
            existing.expires_at = expires_at
            existing.revoked = False
        else:
            self.session.add(
                RefreshToken(
                    user_id=user_id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                )
            )

        await self.session.commit()

    async def validate(self, refresh_token: str) -> RefreshToken | None:
        token_hash = self._hash(refresh_token)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked.is_(False),
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def revoke(self, user_id: int):
        token = await self.get_by_user(user_id)
        if token:
            token.revoked = True
            await self.session.commit()