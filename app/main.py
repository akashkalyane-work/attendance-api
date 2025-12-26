from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_orm, close_orm
from app.attendance.routes import attendance_router


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


app.include_router(attendance_router)
