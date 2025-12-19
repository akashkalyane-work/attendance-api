from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase, AsyncAttrs):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)