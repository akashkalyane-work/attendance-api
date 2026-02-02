from typing import List
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.attendance.schemas import AttendanceResponseSchema, AttendanceSummaryResponse
from app.attendance.dependencies import AttendanceServiceDep
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.utils.date_utils import resolve_date_range


router = APIRouter(prefix="/attendances", tags=["attendances"])


@router.get("/today", response_model=AttendanceResponseSchema | None)
async def get_today_attendance(
    service: AttendanceServiceDep,
    user: User = Depends(get_current_user)
):
    return await service.today_attendace(user.id)

@router.post(
    "/clock-in",
    response_model=AttendanceResponseSchema,
    status_code=201
)
async def clock_in(
    service: AttendanceServiceDep,
    user: User = Depends(get_current_user)
):
    return await service.clock_in(user.id)


@router.post(
    "/clock-out",
    response_model=AttendanceResponseSchema
)
async def clock_out(
    service: AttendanceServiceDep,
    user: User = Depends(get_current_user)
):
    return await service.clock_out(user.id)


@router.get("/my")
async def my_attendance_by_month(
    service: AttendanceServiceDep,
    cursor: str | None = Query(
        default=None,
        description="Month cursor in YYYY-MM format"
    ),
    user: User = Depends(get_current_user),
):
    return await service.get_attendance_by_month(
        user.id,
        cursor=cursor,
    )

@router.get(
    "/summary",
    response_model=AttendanceSummaryResponse
)
async def get_attendance_summary(
    service: AttendanceServiceDep,
    month: str = Query(..., example="2025-12"),
    user: User = Depends(get_current_user),
):
    return await service.get_monthly_summary(user.id, month)

@router.get("/attendance/export/excel")
async def export_attendance_excel(
    service: AttendanceServiceDep,
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

@router.get("/months", response_model=List[str])
async def get_attendance_summary_months(
    service: AttendanceServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.get_available_months_by_user_id(user.id)
