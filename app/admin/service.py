from decimal import Decimal, ROUND_HALF_UP

from fastapi import Depends

from app.attendance.service import AttendanceService
from app.attendance.dependencies import AttendanceServiceDep
from app.attendance_request.service import AttendanceRequestService
from app.attendance_request.dependencies import AttendanceRequestServiceDep
from app.admin.repository import AdminRepository
from app.admin.dependencies import get_repository
from app.utils.date_utils import get_month_range

MINUTES_PER_DAY = 8 * 60 + 30


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
        return await self.attendance_service.get_attendance_by_month(user_id, cursor=month)

    async def approve_request(self, request_id: int, admin_id: int):
        # admin-specific checks/logging
        return await self.request_service.approve_request(
            request_id=request_id,
            admin_id=admin_id
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

            present_days = summary["presentDays"]
            overtime_minutes = Decimal(summary["overtimeMinutes"])

            ot_days = overtime_minutes / MINUTES_PER_DAY

            payable_days = Decimal(present_days) + ot_days

            payable_amount = (
                payable_days * user.hourly_rate
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
                "perDayRate": user.hourly_rate,
                "presentDays": summary["presentDays"],
                "paidHolidays": summary["paidHolidays"],
                "totalWorkingMinutes": summary["totalWorkingMinutes"],
                "overtimeMinutes": overtime_minutes,
                "payableAmount": payable_amount,
                "missingClockOutCount": missing_clock_outs,
            })

        return results
