# Changeset Verification Standard

## 1. Purpose

The Changeset Verification Standard establishes the deterministic engineering process for evaluating raw repository modifications following an implementation batch. It ensures that all claims of repository change are explicitly verified against tangible Repository Evidence before any architectural or specification review occurs. 

Changeset Verification answers a single, isolated question: *"What physically changed?"*

This standard explicitly does NOT perform the responsibilities of the Repository Review Standard.

## 2. Scope

This standard governs the inspection of file-level and repository-level modifications. It strictly isolates the identification of changes from the evaluation of their correctness. 

Changeset Verification is constrained to:
- Identifying created, modified, and deleted files.
- Verifying the implementation stayed within the approved repository boundaries.
- Verifying documentation was updated synchronously with code.
- Confirming the physical presence of expected deliverables.
- Identifying external integration points affected by the changeset.

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

Changeset Verification is governed by the following core principles:
- **Repository Truth**: The physical state of the repository is the only accepted reality.
- **Evidence First Engineering**: Every claim must be backed by verifiable Repository Evidence.
- **Deterministic Reviews**: The verification must produce the same result regardless of the reviewer.
- **Repeatability**: The evidence collection must be reproducible at any future date.
- **Objectivity**: Findings are factual observations, free from opinion or interpretation.
- **Scope Discipline**: Implementation must remain strictly within approved boundaries.
- **Traceability**: Every Engineering Finding, Risk, Readiness Assessment, and Verdict must trace back to Repository Evidence.

## 5. Responsibilities

**Author**
- Must provide clear, reproducible Repository Evidence of the changeset (e.g., file inventory, diff logs).
- Must declare all repository boundaries affected by the implementation.
- Must ensure documentation reflects the exact physical state of the implementation.

**Reviewer (Changeset Verifier)**
- Must objectively verify the provided Repository Evidence against the repository's physical state.
- Must identify any undisclosed or out-of-scope modifications.
- Must suspend verification if Repository Truth contradicts the author's claims.

## 6. Repository Boundaries

Implementation must remain strictly within the approved boundaries defined in the governing Engineering Specification. Changeset Verification involves comparing the actual modified paths against the approved operational scope. Any file modified outside these boundaries represents an engineering violation.

## 7. Expected Files

Changeset Verification categorizes changes based on the specification's approved scope:

- **Expected Created Files:** Files explicitly authorized to be created.
- **Expected Modified Files:** Existing files explicitly authorized to be altered.
- **Expected Deleted Files:** Files explicitly authorized to be removed.

## 8. Unexpected Files

Any file created, modified, or deleted that was not explicitly authorized by the governing specification is categorized as an **Unexpected File**. 

Unexpected files constitute a violation of Scope Discipline and must be flagged as a Changeset Risk. The verification must halt, and the unexpected changes must be documented for rejection or subsequent remediation.

## 9. Change Budget

Changeset Verification respects the concept of a Change Budget, which represents the maximum allowable impact area defined during specification. If the sheer volume or spread of changes drastically exceeds the anticipated footprint, it must be recorded as an Engineering Finding, regardless of whether individual file changes seem justified.

## 10. Repository Truth Verification

The core principle of this standard is **Repository Truth**. The verifier must rely solely on the physical state of the repository (e.g., Git history, file existence) rather than the author's assertions. If a file is claimed to be complete but is not physically present in the expected location, the Repository Truth takes precedence, and the claim is invalidated.

## 11. Documentation Synchronization Verification

Implementation is not complete until the accompanying documentation accurately reflects the new repository state. Changeset Verification checks that:
- Any modified component's documentation (e.g., READMEs, internal docs) was updated in the same changeset.
- The documentation accurately describes the new physical layout and file structure.
- No obsolete files or directories remain referenced in updated documentation.

## 12. Dependency Awareness

Changeset Verification observes dependencies solely to document them. It identifies new `import` statements, new package inclusions (e.g., `package.json`, `requirements.txt`), and external calls. 
It **does not** evaluate whether these dependencies are architecturally sound or permitted. It only records their physical addition to the repository.

## 13. Integration Awareness

The verifier must identify and list all boundary integration points that the changeset interacts with. This includes APIs, database schemas, external services, or shared libraries. Like dependency awareness, this is an observational step to establish facts for downstream Architecture Verification.

## 14. Scope Verification

Scope Verification confirms that the physical boundaries of the changeset perfectly map to the authorized scope in the specification. It ensures no "drive-by" refactoring or speculative implementations were included.

## 15. Deliverable Verification

The verifier checks the physical existence of every deliverable promised in the Engineering Specification. This is a binary check: the deliverable exists at the specified path, or it does not.

## 16. Evidence Collection Expectations

Authors are expected to provide verifiable Repository Evidence formats, such as:
- Raw Git diffs or status outputs.
- File system tree snapshots.
- Search (grep) results proving the existence or absence of specific patterns.

Reviewers must be able to deterministically reproduce this Repository Evidence.

## 17. Changeset Findings

Findings during Changeset Verification are purely factual observations of the repository state:
- Missing deliverables.
- Unexpected file modifications.
- Out-of-sync documentation.
- Undocumented new dependencies.

Every Engineering Finding must be traceable to Repository Evidence.

## 18. Changeset Risks

Risks are factual deviations that threaten downstream verification:
- Modifications extending into core architecture boundaries without authorization.
- Large swaths of unexpected file deletions.
- Evidence of "shadow" implementation not tracked in the specification.

Every Risk must be traceable to Repository Evidence.

## 19. Readiness Assessment

A changeset is deemed ready for downstream Repository Review only when:
- The file inventory matches the approved scope.
- No unexpected files remain unexplained or unmitigated.
- Documentation is synchronized.
- All requested deliverables physically exist in the repository.

Every Readiness Assessment must be traceable to Repository Evidence.

## 20. Verification Verdict

The Changeset Verification concludes with one of the following Verdicts:

- **Ready for Repository Review:** The changeset perfectly matches the approved scope, deliverables are present, and documentation is synchronized.
- **Ready for Repository Review (with Minor Discrepancies):** The changeset is fundamentally sound but contains trivial, non-architectural deviations (e.g., typo fixes in unrelated files) that do not impact scope.
- **Verification Deferred:** The provided Repository Evidence is incomplete, or the physical Repository Truth contradicts the author's claims. Verification cannot proceed until evidence is corrected.
- **Verification Rejected:** The changeset grossly violates Scope Discipline, contains significant unexpected files, or fails to deliver the promised artifacts. The implementation must be reverted or heavily revised.

Every Verdict must be traceable to Repository Evidence. Repository Evidence must always take precedence over reviewer opinion.

This standard explicitly concludes with a "Ready for Repository Review" status. It does NOT imply Approval, Certification, Merge, Final Acceptance, or Architecture Sign-off.
