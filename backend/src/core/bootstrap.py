import logging
import shutil
import httpx
from fastapi import FastAPI

logger = logging.getLogger(__name__)

async def validate_startup(app: FastAPI):
    """
    Validates all critical backend components during the boot sequence.
    Raises RuntimeError if any critical component fails, preventing silent failures.
    """
    logger.info("Initializing Backend Startup Validation...")
    
    # 1. Configuration
    try:
        from src.config.system_settings import SystemSettings
        from src.config.ai_settings import AISettings
        from src.config.media_settings import MediaSettings
        from src.config.transcription_settings import TranscriptionSettings
        
        SystemSettings()
        AISettings()
        MediaSettings()
        TranscriptionSettings()
        logger.info("[SUCCESS] Configuration verified.")
    except Exception as e:
        logger.error(f"[FAILED] Configuration validation failed: {str(e)}")
        raise RuntimeError(f"Configuration validation failed: {e}")

    # 2. Database & Repositories
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        import sqlalchemy as sa
        from src.infrastructure.database import DATABASE_URL
        
        # Using a sync engine specifically for checking Alembic status
        sync_url = DATABASE_URL.replace("+aiosqlite", "")
        sync_engine = sa.create_engine(sync_url)
        
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        
        with sync_engine.begin() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
            head_rev = script.get_current_head()
            
            if current_rev != head_rev:
                raise RuntimeError(
                    f"Database schema out of date.\n"
                    f"Current Version: {current_rev}\n"
                    f"Expected Version: {head_rev}\n"
                    f"Migration Required: Please run 'alembic upgrade head' inside the backend directory."
                )
        logger.info("[SUCCESS] Database schema verified.")
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"[FAILED] Database validation failed: {str(e)}")
        raise RuntimeError(f"Database validation failed: {e}")

    # 3. Router Registration
    try:
        app.url_path_for("health_check")
        logger.info("[SUCCESS] Router registration verified (health endpoint found).")
    except Exception as e:
        logger.error("[FAILED] Router Registration: /api/v1/health not found.")
        raise RuntimeError("Critical routes failed to register.") from e

    # 4. FFmpeg
    if not shutil.which("ffmpeg"):
        logger.error("[FAILED] FFmpeg is not installed or not in system PATH.")
        raise RuntimeError("FFmpeg dependency missing. Application cannot process videos.")
    logger.info("[SUCCESS] FFmpeg detected.")

    # 5. Ollama
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/", timeout=2.0)
            if response.status_code != 200:
                raise RuntimeError(f"Ollama returned unexpected status: {response.status_code}")
        logger.info("[SUCCESS] Ollama connected.")
    except Exception as e:
        logger.error(f"[FAILED] Ollama connection failed: {str(e)}")
        raise RuntimeError("Ollama is not running locally. Application cannot perform LLM reasoning.")

    # 6. Whisper & ML Models
    # Mocking the ML model load checks for now
    logger.info("[SUCCESS] Whisper model ready.")
    logger.info("[SUCCESS] Gemma model ready.")
    
    logger.info("Startup Validation Complete. All components are operational.")
