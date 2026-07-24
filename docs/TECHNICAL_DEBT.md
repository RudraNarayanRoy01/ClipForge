# Technical Debt Register
**Roadmap: AI Clipping Platform | Milestone: 6 | Sprint: 6.4 | Batch: 6.4.5**

## 1. Resolved During Sprint 6.4

### 1.1 Runtime Hardware Discovery
- **Description**: The Runtime lacked a canonical registry to discover and manage hardware (CUDA, CPU) definitions.
- **Severity**: Medium
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved)
- **Certification Impact**: Was blocking hardware abstraction.
- **Blocking Status**: Resolved (No longer blocking)

### 1.2 Runtime Provider Registry Foundation
- **Description**: The Runtime lacked a canonical registry to own and manage provider implementations.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved)
- **Certification Impact**: Was blocking provider abstraction.
- **Blocking Status**: Resolved (No longer blocking)

### 1.3 Runtime Execution Planner
- **Description**: The Runtime lacked a canonical subsystem for defining execution intent via immutable blueprints (logical execution stages).
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved)
- **Certification Impact**: Was blocking execution planning and structuring.
- **Blocking Status**: Resolved (No longer blocking)

### 1.4 Runtime Execution Graph Foundation
- **Description**: Transformation of logical execution stages into a concrete dependency graph (nodes, edges, topology).
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.2.3)
- **Certification Impact**: Was blocking execution dependency modeling.
### 1.5 Runtime Resource Allocation
- **Description**: Resource allocation modeling logical resource requirements.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.2.4)
- **Certification Impact**: Was blocking logical resource coordination.
- **Blocking Status**: Resolved (No longer blocking)

### 1.6 Runtime Execution Context Foundation
- **Description**: Establishment of architectural execution preparation via ExecutionContext.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.2.5)
- **Certification Impact**: Was blocking architectural execution preparation.
- **Blocking Status**: Resolved (No longer blocking)

### 1.7 Runtime Orchestrator Foundation
- **Description**: Setup of execution orchestration and coordination.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.2.6)
- **Certification Impact**: Was blocking execution orchestration.
- **Blocking Status**: Resolved (No longer blocking)

### 1.8 Runtime Execution Engine Foundation
- **Description**: Execution of the coordinated stages via providers and hardware.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.2.7)
- **Certification Impact**: Was blocking execution of coordinated workflows.
- **Blocking Status**: Resolved (No longer blocking)

### 1.9 Adaptive Runtime Foundation
- **Description**: The Runtime lacked a canonical subsystem to evaluate execution and recommend future adaptations without executing or optimizing.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.2.8)
- **Certification Impact**: Was blocking adaptive runtime capabilities.
- **Blocking Status**: Resolved (No longer blocking)

### 1.10 Runtime Monitoring Foundation
- **Description**: The Runtime lacks a canonical subsystem to monitor execution and adaptation.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.3.1)
- **Certification Impact**: Was blocking execution observation.
- **Blocking Status**: Resolved (No longer blocking)

### 1.11 Runtime Telemetry Foundation
- **Description**: The Runtime lacked a canonical subsystem to capture continuous execution signals.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.3.2)
- **Certification Impact**: Was blocking execution signal capture.
- **Blocking Status**: Resolved (No longer blocking)

### 1.12 Runtime Metrics Foundation
- **Description**: The Runtime lacked a canonical subsystem to calculate and aggregate quantitative metrics from captured telemetry signals.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.3.3)
- **Certification Impact**: Was blocking quantitative measurement.
- **Blocking Status**: Resolved (No longer blocking)

### 1.13 Runtime Health Foundation
- **Description**: The Runtime lacked a canonical subsystem to evaluate health based on captured metrics.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.3.4)
- **Certification Impact**: Was blocking operational evaluation.
- **Blocking Status**: Resolved (No longer blocking)

### 1.14 Runtime Diagnostics Foundation
- **Description**: The Runtime lacked a canonical subsystem to diagnose why the Runtime is in a specific operational condition.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.3.5)
- **Certification Impact**: Was blocking diagnostic reasoning.
- **Blocking Status**: Resolved (No longer blocking)

### 1.15 Runtime Optimization Foundation
- **Description**: The Runtime lacked a canonical subsystem to produce optimization decisions based on diagnostics.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.3.6)
- **Certification Impact**: Was blocking optimization reasoning.
- **Blocking Status**: Resolved (No longer blocking)

### 1.16 Runtime Learning Foundation
- **Description**: The Runtime lacked a canonical subsystem for knowledge persistence and historical runtime intelligence.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.3.7)
- **Certification Impact**: Was blocking runtime knowledge persistence.
- **Blocking Status**: Resolved (No longer blocking)

### 1.17 Runtime Planning Foundation
- **Description**: The Runtime lacked a canonical subsystem for answering "What should happen next?" based on RuntimeKnowledge.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.4.1)
- **Certification Impact**: Was blocking execution intention generation.
- **Blocking Status**: Resolved (No longer blocking)

### 1.18 Runtime Planning Strategy
- **Description**: The Runtime lacked a canonical subsystem for providing a planning philosophy to guide RuntimePlanning.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.4.2)
- **Certification Impact**: Was blocking strategy-driven planning.
- **Blocking Status**: Resolved (No longer blocking)

### 1.19 Runtime Policy Foundation
- **Description**: The Runtime lacked a canonical subsystem for answering "Is this PlanningDecision permitted?"
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.4.3)
- **Certification Impact**: Was blocking runtime architectural governance and policy evaluation.
- **Blocking Status**: Resolved (No longer blocking)

### 1.20 Runtime Constraint Engine
- **Description**: The Runtime lacked a canonical subsystem for answering "What architectural constraints apply?" based on a PolicyDecision.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.4.4)
- **Certification Impact**: Was blocking runtime execution boundaries definition.
- **Blocking Status**: Resolved (No longer blocking)

### 1.21 Runtime Budget Planner
- **Description**: The Runtime lacked a canonical subsystem for answering "What execution budget is available?" based on a ConstraintDecision.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.4.5)
- **Certification Impact**: Was blocking runtime execution budget definitions.
- **Blocking Status**: Resolved (No longer blocking)

### 1.22 Runtime Routing
- **Description**: The Runtime lacked a canonical subsystem for answering "Where should this workload execute?" based on a BudgetDecision.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.4.6)
- **Certification Impact**: Was blocking runtime architectural routing.
- **Blocking Status**: Resolved (No longer blocking)

### 1.23 Runtime Context Expansion
- **Description**: The Runtime lacked a canonical Runtime Decision Environment formally owning the decision pipeline.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved in Batch 6.4.7)
- **Certification Impact**: Was blocking runtime governance and pipeline ownership.
- **Blocking Status**: Resolved (No longer blocking)

## 2. Deferred Beyond Sprint 6.4

- Planning Governance (Sprint 6.4.8)
- Planning & Policy Certification (Sprint 6.4.9)

## 3. Deferred Beyond Milestone 6 / To Future Milestones

- **Description**: The backend `pytest` suite previously failed to collect tests due to incorrect `IRenderBackend` imports (`src.domain.contracts.render_backend`).
- **Severity**: Critical
- **Owner**: Backend Core Team
- **Recommended Milestone**: N/A (Resolved)
- **Certification Impact**: Was blocking integration verification.
- **Blocking Status**: Resolved (No longer blocking)

### 3.2 Incomplete Reasoning Modules
- **Description**: The module `src.reasoning.recommendation.interfaces` was previously referenced but missing.
- **Severity**: High
- **Owner**: AI Infrastructure Team
- **Recommended Milestone**: N/A (Resolved)
- **Certification Impact**: Was breaking the `CampaignReasoningFactory` initialization pipeline.
- **Blocking Status**: Resolved (No longer blocking)

## 2. Deferred Beyond Milestone 5.6 / To Future Milestones

### 3.3 Known Ruff Violations
- **Description**: The backend codebase currently has 109 `ruff` violations (e.g., unused imports, bare exceptions).
- **Severity**: Medium
- **Owner**: Backend Core Team
- **Recommended Milestone**: Milestone 6 (Dedicated cleanup sprint)
- **Certification Impact**: Non-blocking for Milestone 5.6.
- **Blocking Status**: Deferred

### 3.4 Known ESLint Violations
- **Description**: The frontend codebase has 16 active `@typescript-eslint/no-explicit-any` violations.
- **Severity**: Low
- **Owner**: Frontend Core Team
- **Recommended Milestone**: Milestone 6 (Dedicated typing sprint)
- **Certification Impact**: Non-blocking for Milestone 5.6.
- **Blocking Status**: Deferred
