import uuid
from typing import Dict
from src.domain.job import Job
from src.domain.ports import IJobRepository

class InMemoryJobRepository(IJobRepository):
    """
    In-memory implementation of IJobRepository for testing and mock environments.
    """
    def __init__(self):
        self._store: Dict[uuid.UUID, Job] = {}

    async def save(self, job: Job) -> None:
        self._store[job.id] = job

    async def get(self, job_id: uuid.UUID) -> Job | None:
        return self._store.get(job_id)

# Global singleton for in-memory persistence during development/mock phase
global_job_repository = InMemoryJobRepository()
