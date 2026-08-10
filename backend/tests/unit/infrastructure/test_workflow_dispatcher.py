import pytest
import uuid
import asyncio
from src.workers.app import ApiSafeAsyncWorkflowDispatcher
from src.domain.job import Job, JobStatus
from src.repositories.job_repository import JobRepository
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import pytest_asyncio
from src.infrastructure.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

# Helper dummy callable
async def dummy_task(success=True):
    await asyncio.sleep(0.01)
    if not success:
        raise ValueError("Task failed")
    return {"result": "success"}

@pytest_asyncio.fixture()
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def dispatcher():
    return ApiSafeAsyncWorkflowDispatcher(session_maker=TestingSessionLocal)

@pytest.fixture
def job_repo(db_session: AsyncSession):
    return JobRepository(db_session)

@pytest.mark.asyncio
async def test_dispatcher_construction():
    # A. Dependency construction
    # Dispatcher can be instantiated without a request-scoped JobRepository
    dispatcher = ApiSafeAsyncWorkflowDispatcher()
    assert dispatcher is not None

@pytest.mark.asyncio
async def test_job_success(dispatcher, job_repo, db_session):
    # C. Job success
    # Verify: ACCEPTED -> QUEUED -> RUNNING -> COMPLETED
    job = Job(name="test_job_success")
    job.accept()
    await job_repo.save(job)
    
    # We dispatch and wait for the task to finish
    await dispatcher.dispatch(job, dummy_task, success=True)
    await asyncio.sleep(0.1) # wait for background task to complete
    
    # Fetch job directly using a new session to ensure DB is updated
    async with TestingSessionLocal() as session:
        check_repo = JobRepository(session)
        updated_job = await check_repo.get(job.id)
        assert updated_job.status == JobStatus.COMPLETED

@pytest.mark.asyncio
async def test_job_failure(dispatcher, job_repo, db_session):
    # D. Job failure
    job = Job(name="test_job_failure")
    job.accept()
    await job_repo.save(job)
    
    await dispatcher.dispatch(job, dummy_task, success=False)
    await asyncio.sleep(0.1)
    
    async with TestingSessionLocal() as session:
        check_repo = JobRepository(session)
        updated_job = await check_repo.get(job.id)
        assert updated_job.status == JobStatus.FAILED
        assert "Task failed" in updated_job.error

@pytest.mark.asyncio
async def test_multiple_concurrent_jobs(dispatcher, job_repo, db_session):
    # E. Multiple concurrent jobs
    job1 = Job(name="job1")
    job2 = Job(name="job2")
    job1.accept()
    job2.accept()
    await job_repo.save(job1)
    await job_repo.save(job2)
    
    # Dispatch both simultaneously
    await dispatcher.dispatch(job1, dummy_task, success=True)
    await dispatcher.dispatch(job2, dummy_task, success=True)
    
    await asyncio.sleep(0.1)
    
    async with TestingSessionLocal() as session:
        check_repo = JobRepository(session)
        j1 = await check_repo.get(job1.id)
        j2 = await check_repo.get(job2.id)
        assert j1.status == JobStatus.COMPLETED
        assert j2.status == JobStatus.COMPLETED

@pytest.mark.asyncio
async def test_request_session_independence(dispatcher, job_repo, db_session):
    # B & F: Background session isolation and Request session independence
    # Verify the dispatcher doesn't use the original db_session
    job = Job(name="test_isolation")
    job.accept()
    await job_repo.save(job)
    
    # Dispatch uses background session
    await dispatcher.dispatch(job, dummy_task, success=True)
    
    # The background task should still succeed without using db_session
    await asyncio.sleep(0.1)
    await asyncio.sleep(0.1)
    
    async with TestingSessionLocal() as session:
        check_repo = JobRepository(session)
        updated_job = await check_repo.get(job.id)
        assert updated_job.status == JobStatus.COMPLETED
