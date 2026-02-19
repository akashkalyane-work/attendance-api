from fastapi import APIRouter, Depends

from app.users.dependencies import UserServiceDep
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate, UserResponse, UserAdminResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    service: UserServiceDep
):
    return await service.create_user(data)

@router.get("", response_model=list[UserAdminResponse])
async def list_users(service: UserServiceDep):
    return await service.get_users()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    user: User = Depends(get_current_user),
):
    return user

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