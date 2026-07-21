from src.domain.models.render_draft import RenderDraft
from src.domain.models.render_plan import RenderPlan


class RenderComposer:
    """
    Transforms a validated RenderDraft into an immutable RenderPlan.
    
    This component performs composition only. It does not validate, render, export,
    or mutate any domain objects.
    """
    
    def compose(self, draft: RenderDraft) -> RenderPlan:
        """
        Assembles a RenderPlan from a validated RenderDraft.
        
        Args:
            draft: The intermediate rendering specification.
            
        Returns:
            RenderPlan: The canonical execution blueprint.
        """
        return RenderPlan(
            timeline_state=draft.timeline_state,
            render_profile=draft.render_profile
        )
