import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Get database URL from environment or use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL")
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

# If no DATABASE_URL is provided, use SQLite in-memory
if not DATABASE_URL or USE_SQLITE:
    logger.warning("Using SQLite in-memory database for development/testing")
    DATABASE_URL = "sqlite:///./library.db"
    # For in-memory SQLite: "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    logger.info(f"Connecting to PostgreSQL database")
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()