# Repository Review Standard

## 1. Purpose

The Repository Review Standard establishes the process for evaluating an implemented changeset against its governing Engineering Specification. While Changeset Verification identifies *what* changed, the Repository Review determines if those changes *satisfy* the approved requirements.

This standard ensures that implementations meet Acceptance Criteria, fulfill the Definition of Done, and provide verifiable Repository Evidence before advancing to Architecture Verification.

This standard explicitly does NOT perform the responsibilities of the Changeset Verification Standard. It answers only: *"Did the implementation satisfy the approved Engineering Specification?"*

## 2. Scope

The Repository Review evaluates:
- Fulfillment of all promised deliverables.
- Adherence to the Acceptance Criteria defined in the specification.
- Completion of all items in the Definition of Done.
- The alignment between Repository Evidence and specification intent.

## 3. What This Standard is NOT (Out of Scope)

This standard explicitly does NOT perform:
- Architecture Verification
- Certification
- Repository Inspection
- Engineering Checklists
- Testing Standards
- CI/CD
- Coding Standards
- Style Guides
- Formatting Guides
- Automation
- Git Workflow
- Prompt Generation
- AI Instructions
- Implementation Guidance
- Future Batch Responsibilities

## 4. Engineering Principles

Repository Review is governed by the following core principles:
- **Repository Truth**: The physical state of the repository is the only accepted reality.
- **Evidence First Engineering**: Every claim must be backed by verifiable Repository Evidence.
- **Deterministic Reviews**: The verification must produce the same result regardless of the reviewer.
- **Repeatability**: The evidence collection must be reproducible at any future date.
- **Objectivity**: Findings are factual observations, free from opinion or interpretation.
- **Scope Discipline**: Implementation must remain strictly within approved boundaries.
- **Traceability**: Every Engineering Finding, Risk, Readiness Assessment, and Verdict must trace back to Repository Evidence.

## 5. Engineering Responsibilities

**Author**
- Must provide clear Repository Evidence linking implementation to the specification's Acceptance Criteria.
- Must ensure the implementation strictly fulfills the Definition of Done.
- Must address any Engineering Finding before the review is concluded.

**Reviewer**
- Must evaluate the implementation strictly against the approved specification.
- Must demand objective Repository Evidence for every Acceptance Criterion.
- Must categorize findings deterministically and objectively.

**Approver**
- Evaluates the final Readiness Assessment and Repository Review Verdict to determine if the batch can advance to Architecture Verification.

## 6. Repository Evidence Review

Evidence is the cornerstone of Repository Review. Reviewers must evaluate:
- **Completeness:** Does the evidence cover the entirety of the Acceptance Criteria?
- **Accuracy:** Does the evidence accurately reflect the current physical state of the repository?
- **Relevance:** Does the evidence specifically prove the criterion in question?

Subjective assertions (e.g., "The feature works") are invalid. Verifiable assertions (e.g., "Script `X` outputs `Y` when run against file `Z`") are required.

## 7. Deliverable Review

The reviewer verifies that every deliverable listed in the Engineering Specification has been implemented exactly as described. If a deliverable is present but structurally deficient compared to the specification, it is flagged as an Engineering Finding.

## 8. Acceptance Criteria Review

Each Acceptance Criterion is evaluated individually against provided Repository Evidence. The reviewer must state definitively whether the evidence proves the criterion has been met. Partial fulfillment is considered failure unless specifically permitted by the specification.

## 9. Definition of Done Review

The reviewer confirms that all conditions of the Definition of Done have been satisfied. This includes verifying that documentation is synchronized, dependencies are managed, and integration points are documented.

## 10. Engineering Findings

Findings are categorized based on their impact on the specification's fulfillment:

- **Critical:** The implementation fails to meet core Acceptance Criteria, breaks existing functionality, or violates immutable constraints. Requires immediate remediation.
- **Major:** A deliverable is incomplete or structurally deficient, or a Definition of Done item is unmet. Requires remediation before approval.
- **Minor:** A small deviation from the specification that does not impact core functionality or Acceptance Criteria (e.g., a missing metadata tag). Should be fixed but may not block conditional approval.
- **Observation:** A factual note about the implementation that does not violate the specification but warrants documentation.
- **Suggestion:** A recommendation for future improvement that is explicitly out of scope for the current review.

Every Engineering Finding must be traceable to Repository Evidence.

## 11. Positive Observations

The reviewer should explicitly document engineering strengths, particularly implementations that demonstrate exceptional adherence to Repository Truth, clear evidence collection, or elegant satisfaction of complex criteria.

Every Observation must be traceable to Repository Evidence.

## 12. Remaining Risks

The reviewer must document any risks identified during the review that may impact downstream Architecture Verification or Certification. This includes potential edge cases not covered by Acceptance Criteria or observed technical debt.

Every Risk must be traceable to Repository Evidence.

## 13. Readiness Assessment

The review concludes with a Readiness Assessment for subsequent phases:
- **Architecture Verification Readiness:** Is the implementation complete and sound enough for the Architecture Owner to evaluate drift and boundaries?
- **Certification Readiness:** Is the evidentiary trail robust enough to support final merge certification?
- **Git Readiness:** Are the commits logically structured and ready for integration?
- **Batch Readiness:** Does this implementation satisfy the overarching goals of the batch?

Every Readiness Assessment must be traceable to Repository Evidence.

## 14. Repository Review Verdict

The review yields one of the following Verdicts:

- **Ready for Architecture Verification:** The implementation perfectly satisfies the Engineering Specification. All Acceptance Criteria and Definitions of Done are met with clear Repository Evidence.
- **Ready for Architecture Verification (with Minor Observations):** The implementation satisfies the core specification, but contains minor, non-blocking findings. 
- **Ready for Architecture Verification (with Tracked Documentation Debt):** The implementation is technically sound, but non-critical documentation updates are required and explicitly tracked for a future batch.
- **Review Deferred:** The provided Repository Evidence is insufficient to evaluate the Acceptance Criteria, or the implementation is severely incomplete.
- **Review Rejected:** The implementation fails to satisfy the Engineering Specification, violates Critical criteria, or fundamentally misinterprets the requirements. Substantial rework is required.

Every Verdict must be traceable to Repository Evidence. Repository Evidence must always take precedence over reviewer opinion.

This standard explicitly concludes with a "Ready for Architecture Verification" status. It does NOT imply Approval, Certification, Merge, Final Acceptance, or Architecture Sign-off.

