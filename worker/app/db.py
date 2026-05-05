from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.postgres_url, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
