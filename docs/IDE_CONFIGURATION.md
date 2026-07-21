# IDE Configuration Guide

This document details the IDE and tooling configurations for the AI Clipping Platform monorepo. It specifically focuses on how to properly set up Pyright/Pylance to work seamlessly with the project's structure and Python virtual environment.

## Workspace Structure

The project uses a monorepo structure:
```text
AI Clipping Platform/
├── backend/            # Python backend services
│   ├── .venv/          # Python virtual environment
│   ├── src/            # Source code
│   └── tests/          # Test files
├── frontend/           # Web frontend applications
├── docs/               # Project documentation
├── pyrightconfig.json  # Pyright module resolution configuration
└── .vscode/
    ├── settings.json   # IDE and extension-specific settings
    └── extensions.json # Recommended extensions
```

All backend Python absolute imports start from the `backend/` directory (e.g., `from src.intelligence.timeline.models import ...`). 

## Virtual Environment Configuration

The virtual environment is located at `backend/.venv`. We rely on the language server to resolve installed third-party packages directly from this environment.

### `pyrightconfig.json` Explanation

The `pyrightconfig.json` is located at the workspace root and explicitly tells the language server how to locate the virtual environment.

```json
{
  "venvPath": "backend",
  "venv": ".venv"
}
```

* **`venvPath`**: Instructs Pyright to look inside the `backend` directory for virtual environments.
* **`venv`**: Instructs Pyright to select the virtual environment named `.venv`.

### `.vscode/settings.json` Explanation

The `.vscode/settings.json` file is meant for VS Code-specific features like the integrated test explorer and debugger.

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/Scripts/python.exe",
  "python.analysis.extraPaths": [
    "${workspaceFolder}/backend"
  ]
}
```

* **`python.defaultInterpreterPath`**: Tells the Python extension which executable to use for running scripts, linting, and debugging. 
* **`python.analysis.extraPaths`**: Because the codebase uses `from src...` absolute imports, adding the `backend` directory to the extraPaths is necessary so the language server knows where to resolve the `src` package.

## Python Interpreter Selection

The language server automatically discovers the correct Python interpreter by combining the `venvPath` and `venv` fields. 

## Recommended Troubleshooting Steps

If your IDE reports missing module errors (e.g., `Cannot find module "fastapi"`):
1. Ensure the virtual environment actually exists at `backend/.venv`.
2. Ensure you have activated the virtual environment and installed the dependencies via `pip install -r backend/requirements-dev.txt`.
3. Restart the IDE's Python Language Server (or reload the window).
4. Verify that `pyrightconfig.json` contains the `venvPath` and `venv` settings.
