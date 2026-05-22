from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str
    DEBUG:  bool
    VERSION: str
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    PLATFORM_COMMISSION_PERCENT: float
    LOW_STOCK_THRESHOLD: int

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
