from fastapi import APIRouter, Depends, Query

from app.core.dependencies import require_admin
from app.admin.service import AdminService
from app.attendance.schemas import TodayAttendanceAdminResponse
from app.attendance_request.schemas import AttendanceRequestResponseSchema, AttendanceRequestAdminResponse


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    # dependencies=[Depends(require_admin)]
)


@router.get(
    "/attendance/today",
    response_model=list[TodayAttendanceAdminResponse]
)
async def today_attendance_all_users(
    service: AdminService = Depends(),
):
    return await service.get_today_attendance_all_users()

@router.get("/attendance/monthly/{user_id}")
async def attendance_by_month(
    user_id: int,
    month: str | None = Query(
        default=None,
        description="Month in YYYY-MM format"
    ),
    service: AdminService = Depends()
):
    return await service.get_attendance_by_month(user_id, month)

@router.get(
    "/attendance-requests",
    response_model=list[AttendanceRequestAdminResponse]
)
async def list_requests(service: AdminService = Depends()):
    return await service.get_pending_requests()

@router.post(
    "/attendance-requests/{request_id}/approve",
    response_model=AttendanceRequestResponseSchema
)
async def approve_request(
    request_id: int,
    admin_id: int,
    service: AdminService = Depends()
):
    return await service.approve_request(request_id, admin_id)

@router.post(
    "/attendance-requests/{request_id}/reject",
    response_model=AttendanceRequestResponseSchema
)
async def reject_request(
    request_id: int,
    admin_id: int,
    service: AdminService = Depends()
):
    return await service.reject_request(request_id, admin_id)


@router.get("/attendance/summary")
async def monthly_summary(
    month: str  = Query(
        description="Month in YYYY-MM format"
    ),
    service: AdminService = Depends()
):
    return await service.get_monthly_summary(month)
