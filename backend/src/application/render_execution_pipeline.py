from src.domain.render_plan import RenderPlan
from src.domain.models.render_result import RenderResult
from src.application.render_executor import RenderExecutor


class RenderExecutionPipeline:
    """
    Orchestrates the render execution process.
    
    Acts as the application entry point for rendering, delegating the actual
    execution to the RenderExecutor. Ensures that execution is decoupled
    from planning and infrastructure details.
    """
    
    def __init__(self, executor: RenderExecutor):
        self.executor = executor
        
    def execute(self, plan: RenderPlan) -> RenderResult:
        """
        Executes the render plan.
        
        Args:
            plan (RenderPlan): The canonical execution blueprint.
            
        Returns:
            RenderResult: The canonical domain-level outcome of execution.
        """
        return self.executor.execute(plan)
