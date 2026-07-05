import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Local SQLite Database for the AI Clipping Platform
DB_PATH = os.environ.get("DB_PATH", "clipping_platform.db")
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
