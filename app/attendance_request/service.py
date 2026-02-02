from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo 

from fastapi import HTTPException, status

from app.attendance.models import Attendance
from app.attendance_request.schemas import AttendanceRequestCreateSchema, AttendanceRequestResponseSchema, AttendanceRequestAdminResponse
from app.attendance.repository import AttendanceRepository
from app.attendance_request.models import AttendanceRequest
from app.attendance_request.repository import AttendanceRequestRepository
from app.utils.date_utils import to_utc
from app.core.enums import AttendanceRequestType, AttendanceRequestStatus

STANDARD_WORK_MINUTES = (8 * 60) + 30
IST = ZoneInfo("Asia/Kolkata")


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
        today = date.today()
        today_attendance = await self.attendance_repo.get_today_attendance(user_id, today)

        request_data = {
            "user_id": user_id,
            "attendance_id": today_attendance.id if today_attendance else None,
            "request_type": data.request_type,
            "reason": data.reason,
        }

        if data.request_type == AttendanceRequestType.FORGOT_CLOCK_IN:
            request_data["requested_time"] = data.requested_time
        elif data.request_type == AttendanceRequestType.FORGOT_CLOCK_OUT:
            request_data["requested_time"] = data.requested_time

        req = AttendanceRequest(**request_data)
        req = await self.request_repo.create(req)

        return AttendanceRequestResponseSchema.model_validate(req)

    async def approve_request(
        self,
        request_id: int,
        admin_id: int
    ):
        request = await self.request_repo.get_by_id(request_id)

        if not request:
            raise HTTPException(404, "Request not found")

        if request.status != AttendanceRequestStatus.PENDING:
            raise HTTPException(400, "Request already processed")

        if not request.requested_time:
            raise HTTPException(400, "Requested time missing")

        attendance = None
        if request.attendance_id:
            attendance = await self.attendance_repo.get_by_id(
                request.attendance_id
            )

        if request.request_type == AttendanceRequestType.FORGOT_CLOCK_IN:

            if attendance:
                attendance.clock_in = request.requested_time
            else:
                attendance = Attendance(
                    user_id=request.user_id,
                    clock_in=request.requested_time,
                    attendance_date=request.requested_time.astimezone(IST).date(),
                    is_manual=True,
                )
                attendance = await self.attendance_repo.create(attendance)

            # If clock-out exists, recompute totals
            if attendance.clock_out:
                attendance.total_minutes = int(
                    (attendance.clock_out - attendance.clock_in).total_seconds() // 60
                )
                attendance.overtime_minutes = max(
                    0, attendance.total_minutes - STANDARD_WORK_MINUTES
                )

            attendance.is_manual = True
            await self.attendance_repo.update(attendance)

            request.attendance_id = attendance.id

        elif request.request_type == AttendanceRequestType.FORGOT_CLOCK_OUT:

            if not attendance or not attendance.clock_in:
                raise HTTPException(
                    400, "Cannot approve clock-out without clock-in"
                )

            attendance.clock_out = request.requested_time
            attendance.total_minutes = int(
                (attendance.clock_out - attendance.clock_in).total_seconds() // 60
            )
            attendance.overtime_minutes = max(
                0, attendance.total_minutes - STANDARD_WORK_MINUTES
            )
            attendance.is_manual = True

            await self.attendance_repo.update(attendance)

        else:
            raise HTTPException(400, "Unsupported request type")

        request.status = AttendanceRequestStatus.APPROVED
        request.reviewed_by = admin_id
        request.reviewed_at = datetime.now(timezone.utc)

        await self.request_repo.update(request)

        return request

    async def reject_request(
        self,
        request_id: int,
        admin_id: int
    ):
        request = await self.request_repo.get_by_id(request_id)

        if not request:
            raise HTTPException(404, "Request not found")

        if request.status != AttendanceRequestStatus.PENDING:
            raise HTTPException(400, "Request already processed")

        request.status = AttendanceRequestStatus.REJECTED
        request.reviewed_by = admin_id
        request.reviewed_at = datetime.now(timezone.utc)

        await self.request_repo.update(request)

        return request
    
    async def get_request_by_user_id(self, user_id: int) -> list[AttendanceRequestResponseSchema]:
        requests = await self.request_repo.get_my_requests(user_id)

        return [
            AttendanceRequestResponseSchema.model_validate(req)
            for req in requests
        ]

    async def get_pending_requests(self) -> list[AttendanceRequestAdminResponse]:
        requests = await self.request_repo.get_pending_requests()

        return [
            AttendanceRequestAdminResponse.model_validate(req)
            for req in requests
        ]

