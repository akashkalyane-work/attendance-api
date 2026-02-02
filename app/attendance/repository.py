from datetime import datetime, date, timezone
from calendar import monthrange

from sqlalchemy import select, outerjoin, func, extract, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.attendance.models import Attendance
from app.users.models import User
from app.holidays.models import PaidHoliday
from app.core.enums import UserRole


class AttendanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, attendance_id: int):
        stmt = (
            select(Attendance)
            .where(
                Attendance.id == attendance_id
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

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

    async def get_today_attendance_all_users(self, today: date):
        stmt = (
            select(
                Attendance.id.label("attendance_id"),
                User.id.label("user_id"),
                User.name.label("user_name"),
                Attendance.clock_in,
            )
            .select_from(
                outerjoin(
                    User,
                    Attendance,
                    (Attendance.user_id == User.id)
                    & (Attendance.attendance_date == today),
                )
            )
            .where(User.role == UserRole.USER)   # ✅ EXCLUDE ADMINS
            .order_by(User.name)
        )

        result = await self.session.execute(stmt)
        return result.mappings().all()
    
    async def get_latest_month_with_data(
        self,
        user_id: int,
        before_year: int,
        before_month: int,
    ):
        stmt = (
            select(
                extract("year", Attendance.attendance_date).label("year"),
                extract("month", Attendance.attendance_date).label("month"),
            )
            .where(
                Attendance.user_id == user_id,
                or_(
                    extract("year", Attendance.attendance_date) < before_year,
                    and_(
                        extract("year", Attendance.attendance_date) == before_year,
                        extract("month", Attendance.attendance_date) <= before_month,
                    ),
                ),
            )
            .group_by("year", "month")
            .order_by(desc("year"), desc("month"))
            .limit(1)
        )

        row = (await self.session.execute(stmt)).first()
        return row
    
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
        self,
        user_id: int,
        start: date,
        end: date,
    ) -> set[date]:
        stmt = select(Attendance.attendance_date).where(
            Attendance.user_id == user_id,
            Attendance.attendance_date >= start,
            Attendance.attendance_date < end,
        ).distinct()

        res = await self.session.execute(stmt)
        return {row[0] for row in res.all()}

    async def get_missing_clock_out_count(
        self,
        user_id: int,
        start: date,
        end: date,
    ) -> int:
        stmt = select(func.count()).where(
            Attendance.user_id == user_id,
            Attendance.attendance_date >= start,
            Attendance.attendance_date < end,
            Attendance.clock_in.is_not(None),
            Attendance.clock_out.is_(None),
            Attendance.attendance_date < date.today(),  # exclude today
        )

        res = await self.session.execute(stmt)
        return res.scalar_one()
    
    async def get_paid_holiday_dates(
        self,
        start: date,
        end: date,
    ) -> set[date]:
        stmt = select(PaidHoliday.date).where(
            PaidHoliday.date >= start,
            PaidHoliday.date < end,
            PaidHoliday.is_active.is_(True),
        )

        res = await self.session.execute(stmt)
        return {row[0] for row in res.all()}

    async def get_monthly_aggregates(
        self,
        user_id: int,
        start: date,
        end: date,
    ):
        stmt = select(
            func.coalesce(func.sum(Attendance.total_minutes), 0),
            func.coalesce(func.sum(Attendance.overtime_minutes), 0),
        ).where(
            Attendance.user_id == user_id,
            Attendance.attendance_date >= start,
            Attendance.attendance_date < end,
        )

        res = await self.session.execute(stmt)
        total_minutes, overtime_minutes = res.one()

        return {
            "total_minutes": total_minutes,
            "overtime_minutes": overtime_minutes,
        }
    
    async def get_available_months_by_user_id(self, user_id: int) -> list[str]:
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
    
    async def get_available_months_all_users(self) -> list[str]:
        month_expr = func.to_char(
            func.date_trunc('month', Attendance.clock_in),
            'YYYY-MM'
        )

        stmt = (
            select(month_expr.label('month'))
            .group_by(month_expr)
            .order_by(month_expr.desc())
        )

        result = await self.session.execute(stmt)
        return [row.month for row in result.all()]
    
    async def fetch_attendance_range(self, start_date, end_date):
        stmt = (
            select(Attendance, User)
            .join(User)
            .where(
                Attendance.attendance_date.between(start_date, end_date)
            )
            .order_by(User.id, Attendance.attendance_date)
        )

        result = await self.session.execute(stmt)
        return result.all()