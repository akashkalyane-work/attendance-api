from datetime import datetime
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
            clock_in=datetime.utcnow(),
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

        now = datetime.utcnow()
        attendance.clock_out = now
        attendance.total_minutes = int(
            (now - attendance.clock_in).total_seconds() / 60
        )

        return await self.repo.update(attendance)

    async def my_attendance(self, user_id: int):
        return await self.repo.get_my_attendance(user_id)
