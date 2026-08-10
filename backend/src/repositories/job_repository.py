import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.infrastructure.models import JobModel
from src.domain.ports import IJobRepository
from src.domain.job import Job

class JobRepository(IJobRepository):
    """
    Production-grade SQLAlchemy repository for Jobs.
    Maps Domain Job to JobModel and strictly persists workflow state.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: JobModel) -> Job:
        job = Job(
            id=uuid.UUID(model.id),
            name=model.name,
            status=model.status,
            previous_status=model.previous_status,
            created_at=model.created_at,
            status_updated_at=model.status_updated_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
            cancellation_requested=model.cancellation_requested,
            retry_count=model.retry_count,
            max_retries=model.max_retries,
            error=model.error,
            result=model.result_json
        )
        return job

    def _to_model(self, entity: Job) -> JobModel:
        return JobModel(
            id=str(entity.id),
            name=entity.name,
            status=entity.status,
            previous_status=entity.previous_status,
            created_at=entity.created_at,
            status_updated_at=entity.status_updated_at,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            cancellation_requested=entity.cancellation_requested,
            retry_count=entity.retry_count,
            max_retries=entity.max_retries,
            error=entity.error,
            result_json=entity.result
        )

    async def save(self, job: Job) -> None:
        """
        Idempotent save operation using SQLAlchemy merge.
        Handles both insertions (new jobs) and updates (status transitions).
        """
        model = self._to_model(job)
        await self.session.merge(model)
        await self.session.commit()

    async def get(self, job_id: uuid.UUID) -> Optional[Job]:
        """
        Retrieves a job by its unique identifier.
        """
        result = await self.session.execute(
            select(JobModel).where(JobModel.id == str(job_id))
        )
        model = result.scalars().first()
        return self._to_domain(model) if model else None
