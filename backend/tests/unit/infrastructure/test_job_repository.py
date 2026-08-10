import pytest
import uuid
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
import pytest_asyncio

from src.infrastructure.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest_asyncio.fixture()
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

from src.repositories.job_repository import JobRepository
from src.domain.job import Job, JobStatus
from src.infrastructure.models import JobModel

@pytest.mark.asyncio
async def test_job_repository_save_and_get(db_session: AsyncSession):
    # Given
    repo = JobRepository(db_session)
    job_id = uuid.uuid4()
    job = Job(
        id=job_id,
        name="Test Analysis",
        status=JobStatus.REQUESTED
    )
    
    # When: Saving the job
    await repo.save(job)
    
    # Then: It can be retrieved
    retrieved_job = await repo.get(job_id)
    assert retrieved_job is not None
    assert retrieved_job.id == job_id
    assert retrieved_job.name == "Test Analysis"
    assert retrieved_job.status == JobStatus.REQUESTED
    assert retrieved_job.retry_count == 0

@pytest.mark.asyncio
async def test_job_repository_update_status(db_session: AsyncSession):
    # Given
    repo = JobRepository(db_session)
    job_id = uuid.uuid4()
    job = Job(id=job_id, name="Status Update Test", status=JobStatus.REQUESTED)
    await repo.save(job)
    
    # When: State changes and is saved again
    retrieved_job = await repo.get(job_id)
    retrieved_job.status = JobStatus.RUNNING
    retrieved_job.started_at = datetime.datetime.now(datetime.timezone.utc)
    await repo.save(retrieved_job)
    
    # Then: The updates are persisted
    updated_job = await repo.get(job_id)
    assert updated_job is not None
    assert updated_job.status == JobStatus.RUNNING
    assert updated_job.started_at is not None
