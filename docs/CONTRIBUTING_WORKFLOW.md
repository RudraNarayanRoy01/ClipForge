# Contribution Workflow

This document details the standard lifecycle for all contributions to the ClipForge repository. Please follow these steps strictly to ensure a consistent developer experience and repository governance.

## 1. Issue

All work begins with an issue.
- Choose the appropriate template: **Bug Report**, **Feature Request**, or **Architecture Improvement**.
- Discuss the proposed solution with maintainers before starting implementation.

## 2. Branch

Create a feature branch from `main`. Use a descriptive naming convention indicating the type of work and a short description:
```bash
git checkout -b <type>/<short-description>
# Example: git checkout -b feat/render-pipeline
```

## 3. Development

Write your code following the repository's established conventions.
- Do not introduce new automation, CI pipelines, or unapproved global tools (e.g., Husky, pre-commit) unless explicitly requested.
- Adhere strictly to the existing tooling outlined in [`DEVELOPMENT.md`](DEVELOPMENT.md).

### Optional Local Git Hooks
You may manually configure local Git hooks (e.g., `.git/hooks/pre-commit` or `.git/hooks/pre-push`) to automatically run static analysis and tests before committing.
*Note:* These are strictly opt-in and local-only. We do not enforce `Husky`, `pre-commit` frameworks, or automated Git hook injection on clone, in order to keep the developer environment un-opinionated.

## 4. Verification

Before committing, manually verify your changes:
- Run all local unit tests via `pytest` for the backend.
- Run static analysis via `ruff check .` for backend and `npm run lint` for frontend.
- Ensure no new violations are introduced and all existing quality gates pass (or maintain the current state of known failures).

## 5. Commit

We enforce a strict commit message convention based on existing repository patterns. Do not invent a new format.

**Format:**
```
<type>(<scope>): Batch <milestone.batch> <description>
```

**Examples:**
- `chore(tooling): Batch 5.5.1.4 standardize development environment`
- `feat(render): Batch 5.6.4 implement render execution pipeline`
- `test(render): Batch 5.6.5 verify end-to-end render integration`

## 6. Pull Request

Push your branch and open a Pull Request against `main`.
- Use the standard `.github/pull_request_template.md`.
- Fill out all sections, including the Milestone and Batch number.

## 7. Review

- Code review focuses on architectural consistency, code quality, and adherence to repository governance.
- Address all feedback. If changes are requested, push new commits to your branch.

## 8. Merge

Once approved and verified, the Pull Request will be merged into `main`. We prefer squash-merging or rebase-merging to keep a clean, linear history, ensuring the commit message follows the required convention.
