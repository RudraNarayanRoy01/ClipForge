from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from src.config.system_settings import SystemSettings

import os
from pathlib import Path

# Local SQLite Database for the AI Clipping Platform
_db_path_str = SystemSettings().db_path
_db_path = Path(_db_path_str)

if not _db_path.is_absolute():
    _backend_dir = Path(__file__).resolve().parent.parent.parent
    _db_path = _backend_dir / _db_path

DB_PATH = str(_db_path)
# Note the use of aiosqlite for async database drivers
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Connect args needed for SQLite
engine = create_async_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False, 
    autoflush=False
)

Base = declarative_base()

async def get_db():
    """Dependency injection for FastAPI to provide async DB sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
