# Development Workflow

This document details the standardized developer tooling commands for the project.

> [!WARNING]
> Some of the canonical development commands currently fail (return non-zero exit codes) due to existing violations or issues in the application code. These quality gates remain strictly enforced and have not been relaxed. You should expect these commands to report the known issues until they are addressed.

## Backend Development

The backend uses standard Python tooling. Ensure you are running commands from the `backend/` directory with your virtual environment activated.

### Setup
```bash
cd backend
python -m venv .venv
# On Windows
.\.venv\Scripts\activate
# On Unix
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Testing
We use `pytest` for running automated tests. 

```bash
pytest
```

> [!NOTE]
> **Current Status**: Pytest currently fails (exit code `1`) during test collection and execution due to known application issues:
> - Broken imports (e.g., `src.reasoning.recommendation.interfaces` is missing).
> - An assertion failure in `tests/test_api_integration.py` (`test_projects_create_schema_and_error`).

### Static Analysis
We use `ruff` as our primary linter. Pyright is used via the IDE for type checking.

```bash
ruff check .
```

> [!NOTE]
> **Current Status**: Ruff currently fails (exit code `1`) as the codebase contains roughly 109 legacy violations (e.g., `E402`, `F401`, `F821`, `E722`, `E741`). These must be manually resolved in future batches.

### Formatting
Formatting should be handled by your IDE via Ruff formatting rules. No separate formatting script is enforced at this time to avoid competing tools.

## Frontend Development

The frontend uses Vite, TypeScript, and React. Ensure you are running commands from the `frontend/` directory.

### Setup
```bash
cd frontend
npm install
```

### Static Analysis
We use ESLint for static analysis.

```bash
npm run lint
```

> [!NOTE]
> **Current Status**: The lint command currently fails (exit code `1`) due to 16 existing `@typescript-eslint/no-explicit-any` violations. The rule has been kept active to reflect the intended coding standard.

### Building
```bash
npm run build
```

## Recommended IDE Configuration

We recommend using VS Code. The repository includes an `extensions.json` file recommending the following:
- Python (`ms-python.python`)
- Ruff (`charliermarsh.ruff`)
- ESLint (`dbaeumer.vscode-eslint`)

These extensions will automatically pick up the repository's configuration.
