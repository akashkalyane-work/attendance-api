from typing import Optional

from pydantic import BaseModel

from app.core.enums import UserRole

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    perday_rate: Optional[float] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    perday_rate: Optional[float] = None
    is_active: Optional[bool] = None
    role: UserRole

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    perday_rate: float

    class Config:
        from_attributes = True

class UserAdminResponse(BaseModel):
    id: int
    name: str
    email: str
    perday_rate: float
    is_active: bool
    role: UserRole

    class Config:
        from_attributes = True