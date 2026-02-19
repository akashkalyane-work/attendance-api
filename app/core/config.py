from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str 
    ASYNC_DATABASE_URL: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    ENV: str

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    model_config = {
        "env_file": ".env",
    }

settings = Settings()