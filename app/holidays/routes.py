from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import require_admin
from app.holidays.schemas import (
    PaidHolidayCreate,
    PaidHolidayUpdate,
    PaidHolidayResponse,
)
from app.holidays.dependencies import PaidHolidayServiceDep 


router = APIRouter(
    prefix="/admin/holidays",
    tags=["Admin - Holidays"],
    dependencies=[Depends(require_admin)]
)


@router.get("", response_model=list[PaidHolidayResponse])
async def list_holidays(
    service: PaidHolidayServiceDep,
    year: int = Query(..., description="Year e.g. 2026"),
):
    return await service.list_holidays(year)


@router.post(
    "",
    response_model=PaidHolidayResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_holiday(
    data: PaidHolidayCreate,
    service: PaidHolidayServiceDep
):
    return await service.create_holiday(data)


@router.put("/{holiday_id}", response_model=PaidHolidayResponse)
async def update_holiday(
    holiday_id: int,
    data: PaidHolidayUpdate,
    service: PaidHolidayServiceDep
):
    return await service.update_holiday(holiday_id, data)


@router.patch("/{holiday_id}/toggle", response_model=PaidHolidayResponse)
async def toggle_holiday(
    holiday_id: int,
    service: PaidHolidayServiceDep
):
    return await service.toggle_holiday(holiday_id)


@router.delete("/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    holiday_id: int,
    service: PaidHolidayServiceDep
):
    await service.delete_holiday(holiday_id)