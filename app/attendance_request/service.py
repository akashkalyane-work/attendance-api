from datetime import datetime, date

from fastapi import HTTPException, status

from app.attendance.models import Attendance
from app.attendance_request.schemas import AttendanceRequestCreateSchema
from app.attendance.repository import AttendanceRepository
from app.attendance_request.models import AttendanceRequest
from app.attendance_request.repository import AttendanceRequestRepository


class AttendanceRequestService:
    def __init__(
        self,
        request_repo: AttendanceRequestRepository,
        attendance_repo: AttendanceRepository,
    ):
        self.request_repo = request_repo
        self.attendance_repo = attendance_repo

    async def create_request(
        self,
        user_id: int,
        data: AttendanceRequestCreateSchema
    ):
        today_attendance = await self.attendance_repo.get_today_attendance(user_id)

        request = AttendanceRequest(
            user_id=user_id,
            attendance_id=today_attendance.id if today_attendance else None,
            request_type=data.request_type,
            requested_time=data.requested_time,
            reason=data.reason,
        )
        return await self.request_repo.create(request)

    async def approve_request(
        self,
        request_id: int,
        admin_id: int
    ):
        request = await self.request_repo.get_by_id(request_id)

        if not request or request.status != "PENDING":
            raise HTTPException(400, "Invalid request")

        attendance = request.attendance

        # Apply correction
        if request.request_type == "FORGOT_CLOCK_IN":
            if attendance:
                attendance.clock_in = request.requested_time
            else:
                attendance = Attendance(
                    user_id=request.user_id,
                    clock_in=request.requested_time,
                    is_manual=True
                )
                await self.attendance_repo.create(attendance)

        elif request.request_type == "FORGOT_CLOCK_OUT":
            if not attendance or not attendance.clock_in:
                raise HTTPException(400, "Clock-in missing")

            attendance.clock_out = request.requested_time
            attendance.total_minutes = int(
                (attendance.clock_out - attendance.clock_in).total_seconds() / 60
            )
            attendance.is_manual = True
            await self.attendance_repo.update(attendance)

        request.status = "APPROVED"
        request.reviewed_by = admin_id
        request.reviewed_at = datetime.utcnow()

        return await self.request_repo.create(request)

    async def reject_request(
        self,
        request_id: int,
        admin_id: int
    ):
        request = await self.request_repo.get_by_id(request_id)

        if not request or request.status != "PENDING":
            raise HTTPException(400, "Invalid request")

        request.status = "REJECTED"
        request.reviewed_by = admin_id
        request.reviewed_at = datetime.utcnow()

        return await self.request_repo.create(request)