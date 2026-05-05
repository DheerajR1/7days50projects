from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    redis_url: str = 'redis://redis:6379/0'
    postgres_url: str = 'postgresql://postgres:postgres@postgres:5432/jobs'
    queue_name: str = 'jobs'
    worker_id: str = 'worker-1'
    worker_ip: str = '127.0.0.1'
    max_capacity: int = 2


settings = Settings()
