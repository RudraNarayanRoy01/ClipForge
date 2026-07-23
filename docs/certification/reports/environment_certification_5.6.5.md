# Environment Certification 5.6.5

## Environment Ownership Matrix

| Area | Owner | Source | Type/Validation | Default Values |
| :--- | :--- | :--- | :--- | :--- |
| **Environment Variables** | Platform | `.env` or OS | Strict via Pydantic | Provided for all fields |
| **Configuration Files** | Modules (`src/config/`) | Codebase | Class validation | N/A |
| **Secrets** | Infrastructure | Secrets Manager | Secure injection | None (Requires explicit injection) |
| **Runtime Overrides** | Operations | CLI / ENV | Environment overrides | None |
| **AI Settings** | `AISettings` | `ai_settings.py`| Provider, Host, Tuning | `ollama`, `gemma4:latest`, `http://localhost:11434` |
| **Database Settings**| `SystemSettings` | `system_settings.py` | Connection string | `clipping_platform.db` |
| **Media Settings** | `MediaSettings` | `media_settings.py` | Paths & Timeouts | `ffmpeg`, `ffprobe`, `300s` |
| **Logging Settings** | `SystemSettings` | Logging Config | Log Levels | `INFO` |

## Certification
Deterministic configuration is verified. Secret boundaries and environment overrides operate correctly via Pydantic's hierarchical loading.
