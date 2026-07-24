---
Classification: Living Document (Continuously Updated)
Update Frequency: Continuously
Primary Owner: CTO / Principal Architect
---

# Component Catalog

This document serves as the architectural inventory of ClipForge, cataloging major subsystems, their responsibilities, and current implementation states.

## Subsystem: Campaign Intelligence
- **Responsibility**: Reasoning and evaluation of raw inputs and campaigns to determine eligibility and strategy.
- **Public Interfaces**: `ICampaignReasoningService`
- **Dependencies**: Depends on Application contracts, uses local evaluation models.
- **Lifecycle**: Per-request / Campaign evaluation cycle.
- **Current Implementation Status**: Active and stable.
- **Future Extension Points**: Pluggable evaluation rules engines.

## Subsystem: Editing Engine
- **Responsibility**: Orchestration of video rendering, effects, and manipulation pipelines.
- **Public Interfaces**: `IVideoProcessor`, `ITimelineBuilder`
- **Dependencies**: System dependencies (ffmpeg).
- **Lifecycle**: Task-based worker execution.
- **Current Implementation Status**: Active and stable.
- **Future Extension Points**: Distributed rendering, GPU acceleration.

## Subsystem: Adaptive AI Runtime
- **Responsibility**: Orchestrating AI computation independently of specific providers and hardware, discovering available resources, and managing runtime architecture.
- **Public Interfaces**: (Deferred to subsequent batches)
- **Dependencies**: Depends ONLY on Application-defined abstract contracts. No outward dependencies to providers yet.
- **Lifecycle**: Global / Platform-wide execution engine, managed by `RuntimeLifecycleCoordinator` (owned by `RuntimeContext`).
- **Current Implementation Status**: Foundation phase complete. Runtime Observation & Reasoning subsystems (Monitoring, Telemetry, Metrics, Health, Diagnostics, Optimization, and Learning) are structurally complete and formally certified (Sprint 6.3). Runtime Planning Foundation, Runtime Planning Strategy, Runtime Policy, Runtime Constraint Engine, Runtime Budget Planner, and Runtime Routing are established (Sprint 6.4). The `RuntimeContext` has been formally expanded to act as the canonical Runtime Decision Environment, owning the complete decision pipeline. Batch 6.4.8 establishes declarative Runtime Planning Governance over this pipeline. Batch 6.4.9 formally certifies the Runtime Planning & Policy Engine. Sprint 6.4 is now declared architecturally complete, serving as the certified foundation for future Runtime capabilities.
- **Future Extension Points**: Provider Ecosystem.
