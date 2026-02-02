import calendar
from calendar import month_name
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from app.attendance.models import Attendance
from app.attendance.repository import AttendanceRepository
from app.admin.schemas import AdminTimeEditSchema
from app.utils.date_utils import get_month_range
from app.utils.excel import create_attendance_excel

STANDARD_WORK_MINUTES = (8 * 60) + 30
IST = ZoneInfo("Asia/Kolkata")

class AttendanceService:
    def __init__(
        self, 
        attendance_repo: AttendanceRepository
    ):
        self.attendance_repo = attendance_repo

    def _group_by_user(self, rows):
        data = {}

        for attendance, user in rows:
            if user.id not in data:
                data[user.id] = {
                    "name": user.name,
                    "records": []
                }

            data[user.id]["records"].append({
                "date": attendance.attendance_date,
                "in_time": attendance.clock_in,
                "out_time": attendance.clock_out,
                "total_minutes": attendance.total_minutes,
                "ot_minutes": attendance.overtime_minutes,
            })

        return data

    async def today_attendace(self, user_id: int):
        today = date.today()
        return await self.attendance_repo.get_today_attendance(user_id, today)
    
    async def get_today_attendance_all_users(self):
        today = date.today()
        return await self.attendance_repo.get_today_attendance_all_users(today)

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
    
    async def edit_attendance_time(
        self,
        attendance_id: int,
        payload: AdminTimeEditSchema
    ):
        attendance = await self.attendance_repo.get_by_id(attendance_id)

        if not attendance:
            raise HTTPException(404, "Attendance not found")

        if not payload.clock_in and not payload.clock_out:
            raise HTTPException(400, "Nothing to update")

        # Apply updates
        if payload.clock_in:
            attendance.clock_in = payload.clock_in

        if payload.clock_out:
            attendance.clock_out = payload.clock_out

        # Validate time order
        if attendance.clock_in and attendance.clock_out:
            if attendance.clock_out <= attendance.clock_in:
                raise HTTPException(
                    400, "Clock-out must be after clock-in"
                )

            attendance.total_minutes = int(
                (attendance.clock_out - attendance.clock_in).total_seconds() // 60
            )
            attendance.overtime_minutes = max(
                0, attendance.total_minutes - STANDARD_WORK_MINUTES
            )

        attendance.is_manual = True
        await self.attendance_repo.update(attendance)

        return attendance
    
    async def get_attendance_by_month(
        self,
        user_id: int,
        cursor: str | None = None,
    ):
        if cursor:
            year, month = map(int, cursor.split("-"))
        else:
            now = datetime.now(timezone.utc)
            year, month = now.year, now.month

        # 🔑 Find the nearest month that actually has data
        latest = await self.attendance_repo.get_latest_month_with_data(
            user_id=user_id,
            before_year=year,
            before_month=month,
        )

        if not latest:
            return None  # ⛔ No more data at all

        year = int(latest.year)
        month = int(latest.month)

        records = await self.attendance_repo.get_attendance_by_month(
            user_id=user_id,
            year=year,
            month=month,
        )

        # Calculate next cursor (previous month)
        if month == 1:
            next_cursor = f"{year - 1}-12"
        else:
            next_cursor = f"{year}-{month - 1:02d}"

        return {
            "month": f"{month_name[month]} {year}",
            "month_key": f"{year}-{month:02d}",
            "records": records,
            "next_cursor": next_cursor,
        }
    
    async def get_attendance_by_user_id(self, user_id: int, month: str):
        year, month_num = map(int, month.split("-"))

        records = await self.attendance_repo.get_attendance_by_month(
            user_id=user_id,
            year=year,
            month=month_num,
        )

        return records
    
    async def get_monthly_summary(self, user_id: int, month: str):
        year, month_num = map(int, month.split("-"))
        start, end = get_month_range(year, month_num)

        today = date.today()
        days_in_month = calendar.monthrange(year, month_num)[1]

        # ✅ Decide effective end date
        if year == today.year and month_num == today.month:
            effective_end = today
            effective_days = today.day
        else:
            effective_end = end
            effective_days = days_in_month

        # -------- DATA FETCH --------
        aggregates = await self.attendance_repo.get_monthly_aggregates(
            user_id, start, effective_end
        )

        attendance_dates = await self.attendance_repo.get_attendance_dates(
            user_id, start, effective_end
        )

        paid_holiday_dates = await self.attendance_repo.get_paid_holiday_dates(
            start, effective_end
        )

        # -------- CALCULATIONS --------
        present_days = len(attendance_dates)
        paid_holidays = len(paid_holiday_dates)

        payable_dates = attendance_dates | paid_holiday_dates
        payable_days = len(payable_dates)

        absent_days = max(0, effective_days - payable_days)

        return {
            "month": month,
            "totalWorkingMinutes": aggregates["total_minutes"],
            "overtimeMinutes": aggregates["overtime_minutes"],
            "presentDays": present_days,
            "paidHolidays": paid_holidays,
            "payableDays": payable_days,
            "absentDays": absent_days,
        }
    
    async def get_missing_clock_out_count(self, user_id: int, start: date, end: date):
        return await self.attendance_repo.get_missing_clock_out_count(user_id, start, end)
    
    async def get_available_months_by_user_id(self, user_id: int) -> list[str]:
        return await self.attendance_repo.get_available_months_by_user_id(user_id)
    
    async def get_available_months_all_users(self) -> list[str]:
        return await self.attendance_repo.get_available_months_all_users()
    
    async def export_attendance_excel(self, start_date, end_date):
        rows = await self.attendance_repo.fetch_attendance_range(
            start_date=start_date,
            end_date=end_date,
        )

        grouped = self._group_by_user(rows)

        return create_attendance_excel(grouped)
