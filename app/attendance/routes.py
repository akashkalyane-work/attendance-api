from typing import List

from fastapi import APIRouter, Query

from app.attendance.schemas import AttendanceResponseSchema, AttendanceSummaryResponse
from app.attendance.dependencies import AttendanceServiceDep

attendance_router = APIRouter(prefix="/attendances", tags=["attendances"])


@attendance_router.get("/today", response_model=AttendanceResponseSchema | None)
async def get_today_attendance(
    service: AttendanceServiceDep,
    user_id: int = 1
):
    return await service.today_attendace(user_id)

@attendance_router.post(
    "/clock-in",
    response_model=AttendanceResponseSchema,
    status_code=201
)
async def clock_in(
    service: AttendanceServiceDep,
    # user: User = Depends(get_current_user),
    user_id: int
):
    return await service.clock_in(user_id)


@attendance_router.post(
    "/clock-out",
    response_model=AttendanceResponseSchema
)
async def clock_out(
    service: AttendanceServiceDep,
    # user: User = Depends(get_current_user),
    user_id: int
):
    return await service.clock_out(user_id)


@attendance_router.get(
    "/me",
    response_model=list[AttendanceResponseSchema]
)
async def my_attendance(
    service: AttendanceServiceDep,
    # user: User = Depends(get_current_user),
    user_id: int = 1
):
    return await service.my_attendance(user_id)

@attendance_router.get("/my")
async def my_attendance_by_month(
    service: AttendanceServiceDep,
    cursor: str | None = Query(
        default=None,
        description="Month cursor in YYYY-MM format"
    ),
    user_id: int = 1
):
    return await service.my_attendance_my_month(
        user_id,
        cursor=cursor,
    )

@attendance_router.get(
    "/summary",
    response_model=AttendanceSummaryResponse
)
async def get_attendance_summary(
    service: AttendanceServiceDep,
    month: str = Query(..., example="2025-12"),
    user_id: int = 1
    # user: UserResponseSchema = Depends(get_current_user),
):
    return await service.get_monthly_summary(user_id, month)

@attendance_router.get("/months", response_model=List[str])
async def get_attendance_summary_months(
    service: AttendanceServiceDep,
    user_id: int = 1
):
    return await service.get_available_months(user_id)
