from src.domain.models.render_draft import RenderDraft
from src.domain.models.render_profile import RenderProfile
from src.editing.domain.pipeline.export import FinalizedEdit


class RenderPlanner:
    """
    Assembles the information required for rendering into an intermediate rendering specification.
    
    Its responsibility is orchestration only. It does not perform validation, rendering, 
    or exporting, and it remains decoupled from filesystem concepts.
    """

    def plan(self, finalized_edit: FinalizedEdit, render_profile: RenderProfile) -> RenderDraft:
        """
        Assembles rendering inputs into a RenderDraft.
        
        Args:
            finalized_edit: The complete immutable representation of the Editing Domain outcome.
            render_profile: The rendering profile containing platform rendering defaults.
            
        Returns:
            RenderDraft: An intermediate rendering specification.
        """
        return RenderDraft(
            finalized_edit=finalized_edit,
            render_profile=render_profile,
        )
