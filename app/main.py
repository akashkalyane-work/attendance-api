from typing import AsyncGenerator
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_orm, close_orm
from app.attendance.routes import router as attendance_router
from app.attendance_request.routes import router as request_router
from app.holidays.routes import router as holiday_router
from app.admin.routes import router as admin_router
from app.users.routes import router as user_router
from app.auth.routes import router as auth_router


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
    expose_headers=["content-disposition"],
)

app.include_router(attendance_router)
app.include_router(request_router)
app.include_router(holiday_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)