from datetime import datetime, date, time, timedelta, timezone
from calendar import monthrange

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.attendance.models import Attendance
from app.holidays.models import PaidHoliday


class AttendanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_today_attendance(self, user_id: int, today: date):
        stmt = (
            select(Attendance)
            .where(
                Attendance.user_id == user_id,
                Attendance.attendance_date == today
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
    
    async def get_attendance_dates(
        self, user_id: int, start: date, end: date
    ) -> set[date]:
        stmt = select(func.date(Attendance.clock_in)).where(
            Attendance.user_id == user_id,
            Attendance.clock_in >= start,
            Attendance.clock_in < end
        ).distinct()

        res = await self.session.execute(stmt)
        return {row[0] for row in res.all()}
    
    async def get_paid_holiday_dates(self, start: date, end: date) -> set[date]:
        stmt = select(PaidHoliday.date).where(
            PaidHoliday.date >= start,
            PaidHoliday.date < end,
            PaidHoliday.is_active.is_(True)
        )

        res = await self.session.execute(stmt)
        return {row[0] for row in res.all()}
    
    async def get_paid_holidays_count(self, start: date, end: date) -> int:
        stmt = select(func.count()).where(
            PaidHoliday.date >= start,
            PaidHoliday.date < end,
            PaidHoliday.is_active == True
        )
        res = await self.session.execute(stmt)
        return res.scalar() or 0

    async def get_attendance_aggregates(self, user_id: int, start: date, end: date):
        stmt = select(
            func.sum(Attendance.total_minutes),
            func.sum(Attendance.overtime_minutes),
            func.count(func.distinct(func.date(Attendance.clock_in)))
        ).where(
            Attendance.user_id == user_id,
            Attendance.clock_in >= start,
            Attendance.clock_in < end
        )

        res = await self.session.execute(stmt)
        total_minutes, overtime_minutes, present_days = res.one()

        return {
            "total_minutes": total_minutes or 0,
            "overtime_minutes": overtime_minutes or 0,
            "present_days": present_days or 0
        }
    
    async def get_available_months(self, user_id: int) -> list[str]:
        month_expr = func.to_char(
            func.date_trunc('month', Attendance.clock_in),
            'YYYY-MM'
        )

        stmt = (
            select(month_expr.label('month'))
            .where(Attendance.user_id == user_id)
            .group_by(month_expr)
            .order_by(month_expr.desc())
        )

        result = await self.session.execute(stmt)
        return [row.month for row in result.all()]