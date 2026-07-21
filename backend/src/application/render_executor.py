from src.domain.models.render_plan import RenderPlan
from src.domain.models.render_result import RenderResult
from src.domain.ports import IRenderBackend


class RenderExecutor:
    """
    Coordinates the execution of a RenderPlan at the application layer.
    
    It serves as the execution contract and will delegate to underlying 
    rendering providers. It performs no planning, validation, or composition,
    and remains completely backend-independent.
    """

    def __init__(self, backend: IRenderBackend):
        self._backend = backend

    def execute(self, plan: RenderPlan) -> RenderResult:
        """
        Executes a rendering plan and returns the canonical result.
        
        Args:
            plan (RenderPlan): The canonical execution blueprint.
            
        Returns:
            RenderResult: The canonical domain-level outcome of execution.
        """
        return self._backend.execute(plan)
