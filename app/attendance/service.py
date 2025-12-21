from datetime import datetime, timezone
from calendar import month_name

from fastapi import HTTPException, status

from app.attendance.models import Attendance
from app.attendance.repository import AttendanceRepository


class AttendanceService:
    def __init__(self, repo: AttendanceRepository):
        self.repo = repo

    async def clock_in(self, user_id: int):
        today_attendance = await self.repo.get_today_attendance(user_id)

        if today_attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already clocked in today"
            )

        attendance = Attendance(
            user_id=user_id,
            clock_in=datetime.now(timezone.utc),
            is_manual=False
        )
        return await self.repo.create(attendance)

    async def clock_out(self, user_id: int):
        attendance = await self.repo.get_today_attendance(user_id)

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
        attendance.total_minutes = int(
            (now - attendance.clock_in).total_seconds() / 60
        )

        return await self.repo.update(attendance)

    async def my_attendance(self, user_id: int):
        return await self.repo.get_my_attendance(user_id)
    
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

        records = await self.repo.get_attendance_by_month(
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
