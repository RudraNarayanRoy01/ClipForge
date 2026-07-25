---
Classification: Living Document (Continuously Updated)
Update Frequency: Continuously
Primary Owner: CTO / Principal Architect
---

# Architecture Map

This document provides a high-level navigation map of the platform's architecture.

## High-Level Topology

```mermaid
flowchart TD
    Platform[ClipForge Platform]
    
    Platform --> UI[Frontend / UI]
    Platform --> Core[Application Core]
    Platform --> Runtime[Adaptive AI Runtime]
    Platform --> Data[Data Persistence]
    
    Core --> Campaign[Campaign Intelligence]
    Core --> Editing[Editing Engine]
    Core --> Timeline[Timeline Engine]
    
    Runtime --> Registry[Capability Registry]
    Runtime --> Context[Runtime Context]
    Context --> DecisionPipeline[Runtime Decision Pipeline]
    
    DecisionPipeline --> PlanningStrategy[Runtime Planning Strategy]
    DecisionPipeline --> Planning[Runtime Planning]
    DecisionPipeline --> Policy[Runtime Policy]
    DecisionPipeline --> Constraint[Runtime Constraint Engine]
    DecisionPipeline --> Budget[Runtime Budget Planner]
    DecisionPipeline --> Routing[Runtime Routing]
    
    Runtime --> Planner[Execution Planning]
    Runtime --> Graph[Execution Graph Builder]
    Runtime --> Sched[Scheduler]
    Runtime --> Executor[Runtime Executor]
    Runtime --> Lifecycle[Runtime Lifecycle]
    Runtime --> Retry[Runtime Retry]
    Runtime --> Adapt[Adaptive Runtime]
    Runtime --> Monitor[Runtime Monitoring]
    Runtime --> Telemetry[Runtime Telemetry]
    Runtime --> Metrics[Runtime Metrics]
    Runtime --> Health[Runtime Health]
    Runtime --> Diagnostics[Runtime Diagnostics]
    Runtime --> Observation[Runtime Observation]
    Runtime --> Optimization[Runtime Optimization]
    Runtime --> Learning[Runtime Learning]
    
    Sched --> Providers[Provider Ecosystem]
    
    Providers --> ProviderRegistry[Provider Registry - Identity]
    Providers --> ProviderCapabilityRegistry[Provider Capability Registry - Features]
    Providers --> ModelRegistry[Model Registry - Metadata]
    Providers --> ModelLifecycleManager[Model Lifecycle Manager]
    Providers --> ProviderHealthManager[Provider Health Manager]
    Providers --> ProviderFailoverManager[Provider Failover Manager]
    Providers --> RuntimeRetryManager[Runtime Retry Manager]
    Providers --> RuntimeSchedulingManager[Runtime Scheduling Manager]
    Providers --> RuntimeExecutionManager[Runtime Execution Manager]
    
    ProviderRegistry --> Local[Local Hardware (CUDA, CPU)]
    Providers --> Cloud[Cloud APIs (OpenAI, Gemini)]
```

## Data Flow & Dependencies

**Dependency Direction (Inversion Principle):**
Application -> Runtime Contracts
Application -> Runtime Bootstrap -> Runtime Context -> Runtime Capability Registry -> Runtime Resource Discovery -> Runtime Provider Registry -> Runtime Hardware Discovery -> Hardware Registrations -> Runtime Provider Selection -> Runtime Scheduler -> Runtime Execution Planner -> Runtime Execution Graph Builder -> Runtime Resource Allocator -> Runtime Execution Context Factory -> Runtime Orchestrator -> Runtime Executor -> Runtime Lifecycle -> Runtime Retry -> Adaptive Runtime -> Runtime Monitoring -> Runtime Telemetry -> Runtime Metrics -> Runtime Health -> Runtime Diagnostics -> Runtime Optimization -> Runtime Learning -> Runtime Planning Strategy -> Runtime Planning -> Runtime Policy -> Runtime Constraint Engine -> Runtime Budget Planner -> Runtime Routing
Runtime -> Provider Ecosystem -> Hardware
ProviderRegistry -> ProviderInfo -> ProviderCapabilityRegistry -> ProviderCapability -> ModelRegistry -> ModelInfo -> ModelLifecycleManager -> ProviderHealthManager -> ProviderFailoverManager -> RuntimeRetryManager -> RuntimeSchedulingManager -> RuntimeExecutionManager

**Ownership:**
- **Application Core**: Owned by Domain Logic.
- **Adaptive AI Runtime**: Owned by Platform Engineering / Architecture.
- **Data Persistence**: Owned by Infrastructure layer.

**Decision Ownership (Runtime Pipeline):**
- `PlanningDecision`: Owned exclusively by `RuntimePlanning`.
- `PolicyDecision`: Owned exclusively by `RuntimePolicy`.
- `ConstraintDecision`: Owned exclusively by `RuntimeConstraintEngine`.
- `BudgetDecision`: Owned exclusively by `RuntimeBudgetPlanner`.
- `RoutingDecision`: Owned exclusively by `RuntimeRouting`.
- `ExecutionIdentity`, `ExecutionRequest`, `ExecutionStatus`, `ExecutionResult`: Owned by the Runtime Execution Model.
- `LifecycleIdentity`, `LifecycleResult`, `LifecycleTransition`, `LifecycleState`, `LifecycleStage`, `LifecycleSummary`: Owned by the Runtime Lifecycle Domain.
- `RetryIdentity`, `RetryResult`, `RetryDecision`, `RetryReason`, `RetryPolicy`, `RetrySummary`: Owned by the Runtime Retry Domain.
- `ObservationResult`, `ObservationRecord`, `ObservationCategory`, `ObservationSeverity`, `ObservationSummary`: Owned by the Runtime Observation Domain.
- `LearningResult`, `LearningPattern`, `LearningCategory`, `LearningConfidence`, `LearningSummary`: Owned by the Runtime Learning Domain.
- `OptimizationResult`, `OptimizationDecision`, `OptimizationCategory`, `OptimizationPriority`, `OptimizationSummary`: Owned by the Runtime Optimization Domain.
- `SchedulingIdentity`, `SchedulingDecision`: Owned by the RuntimeScheduler subsystem.
- `ProviderInfo`, `ProviderStatus`, `ProviderType`: Owned by the ProviderRegistry.
- `ProviderCapability`, `CapabilityLimits`, `CapabilityType`: Owned by the ProviderCapabilityRegistry.
- `ModelInfo`, `ModelStatus`, `ModelType`: Owned by the ModelRegistry.
- `ModelLifecycleInfo`, `ModelLifecycleState`, `ModelLifecycleTransition`, `ModelLifecycleResult`: Owned by the ModelLifecycleManager.
- `ProviderHealthInfo`, `ProviderHealthState`, `ProviderHealthTransition`, `ProviderHealthResult`: Owned by the ProviderHealthManager.
- `ProviderFailoverInfo`, `ProviderFailoverState`, `ProviderFailoverTrigger`, `ProviderFailoverDecision`, `ProviderFailoverResult`: Owned by the ProviderFailoverManager.
- `RuntimeRetryInfo`, `RuntimeRetryState`, `RuntimeRetryTrigger`, `RuntimeRetryDecision`, `RuntimeRetryResult`: Owned by the RuntimeRetryManager.
- `RuntimeScheduleInfo`, `RuntimeScheduleState`, `RuntimeScheduleTrigger`, `RuntimeScheduleDecision`, `RuntimeScheduleResult`: Owned by the RuntimeSchedulingManager.
- `RuntimeExecutionInfo`, `RuntimeExecutionState`, `RuntimeExecutionTrigger`, `RuntimeExecutionDecision`, `RuntimeExecutionResult`: Owned by the RuntimeExecutionManager.
- `RuntimeContext`: Owns the Runtime Decision Environment and composition, but NOT the decisions themselves.

**Certification Status:**
- Sprint 6.4 (Planning & Policy) is formally certified and architecturally complete. Future components integrate via composition on the RuntimeContext.
- Batch 6.5.1 (Runtime Execution Model) is complete, establishing pure declarative execution artifacts.
- Batch 6.5.2 (Runtime Scheduler) is complete, establishing the immutable Scheduling Domain Model.
- Batch 6.5.3 (Runtime Executor) is complete, establishing the Execution Result Domain and RuntimeExecutor service.
- Batch 6.5.4 (Runtime Lifecycle) is complete, establishing the immutable Lifecycle Domain and RuntimeLifecycle engine.
- Batch 6.5.5 (Runtime Retry) is complete, establishing the immutable Retry Domain and RuntimeRetry evaluation engine.
- Batch 6.5.6 (Runtime Observation) is complete, establishing the immutable Observation Domain and RuntimeObservation extraction engine, explicitly distinguished from Monitoring.
- Batch 6.5.7 (Runtime Learning) is complete, establishing the immutable Learning Domain and RuntimeLearning extraction engine, explicitly distinguished from Prediction and Optimization.
- Batch 6.5.8 (Runtime Optimization) is complete, establishing the immutable Optimization Domain and RuntimeOptimization engine, strictly concluding the Sprint 6.5 adaptive pipeline.
- Batch 6.6.1 (Provider Registry) is complete, establishing the pure metadata registry for Provider Identity.
- Batch 6.6.2 (Provider Capability) is complete, establishing the ProviderCapabilityRegistry and immutable capability artifacts, enforcing strict separation from Identity.
- Batch 6.6.3 (Model Registry) is complete, establishing the pure metadata registry for Model Metadata.
- Batch 6.6.4 (Model Lifecycle) is complete, establishing declarative structural transitions for model states.
- Batch 6.6.5 (Provider Health) is complete, establishing the observational ProviderHealthManager independent of execution.
- Batch 6.6.6 (Provider Failover) is complete, establishing the purely structural observational failover manager.
- Batch 6.6.7 (Runtime Retry) is complete, establishing the purely structural ecosystem retry policy distinct from execution retries.
- Batch 6.6.8 (Runtime Scheduling) is complete, establishing the pure structural Execution Eligibility manager.
- Batch 6.6.9 (Runtime Execution) is complete, establishing the pure structural Execution Preparation manager decoupled from Scheduling.
