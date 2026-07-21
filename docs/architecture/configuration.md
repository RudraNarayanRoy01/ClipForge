# Configuration Architecture

The configuration architecture in ClipForge is built on the principle of clear ownership, deterministic precedence, bounded contexts, and early validation.

## Bounded Contexts

Configuration is strictly divided by its bounded context, ensuring no single "god object" holds unrelated settings. The settings are defined in `backend/src/config/`:

- **`SystemSettings`**: Controls system-level execution defaults, such as `ENVIRONMENT`, `DB_PATH`, and `CORS_ORIGINS`.
- **`AISettings`**: Controls AI model preferences, routing, and parameters (e.g. `OLLAMA_HOST`, `AI_TEMPERATURE`).
- **`MediaSettings`**: Controls underlying media execution parameters (e.g. `FFMPEG_EXECUTABLE_PATH`, `PROCESS_TIMEOUT`).
- **`TranscriptionSettings`**: Controls speech-to-text behaviors (e.g. `TRANSCRIPTION_MODEL`, `TRANSCRIPTION_DEVICE`).

All modules independently inherit from Pydantic's `BaseSettings`.

## Loading Precedence

Configuration values are resolved in the following deterministic order (highest priority first):

1. **Runtime Overrides:** Values passed directly in code.
2. **Environment Variables:** Values exported in the OS environment.
3. **Configuration Files (`.env`):** Loaded from the local `.env` file at the root.
4. **Application Defaults:** Hardcoded defaults in the respective Pydantic model fields.

## Validation

All configuration models are explicitly instantiated during the `validate_startup` sequence in `backend/src/core/bootstrap.py`.
This guarantees that missing required variables, incorrect types, or violations of configuration constraints will fail the boot sequence immediately, preventing runtime anomalies and silent failures.

## Secrets Management

Secrets (e.g., API keys) must never be committed.
1. The `.env.example` file contains structural examples and dummy values.
2. For local development, copy `.env.example` to `.env` and fill in sensitive details.
3. The `.env` file is excluded from version control via `.gitignore`.
