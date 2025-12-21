from typing import Optional
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    DateTime
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func

from app.core.database import BaseModel


class AttendanceRequest(BaseModel):
    __tablename__ = "attendance_requests"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    attendance_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("attendance.id", ondelete="SET NULL"),
        nullable=True
    )

    request_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
        # FORGOT_CLOCK_IN | FORGOT_CLOCK_OUT | TIME_EDIT
    )

    requested_clock_in: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    requested_clock_out: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False
        # PENDING | APPROVED | REJECTED
    )

    admin_comment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    reviewed_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # relationships
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[reviewed_by])
    attendance = relationship("Attendance", backref="requests")
