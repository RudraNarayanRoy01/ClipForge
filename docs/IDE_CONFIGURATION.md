# IDE Configuration Guide

This document details the IDE and tooling configurations for the AI Clipping Platform monorepo. It specifically focuses on how to properly set up Pyrefly (and Pyright/Pylance) to work seamlessly with the project's structure and Python virtual environment.

## Workspace Structure

The project uses a monorepo structure:
```
AI Clipping Platform/
├── backend/            # Python backend services
│   ├── .venv/          # Python virtual environment
│   ├── src/            # Source code (imported as backend.src.*)
│   └── tests/          # Test files
├── frontend/           # Web frontend applications
├── docs/               # Project documentation
├── pyrightconfig.json  # Pyright module resolution configuration
└── .vscode/
    └── settings.json   # IDE and extension-specific settings
```
Crucially, all backend Python absolute imports start from the workspace root (e.g., `from backend.src.intelligence.timeline.models import ...`). This means the Python tooling must consider the root directory as the starting point for module resolution.

## Virtual Environment Configuration

The virtual environment is located at `backend/.venv`. We rely on Pyrefly (the language server) to resolve installed third-party packages (like `fastapi`, `pydantic`, `sqlalchemy`) directly from this environment.

### `pyrightconfig.json` Explanation

The `pyrightconfig.json` is located at the workspace root and explicitly tells Pyrefly how to locate the virtual environment.

```json
{
  "venvPath": "backend",
  "venv": ".venv"
}
```

* **`venvPath`**: Instructs Pyrefly to look inside the `backend` directory for virtual environments.
* **`venv`**: Instructs Pyrefly to select the virtual environment named `.venv`.

**Why we removed `pythonPath` and `extraPaths`:**
Older configurations sometimes used `"pythonPath": "backend/.venv/Scripts/python.exe"` in `pyrightconfig.json`. Pyright strongly discourages this for virtual environment setup, as it often fails to properly resolve site-packages.
We also removed `"extraPaths": ["backend/src"]` because the application code imports via `backend.src...`. By removing `extraPaths`, Pyright naturally uses the workspace root, matching the application's absolute import style perfectly.

### `.vscode/settings.json` Explanation

The `.vscode/settings.json` file is meant for VS Code-specific features like the integrated test explorer and debugger.

```json
{
  "python.defaultInterpreterPath": "backend/.venv/Scripts/python.exe"
}
```

* **`python.defaultInterpreterPath`**: Tells the Python extension which executable to use for running scripts, linting, and debugging. 

**Why we removed `python.analysis.extraPaths`:**
This setting conflicts with Pyright's native workspace root resolution when using absolute `backend.src` imports, causing confusion between `backend/src` and the root folder. 

## Python Interpreter Selection

Pyrefly automatically discovers the correct Python interpreter by combining the `venvPath` and `venv` fields. You do not need to manually configure the Python path in `pyrightconfig.json`.

## Known Pyrefly Limitations

* **Nested Virtual Environments**: Pyrefly is designed around a single root `pyrightconfig.json`. If the frontend directory later introduces its own Python virtual environment, you may experience resolution conflicts. In that case, you would need to use `executionEnvironments` within `pyrightconfig.json` to map specific directories to different Python environments.
* **Src-Layout**: Because the codebase uses `from backend.src...` instead of a typical src-layout (`from intelligence...`), configuring `extraPaths` is detrimental. You must treat the entire repository root as the Python module root.

## Recommended Troubleshooting Steps

If Pyrefly suddenly reports `Cannot find module "fastapi"` again:
1. Ensure the virtual environment actually exists at `backend/.venv`.
2. Ensure you have activated the virtual environment and installed the dependencies via `pip install -r backend/requirements.txt`.
3. Restart the IDE's Python Language Server (or reload the window).
4. Verify that `pyrightconfig.json` contains the `venvPath` and `venv` settings. Do not re-add `pythonPath`.

## How to Recover the Workspace After Cloning

1. Clone the repository.
2. Open the repository root in the IDE.
3. Open a terminal and run:
   ```cmd
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Reload the IDE window so Pyrefly can index the newly created `.venv`.

## Future Maintenance Recommendations

If the backend codebase grows and absolute imports like `backend.src` become too tedious, consider converting `backend/src` into a proper pip-installable package. You would:
1. Add a `pyproject.toml` or `setup.py` to `backend/`.
2. Install it in editable mode: `pip install -e backend/`.
3. Change your imports to `from src.intelligence...` or whatever top-level package name you choose.
4. If you do this, you will then need to re-introduce `extraPaths` to `pyrightconfig.json`. Until then, keep the current configuration.
