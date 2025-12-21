from fastapi import APIRouter, Query

from app.attendance.schemas import AttendanceResponseSchema
from app.attendance.dependencies import AttendanceServiceDep


attendance_router = APIRouter(prefix="/attendances", tags=["attendances"])


@attendance_router.get("/", status_code=200, response_model=str)
async def get_attendance() -> str:
    return "Working"

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
    user_id: int
):
    return await service.my_attendance(user_id)

@attendance_router.get("/my")
async def my_attendance_by_month(
    service: AttendanceServiceDep,
    user_id: int,
    cursor: str | None = Query(
        default=None,
        description="Month cursor in YYYY-MM format"
    ),
):
    return await service.my_attendance_my_month(
        user_id=user_id,
        cursor=cursor,
    )
