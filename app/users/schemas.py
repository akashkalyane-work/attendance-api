from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    hourly_rate: float

    class Config:
        from_attributes = True