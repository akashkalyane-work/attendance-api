from datetime import date

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PaidHoliday


class PaidHolidayRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_year(self, year: int) -> list[PaidHoliday]:
        stmt = select(PaidHoliday).where(PaidHoliday.year == year).order_by(PaidHoliday.date.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_date(self, holiday_date: date) -> PaidHoliday | None:
        stmt = select(PaidHoliday).where(PaidHoliday.date == holiday_date)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, holiday_id: int) -> PaidHoliday | None:
        return await self.session.get(PaidHoliday, holiday_id)

    async def create(self, holiday: PaidHoliday) -> PaidHoliday:
        self.session.add(holiday)
        await self.session.commit()
        await self.session.refresh(holiday)
        return holiday

    async def update(self, holiday: PaidHoliday) -> PaidHoliday:
        await self.session.commit()
        await self.session.refresh(holiday)
        return holiday

    async def delete(self, holiday_id: int) -> None:
        stmt = delete(PaidHoliday).where(PaidHoliday.id == holiday_id)
        await self.session.execute(stmt)
        await self.session.commit()