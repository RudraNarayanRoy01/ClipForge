# Planning Pipeline Documentation

The Planning Pipeline is the orchestration layer responsible for transforming an imported `Campaign` into a set of highly specific instructions (Planning Artifacts) that the downstream Video Engine can use to generate clips.

## Overview

The `PlanningPipelineService` orchestrates the pipeline. It strictly coordinates the `when` and `how` of the planning stages, delegating the actual reasoning to the AI Intelligence Ports, and persistence to the Repository Ports.

### Key Principles
1. **No Domain Logic in Orchestration**: The pipeline does not make planning decisions. It only transitions states.
2. **Deterministic State Machine**: The pipeline enforces a strict sequence:
   `NOT_STARTED` -> `RUNNING` -> `EXECUTION_PLAN_COMPLETE` -> `CLIP_STRATEGY_COMPLETE` -> `PROMPT_TEMPLATE_COMPLETE` -> `SUITABILITY_COMPLETE` -> `COMPLETED`.
3. **Resilience**: If a stage fails (e.g. AI provider timeout), the pipeline state is marked as `FAILED`. Re-running the pipeline will resume exactly from the last completed stage.
4. **Typed Exceptions**: Only explicit `DomainError` subclasses (`PlanningError`, `ValidationError`, `InfrastructureError`, `PersistenceError`) are raised.

## `PlanningPipelineResult` Aggregate

The result of the pipeline is persisted as a `PlanningPipelineResult`.
It contains:
- `execution_plan`: High-level creative direction.
- `clip_strategy`: Granular clip breakdowns.
- `prompt_template`: The literal prompts to be fed into the Video Engine.
- `suitability_assessment`: An assessment of whether the campaign is feasible.
- `overall_confidence`: A deterministically aggregated float (0.0 to 1.0) indicating AI confidence.

### Confidence Calculation
Confidence is aggregated deterministically by taking the mean of all available confidence scores (e.g., `execution_plan.confidence_score` and `suitability_assessment.confidence`). The aggregation occurs in `result.compute_overall_confidence()`. It is never silently overwritten or lost.

## Extension Points

### Future Planner Implementations
If you need to add a new planning stage (e.g., `MusicSelectionPlan`), you must:
1. Define the Domain Entity (e.g., `CampaignMusicPlan`) in `src/domain/campaign_entities.py`.
2. Add the field to `PlanningPipelineResult`.
3. Add a new `PipelineStatus` enum (e.g., `MUSIC_PLAN_COMPLETE`).
4. Update `PlanningPipelineResult.validate_consistency()` to check for it.
5. Create a new atomic use case in `src/application/planning_use_cases.py` (e.g., `GenerateMusicPlanUseCase`).
6. Inject the use case into `PlanningPipelineService` and add a new Stage execution block that checks `if not result.music_plan: ...`.

### Adding AI Providers
Because the pipeline depends on `ICampaignIntelligence`, you can swap the LLM provider (e.g., from OpenAI to Anthropic) by simply changing the DI binding in `presentation/api/campaigns.py`. The Orchestration layer requires absolutely zero changes.
