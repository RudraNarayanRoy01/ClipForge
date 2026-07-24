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
- **Current Implementation Status**: Foundation phase (Architecture boundary, canonical Runtime Context, bootstrap, lifecycle, Capability Registry, Resource Discovery, Provider Registry, Hardware Discovery, Provider Selection, Scheduler, Execution Planner, Execution Graph Builder, Resource Allocator, Execution Context Factory, Runtime Orchestrator, Runtime Execution Engine, Adaptive Runtime, Runtime Monitoring, and Runtime Telemetry established).
- **Future Extension Points**: Metrics, Diagnostics, Adaptive Optimization, Provider Ecosystem.
