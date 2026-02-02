from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.models import BaseModel
from app.core.config import settings


engine = create_async_engine(settings.ASYNC_DATABASE_URL)
DbSession = async_sessionmaker(engine, expire_on_commit=False)

async def init_orm() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

async def close_orm() -> None:
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with DbSession() as session:
        yield session