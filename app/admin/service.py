from datetime import datetime, time
from zoneinfo import ZoneInfo
from decimal import Decimal, ROUND_HALF_UP

from fastapi import Depends

from app.attendance.service import AttendanceService
from app.attendance.dependencies import AttendanceServiceDep
from app.attendance_request.service import AttendanceRequestService
from app.attendance_request.dependencies import AttendanceRequestServiceDep
from app.admin.schemas import (
    AdminDashboardResponse,
    TodayAttendanceDashboardItem,
    PendingRequestDashboardItem
)
from app.admin.repository import AdminRepository
from app.admin.dependencies import get_repository
from app.admin.schemas import AdminTimeEditSchema
from app.utils.date_utils import get_month_range

MINUTES_PER_DAY = 8 * 60 + 30
IST = ZoneInfo("Asia/Kolkata")


class AdminService:
    def __init__(
        self,
        attendance_service: AttendanceServiceDep,
        request_service: AttendanceRequestServiceDep,
        admin_repo: AdminRepository = Depends(get_repository)
    ):
        self.admin_repo = admin_repo
        self.attendance_service = attendance_service
        self.request_service = request_service

    async def get_today_attendance_all_users(self):
        return await self.attendance_service.get_today_attendance_all_users()
    
    async def get_attendance_by_month(self, user_id: int, month: str):
        return await self.attendance_service.get_attendance_by_user_id(user_id, month)

    async def approve_request(self, request_id: int, admin_id: int):
        # admin-specific checks/logging
        return await self.request_service.approve_request(
            request_id=request_id,
            admin_id=admin_id
        )
    
    async def edit_attendance_time(self, attendance_id: int, payload: AdminTimeEditSchema):
        return await self.attendance_service.edit_attendance_time(
            attendance_id,
            payload
        )
    
    async def reject_request(self, request_id: int, admin_id: int):
        return await self.request_service.reject_request(
            request_id,
            admin_id
        )

    async def get_pending_requests(self):
        return await self.request_service.get_pending_requests()
    
    async def get_monthly_summary(self, month: str):
        users = await self.admin_repo.get_users_with_attendance()
        results = []

        for user in users:
            summary = await self.attendance_service.get_monthly_summary(
                user.id, month
            )

            if summary["presentDays"] == 0:
                continue

            worked_days = (
                Decimal(summary["totalWorkingMinutes"]) / MINUTES_PER_DAY
            )

            paid_holiday_days = Decimal(summary["paidHolidays"])

            payable_days = worked_days + paid_holiday_days

            payable_amount = (
                payable_days * user.perday_rate
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # ---- Missing clock-out
            year, month_num = map(int, month.split("-"))
            start, end = get_month_range(year, month_num)

            missing_clock_outs = await self.attendance_service.get_missing_clock_out_count(
                user.id, start, end
            )

            results.append({
                "userId": user.id,
                "userName": user.name,
                "perDayRate": user.perday_rate,
                "presentDays": summary["presentDays"],
                "paidHolidays": summary["paidHolidays"],
                "absentDays": summary["absentDays"],
                "totalWorkingMinutes": summary["totalWorkingMinutes"],
                "overtimeMinutes": summary["overtimeMinutes"],
                "payableAmount": payable_amount,
                "missingClockOutCount": missing_clock_outs,
            })

        return results
    
    async def get_dashboard(self) -> AdminDashboardResponse:
        today_attendance = await self.get_today_attendance_all_users()
        pending_requests = await self.get_pending_requests()

        dashboard_attendance = []

        for item in today_attendance:
            status = "Not In Yet"

            if item.clock_in:
                clock_in = item.clock_in.astimezone(IST)

                late_cutoff = datetime.combine(
                    clock_in.date(),
                    time(9, 00),
                    tzinfo=IST
                )

                status = "Late" if clock_in > late_cutoff else "Present"

            dashboard_attendance.append(
                TodayAttendanceDashboardItem(
                    attendance_id=item.attendance_id,
                    user_id=item.user_id,
                    user_name=item.user_name,
                    clock_in=item.clock_in,
                    status=status
                )
            )

        dashboard_requests = [
            PendingRequestDashboardItem(
                id=req.id,
                user_id=req.user.id if req.user else req.user_id,
                user_name=req.user.name if req.user else "Unknown",
                request_type=req.request_type.label(),
                requested_time=req.requested_time,
                status=req.status
            )
            for req in pending_requests
        ]

        return AdminDashboardResponse(
            today_attendance=dashboard_attendance,
            pending_requests=dashboard_requests[:5]  # limit for dashboard
        )

    async def get_available_months(self):
        return await self.attendance_service.get_available_months_all_users()
    
    async def export_attendance_excel(self, start_date, end_date):
        return await self.attendance_service.export_attendance_excel(start_date, end_date)
