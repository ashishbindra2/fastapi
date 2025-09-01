from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from src.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args=settings.DATABASE_CONNECT_DICT  # Only needed for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()



# ✅ Context manager for DB sessions
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
