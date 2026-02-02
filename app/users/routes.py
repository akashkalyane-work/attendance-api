from fastapi import APIRouter, Depends

from app.users.schemas import UserCreate, UserUpdate, UserResponse, UserAdminResponse
from app.users.dependencies import UserServiceDep

router = APIRouter(prefix="/admin/users", tags=["Users"])

@router.post("", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    service: UserServiceDep
):
    return await service.create_user(data)

@router.get("", response_model=list[UserAdminResponse])
async def list_users(service: UserServiceDep):
    return await service.get_users()

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    service: UserServiceDep
):
    return await service.update_user(user_id, data)

@router.delete("/{user_id}")
async def delete_user(user_id: int, service: UserServiceDep):
    await service.delete_user(user_id)
    return {"message": "User deleted"}