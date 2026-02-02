from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.core.dependencies import require_admin
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.admin.service import AdminService
from app.admin.schemas import AdminTimeEditSchema
from app.admin.schemas import AdminDashboardResponse
from app.attendance.schemas import AttendanceResponseSchema
from app.attendance_request.schemas import AttendanceRequestResponseSchema, AttendanceRequestAdminResponse
from app.utils.date_utils import resolve_date_range


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse
)
async def admin_dashboard(
    service: AdminService = Depends(),
):
    return await service.get_dashboard()

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

@router.put(
    "/attendance/{attendance_id}/time",
    response_model=AttendanceResponseSchema
)
async def admin_edit_attendance_time(
    attendance_id: int,
    payload: AdminTimeEditSchema,
    service: AdminService = Depends()
):
    return await service.edit_attendance_time(
        attendance_id,
        payload
    )

@router.post(
    "/attendance-requests/{request_id}/approve",
    response_model=AttendanceRequestResponseSchema
)
async def approve_request(
    request_id: int,
    admin: User = Depends(get_current_user),
    service: AdminService = Depends()
):
    return await service.approve_request(request_id, admin.id)

@router.post(
    "/attendance-requests/{request_id}/reject",
    response_model=AttendanceRequestResponseSchema
)
async def reject_request(
    request_id: int,
    admin: User = Depends(get_current_user),
    service: AdminService = Depends()
):
    return await service.reject_request(request_id, admin.id)


@router.get("/attendance/summary")
async def monthly_summary(
    month: str  = Query(
        description="Month in YYYY-MM format"
    ),
    service: AdminService = Depends()
):
    return await service.get_monthly_summary(month)

@router.get("/attendance/months", response_model=list[str])
async def get_attendance_months(
    service: AdminService = Depends()
):
    return await service.get_available_months()

@router.get("/attendance/export/excel")
async def export_attendance_excel(
    service: AdminService = Depends(),
    start_date: date | None = None,
    end_date: date | None = None,
):
    start_date, end_date = resolve_date_range(start_date, end_date)

    excel_buffer = await service.export_attendance_excel(
        start_date=start_date,
        end_date=end_date,
    )

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=attendance_{start_date}_{end_date}.xlsx"
        },
    )
