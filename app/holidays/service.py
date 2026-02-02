from fastapi import HTTPException, status

from app.holidays.models import PaidHoliday
from app.holidays.repository import PaidHolidayRepository
from app.holidays.schemas import (
    PaidHolidayCreate,
    PaidHolidayUpdate,
)


class PaidHolidayService:
    def __init__(self, repo: PaidHolidayRepository):
        self.repo = repo

    async def list_holidays(self, year: int):
        return await self.repo.get_by_year(year)

    async def create_holiday(self, data: PaidHolidayCreate):
        existing = await self.repo.get_by_date(data.date)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Holiday already exists for this date"
            )

        holiday = PaidHoliday(
            date=data.date,
            name=data.name,
            year=data.date.year,
            is_active=data.is_active,
        )

        return await self.repo.create(holiday)

    async def update_holiday(self, holiday_id: int, data: PaidHolidayUpdate):
        holiday = await self.repo.get_by_id(holiday_id)
        if not holiday:
            raise HTTPException(404, "Holiday not found")

        if data.name is not None:
            holiday.name = data.name

        if data.is_active is not None:
            holiday.is_active = data.is_active

        return await self.repo.update(holiday)

    async def delete_holiday(self, holiday_id: int):
        holiday = await self.repo.get_by_id(holiday_id)
        if not holiday:
            raise HTTPException(404, "Holiday not found")

        await self.repo.delete(holiday_id)

    async def toggle_holiday(self, holiday_id: int):
        holiday = await self.repo.get_by_id(holiday_id)
        if not holiday:
            raise HTTPException(404, "Holiday not found")

        holiday.is_active = not holiday.is_active
        return await self.repo.update(holiday)