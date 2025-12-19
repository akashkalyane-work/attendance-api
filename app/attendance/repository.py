from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.attendance.models import Attendance


class AttendanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_today_attendance(self, user_id: int):
        stmt = (
            select(Attendance)
            .where(
                Attendance.user_id == user_id,
                Attendance.clock_in.cast(date) == date.today()
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