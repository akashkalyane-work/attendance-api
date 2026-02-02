from datetime import date, datetime

from pydantic import BaseModel, Field


class PaidHolidayBase(BaseModel):
    date: date
    name: str = Field(..., max_length=100)
    is_active: bool = True


class PaidHolidayCreate(PaidHolidayBase):
    pass


class PaidHolidayUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    is_active: bool | None = None


class PaidHolidayResponse(PaidHolidayBase):
    id: int
    year: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True