import calendar
from calendar import month_name
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from app.attendance.models import Attendance
from app.attendance.repository import AttendanceRepository
from app.utils.date_utils import get_month_range

STANDARD_WORK_MINUTES = (8 * 60) + 30
IST = ZoneInfo("Asia/Kolkata")

class AttendanceService:
    def __init__(
        self, 
        attendance_repo: AttendanceRepository
    ):
        self.attendance_repo = attendance_repo

    async def today_attendace(self, user_id: int):
        today = date.today()
        return await self.attendance_repo.get_today_attendance(user_id, today)

    async def clock_in(self, user_id: int):
        today = date.today()
        today_attendance = await self.attendance_repo.get_today_attendance(user_id, today)

        if today_attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already clocked in today"
            )
        
        clock_in=datetime.now(timezone.utc)
        
        attendance = Attendance(
            user_id=user_id,
            clock_in=clock_in,
            attendance_date=clock_in.astimezone(IST).date(),
            is_manual=False
        )
        return await self.attendance_repo.create(attendance)

    async def clock_out(self, user_id: int):
        today = date.today()
        attendance = await self.attendance_repo.get_today_attendance(user_id, today)

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have not clocked in today"
            )

        if attendance.clock_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already clocked out"
            )

        now = datetime.now(timezone.utc)
        attendance.clock_out = now

        worked_minutes = int(
            (now - attendance.clock_in).total_seconds() // 60
        )
        worked_minutes = max(worked_minutes, 0)

        attendance.total_minutes = worked_minutes
        attendance.overtime_minutes = max(
            0,
            worked_minutes - STANDARD_WORK_MINUTES
        )

        return await self.attendance_repo.update(attendance)

    async def my_attendance(self, user_id: int):
        return await self.attendance_repo.get_my_attendance(user_id)
    
    async def my_attendance_my_month(
        self,
        user_id: int,
        cursor: str | None = None,
    ) -> dict:
        # Determine year & month
        if cursor:
            year, month = map(int, cursor.split("-"))
        else:
            now = datetime.now(timezone.utc)
            year, month = now.year, now.month

        records = await self.attendance_repo.get_attendance_by_month(
            user_id=user_id,
            year=year,
            month=month,
        )

        # Calculate previous month cursor
        if month == 1:
            next_cursor = f"{year - 1}-12"
        else:
            next_cursor = f"{year}-{month - 1:02d}"

        return {
            "month": f"{month_name[month]} {year}",
            "month_key": f"{year}-{month:02d}",
            "records": records,
            "next_cursor": next_cursor if records else None,
        }
    
    async def get_monthly_summary(self, user_id: int, month: str):
        year, month_num = map(int, month.split("-"))
        start, end = get_month_range(year, month_num)

        attendance = await self.attendance_repo.get_attendance_aggregates(
            user_id, start, end
        )

        attendance_dates = await self.attendance_repo.get_attendance_dates(
            user_id, start, end
        )

        paid_holiday_dates = await self.attendance_repo.get_paid_holiday_dates(
            start, end
        )

        days_in_month = calendar.monthrange(year, month_num)[1]

        payable_dates = attendance_dates | paid_holiday_dates
        payable_days = len(payable_dates)

        present_days = len(attendance_dates)

        today = date.today()

        days_in_month = calendar.monthrange(start.year, start.month)[1]

        if start.year == today.year and start.month == today.month:
            effective_days = today.day
        else:
            effective_days = days_in_month

        absent_days = max(0, effective_days - payable_days)

        return {
            "month": month,
            "totalWorkingMinutes": attendance["total_minutes"],
            "overtimeMinutes": attendance["overtime_minutes"],
            "presentDays": present_days,
            "paidHolidays": len(paid_holiday_dates),
            "payableDays": payable_days,
            "absentDays": absent_days
        }
    
    async def get_available_months(self, user_id: int) -> list[str]:
        return await self.attendance_repo.get_available_months(user_id)
