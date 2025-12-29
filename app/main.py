from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_orm, close_orm
from app.attendance.routes import attendance_router
from app.attendance_request.routes import request_router
from app.attendance.schemas import AttendanceTodayStateResponse
from app.attendance_request.dependencies import AttendanceRequestServiceDep


async def lifespan(app: FastAPI) -> AsyncGenerator:
    await init_orm()
    print("db initialized")
    print("Startup")

    yield
    await close_orm()
    print("Shutdown")


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/attendances/today/state",
    response_model=AttendanceTodayStateResponse
)
async def get_today_attendance_state(
    service: AttendanceRequestServiceDep,
    user_id: int = 1
    # current_user: CurrentUser,
):
    return await service.get_today_state(user_id)

app.include_router(attendance_router)
app.include_router(request_router)
