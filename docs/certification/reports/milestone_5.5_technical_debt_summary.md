# Milestone 5.5 Technical Debt Summary

## Objective
This document reviews and classifies all known technical debt recorded during Milestone 5.5 certification, without introducing new items.

## Classification Policy
- **Resolved**: Debt that has been paid down during the certification batches.
- **Deferred**: Debt explicitly accepted as a constraint for the current milestone.
- **Future Milestone**: Actionable debt that must be resolved in subsequent development.

---

## 1. Resolved
- **Documentation Discrepancy (npm ci vs npm install)**: A known discrepancy in the health tracking documents was identified and resolved during Batch 5.5.7.3. (Evidence: `batch_5.5.7.3_documentation_consistency_report.md`)

## 2. Deferred
- **Python 3.14 MSVC Requirement (av package)**: Upstream constraints for the `av` package require MSVC tools on Python 3.14. This does not block core runtime startup on supported Python versions (>= 3.9) and is accepted as an Environment Compatibility Limitation. (Evidence: `batch_5.5.7.2_workflow_certification_summary.md`)
- **ESLint `any` Violations**: 16 active `@typescript-eslint/no-explicit-any` violations distributed across the frontend. Defining proper interfaces is deferred. (Evidence: `docs/TECHNICAL_DEBT.md`)

## 3. Future Milestone (Actionable)
- **CRITICAL BLOCKER: Missing Recommendation Interfaces**: The module `src.reasoning.recommendation.interfaces` is missing, breaking `CampaignReasoningFactory` and the backend test suite. **This must be fixed before any new functionality is implemented in Milestone 6.** (Evidence: `docs/ARCHITECTURE_CERTIFICATION.md`, `docs/TECHNICAL_DEBT.md`)
- **Backend Test Suite Integrity**: The backend `pytest` suite fails to collect tests due to the missing module, and contains a documented assertion failure in `test_projects_create_schema_and_error`. (Evidence: `docs/TECHNICAL_DEBT.md`)
- **Ruff Linting Violations**: 109 `ruff` violations exist in the backend (unused imports, undefined names, bare exceptions). Must resolve `F821`, `E722`, and `E741` issues immediately in the future milestone. (Evidence: `docs/TECHNICAL_DEBT.md`)
