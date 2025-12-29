from typing import Optional
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    DateTime,
    Enum as SAEnum
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func

from app.core.database import BaseModel
from app.core.enums import AttendanceRequestType, AttendanceRequestStatus


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

    request_type: Mapped[AttendanceRequestType] = mapped_column(
        SAEnum(AttendanceRequestType, name="attendance_request_type"),
        nullable=False
    )

    requested_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[AttendanceRequestStatus] = mapped_column(
        SAEnum(AttendanceRequestStatus, name="attendance_request_status"),
        default=AttendanceRequestStatus.PENDING,
        nullable=False
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
