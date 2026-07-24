---
Classification: Living Document (Continuously Updated)
Update Frequency: Continuously
Primary Owner: CTO / Principal Architect
---

# AI Development Workflow

This document outlines the engineering operating procedure for ClipForge.

## The Workflow Lifecycle

1. **Definition of Ready**: The Batch objective is clearly defined, and architectural boundaries are understood.
2. **Implementation Plan**: An AI agent proposes a plan (e.g., `implementation_plan.md`) for the current Batch.
3. **Approval**: The Principal Engineer (User) approves the plan.
4. **Implementation**: Code and architecture scaffolding is written.
5. **Verification**: Automated and manual checks ensure no boundaries were violated.
6. **Architecture Review**: Ensuring Clean Architecture principles remain intact.
7. **Documentation Update**: Living documents (Architecture State, Component Catalog) are updated.
8. **Technical Debt Review**: Any accepted debt is logged.
9. **Acceptance**: The Batch is complete.
10. **Git Commit**: (Standard VC practices).
11. **Certification**: Periodically, the architecture is certified at the Sprint boundary.

## AI Agent Expectations
Since ClipForge is developed heavily using AI-assisted engineering, future coding agents **MUST**:
- Review the repository and handoff docs before proposing changes.
- Produce a detailed implementation plan prior to execution.
- Respect the Batch scope strictly. Do not invent unrequested features.
- Respect the estimated change budget.
- Avoid unrelated refactoring outside the Batch scope.
- Preserve dependency direction (Core <- Application <- Adapters/Runtime).
- Maintain architectural boundaries.
- Update documentation alongside implementation.
- Review technical debt before completion.
- Avoid introducing architectural shortcuts.
- **Preserve long-term maintainability over implementation speed.**
