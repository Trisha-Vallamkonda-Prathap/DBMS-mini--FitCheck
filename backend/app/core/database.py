from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

connect_args = {}
if "mysql" in settings.DATABASE_URL:
    connect_args["connect_timeout"] = 2

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """Dependency for obtaining a transactional SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
