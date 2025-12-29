from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo 

from fastapi import HTTPException, status

from app.attendance.models import Attendance
from app.attendance.schemas import AttendanceTodayStateResponse
from app.attendance_request.schemas import AttendanceRequestCreateSchema, AttendanceRequestResponseSchema
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

    async def get_today_state(
        self,
        user_id: int
    ) -> AttendanceTodayStateResponse:
        today = date.today()

        attendance = await self.attendance_repo.get_today_attendance(user_id, today)

        pending_clock_in_req = await self.request_repo.get_pending_request_by_user_id(
            user_id,
            today,
            AttendanceRequestType.FORGOT_CLOCK_IN
        )

        pending_clock_out_req = await self.request_repo.get_pending_request_by_user_id(
            user_id,
            today,
            AttendanceRequestType.FORGOT_CLOCK_OUT
        )

        # 1️⃣ Attendance exists
        if attendance:
            if attendance.clock_out:
                return AttendanceTodayStateResponse(
                    state="CLOCKED_OUT",
                    source="ATTENDANCE",
                    effective_clock_in=attendance.clock_in,
                    effective_clock_out=attendance.clock_out,
                    can_clock_in=False,
                    can_clock_out=False,
                    can_request_clock_in=False,
                    can_request_clock_out=False,
                    message="You have already clocked out"
                )

            return AttendanceTodayStateResponse(
                state="CLOCKED_IN",
                source="ATTENDANCE",
                effective_clock_in=attendance.clock_in,
                can_clock_in=False,
                can_clock_out=True,
                can_request_clock_in=False,
                can_request_clock_out=False
            )

        # 2️⃣ Pending clock-in request (virtual clock-in)
        if pending_clock_in_req:
            return AttendanceTodayStateResponse(
                state="CLOCKED_IN",
                source="REQUEST",
                effective_clock_in=pending_clock_in_req.requested_time,
                can_clock_in=False,
                can_clock_out=True,
                can_request_clock_in=False,
                can_request_clock_out=not bool(pending_clock_out_req),
                message="Clock-in request pending approval"
            )

        # 3️⃣ Pending clock-out request without attendance
        if pending_clock_out_req:
            return AttendanceTodayStateResponse(
                state="CLOCKED_OUT",
                source="REQUEST",
                can_clock_in=False,
                can_clock_out=False,
                can_request_clock_in=False,
                can_request_clock_out=False,
                message="Clock-out request pending approval"
            )

        # 4️⃣ Fresh day
        return AttendanceTodayStateResponse(
            state="NOT_CLOCKED_IN",
            source="NONE",
            can_clock_in=True,
            can_clock_out=False,
            can_request_clock_in=True,
            can_request_clock_out=False
        )

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
        
        today = date.today()

        attendance = await self.attendance_repo.get_today_attendance(request.user_id, today)

        # ---- APPLY CORRECTION ----
        if request.request_type == AttendanceRequestType.FORGOT_CLOCK_IN:
            if request.requested_time is None:
                raise HTTPException(400, "Requested clock-in missing")

            if attendance:
                attendance.clock_in = request.requested_time
                attendance.total_minutes = int(
                    (attendance.clock_out - attendance.clock_in).total_seconds() // 60
                )
                attendance.overtime_minutes = max(
                    0,
                    attendance.total_minutes - STANDARD_WORK_MINUTES
                )
                attendance.is_manual = True
                
                await self.attendance_repo.update(attendance)
            else:
                attendance = Attendance(
                    user_id=request.user_id,
                    clock_in=request.requested_time,
                    attendance_date=request.requested_time.astimezone(IST).date(),
                    is_manual=True
                )
                attendance = await self.attendance_repo.create(attendance)

            request.attendance_id = attendance.id

        elif request.request_type == AttendanceRequestType.FORGOT_CLOCK_OUT:
            if request.requested_time is None:
                raise HTTPException(400, "Requested clock-out missing")

            if not attendance or not attendance.clock_in:
                raise HTTPException(400, "Clock-in missing")

            attendance.clock_out = request.requested_time
            attendance.total_minutes = int(
                (attendance.clock_out - attendance.clock_in).total_seconds() // 60
            )
            attendance.overtime_minutes = max(
                0,
                attendance.total_minutes - STANDARD_WORK_MINUTES
            )
            attendance.is_manual = True

            await self.attendance_repo.update(attendance)

        else:
            raise HTTPException(400, "Unsupported request type")

        # ---- FINALIZE REQUEST ----
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

