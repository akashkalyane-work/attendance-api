from typing import Optional
from datetime import datetime

from sqlalchemy import String, Numeric, DateTime, Boolean, text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user"  # user | admin
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    perday_rate: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )