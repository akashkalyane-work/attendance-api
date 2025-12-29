from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.attendance_request.models import AttendanceRequest
from app.core.enums import AttendanceRequestType, AttendanceRequestStatus

IST = ZoneInfo("Asia/Kolkata")


class AttendanceRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, request: AttendanceRequest):
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_my_requests(self, user_id: int):
        stmt = (
            select(AttendanceRequest)
            .where(AttendanceRequest.user_id == user_id)
            .order_by(AttendanceRequest.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_pending_requests(self):
        stmt = (
            select(AttendanceRequest)
            .where(AttendanceRequest.status == "PENDING")
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_pending_request_by_user_id(
        self,
        user_id: int,
        today: date,
        request_type: AttendanceRequestType
    ) -> AttendanceRequest | None:
        now = datetime.now(IST)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        stmt = (
            select(AttendanceRequest)
            .where(
                AttendanceRequest.user_id == user_id,
                AttendanceRequest.request_type == request_type,
                AttendanceRequest.status == AttendanceRequestStatus.PENDING,
                AttendanceRequest.created_at >= start_of_day,
                AttendanceRequest.created_at < end_of_day
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, request_id: int) -> AttendanceRequest:
        stmt = select(AttendanceRequest).where(
            AttendanceRequest.id == request_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update(self, request: AttendanceRequest) -> AttendanceRequest:
        await self.session.commit()
        await self.session.refresh(request)

        return request