"""
Database connection setup.

Reads MySQL credentials from environment variables (loaded from a .env file
via python-dotenv) and builds the SQLAlchemy engine + session factory used
throughout the app.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load variables from .env into the environment
load_dotenv()

DB_USER = (os.getenv("DB_USER") or "").strip()
DB_PASSWORD = (os.getenv("DB_PASSWORD") or "").strip()
DB_HOST = (os.getenv("DB_HOST") or "").strip()
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "student_records_db")
USE_SQLITE = (os.getenv("USE_SQLITE") or "").strip().lower() in {"1", "true", "yes", "on"}

# Prefer SQLite when no MySQL host is configured or when SQLite is explicitly
# requested. This keeps the project runnable in local dev environments where
# MySQL is unavailable or misconfigured.
if USE_SQLITE or not DB_HOST:
    DATABASE_URL = "sqlite:///./student_records.db"
else:
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# pool_pre_ping avoids "MySQL server has gone away" errors on idle connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session per-request
    and always closes it afterwards, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
