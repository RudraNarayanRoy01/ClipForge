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
    Runtime --> Adapt[Adaptive Runtime]
    Runtime --> Monitor[Runtime Monitoring]
    Runtime --> Telemetry[Runtime Telemetry]
    Runtime --> Metrics[Runtime Metrics]
    Runtime --> Health[Runtime Health]
    Runtime --> Diagnostics[Runtime Diagnostics]
    Runtime --> Optimization[Runtime Optimization]
    Runtime --> Learning[Runtime Learning]
    
    Sched --> Providers[Provider Ecosystem]
    
    Providers --> Local[Local Hardware (CUDA, CPU)]
    Providers --> Cloud[Cloud APIs (OpenAI, Gemini)]
```

## Data Flow & Dependencies

**Dependency Direction (Inversion Principle):**
Application -> Runtime Contracts
Application -> Runtime Bootstrap -> Runtime Context -> Runtime Capability Registry -> Runtime Resource Discovery -> Runtime Provider Registry -> Runtime Hardware Discovery -> Hardware Registrations -> Runtime Provider Selection -> Runtime Scheduler -> Runtime Execution Planner -> Runtime Execution Graph Builder -> Runtime Resource Allocator -> Runtime Execution Context Factory -> Runtime Orchestrator -> Runtime Execution Engine -> Adaptive Runtime -> Runtime Monitoring -> Runtime Telemetry -> Runtime Metrics -> Runtime Health -> Runtime Diagnostics -> Runtime Optimization -> Runtime Learning -> Runtime Planning Strategy -> Runtime Planning -> Runtime Policy -> Runtime Constraint Engine -> Runtime Budget Planner -> Runtime Routing
Runtime -> Provider Ecosystem -> Hardware

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
- `RuntimeContext`: Owns the Runtime Decision Environment and composition, but NOT the decisions themselves.

**Certification Status:**
- Sprint 6.4 (Planning & Policy) is formally certified and architecturally complete. Future components integrate via composition on the RuntimeContext.
