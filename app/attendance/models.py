from typing import Optional
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    DateTime,
    Boolean,
    Integer
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func

from app.core.database import BaseModel
from app.users.models import User


class Attendance(BaseModel):
    __tablename__ = "attendance"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    clock_in: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    clock_out: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    total_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    is_manual: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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

    # relationships
    user: Mapped[User] = relationship("User", backref="attendances")


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


class AttendanceAudit(BaseModel):
    __tablename__ = "attendance_audit"

    attendance_id: Mapped[int] = mapped_column(
        ForeignKey("attendance.id", ondelete="CASCADE"),
        nullable=False
    )

    old_clock_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    old_clock_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    new_clock_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    new_clock_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    changed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    attendance = relationship("Attendance")
