import asyncio
import logging
import traceback
from src.domain.job import Job, JobStatus
from src.domain.ports import IWorkflowDispatcher, IJobRepository
from src.infrastructure.database import AsyncSessionLocal
from src.repositories.job_repository import JobRepository

logger = logging.getLogger(__name__)

class AsyncWorkflowDispatcher(IWorkflowDispatcher):
    """
    Asyncio-based Workflow Dispatcher for local execution.
    Complies with IWorkflowDispatcher, meaning it can be replaced by a Celery/Temporal adapter without changing application logic.
    """
    def __init__(self, job_repository: IJobRepository):
        self.job_repository = job_repository

    async def dispatch(self, job: Job, task_callable, *args, **kwargs) -> None:
        """
        Transitions job through QUEUED, RUNNING, and COMPLETED/FAILED, delegating to the callable.
        """
        try:
            job.queue()
            await self.job_repository.save(job)
        except Exception as e:
            logger.error(f"Failed to queue job {job.id}: {e}")
            job.fail(str(e))
            await self.job_repository.save(job)
            return

        # Fire and forget
        asyncio.create_task(self._execute_workflow(job, task_callable, *args, **kwargs))

    async def _execute_workflow(self, job: Job, task_callable, *args, **kwargs) -> None:
        try:
            # 1. Start
            job.start()
            await self.job_repository.save(job)

            # 2. Execute
            result = await task_callable(*args, **kwargs)

            # 3. Complete
            job.complete(result)
            await self.job_repository.save(job)

        except Exception as e:
            logger.error(f"Workflow execution failed for job {job.id}: {traceback.format_exc()}")
            job.fail(str(e))
            await self.job_repository.save(job)

class ApiSafeAsyncWorkflowDispatcher(IWorkflowDispatcher):
    """
    Production-safe local dispatcher for API integration.
    Creates a new, independent database session for each background task.
    Designed to be registered as a Singleton, preventing request-scoped session leaks.
    """
    def __init__(self, session_maker=None):
        self.session_maker = session_maker or AsyncSessionLocal

    async def dispatch(self, job: Job, task_callable, *args, **kwargs) -> None:
        # Fire and forget with job.id to avoid passing request-scoped SQLAlchemy state
        asyncio.create_task(self._execute_workflow(job.id, task_callable, *args, **kwargs))

    async def _execute_workflow(self, job_id, task_callable, *args, **kwargs) -> None:
        # Create a fresh database session purely for this background task
        async with self.session_maker() as session:
            bg_job_repo = JobRepository(session)
            
            job = await bg_job_repo.get(job_id)
            if not job:
                logger.error(f"Workflow execution failed: Job {job_id} not found")
                return
                
            try:
                # 1. Queue
                job.queue()
                await bg_job_repo.save(job)

                # 2. Start
                job.start()
                await bg_job_repo.save(job)

                # 3. Execute
                result = await task_callable(*args, **kwargs)

                # 4. Complete
                job.complete(result)
                await bg_job_repo.save(job)

            except Exception as e:
                logger.error(f"Workflow execution failed for job {job_id}: {traceback.format_exc()}")
                job.fail(str(e))
                await bg_job_repo.save(job)

