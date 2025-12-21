from datetime import datetime, date, time, timedelta, timezone
from calendar import monthrange

from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.attendance.models import Attendance


class AttendanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_today_attendance(self, user_id: int):
        today_utc = datetime.now(timezone.utc).date()

        start = datetime.combine(today_utc, time.min, tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        stmt = (
            select(Attendance)
            .where(
                Attendance.user_id == user_id,
                Attendance.clock_in >= start,
                Attendance.clock_in < end
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, attendance: Attendance):
        self.session.add(attendance)
        await self.session.commit()
        await self.session.refresh(attendance)
        return attendance

    async def update(self, attendance: Attendance):
        await self.session.commit()
        await self.session.refresh(attendance)
        return attendance

    async def get_my_attendance(self, user_id: int):
        stmt = (
            select(Attendance)
            .where(Attendance.user_id == user_id)
            .order_by(Attendance.clock_in.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_attendance_by_month(
        self,
        user_id: int,
        year: int,
        month: int,
    ):
        start = datetime(year, month, 1, tzinfo=timezone.utc)
        end = datetime(
            year,
            month,
            monthrange(year, month)[1],
            23, 59, 59,
            tzinfo=timezone.utc
        )

        stmt = (
            select(Attendance)
            .where(
                Attendance.user_id == user_id,
                Attendance.clock_in >= start,
                Attendance.clock_in <= end,
            )
            .order_by(Attendance.clock_in.desc())
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()