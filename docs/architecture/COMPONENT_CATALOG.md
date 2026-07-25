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
- **Current Implementation Status**: Foundation phase complete. Runtime Observation & Reasoning subsystems (Monitoring, Telemetry, Metrics, Health, Diagnostics, Optimization, and Learning) are structurally complete and formally certified (Sprint 6.3). Runtime Planning Foundation, Runtime Planning Strategy, Runtime Policy, Runtime Constraint Engine, Runtime Budget Planner, and Runtime Routing are established (Sprint 6.4). The `RuntimeContext` has been formally expanded to act as the canonical Runtime Decision Environment, owning the complete decision pipeline. Batch 6.4.8 establishes declarative Runtime Planning Governance over this pipeline. Batch 6.4.9 formally certifies the Runtime Planning & Policy Engine. Sprint 6.4 is now declared architecturally complete, serving as the certified foundation for future Runtime capabilities. Batch 6.5.1 establishes the Runtime Execution Domain Model, setting the architectural foundation with immutable execution artifacts for subsequent scheduling and execution implementations. Batch 6.5.2 establishes the Runtime Scheduling Domain (SchedulingIdentity, SchedulingDecision, Policy, Strategy, QueueClassification) and implements the RuntimeScheduler as a pure decision service independent of execution mechanics. Batch 6.5.3 establishes the Runtime Executor and Execution Result Domain Model, implementing immutable execution outcomes (ExecutionResult, ExecutionOutcome, ExecutionStatus, ExecutionSummary) exclusively produced by the RuntimeExecutor service. Batch 6.5.4 establishes the Runtime Lifecycle Domain, distinguishing the Application Lifecycle from the Execution Lifecycle. It introduces the RuntimeLifecycle engine and immutable Lifecycle artifacts (LifecycleResult, LifecycleTransition, LifecycleState, LifecycleStage, LifecycleSummary) strictly decoupling execution evaluation from future capabilities like Retry and Observation. Batch 6.5.5 establishes the Runtime Retry Evaluation engine (RuntimeRetry) and immutable Retry Domain artifacts (RetryResult, RetryDecision, RetryReason, RetryPolicy, RetrySummary). It explicitly decouples pure retry evaluation from recovery behavior, ensuring RetryResult acts as an immutable observation source for future components. Batch 6.5.6 establishes the Runtime Observation Domain, introducing the RuntimeObservation engine and immutable Observation artifacts (ObservationResult, ObservationRecord, ObservationCategory, ObservationSeverity, ObservationSummary). It explicitly distinguishes pure Runtime Observation from continuous active Monitoring. Batch 6.5.7 establishes the Runtime Learning Domain, introducing the RuntimeLearning engine and immutable Learning artifacts (LearningResult, LearningPattern, LearningCategory, LearningConfidence, LearningSummary). It explicitly distinguishes Runtime Learning from Prediction and Optimization. Batch 6.5.8 establishes the Runtime Optimization Domain, introducing the RuntimeOptimization engine and immutable Optimization artifacts (OptimizationResult, OptimizationDecision, OptimizationCategory, OptimizationPriority, OptimizationSummary). It strictly differentiates declarative optimization derivation from optimization application and resource management. Sprint 6.5 is formally certified as architecturally complete, finalizing the immutable execution pipeline from Execution Request through Optimization.
- **Future Extension Points**: Provider Ecosystem.
