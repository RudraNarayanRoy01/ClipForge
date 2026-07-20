from src.editing.domain.models.pipeline import EditingPipelineResult
from src.editing.domain.models.project import EditingProject
from src.editing.domain.services.editing_pipeline_service import IEditingPipelineService
from src.editing.domain.services.editing_strategy_service import IEditingStrategyService
from src.editing.domain.services.editing_validation_service import IEditingValidationService
from src.editing.domain.services.transformation import ITimelineTransformationService


class DefaultEditingPipelineService(IEditingPipelineService):
    """
    Default implementation of the Editing Pipeline Service.
    
    Coordinates the execution of the editing workflow by sequentially delegating 
    to the Strategy, Transformation, and Validation services. This service does 
    not contain editing business logic itself, but acts as the workflow orchestrator.
    """

    def __init__(
        self,
        strategy_service: IEditingStrategyService,
        transformation_service: ITimelineTransformationService,
        validation_service: IEditingValidationService,
    ):
        self._strategy_service = strategy_service
        self._transformation_service = transformation_service
        self._validation_service = validation_service

    async def run_pipeline(self, project: EditingProject) -> EditingPipelineResult:
        """
        Executes the editing pipeline workflow for a given project.
        """
        # 1. Generate editing plan via strategy
        plan = await self._strategy_service.generate_plan(project)

        # 2. Transform the plan into backend-independent timeline operations
        transformation_result = await self._transformation_service.transform(plan)

        # 3. Validate the generated plan and operations against the project constraints
        validation_result = await self._validation_service.validate(
            project, plan, transformation_result
        )

        # 4. Return the canonical pipeline result
        return EditingPipelineResult(
            plan=plan,
            transformation_result=transformation_result,
            validation_result=validation_result,
        )
