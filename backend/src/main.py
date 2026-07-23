from contextlib import asynccontextmanager
from typing import Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging


from src.presentation.api.v1 import api_router
from src.config.system_settings import SystemSettings
from src.core.bootstrap import validate_startup
import httpx
from src.intelligence.providers.registry import ProviderRegistry
from src.intelligence.providers.ollama.provider import OllamaProvider
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.presentation.schemas import ErrorResponse, ErrorDetail
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
APP_TITLE = "AI Clipping Platform API"
APP_DESCRIPTION = "Local-first REST API for multimodal video analysis and clip generation."
APP_VERSION = "1.0.0"



system_settings = SystemSettings()
ENVIRONMENT = system_settings.environment

CORS_ORIGIN_REGEX: Optional[str]

if ENVIRONMENT == "development":
    # Development: Allow all localhost ports to gracefully handle Vite port-hopping
    CORS_ORIGINS = []
    CORS_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
else:
    # Production: Require explicit origins, deny all by default
    raw_origins = system_settings.cors_origins
    CORS_ORIGINS = [origin.strip() for origin in raw_origins.split(",")] if raw_origins else []
    CORS_ORIGIN_REGEX = None

# --- Lifecycle ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Resources initialized here will be available for the entire lifespan of the app.
    """
    # Startup: Initialize resources (DB pools, ML models, background tasks)
    logger.info("Starting AI Clipping Platform API...")
    
    # Initialize DI Container
    from src.bootstrap.startup import initialize_container
    container = initialize_container()
    app.state.container = container
    
    # Run strict startup validation
    await validate_startup(app)
    
    yield  # Application runs while yielded
    
    # Shutdown: Clean up resources
    import httpx
    from src.infrastructure.database import engine
    
    try:
        http_client = container.resolve(httpx.AsyncClient)
        await http_client.aclose()
    except Exception as e:
        logger.warning(f"Failed to close HTTP client: {e}")
        
    try:
        await engine.dispose()
        logger.info("Database connection pool disposed.")
    except Exception as e:
        logger.warning(f"Failed to dispose database engine: {e}")
    
    logger.info("Shutting down AI Clipping Platform API...")

# --- Bootstrapping ---

def configure_middleware(app: FastAPI) -> None:
    """Configures application middleware stacks (CORS, Auth, Request Logging)."""
    cors_kwargs: dict[str, Any] = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    
    if CORS_ORIGINS:
        cors_kwargs["allow_origins"] = CORS_ORIGINS
    if CORS_ORIGIN_REGEX:
        cors_kwargs["allow_origin_regex"] = CORS_ORIGIN_REGEX
        
    app.add_middleware(CORSMiddleware, **cors_kwargs)


def configure_exception_handlers(app: FastAPI) -> None:
    """Configures global exception handlers to enforce strict API contracts."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        """Overrides default FastAPI 422 shape to match our ErrorResponse schema."""
        details = str(exc.errors())
        error_detail = ErrorDetail(
            code="VALIDATION_ERROR",
            message="The request payload failed schema validation.",
            details=details
        )
        error_response = ErrorResponse(error=error_detail)
        return JSONResponse(
            status_code=422,
            content=error_response.dict(),
        )

def configure_routers(app: FastAPI) -> None:
    """Registers all application routers."""
    app.include_router(api_router, prefix="/api/v1")

# --- OpenAPI Metadata ---
TAGS_METADATA = [
    {"name": "System", "description": "Core infrastructure checks and lifecycle management."},
    {"name": "Projects", "description": "Manage video clipping workspaces."},
    {"name": "Videos", "description": "Upload and manage raw source footage."},
    {"name": "Clips", "description": "Interact with AI-generated short-form content."},
    {"name": "Analysis", "description": "Endpoints to trigger the AI multimodal processing pipeline."},
    {"name": "Exports", "description": "Render and download finalized videos with subtitles."},
    {"name": "Models", "description": "Manage local LLMs, Whisper weights, and vision pipelines."},
    {"name": "Settings", "description": "Global user configuration and preferences."}
]

def create_app() -> FastAPI:
    """
    Application Factory.
    Creates, configures, and returns the FastAPI application instance.
    """
    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        openapi_tags=TAGS_METADATA,
        lifespan=lifespan,
    )
    
    configure_middleware(app)
    configure_exception_handlers(app)
    configure_routers(app)
    
    return app

# Expose default instance for convenience (e.g., `uvicorn main:app --reload`)
app = create_app()
