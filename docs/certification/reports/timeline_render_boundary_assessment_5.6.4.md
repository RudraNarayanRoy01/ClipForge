# Timeline–Render Boundary Assessment
**Batch**: 5.6.4.2

## Assessment Goal
Verify the architectural boundary between the editing domain and the rendering infrastructure (EditingPlan ↓ Timeline ↓ RenderPlan), ensuring absolute deterministic handoff and ownership transfer.

## Findings
The rendering abstraction defined in `src/domain/render_plan.py` (`RenderPlan`, `RenderLayer`, `RenderSegment`) perfectly models a declarative rendering intent devoid of encoder specifics (like FFmpeg).
The editing pipeline appropriately uses services (`ITimelineTransformationService`, `IExportPlanningService`) to generate final sequences.

## Architectural Ownership Correction
**Issue**: A severe naming collision existed where `src/editing/domain/pipeline/export.py` defined its own `RenderPlan`. The Orchestrator returned this object as its final output, falsely suggesting a successful mapping to the global rendering boundary.
**Evidence for Correction**: An analysis of the object's properties confirmed it encapsulates:
- `EditingSequence`: The canonical artifact for editorial intent (clip ordering and metadata).
- `SubtitleTrack`: The completed subtitle layer containing text timing, devoid of font engine logic.
- `ExportProfile`: High-level export preferences (orientation, resolution, fps), devoid of execution configuration.

Because the object contains exclusively editorial concepts and no renderer-facing concepts (such as `RenderLayer`, `RenderSegment`, or `RenderInstruction`), it fundamentally represents **Editing Domain Intent**, not Render Planning intent. The Editing Domain must not own the `RenderPlan` concept.

**Correction**: Renamed the pipeline's internal export object from `RenderPlan` to `FinalizedEdit`.
- **Justification**: This is an explicit **Architectural Ownership Correction**. It prevents the Editing Domain from claiming ownership of rendering logic and properly limits its boundary to producing editorial intent. The true `RenderPlan` (`src/domain/render_plan.py`) is appropriately reserved for the downstream rendering phase.
- **Runtime impact**: Zero runtime behavior changes. The modification strictly alters type declarations, import paths, and attribute names, flawlessly restoring the semantic boundary without altering execution flow.

## Conclusion
The boundary is now structurally sound and correctly named, eliminating ambiguity regarding layer ownership.
