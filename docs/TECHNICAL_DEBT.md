# Technical Debt Register

## Known Ruff Violations
- **Description**: The backend codebase currently has 109 `ruff` violations. These consist primarily of unused imports (`F401`), module-level imports not at the top of the file (`E402`), undefined names (`F821`), bare exceptions (`E722`), and ambiguous variable names (`E741`). 
- **Impact**: Code readability is diminished, and in cases of `F821` and `E722`, it risks masking real runtime errors and makes the codebase harder to maintain and test.
- **Future Milestone Recommendation**: Resolve all `F821`, `E722`, and `E741` issues immediately. Automate the resolution of `F401` and `E402` using `ruff --fix`.
- **Priority**: Medium

## Known ESLint Violations
- **Description**: The frontend codebase has 16 active `@typescript-eslint/no-explicit-any` violations distributed across components (e.g., `CreateProjectDialog.tsx`, `VideoUploader.tsx`) and stores (e.g., `useAppStore.ts`, `useCampaignStore.ts`).
- **Impact**: Suppressing strict typing bypasses TypeScript's safety mechanisms, leading to potential runtime errors when the shapes of objects or API responses change.
- **Future Milestone Recommendation**: Define proper interfaces/types for all existing `any` usages and ensure subsequent PRs do not introduce new usages of `any`.
- **Priority**: Low

## Failing Tests
- **Description**: The backend `pytest` suite fails to collect tests and exits with code `1`. The failure is rooted in `ModuleNotFoundError: No module named 'src.reasoning.recommendation.interfaces'`. Furthermore, there is a documented assertion failure in `test_projects_create_schema_and_error` inside `tests/test_api_integration.py`.
- **Impact**: Developers cannot confidently verify that their changes do not break existing backend logic. Missing tests directly compromise the continuous integration pipeline's ability to guard the main branch.
- **Future Milestone Recommendation**: Fix the missing module imports, resolve the broken assertions, and ensure the test suite achieves a clean green state.
- **Priority**: High

## Incomplete Modules
- **Description**: The module `src.reasoning.recommendation.interfaces` is referenced but completely missing from the codebase.
- **Impact**: It breaks the `CampaignReasoningFactory` initialization pipeline, preventing reasoning modules from being instantiated and severely impacting testing and runtime behavior.
- **Future Milestone Recommendation**: Implement the missing interface contracts for the recommendation engine.
- **Priority**: High

