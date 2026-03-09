from typing import AsyncGenerator
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.models import BaseModel
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)
DbSession = async_sessionmaker(engine, expire_on_commit=False)

async def init_orm() -> None:
    max_retries = 10
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.create_all)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"DB not ready (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("DB never became ready after %d attempts.", max_retries)
                raise

async def close_orm() -> None:
    await engine.dispose()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with DbSession() as session:
        yield session