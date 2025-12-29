from fastapi import APIRouter, Depends

from app.attendance_request.schemas import (
    AttendanceRequestCreateSchema,
    AttendanceRequestResponseSchema
)
from app.attendance_request.dependencies import AttendanceRequestServiceDep
# from app.auth.dependencies import get_current_user
from app.users.models import User

request_router = APIRouter(
    prefix="/requests",
    tags=["Attendance Requests"]
)


@request_router.post(
    "",
    response_model=AttendanceRequestResponseSchema,
    status_code=201
)
async def create_request(
    data: AttendanceRequestCreateSchema,
    service: AttendanceRequestServiceDep,
    user_id: int
):
    return await service.create_request(user_id, data)


@request_router.get(
    "/me",
    response_model=list[AttendanceRequestResponseSchema]
)
async def my_requests(
    service: AttendanceRequestServiceDep,
    # user: User = Depends(get_current_user),
    user_id: int
):
    return await service.get_request_by_user_id(user_id)

@request_router.post(
    "/approve",
    response_model=AttendanceRequestResponseSchema
)
async def approve_request(
    service: AttendanceRequestServiceDep,
    request_id: int,
    admin_id: int
):
    return await service.approve_request(request_id, admin_id)

@request_router.post(
    "/reject",
    response_model=AttendanceRequestResponseSchema
)
async def reject_request(
    service: AttendanceRequestServiceDep,
    request_id: int,
    admin_id: int
):
    return await service.reject_request(request_id, admin_id)
