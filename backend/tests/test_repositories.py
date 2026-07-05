import pytest
import uuid
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from src.infrastructure.database import Base
from src.repositories.project_repository import ProjectRepository
from src.domain.entities import Project, ClipSegment, TimeRange

# Use an in-memory SQLite database for testing with aiosqlite
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest_asyncio.fixture()
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_save_and_get_project(db_session: AsyncSession):
    repo = ProjectRepository(db_session)
    
    # Create Domain Entity
    new_project = Project(name="Test Podcast")
    
    # Save to DB
    await repo.save_project(new_project)
    
    # Retrieve from DB
    retrieved = await repo.get_project(new_project.id)
    
    assert retrieved.id == new_project.id
    assert retrieved.name == "Test Podcast"
    assert retrieved.status == "created"

@pytest.mark.asyncio
async def test_save_and_get_clips(db_session: AsyncSession):
    repo = ProjectRepository(db_session)
    
    project_id = uuid.uuid4()
    video_id = uuid.uuid4()
    
    clip1 = ClipSegment(
        project_id=project_id,
        video_asset_id=video_id,
        boundaries=TimeRange(10.5, 20.0),
        title="Viral Moment",
        virality_score=99
    )
    
    try:
        # Since we use async sqlite, turning off foreign_keys requires executing on connection.
        # It's usually off by default in sqlite. Let's just execute the queries directly.
        await db_session.execute(text("PRAGMA foreign_keys=OFF"))
        await repo.save_clips([clip1])
        
        clips = await repo.get_clips_for_video(video_id)
        assert len(clips) == 1
        assert clips[0].title == "Viral Moment"
        assert clips[0].boundaries.start_time == 10.5
        assert clips[0].virality_score == 99
    finally:
        await db_session.execute(text("PRAGMA foreign_keys=ON"))
