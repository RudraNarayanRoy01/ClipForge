# Development Workflow

| Field | Value |
| --- | --- |
| Status | Draft |
| Owner | TPM / Governance Lead |
| Applies to | All engineering activity |
| Governing authority | [Engineering Constitution](MILESTONE_6A_ENGINEERING_SPECIFICATION.md) |
| Last updated | 2026-08-03 |

## 1. Purpose

This document defines the canonical engineering execution lifecycle for ClipForge. It establishes the sequential stages of implementation, the responsibilities of engineers, and the clear boundaries of engineering work. This workflow ensures that engineering execution remains aligned with the Engineering Constitution and the Milestone Execution Plan.

## 2. Workflow Principles

The engineering execution workflow is governed by the following principles:
- **Sequential Lifecycle**: Engineering progresses through strict, ordered stages.
- **Explicit Stage Boundaries**: The inputs, expectations, and transition criteria of each stage are clearly defined.
- **No Skipped Stages**: Every engineering change must proceed through all stages to ensure verification readiness and traceability.
- **Bounded Implementation**: Execution remains strictly confined within the scope and acceptance criteria of the approved specification.
- **Defined Purpose**: Each stage exists to achieve a specific repository reality, rather than to serve as a procedural hurdle.

## 3. When Implementation Begins

Implementation work does not begin based on assumptions, undocumented discussions, or incomplete designs. Engineering execution strictly commences only after an Engineering Specification has been formally approved and authorized by the Architecture Owner. The approved specification is the immutable boundary for the implementation phase.

## 4. The Implementation Lifecycle

The engineering execution workflow progresses through the following sequential stages. It terminates at the boundary of Repository Review readiness.

**Approved Engineering Specification**
The formal authorization and blueprint for the work.
↓
**Preparation**
Engineers align on the specification boundaries, understand the acceptance criteria, and ensure local environments reflect the current repository truth.
↓
**Implementation**
The core engineering work where code and structure are modified to satisfy the specification while preserving existing architecture.
↓
**Documentation Synchronization**
Updating all relevant documentation in the same change-set to ensure the repository truth remains cohesive.
↓
**Repository Evidence Collection**
Gathering objective proof (logs, command outputs, structural analysis) that the implementation satisfies the acceptance criteria.
↓
**Internal Engineering Self Review**
A final check by the implementing engineer to ensure scope discipline, architectural preservation, and evidence completeness.
↓
**Ready for Repository Review**
The implementation phase is complete, and the change-set is handed off for subsequent verification stages.

## 5. Engineering Stage Transitions

Work transitions between lifecycle stages only when specific philosophical criteria are met. This ensures quality is embedded in the process rather than deferred to final review.

**Preparation** ↓ **Implementation**
Execution begins *only after* the specification boundaries, acceptance criteria, and repository scope are fully understood.

**Implementation** ↓ **Documentation Synchronization**
Documentation updates occur *only after* the core implementation objectives have been satisfied within the change-set.

**Documentation** ↓ **Repository Evidence**
Evidence collection commences *only after* the repository truth has been restored and documentation correctly reflects the newly implemented state.

**Repository Evidence** ↓ **Internal Self Review**
Self review begins *only after* objective, deterministic evidence has been completely collected.

**Internal Self Review** ↓ **Ready for Repository Review**
The implementation phase concludes *only after* the change-set is internally validated against the scope, architecture, and evidence constraints defined in the specification.

## 6. Engineering Responsibilities

During the execution lifecycle, engineers are responsible for:
- Adhering strictly to the boundaries defined in the approved specification.
- Making architectural decisions that align with the Engineering Philosophy and the Engineering Decision Hierarchy.
- Ensuring that every implemented capability is backed by verifiable repository evidence.
- Maintaining the cohesion between code and documentation within the same logical change.
- Communicating openly about implementation constraints without unilaterally expanding scope.

## 7. Expected Engineering Behavior

Engineers are expected to operate with scope discipline and an evidence-first mindset. Behavior should focus on proving correctness rather than asserting it. The implementation must favor repository truth over undocumented assumptions, and engineers must prioritize the long-term maintainability of the architecture over temporary conveniences.

## 8. Implementation Completion

Implementation is considered complete when the repository state satisfies all requirements defined in the engineering specification, all necessary evidence has been collected, and the documentation accurately reflects the new state. 

Implementation completion does **NOT** equal:
- Repository Review
- Engineering Approval
- Architecture Verification
- Certification

Completion of implementation merely produces a repository state that becomes eligible for future review. This distinction is absolute: the implementation phase creates the evidentiary artifact, while subsequent, separate phases are responsible for evaluation and authorization.

## 9. Workflow Boundaries and Transition

The development workflow is strictly bounded. It governs only the process of translating an approved specification into a verifiable repository state. 

This workflow explicitly terminates when the implementation reaches the **Ready for Repository Review** state. It does not encompass the processes of Repository Review, Architecture Verification, Repository Inspection, or Certification, which are governed by separate, subsequent standards.
