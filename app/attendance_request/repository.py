from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.attendance_request.models import AttendanceRequest


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

    async def get_by_id(self, request_id: int):
        stmt = select(AttendanceRequest).where(
            AttendanceRequest.id == request_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()