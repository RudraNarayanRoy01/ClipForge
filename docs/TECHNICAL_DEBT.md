# Technical Debt Register
**Roadmap: AI Clipping Platform | Milestone: 6 | Sprint: 6.1 | Batch: 6.1.6**

## 1. Resolved During Sprint 6.1 (Batch 6.1.6)

### 1.1 Runtime Provider Registry Foundation
- **Description**: The Runtime lacked a canonical registry to own and manage provider implementations.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: N/A (Resolved)
- **Certification Impact**: Was blocking provider abstraction.
- **Blocking Status**: Resolved (No longer blocking)

## 2. Deferred Beyond Sprint 6.1 (Batch 6.1.6)

### 2.1 Hardware Discovery
- **Description**: Hardware detection (CUDA, CPU) is required for local execution but deferred.
- **Severity**: Medium
- **Owner**: Architecture Team
- **Recommended Milestone**: Milestone 6 (Next Batch)
- **Blocking Status**: Deferred

### 2.2 Provider Selection and Execution Engine
- **Description**: Intelligent provider selection, scheduling, and execution logic.
- **Severity**: High
- **Owner**: Architecture Team
- **Recommended Milestone**: Milestone 6 (Later Sprint)
- **Blocking Status**: Deferred

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
