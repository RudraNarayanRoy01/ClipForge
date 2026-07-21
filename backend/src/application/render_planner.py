from src.domain.models.render_draft import RenderDraft
from src.domain.models.render_profile import RenderProfile
from src.editing.domain.models.state import TimelineState


class RenderPlanner:
    """
    Assembles the information required for rendering into an intermediate rendering specification.
    
    Its responsibility is orchestration only. It does not perform validation, rendering, 
    or exporting, and it remains decoupled from filesystem concepts.
    """

    def plan(self, timeline_state: TimelineState, render_profile: RenderProfile) -> RenderDraft:
        """
        Assembles rendering inputs into a RenderDraft.
        
        Args:
            timeline_state: The complete state of the timeline to be rendered.
            render_profile: The rendering profile containing platform rendering defaults.
            
        Returns:
            RenderDraft: An intermediate rendering specification.
        """
        return RenderDraft(
            timeline_state=timeline_state,
            render_profile=render_profile,
        )
