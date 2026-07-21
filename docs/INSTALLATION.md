# Installation

This document details the exact steps and requirements to achieve a deterministic and reproducible environment for the AI Clipping Platform.

## External Runtime Requirements

Before installing project dependencies, ensure the following tools are installed and available in your system's PATH:

- **Python**: `>= 3.9` (Required for backend services)
- **Node.js**: `>= 18.0` (Required for frontend application)
- **FFmpeg**: Required for media processing by both the Python `moviepy` backend and direct subprocess calls.
- **Ollama**: Required for running local LLM models (e.g., Gemma 4 local inference).
- **Git**: Required for version control and cloning.

## Backend Installation

The backend explicitly separates production dependencies from development tools.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a clean virtual environment:
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\activate
   # Unix/macOS
   source .venv/bin/activate
   ```
3. Install dependencies:
   - **For Production**:
     ```bash
     pip install -r requirements.txt
     ```
   - **For Development** (includes testing and typing tools):
     ```bash
     pip install -r requirements-dev.txt
     ```

## Frontend Installation

The frontend relies on `package-lock.json` as the authoritative source for dependency resolution. Do **not** use standard `npm install` for reproducible environments.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install exact dependencies from the lockfile:
   ```bash
   npm ci
   ```

## Verifying the Installation

To verify that the installation was successful:

**Backend**:
Run the test suite or start the server.
```bash
cd backend
pytest
uvicorn src.presentation.api.system:app --reload
```

**Frontend**:
Start the development server to ensure all modules load correctly.
```bash
cd frontend
npm run dev
```
