from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "Shopify Lead Generator"
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/leadgen"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Scraping settings
    scrape_delay_min: float = 1.0
    scrape_delay_max: float = 3.0
    max_concurrent_scrapes: int = 5

    # API settings
    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
