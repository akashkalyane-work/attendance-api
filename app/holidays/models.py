from typing import Optional
from datetime import date as DateType, datetime

from sqlalchemy import Date, String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import BaseModel


class PaidHoliday(BaseModel):
    __tablename__ = "paid_holidays"

    date: Mapped[DateType] = mapped_column(
        Date,
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now()
    )