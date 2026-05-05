from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    redis_url: str = 'redis://redis:6379/0'
    postgres_url: str = 'postgresql+asyncpg://postgres:postgres@postgres:5432/jobs'
    sync_postgres_url: str = 'postgresql://postgres:postgres@postgres:5432/jobs'
    queue_name: str = 'jobs'
    rate_limit: str = '60/minute'
    worker_timeout_seconds: int = 20


settings = Settings()
