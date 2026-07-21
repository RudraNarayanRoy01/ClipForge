import asyncio
import logging
import traceback
from src.domain.job import Job, JobStatus
from src.domain.ports import IWorkflowDispatcher, IJobRepository

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
