from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str 
    ASYNC_DATABASE_URL: str
    
    model_config = {
        "env_file": ".env",
    }

settings = Settings()