from src.application.render_planner import RenderPlanner
from src.application.render_validator import RenderValidator
from src.application.render_composition_service import RenderCompositionService
from src.domain.render_plan import RenderPlan
from src.domain.models.render_profile import RenderProfile
from src.editing.domain.pipeline.export import FinalizedEdit


class RenderPlanningPipeline:
    """
    Orchestrates the render planning process.
    
    Coordinates planning, validation, and composition to produce
    a final immutable RenderPlan ready for execution.
    """
    
    def __init__(
        self,
        planner: RenderPlanner,
        validator: RenderValidator,
        composer: RenderCompositionService
    ):
        self.planner = planner
        self.validator = validator
        self.composer = composer
        
    def execute(self, finalized_edit: FinalizedEdit, render_profile: RenderProfile) -> RenderPlan:
        """
        Executes the render planning workflow.
        
        Args:
            finalized_edit: The canonical outcome of the Editing Domain.
            render_profile: The rendering profile containing platform defaults.
            
        Returns:
            RenderPlan: The canonical execution blueprint.
            
        Raises:
            ValueError: If the render draft fails validation.
        """
        # 1. Plan
        draft = self.planner.plan(finalized_edit, render_profile)
        
        # 2. Validate
        validation_result = self.validator.validate(draft)
        
        # 3. Decide whether composition may continue
        if not validation_result.is_valid:
            raise ValueError(
                f"Render planning failed validation. Errors: {validation_result.errors}"
            )
            
        # 4. Compose
        return self.composer.compose(draft)
